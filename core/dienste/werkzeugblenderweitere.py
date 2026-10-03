# -*- coding: utf-8 -*-
"""Werkzeugblenderweitere — Gruppe „Weitere an Blender angelehnte Werkzeuge“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Gesucht wurde in Code und Regeln nach „Blender“ und „MPFB“; aufgenommen ist nur, was es gibt und was nicht schon in der Gruppe
„Stoffsolver …“ oder „Schleifen über Blender“ steht. Quellen: `templates/hilfe/kopf_pipelines_2d3dblender.html` (Abschnitt „Was von Blender übernommen ist“, Stand 01.10.2026),
`.claude/rules/ortsmorphe.md`, `figurnetz.md`, `effekte.md`; die Rezeptnamen sind gegen `Genesis9/` geprüft."""

__all__ = ['Werkzeugblenderweitere']

H = 'HumanBody/humanbody_core/'
M = 'HumanBodyWeb/TheatreJS/ModelPhysik/'
E = 'HumanBodyWeb/effekte/blender/'


class Werkzeugblenderweitere:
    KENNUNG = 'blenderweitere'
    TITEL = 'Weitere an Blender angelehnte Werkzeuge'
    EINLEITUNG = (
        'Neben dem Stoffsolver und den Blender-Schleifen gibt es drei Arten von Blender-Bezug: Funktionen, die in Python nachgebaut sind und als Rezeptzeilen laufen (die Zuordnung steht in '
        'der ersten Zeile; die Aufrufe selbst in den Gruppen zu Körper, Kleidung und Haar), MB-Lab-Modifier in NumPy für den Film der HumanBody-Figur, und die Effekte-Pipeline „Kleid + Wind“, '
        'die Blender als Prozess startet. Was nicht an Fotos oder an Genesis 9 hängt, sagt der Hinweis ausdrücklich. Blender-Läufe nur nach Ansage von Edgar.')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Blender-Funktion → Rezeptzeile (Zuordnung)',
         'Nachschlagen, welche Blender-Funktion in der Pipeline welche Rezeptzeile hat — damit man das Werkzeug findet, wenn man Blender kennt.',
         'regel',
         'Kein eigener Aufruf: die Rezeptzeilen m.<funktion>(…) stehen mit Argumenten in den Gruppen zu Körper, Kleidung und Haar; die Funktionen sind gegen Genesis9/ geprüft.',
         [],
         'Form: Shape Keys → morph_neu, morph_wert (eigene Morphe eigen.<name>); Lattice, Hook, Laplacian Deform, Warp → morph_ort, koerper_ort; Shrinkwrap (Ziel Netz) → kleid_huelle, '
         'koerper_huelle (Sichtkörper der Fotos); Wave, Displace → kleid_welle; Cloth → kleid_drapieren (motor newton | blender | stoffsolver); Sculpt → Knopf „Formen“ auf der Bühne (eigener Morph); '
         'Armature, Pose → haltung, haltung_gelenk. Haar: Hair Nodes Trim, Clump, Noise, Straighten, Displace → haar_trim, haar_clump, haar_noise, haar_straighten, haar_biegen, haar_anlegen '
         '(Python, auch Kartenhaar); Curl, Braid → haar_curl, haar_braid; Duplicate, Interpolate → haar_duplizieren, haar_interpolieren; Set Hair Curve Profile → haar_profil; alle Hair-Node-Gruppen '
         '→ haar_knoten (Blender, nur Stranghaar, Gruppe „Schleifen über Blender“); Haar-Dynamik → haar_dynamik (Stoffsolver). Textur: Project Image → kleid_fototextur, haar_fototextur; Texture '
         'Paint → kleid_decal und Knopf „Malen“; Multires + Bake → kleid_falten, kleid_falten_backen. Kleid: Garment Tool → kleid_schnitt (GarmentCode). Foto und Render: fSpy → Blickwinkel '
         'aus der Pose (Blickwinkelschaetzung), FaceBuilder → Gesichtsmaße (Gesichtsmasse), Cycles → Mitsuba 3. Was Blender nicht hat und unser Code ist: Sichtkörper, kleid_ring, Befund, Noten, '
         'Automatik, Rezept als Text, Mischung nach Ort (haar_anteil mit ort). Stand: kopf_pipelines_2d3dblender.html, 01.10.2026 nachmittags; jede Funktion mindestens einmal an echten Daten '
         'gemessen, Zahlen dort.'),
        ('Körperfeinheit im Film: Corrective Smooth, Unterteilung, Displace (MB-Lab-Modifier)',
         'Die drei Modifier, die MB-Lab an die Figur hängt und die Blender in C++ rechnet, als NumPy-Nachbau: den Körper glätten, unterteilen und mit der Hauttextur verschieben.',
         'python',
         '\n'.join((
             "fein = Koerperfeinheit(unterteiler, vierecke, verschiebung=<(H, W)-Textur 0..1 oder None>, korrektur=True)    # unterteiler = CatmullClarkSubdivider",
             "fein.anlegen(punkte_ruhe, gewichte, namen)         # Corrective Smooth an der Ruhelage, Kopf ausgenommen (Kopfmaske aus den Knochennamen)",
             "punkte = fein.punkte(basis, basis_dreiecke)        # je Bild: glätten → unterteilen → Haut entlang der Normale verschieben")),
         [(M + 'koerperfeinheit.py', 'Koerperfeinheit'), (H + 'korrekturglaettung.py', 'Korrekturglaettung'), (H + 'catmull_clark.py', 'CatmullClarkSubdivider'),
          (H + 'hautverschiebung.py', 'Hautverschiebung')],
         'Gilt für die HumanBody-Figur (MB-Lab-Basis, 18.210 Basispunkte), nicht für Genesis 9, und nur im Film (Server-Videoweg ModelPhysik/filmlauf.py); im Browser häutet die GPU ohne '
         'Glättung. Corrective Smooth SIMPLE wie MB-Lab: Faktor 0,5, 5 Durchgänge, Deltas im Tangentenraum (MOD_correctivesmooth.cc), alles außer dem Kopf. Hautverschiebung: wert = R + alter · '
         '(G − 0,5) + tonus⁺ · (B − 0,5) + (1 − tonus⁺) · masse · (A − 0,5), Verschiebung (wert − 0,5) · 0,01 m entlang der Normale. Zeiten (figurnetz.md, 17.09.2026, weiblich): Aufbau der '
         'Unterteilung 1 Stufe 2,7 s, 2 Stufen 12,8 s, 3 Stufen 57 s, mit Ablage Laden 0,02, 0,06 und 0,29 s; Film mit 12 Bildern, 3 Stufen und Verschiebung 69,5 s. Ein Vergleich gegen Blenders '
         'Modifier steht in der Regeldatei nicht (die Nachbauten sind nach dem Quelltext gebaut). Kein Blender-Lauf nötig.'),
        ('Kleid + Wind (Process Videos → Effekte, Blender Cloth mit MPFB-Figur)',
         'Ein BVH auf eine MPFB-Figur mit Kleid übertragen, den Stoff in Blender simulieren (Cloth, Kollider, Wind) und als MP4 rendern — ein Offline-Video.',
         'seite',
         '\n'.join((
             'Process Videos → Effekte → Pipeline „Kleid + Wind“ (core/api/effekte.py); der Server baut den Befehl (Effektbefehl):',
             'blender -b --python effekte/blender/kleidwind.py -- --bvh … --kleid … --ausgabe … [--bilder 300 …]')),
         [(E + 'kleidwind.py', 'Kleidwindlauf'), (E + 'effektfigur.py', 'Effektfigur'), (E + 'bvhretarget.py', 'Bvhretarget'), (E + 'stoffsimulation.py', 'Stoffsimulation'),
          (E + 'effektrender.py', 'Effektrender')],
         'NUR NACH ANSAGE VON EDGAR (startet Blender). Für MPFB-Figuren mit DEF-/CMU-Rig, nicht für Genesis 9, und nur fürs Offline-Video: im Theatre bleibt Newton (effekte.md, Edgar '
         '10.09.2026); der Weg ohne Blender ist effekte/figur/ (pyrender und Newton). Ablauf: 1. Figur (MPFB 2.0.14 mit Rig cmu_mb, Kleid aus der Kleiderbibliothek), 2. Retarget der BVH '
         '(BVH Retargeter), 3. Stoff (Anker, Unterteilung, Cloth, Kollider, Wind, Bild für Bild), 4. Rendern (Workbench → MP4), daneben .blend und .json mit den Zahlen. Fallen (effekte.md, '
         '12.09.2026, 002_Dance, 300 Bilder): MPFBs Delete.<kleid>-Maske nimmt dem Kollider Hüfte und Oberschenkel → Maske entfernen; Selbstkollisionsabstand 6 mm auf dem unterteilten Netz → je '
         'Stufe halbieren (3 mm); Wind 6 wickelt den Rock um die Hüfte → 2; Reibung 5 hält den Saum am Knie → 1; Blender 5.0: image_settings.media_type = \'VIDEO\' vor file_format = \'FFMPEG\'. '
         'Retarget 6,2 s statt 33,1 s mit useAllFrames = False. Fortschritt nur aus den Zeilen „Effekte: …“. Blender Cloth war auf denselben Daten schlechter als Newton (Knick 35–47°, Rock über '
         'der Hüfte; effekte.md): kein Grund, dorthin zurückzugehen.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Koerperfeinheit', 'ruft', 'Korrekturglaettung', 'Korrekturglaettung(vierecke, gewichte=).ruhelage(punkte_ruhe); anwenden(basis) je Bild'),
        ('Koerperfeinheit', 'ruft', 'CatmullClarkSubdivider', 'subdivide(basis): die Unterteilung als Matrixprodukt W @ basis'),
        ('Koerperfeinheit', 'ruft', 'Hautverschiebung', 'anwenden(fein, normalen, uvs, textur, staerke=, …): Verschiebung entlang der Normale'),
        ('Kleidwindlauf', 'ruft', 'Effektfigur', 'Effektfigur(geschlechtswert).bauen(kleid): die MPFB-Figur mit Rig und Kleid'),
        ('Kleidwindlauf', 'ruft', 'Bvhretarget', 'Bvhretarget(figur, bvh, ordner, bilder).fahren(): die BVH auf das Rig'),
        ('Kleidwindlauf', 'ruft', 'Stoffsimulation', 'Stoffsimulation(figur, parameter, melden): aufbauen() und rechnen(bilder)'),
        ('Kleidwindlauf', 'ruft', 'Effektrender', 'kamera_setzen(), boden_setzen(), einstellen(ausgabe), rendern(gesamt, bilder)'),
    ]
