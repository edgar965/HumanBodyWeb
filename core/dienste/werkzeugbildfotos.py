# -*- coding: utf-8 -*-
"""Werkzeugbildfotos — Gruppe „Bildvergleich: Fotos und Blickwinkel“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge` (KENNUNG, TITEL, EINLEITUNG, ZEILEN, BEZIEHUNGEN). Alles hier ist aus dem Code gelesen
(Endpunkte `core/api/engine2d3dkleiderfotos.py`, Klassen `Iterationsreferenz`, `Blickwinkelschaetzung`, `Fotolandmarken`,
`Haltungsfotos`, `Fotopruefung`); gelaufen ist davon nichts.
"""

__all__ = ['Werkzeugbildfotos']


class Werkzeugbildfotos:
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    P = '2d3DIterationen/iterationen2d3d/'
    ABLAGE = ('HumanBodyWeb/core/daten/engine2d3dkleiderablage.py', 'Engine2d3dKleiderablage')
    KENNUNG = 'bildfotos'
    TITEL = 'Bildvergleich: Fotos und Blickwinkel'
    EINLEITUNG = (
        'Die Fotos sind die Vorlage jeder Runde, nicht das TRELLIS-Netz. 1. Fotos in den Auftrag legen und je Foto Rolle und Gewicht setzen '
        '(Zeilen 1–3): Die Rolle liefert den Blickwinkel. 2. Beim Lauf der Iterationen holt Blickwinkelschaetzung die fehlenden Winkel aus der '
        'Pose, Iterationsreferenz.laden macht daraus die Vorlagen (Bild, Winkel, Gewicht), Haltungsfotos misst die Arme der Fotos '
        '(Zeilen 4–8). Vorher da sein muss ein Auftrag „2D3D Kleider“ mit Fotos; für die Runden zusätzlich arbeit/grundkoerper.glb '
        '(Schritt „grundfigur“, sonst bricht die Runde mit „Keine Grundfigur“ ab). Winkel zählen in Grad ab vorn, positiv zur LINKEN Seite '
        'der Figur. In den Adressen steht <id> für die UUID des Auftrags (Feld id im Zustand), nicht für die Kennung 2026.10.01.… .'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Fotos in einen Auftrag legen, ersetzen, entfernen',
         'Bildauswahl eines bestehenden Auftrags ändern: Fotos anhängen, eines austauschen, eines entfernen.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/fotos/                    multipart: bilder (mehrere Dateien)',
             'POST /api/engine2d3dkleider/<id>/foto/<datei>/ersetzen/    multipart: bild (eine Datei)',
             'POST /api/engine2d3dkleider/<id>/foto/<datei>/loeschen/',
             '→ {ok, bilder: [{datei, original, gewicht, bereich, rolle}]}',
         )),
         [(A + 'engine2d3dkleiderfotos.py', 'Engine2d3dKleiderfotoendpunkte'), ABLAGE],
         '<datei> ist der Name im Auftrag (bilder[].datei), nicht der Originalname (bilder[].original). Neue Fotos bekommen die Rolle „aus“ — '
         'erst die Rolle setzen (nächste Zeile), sonst zählen sie nicht. Das letzte Foto lässt sich nicht entfernen (400). Hinzufügen, '
         'Ersetzen und Entfernen gehen auch während eines Laufs; ein laufender Kreislauf sieht es ab dem nächsten Lauf. Alle POST brauchen '
         'die CSRF-Marke (Gruppe „Server-Endpunkte“). Quelle: Docstring und Code von Engine2d3dKleiderfotoendpunkte.'),

        ('Rolle eines Fotos setzen',
         'Die Rolle bestimmt den Blickwinkel eines Fotos und ob es überhaupt zählt.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/rolle/<datei>/',
             '{"rolle": "vorne"}      # auto | vorne | hinten | links | rechts | gesicht | detail | aus',
             '→ {ok, bild}',
         )),
         [(A + 'engine2d3dkleiderfotos.py', 'Engine2d3dKleiderfotoendpunkte'), (D + 'meshoptionen.py', 'Meshoptionen'),
          (D + 'iterationsreferenz.py', 'Iterationsreferenz')],
         'Winkel aus der Rolle (Iterationsreferenz.ROLLEN): vorne 0°, links +90°, rechts −90°, hinten 180°. auto, gesicht und detail haben '
         'keinen Winkel aus der Rolle — dann zählt der Name ansicht_<reihe>_<spalte> (Ansichtenbogen, Iterationsreferenz.BOGEN) oder die '
         'Schätzung aus der Pose; findet sich keiner, steht das Foto in kreislauf.ausgelassen und fehlt in der Note. aus schließt das Foto '
         'aus. Unbekannte Rollen werden zu auto (Meshoptionen.rolle_pruefen). Gelesen, nicht ausprobiert: Iterationsreferenz.laden schließt '
         'gesicht und detail NICHT aus — eine Nahaufnahme, in der eine Pose erkannt wird, bekäme einen Winkel und zählte als Ansicht; im '
         'Zweifel Rolle aus setzen.'),

        ('Gewicht und Platz eines Fotos',
         'Wie stark ein Foto in die gewichtete Note eingeht (0 = gar nicht) und welches Foto Platz 1 (die „Vorlage“ der Tabelle) ist.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/gewicht/<datei>/       {"gewicht": 100, "bereich": [x0, y0, x1, y1]}   # bereich optional',
             'POST /api/engine2d3dkleider/<id>/reihenfolge/            {"datei": "<datei>", "index": 1}               # 1-basiert',
         )),
         [(A + 'engine2d3dkleiderfotos.py', 'Engine2d3dKleiderfotoendpunkte'), (D + 'meshoptionen.py', 'Meshoptionen')],
         'gewicht ist eine ganze Zahl 0–100 (Vorgabe 100, Meshoptionen.gewicht_pruefen); in den Runden zählt gewicht/100 als Mittelungsgewicht '
         'der Noten, 0 lässt das Foto aus. bereich (Ausschnitt, vier Zahlen 0–1) wirkt nur im Schritt „netz“. Der Docstring von gewicht '
         'sagt „wirkt beim nächsten Lauf von netz“; Iterationsreferenz.laden liest das Gewicht aber bei jedem Lauf der Iterationen. Platz 1 '
         'ist das Vorlagenbild der Tabelle; index wird auf die Länge der Liste begrenzt.'),

        ('Vorlagen eines Auftrags laden',
         'Liefert die Vorlagenbilder der Runden: je Foto Bild, Blickwinkel und Gewicht; Fotos ohne Winkel werden gemeldet.',
         'python',
         '\n'.join((
             'from core.dienste.iterationsreferenz import Iterationsreferenz',
             'referenzen, ausgelassen = Iterationsreferenz.laden(job)   # job: Engine2d3dKleiderauftrag',
             '[(r.original, r.winkel, r.gewicht, r.farbe) for r in referenzen]   # r.bild ist ein Iterationsbild (128 × 192)',
             "Iterationsreferenz.winkel_von(job.bilder[0])   # Grad oder None",
         )),
         [(D + 'iterationsreferenz.py', 'Iterationsreferenz'), (D + 'iterationsbild.py', 'Iterationsbild'), ABLAGE],
         'Braucht Django (Auftrag aus der Datenbank) und die Fotos in eingang/. Zählt jedes Foto mit Rolle ≠ aus und Gewicht > 0. Winkel in '
         'dieser Reihenfolge: (1) bilder[].winkel von Hand, (2) Name ansicht_<reihe>_<spalte>, (3) Rolle, (4) Schätzung aus der Pose '
         '(kreislauf.winkel_geschaetzt) — der Klassen-Docstring nennt nur drei, die vierte steht in laden(). Das Bild ist das freigestellte '
         'vorbereitet/<name>.png des Schritts „netz“ (Alpha = Figur), sonst das Foto auf Weiß; ohne vorbereitet/ gilt ein Foto mit Zimmer '
         'dahinter als ganze Figur (IoU 0,32 gegen den Flur, engine2d3dkleider.md, 30.09.2026). Fotos, die die Fotoprüfung ausließ '
         '(ergebnis.fotopruefung.ausgelassen), haben farbe=False: Sie zählen nur für die Form. Zeit: nicht gemessen.'),

        ('Blickwinkel eines Fotos aus der Pose schätzen',
         'Ersatz für fSpy: aus den MediaPipe-Weltpunkten (Schulter-, Hüftlinie, Gesicht) den Winkel ab vorn rechnen.',
         'python',
         '\n'.join((
             'import sys; sys.path.insert(0, "A:/3DTools/2d3DIterationen")',
             'from iterationen2d3d.blickwinkel import Blickwinkel',
             'Blickwinkel.schaetzen({11: {"x": 0.1, "y": -0.4, "z": 0.0, "sichtbar": 0.9}, 12: {…}, 23: {…}, 24: {…}, 0: {…}, 7: {…}, 8: {…}})',
             '# → Grad (−180…180) oder None;  Blickwinkel.rolle(winkel) → "vorne" | "links" | "rechts" | "hinten"',
         )),
         [(P + 'blickwinkel.py', 'Blickwinkel')],
         'Reine Rechnung ohne Django. Eingang sind die Weltpunkte der MediaPipe-Pose (pose_welt aus Fotolandmarken: Meter, Ursprung '
         'Hüftmitte, Kamera blickt entlang +z). Schulter- (11/12) und Hüftlinie (23/24) werden einzeln mit ihrer Sichtbarkeit gewichtet '
         '(ab 0,5), eine Linie unter 0,08 m zählt halb; Nase (0) gegen Ohren (7/8) entscheidet vorn oder hinten. Kein Landmarkenpunkt '
         'sichtbar → None. Gemessen an Edgars Fotos (.51, 01.10.2026): vorne −6°, hinten −173°, Seite −78° (rechts), passend zu den '
         'Rollen (engine2d3dkleider.md). Genauigkeit über diese drei Fotos hinaus: nicht gemessen. Eine Suche des Winkels über die '
         'Umriss-Note ist verworfen (BlenderModel: sie schob Seitenansichten an den Rand des Suchfensters; Docstring Iterationsreferenz).'),

        ('Blickwinkel für alle Fotos eines Auftrags nachholen',
         'Schätzt den Winkel jedes Fotos ohne Winkel aus der Pose und legt ihn im Kreislauf des Auftrags ab.',
         'python',
         '\n'.join((
             'from core.dienste.blickwinkelschaetzung import Blickwinkelschaetzung',
             'ablage = Engine2d3dKleiderablage(job.kennung)',
             'Blickwinkelschaetzung(job, ablage).offene()       # Einträge der Bildauswahl, die zählen sollen, aber keinen Winkel haben',
             'z = Blickwinkelschaetzung(job, ablage).fuer_lauf()   # kreislauf-Dict; z["winkel_geschaetzt"][datei] = {winkel, rolle, quelle}',
         )),
         [(D + 'blickwinkelschaetzung.py', 'Blickwinkelschaetzung'), (D + 'iterationsreferenz.py', 'Iterationsreferenz'),
          (D + 'fotolandmarken.py', 'Fotolandmarken'), (P + 'blickwinkel.py', 'Blickwinkel'), ABLAGE],
         'Läuft von selbst am Anfang jeder Begutachtungsrunde (Begutachtungsrunde.ausfuehren); von Hand nur zum Nachsehen. Je Datei einmal '
         '(Cache arbeit/fotolandmarken.json — der Aufruf schreibt diese Datei). fuer_lauf ändert job.ergebnis["kreislauf"] nur im Speicher, '
         'gesichert wird erst vom Lauf. Ein Foto ohne erkennbare Person bekommt winkel None und bleibt ausgelassen (Grund im Log). '
         'Scheitert der Wrapper, steht nur eine Warnung im Log. Kosten des Wrappers: nächste Zeile.'),

        ('Posen- und Gesichtslandmarken je Foto',
         'MediaPipe-Landmarken (Pose in Weltmetern, Gesicht mit 478 Punkten) für Blickwinkel, Haltung und Gesichtsmaße.',
         'python',
         '\n'.join((
             'from core.dienste.fotolandmarken import Fotolandmarken',
             'ablage = Engine2d3dKleiderablage(job.kennung)',
             "Fotolandmarken(ablage).holen([ablage.unter(Engine2d3dKleiderablage.EINGANG) / 'vorne.jpg'])",
             "# → {'vorne.jpg': {pose_welt, gesicht, breite, hoehe, fassung, stand, …}}",
         )),
         [(D + 'fotolandmarken.py', 'Fotolandmarken'), ABLAGE],
         'Rechnet im Wrapper VideoToBVH/wrappers/_run_fotolandmarken.py unter python10 (python14 hat kein MediaPipe), Zeitgrenze 600 s. Ein '
         'Aufruf lädt die Modelle einmal (≈ 2 s) und rechnet ≈ 0,3 s je Bild (Docstring der Klasse, nicht nachgemessen). Ergebnis je Datei in '
         'arbeit/fotolandmarken.json; neu gerechnet wird nur, wenn sich Größe oder Änderungszeit der Datei oder die Fassung ändern '
         '(Fotolandmarken.FASSUNG = 2: seit 01.10.2026 sucht Fassung 2 das Gesicht auch im Kopfausschnitt der Pose). pose_welt: 33 Punkte '
         '[x, y, z, sichtbar]; gesicht: 478 Punkte (x, y) in Bildanteilen. Scheitert der Wrapper: leeres Ergebnis und Warnung im Log.'),

        ('Haltung der Arme auf den Fotos',
         'Misst, wie die Arme auf den Fotos hängen (Oberarm zur Senkrechten, Ellbogenbeuge), damit das Modell in derselben Haltung gerendert wird.',
         'python',
         '\n'.join((
             'from iterationen2d3d.haltungsschaetzung import Haltungsschaetzung',
             'Haltungsschaetzung.schaetzen([b["pose_welt"] for b in landmarken.values()])   # {seitlich, beuge, arme[, beine]} oder None',
             'from core.dienste.haltungsfotos import Haltungsfotos',
             'Haltungsfotos(job, ablage).fuer_lauf(z, referenzen)   # schreibt z["haltung_foto"]; None bei Fehler',
         )),
         [(D + 'haltungsfotos.py', 'Haltungsfotos'), (P + 'haltungsschaetzung.py', 'Haltungsschaetzung'),
          (D + 'fotolandmarken.py', 'Fotolandmarken')],
         'seitlich = Winkel des Oberarms zur Senkrechten im Körperrahmen der Hüftlinie (Vorder-, Rücken- und Seitenfoto liefern dasselbe Maß), '
         'beuge = Beugung im Ellbogen; ein Arm zählt nur, wenn Schulter, Ellbogen und Handgelenk sichtbar sind (ab 0,5). An Edgars Fotos '
         '(.51, 01.10.2026): vorn 12,7° / 15,9° seitlich, Ellbogen 23° / 21°; die A-Pose der Figur hat 42,8° und 13,6° (Docstring '
         'Haltungsschaetzung). Hier wird nur gemessen. Gestellt wird die Haltung von haltung(g) und haltung_gelenk(…), gehäutet für den '
         'Render von G9haltungshaut (ortsmorphe.md, 01.10.2026). Läuft von selbst am Anfang jeder Runde; bei einem Fehler bleibt die A-Pose.'),

        ('Fotos mit anderer Kleidung erkennen',
         'Prüft vor TRELLIS, ob die Fotos dieselbe Kleidung zeigen; ein abweichendes Foto zählt später nur für die Form.',
         'python',
         '\n'.join((
             'import sys; sys.path.insert(0, "A:/3DTools/VideoToBVH/wrappers")',
             'from mesh_fotopruefung import Fotopruefung',
             'Fotopruefung.pruefen([(datei, rolle, rgba_uint8_H_B_4), …])',
             '# → {farben, abstaende, ausgelassen: [datei], grund: {datei: Text}, schwelle, nicht_geprueft: [datei]}',
         )),
         [('VideoToBVH/wrappers/mesh_fotopruefung.py', 'Fotopruefung'), (D + 'engine2d3dkleidernetz.py', 'Engine2d3dKleidernetz'),
          (D + 'iterationsreferenz.py', 'Iterationsreferenz')],
         'Im Auftrag läuft sie im Netz-Runner (_run_mesh.py) nur mit der Option fotopruefung = an, die Engine2d3dKleidernetz setzt; das '
         'Ergebnis steht in ergebnis.fotopruefung. Je Foto die Medianfarbe zweier Bänder (Rumpf, Hüfte) eines Mittelstreifens der Figur; '
         'Bandabstand = der größere von Farbton-Abstand ÷ 0,05 (FARBTON) und Helligkeitsverhältnis gegen 2,5 (HELL_FAKTOR), Grenze 1,0 '
         '(SCHWELLE, gemessen am Auftrag .51, Docstring, 01.10.2026). Ein Foto fällt heraus, wenn es der Mehrheit der anderen widerspricht, '
         'mindestens zwei Fotos bleiben und es nicht „vorne“ ist; Nahaufnahmen (Rolle gesicht, detail, aus, oder Figur nicht mindestens '
         'doppelt so hoch wie breit) werden nicht verglichen. Wirkung in den Runden: Iterationsreferenz.laden setzt für ausgelassene Fotos '
         'farbe=False — sie zählen für Umriss, Breiten und Haltung, nicht für Farbe, Textur und Fotoprojektion.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Engine2d3dKleiderfotoendpunkte', 'ruft', 'Engine2d3dKleiderablage',
         'eingang_ablegen(): legt hochgeladene Fotos unter eingang/ ab; datei(): Pfadprüfung beim Entfernen'),
        ('Engine2d3dKleiderfotoendpunkte', 'ruft', 'Meshoptionen', 'rolle_pruefen(), gewicht_pruefen(), bereich_pruefen()'),
        ('Iterationsreferenz', 'ruft', 'Iterationsbild', 'aus_render() / aus_vorlage(): das Vorlagenbild auf der Fläche der Note'),
        ('Iterationsreferenz', 'ruft', 'Engine2d3dKleiderablage', 'unter(EINGANG), unter(VORBEREITET): Pfade der Fotos und der freigestellten Bilder'),
        ('Blickwinkelschaetzung', 'ruft', 'Iterationsreferenz', 'winkel_von(eintrag): welche Fotos noch keinen Winkel haben'),
        ('Blickwinkelschaetzung', 'ruft', 'Fotolandmarken', 'holen(pfade): pose_welt je Foto'),
        ('Blickwinkelschaetzung', 'ruft', 'Blickwinkel', 'schaetzen(welt), rolle(winkel)'),
        ('Haltungsfotos', 'ruft', 'Fotolandmarken', 'holen(pfade): pose_welt je Foto'),
        ('Haltungsfotos', 'ruft', 'Haltungsschaetzung', 'schaetzen(fotos): Arme und Beine im Körperrahmen'),
        ('Fotolandmarken', 'ruft', 'Engine2d3dKleiderablage', 'arbeit(DATEI): Cache fotolandmarken.json'),
        ('Engine2d3dKleidernetz', 'ruft', 'Fotopruefung',
         'setzt die Option fotopruefung = an; der Netz-Runner _run_mesh.py ruft Fotopruefung.pruefen(fotos)'),
    ]
