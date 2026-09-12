# -*- coding: utf-8 -*-
u"""Die 3D- und Hybrid-Pipelines des Vergleichs (Hilfe -> Video to BVH).

Messung 12.09.2026 auf `001_ShyrinKurz.mp4` (298 Bilder, 60 fps, 1280 x 720),
ueber die Web-API: Dauer = updated_at - created_at des Auftrags; Ruhe/Boden aus
`_wegwerf/vergleich_001/vergleich.py` (vergleich.md); Delta ViTPose aus
`skelettvideos.py` (ueberlagerung.json). `None` heisst: nicht gemessen —
die Seite schreibt das aus. Felder siehe `Pipelinevergleich.FELDER`.

NEUBEWERTUNG 12.09.2026 (Edgar: „Mach auch eine neubewertung der Pipelines, vor
allem GEM-X"): GEM-X mit Glaettung 4 (Standard seit dem Tag), zwei neue
Hybride auf dem GEM-SMPL-Koerper. Ein Eintrag mit `variante` ist dieselbe
Pipeline mit anderer Bestellung (hier `hands_source: gemx`) — eigene Zeile,
eigener Rang, gleicher Schluessel. Raenge 1..12 fuer alles mit BVH.
"""


class Pipelines3d:

    # Dictionary gewollt: geht ueber `Pipelinevergleich.alle()` in die Vorlage.
    EINTRAEGE = [
        {'schluessel': 'hybrid_gem', 'art': 'Hybrid', 'rang': 1, 'variante': 'Finger aus GEM-X',
         'variante_kennung': 'hands_source: gemx',
         'verfahren': 'Körper aus GEM-SMPL, danach GEM-X (SOMA, 77 Gelenke) für die Finger und '
                      'MocapNET v4 für das Gesicht (Ausdrücke aus SMPLest-X); drei BVH-Dateien, '
                      'zusammengeführt auf dem Rig (`Handspuren`). Neu am 12.09.2026.',
         'gelenke': 24, 'haende': True, 'gesicht': True, 'kamera': 'statisch (Kameraraum)',
         'dauer_s': 348, 'ueberlagerung_px': 24.3, 'ruhe_wurzel': 3.1, 'ruhe_pose': 0.20,
         'boden_cm': -103, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Der GEM-SMPL-Körper (24,3 px, Pose 0,20) plus 30 Fingerspuren aus derselben '
                      'NVIDIA-Familie — gemessen: Fingerzittern 0,28 cm/Bild² (GEM-X, σ 4)',
                      'Gesicht als SMPLest-X-Ausdrücke wie bei jedem Hybrid',
                      'Beide Zugaben abschaltbar (Hände-Quelle, Gesicht-Quelle auf der Karte)'],
         'nachteile': ['Langsamste Pipeline: drei Läufe, GEM und GEM-X nacheinander auf der GPU (348 s)',
                       'Finger sitzen an GEMs Handgelenk, gerechnet hat sie GEM-X an seinem eigenen — '
                       'die Handgelenke der beiden weichen um die Deckungsdifferenz voneinander ab',
                       'Wurzel und Boden wie GEM-SMPL; Lizenz NVIDIA OneWay'],
         'begruendung': 'Derselbe Körper wie GEM-SMPL (Deckung und Ruhe gleich), dazu Finger, deren '
                        'Güte gemessen ist, und ein Gesicht. Nach den vier Kriterien Rang 1 — die '
                        'Dauer zählt zuletzt.'},
        {'schluessel': 'hybrid_gem', 'art': 'Hybrid', 'rang': 4,
         'verfahren': 'Körper aus GEM-SMPL, daneben MocapNET v4 für Gesicht und Hände; zwei '
                      'BVH-Dateien, die der Viewer zusammenführt. Neu am 12.09.2026.',
         'gelenke': 24, 'haende': True, 'gesicht': True, 'kamera': 'statisch (Kameraraum)',
         'dauer_s': 171, 'ueberlagerung_px': 24.5, 'ruhe_wurzel': 3.1, 'ruhe_pose': 0.25,
         'boden_cm': -103, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Der GEM-SMPL-Körper (24,5 px) plus Gesicht und Hände',
                      'v4 läuft parallel auf der CPU — nur 60 s länger als GEM-SMPL allein'],
         'nachteile': ['Hände aus MocapNET v4 (MediaPipe) — hier nicht gemessen (keine Referenz)',
                       'Wurzel und Boden wie GEM-SMPL; Lizenz NVIDIA OneWay'],
         'begruendung': 'Wie GEM-SMPL plus Gesicht und Hände, aber die Hände sind ungemessen — '
                        'deshalb hinter GEM-X, dessen Finger gemessen sind, und hinter dem '
                        'Hybrid mit GEM-X-Fingern.'},
        {'schluessel': 'gem', 'art': '3D', 'rang': 2,
         'verfahren': 'GEM (NVIDIA, ICCV 2025, vormals GENMO) — auf dem GVHMR-Code aufgebaut, '
                      'dieselbe Vorstufe (YOLO-Spur, ViTPose, HMR2-Merkmale), rund 0,5 Mrd. Parameter; '
                      'Paperwerte EMDB-2 74,3 mm gegen GVHMR 111,0 mm (WA-MPJPE).',
         'gelenke': 24, 'haende': False, 'gesicht': False, 'kamera': 'statisch (Kameraraum)',
         'dauer_s': 111, 'ueberlagerung_px': 24.5, 'ruhe_wurzel': 3.1, 'ruhe_pose': 0.22,
         'boden_cm': -103, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Ruhigste Pose der SMPL-Familie (0,22)',
                      'Deckung mit dem Video wie GVHMR (24,5 px)',
                      'Schnellste SMPL-Pipeline (111 s)'],
         'nachteile': ['Wurzel zittert wie GVHMR (3,1 cm/Bild²)',
                       'Boden nicht bei y = 0 — Figur steht im Kameraraum',
                       'Keine Hände, kein Gesicht',
                       'Lizenz NVIDIA OneWay: nicht-kommerziell'],
         'begruendung': 'Gleiche Deckung wie GVHMR, aber die ruhigere Pose und ein Drittel '
                        'weniger Zeit. Was GVHMR kann, kann GEM-SMPL hier auch — nur schneller.'},
        {'schluessel': 'gvhmr', 'art': '3D', 'rang': 5,
         'verfahren': 'GVHMR (Shen u. a., SIGGRAPH Asia 2024) — ViTPose + HMR2-Merkmale, Transformer '
                      'über die Sequenz, SMPL in Kamera- und schwerkraftausgerichteten Weltkoordinaten.',
         'gelenke': 24, 'haende': False, 'gesicht': False,
         'kamera': 'statisch oder bewegt (DPVO-SLAM)',
         'dauer_s': 159, 'ueberlagerung_px': 23.4, 'ruhe_wurzel': 3.4, 'ruhe_pose': 0.26,
         'boden_cm': -103, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Beste Deckung mit dem Video (23,4 px)',
                      'Bewährter Referenzweg, auch für bewegte Kameras (SLAM)',
                      'Bildweise Vorstufe auch für lange Videos'],
         'nachteile': ['Wurzel zittert (3,4 cm/Bild²) — die 6 m „Hüftweg" sind Rauschen',
                       'Boden nicht bei y = 0',
                       'Langsamste laufende 3D-Pipeline (159 s)', 'Keine Hände, kein Gesicht'],
         'begruendung': 'Die Referenz: beste Deckung, robust, mit Kameraverfolgung. Hinter GEM-SMPL '
                        'wegen der etwas unruhigeren Pose und der längeren Laufzeit, hinter GEM-X '
                        '(σ 4) wegen der Finger bei gleicher Ruhe.'},
        {'schluessel': 'hybrid_gvhmr', 'art': 'Hybrid', 'rang': 6,
         'verfahren': 'Körper aus GVHMR, danach MocapNET v4 für Gesicht und Hände; zwei BVH-Dateien, '
                      'die der Viewer zusammenführt.',
         'gelenke': 24, 'haende': True, 'gesicht': True,
         'kamera': 'statisch oder bewegt (DPVO-SLAM)',
         'dauer_s': 145, 'ueberlagerung_px': 23.4, 'ruhe_wurzel': 3.4, 'ruhe_pose': 0.26,
         'boden_cm': -103, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Vollständigste Ausgabe: Körper, Gesicht, Hände',
                      'Körper ist bitgleich GVHMR (23,4 px)'],
         'nachteile': ['Zwei Läufe hintereinander (145 s)',
                       'Gesicht und Hände kommen aus MocapNET v4 — hier nicht gemessen (keine Referenz)',
                       'Wurzel und Boden wie GVHMR'],
         'begruendung': 'Derselbe Körper wie GVHMR plus Gesicht und Hände. Hinter GVHMR, weil die '
                        'Zugabe aus MocapNET v4 stammt und ihre Güte hier niemand gemessen hat.'},
        {'schluessel': 'gemx', 'art': '3D', 'rang': 3,
         'verfahren': 'GEM-X (NVIDIA, Gewichte `nvidia/GEM-X`, 6,7 GB) — GEM mit dem SOMA-'
                      'Körpermodell (77 Gelenke mit Fingern), Mixamo-Namen im BVH; Kameraraum '
                      'um x gedreht wie bei GVHMR. Glättung σ 4 (Standard seit 12.09.2026).',
         'gelenke': 77, 'haende': True, 'gesicht': False, 'kamera': 'statisch (Kameraraum)',
         'dauer_s': 149, 'ueberlagerung_px': 25.1, 'ruhe_wurzel': 3.6, 'ruhe_pose': 0.25,
         'boden_cm': -98, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Finger im BVH (77 Gelenke, 38 davon Finger), Retarget legt sie auf 30 DEF-Knochen',
                      'Deckung wie die SMPL-Familie (25,1 px, Median 19,3)',
                      'Mit σ 4 so ruhig wie GVHMR: Körpergelenke 0,21 cm/Bild² (GEM 0,20, GVHMR 0,23), '
                      'Finger 0,28 — bei σ 2 waren es 0,31 und 0,42, die Deckung blieb (25,0 → 25,1 px)'],
         'nachteile': ['„Ruhe Pose" 0,25 mittelt über alle 77 Gelenke, die Finger zittern mit',
                       'Geglättete Weltbahn (ayfz-Rahmen) bleibt ungenutzt — Kameraraum, Wurzel zittert',
                       '149 s, kein Gesicht, 6,7 GB Gewichte',
                       'Lizenz NVIDIA OneWay: nicht-kommerziell'],
         'begruendung': 'Die einzige eigenständige SMPL-Pipeline mit Fingern; seit σ 4 ist der '
                        'Körper so ruhig wie GEM-SMPL und GVHMR bei gleicher Deckung. Hinter GEM-SMPL '
                        'nur wegen 0,6 px weniger Deckung und 40 s mehr; vor GVHMR wegen der Finger.'},
        {'schluessel': 'duomo', 'art': '3D', 'rang': 7,
         'verfahren': 'DuoMo (Meta, CVPR 2026) — Diffusionsmodell über die Bewegung mit PromptHMR-'
                      'Bildmerkmalen und dichten 2D-Punkten; Netz (LOD6) in Kamera- und Weltraum, '
                      'daraus SMPL-X, daraus SMPL.',
         'gelenke': 24, 'haende': False, 'gesicht': False,
         'kamera': 'statisch (Weltraum, Boden bei y = 0)',
         'dauer_s': 50, 'ueberlagerung_px': 41.6, 'ruhe_wurzel': 0.2, 'ruhe_pose': 0.25,
         'boden_cm': 11, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Ruhigste Wurzelbahn aller Pipelines (0,2 cm/Bild²)',
                      'Boden bei y = 0, physikalisch plausible Weltbahn',
                      'Schnellste 3D-Pipeline (50 s)'],
         'nachteile': ['Weltbahn weicht von der Kamerabahn ab: Deckung 41,6 px mit statischer Kamera, '
                       'bis 0,85 m Versatz über 5 s',
                       '2,3-GB-PromptHMR-Checkpoint nur über den angemeldeten Browser (Drive-Quota)',
                       'Blackwell-Sonderwege: xformers-Kernel abschalten, kein Rendern unter Windows',
                       'Keine Hände, kein Gesicht'],
         'begruendung': 'Nach den Kriterien dieser Messung Rang 7, weil die Deckung mit dem Video '
                        'am schlechtesten ist. Wer eine ruhige Weltbahn mit Bodenkontakt braucht, '
                        'nimmt trotzdem DuoMo — das kann hier sonst keine.'},
        {'schluessel': 'v4', 'art': '3D', 'rang': 8,
         'verfahren': 'MocapNET v4 (Qammaz & Argyros, FORTH) — MediaPipe Holistic, Ensemble kleiner '
                      'Netze (ONNX), native IK (HCD) gegen die 2D-Punkte; volles Rig mit Gesicht, '
                      'Händen und Zehen.',
         'gelenke': 165, 'haende': True, 'gesicht': True, 'kamera': 'statisch (MocapNET-Kamera)',
         'dauer_s': 46, 'ueberlagerung_px': 31.6, 'ruhe_wurzel': 0.55, 'ruhe_pose': 1.02,
         'boden_cm': -90, 'zustand': 'laeuft', 'zustand_grund': '',
         'vorteile': ['Schnell (46 s), läuft ohne CUDA-Bibliotheken (ONNX)',
                      'Volles Rig: Gesicht, Hände, Zehen in einer Datei',
                      'Median der Deckung so gut wie SMPL (21 px)'],
         'nachteile': ['Pose viermal so unruhig wie die SMPL-Familie (1,0 cm/Bild²)',
                       'z zur SMPL-Familie gespiegelt (MocapNET-Konvention)',
                       'Native IK überlief unter Windows den Stack — Fix nur lokal im Klon'],
         'begruendung': 'Schnell und vollständig, aber die Pose zittert; die Deckung ist im Mittel '
                        'schlechter als bei SMPL (31,6 px), im Median gleich.'},
        {'schluessel': 'hybrid_prompthmr', 'art': 'Hybrid', 'rang': None,
         'verfahren': 'Körper aus PromptHMR, Gesicht und Hände aus MocapNET v4.',
         'gelenke': None, 'haende': True, 'gesicht': True,
         'kamera': 'statisch oder bewegt (DROID-SLAM)',
         'dauer_s': 46, 'ueberlagerung_px': None, 'ruhe_wurzel': None, 'ruhe_pose': None,
         'boden_cm': None, 'zustand': 'teilweise',
         'zustand_grund': 'Der Körperteil scheitert wie PromptHMR (`gloss` fehlt); übrig bleibt nur '
                          'das Gesicht aus MocapNET v4 („partial").',
         'vorteile': ['Wäre die vollständige Ausgabe mit PromptHMRs Körper'],
         'nachteile': ['Läuft hier nur zur Hälfte: kein Körper'],
         'begruendung': 'Ohne Körper kein Vergleich, deshalb kein Rang.'},
        {'schluessel': 'prompthmr', 'art': '3D', 'rang': None,
         'verfahren': 'PromptHMR (2025) — promptbare Körperschätzung (Boxen, Text), Kamera aus DROID-SLAM.',
         'gelenke': None, 'haende': False, 'gesicht': False,
         'kamera': 'statisch oder bewegt (DROID-SLAM)',
         'dauer_s': 21, 'ueberlagerung_px': None, 'ruhe_wurzel': None, 'ruhe_pose': None,
         'boden_cm': None, 'zustand': 'gescheitert',
         'zustand_grund': 'Bricht nach 21 s ab: das Modul `gloss` (gloss-rs) fehlt in python10.',
         'vorteile': ['Liefert dem DuoMo-Weg den Bildkodierer (Checkpoint vorhanden)'],
         'nachteile': ['Läuft hier nicht'],
         'begruendung': 'Kein Ergebnis, deshalb kein Rang.'},
        {'schluessel': 'wham', 'art': '3D', 'rang': None,
         'verfahren': 'WHAM (Shin u. a., CVPR 2024) — 2D-Spur + Bildmerkmale, SMPL in Weltkoordinaten '
                      'mit Fußkontakt.',
         'gelenke': None, 'haende': False, 'gesicht': False,
         'kamera': 'statisch oder bewegt (DPVO-SLAM)',
         'dauer_s': 14, 'ueberlagerung_px': None, 'ruhe_wurzel': None, 'ruhe_pose': None,
         'boden_cm': None, 'zustand': 'gescheitert',
         'zustand_grund': 'Bricht nach 14 s ab: xtcocotools ist gegen ein anderes numpy gebaut '
                          '(„dtype size changed"), und die Checkpoints fehlen.',
         'vorteile': ['Fußkontakt und Weltbahn — auf dem Papier'],
         'nachteile': ['Läuft hier nicht'],
         'begruendung': 'Kein Ergebnis, deshalb kein Rang.'},
    ]
