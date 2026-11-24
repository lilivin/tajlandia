"""Buduje docs/bangkok-doc.html — plan Bangkoku do skopiowania do Google Docs (style inline, żeby przeżyły wklejenie)."""
from pathlib import Path

F = "font-family:Arial,sans-serif;"
def hl(s, c): return f'<span style="background-color:{c};font-weight:bold">{s}</span>'
Y = lambda s: hl(s, "#fff2a8")   # ważne
G = lambda s: hl(s, "#d9f2d9")   # cena
R = lambda s: hl(s, "#ffd6d6")   # pułapka
TH = "background-color:#333333;color:#ffffff;font-weight:bold;padding:6px 10px;border:1px solid #333333"

def band(title, sub, color):
    return (f'<table style="border-collapse:collapse;width:100%;{F}margin:0"><tr><td style="background-color:{color};padding:12px 14px;border:1px solid {color}">'
            f'<span style="color:#ffffff;font-size:18pt;font-weight:bold;{F}">{title}</span><br><span style="color:#ffffff;font-size:11pt;{F}">{sub}</span></td></tr></table>')

def day(title, sub, color, light, rows, notes=()):
    o = band(title, sub, color) + f'<table style="border-collapse:collapse;width:100%;{F}font-size:11pt"><tr><td style="{TH};width:18%">Godzina</td><td style="{TH}">Co robimy</td></tr>'
    for i, (t, what) in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f7f7f7"
        o += (f'<tr><td style="background-color:{light};font-weight:bold;padding:7px 10px;border:1px solid #cccccc;vertical-align:top;white-space:nowrap">{t}</td>'
              f'<td style="background-color:{bg};padding:7px 10px;border:1px solid #cccccc;vertical-align:top">{what}</td></tr>')
    o += '</table>'
    for n in notes: o += f'<p style="{F}font-size:10.5pt;margin:8px 0 0">💡 {n}</p>'
    return o + '<p style="margin:0">&nbsp;</p>'

def part(t): return f'<h2 style="{F}font-size:17pt;margin:14px 0 8px;color:#222222">{t}</h2>'
def note(t): return f'<p style="{F}font-size:10.5pt;margin:6px 0 0">💡 {t}</p>'
C = "padding:7px 10px;border:1px solid #cccccc;vertical-align:top"

doc = f'''<h1 style="{F}font-size:26pt;margin:0 0 4px">🇹🇭 Bangkok — plan na 2 + 2 dni</h1>
<p style="{F}font-size:12pt;color:#555555;margin:0 0 6px">Start: czwartek 11.02 – piątek 12.02.2027 · Finał: poniedziałek 1.03 – wtorek 2.03.2027 · wylot do domu w środę 3.03</p>
<p style="{F}font-size:10.5pt;margin:0 0 6px">Legenda: {Y("ważne / pilnuj godziny")} &nbsp; {G("cena")} &nbsp; {R("uwaga, pułapka")} &nbsp;·&nbsp; Ceny i godziny otwarcia orientacyjne — sprawdźcie przed wyjazdem.</p>
<p style="{F}font-size:10.5pt;margin:0 0 4px"><b>Podział:</b> na start to, czego nie da się przenieść (zabytki, Chinatown, jedyny weekendowy wieczór). Na finał zakupy, rooftop i Muay Thai — pamiątek nie wozimy przez trzy tygodnie.</p>'''

