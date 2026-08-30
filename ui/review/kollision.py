# -*- coding: utf-8 -*-
"""Review-Bereiche: Stoffsimulation und Kollision

Warp auf der GPU, die Brücke aus dem Browser, Rendern.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'warp', 'name': 'Stoffsimulation (Warp, GPU)',
     'dateien': ['HumanBody/collision/warp_sim.py',
                 'HumanBody/collision/warp_only.py'],
     'hinweis': (
         'Läuft als eigener Prozess in Python 3.10 (warp-lang 1.4.2, letzte '
         'Fassung mit warp.sim) und wird von Django (3.14) gestartet. Simuliert '
         'Kleidung auf dem Körper: Partikel mit Federn, Kollision gegen das '
         'Körpernetz, Zeitschritte mit Unterschritten. Maße in Metern, Y ist '
         'oben, ein Zeitschritt ist typisch 1/30 s mit mehreren Unterschritten. '
         'Fehler zeigen sich als explodierendes Netz, durchfallender Stoff oder '
         'als Simulation, die scheinbar läuft und nichts bewegt.'),
     'fragen': [
         'Wo hängt das Ergebnis von der Schrittweite ab, ohne dass es soll — '
         'und welche Kombination aus Zeitschritt, Unterschritten und '
         'Federsteifigkeit lässt es explodieren?',
         'Kollision: Wird gegen Dreiecke oder nur gegen Vertices geprüft? Was '
         'passiert bei schnellen Bewegungen (Durchtunneln)?',
         'Was passiert, wenn die Grafikkarte den Speicher nicht hergibt oder '
         'Warp fehlt — bricht es ab oder liefert es stillschweigend die '
         'Eingabe zurück?',
         'Welche Einheiten werden gemischt (Meter/Zentimeter, Sekunden/Frames)?',
     ]},
    {'slug': 'coll_bridge', 'name': 'Kollision: Brücke vom Browser zur Pipeline',
     'dateien': ['HumanBody/collision/bridge.py', 'HumanBody/collision/scene_input.py'],
     'hinweis': ('Der Browser schickt eine ganze Szene als JSON: Netze base64-kodiert '
                 '(Float32/Uint32), Skelett-Matrizen, Animationsspuren, '
                 'Kleidungsteile. '
                 'bridge.payload_to_scene_input baut daraus SceneInput; das wird als '
                 '.npz '
                 'gespeichert und von einem Python-3.10-Unterprozess wieder geladen. '
                 'Alles '
                 'hier kommt aus einer HTTP-Anfrage. Ich kann diesen Code ausfuehren '
                 '(NumPy '
                 'vorhanden) und Messungen machen.'),
     'fragen': [
         ('Welche Eingabe laesst _b64_to_f32 oder _b64_to_u32 abstuerzen oder '
             'stillschweigend Unsinn liefern (Laenge kein Vielfaches von 4, falsches '
             'base64, leerer String)? Ich pruefe das nach.'),
         ('Wo werden Feldlaengen NICHT gegeneinander geprueft (Vertexzahl gegen '
             'Gewichte, Knochenzahl gegen Matrizen, Framezahl gegen Spuren)?'),
         ('save_npz: Was passiert bei ungleich langen Spuren, und was liest der '
             'Unterprozess dann?'),
     ]},
    {'slug': 'coll_splitter', 'name': 'Kollision: Szene aufteilen, Ton anhängen',
     'dateien': ['HumanBody/collision/splitter.py', 'HumanBody/collision/audio_mux.py'],
     'hinweis': ('splitter.split_scene trennt die Szene in Koerper und Stoff und '
                 'bestimmt die '
                 'Pins (die festgehaltenen Stoffpunkte). audio_mux.mux_audio ruft '
                 'ffmpeg auf, '
                 'um Tonspuren unter das gerenderte Video zu legen; _resolve_url macht '
                 'aus '
                 'einer URL aus dem Browser einen Pfad auf der Platte. Ausfuehrbar.'),
     'fragen': [
         ('_resolve_url: Welche URL fuehrt aus dem Medienverzeichnis heraus? Nenne die '
             'Zeichenkette, ich probiere sie aus.'),
         ('compute_pin_group: Was, wenn keine Pins gefunden werden oder alle Punkte '
             'Pins sind — merkt das jemand, oder simuliert die GPU dann Unsinn?'),
         ('mux_audio ruft ffmpeg mit Werten aus dem Browser auf. Wo landet etwas in '
             'einer Kommandozeile, das dort nicht hingehoert?'),
     ]},
    {'slug': 'coll_skinning', 'name': 'Kollision: rigides Skinning und Body-Push-Out',
     'dateien': ['HumanBody/collision/skinning_only.py',
                 'HumanBody/collision/skinning_blender.py'],
     'hinweis': ('Die schnellste der vier Pipelines: keine Stoffsimulation, sondern '
                 'der Stoff '
                 'wird mitbewegt (rigid skinning) und danach aus dem Koerper geschoben '
                 '(_push_outside_body). Die Kernrechnung ist reines NumPy und laeuft '
                 'je Frame '
                 'ueber alle Vertices. Ausfuehrbar und MESSBAR — nenne Groessen, ich '
                 'messe.'),
     'fragen': [
         ('_skin_rigid_frame: Ist die Reihenfolge inv_bind mal frame_mat richtig, oder '
             'ist sie vertauscht? Woran wuerde man es im Bild sehen?'),
         ('_push_outside_body arbeitet mit Normalen des Koerpers und einer Marge. In '
             'welcher Lage schiebt das den Stoff IN den Koerper statt heraus?'),
         ('Wo ist die Schleife unnoetig quadratisch, und was kostet das bei 70.000 '
             'Vertices und 300 Frames?'),
     ]},
    {'slug': 'coll_render', 'name': 'Kollision: Bilder rendern (pyrender und Blender)',
     'dateien': ['HumanBody/collision/warp_render.py',
                 'HumanBody/collision/blender_render_from_bake.py'],
     'hinweis': ('Zwei Renderwege aus derselben Bake-Datei: pyrender offscreen (Python '
                 '3.14) '
                 'und Blender im Hintergrund. Beide bauen Kamera und Licht aus '
                 'derselben '
                 'Nutzlast, und beide rechnen zwischen Y-oben (Three.js) und Z-oben '
                 '(Blender) '
                 'um. Zwei Wege, dieselbe Kamera — wenn die Umrechnung an einer Stelle '
                 'anders '
                 'ist, sehen die Videos verschieden aus. warp_render ist ausfuehrbar.'),
     'fragen': [
         ('Vergleiche _pose_from_camera_matrix (pyrender) mit _yup_to_zup_mat44 und '
             'setup_camera_from_payload (Blender): Wo weichen sie inhaltlich ab?'),
         ('_fit_camera bei entarteten Eingaben (ein Punkt, NaN, leere Liste) — was '
             'kommt heraus?'),
         ('mux_ffmpeg und render_bake: Was bleibt liegen, wenn der Aufruf mitten drin '
             'abbricht (Frames, Prozesse, Speicher)?'),
     ]},
]
