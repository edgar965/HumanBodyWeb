# -*- coding: utf-8 -*-
"""Stoffsolverumfanguv — die Zeilen „UV und Textur" und „Nicht gebaut" der Umfangstabelle des Stoffsolvers (`Stoffsolverumfang`, Stand 02.10.2026).

Maße: Form = Abstand der UV nach dem besten Ähnlichkeitsabgleich je Insel, in Inseldiagonalen; Lage = größter UV-Unterschied ohne Abgleich; Rauschgrenze (Blender gegen Blender in zwei
Prozessen, bitgleich) 3e-8. Die Messungen: `Stoffsolver/werkzeug/_vergleich/uv/`."""

__all__ = ['Stoffsolverumfanguv']

S = 'Stoffsolver/'


class Stoffsolverumfanguv:
    ZEILEN = [
        ('UV und Textur', 'UV abwickeln (Smart UV Project, Unwrap: LSCM, ABF++)', [(S + 'uvabwicklung.py', 'Uvabwicklung')], 'blender',
         'Form im Mittel 3e-8. Gleichstände der Vordrehung (Kastenfläche, ±90°, gleich große Inseln) entscheidet Blender in float32 anders als der Solver in float64.'),
        ('UV und Textur', 'Löcher füllen, Symmetrie-Pins, scale_to_bounds, correct_aspect',
         [(S + 'uvloecher.py', 'Uvloecher'), (S + 'uvsymmetrie.py', 'Uvsymmetrie'), (S + 'uvaspekt.py', 'Uvaspekt')], 'blender',
         'Form 1,5e-8 bis 6e-8 in 24 + 14 + 82 Zeilen; ohne die Funktion liegt der Solver 0,02 bis 0,16 daneben (Symmetrie-Pins nur bei LSCM, bis 5,6e-3). '
         '`fill_holes` ist nicht die Vorgabe: Aufschneiden verzerrt die Textur weniger.'),
        ('UV und Textur', 'SLIM (MINIMUM_STRETCH)', [(S + 'uvslim.py', 'Uvslim')], 'blender',
         '14 Netze, 10 Iterationen: Form 2e-8 bis 7,5e-8, Energie auf 4 Stellen gleich, keine umgeklappten Dreiecke. Mit vier Heftpunkten weicht Blender selbst rundungsabhängig ab (3 bis 11 von 16 Varianten gleich).'),
        ('UV und Textur', 'Flächen mit Henkeln (Torus, Tasse): automatischer Schnitt', [(S + 'uvhenkelschnitt.py', 'Uvhenkelschnitt')], 'eigen',
         'Blender schneidet nicht selbst (ohne Naht: „Unwrap failed to solve"). Mit denselben Nähten wie der Solver gleich (Form ≤ 5e-8, 18 von 24 Zeilen gleich, 6 erklärt). '
         'Der Algorithmus (Erickson/Whittlesey) ist nicht gegen die Veröffentlichung geprüft.'),
        ('UV und Textur', 'Inseln packen (Pack Islands, AABB)', [(S + 'uvpacker.py', 'Uvpacker')], 'blender',
         'Lage 4e-6 in 41 Fällen (3 bis 100 Inseln, alle Drehmethoden, SCALED/ADD/FRACTION); ab 82 Inseln gibt Blender dem Kastenpacker nur 81.'),
        ('UV und Textur', 'Packen mit Form (CONVEX, CONCAVE), xatlas-Bitmap, optimal_pack',
         [(S + 'uvxatlas.py', 'Uvxatlas'), (S + 'uvoptimalpack.py', 'Uvoptimalpack'), (S + 'uvkonvex.py', 'Uvkonvex')], 'blender',
         'Lage ≤ 5,1e-7 in 59 Fällen, 15 Gegenproben deutlich schlechter. Packdichte gegenüber dem Kasten bei 12 Rechtecken +4,9 % (konvex), +13,2 % (konkav). '
         'Blender 5.2.2 hat `extern/xatlas` nicht mehr: der Bitmap-Packer steht in `uv_pack.cc`. Nicht übernommen: Seitenverhältnis ≠ 1 mit Form; Pins und Zielrahmen gehen mit den Formen nicht (der Solver meldet einen Fehler).'),
        ('UV und Textur', 'Packer-Pins (pin, pin_method), merge_overlap, Zielkachel (udim_source)',
         [(S + 'uvpackpins.py', 'Uvpackpins'), (S + 'uvpackverschmelzung.py', 'Uvpackverschmelzung'), (S + 'uvpackziel.py', 'Uvpackziel'),
          (S + 'uvpackweg.py', 'Uvpackweg')], 'blender',
         'Lage ≤ 5,1e-5 (sonst < 1e-6): Pins in 444 Fällen (alle vier Methoden, Rand, Drehung, Seitenverhältnis), `merge_overlap` in 168, Zielkachel in 298 (CLOSEST, ACTIVE, ORIGINAL_AABB); '
         'sieben Zeilen erklärt (Wurzelsuche bricht bei 1e-4 ab), Gegenprobe 0,1 und mehr, Rauschgrenze 0. '
         'Eine UDIM-Verteilung auf mehrere Kacheln gibt es in Blender 5.2.2 nicht: `pack_islands` packt alles in ein Quadrat und verschiebt es um einen Versatz (140 Läufe). '
         'Nicht in Blender messbar: CUSTOM_REGION mit gesetztem Rechteck (View2D im Hintergrund NaN), `pin_unselected`.'),
        ('UV und Textur', 'UV prüfen (Überlappung, Dehnung, Rand)', [(S + 'uvpruefung.py', 'Uvpruefung')], 'eigen',
         'Gegenprobe der Abwicklung; Blender hat keine solche Prüfung.'),
        ('UV und Textur', 'Texturen backen (Farbe, Cycles EMIT), abtasten, Kamera, Sichtbarkeit',
         [(S + 'texturbacker.py', 'Texturbacker'), (S + 'texturraster.py', 'Texturraster')], 'blender',
         'Texel auf 0,5 Stufen, Abtasten 1,4e-4, Kamera 5e-5 px; Sichtbarkeit: 0,9 % falsch verdeckt, 4,6 % falsch sichtbar (Silhouette, Knicke).'),
        ('UV und Textur', 'UDIM-Kacheln (1001 + u + 10·v)', [(S + 'texturudim.py', 'Texturudim')], 'blender',
         'Cycles-Bake in 16 Kacheln: Farbe auf 0,5 Stufen; Linear mit EXTEND und REPEAT 7e-4. Gebacken nur EMIT mit Rand 0; das Padding von Blender ist nicht verglichen.'),
        ('UV und Textur', 'Fotos auf Texturen (Lochkamera, Verdeckung, Randauffüllung)', [(S + 'texturbacker.py', 'Texturbacker')], 'eigen',
         'Eigenbau. Mit Blenders Projektion nachgerechnet: Farbe ≤ 2,2e-6. Die Orthokamera der Pipeline ist nachgebildet, nicht erprobt.'),
        ('UV und Textur', 'Mipmaps, weiches Mischen der Fotos (Randgewicht)',
         [(S + 'texturmip.py', 'Texturmip'), (S + 'texturrandgewicht.py', 'Texturrandgewicht')], 'eigen',
         'Eigenbau, nicht gegen Blender gemessen (Cycles nutzt für Mipmaps OpenImageIO, dessen Quelltext nicht gelesen ist); mit Handrechnung und Energieerhaltung getestet. '
         'Die Verdeckung bleibt hart, einen Modus „bestes Foto" gibt es nicht.'),
        ('Nicht gebaut', 'Cache/Bake (Punktcache), Szene: Modifier-Stapel, Keyframes, Materialien', [], 'nein',
         'Bewusst und auf Edgars Wort („das brauche ich nicht"): Netz, UV und Textur bleiben am Genesis-Stück, der Solver liefert Verschiebungen je Punkt.'),
        ('Nicht gebaut', 'Körperanpassung (Shrinkwrap, Armature, Lattice, Sculpt)', [], 'nein',
         'Nicht im Solver, sondern in der Pipeline schon in Python (Genesis9: Ortsmorph, Hülle, Haltung).'),
        ('Nicht gebaut', 'Einzelheiten: bewegte Sichtkörper für Felder, Kurven-Knoten, Knotengruppen und Rauschen-Knoten in Texturen, Texturen auf Haarpfaden (Bild, Musgrave, Voronoi, Noise), '
         'Auto-Griffe der Bezier-Kurven, Seitenverhältnis je Insel beim Packen, `scale_to_fit` aus', [], 'nein',
         'Jeweils nach Quelltext bewertet; die Texturen und Kurven gibt es für Kraftfelder bzw. Führungskurven (`Feldtexknotenbaum`, `Kurvenspline`), die Pfad-Texturen der Haare kennen sie nicht.'),
    ]
