# -*- coding: utf-8 -*-
"""Werkzeugstoffsolver — Gruppe „Stoffsolver: Einstiege, Aufträge und Gerät“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: `Stoffsolver/README.md`, `Stoffsolver/LUECKEN.md`, die Docstrings der genannten Klassen, `.claude/rules/ortsmorphe.md`
und die Tabelle `Stoffsolverumfang*` der Seite. Schema: `Architektur2d3dwerkzeuge` (Kennung, Titel, Einleitung, Zeilen, Beziehungen)."""

__all__ = ['Werkzeugstoffsolver']

S = 'Stoffsolver/'
D = 'HumanBodyWeb/core/dienste/'
G = 'Genesis9/'


class Werkzeugstoffsolver:
    KENNUNG = 'stoffsolver'
    TITEL = 'Stoffsolver: Einstiege, Aufträge und Gerät'
    EINLEITUNG = (
        'Der Stoffsolver (A:\\3DTools\\Stoffsolver) ist Blenders Cloth-, Haar- und UV-Code als eigenes Python/Warp-Paket ohne Bezug zu Genesis: Punkte (N, 3) und Dreiecke (T, 3) '
        'hinein, Punkte an derselben Nummer zurück. Aus der Pipeline erreichbar sind genau zwei Rezeptzeilen — kleid_drapieren mit motor=\'stoffsolver\' und haar_dynamik; alles '
        'andere (Material, Felder, Haar erzeugen, UV, Texturen) nur per Auftrag oder direktem Python-Aufruf. Reihenfolge: 1. Rezeptzeile oder Auftrag wählen, 2. der Prozess läuft in '
        'python14 mit Warp auf der CUDA-GPU, 3. Bericht und Ergebnis lesen. Ohne CUDA-GPU lehnen Pipeline-Motor und Haar-Dynamik ab; Blender (Gruppe „Schleifen über Blender“) ist '
        'dann der Weg — nur nach Ansage von Edgar.')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Kleid drapieren (Stoffsolver, Rezept)',
         'Ein Kleidungsstück der Garderobe einmal gegen die Grundfigur fallen lassen (Falten, Fall, Ausbeulung durch Innendruck) — Blenders Cloth als Warp-Löser auf der GPU.',
         'rezept',
         '\n'.join((
             "m.kleid_drapieren('<kennung>', bilder=24, druck=0.0, motor='stoffsolver', wert=1.0)",
             "# ohne Rezept, im Arbeitsordner der Runde:",
             "Stoffsolverdrapierung(<ordner>).drapieren('<kennung>', bilder=24, druck=0.0, steifigkeit=15.0, fest_oben=0.08)")),
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'), (D + 'stoffsolverdrapierung.py', 'Stoffsolverdrapierung'),
          (S + 'drapierauftrag.py', 'Drapierauftrag')],
         'Ergebnis: Morph <kennung>.eigen.drapiert_<Kürzel des Auftrags> mit einer Verschiebung je Käfigpunkt (Netz, UV und Textur bleiben), linear stellbar 0…1 über wert. '
         'Nur in einer Runde des Auftrags (Rezeptumgebung, sonst ValueError). Das obere Band (fest_oben = 0,08 der Höhe) bleibt hart angeheftet, die Schwerkraft fällt entlang −Y. '
         'Über die Rezeptzeile sind nur bilder und druck einstellbar; steifigkeit und fest_oben nur im Python-Aufruf, Material, Wind, Pins u. a. nur über einen eigenen Auftrag '
         '(Zeile „Stoffsolver als Prozess“). Anders als Newton kann er Druck (Ausbeulung). Ohne CUDA-GPU RuntimeError, Zeitgrenze 900 s. '
         'Zeit (Stoffsolver/README.md, Messungen vom 02.10.2026, vor dem Ausbau, ganzer Prozess, 24 Bilder): Oberteil 17.552 Punkte 2,3 s gegen 55,0 s in Blender, Hose 3.123 Punkte '
         '2,1 s gegen 19,5 s; Ergebnis im Mittel 2,7 mm von Blender (Oberteil, 24 Bilder). Die Automatik schreibt kleid_drapieren nur mit dem Motor Newton '
         '(2d3DIterationen/iterationen2d3d/iterationkleider.py), die Prüf-KI darf es nicht (Begutachtungskritik.VERBOTEN). Stand: gegen Blender 5.2.2 gemessen.'),
        ('Haar-Dynamik (Stoffsolver, Rezept)',
         'Das Stranghaar einer Frisur fallen lassen: Strähnen unter Schwerkraft gegen die ganze Grundfigur, Wurzeln bleiben an der Kopfhaut — Blenders Haar-Dynamik '
         '(Cloth auf Strängen) als Warp-Löser.',
         'rezept',
         '\n'.join((
             "m.haar_dynamik('<sorte>', bilder=24, name='dynamik', wert=1.0, material='vorgabe', mindestabstand_mm=2.0)",
             "# weitere Argumente gehen unverändert an Haarsimulation: kontinuum=…, biegung_zufall=…, zufall_seed=…, abstand=…",
             "# ohne Rezept:",
             "Haardynamik(<ordner>).simulieren('<sorte>', name='dynamik', bilder=24, material='vorgabe', mindestabstand_mm=2.0)")),
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'), (D + 'haardynamik.py', 'Haardynamik'),
          (D + 'haarstraehnen.py', 'Haarstraehnen'), (S + 'haarauftrag.py', 'Haarauftrag')],
         'Ergebnis: Morph <sorte>.eigen.dynamik_<Kürzel des Auftrags> (Delta je Käfigpunkt, Wurzeln genau 0), stellbar 0…1. Nur Stranghaar (Pixie, Hime Cut …); Kartenhaar wirft '
         'ValueError — dort haar_trim, haar_clump, haar_noise u. a. nehmen. Braucht eine CUDA-GPU: ohne sie RuntimeError, nie still durch den Kopf. Mindestabstand Haar–Körper '
         '2 mm statt Blenders 31 mm (gemessen: an Hime Cut laufen bei 1 mm 43 von 30.000 Punkten durch den Kopf, bei 1,5, 2 und 3 mm keiner; ortsmorphe.md, 02.10.2026). '
         'Ab einer Reichweite abstand + dicke von 3,4 mm divergiert die Rechnung an Hime Cut (Blenders Vorgabe 35 mm auch): Haarsimulation wirft Haardivergenz (ein RuntimeError) — den '
         'früheren CUDA-Absturz 700 behebt der Code seit warpplatz.py/haardivergenz.py, während ortsmorphe.md und der Docstring von Haardynamik ihn noch „offen“ nennen. '
         'Zeit (Probe an der Bibliothek, NICHT in der Pipeline gemessen, 24 Bilder, warmer Warp-Cache; ortsmorphe.md, workflowhaardynamik.py, 02.10.2026): Pixie (21.755 Strähnen) '
         '5,7 s, im ersten Lauf des Prozesses 8,8 s; Hime Cut (2.292 Strähnen) 4,4 s, erster Lauf 7,5 s. Das Render der Haar-Dynamik ist nicht angesehen. '
         'Nur von Hand: Automatik und Prüf-KI wählen sie nie. Stand: Pipeline-Anschluss nur nach Quelltext (Stoffsolverumfang: quelle); die Dynamik selbst gegen Blender gemessen '
         '(Gruppe „Stoffsolver: Haar“).'),
        ('Stoffsolver als Prozess (stoff_lauf.py)',
         'Ein Kleidstück gegen einen Körper rechnen wie Blender mit drapieren.py: Auftrag als JSON, Ergebnis als npz, Bericht als JSON — der Weg, den die Pipeline selbst '
         'geht und den jede Session für eigene Läufe nimmt.',
         'cli',
         '\n'.join((
             r'cd A:\3DTools',
             r'python14\Scripts\python.exe Stoffsolver\werkzeug\stoff_lauf.py --auftrag <auftrag.json>',
             '# Pflicht in der auftrag.json: {"koerper": "<k.npz>", "stueck": "<s.npz>", "aus": "<aus.npz>", "bericht": "<bericht.json>"}',
             '# häufig: "bilder": 24, "druck": 0, "steifigkeit": 15, "anheften": [<Punktnummern>], "schwerkraft": [0, -9.81, 0], "material": "vorgabe", "rechner": "warp"')),
         [(S + 'drapierauftrag.py', 'Drapierauftrag'), (S + 'auftragsoptionen.py', 'Auftragsoptionen'), (S + 'simulationsbericht.py', 'Simulationsbericht')],
         'k.npz und s.npz tragen punkte (N, 3) und dreiecke (T, 3); s.npz optional vierecke (V, 4) sowie vielecke_ecken und vielecke_anfang. Die Punkte kommen in aus.npz an derselben '
         'Nummer zurück (float32). Weitere Schlüssel: bilder (24; Bild 1 ist die Ausgangslage, gerechnet werden bilder − 1), druck, steifigkeit (15), biegung (0,5), qualitaet '
         '(Vorgabe 6 wie drapieren.py), anheften, schwerkraft (Vorgabe Y unten; bei Z oben [0, 0, −9,81] angeben), selbstkontakt, abstand und dicke (je 0,004 m), selbstabstand '
         '(0,003 m), material, rechner, kollision, cg — dazu die Schlüssel der Gruppen „Stoffsolver: Material, Federn, Anheften, Druck, Kollision“ und „Stoffsolver: Kraftfelder“. '
         'Bericht: punkte, bilder, weg_mittel_mm, weg_max_mm, solver, dazu federn, schritte, sekunden, kontakte, rechner, cg_mittel, cg_nicht_konvergiert sowie import_s und lauf_s; '
         'ein Fehler steht als {"fehler": "<Typ>: <Text>"} im Bericht, der Prozess endet trotzdem normal. Der Prozess läuft in python14, nicht im Django-Server (Warp und CUDA '
         'gehören nicht dorthin). Derselbe Auftrag läuft in Blender (Gruppe „Schleifen über Blender“, drapieren.py). Stand: gegen Blender 5.2.2 gemessen; Auftragsweg und '
         'direkter Weg bitgleich (8 von 8 Fällen, LUECKEN.md P1).'),
        ('Drapierauftrag.rechnen (Arrays statt Dateien)',
         'Dasselbe wie der Prozess, aber mit NumPy-Arrays im eigenen Python: Tuch auf Körper, die Lage danach und ein Bericht.',
         'python',
         '\n'.join((
             "import sys; sys.path.insert(0, 'A:/3DTools')",
             "from Stoffsolver import Drapierauftrag",
             "lage, bericht = Drapierauftrag.rechnen(stueck_punkte, stueck_dreiecke, koerper_punkte, koerper_dreiecke,",
             "                                       bilder=24, material='vorgabe', schwerkraft=(0, -9.81, 0), anheften=(), druck=0.0)")),
         [(S + 'drapierauftrag.py', 'Drapierauftrag'), (S + 'stoffnetz.py', 'StoffNetz'), (S + 'stoffmaterial.py', 'StoffMaterial'), (S + 'kollider.py', 'Kollider'),
          (S + 'stoffsimulation.py', 'Stoffsimulation')],
         'Weitere Argumente: steifigkeit=15, biegung=0.5, qualitaet=None, selbstkontakt=True, abstand=0.004, dicke=0.004, selbstabstand=0.003, rechner=\'auto\', kollision=\'blender\', '
         'cg=\'blender\', optionen (Stoffoptionen), naehte (K, 2), material_felder, bewegung, pins, vierecke, vielecke, ruhe, verlauf. Die Vorgaben sind die von drapieren.py; Blenders '
         'eigene Vorgaben (0,015 m, Dicke 0) ergäben 13,3 statt 7,1 mm Abstand zum Körper (Docstring Drapierauftrag, 02.10.2026). Achsen: Die Netze von 3dTools sind Y oben, '
         'Vorgabe (0, −9,81, 0); Blenders Szene fällt nach −Z. lage ist (N, 3), Bild 1 ist die Ausgangslage. Ohne CUDA-GPU rechnet rechner=\'auto\' auf dem Host (NumPy): Hose, '
         '12 Bilder 462 s gegen 10,1 s in Blender (ganzer Prozess; README Messungen, 02.10.2026) — nur als Referenz, siehe Zeile „Gerät und Rechenweg“. Stand: gegen Blender 5.2.2 gemessen.'),
        ('Stoffsimulation (Bild für Bild, bewegter Körper und Pins)',
         'Den Ablauf selbst steuern: Zeitschritte, Lagen je Bild, Körper und angeheftete Punkte je Bild bewegen.',
         'python',
         '\n'.join((
             "from Stoffsolver import Stoffsimulation, StoffNetz, StoffMaterial, Kollider",
             "sim = Stoffsimulation(StoffNetz(punkte, dreiecke), StoffMaterial.baumwolle(), kollider=Kollider(koerper_punkte, koerper_dreiecke),",
             "                      anheften=[<Punktnummern>], schwerkraft=(0, -9.81, 0), selbstkollision=True, rechner='auto')",
             "lagen = sim.lauf(24)    # Liste (N, 3), eine je Bild; sim.x ist die letzte, sim.bericht() der Bericht",
             "sim.lauf(24, bewegung=<Körperlagen je Bild>, pins=<Lagen aller Punkte je Bild>)    # oder je Bild sim.koerper_bewegen(…), sim.pins_bewegen(…) vor sim.bild()")),
         [(S + 'stoffsimulation.py', 'Stoffsimulation'), (S + 'stoffnetz.py', 'StoffNetz'), (S + 'stoffmaterial.py', 'StoffMaterial'), (S + 'kollider.py', 'Kollider'),
          (S + 'stoffoptionen.py', 'Stoffoptionen')],
         'lauf(bilder) rechnet bilder Bilder (Drapierauftrag: bilder − 1). Die Zeit läuft in Bildern, nicht in Sekunden: ein Bild = material.schritte Zeitschritte, Schwerkraft × 0,001, '
         'Luft × 0,01 (README) — wer Sekunden und 9,81 einsetzt, liegt beim Verhältnis Feder zu Schwerkraft um rund 1.000 daneben. Je Zeitschritt wie Blender: Geschwindigkeit lösen '
         '(Blenders CG) → vorläufige Lage → Kollision korrigiert die Geschwindigkeit → Lage → angeheftete Punkte zurück. kollision=\'blender\' (Dreieck gegen Dreieck, Vorgabe) oder '
         '\'schnell\' (Näherung nächster Hautpunkt, nur Host); weitere Kollisionskörper nur mit kollision=\'blender\'. koerper_bewegen und pins_bewegen einmal je Bild vor bild() rufen, '
         'auch mit gleicher Lage; pins_bewegen ohne Pins ist ein RuntimeError, koerper_bewegen ohne Kollisionsablauf ebenso. Stand: gegen Blender 5.2.2 gemessen.'),
        ('Haar-Dynamik als Prozess (haar_lauf.py)',
         'Strähnen durch die Haar-Dynamik schicken: Auftrag als JSON wie bei stoff_lauf.py, Ergebnis als npz.',
         'cli',
         '\n'.join((
             r'cd A:\3DTools',
             r'python14\Scripts\python.exe Stoffsolver\werkzeug\haar_lauf.py --auftrag <auftrag.json>',
             '# Pflicht in der auftrag.json: {"straehnen": "<s.npz>", "aus": "<aus.npz>", "bericht": "<bericht.json>"}',
             '# häufig: "koerper": "<k.npz>", "bilder": 24, "schwerkraft": [0, -9.81, 0], "material": "vorgabe", "dicke": 0.02, "rechner": "warp", "haarargumente": {"abstand": 0.0034}')),
         [(S + 'haarauftrag.py', 'Haarauftrag'), (S + 'haarsimulation.py', 'Haarsimulation')],
         's.npz: punkte (M, 3) aller Strähnen hintereinander, die WURZEL JEDER STRÄHNE ZUERST; laengen (S,) Punkte je Strähne (mindestens 2); optional normalen (S, 3), die Flächennormale '
         'der Kopfhaut an der Wurzel. k.npz (optional): punkte (N, 3), dreiecke (T, 3), der Kollisionskörper (Kopf oder ganzer Körper); die Haarkollision gibt es nur auf dem Gerät. '
         'Weitere Schlüssel: material (vorgabe|baumwolle|seide|jeans|leder|gummi; vorgabe sind 5 Zeitschritte je Bild, nicht die Qualität 6 des Stoffs), material_felder, dicke (0,02 m), '
         'rechner, haarargumente {kontinuum, biegung_zufall, zufall_seed, haarnummern, abstand, kontinuum_zellen, pin_steifigkeit …}: JSON-fähige Argumente von Haarsimulation; ein Schlüssel, '
         'der schon ein eigener Schlüssel ist, wirft ValueError. Bericht: punkte, straehnen, bilder, weg_mittel_mm, weg_max_mm, wurzel_weg_max_mm (muss 0 sein), solver, dazu der Bericht '
         'von Haarsimulation, import_s und lauf_s. Mit Körper und ohne CUDA-Motor bricht der Aufbau ab (RuntimeError), mit rechner=\'numpy\' und Körper ist es ein ValueError. '
         'Stand: gegen Blender 5.2.2 gemessen (Gruppe „Stoffsolver: Haar“).'),
        ('Gerät und Rechenweg (rechner, Warp, CUDA)',
         'Prüfen, ob der Solver auf der GPU rechnen kann, und den Rechenweg wählen: Gerät (Warp, CUDA-Graph), Host (NumPy, Referenz) oder automatisch.',
         'python',
         '\n'.join((
             "from Stoffsolver.warpumgebung import Warpumgebung",
             "Warpumgebung.verfuegbar()      # Warp importierbar und initialisiert?",
             "Warpumgebung.geraet('auto')    # 'cuda:0' mit GPU, sonst 'cpu'; None, wenn Warp fehlt",
             "Warpumgebung.fehler()          # der Grund, wenn Warp fehlt",
             "# überall: rechner='auto' | 'warp' | 'numpy'    (im Auftrag: \"rechner\": \"warp\")")),
         [(S + 'warpumgebung.py', 'Warpumgebung'), (S + 'warpmotor.py', 'WarpMotor'), (S + 'stoffsimulation.py', 'Stoffsimulation'), (S + 'haarsimulation.py', 'Haarsimulation')],
         'rechner=\'auto\': Gerät, wenn Warp und eine CUDA-GPU da sind, sonst Host (NumPy, float64). \'warp\': Gerät oder Fehler (RuntimeError: der Gerätemotor braucht eine CUDA-GPU) — so '
         'stellen Stoffsolverdrapierung und Haardynamik es ein, deshalb lehnen sie ohne GPU ab. \'numpy\': Host erzwingen (die Referenz der Tests). Der Host ist keine Alternative: Hose, 12 Bilder '
         '462 s gegen 10,1 s in Blender (README, 02.10.2026, blender_roundtrip.py --host). Das Gerät rechnet in float32 wie Blender, ein ganzer Zeitschritt ist ein CUDA-Graph (WarpMotor); '
         'zwei Läufe sind bitgleich (README). Die Haarkollision gibt es nur auf dem Gerät. Warp 1.17.0 in python14, GPU dieses Rechners RTX PRO 4500 Blackwell (README Messungen; CLAUDE.md). '
         'Der Kernel-Cache liegt in Stoffsolver/_warp_cache/ (nicht im Systemordner, nicht in git); der erste Lauf nach einer Änderung an Warp-Kernen übersetzt neu und dauert länger. '
         'Stand: Gerät gegen Blender gemessen, Host als Referenz der Tests.'),
        ('Auftragsschlüssel über Drapierauftrag hinaus (Auftragsoptionen)',
         'Die Schlüssel der auftrag.json, die die Bausteine des Ausbaus einschalten, und ihre Übersetzung in Stoffoptionen, Nähte, Materialfelder und Körperbewegung.',
         'python',
         '\n'.join((
             "from Stoffsolver.auftragsoptionen import Auftragsoptionen",
             "werte = Auftragsoptionen.lesen(auftrag, anzahl_punkte)   # → optionen, naehte, material_felder, bewegung, pins, ruhe, verlauf",
             "# Drapierauftrag.ausfuehren(auftrag) tut das selbst; der Prozess stoff_lauf.py ebenso")),
         [(S + 'auftragsoptionen.py', 'Auftragsoptionen'), (S + 'stoffoptionen.py', 'Stoffoptionen'), (S + 'windfelder.py', 'Windfelder'),
          (S + 'kollisionskoerper.py', 'Kollisionskoerper'), (S + 'federgewichte.py', 'Federgewichte'), (S + 'federverlauf.py', 'Federverlauf')],
         'Alle Schlüssel sind optional; ohne sie rechnet der Auftrag bitgleich wie vorher. Dateien sind npz. material_felder {Feld: Wert} (alles aus StoffMaterial.FELDER); gruppen '
         '(npz je Punkt (N,): struktur, scherung, biegung, intern, schrumpfen, pin, pin_mitglied, druck, ohne_koerperkontakt, ohne_selbstkontakt, naehte (K, 2)); pin {steifigkeit, reibung, '
         'standard}; wind (Liste von Feldern) mit wind_fps, wind_startbild, wind_gewicht_alle, wind_gewichte, wind_sicht; fluiddichte; druck_nur_mit_schalter; koerper_weitere; '
         'kollision_qualitaet; impulse_clamp; self_impulse_clamp; bewegung (npz lagen (B, M, 3)); pins_bewegung (npz lagen (B, N, 3)); ruhe; ruhe_dynamisch; schrumpfen_verlauf; '
         'das Biegemodell steht in material_felder (\'biegemodell\'). Jeder Schlüssel wird in der Gruppe erklärt, zu der seine Funktion gehört (Material, Federn, Anheften, Druck, '
         'Kollision, Kraftfelder). Aus der Pipeline setzt Stoffsolverdrapierung nur koerper, stueck, aus, bericht, bilder, druck, steifigkeit, schwerkraft, anheften und rechner. '
         'Stand: je Funktion gegen Blender gemessen.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellFormMixin', 'ruft', 'Rezeptumgebung', 'drapierung(motor): der Drapierer des Motors, ValueError außerhalb einer Runde'),
        ('ModellFormMixin', 'ruft', 'Stoffsolverdrapierung', 'drapieren(kennung, bilder, druck, name=): legt den Morph <kennung>.eigen.drapiert_<Kürzel> ab'),
        ('ModellHaarMixin', 'ruft', 'Rezeptumgebung', 'haardynamik(): der Arbeiter der Haar-Dynamik, ValueError außerhalb einer Runde'),
        ('ModellHaarMixin', 'ruft', 'Haardynamik', 'simulieren(sorte, name, bilder, material=, mindestabstand_mm=, **haarargumente)'),
        ('Stoffsolverdrapierung', 'ruft', 'Drapierauftrag', 'als Prozess python14 stoff_lauf.py --auftrag: Drapierauftrag.ausfuehren(auftrag)'),
        ('Haardynamik', 'ruft', 'Haarstraehnen', 'Haarstraehnen(punkte, ketten, haut): Strähnen mit der Wurzel zuerst, delta(nachher) → Delta je Käfigpunkt'),
        ('Haardynamik', 'ruft', 'Haarauftrag', 'als Prozess python14 haar_lauf.py --auftrag: Haarauftrag.ausfuehren(auftrag)'),
        ('Drapierauftrag', 'ruft', 'Auftragsoptionen', 'lesen(auftrag, anzahl): optionen, naehte, material_felder, bewegung, pins, ruhe, verlauf'),
        ('Auftragsoptionen', 'ruft', 'Stoffoptionen', 'Stoffoptionen(gewichte=, wind=, koerper_weitere=, …) aus den Schlüsseln des Auftrags'),
        ('Auftragsoptionen', 'ruft', 'Windfelder', 'lesen(auftrag): die Kraftfelder von wind als Windkraft'),
        ('Auftragsoptionen', 'ruft', 'Kollisionskoerper', 'Kollisionskoerper(punkte, dreiecke, **) je Eintrag von koerper_weitere'),
        ('Auftragsoptionen', 'ruft', 'Federgewichte', 'Federgewichte(anzahl, **werte): die Vertexgruppen aus gruppen'),
        ('Auftragsoptionen', 'ruft', 'Federverlauf', 'Federverlauf(minimum, maximum, gewichte) aus schrumpfen_verlauf'),
        ('Drapierauftrag', 'ruft', 'StoffNetz', 'StoffNetz(punkte, dreiecke, naehte=, vierecke=, vielecke=)'),
        ('Drapierauftrag', 'ruft', 'StoffMaterial', 'Preset per getattr(StoffMaterial, material)(), dann mit(zug=, druck=, biegung=, schritte=, …)'),
        ('Drapierauftrag', 'ruft', 'Kollider', 'Kollider(koerper_punkte, koerper_dreiecke, abstand=, dicke=, reibung=)'),
        ('Drapierauftrag', 'ruft', 'Stoffsimulation', 'Stoffsimulation(stoff, werte, kollider, anheften, schwerkraft, …); lauf(bilder − 1)'),
        ('Stoffsimulation', 'ruft', 'Stoffoptionen', 'ziele(), aussenkraefte(), kollisionseinstellungen(): was die Optionen einschalten'),
        ('Stoffsimulation', 'ruft', 'Simulationsbericht', 'von(sim): Bericht mit Punkten, Federn, Schritten, Sekunden, Kontakten, CG'),
        ('Stoffsimulation', 'ruft', 'Warpumgebung', 'verfuegbar(), warp(), geraet(): Warp und CUDA-Gerät prüfen'),
        ('Stoffsimulation', 'ruft', 'WarpMotor', 'WarpMotor(wp, geraet, punkte, dreiecke, …): ein Zeitschritt als CUDA-Graph; schritte(), lage()'),
        ('Haarauftrag', 'ruft', 'Haarsimulation', 'Haarsimulation(punkte, laengen, material, schwerkraft, wurzelnormalen, koerper, rechner, **haarargumente); bild() je Bild'),
        ('Haarauftrag', 'ruft', 'StoffMaterial', 'Preset per getattr(StoffMaterial, material)(), dann mit(**material_felder)'),
        ('Haarsimulation', 'ruft', 'Warpumgebung', 'verfuegbar(), warp(), geraet(): ohne CUDA kein Gerätemotor'),
        ('Haarsimulation', 'ruft', 'WarpMotor', 'WarpMotor mit Haar-Biegung; ohne ihn bricht der Aufbau mit Körper ab'),
    ]
