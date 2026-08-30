# -*- coding: utf-8 -*-
"""Review-Bereiche: Video nach BVH

2D-Erkennung, 3D-Lifting, Foto-Analyse — die ML-Kette.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'lifting', 'name': 'Video-nach-BVH: 3D-Lifting (GVHMR)',
     'dateien': ['VideoToBVH/wrappers/gvhmr_lift.py'],
     'hinweis': (
         'Nimmt die Ausgabe von GVHMR (SMPL-Parameter je Frame, Weltkoordinaten '
         'aus einem Video) und schreibt daraus eine BVH-Datei. Zwei Dinge sind '
         'hier historisch schmerzhaft: Die Frame-0-Drehungen werden auf die '
         'Einheitsdrehung normalisiert (Delta), damit das Retarget damit '
         'umgehen kann — und die Konventionen (Y-oben gegen Z-oben, Grad gegen '
         'Radiant, Euler-Reihenfolge, Bildrate) müssen zwischen SMPL, GVHMR und '
         'BVH zusammenpassen. Ein Vorzeichen daneben und die Figur läuft '
         'rückwärts oder liegt.'),
     'fragen': [
         'Prüfe die Achsen- und Vorzeichen-Umrechnung Schritt für Schritt. Wo '
         'wird eine Drehung wie ein Punkt behandelt (oder umgekehrt)?',
         'Die Delta-Normalisierung auf Frame 0: Was passiert, wenn Frame 0 '
         'unbrauchbar ist (Person halb im Bild, Erkennung wackelt)?',
         'Bildrate und Frame-Zeit: Woher kommt der Wert, und was passiert bei '
         'variabler Bildrate im Video?',
         'Wurzel-Verschiebung: Wird sie skaliert, und passt die Einheit zum '
         'BVH-Kopf?',
     ]},
    {'slug': 'vtb_detect', 'name': 'VideoToBVH: 2D-Erkennung und Lifting-Wrapper',
     'dateien': ['VideoToBVH/wrappers/detect_2d.py', 'VideoToBVH/wrappers/yolo_det.py',
                 'VideoToBVH/wrappers/wham_lift.py'],
     'hinweis': ('Diese Skripte laufen als Subprozess in Python 3.10 und schreiben '
                 'ihren Fortschritt auf stdout, den Django zeilenweise liest '
                 '(TOTAL:/STATUS:). Sie erwarten Modellgewichte auf der Platte. Seit '
                 '13.08.2026 gilt: Bleibt die Ausgabe zu lange aus, beendet die '
                 'aufrufende Seite den Prozess.'),
     'fragen': [
         'Fortschrittsausgabe: Wird sie zuverlaessig geleert (flush), und gibt es '
         'Phasen, in denen minutenlang nichts kommt?',
         'Was passiert bei einem Video ohne erkannte Person, bei einem Frame ohne '
         'Erkennung, und bei mehreren Personen?',
         'Kann das Skript mit Rueckgabewert 0 enden, ohne eine brauchbare Ausgabe '
         'geschrieben zu haben?',
     ]},
    {'slug': 'vtb_smplestx', 'name': 'VideoToBVH: SMPLest-X (Körperschätzung)',
     'dateien': ['VideoToBVH/wrappers/smplest_x_wrapper.py',
                 'VideoToBVH/wrappers/_run_smplest_x.py'],
     'hinweis': ('Der Wrapper startet einen Unterprozess (Python 3.10, CUDA) und liest '
                 'dessen '
                 'Ausgabe; das Ergebnis sind SMPL-X-Parameter je Frame. Bekannt und '
                 'mehrfach '
                 'gefunden: SMPL hat 6.890 Vertices, SMPL-X 10.475 — die Topologien '
                 'sind '
                 'unvereinbar, und ein Netz mit der falschen Zahl darf nicht '
                 'durchrutschen. '
                 'Ebenfalls bekannt: Ein Unterprozess, dessen Ausgabe niemand abholt, '
                 'laeuft '
                 'in einen vollen Puffer und haengt (im Projekt schon einmal passiert, '
                 'behoben '
                 'durch einen Leerlese-Faden).'),
     'fragen': [
         ('Wird die Ausgabe des Unterprozesses waehrend des Laufs abgeholt, oder erst '
             'am Ende? Wo kann er haengen bleiben?'),
         ('Wo wird die Vertex- oder Gelenkzahl NICHT geprueft, bevor damit gerechnet '
             'wird?'),
         ('Was passiert bei einem Video ohne erkannte Person, bei mehreren Personen '
          'und '
             'bei einem Frame ohne Erkennung — Luecke, Sprung oder Absturz?'),
     ]},
    {'slug': 'vtb_foto', 'name': 'VideoToBVH: Foto-Analyse und 2D-Erkennung',
     'dateien': ['VideoToBVH/wrappers/mediapipe_photo.py',
                 'VideoToBVH/wrappers/photo_analyzer.py',
                 'VideoToBVH/wrappers/rtmpose_det.py'],
     'hinweis': ('Aus einem Foto Koerpermasse schaetzen: MediaPipe findet Landmarken, '
                 'photo_analyzer rechnet daraus Masse, rtmpose_det ist der zweite '
                 'Erkennungsweg (ONNX Runtime GPU). MediaPipe hat mp.solutions ab '
                 '0.10.30 '
                 'entfernt; dafuer gibt es hier eine eigene Anpassung '
                 '(mediapipe_compat, '
                 'Tasks-API). Landmarken sind normiert (0..1) — wer sie mit Pixeln '
                 'verwechselt, bekommt Masse, die um Faktor Bildbreite falsch sind.'),
     'fragen': [
         ('Wo werden normierte Koordinaten und Pixel verwechselt, und wo fehlt die '
             'Umrechnung mit dem Seitenverhaeltnis?'),
         ('photo_analyzer rechnet Masse aus Abstaenden. Welche Annahme ueber die '
             'Koerperhaltung steckt darin, und was liefert sie bei einem schraegen '
             'oder '
             'sitzenden Menschen?'),
         ('Was passiert bei einem Foto ohne Person, mit zwei Personen oder mit '
             'abgeschnittenen Beinen?'),
     ]},
]
