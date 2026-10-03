# -*- coding: utf-8 -*-
"""Blendervergleichtextur — Abschnitt „UV und Textur“ der Tabelle „Wie liefe das mit Blender“ (Reiter „Tools“, 03.10.2026).

Schema und Stände: `Architektur2d3dblender`. Belege „Blender hat das“: `ProjektTemp/_wegwerf/tools_seite/t5/ergebnis_introspektion*.json` und
`operatoren.txt` (Blender 5.2.2 LTS, Werksstart, nur Namen). Belege „gemessen“: `Stoffsolver/README.md`, Abschnitt „Messungen“, und
`Stoffsolver/werkzeug/vergleich_uv*.py`, `vergleich_textur*.py` (Blender im Hintergrundmodus gegen den Solver).
"""

__all__ = ['Blendervergleichtextur']


class Blendervergleichtextur:
    KENNUNG = 'blender-textur'
    TITEL = 'UV und Textur: Abwickeln, Packen, Backen, Fotoprojektion'
    EINLEITUNG = ('UV-Abwicklung, Packen und Backen hat der Stoffsolver aus Blenders Quelltext nachgebaut und gegen Blender 5.2.2 gemessen; die Pipeline '
                  'selbst ruft diesen Teil nicht auf. Fotoprojektion, Decal und Falten sind Eigenbau am Genesis-Modell — Blender hat dafür Texture Paint, '
                  'Project Paint und Bake.')
    # (Aufgabe, lokales Werkzeug, lokaler Aufruf, lokale Klassen [(Datei, Klasse)], Blender-Werkzeug, Blender-Aufruf, Blender-Stand, Unterschied)
    ZEILEN = [
        ('UV abwickeln',
         'Stoffsolver-Abwicklung: Projektion, LSCM, ABF++, SLIM; Löcher, Pins, Symmetrie, Henkel',
         "Uvabwicklung(punkte, dreiecke, verfahren='lscm').rechnen()   # → Uvergebnis; verfahren: projektion | lscm | abf | slim",
         [('Stoffsolver/uvabwicklung.py', 'Uvabwicklung'), ('Stoffsolver/uvslim.py', 'Uvslim'), ('Stoffsolver/uvhenkelschnitt.py', 'Uvhenkelschnitt')],
         'Operatoren `uv.smart_project` und `uv.unwrap` (Methoden ANGLE_BASED, CONFORMAL, MINIMUM_STRETCH), Projektionen (cube, cylinder, sphere, from_view)',
         "bpy.ops.uv.unwrap(method='CONFORMAL')   # Edit-Modus, Flächen gewählt; bpy.ops.uv.smart_project() für Smart UV Project",
         'gemessen',
         'Gegen Blender 5.2.2 verglichen: Smart UV Project (`vergleich_uvsmart.py`), Unwrap ANGLE_BASED ↔ `abf` und CONFORMAL ↔ `lscm` (`vergleich_uvunwrap.py`), '
         'MINIMUM_STRETCH ↔ `slim` (`vergleich_uvslim.py`), dazu Löcher, Pins, Henkel. Ergebnis: gleich bis auf erklärte Gleichstände, Form ~3e-8, Lage ≤ 5e-7 '
         '(`vergleich_uv.py`; `Stoffsolver/README.md`, 02.10.2026). Die Pipeline ruft Blenders UV-Operatoren nicht auf und den Solver-Teil auch nicht: '
         'Kein Treffer für `Uvabwicklung` in HumanBodyWeb, Genesis9, 2d3DIterationen, Assets, HumanBody — außer der Hilfeseite (`stoffsolverumfanguv.py`). '
         'Die UV der Genesis-Stücke kommen aus Daz (UV je Flächenecke, 5 UDIM-Kacheln, `genesis9.md`), die der GarmentCode-Stücke aus dem Schnitt.'),

        ('UV packen',
         'Packer des Stoffsolvers: Kasten, konvexe und konkave Form, xatlas, Pins, merge_overlap, Zielkachel',
         "Uvpacker(rand=0.01, methode='anteil', rotation='achse_y', formmodell='aabb').packen(uv_ecken, insel)   # uv_ecken (T, 3, 2), insel (T,)",
         [('Stoffsolver/uvpacker.py', 'Uvpacker'), ('Stoffsolver/uvpackpins.py', 'Uvpackpins')],
         'Operator `uv.pack_islands` (shape_method AABB, CONVEX, CONCAVE; rotate_method, margin_method, merge_overlap, pin, udim_source)',
         "bpy.ops.uv.pack_islands(shape_method='CONVEX', margin=0.001)   # Edit-Modus, Inseln gewählt",
         'gemessen',
         'Packer-Pins, `merge_overlap` und Zielkachel: Lage ≤ 5,1e-5 in 444 + 168 + 298 Fällen, sieben erklärt (Abbruch der Wurzelsuche bei 1e-4), Rauschgrenze '
         '0 (`vergleich_uv.py packpins packmerge packudim`; `Stoffsolver/README.md`, 03.10.2026). Eine UDIM-Verteilung auf mehrere Kacheln gibt es in 5.2.2 '
         'nicht: `pack_islands` packt alles in ein Quadrat und verschiebt es um einen Versatz (`udim_source` wählt die Zielkachel; README). Die Werte der '
         'Aufzählungen (shape_method, rotate_method, margin_method) stammen aus der Introspektion (`ergebnis_introspektion4.json`).'),

        ('Texturen backen',
         'Texturbacker des Stoffsolvers (Lage, Normale, Farbe je Punkt, Dreieck und Material, Foto, UDIM) und `G9texturbacken` für die Genesis-Haut',
         "Texturbacker(punkte, dreiecke, uv, groesse=1024).farbe_je_punkt(farben)   # farben (N, C) → Textur (H, B, C); Foto: .foto(fotos)",
         [('Stoffsolver/texturbacker.py', 'Texturbacker'), ('Stoffsolver/texturudim.py', 'Texturudim'), ('Genesis9/texturbacken.py', 'G9texturbacken')],
         'Operator `object.bake` (Cycles; Typen COMBINED, AO, SHADOW, POSITION, NORMAL, UV, ROUGHNESS, EMIT, ENVIRONMENT, DIFFUSE, GLOSSY, TRANSMISSION)',
         "bpy.ops.object.bake(type='EMIT', margin=0, use_clear=True, margin_type='EXTEND')   # Ziel: Image-Texture-Knoten im Material",
         'gemessen',
         'Gemessen: Cycles EMIT mit Rand 0 gegen `Texturbacker.farbe_je_punkt`, `farbe_je_dreieck` und `farbe_je_material` auf derselben UV, dazu UDIM-Kacheln und '
         'die Bildabtastung (`vergleich_texturbake.py`, `vergleich_texturudim.py`; Aufruf in Blender: `blender_textur_lauf.py`). Ohne Blender-Gegenstück: '
         'Fotoprojektion, Mipmaps, weiches Mischen (Eigenbau, `Stoffsolver/README.md`). Die Genesis-Haut backt das Projekt mit `G9texturbacken` (Fotohaut je '
         'UDIM-Kachel, Seite 2048); den Texturbacker des Solvers ruft die Pipeline nicht auf.'),

        ('Haut und Textur aus Fotos',
         'Fotoprojektion je Texel auf Körper, Kleid und Haar (Normierung über Figurhöhe und Rumpfschwerpunkt statt Kamera)',
         "m.kleid_fototextur('g9_base_shirt', staerke=1.0)   # die Runde rechnet die Projektion (Kleidfotoprojektion)",
         [('HumanBodyWeb/core/dienste/kleidfotoprojektion.py', 'Kleidfotoprojektion'),
          ('HumanBodyWeb/core/dienste/koerperfotoprojektion.py', 'Koerperfotoprojektion'),
          ('Genesis9/kleidfototextur.py', 'G9kleidfototextur'), ('Genesis9/modelltextur.py', 'ModellTexturMixin')],
         'Project Paint (`paint.project_image`, `image.project_edit`, `image.project_apply`), Modifier UV_PROJECT, Bake',
         "bpy.ops.paint.project_image(image='Foto.png')   # Texture-Paint-Modus, braucht View-Kontext (nur Namen geprüft, nicht ausgeführt)",
         'vorhanden',
         'Alle drei Bausteine gibt es in 5.2.2 (Operatoren und Modifier UV_PROJECT; Introspektion). Das Projekt hat die Projektion mit eigener Normierung gebaut: '
         'je Texel Gewicht Normale · Blick⁴, Teilmasken je Stück, Lückenfüllung per Push-Pull; Kunstfoto am Base Shirt: 89 % der Texel getroffen, 4,4 s '
         '(`ortsmorphe.md`, 01.10.2026). Das Konzept 30.09.2026 §6.2 erwartet, dass Blender es als Arbeiter rechnen KÖNNTE (`project_image` je Ansicht); gebaut ist '
         'das nicht, Zeiten dafür sind nicht gemessen.'),

        ('Decal und Malen von Hand',
         'Decal (Farbe oder Bild an einem Ort) und Malen von Hand auf der Bühne (Kreise in eine Decal-Schicht)',
         "m.kleid_decal('g9_base_shirt', 'fleck', {'band': (0.4, 0.6)}, farbe='#aa3322', deckung=1.0)   # Malen von Hand: POST /api/engine2d3dkleider/<job_id>/malen/",
         [('Genesis9/kleiddecal.py', 'G9kleiddecal'), ('Genesis9/kleidpinsel.py', 'G9kleidpinsel'), ('Genesis9/modelltextur.py', 'ModellTexturMixin')],
         'Texture Paint (`paint.texture_paint_toggle`, `paint.add_texture_paint_slot`) mit Pinsel-Assets (`essentials_brushes-mesh_texture.blend`)',
         "bpy.ops.paint.texture_paint_toggle()   # Modus; Pinsel aus assets/brushes/essentials_brushes-mesh_texture.blend",
         'vorhanden',
         'Vorhanden sind die Operatoren und die Pinsel-Asset-Datei (`ergebnis_introspektion.json`, `operatoren.txt`). Das Projekt malt ohne Blender: Raycast auf die '
         'GLB der Runde, UV in glTF-Konvention, Kreise in eine Decal-Schicht (20 Striche 0,05 s; `ortsmorphe.md`, 01.10.2026). Konzept 30.09.2026 §6.2: Eine '
         'Maske in UV zu malen ist in Pillow eine Zeile — deshalb nicht über Blender.'),

        ('Falten backen',
         'Faltenkarte (Normalkarte), prozedural oder aus der Simulation gebacken',
         "m.kleid_falten_backen('g9_base_shirt', 'falten', quelle='drapiert')   # nach m.kleid_drapieren(...); prozedural: m.kleid_falten(...)",
         [('Genesis9/faltenbacken.py', 'G9faltenbacken'), ('Genesis9/modelltextur.py', 'ModellTexturMixin')],
         'Modifier MULTIRES und `object.bake` (Typ NORMAL), Cloth-Filter im Sculpt-Modus (`sculpt.cloth_filter`)',
         "bpy.ops.object.bake(type='NORMAL')   # Hochpoly oder Multires → Normalkarte; Ziel: Image-Texture-Knoten",
         'vorhanden',
         'Alle Bausteine stehen in 5.2.2 (MULTIRES, `object.bake` mit Typ NORMAL, `sculpt.cloth_filter`; Introspektion). Das Projekt backt die Normale der verschobenen '
         'Fläche im Tangentenraum je Texel (Lengyel-Tangenten, UV-Handigkeit über die Bitangente): Base Shirt aus `drapiert` 2,6 s, 90 % der Shirt-Texel gekippt '
         '(`ortsmorphe.md`, 01.10.2026). Vorbild laut Konzept 30.09.2026 §3.1: Multires und Bake from Multires.'),
    ]
