# -*- coding: utf-8 -*-
"""Werkzeugstoffuv — Gruppe „Stoffsolver: UV, Packen, Texturen backen“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: `Stoffsolver/README.md`, `Stoffsolver/LUECKEN.md`, die Docstrings der Klassen und die Tabelle `Stoffsolverumfanguv`. Maße: Form =
Abstand der UV nach dem besten Ähnlichkeitsabgleich je Insel, in Inseldiagonalen; Lage = größter UV-Unterschied ohne Abgleich; Rauschgrenze (Blender gegen Blender) 3e-8."""

__all__ = ['Werkzeugstoffuv']

S = 'Stoffsolver/'


class Werkzeugstoffuv:
    KENNUNG = 'stoffuv'
    TITEL = 'Stoffsolver: UV, Packen, Texturen backen'
    EINLEITUNG = (
        'Der Stoffsolver bringt Blenders UV-Werkzeuge (Smart UV Project, Unwrap, Pack Islands) und das Backen von Texturen in Python mit — für Netze, die noch keine UV haben (etwa ein '
        'Kleidstück aus einem Fotoumriss oder ein TRELLIS-Netz). Reihenfolge: 1. Uvabwicklung(…).rechnen() legt die UV an und packt sie (Uvpacker), 2. Uvergebnis.punktnetz(punkte) '
        'macht ein Netz mit UV je Punkt, 3. Texturbacker (oder Texturudim) backt Farbe aus dem Netz oder aus Fotos in die Textur. Aus der Pipeline (Genesis9, HumanBodyWeb) nicht aufgerufen: '
        'nur per direktem Python-Aufruf (die Fotoprojektion der Runden läuft über Kleidfotoprojektion, nicht über den Texturbacker). Der Stand je Zeile steht in der Tabelle „Der '
        'Stoffsolver gegen Blender“ (Reiter Workflow).')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('UV abwickeln (Smart UV Project, Unwrap: LSCM, ABF++)',
         'Ein Dreiecksnetz ohne UV abwickeln und die Inseln packen: UV je Dreieckseck, Inselnummern, ein Netz mit UV je Punkt.',
         'python',
         '\n'.join((
             "import sys; sys.path.insert(0, 'A:/3DTools')",
             "from Stoffsolver.uvabwicklung import Uvabwicklung",
             "erg = Uvabwicklung(punkte, dreiecke, verfahren='lscm', winkel=66.0, inselrand=0.01).rechnen()",
             "erg.uv       # (T, 3, 2) UV je Dreieckseck, 0…1, v nach oben;  erg.insel (T,) Inselnummer je Dreieck",
             "punkte2, dreiecke2, uv2, herkunft = erg.punktnetz(punkte)    # Netz mit UV je Punkt, an Inselrändern verdoppelt")),
         [(S + 'uvabwicklung.py', 'Uvabwicklung'), (S + 'uvinseln.py', 'Uvinseln'), (S + 'uvparametrisierung.py', 'Uvparametrisierung'), (S + 'uvlscm.py', 'Uvlscm'),
          (S + 'uvabf.py', 'Uvabf'), (S + 'uvschnitt.py', 'Uvschnitt'), (S + 'uvergebnis.py', 'Uvergebnis')],
         'verfahren: \'projektion\' (Smart UV Project), \'lscm\' (Unwrap „Conformal“), \'abf\' (Unwrap „Angle Based“, ABF++ mit LSCM-Rückfall), \'slim\' (eigene Zeile). Optionen: gruppierung '
         '\'winkel\'|\'zusammenhang\', winkel, flaechengewicht, naehte (Punktpaare), inselrand, randmethode, rotation, schneiden (Inseln, die keine Scheibe sind, automatisch aufschneiden; '
         'was nicht flach geht, fällt auf die Projektion zurück — Uvergebnis.gruende sagt es). Die Vorgaben weichen von Blenders Smart UV Project ab (lscm statt Projektion, inselrand 0,01 '
         'statt 0, randmethode \'anteil\', Maßstabsabgleich); verfahren=\'projektion\', massstab_abgleichen=False, randmethode=\'skaliert\', inselrand=0 ist Smart UV Project. Gemessen: '
         'dieselbe Einteilung in Inseln, Form im Mittel 3e-8 Inseldiagonalen (float32 gegen float64), Lage gleich bis auf Gleichstände der Vordrehung (symmetrische Netze wie Würfel und '
         'Kugel entscheidet Blender in float32 anders als der Solver in float64 — Netze mit leichter Störung vergleichen). Stand: blender.'),
        ('SLIM (Unwrap „Minimum Stretch“)',
         'Die verzerrungsarme Abwicklung: SLIM mit Iterationen, Gewichten je Punkt und Umklapp-Schutz.',
         'python',
         '\n'.join((
             "Uvabwicklung(punkte, dreiecke, verfahren='slim', iterationen=10, gewichte=<(N,)>, gewicht_einfluss=1.0, kein_umklappen=False).rechnen()",
             "Uvslim(punkte, dreiecke, iterationen=10, heftpunkte=<Punkte>, heftuv=<UV je Heftpunkt>)    # Heftpunkte nur direkt, ohne Packen")),
         [(S + 'uvslim.py', 'Uvslim'), (S + 'uvslimparametrisierung.py', 'Uvslimparametrisierung'), (S + 'uvabwicklung.py', 'Uvabwicklung')],
         'iterationen (Vorgabe 10 wie Blender), gewichte (Vertexgruppe) mit gewicht_einfluss (weight_factor), kein_umklappen (no_flip), slim_korrigieren (Korrektur entarteter Dreiecke vor SLIM). '
         'SLIM füllt Löcher immer (wie Blender), dreht die Insel nicht um den kleinsten Kasten (das tut nur LSCM) und behält umgeklappte Dreiecke (der Grund nennt die Zahl). Gemessen: '
         '14 Netze, 10 Iterationen, Form 2e-8 bis 7,5e-8, Energie auf vier Stellen gleich, keine umgeklappten Dreiecke. Heftpunkte gehen nur an Uvslim, nicht an Uvabwicklung; dort weicht '
         'Blender selbst rundungsabhängig ab (3 bis 11 von 16 Varianten gleich). Nicht übernommen: der interaktive Weg und skip_init. Stand: blender.'),
        ('Löcher füllen, Symmetrie-Pins, Bildseitenverhältnis, scale_to_bounds',
         'Die Optionen von Unwrap: Löcher mit Dreiecken füllen, Festpunkte symmetrisch wählen, das Seitenverhältnis des Bildes einrechnen, die UV auf 0…1 spannen.',
         'python',
         '\n'.join((
             "Uvabwicklung(punkte, dreiecke, fill_holes=True, symmetrie_pins=True, bildaspekt=<Breite / Höhe des Bildes>, auf_grenzen=False)")),
         [(S + 'uvabwicklung.py', 'Uvabwicklung'), (S + 'uvloecher.py', 'Uvloecher'), (S + 'uvsymmetrie.py', 'Uvsymmetrie'), (S + 'uvaspekt.py', 'Uvaspekt')],
         'fill_holes ist nicht die Vorgabe (Blenders uv.unwrap hat True): True gibt dasselbe Ergebnis wie Blender, verzerrt aber Rohr und Kappe mit Loch viel stärker (Flächenstreuung Rohr '
         '2,3 gegen 0,015) — für Texturen bleibt der Schnitt die Vorgabe. symmetrie_pins (Vorgabe True, Blender hat keinen Schalter): bei einer Insel mit über der Hälfte ihres Randes an einer '
         'Naht heftet LSCM nicht die äußersten Punkte. bildaspekt gilt nur mit dem Packen in Kästen (formmodell=\'aabb\'). Gemessen: Form 1,5e-8 bis 6e-8 in 24 + 14 + 82 Zeilen; ohne die '
         'Funktion liegt der Solver 0,02 bis 0,16 daneben (Symmetrie-Pins nur bei LSCM, bis 5,6e-3). Stand: blender.'),
        ('Henkelschnitt (Torus, Tasse)',
         'Flächen mit Henkeln (Geschlecht ≥ 1) automatisch zur Scheibe aufschneiden, damit sie sich abwickeln lassen.',
         'python',
         '\n'.join((
             "Uvabwicklung(punkte, dreiecke, schneiden=True, henkel=True, blender_reihenfolge=False).rechnen()")),
         [(S + 'uvhenkelschnitt.py', 'Uvhenkelschnitt'), (S + 'uvschnitt.py', 'Uvschnitt'), (S + 'uvabwicklung.py', 'Uvabwicklung')],
         'Eigenbau, ohne Gegenstück in Blender: Blender schneidet nicht selbst (ohne Naht „Unwrap failed to solve“). Der Algorithmus (kürzeste-Wege-Baum + Maximum-Gegenbaum, 2g Schleifen, '
         'Erickson/Whittlesey) ist nicht gegen die Veröffentlichung geprüft. Ohne henkel=True fallen Henkelinseln auf die Projektion zurück. Mit denselben Nähten wie der Solver rechnet Blender '
         'dieselbe Abwicklung: Form höchstens 5e-8, 18 von 24 Zeilen gleich, 6 erklärt (vergleich_uv.py henkel). Stand: eigen (Eigenbau, nur die Abwicklung mit Nähten gegen Blender gemessen).'),
        ('Inseln packen (Pack Islands: Kasten, Form, xatlas, optimal_pack)',
         'UV-Inseln mit Rand in das Einheitsquadrat packen: Kästen wie Blenders Vorgabe oder die Form der Inseln (konvex, konkav), dazu Bitmap-Packer und Optimalpackungen.',
         'python',
         '\n'.join((
             "from Stoffsolver.uvpacker import Uvpacker",
             "packer = Uvpacker(rand=0.01, methode='anteil', rotation='achse_y', formmodell='aabb')    # formmodell 'konvex' | 'konkav'; rotation auch 'beliebig'",
             "uv_neu = packer.packen(uv_ecken, insel)    # uv_ecken (T, 3, 2), insel (T,) Inselnummer; danach packer.faktor, packer.rand_ergebnis")),
         [(S + 'uvpacker.py', 'Uvpacker'), (S + 'uvformpacker.py', 'Uvformpacker'), (S + 'uvxatlas.py', 'Uvxatlas'), (S + 'uvoptimalpack.py', 'Uvoptimalpack'),
          (S + 'uvkonvex.py', 'Uvkonvex')],
         'methode skaliert|addiert|anteil, rotation keine|achse_x|achse_y|achse|kardinal|beliebig, geraet auto|warp|host für den Bitmap-Packer. Welcher Packer gewinnt, entscheidet wie in Blender '
         'der kleinste Umriss. Mit Form rechnet der Packer Sekunden bis Minuten statt Millisekunden (Blender selbst einige Sekunden für 12 Inseln). Blender 5.2.2 hat extern/xatlas nicht '
         'mehr: der Bitmap-Packer steht in uv_pack.cc. Ab 82 Inseln gibt Blender dem Kastenpacker nur 81. Gemessen: Kasten Lage 4e-6 in 41 Fällen (3 bis 100 Inseln, alle Drehmethoden, '
         'SCALED/ADD/FRACTION); Formen Lage höchstens 5,1e-7 in 59 Fällen, 15 Gegenproben deutlich schlechter; Packdichte gegenüber dem Kasten bei 12 Rechtecken +4,9 % (konvex) und '
         '+13,2 % (konkav). Nicht übernommen: Seitenverhältnis ≠ 1 mit Form. Stand: blender.'),
        ('Packer-Pins, merge_overlap, Zielkachel (udim_source)',
         'Beim Packen festgesetzte Inseln respektieren, überlappende Inseln zusammenlegen, in eine bestimmte UDIM-Kachel oder einen Rahmen packen.',
         'python',
         '\n'.join((
             "Uvpacker(rand=0.01, pin_methode='skala', zusammenlegen=True, ziel=Uvpackziel(quelle='naechste')).packen(uv_ecken, insel, pins=<(T, 3) Bool>)",
             "# pin_methode: None | 'skala' | 'drehung' | 'drehung_skala' | 'fest' | 'ignorieren';  Uvpackziel.quelle: 'naechste' | 'aktive' | 'urspruenglich' | 'region'")),
         [(S + 'uvpackweg.py', 'Uvpackweg'), (S + 'uvpackpins.py', 'Uvpackpins'), (S + 'uvpackverschmelzung.py', 'Uvpackverschmelzung'), (S + 'uvpackziel.py', 'Uvpackziel'),
          (S + 'uvpacker.py', 'Uvpacker')],
         'Eine UDIM-Verteilung auf mehrere Kacheln gibt es in Blender 5.2.2 nicht: pack_islands packt alles in ein Quadrat und verschiebt es um einen Versatz (uvedit_unwrap_ops.cc:1596-1654, '
         '140 Läufe). Wer mehrere Kacheln belegen will, packt Inselgruppen nacheinander mit verschiedenen Zielen und setzt die UV zusammen. Pins und ein Rahmen ≠ Einheitsquadrat gehen nur '
         'mit der Form aabb (mit konvex/konkav meldet der Solver einen Fehler). Gemessen (03.10.2026): Lage höchstens 5,1e-5, Pins in 444 Fällen, merge_overlap in 168, Zielkachel in 298 '
         '(CLOSEST, ACTIVE, ORIGINAL_AABB); sieben Zeilen erklärt (die Wurzelsuche bricht bei 1e-4 ab), Gegenprobe 0,1 und mehr, Rauschgrenze 0. Nicht in Blender messbar: CUSTOM_REGION mit '
         'gesetztem Rechteck (View2D im Hintergrund NaN), pin_unselected (der Operator setzt es nie). Stand: blender.'),
        ('UV prüfen (Überlappung, Dehnung, Rand)',
         'Die Gegenprobe einer Abwicklung: überlappen sich Dreiecke, sind welche umgeklappt, wie stark ist die Dehnung, wie groß sind die Abstände.',
         'python',
         '\n'.join((
             "from Stoffsolver.uvpruefung import Uvpruefung",
             "befund = Uvpruefung(punkte, dreiecke, uv, insel).pruefen()    # uv (T, 3, 2), insel (T,)")),
         [(S + 'uvpruefung.py', 'Uvpruefung')],
         'Gemessen wird nur aus der Geometrie: Überlappung (exakter Test mit trennenden Achsen, Berühren erlaubt), Dichte je Dreieck (|UV-Fläche| / 3D-Fläche, normiert), Streckung '
         '(Verhältnis der Singulärwerte σ1/σ2), Abstände. Eigenbau: Blender hat keine solche Prüfung. Stand: eigen.'),
        ('Texturen backen (Farbe je Punkt, Dreieck, Material)',
         'Farben aus dem Netz in eine Textur auf der UV-Abwicklung backen, mit Randauffüllung.',
         'python',
         '\n'.join((
             "from Stoffsolver.texturbacker import Texturbacker",
             "backer = Texturbacker(punkte, dreiecke, uv, groesse=1024, normalen=None, rand_texel=None, falten=True)    # uv (T, 3, 2) oder (N, 2)",
             "textur = backer.farbe_je_punkt(farben)    # auch farbe_je_dreieck(farben) und farbe_je_material(material, palette); uint8 (H, B, C)",
             "Texturbacker.als_png(textur, 'textur.png')    # nur mit Pillow")),
         [(S + 'texturbacker.py', 'Texturbacker'), (S + 'texturraster.py', 'Texturraster'), (S + 'texturfuellung.py', 'Texturfuellung')],
         'Zeile 0 der Textur = oben = v = 1 (OBJ-Konvention wie Genesis9/uvraster.py), Texelmitten bei (s + 0,5) / B. Texel außerhalb jeder Insel sind 0; die Randauffüllung schreibt die Farbe jeder '
         'Insel rand_texel (Vorgabe 8) Texel über ihren Rand hinaus. UV außerhalb 0…1 wiederholen die Kachel (falten=True; für UDIM falten=False). Gebacken wird Cycles EMIT mit Rand 0; das '
         'Padding von Blender ist nicht verglichen. Gemessen: Farbe der Texel auf 0,5 Stufen, Abtasten 1,4e-4, Kamera 5e-5 px. Stand: blender.'),
        ('Fotos auf Texturen (Lochkamera, Verdeckung, Randauffüllung)',
         'Fotofarbe je Texel aus ein oder mehreren Fotos mit Kamera: Verdeckung, Gewicht nach Normale und Blick, Lücken füllen.',
         'python',
         '\n'.join((
             "foto = Texturfoto(bild, Texturkamera(matrix, breite, hoehe), maske=<(H, B) Bool>)",
             "textur, gewicht = backer.foto([foto], grund=None, verdeckung=True, tiefentoleranz_px=1.0, saum_px=0.0)    # gewicht (H, B): 0 = von keinem Foto gesehen")),
         [(S + 'texturbacker.py', 'Texturbacker'), (S + 'texturfoto.py', 'Texturfoto'), (S + 'texturkamera.py', 'Texturkamera'), (S + 'texturprojektion.py', 'Texturprojektion'),
          (S + 'texturrandgewicht.py', 'Texturrandgewicht')],
         'Gewicht = (Normale · Blick)^4, Tiefenpuffer-Verdeckung, Bildmaske; Mischung = Vertrauen · Foto + (1 − Vertrauen) · Grund, Vertrauen = Gewicht / 0,5^4; ohne grund werden Lücken per '
         'Push-Pull aus den sicher gesehenen Texeln gefüllt. saum_px > 0: weiche Randgewichtung der Fotos (Eigenbau). Eigenbau, mit Blenders Projektion nachgerechnet: Farbe höchstens 2,2e-6; '
         'Sichtbarkeit 0,9 % falsch verdeckt, 4,6 % falsch sichtbar (Silhouette, Knicke). Die Orthokamera der Pipeline ist nachgebildet, nicht erprobt. Die Verdeckung bleibt hart, einen '
         'Modus „bestes Foto“ gibt es nicht. Stand: eigen.'),
        ('UDIM-Kacheln (1001 + u + 10·v)',
         'Texturen auf mehrere UDIM-Kacheln backen und abtasten; die Kachel eines UV-Punkts bestimmt die Nummer.',
         'python',
         '\n'.join((
             "from Stoffsolver.texturudim import Texturudim",
             "udim = Texturudim(punkte, dreiecke, uv, groesse=1024, kacheln=None)    # kacheln None = die belegten",
             "texturen = udim.farbe_je_punkt(farben)                                  # {Kachelnummer: Textur uint8 (H, B, C)}",
             "farbe, abdeckung = udim.abtasten(texturen, u, v, lod=0.0, rand='kante')    # rand 'kante' (EXTEND) oder 'wiederholen' (REPEAT)")),
         [(S + 'texturudim.py', 'Texturudim'), (S + 'texturbacker.py', 'Texturbacker'), (S + 'texturmip.py', 'Texturmip')],
         'Kachel (iu, iv) hat die Nummer 1001 + 10 · iv + iu (BKE_image_get_tile_from_pos); u muss in 0…10 liegen, die größte Nummer ist 2000. Backen wie RE_bake_pixels_populate: jedes Dreieck '
         'wird in JEDE Kachel gezeichnet, mit den UV minus dem Versatz der Kachel — ein Dreieck über einer Kachelgrenze füllt beide Kacheln. Kein Mischen über die Kachelgrenze. Gemessen: '
         'Cycles-Bake in 16 Kacheln, Farbe auf 0,5 Stufen; Linear mit EXTEND und REPEAT 7e-4; gebacken nur EMIT mit Rand 0. Stand: blender.'),
        ('Mip-Kette und weiches Mischen (Mipmaps, Randgewicht)',
         'Eine Textur in Detailstufen halbieren und mit LOD abtasten; die Ränder der Fotos weich ausblenden.',
         'python',
         '\n'.join((
             "mip = backer.mip(textur)                       # Texturmip: Mip-Kette, gewichtet mit den belegten Texeln",
             "farbe = mip.abtasten(u, v, lod=0.0, rand='kante')    # lod aus lod_aus_ableitung(…) oder lod_aus_flaeche(…)")),
         [(S + 'texturmip.py', 'Texturmip'), (S + 'texturrandgewicht.py', 'Texturrandgewicht'), (S + 'texturbacker.py', 'Texturbacker')],
         'Eigenbau, nicht gegen Blender gemessen (Cycles nutzt für Mipmaps OpenImageIO, dessen Quelltext nicht gelesen ist); mit Handrechnung und Energieerhaltung getestet. Die leeren Texel '
         'zwischen den Inseln dunkeln die gröberen Stufen nicht ab (Gewichtung mit der Maske). Stand: eigen.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Uvabwicklung', 'ruft', 'Uvinseln', 'Uvinseln(punkte, dreiecke, winkel, flaechengewicht, naehte): Smart-UV-Gruppen oder Zusammenhang'),
        ('Uvabwicklung', 'ruft', 'Uvparametrisierung', 'jede Insel flach legen: projektion, lscm, abf oder slim'),
        ('Uvabwicklung', 'ruft', 'Uvpacker', 'Uvpacker(inselrand, randmethode, rotation, formmodell, geraet, aspekt=): packt die Inseln'),
        ('Uvabwicklung', 'ruft', 'Uvergebnis', 'Uvergebnis(uv, insel, ecken, herkunft, verfahren, gruende, faktor, rand): das Ergebnis von rechnen()'),
        ('Uvabwicklung', 'ruft', 'Uvsymmetrie', 'Symmetrie-Festpunkte für LSCM'),
        ('Uvabwicklung', 'ruft', 'Uvaspekt', 'Seitenverhältnis des Bildes und scale_to_bounds'),
        ('Uvparametrisierung', 'ruft', 'Uvlscm', 'loesen(punkte, tri, winkel, geteilt, rang): LSCM (Conformal)'),
        ('Uvparametrisierung', 'ruft', 'Uvabf', 'ABF++ mit LSCM-Rückfall'),
        ('Uvparametrisierung', 'ruft', 'Uvloecher', 'fuellen(punkte, tri): Löcher mit Dreiecken füllen (fill_holes)'),
        ('Uvparametrisierung', 'ruft', 'Uvschnitt', 'schneiden(punkte, tri, henkel=): Inseln, die keine Scheibe sind, automatisch aufschneiden'),
        ('Uvparametrisierung', 'ruft', 'Uvslimparametrisierung', 'loesen(punkte, tri, herkunft, optionen): verfahren=slim'),
        ('Uvslimparametrisierung', 'ruft', 'Uvslim', 'Uvslim(punkte, dreiecke, iterationen, gewichte, …): SLIM-Iterationen'),
        ('Uvschnitt', 'ruft', 'Uvhenkelschnitt', 'maske(punkte, topo, …): Schnitt für Flächen mit Henkeln'),
        ('Uvpacker', 'ruft', 'Uvformpacker', 'Uvformpacker(packer, inseln, beliebig, geraet): Packen nach der Form der Inseln'),
        ('Uvpacker', 'ruft', 'Uvpackweg', 'Uvpackweg(packer, pin_methode, zusammenlegen, ziel, …): Pins, merge_overlap und Zielkachel'),
        ('Uvformpacker', 'ruft', 'Uvxatlas', 'packen(…): der Bitmap-Packer pack_island_xatlas'),
        ('Uvformpacker', 'ruft', 'Uvoptimalpack', 'packen(…): pack_islands_optimal_pack (nur rotation=beliebig)'),
        ('Uvpackweg', 'ruft', 'Uvpackpins', 'inseln(pins, insel, zahl, …): was festgesetzte Inseln beim Packen dürfen'),
        ('Uvpackweg', 'ruft', 'Uvpackverschmelzung', 'gruppen(uv je Insel): überlappende Inseln zusammenlegen (merge_overlap)'),
        ('Texturbacker', 'ruft', 'Texturraster', 'Texturraster.aus_uv(uv, groesse, falten): welcher Texel zu welchem Dreieck gehört'),
        ('Texturbacker', 'ruft', 'Texturfuellung', 'randfuellen(), luecken(): Randauffüllung und Push-Pull'),
        ('Texturbacker', 'ruft', 'Texturprojektion', 'Texturprojektion(punkte, dreiecke, …).farbe(lage, normale, fotos): Fotofarbe je Texel'),
        ('Texturbacker', 'ruft', 'Texturmip', 'Texturmip(textur, maske): die Mip-Kette'),
        ('Texturprojektion', 'ruft', 'Texturrandgewicht', 'faktor(x, y, saum_px): weiche Randgewichtung der Fotos'),
        ('Texturudim', 'ruft', 'Texturbacker', 'je Kachel ein Texturbacker mit falten=False und den UV minus dem Versatz'),
    ]
