# -*- coding: utf-8 -*-
"""Werkzeugstoffvergleich — Gruppe „Stoffsolver gegen Blender 5.2.2: Vergleichswerkzeuge und Messstand“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026).

Gelesen am 03.10.2026, nichts gestartet. Quellen: die Docstrings der Skripte unter `Stoffsolver/werkzeug/` und `Stoffsolver/README.md` (Abschnitt „Messungen“, Tabelle der Werkzeuge) —
jede Zahl der Hinweise steht dort mit Datum. Alle Skripte starten Blender 5.2.2 als Prozess; sie laufen nur nach Ansage von Edgar."""

__all__ = ['Werkzeugstoffvergleich']

W = 'Stoffsolver/werkzeug/'
R = 'python14\\Scripts\\python.exe Stoffsolver\\werkzeug\\'


class Werkzeugstoffvergleich:
    KENNUNG = 'stoffvergleich'
    TITEL = 'Stoffsolver gegen Blender 5.2.2: Vergleichswerkzeuge und Messstand'
    EINLEITUNG = (
        'Jede Funktion des Stoffsolvers ist gegen echtes Blender 5.2.2 (Hintergrundmodus) gemessen, wo Blender sie dort ausführt; je Funktion ein Werkzeug vergleich_*.py. Die Methode '
        '(README, „Messungen“): 1. Rauschgrenze = Blender gegen Blender mit 1e-7 m bis 1 µm Störung der Ausgangslage (ungestört ist Blender bitgleich zu sich selbst), 2. Wirkung = Blender mit '
        'gegen ohne die Funktion, 3. Vergleich = Solver gegen Blender, 4. Gegenprobe = Solver ohne die Funktion gegen Blender mit ihr (muss so weit daneben liegen wie die Wirkung). Maß = '
        'Punktabstand Solver ↔ Blender im letzten Bild in mm (Mittel / größter), bei UV die Form in Inseldiagonalen. Alle Werkzeuge starten Blender als Prozess (immer nur einer zugleich, '
        'im Vordergrund, mit Zeitgrenze) — nur nach Ansage von Edgar; eine laufende Messreihe belegt die Maschine, dann nicht parallel starten. Aufruf immer aus A:\\3DTools; Ergebnisse '
        'unter Stoffsolver/werkzeug/_vergleich/<thema>/ (nicht in git). Die Zeiten der README sind vor dem Ausbau mit 30 % Fremdlast gemessen und nach dem Ausbau neu zu messen.')
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Kern: Kleidstück auf Körper, Kleinproben, Auftragsweg, Ensemble (vergleich_kern.py)',
         'Das echte Oberteil, die Hose und das Genesis-Hemd gegen Blender, dazu die Kleinproben (Tuch auf Kugel und Würfel, Selbstkollision, Reibung, Luft, Presets, Biegedämpfung).',
         'cli',
         '\n'.join((
             'cd A:\\3DTools',
             R + 'vergleich_kern.py <thema> [Argumente]',
             '# Themen: roundtrip hose|oberteil [bilder=12] | kleinteile [Name …] [--neu] [--host] | alt [Name …] | auftrag [Name …] | ensemble <Name> … [--n=8] [--neu]')),
         [(W + 'kernroundtrip.py', 'Kernroundtrip'), (W + 'kernfaelle.py', 'Kernfaelle'), (W + 'kernblender.py', 'Kernblender'), (W + 'kernensemble.py', 'Kernensemble'),
          (W + 'kernauftrag.py', 'Kernauftrag'), (W + 'kernalt.py', 'Kernalt'), (W + 'kernprobe.py', 'Kernprobe')],
         'roundtrip: dieses Stück auf diesem Körper, drapieren.py gegen den Solver (Blender zweimal); kleinteile rechnet die Proben von kernfaelle.py (Blender aus der Ablage, --neu rechnet ihn '
         'neu); alt: dieselben Proben im Paket vor dem Ausbau gegen heute; auftrag: Auftragsweg (stoff_lauf.py) gegen den direkten Weg, bitgleich?; ensemble: je n Läufe mit 1 µm Störung. '
         'Eigene Skripte, dieselbe Messung: das Hosen-Ensemble (blender_ensemble.py hose 24 5), das Genesis-Hemd über die Pipeline-Klassen (kernhemd.py aus HumanBodyWeb), das echte Haar '
         '(blender_haar_vergleich.py 32315 12 13 --echt). Ergebnis (README, 02.10.2026): Oberteil 12 Bilder 1,8 mm, 24 Bilder 2,7 mm (Blender-Rauschen 2,3 mm); Hose im Ensemble nicht von '
         'Blender zu unterscheiden; Genesis-Hemd 3,0 mm.'),
        ('Federn, Gruppen, Schrumpfen, Innenfedern, Nähte, Material, Druck, Presets (vergleich_federn.py)',
         'Die Federn-Funktionen je Thema gegen Blender: ein Fall ist ein Paar (mit, ohne) einer Funktion.',
         'cli',
         '\n'.join((
             R + 'vergleich_federn.py [thema ...] [--ohne-geraet]',
             '# Themen: gruppen schrumpfen innen naehte material druck presets (ohne Angabe: alle)')),
         [(W + 'vergleich_federn.py', 'VergleichFedern'), (W + 'feder_blender.py', 'FederBlender'), (W + 'feder_vergleich.py', 'FederVergleich'),
          (W + 'feder_thema_gruppen.py', 'FederThemaGruppen'), (W + 'feder_thema_presets.py', 'FederThemaPresets')],
         'Jeder Fall druckt eine Zeile (mm als mittel/max, Definition in feder_vergleich.py); die Tabelle des letzten Aufrufs steht in _vergleich/federn/ergebnis_<thema>.txt. '
         'Ergebnis (README, 02.10.2026): gleich in etwa 100 Fällen (höchstens 0,003 mm), Vierecke 0,01 mm.'),
        ('Anheften und Wind (vergleich_pins.py)',
         'Weiches und bewegtes Anheften (Goal-Feder, pin_stiffness) und Wind/Kraftfelder an einem hängenden Tuch.',
         'cli',
         '\n'.join((
             R + 'vergleich_pins.py [weich] [bewegt] [wind] [name ...]',
             '# ohne Angabe laufen alle drei Gruppen; ein Name wählt einen Fall; Ergebnisse: _vergleich/pins/<fall>_ergebnis.json')),
         [(W + 'vergleich_pins.py', 'VergleichPins'), (W + 'vergleich_pinfaelle.py', 'Pinfaelle'), (W + 'vergleich_windfaelle.py', 'Windfaelle'),
          (W + 'vergleich_szene.py', 'Vergleichsszene'), (W + 'vergleich_fall.py', 'Vergleichsfall'), (W + 'vergleich_netze.py', 'Vergleichsnetze')],
         'Szene: Tuch 0,6 m × 0,6 m (25 × 25 Punkte, 1.152 Dreiecke) hängt in der XZ-Ebene an seiner oberen Punktreihe, Z oben, Quality 6, Masse 0,3, 16 Bilder; Aufträge entstehen aus '
         'einer Beschreibung (Vergleichsszene), der Solver läuft über den Dateiweg. Ergebnis (README, 02.10.2026): gleich, 0,0001 bis 0,04 mm.'),
        ('Kollision: mehrere und bewegte Körper, Qualität, Klammern, Gruppen (vergleich_kollision.py)',
         'Die Kollisionseinstellungen gegen Blender: Kollisionsobjekte, collision_quality, Impuls-Klammern, Gruppen, Dicke, Reibung, Culling, Use Normal, Selbstkollision.',
         'cli',
         '\n'.join((
             R + 'vergleich_kollision.py [koll] [bewegt] [name ...] [--ohne-host]',
             '# Der Solver läuft standardmäßig auf dem Gerät UND auf dem Host; Ergebnisse: _vergleich/kollision/<fall>_ergebnis.json')),
         [(W + 'vergleich_kollision.py', 'VergleichKollision'), (W + 'vergleich_kollfaelle.py', 'Kollfaelle'), (W + 'vergleich_bewegtfaelle.py', 'Bewegtfaelle'),
          (W + 'vergleich_fall.py', 'Vergleichsfall')],
         'Ergebnis (README, 02.10.2026): gleich, 0,0001 bis 0,04 mm; Kollision im Rauschen von Blender; unklar bleiben impulse_clamp 0,04 und self_impulse_clamp 0,02 (Blender selbst chaotisch).'),
        ('Ensemble: wer liegt näher an Blender (vergleich_ensemble.py)',
         'Blender, Solver auf dem Gerät und auf dem Host je mit denselben Störungen der Ausgangslage; mittlere Abstände innerhalb jeder Gruppe und zwischen den Gruppen.',
         'cli',
         '\n'.join((
             R + 'vergleich_ensemble.py <fall> [anzahl=6]',
             '# fall: ein Name aus Kollfaelle, Bewegtfaelle, Pinfaelle oder Windfaelle (die Variante MIT der Funktion)')),
         [(W + 'vergleich_ensemble.py', 'Vergleichsensemble'), (W + 'vergleich_blender.py', 'Blenderlauf'), (W + 'vergleich_solver.py', 'Solverlauf'),
          (W + 'vergleich_mass.py', 'Vergleichsmass')],
         'Ein Lauf nahe einer Verzweigung (Reibungsschwelle, Kontakt am Rand) ist nur eine Probe seiner Verteilung. Liegt der Abstand Gerät ↔ Blender im Bereich der Abstände INNERHALB von '
         'Blender, ist das Gerät von Blender nicht zu unterscheiden. Störung 1e-7 m (Rundungsniveau von float32), Kreuzabstände: „gleiche Störung“ = Mittel über i von d(A_i, B_i), „andere“ = '
         'Mittel über i ≠ j.'),
        ('Quality 12/19 und time_scale (vergleich_qualitaet.py)',
         'Blenders float32-Schrittschleife (Quality 12 → 13, 19 → 20 Teilschritte) und time_scale ≠ 1: Wind mit Rauschen, weiche bewegte Ziele, Haar-Dynamik.',
         'cli',
         '\n'.join((
             R + 'vergleich_qualitaet.py [wind] [ziele] [haar] [name ...]',
             '# ohne Angabe laufen Wind und Ziele; je Fall Gerät UND Host und die Gegenproben mit dem Altstand; Ergebnisse: _vergleich/qualitaet/')),
         [(W + 'vergleich_qualitaet.py', 'VergleichQualitaet'), (W + 'vergleich_qualitaetfaelle.py', 'Qualitaetsfaelle'), (W + 'vergleich_qualitaetfall.py', 'Qualitaetsfall'),
          (W + 'vergleich_qualitaethaar.py', 'VergleichQualitaetHaar'), (W + 'vergleich_qualitaetalt.py', 'Altstand')],
         'Ergebnis (README, 02.10.2026): 65 Fälle gleich, 0,0000 bis 0,0004 mm. Vorher war Denim 106 mm daneben (LUECKEN.md A1).'),
        ('Biegung an Vielecken, linear, Ruhegestalt, Schrumpfen mit der Zeit (vergleich_biegung.py)',
         'Winkelbiegung an Vielecken, das lineare Biegemodell, Ruhegestalt (Shape Key, dynamisches Netz) und zeitabhängiges Schrumpfen gegen Blender.',
         'cli',
         '\n'.join((
             R + 'vergleich_biegung.py [thema ...] [--ohne-geraet] [--nur <teil des titels>]',
             '# Themen: polygon linear ruhe zeit (ohne Angabe: alle)')),
         [(W + 'vergleich_biegung.py', 'VergleichBiegung'), (W + 'biegung_lauf.py', 'BiegungBlender'), (W + 'biegung_themen.py', 'BiegungThemen'),
          (W + 'biegung_vergleich.py', 'BiegungVergleich')],
         'Ergebnis (README, 02.10.2026): gleich, Vierecke 0,002 bis 0,008 mm, Sechsecke auf dem Host 0,025 mm; Fünfecke sind chaotisch.'),
        ('Choi-Ko fbstar: kubischer Zweig (vergleich_fbstar.py)',
         'Den kubischen Zweig der Druckkraft gegen Blender: Zylinder mit Biegedämpfung 1000, Tuch von 40 m im Winkelmodell.',
         'cli',
         '\n'.join((
             R + 'vergleich_fbstar.py [thema ...] [--ohne-geraet] [--nur <teil des titels>]',
             '# Themen: linear winkel (ohne Angabe: alle)')),
         [(W + 'vergleich_fbstar.py', 'VergleichFbstar'), (W + 'fbstar_lauf.py', 'FbstarBlender'), (W + 'fbstar_themen.py', 'FbstarThemen'),
          (W + 'fbstar_vergleich.py', 'FbstarVergleich')],
         'Ergebnis (README, 03.10.2026): 0,003 mm (Zylinder 0,0028, Winkel 0,0031); ohne den Zweig 2,8 und 569 mm; Negativkontrollen gleich.'),
        ('Kraftfelder, Formen, Sichtbarkeit, Texturen (vergleich_felder.py)',
         'Alle Feldarten, Formen Linie, Oberfläche, Punkte, Sichtbarkeit durch Kollisionsobjekte und Rauschen an einem Textur-Tuch gegen Blender.',
         'cli',
         '\n'.join((
             R + 'vergleich_felder.py [gruppe ...] [name ...]',
             R + 'vergleich_felder.py probe [gruppe ...] [name ...]    # nur Blender: wie weit bewegt das Feld das Tuch (mm), zum Wählen der Stärken',
             '# Gruppen: arten, formen, sicht, textur, textur_neu, rauschen, abfall, nicht_anwendbar')),
         [(W + 'vergleich_felder.py', 'VergleichFelder'), (W + 'vergleich_feldfaelle.py', 'Feldfaelle'), (W + 'vergleich_felderszene.py', 'Feldszene'),
          (W + 'vergleich_blender.py', 'Blenderlauf'), (W + 'vergleich_fall.py', 'Vergleichsfall')],
         'Ergebnis (README, 02.10.2026): gleich; Blender-Texturwerte auf 3e-7.'),
        ('Feldtexturen: Bild, Farbband, Rausch-Arten, Knoten (vergleich_feldtexturen.py)',
         'Zwei Stufen: erst die Texturwerte (Texture.evaluate) in Blender und im Solver an denselben Punkten, dann die Kraft am hängenden Tuch.',
         'cli',
         '\n'.join((
             R + 'vergleich_feldtexturen.py [gruppe ...] [name ...]',
             R + 'vergleich_feldtexturen.py werte [gruppe ...] [name ...]    # nur die Texturwertprobe',
             '# Gruppen: band, farbe, bild, knoten, rauschen, nicht_vergleichbar (nur Blender: Nabla 0 ohne Farbe liest nicht initialisierten Speicher)')),
         [(W + 'vergleich_feldtexturen.py', 'VergleichFeldtexturen'), (W + 'feldtexturen_wertprobe.py', 'Feldtexturenwertprobe'), (W + 'feldtexturen_faelle.py', 'Feldtexturenfaelle'),
          (W + 'feldtexturen_szene.py', 'Feldtexturenszene')],
         'Ergebnis (README, 03.10.2026): 17 Texturen gleich: Wert auf 2,4e-7, Kraft 0,0000 bis 0,004 mm, Gerät gleich Host. Das Bild der Bildfälle liegt als feldtextur_bild.png neben den Ergebnissen.'),
        ('Bewegte Feldobjekte (vergleich_feldbewegung.py)',
         'Das Feldobjekt ändert Ort, Drehung und Größe je Bild oder verformt sein Netz; OHNE = dasselbe Feld fest, MIT = bewegt; die Gegenprobe ist der Solver mit FESTEM Feld.',
         'cli',
         '\n'.join((
             R + 'vergleich_feldbewegung.py [gruppe ...] [fall ...]',
             R + 'vergleich_feldbewegung.py zeit [fall ...]    # Zeitversatz-Gegenprobe: Lage um −1 … +1 Bild verschoben',
             '# Gruppen: verschiebung, drehung, skalierung, netz')),
         [(W + 'vergleich_feldbewegung.py', 'VergleichFeldbewegung'), (W + 'feldbewegung_faelle.py', 'Feldbewegungsfaelle'), (W + 'feldbewegung_szene.py', 'Bewegtfeldszene'),
          (W + 'feldbewegung_pruefung.py', 'Feldlagepruefung')],
         'Ergebnis (README, 03.10.2026): 14 Fälle gleich, 0,0001 bis 0,02 mm; mit festem Feld bis 146 mm daneben.'),
        ('Oberteil-Inseln im Ensemble (vergleich_inseln.py)',
         'Die 28 losen Punkte des Oberteils (22 und 6 Punkte ohne Feder zum Hauptstück): Blender und Solver je n Läufe, Vergleich der Verteilungen (Endlage, Hautabstand, Lösebild).',
         'cli',
         '\n'.join((
             R + 'vergleich_inseln.py ensemble [--n=12] [--ungestoert] [--neu] [--budget=SEK]',
             R + 'vergleich_inseln.py auswerten [--n=12]    # nur aus den Ablagen, kein Blender',
             R + 'vergleich_inseln.py isoliert <frei|frei_ohne|koerper> [--n=40] [--host] [--neu]')),
         [(W + 'inselablauf.py', 'Inselablauf'), (W + 'inselensemble.py', 'Inselensemble'), (W + 'inselisoliert.py', 'Inselisoliert'), (W + 'kernblender.py', 'Kernblender'),
          (W + 'kernroundtrip.py', 'Kernroundtrip')],
         'Blender-Läufe liegen in _vergleich/inseln/ (Name mit Hash aus Auftrag und Netzen), die des Solvers mit dem Hash der Paketquellen — ein Aufruf rechnet nur, was fehlt. --budget '
         'begrenzt die Zeit (ein Lauf 70–100 s). Ergebnis (README, 02.10.2026): nicht unterscheidbar (12 Läufe je Seite).'),
        ('Streuung: Verteilungen mit n Läufen (vergleich_streuung.py)',
         'Weicht der Solver in Streuung und Mittelwert von Blender ab? Energietest, Streuungstest, Schwerpunkt, Mann-Whitney, KS, Brown-Forsythe über n Läufe je Seite.',
         'cli',
         '\n'.join((
             R + 'vergleich_streuung.py ensemble <fall> [--n=30] [--ungestoert] [--neu] [--budget=SEK] [--host]',
             R + 'vergleich_streuung.py auswerten <fall> [--n=30] [--host]     # nur aus den Ablagen',
             R + 'vergleich_streuung.py bitgleich <fall> [--index=0]            # Gerätelauf in zwei Prozessen bitgleich?',
             R + 'vergleich_streuung.py ordnung <fall> [--n=30] [--nur-dreiecke]    # nur die Reihenfolge der Dreiecke und Punkte gemischt',
             '# Fälle: hose, hemd, reibung, kugel_dicke, kugel; Fall <fall>@<Störung in m> skaliert die Zufallszahlen')),
         [(W + 'streuungablauf.py', 'Streuungsablauf'), (W + 'streuungfall.py', 'Streuungsfall'), (W + 'streuungfaelle.py', 'Streuungsfaelle'),
          (W + 'streuungbericht.py', 'Streuungsbericht'), (W + 'streuungordnung.py', 'Streuungordnung')],
         'Ergebnis (README, A5, 03.10.2026): Hose, Gerät, 200 Blender- und 500 Solver-Läufe: Streuung innen 44,3 gegen 45,2 mm, Verhältnis Solver/Blender 1,02 (95-%-Intervall 0,95–1,10), '
         'Energietest p = 0,84, Schwerpunkt z −1,5 ± 2,0 mm — gleich. Das Verhältnis 1,17 bei n = 12 war Stichprobenrauschen (ein Ensemble von 12 streut im Verhältnis um den Faktor 0,72–1,36). '
         'Platte mit Reibung 50 1,04, Kugel 0,99, Kugel mit Dicke 0,02 0,98. Das Hemd liegt 0,20 ± 0,08 mm höher als in Blender (p = 0,014), Ursache nicht gefunden. Der Gerätelauf ist über zwei '
         'Prozesse bitgleich, Blender ebenso. --fassung=<hash>|jetzt|neueste legt die Solver-Ablage fest. Ablagen: _vergleich/streuung/<fall>/.'),
        ('Haar-Dynamik: Kopf, Hime Cut, Dynamik, Kontinuum, Zusätze (vergleich_haar.py)',
         'Blenders Haar-Dynamik gegen Haarsimulation, je Thema ein ganzer Vergleich.',
         'cli',
         '\n'.join((
             R + 'vergleich_haar.py <thema> [unterthema]',
             '# Themen: kopf (platte|hang|kugel|echt|raender) | hime (nullsegment|ensemble|voll) | dynamik (| echt, 32.315 Strähnen) | kontinuum | zusaetze (bending_random, pin, wind, kopf) | '
             'eingefroren | alle (eine Stunde und mehr)')),
         [(W + 'haarvergleich_dynamik.py', 'HaarvergleichDynamik'), (W + 'haarvergleich_kopf.py', 'HaarvergleichKopf'), (W + 'haarvergleich_hime.py', 'HaarvergleichHime'),
          (W + 'haarvergleich_kontinuum.py', 'HaarvergleichKontinuum'), (W + 'haarvergleich_zusaetze.py', 'HaarvergleichZusaetze'),
          (W + 'haarvergleich_eingefroren.py', 'HaarvergleichEingefroren')],
         'Ergebnisse unter _vergleich/haar/<thema>/. Ergebnis (README, 02.10.2026): ohne Kollision gleich (32.315 Strähnen 0,001 mm im Mittel, 1,4 mm im Größten); Kopfkollision: Blender selbst '
         'chaotisch (Blender gegen Blender 13,4 mm); Hime Cut explodiert in Blender mit 3 mm Rand in 6 von 30 gestörten Läufen, im Solver in 7 von 28.'),
        ('Haar mit float32-genauen Ausgangspunkten (vergleich_haarruhe.py)',
         'Profitiert das Haar von der Angleichung der Ruhewerte des Geräts (Geraeteruhe)? Der Solver im Zustand vor und nach dem Fix gegen dieselben Blender-Läufe.',
         'cli',
         '\n'.join((
             R + 'vergleich_haarruhe.py <thema> [--neu]',
             '# Themen: zustand | host | ohne | kopf | ensemble | alle (eine Dreiviertelstunde); Zwischenspeicher _vergleich/haarruhe/')),
         [(W + 'vergleich_haarruhe.py', 'Haarruhevergleich'), (W + 'haarruhe_ensemble.py', 'Haarruheensemble'), (W + 'haarruhe_szene.py', 'Haarruheszene')],
         'Befund vor dem Fix: Die Angleichung griff beim Haar nie, weil der virtuelle Punkt bei float32-Schlüsseln in float64 keine float32-Zahl war (HaarNetz.virtuelle_wurzel). '
         'Ergebnis (README, 02.10.2026): Haar-Dynamik ohne Kollision gleich; mit Kopfkollision ist Blender selbst chaotisch.'),
        ('Haar-Erzeugung: Wurzeln bis Kinder, Vierecke, Ecken, Volumen (vergleich_haarform.py)',
         'Haarverteilung, Wachsen, Pfade, Kinder und Kamm gegen Blender; klein (8 bis 500 Wurzeln) und deterministisch.',
         'cli',
         '\n'.join((
             R + 'vergleich_haarform.py [wurzeln] [wachsen] [pfade] [kinder] [kamm] [vierecke] [ecken] [volumen]',
             '# ohne Angabe alle Teile; Ergebnisse: _vergleich/haarform/')),
         [(W + 'haarform_blender.py', 'Haarformblender'), (W + 'haarform_tabelle.py', 'Haarformtabelle'), (W + 'haarform_wurzeln.py', 'Wurzelvergleich'),
          (W + 'haarform_wachsen.py', 'Wachsvergleich'), (W + 'haarform_pfade.py', 'Pfadvergleich'), (W + 'haarform_kinder.py', 'Kindervergleich'), (W + 'haarform_kamm.py', 'Kammprobe')],
         'Ergebnis (README, 02.10.2026): gleich, höchstens 0,0016 mm. Der Kamm läuft nur als Probe (brush_edit stürzt in Blender im Hintergrund ab).'),
        ('Haar-Pfade: Effektoren, Kurven, Texturen, Bearbeitung, Vielecke (vergleich_haarrest.py)',
         'Die übrigen Haar-Funktionen gegen Blender: Kraftfelder auf Pfaden, Führungskurven, Texturen, Edit-Modus, Vielecke als Emitter.',
         'cli',
         '\n'.join((
             R + 'vergleich_haarrest.py [kraefte] [kinderkraefte] [kurven] [kinderkurven] [texturen] [texturgeschwindigkeit] [texturkinder] [edit] [polygone] [polygonrahmen] [polygonkinder]',
             '# ohne Angabe alle Teile; Ergebnisse: _vergleich/haarrest/')),
         [(W + 'haarrest_blender.py', 'Haarrestblender'), (W + 'haarrest_kraefte.py', 'Kraeftevergleich'), (W + 'haarrest_edit.py', 'Editvergleich'),
          (W + 'haarrest_polygone.py', 'Polygonvergleich'), (W + 'haarrest_textvergleich.py', 'Texturvergleich'), (W + 'haarform_tabelle.py', 'Haarformtabelle')],
         'Die Felder stehen in der Schreibweise von object.field und werden für beide Seiten aus derselben Beschreibung gebaut. Ergebnis (README, 02.10.2026): gleich, 214 Zeilen.'),
        ('Führungskurven: Bezier, NURBS, Poly (vergleich_kurven.py)',
         'Den Pfad der ausgewerteten Kurve (Follow Path bei 129 Zeiten) und Haare, die einer Bezier- oder NURBS-Führungskurve folgen.',
         'cli',
         '\n'.join((
             R + 'vergleich_kurven.py [pfad] [haar]',
             '# ohne Argument beide Teile; Ergebnisse: _vergleich/kurven/')),
         [(W + 'kurven_pfadvergleich.py', 'Kurvenpfadvergleich'), (W + 'kurven_haarvergleich.py', 'Kurvenhaarvergleich'), (W + 'kurven_szenen.py', 'Kurvenszenen'),
          (W + 'haarform_tabelle.py', 'Haarformtabelle')],
         'Blender nimmt dafür nur Legacy-Kurven mit use_path. Ergebnis (README, 03.10.2026): Pfad 47 Szenen höchstens 0,00025 mm, Haare 25 Szenen höchstens 0,0051 mm; als Poly gerechnet 11 bis 1965 mm daneben.'),
        ('UV, Packen, Texturbacken, UDIM (vergleich_uv.py)',
         'UV-Abwicklung, Packer, Löcher, Symmetrie, SLIM, Henkel, Packer-Pins, Zielkachel und das Backen von Texturen gegen Blender.',
         'cli',
         '\n'.join((
             R + 'vergleich_uv.py [selbst] [smart] [unwrap] [pack] [grenzen] [bake] [kamera] [foto] [loecher] [symmetrie] [optionen] [slim] [xatlas] [optimal] [formmodell] [henkel] [udim] [packpins] [packmerge] [packudim]',
             '# ohne Angabe: alle; selbst = Blender gegen sich selbst in zwei Prozessen (bitgleich?)')),
         [(W + 'vergleich_uv.py', 'VergleichUv'), (W + 'blender_aufruf.py', 'Blenderaufruf'), (W + 'vergleich_textabelle.py', 'Textabelle'), (W + 'vergleich_uvsmart.py', 'VergleichUvSmart'),
          (W + 'vergleich_uvunwrap.py', 'VergleichUvUnwrap'), (W + 'vergleich_uvpack.py', 'VergleichUvPack'), (W + 'vergleich_uvform.py', 'VergleichUvForm'),
          (W + 'vergleich_uvpackpins.py', 'VergleichUvPackPins'), (W + 'vergleich_uvpackudim.py', 'VergleichUvPackUdim'), (W + 'vergleich_texturbake.py', 'VergleichTexturBake'),
          (W + 'vergleich_texturudim.py', 'VergleichTexturUdim')],
         'Ergebnisse unter _vergleich/uv/. Ergebnis (README, 02.10./03.10.2026): gleich bis auf erklärte Gleichstände (Form etwa 3e-8, Lage höchstens 5e-7); Packer-Pins, merge_overlap und Zielkachel '
         'Lage höchstens 5,1e-5 in 444 + 168 + 298 Fällen (Zählung aus ergebnis.json), sieben erklärt. Blenderaufruf startet Blender mit TMP/TEMP im Arbeitsordner (nie im System-Temp), '
         'immer nur ein Prozess.'),
        ('Einzelvergleiche am Kleidstück (blender_ab, blender_verlauf, blender_streuung, blender_ensemble, blender_vergleich)',
         'Wo trennen sich Blender und Solver? Schaltergruppen, Verlauf Bild für Bild, Streuung, Ensemble, Tuch auf Kugel.',
         'cli',
         '\n'.join((
             R + 'blender_ab.py [hose|oberteil|tuch] [bilder=6] [satz,satz,…]    # Sätze: frei, koerper, selbst, beides, ohnereibung, schnell',
             R + 'blender_verlauf.py [hose|oberteil] [bilder=24] [--ohne-selbst] [--reibung=5]',
             R + 'blender_streuung.py [hose|oberteil] [bilder=13] [stoerung_mm=0.01] [anheften=0|1]',
             R + 'blender_ensemble.py [hose|oberteil] [bilder=24] [anzahl=5] [stoerung_m=1e-7]',
             R + 'blender_vergleich.py [bilder] [punkte_je_seite]    # Tuch auf Kugel, Z oben')),
         [('Stoffsolver/stoffsimulation.py', 'Stoffsimulation'), ('Stoffsolver/stoffnetz.py', 'StoffNetz'), ('Stoffsolver/stoffmaterial.py', 'StoffMaterial'),
          ('Stoffsolver/kollider.py', 'Kollider')],
         'Eingaben der Hose und des Oberteils: _vergleich/eingaben/z_oben/ (Job test3, Runde 21 — Meter, Z oben, Füße bei 0, nichts angeheftet), Einstellungen wie drapieren.py (Quality 6, '
         'Abstand 0,004, Körperdicke 0,004, Selbstabstand 0,003); Blender simuliert Bild 2…bilder, der Solver bilder − 1 Bilder. Die Kugel muss nach außen zeigen — Blender dreht nichts um. '
         'Der Solver bekommt Z oben mit schwerkraft (0, 0, −9,81), wie Blender fällt. Die Hose ist chaotisch (1e-7 m Störung ändern das Ergebnis nach 11 Bildern im Mittel um 11 mm): '
         'Einzelläufe sagen nichts, das Ensemble schon.'),
        ('Einzelvergleiche am Haar (blender_haar_vergleich, blender_haar_kopf, blender_haar_probe, blender_haar_streuung)',
         'Synthetische und echte Strähnen in Blenders Haar-Dynamik und im Solver nebeneinander: Lage je Bild, Kopfkollision, Probe der Blender-Seite, Streuung.',
         'cli',
         '\n'.join((
             R + 'blender_haar_vergleich.py [straehnen=64] [punkte=12] [bilder=25] [--variabel] [--numpy]',
             R + 'blender_haar_kopf.py [straehnen=48] [punkte=10] [bilder=13] [rand_mm=3]',
             R + 'blender_haar_probe.py [--straehnen 8] [--punkte 12] [--bilder 20] [--segment 0.01] [--variabel] [--verlauf] [--abseits] [--wert name=zahl ...] [--nur-start]',
             R + 'blender_haar_streuung.py [von=24000] [anzahl=600] [bilder=13] [stoerung_mm=0.01]')),
         [(W + 'blender_haarlauf.py', 'Haarlauf'), ('Stoffsolver/haarsimulation.py', 'Haarsimulation'), ('Stoffsolver/haarwurzeln.py', 'Haarwurzeln')],
         'blender_haarlauf.py läuft IN Blender (Partikelsystem Typ HAIR mit use_hair_dynamics, bpy.ops.curves.convert_to_particle_system) und nimmt die Strähnen als npz; die Namen der Werte '
         'stehen wie in bpy (quality, mass, bending_stiffness, pin_stiffness, time_scale, …). blender_haar_kopf nimmt 3 mm Rand statt Blenders 0,02 + 0,015 m, damit Blender selbst stabil '
         'bleibt. Ergebnis (README, 02.10.2026): 64 Strähnen 0,000 / 0,00 mm, 4.000 Strähnen 0,000 / 0,03 mm, 32.315 Strähnen 0,001 / 1,42 mm (Blender gegen Blender 0,002 / 14,75 mm).'),
        ('Tests des Stoffsolvers (nur auf Ansage)',
         'Jacobi-Matrizen gegen finite Differenzen, Handrechnung der Federkräfte, Kontaktantwort, Geometrie gegen Brute-Force, Blender-Messwerte als feste Zahlen, Warp gegen NumPy je Baustein.',
         'regel',
         '\n'.join((
             'cd A:\\3DTools',
             'python14\\Scripts\\python.exe -m unittest Stoffsolver.tests.test_stoffnetz …    # einzeln benannte Module, nur auf Ansage',
             'python14\\Scripts\\python.exe -m unittest discover -s Stoffsolver/tests -t . -p "test_*.py"    # alles')),
         [],
         'Nicht ohne Ansage starten (Regel testsuite-nur-auf-ansage). Die Host-Läufe erzwingen rechner=\'numpy\', die Warp-Kerne laufen auf geraet=\'cpu\' (LLVM), nur der CUDA-Motor ist mit '
         'skipUnless(CUDA) markiert; der erste Lauf nach einer Änderung an Warp-Kernen übersetzt neu. Gesamtlauf vom 03.10.2026 (README): 3.127 Tests in 191,7 s, alle grün, mit CUDA-GPU, '
         'Maschine von anderen Sitzungen belegt. Gegenprobe: mehr als 150 Verfälschungen (Monkeypatch oder Eingriff in den Quelltext, danach zurückgenommen) — jede macht mindestens einen Test rot.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('VergleichFedern', 'ruft', 'FederBlender', 'der Blender-Lauf eines Falls'),
        ('VergleichFedern', 'ruft', 'FederVergleich', 'die Maße und das Urteil je Fall'),
        ('VergleichFedern', 'ruft', 'FederThemaGruppen', 'thema(name): je Thema eine Klasse, hier gruppen (ebenso FederThemaPresets für presets)'),
        ('VergleichPins', 'ruft', 'Pinfaelle', 'die Fälle für weich und bewegt'),
        ('VergleichPins', 'ruft', 'Windfaelle', 'die Fälle für wind'),
        ('VergleichPins', 'ruft', 'Vergleichsszene', 'eine Beschreibung → Auftrag für Blender und für den Solver'),
        ('VergleichPins', 'ruft', 'Vergleichsfall', 'Rauschgrenze, Grundwert, Wirkung, Vergleich, Gegenprobe'),
        ('VergleichPins', 'ruft', 'Vergleichsnetze', 'das Tuch'),
        ('VergleichKollision', 'ruft', 'Kollfaelle', 'die Fälle für koll'),
        ('VergleichKollision', 'ruft', 'Bewegtfaelle', 'die Fälle für bewegt'),
        ('VergleichKollision', 'ruft', 'Vergleichsfall', 'Rauschgrenze, Grundwert, Wirkung, Vergleich, Gegenprobe'),
        ('Vergleichsensemble', 'ruft', 'Blenderlauf', 'der Blender-Prozess je Störung'),
        ('Vergleichsensemble', 'ruft', 'Solverlauf', 'lauf(ordner, name, auftrag): der Solver über den Dateiweg'),
        ('Vergleichsensemble', 'ruft', 'Vergleichsmass', 'Punktabstände in mm'),
        ('Vergleichsensemble', 'ruft', 'Kollfaelle', 'ein Fall mit der Funktion (ebenso Bewegtfaelle, Pinfaelle, Windfaelle)'),
        ('VergleichQualitaet', 'ruft', 'VergleichPins', 'dasselbe Tuch der Pins'),
        ('VergleichQualitaet', 'ruft', 'Qualitaetsfaelle', 'die Fälle für Wind und Ziele'),
        ('VergleichQualitaet', 'ruft', 'VergleichQualitaetHaar', 'die Fälle für haar'),
        ('VergleichBiegung', 'ruft', 'BiegungBlender', 'der Blender-Lauf'),
        ('VergleichBiegung', 'ruft', 'BiegungThemen', 'die Themen polygon, linear, ruhe, zeit'),
        ('VergleichBiegung', 'ruft', 'BiegungVergleich', 'Maße und Urteil'),
        ('VergleichFbstar', 'ruft', 'FbstarBlender', 'der Blender-Lauf'),
        ('VergleichFbstar', 'ruft', 'FbstarThemen', 'die Themen linear und winkel'),
        ('VergleichUv', 'ruft', 'Blenderaufruf', 'lauf(skript, auftrag, name): Blender im Hintergrund, TMP im Arbeitsordner'),
        ('VergleichUv', 'ruft', 'Textabelle', 'die Tabelle mit Urteil'),
    ]
