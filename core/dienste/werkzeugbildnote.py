# -*- coding: utf-8 -*-
"""Werkzeugbildnote — Gruppe „Bildvergleich: Maske, Umriss, Farbe und Noten“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code: `Iterationsbild`, `Iterationsnote`, `Iterationsnetznote`, `Gesamtnote`,
`Rundenauswahl`, `Begutachtungsrunde._runde`, `Begutachtungsstand.fortschreiben`. Grep über A:\\3DTools (03.10.2026): `Iterationsnote.vergleichen`
wird nur von `Begutachtungsrunde._runde` und `Iterationsrunde.bewerten` gerufen — es gibt keinen Endpunkt und keinen Befehl dafür.
"""

__all__ = ['Werkzeugbildnote']


class Werkzeugbildnote:
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    P = '2d3DIterationen/iterationen2d3d/'
    ABLAGE = ('HumanBodyWeb/core/daten/engine2d3dkleiderablage.py', 'Engine2d3dKleiderablage')
    KENNUNG = 'bildnote'
    TITEL = 'Bildvergleich: Maske, Umriss, Farbe und Noten'
    EINLEITUNG = (
        'Eine Note vergleicht EIN Foto mit EINEM Render im selben Blickwinkel; kleiner ist überall besser. 1. Beide auf dieselbe Fläche bringen '
        '(Iterationsbild), 2. Umriss und Farbe vergleichen (Iterationsnote), 3. über die Ansichten mitteln, 4. in 3D gegen das Netz messen '
        '(Iterationsnetznote), 5. zur Gesamtnote zusammensetzen (Gesamtnote), nach der die Rundenauswahl entscheidet. Die Zahlen sind '
        'Hilfsmaße: Die Fotonote belohnte eine lange Frisur mit 1,799 gegenüber der richtigen kurzen mit 1,937 (engine2d3dkleider.md, '
        '01.10.2026) — die Tafel (Gruppe „Prüfbilder“) entscheidet, nicht die Zahl. Wer EINEN Vergleich ohne Runde braucht, findet ihn in '
        'Zeile 2.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Foto oder Render auf die gemeinsame Fläche bringen',
         'Normiert ein Bild so, dass Foto und Render pixelweise vergleichbar sind: gleiche Figurhöhe, Rumpfmitte in der Bildmitte.',
         'python',
         '\n'.join((
             'import sys; sys.path.insert(0, "A:/3DTools/HumanBodyWeb")      # kein Django nötig: nur numpy und PIL',
             'from core.dienste.iterationsbild import Iterationsbild',
             'Iterationsbild.aus_render("<RGBA-PNG, Alpha = Figur>", (256, 384))   # Render oder freigestelltes Foto (vorbereitet/<name>.png)',
             'Iterationsbild.aus_vorlage("<Foto auf weißem Grund>", (256, 384))    # Figur = merklich nicht weiß',
             'Iterationsbild.abbildung(maske)                                     # (cx, y0, y1) der Figur in einer Maske oder None',
         )),
         [(D + 'iterationsbild.py', 'Iterationsbild')],
         'Der zweite Parameter ist (Breite, Höhe) der Fläche; ohne ihn 128 × 192. Beide Bilder werden an der Figur ausgerichtet, nicht am '
         'Bildrand: Höhe vom höchsten Punkt bis zu den Füßen mit 3 % Rand (RAND), waagerecht auf den Schwerpunkt des Rumpfbands (30–70 % '
         'der Figurhöhe). Wie groß die Figur im Foto ist, spielt keine Rolle. Ergebnis: .farbe (H, B, 3) float 0–1, .maske (H, B) bool, '
         '.als_bild() für Tafeln. aus_vorlage zählt als Figur, was von Weiß abweicht (Kanalsumme mehr als 40 unter 765); ein Foto mit Zimmer '
         'dahinter ist dann ganz „Figur“ (IoU 0,32 gegen den Flur, engine2d3dkleider.md, 30.09.2026) — das freigestellte vorbereitet/<name>.png '
         'nehmen (Iterationsreferenz.bild tut das). Eine Zeile oder Spalte zählt erst ab 3 Figurpixeln (MINDESTENS).'),

        ('Note eines Foto-Render-Paars: Umriss und Farbe',
         'Der kleinste Einzelvergleich: ein Foto gegen einen fertigen Render, ohne Server, ohne GPU, ohne Runde.',
         'python',
         '\n'.join((
             'import sys; sys.path.insert(0, "A:/3DTools/HumanBodyWeb")',
             'from core.dienste.iterationsbild import Iterationsbild',
             'from core.dienste.iterationsnote import Iterationsnote',
             'g = (256, 384)    # (Breite, Höhe) der Fläche, Höhe = Breite × 1,5 (Aufloesungsstufe.groesse)',
             'foto = Iterationsbild.aus_render("<auftrag>/vorbereitet/vorne.png", g)',
             'render = Iterationsbild.aus_render("<auftrag>/iterationen/runde_007_ansicht_+000.png", g)',
             'Iterationsnote.vergleichen(foto, render)    # → {"iou": 0…1, "farbe": 0…1, "abweichung": (1 − iou) + farbe}',
         )),
         [(D + 'iterationsnote.py', 'Iterationsnote'), (D + 'iterationsbild.py', 'Iterationsbild')],
         'abweichung = (1 − IoU des Umrisses) + FARBGEWICHT (1,0) · Farbabweichung; 0 = deckungsgleich, höchstens 2. Farbe: mittlerer '
         'RGB-Unterschied (0–1) über ein Raster von Feldern, in denen BEIDE Bilder mindestens 40 % Figur haben (DECKUNG); je Feld zählt '
         'der Mittelwert der Figurpixel, also Farbflächen, keine Falten. Ohne gemeinsames Feld ist die Farbe 1,0. Das Raster wächst mit '
         'der Fläche (Zeile „Farbraster“ in der Gruppe „Auflösungsstufen“). Renders einer Runde liegen als runde_NNN_ansicht_±WWW.png in '
         'iterationen/, auf die Figur zugeschnitten — die Normierung rechnet das heraus; die Auflösung des Renders (Vorgabe mindestens 384 '
         'px breit) begrenzt die Fläche. Kosten je Ansicht: 128 px 0,003 s, 512 px 0,05 s, 2485 px (155 × 233 Felder) 1,1 s (Docstring '
         'Iterationsnote._farbe, 02.10.2026). Probe am 03.10.2026 (nur Lesen, Millisekunden): vorbereitet/vorne.png gegen runde_024_ansicht_+000.png '
         'des Auftrags 2026.10.01.20.10.04 gab bei 128 × 192 IoU 0,8182, Farbe 0,0492, abweichung 0,231 und bei 256 × 384 IoU 0,8221, Farbe '
         '0,0629, abweichung 0,2408 (Wegwerfskript ProjektTemp/_wegwerf/tools_seite/t4/pruefen.py --probe).'),

        ('Note über mehrere Ansichten mitteln',
         'Fasst die Noten je Blickwinkel zu einer Fotonote zusammen, gewichtet nach dem Gewicht der Fotos.',
         'python',
         '\n'.join((
             'Iterationsnote.gesamt_getrennt([(gewicht, note, farbe_zaehlt), …])   # was die Runde benutzt → {abweichung, iou, farbe}',
             'Iterationsnote.gesamt([(gewicht, note), …])                          # ältere Fassung der Optimierer-Schleife',
         )),
         [(D + 'iterationsnote.py', 'Iterationsnote')],
         'gewicht ist Iterationsreferenz.gewicht (Foto-Gewicht ÷ 100), note das Ergebnis von vergleichen(). gesamt_getrennt mittelt den Umriss '
         'über ALLE Ansichten, die Farbe nur über die Fotos mit farbe_zaehlt — ein Foto mit anderer Kleidung zählt nur für die Form; bleibt '
         'keines mit Farbe, mittelt auch die Farbe über alle. Das Ergebnis ist note.foto der Runde. Quelle: Docstring und Code von '
         'Iterationsnote.'),

        ('Netznote: Abstand zum Netz aus den Fotos',
         'Misst das Modell in 3D gegen das TRELLIS-Netz (Bezugsnetz): wie weit stehen Stoff und Haar ab, wie viel vom Netz ist gedeckt.',
         'python',
         '\n'.join((
             'from core.dienste.iterationsnetznote import Iterationsnetznote',
             'netznote = Iterationsnetznote.laden(ablage)   # None ohne arbeit/bezugsnetz.glb',
             'netznote.vergleichen(teile)                   # teile = Kleidermodellbau.teile(modell)',
             "# → {'modell_mm', 'koerper_mm', 'deckung': 0…1, 'abweichung': modell_mm / 50 + (1 − deckung)}",
         )),
         [(D + 'iterationsnetznote.py', 'Iterationsnetznote'), ABLAGE],
         'modell_mm: mittlerer Abstand der Kleider- und Haarpunkte zur Netzoberfläche; koerper_mm dasselbe für den Körper; deckung: Anteil '
         'der Netzproben, die näher als 15 mm (NAH_M) an einem Modellpunkt liegen. 60.000 Proben (PROBEN), fest gesät (SAAT 20260930), damit '
         'zwei Runden vergleichbar bleiben; 50 mm Abstand zählen so viel wie eine ganz fehlende Deckung (MASS_MM). Das Netz kommt in der '
         'Lage der Erkennung (arbeit/bezugsnetz_lage.npz). Die Netznote geht NICHT in die Gesamtnote ein: Der Körper lag in jeder .51-Runde '
         'im Mittel 87,9 mm neben dem Netz (Pose; Docstring Gesamtnote, 01.10.2026). Sie steckt aber in note.abweichung (NETZGEWICHT 1,0), '
         'der Spalte „Abweichung“ der Tabelle. Kosten: nicht einzeln gemessen; sie liegt im Abschnitt „Rendern 3 von 3“ (12,6–14,7 s '
         'kalt, mit Befund, Messgüte und Gesichtsmaßen; Workflowzeiten.RENDERN_3, auftrag.log …20.10.04).'),

        ('Gesamtnote einer Runde',
         'Eine Zahl je Runde: Fotonote plus Farbe je Teil plus Gesicht plus Kopfhaar. An ihr hängt die Wahl der besten Runde.',
         'python',
         '\n'.join((
             'from iterationen2d3d.gesamtnote import Gesamtnote',
             'Gesamtnote.berechnen(note, befund)   # → {gesamt, foto, farbe_teile, gesicht, haar}, auf 4 Stellen gerundet',
         )),
         [(P + 'gesamtnote.py', 'Gesamtnote'), (D + 'begutachtungsstand.py', 'Begutachtungsstand')],
         'gesamt = foto + farbe_teile + gesicht + haar. farbe_teile: mittlerer Farbfehler je Kanal unter der Maske jedes Kleidungs- und '
         'Haarteils, nach Pixeln gewichtet (befund.teile); gesicht: mittlere Abweichung |Foto ÷ Render − 1| der Gesichtsmaße '
         '(befund.gesicht.verhaeltnis); haar: HAAR (0,25, gesetzt, nicht gemessen) mal der Fehler des Kopfhaars (befund.haarabgleich.fehler). '
         'Ohne Netznote (siehe oben). Die Tabelle der Runden zeigt note.abweichung (Foto plus Netz), nicht die Gesamtnote; sie steht nur in '
         'der Notiz der Runde und in note.gesamt (Architektur2d3dmessung.OFFEN, 02.10.2026; der Tooltip der Spalte nennt nur „(1 − '
         'Umriss-IoU) + Farbabstand“).'),

        ('Welche Runde zählt: Rundenauswahl',
         'Ordnet jede gerechnete Runde ein: besser (neue beste Runde), Probe, verworfen — nach der Gesamtnote.',
         'python',
         '\n'.join((
             'from iterationen2d3d.rundenauswahl import Rundenauswahl',
             'auswahl = Rundenauswahl(kreislauf.get("auswahl"))',
             'aktion, weiter = auswahl.nach_runde(runde, gesamt, rezeptzeilen)   # aktion: besser | probe | verworfen | probe_verworfen',
         )),
         [(P + 'rundenauswahl.py', 'Rundenauswahl'), (D + 'begutachtungsstand.py', 'Begutachtungsstand')],
         'besser: Gesamtnote kleiner als die beste um mehr als 0,002 (TOLERANZ), oder eine Pflichtzeile (Fotostück, erkannte Uhr, Bart), '
         'oder ein reiner Farbschritt, der nicht schlechter ist (FARB_RAUSCHEN 0,0005). probe: nicht besser, aber das Rezept baut um '
         '(STRUKTUR: Stück an/aus, Frisur, Umfärben, Fotoprojektion, Haltung …) — bis zu 3 Runden (PROBE_RUNDEN) von der neuen Lage aus. '
         'verworfen: zurück zur besten Runde, die Zeilen sind für diese Lage gesperrt. Ein Rezept ohne Zeilen ist daher „verworfen“, wenn '
         'es nicht um mehr als 0,002 besser ausfällt (so gelesen, nicht ausprobiert). Der Stand des Auftrags (kreislauf.modell, Bühne, '
         'Export, Film) ist immer die BESTE Runde. Quelle: Docstring Rundenauswahl, 01.10.2026.'),

        ('Noten und Maße einer Runde lesen',
         'Wo im Zustand eines Auftrags die Zahlen jeder Runde stehen — je Blickwinkel, gesamt, Netz, Teilnoten.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/<id>/zustand/',
             'ergebnis.iterationen[i].note         {abweichung, iou, farbe, foto, netz: {modell_mm, koerper_mm, deckung, abweichung},',
             '                                       gesamt, teilnoten: {gesamt, foto, farbe_teile, gesicht, haar}}',
             'ergebnis.iterationen[i].je_ansicht   [{original, winkel, iou, farbe, render}]   # je Foto',
             'ergebnis.kreislauf                   {runde_bester, auswahl, verlauf, note, befund, aufloesung, …}',
         )),
         [(A + 'engine2d3dkleider.py', 'Engine2d3dKleiderendpunkte'), (D + 'engine2d3dkleiderzustand.py', 'Engine2d3dKleiderzustand'),
          (D + 'begutachtungsrunde.py', 'Begutachtungsrunde'), (D + 'begutachtungsstand.py', 'Begutachtungsstand')],
         'note.abweichung = Fotonote + 1,0 · Netznote; note.foto = die Fotonote allein (gewichtetes gesamt_getrennt: abweichung, iou, '
         'farbe stehen daneben); note.gesamt und teilnoten stellt Begutachtungsstand.fortschreiben dazu. Je Runde zusätzlich: dateien '
         '{vergleich, kopf, formbezug}, aufloesung (Breite der Notenfläche), auswahl {aktion, beste, gesamt}, befund, rezept, fehler. '
         'Der Zustand ist ein großes JSON (Befund und Werte jeder Runde); die Seite fragt ihn alle zwei Sekunden. Quelle: '
         'Begutachtungsrunde._ablegen und Engine2d3dKleiderzustand.von.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Begutachtungsrunde', 'ruft', 'Iterationsnote', 'vergleichen() je Ansicht, gesamt_getrennt() über die Ansichten'),
        ('Begutachtungsrunde', 'ruft', 'Iterationsnetznote', 'laden(ablage), vergleichen(teile)'),
        ('Begutachtungsrunde', 'ruft', 'Begutachtungsstand', 'fortschreiben(): Gesamtnote, Rundenauswahl, Stand des Kreislaufs'),
        ('Begutachtungsstand', 'ruft', 'Gesamtnote', 'berechnen(note, befund)'),
        ('Begutachtungsstand', 'ruft', 'Rundenauswahl', 'nach_runde(runde, gesamt, rezept), filtern(), pflicht()'),
        ('Iterationsnote', 'ruft', 'Iterationsbild', 'liest .maske und .farbe zweier Iterationsbild (keine Methode)'),
        ('Iterationsnetznote', 'ruft', 'Engine2d3dKleiderablage', 'bezugsnetz(), arbeit(): Netz, Lage, Flächenlabels'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderzustand', 'von(job): ergebnis samt iterationen[] und kreislauf'),
    ]
