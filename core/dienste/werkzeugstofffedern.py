# -*- coding: utf-8 -*-
"""Werkzeugstofffedern — Gruppe „Stoffsolver: Material, Federn, Anheften, Druck, Kollision“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: `Stoffsolver/README.md`, `Stoffsolver/LUECKEN.md`, die Docstrings der Klassen und die Tabelle `Stoffsolverumfangkleid`.
Der Stand je Zeile („blender“ = gegen Blender 5.2.2 gemessen) und die Maße (Punktabstand Solver ↔ Blender im letzten Bild, mm) stehen dort mit Szene und Gegenprobe."""

__all__ = ['Werkzeugstofffedern']

S = 'Stoffsolver/'


class Werkzeugstofffedern:
    KENNUNG = 'stofffedern'
    TITEL = 'Stoffsolver: Material, Federn, Anheften, Druck, Kollision'
    EINLEITUNG = (
        'Diese Zeilen sind Auftragsschlüssel der auftrag.json (Zeile „Stoffsolver als Prozess“ in der Gruppe „Stoffsolver: Einstiege, Aufträge und Gerät“) oder Argumente von '
        'Drapierauftrag.rechnen und Stoffsimulation; ohne sie rechnet der Auftrag wie vorher, bitgleich. Reihenfolge der Entscheidungen: 1. Material oder Preset, 2. Federn, '
        'Gruppen, Nähte, Anheften, 3. Innendruck, 4. Kollision. Der Stand je Zeile steht in der Tabelle „Der Stoffsolver gegen Blender“ (Reiter Workflow): blender = gegen Blender '
        '5.2.2 gemessen; Maß = Punktabstand Solver ↔ Blender im letzten Bild in mm (Stoffsolver/README.md, Abschnitt „Messungen“). Aus der Pipeline erreichbar ist davon nichts außer '
        'bilder, druck und dem harten Anheften des oberen Bandes.')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Material, Presets, time_scale, Teilschritte je Bild',
         'Den Stoff wählen: Blenders Cloth ohne Preset oder eines der fünf Presets, einzelne Werte überschreiben, Zeitskala und Qualität setzen.',
         'python',
         '\n'.join((
             "from Stoffsolver import StoffMaterial",
             "material = StoffMaterial.jeans().mit(biegung=2.0, zeitskala=1.0)    # vorgabe() baumwolle() seide() jeans() leder() gummi()",
             '# im Auftrag: "material": "jeans", "qualitaet": 12, "material_felder": {"biegung": 2.0}')),
         [(S + 'stoffmaterial.py', 'StoffMaterial'), (S + 'schrittzahl.py', 'Schrittzahl')],
         'Presets (scripts/presets/cloth/*.py von Blender): baumwolle = Cotton (Quality 5), seide = Silk (5), jeans = Denim (12), leder = Leather (15), gummi = Rubber (7); vorgabe ist '
         'Blenders Cloth ohne Preset (Quality 5; der Drapierauftrag nimmt ohne Angabe 6 wie drapieren.py). Die 36 Felder (StoffMaterial.FELDER) heißen wie im Blender-Panel: schritte '
         '(quality), masse (je PUNKT, 0,3), zug, druck, scherung, biegung, daempfung_zug, daempfung_druck, daempfung_scherung, daempfung_biegung, luft, druckkraft, druckfaktor, abstand, '
         'reibung, selbstabstand, selbstreibung, zeitskala (time_scale), zug_max, druck_max, scherung_max, biegung_max, schrumpfen_min, schrumpfen_max, innenfedern, innen_*, '
         'nahtkraft_max, biegemodell. Die Zeit läuft in Bildern: dt = zeitskala / schritte; die Teilschritte je Bild zählt Blender in einer float32-Schleife (Schrittzahl): Quality 12 '
         'rechnet 13, Quality 19 rechnet 20. Gemessen: Denim vorher 106 mm daneben, mit Blenders Zählung 0,00 mm (LUECKEN.md A1); Presets höchstens 0,0027 mm; time_scale 0,5, 2 und 0,7 '
         'und mit Quality 10 und 20: 0,0001–0,0003 mm, time_scale 0 rechnet nichts (Stoffsolverumfang). Stand: blender.'),
        ('Federn und Biegung (Struktur, Scherung, Winkel, linear, Vielecke, kubischer Zweig)',
         'Wie das Netz Zug, Druck, Scherung und Biegung leistet; Vierecke und Vielecke als echte Flächen übergeben, das Biegemodell wählen.',
         'python',
         '\n'.join((
             "StoffNetz(punkte, dreiecke, vierecke=<(V, 4)>, vielecke=[<Eckenfolge mit mindestens 4 Ecken>, …])",
             "material_felder={'zug': 15, 'druck': 15, 'scherung': 5, 'biegung': 0.5, 'biegemodell': 'winkel'}    # oder 'linear'",
             '# im Auftrag: stueck.npz mit vierecke (V, 4) bzw. vielecke_ecken + vielecke_anfang; "material_felder": {"biegemodell": "linear"}')),
         [(S + 'stoffnetz.py', 'StoffNetz'), (S + 'federn.py', 'Federn'), (S + 'federkraefte.py', 'Federkraefte'), (S + 'winkelbiegung.py', 'Winkelbiegung'),
          (S + 'polygonflaechen.py', 'Polygonflaechen'), (S + 'polygonbiegung.py', 'Polygonbiegung'), (S + 'linearbiegung.py', 'Linearbiegung'), (S + 'choiko.py', 'Choiko'),
          (S + 'kubischfedern.py', 'Kubischfedern')],
         'Struktur = Kanten der Flächen; Scherfedern nur bei Flächen mit mehr als 3 Ecken (ein reines Dreiecksnetz hat keine); Biegung im Winkelmodell (Blenders Vorgabe, k = Biegung · '
         'Ruhelänge · 0,1), an Vielecken über die Polygonmittelpunkte; im linearen Modell wirken die Biegefedern nur im Druck, Struktur- und Innenfedern gar nicht im Druck, und ein '
         'Dreiecksnetz ohne Scherfedern hat dort keine Biegung. Zug/Druck-Grenze bei >=. Ohne vierecke zählt die Aufteilungs-Diagonale eines Vierecks als Strukturfeder: 5,8 mm daneben '
         '(gemessen). Der kubische Zweig von Choi-Kos fbstar gilt erst ab Dämpfung · Federlänge ≥ 7,81 (nicht 3,03) und greift nur bei sehr großen Tüchern. Gemessen (README, '
         'Stoffsolverumfang, 02./03.10.2026): etwa 100 Fälle höchstens 0,003 mm, Vierecke 0,01 mm; Biegung an Vierecken 0,002–0,008 mm statt 0,6–4,4 mm mit der Dreiecksnäherung, '
         'Sechsecke bis 0,025 mm (Host), Fünfecke: Szene chaotisch, nicht beurteilbar; linear 0,001–0,042 mm; kubischer Zweig 0,003 mm (ohne ihn 2,8 und 569 mm). Nicht ebene '
         'Vielecke legt Blender unbestimmt an, der Solver rechnet sie flach. Stand: blender.'),
        ('Vertexgruppen, Schrumpfen, Innenfedern, Nähte',
         'Steifigkeit je Punkt malen, das Tuch schrumpfen lassen, Federn quer durch das Stück legen, lose Kanten als Nähte zusammenziehen.',
         'python',
         '\n'.join((
             "Stoffoptionen(gewichte=Federgewichte(anzahl, struktur=<(N,)>, scherung=…, biegung=…, intern=…, schrumpfen=…))",
             "material_felder={'schrumpfen_min': 0.1, 'schrumpfen_max': 0.3, 'innenfedern': True, 'nahtkraft_max': 0.0}",
             "StoffNetz(punkte, dreiecke, naehte=<(K, 2)>)",
             '# im Auftrag: "gruppen": "<gruppen.npz>" (Felder struktur, scherung, biegung, intern, schrumpfen je (N,); naehte (K, 2)),',
             '#   "schrumpfen_verlauf": {"minimum": <Zahl oder Liste je Bild>, "maximum": …, "gewichte": "<npz>"}')),
         [(S + 'federgewichte.py', 'Federgewichte'), (S + 'federsteifigkeit.py', 'Federsteifigkeit'), (S + 'schrumpfen.py', 'Schrumpfen'), (S + 'federverlauf.py', 'Federverlauf'),
          (S + 'innenfedern.py', 'Innenfedern'), (S + 'naehte.py', 'Naehte'), (S + 'federnachfuehrung.py', 'Federnachfuehrung'), (S + 'stoffoptionen.py', 'Stoffoptionen')],
         'Steifigkeit = Wert + Gewicht · |Maximum − Wert| (die Maxima zug_max, druck_max, scherung_max, biegung_max und innen_*_max stehen in StoffMaterial). Schrumpfen auch mit der Zeit '
         '(Blenders Bedingung cloth.cc:300 wörtlich). Innenfedern: höchstens eine Feder je Punkt zum Punkt gegenüber, begrenzt durch innen_laenge, innen_winkel (0…π/4) und '
         'innen_normalentest. Nähte: lose Kanten (in keinem Dreieck) als Zugfedern der Länge 0; zum Rechenzeitpunkt trägt die Naht tension_stiffness, nicht _max (gemessen). Gemessen: '
         'Gruppen höchstens 0,001 mm; Schrumpfen auch mit der Zeit 0,0000 mm in vier Fällen (Host und Gerät); Innenfedern höchstens 0,001 mm in sechs Fällen (Blender gibt die Federliste '
         'nicht heraus, verglichen wurde die Wirkung an 49 bis 98 Punkten). Stand: blender.'),
        ('Ruhegestalt (use_dynamic_mesh)',
         'Federn und Biegung nehmen ihre Ruhewerte aus einer anderen Lage als der Ausgangslage — ein Shape Key oder ein Netz, das sich von Bild zu Bild ändert.',
         'python',
         '\n'.join((
             "Stoffsimulation(netz, material, …, ruhe=<(N, 3) oder (B, N, 3)>)",
             '# im Auftrag: "ruhe": "<npz mit punkte (N, 3) oder lagen (B, N, 3)>"   oder   "ruhe_dynamisch": true (braucht "pins_bewegung")')),
         [(S + 'ruhegestalt.py', 'Ruhegestalt'), (S + 'federnachfuehrung.py', 'Federnachfuehrung')],
         'ruhe (N, 3) ist die Ruhegestalt aus einem Shape Key, (B, N, 3) ein dynamisches Netz (Eintrag nr − 1 im nr-ten Bild). ruhe_dynamisch=true nimmt die Lagen von pins_bewegung zugleich '
         'als dynamische Ruhegestalt (Blender: Basisnetz des Bildes = xconst = xrest); ohne pins_bewegung ist es ein Fehler. Gemessen: dynamisches Netz 0,0009 mm, Sprung in Bild 2 0,0008 mm. '
         'rest_shape_key wirkt in Blender 5.2.2 nicht (mesh_data_update.cc:354-371): dort nicht vergleichbar. Stand: blender.'),
        ('Anheften: hart, weich (pin_stiffness), bewegt',
         'Punkte festhalten, weich an ein Ziel ziehen oder mit dem Körper mitbewegen (Bund, Schultern, Kopfhaut).',
         'python',
         '\n'.join((
             "anheften=[<Punktnummern>]                                                                # hart, Blenders Pin-Gruppe",
             "Stoffoptionen(pin_gewicht=<(N,) 0…1>, pin_steifigkeit=1.0, pin_reibung=0.0, pin_standard=0.0)    # weich",
             "sim.pins_bewegen(punkte_neu)    # bewegt: die Lagen ALLER Punkte im nächsten Bild, einmal je Bild vor sim.bild()",
             '# im Auftrag: "anheften": […], "gruppen": "<npz mit pin (N,) und pin_mitglied>", "pin": {"steifigkeit": 1.0, "reibung": 0.0, "standard": 0.0},',
             '#   "pins_bewegung": "<npz mit lagen (B, N, 3)>"')),
         [(S + 'zielfedern.py', 'Zielfedern'), (S + 'pinbewegung.py', 'Pinbewegung'), (S + 'stoffoptionen.py', 'Stoffoptionen'), (S + 'stoffsimulation.py', 'Stoffsimulation')],
         'Gewicht⁴, ab 0,999 fest angeheftet; goal_friction; bewegte feste und weiche Pins; time_scale; Quality 12 und 19; auf dem Gerät im CUDA-Graph (WarpPinbewegung). pins_bewegung (B, N, 3): '
         'Eintrag nr − 1 im nr-ten Bild, zu kurz: die letzte; ohne Pins ist der Schlüssel ein Fehler. Die Pipeline (Stoffsolverdrapierung) heftet nur das obere Band hart an '
         '(fest_oben 0,08). Gemessen: 0,0000–0,002 mm. Stand: blender.'),
        ('Innendruck, Volumenterm, Hydrostatik, Druckgruppe',
         'Das Stück aufblasen (Ausbeulung), auf ein Zielvolumen regeln, in eine Flüssigkeit tauchen, den Druck nur auf Teile wirken lassen.',
         'python',
         '\n'.join((
             "Drapierauftrag.rechnen(…, druck=<Kraft>, material_felder={'druckfaktor': 1.0, 'zielvolumen': <m³>})",
             "Stoffoptionen(fluiddichte=<kg/m³>, druck_gewicht=<(N,)>, druck_nur_mit_schalter=False)",
             '# im Auftrag: "druck": <Kraft>, "fluiddichte": <kg/m³>, "gruppen": "<npz mit druck (N,)>"')),
         [(S + 'aussenkraefte.py', 'Aussenkraefte'), (S + 'flaechenkraefte.py', 'Flaechenkraefte'), (S + 'hydrostatik.py', 'Hydrostatik'), (S + 'druckgruppe.py', 'Druckgruppe')],
         'Innendruck wie Blenders Pressure: (min(V0/V − 1, |P| + 200) + P) · Faktor, der Volumenterm nur bei einem Ausgangsvolumen über 1e-6 m³ (geschlossenes Stück); Schwerkraft × 0,001, '
         'Luft × 0,01. druck ≠ 0 schaltet den Druck an (sonst nur mit druck_an oder druck_nur_mit_schalter). Newton (Vorgabe der Pipeline) kann keinen Druck, nur Blender und Stoffsolver. '
         'Gemessen: Zielvolumen, Faktor, Deckel 200 und Druckgruppe höchstens 0,0004 mm; Hydrostatik +10, −30 und mit Gruppe höchstens 0,002 mm; −100 liegt in der Streuung der Szene '
         '(Solver gegen sich selbst bei 1e-7 m Störung 0,68 mm). Stand: blender.'),
        ('Kollision: Körper und Selbst, Qualität, Klammern, Gruppenmasken',
         'Wie der Stoff mit dem Körper und mit sich selbst kollidiert: Abstände, Runden je Schritt, Impuls-Klammern, Dreiecke von der Kollision ausnehmen.',
         'python',
         '\n'.join((
             "Drapierauftrag.rechnen(…, selbstkontakt=True, abstand=0.004, dicke=0.004, selbstabstand=0.003)",
             "Stoffoptionen(kollision_qualitaet=2, impulse_clamp=None, self_impulse_clamp=0.0, ohne_koerperkontakt=<Maske (N,)>, ohne_selbstkontakt=<Maske (N,)>)",
             "Kollisionseinstellungen.maske(<Gewichte>)    # Gewicht > 0 = in der Gruppe",
             '# im Auftrag: "selbstkontakt": true, "abstand": 0.004, "dicke": 0.004, "selbstabstand": 0.003, "kollision_qualitaet": 2, "impulse_clamp": 0, "self_impulse_clamp": 0,',
             '#   "gruppen": "<npz mit ohne_koerperkontakt, ohne_selbstkontakt>"')),
         [(S + 'kollisionsablauf.py', 'Kollisionsablauf'), (S + 'kollisionseinstellungen.py', 'Kollisionseinstellungen'), (S + 'kollisionskoerper.py', 'Kollisionskoerper'),
          (S + 'koerperantwort.py', 'Koerperantwort'), (S + 'geraeteruhe.py', 'Geraeteruhe')],
         'Dreieck gegen Dreieck wie cloth_bvh_collision (collision.cc): Mindestabstand (Abstand + Dicke) · 8/9 zum Körper und 2 · Selbstabstand · 8/9 zwischen Stoffteilen, '
         'Impulskonstanten, Culling, Reibung; die Paarlisten werden einmal je Schritt gebaut. collision_quality = Runden je Schritt (Vorgabe 2). Der GPU-Motor rechnet Ruhelängen und '
         '-winkel wie Blender in float32 (Geraeteruhe). Gemessen: gleich bis auf impulse_clamp 0,04 und self_impulse_clamp 0,02 (dort ist Blender selbst chaotisch); Selbstkollision am Oberteil '
         '0,13 mm (Blender gegen Blender 0,13 mm), davor +0,5 bis +2,7 mm Bias. Die unangeheftete Hose rutscht und ist chaotisch: Lauf gegen Lauf nicht vergleichbar (200 Blender- gegen '
         '500 Solver-Läufe: Streuung 44,3 gegen 45,2 mm, README A5, 03.10.2026). Stand: blender.'),
        ('Mehrere und bewegte Kollisionskörper',
         'Mehr als einen Körper kollidieren lassen und Körper je Bild bewegen (Hub, Schritt, Drehung).',
         'python',
         '\n'.join((
             "Kollisionskoerper(punkte, dreiecke, dicke=0.02, reibung=5.0, culling=True, use_normal=False, klammer=0.0, bewegbar=True)",
             "Stoffoptionen(koerper_weitere=[<Kollisionskoerper>, …], bewegbar=True)    # bewegbar: der Hauptkörper wird bewegt",
             "sim.koerper_bewegen(punkte_neu, nr=0)    # einmal je Bild vor sim.bild(); nr 0 = Hauptkörper",
             '# im Auftrag: "koerper_weitere": [{"datei": "<npz>", "dicke": 0.02, "reibung": 5.0, "culling": true, "use_normal": false, "klammer": 0}],',
             '#   "bewegung": "<npz mit lagen (B, M, 3)>"')),
         [(S + 'kollisionskoerper.py', 'Kollisionskoerper'), (S + 'koerperantwort.py', 'Koerperantwort'), (S + 'warpkoerpersatz.py', 'WarpKoerpersatz'),
          (S + 'stoffoptionen.py', 'Stoffoptionen')],
         'Blender kollidiert mit allen Objekten mit Collision-Modifier, jedes mit eigener Dicke, Reibung und Culling; die Impulse mehrerer Körper wirken je Achse mit dem größten Betrag zusammen '
         '(Impulssammler), nicht addiert. Dicke: Kollisionskoerper 0,02 wie Blender (Kugel 29 → 1,5 mm); der Drapierauftrag nennt 0,004 selbst. Die Körperdreiecke müssen nach außen zeigen: '
         'aussen_pruefen dreht um, wenn das Volumen negativ ist (Blender dreht nichts um; ein Lauf mit der Innenseite nach außen ließ das Tuch hindurchfallen). Weitere Körper nur mit '
         'kollision=\'blender\'. Gemessen: zwei und drei Körper 0,4–0,8 mm im Rauschen von Blender (0,3–4,5 mm); bewegter Körper (Hub, seitlich, schräg, abrupter Halt, Quality 12) 0,007–0,5 mm, '
         'im CUDA-Graph; der Host (float64) weicht bei koplanarem Aufprall ab, das Gerät liegt näher an Blender. Stand: blender.'),
        ('Näherung „nächster Hautpunkt“ (kollision=\'schnell\') und CG „schnell“',
         'Der Nebenzweig: schneller und ungenauer, nicht Blenders Verfahren.',
         'python',
         '\n'.join((
             "Drapierauftrag.rechnen(…, kollision='schnell', cg='schnell')",
             '# im Auftrag: "kollision": "schnell", "cg": "schnell"')),
         [(S + 'kollider.py', 'Kollider'), (S + 'selbstkollision.py', 'Selbstkollision'), (S + 'distanzfeld.py', 'Distanzfeld')],
         'Je Stoffpunkt der nächste Hautpunkt (KD-Baum, Impulse auf die Geschwindigkeit) und Selbstkollision Punkt gegen Punkt; Kante gegen Kante und Fläche des Stoffs gegen Punkt des Körpers '
         'fehlen. cg=\'schnell\' (Block-Jacobi, Warmstart) liefert ein anderes Ergebnis als Blenders CG. Beides läuft auf dem Host (kein CUDA-Motor). Wer Blenders Ergebnis will, lässt die '
         'Vorgaben stehen. Stand: Nebenzweig (README), nicht gegen Blender gemessen.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Stoffsimulation', 'ruft', 'Federn', 'Federn.aus_netz(ruhenetz, vierecke, material, gewichte)'),
        ('Stoffsimulation', 'ruft', 'Federkraefte', 'Federkraefte(federn, anzahl, material, None, gewichte)'),
        ('Stoffsimulation', 'ruft', 'Winkelbiegung', 'Winkelbiegung.aus_netz(ruhenetz, material, federn, gewichte)'),
        ('Stoffsimulation', 'ruft', 'Ruhegestalt', 'von(ruhe, anzahl), netz(), volumen(): die Ruhegestalt aus ruhe'),
        ('Stoffsimulation', 'ruft', 'Federnachfuehrung', 'bauen(sim, ruhe, verlauf): Federn und Gewichte von Bild zu Bild nachführen'),
        ('Stoffsimulation', 'ruft', 'Kollisionsablauf', 'Kollisionsablauf(dreiecke, koerper, …): Dreieck gegen Dreieck, antwort() je Schritt'),
        ('Stoffsimulation', 'ruft', 'Kollisionskoerper', 'Kollisionskoerper(punkte, dreiecke, dicke=, reibung=, bewegbar=) aus dem Kollider'),
        ('Stoffsimulation', 'ruft', 'Pinbewegung', 'Pinbewegung(index, lagen, zeitskala, unterschritte).bewegen(lagen_neu): bewegte Pins'),
        ('Stoffsimulation', 'ruft', 'Kollider', 'antwort(…) bei kollision=schnell'),
        ('Federn', 'ruft', 'Innenfedern', 'bauen(punkte, dreiecke, max_laenge, max_winkel, normalentest): die internen Federn'),
        ('Federn', 'ruft', 'Linearbiegung', 'paare(diagonalen, anzahl): die Biegefedern des linearen Modells'),
        ('Federn', 'ruft', 'Schrumpfen', 'aus_material(material, gewichte): der Federfaktor je Feder'),
        ('Federkraefte', 'ruft', 'Federsteifigkeit', 'berechnen(federn, material, gewichte): Steifigkeit je Feder'),
        ('Federkraefte', 'ruft', 'Kubischfedern', 'koeffizient(), index(): welche Federn den kubischen Zweig nehmen können'),
        ('Federkraefte', 'ruft', 'Choiko', 'druckzweig(…): der Zweig von fbstar im Druck'),
        ('Federnachfuehrung', 'ruft', 'Federverlauf', 'Federverlauf(**verlauf): Schrumpfen und Gewichte je Bild'),
        ('Federnachfuehrung', 'ruft', 'Schrumpfen', 'Schrumpffaktor je Feder: Ruhelängen und Ruhewinkel zu Beginn jedes Bildes neu'),
        ('Stoffoptionen', 'ruft', 'Zielfedern', 'Zielfedern(gewicht, ziel, mittlere_laenge, goalspring, goalfrict, mitglied, defgoal, gesperrt): weiches Anheften'),
        ('Stoffoptionen', 'ruft', 'Aussenkraefte', 'Aussenkraefte(netz, material, schwerkraft, ziele=, wind=, druckgruppe=, fluiddichte=, …)'),
        ('Stoffoptionen', 'ruft', 'Druckgruppe', 'Druckgruppe(druck_gewicht, dreiecke)'),
        ('Stoffoptionen', 'ruft', 'Kollisionseinstellungen', 'Kollisionseinstellungen(qualitaet, klammer, selbst_klammer, ohne_koerperkontakt, ohne_selbstkontakt)'),
        ('Aussenkraefte', 'ruft', 'Hydrostatik', 'Hydrostatik: das Druckgefälle einer Flüssigkeit (fluid_density)'),
        ('Aussenkraefte', 'ruft', 'Flaechenkraefte', 'Flaechenkraefte: Druck, Wind und Feldkraft je Dreieck auf die drei Ecken'),
        ('Kollisionsablauf', 'ruft', 'Koerperantwort', 'durchgang(koerper, kontakte, mindest, einstellungen, tv, zeitfaktor, h): ein Durchgang für alle Körper'),
        ('Kollisionsablauf', 'ruft', 'Kollisionseinstellungen', 'Qualität, Klammern und Gruppenmasken lesen'),
    ]
