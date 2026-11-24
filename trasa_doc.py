"""Buduje docs/trasa-doc.html — podział 16 nocy (13–28.02.2027) między miejsca, do skopiowania do Google Docs."""
from pathlib import Path

F = "font-family:Arial,sans-serif;"
def hl(s, c): return f'<span style="background-color:{c};font-weight:bold">{s}</span>'
Y = lambda s: hl(s, "#fff2a8")
G = lambda s: hl(s, "#d9f2d9")
R = lambda s: hl(s, "#ffd6d6")
TH = "background-color:#333333;color:#ffffff;font-weight:bold;padding:6px 10px;border:1px solid #333333"
C = "padding:7px 10px;border:1px solid #cccccc;vertical-align:top"
def a(u, t): return f'<a href="{u}" style="color:#1155cc">{t}</a>'
def band(title, sub, color):
    return (f'<table style="border-collapse:collapse;width:100%;{F}margin:0"><tr><td style="background-color:{color};padding:12px 14px;border:1px solid {color}">'
            f'<span style="color:#ffffff;font-size:17pt;font-weight:bold;{F}">{title}</span><br><span style="color:#ffffff;font-size:11pt;{F}">{sub}</span></td></tr></table>')
def table(head, rows, widths=None, first_bg=None):
    o = f'<table style="border-collapse:collapse;width:100%;{F}font-size:11pt"><tr>'
    for i, h in enumerate(head):
        w = f";width:{widths[i]}" if widths and widths[i] else ""
        o += f'<td style="{TH}{w}">{h}</td>'
    o += '</tr>'
    for r, row in enumerate(rows):
        bg = "#ffffff" if r % 2 == 0 else "#f7f7f7"
        o += '<tr>'
        for i, cell in enumerate(row):
            b = (first_bg[r] if first_bg else "#eeeeee") if i == 0 else bg
            fw = "font-weight:bold;" if i == 0 else ""
            o += f'<td style="background-color:{b};{fw}{C}">{cell}</td>'
        o += '</tr>'
    return o + '</table>'
def h2(t): return f'<h2 style="{F}font-size:17pt;margin:18px 0 8px;color:#222222">{t}</h2>'
def p(t): return f'<p style="{F}font-size:11pt;margin:6px 0">{t}</p>'
def ul(items): return f'<ul style="{F}font-size:11pt;margin:4px 0">' + "".join(f"<li style=\"margin:3px 0\">{i}</li>" for i in items) + "</ul>"
SP = '<p style="margin:0">&nbsp;</p>'

doc = f'''<h1 style="{F}font-size:26pt;margin:0 0 4px">🗺️ Tajlandia — podział 16 nocy</h1>
<p style="{F}font-size:12pt;color:#555555;margin:0 0 6px">Sobota 13.02 – poniedziałek 1.03.2027 · między dwoma pobytami w Bangkoku (11–12.02 i 1–2.03)</p>
<p style="{F}font-size:10.5pt;margin:0 0 6px">Legenda: {Y("ważne")} &nbsp; {G("za")} &nbsp; {R("przeciw / ryzyko")} &nbsp;·&nbsp; Stan wiedzy: listopad 2026. Rozkładów na luty 2027 jeszcze nie ma.</p>'''

doc += band("WERDYKT", "Bez północy. Dżungla, Krabi, potem Zatoka z Full Moon Party", "#d4006a")
doc += table(["Noce", "Gdzie", "Ile", "Po co"], [
 ("13–14.02", "Khao Sok", "2 noce", "Dżungla i nocleg w domku na jeziorze Cheow Lan"),
 ("15–19.02", "Krabi (Ao Nang / Railay)", "5 nocy", "Baza na Andamany: Railay, wyspy Hong, jednodniówka na Phi Phi i Maya Bay, kajaki, słonie"),
 ("20–24.02", "Koh Phangan", "5 nocy", f"Impreza: {Y('Full Moon Party wstępnie w poniedziałek 22.02')}, bary o zachodzie na zachodnim wybrzeżu"),
 ("25–27.02", "Koh Tao", "3 noce", "Odpoczynek po imprezach: snorkeling, plaża Sairee, taniej niż na Samui"),
 ("28.02", "Koh Samui", "1 noc", "Ostatni wieczór w Chaweng i lotnisko 15 minut od hotelu"),
], ["16%", "26%", "10%", None], ["#dff2e4", "#ffe9d2", "#fde3ef", "#d6effa", "#eee0fb"])
doc += p(f"<b>Razem:</b> 5 miejsc, 4 przeprowadzki, 2 loty (Bangkok → Surat Thani i Samui → Bangkok). Najdłuższy przejazd po drodze to ok. 5 godzin.")
doc += SP

