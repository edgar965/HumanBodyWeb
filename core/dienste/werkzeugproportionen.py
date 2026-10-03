# -*- coding: utf-8 -*-
"""Werkzeugproportionen — Gruppe „Größe, Proportionen und Anpassung an Fotos (Modell aus Bildern)“ des Reiters „Tools“ (03.10.2026).

Schema: `Architektur2d3dwerkzeuge`. Gelesen am 03.10.2026: `G9knochenmatrizen`, `G9proportionen`, `G9proportionsformung`, `G9fotoproportionen`, `G9umrissformung`, `G9koerpergewicht`,
`G9reglerableitung`, `G9formanpassung`, `G9netzpaarung`, `G9zielnetz`, `Bildmodelllauf`, `Bildmodelloptionen`, `Bildmodellanpassung`. Der Weg „Mesh to 3D“ (Netz als Ziel) steht
in der Gruppe „Mesh to 3D“; hier die Maße und der ältere Weg über ein geschätztes SMPL-X-Netz.
"""

__all__ = ['Werkzeugproportionen']


class Werkzeugproportionen:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'proportionen'
    TITEL = 'Größe, Proportionen und Anpassung an Fotos (Modell aus Bildern)'
    EINLEITUNG = (
        'Größe und Proportionen stecken in Knochenkanälen (Skalierung) und in Formreglern. Reihenfolge der Anpassung: 1. Größe und Proportionen, 2. Körpertyp, 3. Bereiche, '
        '4. der Rest als Eigenmorph — so in „Mesh to 3D“ (Stufen 1–3) und im Weg „Modell aus Bildern“ (Schritte ziel, anpassung, rest). Messen heißt: dieselbe Messfunktion am Ziel und am '
        'Modell (G9proportionen), nie zwei Definitionen. Wer eine Zahl nennt, nennt Quelle und Definition.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Größe der Figur',
         'Stellt die Gesamtgröße (Proportion Height) — Knochenskalierung, kein Punktversatz.',
         'rezept',
         "m.koerper_regler('body_bs_ProportionHeight', 0.4)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept'), (G + 'knochenmatrizen.py', 'G9knochenmatrizen'), (G + 'formung.py', 'G9formung')],
         'Proportion Height: Figur +25 %, 65 Fuß- und Zehenknochen −4 %, 36 Hand- und Kopfknochen −10 %; Height +100 % macht 1,70 → 2,10 m, Amala 1,78 m, Fabrice 1,85 m (genesis9.md, 17.09.2026). '
         'Proportion Legs Length schiebt die Füße 23 cm unter den Boden und hebt hip um 22,95 cm: Netz und Skelett werden um G9formung.boden() gehoben. Head Size: head und 37 Gesichtsknochen +50 %, '
         'Hals +25 %; Hand Size: 20 Handknochen +50 %. In Mesh to 3D setzt niemand die Größe von Hand: Option hoehe_cm streckt das Netz nach der ersten Runde auf die Scheitelhöhe (ohne Haar), die '
         'folgenden Runden passen die Regler an. ProportionSmaller/Larger sind für die Anpassung gesperrt (Kinderproportionen, doppelt zu Height). Prüf-KI: koerper_regler verboten.'),
        ('Proportionen messen (19 Maße)',
         'Misst Breiten, Dicken, Tiefen und Kopfmaße an Punktmengen des Käfigs — am Ziel wie am Modell mit derselben Definition.',
         'python',
         'from Genesis9.proportionen import G9proportionen\n'
         'befund = G9proportionen().messen(punkte, gelenke, gueltig=None)   # {schluessel: {m, a, b, lage}} in Metern\n'
         'G9proportionen.in_cm(befund)   # {schluessel: cm}      G9proportionen.katalog()   # [{schluessel, name, ansicht, formbar}]',
         [(G + 'proportionen.py', 'G9proportionen'), (G + 'koerperteile.py', 'G9koerperteile'), (G + 'haut.py', 'G9haut'), (G + 'proportionenbild.py', 'G9proportionenbild')],
         'Schlüssel: kopf_breite, hals_breite, schulter_breite, brust_breite, taille_breite (schmalste Stelle), huefte_breite (breiteste), oberarm_dicke, unterarm_dicke, oberschenkel_dicke, wade_dicke, '
         'brust_tiefe, brust_vorsprung, bauch_tiefe, gesaess_tiefe, kopf_hoehe, augen_abstand, nase_breite, nase_laenge, mund_breite. Gemessen an Punktmengen (Körperteil oder führender Knochen je '
         'Punkt), nicht an der Silhouette: das gepaarte Zielnetz und das Modell haben dieselbe Topologie. 0,05 s je Messung (bildmodell.md, 19.09.2026). Grenzen: der Augenabstand ist nur eine Ansicht '
         '(die Augäpfel sind eigene Figuren); das Zielnetz nie als SMPL-X-Netz messen — dessen Hände hängen im Hüftband (Hüfte 36,3 statt 33,4 cm, ein Artefakt).'),
        ('Proportionen formen (Zielnetz)',
         'Formt das Zielnetz lokal auf vorgegebene Außenmaße, bevor die Regler angepasst werden.',
         'python',
         'from Genesis9.proportionsformung import G9proportionsformung\n'
         "punkte, gelenke, bericht = G9proportionsformung().formen(punkte, gelenke, {'huefte_breite': 0.37}, gueltig=None, runden=None)   # Meter; bericht {schluessel: {vorher, ziel, nachher}}",
         [(G + 'proportionsformung.py', 'G9proportionsformung'), (G + 'proportionen.py', 'G9proportionen'), (D + 'bildmodellzielproportionen.py', 'Bildmodellzielproportionen')],
         'Lokale Skalierung: Faktor Ziel/Ist (0,6…1,6 je Runde) mit Fenster 1 im Band, zwischen den Nachbarmaßen der Kette linear (G9proportionsketten, seit 20.09.2026), 3 Runden: messen, formen, messen. '
         'Der Grund: die Starter Essentials haben für Hüfte, Armdicke und Nase keinen Regler. Im Rezept gibt es nichts Entsprechendes; im Weg „Modell aus Bildern“ steht es als Option proportionen '
         '({schluessel: cm}, nur formbare Maße, 0,5…120 cm) und als Popup auf dem Foto. Nebenwirkung gemessen: Hüfte +3,2 cm zieht den Oberschenkel 14,2 → 14,6; der Restmorph glättet die Nase 4,0 → 4,2 '
         '(Damira: Ziel 37,0 / 9,5 / 4,0 → Modell 36,9 / 9,4 / 4,2).'),
        ('Fotomaße und Umriss formen das Ziel',
         'Misst Maße und den Umriss aus der Silhouette der Hauptbilder und überträgt sie Zeile für Zeile auf das Zielnetz.',
         'python',
         'G9fotoproportionen(bild).messen()   # {schluessel: Anteil der Maskenhöhe}   (Option fotomasse, Vorgabe an)\n'
         'G9umrissformung(teil, dreiecke=None).formen(punkte, gelenke, vorn=(), seite=(), hoehe_m=None)   # → (punkte, gelenke, bericht)   (Option umriss, Vorgabe an)',
         [(G + 'fotoproportionen.py', 'G9fotoproportionen'), (G + 'umrissformung.py', 'G9umrissformung'), (G + 'kaefigumriss.py', 'G9kaefigumriss'), (G + 'umrissprofile.py', 'G9umrissprofile'),
          (D + 'bildmodellfotomasse.py', 'Bildmodellfotomasse'), (D + 'bildmodellumriss.py', 'Bildmodellumriss')],
         'Breitenprofil von vorn/hinten (192 Stufen) und Vorder-/Rückkante von der Seite werden auf den Käfig übertragen, der genauso gemessen wird (orthografisch gerendert, Arme auf die Achse eingeklappt, '
         'laufender Median über 9 Zeilen). Wahrheitsprobe Grundfigur → Ursula mit Ursulas Umriss, Flächenabstand: Rumpf 10,2 → 5,2, Becken 9,9 → 6,0, Oberschenkel 7,5 → 4,6, Unterschenkel 2,9 → 1,3 mm; '
         'Ursula gesamt Fläche 7,85 mm ohne alles → 6,57 mit den 19 Fotomaßen → 6,20 mit Umriss (bildmodell.md, 19.–20.09.2026). Mit Umriss formen die Fotomaße nicht mehr, nur Eingaben. Grenzen: die '
         'YOLO-Maske ist an schmalen Stellen zu breit (Hals +12 % bleibt Rohwert); anliegende Arme machen das Rumpfsegment breiter (Maß entfällt: „Arme anliegend“); Nase, Mund, Brustform nicht aus einer '
         'Frontalsilhouette.'),
        ('Reglerableitung und Anpassung (BVLS)',
         'Findet die Reglerwerte, mit denen der Käfig einem Zielnetz am nächsten kommt: Jacobi-Matrix je Regler, beschränkte kleinste Quadrate, echte Neurechnung zwischen den Durchgängen.',
         'python',
         "from Genesis9.reglerableitung import G9reglerableitung; from Genesis9.formanpassung import G9formanpassung\n"
         "a = G9reglerableitung.holen('charaktere', {'BaseFeminine_figure_ctrl_Character': 1.0}, teil='koerper')   # teil: 'koerper' | 'kopf'\n"
         'erg = G9formanpassung(a, ziel_punkte, gewicht, ziel_gelenke=None, durchgaenge=None, daempfung=None, gelenkgewicht=None, fest=None).anpassen(melder=None)\n'
         "# erg: {regler, x, variablen, verlauf, teile, punkte_rms_mm, gelenke_mm, rest, punkte}     G9reglerableitung.regler('charaktere', teil='kopf')   # Variablen",
         [(G + 'reglerableitung.py', 'G9reglerableitung'), (G + 'formanpassung.py', 'G9formanpassung'), (G + 'formung.py', 'G9formung'), (G + 'restmorph.py', 'G9restmorph')],
         'Sätze: proportionen (19 Proportion…), charaktere (dazu Figur-, Körper- und Kopfregler: 448 Variablen seit 20.09.2026 mit den 289 Gesichtsreglern von „200 Plus“; in Mesh to 3D 158 Körper + 296 Kopf, '
         '27.09.2026), alle (dazu Asymmetrie als Links/Rechts-Paar). teil koerper = alle Bereiche außer kopf und mimik, teil kopf = nur Kopfpunkte mit dem Körperergebnis als Grund (mit_grund). Nicht dabei: '
         'HD-Details, Gelenkkorrekturen, Nippel/Nabel, Mundhöhle, Nägel, Einzelseiten. Ablage ableitung_<schluessel>.npz je (Satz, Teil, Grundstellung, Morphbestand): 130 Regler × 25.182 × 3 float32 = 39 MB, '
         'einmal ≈ 8 s. Dämpfung 0,02 relativ zur EIGENEN Wirkung des Reglers (Spaltenmittel ließ Ursula bei 0,08 statt 1,0 — Height bewegt 40 cm, ein Charakter 6 mm); 3 Durchgänge; Gelenke zählen je 40 '
         'Punkte; Werte unter 0,005 werden 0; Variablen ERSETZEN ihren Grundwert. Gemessen (Ursulas Käfig als Ziel): mit Ursulas Reglern 0,12 mm RMS, ohne sie 4,76 mm (max 18) — das gibt der installierte '
         'Reglersatz für einen fremden Charakter her; Restmorph 0,47 mm.'),
        ('Zielnetz und Paarung (SMPL-X ↔ Genesis)',
         'Bringt ein SMPL-X-Zielnetz (aus den Betas, optional mit FLAME-Kopf) als Verschiebungen auf die 25.182 Käfigpunkte.',
         'python',
         'from Genesis9.zielnetz import G9zielnetz; from Genesis9.netzpaarung import G9netzpaarung\n'
         'ziel = G9zielnetz.aus(betas=None, kopf=None, symmetrisch=True, armwinkel=None)   # .punkte (10475, 3), .gelenke (55, 3), .hoehe()\n'
         'G9netzpaarung.holen().zielpunkte(ziel, hoehe_cm=None)   # Zielpunkte je Käfigpunkt;  .zielgelenke(ziel, hoehe_cm=None)',
         [(G + 'zielnetz.py', 'G9zielnetz'), (G + 'netzpaarung.py', 'G9netzpaarung'), (G + 'koerperteile.py', 'G9koerperteile')],
         'Verschiebungen statt Lagen: Käfig (25.182) und SMPL-X (10.475) sind zwei Anatomien. Die Zuordnung entsteht einmal zwischen den Grundfiguren (12 Nachbarn, gleiches oder Nachbarteil, Normale > 0,3): '
         '23.581 von 25.182 zugeordnet; Ziel je Punkt = Basis + (Ziel − Neutral)[Zuordnung]; Gelenke 19 Paare. Ohne Zuordnung: Augenhöhle, Mundinnenraum; Hände nur zu 42–46 % „voll“. Das Geschlecht der '
         'Grundfigur kommt aus den Betas (Morphzuordnung.geschlecht_schaetzen), nicht aus dem Schulter-Hüft-Verhältnis von MediaPipe (Damira 1,3 galt als männlich).'),
        ('Gewicht und Größe aus Angaben',
         'Stellt Beta 1 des Zielnetzes so, dass das Volumen bei der Zielgröße das angegebene Gewicht ergibt.',
         'python',
         'from Genesis9.koerpergewicht import G9koerpergewicht\n'
         'betas, beleg = G9koerpergewicht.betas_fuer_gewicht(betas, hoehe_cm, gewicht_kg, bauen=None)   # beleg {gewicht_vorher, gewicht_nachher, beta1}',
         [(G + 'koerpergewicht.py', 'G9koerpergewicht'), (G + 'zielnetz.py', 'G9zielnetz'), (D + 'bildmodelloptionen.py', 'Bildmodelloptionen')],
         'Gewicht = Volumen des wasserdichten SMPL-X-Netzes × Dichte; die Dichte 1000 kg/m³ ist eine Vorgabe, keine Messung an der Person. Sekante auf Beta 1 (≈ 10 kg je Einheit, GENAU_KG 0,05, höchstens '
         '12 Schritte). Gemessen (SMPL-X neutral): 1,719 m und 75,4 kg; beta1 −2 / +2 = 56 / 97 kg bei ±3,5 cm Größe. Alter und Tonus haben bei Genesis keinen Regler (kein Age-, kein Fitness-Kanal): sie '
         'werden nur am Modell abgelegt. Eingabe im Weg „Modell aus Bildern“: Option person {alter 0…120, groesse_cm 100…250, gewicht_kg 20…250, tonus 0…100, haar}.'),
        ('Modell aus Bildern (Fotos → Genesis, SMPL-X-Weg)',
         'Legt einen Auftrag aus Fotos an und rechnet sichten, schätzen, Kopf, Zielnetz, Regler, Restmorph, Vorschau, Textur — ein älterer Weg als Mesh to 3D.',
         'api',
         'POST /api/bildmodell/anlegen/   (multipart: name, typ=genesis9, bilder[], optionen?)   → {kennung, url}\n'
         "POST /api/bildmodell/<id>/starten/   {optionen, ab, bis, schritte}   # Schritte: sichtung, schaetzung, kopf, ziel, anpassung, rest, vorschau, textur, speichern\n"
         'GET /api/bildmodell/katalog/   GET /api/bildmodell/<id>/zustand/      Seite: /modell-aus-dateien/ (Reiter „3D“)',
         [(A + 'bildmodell.py', 'Bildmodellendpunkte'), (D + 'bildmodellarbeiter.py', 'Bildmodellarbeiter'), (D + 'bildmodelllauf.py', 'Bildmodelllauf'),
          (D + 'bildmodelloptionen.py', 'Bildmodelloptionen'), (D + 'bildmodellanpassung.py', 'Bildmodellanpassung'), (D + 'bildmodellstart.py', 'Bildmodellstart')],
         'Nur nach Ansage von Edgar (Schätzer und Grafikkarte). Der Lauf ist ein abgelöster Prozess (manage.py bildmodell_fahren <id> --ab <schritt>). Wichtige Optionen (Katalog): weg = schaetzer | '
         'silhouette (Vorgabe: die Bilder formen die Regler, ohne SMPL-X) | silhouette_rein; reglersatz proportionen | charaktere | alle; kopffit an | aus; basis auto | feminine | masculine | keine; daempfung '
         'gering 0,02 (Vorgabe) | mittel 0,1 | stark 0,5; glaettung wenig 3 | mittel 6 | viel 12 Schritte; nebenbilder aus | haende. Kopf: MICA (Vorgabe, ≈ 8 s je Foto nach dem Laden), PyMAF-X FLAME, FaceBuilder '
         '(KeenTools in Blender) oder keiner. Zeit: „Neu berechnen“ ab Zielnetz bei Damira 40 s; GVHMR-Lauf 85 s, Auftrag 92 s (Dance1, 125 Bilder). Ergebnis Damira (SMPLest-X, 6 Hauptbilder, Median, '
         'Feminine, 49 Regler): 5,01 mm RMS, mit Restmorph 0,55 mm (19.09.2026).'),
        ('Regel: Erst prüfen, wer schlecht ist',
         'Bevor man an Reglern dreht: ist es die Anpassung oder das Ziel?',
         'regel',
         '— keine Rezeptzeile: Modell gegen Zielnetz messen (Restmorph, Maße), dann Ziel gegen Foto',
         [(G + 'proportionen.py', 'G9proportionen')],
         'Modell und gepaartes Zielnetz messen gleich (Hüfte 33,4 / 33,4 cm, Restmorph 0,7 mm) — falsche Proportionen sind Proportionen des ZIELS, also des Schätzers (19.09.2026). Der Testfall Ursula misst '
         'deshalb zweierlei: Abstand zum Netz (das Ziel) und zur Referenz (Obergrenze durch die Netzgüte); SMPLest-X schätzt die volle Figur schlank — alle Tiefen zu klein (Brusttiefe −5,2 cm). Der '
         'Silhouettenabgleich hob die IoU (Damira 0,82 → 0,87) und machte die Form schlechter (Ursula roh 9,75 mm, abgeglichen 10,90): Betas gleichen Pose- und Projektionsfehler aus. Kein Fit holt mehr '
         'heraus, als das Netz hat.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9rezept', 'ruft', 'ModellMitKleidern', 'anwenden(): koerper_regler(…) je Zeile'),
        ('G9formung', 'ruft', 'G9knochenmatrizen', 'matrizen(): Skalierung und Verschiebung der Knochen aus den Posenformeln'),
        ('G9proportionsformung', 'ruft', 'G9proportionen', 'messen(punkte, gelenke, gueltig): vorher und nachher je Runde'),
        ('G9proportionen', 'ruft', 'G9koerperteile', 'genesis_punkte(haut): Körperteil je Käfigpunkt'),
        ('G9proportionen', 'ruft', 'G9haut', 'holen(): führender Knochen je Punkt'),
        ('Bildmodellzielproportionen', 'ruft', 'G9proportionsformung', 'formen(punkte, gelenke, ziele, gewicht > 0): vor der Ausgleichung'),
        ('Bildmodellfotomasse', 'ruft', 'G9fotoproportionen', 'messen(): Maße aus der Silhouette je Hauptbild'),
        ('Bildmodellumriss', 'ruft', 'G9umrissformung', 'formen(punkte, gelenke, vorn, seite, hoehe_m): Umriss auf den Käfig'),
        ('G9umrissformung', 'ruft', 'G9kaefigumriss', 'dreiecke(), profil(): der Käfig wird genauso gemessen wie das Foto'),
        ('Bildmodelllauf', 'ruft', 'Bildmodellanpassung', 'Schritte ziel, anpassung, rest, vorschau, speichern'),
        ('Bildmodellanpassung', 'ruft', 'G9zielnetz', 'aus(betas, kopf): Zielnetz aus den Schätzerwerten'),
        ('Bildmodellanpassung', 'ruft', 'G9netzpaarung', 'zielpunkte(), zielgelenke(): Ziel je Käfigpunkt'),
        ('Bildmodellanpassung', 'ruft', 'G9reglerableitung', 'holen(satz, grund, teil): Jacobi-Matrix'),
        ('Bildmodellanpassung', 'ruft', 'G9formanpassung', 'anpassen(): Reglerwerte, RMS je Teil'),
        ('Bildmodellanpassung', 'ruft', 'G9restmorph', 'Rest als Eigenmorph (Schritt rest)'),
        ('Bildmodellanpassung', 'ruft', 'G9koerpergewicht', 'betas_fuer_gewicht(betas, hoehe_cm, gewicht_kg): Option person'),
        ('G9netzpaarung', 'ruft', 'G9zielnetz', 'neutral(): SMPL-X mit allen Parametern 0 als Grundlage der Zuordnung'),
        ('G9formanpassung', 'ruft', 'G9formung', 'G9formung(ableitung.stellung(x)): echte Neurechnung je Durchgang'),
        ('G9formanpassung', 'ruft', 'G9reglerableitung', 'lage(formung): Punkte und Gelenkköpfe der Stellung'),
        ('Bildmodellendpunkte', 'ruft', 'Bildmodellstart', 'starten(job, rumpf): Optionen prüfen, Arbeitsprozess ab einem Schritt'),
        ('Bildmodellendpunkte', 'ruft', 'Bildmodellarbeiter', 'lebt(job) und anhalten(job): Prozess prüfen und beenden'),
        ('Bildmodellstart', 'ruft', 'Bildmodellarbeiter', 'starten(job, ab, bis, schritte)'),
        ('Bildmodellarbeiter', 'ruft', 'Bildmodelllauf', 'bildmodell_fahren: Bildmodelllauf(id).ausfuehren(ab, bis, schritte)'),
        ('Bildmodellendpunkte', 'ruft', 'Bildmodelloptionen', 'pruefen(optionen), katalog()'),
    ]
