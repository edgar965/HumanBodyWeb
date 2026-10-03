# -*- coding: utf-8 -*-
"""Blendervergleichhaar — Abschnitt „Haar“ der Tabelle „Wie liefe das mit Blender“ (Reiter „Tools“, 03.10.2026).

Schema und Stände: `Architektur2d3dblender`. Belege „Blender hat das“: `ProjektTemp/_wegwerf/tools_seite/t5/ergebnis_introspektion.json` und
`operatoren.txt` (Blender 5.2.2 LTS, Werksstart, nur Namen; die 26 Hair-Node-Gruppen aus `procedural_hair_node_assets.blend`). Belege „gemessen“:
`Stoffsolver/README.md`, Abschnitt „Messungen“, und `Stoffsolver/werkzeug/vergleich_haar*.py`.
"""

__all__ = ['Blendervergleichhaar']


class Blendervergleichhaar:
    KENNUNG = 'blender-haar'
    TITEL = 'Haar: Frisuren, Operationen, Dynamik'
    EINLEITUNG = ('Blender hat für Haar zwei Wege: das Partikelsystem (Typ HAIR, mit Dynamik) und Curves-Objekte mit den 26 Hair-Node-Gruppen. Das Projekt '
                  'ruft die Hair-Nodes auf Stranghaar (`m.haar_knoten`) und hat Erzeugung und Dynamik als Stoffsolver nachgebaut und gegen Blender 5.2.2 '
                  'gemessen; die Frisuren selbst kommen aus Daz.')
    # (Aufgabe, lokales Werkzeug, lokaler Aufruf, lokale Klassen [(Datei, Klasse)], Blender-Werkzeug, Blender-Aufruf, Blender-Stand, Unterschied)
    ZEILEN = [
        ('Frisuren-Bibliothek und Mischen',
         'Daz-Frisuren (18 Sorten) als „Haar – Generisch“: Anteile mischen, fünf Formachsen',
         "m.haar_anteil('toulouse_hair', 0.3)   # Summe aller Anteile wird auf 100 % gerechnet; m.haar_nur('mavick_hair'); m.haar_achse('kin_hair', 'laenge', 0.5)",
         [('Genesis9/haargenerisch.py', 'G9haargenerisch'), ('Genesis9/haarachsen.py', 'G9haarachsen'),
          ('Genesis9/haarmischung.py', 'G9haarmischung'), ('Genesis9/modellhaar.py', 'ModellHaarMixin')],
         'Keine Frisuren im Kern; Haar baut man als Partikelsystem (HAIR) oder Curves-Objekt',
         "bpy.ops.object.curves_empty_hair_add()   # legt ein leeres Haar-Objekt (Typ CURVES) an",
         'keins',
         'In `assets/nodes/procedural_hair_node_assets.blend` liegen 26 Knotengruppen und keine Objekte (`hair_asset_objekte` leer, '
         '`ergebnis_introspektion.json`): Blender liefert Werkzeuge, keine Frisuren. Das Projekt hat 18 Daz-Frisuren mit einem gemeinsamen Satz Formachsen '
         '(Länge, Kurz, Dichte, Wellig, Dutt; 18 von 18 gebaut, zusammen 45 s) und mischt Sorten über die Strähnendichte, mit ganzen Inseln nach Saat: '
         '70 % Kin plus 30 % Toulouse trägt 70 % der Kin-Inseln und 30 % der Toulouse-Inseln (`engine2d3dkleider.md`, 30.09.2026).'),

        ('Haar erzeugen',
         'Stoffsolver-Haarsystem: Wurzeln verteilen, wachsen, Kinder, Clump, Kink, Effektoren (nach `particle_distribute.cc` und `particle.cc`)',
         "Haarsystem(punkte, dreiecke, einstellungen, vierecke=None).straehnen()   # (punkte (M, 3), laengen (S,)) für Haarsimulation oder Render",
         [('Stoffsolver/haarsystem.py', 'Haarsystem'), ('Stoffsolver/haarverteilung.py', 'Haarverteilung'),
          ('Stoffsolver/haarwachstum.py', 'Haarwachstum'), ('Stoffsolver/kinderpfade.py', 'Kinderpfade')],
         'Partikelsystem Typ HAIR (`ParticleSettings`: hair_length, Kinder, Clump, Kink, Roughness, Effektoren) oder Curves-Objekt mit Geometry Nodes',
         "ps = obj.modifiers.new('Haar', 'PARTICLE_SYSTEM').particle_system; ps.settings.type = 'HAIR'; ps.settings.hair_length = 0.2",
         'gemessen',
         'Gegen Blender 5.2.2: Haar-Erzeugung (Wurzeln bis Kinder, Vierecke, Ecken, Volumen) gleich, höchstens 0,0016 mm (`vergleich_haarform.py`); '
         'Effektoren, Kurven, Texturen, Bearbeitung, Vielecke gleich, 214 Zeilen (`vergleich_haarrest.py`); Bezier- und NURBS-Führungskurven: Pfad 47 Szenen '
         '≤ 0,00025 mm, Haare 25 Szenen ≤ 0,0051 mm, als Poly 11 bis 1965 mm daneben (`vergleich_kurven.py`; `Stoffsolver/README.md`, 02./03.10.2026). Nicht '
         'gegen Blender gemessen: Haarkamm und Bearbeitung von Führungshaaren im Edit-Modus. Die Pipeline ruft die Erzeugung nicht auf (kein Treffer für '
         '`Haarsystem` in HumanBodyWeb, Genesis9, 2d3DIterationen): Frisuren kommen aus Daz, das Modul dient der Haar-Dynamik und dem Kämmen.'),

        ('Haar bearbeiten (Operationen)',
         'Haar-Operationen in Python mit Ortsgewicht: trim, clump, noise, straighten, biegen, anlegen, curl, braid (Karten und Strähnen)',
         "m.haar_trim('toulouse_hair', 'kuerzer', faktor=0.5, ort={'landmarke': 'schlaefe_l', 'radius_cm': 6})",
         [('Genesis9/modellhaar.py', 'ModellHaarMixin'), ('Genesis9/haarops.py', 'G9haarops')],
         'Hair-Node-Gruppen (Geometry Nodes auf Curves): Trim, Clump, Curl, Frizz, Straighten, Roll, Smooth, Braid, Displace, Rotate, Blend',
         "m.haar_knoten('<stranghaar-sorte>', 'kuerzer', 'trim', length_factor=0.5)   # Blender-Seite: Gruppe „Trim Hair Curves“ in einer Hüll-Nodegruppe",
         'genutzt',
         'Das Projekt ruft 16 der 20 Operationsgruppen (trim, clump, curl, frizz, noise, straighten, roll, smooth, braid, displace, rotate, shrinkwrap, attach, '
         'duplicate, interpolate, generate; `Engine2d3dKleiderblender.KNOTEN`) über eine Hüll-Nodegruppe; nicht aufgerufen sind Blend, Redistribute Curve '
         'Points, Restore Curve Segment Length und Set Hair Curve Profile. Gemessen am Pixie (236.136 Punkte, 21.755 Strähnen): Trim 2,4 s in Blender, 6 s mit '
         'Start; „Replace Length“ steht auf an und setzt jede Strähne auf 1 m (500 mm Weg) — mit Faktor aus; `Mask` wirkt je Strähne, das Ortsgewicht legt Python '
         'je Punkt an (`ortsmorphe.md`, 01.10.2026). Blenders Gruppen arbeiten auf Strähnen (Curves), Kartenhaar ist kein Curves-Objekt — dort rechnet '
         '`G9haarops`: `haar_clump` 1,6 s an Mavick Hair mit 576.309 Punkten (`ortsmorphe.md`).'),

        ('Haar verdichten',
         'Zusatzsträhnen in Python: Duplicate und Interpolate als Punktmischung aus vorhandenen Strähnen',
         "m.haar_duplizieren('<stranghaar-sorte>', 'dichter', anzahl=2, radius_mm=4.0)   # dazu m.haar_interpolieren('<stranghaar-sorte>', 'zwischen')",
         [('Genesis9/haarzusatz.py', 'G9haarzusatz'), ('Genesis9/kopfhaut.py', 'G9kopfhaut'), ('Genesis9/modellhaar.py', 'ModellHaarMixin')],
         'Hair-Node-Gruppen Duplicate, Interpolate und Generate Hair Curves (Attach to Surface davor)',
         "m.haar_knoten('<stranghaar-sorte>', 'dichter', 'duplicate', amount=2)   # Interpolate und Generate brauchen die Kopfhaut mit eindeutiger UV (G9kopfhaut)",
         'genutzt',
         'Am Pixie: Blenders Duplicate mit 2 Kopien 3,5 s (8,8 s mit Start), 43.510 Zusatzsträhnen mit 472.272 Punkten; die Python-Fassung `haar_duplizieren` '
         '2,5 s, `haar_interpolieren` 1,4 s (`ortsmorphe.md`, 01.10.2026). Blenders Vorgabe „Amount“ 10 machte aus 236.136 Punkten 2,6 Mio. — das Projekt nimmt 2. '
         'Mit einer Draufsicht als UV versetzte Attach alle 236.136 Pixie-Punkte um 1,66 m; seit `G9kopfhaut` (Daz-Kappe oder Kopf der Grundfigur mit '
         'Genesis-UV) stimmt es: Attach 1,14 mm Mittel (`ortsmorphe.md`, 01.10.2026).'),

        ('Strähnendicke',
         'Strähnendicke als Bänder (Wurzel, Spitze in mm), kamera-unabhängig',
         "m.haar_profil('<stranghaar-sorte>', wurzel_mm=1.5, spitze_mm=0.5)   # im Render und in der Runden-GLB; im Browser bleiben Linien",
         [('Genesis9/haarprofil.py', 'G9haarprofil'), ('Genesis9/strang.py', 'G9strang')],
         'Hair-Node-Gruppe „Set Hair Curve Profile“ (in `procedural_hair_node_assets.blend`)',
         "# Gruppe per bpy.data.libraries.load(pfad, assets_only=True) holen und in eine Hüll-Nodegruppe legen — wie haarknoten.py",
         'vorhanden',
         'Die Gruppe steht in der Asset-Datei (26 Gruppen, `ergebnis_introspektion.json`); das Projekt ruft sie nicht auf (`Engine2d3dKleiderblender.KNOTEN` '
         'kennt sie nicht). Stranghaar war im Render und in der Runden-GLB unsichtbar (entartete Linien); `G9haarprofil` macht je Segment ein Band '
         '(Kreuzprodukt Strähne × radial, 1,23 Mio. Punkte in 0,5 s; `ortsmorphe.md`, 01.10.2026).'),

        ('Haar-Dynamik',
         'Stoffsolver-Haardynamik: Cloth-Solver auf Strängen (GPU), Wurzeln fest, Körper als Kollider; nur von Hand',
         "m.haar_dynamik('<stranghaar-sorte>', bilder=24, material='vorgabe')   # Morph eigen.dynamik; braucht eine CUDA-GPU",
         [('HumanBodyWeb/core/dienste/haardynamik.py', 'Haardynamik'), ('HumanBodyWeb/core/dienste/haarstraehnen.py', 'Haarstraehnen'),
          ('Stoffsolver/haarauftrag.py', 'Haarauftrag'), ('Stoffsolver/haarsimulation.py', 'Haarsimulation')],
         'Partikelhaar-Dynamik: `ParticleSystem.use_hair_dynamics` mit `particle_system.cloth` (Cloth-Einstellungen des Haars)',
         "ps.use_hair_dynamics = True   # Cloth-Solver auf Strängen; Einstellungen: ps.cloth.settings, Kollision: ps.cloth.collision_settings",
         'gemessen',
         'Gegen Blender 5.2.2 (`Stoffsolver/README.md`, 02.10.2026): ohne Kopfkollision gleich — 32.315 Strähnen 0,001 mm Mittel, 1,42 mm größter (Blender gegen '
         'Blender 0,002 / 14,75 mm); mit Kopfkollision ist Blender selbst chaotisch (4.000 Strähnen: Solver gegen Blender 13,4 / 103 mm, Blender gegen Blender '
         '13,4 / 99 mm; `vergleich_haar.py`). Zeit, 32.315 Strähnen, 13 Bilder: Blender 193 s (57 s Simulation), Solver 1,2 s; 4.000 Strähnen mit Kopfkollision '
         '69 s gegen 0,5 s. Das Projekt wählt den Solver nur per Rezeptzeile; Mindestabstand Haar–Körper 2 mm statt Blenders 31 mm: In Ruhe liegen 97,9 % '
         '(Pixie) bzw. 93,3 % (Hime Cut) der freien Haarpunkte näher als 31 mm an der Körperfläche, und bei 3 mm Rand explodieren am Hime Cut 6 von 30 '
         'gestörten Blender-Läufen, bei 2 mm keiner (README; `ortsmorphe.md`).'),

        ('Haar kämmen',
         'Haarkamm und Bildschirmkamm im Stoffsolver (Python): Führungshaare kämmen',
         "Haarsystem(punkte, dreiecke, einstellungen).kamm(**optionen)   # Haarkamm auf den jetzigen Führungshaaren",
         [('Stoffsolver/haarkamm.py', 'Haarkamm'), ('Stoffsolver/bildschirmkamm.py', 'Bildschirmkamm'), ('Stoffsolver/haarsystem.py', 'Haarsystem')],
         'Partikel-Edit-Modus mit Kamm-Pinsel (`particle.brush_edit`); Curves-Sculpt-Modus (`sculpt_curves.brush_stroke`)',
         "bpy.ops.particle.brush_edit(...)   # Partikel-Edit-Modus, im Hintergrundmodus nur mit GPU-Kontext (Stoffsolver/README.md)",
         'vorhanden',
         'Nicht gegen Blender gemessen: `particle.brush_edit` braucht im Hintergrundmodus einen GPU-Kontext, ebenso die Bearbeitung von Führungshaaren im '
         'Edit-Modus (`Stoffsolver/README.md`, „Was noch fehlt“, 03.10.2026). Beide Operatoren stehen in der Operatorliste von 5.2.2 (`operatoren.txt`).'),
    ]
