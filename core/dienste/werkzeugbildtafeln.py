# -*- coding: utf-8 -*-
"""Werkzeugbildtafeln — Gruppe „Bildvergleich: Prüfbilder (Vergleichstafel und Kopftafel)“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code: `Pruefbilder`, `Iterationstafel`, `Begutachtungsrunde._runde/_ablegen`,
`Engine2d3dKleiderendpunkte.datei`, `Engine2d3dKleiderablage`; die Dateinamen stehen im Ordner eines echten Auftrags
(`3DObjects/engine2d3dkleiderauftraege/2026.10.01.20.10.04/iterationen/`, gelistet am 03.10.2026). Gelaufen ist hier nichts.
"""

__all__ = ['Werkzeugbildtafeln']


class Werkzeugbildtafeln:
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    ABLAGE = ('HumanBodyWeb/core/daten/engine2d3dkleiderablage.py', 'Engine2d3dKleiderablage')
    PRUEF = ('HumanBodyWeb/core/dienste/pruefbilder.py', 'Pruefbilder')
    KENNUNG = 'bildtafeln'
    TITEL = 'Bildvergleich: Prüfbilder (Vergleichstafel und Kopftafel)'
    EINLEITUNG = (
        'Fable prüft am BILD, nicht an der Zahl: Jede Runde legt runde_NNN_vergleich.png (oben die Fotos, unten die Renders aus denselben '
        'Winkeln) und runde_NNN_kopf.png (Kopf aus dem Foto oben, Kopf aus dem Render unten) ab. Reihenfolge: 1. Runde rechnen (Gruppe '
        '„Server-Endpunkte“), 2. beide Bilder ansehen (Zeile 1), 3. benennen, was nicht wie auf dem Foto aussieht, 4. den Code verbessern, der '
        'es erzeugt (die Vorgabe „nach jeder Runde prüft Fable“ steht in der Gruppe „Regeln, Befehle und Seiten“). Die Bilder haben je '
        'Ansicht mindestens 384 px Breite; die Tafel der Note allein (128 × 192) war zu grob für Lippe, Säume und Ausschnitt (Edgar, '
        '02.10.2026; Docstring Pruefbilder).'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Vergleichstafel und Kopftafel einer Runde ansehen',
         'Holt die Bilder einer Runde: Tafel, Kopftafel, einzelne Renders — über den Server oder direkt von der Platte.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/<id>/datei/iterationen/runde_007_vergleich.png      # Fotos oben, Renders unten, je Blickwinkel',
             'GET /api/engine2d3dkleider/<id>/datei/iterationen/runde_007_kopf.png           # Kopf aus dem Foto oben, aus dem Render unten',
             'GET /api/engine2d3dkleider/<id>/datei/iterationen/runde_007_ansicht_+000.png   # ein Render, auf die Figur zugeschnitten',
             'Platte: A:\\3DTools\\3DObjects\\engine2d3dkleiderauftraege\\<kennung>\\iterationen\\runde_007_vergleich.png',
         )),
         [(A + 'engine2d3dkleider.py', 'Engine2d3dKleiderendpunkte'), ABLAGE, (D + 'auftragsdatei.py', 'Auftragsdatei')],
         'Die Nummer ist dreistellig (runde_%03d_…); der Winkel im Namen hat Vorzeichen und drei Stellen (ansicht_+000, ansicht_-090, '
         'ansicht_+180; so liegen sie im Auftrag 2026.10.01.20.10.04). Lesbar '
         'sind die Ordner eingang, vorbereitet, netz, ergebnis, vorlage und iterationen (Engine2d3dKleiderablage.LESBAR); ?laden=1 lädt '
         'herunter, ?v=<kennung> ist die Cache-Kennung. Die Tafel zeigt die Fotos NICHT im Original, sondern auf der Fläche der Note '
         '(freigestellt, auf Weiß, an der Figur ausgerichtet); je Ansicht tafelbreite × 1,5 · tafelbreite (Vorgabe 384 × 576), unter jedem '
         'Paar „±Winkel° IoU 0,xx“ (nur die Umriss-Zahl, nicht die Gesamtnote). Die Renders je Winkel sind auf die Figur zugeschnitten '
         '(Alpha, 4 % Rand; Iterationsrunde.zuschneiden). Eine GLB je Runde gibt es nicht mehr (Edgar, 02.10.2026: 56 MB je Runde); '
         'runde_NNN_modell.glb entsteht nur für die beste Runde am Ende eines Laufs (Begutachtungswerkzeug.bestes_glb). In der Seite: '
         'Auftrag → Reiter „Iterationen“ → Unterzeile „Bilder“ der Runde (Klick öffnet groß, ←/→ blättern).'),

        ('Vergleichstafel bauen',
         'Baut aus vorhandenen Renders und den Vorlagen eines Auftrags die Vergleichstafel — ohne Runde.',
         'python',
         '\n'.join((
             'from pathlib import Path',
             'from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage',
             'from core.dienste.pruefbilder import Pruefbilder',
             "ablage = Engine2d3dKleiderablage('<kennung>')",
             "Pruefbilder(ablage, 384).tafel([(0.0, 'vorne.jpg', Path('<…>/runde_007_ansicht_+000.png'), 0.62)], Path('tafel.png'))",
             '# ansichten = [(winkel, datei der Vorlage, Pfad des Renders, iou)] → ziel oder None',
         )),
         [PRUEF, (D + 'iterationsreferenz.py', 'Iterationsreferenz'), (D + 'iterationsbild.py', 'Iterationsbild'),
          (D + 'iterationstafel.py', 'Iterationstafel')],
         'datei ist bilder[].datei (der Name in eingang/); das Foto kommt als vorbereitet/<name>.png auf die Fläche breite × 1,5 · breite, '
         'der Render wird auf dieselbe Fläche normiert (Iterationsbild.aus_render). iou ist nur die Beschriftung. Fehlt eine Render-Datei, '
         'wird die Ansicht übersprungen; ohne eine einzige Ansicht kommt None. Braucht Django (Ablage in OBJECTS_ROOT), keine GPU. In der '
         'Runde ruft Begutachtungsrunde._ablegen diese Methode (Log-Abschnitt „ablegen“, 5,9–7,1 s kalt; Workflowzeiten.ABLEGEN, auftrag.log '
         '…20.10.04, 02.10.2026). Zusammengesetzt aus den gelesenen Signaturen, als Ganzes nicht ausgeführt.'),

        ('Kleine Tafel aus fertigen Bildpaaren',
         'Der Baustein darunter: Foto oben, Render unten, Winkel und IoU darunter — aus zwei Listen von Iterationsbild.',
         'python',
         '\n'.join((
             'from core.dienste.iterationstafel import Iterationstafel',
             "Iterationstafel.bauen([(winkel, vorlage_bild, render_bild, {'iou': 0.62}), …], Path('tafel.png'))   # → ziel",
         )),
         [(D + 'iterationstafel.py', 'Iterationstafel'), (D + 'iterationsbild.py', 'Iterationsbild')],
         'Die Größe eines Felds ist die der Bilder (Iterationsbild.maske.shape): 128 × 192 wie die Note, 256 × 384 für die Prüf-KI der alten '
         'Optimierer-Schleife, Prüfbreite für die Prüfbilder. Der Alphakanal des Renders wird auf Weiß gelegt (Iterationsbild.als_bild); '
         'dazu Trennlinien und die Beschriftung. note muss den Schlüssel iou tragen. Quelle: Docstring und Code von Iterationstafel.'),

        ('Kopftafel bauen',
         'Je Blickwinkel der Kopf aus dem Foto (oben) gegen den Kopf aus dem Render (unten) — für Mund, Gesicht und Haardeckung.',
         'python',
         '\n'.join((
             'Pruefbilder(ablage, 384).kopf(render, teile, referenzen, modell_hoehe, aus_ordner, Path("kopf.png"))   # → ziel oder None',
             'Pruefbilder(ablage, 384).kopfausschnitt(datei, modell_hoehe, render, 384)   # → (rgb uint8, maske bool) des Foto-Kopfs',
         )),
         [PRUEF, (D + 'genesishaarrender.py', 'Genesishaarrender'), (D + 'iterationstafel.py', 'Iterationstafel')],
         'render ist der offene Genesishaarrender der Runde, teile sind die gehäuteten Teile (Haltung der Fotos), referenzen kommen aus '
         'Iterationsreferenz.laden, modell_hoehe ist der höchste Punkt des Modells in m (kreislauf.modell_hoehe), aus_ordner nimmt die '
         'Zwischenbilder kopf_±WWW.png. Ausschnitt: 0,34 m im Quadrat, Mitte 0,13 m unter dem Scheitel, 384 × 384 je Blickwinkel; das Foto '
         'wird über die Modellhöhe in Meter umgerechnet (Figur im Foto vom Scheitel bis zu den Füßen = modell_hoehe) und waagerecht auf '
         'die Kopfmitte gestellt (Schwerpunkt der Figur bis 2 × 0,13 m unter dem Scheitel). Ohne erkennbare Figur oder Kopf im Foto fehlt '
         'der Blickwinkel in der Tafel (Warnung im Log); ein Fehler hält die Runde nicht auf. Kosten: Log-Abschnitt „Prüfbilder“ 21,1–24,0 s '
         'kalt (vor Runde 20: 7,7–12,9 s; Workflowzeiten.PRUEFBILDER, auftrag.log …20.10.04) — er enthält auch den Haarabgleich. '
         'Widerspruch: Workflowzeiten nennt dort auch die Vergleichstafel; im Code läuft sie erst in _ablegen (Abschnitt „ablegen“).'),

        ('Worauf man auf den Tafeln achtet',
         'Die Prüfliste der Vorgabe „nach jeder Runde prüft Fable“: Teil für Teil, mit Ort (Blickwinkel, Körperteil).',
         'regel',
         'Kein Aufruf. Teil für Teil: Umriss, Kleider (Säume, Ausschnitt, Risse, Länge), Haut, Gesicht und Mund, Haar (Deckung, Farbe je '
         'Zone), Zubehör (Architektur2d3d.PRUEFSCHLEIFE, Schritt 2).',
         [(D + 'begutachtungsrunde.py', 'Begutachtungsrunde'), PRUEF],
         'Die Tafel zeigt, was die Note sieht (dieselbe Fläche, nur größer); Rückseiten und Bewegung zeigt sie nicht. Erst prüfen, ob die '
         'Messung den Fehler überhaupt SEHEN kann (Edgar, 02.10.2026; engine2d3dkleider.md) — deshalb gibt es die Kopftafel und Prüfbilder '
         'ab 384 px. Mund geschlossen: Mimikregler (Lip Part, Lip Gaps, Mouth Opening) werden beim Lesen der Stellung gefiltert '
         '(Meshfigurregler.ohne_mimik; Architektur2d3d.REGELN). Ein Hintergrundrest im Foto ist kein Fehler des Modells: Die Vorlage ist das '
         'freigestellte vorbereitet/<name>.png. Fehler werden im CODE behoben, der sie erzeugt (2d3DIterationen/, Genesis9/, core/dienste/), '
         'nur bei einem Einzelfall per Rezept (Architektur2d3d.PRUEFSCHLEIFE, Schritt 4).'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Pruefbilder', 'ruft', 'Iterationstafel', 'bauen(paare, ziel); TRENNER: Foto oben, Render unten'),
        ('Pruefbilder', 'ruft', 'Iterationsreferenz', 'bild(ablage, datei, groesse): das Foto auf der Fläche der Tafel'),
        ('Pruefbilder', 'ruft', 'Iterationsbild', 'aus_render(pfad, groesse), abbildung(maske): Render und Figurhöhe im Foto'),
        ('Pruefbilder', 'ruft', 'Genesishaarrender', 'bild_kopf(): der Render-Kopf; KOPF_HOEHE, KOPF_UNTER_SCHEITEL'),
        ('Iterationstafel', 'ruft', 'Iterationsbild', 'als_bild(): Farbe auf weißem Grund'),
        ('Begutachtungsrunde', 'ruft', 'Pruefbilder', 'kopf() im Abschnitt „Prüfbilder“, tafel() in _ablegen()'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderablage',
         'datei(ordner, name): Pfadprüfung, nur eingang, vorbereitet, netz, ergebnis, vorlage, iterationen'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Auftragsdatei', 'antwort(request, pfad, …): liefert die Datei'),
    ]
