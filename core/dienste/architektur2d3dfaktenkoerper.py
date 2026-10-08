# -*- coding: utf-8 -*-
"""Architektur2d3dfaktenkoerper — technische Fakten zu Körper, Segmentierung (Sapiens), Kleidern, Haar, Fotoprojektion, Haltung, Licht und Noten (Hilfe → Architektur → 2D3D, 06.10.2026).

Zweiter Teil der Sammlung neben `Architektur2d3dfaktennetz` (Edgar, 06.10.2026: „möglichst viele technische Details … damit wir später nicht von neuem anfangen und Fehler nicht wiederholen").
Jeder Eintrag steht so in der Regeldatei der Quellspalte (gelesen 06.10.2026): Zahlen wörtlich, „nicht gemessen" und „vermutet" bleiben stehen.

Eintrag: `(bereich, art, thema, befund, quelle)`; `art`: parameter | messung | falle | entscheidung.
"""

__all__ = ['Architektur2d3dfaktenkoerper']


class Architektur2d3dfaktenkoerper:
    I0 = 'engine2d3dkleider-iteration0.md'
    SG = 'engine2d3dkleider-segmentierung.md'
    ED = '2d3DIterationen/Edgar/README.md'
    EINTRAEGE = [
        # ------------------------------------------------------------------ Segmentierung
        ('Segmentierung', 'parameter', 'Sapiens: 28 Klassen, drei Modellgrößen',
         'Goliath-Klassen (sapiens_klassen.py): Background, Apparel, Face_Neck, Hair, Left/Right_Foot, _Hand, _Lower_Arm, _Lower_Leg, _Shoe, _Sock, _Upper_Arm, _Upper_Leg, Lower_Clothing, Torso, Upper_Clothing, '
         'Lower_Lip, Upper_Lip, Lower_Teeth, Upper_Teeth, Tongue. Gewichte: seg 0.3B 1,36 GB (mIoU 76,73 laut Dateiname), 0.6B 2,69 GB (77,77), 1B 4,72 GB (79,94); 0.3B und 0.6B sind NICHT gelaufen; die '
         '2B-Segmentierung ist nicht öffentlich (401). Lizenz CC BY-NC 4.0 (nicht kommerziell). Der Runner legt die Stimmen je KLASSE ab (sapiens_flaechen.npz, Fassung 2) — die Zuordnung ändern braucht keinen neuen Lauf.',
         SG + ', „Aufbau" und „Alle Klassen und Einstellungen"'),
        ('Segmentierung', 'parameter', 'Die zwölf Einstellungen (Gruppe segmentierung)',
         'verwenden (Kleidung), haar (Farbe | Sapiens | beides), modell (0.3b | 0.6b | 1b), schuhe, socken, zubehoer (Apparel), fein: min_stimmen, glaettung, nah_mm, raster, kante, rand. modell, raster, kante und rand '
         'ändern, WAS gerechnet wird (sie stehen im Stand der Ablage; andere Werte → „passt nicht mehr"). Vorgabe verwenden = aus; die Sapiens-Aufträge setzen an (8 von 11 Aufträgen mit Runden).',
         SG + ', „Alle Klassen und Einstellungen"; gezählt 06.10.2026'),
        ('Segmentierung', 'messung', 'Dauer und Güte (Auftrag …20.10.04)',
         'Schritt allein 23 s und 30 s (Modell laden ~7 s, Spitze 5,9 GB GPU); im vollen Lauf …14.10.22 28,0 s. Gesehen 38.509 Flächen (40 %, 16.607 von 37.059 cm²). Silhouetten-IoU Netz ↔ Foto: vorne 0,89, hinten 0,84, '
         'Seite 0,69 — die Seitenansicht eines Netzes, das nur aus dem Vorderfoto kam, passt schlecht; ob eine Ansicht unter IoU 0,7 die Stimmen verschlechtert, ist nicht ausgewertet. Beim ersten Lauf kommen '
         '4,7 GB Gewichte dazu (Download ~6 min bei 11 MB/s, nicht im Auftrag gemessen).',
         SG + ', „Gemessen"'),
        ('Segmentierung', 'messung', 'Wirkung auf die Kleidungsmaske',
         'Mit Option „aus" dieselbe Maske wie im Auftrag (0 von 94.970 Flächen anders); mit „an": Oberteil 8.682 → 13.244 cm² (Saum bei 0,80 m statt 1,00 m), Hose 0 → 2.284 cm² (die Regel hielt die Shorts für Haut), '
         'Socken 597 → 2.746 cm², Zubehör 38 → 150 cm² (Uhr am Handgelenk, y 0,86–0,92 m). Verbinden (Sapiensmaske.verbinden): Stimmen einmal über die Kantennachbarn glätten, ab 4 Pixel Stimmen das stärkste Stück, '
         'ungesehene Flächen dicht (1,5 cm) neben einer gesehenen übernehmen deren Stück, Kopf nie Kleidung, Inseln unter 60 cm² fallen weg. Übernommene Körper (koerper.quelle = uebernehmen) haben keine eigene Maske.',
         SG + ', „Gemessen" und „Aufbau"'),
        ('Segmentierung', 'falle', '„haut" blieb auf den Kleidungsflächen stehen',
         'Die Sapiens-Fassung brach die Regel „Kleidung nur auf ~haut": haut stand auf 85 % der Hosenflächen (6.000 von 7.049), 73 % der Socken, 36 % des Oberteils. Folge: Fotostuecke baute keine Hose. Fix in '
         'Kleidungsmaske.abschliessen (haut & (stueck == 0), Test DieHaut). Messfalle dabei: die Nachbarschaft aus Rohpunkten (UV-Nähte getrennt) ließ den Inselfilter 8.675 Flächen entfernen — die Pipeline lädt über '
         'Meshfigurscan.laden (Punkte zusammengeführt); wer die Maske außerhalb nachrechnet, nimmt dieselbe Klasse.',
         SG + ', „Nicht gemessen / offen"'),
        ('Segmentierung', 'messung', 'Haar aus Sapiens gegen Haar aus Farbe',
         'Sapiens sieht 714 cm² Haar (1.860 Flächen) auf Kopfhöhe (1,53–1,68 m), die Farbmaske 2.039 cm² (5.694 Flächen); nur Farbe 3.879 Flächen mit Median 1,50 m (Hals und Schultern, das „Schulterstück"); IoU 0,316. '
         'Besser ist Sapiens WAHRSCHEINLICH, bewiesen ist es nicht (kein Blick auf das Haar-Objekt, eine Aufnahme); die Vorgabe bleibt „Farbe". Sapiens kann sonst Tiefe (0,3B 1,28 GB … 2B 8,61), Normalen, '
         'Pose mit 308 Punkten und Merkmale — nicht eingebaut, jedes brauchte neue Gewichte.',
         SG + ', „Alle Klassen und Einstellungen"'),
        # ------------------------------------------------------------------ Körper
        ('Körper', 'parameter', 'Die Kette des Körperschritts',
         'erkennung, haar, kleidung, kalibrierung, koerper, gesicht, rest, textur, vorschau, frisur (Engine2d3dKleiderkoerper.KETTE). Gemessen 01.10.2026 (Summe 871,7 s): koerper 217,9 s, textur 210,1, frisur 161,1, '
         'gesicht 152,0, vorschau 40,3, erkennung 37,9, rest 30,8, haar 10,9, kleidung 10,7; Lauf …14.10.22 vom 06.10.2026: 877,0 s. Frühstopp (02.10.2026): hält an, wenn der Verlust über 50 Schritte um < 0,2 % fällt.',
         'Architektur2d3dmessung.KOERPER; Workflowzeiten'),
        ('Körper', 'messung', 'Rumpftiefe: der Bauch folgt dem Seitenfoto, nicht dem Netzvolumen',
         'Körper + Hemd standen in Iteration 0 bei 0,50 / 0,55 / 0,60 / 0,65 der Körpergröße 19 / 16 / 43 / 14 mm tiefer als die Silhouette des Seitenfotos, an der Brust (0,70) 9 mm flacher. Der Hebel ist der Zuschlag von '
         'koerper_rumpftiefe: 8 mm Hemd + Haut (schale_mm) passt an Brust und Hüfte; im Bauchfenster (Höhenanteil 0,50–0,64, glatter Auslauf 0,04, G9rumpftiefe.BAUCH) hängt das Hemd frei, bauch_mm 24. Gemessen '
         '(Körper+Hemd minus Foto, mm): 0,45 −6 → −6; 0,50 +19 → +3; 0,55 +16 → +1; 0,60 +43 → +15; 0,65 +14 → +5; 0,70 −9 → −9; 0,75 +5 → +5; RMS 19 → 8 mm; Seiten-IoU 0,8457 → 0,8544. Einheitlich 16 oder 24 mm '
         'über die ganze Höhe machte die Brust flacher (−19 / −27 mm). Die Fensterlage ist an EINEM Auftrag gemessen; ein Mann mit anderer Hemdlänge hat sie vielleicht woanders.',
         I0 + ', „Der Bauch (06.10.2026)"'),
        ('Körper', 'falle', 'Hülle, Ring, Ortsmorph und Passform bewegen das Hemd am Bauch nicht',
         'Das Hemd liegt dort 4–10 mm an der Haut (kleinster 3D-Abstand zum Körperpunkt); die z-Lücken aus Schichtmessungen am groben Käfig waren Messartefakte (der Körper hat dort nur ~1 cm Punktabstand). '
         'Das Hemd an die Silhouette zu zwingen (kleid_huelle) machte es weit und faltig; es allein enger zu legen ließ die Brust flach. Offen: der Hemdsaum bei 0,60 der Größe steht 43 mm tiefer als das Foto.',
         I0 + ', „Die Rumpftiefe korrigiert den Körper, nicht das Hemd"'),
        ('Körper', 'entscheidung', 'Erst ausrichten, dann messen (Gesichtsprofil)',
         'Eine Messung, deren Bezug schwankt, taugt nicht als Maß: die absolute Lage der Seitensilhouette war um 15–40 mm unsicher, am Gesicht schwankte der Fehlbetrag mit dem Bezugsrahmen um 10–20 mm. Die erste Fassung '
         '(Kante gegen Kante) schob das Kinn vor; erst die Ausrichtung des Fotos an der oberen Gesichtshälfte (Höhe UND Tiefe, 1,2 mm RMS) machte den Rest messbar. Dicken sind vom Bezug unabhängig, Lagen nicht; ein '
         'Ausrichtungsfehler über RMS_MAX_M heißt „keine Korrektur".',
         I0 + ', „Iteration 0 ist eine Runde wie jede andere"'),
        ('Körper', 'parameter', 'Netztiefe (Option koerper.tiefe, Vorgabe aus)',
         'Das Netz kann am Bauch tiefer sein als die Silhouette im Seitenfoto (Testauftrag: bei 0,50 und 0,55 der Körpergröße 33 und 29 mm); mit „an" wird die Tiefe des Rumpfs höchstens so groß wie im Seitenfoto '
         '(Faktoren 0,83–0,95 am Sapiens-Auftrag). Hemd im Band 0,50–0,80: +20 mm → +3 mm gegen das Foto (05.10.2026).',
         'engine2d3dkleiderkoerperoptionen.py (Hinweis); ' + I0),
        # ------------------------------------------------------------------ Kleider und Haar
        ('Kleiderstücke', 'messung', 'Kleiderstuecknote: Fotostücke gegen die Bibliotheksstücke',
         'Abweichung = 1 − F (Deckung, Treue, F-Wert gegen die Maskenflächen, Aufbau, Körper gegen Haut, Bibliotheks-Anker): Oberteil 0,085, Hose 0,264, Socken 0,210 gegen Hemd 0,279 / Shorts 0,610 / Socken 0,261 '
         '(04.10.2026). Diagnose: kein systematischer Versatz, darum keine Weite-Korrektur. Dauer des Schritts 47,2 s mit gemerkten Stücken, im vollen Lauf …14.10.22 297,9 s (bauen 248 s, messen 50 s).',
         'CLAUDE.md, Tabelle engine2d3dkleider-kleiderstuecke.md; Workflowzeiten'),
        ('Kleiderstücke', 'entscheidung', 'Oberteil: Genesis-Hemd statt Fotostück; GarmentCode-Hemden sind Crop-Tops',
         'Option koerper.oberteil = bibliothek (Vorgabe): das Genesis-Hemd mit Saum, Ausschnitt und Ärmelabschlüssen in der mittleren Farbe des Fotostücks (hemdfarbe). Hose und Socken bleiben Fotostücke '
         '(Fotohuelle schließt Hosenbund und Socken; Socke höchstens 8 mm vom Bein, Bund vorher +27 mm). Zwei Fallen des Standmodells: ModellMitKleidern().kleid_nur lässt das Standardhemd stehen (sein Regler fehlt, die '
         'Bibliothek zählt es als 1) und ein frisches Modell trägt das Standardhaar kin_hair (421.846 Flächen).',
         'Standvorabkleider (Docstring); CLAUDE.md, Tabelle engine2d3dkleider-kleiderstuecke.md'),
        ('Haar', 'parameter', 'Herrenhaar: Röhren statt Bänder, Haarlinie am Ohrknochen',
         'Option iterationen.haarumbau = herren (Vorgabe): Röhren, nicht Bänder — ein Band ist von der Kante gesehen unsichtbar (seitlich schwarze Ränder im Mitsuba-Render). HELL 1,11 gleicht aus, dass die Röhren im Mittel '
         '0,90 so hell rendern wie ihre Farbe (an EINEM Auftrag gemessen). Wuchs, Spreizung (0,70) und Streifenbreite sind Annahmen; gemessen ist nur die Wirkung am Foto. Haarlinie liest den Ohrknochen aus den '
         'Hautgewichten (l_ear / r_ear), keine festen Winkel. Log Sapiens 4: 26.275 Strähnen (472.950 Dreiecke) in 5 Gruppen, Haarkappe 1.401 Dreiecke, Dicke im Mittel 6,6 mm. eigen_Herrenhaar als Bibliotheksstück: '
         'nicht im Browser geladen.',
         I0 + ', „Herrenhaar"; auftrag.log von 2026.10.06.00.33.38'),
        ('Haar', 'falle', 'Haar als Textur auf dem Kopf (die „Kappe")',
         'figur.kopfhaut = haar malt die Haarfarbe des Netzes auf die Kopfhaut — das ist die Kappe, die Edgar sah (05.10.2026: „die Haare sind bei Sapiens noch keine Objekte"). In 2D3D Kleider ist die Vorgabe „haut"; '
         'Aufträge mit gespeichertem „haar" behalten es. Die Haarkappe (Haarkappe) legt EIN Haarteil in EINER Farbe über den Haarbereich, Dicke aus der Hülle des Fotohaars; die Haarklemme schneidet die Frisur an die '
         'Hülle des Fotohaars (die Wahl nahm eine Tolle, oben vorn +39 mm).',
         'engine2d3dkleideroptionen.py; CLAUDE.md, Tabelle engine2d3dkleider-kleiderstuecke.md'),
        # ------------------------------------------------------------------ Fotoprojektion
        ('Fotoprojektion und Textur', 'falle', 'Das Seitenfoto zählte nie für die Farbe (Schulterfleck, Hosenflanke)',
         'ergebnis.fotopruefung.ausgelassen führte seite.jpg („Kleidung weicht ab, Bandabstand 2,17 / 1,77 > 1,00"); Iterationsreferenz.laden setzt dann farbe=False, die Fotoprojektion lief nur mit Vorder- und Rückfoto '
         '(Winkel [0, 180]). Ärmel und Flanken (Normale ±x, 90° zu beiden Fotos) hatten keinen Fototreffer — Gewicht (n·v)^4 ≈ 0 —, im Atlas fächerförmige Strähnen, im Render ein dunkler Oval-Fleck mit hellem Rand. '
         'Nach der Fotoprüfungs-Korrektur: Fleck weg. Die Hosenflanke war im FOTO schon 1,78 / 1,62-mal so hell wie die Mitte (Satin); die Behauptung „im Render etwas heller als Fehler" war falsch gesehen. '
         'Noten dabei nicht vergleichbar: Iteration 0 0,3633 → 0,3894, Iteration 1 0,3516 → 0,3658 (die Farbe mittelt über drei statt zwei Ansichten).',
         I0 + ', „Das Seitenfoto zählte nie für die Farbe"'),
        ('Fotoprojektion und Textur', 'falle', 'Haut in der Stücktextur (Hose, Ärmel)',
         'Die um TOLERANZ erweiterte Teilmaske nimmt Haut neben dem Saum mit — im Render ein hautfarbener Keil am Hosensaum. Kleidhautfilter lässt Foto-Pixel weg, deren FARBTON (Lab a, b, ohne Helligkeit) näher an der '
         'Haut liegt als am Stück; in RGB war es falsch (der Glanz des dunklen Satins lag näher an der Haut als an seinem Mittel; am Bild gesehen, nicht an der Zahl). Im Seitenfoto schaltete sich der Filter ab (Maske der Hose '
         'zu 45 % Hand, Abstand der Farbtöne 2,1 statt 19,5 vorn) — Kleidhautfilter.reinster nimmt den Farbton aus der Ansicht mit dem größten Abstand zur Haut. Fotoprojektion(figurrand=2): die Randpixel der Freistellung '
         'sind Mischfarben mit der weißen Wand; AUSSCHLUSS_RAND 1 (bilineare Abtastung mischt die Haut daneben mit). Der Farbabstand Foto ↔ Render der Hose taugt als Maß nicht (das Foto-Mittel enthält dieselbe Haut).',
         I0 + ', „Die Hose (06.10.2026, zweiter Gang)" und „Das Seitenfoto zählte nie für die Farbe"'),
        ('Fotoprojektion und Textur', 'parameter', 'Hände, Nähte, Licht der Fotohaut',
         'Hände bekommen nie Fotofarbe (die Pose des Fotos liegt nie genau auf der Hand der Figur); der TON der Fotohaut wird auf die gebackene Kachel übertragen statt sie zu überblenden (Hautmischung, Hautproben). '
         'Die Kopfkachel (1001) bleibt die gebackene — am Mund und Kinn sind ihre Flecken im Kopfbild zu sehen. Fotolicht: sieben Zahlen je Ansicht, keine Intrinsic-Zerlegung, Schalter iterationen.licht; ob es die '
         'Textur verbessert, entscheidet das Bild, eine Kennzahl dafür gibt es nicht. Ungesehenes trägt in Kleid und Haar das Fotomittel SEINER Höhe (hoehenprofil=True), Haut nicht.',
         I0 + ', „Hände und Nähte" und „Licht"'),
        ('Fotoprojektion und Textur', 'falle', 'Fototextur und Tönung multiplizierten sich',
         'Das Startrezept färbt das Hemd auf Grau um und tönt es dunkel (Bild × 2 × Tönung); legte die Automatik danach eine Fototextur darüber, multiplizierte sich die Fotofarbe mit dieser Tönung: Hemd im Render 0,62 '
         'der Fotohelligkeit (Iteration 0: 1,04), Gesamtnote 0,5149 gegen 0,364. kleid_fototextur stellt die Tönung jetzt auf neutral (NEUTRALE_TOENUNG #808080): Hemd 1,10 der Fotohelligkeit, Note 0,3539. '
         'Rundenauswahl.PFLICHT_HAAR (der Bart) schlägt die Note: die schlechtere Runde war nur deshalb „beste" — Absicht.',
         I0 + ', „Fototextur und Tönung"'),
        # ------------------------------------------------------------------ Haltung und Kollision
        ('Haltung und Kollision', 'messung', 'Orange Linien an den Armlöchern: Geometrie, nicht Textur',
         'An jeder Ärmelecke der Seitenansicht ein 1 Pixel breiter orange Strich (R − B ≈ 60). Z-Puffer über die gehäuteten Teile (1 mm): die Haut steht bis 1,3 mm VOR dem Hemd (48 Pixel). Ursache: die Kollision (3 mm) '
         'rechnet in der A-Pose, G9haltungshaut häutet danach Körper und Hemd mit ihren Gewichten in die Haltung — am Armloch weichen beide um Millimeter ab (Hemdpunkte unter 3 mm über der Haut: 1.106 von 8.533, 172 darunter, '
         'tiefster −8,9 mm). G9haltungsabstand: 3.064 Hemdpunkte bewegt (die meisten unter 1 mm), 174 über 5 mm, alle am Armloch (y 1,21–1,28 m), größter Hub 12,3 mm; danach 0 Pixel Haut vor dem Hemd. '
         'Das Körperteil einer Runde trägt keine Normalen (der erste Anlauf lief ins Leere) — sie kommen aus den Dreiecken. TIEFE_MAX 2 cm. Eine sehr blasse warme Linie am Vorderrand bleibt (R − B 5–6, Ursache nicht bestimmt).',
         I0 + ', „Orange Linien an den Armlöchern"'),
        ('Haltung und Kollision', 'entscheidung', 'Gebaut wird in der A-Pose, gehäutet wird in die Haltung der Fotos',
         'Die Fotos zeigen hängende Arme, das Modell steht in der A-Pose (Oberarme 43° zur Senkrechten); Edgar, 30.09.2026: „Das Modell soll in A-Pose angezeigt werden". Bühne, GLB und Standmodell bleiben dort; für '
         'Render, Note, Befund und Fotoprojektion häutet G9haltungshaut jedes Teil mit SEINER Haut (D_b = M_b(Stellung + Drehung) · M_b(Stellung)⁻¹, p\' = Σ wᵢ · D_bᵢ · p). Früher ging die Haltung in den Bau: die '
         'Arme hingen durch die Ärmel, und die Note verglich A-Pose gegen hängende Arme (Umriss-IoU vorn/hinten um 0,6). Ältere Messung: 55° Armhaltung stellte die Hand IM Rumpf und die Note fand das „besser" — '
         'Silhouettenbetrug.',
         'Genesis9/haltungshaut.py (Docstring); engine2d3dkleider.md'),
        ('Haltung und Kollision', 'parameter', 'G9kollision: Kleidung aus der Haut drücken',
         'ABSTAND 0,003 m (3 mm), NACHBARN 6, zwei Durchgänge; je Kleidpunkt der nächste Körperpunkt (cKDTree) und die Tiefe entlang seiner Normale, Hub über die 6 nächsten Kleidpunkte gemittelt. Befund vom 17.09.2026 an '
         'Base Feminine: Bikini 303 Punkte innen (6,8 %), tiefste 2,4 mm — Daz liefert jedem Kleidungsstück einen Smoothing Modifier mit Kollision. G9stoff.entscheiden: dynamisch nur mit dForce-Modifikator UND p90 des '
         'Hautabstands ≥ ENG_M 5 cm (ENG_ANTEIL 90 %); enge Stücke werden gehäutet, nicht simuliert; starre (STARR: eigen_foto_*, Uhr, Hut, Brille, Gürtel, Ohrstecker, Armband, Manschette, Kette) nie.',
         'Genesis9/kollision.py; Genesis9/stoff.py'),
        # ------------------------------------------------------------------ Licht, Render, Noten
        ('Licht und Render', 'messung', 'Der Render ist nicht insgesamt dunkler, sondern je Ansicht',
         'Render geteilt durch Foto (ganze Figur): vorn 1,067, hinten 0,951, Seite 0,858. Das Licht des Renders steht fest in der Welt (Mitsubaszene: Himmel 0,8 plus Richtlicht von oben vorn links), die Seitenansicht von rechts '
         'liegt im Schatten; das Seitenfoto ist heller belichtet (Ganzfigur 90,6 gegen 77,0 und 77,9). Belichtung (Option iterationen.belichtung, Vorgabe an): je Ansicht ein Faktor Foto ÷ Render in linearem Licht, '
         'geteilt durch das GEOMETRISCHE MITTEL aller (Mittel 1), begrenzt auf 0,7–1,4, nur Ansichten mit Farbe; wirkt vor Note, Befund und Tafel. Danach 0,955 / 0,952 / 0,960; Farbfehler der Seite 0,0582 → 0,0322. '
         'Bleibt: rund 4–5 % im Mittel (Haut 0,93–0,94, Hose 0,93, Haar 0,90–0,93, Brauen 0,73, Uhr 0,60), Ursache nicht gemessen (vermutet: mittlere Schattierung des Renderlichts gegen die Albedo aus dem Foto).',
         I0 + ', „Render insgesamt dunkler"'),
        ('Licht und Render', 'entscheidung', 'Renderer: Mitsuba oder pyrender',
         'Einstellungen → 2D3D Kleider (kleider2d3d_renderer). Mitsuba 3 traf die Fotos besser (Abweichung 1,725 gegen 1,820; 72 gegen 62 s derselben Runde); fehlt Mitsuba oder CUDA, fällt es auf pyrender zurück '
         '(Warnung im Log). pyrender macht Stranghaar unsichtbar. Noten zweier Renderer sind nicht vergleichbar. Die Tafel zeigt, wonach benotet wird („Licht x0.80").',
         'workflowrundebau.py (Baum Renderer); Hilfetext der Einstellung'),
        ('Noten und Auswahl', 'parameter', 'Die Gesamtnote und die Rundenauswahl',
         'gesamt = foto + farbe_teile + gesicht + haar. foto = (1 − IoU des Umrisses) + Farbabweichung der ganzen Figur (Raster 8 × 12 je 128 × 192); farbe_teile = mittlerer Farbfehler unter der Maske jedes Teils; '
         'gesicht = mittlere Abweichung |Foto ÷ Render − 1| der Gesichtsmaße; haar = 0,25 × (1 − IoU des Kopfhaars im Kopfausschnitt) — das Gewicht ist gesetzt, nicht gemessen. Die Netznote zählt NICHT '
         '(der Körper lag in jeder Runde von „.51" 87,9 mm neben dem Netz, Pose). Besser = kleiner als die beste − 0,002 (Toleranz), oder eine Pflichtzeile, oder ein reiner Farbschritt, der nicht schlechter ist (+ 0,0005). '
         'Ein Umbau darf bis zu 3 Runden als Probe laufen.',
         'Gesamtnote (Docstring); workflowrundebau.py (Baum Rundenauswahl)'),
        ('Noten und Auswahl', 'falle', 'Die Note sieht Verformungen nicht, und Noten sind nicht über Änderungen vergleichbar',
         'Iteration 1 verformte das Hemd (die Hülle zog Ärmel, Schultern, Kragen und Saum auseinander: Hüllenabstand je Band 7 / 10 / 50 / 52 / 12 mm), und die Note blieb gleich (Iteration 0 0,3637, mit verformender Hülle '
         '0,3641): ein Umbau an Kleidern gehört neben die Noten auch ins Bild und in Einzelproben. Jetzt messen und ziehen nur Vorder- und Rückseite (Befundmessung.HUELLE_TIEFE_COS, kleid_huelle(…, tiefe=True)). Ergebnis '
         '(Kopie …00.33.38): Iteration 0 0,3624, Iteration 1 0,3522; Hemd-Farbabstand 0,0248 → 0,0103. Noten vor und nach einer Änderung an Farbquellen oder Belichtung sind nicht gleich zu lesen (die Rundenauswahl '
         'vergleicht die erste neue Runde eines alten Auftrags mit einer anders benoteten besten): Iteration 0 0,3893 → 0,3885, Iteration 1 0,3657 → 0,3577.',
         I0 + ', „Iteration 1 verformte das Hemd" und „Render insgesamt dunkler"'),
        # ------------------------------------------------------------------ Standmodell und Ablagen
        ('Standmodell und Ablagen', 'falle', 'Weißes Hemd im Standmodell: die Fassung kannte die Atlanten nicht',
         'stand_ab281e7b38b5.glb (00:39) trug die vier Hemdtexturen als graue Grundtextur (Mittel 191, ohne Foto, ohne Saumfarbe); der heutige Bau desselben Modells hat Foto (82/78/76). Die Datei blieb „aktuell". Jetzt '
         'gehören die Atlanten des Auftrags (kleidtexturen/*foto_<kürzel>_f*.png: Name, Größe, Zeit) zur Fassung (Engine2d3dKleiderstandmodell._fotoschichten, nur wenn es welche gibt); Sapiens 4 neu gebaut '
         '(stand_790c726f561a.glb, 40 s). Ursache des weißen Stands von damals nicht bestimmt. Weiß geblieben, weil nie eine Fotoschicht lief: Sapiens 1 und 2. Das Standmodell baut der Lauf am Ende (Modus „Begutachtung") '
         'und auf Bestellung der Bühne: 46 MB, 26–30 s (Auftrag …51), Fassung = Fingerabdruck aus Stellung, Modell der Runde, Kacheln, Schreiberfassung (und Atlanten).',
         I0 + ', „Weißes Hemd im Standmodell"; engine2d3dkleider.md'),
        ('Standmodell und Ablagen', 'falle', 'Probeläufe mit echter Kennung überschreiben Atlanten und Morphe',
         'runde_trocken.py / fleck_probe.py mit der Kennung eines echten Auftrags schreiben kleidtexturen/*foto_<kürzel>_f1.* dieses Auftrags (Sapiens 4 um 09:57, im JSON „ansichten: [0, 180]" — der Stand vor der Korrektur '
         'des Seitenfotos). Vorher sichern und zurückspielen oder eine eigene Kopie nehmen. Die Zellenmorphe der Automatik (kleidmorphe/<Stück>__netz_b<i>s<j>_f1.npz) trugen keine Auftragskennung und wurden von jedem Lauf überschrieben; seit 06.10.2026 trägt ein NEUER das Kürzel (…_<kürzel>_f1.npz), die alten bleiben unter dem alten Namen (im Code geändert, nicht gelaufen).',
         I0 + ', „Meine Probeläufe überschreiben Atlanten"; gemessen 06.10.2026'),
        # ------------------------------------------------------------------ Nachbesserung durch eine KI
        ('Nachbesserung', 'messung', 'Kosten und Zeit der KI-Aufrufe (gemessen 05.10.2026)',
         'claude -p, Mini-Prompt: unverschlankt 14,3 s, 0,29 USD, 41 Werkzeuge (auch MCP: Browser, Docs); mit den Optionen von Agentenaufruf (--tools Read, dontAsk, ohne MCP/Skills) 4,9 s, 0,073 USD. '
         'Eine ganze Iteration als Trockenlauf gegen „Randy" (Prompt 28.598 Zeichen, 8 Vorlagen, Tafel, Kopf): 65,5 s, 11 Züge, 0,42 USD. Probebild lesen: Qwen 3.8 27B (Q4_K_M) lokal 28 s inklusive Laden, '
         'Claude Sonnet 5.5 Stufe gering 4,9 s / 0,04 USD, Nemotron 3 Nano Omni 30B-A3B (kostenlos) Stufe gering 56 s, 2.627 Token. Eine Iteration als Trockenlauf mit Qwen (Prompt 15.712 Token, Fenster 32.768): 53 s, '
         '29 Rezeptzeilen mit 14 Funktionen.',
         ED + ', „Gemessen (05.10.2026)"'),
        ('Nachbesserung', 'falle', 'Die erste echte KI-Iteration erfand Namen',
         'Sapiens 2, Nemotron „extra hoch" (04.10.2026 23:38–23:46): die KI schrieb kleid_nur(\'oberteil\') und FBMHeavy — erfundene Namen; die Ausgangsrunde trug die Fotostücke nicht. Daraus: Katalog „Was es gibt" '
         '(Rezeptkatalog), Startrezept, keine Ausgangsrunde, Namenprüfung am Server (pruefen_bestand, 400 bei erfundenem Namen). Ollama schneidet ein zu kleines Fenster STILL vorn ab — Ollamaaufruf meldet es '
         '(prompt_eval_count ≥ num_ctx). communicate(eingabe) nimmt die Eingabe nur beim ersten Aufruf. Trockenlauf einer echten Runde aus dem Startrezept (Sapiens 2): Gesamtnote 0,7560 → 0,3932; der Gewinn einer '
         'KI-Iteration an der Note ist nicht gemessen.',
         ED + '; engine2d3dkleider-nachbesserung.md'),
    ]

    @classmethod
    def eintraege(cls):
        return [{'bereich': b, 'art': a, 'thema': t, 'befund': f, 'quelle': q} for b, a, t, f, q in cls.EINTRAEGE]
