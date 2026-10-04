# -*- coding: utf-8 -*-
"""Werkzeugblenderschleife — Gruppe „Schleifen über Blender (nur nach Ansage von Edgar)“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: `Engine2d3dKleiderblender` (Klassenkommentar und Code), `Haarknotenauftrag`, `effekte/blender/engine2d3dkleider/*.py`,
`.claude/rules/projekt.md`, `engine2d3dkleider.md`, `ortsmorphe.md`, `blendermodell.md`, `Stoffsolver/README.md` und `workflowzeiten.py` (Zeiten mit Quelle)."""

__all__ = ['Werkzeugblenderschleife']

S = 'Stoffsolver/'
D = 'HumanBodyWeb/core/dienste/'
G = 'Genesis9/'
R = 'python14\\Scripts\\python.exe Stoffsolver\\werkzeug\\'


class Werkzeugblenderschleife:
    KENNUNG = 'blenderschleife'
    TITEL = 'Schleifen über Blender (nur nach Ansage von Edgar)'
    EINLEITUNG = (
        'NUR NACH ANSAGE VON EDGAR. Blender ist der Weg, wenn der Stoffsolver nicht geht (keine CUDA-GPU, ein Fehler im Solver, ein Ergebnis, das gegen die Referenz geprüft werden '
        'soll) und für die Haar-Knoten, für die es keinen Solver-Ersatz gibt. Die Pipeline wählt Blender nie selbst: Vorgabe beim Drapieren ist Newton, die Automatik schreibt '
        'kleid_drapieren nur mit Newton und haar_knoten nie; Blender kommt nur als Rezeptzeile in einer Runde (motor=\'blender\', m.haar_knoten), jeder Aufruf ein eigener Blender-Prozess '
        'über die EINE Arbeiterklasse Engine2d3dKleiderblender. Reihenfolge: 1. die Entscheidungsregel unten lesen, 2. die Rezeptzeile in die Runde schreiben (POST …/begutachtung/ '
        '{aufrufe}), 3. Ergebnis als Morph prüfen. Die Messwerkzeuge blender_roundtrip.py und blender_zeiten.py starten Blender ebenfalls und gelten dieselbe Regel.')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Wann Blender, wann Stoffsolver, wann Newton — und die Regel „nur nach Ansage“',
         'Die Entscheidungsregel für den Löser beim Drapieren, und wer die Blender-Schleife starten darf.',
         'regel',
         'Kein Aufruf. Blender nur nach Ansage von Edgar: m.kleid_drapieren(…, motor=\'blender\') und m.haar_knoten(…) schreibt weder die Automatik noch die Prüf-KI.',
         [],
         'NUR NACH ANSAGE VON EDGAR. Quellen: .claude/rules/projekt.md („Blender nicht von selbst starten — den Blender-Test-Weg nutzt Edgar nicht mehr“), Edgar 30.09.2026 („blender aufrufe sind '
         'möglich“, engine2d3dkleider.md: Blender darf als Arbeiter für einzelne Rechnungen dazukommen, aber nur über EINE Arbeiterklasse) und die Regel des Reiters Tools (Edgar, 03.10.2026: '
         'Schleifen über Blender nur nach Ansage). Die ältere Aussage in effekte.md (12.09.2026, „Ich möchte mich nicht mit blender herumschlagen“) betrifft den Effekte-Bereich. '
         'Entscheidung beim Drapieren: Newton (Vorgabe, Automatik) kann keinen Druck: Base Shirt (7.552 Punkte), 24 Bilder, 142 s beim ersten Aufruf mit Kernelübersetzung, 590 ms '
         'je Bild (ortsmorphe.md); die 14,2 s eines warmen Laufs sind errechnet, nicht gemessen (workflowzeiten.py). Stoffsolver, wenn Druck (Ausbeulung) oder Blenders Verhalten gewünscht ist und eine CUDA-GPU da ist: Oberteil 24 Bilder 2,3 s. Blender, wenn der '
         'Stoffsolver ausfällt oder die Referenz nötig ist: Hose 19,5 s, Oberteil 55,0 s je Stück (Zeilen darunter). Für Haar-Knoten gibt es keinen Solver-Ersatz — die Knoten sind '
         'Geometry-Nodes, keine Haar-Dynamik (README) —; Kartenhaar nimmt haar_trim, haar_clump, haar_noise u. a. in Python. Ein Blender-Aufruf außerhalb von Engine2d3dKleiderblender ist im '
         'Bereich 2D3D Kleider ein Fehler (Test BlenderNurUeberEinenArbeiterTest). Der Stoffsolver ist Blenders Nachbau und gegen Blender gemessen (Gruppe „Stoffsolver gegen Blender 5.2.2“): '
         'Wer Blender zur Gegenprobe braucht, nimmt blender_roundtrip.py.'),
        ('Drapieren über Blender Cloth (Rezept motor=\'blender\')',
         'Ein Kleidungsstück durch Blenders echte Cloth-Simulation gegen die Grundfigur fallen lassen, mit Druck (Ausbeulung) — der Weg, wenn der Stoffsolver nicht geht.',
         'rezept',
         '\n'.join((
             "m.kleid_drapieren('<kennung>', bilder=24, druck=0.0, motor='blender', wert=1.0)",
             "# ohne Rezept, im Arbeitsordner der Runde:",
             "Engine2d3dKleiderblender(<ordner>).drapieren('<kennung>', bilder=24, druck=0.0, steifigkeit=15.0, fest_oben=0.08)")),
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'), (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug'),
          (D + 'engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender'), (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'NUR NACH ANSAGE VON EDGAR. Nur in einer Runde des Auftrags (Begutachtungswerkzeug.drapierer hängt Engine2d3dKleiderblender als Drapierer „blender“ ein), sonst ValueError. Ergebnis: '
         'Morph <kennung>.eigen.drapiert_<Kürzel des Auftrags>, linear 0…1. Je Stück ein Blender-Prozess: BLENDER_EXE -b --factory-startup --python effekte/blender/engine2d3dkleider/drapieren.py '
         '-- --auftrag <auftrag.json>, TMP und TEMP im Arbeitsordner, Zeitgrenze 900 s. BLENDER_EXE ist die portable Blender 5.2.2 LTS unter A:\\3DTools\\tools\\blender-5.2.2-windows-x64\\ '
         '(Rückfall: die installierte 5.0). Das Skript baut die Netze per from_pydata (kein Importer: die Punktreihenfolge bleibt), der Körper ist Kollisionsobjekt (Dicke 0,004 m), das Stück '
         'Cloth mit quality 6, mass 0,3, Zug und Druck = steifigkeit, shear 5, bending 0,5, air 1,0, Selbstkollision (0,003 m); druck ≠ 0 schaltet Pressure an. Seit 02.10.2026 fällt der Stoff '
         'entlang −Y und das obere Band (fest_oben 0,08) bleibt fest; vorher setzte das Skript keine Schwerkraft und Blender fiel nach −Z, quer zur Figur (533 mm in 11 Bildern gemessen): '
         'ältere Morphe eigen.drapiert aus Blender-Läufen sind mit der falschen Schwerkraft gerechnet. Zeit (Stoffsolver/README.md, werkzeug/blender_zeiten.py, 02.10.2026, ganzer Prozess, '
         'Median von 2–3 abwechselnden Läufen, mit 30 % Fremdlast): Hose 3.123 Punkte, 24 Bilder 19,5 s (Skript 18,3 s); Oberteil 17.552 Punkte, 24 Bilder 55,0 s (Skript 53,8 s); der '
         'Blender-Start allein 4–9 s (Klassenkommentar Engine2d3dKleiderblender, 30.09.2026). Der Stoffsolver braucht für dasselbe 2,1 s und 2,3 s.'),
        ('Haar-Knoten über Blender (Rezept haar_knoten)',
         'Eine von Blenders Hair-Node-Gruppen auf das Stranghaar einer Frisur anwenden: Trim, Clump, Curl, Frizz, Noise, Straighten, Roll, Smooth, Braid, Displace, Rotate, Shrinkwrap, Attach, Duplicate, Interpolate, Generate.',
         'rezept',
         '\n'.join((
             "m.haar_knoten('<sorte>', '<name>', 'trim', ort=None, wert=1.0, length_factor=0.5)",
             "m.haar_knoten('<sorte>', '<name>', 'duplicate', amount=2)",
             "# ort: Wörterbuch wie {'sektor': (30, 150)} oder None; weitere Argumente = Eingänge der Gruppe (length_factor → Length Factor)",
             "# ohne Rezept: Engine2d3dKleiderblender(<ordner>).haar('<sorte>', '<name>', 'trim', ort, **parameter)")),
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'), (D + 'engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender'),
          (D + 'haarknotenauftrag.py', 'Haarknotenauftrag'), (G + 'kleidmorphe.py', 'G9kleidmorphe'), (G + 'haarzusatz.py', 'G9haarzusatz'), (G + 'kopfhaut.py', 'G9kopfhaut'),
          ('HumanBodyWeb/core/pipeline_process.py', 'PipelineProzess'), ('HumanBodyWeb/core/atomic_write.py', 'AtomarSchreiber')],
         'NUR NACH ANSAGE VON EDGAR. Nur Stranghaar (Pixie, Hime Cut, Viola); Kartenhaar wirft ValueError — dort haar_trim, haar_clump, haar_noise u. a. nehmen. knoten ist eines von 16 Wörtern '
         '(Engine2d3dKleiderblender.KNOTEN); Blenders Asset-Datei procedural_hair_node_assets.blend hat 26 Gruppen, erreichbar sind nur diese 16. Verformende Knoten (trim, clump, curl, frizz, '
         'noise, straighten, roll, smooth, braid, displace, rotate, shrinkwrap, attach) liefern ein Delta je Punkt als Morph <sorte>.eigen.<name>, erzeugende (duplicate, interpolate, generate) '
         'Zusatzsträhnen <sorte>.str.<name> (ein Ergebnis mit weniger als 1 % der Strähnen oder im Mittel unter 2 Punkten je Strähne wird mit ValueError abgewiesen; haar_duplizieren und '
         'haar_interpolieren in Python gehen immer). Fallen (gemessen 01.10.2026): Trim hat „Replace Length“ an und setzt jede Strähne auf Length 1 m (500 mm Weg am Pixie) — ohne Angabe wird es aus und Length Factor '
         '0,5 gesetzt; Duplicate mit Blenders Amount 10 gäbe 2,6 Mio. Punkte, die Vorgabe ist 2; Mask als Punktattribut wirkt je Strähne, das Ortsgewicht wird deshalb in Python je Punkt '
         'angelegt; Attach, Interpolate und Generate brauchen eine Kopfhaut mit EINDEUTIGER UV (G9kopfhaut: Daz-Haarkappe oder Kopf der Grundfigur mit Genesis-UV), Density zählt je m² '
         '(ohne Angabe 0,5 × Strähnen / Fläche). Die Gruppen werden über eine Hüll-Nodegruppe gesetzt, weil Modifier-Eingänge in Blender 5.2 nicht mehr per mod[…] setzbar sind (CLAUDE.md). '
         'Zeit (ortsmorphe.md, 01.10.2026, Pixie 236.136 Punkte, 21.755 Strähnen): Trim und die anderen Knoten 2,4 s Rechnung, 6 s mit Blender-Start (workflowzeiten.py BLENDER_HAAR); '
         'Shrinkwrap 2,8 s, gesamt 6,5 s; Duplicate (2 Kopien) 3,5 s, gesamt 8,8 s; Attach, Interpolate und Generate je 5–6 s mit Start (Pixie und Hime Cut). Kein Solver-Ersatz: die Knoten '
         'sind Geometry-Nodes, keine Haar-Dynamik (README). Die Automatik schreibt sie nie.'),
        ('Roundtrip: dasselbe Stück in Blender und im Solver (blender_roundtrip.py)',
         'Das echte Oberteil oder die echte Hose auf dem echten Körper durch drapieren.py (unverändert) und durch den Stoffsolver: Ergebnis und Zeit nebeneinander.',
         'cli',
         '\n'.join((
             'cd A:\\3DTools',
             R + 'blender_roundtrip.py [hose|oberteil] [bilder=12] [druck=0] [--ohne-blender] [--host]')),
         [(S + 'stoffsimulation.py', 'Stoffsimulation'), (S + 'stoffnetz.py', 'StoffNetz'), (S + 'stoffmaterial.py', 'StoffMaterial'), (S + 'kollider.py', 'Kollider')],
         'NUR NACH ANSAGE VON EDGAR (startet Blender). Messwerkzeug, kein Pipeline-Schritt: Eingaben aus werkzeug/_vergleich/eingaben/z_oben/ (Job test3, Runde 21; Meter, Z oben, Füße bei 0), '
         'Einstellungen wie drapieren.py, nichts angeheftet, schwerkraft [0, 0, −9,81] (die Eingaben liegen Z oben). Blender simuliert Bild 2…bilder, der Solver bilder − 1 Bilder; Zeiten '
         'getrennt in Prozess gesamt, Skript und Blender-Start (leeres Skript blender_leer.py); --host nimmt den NumPy-Weg dazu. Die Ergebnisse liegen unter _vergleich/roundtrip/. '
         'Gemessen (README, 02.10.2026): Hose 12 Bilder Blender 10,1 s (Skript 8,9 s), Solver 1,9 s; Host 462 s. Die Hose rutscht unangeheftet und ist chaotisch: ein Einzellauf sagt nichts '
         '(Gruppe „Stoffsolver gegen Blender 5.2.2“, Ensemble).'),
        ('Zeitmessung Blender gegen Stoffsolver (blender_zeiten.py)',
         'Beide als eigener Prozess über DENSELBEN Auftrag, abwechselnd, Wanduhr dieses Rechners: Prozess gesamt, Skript ohne Start, Import und Abstand der Ergebnisse.',
         'cli',
         '\n'.join((
             'cd A:\\3DTools',
             R + 'blender_zeiten.py [hose|oberteil ...] [bilder=12] [wiederholungen=3] [druck=0]')),
         [(S + 'drapierauftrag.py', 'Drapierauftrag')],
         'NUR NACH ANSAGE VON EDGAR (startet Blender, mehrfach). Ausgabe je Stück: min und Median je Zeit und der Abstand beider Lagen. Abwechselnd gemessen, damit der Dateicache keinen '
         'bevorzugt (Regel zeit-messen). Der Solver-Prozess enthält Python-Start und Importe (0,5 s) und Warps Start. Gemessen (README, 02.10.2026, Median von 2–3 Läufen, mit 30 % Fremdlast, '
         'vor dem Ausbau): Oberteil 12 Bilder Blender 26,7 s, Solver 2,0 s; 24 Bilder 55,0 s gegen 2,3 s; Hose 12 Bilder 10,1 s gegen 1,9 s; 24 Bilder 19,5 s gegen 2,1 s; reine Simulation '
         'Oberteil 12 Bilder 0,35 s gegen 25,5 s. Nach dem Ausbau neu zu messen, wenn keine Agenten laufen.'),
        ('BlenderModel: Grundfigur → Kostüm-Kreislauf in Blender → Film (Dashboard → BlenderModel)',
         'Der ältere Blender-Weg: Genesis-Grundfigur, ein Kostüm aus Ringen und Rohren in Blender (Maße, Farben, Haltung), Runde um Runde gegen die Vorlagenbilder benotet, am Ende ein Blender-Film.',
         'seite',
         '\n'.join((
             'Dashboard → BlenderModel (/blendermodell/, /blendermodell/<kennung>/); API /api/blendermodell/…',
             'Schritte: grundfigur · kostuem · export · blender · speichern; Blendermodelllauf.ausfuehren(ab, bis)')),
         [(D + 'blendermodelllauf.py', 'Blendermodelllauf'), (D + 'kostuemkreislauf.py', 'Kostuemkreislauf'), (D + 'kostuemrunde.py', 'Kostuemrunde'),
          (D + 'kostuemoptimierer.py', 'Kostuemoptimierer'), (D + 'kostuemblender.py', 'Kostuemblender'), (D + 'kostuemarbeiter.py', 'Kostuemarbeiter'),
          (D + 'blendermodellblender.py', 'Blendermodellblender')],
         'NUR NACH ANSAGE VON EDGAR (jede Runde ein Blender-Prozess). Das Kostüm ist DATEN (Kostuemparameter), gebaut von effekte/blender/kostuem/, nicht die Genesis-Garderobe der 2D3D '
         'Kleider; der Kreislauf ist ein (1+λ)-ES (Kostuemoptimierer) mit optionaler Prüf-KI, „Weiter iterieren“ rechnet nur den Schritt kostuem. Das Netz aus Fotos ist ausgebaut '
         '(„trellis soll nicht laufen“, 29.09.2026). Zeit (blendermodell.md, 30.09.2026): Blender starten und die Grundfigur laden kostet je Aufruf 4–9 s, ein Kandidat danach 0,6–0,8 s; mit '
         'dauerhaften Arbeitern (Kostuemarbeiter, Postfach-Ordner, Vorgabe 4 Prozesse) eine Runde 4,5–6 s statt 23 s; der Blender-Film dauert Minuten. Fallen: Wer effekte/blender/kostuem* '
         'ändert, während ein Lauf rechnet, bricht ihn ab (ein neu gestarteter Arbeiter liest den Code von der Platte); ruff format schreibt Python-3.14-Syntax (except A, B:) und bricht damit Blenders Python (Blender 5.0: 3.11) — nie ruff format auf effekte/blender/ ohne Gegenprobe. '
         'Offen laut Regel: der Stoff bewegt sich nur mit den Knochen, keine Stoffsimulation; Tests nicht gelaufen (29./30.09.2026).'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellFormMixin', 'ruft', 'Rezeptumgebung', 'drapierung(motor): der Drapierer des Motors, ValueError außerhalb einer Runde'),
        ('ModellFormMixin', 'ruft', 'Engine2d3dKleiderblender', 'drapieren(kennung, bilder, druck, name=) bei motor=blender'),
        ('ModellHaarMixin', 'ruft', 'Rezeptumgebung', 'blender(): der Blender-Arbeiter der Runde, ValueError außerhalb einer Runde'),
        ('ModellHaarMixin', 'ruft', 'Engine2d3dKleiderblender', 'haar(sorte, name, knoten, ort, **parameter)'),
        ('Begutachtungswerkzeug', 'ruft', 'Engine2d3dKleiderblender', 'Begutachtungswerkzeug.drapierer() baut Engine2d3dKleiderblender(ablage.arbeit(\'blender\')) als Drapierer „blender“'),
        ('Engine2d3dKleiderblender', 'ruft', 'G9kleidmorphe', 'kaefige(kennung), koerper(), ablegen(kennung, name, folger, deltas, brief)'),
        ('Engine2d3dKleiderblender', 'ruft', 'G9haarzusatz', 'ketten(segmente, anzahl), ablegen(…) für erzeugende Knoten'),
        ('Engine2d3dKleiderblender', 'ruft', 'Haarknotenauftrag', 'schreiben(nummer, punkte, ketten, maske) hin; delta(…) und zusatz(…) zurück'),
        ('Engine2d3dKleiderblender', 'ruft', 'PipelineProzess', 'starten([BLENDER_EXE, -b, --factory-startup, --python, skript, --, --auftrag, …]); proc.wait(timeout=900)'),
        ('Engine2d3dKleiderblender', 'ruft', 'AtomarSchreiber', 'json_schreiben(auftrag.json)'),
        ('Haarknotenauftrag', 'ruft', 'G9kopfhaut', 'aus_teilen(teile, kaefige, y0): die Kopfhaut mit echter UV für Attach, Interpolate, Generate'),
        ('Haarknotenauftrag', 'ruft', 'G9kleidmorphe', 'koerper(): die Grundfigur als Zielobjekt für Shrinkwrap und Duplicate'),
        ('Haarknotenauftrag', 'ruft', 'G9haarzusatz', 'aus_blender(folger, punkte, nachher, laengen): neue Strähnen als Rezept aus den alten Punkten'),
        ('Blendermodelllauf', 'ruft', 'Kostuemkreislauf', 'Kostuemkreislauf(lauf).ausfuehren(): der Schritt kostuem'),
        ('Blendermodelllauf', 'ruft', 'Blendermodellblender', 'Blendermodellblender(lauf).ausfuehren(): der Film in Blender'),
        ('Kostuemkreislauf', 'ruft', 'Kostuemrunde', 'Kostuemrunde(…): eine Runde mit Kandidaten und Note'),
        ('Kostuemkreislauf', 'ruft', 'Kostuemoptimierer', 'Kostuemoptimierer(kennung, schritt): die Kandidaten der Runde'),
        ('Kostuemrunde', 'ruft', 'Kostuemblender', 'Kostuemblender(lauf, parallel=, dauerhaft=True): die Renders der Kandidaten'),
        ('Kostuemblender', 'ruft', 'Kostuemarbeiter', 'ein Blender-Prozess im Dienst: senden(auftrag), antwort(nummer)'),
    ]
