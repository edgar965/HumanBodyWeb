# -*- coding: utf-8 -*-
"""Workflowfluss — eine Runde von „2D3D Kleider" als Fluss in Abschnitten, jeder mit seiner gemessenen Zeit und den Verweisen auf die
Entscheidungsbäume, die in ihm fallen (Hilfe → Architektur → 2D3D, 02.10.2026).

Die 22 Schritte kommen unverändert aus `Architektur2d3d.RUNDE`; hier werden sie zu den Abschnitten zusammengefasst, die das
`auftrag.log` zeitlich misst („<s> s Runde <n>: <Abschnitt>", `Begutachtungswerkzeug.takt`). Die Zeit eines Abschnitts gilt für alle
Schritte darin zusammen. Die Schritte 1–10 liegen vor dem ersten Abschnitt: ihre Zeit ist die Dauer eines Laufs mit EINER Runde minus
die Summe der Abschnitte. Ein Test hält fest, dass jeder der 22 Schritte in genau einem Abschnitt steht.
"""

from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowfluss']


class Workflowfluss:
    #: (Titel, erster Schritt, letzter Schritt, [(Beschriftung, Zeit)], [Baumkennung])
    ABSCHNITTE = [
        (
            'Laufanfang und Rezept',
            1,
            10,
            [('ein Lauf mit einer Runde', W.LAUFANFANG), ('Rezept der Automatik', W.REZEPT)],
            ['start', 'modus', 'rezeptweg', 'automatik', 'drapieren', 'haarknoten', 'haardynamik'],
        ),
        ('Modell bauen', 11, 13, [('Vorrat warm', W.BAUEN_WARM), ('Vorrat kalt', W.BAUEN_KALT)], ['bauen']),
        (
            'Fotoprojektion',
            14,
            14,
            [('Haut schon projiziert', W.FOTOPROJEKTION_NICHT), ('Stück gewünscht', W.FOTOPROJEKTION_STUECK)],
            ['fotoprojektion'],
        ),
        (
            'Rendern 1 von 3 und 2 von 3',
            15,
            15,
            [('Bild 1', W.RENDERN_1), ('Bild 2', W.RENDERN_2)],
            ['renderer'],
        ),
        ('Rendern 3 von 3 — mit Netznote, Befund, Messgüte, Gesichtsmaßen', 16, 18, [('', W.RENDERN_3)], []),
        ('Prüfbilder', 19, 19, [('', W.PRUEFBILDER)], []),
        ('ablegen', 20, 21, [('', W.ABLEGEN)], ['auswahl']),
        ('Nach dem Lauf', 22, 22, [], ['modus']),
    ]

    def __init__(self, zeichner, titel, runde):
        """`zeichner`: `Workflowzeichner`, `titel`: Kennung → Überschrift der Bäume, `runde`: `Architektur2d3d.RUNDE`."""
        self.zeichner = zeichner
        self.titel = titel
        self.runde = {nr: (wann, was, klassen, takt) for nr, wann, was, klassen, takt in runde}

    def schritte(self, von, bis):
        aus = []
        for nr in range(von, bis + 1):
            wann, was, klassen, takt = self.runde[nr]
            aus.append(
                {
                    'nr': nr,
                    'wann': wann,
                    'was': was,
                    'takt': takt,
                    'klassen': [self.zeichner.klasse(k) for k in klassen.split(', ')],
                }
            )
        return aus

    def abschnitte(self):
        aus = []
        for titel, von, bis, zeiten, baeume in self.ABSCHNITTE:
            aus.append(
                {
                    'titel': titel,
                    'von': von,
                    'bis': bis,
                    'zeiten': [
                        {'label': label, 'html': self.zeichner.zeit(z), 'hinweis': z.hinweis}
                        for label, z in zeiten
                    ],
                    'baeume': [{'anker': 'baum-' + b, 'titel': self.titel[b]} for b in baeume],
                    'schritte': self.schritte(von, bis),
                }
            )
        return aus

    @classmethod
    def nummern(cls):
        """Alle Schrittnummern, die die Abschnitte abdecken (der Test vergleicht sie mit `Architektur2d3d.RUNDE`)."""
        return [nr for _t, von, bis, _z, _b in cls.ABSCHNITTE for nr in range(von, bis + 1)]
