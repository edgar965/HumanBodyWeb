# -*- coding: utf-8 -*-
"""Blendervergleichmodell — Abschnitt „Modell und Körper“ der Tabelle „Wie liefe das mit Blender“ (Reiter „Tools“, 03.10.2026).

Schema und Stände: `Architektur2d3dblender`; die letzten zwei Felder je Zeile sind die Ausführungszeiten (lokal, Blender) mit Quelle und Datum, sonst genau „nicht gemessen“ oder „entfällt“. Belege für „Blender hat das“: Introspektion von Blender 5.2.2 LTS im Hintergrundmodus
(`blender -b --factory-startup`, nur Namen gelesen, nichts gerechnet) — `ProjektTemp/_wegwerf/tools_seite/t5/ergebnis_introspektion.json`
(dazu `…2.json`, `…3.json`). „Im Kern“ heißt: im Werksstart vorhanden; was erst installiert oder aktiviert werden muss, ist ein Add-on.
Stand `genutzt` gilt, sobald das Projekt das Blender-Werkzeug aufruft — auch ein Add-on, dann steht „Add-on“ im Text.
"""

__all__ = ['Blendervergleichmodell']


class Blendervergleichmodell:
    KENNUNG = 'blender-modell'
    TITEL = 'Modell und Körper: Genesis 9 gegen Blender'
    EINLEITUNG = ('Wie Blender 5.2.2 die Aufgaben „Figur erzeugen, formen, häuten, bewegen, speichern“ löst und was das Projekt stattdessen tut. '
                  'Der tatsächliche Blender-Weg des Projekts: glTF als Brücke, Cloth, Haar-Knoten, Workbench-Render, die Add-ons MPFB und '
                  '„BVH and FBX Retargeter“ — die Figur selbst kommt aus Genesis 9 (Daz-Daten), nicht aus Blender.')
    # (Aufgabe, lokales Werkzeug, lokaler Aufruf, lokale Klassen [(Datei, Klasse)], Blender-Werkzeug, Blender-Aufruf, Blender-Stand, Unterschied, zeit_lokal, zeit_blender)
    ZEILEN = [
        ('Mensch-Figur erzeugen',
         'Genesis-9-Figur aus Reglerwerten (Daz-Daten, DSON-Leser; kein Blender)',
         "G9formung({'FBMHeavy': 0.3}).punkte()   # (N, 3) Meter: Basisnetz plus Morphs, Knochenskalierung gebacken",
         [('Genesis9/formung.py', 'G9formung'), ('Genesis9/morphablage.py', 'G9morphablage'), ('Genesis9/skelett.py', 'G9skelett')],
         'MPFB 2 (Extension „Human character generator and editor“); im Kern nur Primitive, Skin-Modifier und Metaballs',
         "HumanService.create_human(macro_detail_dict=makro)   # from bl_ext.blender_org.mpfb.services.humanservice import HumanService",
         'genutzt',
         'Add-on, nicht im Kern: MPFB 2.0.14 (`extensions/blender_org/mpfb`, Manifest). Das Projekt ruft es nur in „Kleid + Wind“ auf '
         '(`effekte/blender/effektfigur.py`, Rig `cmu_mb` mit 31 Knochen, ohne Finger und Gesicht). Die 2D3D-Pipeline nutzt MPFB nicht: Genesis 9 '
         'kommt aus Daz-Daten, ein Steuerregler stellt über einen Formelgraphen gut 60 Morphs (Docstring `Genesis9/formung.py`). Im Blender-Kern '
         'gibt es keinen Menschengenerator: Die Namenssuche „human“ über 2.499 Operatoren des Werksstarts findet nichts; vorhanden sind '
         'Primitive, der Modifier SKIN und Metaballs (`ergebnis_introspektion.json`).',
         '0,4 s je Reglerzug (Ansichtsstufe 1, 104.480 Punkte, Server; genesis9.md, 17.09.2026)',
         'nicht gemessen'),

        ('Netz aus Fotos erzeugen',
         'Fotos → Netz mit TRELLIS.2 (Pixal3D wählbar), Schritt „netz“ von 2D3D Kleider',
         'POST /api/engine2d3dkleider/<job_id>/starten/   {"ab": "netz", "bis": "netz"}   # nur nach Ansage; GPU-Lauf im Arbeitsprozess',
         [('HumanBodyWeb/core/dienste/engine2d3dkleidernetz.py', 'Engine2d3dKleidernetz'),
          ('HumanBodyWeb/core/dienste/meshoptionen.py', 'Meshoptionen')],
         'Kein Werkzeug im Kern; vorhanden ist Motion Tracking (Kamera-Solve, Punkte aus Markern)',
         "bpy.ops.clip.solve_camera()   # und bpy.ops.clip.bundles_to_mesh(): Kamera und Markerpunkte, kein Körpernetz (nicht ausgeführt)",
         'keins',
         'Die Namenssuche „photo“ und „reconstruct“ über alle 2.499 Operatoren des Werksstarts findet nichts (`ergebnis_introspektion.json`); '
         'vorhanden ist Motion Tracking (`clip.solve_camera`, `clip.track_markers`, `clip.bundles_to_mesh`). Die Rechnung des Projekts läuft außerhalb von '
         'Blender (`VideoToBVH/wrappers/_run_mesh.py`, eigene Umgebung, GPU). Gemessen an denselben Fotos: Auflösung „hoch“ 579 s, „mittel“ 596 s, '
         '„schnell“ 467 s (`engine2d3dkleider.md`, 30.09.2026).',
         '428,3–752,6 s (TRELLIS.2, 8 Aufträge, je nach Auflösung, Textur und Flächenzahl, ganzer Schritt netz; workflowzeiten.py, '
         'Datenbank gelesen 02.10.2026)',
         'entfällt'),

        ('Figur an ein Netz anpassen',
         'Körper-Fit: Genesis-Regler und Eigenmorph auf das Netz rechnen (Kette von „Mesh to 3D“)',
         'POST /api/engine2d3dkleider/<job_id>/starten/   {"ab": "koerper", "bis": "koerper"}   # Option koerper.quelle = uebernehmen | rechnen',
         [('HumanBodyWeb/core/dienste/engine2d3dkleiderkoerper.py', 'Engine2d3dKleiderkoerper'),
          ('HumanBodyWeb/core/dienste/engine2d3dkleiderkoerperlauf.py', 'Engine2d3dKleiderkoerperlauf')],
         'Shrinkwrap- und Surface-Deform-Modifier (Fläche an ein Zielnetz legen), Quadriflow- und Voxel-Remesh (neue Topologie)',
         "m = obj.modifiers.new('Fit', 'SHRINKWRAP'); m.target = netz_obj; m.offset = 0.003   # bpy.ops.object.quadriflow_remesh() für neue Topologie",
         'vorhanden',
         'Alle genannten Typen und Operatoren gibt es in 5.2.2 (SHRINKWRAP, SURFACE_DEFORM, `object.quadriflow_remesh`, `object.voxel_remesh`). Sie legen '
         'ein Netz an ein Ziel oder bauen es neu auf; Regler stellen sie nicht. Das Projekt rechnet stattdessen die Genesis-9-Regler und einen Eigenmorph '
         'auf das Netz (Quelle „rechnen“: rund 15 min Grafikkarte, Quelle „uebernehmen“: Sekunden — Modulkopf `engine2d3dkleiderkoerper.py`). '
         'Ein Vergleich Shrinkwrap gegen die Reglerkette ist nicht gemessen.',
         '694,8–984,1 s (Quelle „rechnen“, 6 Aufträge, ganzer Schritt koerper; „uebernehmen“ 0,0 s; workflowzeiten.py, Datenbank gelesen '
         '02.10.2026)',
         'nicht gemessen'),

        ('Körperform verstellen',
         'Körperregler (Morphs) der Genesis-9-Figur',
         "m.koerper_regler('FBMHeavy', 0.3)   # Namen und Grenzen: ModellMitKleidern.hilfe(), GET /api/engine2d3dkleider/funktionen/",
         [('Genesis9/modellmitkleidern.py', 'ModellMitKleidern'), ('Genesis9/formung.py', 'G9formung'), ('Genesis9/morphablage.py', 'G9morphablage')],
         'Shape Keys (Mesh.shape_keys, Wert je Key-Block); Treiber koppeln Werte',
         "obj.shape_key_add(name='Heavy'); obj.data.shape_keys.key_blocks['Heavy'].value = 0.3",
         'vorhanden',
         'Beides sind lineare Deltas je Punkt, mischbar: `punkte = basis + Σ wert × deltas` (Docstring `Genesis9/formung.py`); Daz kommt mit einem '
         'Formelgraphen dazu. Blender hat `Object.shape_key_add`, `Key.key_blocks`, `ShapeKey.value` und `driver_add` (Introspektion). Das '
         'eigene Blender-Add-on HumanBodyBlender schreibt Morphs dagegen direkt in die Punkte (`HumanBodyBlender/morph/morpher.py`, '
         '`vertices.foreach_set("co", …)`), nicht über Shape Keys.',
         '0,4 s je Reglerzug (Ansichtsstufe 1, 104.480 Punkte, Server; genesis9.md, 17.09.2026)',
         'nicht gemessen'),

        ('Körper örtlich nachformen',
         'Ortsmorph, Körperhülle und Form-Pinsel am Körper (Eigenmorph neben der Bibliothek)',
         "m.koerper_ort('bauch_plus', {'landmarke': 'bauch', 'radius_cm': 8}, weg_cm=1.5)   # richtung='haut'; m.koerper_huelle(staerke=0.5)",
         [('Genesis9/modellkoerper.py', 'ModellKoerperMixin'), ('Genesis9/koerpermorph.py', 'G9koerpermorph'),
          ('Genesis9/ortsmorph.py', 'G9ortsmorph'), ('Genesis9/formpinsel.py', 'G9formpinsel')],
         'Sculpt-Modus (Pinsel), Proportional Editing, Modifier LATTICE, HOOK, LAPLACIANDEFORM',
         "bpy.ops.sculpt.brush_stroke(...)   # braucht View-Kontext; im Hintergrund: obj.modifiers.new('Gitter', 'LATTICE')",
         'vorhanden',
         'Vorhanden (Introspektion): `sculpt.brush_stroke`, `ToolSettings.use_proportional_edit`, die Modifier LATTICE, HOOK, LAPLACIANDEFORM, SHRINKWRAP. '
         'Das Projekt nimmt statt Pinselstrichen einen ORT als Wörterbuch (Band × Sektor, Kugel, Landmarke) und legt das Ergebnis als eigenen Morph '
         'ab (`eigen:ort_<name>`), damit ein Rezept ihn wiederholen kann; der Form-Pinsel (`G9formpinsel`: ziehen, drücken, aufblasen, glätten, flach, '
         'greifen) macht aus Strichen ebenfalls einen Morph. Das Konzept 30.09.2026 §3.1 hält Blenders Sculpt per `bpy` für unhandlich (nur mit '
         'View-Kontext skriptbar) — Einschätzung, nicht neu gemessen.',
         '0,42 s erster Zug, danach 22 ms (Ortsmorph „Links“ am Base Shirt, 3.732 Punkte, Netz-Endpunkt; Szene ist ein Kleid, nicht der '
         'Körper; ortsmorphe.md, 30.09.2026)',
         'nicht gemessen'),

        ('Gelenkkorrekturen',
         'Daz-Joint-Corrective-Morphs (JCMs), je Bild aus den Gelenkwinkeln',
         "G9gelenkkorrekturen.werte({'l_forearm': {'rotation/x': 90.0}})   # {morph: Wert}; im Browser je Bild (genesis9gelenke.js)",
         [('Genesis9/gelenkkorrekturen.py', 'G9gelenkkorrekturen')],
         'Shape Keys mit Treibern (Driver auf die Bone-Rotation), Corrective-Smooth-Modifier',
         "obj.data.shape_keys.key_blocks['Beuge'].driver_add('value')   # Driver-Variable auf PoseBone.rotation_euler; Modifier CORRECTIVE_SMOOTH",
         'vorhanden',
         'Daz-JCMs sind 117 Morphe (`Base Correctives` plus `Base Flexions`) mit einem Formelgraphen aus den `.dsf`-Dateien, im Browser 4 ms je Bild '
         'bei 32 aktiven (`genesis9-bewegung.md`, 18.09.2026). Blender hat die Bausteine (Shape Keys, `driver_add`, CORRECTIVE_SMOOTH; Introspektion); '
         'ein Weg, die Daz-Formeln nach Blender zu bringen, ist im Projekt nicht gebaut.',
         '4 ms je Bild bei 32 aktiven Korrekturen (Browser; genesis9-bewegung.md, 18.09.2026)',
         'nicht gemessen'),

        ('Gesicht an Fotos anpassen',
         'Sieben Gesichtsmaße aus 478 Landmarken auf Foto und Kopf-Render, Kopfregler gedämpft stellen (FaceBuilder-Ersatz)',
         "Gesichtsmasse.masse(punkte, breite=1.0, hoehe=1.0)   # punkte: 478 × (x, y) in Bildanteilen; in der Runde stellt IterationGesicht die Kopfregler",
         [('HumanBodyWeb/core/dienste/gesichtsmasse.py', 'Gesichtsmasse'), ('HumanBodyWeb/core/dienste/fotolandmarken.py', 'Fotolandmarken'),
          ('2d3DIterationen/iterationen2d3d/iterationgesicht.py', 'IterationGesicht')],
         'KeenTools FaceBuilder (Add-on, im Nutzerprofil installiert); im Kern nur Shape Keys und Motion Tracking',
         '— (Oberfläche des Add-ons „FaceBuilder“ mit Pins im 3D-Viewport; Aufruf im Hintergrundmodus nicht geprüft)',
         'addon',
         'KeenTools 2026.3.1 (`scripts/addons/keentools/__init__.py`: „FaceBuilder: Create Heads“) baut einen Kopf aus Fotos mit Pins; kommerziell und nur '
         'Gesicht (Konzept 30.09.2026 §3.4). Im Kern gibt es keine Landmarken: Die Namenssuche „landmark“ über Operatoren und Typen findet nichts '
         '(`ergebnis_introspektion.json`). Das Projekt stellt die Kopfregler gedämpft (0,6, Schritt höchstens 0,35); die Maße rauschen um etwa 1 % je '
         'Maß, deshalb gibt es einen `Gesichtsvorrat` (`ortsmorphe.md`, 01.10.2026).',
         'nicht gemessen',
         'nicht gemessen'),

        ('Rig und Skinning',
         'Genesis-9-Skelett (138 Knochen) mit Daz-Gewichten; Kleidung bekommt die Gewichte des Körpers darunter',
         "G9formung({}).skelett().bauen()   # {name, knochen: [{name, eltern, kopf, schwanz, pos, quat, ende}]}; Gewichte: G9koerperhaut.fuer(folger)",
         [('Genesis9/skelett.py', 'G9skelett'), ('Genesis9/haut.py', 'G9haut'), ('Genesis9/koerperhaut.py', 'G9koerperhaut')],
         'Armature, Parent „With Automatic Weights“ (Bone Heat), Modifier ARMATURE, Weight Paint; Rigify (mitgeliefertes Add-on, im Werksstart aus)',
         "bpy.ops.object.parent_set(type='ARMATURE_AUTO')   # Netz und Armature gewählt; Rigify: addon_utils.enable('rigify')",
         'vorhanden',
         '`ARMATURE_AUTO` steht im Operator `object.parent_set`; Rigify liegt unter `addons_core/rigify`, ist im Werksstart aus und stellt nach '
         '`addon_utils.enable(\'rigify\')` unter anderem `object.armature_human_metarig_add` und `pose.rigify_generate` bereit (`ergebnis_introspektion5.json`; '
         'das Aktivieren ohne Einstellungsdatei meldet einen KeyError, die Operatoren stehen trotzdem in der Liste). Das Projekt ruft die Automatik nirgends auf: '
         'Genesis 9 trägt die Daz-Gewichte, '
         'Kleidung bekommt die des Körpers darunter (drei Projektionsnachbarn gemischt, `genesis9.md`, 17.09.2026). Im BlenderModel-Weg hängt '
         '`effekte/blender/kostuem/kostuembindung.py` seine Teile mit eigenen Gewichten (4 nächste Körperpunkte) über einen ARMATURE-Modifier an das Rig.',
         'nicht gemessen',
         'nicht gemessen'),

        ('Pose und Haltung',
         'Haltung (Arme senken) und einzelne Gelenkwinkel am Rezept, je Bild gehäutet',
         "m.haltung(arme_grad=35.0); m.haltung_gelenk('l_forearm', 'rotation/x', 20.0)",
         [('Genesis9/modellmitkleidern.py', 'ModellMitKleidern'), ('Genesis9/haltungshaut.py', 'G9haltungshaut'),
          ('Genesis9/knochenmatrizen.py', 'G9knochenmatrizen')],
         'Pose-Modus (PoseBone.rotation_euler), `pose.armature_apply` (Pose als Ruhepose), Constraints',
         "obj.pose.bones['upper_arm.L'].rotation_euler.z = 0.6; bpy.ops.pose.armature_apply()",
         'vorhanden',
         'Beides stellt Knochen (`PoseBone.rotation_euler`, `pose.armature_apply`; Introspektion). Die Haltung des Projekts ist ein Rezeptwert (A-Pose bis '
         'hängende Arme, höchstens 43°, gemessen am Bauplan der Grundfigur, 30.09.2026) und wird je Bild gehäutet, nicht als Pose-Zustand in einer Datei '
         'gehalten. Ob Blender-Posen und Genesis-Posen dieselben Knochenachsen haben, ist nicht gemessen — Blenders glTF-Export hat eigene Achsen '
         '(`blendermodell.md`, 29.09.2026).',
         'nicht gemessen',
         'nicht gemessen'),

        ('Retarget im Blender-Kern',
         'Retarget BVH → Genesis 9 (auch DEF, UMA, SMPL, MakeHuman) in Python/NumPy',
         "Retargetdaten(bvh_pfad, body_height=1.68, ziel=Retargetdaten.ZIEL_G9, formung=G9formung(stellung)).holen()   # .als_dict(): Drehungen je Bild",
         [('HumanBodyWeb/core/dienste/retargetdaten.py', 'Retargetdaten'),
          ('HumanBody/humanbody_core/skeleton/retarget/motor.py', 'Retargetlauf'),
          ('HumanBody/humanbody_core/skeleton/retarget/richtungskorrektur.py', 'Richtungskorrektur'),
          ('HumanBody/humanbody_core/skeleton/retarget/handausrichtung.py', 'Handausrichtung'),
          ('HumanBody/humanbody_core/skeleton/formats/g9_zuordnung.py', 'G9zuordnung')],
         'Im Kern kein Retarget-Werkzeug; Bausteine: BVH-Import, Constraints (COPY_ROTATION), `nla.bake`',
         "bpy.ops.import_anim.bvh(filepath=bvh, rotate_mode='QUATERNION')   # dann COPY_ROTATION-Constraints auf das Ziel-Rig und bpy.ops.nla.bake(...)",
         'keins',
         'Die Namenssuche „retarget“ über Operatoren, Typen und Knoten des Werksstarts findet nichts (`ergebnis_introspektion.json`). Vorhanden: '
         '`import_anim.bvh` (Add-on `io_anim_bvh`, mitgeliefert und im Werksstart aktiv), der Constraint COPY_ROTATION, `nla.bake`. Das eigene '
         'Blender-Add-on HumanBodyBlender baut daraus einen Retarget (Rumpf und Beine Bild für Bild in Python, Arme über COPY_ROTATION und `nla.bake`, '
         '`HumanBodyBlender/retarget.py`). Der Retarget von 2D3D Kleider ist reines Python mit Richtungskorrektur und Handausrichtung (`retarget.md`); '
         'Vorgabe: keinen eigenen Retarget-Code erfinden (`CLAUDE.md`, Edgar 08.09.2026).',
         '43 s (7.538 Bilder, erster Abruf je BVH und Ort, vor dem Retargetvorrat; retarget.md, 17.09.2026)',
         'entfällt'),

        ('Retarget mit dem Blender-Add-on',
         'Blender-Aufruf des Projekts: `Bvhretarget` in der Effekte-Pipeline „Kleid + Wind“ (im BlenderModel-Weg bis 29.09.2026)',
         'blender -b --python effekte/blender/kleidwind.py -- --bvh <datei.bvh> --kleid <kleid.mhclo> --ausgabe <video.mp4>   # Seite Effekte',
         [('HumanBodyWeb/effekte/blender/bvhretarget.py', 'Bvhretarget'), ('HumanBodyWeb/effekte/blender/effektfigur.py', 'Effektfigur')],
         'Extension „BVH and FBX Retargeter“ 5.0.0 (Thomas Larsson); im Profil außerdem „Retarget“ 2.9.0 (KBS DEV), Rokoko, Auto-Rig Pro',
         "bpy.ops.mcp.load_and_retarget(filepath=bvh, useDefaultSS=False, ssFactor=1)   # wie effekte/blender/bvhretarget.py",
         'genutzt',
         'Add-on, nicht im Kern (`extensions/user_default/retarget_bvh`, Manifest); unter `--factory-startup` ist es nicht aktiv. Es erkennt Quelle und '
         'Ziel an den Knochennamen, bringt beide in T-Pose und skaliert; MPFBs `default`-Rig kannte es nicht, `cmu_mb` ja (`effektfigur.py`). Fehler '
         'meldet es als Text statt als Exception (`bvhretarget.py`). Im BlenderModel-Weg stand das Ziel damit kopfüber, weil das Add-on die Ruhe-/T-Pose '
         'seines Ziels selbst erkennt; seit 29.09.2026 setzt `posenspuren.py` die fertigen Drehungen als Keyframes (`blendermodell.md`). Zeit: 1.004 Bilder '
         '33 s, davon 300 gebraucht (`bvhretarget.py`, 12.09.2026).',
         '33 s (1.004 Bilder, 002_Dance, Retarget-Schritt des Add-ons ohne Blender-Start; effekte/blender/bvhretarget.py, 12.09.2026)',
         '6,2 s (300 Bilder mit useAllFrames=False, derselbe Schritt, nicht dieselbe Bildzahl; effekte.md, 12.09.2026)'),

        ('Netz unterteilen',
         'Catmull-Clark auf dem Daz-Käfig (Ansicht Stufe 1, Strg+Alt+H Stufe 2)',
         'kein Aufruf: beim Netzbau automatisch (G9netzstufe wählt die Stufe, G9unterteilung rechnet Nähte und Haut mit)',
         [('Genesis9/netzstufe.py', 'G9netzstufe'), ('Genesis9/unterteilung.py', 'G9unterteilung')],
         'Modifier SUBSURF (Subdivision Surface), MULTIRES',
         "obj.modifiers.new('Unterteilung', 'SUBSURF')   # wie effekte/blender/stoffsimulation.py",
         'genutzt',
         'Gleiches Verfahren. Das Projekt nutzt SUBSURF in „Kleid + Wind“ (`effekte/blender/stoffsimulation.py`, Stoff vor der Simulation unterteilt) und zum '
         'Glätten der Kostümrohre (`effekte/blender/kostuem/rohr.py`). Der eigene Unterteiler rechnet die Daz-Nähte (UV je Flächenecke) und die Haut mit: '
         'Stufe 1 hat 104.480, Stufe 2 410.202 Punkte (`genesis9.md`, 17.09.2026). Falle des eigenen Wegs: Catmull-Clark auf GarmentCodes unregelmäßigem '
         'Dreiecksnetz gab Beulen — solche Stücke bleiben Käfig (`genesis9-garderobe.md`, 25.09.2026).',
         '0,4 s je Reglerzug Stufe 1 (104.480 Punkte), 0,55 s je Zug Stufe 2 (410.202 Punkte, Strg+Alt+H), Server; genesis9.md, 17.09.2026',
         'nicht gemessen'),

        ('Export als glTF/GLB',
         'Eigene GLB-Schreiber: Körper mit Rig, Kleider, Haar an einem Skin (figur.glb, je Runde modell.glb)',
         'POST /api/engine2d3dkleider/<job_id>/starten/   {"ab": "export", "bis": "export"}   # → ergebnis/figur.glb (Engine2d3dKleiderexport.DATEI)',
         [('HumanBodyWeb/core/dienste/engine2d3dkleiderexport.py', 'Engine2d3dKleiderexport'),
          ('HumanBodyWeb/core/dienste/rundenglb.py', 'Rundenglb'), ('HumanBodyWeb/core/dienste/standmodellglb.py', 'Standmodellglb'),
          ('HumanBodyWeb/core/dienste/kleidermodellglb.py', 'Kleidermodellglb')],
         'glTF-2.0-Exporter und -Importer (mitgeliefertes Add-on `io_scene_gltf2`, im Werksstart aktiv)',
         "bpy.ops.export_scene.gltf(filepath='figur.glb', use_selection=True, export_apply=True, export_yup=True, export_vertex_color='ACTIVE')",
         'genutzt',
         'Im BlenderModel-Weg ist glTF die Brücke: `import_scene.gltf` lädt die Figur (`effekte/blender/blendermodellfigur.py`), `export_scene.gltf` schreibt das '
         'Kostüm (`kostuembau.py`, mit `export_vertex_color=\'ACTIVE\'`), `modellexportblend.py` schreibt eine GLB als .blend um. Fallen: Blenders Export hat '
         'eigene Knochenachsen (`Posenspuren` stand „verdreht in der Luft“, `blendermodell.md`); das glTF-Zusatzfeld `export_extras` kam nicht in der GLB an; '
         'nach `import_scene.gltf` steht trotz `--factory-startup` eine „Icosphere“ (42 Punkte) in der Szene, die nicht in der GLB ist (`modellexportblend.py`, '
         '26.09.2026). Der eigene Schreiber setzt Körper (je Kachel mit dem '
         'gebackenen Foto), Augen, Mund, Wimpern, Brauen, Kleider und Haar an EINEN Skin mit 143 Knochen (`engine2d3dkleider.md`, 01.10.2026).',
         '1,8–3,4 s (Schritt export, 5 Aufträge, Körper mit Rig; workflowzeiten.py, Datenbank gelesen 02.10.2026)',
         '~3 s (Runden-GLB des BlenderModel-Kostüms, ganzer Blender-Aufruf; andere Szene; blendermodell.md, 29.09.2026)'),

        ('Automatisierung',
         'Rezeptzeilen `m.<funktion>(literale)` — Text, kein Python; jede Runde ist ein wiederholbares Rezept',
         "G9rezept.anwenden(modell, text)   # text zeilenweise, z. B. m.kleid_nur('g9_base_shirt') und m.passform(laenge_cm=-4)",
         [('Genesis9/modellrezept.py', 'G9rezept'), ('Genesis9/modellmitkleidern.py', 'ModellMitKleidern'),
          ('HumanBodyWeb/core/dienste/engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender')],
         '`bpy`-Skripte im Hintergrundmodus: Python 3.13.13 in 5.2.2, alles, was die API kann',
         "blender -b --factory-startup --python skript.py -- --auftrag auftrag.json   # so ruft Engine2d3dKleiderblender._laufen",
         'genutzt',
         'Ein Rezept kann nur die Funktionen von `ModellMitKleidern.hilfe()` mit Literalen (`ast` gelesen, Fehler mit Zeilennummer) — so können Fable und '
         'Edgar Rezepte schreiben, ohne dass ein Rezept mehr kann als das Modell. Blender läuft im Projekt als EIN Prozess je Befehl (`--factory-startup`, '
         'TMP/TEMP in den Auftragsordner, Zeitgrenze 900 s; Start 4–9 s, die Rechnung Sekunden — Modulkopf `engine2d3dkleiderblender.py`). Der '
         'BlenderModel-Weg hielt dauerhafte Arbeiter (Postfach-Ordner): Runde 4,5–6 s statt 23 s (`blendermodell.md`, 30.09.2026). API-Falle 5.2: Eingänge '
         'eines Geometry-Nodes-Modifiers lassen sich nicht mehr per `mod[identifier]` setzen — Hüll-Nodegruppe nehmen (`CLAUDE.md`).',
         '0,1 s (Rezept der Automatik schreiben und anwenden; auftrag.log von 2026.10.01.20.10.04, Runden 9–11; architektur2d3dmessung.py, '
         '02.10.2026)',
         '4–9 s (Blender-Start je Befehl; Klassenkommentar engine2d3dkleiderblender.py, 30.09.2026)'),
    ]
