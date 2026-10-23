# -*- coding: utf-8 -*-
"""Architekturmesh3daigarmentcode — Abschnitt „Kleider-GarmentCode“ der Seite Hilfe → Architektur → Mesh3DAI (20.10.2026).

Edgar: „Erkläre mir nochmal das Konzept. Da ist noch ein Widerspruch drin … Kleider-GarmentCode … wie die Kleider gemacht werden. Wenn du sagst, du misst erstmal alle Stellen, mach eine Liste,
welche Stellen du misst … warum suchst du aber dann am Ende ein existierendes Asset aus der Liste??“, dann „Suche im Internet nach Lösungen wie das andere machen“ und „was fehlt an der Implementierung
der neuronalen Netze?? brauchst du da nicht ein zweites Neuronales Netz dafür??“.
Die Texte sind aus dem Code gelesen (Dateien in `ProjektTemp/_wegwerf/`: `mesh3dai_schnitt_messung.py`, `…_anwenden.py`, `…_regelwahl.py`, `…_katalogwurf.py`, `…_training.py`); was beim Aufruf
gelesen wird: Zahlen je Bauplan und Vorbilder (`_schnitt/daten_katalog_Ursula1/aufbau.json`), Stand der neuen Übungsbeispiele (Zahl der Dateien), Regelwahl des Ursula1-Kopfs (`regelwahl.json`).
Die Messung an Ursula1 ist von Hand eingetragen, mit Skript und Datum.
"""

import json
from pathlib import Path

from .architekturmesh3daiassetbild import Architekturmesh3daiassetbild

__all__ = ['Architekturmesh3daigarmentcode']


