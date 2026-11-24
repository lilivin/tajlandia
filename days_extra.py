"""Ręczne uzupełnienia do strony docs/dni.html: ocena obłożenia każdego dnia i miejsca świadomie pominięte (z powodem).
Uruchom: python3 days_extra.py -> days_extra.json (czytane przez feed.py render)."""
import json
from pathlib import Path

# load: full = przepełniony, ok = w sam raz, light = luz (można coś dodać), travel = dzień przejazdu
R = {
 ("bkk", "2027-02-11"): ("ok", "Po kilkunastu godzinach lotu to już jest sporo. Nic nie dokładać; jeśli ktoś padnie, wypada Wat Traimit.", ""),
 ("bkk", "2027-02-12"): ("full", "Cztery zabytki w upale i wyjście wieczorem. Działa tylko przy starcie o 8:15 i przerwie w środku dnia.", "Do wycięcia w razie zmęczenia: Khao San albo Złota Góra."),
 ("bkk", "2027-02-13"): ("travel", "Lot i bus — do Khao Sok docieracie ok. 13:30–15:00.", ""),
 ("ks", "2027-02-13"): ("light", "Zostaje wolne popołudnie i wieczór w wiosce.", "Można dodać: tubing po rzece (ok. 500 THB) albo nocne safari (ok. 700 THB)."),
 ("ks", "2027-02-14"): ("ok", "Program dnia układa operator rejsu; jest czas na kąpiel i kajak przy tratwie.", ""),
 ("ks", "2027-02-15"): ("travel", "Rano jezioro, potem 4–5 godzin w busie. Wieczór w Ao Nang tylko na kolację.", ""),
 ("krabi", "2027-02-15"): ("travel", "Przyjazd ok. 15:00–16:00. Plaża i kolacja, nic więcej.", ""),
 ("krabi", "2027-02-16"): ("full", "Cztery wyspy, Railay i Tonsai w jeden dzień to dużo słońca i łodzi.", "Jeśli zabraknie sił, wypada Tonsai — Railay i Phra Nang zostają."),
 ("krabi", "2027-02-17"): ("ok", "Całodniowa wycieczka z wczesną pobudką; po powrocie ok. 16:00 już tylko kolacja.", ""),
 ("krabi", "2027-02-18"): ("ok", "Kajaki, lunch, punkt widokowy i zachód słońca — z kierowcą bez pośpiechu.", "Tiger Cave Temple (1 260 schodów) zmieści się tylko zamiast kajaków."),
 ("krabi", "2027-02-19"): ("light", "Celowo luźny dzień przed długim przejazdem.", "Można dodać: wyspy Hong albo słonie (Following Giants), albo Tiger Cave Temple rano."),
 ("krabi", "2027-02-20"): ("travel", "Ok. 5 godzin busem i katamaranem.", ""),
 ("kpg", "2027-02-20"): ("light", "Po przeprawie zostaje wieczór: targ w Thong Sala i bary.", "Można dodać: imprezę w dżungli, jeśli będzie tego dnia (terminy nieopublikowane)."),
 ("kpg", "2027-02-21"): ("ok", "Objazd północy wyspy na spokojnie; alkoholu i tak nie kupicie.", "Bottle Beach nie zmieści się razem z objazdem — albo jedno, albo drugie."),
 ("kpg", "2027-02-22"): ("ok", "Dzień celowo pusty, bo noc jest długa. Nic nie dokładać.", ""),
 ("kpg", "2027-02-23"): ("light", "Luz zamierzony — odsypianie.", "Jeśli ktoś ma siłę: wodospad Phaeng albo plaża Haad Son."),
 ("kpg", "2027-02-24"): ("ok", "Rejs do Ang Thong zajmuje 7–8,5 godziny; po nim tylko kolacja.", "Wersja lżejsza: plaże Thong Nai Pan zamiast rejsu."),
 ("kpg", "2027-02-25"): ("travel", "Prom ok. południa, 1–1,75 h.", ""),
 ("tao", "2027-02-25"): ("light", "Popołudnie na plaży i zachód słońca.", "Można dodać: spacer na punkt widokowy nad Sairee albo plażę Sai Nuan."),
 ("tao", "2027-02-26"): ("ok", "Rejs dookoła wyspy z pięcioma przystankami wypełnia dzień.", ""),
 ("tao", "2027-02-27"): ("light", "Wolny dzień: nurkowanie próbne zajmuje pół dnia, plaża i punkt widokowy drugie pół.", "Można dodać: zatokę Tanote albo Chalok Baan Kao."),
 ("tao", "2027-02-28"): ("travel", "Łódź ok. 11:30 → 13:00.", ""),
 ("usm", "2027-02-28"): ("ok", "Jedno popołudnie: Wielki Budda, plaża, kolacja, ostatni wieczór.", "Wodospady i południe wyspy się nie zmieszczą."),
 ("usm", "2027-03-01"): ("travel", "Poranny lot do Bangkoku.", ""),
 ("bkk2", "2027-03-01"): ("ok", "Po porannym locie: muzeum, ulica z jedzeniem i rooftop.", "Jim Thompson wymaga wejścia przed ok. 17:00 — przy opóźnieniu lotu wypada."),
 ("bkk2", "2027-03-02"): ("full", "Zakupy, pamiątki, park i Muay Thai. Najbardziej napchany dzień finału.", "Do wycięcia: Lumphini albo Song Wat (byliście tam 11.02)."),
 ("bkk2", "2027-03-03"): ("travel", "Zależy od godziny lotu do domu.", "Przy wieczornym wylocie: darmowy Muay Thai przed MBK 18:00–20:00 albo Wat Paknam."),
}

