// Steruje oknem Chrome otwartym z --remote-debugging-port=9333 (profil ~/.cache/tajlandia-feed/chrome-profile).
//   node ig.mjs status              -> czy zalogowany, URL
//   node ig.mjs shot <plik.png>     -> zrzut ekranu
//   node ig.mjs threads             -> lista czatów w skrzynce
//   node ig.mjs open <url|nazwa>    -> otwiera czat
//   node ig.mjs grab <out.txt> [--stop-at kod1,kod2]  -> przewija czat w górę i zbiera linki do postów/rolek
import { chromium } from "playwright-core";
import fs from "node:fs";

const LINK = /instagram\.com\\?\/(?:[\w.]+\\?\/)?(p|reels?|tv)\\?\/([A-Za-z0-9_-]{6,})/g;
const [cmd, ...args] = process.argv.slice(2);
const browser = await chromium.connectOverCDP("http://127.0.0.1:9333");
const ctx = browser.contexts()[0];
const page = ctx.pages().find(p => p.url().includes("instagram.com")) ?? ctx.pages()[0];

async function loggedIn() {
  const cookies = await ctx.cookies("https://www.instagram.com");
  return cookies.some(c => c.name === "sessionid" && c.value);
}

try {
  if (cmd === "status") {
    console.log(JSON.stringify({ loggedIn: await loggedIn(), url: page.url() }));
  } else if (cmd === "cookies") {
    // Netscape cookies.txt dla yt-dlp (fallback, gdy Apify nie działa) — plik 0600, poza repo.
    const cs = await ctx.cookies("https://www.instagram.com");
    const lines = ["# Netscape HTTP Cookie File", ...cs.map(c =>
      [c.domain, c.domain.startsWith(".") ? "TRUE" : "FALSE", c.path, c.secure ? "TRUE" : "FALSE",
       Math.max(0, Math.round(c.expires)), c.name, c.value].join("\t"))];
    fs.writeFileSync(args[0], lines.join("\n") + "\n", { mode: 0o600 });
    console.log(`${cs.length} ciasteczek -> ${args[0]}`);
  } else if (cmd === "post") {
    // Post ze zdjęciami (yt-dlp go nie bierze): metadane z og:* w osobnej karcie, obrazy przez sesję.
    const [code, dir] = args;
    const p = await ctx.newPage();
    await p.goto(`https://www.instagram.com/p/${code}/`, { waitUntil: "domcontentloaded" });
    await p.waitForTimeout(3500);
    const info = await p.evaluate(() => {
      const m = n => document.querySelector(`meta[property="${n}"]`)?.content || "";
      const art = document.querySelector("article") || document.querySelector("main");
      const imgs = [...(art?.querySelectorAll("img") || [])].filter(i => i.naturalWidth >= 600).map(i => i.currentSrc || i.src);
      return { desc: m("og:description"), ogimg: m("og:image"), imgs };
    });
    await p.close();
    const mm = info.desc.match(/-\s*([\w.]+)\s*[–-]\s*([^:]+):\s*"([\s\S]*)"\.?\s*$/);
    fs.mkdirSync(dir, { recursive: true });
    const urls = [...new Set([info.ogimg, ...info.imgs].filter(Boolean))].slice(0, 6);
    let n = 0;
    for (const u of urls) {
      const r = await ctx.request.get(u).catch(() => null);
      if (r && r.ok()) fs.writeFileSync(`${dir}/${n ? `frame_${String(n).padStart(2, "0")}` : "cover"}.jpg`, await r.body());
      n++;
    }
    console.log(JSON.stringify({ owner: mm?.[1] || null, date: mm?.[2] || null, caption: mm?.[3] || info.desc, images: n }));
  } else if (cmd === "shot") {
    await page.screenshot({ path: args[0] });
    console.log(args[0]);
  } else if (cmd === "threads") {
    if (!page.url().includes("/direct/")) await page.goto("https://www.instagram.com/direct/inbox/");
    await page.waitForTimeout(3000);
    const rows = await page.$$eval('a[href*="/direct/t/"], div[role="listitem"], div[role="button"]', els =>
      els.map(e => ({ href: e.getAttribute("href"), text: e.innerText.split("\n").slice(0, 2).join(" | ") }))
        .filter(r => r.text).slice(0, 60));
    console.log(JSON.stringify(rows, null, 1));
  } else if (cmd === "open") {
    const t = args.join(" ");
    if (t.startsWith("http")) await page.goto(t);
    else await page.getByText(t, { exact: false }).first().click();
    await page.waitForTimeout(3000);
    console.log(page.url());
  } else if (cmd === "grab") {
    const out = args[0];
    const si = args.indexOf("--stop-at");
    const stopAt = new Set(si >= 0 ? args[si + 1].split(",").filter(Boolean) : []);
    const found = new Map(); // kod -> {url, order}
    const add = (code, kind, extra = {}) => {
      if (!found.has(code)) found.set(code, { url: `https://www.instagram.com/${kind.startsWith("reel") ? "reel" : kind}/${code}/`, ...extra });
    };
    // Udostępnione posty to karty bez <a href>; kod siedzi w propsach Reacta karty (shortCode/targetUrl).
    const names = {}; // fbid -> {tekst etykiety: ile razy}
    const collect = () => page.evaluate(() => {
      const res = [], labels = [];
      // Wiadomość (nadawca + czas) siedzi w propsach przodka: messageRef/currentMessageRef.
      const msgRef = el => {
        const fk = Object.keys(el).find(k => k.startsWith("__reactFiber"));
        let f = fk && el[fk]; const out = {};
        for (let i = 0; i < 90 && f; i++, f = f.return) {
          const p = f.memoizedProps;
          const r = p && typeof p === "object" && (p.currentMessageRef || p.messageRef || p.slideMessageRef);
          if (r && r.sender_fbid) { out.sender ??= String(r.sender_fbid); if (r.timestamp_ms) { out.ts = Number(r.timestamp_ms); break; } }
        }
        return out;
      };
      for (const c of document.querySelectorAll('div[role="button"], div[role="article"]')) {
        const fk = Object.keys(c).find(k => k.startsWith("__reactFiber"));
        let f = fk && c[fk];
        for (let i = 0; i < 25 && f; i++, f = f.return) {
          const p = f.memoizedProps;
          const t = p && typeof p === "object" ? (p.targetUrl || p.message?.targetUrl || p.xma?.targetUrl) : null;
          const sc = p && typeof p === "object" ? (p.shortCode || p.xma?.shortCode) : null;
          const url = typeof t === "string" ? t : "";
          const m = url.match(/\/(p|reels?|tv)\/([\w-]{6,})/);
          if (m || sc) { res.push({ kind: m ? m[1] : "p", code: m ? m[2] : sc, top: c.getBoundingClientRect().top, ...msgRef(c), right: c.getBoundingClientRect().left > window.innerWidth * 0.55 }); break; }
        }
      }
      // Etykieta z imieniem nad grupą wiadomości ma ten sam sender_fbid co wiadomości pod nią.
      for (const s of document.querySelectorAll('span[dir="auto"]')) {
        const t = s.textContent.trim();
        if (t.length > 1 && t.length < 40 && /^\p{Lu}/u.test(t)) { const r = msgRef(s); if (r.sender) labels.push([r.sender, t]); }
      }
      for (const a of document.querySelectorAll('a[href*="instagram.com/"], a[href^="/p/"], a[href^="/reel"]')) {
        const m = a.getAttribute("href").match(/\/(p|reels?|tv)\/([\w-]{6,})/);
        if (m) res.push({ kind: m[1], code: m[2], top: a.getBoundingClientRect().top });
      }
      for (const s of document.querySelectorAll('div[dir="auto"], span[dir="auto"]')) {
        for (const m of s.textContent.matchAll(/instagram\.com\/(?:[\w.]+\/)?(p|reels?|tv)\/([\w-]{6,})/g)) res.push({ kind: m[1], code: m[2], top: 0 });
      }
      return { res, labels };
    });
    const scrollUp = () => page.evaluate(() => {
      const box = [...document.querySelectorAll("div")].filter(d => d.scrollHeight > d.clientHeight + 200 && getComputedStyle(d).overflowY !== "visible")
        .sort((a, b) => b.clientWidth * b.clientHeight - a.clientWidth * a.clientHeight)[0];
      if (!box) return null;
      const before = box.scrollTop;
      box.scrollBy(0, -box.clientHeight * 0.8); // column-reverse: w górę = bardziej ujemny scrollTop
      return { before, after: box.scrollTop, h: box.scrollHeight };
    });
    let still = 0, order = 0;
    for (let i = 0; i < 600 && still < 10; i++) {
      const before = found.size;
      const { res, labels } = await collect();
      for (const r of res.sort((a, b) => b.top - a.top)) add(r.code, r.kind, { code: r.code, sender: r.sender, ts: r.ts, mine: r.right, order: order++ });
      for (const [fb, t] of labels) { names[fb] ??= {}; names[fb][t] = (names[fb][t] || 0) + 1; }
      if ([...found.keys()].some(k => stopAt.has(k))) { console.error("dotarłem do znanego posta — stop"); break; }
      const s = await scrollUp();
      await page.waitForTimeout(1300 + Math.random() * 900);
      still = found.size === before && s && s.before === s.after ? still + 1 : 0;
      if (i % 10 === 0) console.error(`przewinięcie ${i}: ${found.size} linków (scrollTop ${s && s.after}, wys. ${s && s.h})`);
    }
    // Najstarsze na górze pliku — kolejność jak w czacie.
    const list = [...found.values()].reverse();
    fs.writeFileSync(out, list.map(v => v.url).join("\n") + "\n");
    // Imię nadawcy = najczęstsza etykieta przy jego fbid, preferując "Imię Nazwisko" (nie treść wiadomości).
    const nameOf = {};
    for (const [fb, cnt] of Object.entries(names)) {
      nameOf[fb] = Object.entries(cnt).sort((a, b) => (/^\p{Lu}\p{L}+ \p{Lu}/u.test(b[0]) - /^\p{Lu}\p{L}+ \p{Lu}/u.test(a[0])) || b[1] - a[1])[0][0];
    }
    // Własne wiadomości nie mają etykiety z imieniem (są po prawej) — nadawca z przewagą "mine" to właściciel sesji.
    const mineCnt = {};
    for (const v of list) if (v.sender) { mineCnt[v.sender] ??= [0, 0]; mineCnt[v.sender][v.mine ? 0 : 1]++; }
    for (const [fb, [m, o]] of Object.entries(mineCnt)) if (m > o) nameOf[fb] = process.env.IG_ME || "Karol";
    const meta = list.map(v => ({ url: v.url, code: v.code, sender: v.sender || null, senderName: (v.sender && nameOf[v.sender]) || null,
      sharedAt: v.ts ? new Date(v.ts).toISOString() : null, mine: !!v.mine }));
    fs.writeFileSync(out.replace(/\.txt$/, "") + ".json", JSON.stringify({ names: nameOf, links: meta }, null, 1));
    console.log(`${found.size} linków -> ${out} (+ .json z nadawcami: ${Object.values(nameOf).join(", ")})`);
  } else {
    console.log("komendy: status | shot | threads | open | grab");
  }
} finally {
  process.exit(0); // bez browser.close(): okno ma zostać otwarte z sesją
}
