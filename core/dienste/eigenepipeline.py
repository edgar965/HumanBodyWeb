# -*- coding: utf-8 -*-
u"""Eigenepipeline — der Abschnitt „Eigene Pipeline: SMPL-X als Rückgrat" der
Seite Hilfe -> Video to BVH (12.09.2026).

Edgar: „irgendwie nervt diese 3D to bvh pipeline, mit GVHMR usw. … Kann ich die
pipeline nicht selber implementieren / verbessern? Gibt es einen Code stand auf
dem ich aufsetzen kann?" — und danach: „kann man das nicht mit meinem DEF rig
machen, oder zumindest mit einem SMPL rig mit hand und gesicht?"

Die Antwort steht hier als Daten, nicht in der Vorlage: Jede Zahl traegt ihre
Quelle (README, Dateigroesse, Messung). Die Vorlage `hilfe/_video_to_bvh_eigene.html`
zeichnet sie nur.
"""


class Eigenepipeline:

    # Dictionary gewollt: geht so in die Vorlage.
    IST = [
        {'teil': 'YOLO, ViTPose-H, HMR2-Backbone', 'herkunft': 'drei andere Labs, eingefroren',
         'groesse': '0,1 + 2,4 + 2,6 GB',
         'tut': 'Person finden, 2D-Punkte, Bildmerkmale je Bild — die eigentliche Güte'},
        {'teil': 'GVHMR-Bewegungsmodell', 'herkunft': 'ZJU (README: 2× RTX 4090, 420 Epochen)',
         'groesse': '156 MB, 2.253 Zeilen Modellcode',
         'tut': 'aus den Merkmalen SMPL-Parameter über die Zeit; GEM ist dieselbe Familie'},
        {'teil': 'Demo-Skripte, hydra, Renderer, Dateihandling', 'herkunft': 'dieselben Unis',
         'groesse': '—',
         'tut': 'das, was nervt: Video dreimal laden, vergessene Dateien, Checkpoints auf '
                'Google Drive'},
        {'teil': 'Vorstufe, BVH-Schreiber, Hybrid, Retarget', 'herkunft': 'wir (seit 11.09.2026)',
         'groesse': '—', 'tut': 'bildweise, ein venv, Fehler mit Grund'},
    ]

    STUFEN = [
        {'name': 'Eigene Pipeline auf ihren Gewichten', 'aufwand': 'Wochen — begonnen (unten)',
         'text': 'Die Modellklassen als eingelagerter Code, Checkpoint laden, Forward selbst '
                 'rufen; kein hydra, kein demo.py, kein Rendern, blockweise, mit '
                 'Fehlerbehandlung. Gewinn: Robustheit und Tempo — nicht bessere Bewegung.'},
        {'name': 'Bewegungsmodell nachtrainieren',
         'aufwand': 'Tage auf der 32-GB-Karte (Schätzung)',
         'text': 'Nur der kleine Teil wird trainiert, auf vorberechneten HMR2-Merkmalen; braucht '
                 'AMASS, BEDLAM, 3DPW, H36M (Registrierung, Forschungslizenzen). GVHMR-Niveau ist '
                 'erreichbar, GEM-Niveau nicht — das kam aus NVIDIAs Daten und Rechenzeit.'},
        {'name': 'Neue Methode', 'aufwand': 'nein',
         'text': 'Das Feld läuft schneller als ein Einzelner: GVHMR 2024 → GEM 2025 → DuoMo 2026 '
                 '→ SAM 3D Body.'},
    ]

    #: Warum nicht direkt das DEF-Rig.
    DEF_RIG = (
        'Die Schätzer liefern nicht „Knochen", sondern die Parameter des Körpermodells, in dem '
        'ihre Trainingsdaten vorliegen (AMASS, BEDLAM = SMPL/SMPL-X). Ein Modell mit DEF-Ausgabe '
        'müsste auf AMASS-nach-DEF-retargeteten Daten trainiert werden — das brennt nur den '
        'Retarget ins Netz ein, ohne dass ein Wert genauer wird. Und das DEF-Rig hat anatomisch '
        'nichts, was SMPL-X nicht hätte: 55 Gelenke (22 Körper, Kiefer, 2 Augen, 2 × 15 Finger) '
        'plus Ausdruckskoeffizienten; seine 49 Gesichtsknochen bekommt kein Schätzer als '
        'Rotationen, sie kommen aus den Ausdrücken (`Gesichtsspuren`).'
    )

    QUELLEN = [
        {'teil': 'Körper (22)', 'laeuft': 'GEM-SMPL, GVHMR, DuoMo', 'kandidat': '—',
         'anmerkung': 'SMPL-Körperpose passt 1:1 in die ersten 22 SMPL-X-Gelenke'},
        {'teil': 'Hände (2 × 15)',
         'laeuft': 'SMPLest-X (je Bild) oder GEM-X (SOMA-Finger, zeitlich modelliert — '
                   '`Somahaende` überträgt sie ohne Retarget: gleiche Ruhelage, Mittelhand '
                   'und Grundgelenk verkettet)',
         'kandidat': 'HaMeR (Berkeley, je Bild)',
         'anmerkung': 'SMPL-X’ Handmodell IST MANO; SMPLest-X’ Vorhersage ist relativ zur '
                      'gekrümmten Mittelhand — das Handmittel muss addiert werden '
                      '(`SMPL/finger.py`). Fingerzittern im Handgelenkrahmen bei σ 2: '
                      'SMPLest-X 0,009, GEM-X 0,007 cm/Bild² — die Tabelle misst beckenrelativ '
                      'und damit den Arm, nicht die Finger'},
        {'teil': 'Gesicht (Kiefer + Ausdruck)', 'laeuft': 'SMPLest-X (je Bild)', 'kandidat': '—',
         'anmerkung': 'liefert SMPL-X-Ausdruck und Kiefer direkt; dieselbe Datei wie beim Hybrid'},
        {'teil': 'alles in einem, zeitlich', 'laeuft': 'keins',
         'kandidat': 'PromptHMR (Körper + Hände, hier nie lauffähig)',
         'anmerkung': ''},
    ]

    PLAN = [
        ('Kanonisches Format `Smplxbahn`', 'SMPL-X je Bild (Körperpose, Handposen, Kiefer, '
         'Ausdruck, Betas, Verschiebung, Kamera) als Klasse mit Datei `<lauf>_smplx.npz` — '
         'jede Quelle schreibt hinein, nichts anderes verlässt die Pipeline.', 'gebaut'),
        ('Quellen als Module', 'Körper aus GEM (`Gemlauf`, ohne dessen BVH), Hände und Gesicht aus '
         'SMPLest-X (`_run_smplx_reihe.py`, der ganze SMPL-X-Satz je Bild als npz). Dieselbe '
         'Vorstufe für alle.', 'gebaut'),
        ('Mischung im Parameterraum', '`Smplxmischung`: Lücken gefüllt, Finger und Kiefer als '
         'Quaternionen geglättet, Ausdruck als Zahlen; Gegenprobe Körper gegen Körper '
         '(mittlerer Winkel GEM ↔ SMPLest-X).', 'gebaut'),
        ('EIN Retarget SMPL-X → DEF', 'BVH mit 54 Gelenken (`Smplxbvh`: SMPL-Körper mit '
         'AIST-Namen + 30 Finger mit SMPL-X-Namen), neues Format `SMPLX` im Retarget '
         '(`formats/smplx.py`: Körper wie AIST, Finger wie Mixamo), Gesicht über die '
         'Ausdrucksdatei auch beim Einzel-Retarget.', 'gebaut'),
        ('Quellen wählbar', 'Körper GEM-SMPL, GVHMR oder DuoMo (`Smplxkoerper`); Hände '
         'SMPLest-X oder GEM-X; Gesicht SMPLest-X oder keins; Handgelenk aus der Hand oder '
         'aus dem Körper — auf der Karte, im Auftrag, in `Smplbefehl`.', 'gebaut'),
        ('Handgelenk-Übergabe', 'GEMs Handgelenk liegt im Median 35 (links) und 46 Grad '
         '(rechts) neben dem, was SMPLest-X an derselben Hand sah. `Smplxmischung.handgelenk` '
         'nimmt die Weltdrehung aus der Handquelle und schreibt sie unter GEMs Unterarm '
         'zurück; Sichtprobe auf fünf Bildern: die Handfläche folgt dem Video besser.',
         'gebaut'),
        ('Fußkontakt', '`Bodenkontakt`: Boden = 5-%-Perzentil des tiefsten Fußgelenks, Stand = '
         'nah am Boden UND langsamer als 60 cm/s; im Stand kommt der Fuß auf den Boden und '
         'bleibt auf seinem Mittelort, dazwischen wird überbrückt — nur die Wurzel, nie die '
         'Pose. Beim Ballett (Spitze, Bourrée) findet er kaum Standbilder (4 von 298); '
         'die Bilanz sagt es.', 'gebaut'),
        ('Netz-Video', '`Smplxvideo`: das SMPL-X-Netz aus der Bahn (Körper grau, Hände blau, '
         'Kiefer orange) mit der Kamera des Laufs über das Original gerendert — '
         '`<name>_smplx.mp4`, ca. 10 Bilder/s, „Video + Netz" auf der Ergebnisseite.',
         'gebaut'),
        ('Stufe 2: Training mit SMPL-X-Ausgabe', 'AMASS und BEDLAM liegen in SMPL-X vor; ein '
         'Bewegungsmodell mit Körper + Händen in einem Zug (wie PromptHMR) ist auf der eigenen '
         'Karte trainierbar, die Merkmale kommen aus derselben Vorstufe.', 'offen'),
    ]

    GRENZE = ('Was damit nicht versprochen ist: bessere Hände als der beste Handschätzer, '
              'besseres Gesicht als SMPLest-X — die Spezialisten bleiben die Decke. Besser wird '
              'die Naht zwischen ihnen, und dass es eine Pipeline ist statt fünf Demos.')

    @classmethod
    def kontext(cls):
        # Dictionary gewollt: geht so in die Vorlage.
        return {'ist': cls.IST, 'stufen': cls.STUFEN, 'def_rig': cls.DEF_RIG,
                'quellen': cls.QUELLEN, 'plan': cls.PLAN, 'grenze': cls.GRENZE}
