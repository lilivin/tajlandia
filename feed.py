#!/usr/bin/env python3
"""Tajlandia feed: linki z czatu IG -> Apify -> transkrypcja + klatki -> analiza -> landing page.

  python3 feed.py ingest <links.txt | message_1.json | folder eksportu IG>...
  python3 feed.py scrape        # Apify, tylko nowe
  python3 feed.py media         # okładki, klatki, transkrypcje (OpenAI Whisper API)
  python3 feed.py pending       # co czeka na analizę (agent pisze analysis/<kod>.json)
  python3 feed.py render        # buduje docs/index.html (GitHub Pages) i zapisuje stan
  python3 feed.py update <źródła>...  # ingest + scrape + media + pending

Stan w state.json: każdy post ma status new -> scraped -> media -> analyzed.
Post raz przeanalizowany nigdy nie jest pobierany ani analizowany ponownie.
"""
import datetime

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE / "state.json"
RAW = HERE / "data" / "raw"
MEDIA = HERE / "data" / "media"
ANALYSIS = HERE / "analysis"
SITE = HERE / "docs"  # GitHub Pages serwuje z main:/docs
ACTOR = "apify~instagram-scraper"

LINK_RE = re.compile(r"instagram\.com/(?:[\w.]+/)?(p|reel|reels|tv)/([A-Za-z0-9_-]{5,})")
CATEGORIES = ["Plaże i wyspy", "Atrakcje", "Jedzenie", "Noclegi", "Imprezy i nightlife",
              "Transport", "Porady i koszty", "Inne"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"items": {}, "last": None, "runs": []}


def save_state(st):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(STATE)


