# -*- coding: utf-8 -*-
"""Architekturmesh3daibildkasten — der Kasten unten links in der Grafik von Hilfe → Architektur → Mesh3DAI (`Architekturmesh3daibild`).

Am 17.10.2026 abends aus `architekturmesh3daibild.py` gelöst (die Datei wäre über 300 Zeilen gewachsen). Zwei Fassungen:
`kette` — die Vorstufe läuft VOR dem Netz (seit 17.10.2026), je Schritt ein Kasten mit Eingabe, was passiert, Ausgabe;
`rig` — der Stand vom 16.10.2026, als die Rig-Generierung nur NEBEN dem Netz lief (grau, ohne Pfeil).
`bild` ist die Klasse `Architekturmesh3daibild` (Lage der Spalten, Farben, Pfeil) — als Argument, damit kein Kreisimport entsteht.
"""

from django.utils.html import escape

__all__ = ['Architekturmesh3daibildkasten']


def _de(n, stellen=0):
    from .architekturmesh3daibild import _de as de
    return de(n, stellen)


class Architekturmesh3daibildkasten:
    #: Je Schritt der Kette (Titel, nach dem Netz?, ((Marke, (Zeilen …)), …)). Edgar, 17.10.2026 abends: „Schreib doch einfach hinein, was du tust. Was die Eingabe ist, was die Ausgabe ist.“
    #: (vorher je Kasten zwei Stichworte, „liegt das Netz? dann aufrichten“). Inhalt nach `mesh3dai_vorstufe*.py` (`mesh3dai-vorstufe.md`). Zeilen höchstens ~28 Zeichen (Kasten 206 px, Schrift 12).
    KETTE = (
        ('1 Lage', False, (('Eingabe', ('das Netz aus der Datei', '(Punkte, Dreiecke, Farbe)')),
                           ('Was passiert', ('liegt es (schräg UND flach)?', 'dann aufrichten, Füße auf 0')),
                           ('Ausgabe', ('dasselbe Netz, aufrecht',)))),
        ('2 Rig', False, (('Eingabe', ('das aufrechte Netz',)),
                          ('Was passiert', ('Mesh-3D „Nur Rig“ passt eine', 'Genesis-Figur an', '(einmal je Netzdatei)')),
                          ('Ausgabe', ('Rig-Figur: 138 Gelenke und', 'Haut, in Ruhe und Haltung')))),
        ('3 A-Pose', False, (('Eingabe', ('Netz + Rig-Figur',)),
                             ('Was passiert', ('jeder Punkt dreht mit', 'seinem Knochen zurück', 'in die A-Pose')),
                             ('Ausgabe', ('Punktwolke mit Farbe in', 'der A-Pose → ins Netz')))),
        ('4 Zurück — nach dem Netz', True, (('Eingabe', ('138 Gelenke in der A-Pose', '(Ausgabe des Netzes)')),
                                            ('Was passiert', ('mit dem Rig zurück in die', 'Haltung, Daz-Winkel anpassen')),
                                            ('Ausgabe', ('Skelett in der Haltung', '(über 60 mm vom Rig:', 'Rig allein)')))),
    )
    #: Höhe eines Schrittkastens und Unterkante des ganzen Kastens — er reicht tiefer als die Formreihe (`Architekturmesh3daibild.FORM_UNTEN` 770).
    HOEHE = 200
    UNTEN = 600 + 42 + HOEHE + 40

    @classmethod
    def kette(cls, bild, teile, kette):
        """Unten links, MIT Pfeil in die Eingabe: seit 17.10.2026 läuft die Vorstufe vor dem Netz (Edgar: „warum macht die Pipeline das nicht, als erstes das Mesh zu riggen und in die A-Pose zu übertragen??“ →
        „baue das ein!“). Schritt 4 läuft NACH dem Netz (grau, gestrichelt). Zahlen aus `Architekturmesh3daikette.kontext`."""
        x, oben, breite = 20, bild.FORM_OBEN, bild._x(5) + 40
        m = kette.get('mittel') or {}
        fuell, rand = bild.FARBEN['eingabe']
        teile.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s"/>' % (x, oben, breite, cls.UNTEN - oben, fuell, rand))
        teile.append('<text x="%d" y="%d" font-size="15" font-weight="600" fill="#222">Vorstufe (Abschnitt 1) — was jeder Schritt bekommt, tut und abgibt</text>' % (x + 16, oben + 26))
        kb, abstand, k_oben, k_hoehe = 206, 18, oben + 42, cls.HOEHE
        for i, (titel, danach, abschnitte) in enumerate(cls.KETTE):
            kx = x + 16 + i * (kb + abstand)
            teile.append('<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="%s" stroke="%s"%s/>'
                         % (kx, k_oben, kb, k_hoehe, bild.FARBEN['danach'][0] if danach else '#ffffff', rand, ' stroke-dasharray="6 4"' if danach else ''))
            teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="14" font-weight="600" fill="#222">%s</text>' % (kx + kb / 2, k_oben + 20, escape(titel)))
            y = k_oben + 20
            for marke, zeilen in abschnitte:
                y += 20
                teile.append('<text x="%d" y="%d" font-size="12" font-weight="700" fill="%s">%s</text>' % (kx + 8, y, bild.ZAHLFARBE, escape(marke)))
                for text in zeilen:
                    y += 15
                    teile.append('<text x="%d" y="%d" font-size="12" fill="#222">%s</text>' % (kx + 8, y, escape(text)))
            if 0 < i < 3:
                bild._pfeil(teile, kx - abstand + 2, k_oben + k_hoehe / 2, kx - 2, k_oben + k_hoehe / 2)
        # Aus „3 A-Pose“ hinauf in die Eingabe des Netzes.
        ax = x + 16 + 2 * (kb + abstand) + kb / 2
        cx = bild._x(0) + bild.SPALTE / 2
        y_quer = (bild.KASTEN_UNTEN + oben) / 2
        teile.append('<polyline points="%.0f,%d %.0f,%.0f %.0f,%.0f %.0f,%d" fill="none" stroke="#222" stroke-width="2.5" marker-end="url(#m3a-pfeil)"/>'
                     % (ax, k_oben, ax, y_quer, cx, y_quer, cx, bild.KASTEN_UNTEN + 3))
        if all(m.get(k) is not None for k in ('direkt', 'vorstufe', 'rig')):
            teile.append('<text x="%d" y="%d" font-size="13" fill="#222">%s</text>' % (x + 16, cls.UNTEN - 14, escape(
                'Gemessen, %d schwierige Prüfposen, je ein Lauf: Netz direkt Ø %s · Vorstufe Ø %s · Rig allein Ø %s mm'
                % (len(kette.get('posen') or []), _de(m['direkt'], 1), _de(m['vorstufe'], 1), _de(m['rig'], 1)))))

    @classmethod
    def rig(cls, bild, teile, vorstufe):
        """Unten links, grau und OHNE Pfeil: die Rig-Generierung von Mesh-3D lief am 16.10.2026 getrennt vom Netz (Edgar: „ich sehe die Rig-Vorstufe nicht, die wird doch ganz am Anfang gemacht?“).
        Das Netz bekam nur Punkte + Farbe; das Rig wurde nur zum Vergleich gerechnet (Abschnitt 1). Zahlen aus `Architekturmesh3daivorstufe.kontext`."""
        x, oben, breite = 20, bild.FORM_OBEN, bild._x(4) + bild.SPALTE - 20
        mittel = vorstufe.get('mittel') or {}
        netze = [n for n in mittel.get('netze') or [] if n is not None]
        zeilen = [('Rig-Generierung ohne KI (Abschnitt 1) — heute NICHT vor das Netz geschaltet', True),
                  ('Mesh-3D „Nur Rig“: „Mesh to 3D“ passt eine Genesis-Figur an das Netz an, ohne Training%s.'
                   % (', rund %s s je Netz' % _de(vorstufe['gesamt_s']) if vorstufe.get('gesamt_s') else ''), False),
                  ('Kein Pfeil ins Netz: Mesh3D-AI bekommt nur Punkte + Farbe, im Training wie im Test.', False)]
        if mittel.get('rig') is not None and netze:
            zeilen.append(('Gerechnet nur zum Vergleich, %d Proben von Ursula1: Rig Ø %s mm, Netze %s–%s mm (%d Prüfposen).'
                           % (len(vorstufe.get('zeilen') or []), _de(mittel['rig'], 1), _de(min(netze), 1), _de(max(netze), 1), mittel.get('proben', 0)), False))
        zeilen.append(('Als Vorstufe angeschlossen (Startwert, Trainingsziel, Bezug im Test): Vorschlag, nicht gebaut.', False))
        fuell, rand = bild.FARBEN['danach']
        teile.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" stroke-dasharray="6 4"/>' % (x, oben, breite, bild.FORM_UNTEN - oben, fuell, rand))
        for j, (text, fett) in enumerate(zeilen):
            teile.append('<text x="%d" y="%d" font-size="%d"%s fill="#222">%s</text>'
                         % (x + 16, oben + 30 + 28 * j, 15 if fett else 13, ' font-weight="600"' if fett else '', escape(text)))