doc += band("PÓŁNOC — odpuszczamy", "Chiang Mai, Pai i Chiang Rai nie mieszczą się w 16 nocach", "#8a2be2")
doc += ul([
 f"{R('Smog.')} 13.02 to już skraj czystego okna. 18.02.2026 pod Chiang Mai zmierzono 71 µg/m³ pyłu PM2,5 (poziom „niezdrowy”), w centrum 34. W połowie lutego 2024 Chiang Mai było 21. najbardziej zanieczyszczonym miastem świata w rankingu IQAir. Rok 2025 był łagodny, więc to loteria.",
 f"{R('Słabe miejsce na imprezę.')} Lokale zamykają się ok. północy–1:00, nie ma klubów stricte gejowskich.",
 f"{R('Koszt.')} 3–4 noce z 16, dodatkowy lot i pół dnia w drodze. Wariant z północą miał najwięcej przeprowadzek (5) i najwięcej godzin w podróży (ok. 25).",
 f"{R('Mało was tam ciągnie.')} Na 152 zapisane rolki o Chiang Mai i Chiang Rai jest osiem, o Krabi czternaście, o Phuket dwanaście.",
 f"{G('Słonie da się zrobić na południu.')} Following Giants w Krabi (bez dotykania, karmienia i kąpieli) — macie o nim rolkę.",
 "Pai: 3 godziny i 762 zakręty w jedną stronę, klimat „chill”, nie impreza. Chiang Rai: 12–14 godzin wycieczki dla dwóch świątyń.",
])
doc += p(f"<b>Kiedy jednak północ:</b> jeśli komuś zależy na świątyniach i kursie gotowania — 3 noce w samym Chiang Mai (13–15.02) kosztem Khao Sok i jednej nocy w Krabi. Rezerwować z darmowym anulowaniem i sprawdzić smog tydzień wcześniej.")
doc += SP

doc += band("MIEJSCE PO MIEJSCU", "Dlaczego tyle nocy i na czym to opieram", "#ff7a00")
doc += table(["Miejsce", "Werdykt", "Uzasadnienie"], [
 ("Khao Sok<br>2 noce", G("ZOSTAJE"), "Pięć waszych rolek i rada z czatu, żeby rezerwować domek na jeziorze dużo wcześniej. Wycieczki na jezioro ruszają rano, więc pierwsza noc jest w wiosce, druga na wodzie. Dobry początek: z Bangkoku to 1 h 15 min lotu i ok. 2 h busem."),
 ("Krabi<br>5 nocy", G("ZOSTAJE — główna baza"), "Najwięcej zapisanych miejsc poza Bangkokiem. Z jednego hotelu zrobicie Railay i Tonsai, wyspy Hong, 4 wyspy, Khao Thong, kajaki w Klong Root i jednodniówkę na Phi Phi. Jeden blog ostrzega, że samo Railay nudzi się po 2–3 dniach — stąd baza w Ao Nang albo 2 noce Railay + 3 Ao Nang."),
 ("Koh Phangan<br>5 nocy", G("ZOSTAJE — tu balujemy"), f"Jedyna wyspa, którą źródła zgodnie nazywają imprezową. Full Moon to plaża Haad Rin, wstęp ok. 200 THB gotówką. {Y('Hotele przy Haad Rin wymagają zwykle 3–5 nocy i drożeją 2–3 razy')} — pięć nocy mieści się w tym minimum, a nocleg w Baan Tai omija najgorsze ceny. Przyjazd w sobotę 20.02 daje jeden wieczór przed „suchą” niedzielą."),
 ("Koh Tao<br>3 noce", Y("OPCJA — bierzemy"), "Minimum według źródeł to 3 noce. Mała wyspa do snorkelingu i odsypiania, z barami przy plaży Sairee. Minusy: bez skutera drogie taksówki, a szybka łódź bywa nazywana „kometą wymiotną”."),
 ("Koh Samui<br>1 noc", Y("TYLKO PRZESIADKA"), "Droga i mocno zabudowana, ale ma lotnisko. Ostatnia noc tutaj zdejmuje ryzyko, że poranny prom z Tao spóźni się na lot."),
 ("Koh Phi Phi", Y("JEDNODNIÓWKA Z KRABI"), "Piękna, ale źródła są zgodne: droga, zatłoczona i „operacyjnie męcząca”. Nomadic Matt pisze wprost, że nadaje się głównie do imprezy i płaci się podwójnie. Maya Bay zobaczycie z łodzi z Krabi."),
 ("Phuket", R("WYPADA"), "Dwanaście waszych rolek, ale wasz własny ranking wysp daje mu 4/10, a blogi piszą „przydatny do transportu, nie do odpoczynku”. Ma najmocniejszą scenę gejowską (Paradise Complex w Patong) — to jedyny realny argument za."),
 ("Koh Lanta", R("WYPADA"), "Najlepsze miejsce na odpoczynek po stronie andamańskiej, ale bez życia nocnego. W tym układzie odpoczynek daje Koh Tao."),
 ("Koh Lipe, Koh Yao Noi,<br>Koh Mook / Kradan", R("ODPUŚCIĆ"), "Lipe to dwa dni samych dojazdów. Yao Noi i wyspy Trang są ciche, bez nocnego życia i z kłopotliwym dojazdem."),
], ["20%", "20%", None], ["#dff2e4", "#ffe9d2", "#fde3ef", "#d6effa", "#eee0fb", "#f1f1f1", "#f1f1f1", "#f1f1f1", "#f1f1f1"])
doc += SP

