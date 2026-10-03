# -*- coding: utf-8 -*-
"""Stoffsolverumfangkleid — die Zeilen „Kleid" und „Körper" der Umfangstabelle des Stoffsolvers (`Stoffsolverumfang`, Stand 02.10.2026).

Jede Zeile: (Bereich, Blender-Funktion, [(Datei, Klasse)], Stand, Anmerkung). Alle Maße sind Punktabstände Solver ↔ Blender 5.2.2 im letzten Bild in mm (Mittel, wo nicht
anders steht); die Messungen mit Szene, Rauschgrenze und Gegenprobe stehen in `Stoffsolver/README.md` und unter `Stoffsolver/werkzeug/_vergleich/`."""

__all__ = ['Stoffsolverumfangkleid']

S = 'Stoffsolver/'


class Stoffsolverumfangkleid:
    ZEILEN = [
        ('Kleid', 'Federn (Struktur, Scherung), Winkelbiegung, Dämpfung',
         [(S + 'federn.py', 'Federn'), (S + 'federkraefte.py', 'Federkraefte'), (S + 'winkelbiegung.py', 'Winkelbiegung')], 'blender',
         'Oberteil (24 Bilder) im Mittel 2,7 mm, Blenders eigenes Rauschen bei 1 µm Störung liegt bei 2,3 mm; die Hose ist chaotisch, ein Ensemble trennt beide nicht (200 Läufe Blender, 500 Solver: Streuung 44,3 gegen 45,2 mm, Verhältnis 1,02 mit Intervall 0,95–1,10). Das Hemd liegt 0,20 mm höher als in Blender, Ursache offen. '
         'Vierecke 0,01 mm; die Zug/Druck-Grenze gilt wie in Blender bei `>=`.'),
        ('Kleid', 'Teilschritte je Bild (float32-Zählung: Quality 12 und 19 rechnen einen mehr)', [(S + 'schrittzahl.py', 'Schrittzahl')], 'blender',
         'Quality 12 rechnet 13 Schritte, 19 rechnet 20: mit Blenders Zählung 0,0001 mm, mit der eingestellten Zahl 12 und 6,6 mm daneben. '
         'Gilt auch für Wind, weiche Ziele, bewegte Pins und Körper und das Haar.'),
        ('Kleid', 'Kollision Körper und Selbst (Dreieck gegen Dreieck), Reibung',
         [(S + 'kollisionsablauf.py', 'Kollisionsablauf'), (S + 'geraeteruhe.py', 'Geraeteruhe')], 'blender',
         'Impulse, Runden und Reibung wie `collision.cc`. Der GPU-Motor rechnet Ruhelängen und -winkel wie Blender in float32 aus denselben Punkten: '
         'nur Selbstkollision am Oberteil 0,13 mm (Blender gegen Blender 0,13 mm), davor +0,5 bis +2,7 mm Bias in z.'),
        ('Kleid', 'Implizites Verfahren (Baraff–Witkin, Blenders CG)', [(S + 'implizitesverfahren.py', 'ImplizitesVerfahren')], 'blender',
         'Ein Schritt gleicht Blender; der Rest ist die float32-Rundung.'),
        ('Kleid', 'Innendruck mit Volumenterm, Presets', [(S + 'aussenkraefte.py', 'Aussenkraefte')], 'blender',
         'Zielvolumen, Faktor, Deckel 200 · V0, Druckgruppe: Host höchstens 0,0004 mm, Gerät 0,0009 mm; die fünf Presets: Host höchstens 0,0026 mm, Gerät 0,0064 mm (erneut gemessen am 03.10.2026). Der Volumenterm gilt nur bei Ausgangsvolumen über 1e-6 m³ (geschlossenes Stück).'),
        ('Kleid', 'Vertexgruppen für Struktur, Scherung, Biegung, Innenfedern',
         [(S + 'federgewichte.py', 'Federgewichte'), (S + 'federsteifigkeit.py', 'Federsteifigkeit')], 'blender',
         'Glatte und zufällige Gruppen: höchstens 0,001 mm. Steifigkeit = Wert + Gewicht · |Maximum − Wert|.'),
        ('Kleid', 'Schrumpfen (shrink_min, shrink_max, Gruppe), auch mit der Zeit',
         [(S + 'schrumpfen.py', 'Schrumpfen'), (S + 'federverlauf.py', 'Federverlauf')], 'blender',
         'Auch zeitabhängig (Blenders Bedingung `cloth.cc:300` wörtlich): 0,0000 mm in vier Fällen, auf Host und GPU.'),
        ('Kleid', 'Innenfedern (use_internal_springs)', [(S + 'innenfedern.py', 'Innenfedern')], 'blender',
         'Wirkung in sechs Fällen höchstens 0,001 mm. Blender gibt die Federliste nicht heraus: verglichen wurde die Wirkung an 49 bis 98 Punkten.'),
        ('Kleid', 'Nähte (use_sewing_springs)', [(S + 'naehte.py', 'Naehte')], 'blender',
         'Lose Kanten als Zugfedern der Länge 0; zum Rechenzeitpunkt trägt die Naht `tension_stiffness`, nicht `_max` (gemessen). Die Ausnahme der Dreiecke an der Naht stimmt.'),
        ('Kleid', 'Anheften hart und weich (pin_stiffness), bewegte Pins',
         [(S + 'zielfedern.py', 'Zielfedern'), (S + 'pinbewegung.py', 'Pinbewegung')], 'blender',
         'Gewicht⁴, Schwelle 0,999, `goal_friction`, bewegte feste und weiche Pins, `time_scale`, Quality 12/19: 0,0000 bis 0,002 mm; auf der GPU im Graph.'),
        ('Kleid', 'Wind und Punktkraft (Ebene, Kugel, Röhre, Kegel, Rauschen, Fluss)',
         [(S + 'windkraft.py', 'Windkraft'), (S + 'kraftfeld.py', 'Kraftfeld')], 'blender',
         'Alle gemessenen Fälle gleich (0,0000 bis 0,04 mm, jeweils im Bereich der Rauschgrenze von Blender); das Rauschen zieht auf der GPU nur für Punkte mit Abfall, wie Blender. '
         'Blender begrenzt `noise` auf 0…10, `seed` auf 1…128.'),
        ('Kleid', 'Weitere Kraftfelder (Wirbel, Magnet, Harmonisch, Führung, Turbulenz, Luftwiderstand, Textur), Formen Linie, Oberfläche, Punkte, Sichtbarkeit',
         [(S + 'feldkraefte.py', 'Feldkraefte'), (S + 'feldnetz.py', 'Feldnetz'), (S + 'feldsicht.py', 'Feldsicht'), (S + 'feldtextur.py', 'Feldtextur'),
          (S + 'windfelder.py', 'Windfelder')], 'blender',
         'Alle gemessenen Fälle gleich, einer erklärt: Wirbel 0,0002 mm, Magnet 0,011 bis 0,22 mm (chaotisch), Turbulenz 0,0000, Linie, Oberfläche, Punkte 0,01 mm, Sichtbarkeit 0,0001, Texturen (alle 73 Textur-Werte '
         'und 10 Rauschbasen aus Blender auf 3e-7). Der Gradient der Textur weicht mit 0,0021 mm ab (Differenzquotient in float32). Ladung und Lennard-Jones sind für Stoff in Blender wirkungslos '
         '(`charge` wird nie gesetzt), Boid und Fluidfluss ebenso: gemessen 0,0000 mm, der Solver rechnet 0 bzw. lehnt sie ab.'),
        ('Kleid', 'Feldtexturen: Bild, Farbband, Rausch-Arten, Knotentexturen (`Texture.evaluate`)',
         [(S + 'feldtexbild.py', 'Feldtexbild'), (S + 'feldtexfarbband.py', 'Feldtexfarbband'), (S + 'feldtexzufall.py', 'Feldtexzufall'),
          (S + 'feldtexknotenbaum.py', 'Feldtexknotenbaum')], 'blender',
         'Alle 17 Texturen: Texturwert aus Blender auf 2,4e-7 (Intensität) und 1,3e-6 (Farbe); die Kraft im Tuch 0,0000 bis 0,004 mm (Mittel), die Wirkung der Textur 8 bis 67 mm, ohne Feld ebenso weit daneben. '
         'Die Zufallstextur stimmt bei bekanntem Samen auf 0,000 mm (mit falschem Samen 15 mm daneben). Auf dem Gerät gleich dem Host; 138 von 141 Knotenbäumen (der Rest: float32-Transzendente, ein Gleichstand an einer Fugenkante). '
         'Nicht gebaut: Kurven-Knoten, Knotengruppen, Rauschen-Knoten, stumme Knoten, 16-Bit- und EXR-Bilder; Zufallstextur ohne Farbe mit Nabla 0 liest in Blender nicht initialisierten Speicher.'),
        ('Kleid', 'Bewegte Feldobjekte (Lage je Bild: Verschieben, Drehen, Skalieren, verformte Netze)',
         [(S + 'feldbahn.py', 'Feldbahn'), (S + 'windkraftbewegt.py', 'Windkraftbewegt'), (S + 'warpfeldbewegung.py', 'Warpfeldbewegung')], 'blender',
         'Alle 14 Fälle gleich (Wind, Punktkraft, Luftwiderstand, Magnet, Wirbel, Textur, Oberfläche und Punkte bewegt oder per Shape Key verformt): 0,0001 bis 0,02 mm im Mittel; '
         'mit festem Feld liegt der Solver 0,12 bis 146 mm daneben (die Skalierung eines Empty wirkt nicht: 0,0000 mm). '
         'Blender nimmt die Lage je Bild ohne Zwischenwerte (ein halbes Bild Versatz: 1,7 mm); die Geschwindigkeit des Feldobjekts wirkt bei Stoff nicht. '
         'Nicht gebaut: bewegte Sichtkörper, die ein Feld abschirmen.'),
        ('Kleid', 'Hydrostatik, Druck-Vertexgruppe', [(S + 'hydrostatik.py', 'Hydrostatik'), (S + 'druckgruppe.py', 'Druckgruppe')], 'blender',
         'Hydrostatik +10, −30, mit Gruppe: höchstens 0,002 mm. −100 liegt in der Streuung der Szene (Solver gegen sich selbst bei 1e-7 m Störung 0,68 mm).'),
        ('Kleid', 'time_scale', [(S + 'stoffmaterial.py', 'StoffMaterial')], 'blender',
         '0,5, 2, 0,7 und mit Quality 10 (1,5) und 20 (0,3): 0,0001 bis 0,0003 mm. Skaliert dt, nicht die Schrittzahl; 0 rechnet nichts.'),
        ('Kleid', 'Biegung an Vielecken (Vierecke, Sechsecke)',
         [(S + 'polygonflaechen.py', 'Polygonflaechen'), (S + 'polygonbiegung.py', 'Polygonbiegung')], 'blender',
         'Vierecke 0,002 bis 0,008 mm statt 0,6 bis 4,4 mm mit der Dreiecksnäherung; Sechsecke 0,0001 bis 0,025 mm (Host). Fünfecke: Szene chaotisch (Streuung 112 bis 295 mm), nicht beurteilbar.'),
        ('Kleid', 'Biegemodell LINEAR', [(S + 'linearbiegung.py', 'Linearbiegung')], 'blender',
         '0,001 bis 0,042 mm.'),
        ('Kleid', 'Choi–Ko-Dämpfung: kubischer Zweig von `fbstar` (`implicit_blender.cc:1672-1712`)',
         [(S + 'choiko.py', 'Choiko'), (S + 'kubischfedern.py', 'Kubischfedern')], 'blender',
         'Der Zweig gilt erst ab Dämpfung · Federlänge ≥ 7,81 (nicht 3,03: das war nur die untere Schranke von |fb|). Zylinder mit Biegedämpfung 1000: 0,0028 mm, ohne den Zweig 2,79 mm; '
         'Tuch von 40 m, 60 % gestaucht (Winkelmodell): 0,003 mm statt 569 mm; Gerät und Host gleich. Bei Dämpfung 100 und 300 wählt Blender den Zweig nie, der Solver ebenso (0,003 und 0,011 mm).'),
        ('Kleid', 'Ruhegestalt (use_dynamic_mesh, rest_shape_key)',
         [(S + 'ruhegestalt.py', 'Ruhegestalt'), (S + 'federnachfuehrung.py', 'Federnachfuehrung')], 'blender',
         'Dynamisches Netz 0,0009 mm, Sprung in Bild 2 0,0008 mm. `rest_shape_key` wirkt in Blender 5.2.2 nicht (`mesh_data_update.cc:354-371`): dort nicht vergleichbar.'),
        ('Körper', 'Mehrere Kollisionsobjekte', [(S + 'koerperantwort.py', 'Koerperantwort')], 'blender',
         'Zwei und drei Körper 0,4 bis 0,8 mm, im Rauschen von Blender (0,3 bis 4,5 mm).'),
        ('Körper', 'collision_quality, Impuls-Klammern, Dicke, Abstand, Culling, Gruppen „Object/Self Collisions"',
         [(S + 'kollisionseinstellungen.py', 'Kollisionseinstellungen')], 'blender',
         'Gleich bis auf `impulse_clamp` 0,04 und `self_impulse_clamp` 0,02: dort ist Blender selbst chaotisch, unklar.'),
        ('Körper', 'Bewegter Körper', [(S + 'warpkoerpersatz.py', 'WarpKoerpersatz')], 'blender',
         'Hub, seitlich, schräg, abrupter Halt, Quality 12: 0,007 bis 0,5 mm im Rauschen von Blender; im CUDA-Graph. Der Host (float64) weicht bei koplanarem Aufprall ab, das Gerät liegt näher an Blender.'),
    ]
