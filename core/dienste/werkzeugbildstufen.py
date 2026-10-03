# -*- coding: utf-8 -*-
"""Werkzeugbildstufen — Gruppe „Bildvergleich: Auflösungsstufen (klein zuerst)“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code: `Aufloesungsstufe` (Regel, Schwellen), `Iterationsnote.felder`,
`Begutachtungsrunde.ausfuehren/_runde`, `Begutachtungsstand.fortschreiben`, `Iterationsoptionen.KATALOG`. Gelaufen ist hier nichts.
"""

__all__ = ['Werkzeugbildstufen']


class Werkzeugbildstufen:
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    STUFE = ('HumanBodyWeb/core/dienste/aufloesungsstufe.py', 'Aufloesungsstufe')
    KENNUNG = 'bildstufen'
    TITEL = 'Bildvergleich: Auflösungsstufen (klein zuerst)'
    EINLEITUNG = (
        'Edgars Vorgabe (02.10.2026): erst der gering auflösende Vergleich, höhere Auflösung erst, wenn die Unterschiede klein sind. Im Code '
        'ist das die Note auf einer kleinen Fläche (Aufloesungsstufe.START = 128 × 192, Farbraster 8 × 12); „Template-Vergleich“ ist Edgars '
        'Wort, im Code kommt es nicht vor — so gedeutet. Reihenfolge: 1. Start auf 128 px Breite, 2. steht die Stufe still (3 Runden ohne '
        'Besserung) oder findet die Automatik nichts mehr, verdoppelt die nächste Runde die Breite (Messrunde ohne Rezept), 3. so weiter bis '
        'zur Auflösung der Figur im kleinsten Farbfoto. Wichtig: Die Stufe steigt nur in Blöcken AUTOMATISCHER Runden, nie in Runden mit '
        'einem Rezept von Hand (Zeile 8).'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Die Stufenregel: klein zuerst, dann verdoppeln',
         'Wann die Note feiner misst und bis wohin — Regel, Schwellen und Quelle.',
         'regel',
         'Kein Aufruf. Stufe 0 = Option iterationen.bildbreite (Vorgabe 128 px Breite, Höhe = round(1,5 × Breite) = 192, Farbraster 8 × 12). '
         'Weiter: Breite × 2 (FAKTOR), höchstens bis zur Auflösung der Figur im kleinsten Farbfoto.',
         [STUFE, (D + 'begutachtungsrunde.py', 'Begutachtungsrunde'), (D + 'iterationsoptionen.py', 'Iterationsoptionen')],
         'Auslöser (Aufloesungsstufe.faellig, Begutachtungsrunde.ausfuehren): (a) iterationen.stufe_stillstand Runden der Stufe in Folge ohne '
         'auswahl.aktion = besser (Vorgabe 3, STILLSTAND; die Messrunde zählt nicht) oder (b) die Automatik findet keinen Rezeptschritt mehr '
         '— dort endete der Lauf früher. Höchste Stufe: Figurhöhe in Pixeln im freigestellten Foto (vorbereitet/<name>.png, Alpha > 127), '
         'Breite = Höhe ÷ (1 − 2 · 0,03) ÷ 1,5, vom kleinsten der Farbfotos, mindestens die Startbreite — darüber erfände das Hochrechnen '
         'der Vorlage nur Unschärfe. Am Auftrag 2026.10.01.20.10.04 sind das 2485 px (Architektur2d3d.REGELN, Workflowrunde). Quelle der '
         'Regel: Docstring Aufloesungsstufe; Edgar, 02.10.2026: „am Anfang der Iterationen kleinere Auflösung, und wenn nicht genügend Details '
         'vorhanden sind für Verbesserung, höhere Auflösung … immer höher bis zur maximalen Auflösung, in der die Vorlagen vorhanden sind“. '
         'Was die kleine Stufe sieht: ein Bildpunkt ≈ 1 cm bei 192 px Flächenhöhe (Docstrings Bandbreite und Sichtkoerper) — Lippe, Säume und '
         'Ausschnitt sind dort 1–3 Pixel groß (engine2d3dkleider.md, 02.10.2026: „Tempo nie auf Kosten dessen, was die Prüfung sehen '
         'muss“). Die kleine Stufe ist für grobe Fehler da (Umriss, Farbflächen, Stücke an/aus), nicht für Feinheiten. Gerendert wird in der '
         'größeren von Stufe und Prüfbreite (tafelbreite, Vorgabe 384); der Befund rechnet immer auf 128 × 192 (Begutachtungsrunde._runde).'),

        ('Stufe eines Auftrags lesen',
         'Welche Auflösung die Note gerade hat und wann sie gestiegen ist.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/<id>/zustand/',
             'ergebnis.kreislauf.aufloesung          # laufende Breite; fehlt, solange keine Stufe gewechselt wurde (dann gilt bildbreite)',
             'ergebnis.kreislauf.aufloesung_seit     # erste Runde der Stufe',
             'ergebnis.kreislauf.aufloesung_max      # höchste Breite (erst gemerkt, wenn hoechste() gerufen wurde)',
             'ergebnis.kreislauf.aufloesung_verlauf  # [[runde, breite, grund], …]',
             'ergebnis.iterationen[i].aufloesung     # Breite der Notenfläche dieser Runde',
         )),
         [(A + 'engine2d3dkleider.py', 'Engine2d3dKleiderendpunkte'), (D + 'engine2d3dkleiderzustand.py', 'Engine2d3dKleiderzustand'), STUFE],
         'Eine Note ist nur mit Noten derselben Breite vergleichbar. Die Fotonote, die in der Spalte „Abweichung“ der Rundentabelle steckt, '
         'ist eine Note dieser Breite. Felder aus dem Docstring Aufloesungsstufe („Zustand im Kreislauf“) und aus Begutachtungsrunde._ablegen. Quelle der Adresse: '
         'core/urls_engine2d3dkleider.py.'),

        ('Start-Auflösung, Stillstand und Prüfbreite einstellen',
         'Die drei Optionen der Gruppe „iterationen“, die Stufen und Prüfbilder steuern.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/einstellungen/',
             '{"optionen": {"iterationen": {"bildbreite": 128, "stufe_stillstand": 3, "tafelbreite": 384}}}',
             '→ {ok, optionen}      # 409 „Der Auftrag läuft — Änderungen erst nach dem Lauf“',
         )),
         [(A + 'engine2d3dkleidereinstellungen.py', 'Engine2d3dKleidereinstellungen'),
          (D + 'engine2d3dkleideroptionen.py', 'Engine2d3dKleideroptionen'), (D + 'iterationsoptionen.py', 'Iterationsoptionen')],
         'bildbreite: Breite der ersten Stufe, 96–1024 (Vorgabe 128); stufe_stillstand: Runden ohne Besserung bis zur nächsten Stufe, 1–100 '
         '(Vorgabe 3); tafelbreite: Mindestbreite je Blickwinkel der Vergleichstafel und der Renders, 128–1024 (Vorgabe 384; die Kopftafel '
         'bleibt 384 × 384). Werte außerhalb der Grenzen werden verworfen (Vorgabe bleibt). Es genügt, die Gruppe zu schicken, die man ändert '
         '(Engine2d3dKleideroptionen.mischen). Hat der Auftrag schon eine Stufe gewechselt, hat kreislauf.aufloesung Vorrang vor '
         'bildbreite (Zeile 8). Der Server speichert nicht während eines Laufs. Quelle: Iterationsoptionen.KATALOG, '
         'Engine2d3dKleidereinstellungen.'),

        ('Stufe abfragen und wechseln',
         'Die Methoden der Stufenregel: laufende, höchste und nächste Breite, Stillstand, Wechsel.',
         'python',
         '\n'.join((
             'from core.dienste.aufloesungsstufe import Aufloesungsstufe',
             "stufe = Aufloesungsstufe(job, ablage, job.optionen.get('iterationen'))",
             "z = job.ergebnis['kreislauf']                 # hoechste() ergänzt z im Speicher (aufloesung_max) — nicht zurückschreiben",
             'referenzen, _ = Iterationsreferenz.laden(job)',
             'stufe.breite(z)                 # laufende Breite (z["aufloesung"] oder die Startbreite)',
             'stufe.hoechste(z, referenzen)   # größte Breite, die die Farbfotos tragen',
             'stufe.stillstand(z)             # Runden der laufenden Stufe in Folge ohne „besser“',
             'stufe.faellig(z, referenzen)    # Breite der nächsten Stufe, wenn die laufende stillsteht, sonst None',
             'stufe.naechste(z, referenzen)   # nächste Breite oder None (schon die höchste)',
             'Aufloesungsstufe.groesse(256)   # → (256, 384)',
         )),
         [STUFE, (D + 'iterationsreferenz.py', 'Iterationsreferenz'), (D + 'iterationsbild.py', 'Iterationsbild')],
         'Zum Nachsehen gedacht. steigen(z, neu, runde, grund) wechselt die Stufe wirklich (schreibt aufloesung, aufloesung_seit und '
         'aufloesung_verlauf in z und liefert die Kommentarzeile der Messrunde) — das gehört dem Lauf (Begutachtungsrunde.ausfuehren), '
         'von Hand nicht rufen. hoechste() liest die Fotos (Figurhöhe aus vorbereitet/<name>.png): kostet pro Foto das Öffnen eines PNG, '
         'nicht gemessen. Quelle: Aufloesungsstufe (Docstring und Code).'),

        ('Vorlage auf der Fläche der Stufe',
         'Das Foto in der Auflösung der Stufe — je Lauf und Breite einmal gelesen.',
         'python',
         '\n'.join((
             'stufe.vorlage(referenz, 256)   # → Iterationsbild des Fotos auf 256 × 384; referenz aus Iterationsreferenz.laden',
         )),
         [STUFE, (D + 'iterationsreferenz.py', 'Iterationsreferenz')],
         'Bei Breite 128 kommt die schon geladene referenz.bild; sonst Iterationsreferenz.bild(ablage, datei, groesse(breite)) (freigestelltes '
         'vorbereitet/<name>.png, sonst das Foto auf Weiß). Zwischenspeicher je (Datei, Breite) im Stufen-Objekt, also je Lauf. Das Gegenstück '
         'ist der Render in derselben Breite: Iterationsbild.aus_render(pfad, Aufloesungsstufe.groesse(breite)).'),

        ('Farbraster der Stufe',
         'Wie viele Felder der Farbvergleich je Fläche hat — das Raster wächst mit der Auflösung.',
         'python',
         '\n'.join((
             'Iterationsnote.felder(breite, hoehe)   # → (Spalten, Zeilen)',
             '# 128 × 192 → (8, 12);  256 × 384 → (16, 24);  512 × 768 → (32, 48);  2485 × 3728 → (155, 233)',
         )),
         [(D + 'iterationsnote.py', 'Iterationsnote')],
         'Rechnung: max(8, round(8 · Breite ÷ 128)) Spalten, max(12, round(12 · Höhe ÷ 192)) Zeilen. Mit festen 8 × 12 Feldern sähe die Note '
         'auch auf 1024 px nur Flächenmittel, und eine höhere Stufe brächte keine Einzelheit (Docstring Iterationsnote.felder, 02.10.2026). '
         'Die Rechenzeit der Farbe je Ansicht: 128 px 0,003 s, 512 px 0,05 s, 2485 px 1,1 s (Docstring Iterationsnote._farbe, 02.10.2026). '
         'Die Beispiele sind aus der Formel gerechnet; 2485 × 3728 steht so im Docstring.'),

        ('Messrunde nach einem Stufenwechsel',
         'Was bei jedem Wechsel passiert: keine Änderung am Modell, nur neu messen — die Note der neuen Stufe ist die neue Bezugsnote.',
         'regel',
         'Kein Aufruf. Die nächste Runde nach dem Wechsel hat kein Rezept, nur den Kommentar „# Auflösung a → b px (Grund): die beste '
         'Runde neu gemessen“.',
         [(D + 'begutachtungsrunde.py', 'Begutachtungsrunde'), (D + 'begutachtungsstand.py', 'Begutachtungsstand'), STUFE],
         'Das Modell der Messrunde ist die beste Runde (eine laufende Probe wird verworfen); Begutachtungsstand.fortschreiben setzt wegen '
         'naechste.messrunde beste Runde, Probe und gesperrte Zeilen zurück — eine Note auf 512 px ist mit einer auf 128 px nicht '
         'vergleichbar. Auch ein „fertig“ der Automatik (keine Änderung mehr) führt erst in die nächste Stufe, ehe der Lauf endet; nur auf '
         'der höchsten Stufe endet er („Fertig · beste Runde N“). Während einer Probe (kreislauf.weiter) wechselt die Stufe nicht. Quelle: '
         'Begutachtungsrunde.ausfuehren, Begutachtungsstand.fortschreiben.'),

        ('Von Hand gerechnete Runden steigen nie von selbst',
         'Die Falle der Stufenregel: Sie greift nur im automatischen Block.',
         'regel',
         'Kein Aufruf. Aufloesungsstufe.faellig und steigen stehen in Begutachtungsrunde.ausfuehren unter „if naechste.get(\'automatisch\')“.',
         [(D + 'begutachtungsrunde.py', 'Begutachtungsrunde'), STUFE],
         'In Runden mit Rezept von Hand und in „Weiter iterieren“ bleibt die Breite, wie sie ist: kreislauf.aufloesung, sonst die Option '
         'bildbreite. Wer von Hand feiner messen will, kann bildbreite ändern — nur solange noch keine Stufe gewechselt wurde; danach hat '
         'kreislauf.aufloesung Vorrang (Aufloesungsstufe.breite). Gelesen, nicht ausprobiert: Beim Ändern von bildbreite setzt kein Code die '
         'beste Runde zurück (das tut nur die Messrunde der Automatik); Noten vor und nach der Änderung sind dann nicht vergleichbar. '
         'Quelle: Begutachtungsrunde.ausfuehren, Aufloesungsstufe.breite.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Begutachtungsrunde', 'ruft', 'Aufloesungsstufe', 'breite(), faellig(), naechste(), steigen(), vorlage(), groesse()'),
        ('Begutachtungsrunde', 'ruft', 'Iterationsnote', 'vergleichen(vorlage, fein): die Note in der Stufe'),
        ('Begutachtungsrunde', 'ruft', 'Begutachtungsstand', 'fortschreiben(): bei messrunde werden beste Runde, Probe und Sperren geleert'),
        ('Aufloesungsstufe', 'ruft', 'Iterationsreferenz', 'bild(ablage, datei, groesse): Vorlage auf der Fläche der Stufe'),
        ('Aufloesungsstufe', 'ruft', 'Iterationsbild', 'abbildung(maske), RAND: Figurhöhe im Foto → höchste Stufe'),
        ('Engine2d3dKleidereinstellungen', 'ruft', 'Engine2d3dKleideroptionen', 'mischen(), pruefen(): Optionen speichern'),
        ('Engine2d3dKleideroptionen', 'ruft', 'Iterationsoptionen', 'KATALOG, pruefen(): bildbreite, stufe_stillstand, tafelbreite'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderzustand', 'von(job): ergebnis.kreislauf mit aufloesung_*'),
    ]
