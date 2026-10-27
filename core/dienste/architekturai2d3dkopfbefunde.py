# -*- coding: utf-8 -*-
"""Architekturai2d3dkopfbefunde — die festgehaltenen Befunde der Kopf-KI auf Hilfe → Architektur → 2d-3d-AI (aus `Architekturai2d3dkopfnetz` abgeteilt am 27.10.2026,
die Datei stand bei 298 Zeilen). Je Befund Datum, Quelle (Skript oder Lauf) und was gemessen wurde."""

__all__ = ['Architekturai2d3dkopfbefunde']


class Architekturai2d3dkopfbefunde:
    #: (Datum, Quelle, Befund) — festgehalten
    BEFUNDE = (
        ('26.10.2026', 'kopfnetz_wurfprobe.py, 12 Köpfe', 'Generator 0,23 s je Kopf (Rendering vorn 34 ms, MediaPipe 64 ms, je Profil Rendering 19 ms + Profillinie 46 ms); alle Erkenner fanden '
         'alle 12 Köpfe; MediaPipe am Rendering gegen die Landmarkentabelle 1,6–5,0 % des Augenabstands.'),
        ('26.10.2026', 'kopfnetz_luecke.py', 'Edgars KopfKI-Kopf im Generator gegen die Fotos: ohne Lageabzug vorn 5,1 %, im Profil 4.jpg bis 33 % am Kinn — Ursache die Kopflage '
         '(vorn 15,6°, 3.jpg 2,5°, 4.jpg −12,5° Nicken). Mit Lageabzug vorn 2,6 %, Profile 1–4 % je Zeile, am Kinn (Bart) bis 7 %.'),
        ('26.10.2026', 'Korrektur', '„KopfKI 0,91 % gegen Face Transfer 1,16 %“ verglich die Landmarkentabelle der KopfKI mit MediaPipe an den Face-Transfer-Bildern — zweierlei. Mit Erkennern '
         'auf beiden Seiten (Median vorn) liegen Face Transfer 0,85 % und die KopfKI (nur Fotos) 1,02 % gleichauf; der Vergleich mit gleichem Verfahren steht in der Tabelle unten.'),
        ('26.10.2026', 'kopfnetz_vergleich.py, kopf_ausser_h.py', 'Warum die alte KopfKI (24.10. mittags) besser war als Face Transfer 2 (vorn 1,06 gegen 1,16 %, Profile 0,34 / 0,59 gegen '
         '0,49 / 0,73 %): mehrere Perspektiven, Erkenner auf beiden Seiten — UND ihr Start edgar_knopf (Mesh3D-AI aus dem Tripo-Netz). Von ihm blieben 27 Regler außerhalb der 523 Kopfregler '
         'stehen, die größten Matt_figure_ctrl_Character 0,561 und BaseMasculine_figure_ctrl_Character 0,206 (wirken auf Kopf UND Körper, darum nicht in H). Der Start allein misst '
         '2,72 / 1,21 / 1,51 %; derselbe Abgleich vom neutralen Start nur 1,98 / 0,98 / 1,36 %. Der Abgleich selbst nutzte nur Fotos — der gute Start kam aus Tripo.'),
        ('26.10.2026', 'kopfki_wahrheit_rendering.py OlesiaWalk … eigen', 'Abgleich an Fotos MIT Eigenreglern, an einer Figur mit bekanntem Kopf (OlesiaWalk, ferner Start ohne Tripo): '
         'Rendering ↔ Foto 2,28 → 1,10 % (der WAHRE Kopf misst 1,33 %), Profil 0,92 → 0,32 % (wahr 0,38 %), Prüfprofil 1,15 → 0,55 % — aber die Kopfform läuft von der Wahrheit WEG: '
         'Landmarken 2,79 → 4,24 mm, Gesicht vorn 2,83 → 3,49 mm (nur Daz-Regler: 4,09 / 3,22 mm). Mehr Regler passen die Fotos besser als der wahre Kopf — unter dem Rauschen der Erkenner '
         'heißt „besser am Foto“ nicht „ähnlicher“. Darum lernt die Kopf-KI die Anfasser gegen die WAHRE Form gewürfelter Köpfe und wird an Exporten mit Wahrheit gemessen (mm).'),
        ('26.10.2026', 'Fehler in kopfnetz_edgar.py', 'Die Merkmale von Edgars Fotos wurden gerechnet, BEVOR der Generator die Vorlage der Lage setzt — im Training mit Lageabzug, an Edgars '
         'Fotos ohne (Lauf 09.45: Generator gegen Fotos vorn 4,93 %, Profil links 11,78 % statt 2,6 % und 1–4 %). Die Spalte „KopfKI-Prüfung an Edgars Fotos“ der Läufe bis dahin misst '
         'das Netz also mit falschem Eingang; nachgemessen mit kopfnetz_wahrheit.py (Datei edgar_nachgemessen.json je Lauf, Zeilen „Merkmal mit Lageabzug“ in der Vergleichstabelle).'),
        ('26.10.2026', 'kopfnetz_wahrheit.py, kopfnetz_vergleich.py', 'Kopf-KI mit Eigenreglern (Lauf 10.21, 2.000 Köpfe, 523 Daz-Regler + 282 Anfasser): Prüfköpfe 3,72 → 3,00 mm '
         '(ohne Eigenregler 2,78 → 1,93 mm). An den 6 Exporten mit Wahrheit, Landmarken im Mittel: Edgars Kopf als Antwort 3,80 mm, Netz ohne Eigenregler 3,48 mm, mit Eigenreglern 3,65 mm — '
         'beide Netze kaum besser als die Mitte, um die gewürfelt wurde. An Edgar (Merkmal mit Lageabzug) vorn 1,65 bzw. 1,55 %, Profile 1,09 / 1,39 bzw. 1,07 / 1,40 % — nicht besser '
         'als Face Transfer 2 (1,16 · 0,49 / 0,73 %). Die Eigenregler allein machen die KI nicht besser.'),
        ('26.10.2026', 'Edgar: „Eine KI kann doch einen Trainingssatz perfekt nachbilden“; kopf_darstellbar.py', 'Das Netz bildet nicht einmal seinen Trainingssatz nach: Training 2,10 '
         'bzw. 2,84 mm ≈ Prüfköpfe 1,93 bzw. 3,00 mm — Unteranpassung, kein Datenmangel (der Vorschlag „20.000 Köpfe“ war falsch). Und der alte KopfKI-Kopf liegt nicht im Ausgang: '
         'nur die 523 Kopfregler, der Rest von der Mitte → bestenfalls 1,43 mm daneben (Matt_figure_ctrl_Character allein 0,52 mm). Konzept: Docu/konzepte/2026-10-26_kopfki-nachbilden-konzept.md.'),
        ('26.10.2026', 'kopfnetz_nachbilden.py, kopfnetz_vergleich.py', 'Das Netz bildet das Ergebnis der alten KopfKI aus Edgars Fotos nach (ein Paar, Ausgang alle 1.323 Regler, '
         '2.000 Schritte, 52 s): Regler höchstens 0,0058 daneben, 51 von 1.323 über 0,001; an Edgar vorn 1,07 / 0,99 %, Profile 0,33 / 0,61 % — die alte KopfKI 1,06 / 0,96 · 0,34 / 0,59 %. '
         'Erster Versuch (10.42, Verlust gemittelt statt summiert, 500 Schritte): Form 0,08 mm, aber Regler bis 0,145 daneben, vorn 1,16 %. Das Ziel trägt Tripo (Start edgar_knopf) — '
         'Nachweis, nicht das Netz der Kette.'),
        ('26.10.2026', 'kopfnetz_in_job.py, Kette ab einpassen, Stand kopfnetz1', 'Der Kopf des nachbildenden Netzes in der Jobfigur EdgarTrip (Edgar: „Zeige mir das Ergebnis im Job“ — '
         '„warum hat die Jobfigur einen anderen Körper und Kopf-Anfasser?? Fixe das!“): Ausgabe der Stufe „kopf“ = Kopfregler, Charakterregler und Kopfmorph aus dem Netz (0,28 mm neben '
         'dessen Kopf, vorher 6,77 mm), Körper neu eingepasst, die Kopf-Anfasser von gesicht1 (an den alten Kopf gepasst) entfallen. Abnahme der Jobseite: 53 grün / 47 rot '
         '(gesicht1: 44 / 56), Kopfzellen 5 grün / 3 rot (gesicht1: 2 / 6); Kopf Haut 1.jpg aber 2,3 → 7,8 mm (die Kopflage aus gesicht1 ist mit der neuen Einpassung weg). '
         'Sicherungen: kopf/nurfotos_kopf|nurfotos_einpassen.vor_kopfnetz_kopfnetz1.*'),
        ('26.10.2026', 'kopfmass_gegenprobe.py, ein Prozess auf der GPU, 16 s', 'Messwerk am Kopf (Schritt 1 der Empfehlung). Nullprobe, die Figur gegen ihre eigene in torch gerasterte '
         'Maske: zuerst 27–39 mm je Foto (Strahlen liefen bis 120 mm in Hals und Schulter); mit „Umrisspunkt höchstens 3 mm neben dem eigenen Umriss“ noch 4,7–9,9 mm '
         '(Reglermass.figur nimmt den äußersten Käfigpunkt im Band ±25 mm, an gekrümmten Umrissen 8–12 mm außerhalb); mit dem Schnitt Strahl × Käfigkante 0,20–0,30 mm '
         '(höchstens 0,68). Verstellter Kopf (alle 282 Anfasser +0,3 cm): gegen die eigene Maske 0,24–0,28 mm, gegen die unverstellte 9,1–15,6 mm, alle Zellen rot, auf 0,1 mm wie '
         'der Versatz Maske gegen Maske. Haarprobe (Saum oben am Kopf), Median je Haarstrahl: 10 mm Haar → Abweichung −9,9 bis −11,0 mm, Haarregel 0,0; 25 mm → −24,8 bis '
         '−27,3 mm, Haarregel 4,8–7,3 mm (über 5 bei schrägen Strahlen). Echt, Jobkopf kopfnetz1 gegen Edgars Fotos mit Haarregel und Grenze 2 mm: 1.jpg 7,17 mm im Mittel, 5 von 8 '
         'Zellen rot; 4.jpg 3,83 mm, 2 von 8; 2.jpg 6,49 mm, 4 von 8; 3.jpg 8,56 mm, 3 von 8 — 14 von 32 rot (Hautregel 8,7–10,5 mm). Gezählt werden je Foto nur 80–163 von 495 '
         'Kopfstrahlen (die übrigen liegen in der Ansicht nicht am Umriss), rund die Hälfte davon im Haar; 3.jpg KO-03/KO-04 liegt die Figur 27–38 mm innerhalb.'),
        ('26.10.2026', 'kopf_einpassen.py kopfein1, abnahme_vergleich.py', 'Kopfeinpassung (282 Anfasser + Kopflage je Foto, 300 Schritte, 154 s auf der GPU) vom Stand ohne Tripo, '
         'Gelenkzentren aus der Formung (gegen die gebaute Figur 0,003 mm; mit doppeltem Bodenabzug zuerst 42,17 mm, zentren_probe.py). Kopfmaß: 23 von 28 Zellen rot, 11,68 mm → '
         '14 von 28, 3,61 mm (behalten Schritt 125; spätere Schritte bis 2,11 mm, aber unter 90 % der Strahlen). 1.jpg wurde schlechter (2,50 → 5,65 mm): der Umriss allein drehte den '
         'Kopf dort um 8,6° und schob ihn 17 mm. Im Job (Stand kopfein1, Kette ab kameras): Abnahme 47 grün / 53 rot (gesicht1, derselbe Körper: 44 / 56) — keine Zelle rot geworden, '
         'grün geworden Kopf Haut 2.jpg, Hals Haut 2.jpg, Hals Haar 2.jpg. Kopf Haut 2,2 / 1,5 / 3,6 mm grün (1.jpg, 2.jpg, 3.jpg), 4.jpg 7,8 mm rot; Kopf Haar alle rot (6,2–10,0 mm).'),
        ('26.10.2026', 'kopf_einpassen.py kopfein2–kopfein4, abnahme_vergleich.py', 'kopfein2 (Kopflage gedämpft, Lernrate fallend): Verlust stieg unter fallender Rate (4,39 → 7,16), '
         'weil je Schritt andere Strahlen zählten (300 → 340); Abnahme 45 / 55. kopfein3 (Strahlen des Starts fest): Kopfmaß 2,80 mm, aber Abnahme 43 / 57, Kopf Haut 1.jpg 6,5 mm '
         'rot — das Kopfmaß allein trifft die Abnahme nicht. kopfein4 (dazu ViTPose-Gesichtspunkte auf allen 4 Fotos, Gesichtsanker): die Kopflage lag weit daneben — Gesichtspunkte '
         '4.jpg 19,5 → 3,5 mm, 3.jpg 5,9 → 1,5, 1.jpg 2,1 → 1,8, 2.jpg (5 Punkte) 38 → 5 mm; Abnahme 46 / 54, grün geworden Kopf Haut 4.jpg (4,8 mm, zum ersten Mal ohne Tripo), '
         'Kopf Haar 2.jpg, Hals Haut 4.jpg; rot geworden Kopf Haut 1.jpg (2,3 → 6,7 mm). Rest nach kopfein4: die Ohren — in 1.jpg liegen beide Ohrkanten im Foto ~12 mm weiter '
         'bildrechts als an der Figur (links −12/−16, rechts +10/+12 mm), das Gesicht passt auf 1,8 mm; in 2.jpg steht das linke Ohr 16–19 mm zu weit ab, in 1.jpg 12–16 mm zu wenig. '
         'Vorder- und Rückansicht widersprechen sich am selben Ohr — keine Form löst das; offen, ob Kopflage/Kamera einer Ansicht oder das Haar am Ohr.'),
        ('26.10.2026', 'Edgar, Korrektur', 'kopfein1–kopfein4 waren Fits an EdgarTrip, Überanpassung an einen Job, keine KI (Grundsatz oben): sie stellten die Parameter '
         'des Jobs ein, kein Gewicht wurde gelernt. Ihre Zahlen sagen nichts darüber, wie die Kopf-KI an einem neuen Kopf abschneidet. Was davon bleibt, ist Messwerk: Kopfmaß, '
         'Gesichtsanker, die Haarregel und der Befund, dass die Abnahme Kopf Haar am Haar der Kettenstufe „haar“ misst, nicht am Kopfnetz.'),
        ('26.10.2026', 'fotomesslinien_gegenprobe.py, Grundfigur, GPU', 'Gegenprobe des neuen Messwerks Fotomesslinien (je Strahl der Kopf-Eigenregler und Ansicht: Abstand Ziel '
         '− Startfigur, gefunden, Haar): Wahrheit = Start −0,22 bis −0,35 mm (höchstens 1,1); Kopf 2 % größer +1,6 bis +2,0 mm; 10 mm Haar: Haarstrahlen +10,1 bis +12,1 mm '
         'und als Haar erkannt, Hautstrahlen −0,2 mm; nur die gewürfelte Kopflage (±6°, ±8 mm) 5–8,6 mm — die KI muss die Kopflage mitlernen. 0,85 s je Kopf und 4 Ansichten, '
         'mit größeren Stapeln 0,2 s.'),
        ('26.10.2026', 'kopfki_fotos_lauf.py kopfki1, Stufe A, GPU', '6.000 gewürfelte Köpfe, 400 ungesehene Prüffälle, 20.000 Schritte: Prüffälle 6,48 mm „Netz sagt Start“ → '
         '5,33 mm bei Schritt 1.000 → 5,51 mm bei 20.000, Training 1,48 mm; Kopflage 3,39 → 2,65 (Grad bzw. mm). Das Netz lernt auswendig statt allgemein — zu wenig Fälle. '
         'Stufe B (EdgarTrip als Trainingsjob) brach ab: CUDA out of memory, die Karte teilten drei Läufe. Kopfmaß EdgarTrip nach Netz A (3.jpg nicht im Eingang): 1.jpg 3,35, '
         '4.jpg 4,81, 2.jpg 9,31, 3.jpg 21,57 mm. Nichts übernommen, im Job steht weiter kopfein4.'),
        ('26.10.2026', 'schaedeldecke_probe.py, kopfein4, CPU', 'Edgar: „warum gibt es keine Messpunkte und Konturen an der Schädeldecke?“ — In 4.jpg fielen die Punkte 4–8 von '
         'KO-15 (Schädel seitlich) aus der Wertung: der Rand im Rendering (Haarschale) lag 20,0–29,4 mm über dem Hautpunkt, die Abnahme wertete nur bis NAHE_MM = 20 mm (gedacht für '
         'Punkte, die gar nicht am Umriss liegen). Seither entscheidet der Rand der Figur ohne Haar (Figurmaske, wie Kopfreglermass): 4.jpg 12 statt 5 von 13 Punkten, 3.jpg 10 statt 9.'),
        ('26.10.2026', 'kopfki_jobs_lauf.py kopfki2, Stufe B, GPU', 'Netz A aus kopfki1, 4 Trainingsjobs, 1 Testjob, Schritt 1.000 von 1.500: Trainingsjobs gegen die Wahrheit '
         '7,81 → 2,87 mm, Testjob Damira 5,85 → 6,55 mm (Kopfmaß 9,55 → 12,28) — das Netz lernt die wenigen Jobs auswendig. Auf Edgars Wort abgebrochen, um die Gesichtspunkte '
         'einzubauen; nichts übernommen.'),
        ('26.10.2026', 'kopfki3_ablauf.py (gesichtspunkte_gegenprobe, daten_nachruesten), GPU', 'Gegenprobe der Gesichtspunkte (Fotogesichtspunkte, 478 MediaPipe-Punkte): ohne '
         'Abweichung 0,00 mm (360 zugewandte Punkte), mit 1 mm Erkennerrauschen 1,24 mm, Nase 5 mm zur Seite → 5,13 mm an 23 Nasenpunkten, übrige 0,56 mm. An Fotos (Foto − Figur in '
         'Kamera und Haltung der Kette): EdgarTrip 1.jpg Start 5,69 mm; gegen die WAHRHEIT der Exporte Allyne 3,11, Amala 6,06, Damira 2,45, Fabrice 8,45 (x −6,25), Kin 3,52 mm — '
         'Erkenner, Kamera und Kopflage der Kette zusammen; Vermutung: der größte Teil ist Kopflage (gleichgerichtete Verschiebung), die die KI mitlernt. Nachrüsten statt neu '
         'würfeln: Saat 12 nachgespielt gegen voll gewürfelt bitgleich (Messlinien, Regler, Wahrheit 0, Gesichtsblock 3,8e-6), Saat 11 in 260 s statt 45 min.'),
        ('26.10.2026', 'kopfki_jobs_lauf.py kopfki3, GPU', 'Stufe A (gewürfelt) Prüffälle 6,48 → 4,67 mm (kopfki1 5,33). Stufe B, 6 Trainings- und 2 Testjobs, 1.500 Schritte: '
         'Gesichtspunkte der Trainingsjobs 6,97 → 1,07 mm, ihr Abstand zur Wahrheit dabei 5,70 → 5,99 mm; Testjobs 6,54 → 6,87 mm. An allen 7 Exporten liegt der Kopf der KI weiter '
         'von der Wahrheit als der Startkopf (G9formung, z. B. Allyne 4,34 → 10,02 mm): die KI drückt die Messzahl, nicht den Formfehler. Übernommen als kopfki3.'),
        ('26.10.2026', 'gesichtspunkte_zerlegung.py, GPU', 'Zerlegung Foto − Figur der Gesichtspunkte an 5 Exporten (Foto von vorn), beste 2D-Ähnlichkeit abgezogen: am wahren Kopf bleiben '
         '1,78–4,32 mm, am Startkopf 1,44–3,76 mm — an 4 von 5 liegt der wahre Kopf NICHT näher an den Fotopunkten (nur Kin 2,31 gegen 3,03). Am größten Iris 2,8–10,5, Brauen '
         '2,2–5,6, Gesichtsoval 2,3–7,1 mm. Dazu die Lage: der wahre Kopf in Kamera und Haltung der Kette bis 6,4 mm versetzt und 13 % zu groß (Fabrice). Feste Netzstellen gegen '
         'MediaPipe am Foto taugen so nicht als Verlust — wie am 24.10. für die Landmarkentabelle gemessen. Seither auf der Jobseite drei Karten: Foto ↔ Netzstellen, '
         'Rendering ↔ Netzstellen (der Fehler), Foto ↔ Rendering.'),
        ('26.10.2026', 'haut_haar_lage_probe.py, alle Jobs mit Haut/Haar aus der Kette', 'Zwei Kopflagen je Foto: die Seite rendert in Kamera + Haltung der Einpassung, die Haut holt '
         'ihre Farbe in KopfKI.Kopflagen (schwach perspektivisch, eigener Maßstab). An den Exporten stimmen beide überein (Maßstab 0,997–1,002, Median 0,5–3,9 mm), an EdgarTrip nicht '
         '(1.jpg 3,8 mm, Maßstab 0,930; 4.jpg 22,8 mm; 3.jpg 24,7 mm, Maßstab 0,875) — die Fotomerkmale liegen im Rendering um diesen Abstand neben der Geometrie. Haar: am Startkopf '
         'geschnitten und nur verschoben, sticht der Schädel an 25,3 % der Schalenpunkte durch (Exporte 1,4–9,5 %). Haar am fertigen Kopf in Kopflagen geschnitten: Durchstich 8,0 %, '
         'aber eine Haube, Abnahme Kopf 16,26 → 18,58 mm — zurückgenommen (nurfotos_haar.AM_FERTIGEN_KOPF). Erst die Kopflage der Seite richtig, dann Haut und Haar in ihr.'),
        ('26.10.2026', 'exportwahrheit.py, exportnull_probe.py, vitpose_kopf_null.py', 'Wahre Kamera der Exporte nachgebaut (wie modellansichten.js, Ränder 0,2–3 px): ViTPose am Foto gegen '
         'ViTPose am Rendering des WAHREN Kopfs misst vorn 1,5–2,5 mm, im Profil 1,9–3,9 mm — die Null dieses Erkenners. Ursache der schiefen Profile: der Profil-ICP von Kopflagen '
         '(freie 2D-Drehung, Haar im Umriss) kippte den Kopf um 20–36°.'),
        ('27.10.2026', 'kopflagen_runde.ps1 zweistart, kopflagen_gegenprobe.py', 'Kopflagen mit Schätzer (KopfKI/kopflageschaetzer.py, ViTPose an Foto und Rendering, zwei Startlagen, im '
         'Profil die Gesichtslinie): an den Exporten gegen die wahre Kamera bei allen 21 Fotos ≤ alt, Median 40,0 → 5,0 mm; offen Laura rechts 41,4 mm (ViTPose findet am Foto keine '
         'Punkte), Fabrice links/rechts 26,5/17,9, Amala links 17,5 mm. Eingeschaltet (Kopflagen.SCHAETZER).'),
        ('27.10.2026', 'fotovitpunkte_probe.py, 20 Exportfotos', 'ViTPose als Verlust der Kopf-KI in jeder Ansicht (KoerperKI_Fotos/fotovitpunkte.py, Kopfpunkte 0–4 und 40–90): Null '
         '2,4 mm, 10 mm Versatz → 10,0 mm. Dabei gefunden: der Trainingsjob EdgarTrip bekam bis kopfki4 keine Fotos — ohne Gesichtsblock im Eingang und ohne MediaPipe im Verlust.'),
        ('27.10.2026', 'kopfki5, Kette ab kameras, Abnahme; abnahme_gruppenversatz.py', 'Erstes Netz mit ViTPose im Verlust: Abnahme 63 → 70 von 118 Zellen grün, Kopf 16/36 → 23/40, '
         'Median Kopf 11,1 → 10,75 mm. 4.jpg besser (Augen 26–28 → 8–13 mm, Nase 28 → 11 mm), 1.jpg schlechter (Augen ~3 → 7–8 mm, Profil KO-14 11,2 → 23,6, Schädel seitlich KO-15 '
         '4,8 → 15,3 mm). An 1.jpg ist das gemalte Gesicht gestreckt, nicht verschoben: Augen und Brauen 7–8 mm zu hoch, Mund 2,8 mm zu tief, Maßstab Rendering/Foto 1,058. '
         'Haut gegen Seite Maßstab 0,89–0,91, Haar: der Schädel sticht an 42 % der Schalenpunkte durch. Kopf des Trainings = Kopf der Kette (kopfmodell_echt_probe.py: RMS 0,96 mm, '
         'Maßstab 0,999) — daran liegt es nicht.'),
        ('27.10.2026', 'kopfki_vit_unabhaengig.py, kopffotojob_vitneu_probe.py', 'Ursache: die ViTPose-Anker wurden einmal an der Startfigur gesetzt und wanderten mit der Fläche — das '
         'Netz lernte Formen, die die Anker auf die Fotopunkte schieben, nicht die Merkmale. Training gemessen 1,3 / 0,9 / 1,0 mm (1.jpg / 4.jpg / 3.jpg), ViTPose NEU auf dem neuen '
         'Kopf (Grundhaut, Lage der Seite) 3,7 / 5,2 / 4,5 mm, Maßstab Rendering/Foto 1,06–1,09, Brauen 5–10 mm zu hoch; an der Startfigur messen beide gleich (5,2/5,0, 16,0/15,8, '
         '8,1/7,7 mm). Die Gegenprobe hatte nur Null und starren Versatz geprüft, keine Formänderung. Seither setzt der Trainingsjob die Anker bei jedem Aufruf neu (Kopffotojob.VIT_NEU, '
         'wie MediaPipe an der Figur): am Kopf von kopfki5 fest 0,91 / 0,64 / 0,72 mm, neu 4,16 / 4,90 / 3,70 mm (Median); 1,1 s je Verlust.'),
        ('27.10.2026', 'haltung_vk_probe.py, kopf_starr_probe.py', 'Zweiter Fehler jeder Übernahme der Kopf-KI: ihre Haltung (Knochenorte p) gilt für die Gelenkzentren der STARTfigur, '
         'gebaut wird die Figur mit den neuen Kopfreglern — die Zentren der Gesichtsknochen wandern dabei bis 54,6 mm (r_cheeklower). Gehäutet wird d·(x − c) + p, also standen auf der Seite '
         'und in der Abnahme Unterlippe 12,8 mm, Wangen 11,3 mm, Unterkiefer 8,5 mm, Ohren 6,7 mm neben der Bewegung des Kopfknochens, in allen Fotos gleich. Mit den Startzentren folgt die '
         'Haltung der Vorwärtskinematik (Median 0,06 mm), mit den neuen nicht (57,5 mm). Behoben: KopfKI/haltungumzug.py zieht die Knochenorte über die Elternfolge auf die neuen Zentren '
         'um und behält gewollte Abweichungen (Versatz der Kopflage); kopfki5 danach: Rest nur noch der Kopfversatz 7–11 mm.'),
        ('27.10.2026', 'mp_profil_cpu.py (CPU)', 'MediaPipe im Profil: der Gesichtsfinder findet das Gesicht (in den Kopffenstern 4.jpg 0,926, 3.jpg 0,882; vorn 0,951) — verworfen wird es '
         'erst vom Punktnetz (Anwesenheit Foto 0,371 / 0,606, Seitenbild 0,007 / 0,000; FaceLandmarker verlangt 0,5). Die Punkte liegen im Foto plausibel, streuen aber bei 10 % '
         'verschobenem Rechteck um 6–10 mm (vorn 4–6 mm), Foto ↔ Seitenbild in 3.jpg 48–109 mm: fürs Profil keine Messung. Von vorn (Anwesenheit 1,0) stehen seither die dichten '
         'MediaPipe-Gruppen auch in Feld 3 (Lider 16 und Iris 5 je Auge, Nasenflügel und -löcher 17, Lippen 40, Kinn 12).'),
        ('27.10.2026', 'insightface_profil_probe.py (CPU), abnahme_gesicht106.py', 'Lösung fürs Profil: insightface (buffalo_l, lag auf der Platte: SCRFD det_10g + 2d106det) — SCRFD findet '
         'das Gesicht im Profil mit 0,79–0,81 (Seitenbild 0,77–0,80), die 106 Punkte streuen bei 10 % verschobenem Kasten im Profilfoto um 1,1 mm (Median), am Seitenbild um 3,4 mm, und '
         'liegen an Nasenflügelfalte, Nasenloch, Lidern des sichtbaren Auges, Brauen, Mund und Kinn. Eingebaut als Messung der Abnahme in jeder Ansicht mit Gesicht (KoerperKI_Fotos/'
         'gesichtspunkte106.py, im Profil nur die sichtbare Gesichtshälfte und die Mitte), gerechnet in python10 auf der CPU, 8,5 s für drei Fotos.'),
        ('27.10.2026', 'mpvergleich_port.py, mpvergleich_original.py, mpvergleich_drehung.py', 'Gegenprobe MediapipeTorch ↔ MediaPipe selbst (python10, 0.10.32, dieselbe '
         'face_landmarker.task) auf 18 Kopfausschnitten (1/4/3.jpg, Foto und Seitenbild, 2/3/5 × Gesicht): Fundwert gleich auf 0,001, Anwesenheit auf 0,03, Punkte im Foto 0,1–1 px — der '
         'Port ist nicht die Ursache. Das Punktnetz selbst ist im Profil unzuverlässig: vorn bleibt die Anwesenheit über ±30° Drehung und drei Ausschnittgrößen bei 1,00, im Profilfoto '
         'springt sie bei 10° Drehung zwischen 0,00 und 1,00 (3.jpg: 0° 1,00, ±20° 0,00), am Profil-Seitenbild bleibt sie ≈ 0. Google dazu (GitHub google-ai-edge/mediapipe #3510, '
         '2022): Grenze des Modells, trainiert auf Gesichtern von vorn, keine Verbesserung geplant.'),
        ('27.10.2026', 'if_gegenprobe_original.py (python10), if_gegenprobe_torch.py', 'insightface in torch (A:\\3DTools\\InsightfaceTorch: eigener ONNX-Leser, Operatoren als torch, Ablauf '
         'nach dem Quelltext von insightface): Netz gegen Netz höchstens 1e-5 (Karte 3e-3), Fundwert ±0,004, Punkte im Mittel 0,1–0,5 px auf 18 Kopfausschnitten (ein Rendering 3,6 px), '
         '50 ms je Ausschnitt auf der Karte. SCRFD findet das Gesicht auf allen 18 Ausschnitten (0,53–0,88), vorn und im Profil, Foto und Seitenbild. Erkenner der Gesichtspunkte seit '
         'heute einstellbar (Einstellungen → 2d-3d-AI, Vorgabe insightface; MediaPipe bleibt wählbar) — Kopf-KI (Eingang, Verlust) und Feld 3 der Abnahme folgen der Einstellung; '
         'insightface misst vorn, links und rechts, MediaPipe nur vorn.'),
        ('27.10.2026', 'gesichtsnetzstellen_bauen.py', 'Feste Netzstellen der 106 insightface-Punkte (Grundfigur gerendert, Punkt aufs vorderste Dreieck): von vorn gebaut lagen sie im '
         'Profil 5–7 mm neben dem Erkenner (Nasenloch bis 12 mm) — darum je Fach gebaut (0°, 90°, 270°): in der Bauansicht 0–0,4 mm, bei 15° anderer Drehung vorn 2,2–2,7 mm und im '
         'Profil 2,4–3,2 mm, bei 10° Neigung 1,7–2,0 mm; die Kontur (ein Umriss) bei ±15° 6 mm und mehr, sie zählt nur von vorn. Für 2 mm zu grob: am Job misst die Kopf-KI seit '
         'kopfki7 den Erkenner auch auf dem Rendering der Figur (Karte 3), die Netzstellen tragen nur noch den Gradienten und die gewürfelten Fälle.'),
        ('27.10.2026', 'Seitenbilder kopfki5 angesehen (kopf/mpvergleich/profil_seiten_x3.png)', 'Korrektur: ein „zweites Gesicht auf der Schläfe“ gibt es nicht — in einem '
         'Vorschaubild mit 400 px falsch gelesen. Kaputt sind im Profil die Hautflecken im Haar (Schädel durch die Haarschale), zerrissene Flächen hinter dem Ohr und die Haut in einer '
         'anderen Lage als die Seite (Median 6–9 mm, bis 29 mm, Maßstab 0,89; seitenlage_probe.py).'),
        ('27.10.2026', 'kopfki7 (abgebrochen in Stufe B ohne3, Schritt 500), kopffotojob_insightface_probe.py, if_fenstersuche_probe.py', 'kopfki7 (insightface vorn und Profil) '
         'machte den Trainingsjob in Stufe B schlechter: Kopfmaß 7,64 → 10,40 → 13,48 mm, Gesicht 9,80 mm → bei Schritt 250 in keinem Foto gefunden → 54,52 mm, ViTPose 11,59 → 10,67 mm; '
         '1.222 s je 250 Schritte statt 259 s (kopfki6). Gemessen: der Finder sieht das Gesicht auf dem Rendering bis ±30–45° Verdrehung (Wert 0,70–0,85), ab etwa 60° nicht mehr; '
         'dann suchte `punkte` 170–193 Fenster ab, 4,7–11,9 s je Aufruf, in 6 von 6 Fällen ohne Fund. Und fiel das Gesicht (oder ein ViTPose-Anker) aus, fiel sein Term aus dem '
         'Verlust — die KI konnte der Messung ausweichen. Geschlossen: ohne Fund zählen die festen Netzstellen bzw. die Anker der Startfigur (`Fotogesichtspunkte.mm`, '
         '`Kopffotojob._vit_ankern`), keine Fenstersuche auf dem Rendering; Gegenprobe kopffotojob_loch_probe.py: Term bleibt (Verlust 24,7 → 38,6 / 134 / 187), 1,5 s je Schritt.'),
        ('27.10.2026', 'kopffotojob_gradient_probe.py (Netz A von kopfki7, je Term Gradient gegen Differenz ±2°)', 'Das Kopfmaß hatte am Trainingsjob keinen Gradienten für die '
         'Kopflage: in 21 von 26 Stellungen falsches Vorzeichen, Betrag ~0, obwohl der Wert sich um 0,05–0,34 mm je Grad ändert (Gesicht 2, ViTPose 1 von 26). Ursache: der Strahl '
         'beginnt an der Figur und wandert mit dem Kopf, den Fotorand bestimmt `Reglermass.rand` ohne Gradient. Seit `Kopfreglermass.fotorand` ist der Fotorand ein fester Bildpunkt, '
         'auf den Strahl projiziert (gleicher Wert): falsch nur noch 3 von 26, alle am Minimum (Differenz 0,004–0,07). Bis kopfki7 lernte die Kopf-KI die Lage am Job also nur aus '
         'Gesicht und ViTPose.'),
        ('27.10.2026', 'gesicht_wahrheit_if_probe.py (5 Exporte, insightface auf Foto und Rendering)', 'Von vorn liegt die Messung an der Wahrheit nach der besten 2D-Ähnlichkeit '
         'bei 2,53 mm, am Start bei 3,06 mm; näher an der Wahrheit an 3 von 5 Fotos (MediaPipe 26.10.: 1,97 / 2,15 mm, ebenfalls 3 von 5). Haut des Exports oder Grundhaut: '
         'gleich (±0,05 mm). Die Profilzeilen dieser Probe taugen nicht: die gelesene Haltung der Exporte steht in den Seitenansichten bis 46° verdreht (if_profil_bilder.py) — '
         'nicht der Erkenner.'),
        ('27.10.2026', 'kopfki8 (kopfki_fotos_lauf.py, kopf/kopfki8.log), gegenprobe3_lage_probe.py', 'Nach den drei behobenen Messfehlern macht Stufe B den Job besser: '
         'alle 4 Fotos Kopfmaß 6,90 → 1,16 mm (je Foto 0,33 / 0,85 / 0,28 / 3,35), Gesicht 11,43 → 5,70, ViTPose 12,69 → 3,84 mm; Prüffälle bleiben 4,7 mm. Gegenprobe ohne 3.jpg: '
         '20,68 mm (kopfki5 69,01). Getrennt nach Form und Lage (nur die 5 Lagewerte von 3.jpg nachgeführt, Form des Netzes fest): Netz A (nur gewürfelte Köpfe) 1,16 mm, Gesicht 1,62; '
         'Netz ohne3 nach Stufe B 8,67 mm, Gesicht 9,83. Stufe B mit EINEM Trainingsjob verbiegt also die Form auf die drei gezeigten Fotos — die Form von Netz A überträgt sich auf das '
         'ungesehene Foto, nur ihre Kopflage am echten Foto stimmt nicht (Netz A am Job: Kopfmaß 6,90 mm mit den eigenen Lagen). Abnahme kopfki8: 45 grün / 55 rot; Gesicht '
         'Foto ↔ Rendering (insightface) im Mittel 7,77 / 18,95 / 10,01 mm (1.jpg / 4.jpg / 3.jpg) — im Profil weit über der Verlustmessung (Gesicht 5,70 mm), Ursache offen.'),
    )