doc += part("CZĘŚĆ 1 — po przylocie")
doc += day("CZWARTEK 11.02", "Przylot, Chinatown i Song Wat — dzień na luzie", "#d4006a", "#fde3ef", [
 ("7:20", f"<b>Lądowanie.</b> Kontrola paszportowa i bagaże: ok. 1–1,5 h. Na lotnisku wymienić {Y('tylko trochę gotówki')} — resztę w kantorze SuperRich (lepszy kurs)."),
 ("9:00", f"<b>Dojazd do miasta.</b> Kolejka lotniskowa: ok. 30 min, {G('45 THB')}. Albo taxi z kiosku z numerkiem — {Y('licznik musi być włączony')}, do ceny {G('+50 THB')} opłaty lotniskowej. {R('Nie wsiadać do auta od naganiacza.')}"),
 ("10:00", f"<b>Hotel:</b> zostawiamy bagaże. {Y('Wczesny check-in załatwić mailowo przed wyjazdem.')}"),
 ("10:30–14:00", "Śniadanie, karta SIM / eSIM, drzemka. Nic ambitnego po kilkunastu godzinach podróży."),
 ("15:00", f"<b>Wat Traimit</b> (Złoty Budda) — przy stacji metra Hua Lamphong. {Y('Zamykają ok. 17:00.')}"),
 ("16:00", "<b>Song Wat Road → Talat Noi:</b> kawiarnie, street art, sklepiki; mango sticky rice w Wanjai Cafe House."),
 ("17:45", f"<b>Zachód słońca nad rzeką</b> w kawiarni Hong Sieng Kong ({Y('słońce zachodzi ok. 18:20')})."),
 ("19:00", "<b>Kolacja na Yaowarat (Chinatown).</b> Stoiska rozkładają się wieczorem; najlepsze jedzenie jest w bocznych uliczkach."),
 ("21:30", "Powrót metrem i spać — jutro wczesna pobudka."),
])
doc += day("PIĄTEK 12.02", "Stare Miasto jednym ciągiem + jedyny weekendowy wieczór w Bangkoku", "#8a2be2", "#eee0fb", [
 ("8:15", f"<b>Pod bramą Wielkiego Pałacu</b> (otwierają 8:30, {G('500 THB')}). {R('Ktoś mówi, że „dziś zamknięte”? To naciągacz — idźcie dalej.')}"),
 ("8:30–10:30", "<b>Wielki Pałac</b> i świątynia Szmaragdowego Buddy (Wat Phra Kaew)."),
 ("10:45–12:00", f"<b>Wat Pho</b> z Leżącym Buddą — 10 minut pieszo, {G('300 THB')}."),
 ("12:00–13:30", "Lunch przy przystani Tha Tien, potem <b>tajski masaż</b> w szkole przy Wat Pho."),
 ("13:30–15:00", f"Prom na drugi brzeg ({G('kilka THB')}) i <b>Wat Arun</b> ({G('200 THB')})."),
 ("15:00–16:30", "<b>Przerwa na upał:</b> kawa albo drink w barze Mitr Street z widokiem na Wat Pho."),
 ("17:00–18:30", "<b>Złota Góra (Wat Saket)</b> na zachód słońca — dojazd taxi albo tuk-tukiem."),
 ("19:00–20:30", "Kolacja i piwo na <b>Khao San Road / Rambuttri Alley</b> (10 minut od Złotej Góry)."),
 ("21:00", f"<b>Wieczór na mieście:</b> Silom Soi 4 albo klub z waszej listy. {Y('To jedyny piątek/sobota w Bangkoku na całym wyjeździe')} — na finale są poniedziałek i wtorek."),
], [f"{Y('Ubranie zakrywające ramiona i kolana na cały dzień')} — inaczej nie wpuszczą do pałacu.",
    "Kto nie ma siły po zwiedzaniu: wieczór można skończyć na Khao San, a Silom zostawić na wtorek 2.03 (będzie spokojniej)."])

doc += band("SOBOTA 13.02", "Wyjazd z Bangkoku — kierunek do ustalenia", "#0088cc")
doc += (f'<table style="border-collapse:collapse;width:100%;{F}font-size:11pt"><tr><td style="{TH};width:18%">Wariant</td><td style="{TH}">Jak</td><td style="{TH}">Co dalej</td></tr>'
        f'<tr><td style="background-color:#eee0fb;font-weight:bold;{C}">⛰️ Północ</td><td style="{C}">Lot do Chiang Mai rano (1 h 20 min) albo nocny pociąg o 18:40</td><td style="{C}">Przy pociągu rano zdążycie jeszcze na Chatuchak (targ tylko w weekendy, obok dworca)</td></tr>'
        f'<tr><td style="background-color:#d6effa;font-weight:bold;{C}">🏝️ Wyspy</td><td style="background-color:#f7f7f7;{C}">Lot do Surat Thani rano (ok. 1 h 15 min)</td><td style="background-color:#f7f7f7;{C}">Bus do Khao Sok (ok. 2 h) albo na prom w Don Sak</td></tr></table>')
doc += note(f"Przy porannym locie: {Y('pobudka ok. 6:45–7:00, wyjazd spod hotelu 7:30')}, w dwóch taksówkach. Dojazd na lotnisko: 30–50 min, ok. {G('300–400 THB')} + autostrada.")
doc += note(f"{Y('Sprawdzić, z którego lotniska jest lot')} — tanie linie latają z Don Mueang (DMK), nie z Suvarnabhumi (BKK).")
doc += note(f"{R('Przy porannym wylocie Chatuchak wypada z wyjazdu')} — na finale jesteście w poniedziałek i wtorek, a targ działa tylko w weekendy.")
doc += '<p style="margin:0">&nbsp;</p>'

