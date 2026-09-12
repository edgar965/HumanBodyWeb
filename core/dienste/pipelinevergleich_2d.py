# -*- coding: utf-8 -*-
u"""Die 2D-Pipelines des Vergleichs (Hilfe -> Video to BVH): ein 2D-Erkenner
liefert Bildpunkte als CSV, MocapNET v2.1 (C++, `MocapNET2CSV.exe --hands`)
hebt sie Bild fuer Bild nach 3D und schreibt das MocapNET-Rig (165 Gelenke).

Messung 12.09.2026 auf `001_ShyrinKurz.mp4`, ueber die Web-API (Start eines
bestehenden Auftrags mit anderer Pipeline). Dauer aus der Datenbank
(updated_at - created_at), Ruhe/Boden aus `vergleich.py`, Delta ViTPose aus
`skelettvideos.py` — dort geometrisch, also je Seitenpaar die bessere
Zuordnung: MocapNET v2.1 setzt links und rechts anders als ViTPose.
Felder siehe `Pipelinevergleich.FELDER`.
"""


class Pipelines2d:

    #: Was allen fuenf gemeinsam ist — der Lifter, nicht der Erkenner.
    LIFTER = 'MocapNET v2.1 hebt Bild für Bild, ohne Zeitinformation'
    BILDRATE = ('BVH nennt 25 fps (Frame Time 0,04) bei einem 60-fps-Video — '
                'v4 korrigiert das, der v2.1-Weg nicht')

    # Dictionary gewollt: geht ueber `Pipelinevergleich.alle()` in die Vorlage.
    EINTRAEGE = [
        {'schluessel': 'mediapipe', 'art': '2D + Lifter', 'rang': 7,
         'verfahren': 'MediaPipe Holistic (Google) → CSV → MocapNET v2.1; der Standardweg der 2D-Seite.',
         'gelenke': 165, 'haende': True, 'gesicht': True, 'kamera': 'statisch (MocapNET-Kamera)',
         'dauer_s': 53, 'ueberlagerung_px': 30.6, 'ruhe_wurzel': 0.63, 'ruhe_pose': 4.5,
         'boden_cm': -97, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Schnell (53 s), reine CPU-Erkennung',
                      'Beste Deckung der 2D-Wege (30,6 px, Median 16)',
                      'Volles MocapNET-Rig mit Gesicht und Händen'],
         'nachteile': ['Links und rechts vertauscht gegenüber ViTPose (gemessen)',
                       'Unruhigste Pose aller laufenden Pipelines (4,5 cm/Bild², SMPL 0,22–0,37)',
                       BILDRATE, LIFTER],
         'begruendung': 'Bester der 2D-Wege in dieser Messung — und trotzdem hinter v4: derselbe '
                        'Erkenner mit dem älteren Lifter zittert viermal so stark.'},
        {'schluessel': 'rtmpose', 'art': '2D + Lifter', 'rang': 8,
         'verfahren': 'RTMPose (OpenMMLab, 2023, über rtmlib) → CSV → MocapNET v2.1.',
         'gelenke': 165, 'haende': False, 'gesicht': False, 'kamera': 'statisch (MocapNET-Kamera)',
         'dauer_s': 164, 'ueberlagerung_px': 78.1, 'ruhe_wurzel': 3.57, 'ruhe_pose': 3.08,
         'boden_cm': -102, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Median der Deckung so gut wie SMPL (15 px)',
                      'Kein MediaPipe nötig'],
         'nachteile': ['Einzelne Bilder fliegen weg: Mittel 78 px bei Median 15, Hüftweg 19 m',
                       'Langsamster laufender 2D-Weg (164 s)', BILDRATE, LIFTER],
         'begruendung': 'Im Median genau, im Mittel nicht — der Lifter verliert die Person in '
                        'einzelnen Bildern, und die Ausreißer sind groß.'},
        {'schluessel': 'vitpose', 'art': '2D + Lifter', 'rang': 9,
         'verfahren': 'Heißt ViTPose, fährt RTMPose (`vitpose_det.py`, seit 01.09.2026 dokumentiert) '
                      '→ CSV → MocapNET v2.1.',
         'gelenke': 165, 'haende': False, 'gesicht': False, 'kamera': 'statisch (MocapNET-Kamera)',
         'dauer_s': 71, 'ueberlagerung_px': 78.1, 'ruhe_wurzel': 3.57, 'ruhe_pose': 3.08,
         'boden_cm': -102, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Schneller als der RTMPose-Eintrag (71 s statt 164) bei gleichem Ergebnis'],
         'nachteile': ['CSV und BVH sind Byte für Byte dieselben wie bei RTMPose — kein eigener Erkenner',
                       BILDRATE, LIFTER],
         'begruendung': 'Dasselbe Ergebnis wie RTMPose, weil es derselbe Erkenner ist; ein Rang '
                        'dahinter, weil der Name etwas anderes verspricht.'},
        {'schluessel': 'yolo11', 'art': '2D + Lifter', 'rang': 10,
         'verfahren': 'YOLO11-Pose (Ultralytics, 2024) → CSV → MocapNET v2.1.',
         'gelenke': 165, 'haende': False, 'gesicht': False, 'kamera': 'statisch (MocapNET-Kamera)',
         'dauer_s': 48, 'ueberlagerung_px': 113.2, 'ruhe_wurzel': 5.94, 'ruhe_pose': 4.06,
         'boden_cm': -110, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Schnellste laufende Pipeline überhaupt (48 s)'],
         'nachteile': ['Schlechteste Deckung (113 px im Mittel, Median 22), Hüftweg 27 m',
                       'Unruhigste Wurzel (5,9 cm/Bild²)', BILDRATE, LIFTER],
         'begruendung': 'Schnell, aber der Lifter macht aus guten 2D-Punkten die unruhigste Bahn.'},
        {'schluessel': 'openpose', 'art': '2D + Lifter', 'rang': None,
         'verfahren': 'OpenPose (CMU, Cao u. a.) als Programm → JSON → CSV → MocapNET v2.1.',
         'gelenke': None, 'haende': False, 'gesicht': False, 'kamera': 'statisch (MocapNET-Kamera)',
         'dauer_s': 155, 'ueberlagerung_px': None, 'ruhe_wurzel': None, 'ruhe_pose': None,
         'boden_cm': None, 'zustand': 'gescheitert',
         'zustand_grund': 'OpenPose bricht nach 155 s ab: „no kernel image is available for '
                          'execution on the device" — das Programm ist für ältere GPUs gebaut, '
                          'nicht für Blackwell (sm_120).',
         'vorteile': ['Der klassische Erkenner, JSON je Bild'],
         'nachteile': ['Läuft auf dieser GPU nicht'],
         'begruendung': 'Kein Ergebnis, deshalb kein Rang.'},
    ]