doc += band("PRZEJAZDY", "Samoloty na długich odcinkach, łodzie między wyspami", "#0088cc")
doc += table(["Kiedy", "Odcinek", "Czym", "Czas"], [
 ("Sob 13.02", "Bangkok → Khao Sok", "Lot do Surat Thani + minivan", "ok. 1 h 15 min + 1,5–2,5 h"),
 ("Pon 15.02", "Khao Sok → Krabi", "Minivan po powrocie z jeziora", "4–5 h"),
 ("Sob 20.02", "Krabi → Koh Phangan", "Jeden bilet Lomprayah: bus + szybki prom", "ok. 5 h"),
 ("Czw 25.02", "Koh Phangan → Koh Tao", "Prom Lomprayah", "1–1,75 h"),
 ("Nd 28.02", "Koh Tao → Koh Samui", "Prom Lomprayah", "1,5–2 h"),
 ("Pon 1.03", "Koh Samui → Bangkok", "Lot Bangkok Airways (jedyny przewoźnik, drożej)", "ok. 1 h 10 min"),
], ["14%", "28%", None, "22%"], ["#eeeeee"] * 6)
doc += p(f"💡 {Y('Przejazd z Krabi na Phangan wypada w sobotę 20.02, nie w niedzielę')} — 21.02 to święto Makha Bucha z zakazem sprzedaży alkoholu, więc sobota jest jedynym wieczorem na rozgrzewkę przed Full Moon.")
doc += p("💡 Tańsza alternatywa na powrót: prom z Samui do Don Sak i lot z Surat Thani tanimi liniami — ale to pół dnia zamiast godziny.")
doc += SP

doc += band("WARIANT B", "Gdyby Full Moon Party nie było warte przebudowy trasy", "#00802b")
doc += table(["Noce", "Gdzie", "Ile"], [
 ("13–14.02", "Khao Sok", "2 noce"),
 ("15–18.02", "Krabi (Railay / Ao Nang)", "4 noce"),
 ("19–22.02", "Koh Lanta", "4 noce"),
 ("23–24.02", "Koh Phi Phi", "2 noce"),
 ("25–28.02", "Phuket", "4 noce"),
], ["20%", None, "16%"], ["#dff2e4", "#ffe9d2", "#d6effa", "#fde3ef", "#eee0fb"])
doc += p(f"{G('Plusy:')} pokrywa prawie wszystkie wasze rolki (Krabi, Phi Phi, Phuket), jedno wybrzeże, najmniej godzin w drodze (ok. 20), tańszy powrót z Phuketu. {R('Minusy:')} bez Full Moon; imprezowo zostają Phi Phi i Patong.")
doc += SP

