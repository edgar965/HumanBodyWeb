# -*- coding: utf-8 -*-
"""Werkzeugstofffelder — Gruppe „Stoffsolver: Kraftfelder“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: `Stoffsolver/README.md`, `Stoffsolver/LUECKEN.md` (D2), die Docstrings von `Kraftfeld`, `Windfelder`, `Feldbahnauftrag`,
`Feldtexlesen` und die Tabelle `Stoffsolverumfangkleid`."""

__all__ = ['Werkzeugstofffelder']

S = 'Stoffsolver/'


class Werkzeugstofffelder:
    KENNUNG = 'stofffelder'
    TITEL = 'Stoffsolver: Kraftfelder (Wind, Texturen, bewegte Feldobjekte)'
    EINLEITUNG = (
        'Kraftfelder wirken wie Blenders Effektoren auf den Stoff (und auf Haarpfade): Wind, Punktkraft, Wirbel und mehr, mit Formen, Abfall, Texturen und bewegten Feldobjekten. '
        'Im Auftrag stehen sie unter wind (Liste von Feldern); Windfelder liest sie und baut eine Windkraft, mit bewegung eine Windkraftbewegt. Reihenfolge: 1. ein Feld beschreiben '
        '(art, form, ort, richtung, staerke), 2. bei Bedarf Netz, Textur oder Bahn dazugeben, 3. den Auftrag rechnen (Gruppe „Stoffsolver: Einstiege, Aufträge und Gerät“). '
        'Aus der Pipeline nicht erreichbar; der Stand je Zeile steht in der Tabelle „Der Stoffsolver gegen Blender“ (Reiter Workflow).')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Wind und Punktkraft (Formen, Abfall, Rauschen, Effektor-Gewichte)',
         'Das Tuch mit Wind oder einer Kraft anblasen: ein Feld mit Ort, Richtung, Stärke, Rauschen und Abfall, wie ein Wind-Objekt in Blender.',
         'python',
         '\n'.join((
             '"wind": [{"art": "wind", "form": "ebene", "ort": [x, y, z], "richtung": [x, y, z], "staerke": 1.0, "rauschen": 0.0, "seed": 1, "abfall": "kugel", "max_abstand": <m>}],',
             '"wind_fps": 24, "wind_startbild": 2, "wind_gewicht_alle": 1.0, "wind_gewichte": {"wind": 1.0}',
             "# Python: Stoffoptionen(wind=Windkraft([Kraftfeld(Kraftfeld.WIND, ort=(…), richtung=(…), staerke=1.0)], fps=24, startbild=2))")),
         [(S + 'windfelder.py', 'Windfelder'), (S + 'kraftfeld.py', 'Kraftfeld'), (S + 'windkraft.py', 'Windkraft'), (S + 'feldkraefte.py', 'Feldkraefte')],
         'Arten: wind, kraft (auch Gravitation), wirbel, magnet, harmonisch, fuehrung, turbulenz, luftwiderstand, textur — auch mit Blenders Namen (force, vortex, guide, harmonic, '
         'turbulence, drag, texture). Wind hat die Form ebene, Fluss 1 und Windanteil 1; Wirbel ebene; alle anderen punkt. ort ist der Ort des Objekts, richtung seine Z-Achse (Welt). '
         'Abfall kugel, roehre oder kegel, Richtungssperre zrichtung, Rauschen: noise 0…10 und seed 1…128 wie in Blender (das Rauschen zieht nur für Punkte mit Abfall); die Kraft geht '
         'durch fps (Vorgabe 24). ladung und lennard wirken in Blender auf Stoff nicht (charge wird nie gesetzt, gemessen 0,0000 mm; der Solver rechnet 0), boid und Fluidfluss lehnt der '
         'Solver ab (ValueError). Gemessen: alle Fälle gleich, 0,0000–0,04 mm, im Bereich der Rauschgrenze von Blender; Wind und Felder laufen auf dem Gerät im Graph. '
         'Stand: blender (Stoffsolverumfang, Zeile „Wind und Punktkraft“).'),
        ('Weitere Feldformen und Sichtbarkeit (Oberfläche, Punkte, Linie, Absorption)',
         'Felder, die von einer Fläche, von Punkten oder von einer Linie ausgehen, und Felder, die Kollisionsobjekte abschirmen.',
         'python',
         '\n'.join((
             '{"art": "kraft", "form": "oberflaeche", "netz": {"datei": "<npz mit punkte, dreiecke, optional normalen>"}, "staerke": 1.0, "sicht": true}',
             '"wind_sicht": [{"datei": "<npz mit punkte, dreiecke>", "absorption": 0.0, "epsilon": 0.02}]    # Kollisionsobjekte, die Felder mit "sicht" abschirmen',
             "# Python: Kraftfeld(Kraftfeld.KRAFT, form=Kraftfeld.FORM_OBERFLAECHE, netz=Feldnetz(punkte, dreiecke), sicht=True)")),
         [(S + 'feldnetz.py', 'Feldnetz'), (S + 'feldsicht.py', 'Feldsicht'), (S + 'feldgeometrie.py', 'Feldgeometrie')],
         'Formen punkt, ebene, linie, oberflaeche, punkte. oberflaeche und punkte brauchen ein Feldnetz, sonst ein Fehler (Blender rechnet OBERFLÄCHE ohne Surface-Modifier wie PUNKT). '
         'sicht=true schwächt das Feld durch Kollisionsobjekte (use_absorption); die abschirmenden Objekte stehen in wind_sicht. Die Arten Wirbel, Magnet, Harmonisch, '
         'Führung, Turbulenz und Luftwiderstand laufen über denselben Aufruf (art). Gemessen: Wirbel 0,0002 mm, Magnet 0,011–0,22 mm (chaotisch), Turbulenz 0,0000 mm, Linie, Oberfläche, '
         'Punkte 0,01 mm, Sichtbarkeit 0,0001 mm. Nicht gebaut: bewegte Sichtkörper. Stand: blender.'),
        ('Texturen auf Feldern (Bild, Farbband, Rausch-Arten, Knoten)',
         'Das Feld nach einer Textur wirken lassen: Wolken, Marmor, Holz, ein Bild, ein Farbband oder ein Knotenbaum bestimmen die Kraft je Punkt.',
         'python',
         '\n'.join((
             '{"art": "textur", "tex_modus": "rgb", "nabla": 0.01, "staerke": 1.0, "textur": {"typ": "wolken", "noisegroesse": 0.25, "noisebasis": 0}}',
             '# typ: wolken | holz | marmor | magie | verlauf | stucci | rauschen | bild | musgrave | voronoi | verzerrt | knoten',
             '# Unterbeschreibungen: "farbband": {"elemente": [[0.0, [r, g, b, a]], …]}, "bild": {"daten": {"datei": "<bild.png>"}}, "zufall": {"seed": 1}, "knoten": <Baum>')),
         [(S + 'feldtexlesen.py', 'Feldtexlesen'), (S + 'feldtextur.py', 'Feldtextur'), (S + 'feldtexbild.py', 'Feldtexbild'), (S + 'feldtexfarbband.py', 'Feldtexfarbband'),
          (S + 'feldtexzufall.py', 'Feldtexzufall'), (S + 'feldtexknotenbaum.py', 'Feldtexknotenbaum'), (S + 'feldtexturkraft.py', 'Feldtexturkraft')],
         'tex_modus rgb, gradient oder curl (Blenders texture_mode). nabla (texture_nabla) hat in Blender die Vorgabe 0 — dann ist die Kraft von gradient und curl 0; dort immer nabla setzen. '
         'Bild: PNG oder JPEG mit 8 Bit (datei) oder pixel (Höhe, Breite, Kanäle); Farbband: elemente, interpolation, modus; Zufallstextur: der Strom ist ein Zustand je Textur (seed, '
         'ueberspringen). Gemessen: 17 Texturen, Texturwert aus Blender auf 2,4e-7 (Intensität) und 1,3e-6 (Farbe), Kraft im Tuch 0,0000–0,004 mm, Gerät gleich Host; 73 Textur-Werte und '
         '10 Rauschbasen auf 3e-7; 138 von 141 Knotenbäumen gleich (Rest: float32-Transzendente, ein Gleichstand an einer Fugenkante). Nicht gebaut: Kurven-Knoten, Knotengruppen, '
         'Rauschen-Knoten, stumme Knoten, 16-Bit- und EXR-Bilder; eine Zufallstextur ohne Farbe mit nabla 0 liest in Blender nicht initialisierten Speicher. Stand: blender (03.10.2026).'),
        ('Bewegte Feldobjekte (Lage je Bild)',
         'Das Feldobjekt ändert Ort, Drehung oder Größe von Bild zu Bild oder verformt sein Netz — Wind, Kräfte und Texturen folgen ihm.',
         'python',
         '\n'.join((
             '{"art": "wind", …, "bewegung": {"datei": "<npz mit matrizen (K, 4, 4) [, punkte, dreiecke, normalen]>"}}',
             "# matrizen = object_to_world des Feldobjekts je gerechnetes Bild (Eintrag 0 = Bild wind_startbild); bei oberflaeche/punkte dazu das Netz im Objektraum (V, 3) oder (K, V, 3)")),
         [(S + 'feldbahnauftrag.py', 'Feldbahnauftrag'), (S + 'feldbahn.py', 'Feldbahn'), (S + 'windkraftbewegt.py', 'Windkraftbewegt'),
          (S + 'warpfeldbewegung.py', 'Warpfeldbewegung')],
         'Ort, Richtung, Matrix und Netz des Felds im Auftrag gelten dann nur für Bild 0 und werden von der Bahn überschrieben. Blender nimmt die Lage je Bild ohne Zwischenwerte (ein halbes '
         'Bild Versatz: 1,7 mm). Die Skalierung eines Empty wirkt nicht (0,0000 mm), die Geschwindigkeit des Feldobjekts wirkt bei Stoff nicht. Gemessen: 14 Fälle (Wind, Punktkraft, '
         'Luftwiderstand, Magnet, Wirbel, Textur, Oberfläche und Punkte; verschoben, gedreht, skaliert, per Shape Key verformt) 0,0001–0,02 mm im Mittel; mit festem Feld liegt der Solver '
         '0,12–146 mm daneben. Nicht gebaut: bewegte Sichtkörper, die ein Feld abschirmen. Stand: blender (03.10.2026).'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Windfelder', 'ruft', 'Kraftfeld', 'Kraftfeld(art, **werte): ein Feld je Eintrag von wind'),
        ('Windfelder', 'ruft', 'Windkraft', 'Windkraft(felder, fps, startbild, gewicht_alle, gewichte, sicht)'),
        ('Windfelder', 'ruft', 'Windkraftbewegt', 'Windkraftbewegt(felder, bahnen, **argumente), sobald ein Feld bewegung trägt'),
        ('Windfelder', 'ruft', 'Feldbahnauftrag', 'lesen(bewegung): die Bahn je Feld'),
        ('Windfelder', 'ruft', 'Feldtexlesen', 'textur(angabe): die Textur eines Textur-Felds'),
        ('Windfelder', 'ruft', 'Feldnetz', 'Feldnetz(punkte, dreiecke, normalen) für die Formen Oberfläche und Punkte'),
        ('Feldbahnauftrag', 'ruft', 'Feldbahn', 'Feldbahn(matrizen, punkte, dreiecke, normalen)'),
        ('Feldtexlesen', 'ruft', 'Feldtextur', 'Feldtextur(**werte): die Textur'),
        ('Feldtexlesen', 'ruft', 'Feldtexfarbband', 'Feldtexfarbband(elemente, **werte) aus der Unterbeschreibung farbband'),
        ('Feldtexlesen', 'ruft', 'Feldtexbild', 'Feldtexbild(daten, **werte) aus der Unterbeschreibung bild'),
        ('Feldtexlesen', 'ruft', 'Feldtexzufall', 'Feldtexzufall(**zufall): der Zufallsstrom einer Textur'),
        ('Feldtexlesen', 'ruft', 'Feldtexknotenbaum', 'lesen(knoten): der Knotenbaum'),
        ('Kraftfeld', 'ruft', 'Feldkraefte', 'die Kraft je Feldart'),
        ('Kraftfeld', 'ruft', 'Feldtexturkraft', 'die Kraft einer Textur: rgb, gradient oder curl'),
        ('Windkraft', 'ruft', 'Feldsicht', 'Feldsicht(sicht): Kollisionsobjekte, die Felder mit sicht abschirmen'),
        ('Windkraftbewegt', 'ruft', 'Feldbahn', 'auf(feld, bild): Ort, Richtung und Netz des Felds im laufenden Bild'),
        ('Warpfeldbewegung', 'ruft', 'Windkraftbewegt', 'Warpfeldbewegung.bauen(wp, geraet, windkraft, …) liest die Lagen je Bild, um sie auf das Gerät zu legen'),
    ]