doc += part("CZĘŚĆ 2 — przed odlotem")
doc += day("PONIEDZIAŁEK 1.03", "Powrót z wysp, Jim Thompson i rooftop", "#ff7a00", "#ffe9d2", [
 ("rano", f"<b>Lot z południa do Bangkoku</b> (ok. 1 h 30 min). {Y('Brać poranny lot')} — każda godzina później to godzina mniej w mieście."),
 ("12:00", "Hotel przy Siam albo Sukhumvit: zostawić bagaże, szybki lunch — np. michelinowskie pork noodles w Rung Rueang."),
 ("14:00–15:30", f"<b>Dom Jima Thompsona</b> (BTS National Stadium) — zwiedzanie z przewodnikiem, ok. {G('250 THB')}. {Y('Ostatnie wejście ok. 17:00.')}"),
 ("15:30–17:00", "<b>Banthat Thong</b> (15 minut pieszo): ulica z jedzeniem, lody, kawa. Wieczorem warto tu wrócić na Jeh O Chula."),
 ("17:00–18:00", f"Hotel: prysznic i przebranie na rooftop — {Y('bez klapek i krótkich spodenek')}."),
 ("18:00–20:00", "<b>Rooftop na zachód słońca:</b> Tichuca albo Tribe Sky Beach Club (ten z basenem). W poniedziałek o stolik łatwiej niż w weekend."),
 ("20:30", "Kolacja, potem ukryty <b>Good Trouble Bar</b> (happy hour 19–21) albo listening bar <b>Salon Kiku</b>."),
])
doc += day("WTOREK 2.03", "Zakupy, warany i Muay Thai na pożegnanie", "#00802b", "#dff2e4", [
 ("9:30–12:30", "<b>Zakupy:</b> Platinum Fashion Mall (tanie ciuchy) i MBK Center; kosmetyki i przekąski z 7-Eleven do walizki."),
 ("12:30–14:00", "Lunch w food courcie Terminal 21 albo — dla cierpliwych — omlet z krabem u <b>Jay Fai</b> (kolejka, sprawdzić, czy tego dnia otwarte)."),
 ("14:00–16:00", "<b>Pamiątki na Song Wat:</b> ceramika, pocztówki, metalowe talerze (łatwo przewieźć) — rolka poleca tę trasę właśnie na ostatni dzień."),
 ("16:30–17:30", "<b>Lumphini Park</b> i warany — po największym upale."),
 ("19:00", f"<b>Gala Muay Thai na stadionie Rajadamnern</b> — bilety {G('od 1 000 THB')}, {Y('kupić wcześniej na stronie stadionu')}."),
 ("21:30", "Pożegnalna kolacja; kto ma siłę — Silom Soi 4."),
], [f"{Y('Spakować walizki przed wyjściem na Muay Thai')} — w środę rano ma zostać tylko śniadanie i droga na lotnisko."])

doc += band("ŚRODA 3.03", "Wylot do domu", "#555555")
doc += note(f"Na lotnisku być {Y('3 godziny przed lotem')}; kolejka lotniskowa nie stoi w korkach, taxi tak.")
doc += note("Przy późnym wylocie: 3.03 to pierwsza środa miesiąca — darmowy pokaz Muay Thai przed MBK Center, 18:00–20:00.")
doc += f'''<p style="margin:0">&nbsp;</p>
<h2 style="{F}font-size:15pt;margin:10px 0 6px">✅ Do załatwienia wcześniej</h2>
<ul style="{F}font-size:11pt;margin:0">
<li>Wczesny check-in w hotelu na czwartek 11.02</li>
<li>Transport na sobotę 13.02 (lot albo pociąg) + dwa większe auta na lotnisko</li>
<li>Poranny lot powrotny do Bangkoku na poniedziałek 1.03</li>
<li>Stolik na rooftopie na poniedziałek 1.03 wieczór</li>
<li>Bilety na Muay Thai na wtorek 2.03</li>
</ul>
<h2 style="{F}font-size:15pt;margin:14px 0 6px">✂️ Co wypadło przy 2 + 2 dniach</h2>
<ul style="{F}font-size:11pt;margin:0">
<li>Chatuchak — chyba że w sobotę 13.02 wyjeżdżacie dopiero wieczorem</li>
<li>Sobotni wieczór na mieście — zostaje tylko piątek 12.02</li>
<li>Wat Suthat, Ratchada, dzienne Chinatown — świadomie pominięte</li>
</ul>'''

page = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Bangkok — plan na 2 + 2 dni (do skopiowania)</title>
<style>body{{margin:0;background:#e9e9e9;font-family:Arial,sans-serif}}.bar{{position:sticky;top:0;background:#222;color:#fff;padding:10px 14px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;z-index:5}}
.bar button{{font:bold 15px Arial;padding:9px 16px;border:0;border-radius:6px;background:#ffd400;cursor:pointer}}#doc{{background:#fff;max-width:820px;margin:16px auto;padding:28px 32px;box-shadow:0 2px 10px rgba(0,0,0,.2)}}
@media(max-width:700px){{#doc{{margin:0;padding:14px 10px}}}}</style></head><body>
<div class="bar"><button id="cp">📋 Kopiuj całość</button><span id="msg">Kliknij, potem wklej w Google Docs (Ctrl/Cmd+V) — kolory i tabele zostaną.</span></div>
<div id="doc">{doc}</div>
<script>
document.getElementById("cp").addEventListener("click", async () => {{
  const el = document.getElementById("doc"), msg = document.getElementById("msg");
  try {{
    await navigator.clipboard.write([new ClipboardItem({{"text/html": new Blob([el.innerHTML], {{type: "text/html"}}), "text/plain": new Blob([el.innerText], {{type: "text/plain"}})}})]);
    msg.textContent = "✅ Skopiowane — wklej w Google Docs.";
  }} catch (e) {{
    const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r);
    msg.textContent = document.execCommand("copy") ? "✅ Skopiowane — wklej w Google Docs." : "Zaznaczone — naciśnij Ctrl/Cmd+C.";
  }}
}});
</script></body></html>'''
out = Path(__file__).parent / "docs" / "bangkok-doc.html"
out.write_text(page, encoding="utf-8")
print(out)
