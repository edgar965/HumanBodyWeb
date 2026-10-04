# -*- coding: utf-8 -*-
"""Werkzeugmeshfigur — Gruppe „Mesh to 3D: Netz → Genesis-9-Figur (Körperfit, Gesicht, Registrierung)“ des Reiters „Tools“ (03.10.2026).

Schema: `Architektur2d3dwerkzeuge`. Gelesen am 03.10.2026: `Meshfigurendpunkte`, `Meshfigurlauf`, `Meshfiguroptionen`, `Meshfigurkette`, `Meshfigurregler`, `Meshfigurende`,
`Meshfigurrunner`, `Meshfigurregistrierung`, `Meshfigurmodell`, `G9netzbereiche`, `G9netzlandmarken`, `Engine2d3dKleiderkoerper`. Wer die Zahlen sucht: Tagebuch
`Docu/tagebuch/2026-09-27_modell-aus-dateien-reiter-mesh-to-3d.md` und `architektur2d3dmessung.py`.
"""

__all__ = ['Werkzeugmeshfigur']


class Werkzeugmeshfigur:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    W = 'VideoToBVH/wrappers/'

    KENNUNG = 'meshfigur'
    TITEL = 'Mesh to 3D: Netz → Genesis-Figur (Körperfit, Gesicht, Registrierung)'
    EINLEITUNG = (
        'Mesh to 3D legt Genesis 9 auf ein Menschen-Netz (TRELLIS, Hunyuan, Scan): die Regler und die Haltung werden so gestellt, dass der Abstand Figur ↔ Netz '
        'klein wird (Adam auf der Grafikkarte, Abstände per KNN). Reihenfolge der Schritte: erkennung, haar, kleidung, kalibrierung, koerper, gesicht, rest, textur, vorschau, '
        'frisur, speichern. Erst die Regler der Größe und Proportionen, dann die Feinregler; das Gesicht hat eine eigene Kette. In 2D3D Kleider wird die fertige Figur '
        'übernommen (Sekunden) oder die Kette gerechnet (Minuten). Läufe nur nach Ansage von Edgar — sie belegen die Grafikkarte.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Auftrag anlegen und starten',
         'Legt aus einem Netz (Körper, optional Kopf) einen Auftrag an und rechnet die Kette bis zur fertigen Genesis-Figur.',
         'api',
         'POST /api/meshfigur/anlegen/   (multipart: name, netz=<Datei> ODER pfad_koerper=<Pfad>, pfad_kopf=<Pfad>?, optionen=<JSON>, starten=1|0)   → {ok, id, kennung, url}\n'
         'POST /api/meshfigur/<id>/starten/   {optionen?, ab?: <Schritt>, pfade?: {koerper, kopf}}\n'
         'GET /api/meshfigur/<id>/zustand/   POST …/anhalten/   POST …/modell/ {name}   POST …/loeschen/',
         [(A + 'meshfigur.py', 'Meshfigurendpunkte'), (D + 'meshfigurarbeiter.py', 'Meshfigurarbeiter'), (D + 'meshfigurlauf.py', 'Meshfigurlauf'),
          (D + 'meshfigureingang.py', 'Meshfigureingang'), ('HumanBodyWeb/core/models/meshfigurauftrag.py', 'Meshfigurauftrag')],
         'Nur nach Ansage von Edgar. Netzformate GLB, GLTF, OBJ (mit MTL und Bildern), PLY, STL, OFF, genau ein Körpernetz. Der Lauf ist ein eigener Prozess '
         '(manage.py meshfigur_fahren <id> [--ab <schritt>], den die API startet — nicht von Hand). ab = <Schritt> startet dort; ein geänderter Pfad immer ab der Erkennung; '
         'während eines Laufs antwortet Einstellungen/Starten mit 409. Zeiten (Damira, 27.09.2026): erster Lauf 571 s mit Körper 199 s, Gesicht 128 s, Textur 151 s; dritter 518 s. '
         'In 2D3D Kleider (Auftrag 2026.10.01.20.10.04, vor dem Frühstopp): koerper 217,9 s, gesicht 152,0 s, textur 210,1 s, frisur 161,1 s, Summe 872,0 s '
         '(architektur2d3dmessung.KOERPER). Ergebnis: Modell <Name> Mesh in data/models (Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle) und Ablage '
         'output/Export/MeshTo3D/<Name>_<Zeit>/; „Auftrag löschen“ lässt Modell und Ablage stehen.'),
        ('Optionen von „Mesh to 3D“',
         'Alle Einstellungen der Kette mit Vorgabe und Wirkung; jede Eingabe der Seite wird sofort gespeichert.',
         'api',
         'GET /api/meshfigur/katalog/\n'
         'POST /api/meshfigur/<id>/einstellungen/   {optionen?: {…}, pfade?: {koerper, kopf}, kopf_an?: bool}   → {ok, optionen, eingang, neu_eingelesen}',
         [(D + 'meshfiguroptionen.py', 'Meshfiguroptionen'), (A + 'meshfigureinstellungen.py', 'Meshfigureinstellungen')],
         'Schlüssel (Vorgabe): basis feminine | masculine | neutral (feminine); hoehe_cm 0…250 (0 = Größe des Netzes, sonst Scheitel ohne Haar); runden 1 | 2 | 3 (2); gesicht an | aus (an); '
         'daempfung weich 0,01 | mittel 0,02 | fest 0,05 (mittel); eigenmorph und symmetrie an | aus (an); textur mesh | hautton | aus (mesh); kopfhaut haar | haut (haar); kleidung weich | '
         'ignorieren | wie_haut (weich); kleidungszug 0…100 % (60); kleidungsabstand_mm 0…40 (8); genitalform 0…100 % (30, nur männliche Grundfigur); kandidaten 1…64 (1); rest_kandidaten '
         '1…64 (16); referenz und blind (Testfall: Regler der Referenzfigur gesperrt); frisur beste | daz | eigen | aus; haarkarten und modell an | aus. pruefen() nimmt nur bekannte '
         'Schlüssel und Werte, alles andere fällt auf die Vorgabe. Normalensuche: 16 Nachbarn im Eigenmorph hoben die Punkte mit Gewicht an der Nase von 48 auf 91 %, in der Anpassung '
         'zog dieselbe Suche Lippen und Kinn 6–12 mm vor das Netz — deshalb dort 1.'),
        ('Seite „Mesh to 3D“',
         'Auftragsseite mit Fortschritt, 3D-Bühne, Vergleich und Reglerliste — für Menschen; Sessions nehmen die API.',
         'seite',
         '/modell-aus-dateien/#meshto3d   (Liste)   →   /modell-aus-dateien/meshfigur/<kennung>/',
         [(A + 'meshfigur.py', 'Meshfigurendpunkte')],
         'Schalterreihe über der 3D-Ansicht: Mesh, Haare, Kleider, Nebeneinander, 3DModell (Vorgabe 3DModell, Haar, Kleider). Knöpfe: Neu berechnen (startet ab Erkennung, wenn Pfade '
         'geändert sind), Kopf-Eigen (→ /gesichtsform/), „Als Genesis-Figur speichern“ mit freiem Namen (POST …/modell/; eine fremde Figur gleichen Namens wird abgelehnt). Textfelder werden '
         '700 ms nach dem letzten Tastendruck gespeichert.'),
        ('Erkennung, Kalibrierung und Netzlandmarken',
         'Richtet das Netz aus, findet Körper- (33) und Gesichtspunkte (478) und legt sie auf die Netzfläche; kalibriert einmal je Rechner, wo die Landmarken auf Genesis liegen.',
         'api',
         "POST /api/meshfigur/<id>/starten/   {ab: 'erkennung'}   bzw.   {ab: 'kalibrierung'}   (läuft nur, wenn die Tabelle fehlt)\n"
         '# Python: from Genesis9.netzlandmarken import G9netzlandmarken; G9netzlandmarken.holen()   # Tabelle oder None',
         [(D + 'meshfigurlauf.py', 'Meshfigurlauf'), (W + 'meshfigur_erkennungsschritt.py', 'Meshfigurerkennungsschritt'), (G + 'netzlandmarken.py', 'G9netzlandmarken'),
          (G + 'figurglb.py', 'G9figurglb'), (W + 'meshfigur_landmarkenflaeche.py', 'Meshfigurlandmarkenflaeche')],
         'Erkennung (Damira): 48.935 Punkte nach dem Zusammenführen der UV-Nähte, Körper 33 Punkte (RANSAC-DLT + Gauß-Newton, 2–8 px), Gesicht 478 Punkte in 15 Nahaufnahmen (median 4,3 px). '
         'Kalibrierung: Genesis als texturierte GLB (G9figurglb) durch denselben Weg, Tabelle Genesis9/ablage/meshfigur_landmarken_v1.npz — Gesicht median 1,03 mm vom Käfig '
         '(p90 2,41, max 10,4), Gelenke relativ zum Daz-Gelenk (Detektor gegen Daz 5–31 mm!). Die alte 68-Punkte-Tabelle taugt für 3D nicht (Augen 94 mm daneben, Kinnlinie 20 mm). '
         'Netz-Landmarken auf die Fläche (Meshfigurlandmarkenflaeche, 400.000 Proben): ≤ 3 mm unverändert, ≤ 30 mm auf die nächste Probe, darüber NaN; bei Edgars Körpernetz lagen 126 von 478 '
         'mehr als 8 mm daneben (29.09.2026). Seitentausch in Rückansichten wird je Ansicht geprüft.'),
        ('Kopfnetz (zweites Netz nur für den Kopf)',
         'Setzt ein eigenes Kopfnetz (Hunyuan-Gesicht) auf den Körper des Körpernetzes; die Gesichtskette fittet an dessen Gesicht.',
         'api',
         'POST /api/meshfigur/anlegen/   pfad_kopf=<Pfad>      POST /api/meshfigur/<id>/einstellungen/   {pfade: {kopf: <Pfad>}, kopf_an: true|false}',
         [(D + 'meshfigureingang.py', 'Meshfigureingang'), (W + 'meshfigur_erkennungsschritt.py', 'Meshfigurerkennungsschritt'), (W + 'meshfigur_kopfnetz.py', 'Meshfigurkopfnetz'),
          (W + 'meshfigur_kopfabgleich.py', 'Meshfigurkopfabgleich'), (W + 'meshfigur_zielnetz.py', 'Meshfigurzielnetz'), (W + 'meshfigur_farbangleich.py', 'Meshfigurfarbangleich')],
         'Arbeitsgröße 0,3 m; Hochachse × Blick aus bis zu 6 × 8 Ansichten, 478 Punkte aus 15 Nahaufnahmen, Umeyama mit Maßstab auf die Gesichtspunkte des Körpernetzes, Ausreißer über '
         '2,5 × Median raus. Schnitt quer zur Halsachse Schulter → Ohrenmitte (nicht Gesichtsmitte: die Achse kippte 34°). Angeglichen wird der KÖRPER an den Kopf (Rumpf vorn, 12–45 cm '
         'unter der Halsebene, gegen 15 Hautstellen im Gesicht; Grenzen 0,25…4), die untersten 35 mm des Kopfes werden an der Naht in die Körperfarbe überblendet. „Kopfnetz verwenden“ aus = Kopf, '
         'Gesicht und Haar aus dem Körpernetz. Scheitert der Kopf, läuft der Lauf mit dem Körpernetz, der Grund steht in erkennung.kopf.fehler.'),
        ('Körperkette (Registrierung, Adam-Fit)',
         'Stellt die Körperregler und die Haltung so, dass Genesis dem Netz am nächsten kommt: Haltung → Größe/Proportionen → Körpertyp → Bereiche.',
         'python',
         'Meshfigurkette(lauf).koerper()   # python14: je Runde Genesis ECHT rechnen, dann der Runner\n'
         '# python10: python VideoToBVH/wrappers/_run_meshfigur.py <auftrag.json> koerper <runde>   (ein Schritt je Aufruf, Zustand in arbeit/zustand.npz)',
         [(D + 'meshfigurkette.py', 'Meshfigurkette'), (D + 'meshfigurregler.py', 'Meshfigurregler'), (D + 'meshfigurgenesis.py', 'Meshfigurgenesis'),
          (W + '_run_meshfigur.py', 'Meshfigurrunner'), (W + 'meshfigur_registrierung.py', 'Meshfigurregistrierung'), (W + 'meshfigur_modell.py', 'Meshfigurmodell'),
          (W + 'meshfigur_kinematik.py', 'Meshfigurkinematik'), (G + 'netzbereiche.py', 'G9netzbereiche'), (G + 'reglerableitung.py', 'G9reglerableitung')],
         'Adam über die freien Größen (torch auf der Karte), alle 5 Schritte neue Nachbarn (KNN beidseitig, Punkt-zu-Ebene, Geman-McClure), Regler nach jedem Schritt auf Dazʼ Grenzen geklemmt. '
         'Runde 1: haltung (300 Schritte, nur Haltung und Lage) → groesse (Stufe 1: Proportion…, BodyMass; 300) → koerpertyp (Stufe 2: Charaktere, Heavy, Muscular, Fitness; 300) → bereiche '
         '(Stufe 3: Brust bis Füße; 400); ab Runde 2 eine Stufe mit allen Reglern. Zwischen den Runden rechnet python14 die Figur echt (Formelketten, Knochenskalierung, JCMs der Haltung). '
         'Frühstopp seit 02.10.2026: alle 25 Schritte; bringt das Beste der letzten 50 weniger als 0,2 % gegenüber dem Besten davor, endet die Stufe (frühestens nach einem Drittel der Schritte). '
         'Gewicht der Käfigpunkte (G9netzbereiche): Haut 1, Finger 0, Hand 0,1, innen 0, Ohr 0,2, Zehen 0,3, Schritt 0,1, Kopfhaut einseitig. Stufe 0 (nie gestellt): ProportionSmaller/Larger, Grundfigur, '
         'Mundhöhle, Ears Gone, HipGenitalBulge (fest über genitalform), Mimik. Gemessen (Damira, 27.09.2026): Figur → Netz 3,17 mm (p95 5,6), Höhe 167,5 cm (echte Damira 167,1). Grenze: kein Fit holt mehr '
         'heraus, als das Netz hat — die echte Damira liegt 8,6 mm vom Netz, der Rücken im Netz 1–2 cm zu dick.'),
        ('Gesichtskette',
         'Kopfhaltung, Schädel, Gesichtszüge, Ohren: eigene Kette über 296 Kopfregler gegen 478 Gesichtspunkte.',
         'python',
         'Meshfigurkette(lauf).gesicht()\n'
         '# python10: python VideoToBVH/wrappers/_run_meshfigur.py <auftrag.json> gesicht',
         [(D + 'meshfigurkette.py', 'Meshfigurkette'), (W + 'meshfigur_registrierung.py', 'Meshfigurregistrierung'), (W + 'meshfigur_landmarken.py', 'Meshfigurlandmarken'),
          (G + 'netzbereiche.py', 'G9netzbereiche'), (D + 'meshfigurregler.py', 'Meshfigurregler')],
         'Stufen: kopfhaltung (200 Schritte) → schaedel (Stufe 11: Kopfgröße, Schädel, Charakterköpfe; 300) → zuege (12: Nase, Mund, Lippen, Augen, Brauen, Wangen, Kinn, Kiefer; 400) → fein '
         '(13: Ohren, Rest; 300). Nur Hals und Kopf drehen; Landmarken zählen nur, wenn ihr Dreieck ganz im Gesichtskern liegt (Kopfpunkte bis 3,5 cm über der Augenhöhe und mindestens 2 cm vor '
         'dem Ohrknochen: dort immer beidseitig, Stirn und Schläfen unter Haar einseitig); Iris 0, Umriss ½; die Dämpfung misst die Wirkung eines Reglers an der Kopfregion. Startet aus der '
         'Stellung der Körperkette. Gemessen (Damira, 27.09.2026): Kopf 4,07 → 1,98 mm; Landmarken Mund 2,5, Augen 3,1, Brauen 3,2, Nase 3,4 mm. Falle: zuerst die Höhe prüfen — wächst der Kopf ins '
         'Haar, wird die Figur 170 statt 167 cm (Cranium Size Larger 1,0). Offen (29.09.2026): 16 von 41 Nasenregler an der Grenze, der gespitzte Mund des Netzes bleibt 4,7 mm (p90 11 mm) daneben.'),
        ('Prio-Liste der Regler (Stufen)',
         'Teilt jeden Genesis-Regler einer Stufe zu — in welcher Reihenfolge Mesh to 3D ihn stellt (Größe zuerst, Feinregler zuletzt) oder dass es ihn gar nicht stellt.',
         'python',
         'from core.dienste.meshfigurregler import Meshfigurregler\n'
         'Meshfigurregler.stufe(name, bereich, teil)   # 0 gesperrt, 1–3 Körper, 11–13 Kopf\n'
         'Meshfigurregler(grund, gesperrt=None).daten(teil, stellung)   # {namen, jetzt, grund, stufe, unten, oben}\n'
         'Meshfigurregler.festwerte(optionen)   # feste Werte, z. B. die Genitalform der männlichen Grundfigur',
         [(D + 'meshfigurregler.py', 'Meshfigurregler'), (G + 'reglerableitung.py', 'G9reglerableitung')],
         'Körper (158 Regler, 27.09.2026): Stufe 1 = Name enthält Proportion oder beginnt mit body_bs_BodyMass (Größe, Beine, Arme, Rumpf, Hals, Schultern, Brustkorb, Hände, Füße); 2 = Bereich '
         'figur oder koerper (Charakterkörper, Heavy, Pear, Muscular, Fitness, Tone) ohne „Abs “; 3 = die übrigen Bereiche. Kopf (296 Regler): 11 = Name endet auf head oder enthält ProportionHeadSize, '
         'Cranium, „Face “, ForeHead, Jaw Height, Head Shape; 12 = Nase, Mund, Lippen, Augen, Brauen, Wangen, Kinn, Kiefer, Schläfe, Philtrum, Nostril, Smile; 13 = Ohren und alles Übrige. Stufe 0 '
         '(nie gestellt): ProportionSmaller/Larger (Kinderproportionen, doppelt zu Height), BaseFeminine_figure_ctrl, BaseFeminine_body_bs, Mouth Cavity, Ears Gone, HipGenitalBulge und die vier '
         'Mimik-Namen (Mimik-Filter in der Gruppe „Gesicht“); auf der männlichen Grundfigur dazu body_bs_Breast…; im Testfall „blind“ die Charakterregler der Referenzfigur (sperrmarken). Werte unter 0,005 '
         'werden 0. Grundfiguren: feminine {BaseFeminine_figure_ctrl_Character: 1}, masculine {BaseMasculine_figure_ctrl_Character: 1}, neutral {}.'),
        ('Rest als Eigenmorph',
         'Legt, was die Regler nicht erreichen, als eigenen Morph eigen:<kennung> dazu — links/rechts gemittelt, geglättet.',
         'python',
         'Meshfigurende(lauf).rest()   # Schritt rest\n'
         'from Genesis9.restmorph import G9restmorph; G9restmorph.ablegen(name, rest, gewicht, steckbrief=None)   # → Reglername eigen:<kennung>',
         [(D + 'meshfigurende.py', 'Meshfigurende'), (G + 'restmorph.py', 'G9restmorph'), (G + 'eigenmorphe.py', 'G9eigenmorphe'), (D + 'meshfiguraugenhoehle.py', 'Meshfiguraugenhoehle')],
         'Rest je Käfigpunkt über die Hautmischung in die Ruhelage zurückgerechnet, symmetrisch gemittelt (Option symmetrie), einseitige (bedeckte) Punkte mit Gewicht 1 verankert und nur nach '
         'innen, dann Laplace-Glättung 6 Schritte × 0,5; die Augenpartie ist Lücke (Meshfiguraugenhoehle). Wert 0…2, Datei 3DObjects/Genesis9/eigenmorphe/<kennung>.npz/.json. Gemessen: Rest 3,2 mm (erster '
         'Lauf), 2,74 mm (dritter); Zeit rest 30,8 s (Auftrag 2026.10.01.20.10.04). Grenze: der Eigenmorph übernimmt die Fehler des Netzes — Figur näher am Netz, aber weiter von der echten Damira '
         '(7,66 → 7,97 mm). Ein Eigenmorph wird unter demselben Namen neu abgelegt; der Fingerabdruck der Stellung trägt seit 27.09.2026 den Dateistand, sonst lieferte der Server die alte Form.'),
        ('Körper übernehmen oder rechnen (2D3D Kleider)',
         'Holt die Figur in einen Auftrag „2D3D Kleider“: aus einem fertigen Auftrag „Mesh to 3D“ übernehmen oder die Kette dort rechnen.',
         'api',
         "POST /api/engine2d3dkleider/<id>/einstellungen/   {optionen: {koerper: {quelle: 'uebernehmen', auftrag: '2026.09.29.15.42.36'}}}\n"
         "POST …/einstellungen/   {optionen: {koerper: {quelle: 'rechnen'}, figur: {basis: 'masculine'}}}",
         [(A + 'engine2d3dkleidereinstellungen.py', 'Engine2d3dKleidereinstellungen'), (D + 'engine2d3dkleideroptionen.py', 'Engine2d3dKleideroptionen'),
          (D + 'engine2d3dkleiderkoerperoptionen.py', 'Engine2d3dKleiderkoerperoptionen'), (D + 'engine2d3dkleiderkoerper.py', 'Engine2d3dKleiderkoerper'),
          (D + 'engine2d3dkleiderkoerperlauf.py', 'Engine2d3dKleiderkoerperlauf'), (D + 'engine2d3dkleidergrundfigur.py', 'Engine2d3dKleidergrundfigur')],
         'übernehmen (Vorgabe): Regler, Eigenmorph, gebackene Kacheln und der Befund von Haar und Kleidung kommen mit, dazu das Netz samt scan_lage als arbeit/bezugsnetz.glb — der 3D-Bezug der '
         'Iterationen; Sekunden. Ohne Kennung fällt es auf rechnen zurück. rechnen: Kette erkennung, haar, kleidung, kalibrierung, koerper, gesicht, rest, textur, vorschau, frisur (ohne Speichern), '
         '872,0 s im Auftrag 2026.10.01.20.10.04, danach Frühstopp und Frisur-Überspringen kürzer (nicht neu gemessen). Gelesen am 03.10.2026: in rechnen gilt aus der Gruppe figur nur basis; '
         'hoehe_cm, runden, gesicht, daempfung, kleidung … stehen auf der Vorgabe von Meshfiguroptionen (Engine2d3dKleiderkoerperlauf.__init__). Der Docstring dieser Klasse nennt den Weg noch '
         '„NICHT GELAUFEN (30.09.2026)“; gelaufen ist er am 01.10.2026. Danach baut Engine2d3dKleidergrundfigur die Grundfigur mit Rig.'),
        ('Prüfwerkzeuge für den Fit (Wegwerfskripte, nur lesen)',
         'Zählt Regler am Anschlag, misst Nasen- und Gesichtsschnitte und zeigt Netz-Landmarken, die nicht auf der Fläche liegen.',
         'cli',
         'python14\\Scripts\\python.exe ProjektTemp\\_wegwerf\\meshto3d\\regler_am_anschlag.py <kennung> [<kennung> …]\n'
         'python14\\Scripts\\python.exe ProjektTemp\\_wegwerf\\meshto3d\\landmarken_daneben.py <kennung> [<schwelle mm, Vorgabe 8>]\n'
         'python14\\Scripts\\python.exe ProjektTemp\\_wegwerf\\meshto3d\\nase_schnitte.py <kennung>',
         [('HumanBodyWeb/core/models/meshfigurauftrag.py', 'Meshfigurauftrag'), ('HumanBodyWeb/core/daten/meshfigurablage.py', 'Meshfigurablage')],
         'Wegwerfskripte, nicht Teil der Pipeline: sie können fehlen. Sie lesen nur (Django-Setup, Stellung des Auftrags, arbeit/*.npz). regler_am_anschlag zählt Regler mit |Wert| ≥ 0,95 und ≥ 0,99, getrennt '
         'nach Nase, übrigem Kopf und Körper; gesicht_schnitte.py <job-uuid> <kennung> liest /zustand/ vom Server. Wer Zahlen aus ihnen zitiert, nennt Skript und Kennung.'),
        ('Regel: Was ein Fit nicht kann',
         'Grenzen, die jede Session kennen muss, bevor sie ein Ergebnis für schlecht oder gut erklärt.',
         'regel',
         '— keine Rezeptzeile: Höhe prüfen, Landmarken auf der Fläche prüfen, Netzgüte als Obergrenze',
         [(G + 'netzbereiche.py', 'G9netzbereiche')],
         'Kein Fit holt mehr heraus, als das Netz hat: Hunyuan erfand bei Damira die Rückseite, die Beinrückseiten waren 1–2 cm zu dick (27.09.2026). Doppelwandige Netze (Außenhaut, Innenwand ~3 mm '
         'darunter): Käfigpunkte fanden die Innenwand, die Figur saß 2–3 mm in der Schale — die Normalensuche löst es nur im Eigenmorph (29.09.2026). Finger und Zehen verkleben in Bild-zu-3D-Netzen: Gewicht 0 '
         'bzw. schwach (Damira: Fäuste, MassFeet 1). Der Kopf wächst ins Haar, wenn eine Stelle unter dem Haar beidseitig zählt (170 cm statt 167). Kleidung im Netz zieht die Figur nur schwach '
         '(Option kleidung weich, kleidungszug 60 %): ohne Zug wird der Rumpf ein Standardkörper — bei Edgar ein Sixpack statt des Bauchs —, zu viel Zug bläht die Figur unter weiten Stellen auf. '
         'Landmarken des Netzes vor jeder Aussage auf ihren Abstand zur Fläche prüfen.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Meshfigurendpunkte', 'ruft', 'Meshfigurarbeiter', 'starten(job, ab): eigener Prozess manage.py meshfigur_fahren'),
        ('Meshfigurendpunkte', 'ruft', 'Meshfigureingang', 'anlegen(dateien, pfad_koerper, pfad_kopf) und aendern(eingang, pfade)'),
        ('Meshfigurendpunkte', 'ruft', 'Meshfiguroptionen', 'pruefen(optionen), katalog()'),
        ('Meshfigurarbeiter', 'ruft', 'Meshfigurlauf', 'meshfigur_fahren: Meshfigurlauf(id).ausfuehren(ab)'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurkette', 'koerper() und gesicht()'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurende', 'rest() und textur()'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurrunner', 'runner(schritt, runde): python10-Unterprozess _run_meshfigur.py'),
        ('Meshfigurlauf', 'ruft', 'G9netzlandmarken', '_kalibrierung(): holen(), sonst Tabelle bauen'),
        ('Meshfigurkette', 'ruft', 'Meshfigurregler', 'speichern(pfad, teil, stellung) und stellung(teil, werte, alt)'),
        ('Meshfigurkette', 'ruft', 'Meshfigurgenesis', 'speichern(pfad): Käfig, Skelett, Haut, Landmarken, JCMs der Haltung je Runde'),
        ('Meshfigurgenesis', 'ruft', 'G9netzbereiche', 'bereiche(), gesichtskern(), spiegel(): Gewichte je Käfigpunkt'),
        ('Meshfigurregler', 'ruft', 'G9reglerableitung', 'holen(satz, grund, teil): Jacobi-Matrix Regler → Punkte und Gelenke'),
        ('Meshfigurrunner', 'ruft', 'Meshfigurregistrierung', 'kette(art, runde): Stufen der Körper- und Gesichtskette'),
        ('Meshfigurrunner', 'ruft', 'Meshfigurmodell', 'Meshfigurmodell(genesis, jacobi, geraet, theta, lage)'),
        ('Meshfigurmodell', 'ruft', 'Meshfigurkinematik', 'Haltung: Hautmischung mit Daz-Winkeln'),
        ('Meshfigurregistrierung', 'ruft', 'Meshfigurlandmarken', 'Gesichts- und Gelenkpunkte als Verlustterme'),
        ('Meshfigurende', 'ruft', 'G9restmorph', 'ablegen(name, rest, gewicht): Eigenmorph aus dem Rest'),
        ('G9restmorph', 'ruft', 'G9eigenmorphe', 'ablegen(name, nummern, deltas, brief)'),
        ('Meshfigurerkennungsschritt', 'ruft', 'Meshfigurkopfnetz', 'Meshfigurkopfnetz(kopfnetz, erkenner): Kopf finden und an den Körper legen'),
        ('Meshfigurkopfnetz', 'ruft', 'Meshfigurkopfabgleich', 'Umeyama, Halsschnitt und Farbfaktor'),
        ('Meshfigurzielnetz', 'ruft', 'Meshfigurfarbangleich', 'Körperfarbe an die Gesichtsfarbe des Kopfes angleichen'),
        ('Engine2d3dKleidereinstellungen', 'ruft', 'Engine2d3dKleideroptionen', 'mischen(alt, neu): Gruppe für Gruppe, geprüft'),
        ('Engine2d3dKleideroptionen', 'ruft', 'Engine2d3dKleiderkoerperoptionen', 'pruefen(roh): Gruppe koerper (quelle, auftrag)'),
        ('Engine2d3dKleiderkoerper', 'ruft', 'Engine2d3dKleiderkoerperlauf', '_rechnen(): schrittfolge() und band(): die Schritte von Mesh to 3D'),
        ('Engine2d3dKleiderkoerperlauf', 'erbt', 'Meshfigurlauf', 'auftrag(), runner(), _erkennung, _kalibrierung bleiben; Auftrag und Ablage sind die von 2D3D Kleider'),
    ]
