# -*- coding: utf-8 -*-
"""Werkzeuggesicht — Gruppe „Gesicht, Augen, Brauen, Mund und Mimik“ des Reiters „Tools“ der Seite Hilfe → Architektur → 2D3D (03.10.2026).

Schema: `Architektur2d3dwerkzeuge`. Gelesen am 03.10.2026: `IterationGesicht`, `Gesichtsmasse`, `Gesichtsvorrat`, `Fotolandmarken`, `Gesichtsformendpunkte`, `G9schnittmorph`,
`G9anhang`, `G9brauen`, `Meshfiguriris`, `Meshfiguraugenbild`, `G9mimik`, `G9visemes`, `Meshfigurregler`. Das Gesicht hat keine eigene Rezeptfunktion:
`ModellMitKleidern` kennt kein m.gesicht_… — Kopfregler gehen über m.koerper_regler.
"""

__all__ = ['Werkzeuggesicht']


class Werkzeuggesicht:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    I = '2d3DIterationen/iterationen2d3d/'
    W = 'VideoToBVH/wrappers/'

    KENNUNG = 'gesicht'
    TITEL = 'Gesicht, Augen, Brauen, Mund und Mimik'
    EINLEITUNG = (
        'Das Gesicht einer Genesis-9-Figur sind Kopfregler (Bereich kopf), ein Eigenmorph „Kopf-Eigen“ und die Anhänge Augen, Mund, Wimpern, Brauen. '
        'Reihenfolge: 1. die Kopfform kommt aus der Gesichtskette von Mesh to 3D (Gruppe „Mesh to 3D“); 2. nachstellen mit m.koerper_regler und den '
        'Gesichtsmaßen Foto gegen Render (Gesichtsmasse); 3. wo die Regler nicht reichen, Kopf-Eigen aus Schnitten und Konturen; 4. Augen, Brauen, '
        'Wimpern und Mund wählen. Mimik stellt die Pipeline nicht: der Mund bleibt geschlossen (Mimik-Filter).'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Kopfregler setzen',
         'Stellt einen Regler des Kopfes (Kopfform, Nase, Mund, Lippen, Augen, Brauen, Wangen, Kinn, Kiefer, Ohren, Head Size).',
         'rezept',
         "m.koerper_regler('<Kopfregler-ID aus der Reglerliste>', 0.3)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept'), (D + 'gesichtsmasse.py', 'Gesichtsmasse'),
          (G + 'reglerplan.py', 'G9reglerplan')],
         'Es gibt keine m.gesicht_…-Funktion. Die Kanal-ID nie raten: die 200-Plus-Regler heißen 200_head_bs_Lip Part oder 200_head_bs_Lip Upper Gap-0xa11888f '
         '(Leerzeichen, Suffix bei Namenskollision), Charakterköpfe <X>_head_bs_Head. Suchen über die Anzeige: Gesichtsmasse.kopfregler() liefert '
         '[{name, anzeige}] zu den Suchworten am Ende der Anzeige, die Reglerliste (GET …/genesis9-figur/regler/, Bereich kopf) alle. Zwei Zählungen nicht '
         'gleichsetzen: 296 Kopfregler im Anpassungssatz der Gesichtskette (27.09.2026), 386 im Bedienfeld-Bereich kopf (Gesichtsmasse, 02.10.2026). Wertebereich '
         'je Regler min…max der Liste, geklemmt beim Bau. Prüf-KI: koerper_regler verboten. Mundöffner (Lip Part, Lip Gaps, Mouth Opening) werden beim Lesen '
         'der Stellung entfernt (Mimik-Filter unten).'),
        ('Gesichtsmaße Foto gegen Render',
         'Misst Augenabstand, Nase, Mund, Kinn, Gesichtsbreite und Augenhöhe auf dem Vorderfoto und auf dem Kopf-Render des Modells; das Verhältnis steuert die Kopfregler.',
         'python',
         'from core.dienste.gesichtsmasse import Gesichtsmasse\n'
         'Gesichtsmasse.masse(punkte478, breite_px, hoehe_px)   # {breite, augen, nase, nase_laenge, mund, kinn, augen_hoehe} = Strecke / Gesichtshöhe (Landmarke 10 – 152)\n'
         'Gesichtsmasse.kopfregler()   # [{name, anzeige}]\n'
         'Gesichtsmasse(ablage, render).befund(teile, referenzen, aus)   # im Lauf: Foto gegen Kopf-Render, Median über vier Saaten',
         [(D + 'gesichtsmasse.py', 'Gesichtsmasse'), (D + 'fotolandmarken.py', 'Fotolandmarken'), (D + 'gesichtsvorrat.py', 'Gesichtsvorrat'),
          (G + 'reglerplan.py', 'G9reglerplan')],
         'MediaPipe-FaceLandmarker, 478 Punkte (python10-Wrapper _run_fotolandmarken.py; Modelle laden ≈ 2 s, ≈ 0,3 s je Bild). Strecken: breite 234–454, '
         'augen 468–473, nase 129–358, nase_laenge 168–4, mund 61–291, kinn 17–152. Der Kopf-Render (Genesishaarrender.bild_kopf, 1024 × 1024, je ≈ 0,45 s) wird '
         'über vier Saaten gemittelt und je Kopfstand einmal abgelegt (Gesichtsvorrat, arbeit/gesicht_vorrat.json, höchstens 200 Einträge; der Schlüssel kommt nur '
         'aus den Körperpunkten bis 0,20 m unter dem Scheitel). Grenzen: der Detektor springt je Maß um ≈ 1 %, selbst über vier Saaten schwankt der Gesichtsterm der '
         'Note noch um 0,0125 (bei 512 px, kopfrauschen.py, 01.10.2026), Rundenauswahl.TOLERANZ ist 0,002; ein Render nur aus dem Körper war schlechter (Note +0,036). Ohne Vorderfoto (|Winkel| > 30°) oder ohne '
         'erkanntes Gesicht kein Befund, die Runde läuft weiter. Wrapper-Fassung 2 sucht das Gesicht auch im Kopfausschnitt der Pose (Ganzkörperfotos).'),
        ('Gesichtsregler der Automatik',
         'Schreibt aus den Gesichtsmaßen Rezeptzeilen m.koerper_regler für sechs Kopfregler — gedämpft und mit Rückschritt; nur bei Option iterationen.form = an.',
         'python',
         'IterationGesicht(modell, befund, regler=None, verlauf=None).aufrufe()   # → ["m.koerper_regler(\'<ID>\', 0.35)", …]\n'
         "# Option iterationen.form = 'an' (Vorgabe 'aus')",
         [(I + 'iterationgesicht.py', 'IterationGesicht'), (I + 'reglerpruefung.py', 'Reglerpruefung')],
         'Je Maß ein Regler, gesucht über das Wort am Ende der Anzeige: breite → Face Upper Width, augen → Eyes Distance, augen_hoehe → Eyes Height A (Vorzeichen −), '
         'nase → Nose Width Lower, mund → Lips Width, kinn → Chin Length. Namen und Vorzeichen gemessen 01.10.2026 (gesichtsregler_probe.py, Regler 0,8 an der '
         'Grundfigur „Edgar - Hoch“): Eyes Distance +2,0 % Augenabstand, Lips Width +3,7 % Mund, Chin Length +4,4 % Kinn, Eyes Height A −3,3 % Augenhöhe, Nose Width '
         'Lower +1,6 % Nase, Face Upper Width +0,5 % Breite. „Face Width“, „Nose Width“, „Mouth Width“ gibt es bei Genesis 9 nicht; die Nasenlänge bewegt kein Regler '
         'sauber (Nose Size Full −8,4 %, Chin Length −8,7 %) — gemessen, ungeregelt. Schritt = 0,6 × (Verhältnis − 1) × Vorzeichen, höchstens 0,35, Grenze ±1, unter '
         '3 % Abweichung nichts; Reglerpruefung (BESSER 0,005) nimmt einen Fehlschritt zurück. Grenze (.51, 25 Runden): Lips Width stand mit 1,0 an der Grenze und Chin Length '
         'bei ≈ 0,75, Mund 1,13 und Kinn 1,11 blieben über den Reglern; der Augenabstand konvergierte (1,07 → 0,998) — ein Regler bei 1 ändert ein Maß nur um 2–6 %.'),
        ('Seite „Gesichtsform“ (Kopf-Eigen)',
         'Die Gesichtsform aus Schnitten und Konturen malen und rechnen — für Menschen; Sessions nehmen die API.',
         'seite',
         '/gesichtsform/?auftrag=<kennung>   oder   /gesichtsform/?modell=<Name>',
         [(A + 'gesichtsform.py', 'Gesichtsformendpunkte'), (D + 'gesichtsformquelle.py', 'Gesichtsformquelle')],
         'Figur in 3D mit Schnittlinien, Vorderansicht (Konturen), Schnittfelder zum Malen, Güte; ein Knopf auf der Auftragsseite von Mesh to 3D führt hin. Der '
         'Abschnitt „Kopf-Eigen“ im Reglerfeld steht immer da, auch ohne Morph, und trägt den Link zur Seite (kopfeigenlink.js). Die Rechnung dauert Sekunden und '
         'läuft synchron, ohne Auftrag.'),
        ('Kopf-Eigen rechnen',
         'Berechnet einen Eigenmorph, der Tiefenprofile je Schnitt und Konturpunkte (Augen, Brauen, Nase, Lippen) trifft.',
         'api',
         'POST /api/gesichtsform/profile/   {auftrag|modell, waagerecht?, senkrecht?, ziel_neu?}   → Ist, Ergebnis, Ziel, Rahmen, Güte\n'
         'POST /api/gesichtsform/rechnen/   {auftrag|modell, ziel: {schnitte, punkte} (mm), zielquelle?}   → legt den Morph ab\n'
         'POST /api/gesichtsform/speichern/   {auftrag|modell, wert}   → Wert 0…2 in Auftrag oder Modell\n'
         "# Python: G9schnittmorph(stellung, name).rechnen(ziel, quelle='seite')",
         [(A + 'gesichtsform.py', 'Gesichtsformendpunkte'), (D + 'gesichtsformquelle.py', 'Gesichtsformquelle'), (D + 'gesichtsformantwort.py', 'Gesichtsformantwort'),
          (D + 'gesichtsformziel.py', 'Gesichtsformziel'), (G + 'schnittmorph.py', 'G9schnittmorph'), (G + 'schnittvorgaben.py', 'G9schnittvorgaben'),
          (G + 'schnittloeser.py', 'G9schnittloeser'), (G + 'gesichtsschnitte.py', 'G9gesichtsschnitte'), (G + 'gesichtsrahmen.py', 'G9gesichtsrahmen'),
          (G + 'augenpartie.py', 'G9augenpartie')],
         "Ergebnis ist der Eigenmorph eigen:kopf_<Name> (Wert 0…2, Steckbrief art 'kopf' mit Ziel und Güte je Schnitt), Abschnitt „Kopf-Eigen“. Rahmen aus den "
         "478 Landmarken (x' 33→263, y' 152→10, z' vorn); EIN Rahmen für alles, der der Figur ohne Kopf-Eigen — zwei Rahmen standen bei Damira 3,4° gegeneinander. "
         'Ziel: Tiefenprofile (1 mm, im Gesichtsoval) und Konturpunkte; das Oval selbst nicht, zwei Runden. Augenpartie und Innenräume bekommen keine Tiefenvorgabe; '
         'gemessen wird mit Augäpfeln (ohne sie traf ein Schnitt durch die Augenhöhle den Hinterkopf, 188 mm). Zeit (Damira, 27.09.2026, kopfeigen.md): Profile 5,8 s, '
         'Rechnen 8,4 s, größte Verschiebung 9,1 mm, Konturen 1,5–3,2 → 0–0,02 mm, Schnitte p90 0,08–1,5 mm. OFFEN: im Bild stand das Untergesicht der Figur 0,8–1,0 cm '
         '(7–10 %) schmaler als das Kopfnetz, auf Augenhöhe 1,5 cm breiter — im Widerspruch zu den Schnittzahlen, ungeklärt. Kopf-Eigen auf eine schlecht angepasste '
         'Figur macht sie schlechter (Knitter): erst die Anpassung. Stellbar wie jeder Eigenmorph (eigen:kopf_<Name>), im Rezept über m.koerper_regler — nicht an '
         'einer Runde geprüft. Der POST schreibt eine Datei neben die Bibliothek — nur nach Ansage.'),
        ('Augen, Brauen, Wimpern und Mund wählen',
         'Wählt Augenbild, Brauenstil und -farbe sowie Wimper- und Mundpresets; die Anhänge sind eigene Netze am Körperskelett.',
         'api',
         'GET /api/character/genesis9-figur/regler/   → augen [{id, name}], brauen, brauenstile [{id, name, art}], brauenfarben, praesets\n'
         "POST /api/character/genesis9-figur/<name>/netz/   {augen: '01', brauen: 'Brown', brauenstil: 'card06', praesets: {wimpern: <id>, mund: <id>}, anhaenge: true}",
         [(A + 'g9figur.py', 'G9figur'), (G + 'anhang.py', 'G9anhang'), (G + 'brauen.py', 'G9brauen'), (G + 'hautpresets.py', 'G9hautpresets'),
          (G + 'hautwahl.py', 'G9hautwahl')],
         'Augen: 15 Bilder G9_EyesNN_D.jpg (id 01…15) plus die Augenpresets der Charaktere (<charakter>:<slug>). Brauen: 12 Kartenstile (card01…12), 9 Faserstile '
         '(fiber01…09) und Charakterbrauen (charakter:…); Vorgabe card06 in Braun (Dazʼ Post-Load lädt Karte Style 06), Farben je Art in G9brauen.farben_je_art. '
         'Wimpern und Mund (Zähne, Zunge) über praesets (Kategorien wimpern und mund), die Wimperregler /Eyelashes stehen im Bereich kopf. Anhänge: Augen, Mund, '
         'Wimpern, Träne, Brauen (G9anhang); die Augäpfel folgen den Morphs starr, der Mund führt tongue01..05. Die Albedo von Genesis 9 trägt keine gemalten Brauen — '
         'ohne den Brauen-Anhang hat die Figur keine. Toon-Figuren bekommen Augen, Wimpern und Brauen der Grundfigur plus mund_toon und schatten (18.09.2026).'),
        ('Iris aus dem Netz',
         'Misst die Irisfarbe des Netzes und färbt die Iris des Daz-Augenbilds darauf.',
         'python',
         'Meshfiguriris(scan, gesicht).messen()   # python10-Runner, Schritt textur → {rechts: {farbe, proben, radius_mm}, links: …, farbe}\n'
         'Meshfiguraugenbild.schreiben(ordner, ziel)   # python14: G9_Eyes01_D.jpg in der Irisfarbe → meshfigur_augen.jpg (2048²)',
         [(W + 'meshfigur_iris.py', 'Meshfiguriris'), (D + 'meshfiguraugenbild.py', 'Meshfiguraugenbild'), (D + 'meshfiguraugenhoehle.py', 'Meshfiguraugenhoehle'),
          (G + 'augenpartie.py', 'G9augenpartie')],
         'Ergebnis in ergebnis.fototextur.augen und im Modell figur.fototextur.augen; die Szene setzt es als Albedo der Augäpfel. Gemessen wird der Median der Netzfarbe im '
         'Ring 0,35–0,9 Irisradius um die Landmarken 468 und 473 (20.000 Proben je Auge, mindestens 200); gefärbt wird je Kanal linear (Faktor Ziel / Median der Iris, '
         'Grenzen 0,2…5), an Pupille und Limbus weich ausgeblendet, die Lederhaut bleibt. Damira: Netz bernsteinfarben (≈ 106, 75, 46) gegen Daz (108, 85, 66). Die '
         'Augenpartie nimmt Meshfiguraugenhoehle aus dem Rest-Eigenmorph (Lücke): sonst zog die Mulde des Bild-zu-3D-Netzes den starren Augapfel durch die Lider, '
         'sichtbar 419 statt 195 mm² (27.09.2026). Den sichtbaren Augapfel messen, nicht die Lidlandmarken (10,6 mm Lidspalte gegen 20,4 × 26,5 mm Augapfel).'),
        ('Mimik und Visemes (Felder)',
         'Liefert die Deltafelder der 26 Mimikkanäle und 17 Visemes für Mimik-Spur, Script-Spur und Lipsync.',
         'api',
         'GET /api/character/genesis9-figur/felder/mimik/?stufen=1   → {stufen, mimik: [{id, name}], achsen, felder}\n'
         'GET /api/character/genesis9-figur/felder/visemes/?stufen=1   → {stufen, visemes: [{id, name}], achsen, felder}',
         [(A + 'g9felder.py', 'G9felderapi'), (G + 'mimik.py', 'G9mimik'), (G + 'visemes.py', 'G9visemes'), (G + 'reglerfelder.py', 'G9reglerfelder')],
         'Mimik: Braue, Auge, Wange, Nase, Mund, Zunge aus /Pose Controls/Head (facs_ctrl_BrowUp … facs_ctrl_MouthSmile …); Visemes facs_ctrl_vAA … vW. Ein Feld wird bei '
         'Reglerwert 1 gebacken, deshalb nur einseitige Kanäle (0…1): ein Kanal mit −1…1 hätte bei negativem Gewicht nur eine ungeprüfte lineare Hochrechnung '
         '(22.09.2026). Knochenanteile (lowerjaw 5,2° bei Vis AA, Lippenknochen) stellt der Browser. 11 von 42 MB-Lab-Einheiten bleiben unübersetzt (deglutition, '
         'pupilsDilatation, mouthChew, tongueOut, tongueOutPressure, tongueTipUp, jawOut, jawHoriz, mouthHoriz, eyesHoriz, eyesVert). Es gibt keine Rezeptfunktion für '
         'Mimik; die Pipeline aus Fotos stellt keine Mimik.'),
        ('Mimik-Filter (Mund geschlossen)',
         'Entfernt die Mundöffner aus einer Reglerstellung, damit der Mund auf den Fotos geschlossen bleibt.',
         'python',
         'from core.dienste.meshfigurregler import Meshfigurregler\n'
         'Meshfigurregler.ohne_mimik(stellung)   # Stellung ohne Regler, deren Name Lip Part, Lip Upper Gap, Lip Lower Gap oder Mouth Opening enthält\n'
         "Meshfigurregler.MIMIK   # ('Lip Part', 'Lip Upper Gap', 'Lip Lower Gap', 'Mouth Opening')",
         [(D + 'meshfigurregler.py', 'Meshfigurregler'), ('HumanBodyWeb/core/models/engine2d3dkleiderauftrag.py', 'Engine2d3dKleiderauftrag')],
         'Am verwaschenen Mund des TRELLIS-Netzes stellte die Anpassung Lip Upper Gap 0,74, Lip Part 0,30 und Mouth Opening M/V Shape −1: Mund offen, Unterlippe zurück '
         '(Testauftrag 2026.10.01.12.38.09; auf den Fotos ist der Mund zu). Gesperrt an zwei Stellen: in der Anpassung (Stufe 0, Meshfigurregler.stufe) und beim Lesen einer '
         'gespeicherten Stellung (Engine2d3dKleiderauftrag.stellung ruft ohne_mimik) — so wirkt die Sperre auf alte Aufträge in Sekunden statt in 872 s Körperschritt. '
         'Der Test ist ein Teilstring im Reglernamen (200_head_bs_Lip Part…); die Lippenform bleibt frei, eigen:…-Regler sind nicht betroffen.'),
        ('Regel: Gesichtsform messen, nicht schätzen',
         'Wie man einen Kopf prüft, bevor man etwas über ihn behauptet.',
         'regel',
         '— keine Rezeptzeile: Höhenschnitte alle 2 cm, waagerecht und senkrecht, mit dem Maximum je Schnitt; Werkzeuge ProjektTemp/_wegwerf/meshto3d/gesicht_schnitte.py '
         '<job-uuid> <kennung>, nase_schnitte.py <kennung>, landmarken_daneben.py <kennung> [<schwelle mm>]',
         [(D + 'gesichtsformziel.py', 'Gesichtsformziel')],
         'Edgar, 27.09.2026: „was nutzt ein Median??“ — der Median von 0,73 mm verbarg die Augen, die 10 mm vor dem Kopfnetz standen. Gemessen wird die Browserfigur '
         '(G9koerpernetz: Stufe 1, HD, Anhänge), nicht posiert.npy (der Käfig hat keine Augäpfel). Die Landmarken des Netzes zuerst auf ihren Abstand zur Netzfläche prüfen: '
         'bei Edgars Körpernetz lagen 126 von 478 mehr als 8 mm daneben, 100 in der Luft vor dem Gesicht — „Nase 10 mm kürzer“ war ein Fehler der schwebenden Landmarke '
         '(29.09.2026). Die Kopfform auch im Bild messen (Edgar: „du fabulierst völlig!!!“): die Schnitte der Registrierung meldeten vorn 0–2 mm, das Bild zeigte 7–10 %.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9rezept', 'ruft', 'ModellMitKleidern', 'anwenden(): koerper_regler(<Kopfregler-ID>, wert) je Zeile'),
        ('IterationGesicht', 'ruft', 'Reglerpruefung', 'urteil(punkte): Fehlschritt zurück, danach gesperrt'),
        ('Gesichtsmasse', 'ruft', 'Fotolandmarken', 'holen(pfade): 478 Gesichtspunkte je Foto und Kopf-Render'),
        ('Gesichtsmasse', 'ruft', 'Gesichtsvorrat', 'schluessel(), holen(), ablegen(): je Kopfstand einmal messen'),
        ('Gesichtsmasse', 'ruft', 'G9reglerplan', 'bereiche(): kopfregler() sucht die Suchworte in den Anzeigen des Bereichs kopf'),
        ('Gesichtsformendpunkte', 'ruft', 'Gesichtsformquelle', 'aus(rumpf): Auftrag oder Modell; stellung(), uebernehmen(), speichern()'),
        ('Gesichtsformendpunkte', 'ruft', 'Gesichtsformantwort', 'bauen(): Ist, Ergebnis, Ziel, Rahmen und Güte für die Seite'),
        ('Gesichtsformendpunkte', 'ruft', 'G9schnittmorph', 'rechnen(ziel, quelle) und ziel_aus_seite(roh)'),
        ('Gesichtsformantwort', 'ruft', 'Gesichtsformziel', 'ziel(lagen, rahmen): Ziel aus dem Kopfnetz des Auftrags, wenn vorhanden'),
        ('Gesichtsformantwort', 'ruft', 'G9schnittmorph', 'steckbrief(name), figur(), messen(): Ist und Güte'),
        ('G9schnittmorph', 'ruft', 'G9gesichtsrahmen', 'genesis(kaefig): Rahmen aus den 478 Landmarken'),
        ('G9schnittmorph', 'ruft', 'G9gesichtsschnitte', 'profile(punkte, dreiecke, lagen): Tiefenprofile je Ebene'),
        ('G9schnittmorph', 'ruft', 'G9schnittvorgaben', 'G9schnittvorgaben(rahmen, kaefig, BAND, OHR_RAND).frei: Vorgabepunkte'),
        ('G9schnittmorph', 'ruft', 'G9schnittloeser', 'G9schnittloeser(nachbarmittel, frei): glatte Verschiebung je Achse'),
        ('G9schnittvorgaben', 'ruft', 'G9augenpartie', 'maske(): Lider und Körpernachbarn des Augapfels bekommen keine Tiefenvorgabe'),
        ('Meshfiguraugenhoehle', 'ruft', 'G9augenpartie', 'maske(): die Augenpartie ist im Rest-Eigenmorph eine Lücke'),
        ('G9felderapi', 'ruft', 'G9mimik', 'liste(), felder(stufen): 26 Mimikkanäle'),
        ('G9felderapi', 'ruft', 'G9visemes', 'liste(), felder(stufen): 17 Visemes'),
        ('G9mimik', 'ruft', 'G9reglerfelder', "holen('mimik', kennungen, stufen): Deltafelder je Stufe"),
        ('G9figur', 'ruft', 'G9anhang', 'brauenfarben(): Farben der Brauen in der Reglerliste'),
        ('G9figur', 'ruft', 'G9brauen', 'stile(), farben_je_art(): Brauenstile und Farben je Art'),
        ('G9figur', 'ruft', 'G9hautpresets', 'hautpresets(), augen(): Hautsätze und Augenbilder'),
        ('G9anhang', 'ruft', 'G9brauen', 'duf(stil), bilder(stil, farbe): Geometrie und Bilder der Brauen'),
        ('G9anhang', 'ruft', 'G9hautpresets', 'augenbilder(augen), anhangbilder(ordner): Bilder von Augen, Mund und Wimpern'),
        ('Engine2d3dKleiderauftrag', 'ruft', 'Meshfigurregler', 'stellung(): ohne_mimik(regler.stellung)'),
    ]