class Architekturmesh3daigarmentcode:
    FIGUR = 'Ursula1'
    ZIEL_PROBEN = 2000

    #: (Schritt, wer rechnet, Eingabe, was passiert, Ausgabe)
    SCHRITTE = (
        ('1 Zerlegen', 'KI: Zerlegungsnetz', 'Punktwolke der Figur in der A-Pose (4.096 Punkte mit Farbe)',
         'Für jeden Punkt die Art: Haut, Haar, Oberteil, Hose, Rock, Kleid, Anzug, Unterwäsche, Schuh, Kopfbedeckung oder Zubehör.', 'Art je Punkt'),
        ('2 Ausschneiden', 'Rechnung (Weg k)', 'Netz + Art je Punkt',
         'Die Art geht auf die Flächen des Netzes, die Grenzen werden geglättet, je Art wird ein Stück herausgeschnitten und auf die KI-Figur in ihre Ruhelage (A-Pose) gelegt.',
         'das Stück, z. B. die Hose, als Netz in Ruhelage'),
        ('3 Bauplan wählen', 'KI: Schnittnetz', '4.096 Punkte des Stücks mit Flächenrichtung, durch die Körperhöhe geteilt',
         'Wählt einen der sieben GarmentCode-Baupläne, der zur Art passt (Hose → Hose oder Shorts), eine Form des Bauplans (z. B. Kreisrock) und schlägt für jede Zahl des Bauplans einen Wert vor.',
         'Bauplan, Form, Vorschläge'),
        ('4 Zahlen festlegen', 'Regelwahl', 'Vorgabe der Form · Messung am Stück · Vorschlag des Schnittnetzes',
         'Je Zahl die Quelle, die auf Prüfbeispielen näher an der Wahrheit lag (ausgemessen, nicht von Hand gesetzt). Den Ärmelwinkel setzt die Armhaltung der Figur. Ohne Regelwahl: alle Zahlen vom Netz.',
         'alle Zahlen des Bauplans (Hose 11, Oberteil 63)'),
        ('5 Schnitt rechnen', 'GarmentCode', 'Bauplan + Zahlen + Körpermaße der KI-Figur (Taille, Hüfte, Beinlänge …)',
         'Der Bauplan (bei der Hose `pants.py`) rechnet die flachen Schnittteile wie auf Papier und die Nähte dazwischen — jedes Mal neu, aus genau diesen Zahlen.', 'Schnittmuster: Bahnen + Nähte'),
        ('6 Nähen und Drapieren', 'Stoffsimulation (Warp)', 'Schnittmuster + Körper der KI-Figur',
         'Die Bahnen werden um den Körper gelegt, zusammengenäht, und der Stoff fällt unter Schwerkraft, bis er ruht.', '3D-Stück auf der Figur'),
        ('7 Anziehen', 'Rechnung', '3D-Stück',
         'Knochengewichte vom Körper darunter (das Stück bewegt sich mit), EINE Farbe: Mittel der Farbe des ausgeschnittenen Stücks nach Fläche.', 'Stück im Ergebnis'),
    )

    #: (Stelle, wie gemessen, Zahl im Bauplan, für) — `Schnittmessung.messen` mit den Formeln aus `Assets/GarmentCode/schnittdeutung.py`
    GEMESSEN = (
        ('Oberkante, Unterkante', 'höchster und tiefster Stoffpunkt über dem Boden', '— (Grundlage aller Längen)', 'alle'),
        ('Stoff über der Schulter', 'wie weit Stoff seitlich über die Schulter reicht; ab 4 cm hat das Stück Ärmel', '`sleeve.sleeveless` (Ärmel ja/nein)', 'Oberteil, Kleid, Anzug, Unterwäsche'),
        ('Ärmellänge', 'Stoff über die Schulter ÷ nutzbare Armlänge der Figur', '`sleeve.length`', 'Oberteil, Kleid, Anzug, Unterwäsche'),
        ('Umfang auf Brusthöhe', 'Hülle des Rumpfstoffs von oben, in einer Scheibe auf Brusthöhe, nur innerhalb der halben Schulterbreite (sonst zählten die Ärmel mit) ÷ Brustumfang der Figur',
         '`shirt.width`', 'Oberteil, Kleid, Anzug, Unterwäsche'),
        ('Umfang am Saum', 'wie oben, knapp über der Unterkante ÷ Umfang auf Brusthöhe', '`shirt.flare`', 'Oberteil'),
        ('Länge des Oberteils', '(Schulterhöhe − Saumhöhe) ÷ Taillenlänge der Figur', '`shirt.length`', 'Oberteil'),
        ('Länge des Unterteils', '(Hüfthöhe − Saumhöhe) ÷ Hüfthöhe; nur wenn der Saum mindestens 8 cm unter der Hüfte liegt',
         '`pants.length`, `flare-skirt.length`, `pencil-skirt.length`', 'Hose, Shorts, Rock, Kleid, Anzug'),
        ('Saumumfang des Rocks', 'Hülle am Saum; Kreisrock über die Kreisbogenformel zurückgerechnet, Bleistiftrock Saum ÷ Hüfte', '`flare-skirt.suns`, `pencil-skirt.flare`', 'Rock, Kleid'),
        ('Bundhöhe', 'Oberkante zwischen Hüftlinie (0,5) und Taille (1,0), nur wenn das Stück nicht über die Taille reicht. Gemessen wird die SICHTBARE Oberkante: liegt ein T-Shirt darüber, '
         'ist es dessen Saum, nicht der Bund', '`pants.rise`, `briefs.rise`', 'Hose, Shorts, Unterwäsche'),
    )
    EICHUNG = ('Die Formeln treffen am drapierten Stück nicht genau — der Saum fällt tiefer als der Schnitt. Darum wird jeder Messwert an Übungsbeispielen mit bekanntem Schnitt geeicht '
               '(Gerade „gemessen → wahr“ je Bauplan, Form und Zahl, ab 10 Beispielen; `Schnittmessung.eichen`).')

    #: je Bauplan die Zahlen, die `Schnittmessung.messen` liefern kann (Schnitt mit den Feldern des Bauplans beim Aufruf)
    MESSBAR = {
        'oberteil': {'sleeve.sleeveless', 'sleeve.length', 'shirt.width', 'shirt.flare', 'shirt.length'},
        'kleid': {'sleeve.sleeveless', 'sleeve.length', 'shirt.width', 'flare-skirt.length', 'pencil-skirt.length', 'pants.length', 'flare-skirt.suns', 'pencil-skirt.flare'},
        'anzug': {'sleeve.sleeveless', 'sleeve.length', 'shirt.width', 'flare-skirt.length', 'pencil-skirt.length', 'pants.length', 'flare-skirt.suns', 'pencil-skirt.flare'},
        'unterwaesche': {'sleeve.sleeveless', 'sleeve.length', 'shirt.width', 'pants.rise', 'briefs.rise'},
        'hose': {'pants.length', 'pants.rise'}, 'shorts': {'pants.length', 'pants.rise'},
        'rock': {'flare-skirt.length', 'pencil-skirt.length', 'pants.length', 'flare-skirt.suns', 'pencil-skirt.flare'},
    }
    NAMEN = {'oberteil': 'Oberteil', 'hose': 'Hose', 'shorts': 'Shorts', 'rock': 'Rock', 'kleid': 'Kleid', 'anzug': 'Anzug', 'unterwaesche': 'Unterwäsche'}

    #: (was, Zahlen im Bauplan, Stand) — Edgars Liste „Textur, Drapierung, Falten, Saum, wie eng es am Körper liegt“ und was sonst fehlt
    NICHT_GEMESSEN = (
        ('Beinweite: Oberschenkel, Knie, Wade, Knöchel', '`pants.width`, `pants.flare`',
         'seit 20.10.2026 gemessen (`Messliste`) und nachgestellt (`Schnittnachstellen`) — nicht direkt in eine Zahl umgerechnet'),
        ('Bund: Weite und Breite', '`waistband.waist`, `waistband.width`', 'nicht gemessen'),
        ('Bündchen, Rüschen, Manschetten', '`pants.cuff.*` (5), `sleeve.cuff.*` (5, links noch einmal 5)', 'nicht gemessen'),
        ('Ärmelweite oben und unten', '`sleeve.connecting_width`, `sleeve.end_width`', 'seit 20.10.2026 gemessen (Oberarm, Öffnung) und nachgestellt'),
        ('Kragen, Ausschnitt', '`collar.*` (15, links noch einmal 9)', 'nicht gemessen'),
        ('Enge: Abstand Stoff ↔ Haut', 'keine eigene Zahl — folgt aus den Weiten; Anlegen an die Haut `bau.anliegen_mm`',
         'seit 20.10.2026 gemessen (Zugabe je Stelle, Abstand zur Haut); als Wert probiert: Anlegen 2/6/12 mm, je echt drapiert'),
        ('Falten, Fall des Stoffs (Drapierung)', 'Stoffwerte der Simulation (Biegung, Dehnung, Gewicht)',
         'nicht gemessen und nicht gewählt: ein fester Satz für jedes Stück (`gui_sim_props.yaml`)'),
        ('Textur, Muster, Aufdruck', '—', 'nicht übertragen: das Stück bekommt eine Farbe (Mittel nach Fläche)'),
        ('Saumform: schräg, Schlitz, Zipfel, vorn kürzer als hinten', '—', 'nicht gemessen — nur Höhe der Unterkante und Umfang am Saum'),
    )

    #: (Stichwort, Erklärung) — der Widerspruch „alles neu gebaut“ gegen „Katalog“
    KATALOG = (
        ('Wird am Ende ein fertiges Stück aus einer Liste genommen?',
         'Nein. Jedes Stück wird neu geschnitten, genäht und drapiert (Schritte 5–6), aus seinen eigenen Zahlen. Der Katalog kommt an drei Stellen vor, an keiner als fertiges Stück:'),
        ('Bauplan („Katalogstück“)', 'Sieben Programme: Oberteil, Hose, Shorts, Rock, Kleid, Anzug, Unterwäsche. Ein Bauplan ist die Bauart — „Hose“ heißt zwei Beine, Schritt, Bund; '
         'wie weit und wie lang, entscheiden die Zahlen. Das Schnittnetz wählt die Bauart, kein Stück.'),
        ('Form', 'Startwerte innerhalb eines Bauplans (Rock: Bleistift, Kreis, Stufen …; die Hose hat keine). Was weder Messung noch Schnittnetz besser trifft, bleibt auf diesen Startwerten.'),
        ('Vorbilder', 'Zahlensätze, die bekannte Kleidungsstücke nachbilden (z. B. „Crudefemaletshirt“, „Pantsviking“, „Leggings“). Sie sind NUR Übungsmaterial: je Übungsbeispiel ein Vorbild, '
         'die Hälfte seiner Kommazahlen um bis zu ±8 % des Bereichs verschoben, auf der Figur genäht und drapiert — das Netz übt, aus der Form des Stoffs die Zahlen abzulesen. '
         'Im Ergebnis wird kein Vorbild ausgesucht.'),
        ('Wo der Widerspruch bleibt', 'Weil alle Übungsbeispiele nah an Vorbildern liegen, liefert das Schnittnetz Zahlen nahe an einem Vorbild, das es kennt. Ein Stück, das keinem Vorbild ähnelt — '
         'Ursulas Hose `lva_pant` aus Daz („dForce Leather Viking Armor“; ob „Pantsviking“ dasselbe Stück ist, ist nicht geprüft) —, bekommt die Zahlen des ähnlichsten. Dann trägt nur die '
         'Messung am Stück, und die misst zu wenig (Tabellen oben).'),
        ('Wo wirklich aus der Bibliothek gewählt wird', 'Weg h (Frisur der Garderobe nach Haarmaßen) und Weg a (Garderobe-Stück nach Abdeckung). Beide sind auf der Testseite wählbar, '
         'mit „Bibliothek“ beschriftet und NIE Vorgabe. Vorgabe ist KI: Kleidung s (GarmentCode), Haar k (ausgeschnitten).'),
    )

    #: Ursula1, Probe 1, gemessen 20.10.2026 (`ProjektTemp/_wegwerf/ursula1_kleider_vermessen.py`: Ruhelage, nach Fläche abgetastet, Scheiben ±1 cm)
    URSULA_MESSUNG = (
        ('Hose, Knöchel (Höhe 0,15 m), Breite × Tiefe je Bein', '5,4 × 7,4 cm', '14 × 22 cm'),
        ('Hose, Knie (0,50 m)', '13,5 × 13,3 cm', '15 × 22 cm'),
        ('Hose, Oberkante', '1,022 m', '1,091 m (7 cm zu hoch)'),
        ('Hose, Unterkante', '0,087 m', '0,124 m'),
        ('Oberteil, Unterkante', '0,943 m', '1,074 m (13 cm zu kurz)'),
        ('Oberteil, ganze Breite auf 1,20 / 1,25 m', '26,5 / 42,3 cm', '63,1 / 59,9 cm'),
    )
    #: die Zahlen des alten Schnittnetzes (`kleider_ki/0001/kleider/s/*/eintrag.json`, „alle Regler vom Kopf“)
    URSULA_ZAHLEN = (
        ('Hose', '`pants.flare` 0,94: Bein fast gerade bis zum Saum (eng wäre 0,5–0,6) · `pants.cuff.skirt_flare` 1,22: Bündchen mit Glocke am Saum, das die echte Hose nicht hat · '
                 '`waistband.waist` 1,36: Bund 36 % weiter als die Taille · `pants.rise` 1,0: Bund an der Taille'),
        ('Oberteil', '`shirt.length` 1,11 · `sleeve.length` 0,30 · `sleeve.connect_ruffle` 1,51: Puffärmel · `sleeve.cuff.skirt_flare` 1,21: Ärmelsaum mit Glocke'),
    )

    #: (was fehlt, warum, was andere tun) — Antwort auf „was fehlt an der Implementierung der neuronalen Netze?? brauchst du da nicht ein zweites Neuronales Netz?“
    FEHLT = (
        ('Ein zweites Netz?', 'Gibt es schon, sogar zwei: das Zerlegungsnetz (Art je Punkt) und das Schnittnetz (Bauplan, Form, Zahlen) — beide eigene Netze neben dem Posennetz. '
         'Hunyuan (Form aus Fotos), Sapiens (welcher Pixel ist Kleidung) und MIA (Rig) liefern kein Schnittmuster; sie entsprechen bei uns den Schritten 1–2.', '—'),
        ('Zu wenig Übungsbeispiele', 'Das Schnittnetz von heute sah 256 Beispiele (37 zur Prüfung) für sieben Baupläne mit 11–92 Zahlen. Für Ursula1 entstehen gerade 2.000.',
         'GarmentCodeData: 115.000 Stücke im selben Format; ChatGarment: 20.000 neue Stücke'),
        ('Jede Zahl zählt gleich viel', 'Im Training ist der Fehler der Mittelwert über alle Zahlen eines Bauplans (`Schnitttraining.verlust`). Beim Oberteil zählen 24 Kragenzahlen zusammen mehr als '
         'Weite und Länge; Zahlen, die man dem Stoff nicht ansieht (Bündchen, Rüschen), rät das Netz als Mitte. Bei der Körperform war es dasselbe — gelöst mit dem Formmaß (Fehler eines Reglers × seine '
         'Wirkung auf die Punkte). Für den Schnitt fehlt so ein Maß: Wirkung jeder Zahl auf das drapierte Stück.', 'Verlust auf der Form des Stücks statt auf den Zahlen (DiffAvatar, IGPM)'),
        ('Kein Nachprüfen', 'Das Schnittnetz rät einmal, GarmentCode baut, fertig. Der Abstand gebauter Schnitt ↔ ausgeschnittenes Stück wird schon gemessen (steht im Eintrag), '
         'aber nicht zum Nachstellen benutzt.', 'Zahlen nachstellen, bis der simulierte Stoff das Ziel trifft (DiffAvatar, IGPM)'),
        ('Zu wenig Messstellen', 'Hose 2 von 11 Zahlen, Oberteil 5 von 63 (Tabelle „Zahlen je Bauplan“).', 'feste Messliste je Kleidungsart (Points of Measure der Bekleidungsindustrie)'),
        ('Unsauberes Eingangsstück', 'Das ausgeschnittene Stück trägt Fetzen anderer Arten (Ursula1-Oberteil: kleine Haarstücke), die Grenzen sind geglättet, Verdecktes fehlt (die Hose endet am Shirt-Saum).',
         'Garment Recovery: Ruheform + Verformung getrennt gelernt'),
    )

    #: (Verfahren, Quelle, wie sie es machen, was es für uns heißt) — Recherche 20.10.2026, nichts davon ausprobiert
    RECHERCHE = (
        ('Points of Measure (Bekleidungsindustrie)', 'https://www.delogue.com/en/blog/how-to-spec-a-garment-with-points-of-measure',
         'Je Kleidungsart eine feste Liste von Messstellen mit Messvorschrift: Brust 1 Zoll unter dem Armloch, Saumweite, Schrittlänge, Leibhöhe vorn und hinten, Oberschenkel 1 Zoll unter dem Schritt …',
         'Unsere Messung als solche Liste je Bauplan aufbauen statt einzelner Formeln.'),
        ('DiffAvatar (CVPR 2024)', 'https://arxiv.org/abs/2311.12194',
         'Scan → Kleidung abtrennen → Körper anpassen → Schnitt in 2D UND Stoffwerte mit einer differenzierbaren Stoffsimulation so lange verändern, bis der simulierte Stoff den Scan trifft. '
         'Die Biegesteifigkeit bestimmt die Falten am stärksten.', 'Nachstellen statt einmal raten; Stoffwerte je Stück schätzen.'),
        ('Inverse Garment and Pattern Modeling (Eurographics 2024)', 'https://arxiv.org/abs/2403.06841',
         'Erst eine geometrische Näherung der Form, dann inverse Simulation; die Schnittteile bleiben links-rechts symmetrisch. Code laut Paper unter github.com/MLMS-CG/IGPM.',
         'Gleicher Gedanke: Startwert, dann gegen das Ziel nachstellen.'),
        ('Garment Recovery (CVPR 2024)', 'https://arxiv.org/abs/2311.10356',
         'Implicit Sewing Patterns: gelernte Ruheform des Stücks plus ein Verformungsmodell; Ergebnis ist ein Netz, das sich simulieren lässt.', 'Ruheform und Faltenwurf trennen.'),
        ('ChatGarment (CVPR 2025)', 'https://arxiv.org/abs/2412.17811',
         'Ein Bild-Sprachmodell gibt direkt GarmentCode-JSON aus (Bild oder Text → Schnitt), trainiert mit 20.000 neuen Stücken und 1 Mio. Bildern. Die Autoren nennen falsche Längen und Weiten als '
         'Schwäche und liefern einen Nachschritt: Längen und Weiten nachstellen, bis das drapierte Stück die Silhouette im Foto trifft (Tabelle „fremder Code“ unten).', 'Selbst mit viel mehr Daten braucht es einen Nachschritt für Längen und Weiten.'),
        ('GarmentCodeData (ECCV 2024)', 'https://arxiv.org/abs/2405.17609',
         '115.000 GarmentCode-Stücke mit Schnitt, drapiert auf vielen Körpern, drei Stoffe; offene Drapier-Kette.', 'Übungsmaterial im selben Format, 50-mal mehr als unsere 2.000.'),
        ('SIZER (ECCV 2020) und Zugabe-Messungen', 'https://arxiv.org/abs/2007.11610',
         'Scans mit Körper darunter und Kleidung getrennt; Studien messen die Zugabe (Abstand Stoff ↔ Körper) je Umfang und Querschnitt.',
         'Wir haben den Körper der KI-Figur unter dem Stück: Enge je Messstelle ist messbar.'),
        ('3DBODY.TECH 2022 (Zugabe an Overalls)', 'https://proc.3dbody.tech/abstracts/2022/2251baytar.html',
         'Digitale Overalls auf 29 Körperscans, Zugabe je Umfang und Querschnitt in drei Haltungen gemessen.', 'Messvorschrift für die Enge.'),
        ('FabricDiffusion (SIGGRAPH Asia 2024)', 'https://arxiv.org/abs/2410.01801',
         'Aus einem Kleidungsfoto ein flaches, kachelbares Stoffbild, das auf die UV der Schnittteile gelegt wird.', 'Textur statt einer Mittelfarbe.'),
        ('NeuralTailor (2022)', '', 'Punktwolke eines Stücks → Schnittmuster (eigenes Format, kein GarmentCode).', 'Bei uns schon eingebaut, als Vergleichsweg n auf der Testseite.'),
    )

    #: (Nr., Vorschlag, wozu, Haken, Stand der Abwägung) — überarbeitet 20.10.2026 abends (Edgar: „Überarbeite danach deine Vorschläge … Diskutiere mit mir, ob das so sinnvoll ist“). 1 und 2a gebaut am 20.10.2026 abends, der Rest nicht.
    VORSCHLAEGE = (
        ('1', 'Messliste je Bauplan nach Points of Measure, mit Enge je Stelle. Hose: Bund, Hüfte, Leibhöhe, Oberschenkel, Knie, Wade, Saum, Schrittlänge, Außenlänge; Oberteil: Brust, Taille, Saum, '
              'Länge vorn/hinten, Ärmel oben/Ellbogen/Saum, Halsausschnitt. Gemessen am ausgeschnittenen UND am gebauten Stück; verdeckte Stellen heißen „verdeckt“ statt falsch gemessen.',
         'Grundlage für alles andere: ohne Messstellen kein Ziel zum Nachstellen.',
         'So gut wie das ausgeschnittene Stück: geglättete Grenzen, Fetzen, Verdecktes (Hose unter dem Shirt). Zuerst säubern.',
         'GEBAUT 20.10.2026 (`Messliste`): Hose 12 Stellen (Hüfte, Oberschenkel, Knie, Wade, Saum je Bein, Saumhöhe, Oberkante), Oberteil 10 (Brust, Taille, Saum, Saumhöhe, je Arm Länge, Oberarm, '
         'Öffnung); je Stelle Umfang, Körper, Zugabe, Abstand zur Haut; verdeckt = unter dem Oberteil. Ursulas Hose: Zugabe Oberschenkel 15 → Saum 2 cm (oben weit, unten eng).'),
        ('2', 'Nachstellen nach dem Muster von ChatGarment: Längen und Weiten über endliche Differenzen und Adam, Zug zurück zum Startwert, Zahlen auf ihren Bereich geklemmt — Ziel die Messliste statt '
              'einer Silhouette (wir haben das Stück in 3D, ChatGarment nur ein Foto).',
         'Macht aus „einmal raten“ ein „so lange ändern, bis es passt“ — der Schritt, den alle fertigen Verfahren haben.',
         'Mit echter Drapierung teuer: je Runde 1 + n Drapierungen à 11–12 s; Hose mit 5 Zahlen und 30 Runden ≈ 35 min (gerechnet, nicht gemessen). Darum 2a oder 3.', 'danach'),
        ('2a', 'Dasselbe Nachstellen am flachen Schnittmuster: Stoffbreite je Messstelle ohne Drapieren (ein Bau: Hose 0,23 s, Oberteil ~1,4 s — gemessen), geeicht an einer echten Drapierung, '
               'drei Drapierungen; gewählt wird die beste GEMESSENE.',
         'Schnell genug für jede Probe.', 'Erreicht nur, was die Form schneiden kann: Ursulas Hose bleibt am Saum 14 cm zu weit (`pants.flare` am Rand 0,5), das T-Shirt an der Taille 11 cm (gerader Schlauch).',
         'GEBAUT 20.10.2026 (`Schnittnachstellen`, Weg s): Ursula1 Hose Ø 15,7 → 6,2 cm, T-Shirt 8,9 → 5,1 cm an den Messstellen (Lauf auf der Figur vor dem Formtraining 21:39; neu gerechnet für die heutige Figur).'),
        ('3', 'Drapiernetz: ein zweites KI-Netz, vorwärts — Zahlen → Messstellen nach dem Drapieren. Gelernt aus den Übungsbeispielen, die ohnehin entstehen (Zahlen und drapiertes Stück je Beispiel).',
         'Nachstellen in Millisekunden, auch für weite Stücke; liefert nebenbei die Wirkung jeder Zahl (für 4).',
         'Weiß nur, was es in den Übungsbeispielen sah (Vorbilder ± 8 %); darum am Ende immer einmal echt drapieren.', 'wenn 2a bei weiten Stücken nicht reicht'),
        ('4', 'Schnittmaß im Training: Fehler je Zahl gewichtet mit ihrer Wirkung (wie das Formmaß).', 'besserer Startwert', 'Mit 2/3 nur noch ein Startwert — kleiner Gewinn.', 'später'),
        ('5', 'Mehr Übungsmaterial aus GarmentCodeData.', 'viele Figuren und Stücke', 'Anderer GarmentCode-Stand (Fingerabdruck der Felder), andere Körper (nicht Genesis), Lizenz des Datensatzes nicht geklärt. '
              'Für Ursula1 allein nicht nötig.', 'später'),
        ('6', 'Textur: Farbe und Bild des ausgeschnittenen Stücks auf die UV der Schnittteile projizieren (nächster Punkt), ohne KI.', 'statt einer Mittelfarbe', 'Muster verzerrt, wo der Schnitt anders sitzt.',
         'klein, früh'),
        ('7', 'Stoffwerte (Biegung) je Stück schätzen.', 'Falten', 'Unsere Drapierung nimmt einen festen Stoff; ändern heißt die Simulation anfassen.', 'später'),
        ('8', 'Kurzhaar über Herrenhaar und Haarlänge an die Haarmaße hängen; Schuh als achter Bauplan.', 'Haar und Schuh nicht nur ausgeschnitten', 'Für langes Haar kein Generator; Haar nicht recherchiert.',
         'nach den Kleidern'),
    )

    #: (Code, Quelle, Lizenz, was drin ist, was wir nehmen) — nachgesehen 20.10.2026 auf den Projektseiten; nichts heruntergeladen
    UEBERNAHME = (
        ('ChatGarment', 'https://github.com/biansy000/chatgarment', 'Apache-2.0',
         'Bild-Sprachmodell → GarmentCode-JSON (eigener Stand „GarmentCodeRC“); Größen-Nachschritt `scripts/postprocess/postprocess.py`: neun Zahlen (`shirt.length`, `shirt.width`, `sleeve.length`, '
         '`sleeve.end_width`, `skirt.length`, `flare-skirt.length`, `pencil-skirt.length`, `pants.length`, `pants.flare`), endliche Differenzen (Schritt 0,06 für Weiten, sonst 0,02), Adam, 30 Runden, '
         'Zug 0,01 zum Startwert, je Auswertung echt drapiert.',
         'JA: den Nachschritt als Vorlage für Vorschlag 2/2a — Liste, Schrittweiten, Ablauf; unser Ziel ist die Messliste statt der Silhouette. Das Modell selbst nicht (Bilder, nicht Netze).'),
        ('IGPM (Inverse Garment and Pattern Modeling)', 'https://github.com/MLMS-CG/IGPM', 'MIT',
         'Schnittteile, Nähte, Symmetrie (`panel.py`, `seaming_line.py`, `symmetry.py`); Code laut Seite „schrittweise“ veröffentlicht, Simulator nicht genannt.',
         'NEIN vorerst: arbeitet auf freien Schnittteilen, nicht auf GarmentCode-Zahlen. Die Idee (erst Näherung, dann nachstellen) steckt in 2/3.'),
        ('GarmentCodeData', 'https://igl.ethz.ch/projects/GarmentCodeData/', 'nicht geklärt',
         '115.000 Stücke mit Schnitt, drapiert auf Körpern aus CAESAR, drei Stoffe; Fassung 2 seit 04.09.2024.', 'SPÄTER (Vorschlag 5), nach Klärung der Lizenz.'),
        ('Garment Recovery', 'https://github.com/liren2515/GarmentRecovery', 'keine Lizenz gefunden', 'Anpassung aus Bildern mit SMPL-Körper.', 'NEIN: ohne Lizenz nicht verwendbar, und Bild statt Netz.'),
        ('DiffAvatar', 'https://people.csail.mit.edu/liyifei/publication/diffavatar', 'kein Code gefunden',
         'C++ mit Eigen und libigl; je Runde etwa eine Minute, ganze Läufe 20–200 min (laut Paper).', 'NEIN: nur die Idee (Stoffwerte mitschätzen, Vorschlag 7).'),
        ('NeuralTailor', '', 'MIT', 'Punktwolke → Schnittmuster.', 'schon eingebaut (Vergleichsweg n).'),
    )

    @classmethod
    def _schnitt(cls):
        from django.conf import settings
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_schnitt'

    @classmethod
    def bauplaene(cls, aufbau):
        """Je Bauplan: Formen, Zahl der Zahlen, davon messbar, Vorbilder Training/Prüfung — aus `aufbau.json` der Übungsbeispiele."""
        zeilen = []
        for s in aufbau.get('stuecke') or []:
            a = (aufbau.get('aufbau') or {}).get(s) or {}
            felder = list(a.get('felder') or [])
            gemessen = sorted(cls.MESSBAR.get(s, set()) & set(felder))
            auftraege = (aufbau.get('auftraege') or {}).get(s) or {}
            zeilen.append({'name': cls.NAMEN.get(s, s), 'formen': [f.replace('form_', '').replace('_', ' ') for f in a.get('formen') or [] if f != 'grund'],
                           'felder': len(felder), 'gemessen': gemessen, 'training': auftraege.get('training', 0), 'pruefung': auftraege.get('pruefung', 0)})
        return zeilen

    @classmethod
    def regelwahl(cls, laeufe):
        """Jüngster Lauf `*_katalog_<figur>` mit `regelwahl.json` → je Bauplan, wie viele Zahlen aus Form, Messung, Netz kommen; sonst None."""
        kandidaten = sorted(laeufe.glob('*_katalog_%s' % cls.FIGUR.lower())) if laeufe.is_dir() else []
        for lauf in reversed(kandidaten):
            datei = lauf / 'regelwahl.json'
            if not datei.is_file():
                return {'lauf': lauf.name, 'fehlt': True}
            r = json.loads(datei.read_text(encoding='utf-8'))
            je = []
            for s, felder in (r.get('stuecke') or {}).items():
                zahl = {q: sum(1 for f in felder.values() if f.get('herkunft') == q) for q in ('form', 'messung', 'ki', 'regel')}
                je.append({'name': cls.NAMEN.get(s, s), **zahl})
            b = (r.get('bericht') or {}).get('hälfte_B') or {}
            return {'lauf': lauf.name, 'je': je, 'bericht': {k: b.get(k) for k in ('proben', 'ki', 'form', 'messung', 'gewaehlt', 'median')}}
        return None

    @classmethod
    def kontext(cls):
        schnitt = cls._schnitt()
        daten = schnitt / ('daten_katalog_%s' % cls.FIGUR)
        datei = daten / 'aufbau.json'
        aufbau = json.loads(datei.read_text(encoding='utf-8')) if datei.is_file() else {}
        fertig = sum(1 for _ in daten.glob('[0-9]*.npz')) if daten.is_dir() else 0
        bauplaene = cls.bauplaene(aufbau)
        return {'schritte': cls.SCHRITTE, 'gemessen': cls.GEMESSEN, 'eichung': cls.EICHUNG, 'nicht_gemessen': cls.NICHT_GEMESSEN, 'katalog': cls.KATALOG,
                'bauplaene': bauplaene, 'vorbilder': sum(z['training'] + z['pruefung'] for z in bauplaene), 'aufbau_fehlt': not aufbau,
                'ursula_messung': cls.URSULA_MESSUNG, 'ursula_zahlen': cls.URSULA_ZAHLEN, 'fehlt': cls.FEHLT, 'recherche': cls.RECHERCHE, 'vorschlaege': cls.VORSCHLAEGE,
                'uebernahme': cls.UEBERNAHME, 'bild': Architekturmesh3daiassetbild.svg(),
                'figur': cls.FIGUR, 'proben_fertig': fertig, 'proben_ziel': cls.ZIEL_PROBEN, 'regelwahl': cls.regelwahl(schnitt / 'laeufe')}
