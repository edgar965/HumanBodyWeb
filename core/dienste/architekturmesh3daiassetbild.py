# -*- coding: utf-8 -*-
"""Architekturmesh3daiassetbild — Grafik „Neuronales Netz für Assets“ im Abschnitt Kleider-GarmentCode (Hilfe → Architektur → Mesh3DAI, 20.10.2026).

Edgar: „Im Abschnitt Kleider Garment Code mach eine zweite Grafik: ‚Neuronales Netz für Assets‘, darin dein Vorschlag für die KI für Kleider, Haare und was sonst noch an Assets da ist“.
Ein Ablaufbild, kein Schichtbild: links die gemeinsame Kette (Eingabe, Vorstufe, Zerlegungsnetz, Ausschneiden), rechts je Art ein Weg. Farben wie im Bild „Neuronales Netz – Figur“
(`Architekturmesh3daibild.FARBEN`): blau = neuronales Netz, grau = Rechnung, rot = Eingabe; durchgezogen = gebaut, gestrichelt und weiß = Vorschlag. Was „gebaut“ heißt, belegen die Tabellen
des Abschnitts; die Grafik nennt keine Zahl, die dort nicht steht.

21.10.2026 abends neu gezeichnet (Edgar: „diese Grafik ist nicht mehr aktuell, oder?“): oben Weg g (Schichtkopf, Vorgabe der Seite) mit den Vorschlägen aus Abschnitt 8 des Konzepts
`Docu/konzepte/2026-10-21_mesh3dai-kleider-wie-das-ziel-konzept.md`; darunter die wählbaren Wege s, f, k. Die Haar-Zeile mit der Bibliotheksfrisur (Weg h) ist weg — keine Katalogwahl.
"""

from html import escape

from django.utils.safestring import mark_safe

from .architekturmesh3daibild import Architekturmesh3daibild

__all__ = ['Architekturmesh3daiassetbild']


