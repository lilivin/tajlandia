# Tajlandia feed

Linki z grupowego czatu na Instagramie → Apify (opis, wideo) → lokalna transkrypcja i klatki →
analiza → `docs/index.html`. Każdy post przechodzi przez pipeline **raz**: stan trzyma `state.json`
(statusy `new → scraped → media → analyzed`, plus `unavailable` dla prywatnych/usuniętych postów,
oraz `last` = ostatni przeanalizowany post i data przebiegu).

## Aktualizacja (np. „dodaj nowe”)

Czat: **„Polecajka Tajlandia”** (`https://www.instagram.com/direct/t/2337745603657101/`).

```bash
cd "/Volumes/T7 Res/Projects/tajlandia-feed"
# 1. Chrome z osobnym profilem (sesja IG zostaje w nim; gdy wygaśnie — użytkownik loguje się w tym oknie)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir="$HOME/.cache/tajlandia-feed/chrome-profile" \
  --remote-debugging-port=9333 --no-first-run "https://www.instagram.com/direct/t/2337745603657101/" &
node ig.mjs status                    # loggedIn: true?
# 2. Linki: przewija czat od najnowszych w górę i staje na pierwszym znanym poście
node ig.mjs open https://www.instagram.com/direct/t/2337745603657101/
node ig.mjs grab inbox/links.txt --stop-at "$(python3 -c 'import json;print(",".join(json.load(open("state.json"))["items"]))')"
node ig.mjs cookies ~/.cache/tajlandia-feed/cookies.txt    # dla yt-dlp
# 3. Pobranie (Apify, a gdy brak kredytu: yt-dlp / przeglądarka), klatki + transkrypcje
python3 feed.py ingest inbox/links.json && python3 feed.py scrape   # .json z grab = nadawca + czas wysłania
python3 feed.py media                 # okładki, klatki, transkrypcje (OpenAI whisper-1, 6 równolegle)
python3 feed.py pending               # agent pisze analysis/<shortCode>.json dla każdej pozycji
python3 feed.py geo                   # współrzędne miejsc (OSM Nominatim, 1 zapytanie/s, cache data/geo.json)
python3 feed.py render                # buduje stronę, oznacza jako przeanalizowane, zapisuje `last`
open docs/index.html
```

Udostępnione rolki w DM to karty bez `<a href>`: `ig.mjs` czyta `shortCode`/`targetUrl` z propsów Reacta
karty. Okno wiadomości to kontener column-reverse — przewijanie w górę = ujemny `scrollTop`.

Źródła linków (`ingest`): dowolny plik tekstowy (wyciąga każdy link `instagram.com/p|reel/...`)
albo eksport Instagrama (`message_*.json` lub cały folder `messages/inbox/<czat>/`) — wtedy dochodzi
kto i kiedy wrzucił link. Linki już znane są pomijane, więc można wrzucać cały eksport za każdym razem.

Token Apify: `APIFY_TOKEN` z env albo `~/.config/content-agent/.env`. Klucz OpenAI (transkrypcje):
`OPENAI_API_KEY` z env albo `~/.config/content-agent/.env`. Aktor `apify/instagram-scraper`
(płatność za wynik, grosze za post).

## Format analizy (`analysis/<shortCode>.json`)

Na podstawie opisu, transkrypcji i klatek (`data/media/<kod>/frame_*.jpg` — obejrzeć!). Po polsku.

```json
{
  "title": "Krótki, konkretny tytuł (co to za miejsce/porada)",
  "summary": "2-3 zdania: co pokazuje film i dlaczego warto",
  "category": "Plaże i wyspy | Atrakcje | Jedzenie | Noclegi | Imprezy i nightlife | Transport | Porady i koszty | Inne",
  "region": "Bangkok | Chiang Mai | Phuket | Krabi | Koh Samui | Koh Phangan | Koh Tao | Pattaya | Koh Lanta | Koh Phi Phi | … | null",
  "places": [{"name": "Nazwa do wyszukania w Google Maps", "type": "plaża/restauracja/hotel/…", "area": "dzielnica/wyspa", "note": "czemu warto"}],
  "tips": ["konkretne wskazówki z filmu"],
  "prices": [{"item": "longtail na Phi Phi", "price": "1500 THB / łódź"}],
  "tags": ["street food", "snorkeling"]
}
```

Nie wymyślaj miejsc ani cen, których w materiale nie ma — puste listy są OK.
Post niezwiązany z Tajlandią/podróżą (memy, Halloween itp.): `{"offTopic": true, "title": "…"}` —
zostaje oznaczony jako przeanalizowany, ale nie trafia na stronę.

## Strona

Styl stron domowych z lat 90. (`template.html`): tabela ligowa (+10 za znalezisko, +2 za miejsce, −5 za
wrzutkę nie na temat, odznaki liczone w `leaderboard()`), mapa Leaflet (kafelki Esri — OSM blokuje żądania
bez Referer z `file://`, CARTO chce klucza; puste kółko = miejsca nie ma w OSM, pokazana okolica), znaleziska
po 9 na stronę z filtrami po kategorii i osobie. Nadawcy: `ig.mjs grab` czyta `sender_fbid`/`timestamp_ms`
z propsów wiadomości, imię z etykiety nad grupą; własne wiadomości (bez etykiety, po prawej) = „Karol”
(`IG_ME` zmienia).

## Publikacja (GitHub Pages)

Strona: https://lilivin.github.io/tajlandia/ — repo `lilivin/tajlandia`, Pages z `main:/docs`.
Po każdej aktualizacji: `python3 feed.py render && git add -A && git commit -m "Nowe rolki" && git push`.
Strona jest publiczna (z `noindex`): render pokazuje tylko imiona (`public_name`, ksywki w `NAME_ALIASES`);
`state.json`, `inbox/` i `data/` nie trafiają do repo. Kafelki „Ściągawka” są w `highlights.json` (ręcznie, z analiz) —
przy nowych rolkach warto je uzupełnić.
