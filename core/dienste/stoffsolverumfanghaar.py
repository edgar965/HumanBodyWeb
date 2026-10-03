# -*- coding: utf-8 -*-
"""Stoffsolverumfanghaar — die Zeilen „Haar" der Umfangstabelle des Stoffsolvers (`Stoffsolverumfang`, Stand 02.10.2026).

Maße wie in `Stoffsolverumfangkleid`: Punktabstände Solver ↔ Blender 5.2.2 in mm. Bei der Haar-Erzeugung ist es der Abstand je Wurzel bzw. je Schlüssel (Maximum über alle Haare)."""

__all__ = ['Stoffsolverumfanghaar']

S = 'Stoffsolver/'


class Stoffsolverumfanghaar:
    ZEILEN = [
        ('Haar', 'Haar-Dynamik (Federn, Biegung, Wurzeln, Kopfkollision)',
         [(S + 'haarsimulation.py', 'Haarsimulation'), (S + 'haarnetz.py', 'HaarNetz')], 'blender',
         'Ohne Kollision 32.315 Strähnen 0,001 mm im Mittel, 1,4 mm im Größten. Mit Kopfkollision ist Blender selbst chaotisch (Wurzeln im Kontaktrand): 4.000 Strähnen Blender gegen Blender '
         '13,4 mm, Solver gegen Blender 13,4 mm. Offen bleibt ein Rest bei 1 mm Rand am Dreieck der Wurzel (0,68 mm gegen 0,28 mm Blender-Rauschen).'),
        ('Haar', 'Haar: quality, time_scale, Teilschritte je Bild', [(S + 'haarsimulation.py', 'Haarsimulation')], 'blender',
         'Quality 3, 10, 12, 19 und time_scale 0,5 und 2: 0,000 bis 0,001 mm (die Haarschleife hat Blenders float32-Zählung, 13 Schritte bei Quality 12).'),
        ('Haar', 'Haar-Kontinuum (Dichte, innere Reibung)', [(S + 'haarkontinuum.py', 'Haarkontinuum')], 'blender',
         'Reibung, Zellengröße, Stärke: 0,000 bis 0,002 mm. Blender rechnet den Zielterm bei `dichte_ziel` 0 wirklich als NaN (`ieee_ziel`); starke Ziele lassen Blender NaN erzeugen, der Solver bricht kontrolliert ab. '
         'Der Dichte-Term allein liegt im Rauschen von Blender (2,6 und 10,9 mm gegen 2,4 und 9,9 mm).'),
        ('Haar', 'bending_random', [(S + 'haarzufall.py', 'Haarzufall')], 'blender', 'Zufallsfolge von `psys_frand`: 0,002 mm.'),
        ('Haar', 'Wind, weiches Halten (pin_stiffness), bewegte Kopfhaut',
         [(S + 'haarpin.py', 'Haarpin'), (S + 'haarkopf.py', 'Haarkopf')], 'blender',
         'Wind und Windrauschen, `pin_stiffness` 0,5 bis 50, Verschiebung, Drehung, beides: 0,000 bis 0,008 mm. Bewegter Kopf mit Kollision 0,1 mm (Rauschgrenze 0,07 mm).'),
        ('Haar', 'Schlüsselgewichte (key->weight): Anheften nach Gewicht⁴ ≥ 0,999',
         [(S + 'haargewicht.py', 'Haargewicht'), (S + 'haarnetzgewicht.py', 'HaarNetzGewicht')], 'blender',
         'Host gegen Blender (4 Strähnen): freie Wurzel 0,003 mm statt 8,8 mm, Zwischenpunkt mit Gewicht 1 0,0001 mm statt 27,3 mm; Gerät gegen Host gleich. Greift, wenn `pin_gewicht` gesetzt ist.'),
        ('Haar', 'Haare erzeugen: Wurzeln, Wachsen, Pfade (Dreiecke, Vierecke, Vielecke, Ecken, Volumen)',
         [(S + 'haarverteilung.py', 'Haarverteilung'), (S + 'haarflaechen.py', 'Haarflaechen'), (S + 'haarpolygone.py', 'Haarpolygone'),
          (S + 'haareckenverteilung.py', 'Haareckenverteilung'), (S + 'haarvolumen.py', 'Haarvolumen')], 'blender',
         'Strähne für Strähne gleich (0,0000 bis 0,0016 mm); Vierecke trafen vorher 0 von 100 Wurzeln, jetzt alle. Nicht ebene Vielecke: Blender ist gegen sich selbst nicht reproduzierbar '
         '(nicht initialisierter Speicher in `mesh_tessface_calc`), der Solver rechnet sie flach.'),
        ('Haar', 'Kinder, Clump, Rauheit, Kink, Drall', [(S + 'kinderpfade.py', 'Kinderpfade'), (S + 'kinderverteilung.py', 'Kinderverteilung')], 'blender',
         'Einfache und interpolierte Kinder, gerade und gebogene Führungshaare, sieben Vertexgruppen: höchstens 0,0003 mm.'),
        ('Haar', 'Effektoren, Führungskurven und Texturen auf den Pfaden',
         [(S + 'pfadeffektoren.py', 'Pfadeffektoren'), (S + 'kurvenfuehrung.py', 'Kurvenfuehrung'), (S + 'haartexturen.py', 'Haartexturen')], 'blender',
         'Kraftfelder ≤ 0,004 mm, Führungskurven ≤ 0,0024 mm, Texturen gleich, Kinder nach Bearbeitung 0,0003 mm. '
         'Nicht gebaut: Texturen Bild, Musgrave, Voronoi, Noise auf Haarpfaden (für Kraftfelder gibt es sie).'),
        ('Haar', 'Bezier-, NURBS- und Poly-Kurven als Führung (Curve Guide, Follow Path)',
         [(S + 'kurvenspline.py', 'Kurvenspline'), (S + 'kurvenbezier.py', 'Kurvenbezier'), (S + 'kurvennurbs.py', 'Kurvennurbs')], 'blender',
         'Pfad: 47 Szenen höchstens 0,00025 mm (Poly, Bezier, NURBS, Zyklus, Radius), Haare entlang der Kurve 25 Szenen höchstens 0,0051 mm; als Poly gerechnet 11 bis 1965 mm daneben. '
         'Blender nimmt dafür nur Legacy-Kurven mit `use_path`, nicht die Haar-Kurven. Nicht gebaut: Auto-Griffe, Kurven-Modifikatoren, NURBS-Flächen, Taper.'),
        ('Haar', 'Haare kämmen (Comb)', [(S + 'haarkamm.py', 'Haarkamm'), (S + 'bildschirmkamm.py', 'Bildschirmkamm')], 'quelle',
         'Blenders `brush_edit` stürzt im Hintergrundmodus ab (kein GPU-Kontext), deshalb kein Vergleich. Nach Quelltext gebaut, im 3D-Raum und im Bildschirmraum, mit Handrechnung getestet.'),
        ('Haar', 'Anschluss an die Pipeline', [('HumanBodyWeb/core/dienste/haardynamik.py', 'Haardynamik')], 'quelle',
         'Rezeptzeile `m.haar_dynamik(sorte)`, nur von Hand, nie von der Automatik; Ergebnis ist ein Regler `<sorte>.eigen.dynamik_…`. Mindestabstand 2 mm ist begründet: in Blender explodieren bei 3 mm Rand '
         '6 von 30 gestörten Läufen (Solver 7 von 28), bei 2 mm keiner (0 von 12, beide). Das Render der Haar-Dynamik ist nicht angesehen.'),
    ]
