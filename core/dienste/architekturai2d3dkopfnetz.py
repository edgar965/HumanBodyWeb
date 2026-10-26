# -*- coding: utf-8 -*-
"""Architekturai2d3dkopfnetz — Abschnitt „Kopf-KI“ von Hilfe → Architektur → 2d-3d-AI (26.10.2026, Edgar: „aktualisiere … damit wir das nicht wieder vergessen“).

Was es für den Kopf schon gibt (nicht neu bauen), woraus die Kopf-KI besteht, und wie ihre Läufe stehen. Die Läufe liest die Seite beim Aufruf von der Platte
(`3DObjects/ai2d3d/_kopfnetz/<lauf>/lauf.json`, Vergleich `ProjektTemp/_wegwerf/ai2d3d/kopf/kopfnetz_vergleich.json`); festgehaltene Messungen nennen Datum und Quelle.
"""
import json
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Architekturai2d3dkopfnetz']


class Architekturai2d3dkopfnetz:
    #: (Name, was es ist, Art) — Edgar 26.10.2026: „du hast doch die KopfKI schon, die das alles macht, warum baust du jetzt alles neu???“
    VORHANDEN = (
        ('KopfKI (A:\\3dTools\\KopfKI, 24.10.2026)', 'Die Kopfregler (523) in Runden an das Frontfoto (478 MediaPipe-Punkte) und die Profile (Profillinie), Erkenner auf Foto UND Rendering '
         '(Kopfbild); dazu Haut aus den Fotos, Bart, Haarschale, Ohren (SAM 3). Stufe „kopf“ der Kette (nurfotos_kopf.py). Mehrere Perspektiven — der Vorteil gegen Face Transfer.',
         'Einpassung, kein trainiertes Netz'),
        ('Daz Face Transfer 2', 'Die KI von Daz (geschlossen, nur der Kopf, EIN Frontfoto). Am 24.10.2026 per Skript in Daz Studio an EdgarTrip 1.jpg gerechnet '
         '(ProjektTemp/_wegwerf/ai2d3d/facetransfer/), nur als Vergleich gemessen — kein Nachbau.', 'fremde KI, Vergleich'),
        ('Kopfnetz von Mesh3D-AI (mesh3dai_kopfnetz_*, 21.10.2026)', 'Trainiertes Netz: Eingang ein 3D-Netz (Abstand je Kopfpunkt), Ausgang Δ 523 Kopfregler, trainiert auf gewürfelten '
         'Köpfen (Kopfwurf). Allein an den Tripo-Jobs schlechter als der Formkopf (Architektur Mesh3D-AI).', 'trainiertes Netz, Eingang Netz statt Fotos'),
        ('Einpassungen an der Jobseite (26.10.2026)', 'Reglermass (die Ampel als Rechnung, 101/101 Zellen gleich), Ampeleinpassung, Gesichtseinpassung (Kopflage + Kopf-Eigenregler an 1.jpg: '
         'Gesichtspunkte von vorn 6,2 → 1,9 mm, Lauf gesicht1) — Feinschliff NACH dem Netz.', 'Einpassung'),
        ('Eigenregler (Genesis9/eigenregler.py, eigenform.py, 25.10.2026)', 'Eigene, frei formbare Regler im Bereich „Eigen“; am Kopf 18: Kopf vorne, Schädel vorne/seitlich, Mund, Nase, '
         'Augen, Brauen, Ohren (je beide/links/rechts, Ohren auch von vorn) und Profil. Je Regler eine feste Grundform (eigen:regler_…) und die Anfasserwerte JE FIGUR '
         '(eigenform:regler_…:<Anfasser>:a|b), linear an der Grundfigur — lernbar und messbar wie ein Daz-Regler. Die 523 Daz-Kopfregler bilden nicht jeden Kopf, die Anfasser formen frei.',
         'Regler: Stellgrößen für KopfKI und Kopf-KI'),
    )
    #: (Klasse, Datei, Aufgabe)
    BAUSTEINE = (
        ('Kopfmerkmal', 'KopfKI/kopfmerkmal.py', 'Eingang des Netzes: 468 MediaPipe-Punkte vorn + Profillinien beider Seiten, Lage des Kopfs abgezogen — für Fotos und Generator DIESELBE Rechnung'),
        ('Kopfgenerator', 'KopfKI/kopfgenerator.py', 'Trainingsköpfe nur aus Teilen der KopfKI: Regler gewürfelt um einen Kopf (zuerst Edgars KopfKI-Kopf) und ganz gewürfelt, gerendert mit '
         'Kopfbild von vorn und aus beiden Profilen, darauf MediaPipe und Profillinie'),
        ('Kopfnetz', 'KopfKI/kopfnetz.py', 'Merkmal → 523 Kopfregler (Bauart wie das Kopfnetz von Mesh3D-AI), Start beim Kopf, um den gewürfelt wird'),
        ('Kopfnetztraining', 'KopfKI/kopfnetztraining.py', 'Verlust: Kopfform (5.101 Kopfpunkte) nach Abzug von Lage und Maßstab, mm; Prüfköpfe, die nie trainiert werden'),
        ('Lauf', 'ProjektTemp/_wegwerf/ai2d3d/kopfnetz_edgar.py', 'EIN Prozess, alles auf der Karte; auf die Platte nur netz.pt und lauf.json (Edgar: „alles auf GPU, RAM und in einem Prozess“)'),
        ('Kopfnachbildung', 'KopfKI/kopfnachbildung.py', 'Das Netz lernt gegebene Paare Merkmal → Regler nach, ohne Generator; Ausgang ALLE Regler des Kopfmodells (Edgar 26.10.2026: '
         '„Erstmal reproduziere das Ergebnis der Kopf-KI von Edgar“). Lauf: ProjektTemp/_wegwerf/ai2d3d/kopfnetz_nachbilden.py'),
        ('Kopfeigenbasis', 'KopfKI/kopfeigenbasis.py', 'Die Anfasser aller Kopf-Eigenregler als lineare Spalten an den 5.101 Kopfpunkten (Rechnung von Eigenbasisalle, nur Gruppe Kopf)'),
        ('Figurmaske', 'KopfKI/figurmaske.py', 'Maske der Figur in einer Fotokamera, in torch auf der Karte gerastert (kein Renderer) — für „Umrisspunkt am Umriss“ und die Gegenprobe'),
        ('Kopfreglermass', 'KopfKI/kopfreglermass.py', 'Das Maß der Kopf-KI: Umrisse der Kopf-Eigenregler gegen den Rand der Person im Foto; Haut- und Haarregel (0–20 mm), Grenze 2 mm, '
         'Figurrand als Schnitt Strahl × Käfigkante (differenzierbar); Gegenprobe: ProjektTemp/_wegwerf/ai2d3d/kopfmass_gegenprobe.py'),
        ('Kopfeinpassung', 'KopfKI/kopfeinpassung.py', 'Der Kopf auf allen 4 Fotos zugleich gegen das Kopfmaß: 282 Kopf-Anfasser (gemeinsam) und Kopflage je Foto, Körper und Kameras '
         'fest; Maske je Schritt neu gerastert. NICHT der Weg zur KI: ein Fit an einen Job (Grundsatz oben). Brauchbar bleibt die Rechnung (Maske, Strahlen, Gesichtsanker '
         'differenzierbar in einem Prozess) als Messwerk für Training und Prüfung.'),
        ('Fotomesslinien', 'KoerperKI_Fotos/fotomesslinien.py', 'Das Messwerk der KI aus Fotos (Eingang und Verlust): je Strahl der Kopf-Eigenregler und Ansicht Abstand Ziel − '
         'Startfigur in mm, gefunden, Haar; aus_wahrheit (gewürfelte Köpfe) und aus_job (Fotos) mit DERSELBEN Rechnung. Form der Messlinien mit Mesh3D-AI abgestimmt'),
        ('Fotowurf', 'KoerperKI_Fotos/fotowurf.py', 'Gewürfelte Fotobedingungen für Fälle mit Wahrheit: Kameras in vier Fächern, Haar 0–20 mm als Schicht auf der Kopfhaut, '
         'Kopflage je Ansicht'),
        ('Kopfkaefigwurf', 'KopfKI/kopfkaefigwurf.py', 'Gewürfelte Köpfe mit Wahrheit als ganzer Käfig der Grundfigur (Kopfwurf + Grundcharaktere + 282 Anfasser); Startfigur = '
         'dieselben Regler ohne Kopfregler und Anfasser, wie am Job'),
        ('Kopffototraining', 'KopfKI/kopffototraining.py', 'Training der Gewichte: Eingang Fotomesslinien + Startregler, Ausgang Kopfregler + Anfasser, Verlust Form nach Lage (mm, '
         'Größe zählt), Ansichten zufällig weg. Lauf: ProjektTemp/_wegwerf/ai2d3d/kopfki_fotos_training.py'),
        ('Kopfbildeigenangleich', 'KopfKI/kopfbildeigenangleich.py', 'Die KopfKI mit Rendering, dazu die Anfasser der Kopf-Eigenregler frei (Edgar 26.10.2026: „du hast die neuen Eigen '
         'Regler“); Ergebnis als eigenform:-Werte in den Reglern der Figur. Lauf: ProjektTemp/_wegwerf/ai2d3d/kopf_eigen_angleich.py'),
    )
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
    )
    #: Grundsatz über dem Plan (26.10.2026 nachmittags) — Regel: ~/.claude/rules/ki-allgemein-statt-job.md
    GRUNDSATZ = ('Edgar: „Warum überfüllst du speziell diesen Job und machst keine allgemeine KI? Ich möchte, dass du nur die Messmethoden änderst, aber nicht an diesem Job '
                 'etwas anpasst. Das soll für alle Köpfe, die danach kommen, trainiert sein.“ — „Das machst du immer wieder falsch!!!“ — und dazu: „du sollst eine ganz '
                 'normale KI trainieren. Dabei werden die Gewichte der neuronalen Netze angepasst nach den trainierten Jobs. Die Messmethoden müssen perfekt abgestimmt sein, '
                 'damit die KI trainiert ist. Die Messmethoden zeigen, wie weit das gewünschte Ergebnis des Trainingjobs noch von der Eingabe entfernt ist. … Insofern sind die '
                 'Trainingsjobs nicht nur Prüffälle, sondern es sind halt Trainingsjobs, wonach die KI ihre Gewichte anpasst.“',
                 'Eine normale KI: das Netz lernt seine GEWICHTE gemeinsam über alle Trainingsjobs — EdgarTrip, die Exporte mit Wahrheit und gewürfelte Köpfe mit bekannter Wahrheit. '
                 'Die Messmethoden (Fotomesslinien: Strahlen der Kopf-Eigenregler, Haut-/Haarregel, Gesichtspunkte) sind Eingang UND Verlust: sie messen, wie weit das gewünschte '
                 'Ergebnis eines Trainingsjobs (seine Fotos bzw. die Wahrheit) noch von der Eingabe bzw. vom Ergebnis des Netzes entfernt ist — darum müssen sie stimmen, mit Gegenprobe, '
                 'allgemein und ohne Ausnahmen für einen Job. Geprüft wird an Zurückgehaltenem (Gegenprobe ohne 3.jpg, ungesehene Köpfe). In den Job kommt die Ausgabe der trainierten '
                 'KI, nie ein Fit seiner Parameter: kopfein1–kopfein4 stellten 282 Anfasser und die Kopflage direkt an den 4 Fotos ein — kein Gewicht gelernt, Überanpassung, kein Weg '
                 'zur KI.')
    #: (Punkt, Inhalt, Herkunft) — der Plan vom 26.10.2026 (Edgar: „schreibe diesen Plan auf die Hilfe seite, damit der nicht verloren geht“), ergänzt um die Punkte des alten
    #: Auftrags EdgarTrip, die ihm fehlten, und Edgars Entscheidungen dazu; „offen“ = fehlt noch
    PLAN = (
        ('Eingang', 'Für jeden Kopf-Eigenregler und jedes der 4 Fotos die Abweichung Vorlage (Rand der Person im Foto) gegen Ergebnis (Rand der Figur) je Strahl in mm, dazu '
         '„gemessen ja/nein“ — aus Reglermass (KoerperKI_Fotos/reglermass.py), für den aktuellen Kopf.', 'Plan'),
        ('Ausgang', 'Die Form gemeinsam für alle Fotos: Korrektur der 282 Kopf-Anfasser und der 523 Kopfregler. Dazu die Kopflage JE FOTO als eigene Größe — sonst schluckt die Form '
         'die Fehler der Lage (Stand kopfnetz1: Kopf Haut 1.jpg 2,3 → 7,8 mm, weil die Kopflage aus gesicht1 wegfiel). Körper, Kameras und Charakterregler bleiben stehen.',
         'Plan + alter Auftrag („Form gemeinsam, Haltung je Foto“)'),
        ('Verlust', 'Derselbe Vergleich nach der Korrektur (Reglermass ist in den Figurpunkten differenzierbar). Augen, Mund und Nase liegen von vorn nicht am Rand der Person, dort lässt '
         'Reglerumrisse die Linie offen — für diese drei die Gesichtspunkte (ViTPose, MediaPipe) als zweiter Vergleich, wie in der Gesichtseinpassung.', 'Plan'),
        ('Haare und Bart', 'Am Schädel oben und hinten ist der Rand im Foto das Haar, nicht die Haut (Haare 0–20 mm, eigene Schicht), am Kinn der Bart. Dort zählt ein Strahl nur als „Figur '
         'liegt 0–20 mm innerhalb“, sonst bläst die KI den Schädel ins Haar auf. Reglermass misst bisher gegen den Rand der ganzen Person.', 'alter Auftrag'),
        ('Ziel', 'Kopf ≤ 2 mm auf allen 4 Fotos, Grenzen werden nicht geändert. Reglermass und Reglerumrisse zählen bisher gegen rand_mm = 10 mm (Koerperabnahme.GRENZEN) — „grün“ '
         'dort ist nicht die Grenze des Auftrags.', 'alter Auftrag'),
        ('Messwerk zuerst', 'Vor dem Training die Gegenprobe des Messwerks am Kopf: an Exporten mit bekanntem Kopf (OlesiaWalk, Matt1, …) muss der wahre Kopf besser messen als ein '
         'verstellter, ein sabotierter Kopf muss rot werden. Das Ergebnis wird auch dort in mm gegen die Wahrheit gemessen — mehr Regler passten die Fotos schon einmal besser als der '
         'wahre Kopf und liefen in der Form von ihm weg (Befund oben, OlesiaWalk: Landmarken 2,79 → 4,24 mm).', 'alter Auftrag („Messwerk mit Gegenprobe“)'),
        ('Training', 'Eine normale KI (Grundsatz oben): die Gewichte lernen über ALLE Trainingsjobs. (1) Gewürfelte Köpfe mit Wahrheit (KopfKI/kopfkaefigwurf.py: Kopfregler, '
         'Charaktere, Anfasser) unter gewürfelten Fotobedingungen (KoerperKI_Fotos/fotowurf.py: Kameras vorn/links/hinten/rechts, Haar 0–20 mm, Kopflage) — Verlust die Form in mm '
         'gegen die Wahrheit; (2) die Fotojobs (EdgarTrip, Exporte mit Wahrheit) — Verlust die Messmethode nach der Korrektur des Netzes (Kopfmaß an den Fotos, differenzierbar), '
         'bei den Exporten dazu die Wahrheit. Eingang die Fotomesslinien (Ziel gegen Startfigur) + Regler der Startfigur, Ausgang Kopfregler, Anfasser und (folgt) Kopflage je '
         'Ansicht, in Runden. Zurückgehalten zur Prüfung: 3.jpg von EdgarTrip und ungesehene Köpfe. Gemeinsame Regler-KI mit Mesh3D-AI (Docu/konzepte/'
         '2026-10-26_mesh3dai-ki-neue-regler-konzept.md: 2d-3d-AI baut Fotomesslinien, Form der Messlinien abgestimmt).', 'Edgar 26.10.2026'),
        ('Start', 'Nicht mehr „Edgar mit seinen 4 Fotos, keine neuen Köpfe, keine neuen Trainingsdaten“ — EdgarTrip ist EIN Trainingsjob unter vielen (Punkt „Training“). Gilt '
         'weiter: die Startfigur im Job ohne Tripo. Kopf OHNE Tripo (Edgar 26.10.2026: „Tripo soll nicht als start sein“): der Kettenkopf vor '
         'kopfnetz1 (kopf/nurfotos_kopf.vor_kopfnetz_kopfnetz1.json, KopfKI nur aus Fotos, Start BaseMasculine 1,0, kein Matt/Ty; vorn 1,98 %, Profile 0,98 / 1,36 %) — derselbe Kopf wie '
         'lauf6_1743 (194 von 195 Kopfreglern gleich). Nicht kopfnetz1: dessen Kopf trägt den Tripo-Start edgar_knopf (Matt 0,56, BaseMasculine 0,21).', 'Plan + Edgar'),
        ('Mehrere KIs', 'Edgar: „wir haben mehrere KIs, die eine soll die anderen nicht kaputt machen“ — „der Kopf ist eingefroren, wenn die Körper-KI was ändert“. Jede KI schreibt nur '
         'ihre Teile: die Kopf-KI Kopfregler, Kopf-Anfasser und Kopflage je Foto; die Körper-KI den Rest, der Kopf samt Lage bleibt dort fest. Nach jeder KI die ganze Abnahme vorher/'
         'nachher — keine Zelle der anderen KI darf schlechter werden (Stand kopfnetz1: die neue Körpereinpassung nahm die Kopflage aus gesicht1 mit, Kopf Haut 1.jpg 2,3 → 7,8 mm).',
         'Edgar'),
        ('Eingefroren', 'f aus EXIF, Größe 1,85 m, Kameras und Körper der Einpassung — die Kopf-KI ändert nur den Kopf. Rangfolge Kopf > Kamera/Haltung > Umriss Haut.', 'alter Auftrag'),
        ('Gegenprobe', 'Am Ende dieselbe KI ohne 3.jpg, gemessen an 3.jpg (so lief schon der Kopf lauf6_1743: Ziele 1.jpg + 3.jpg, Prüfung 4.jpg).', 'alter Auftrag'),
        ('Rechnung', 'Alles in EINEM Prozess auf der GPU und im RAM (Edgar: „alles in einem Prozess auf der GPU“ — „warum nutzt du noch pyrender??“): kein Renderer in der Rechnung '
         '(kein pyrender, kein OpenGL, keine Seitenbilder aus dem Chrome) — die Maske der Figur rastert KopfKI/figurmaske.py in torch mit den Fotokameras; Segmente aus der Ablage, '
         'keine Zwischendateien, auf die Platte nur das Ergebnis. Die Seitenbilder bleiben nur für die Abnahme.', 'Edgar'),
        ('Läufe', 'Je Lauf eine Änderung, Stand mit Namen sichern; bis 3 Kettenläufe je Stufe; GPU nur über die Gpusperre.', 'alter Auftrag'),
        ('Zeigen', 'Nach JEDEM Training das Ergebnis als benannter Stand in den Job (Edgar: „bau nach jedem Training das Ergebnis in /2d-3d-AI/test/edgartrip/ hinein, damit ich das '
         'sehen kann!!“) — das Ergebnis der trainierten KI an EdgarTrip, kein Fit (kopf_einpassen.py ist dafür nicht der Weg). Kette ab kameras, Seitenbilder im Chrome, Abnahme.',
         'Edgar'),
        ('Bericht', 'Am Stufenende: Abnahmetabelle vorher/nachher, ein Vergleichsbild je Foto, was offen ist.', 'alter Auftrag'),
        ('Haarmaske', 'Angeschlossen (KopfKI/kopfreglermass.py): Fotorand in haar | bart der Fotosegmentablage → Haarregel 0–20 mm; Haarprobe bestanden (Befund oben).',
         'erledigt'),
        ('Messwerk am Kopf', 'Gegenprobe mit Edgars Kameras, die Figur in torch gerastert: Nullprobe 0,20–0,30 mm, verstellter Kopf überall rot und auf 0,1 mm wie der Versatz Maske '
         'gegen Maske (Befund oben, kopfmass_gegenprobe.py).', 'erledigt'),
        ('Startfigur', 'Ohne Bau: die Gelenkzentren aus der Formung der Regler (bauplan, wie mesh3dai_kinematik), Hautgewichte hängen nicht an der Form — gegen die gebaute Figur '
         '0,003 mm (zentren_probe.py).', 'erledigt'),
        ('Trainingspaare', 'Gewürfelte Köpfe: Wahrheit als Maske in gewürfelten Kameras gerastert (Figurmaske, torch), Haar als Schicht; Eingang die Fotomesslinien gegen die '
         'Startfigur, Ziel die Wahrheit — gebaut (Gegenprobe fotomesslinien_gegenprobe.py). Fotojobs mit der Messmethode als Verlust (KopfKI/kopffotojob.py) — gebaut, Lauf '
         'kopfki1 (EdgarTrip).', 'erledigt'),
        ('Jobliste', 'Edgar 26.10.2026: „du kannst auch die anderen Jobs aus der Jobliste als Trainings oder Testjobs nehmen“ — „diese alle (34 Stück)“. Jeder Job braucht dafür '
         'Kameras und Haltung aus der Kette (kopf bis einpassen: jobs_vorbereiten.py, nurfotos_kette.py --bis einpassen). Rollen (kopfki_jobs_lauf.py ROLLEN): Exporte mit Wahrheit '
         'sechs im Training (Verlust Kopfmaß + Wahrheit), drei zurückgehalten (Damira, Kin, Matt — Prüfung in mm gegen die Wahrheit); EdgarTrip ohne 3.jpg und die echten Fotos '
         'echter Menschen (Königin 1/2/Bühne, N1, W1) im Training; nur Test: Ed2010 (dieselbe Person wie EdgarTrip), Ed als Kind, Bühnenfiguren mit Masken (Triadisch), Gemälde, '
         'Zeichnung. Nicht verwendbar: Randy, Zauberer, Vadim Meller (kein Geschlecht oder Winkel in der job.json), Ed2026 (4 von 8 Fotos fehlen auf der Platte). Die Wahrheit der '
         'Exporte formt G9formung: Kopf gegen Grundfigur 1,65–8,07 mm (wahrheit_kopf_probe.py).', 'läuft'),
        ('Gesichtspunkte', 'Die 478 Punkte von MediaPipe (MediapipeTorch, auf der Karte, im selben Prozess) im Foto von vorn gegen dieselben Punkte an der Figur (Käfigdreieck + '
         'Baryzentrik): Eingang der KI (KoerperKI_Fotos/fotogesichtspunkte.py, Block hinter den Messlinien) und Verlust im Fotojob; gewürfelte Köpfe mit 1 mm Rauschen. Auf der Jobseite '
         'als Karte „Gesichtspunkte“ mit Maßen (Brauen: Dicke, Bogen, Länge; Augen, Iris, Nase, Mund, Lippen, Gesicht) und Gruppen (KoerperKI_Fotos/gesichtsmesspunkte.py). Ohren kennt '
         'MediaPipe nicht — dort bleiben die Umrissstrahlen KO-12/13. Lauf kopfki3: feste Netzstellen messen falsch (Befund) — nächster Schritt MediaPipe auf dem Rendering.', 'läuft'),
        ('Jobkopf', 'Im Job steht seit 13:30 der Fit kopfein4 (Überanpassung, Grundsatz oben); er wird durch das erste Ergebnis der trainierten Kopf-KI ersetzt. Zurücksetzen auf '
         'den Stand davor (Sicherungen kopf/…vor_kopfein_kopfein1.*) nur auf Edgars Wort.', 'offen'),
    )
    #: Kurzfassung und Empfehlung zum Plan (26.10.2026, Edgar: „kurzfassung und empfehlung“ — „schreib das rein in die Hilfe seite und fang an“)
    KURZ = ('Eine normale KI: ihre Gewichte lernen über alle Trainingsjobs (EdgarTrip, Exporte mit Wahrheit, gewürfelte Köpfe), die Messmethoden sind Eingang und Verlust '
            '(Grundsatz). Startfigur im Job ohne Tripo: der Kettenkopf aus der '
            'KopfKI nur mit Fotos (wie lauf6_1743), vorn 1,98 %, Profile 0,98 / 1,36 %. Die Kopf-KI nimmt den Vergleich Vorlage gegen Ergebnis je '
            'Kopf-Eigenregler und Foto und gibt Kopfregler, 282 Kopf-Anfasser und Kopflage je Foto aus; Ziel Kopf ≤ 2 mm auf allen 4 Fotos, Gegenprobe ohne 3.jpg. Jede KI schreibt nur '
            'ihre Teile, keine Zelle der anderen wird schlechter. Gerechnet wird in einem Prozess auf der GPU und im RAM, ohne Renderer. Erledigt (Schritt 1, 26.10.2026 12:16): Haare/Bart an den Strahlen, Grenze 2 mm, '
            'Gegenprobe des Messwerks (Nullprobe 0,2–0,3 mm). Es fehlen: Kopflage fest in der Körpereinpassung, die gebaute Startfigur ohne Tripo, Trainingspaare.')
    EMPFEHLUNG = (
        ('Messwerk zuerst, ohne KI', 'Haare und Bart an die Strahlen, 2-mm-Grenze am Kopf, Gegenprobe mit verstelltem Kopf (mit Edgars Kameras gerendert, die Messung muss die '
         'Verstellung in mm wiederfinden). Bisher sind wir jedes Mal am Maß gescheitert — eine KI, die gegen ein falsches Maß lernt, wird nur schneller falsch.'),
        ('Zuständigkeit festmachen', 'Die Körpereinpassung übernimmt Kopf und Kopflage fest; nach jeder Stufe die ganze Abnahme vorher/nachher. Sonst wiederholt sich kopfnetz1 '
         '(Kopf Haut 1.jpg 2,3 → 7,8 mm).'),
        ('Dann die Kopf-KI', 'Eine normale KI, Gewichte gelernt über alle Trainingsjobs: gewürfelte Köpfe (Verlust Form gegen Wahrheit) und die Fotojobs (Verlust die Messmethode '
         'nach der Korrektur), Eingang die Fotomesslinien. Ergebnis im Job = Vorwärtslauf des Netzes. Fertig bei Kopf ≤ 2 mm auf allen 4 Fotos und bestandener Gegenprobe ohne '
         '3.jpg (3.jpg nicht im Training).'),
    )
    REIHENFOLGE = (
        'Die Leiter (Docu/konzepte/2026-10-26_kopfki-nachbilden-konzept.md): L0 Ausgang mit allen Reglern mit Kopfwirkung (Charaktere, Anfasser) · L1 einen Kopf überanpassen · '
        'L2 alle 2.000 nachbilden (Eingang normiert, Ausgang nicht geklemmt, ohne Rauschen) · L3 den alten KopfKI-Kopf nachbilden (nur Wegwerf-Netz, Ziel trägt Tripo) · '
        'L4 derselbe Kopf aus Edgars echten Fotos = Domänenlücke in mm · L5 Lücke schließen · L6 Wahrheit an den Exporten',
        'Messlatte mit Wahrheit: die Exporte (OlesiaWalk, Matt1, …), nie im Training — Kopfform in mm gegen die Wahrheit; Fotomaße allein liegen schon unter dem Rauschen der Erkenner '
        '(Befund oben). Der Abgleich an Fotos (KopfKI, auch mit Eigenreglern) nur noch, wo er an der Wahrheit nicht schadet',
        'Edgar perfekt: Kopf-KI an Edgar (Generator um seinen KopfKI-Kopf), auf seine echten Fotos, gemessen wie Face Transfer — dann die Kette damit und die Seite (Kopf vorne/seitlich)',
        'allgemein: mehr ganz gewürfelte Köpfe, andere Häute, dann die Exporte mit Wahrheit — seit 26.10.2026 teils im Training, teils zurückgehalten (Punkt „Jobliste“)',
        'danach der Körper (Weg B, Konzept Docu/konzepte/2026-10-26_fotonetz-konzept.md)',
    )

    @classmethod
    def laeufe(cls):
        ordner = Path(settings.TOOLS_ROOT) / '3DObjects' / 'ai2d3d' / '_kopfnetz'
        aus = []
        for datei in sorted(ordner.glob('*/lauf.json'), reverse=True):
            try:
                d = json.loads(datei.read_text(encoding='utf-8'))
            except (OSError, ValueError) as fehler:
                logger.warning('Kopfnetz-Lauf %s nicht lesbar: %s', datei, fehler)
                continue
            tr, gen = d.get('training') or {}, d.get('generator') or {}
            letzte = (tr.get('verlauf') or [{}])[-1]
            aus.append({'name': datei.parent.name, 'gerechnet': d.get('gerechnet'), 'proben': (gen.get('proben') or [None, None])[1], 'schritte': letzte.get('schritt'),
                        'mitte_mm': (tr.get('mitte_mm') or [None])[0], 'pruefung_mm': letzte.get('pruefung_mm'), 'luecke': d.get('generator_gegen_fotos'),
                        'netz_gegen_kopfki_mm': d.get('netz_gegen_kopfki_mm'), 'gewichte': (d.get('netz') or {}).get('gewichte'),
                        # Face Transfer nur in der Vergleichstabelle: hier stünde er neben der Landmarkentabelle der KopfKI — zweierlei Maß (Korrektur 26.10.2026)
                        'messung': {n: m for n, m in (d.get('messung') or {}).items() if not n.startswith('Face Transfer')},
                        'wahrheit': cls._wahrheit(datei.parent)})
        return aus

    @staticmethod
    def _wahrheit(ordner):
        """`kopfnetz_wahrheit.py` → (Netz, Mitte): mittlerer Landmarken-RMS in mm an den Exporten mit Wahrheit; None ohne Datei."""
        datei = ordner / 'wahrheit.json'
        if not datei.is_file():
            return None
        tabelle = json.loads(datei.read_text(encoding='utf-8')).get('tabelle') or {}
        netz, mitte = tabelle.get('Kopf-KI ' + ordner.name) or {}, tabelle.get('Mitte (Edgars Kopf)') or {}
        if not netz or not mitte:
            return None
        return {'netz_mm': sum(v[0] for v in netz.values()) / len(netz), 'mitte_mm': sum(v[0] for v in mitte.values()) / len(mitte), 'exporte': len(netz)}

    @classmethod
    def vergleich(cls):
        datei = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'ai2d3d' / 'kopf' / 'kopfnetz_vergleich.json'
        if not datei.is_file():
            return None
        d = json.loads(datei.read_text(encoding='utf-8'))
        zeilen = [(name, z['vorne']['mittel'], z['vorne']['median'], (z.get('vorne_ohne') or {}).get('mittel'), (z.get('vorne_ohne') or {}).get('median'),
                   (z.get('3.jpg') or {}).get('mittel'), (z.get('4.jpg') or {}).get('mittel'))
                  for name, z in (d.get('tabelle') or {}).items()]
        return {'gerechnet': d.get('gerechnet'), 'zeilen': zeilen}

    @classmethod
    def kontext(cls):
        return {'vorhanden': cls.VORHANDEN, 'bausteine': cls.BAUSTEINE, 'befunde': cls.BEFUNDE, 'grundsatz': cls.GRUNDSATZ, 'plan': cls.PLAN, 'kurz': cls.KURZ,
                'empfehlung': cls.EMPFEHLUNG, 'reihenfolge': cls.REIHENFOLGE, 'laeufe': cls.laeufe(),
                'vergleich': cls.vergleich()}