class Architekturmesh3daiassetbild:
    BREITE = 1800
    HOEHE = 1010
    FARBEN = {'ki': Architekturmesh3daibild.FARBEN['versteckt'], 'rechnung': Architekturmesh3daibild.FARBEN['danach'], 'eingabe': Architekturmesh3daibild.FARBEN['eingabe']}
    ZEILE = 17
    ART_TEXT = {'ki': 'neuronales Netz', 'rechnung': 'Rechnung', 'eingabe': 'Eingabe'}

    #: (Schlüssel, x, y, Breite, Höhe, Art, Vorschlag?, Titel, Zeilen)
    KAESTEN = (
        ('ein', 20, 420, 160, 130, 'eingabe', False, 'Eingabe', ('Netz der Figur', '(Tripo, Scan, GLB/OBJ)', 'Punkte, Dreiecke,', 'Farbe')),
        ('vor', 200, 420, 160, 130, 'rechnung', False, 'Vorstufe', ('Rig (MIA), A-Pose,', '16.384 Punkte', 'mit Farbe')),
        ('zer', 380, 420, 180, 130, 'ki', False, 'Zerlegungsnetz', ('Art je Punkt:', '11 Arten', '+ 8 Haarmaße')),
        ('fig', 590, 425, 165, 110, 'ki', False, 'KI-Figur', ('Netz „Figur“:', 'Pose + Form,', 'Käfig in Ruhelage')),
        ('aus', 590, 680, 165, 120, 'rechnung', False, 'Ausschneiden', ('je Art ein Stück,', 'auf die KI-Figur', 'in Ruhelage gelegt')),
        # Weg g: Schichtkopf (Vorgabe), Vorschläge aus Abschnitt 8 gestrichelt
        ('soll', 590, 112, 165, 110, 'rechnung', False, 'Soll im Training', ('Strahlen auf die', 'Zielstücke der', '244 Figuren')),
        ('g1', 790, 112, 155, 120, 'ki', False, 'Schichtkopf', ('Deckung + Abstand', 'je Käfigpunkt', 'und Art (11 Arten)')),
        ('g2', 957, 112, 155, 120, 'rechnung', True, 'Abgleich', ('Körper und Stück an', 'den Eingang, Körper', 'immer unter Stoff')),
        ('g3', 1124, 112, 155, 120, 'rechnung', False, 'Rückbau', ('Fläche an der', 'Höhenlinie 0,5,', 'EINE Farbe je Stück')),
        ('g4', 1291, 112, 155, 120, 'rechnung', False, 'Bindung', ('Gewichte der', 'Käfigpunkte; Haut', 'darunter verdeckt')),
        ('hk', 957, 252, 155, 100, 'rechnung', True, 'Hülle', ('Mulden geschlossen,', 'Träger jedes Stücks')),
        ('fp', 1124, 252, 155, 100, 'rechnung', True, 'Farbe je Punkt', ('aus dem Eingang', 'statt EINER Farbe')),
        # Weg s: Kleidung mit Bauplan
        ('s1', 790, 404, 155, 110, 'rechnung', False, 'Messliste', ('Umfänge, Längen,', 'Enge je Stelle', '(Points of Measure)')),
        ('s2', 957, 404, 155, 110, 'ki', False, 'Schnittnetz', ('Bauplan, Form,', 'Startwert je Zahl')),
        ('s3', 1124, 404, 155, 110, 'rechnung', False, 'Nachstellen', ('am flachen Muster,', 'geeicht an echter', 'Drapierung')),
        ('dr', 1124, 532, 155, 100, 'ki', True, 'Drapiernetz', ('Zahlen → Messstellen', 'nach dem Drapieren,', 'in Millisekunden')),
        ('s4', 1291, 404, 155, 110, 'rechnung', False, 'GarmentCode', ('schneiden, nähen,', 'drapieren, dann', 'nachmessen')),
        ('s5', 1458, 404, 155, 110, 'rechnung', True, 'Textur', ('Bild des Stücks', 'auf die', 'Schnittteile')),
        # Weg f: Schnitt aus der Fläche
        ('f1', 790, 674, 155, 106, 'rechnung', False, 'Nahtlinien', ('vom Genesis-Körper', 'auf das Stück')),
        ('f2', 957, 674, 155, 106, 'rechnung', False, 'Flachlegen', ('Teile flach legen', '(GPU)')),
        ('f3', 1124, 674, 155, 106, 'rechnung', False, 'Drapieren', ('GarmentCode-Schnitt,', 'Warp-Simulation', 'auf der KI-Figur')),
        # Weg k: das ausgeschnittene Stück
        ('k1', 790, 826, 155, 100, 'rechnung', True, 'Säubern', ('Fetzen anderer Arten', 'weg, Löcher zu')),
        ('k2', 957, 826, 155, 100, 'rechnung', False, 'Bindung', ('starr am Knochen oder', 'folgt der Haut')),
    )
    #: (von, nach, beide Richtungen?)
    PFEILE = (('ein', 'vor', False), ('vor', 'zer', False), ('zer', 'g1', False), ('fig', 'g1', False), ('soll', 'g1', False), ('g1', 'g2', False), ('g2', 'g3', False),
              ('g3', 'g4', False), ('hk', 'g1', False), ('fp', 'g3', False), ('zer', 'aus', False), ('fig', 'aus', False),
              ('aus', 's1', False), ('s1', 's2', False), ('s2', 's3', False), ('s3', 'dr', True), ('s3', 's4', False), ('s4', 's5', False),
              ('aus', 'f1', False), ('f1', 'f2', False), ('f2', 'f3', False), ('aus', 'k1', False), ('k1', 'k2', False))
    #: (x, y, Text, fett) — Überschriften der Wege und Fußzeilen
    TEXTE = (
        (790, 100, 'Weg g — Schichtkopf: Vorgabe auf der Seite, für jede Art, die das Netz zeigt (ab 0,5 % der Fläche)', True),
        (1300, 272, 'Training heute: Wolke an ihrer Stelle, Soll auf dem echten Körper.', False),
        (1300, 290, 'Vorschlag (Konzept Abschnitt 8): Training sieht genau den Einsatz', False),
        (1300, 308, '(Soll auf dem Käfig der KI); Saum als Abstand; Bedeckung und Art', False),
        (1300, 326, 'getrennt; Prüfung nach Fehlerklassen an allen Jobs.', False),
        (790, 392, 'Weg s — Kleidung mit Bauplan (wählbar): Oberteil, Hose, Shorts, Rock, Kleid, Anzug, Unterwäsche', True),
        (1300, 570, 'Erst wenn die Messstellen über das Drapiernetz passen,', False),
        (1300, 588, 'wird einmal echt drapiert und nachgemessen.', False),
        (790, 662, 'Weg f — Schnitt aus der Fläche (wählbar): das ausgeschnittene Stück flach gelegt, genäht, drapiert', True),
        (790, 814, 'Weg k — das ausgeschnittene Stück selbst (wählbar; ohne g-Stück die Vorgabe für Haar, Schuh, Kopfbedeckung, Zubehör)', True),
        (20, 966, 'Ausgabe jedes Wegs: ein Genesis-Stück an der KI-Figur, gehäutet mit ihrem Rig; es verdeckt die Haut darunter. Haut und Anatomie gehören zur Figur (Netz „Figur“).', False),
        (20, 988, 'Keine Wahl aus Katalog oder Garderobe — deren Stücke sind nur Übungsmaterial der Trainingsfiguren. Gestrichelt = Vorschlag (Konzept 21.10.2026, Abschnitte 3 und 8).', False),
    )

    @classmethod
    def _kasten(cls, teile, x, y, b, h, art, vorschlag, titel, zeilen):
        fuell, rand = cls.FARBEN[art]
        strich = ' stroke-dasharray="7 4" stroke-width="2"' if vorschlag else ' stroke-width="1.6"'
        teile.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s"%s/>' % (x, y, b, h, '#ffffff' if vorschlag else fuell, rand, strich))
        cx = x + b / 2
        teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="15" font-weight="700" fill="#222">%s</text>' % (cx, y + 22, escape(titel)))
        teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="11.5" font-style="italic" fill="%s">%s</text>'
                     % (cx, y + 39, rand, escape(cls.ART_TEXT[art] + (' · Vorschlag' if vorschlag else ' · gebaut'))))
        for k, z in enumerate(zeilen):
            teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="13" fill="#333">%s</text>' % (cx, y + 60 + cls.ZEILE * k, escape(z)))

    @staticmethod
    def _rand(k, ziel):
        """Punkt auf dem Rand von Kasten k in Richtung der Mitte von ziel."""
        x, y, b, h = k[1:5]
        cx, cy = x + b / 2, y + h / 2
        dx, dy = ziel[1] + ziel[3] / 2 - cx, ziel[2] + ziel[4] / 2 - cy
        s = min(b / 2 / abs(dx) if dx else 1e9, h / 2 / abs(dy) if dy else 1e9)
        return cx + dx * s, cy + dy * s

    @classmethod
    def _legende(cls, teile):
        x = 20
        for art, vorschlag, text in (('ki', False, 'neuronales Netz, gebaut'), ('ki', True, 'neuronales Netz, Vorschlag'), ('rechnung', False, 'Rechnung, gebaut'),
                                     ('rechnung', True, 'Rechnung, Vorschlag'), ('eingabe', False, 'Eingabe')):
            fuell, rand = cls.FARBEN[art]
            strich = ' stroke-dasharray="7 4" stroke-width="2"' if vorschlag else ' stroke-width="1.6"'
            teile.append('<rect x="%d" y="52" width="34" height="18" rx="4" fill="%s" stroke="%s"%s/>' % (x, '#ffffff' if vorschlag else fuell, rand, strich))
            teile.append('<text x="%d" y="66" font-size="13" fill="#222">%s</text>' % (x + 42, escape(text)))
            x += 64 + 7 * len(text)

    @classmethod
    def svg(cls):
        kaesten = {k[0]: k for k in cls.KAESTEN}
        teile = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="Neuronales Netz für Assets: Vorschlag" class="m3a-bild">' % (cls.BREITE, cls.HOEHE),
                 '<defs><marker id="m3a-assetpfeil" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                 '<path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker></defs>',
                 '<rect x="0" y="0" width="%d" height="%d" rx="10" fill="#ffffff"/>' % (cls.BREITE, cls.HOEHE),
                 '<text x="20" y="32" font-size="18" font-weight="700" fill="#222">Neuronales Netz für Assets — Vorschlag: Kleider, Haar, Zubehör aus dem Netz einer Figur</text>']
        cls._legende(teile)
        for von, nach, beide in cls.PFEILE:
            a, b = kaesten[von], kaesten[nach]
            x1, y1 = cls._rand(a, b)
            x2, y2 = cls._rand(b, a)
            teile.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#222" stroke-width="1.5" marker-end="url(#m3a-assetpfeil)"%s/>'
                         % (x1, y1, x2, y2, ' marker-start="url(#m3a-assetpfeil)"' if beide else ''))
        for k in cls.KAESTEN:
            cls._kasten(teile, *k[1:])
        for x, y, text, fett in cls.TEXTE:
            teile.append('<text x="%d" y="%d" font-size="%d"%s fill="#222">%s</text>' % (x, y, 14 if fett else 13, ' font-weight="600"' if fett else '', escape(text)))
        teile.append('</svg>')
        return mark_safe(''.join(teile))
