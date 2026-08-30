# -*- coding: utf-8 -*-
"""Review-Bereiche: das Blender-Addon

Läuft in Blenders Python, nicht im Server — eigene Fehlerklassen
(Handler, Timer, bpy-Kontext).

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'blender', 'name': 'Blender-Addon: Rig und Operatoren',
     'dateien': ['HumanBodyBlender/rig.py', 'HumanBodyBlender/operators.py'],
     'hinweis': (
         'Blender-5.0-Addon (bpy), das dieselbe Kern-Bibliothek benutzt wie die '
         'Webapp (`sys.path.insert` auf HumanBody/). Operatoren laufen im '
         'Blender-Hauptfaden; ein Fehler darin reisst im besten Fall den '
         'Aufruf ab, im schlechteren hinterlaesst er die Szene halb verändert — '
         'Blender kennt keine Transaktion. Wichtig zu wissen: KEIN Operator in '
         'diesen beiden Dateien hat eine `poll`-Methode (11 von 11 geprüft), '
         'die Knöpfe sind also immer klickbar, auch ohne passende Auswahl. '
         'Ich kann hier NICHT ausführen — es gibt kein bpy ausserhalb von '
         'Blender. Argumentiere aus dem Code, und sag es, wenn du etwas nur '
         'in Blender selbst entscheiden könntest.'),
     'fragen': [
         'Welcher Operator hinterlässt die Szene halb verändert, wenn er '
         'mittendrin scheitert? Nenne den Ablauf: was ist dann angelegt, was '
         'fehlt, und was passiert beim zweiten Klick darauf?',
         'Fehlendes `poll()`: Bei welchem Operator ist der Absturz bei falscher '
         'Auswahl (kein aktives Objekt, falscher Objekttyp, Objekt versteckt) am '
         'wahrscheinlichsten — und was wäre die richtige Bedingung?',
         'Wo wird der Zustand der Szene angefasst, ohne den Modus zu prüfen '
         '(Object/Edit/Pose)? Bewege-, Lösch- und Datenzugriffe verhalten sich '
         'je Modus verschieden.',
         'Wo werden Objekte, Meshes oder Armaturen erzeugt und bei einem Fehler '
         'nicht wieder entfernt (verwaiste Datenblöcke in der .blend-Datei)?',
     ]},
    {'slug': 'blender_cloth', 'name': 'Blender-Addon: Kleidungsbau',
     'dateien': [{'pfad': 'HumanBodyBlender/cloth_builder.py',
                  'funktionen': ['_create_garment', '_add_cloth', '_add_pin',
                                 '_bmesh_body_ring', '_transfer_bone_weights',
                                 '_create_prim_puffer', '_create_tpl_pants',
                                 'HUMANBODY_OT_cloth_prim_create']},
                 'HumanBodyBlender/wardrobe.py'],
     'hinweis': (
         'Baut Kleidung im Blender-Addon: Ringe aus dem Körpernetz über bmesh '
         'abnehmen, daraus ein Kleidungsnetz erzeugen, Blenders Cloth-Modifier '
         'und Pin-Vertexgruppen anlegen, Knochengewichte vom Körper übertragen. '
         'bmesh muss von Hand freigegeben werden (`bm.free()`), sonst bleibt '
         'Speicher liegen; ein `bmesh.from_edit_mesh` darf nicht wie ein '
         '`bmesh.new` behandelt werden. Blender kennt keine Transaktion: Was '
         'ein Operator bis zum Fehler angelegt hat, bleibt in der Datei. '
         'Ich kann hier NICHT ausführen (kein bpy ausserhalb von Blender) — '
         'argumentiere aus dem Code.'),
     'fragen': [
         'bmesh: Wo fehlt ein `free()` auf einem Fehlerpfad, und wo wird ein '
         'Edit-Mesh-bmesh falsch behandelt?',
         'Pin-Gruppen und Gewichtsübertragung: Was passiert, wenn Körper und '
         'Kleidung unterschiedlich viele Vertices haben oder die Zuordnung '
         'leer ausfällt?',
         '_create_garment ist die längste Funktion. Welcher Zwischenzustand '
         'bleibt bei einem Fehler in ihrer Mitte in der Szene stehen?',
         'Wo wird ein Name für ein Objekt oder eine Vertexgruppe gebildet, der '
         'kollidieren kann — und was macht Blender dann daraus?',
     ]},
    {'slug': 'blender_ui', 'name': 'Blender: Bedienfelder, Timer, Handler',
     'dateien': [{'pfad': 'HumanBodyBlender/ui.py',
                  'funktionen': ['HUMANBODY_OT_pick_part', '_deferred_mesh_update',
                                 '_on_depsgraph_update', 'register', 'unregister',
                                 '_draw_cloth_builder_body', '_draw_parts_body']}],
     'hinweis': ('Blender-Bedienfelder. Zwei Dinge laufen NEBEN der Bedienung: ein '
                 'Timer (bpy.app.timers.register, entprellte Morph-Aktualisierung) und '
                 'ein depsgraph_update_post-Handler; beide werden in register() '
                 'angehaengt. Ein Handler, der bei jeder Szenenaenderung laeuft und '
                 'selbst die Szene aendert, ruft sich wieder auf. Ein Timer, der beim '
                 'Deaktivieren des Addons nicht abgemeldet wird, laeuft weiter und '
                 'greift auf entfernte Klassen zu. Ich kann hier NICHT ausfuehren '
                 '(kein bpy ausserhalb von Blender).'),
     'fragen': [
         'Wird der Timer beim Deaktivieren zuverlaessig abgemeldet? Was, wenn er '
         'feuert, nachdem das Objekt geloescht oder der Modus gewechselt wurde?',
         'Wo kann sich der depsgraph-Handler selbst ausloesen, und was kostet er bei '
         'jeder Mausbewegung?',
         'HUMANBODY_OT_pick_part ist die laengste Funktion — welcher Zwischenzustand '
         'bleibt bei einem Fehler darin stehen?',
     ]},
    {'slug': 'blender_anim', 'name': 'Blender: Animation und BVH-Import',
     'dateien': [{'pfad': 'HumanBodyBlender/animation.py',
                  'funktionen': ['HUMANBODY_OT_load_bvh_native', '_load_cached_action',
                                 '_cleanup_old_anim', 'HUMANBODY_OT_load_animation',
                                 '_gen_walk']}],
     'hinweis': ('Laedt BVH ueber Blenders eigenen Importer, legt Actions an, raeumt '
                 'alte auf und erzeugt einfache Bewegungen rechnerisch. Actions und '
                 'NLA-Streifen sind eigene Datenbloecke: Wer sie nicht loest, sammelt '
                 'sie in der .blend-Datei. Ich kann hier NICHT ausfuehren.'),
     'fragen': [
         '_cleanup_old_anim: Was wird NICHT geloescht (Actions ohne Nutzer, '
         'NLA-Streifen, Fake-User)?',
         'Der Import laeuft ueber bpy.ops — was passiert bei einer Datei, die Blender '
         'nicht mag, und was bleibt dann in der Szene?',
         'Was, wenn die BVH-Frame-Zeit nicht zur Szenen-Bildrate passt?',
     ]},
    {'slug': 'blender_retarget', 'name': 'Blender: eigener Retargeter',
     'dateien': ['HumanBodyBlender/retarget.py'],
     'hinweis': ('Der DRITTE Retargeter im Projekt (neben '
                 'humanbody_core/skeleton/retarget.py und der JS-Seite). Ordnet '
                 'BVH-Knochen den DEF-Knochen zu und setzt Pose-Bone-Rotationen. In '
                 'Blender sind Knochendrehungen lokal in der Elternachse; '
                 'matrix_basis, matrix_channel und matrix_world sind verschiedene '
                 'Dinge. Fehler sehen wie eine unsaubere Animation aus, nicht wie ein '
                 'Fehler.'),
     'fragen': [
         'Wo wird eine Weltdrehung wie eine lokale behandelt (oder umgekehrt)?',
         'Wo weicht dieser Retargeter inhaltlich von der Python-Kernfassung ab — '
         'gleiche Zuordnung, gleiche Richtungskorrektur, gleicher Delta-Weg?',
         'Was passiert bei fehlenden Knochen und bei einer Armatur, die nicht im '
         'Pose-Modus ist?',
     ]},
    {'slug': 'blender_hair', 'name': 'Blender: Haare, Morphing, Charakteraufbau',
     'dateien': ['HumanBodyBlender/hair.py', 'HumanBodyBlender/morphing.py',
                 'HumanBodyBlender/human_body.py'],
     'hinweis': ('Haare als Partikel-/Kurvenobjekte, Morph-Anwendung im Addon, Aufbau '
                 'des Charakters. morphing.py benutzt dieselbe Kern-Bibliothek wie die '
                 'Webapp; dort ist bekannt, dass CharacterState.compute() einen '
                 'INTERNEN Puffer zurueckgibt, der beim naechsten Aufruf '
                 'ueberschrieben wird. Ich kann hier NICHT ausfuehren.'),
     'fragen': [
         'Wird das Ergebnis von compute() irgendwo festgehalten, obwohl es beim '
         'naechsten Aufruf ueberschrieben wird?',
         'Haare: Was bleibt liegen, wenn ein Haar-Objekt ersetzt wird?',
         'Wo werden Vertex-Zahlen von Basisnetz und unterteiltem Netz verwechselt?',
     ]},
]
