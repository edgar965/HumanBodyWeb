# -*- coding: utf-8 -*-
"""Werkzeugstoffhaar — Gruppe „Stoffsolver: Haar“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: `Stoffsolver/README.md`, `Stoffsolver/LUECKEN.md` (H1–H12), die Docstrings der Klassen und die Tabelle `Stoffsolverumfanghaar`.
Die Rezeptzeile `m.haar_dynamik` und der Prozess `haar_lauf.py` stehen in der Gruppe „Stoffsolver: Einstiege, Aufträge und Gerät“."""

__all__ = ['Werkzeugstoffhaar']

S = 'Stoffsolver/'


class Werkzeugstoffhaar:
    KENNUNG = 'stoffhaar'
    TITEL = 'Stoffsolver: Haar (Dynamik, Erzeugen, Kinder, Kurven, Kamm)'
    EINLEITUNG = (
        'Der Stoffsolver kann Haar in zwei Richtungen: Haare ERZEUGEN (Haarsystem mit Haareinstellungen: Wurzeln, Wachsen, Pfade, Kinder, Kurven, Kamm — Blenders Partikelsystem) und '
        'Haare SIMULIEREN (Haarsimulation: Blenders Haar-Dynamik, Cloth auf Strängen). Reihenfolge: 1. Haarsystem(punkte, dreiecke, einstellungen) erzeugt Führungshaare, 2. '
        'system.simulation() liefert (punkte, laengen, wurzelnormalen), 3. Haarsimulation rechnet sie, 4. system.mit_fuehrung(…) und system.straehnen() geben die Strähnen zurück. '
        'Aus der Pipeline erreichbar ist nur m.haar_dynamik (Gruppe „Einstiege“); alles hier nur per direktem Python-Aufruf. Der Stand je Zeile steht in der Tabelle „Der Stoffsolver '
        'gegen Blender“ (Reiter Workflow). Die Haarknoten der Pipeline (haar_knoten) sind Blenders Geometry-Nodes und keine Haar-Dynamik — der Solver ersetzt sie nicht (Gruppe „Schleifen über Blender“).')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Haar-Dynamik direkt (Haarsimulation)',
         'Strähnen fallen lassen: Federn, Haar-Biegung, Schwerkraft, Luft, optional Kopfkollision; Wurzeln bleiben (oder folgen dem Kopf).',
         'python',
         '\n'.join((
             "from Stoffsolver import Haarsimulation",
             "haar = Haarsimulation(punkte, laengen, wurzelnormalen=normalen, koerper=(kopf_punkte, kopf_dreiecke), schwerkraft=(0, -9.81, 0), rechner='auto')",
             "lagen = haar.lauf(24)    # Liste der Schlüssellagen (M, 3), eine je Bild; haar.bericht()")),
         [(S + 'haarsimulation.py', 'Haarsimulation'), (S + 'haarnetz.py', 'HaarNetz'), (S + 'haarbiegung.py', 'Haarbiegung'), (S + 'haardivergenz.py', 'Haardivergenz')],
         'punkte (M, 3) aller Strähnen hintereinander, die Wurzel jeder Strähne zuerst, laengen (S,) mit mindestens 2 Punkten. Die Vorgabe-Schwerkraft der Klasse ist (0, 0, −9,81) (Blenders Z '
         'unten); die Pipeline-Netze sind Y oben, dort (0, −9,81, 0) angeben. Mit koerper bricht der Aufbau ohne CUDA-Motor ab (RuntimeError mit dem Grund), mit rechner=\'numpy\' und Körper '
         'ist es ein ValueError; ohne Körper läuft der Host. Divergiert die Rechnung (Lagen nicht endlich), wirft bild() Haardivergenz; eine endliche, aber absurde Lage zeigt weg_max_mm im '
         'Bericht von Haarauftrag. Gemessen (README, 02.10.2026): 32.315 Strähnen, 13 Bilder, ohne Kollision 0,001 mm im Mittel und 1,42 mm im Größten; Zeit Blender 193 s (57 s Simulation), '
         'Solver 1,2 s; 4.000 Strähnen mit Kopfkollision Blender 69 s, Solver 0,5 s. Mit Kopfkollision ist Blender selbst chaotisch (Wurzeln im Kontaktrand von 31 mm): Blender gegen '
         'Blender 13,4 mm, Solver gegen Blender 13,4 mm. Hime Cut (2.292 Strähnen): bei 3 mm Rand explodieren in Blender 6 von 30 gestörten Läufen, im Solver 7 von 28, bei 2 mm keiner. '
         'Stand: blender.'),
        ('Haar-Kontinuum, bending_random, weiches Halten, Schlüsselgewichte, Wind, bewegte Kopfhaut',
         'Die Zusatzeinstellungen der Haar-Dynamik: Haar-Haar-Kopplung über ein Voxelgitter, zufällige Biegesteifigkeit, Halten an den Ausgangspfad, gemalte Gewichte, Wind, ein Kopf, der sich bewegt.',
         'python',
         '\n'.join((
             "Haarsimulation(…, kontinuum={'zellgroesse': 0.1, 'innere_reibung': 0.3, 'dichte_ziel': 0.0, 'dichte_staerke': 0.0}, biegung_zufall=0.5, zufall_seed=1,",
             "               pin_gewicht=<(M,) je Schlüssel>, pin_steifigkeit=1.0, pin_reibung=0.0, wind=<Windkraft>)",
             "kopf = Haarkopf(kopf_punkte, kopf_dreiecke, haar.netz)",
             "kopf.bewegen(haar, kopf_punkte_neu, koerper_neu=None)    # einmal je Bild vor haar.bild(); oder haar.lauf(24, kopf=<Folge>)")),
         [(S + 'haarkontinuum.py', 'Haarkontinuum'), (S + 'haarzufall.py', 'Haarzufall'), (S + 'haarpin.py', 'Haarpin'), (S + 'haargewicht.py', 'Haargewicht'),
          (S + 'haarnetzgewicht.py', 'HaarNetzGewicht'), (S + 'haarkopf.py', 'Haarkopf'), (S + 'haarkopfbewegung.py', 'Haarkopfbewegung')],
         'Kontinuum aus, wenn innere_reibung = 0 und dichte_staerke = 0 (Blenders Vorgabe); die Reibung ist der Faktor ALLER Wirkungen. dichte_ziel 0 rechnet wie Blender den Zielterm '
         'als NaN (ieee_ziel); starke Ziele lassen Blender NaN erzeugen, der Solver bricht kontrolliert ab. Das Gitter kappt Blender still auf 256 Zellen je Achse. pin_stiffness ist in '
         'Blenders Haar-Vorgabe 0 (nur dann ist das weiche Halten aus); Wurzel, virtueller Punkt und eingefrorene Strähnen sind immer fest. Kopf: bewegung liefert Lagen und Wurzelrahmen je '
         'Bild; die Drehung des Kopfes kommt nur mit wurzelrahmen richtig an. Gemessen: Kontinuum 0,000–0,002 mm (der Dichte-Term allein 2,6 und 10,9 mm gegen 2,4 und 9,9 mm Blender-Rauschen); '
         'bending_random 0,002 mm; Wind und Windrauschen, pin_stiffness 0,5–50, Verschiebung und Drehung des Kopfes 0,000–0,008 mm; Schlüsselgewichte (4 Strähnen, Host gegen Blender) freie '
         'Wurzel 0,003 mm statt 8,8 mm, Zwischenpunkt mit Gewicht 1 0,0001 mm statt 27,3 mm; bewegter Kopf mit Kollision 0,1 mm (Rauschgrenze 0,07 mm). Stand: blender.'),
        ('Wurzeln und Wurzelnormalen (Haarwurzeln)',
         'Zu jeder Strähnenwurzel das nächste Dreieck der Kopfhaut, ihre Normale und den nächsten Punkt auf der Fläche finden — die wurzelnormalen der Haarsimulation.',
         'python',
         '\n'.join((
             "from Stoffsolver import Haarwurzeln",
             "w = Haarwurzeln(kopf_punkte, kopf_dreiecke)",
             "dreieck, fuss = w.naechste(wurzeln)                  # Dreiecksnummer und nächster Punkt je Wurzel",
             "normalen = w.normalen(wurzeln)                       # → Haarsimulation(…, wurzelnormalen=normalen)",
             "punkte, verschiebung = w.anheften(punkte, laengen)   # Wurzeln auf die Fläche setzen, wie Blender beim Aufbau")),
         [(S + 'haarwurzeln.py', 'Haarwurzeln'), (S + 'haarkopf.py', 'Haarkopf')],
         'Blender ordnet jede Wurzel dem nächsten Dreieck der Kopfhaut zu (BLI_bvhtree_find_nearest) — nach der EINGABE-Wurzel, nicht nach der danach auf die Fläche gesetzten. Wer die '
         'Normalen für einen Vergleich mit Blender braucht, übergibt die Eingabe-Wurzeln (am echten Haar mit 32.315 Strähnen: 1,4 mm Abstand zu Blender mit Eingabe-Wurzeln, 10,7 mm mit denen aus '
         'Blenders Bild 1). Eine Wurzel neben der Fläche setzt Blender beim Aufbau auf die Fläche und schiebt die ganze Strähne mit (5 mm daneben → 7,5 mm Verschiebung). Stand: blender (Teil '
         'der Haar-Dynamik).'),
        ('Haare erzeugen (Haarsystem, Haareinstellungen: Wurzeln, Wachsen, Pfade)',
         'Aus einer Emitterfläche Führungshaare machen wie ein Partikelsystem vom Typ Hair: Verteilung, Wachsen, Pfade mit Segmenten; Emitter aus Dreiecken, Vierecken, Vielecken, Ecken oder Volumen.',
         'python',
         '\n'.join((
             "from Stoffsolver.haarsystem import Haarsystem",
             "from Stoffsolver.haareinstellungen import Haareinstellungen",
             "e = Haareinstellungen(anzahl=500, haarlaenge=0.25, kinderart='interpoliert', kinder=10, buendel=0.3)",
             "system = Haarsystem(punkte, dreiecke, e)                   # Emitterfläche (Kopfhaut); optional vierecke=…",
             "punkte_h, laengen, normalen = system.simulation()          # Führungshaare → Haarsimulation(…, wurzelnormalen=normalen, zufall_seed=e.samen)",
             "punkte_h, laengen = system.straehnen(render=True)          # alle Darstellungsstränge: Führungshaare und sichtbare Kinder")),
         [(S + 'haarsystem.py', 'Haarsystem'), (S + 'haareinstellungen.py', 'Haareinstellungen'), (S + 'haarwachstum.py', 'Haarwachstum'), (S + 'haarpfade.py', 'Haarpfade'),
          (S + 'haarverteilung.py', 'Haarverteilung'), (S + 'haarflaechen.py', 'Haarflaechen'), (S + 'haarpolygone.py', 'Haarpolygone'),
          (S + 'haareckenverteilung.py', 'Haareckenverteilung'), (S + 'haarvolumen.py', 'Haarvolumen')],
         'Haareinstellungen sind Blenders ParticleSettings, deutsch benannt, Vorgaben aus der DNA (DNA_particle_types.h): quelle flaechen|ecken|volumen, verteilung jitter|zufall, '
         'haar_segmente, anzeige_stufe, render_stufe, haarlaenge (= normfac · 4) u. v. m.; Haareinstellungen.aus_blender(**dna) nimmt die DNA-Namen (hair_step, childrad, kink_amp …). Emitter mit '
         'Vierecken: Haarsystem(punkte, dreiecke, e, vierecke=<(Q, 4)>); mit Vielecken Haarsystem(punkte, Haarpolygone(punkte, polygone).flaechen(), e) (Zerlegung wie Blender). Nicht abgebildet, weil ohne Wirkung '
         'auf die Strähnenform: Größen, Lebensdauer, Material, Boids, Instanzen, Effektorgewichte, Kräfte. Gemessen: Strähne für Strähne gleich, 0,0000–0,0016 mm; Vierecke trafen vorher 0 von '
         '100 Wurzeln, jetzt alle; die zweite Achse des Wurzelrahmens ist die erste Kante der Fläche (Origspace wirkt bei Haaren nicht). Nicht ebene Vielecke legt Blender unbestimmt an '
         '(nicht initialisierter Speicher in mesh_tessface_calc), der Solver rechnet sie flach. Stand: blender.'),
        ('Kinder, Clump, Rauheit, Kink, Drall',
         'Aus den Führungshaaren Kinder erzeugen und formen: einfache und interpolierte Kinder, Bündelung, Rauheit, Knick (Locke, Welle, Spirale …), Drall.',
         'python',
         '\n'.join((
             "e = Haareinstellungen(kinderart='interpoliert', kinder=10, kinder_render=100, buendel=0.3, buendel_form=0.0, rauheit1=0.1, knick='locke', knick_amplitude=0.2, drall=0.0)",
             "satz, pfade = system.kinder(render=False)    # (Kindersatz, Pfadcache der Kinder) oder (None, None) ohne Kinder")),
         [(S + 'kinderverteilung.py', 'Kinderverteilung'), (S + 'kinderpfade.py', 'Kinderpfade'), (S + 'haarsystem.py', 'Haarsystem')],
         'kinderart keine|einfach|interpoliert; knick keiner|locke|radial|welle|zopf|spirale; die Verteilung der Kinder hängt nur an den Wurzeln der Führungshaare und wird je Modus gemerkt. '
         'Vertexgruppen: Länge, Effektor u. a. (sieben Gruppen gemessen). Gemessen: einfache und interpolierte Kinder, gerade und gebogene Führungshaare, sieben Vertexgruppen höchstens '
         '0,0003 mm. Stand: blender.'),
        ('Kraftfelder, Führungskurven und Texturen auf Haarpfaden',
         'Die gewachsenen Pfade nachträglich durch Wind, Wirbel & Co. oder einer Kurve entlang formen (Curve Guide); Texturen steuern Länge, Dichte, Geschwindigkeit, Kinderwerte.',
         'python',
         '\n'.join((
             "system = Haarsystem(punkte, dreiecke, e, pfadkraefte=Pfadkraefte(felder=[Kraftfeld(…)], fuehrungen=[Kurvenfuehrung(Kurvenspline(…))]))",
             "e = Haareinstellungen(texturen=(<Partikeltextur>, …))    # Plätze für Länge, Bündelung, Knick, Rauheit, Drall, Dichte, Geschwindigkeit")),
         [(S + 'pfadkraefte.py', 'Pfadkraefte'), (S + 'pfadeffektoren.py', 'Pfadeffektoren'), (S + 'kurvenfuehrung.py', 'Kurvenfuehrung'), (S + 'kurvenspline.py', 'Kurvenspline'),
          (S + 'kurvenbezier.py', 'Kurvenbezier'), (S + 'kurvennurbs.py', 'Kurvennurbs'), (S + 'haartexturen.py', 'Haartexturen')],
         'Felder wirken auf die Führungshaare; mit apply_effector_to_children wirken sie auf die Kinder und die Führungshaare bleiben unberührt (Pfadkraefte). Führungskurven (Poly, Bezier, '
         'NURBS) wirken mit apply_effector_to_children je Schlüssel auf die Kinder, nie auf die Führungshaare (Kurvenfuehrung, 18 Szenen mit Kindern gemessen). Bei laufender '
         'Haar-Dynamik wirken Pfadeffektoren nicht (Blender kehrt dann sofort zurück). Der Curve Guide kennt nur den Kugel-Abfall (Röhre und Kegel: Fehler); Taper-Objekte gibt es nicht. '
         'Blender nimmt dafür nur Legacy-Kurven mit use_path, nicht die Haar-Kurven. Gemessen: Kraftfelder höchstens 0,004 mm; Führungskurven Pfad 47 Szenen höchstens 0,00025 mm, Haare entlang '
         'der Kurve 25 Szenen höchstens 0,0051 mm; als Poly gerechnet 11–1965 mm daneben; Texturen gleich, Kinder nach Bearbeitung 0,0003 mm. Nicht gebaut: Auto-Griffe, '
         'Kurven-Modifikatoren, NURBS-Flächen, Texturen Bild, Musgrave, Voronoi und Noise auf Haarpfaden (für Kraftfelder gibt es sie). Stand: blender (Kurven seit 03.10.2026).'),
        ('Haare kämmen (Comb)',
         'Führungshaare mit einem Kammstrich verschieben, Wurzel und Segmentlängen bleiben — im 3D-Raum oder als Mauszug im Bildschirmraum.',
         'python',
         '\n'.join((
             "kamm = system.kamm(erster_fest=True, laengen_halten=True)",
             "kamm.ziehen(von=(x, y, z), nach=(x, y, z), radius=0.02, staerke=0.5)    # Weg im 3D-Raum",
             "system.mit_fuehrung(kamm.punkte)                                        # zurück ins System",
             "Bildschirmkamm(kamm, Bildschirmansicht.orthogonal(breite, hoehe)).ziehen(von_px, nach_px, radius=50.0, staerke=0.5)    # Mauszug in Pixeln")),
         [(S + 'haarkamm.py', 'Haarkamm'), (S + 'bildschirmkamm.py', 'Bildschirmkamm'), (S + 'bildschirmansicht.py', 'Bildschirmansicht'), (S + 'haarsystem.py', 'Haarsystem')],
         'Auswahl pfad|punkt|spitze; laengen_halten (Vorgabe) hält die Segmentlängen, emitter weist Punkte von der Kopfhaut ab. Blenders brush_edit stürzt im Hintergrundmodus ab (kein '
         'GPU-Kontext), mit offenem Blender-Fenster läuft es: Der Bildschirmkamm ist nach dem Quelltext (particle_edit.cc) gebaut und am 03.10.2026 in 13 Szenen gegen Blender gemessen '
         '(Solver gegen Blender höchstens 0,00087 mm bei 2,97 bis 178 mm Wirkung; Aufruf: python14\\Scripts\\python.exe Stoffsolver\\werkzeug\\vergleich_haarform.py kamm, öffnet zweimal ein '
         'Blender-Fenster). Der 3D-Kamm (`ziehen` im Raum) ist nicht gegen Blender gemessen: er misst den Weg als größte Koordinate des Wegvektors (Blender: Bildschirmdistanz). '
         'Ebenso nicht gemessen: die Bearbeitung von Führungshaaren im Edit-Modus. Stand: blender für den Bildschirmkamm, quelle für den 3D-Kamm.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Haarsimulation', 'ruft', 'HaarNetz', 'HaarNetz(punkte, laengen, wurzelnormalen): Federn, Wurzeln, virtuelle Punkte, Rahmen'),
        ('Haarsimulation', 'ruft', 'HaarNetzGewicht', 'HaarNetzGewicht(punkte, laengen, wurzelnormalen, pin_gewicht) bei gemalten Schlüsselgewichten'),
        ('Haarsimulation', 'ruft', 'Haarbiegung', 'Haarbiegung(netz, mittlere_laenge, biegung, daempfung, frei, …): die Biegeziele'),
        ('Haarsimulation', 'ruft', 'Haarpin', 'ziele(netz, …): das weiche Halten (pin_stiffness)'),
        ('Haarsimulation', 'ruft', 'Haarkontinuum', 'Haarkontinuum(**kontinuum): die Haar-Haar-Kopplung'),
        ('Haarsimulation', 'ruft', 'Haarzufall', 'die Biegesteifigkeit je Haar aus bending_random'),
        ('Haarsimulation', 'ruft', 'Haardivergenz', 'pruefen(sim, lage): wirft Haardivergenz, wenn die Lagen nicht endlich sind'),
        ('Haarsimulation', 'ruft', 'Haarkopfbewegung', 'Haarkopfbewegung(sim).bewegen(lagen_neu, koerper_neu, wurzelrahmen) aus kopf_bewegen(): Pins, Ziele und Rahmen je Bild'),
        ('HaarNetzGewicht', 'ruft', 'Haargewicht', 'gemalte Gewichte je Schlüssel: Zwischenpunkte mit Gewicht 1 heften an, freie Wurzel'),
        ('Haarkopf', 'ruft', 'Haarwurzeln', 'Haarwurzeln(kopfpunkte, kopfdreiecke): jede Wurzel dem nächsten Dreieck der Kopfhaut zuordnen'),
        ('Haarkopf', 'ruft', 'Haarsimulation', 'Haarkopf.bewegen(sim, kopf_neu, koerper_neu) ruft sim.kopf_bewegen(lagen, koerper_neu, rahmen)'),
        ('Haarsystem', 'ruft', 'Haareinstellungen', 'die Werte des Partikelsystems (Einstellungen, Texturplätze, Kinderzahl)'),
        ('Haarsystem', 'ruft', 'Haarwachstum', 'erzeugen(punkte, eingabe, einstellungen, …): die Führungshaare'),
        ('Haarsystem', 'ruft', 'Haarpfade', 'fuehrungspfade(…): Pfadcache der Führungshaare mit Segmenten'),
        ('Haarsystem', 'ruft', 'Kinderverteilung', 'verteilen(…): Wurzeln und Eltern der Kinder'),
        ('Haarsystem', 'ruft', 'Kinderpfade', 'berechnen(…): Pfadcache der Kinder'),
        ('Haarsystem', 'ruft', 'Haartexturen', 'von(plaetze, punkte, uv): die Textur-Plätze des Systems'),
        ('Haarsystem', 'ruft', 'Haarkamm', 'Haarkamm(punkte, laengen, **optionen): kamm()'),
        ('Haarsystem', 'ruft', 'Pfadkraefte', 'gruppenwert(…): Kraftfelder und Führungskurven auf den Pfaden'),
        ('Haarsystem', 'ruft', 'Haarflaechen', 'von(dreiecke, vierecke): Emitter mit Vierecken oder Vielecken'),
        ('Haarwachstum', 'ruft', 'Haarverteilung', 'die Wurzeln auf der Emitterfläche'),
        ('Haarpolygone', 'ruft', 'Haarflaechen', 'Haarpolygone.flaechen() baut Haarflaechen.aus_polygonen(ecken, herkunft): die Zerlegung der Vielecke in Blenders Form'),
        ('Haareckenverteilung', 'ruft', 'Haarverteilung', 'Wurzeln aus den Ecken des Emitters (quelle=ecken)'),
        ('Pfadkraefte', 'ruft', 'Pfadeffektoren', 'Kraftfelder auf den Darstellungspfaden'),
        ('Kurvenfuehrung', 'ruft', 'Kurvenspline', 'die Kurve: Poly, Bezier oder NURBS, ausgewertet wie Blender'),
    ]