def env_token():
    tok = os.environ.get("APIFY_TOKEN")
    if tok:
        return tok
    env = pathlib.Path.home() / ".config" / "content-agent" / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("APIFY_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"')
    sys.exit("Brak APIFY_TOKEN (env albo ~/.config/content-agent/.env).")


# ---------- ingest ----------

def fix_mojibake(s):
    # Eksport IG zapisuje UTF-8 jako latin-1 ("Å¼" zamiast "ż").
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def links_from_export(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for m in data.get("messages", []):
        texts = [(m.get("share") or {}).get("link") or "", m.get("content") or ""]
        for t in texts:
            for kind, code in LINK_RE.findall(t):
                ts = m.get("timestamp_ms")
                yield code, {
                    "url": f"https://www.instagram.com/{'reel' if kind.startswith('reel') else kind}/{code}/",
                    "sharedBy": fix_mojibake(m.get("sender_name", "")),
                    "sharedAt": datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).isoformat(timespec="seconds") if ts else None,
                    "note": fix_mojibake((m.get("share") or {}).get("share_text") or ""),
                }


def links_from_text(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        for kind, code in LINK_RE.findall(line):
            yield code, {"url": f"https://www.instagram.com/{'reel' if kind.startswith('reel') else kind}/{code}/",
                         "sharedBy": None, "sharedAt": None, "note": ""}


def links_from_grab(data):
    # inbox/links.json z `node ig.mjs grab`: nadawca i czas wysłania każdego linku
    for l in data["links"]:
        yield l["code"], {"url": l["url"], "sharedBy": l.get("senderName"), "sharedAt": l.get("sharedAt"), "note": ""}


def ingest(paths):
    st = load_state()
    files = []
    for p in map(pathlib.Path, paths):
        files += sorted(p.rglob("message_*.json")) if p.is_dir() else [p]
    added = 0
    for f in files:
        if f.suffix == ".json":
            data = json.loads(f.read_text(encoding="utf-8"))
            gen = links_from_grab(data) if "links" in data else links_from_export(f)
        else:
            gen = links_from_text(f)
        for code, meta in gen:
            if code in st["items"]:
                it = st["items"][code]  # znany post: tylko uzupełnij, kto i kiedy go wrzucił
                for k in ("sharedBy", "sharedAt"):
                    if meta.get(k) and not it.get(k):
                        it[k] = meta[k]
                continue
            st["items"][code] = {**meta, "status": "new", "ingestedAt": now()}
            added += 1
    save_state(st)
    print(f"ingest: +{added} nowych linków (razem {len(st['items'])})")


# ---------- scrape ----------

def scrape():
    st = load_state()
    todo = [c for c, it in st["items"].items() if it["status"] == "new"]
    if not todo:
        print("scrape: nic nowego")
        return
    token = env_token()
    RAW.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(todo), 20):
        batch = todo[i:i + 20]
        body = json.dumps({"directUrls": [st["items"][c]["url"] for c in batch],
                           "resultsType": "posts", "resultsLimit": 1, "addParentData": False}).encode()
        req = urllib.request.Request(
            f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items?token={token}",
            body, {"Content-Type": "application/json"})
        print(f"scrape: Apify {len(batch)} postów…")
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                results = json.load(r)
        except Exception as e:  # 402 = skończony kredyt Apify; yt-dlp z sesją z okna Chrome
            print(f"scrape: Apify niedostępny ({e}) — przechodzę na yt-dlp")
            scrape_ytdlp(st, todo[i:])
            break
        for it in results:
            code = it.get("shortCode")
            if code in st["items"] and not it.get("error"):
                (RAW / f"{code}.json").write_text(json.dumps(it, ensure_ascii=False, indent=1), encoding="utf-8")
                st["items"][code]["status"] = "scraped"
        for c in batch:
            if st["items"][c]["status"] == "new":
                st["items"][c]["status"] = "unavailable"  # prywatny/usunięty post — nie ponawiamy co run
        save_state(st)
    print("scrape: gotowe")


COOKIES = pathlib.Path.home() / ".cache" / "tajlandia-feed" / "cookies.txt"  # `node ig.mjs cookies <plik>`


def scrape_ytdlp(st, codes):
    if not COOKIES.exists():
        sys.exit(f"Brak {COOKIES}: uruchom Chrome z ig.mjs i `node ig.mjs cookies {COOKIES}`.")
    for code in codes:
        url = st["items"][code]["url"]
        out = MEDIA / code
        out.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["yt-dlp", "--cookies", str(COOKIES), "--no-warnings", "-q", "-J",
                            "--no-simulate", "-f", "b[height<=720]/b", "-o", str(out / "video.%(ext)s"), url],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except json.JSONDecodeError:
            d = None
        if not d:  # post ze zdjęciami — przez zalogowaną przeglądarkę
            p = subprocess.run(["node", str(HERE / "ig.mjs"), "post", code, str(out)], capture_output=True, text=True)
            try:
                info = json.loads(p.stdout.strip().splitlines()[-1])
            except (json.JSONDecodeError, IndexError):
                print(f"   {code}: niedostępny ({(r.stderr or p.stderr).strip()[:120]})")
                st["items"][code]["status"] = "unavailable"
                save_state(st)
                continue
            raw = {"shortCode": code, "url": url, "source": "browser", "caption": info["caption"],
                   "ownerUsername": info["owner"], "timestamp": info["date"], "type": "Image"}
            (RAW / f"{code}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
            st["items"][code]["status"] = "scraped"
            save_state(st)
            print(f"   {code}: ok (@{raw['ownerUsername']}, zdjęcia: {info['images']})")
            continue
        entries = [e for e in d.get("entries") or [] if e] or [d]  # karuzela = playlista; zdjęcia to None
        first = entries[0]
        raw = {"shortCode": code, "url": url, "source": "yt-dlp", "caption": d.get("description") or first.get("description"),
               "ownerUsername": d.get("channel") or first.get("channel"), "ownerFullName": d.get("uploader") or first.get("uploader"),
               "timestamp": datetime.datetime.fromtimestamp(first["timestamp"], datetime.timezone.utc).isoformat() if first.get("timestamp") else None,
               "videoDuration": first.get("duration"), "displayUrl": first.get("thumbnail"),
               "type": "Sidecar" if d.get("entries") else "Video",
               "localVideo": next((str(p) for p in out.glob("video.*")), None)}
        (RAW / f"{code}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        st["items"][code]["status"] = "scraped"
        save_state(st)
        print(f"   {code}: ok (@{raw['ownerUsername']}, {raw['type']})")


# ---------- media ----------

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


OPENAI_ENV_FILES = [pathlib.Path.home() / ".config" / "content-agent" / ".env"]


def openai_key():
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    for f in OPENAI_ENV_FILES:
        if f.exists():
            for line in f.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("Brak OPENAI_API_KEY (env albo ~/.config/content-agent/.env).")


def transcribe(mp4, key):
    """Whisper API (whisper-1, verbose_json = segmenty z czasem). Audio jako mono mp3 64k — mały upload."""
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = pathlib.Path(tmp) / "a.mp3"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vn", "-ac", "1",
                            "-b:a", "64k", str(mp3)], capture_output=True)
        if r.returncode or not mp3.exists():
            return None  # film bez ścieżki audio
        out = subprocess.run(["curl", "-s", "--max-time", "300", "https://api.openai.com/v1/audio/transcriptions",
                              "-H", f"Authorization: Bearer {key}", "-F", "model=whisper-1",
                              "-F", "response_format=verbose_json", "-F", f"file=@{mp3}"],
                             capture_output=True, text=True)
    res = json.loads(out.stdout)
    if "error" in res:
        raise RuntimeError(res["error"].get("message"))
    return {"language": res.get("language"), "text": res.get("text", "").strip(),
            "segments": [{"start": round(s["start"], 1), "text": s["text"].strip()} for s in res.get("segments", [])]}


def media_one(code, key):
    raw = json.loads((RAW / f"{code}.json").read_text(encoding="utf-8"))
    out = MEDIA / code
    out.mkdir(parents=True, exist_ok=True)
    msg = f"media: {code} ({raw.get('type')})"
    try:
        if raw.get("displayUrl") and not (out / "cover.jpg").exists():
            download(raw["displayUrl"], out / "cover.jpg")
        if raw.get("videoUrl") or raw.get("localVideo"):
            with tempfile.TemporaryDirectory() as tmp:
                mp4 = pathlib.Path(tmp) / "v.mp4"
                if raw.get("localVideo") and pathlib.Path(raw["localVideo"]).exists():
                    mp4 = pathlib.Path(raw["localVideo"])
                else:
                    download(raw["videoUrl"], mp4)
                if not (out / "frame_01.jpg").exists():
                    dur = float(raw.get("videoDuration") or 30)
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                                    f"fps={8 / max(dur, 1):.4f},scale=480:-2", "-frames:v", "8",
                                    out / "frame_%02d.jpg"], check=True)
                if not (out / "transcript.json").exists():
                    res = transcribe(mp4, key)
                    if res:
                        (out / "transcript.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        elif not (out / "frame_01.jpg").exists():
            imgs = raw.get("images") or [c.get("displayUrl") for c in raw.get("childPosts") or []]
            for n, u in enumerate([u for u in imgs if u][:8], 1):
                download(u, out / f"frame_{n:02d}.jpg")
    except Exception as e:  # wygasły link CDN itp. — analiza i tak może iść z opisu
        msg += f" — częściowo: {e}"
    return code, msg


def media():
    from concurrent.futures import ThreadPoolExecutor
    st = load_state()
    todo = [c for c, it in st["items"].items() if it["status"] == "scraped"]
    key = openai_key()
    with ThreadPoolExecutor(6) as ex:
        for code, msg in ex.map(lambda c: media_one(c, key), todo):
            print(msg, flush=True)
            st["items"][code]["status"] = "media"
            save_state(st)


# ---------- pending ----------

def pending():
    st = load_state()
    todo = [c for c, it in st["items"].items() if it["status"] == "media" and not (ANALYSIS / f"{c}.json").exists()]
    if not todo:
        print("pending: brak — wszystko przeanalizowane")
    for c in todo:
        raw = json.loads((RAW / f"{c}.json").read_text(encoding="utf-8"))
        tr = MEDIA / c / "transcript.json"
        print(json.dumps({
            "shortCode": c, "url": st["items"][c]["url"], "owner": raw.get("ownerUsername"),
            "type": raw.get("type"), "location": raw.get("locationName"),
            "caption": raw.get("caption"),
            "transcript": json.loads(tr.read_text())["text"] if tr.exists() else None,
            "frames": sorted(str(p) for p in (MEDIA / c).glob("frame_*.jpg")),
        }, ensure_ascii=False))
    return todo


# ---------- geo ----------

GEO = HERE / "data" / "geo.json"  # cache: zapytanie -> [lat, lon] albo null (nie znaleziono)


def geo_queries(place, region):
    name, area = place.get("name", ""), place.get("area") or ""
    reg = region if region and region != "Cała Tajlandia" else ""
    qs = [", ".join(x for x in (name, area or reg) if x), name]
    return list(dict.fromkeys(q for q in qs if q))


def geo_area_queries(place, region):
    """Przybliżenie, gdy samego miejsca nie ma w OSM: dzielnica/wyspa, potem region."""
    reg = region if region and region != "Cała Tajlandia" else ""
    qs = [place.get("area") or "", reg]
    return list(dict.fromkeys(q for q in qs if q))


def geo():
    """OpenStreetMap Nominatim: 1 zapytanie/s (polityka usługi), tylko Tajlandia, wyniki w cache."""
    import time
    import urllib.parse
    cache = json.loads(GEO.read_text(encoding="utf-8")) if GEO.exists() else {}
    todo = []
    for p in ANALYSIS.glob("[!.]*.json"):
        a = json.loads(p.read_text(encoding="utf-8"))
        if a.get("offTopic"):
            continue
        for pl in a.get("places", []):
            todo.append(geo_queries(pl, a.get("region")))
            todo.append(geo_area_queries(pl, a.get("region")))
    asked = 0
    for qs in todo:
        for q in qs:
            if q in cache:
                if cache[q]:
                    break
                continue
            url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
                {"q": q, "countrycodes": "th", "format": "json", "limit": 1})
            req = urllib.request.Request(url, headers={"User-Agent": "tajlandia-feed/1.0 (private trip page)"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    res = json.load(r)
                cache[q] = [float(res[0]["lat"]), float(res[0]["lon"])] if res else None
            except Exception as e:
                print(f"geo: {q}: {e}")
            asked += 1
            time.sleep(1.1)
            if cache.get(q):
                break
        GEO.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"geo: {sum(1 for v in cache.values() if v)}/{len(cache)} zapytań trafionych ({asked} nowych)")


def geo_lookup(place, region, cache):
    """-> (lat, lon, przybliżone?) albo None. Trafienie >80 km od regionu posta = pomyłka OSM (np. inne „Monkey Hill”)."""
    import math
    center = cache.get(region or "")
    def far(ll):
        if not center:
            return False
        la1, lo1, la2, lo2 = map(math.radians, [*center, *ll])
        h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
        return 2 * 6371 * math.asin(math.sqrt(h)) > 80
    for q in geo_queries(place, region):
        if cache.get(q) and not far(cache[q]):
            return cache[q], False
    for q in geo_area_queries(place, region):
        if cache.get(q):
            return cache[q], True
    return None


# ---------- render ----------

NAME_ALIASES = {"MATYJASEK": "Mikołaj"}  # ksywki z czatu -> imię na stronie


def public_name(name):
    """Strona jest publiczna (GitHub Pages): tylko imię, bez nazwiska. Pełne dane zostają w state.json (poza repo)."""
    if not name:
        return name
    return NAME_ALIASES.get(name, name.split()[0])


def leaderboard(posts, offtopic):
    """Grywalizacja: +10 za znalezisko, +2 za każde miejsce, -5 za wrzutkę nie na temat. Odznaki na śmiesznie."""
    import collections
    people = collections.defaultdict(lambda: {"posts": 0, "places": 0, "off": 0, "cats": collections.Counter(),
                                              "regions": collections.Counter(), "hours": [], "first": None})
    for p in posts:
        who = p.get("sharedBy") or "Anonim"
        d = people[who]
        d["posts"] += 1
        d["places"] += len(p.get("places", []))
        d["cats"][p.get("category")] += 1
        d["regions"][p.get("region")] += 1
        if p.get("sharedAt"):
            t = datetime.datetime.fromisoformat(p["sharedAt"].replace("Z", "+00:00")).astimezone()
            d["hours"].append(t.hour)
            d["first"] = min(d["first"] or p["sharedAt"], p["sharedAt"])
    for o in offtopic:
        people[o.get("sharedBy") or "Anonim"]["off"] += 1
    rows = []
    for who, d in people.items():
        rows.append({"name": who, "posts": d["posts"], "places": d["places"], "off": d["off"],
                     "points": d["posts"] * 10 + d["places"] * 2 - d["off"] * 5,
                     "topCat": d["cats"].most_common(1)[0][0] if d["cats"] else None,
                     "night": sum(1 for h in d["hours"] if h < 6), "first": d["first"],
                     "bangkok": d["regions"].get("Bangkok", 0), "party": d["cats"].get("Imprezy i nightlife", 0),
                     "food": d["cats"].get("Jedzenie", 0), "tips": d["cats"].get("Porady i koszty", 0)})
    rows.sort(key=lambda r: -r["points"])
    def award(key, label, min_val=1):  # odznaka dla lidera danej kategorii
        best = max(rows, key=lambda r: r[key], default=None)
        if best and best[key] >= min_val:
            best.setdefault("badges", []).append(label)
    award("bangkok", "👑 Król/Królowa Bangkoku", 3)
    award("party", "🪩 Imprezowicz(ka) roku", 2)
    award("food", "🍜 Główny degustator", 2)
    award("tips", "🧠 Profesor od porad", 2)
    award("night", "🦉 Nocny Marek (wrzuca po północy)", 1)
    award("off", "🙈 Spamer — wrzuca nie na temat", 1)
    award("places", "🗺️ Kartograf", 5)
    firsts = [r for r in rows if r["first"]]
    if firsts:
        min(firsts, key=lambda r: r["first"]).setdefault("badges", []).append("🐣 Pierwsza wrzutka na czacie")
    return rows


def render():
    st = load_state()
    prev_last = st.get("last") or {}
    added = []
    for c, it in st["items"].items():
        if it["status"] == "media" and (ANALYSIS / f"{c}.json").exists():
            it["status"] = "analyzed"
            it.setdefault("analyzedAt", now())
            added.append(c)
    # "NOWE" = dodane w ostatniej aktualizacji, która coś dodała (ponowny render tego nie zeruje);
    # pierwsze zbudowanie strony nie oznacza niczego jako nowe.
    if added:
        new_codes = set(added) if prev_last else set()
    else:
        new_codes = set(prev_last.get("newCodes", []))
    order = {c: i for i, c in enumerate(st["items"])}  # kolejność z czatu (ingest: od najstarszych)
    posts, offtopic = [], []
    geocache = json.loads(GEO.read_text(encoding="utf-8")) if GEO.exists() else {}
    for c, it in st["items"].items():
        if it["status"] != "analyzed":
            continue
        a = json.loads((ANALYSIS / f"{c}.json").read_text(encoding="utf-8"))
        if a.get("offTopic"):  # nie pokazujemy jako znalezisko, ale liczy się w rankingu (na minus)
            offtopic.append({"title": a.get("title"), "sharedBy": public_name(it.get("sharedBy")), "url": it["url"]})
            continue
        for pl in a.get("places", []):
            hit = geo_lookup(pl, a.get("region"), geocache)
            if hit:
                pl["ll"], pl["approx"] = hit
        raw = json.loads((RAW / f"{c}.json").read_text(encoding="utf-8"))
        cover = MEDIA / c / "cover.jpg"
        if not cover.exists():
            frames = sorted((MEDIA / c).glob("frame_*.jpg"))
            cover = frames[0] if frames else None
        if cover:
            (SITE / "img").mkdir(parents=True, exist_ok=True)
            shutil.copy(cover, SITE / "img" / f"{c}.jpg")
        posts.append({**a, "shortCode": c, "url": it["url"], "owner": raw.get("ownerUsername"),
                      "sharedBy": public_name(it.get("sharedBy")), "sharedAt": it.get("sharedAt"),
                      "isVideo": bool(raw.get("videoUrl") or raw.get("localVideo")), "img": f"img/{c}.jpg" if cover else None,
                      "isNew": c in new_codes, "postedAt": raw.get("timestamp"),
                      "analyzedAt": it["analyzedAt"], "_order": order[c]})
    posts.sort(key=lambda p: (p.get("sharedAt") or "", p["_order"]), reverse=True)  # najnowsze z czatu na górze
    SITE.mkdir(exist_ok=True)
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    # Kafelki tematyczne (highlights.json, ręcznie ułożone z analiz): ref -> link i tytuł źródłowej rolki.
    by_code = {p["shortCode"]: p for p in posts}
    tiles = json.loads((HERE / "highlights.json").read_text(encoding="utf-8")) if (HERE / "highlights.json").exists() else []
    for t in tiles:
        for item in t["items"]:
            src = by_code.get(item.get("ref"))
            if src:
                item.update(url=src["url"], src=src["title"])
    data = json.dumps({"posts": posts, "categories": CATEGORIES, "updatedAt": now(), "tiles": tiles,
                       "leaderboard": leaderboard(posts, offtopic), "offtopic": offtopic}, ensure_ascii=False)
    (SITE / "index.html").write_text(tpl.replace("/*__DATA__*/null", data.replace("</", "<\\/")), encoding="utf-8")
    # Ostatni (najnowszy w czacie) przeanalizowany post — punkt, na którym `ig.mjs grab` może się zatrzymać.
    analyzed = [c for c, it in st["items"].items() if it["status"] == "analyzed"]
    newest = analyzed[-1] if analyzed else None
    st["last"] = {"at": now() if added or not prev_last else prev_last.get("at"), "shortCode": newest,
                  "url": newest and st["items"][newest]["url"], "total": len(posts), "newCodes": sorted(new_codes)}
    if added:
        st["runs"].append({"at": now(), "total": len(posts), "added": len(added)})
    save_state(st)
    print(f"render: {len(posts)} postów -> {SITE / 'index.html'}")


def main():
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    if cmd == "ingest":
        ingest(args)
    elif cmd == "scrape":
        scrape()
    elif cmd == "media":
        media()
    elif cmd == "pending":
        pending()
    elif cmd == "geo":
        geo()
    elif cmd == "render":
        render()
    elif cmd == "update":
        if args:
            ingest(args)
        scrape(); media(); pending()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
