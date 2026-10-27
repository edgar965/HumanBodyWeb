# -*- coding: utf-8 -*-
"""Architekturai2d3dkopfnetz — Abschnitt „Kopf-KI“ von Hilfe → Architektur → 2d-3d-AI (26.10.2026, Edgar: „aktualisiere … damit wir das nicht wieder vergessen“).

Was es für den Kopf schon gibt (nicht neu bauen), woraus die Kopf-KI besteht, und wie ihre Läufe stehen. Die Läufe liest die Seite beim Aufruf von der Platte
(`3DObjects/ai2d3d/_kopfnetz/<lauf>/lauf.json`, Vergleich `ProjektTemp/_wegwerf/ai2d3d/kopf/kopfnetz_vergleich.json`); festgehaltene Messungen nennen Datum und Quelle.
"""
import json
import logging
from pathlib import Path

from django.conf import settings

from .architekturai2d3dkopfbefunde import Architekturai2d3dkopfbefunde

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
        return {'vorhanden': cls.VORHANDEN, 'bausteine': cls.BAUSTEINE, 'befunde': Architekturai2d3dkopfbefunde.BEFUNDE, 'grundsatz': cls.GRUNDSATZ, 'plan': cls.PLAN, 'kurz': cls.KURZ,
                'empfehlung': cls.EMPFEHLUNG, 'reihenfolge': cls.REIHENFOLGE, 'laeufe': cls.laeufe(),
                'vergleich': cls.vergleich()}
