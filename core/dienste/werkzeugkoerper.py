# -*- coding: utf-8 -*-
"""Werkzeugkoerper — Gruppe „Körper-Regler und Ortsmorphe“ des Reiters „Tools“ der Seite Hilfe → Architektur → 2D3D (03.10.2026).

Schema: `Architektur2d3dwerkzeuge` (Datei `werkzeug<name>.py`, Klasse `Werkzeug<Name>`, `ZEILEN`, `BEZIEHUNGEN`). Quelle der Wahrheit ist der Code: jede
Klasse hier steht in ihrer Datei, jede Rezeptzeile ruft eine öffentliche Methode von `ModellMitKleidern` oder seiner Mixins (gelesen am 03.10.2026).
"""

__all__ = ['Werkzeugkoerper']


class Werkzeugkoerper:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    P = '2d3DIterationen/iterationen2d3d/'

    KENNUNG = 'koerper'
    TITEL = 'Körper-Regler und Ortsmorphe (Genesis 9)'
    EINLEITUNG = (
        'Der Körper einer Genesis-9-Figur ist eine Reglerstellung {Kanal-ID: Wert} (Daz-Kanäle wie body_bs_ProportionHeight, dazu eigen:… und hb:…) '
        'plus Haltung — ein Netz, viele Stellungen. Reihenfolge: 1. Reglerliste lesen (Namen, Bereiche, Grenzen), 2. Regler setzen — die Form kommt '
        'sonst aus dem Schritt „koerper“ (Gruppe „Mesh to 3D“), m.koerper_regler gilt in einer Runde von 2D3D Kleider —, 3. wo die Regler nicht '
        'reichen, m.koerper_ort örtlich nachformen, 4. m.koerper_huelle nur mit Fotos in der Runde. Ein Rezept reicht man mit '
        'POST /api/engine2d3dkleider/<id>/begutachtung/ {aufrufe} ein (nur nach Ansage von Edgar).'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Reglerliste lesen',
         'Alle Genesis-Regler mit Kanal-ID, Anzeige, Grenzen und Bereich — der Schlüssel für jedes koerper_regler und jeden POST.',
         'api',
         'GET /api/character/genesis9-figur/regler/\n'
         '# Python: from Genesis9.reglerplan import G9reglerplan; G9reglerplan.bereiche()',
         [(A + 'g9figur.py', 'G9figur'), (G + 'reglerplan.py', 'G9reglerplan'), (G + 'reglerbereiche.py', 'G9reglerbereiche'),
          (G + 'reglergrenzen.py', 'G9reglergrenzen'), (G + 'morphablage.py', 'G9morphablage')],
         'Antwort {bereiche: [{schluessel, name, regler: [{name, anzeige, min, max, daz_min, vorgabe, bereich, art}]}], haut, augen, praesets, brauen, '
         'brauenstile, brauenfarben}. name ist die Kanal-ID (z. B. body_bs_ProportionHeight), nicht die Anzeige; die IDs der 200-Plus-Gesichtsregler '
         'tragen Leerzeichen und Suffixe (200_head_bs_Lip Upper Gap-0xa11888f) — nie raten, immer aus der Liste nehmen. 13 Bereiche nach Daz-Region: '
         'figur, koerper, kopf, mimik, hals, brust, ruecken, taille, huefte, arme, haende, beine, fuesse; dahinter „HB-Morphs Körper/Gesicht/Fantasie“, '
         '„Kopf-Eigen“ und „Nachformung (Ort)“. art = pose sind Posensteuerungen (drehen Knochen, nie für die Anpassung an Fotos). Einseitige Formregler '
         '(Daz 0…1) gehen zweiseitig (min = −max; 75 von 610 gemessen am 20.09.2026, G9reglergrenzen), daz_min ist Dazʼ eigene Grenze. Die Zahl der '
         'Regler hängt am installierten Daz-Bestand und ist nicht neu gemessen — die Liste fragen, nicht aus dieser Seite zitieren. Ohne Daz-Bibliothek '
         'antwortet der Endpunkt mit leeren Listen und dem Feld fehler statt mit einem Statuscode.'),
        ('Figur zu einer Reglerstellung rechnen',
         'Rechnet Netz, Skelett und Höhe zu einer Reglerstellung — so sieht man, was ein Regler tut, ohne die Szene.',
         'api',
         'POST /api/character/genesis9-figur/<name>/netz/   {regler: {<Kanal-ID>: wert}, drehung?: {<knochen>: {"rotation/z": grad}}, haut?, augen?, '
         'brauen?, brauenstil?, praesets?, pose?, ausdruck?, griffe?, anhaenge?: false, kleidung?}\n'
         '# Python: from Genesis9.formung import G9formung; f = G9formung.aus_abfrage({"body_bs_ProportionHeight": 0.4}); f.punkte(); f.skelett().bauen()',
         [(A + 'g9figur.py', 'G9figur'), (D + 'g9antworten.py', 'G9antworten'), (G + 'koerpernetz.py', 'G9koerpernetz'),
          (G + 'formung.py', 'G9formung'), (G + 'formeln.py', 'G9formeln')],
         '<name> ist basis, feminine, masculine, ein Charakter oder ein gespeichertes Modell (GET /api/character/genesis9-figur/). Unbekannte oder '
         'unlesbare Kanäle werden still übergangen, Werte auf min…max geklemmt (G9formung.aus_abfrage) — ein Tippfehler im Namen wirkt nicht und '
         'meldet nichts. eigen:… (Eigenmorph, 0…2) und hb:… (HumanBody-Morph, −1…1) gelten auch. Die Antwort trägt Netz, Skelett (skelett), Höhe '
         '(hoehe) und boden: Proportion Legs Length schiebt die Füße 23 cm unter y = 0, Netz und Skelett werden um boden gehoben. Kosten: Ansichtsstufe 1 '
         '(104.480 Punkte) 0,4 s je Reglerzug, 18,7 MB Netz (genesis9.md, 17.09.2026); dieselbe Stellung kommt danach aus dem Antwortvorrat. Das Feld '
         'drehung ist die Haltung der Runden von 2D3D Kleider (G9figur.formung), kein Posenpreset.'),
        ('Grundfigur oder Charakter wählen',
         'Setzt die Grundstellung: neutral, Base Feminine/Masculine oder ein installierter Charakter — Reglerstellungen auf EINEM Netz.',
         'api',
         'GET /api/character/genesis9-figur/   → {figuren: [{name, anzeige, geschlecht, regler, haut}], vorhanden, punkte}\n'
         '# Python: from Genesis9.charaktere import G9charaktere; G9charaktere.liste()',
         [(A + 'g9figur.py', 'G9figur'), (G + 'charaktere.py', 'G9charaktere')],
         'basis = alle Regler 0; feminine = BaseFeminine_figure_ctrl_Character 1; masculine = BaseMasculine_figure_ctrl_Character 1; dazu jede character-.duf '
         'der Daz-Bibliothek und jeder Steuerregler <X>_figure_ctrl_Character (G9charaktere, 18.09.2026). Wer Amala lädt und Amala auf 0 zieht, hat die '
         'Grundfigur mit Amalas Haut — gewollt. Mesh to 3D und 2D3D Kleider wählen die Grundfigur mit der Option basis (feminine | masculine | neutral); '
         'gespeicherte Modelle (data/models/*.json, quelle genesis9) stehen hinter den Katalogeinträgen.'),
        ('Körperregler setzen',
         'Setzt einen Regler der Figur; die Stellung gilt für Bau, Render, Note und Export der Runde.',
         'rezept',
         "m.koerper_regler('body_bs_WaistWidth', 0.3)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept'), (D + 'kleidermodellbau.py', 'Kleidermodellbau'),
          (G + 'formung.py', 'G9formung')],
         'Signatur koerper_regler(name, wert); name ist eine Kanal-ID aus der Reglerliste (auch eigen:…, hb:…). Der Aufruf speichert nur den Wert; '
         'begrenzt wird erst beim Bau (G9formung.aus_abfrage), unbekannte Namen verschwinden stumm. Seit 01.10.2026 legt Kleidermodellbau die Regler des '
         'Modells über die Stellung des Auftrags (job.stellung()); davor erreichte koerper_regler den Bau nie (engine2d3dkleider.md). Von Hand '
         'erlaubt; die Prüf-KI darf es nicht (Begutachtungskritik.VERBOTEN), die Automatik schreibt es nur bei Option iterationen.form = an (Regel unten).'),
        ('Mehrere Körperregler setzen',
         'Wie koerper_regler, mehrere auf einmal als Schlüsselwörter.',
         'rezept',
         'm.koerper_regler_setzen(body_bs_WaistWidth=0.3, body_bs_CalvesSize=-0.2)',
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept')],
         'Schlüsselwörter müssen Python-Namen sein: Kanäle mit : oder - (eigen:ort_bauch, …-0x…) und mit Leerzeichen gehen nur über koerper_regler. '
         'G9rezept lässt Schlüsselwörter mit Literalen zu, **argumente nicht. Das Beispiel im Docstring (FBMHeavy, PBMBellySize) nicht blind übernehmen: '
         'die echten IDs stehen in der Reglerliste (nicht gegen die Bibliothek geprüft). Prüf-KI: verboten.'),
        ('Körper am Ort nachformen',
         'Formt den Körper örtlich nach, wo die Regler nicht reichen: Kugel um eine Landmarke, Band × Sektor, Welle — als Eigenmorph, gespiegelt.',
         'rezept',
         "m.koerper_ort('bauch2', {'landmarke': 'bauch', 'radius_cm': 8}, weg_cm=1.5, richtung='haut', spiegeln=True, wert=1.0)\n"
         "m.koerper_ort('huefte2', {'band': (0.45, 0.6), 'sektor': (-40, 40)}, weg_cm=1.0)",
         [(G + 'modellkoerper.py', 'ModellKoerperMixin'), (G + 'koerpermorph.py', 'G9koerpermorph'), (G + 'ortsmorph.py', 'G9ortsmorph'),
          (G + 'eigenmorphe.py', 'G9eigenmorphe')],
         "Signatur koerper_ort(name, ort, weg_cm=1.5, richtung='haut', spiegeln=True, wert=1.0). ort ist ein Wörterbuch: {'landmarke': Name, 'radius_cm': r} | "
         "{'band': (von, bis)} (Höhenanteil, 0 Füße … 1 Scheitel) | {'sektor': (a°, b°)} (0 vorn, positiv links, 180 hinten) | {'kugel': [x, y, z], "
         "'radius_cm': r} (Meter, Y oben, Füße auf 0) | {'welle': {'laenge_cm', 'richtung': 'laengs'|'quer'}}; Band, Sektor, Kugel und Welle multiplizieren sich. "
         'Landmarken (G9ortsmorph.landmarken()): scheitel, stirn, nacken, schlaefe_l/_r, ohr_l/_r, kinn, brust, ruecken, bauch, taille_l/_r, po, huefte_l/_r, '
         "schulter_l/_r, knie_l/_r, wade_l/_r, ellbogen_l/_r. richtung 'haut' = Normale des nächsten Hautpunkts der Grundfigur, sonst aussen | innen | oben | "
         'unten | vorn | hinten | [x, y, z]. Ergebnis ist der Eigenmorph eigen:ort_<name>, stellbar −2…2 (negativ = nach innen). Gemessen 30.09.2026 '
         '(ortsmorphe.md): „Bauch“ bewegt 220 Punkte um 22,5 mm bei Wert 1,5 und weg 1,5 cm; die Landmarken rechnet der erste Aufruf mit landmarke je '
         'Prozess einmal (0,7 s). koerper_ort steht nicht in Begutachtungskritik.VERBOTEN, obwohl deren Docstring Körperregler der Automatik zuweist.'),
        ('Feste Ortsregler „Nachformung (Ort)“',
         'Zehn fertige Ortsregler am Körper — ohne eigenen Bau stellbar.',
         'rezept',
         "m.koerper_regler('eigen:ort_bauch', 1.0)",
         [(G + 'koerperstandardmorphe.py', 'G9koerperstandardmorphe'), (G + 'eigenmorphe.py', 'G9eigenmorphe'), (G + 'koerpermorph.py', 'G9koerpermorph')],
         'Namen: eigen:ort_ + bauch, po, brust, schultern, taille, huefte, oberschenkel, waden, kinn, ruecken (G9koerperstandardmorphe.KATALOG: Landmarke, '
         'Radius 4–14 cm, Weg 0,8–1,5 cm). Bereich „Nachformung (Ort)“ im Körper-Reiter; Wert −2…2, negativ nach innen. Sie bauen sich beim ersten Zug '
         '(G9eigenmorphe.vorhanden → sicherstellen), der erste Zug kostet also die Rechnung (nicht gemessen). IterationKoerper nimmt eigen:ort_waden, '
         'eigen:ort_oberschenkel und eigen:ort_taille als zweite Wahl, wenn body_bs_CalvesSize, body_bs_MassThighs und body_bs_WaistWidth am Anschlag stehen.'),
        ('Körper-Hülle (Umriss der Fotos)',
         'Schiebt den Körper nach außen bis an den Umriss der Fotos — nur dort, wo im Foto Haut zu sehen ist.',
         'rezept',
         "m.koerper_huelle('huelle_rumpf', staerke=0.5, von=0.55, bis=0.72)",
         [(G + 'modellkoerper.py', 'ModellKoerperMixin'), (G + 'huellenmorph.py', 'G9huellenmorph'), (G + 'koerpermorph.py', 'G9koerpermorph'),
          (G + 'eigenmorphe.py', 'G9eigenmorphe'), (G + 'rezeptumgebung.py', 'Rezeptumgebung')],
         "Signatur koerper_huelle(name='huelle', staerke=0.5, von=0.0, bis=1.0, wert=1.0). Braucht die Runde (Rezeptumgebung mit Sichtkörper und Hautbändern); "
         'ohne sie ValueError „braucht den Sichtkörper der Vorlagen“. Nur hinaus und nur, wo das Körperband im Foto unbedeckt ist, sonst wüchse der Körper in '
         'den Mantel. Eigenmorph eigen:ort_<name>_<Auftragskürzel>. Die Automatik setzt es erst als dritte Stufe (Rumpf, Band 0,55–0,72, Stärke 0,5, +0,25 je '
         'Runde bis 1,5), wenn Genesis-Regler und Ortsregler am Anschlag stehen und das Foto breiter ist; an den Beinen nie — die Achse liegt in der Lücke '
         'zwischen den Beinen (01.10.2026). Wirkung gemessen: Körperpunkte 0,25–0,30 m unter dem Scheitel bis 15,6 mm (Schultern), darüber nichts '
         '(Gesichtsvorrat, 01.10.2026). Prüf-KI: verboten.'),
        ('Freies Morph-Formular (Körper)',
         'Baut einen Ortsmorph am Körper über den Server — dieselbe Rechnung wie koerper_ort, dazu die Landmarkenliste.',
         'api',
         'POST /api/character/genesis9-figur/morph/   {name, ort: {band, sektor, landmarke, radius_cm, kugel, welle}, richtung, weg_cm, spiegeln}\n'
         'GET /api/character/genesis9-figur/landmarken/',
         [(A + 'g9morphformular.py', 'G9morphformularapi'), (G + 'koerpermorph.py', 'G9koerpermorph'), (G + 'ortsmorph.py', 'G9ortsmorph'),
          (G + 'eigenmorphe.py', 'G9eigenmorphe')],
         "Antwort {regler: {name: 'eigen:ort_<name>', min −2, max 2, bereich 'ort'}, brief, form}; 400 bei „name fehlt“ und „ort fehlt“. Eingaben werden "
         'begrenzt (weg_cm −20…20, radius_cm 0,5…60, weich 0,01…0,5), Landmarken nur aus der Liste des GET. Der Name wird Kennung (a–z, 0–9, _; ä → ae). '
         'Der Browser hängt den Regler sofort an und stellt ihn auf 1 (genesis9koerpermorphformular.js). Jeder POST schreibt eine Datei neben die '
         'Bibliothek (3DObjects/models/Genesis9/eigenmorphe/) — nur nach Ansage.'),
        ('HumanBody-Morphe auf Genesis (hb:…)',
         'Stellt einen der 204 HumanBody-Regler (MB-Lab) als Morph auf dem Genesis-Körper — Brust, Taille, Nase und mehr, wo Daz ohne Kaufpakete keinen Einzelregler hat.',
         'rezept',
         "m.koerper_regler('hb:Torso_BreastPosZ', 0.3)",
         [(G + 'hbmorphe.py', 'G9hbmorphe'), (G + 'formung.py', 'G9formung'), (D + 'hbmorpheaufgenesis.py', 'Hbmorpheaufgenesis')],
         'Reglername hb:<HumanBody-Regler>, ZWEISEITIG −1…1 mit eigenen Deltas je Richtung (plus für > 0, minus für < 0). 204 Regler: 110 Gesicht, ≈ 85 Körper, 8 Fantasie, '
         'übertragen auf die 25.182 Käfigpunkte über die Paarung der Grundfiguren; im Bedienfeld „HB-Morphs Körper/Gesicht/Fantasie“ (Bereiche hb_koerper, hb_gesicht, hb_fantasie). '
         '21 Regler mit Skelettwirkung (Body Size, Längen, Winkel, Head Size, Elfenohren) liegen nur als Steckbrief (rig: true) und sind nicht stellbar: ein Punktversatz ohne '
         'Skelett-Nachzug blähte die Anhänge auf (Mund 6,8 → 94 cm bei Body Size −100 %, 20.09.2026, genesis9-inhalte.md). Die genauen Namen aus der Reglerliste nehmen; '
         'Torso_BreastPosZ ist das Beispiel der Klasse, nicht gegen den Bestand geprüft.'),
        ('HumanBody-Morphe bauen',
         'Überträgt alle HumanBody-Regler auf den Genesis-Käfig und schreibt sie in die Ablage — nötig nach einer Änderung der HumanBody-Morphpakete oder der Paarung.',
         'cli',
         'python14\\Scripts\\python.exe HumanBodyWeb\\manage.py hbmorphe_bauen [--nur-veraltet] [--leise]',
         [(D + 'hbmorpheaufgenesis.py', 'Hbmorpheaufgenesis'), (G + 'hbmorphe.py', 'G9hbmorphe')],
         'Schreibt nach Genesis9/ablage/hbmorphe/ (Artefakt, nicht im Git; bestand.json trägt Fassung und Stand) — nur nach Ansage. --nur-veraltet baut nur, wenn der Bestand fehlt oder älter '
         'ist als die HumanBody-Morphs. Dauer: nicht gemessen.'),
        ('Seite: Szene, Genesis-9-Figur',
         'Regler von Hand ziehen und die Wirkung im 3D-Bild sehen; Figur als Modell speichern.',
         'seite',
         '/Charakter/  →  Charakter hinzufügen → Genesis 9  →  Eigenschaften: Bereiche Körper … Füße, „Nachformung (Ort)“ (mit Formular), „Kopf-Eigen“',
         [(A + 'seiten.py', 'Vorlagenseite'), (A + 'g9figur.py', 'G9figur')],
         'Jeder Reglerzug schickt einen POST an …/genesis9-figur/<name>/netz/. „Modell speichern“ schreibt data/models/<Name>.json (quelle genesis9) — '
         'Edgars Daten, nur nach Ansage (szene.md). Die Szene ist für Menschen; Sessions arbeiten über Rezept und API.'),
        ('Wer die Körperregler stellt',
         'Die Form kommt aus dem Schritt „koerper“; die Runden fassen Körper und Gesicht nur bei Option iterationen.form = an an, die Prüf-KI nie.',
         'regel',
         "Option iterationen.form = 'aus' (Vorgabe) | 'an'\n"
         "POST /api/engine2d3dkleider/<id>/einstellungen/   {optionen: {iterationen: {form: 'an'}}}",
         [(P + 'iterationmodell.py', 'IterationModell'), (P + 'iterationkoerper.py', 'IterationKoerper'), (P + 'reglerpruefung.py', 'Reglerpruefung'),
          (D + 'iterationsoptionen.py', 'Iterationsoptionen'), (D + 'begutachtungskritik.py', 'Begutachtungskritik')],
         'Der Schritt „koerper“ fittet die Figur mit Verlustfunktion an das Netz; die Regeln der Runden schoben die Beine von „.51“ 40 Runden lang an den '
         'Anschlag (01.10.2026), deshalb Vorgabe aus (Iterationsoptionen). Mit form = an: IterationKoerper je Band Genesis-Regler (±1), dann Ortsregler (±2), '
         'dann Hülle nur am Rumpf; Schritt = 0,35 × Rest / mm je 1,0; ein Band zählt nur mit Haut im Foto und ab 10 mm Hüllenabstand. Reglerpruefung nimmt einen '
         'Schritt zurück, der den Rest nicht um BESSER_MM (2,0 mm) verkleinert; danach bleibt der Regler für den Auftrag stehen. Die Prüf-KI (pruefki, Vorgabe '
         'aus) darf haltung, haltung_gelenk, koerper_regler, koerper_regler_setzen und koerper_huelle nicht schreiben. Prüfen vor jeder neuen Regel: Messung am '
         'echten Auftrag gegen ein Bild (engine2d3dkleider.md, 01.10.2026).'),
        ('Rumpf so tief wie das Seitenfoto',
         'Brust, Bauch und Rücken nur dort vertiefen, wo der Körper flacher ist als die Seitenansicht der Fotos — als Eigenmorph, im Startrezept der Iteration 0.',
         'rezept',
         "m.koerper_rumpftiefe(name='rumpftiefe', schale_mm=8.0, wert=1.0, bauch_mm=24.0)   # Option iterationen.rumpftiefe (Vorgabe an)",
         [(G + 'rumpftiefe.py', 'G9rumpftiefe')],
         'Korrigiert den Körper, nicht das Hemd: vorn nach vorn, hinten nach hinten, nie negativ. 8 mm Hemd + Haut (schale_mm) passen an Brust und Hüfte; im Bauchfenster (Höhenanteil 0,50–0,64, '
         'Auslauf 0,04) hängt das Hemd frei und bauch_mm 24 rechnet ab. Gemessen an EINEM Auftrag (Sapiens, 06.10.2026): Körper + Hemd minus Foto bei 0,50 / 0,55 / 0,60 / 0,65 der Größe '
         '+19 / +16 / +43 / +14 mm → +3 / +1 / +15 / +5 mm, RMS 19 → 8 mm, Seiten-IoU 0,8457 → 0,8544; die Fensterlage ist nicht an anderen Männern geprüft. Braucht die Runde '
         '(Rezeptumgebung mit Sichtkörper); eine einheitliche Zugabe von 16 oder 24 mm machte die Brust flacher (engine2d3dkleider-iteration0.md).'),
        ('Lippen und Kinn nach dem Seitenfoto',
         'Lippen und Kinn so weit vorn wie im Seitenfoto, bezogen auf Augen und Nasenwurzel — gegen das eingefallene Kinn; Eigenmorph, im Startrezept der Iteration 0.',
         'rezept',
         "m.koerper_gesichtsprofil(name='gesichtsprofil', wert=1.0)   # Option iterationen.gesichtsprofil (Vorgabe an)",
         [(G + 'gesichtsprofil.py', 'G9gesichtsprofil')],
         'Erst ausrichten, dann messen: die erste Fassung (Kante gegen Kante) schob das Kinn vor; die Ausrichtung des Fotos an der oberen Gesichtshälfte (Höhe UND Tiefe, 1,2 mm RMS) machte den Rest '
         'messbar, ein Ausrichtungsfehler über RMS_MAX_M heißt „keine Korrektur". Braucht die Runde mit dem feinen Seitenprofil; ohne Seitenfoto bleibt der Morph leer.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9figur', 'ruft', 'G9reglerplan', 'bereiche(): Antwort von GET …/regler/'),
        ('G9figur', 'ruft', 'G9formung', 'formung(rumpf, eintrag): G9formung.aus_abfrage(regler, drehung)'),
        ('G9figur', 'ruft', 'G9koerpernetz', 'G9koerpernetz(formung, eintrag, …).bauen(): Netz, Skelett, Anhänge'),
        ('G9figur', 'ruft', 'G9antworten', "liefern('koerper', name, rumpf, rechnen): Antwortvorrat je Fingerabdruck der Stellung"),
        ('G9reglerplan', 'ruft', 'G9reglerbereiche', 'bereich(kanal): Bereichsschlüssel nach Daz-region und -group'),
        ('G9reglerplan', 'ruft', 'G9morphablage', 'holen(): alle Kanäle der Daz-Bibliothek'),
        ('G9morphablage', 'ruft', 'G9reglergrenzen', 'anwenden(ablage): einseitige Formregler zweiseitig machen'),
        ('G9formung', 'ruft', 'G9eigenmorphe', 'deltas(name) in _eigen_dazu(): Eigenmorphe auf die Morphpunkte; dateistand() im Fingerabdruck'),
        ('G9formung', 'ruft', 'G9hbmorphe', 'deltas(name, wert): hb:…-Morphe, die Richtung steckt schon drin'),
        ('Hbmorpheaufgenesis', 'ruft', 'G9hbmorphe', 'ablegen(kennung, nummern, plus, minus, steckbrief): Morph je HumanBody-Regler schreiben'),
        ('G9rezept', 'ruft', 'ModellMitKleidern', 'anwenden(): getattr(modell, name)(*args, **kwargs) je Zeile'),
        ('ModellMitKleidern', 'erbt', 'ModellKoerperMixin', 'koerper_ort(), koerper_huelle(), haltung_gelenk() stehen im Mixin'),
        ('ModellKoerperMixin', 'ruft', 'G9koerpermorph', 'bauen(name, form, spiegeln): Ortsmorph als Eigenmorph ablegen'),
        ('ModellKoerperMixin', 'ruft', 'G9huellenmorph', 'deltas(sicht, [punkte], 0, y1, mitte, staerke, von, bis, nur_hinaus=True)'),
        ('ModellKoerperMixin', 'ruft', 'G9eigenmorphe', 'ablegen(name, nummern, deltas, brief): die Hülle als eigen:ort_<name>'),
        ('ModellKoerperMixin', 'ruft', 'Rezeptumgebung', 'sicht() und unbedeckt(): Sichtkörper und Hautbänder der Runde'),
        ('G9koerpermorph', 'ruft', 'G9ortsmorph', 'gewicht(form, punkte, y0, y1, mitte): Band × Sektor × Kugel × Welle'),
        ('G9koerpermorph', 'ruft', 'G9eigenmorphe', 'ablegen(PRAEFIX + name, wahl, delta[wahl], brief)'),
        ('G9koerperstandardmorphe', 'ruft', 'G9koerpermorph', 'bauen(name, form, spiegeln=True): baut den festen Regler beim ersten Zug'),
        ('G9eigenmorphe', 'ruft', 'G9koerperstandardmorphe', 'vorhanden(): sicherstellen(kennung) baut fehlende feste Regler'),
        ('G9morphformularapi', 'ruft', 'G9koerpermorph', 'bauen(name, form, spiegeln): dieselbe Rechnung wie koerper_ort'),
        ('G9morphformularapi', 'ruft', 'G9ortsmorph', 'landmarken(): erlaubte Landmarken des Formulars'),
        ('IterationModell', 'ruft', 'IterationKoerper', 'aufrufe(): Rezeptzeilen aus dem Befund (nur bei form = an)'),
        ('IterationKoerper', 'ruft', 'Reglerpruefung', 'urteil(punkte): FREI, ZURUECK oder GESPERRT'),
        ('Begutachtungskritik', 'ruft', 'G9rezept', 'pruefen(text): jede Zeile der Prüf-KI einzeln'),
    ]