doc += band("CZEGO NIE UDAŁO SIĘ POTWIERDZIĆ", "Żebyście wiedzieli, gdzie ten plan stoi na słabszych nogach", "#555555")
doc += ul([
 f"{R('Reddit był niedostępny.')} Wyszukiwarka go odrzuca, a strona pokazuje test „udowodnij, że jesteś człowiekiem”. Opinie pochodzą z blogów podróżniczych i forum Fodor's; część blogów zarabia na linkach partnerskich.",
 f"{Y('Data Full Moon Party.')} Jedna strona podaje poniedziałek 22.02 (przesunięcie przez Makha Bucha), dwie inne niedzielę 21.02. Oficjalnego potwierdzenia jeszcze nie ma — sprawdzić przed rezerwacją Phangan.",
 "Terminów imprez Half Moon, Jungle Experience i Waterfall na luty 2027 nikt jeszcze nie opublikował.",
 "Loty są potwierdzone tylko w rozkładzie z listopada 2026; cen w bahtach prawie nie udało się ustalić.",
 "Czy bary na Phangan sprzedają alkohol 21.02 — brak danych.",
 "Scena gejowska na Samui i Phangan: źródła są z lat 2017–2019, lokale mogły się zmienić.",
])
doc += SP + h2("📚 Źródła")
doc += ul([
 a("https://explorertom.com/en/andaman-sea-or-gulf-of-thailand/", "Explorertom — Zatoka czy Andamany, pogoda w lutym"),
 a("https://www.geekyexplorer.com/thailand-island-hopping-guide/", "Geeky Explorer — przewodnik po wyspach (Phi Phi, Railay, Phuket, Lanta)"),
 a("https://www.nomadicmatt.com/travel-blogs/ko-phi-phi/", "Nomadic Matt — krytycznie o Koh Phi Phi"),
 a("https://fullmoonparty-thailand.com/schedule", "Full Moon Party — kalendarz"),
 a("https://kohphangan.com/where-to-stay-full-moon-party/", "Koh Phangan — gdzie spać na Full Moon"),
 a("https://lomprayah.com/time-table", "Lomprayah — rozkład promów"),
 a("https://explorertom.com/en/burning-season-thailand/", "Explorertom — sezon wypalania pól"),
 a("https://destinationthailand.io/chiang-mai-burning-season/", "Destination Thailand — smog w Chiang Mai"),
 a("https://www.fodors.com/community/asia/finalizing-my-itinerary-520557", "Forum Fodor's — ile nocy w Chiang Mai"),
 a("https://www.flightconnections.com/flights-from-bkk-to-urt", "FlightConnections — loty Bangkok → Surat Thani"),
 a("https://www.flightconnections.com/flights-from-bkk-to-usm", "FlightConnections — loty Bangkok ↔ Samui"),
 a("https://shippedaway.com/2-day-cheow-lan-lake-tour/", "Shipped Away — 2 dni na jeziorze Cheow Lan"),
 a("https://thegaypassport.com/destinations/gay-koh-phangan/", "The Gay Passport — Koh Phangan"),
])

page = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Tajlandia — podział 16 nocy (do skopiowania)</title>
<style>body{{margin:0;background:#e9e9e9;font-family:Arial,sans-serif}}.bar{{position:sticky;top:0;background:#222;color:#fff;padding:10px 14px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;z-index:5}}
.bar button{{font:bold 15px Arial;padding:9px 16px;border:0;border-radius:6px;background:#ffd400;cursor:pointer}}#doc{{background:#fff;max-width:860px;margin:16px auto;padding:28px 32px;box-shadow:0 2px 10px rgba(0,0,0,.2)}}
#doc table{{table-layout:auto}}#doc td{{word-break:break-word}}
@media(max-width:700px){{#doc{{margin:0;padding:14px 8px}}#doc td{{font-size:10pt;padding:5px 6px!important}}}}</style></head><body>
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
out = Path(__file__).parent / "docs" / "trasa-doc.html"
out.write_text(page, encoding="utf-8")
print(out)