def s(name, ll, why, rec, fit=""):
    return {"name": name, "ll": ll, "why": why, "rec": rec, "fit": fit}

SKIPPED = {
 "bkk": [
  s("Chatuchak Weekend Market", [13.7999, 100.5503], "Działa tylko w weekendy, a w Bangkoku jesteście czw–pt i pn–wt.", "rolki z czatu; klasyk przewodników", "Tylko gdyby wylot 13.02 był wieczorem."),
  s("Wat Paknam (wielki Budda, „kosmiczny” sufit)", [13.7217, 100.4703], "Leży na uboczu, po drugiej stronie rzeki — pół dnia z dojazdem.", "rolka z czatu", "3.03 przy wieczornym wylocie."),
  s("ICONSIAM", [13.7266, 100.5103], "Centrum handlowe nad rzeką; zakupy są w planie na finał w innym miejscu.", "rolka z czatu", "Zamiast Platinum/MBK 2.03."),
  s("Mahanakhon SkyWalk", [13.7234, 100.5282], "Płatny taras widokowy; widok z góry daje wam rooftop.", "rolka z czatu", "11.02 po południu zamiast Song Wat."),
  s("Wat Suthat", [13.7510, 100.5012], "Byłaby to piąta świątynia jednego dnia.", "popularne w przewodnikach", "Po drodze na Złotą Górę, 30 min."),
  s("Raan Jay Fai", [13.7526, 100.5047], "Kolejka bywa wielogodzinna i drogo (omlet ok. 170 zł).", "rolka z czatu; gwiazdka Michelin", "12.02 na lunch, jeśli ktoś stanie w kolejce rano."),
  s("Pływające targi (Khlong Lat Mayom)", [13.7616, 100.4155], "Działają w weekendy.", "rolka „5 błędów w Bangkoku”", "Nie w tych datach."),
  s("Ayutthaya", [14.3532, 100.5689], "Całodniowy wypad za miasto.", "rolka z czatu; klasyk przewodników", "Wymaga piątego dnia w Bangkoku."),
  s("Bang Krachao (rowery)", [13.6830, 100.5640], "Pół dnia; przegrywa ze Starym Miastem.", "rolka z czatu", "Wymaga dodatkowego dnia."),
  s("Erawan Museum", [13.6285, 100.5890], "Daleko na południe od centrum.", "rolka z czatu", "Wymaga dodatkowego dnia."),
 ],
 "ks": [
  s("Druga noc na jeziorze", [8.9900, 98.6900], "Dwa razy drożej i odpada łatwa pierwsza noc po locie.", "część blogów poleca 3 dni / 2 noce", "Zamiast nocy w wiosce, z prywatnym busem prosto z lotniska."),
  s("Trekking w dżungli z wioski", [8.9170, 98.5270], "Pół dnia; przyjeżdżacie dopiero po południu.", "popularne w przewodnikach", "Tylko przy locie o 7:25."),
  s("Jaskinia Nam Talu (z jeziora)", [9.0300, 98.6200], "Wymeldowanie z tratwy jest ok. 9:00, więc w poniedziałek się nie zmieści.", "częsty punkt 2-dniowych wycieczek", "Jeśli operator ma ją w programie niedzieli."),
 ],
 "krabi": [
  s("Nocleg na Phi Phi (fire show, punkt widokowy o zachodzie)", [7.7407, 98.7784], "Macie ją jako jednodniówkę; nocleg to przenoszenie się i najdroższe łóżka na trasie.", "źródła zgodnie: wyspa imprezowa", "Z plecakami realne: 1 noc zamiast piątej w Ao Nang (noc 17/18.02)."),
  s("Nocleg na Railay", [8.0118, 98.8375], "Wszystko, co daje Railay, jest w wycieczce we wtorek.", "rolka „po 2 miesiącach”: spać w Railay, nie w Ao Nang", "Z plecakami łatwiejsze niż z walizkami: 1 noc 16/17.02."),
  s("Tiger Cave Temple", [8.1247, 98.9247], "1 260 schodów w upale; w planie tylko „dla ambitnych”.", "popularne w przewodnikach", "19.02 rano albo 18.02 zamiast kajaków."),
  s("Zatoka Phang Nga i Wyspa Jamesa Bonda", [8.2744, 98.5010], "Kolejny cały dzień na łodzi; trzy już macie.", "popularna jednodniówka", "19.02 zamiast Hong."),
  s("Emerald Pool i gorące źródła", [7.9230, 99.2640], "Ok. 1,5 h jazdy w jedną stronę w głąb lądu.", "popularna jednodniówka z Krabi", "19.02 jako dzień luzu."),
  s("Phuket", [7.8847, 98.3880], "Inny kierunek niż Zatoka; wasz ranking daje mu 4/10.", "12 rolek z czatu", "Tylko zamiast Koh Tao (lot Samui → Phuket)."),
  s("Koh Lanta", [7.6130, 99.0310], "Wymaga 3–4 nocy; odpoczynek daje Koh Tao.", "blogi: najlepsza wyspa na odpoczynek", "Tylko w wariancie bez Zatoki."),
  s("Similany", [8.6500, 97.6400], "Wypływa się spod Khao Lak, ok. 2,5 h od Ao Nang.", "3 rolki z czatu", "Realnie nie."),
  s("Koh Mook — Szmaragdowa Jaskinia", [7.3740, 99.2930], "Dostępna z Koh Lanty albo Trang.", "rankingi wysp z rolek", "Tylko w wariancie bez Zatoki."),
 ],
 "kpg": [
  s("Bottle Beach", [9.8000, 100.0300], "Dopływa się tylko łodzią; nie mieści się w dniu z objazdem północy.", "popularne w przewodnikach", "21.02 zamiast objazdu albo 24.02 zamiast Ang Thong."),
  s("Thong Nai Pan", [9.7700, 100.0600], "W planie jest jako zamiennik rejsu do Ang Thong.", "uchodzą za najładniejsze plaże wyspy", "24.02 — jedno z dwojga."),
  s("Wodospad Than Sadet", [9.7560, 100.0700], "Na wschodnim wybrzeżu, słaba droga.", "popularne w przewodnikach", "Razem z Thong Nai Pan."),
  s("Wodospad Phaeng i punkt widokowy Domsila", [9.7370, 99.9990], "W lutym mało wody; nie ma go w żadnym dniu.", "popularne w przewodnikach", "23.02 po południu."),
  s("Haad Son (Secret Beach)", [9.7650, 99.9640], "Objazd 21.02 ma już trzy plaże.", "popularne w przewodnikach", "23.02 zamiast Zen Beach."),
  s("Imprezy w dżungli (Half Moon, Jungle Experience)", [9.7200, 100.0350], "Terminów na luty 2027 jeszcze nie ma.", "źródła: obok Full Moon najlepsze imprezy wyspy", "20.02 albo 24.02, jeśli trafią w daty."),
 ],
 "tao": [
  s("Kurs nurkowy PADI", [10.0980, 99.8270], "Trwa 3–4 dni i zjada cały pobyt.", "rolka z czatu: Koh Tao na PADI", "Zostaje nurkowanie próbne 27.02."),
  s("Zatoka Tanote", [10.0840, 99.8480], "Po drugiej stronie wyspy, taksówką po stromej drodze.", "popularne w przewodnikach", "27.02 zamiast Freedom Beach."),
  s("Chalok Baan Kao", [10.0640, 99.8260], "Spokojniejsza zatoka na południu; wieczorem wymaga taksówki.", "druga baza w przewodnikach", "27.02 po południu."),
  s("Plaża Sai Nuan", [10.0730, 99.8170], "Dojście pieszo ok. 30–40 min z Mae Haad.", "popularne w przewodnikach", "25.02 po południu."),
 ],
 "usm": [
  s("Wodospady Na Muang", [9.4660, 99.9870], "Południe wyspy, a macie jedno popołudnie.", "popularne w przewodnikach", "Nie przy jednej nocy."),
  s("Lamai i skały Hin Ta Hin Yai", [9.4520, 100.0390], "Jak wyżej.", "popularne w przewodnikach", "Nie przy jednej nocy."),
  s("Targ w Fisherman's Village", [9.5600, 100.0270], "Działa w piątki; jesteście w niedzielę.", "popularne w przewodnikach", "Kolacja tam jest możliwa, bez targu."),
  s("Wat Plai Laem", [9.5710, 100.0680], "Tuż obok Wielkiego Buddy, ale to kolejna świątynia.", "popularne w przewodnikach", "28.02 razem z Wielkim Buddą, +30 min."),
 ],
 "bkk2": [
  s("Mahasan (tajski steakhouse)", [13.7040, 100.5280], "Wymaga rezerwacji i dojazdu na południe miasta.", "rolka z czatu", "Kolacja 1.03 zamiast Banthat Thong."),
  s("Wattana Panich (zupa gotowana od 1974)", [13.7400, 100.5850], "Ekkamai, nie po drodze z Siam.", "rolka z czatu; Michelin", "Lunch 2.03 zamiast Terminal 21."),
  s("Rung Rueang (pork noodles)", [13.7260, 100.5690], "Objazd na Sukhumvit 26.", "2 rolki z czatu; Michelin", "Lunch 1.03, jeśli śpicie przy Sukhumvit."),
  s("Kluby na Thonglor", [13.7330, 100.5810], "Poniedziałek i wtorek to słabe dni na kluby.", "2 rolki z rankingami klubów", "Nie w tych datach."),
  s("Rejs tramwajem wodnym o zachodzie (16 THB)", [13.7190, 100.5130], "Nie wpisany w żaden dzień.", "rolka z czatu", "2.03 po Song Wat zamiast taksówki do Lumphini."),
  s("Nai Lert Park", [13.7470, 100.5480], "Mały park przy BTS Ploenchit.", "rolka z czatu", "2.03 zamiast Lumphini."),
 ],
}

out = {"ratings": [{"stop": k[0], "date": k[1], "load": v[0], "note": v[1], "add": v[2]} for k, v in R.items()], "skipped": SKIPPED}
Path(__file__).with_name("days_extra.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(R), "ocen;", sum(len(v) for v in SKIPPED.values()), "pominiętych miejsc")
