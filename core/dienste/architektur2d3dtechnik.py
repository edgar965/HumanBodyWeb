# -*- coding: utf-8 -*-
"""Architektur2d3dtechnik — der Abschnitt „Technische Details" im Reiter Workflow der Seite Hilfe → Architektur → 2D3D (06.10.2026).

Edgar, 06.10.2026: „mach auch möglichst viele technische Details im unteren Bereich hinein, zu den Trellis Parametern usw. damit wir später nicht von neuem anfangen und Fehler nicht wiederholen".
Zwei Teile, getrennt nach dem, was sie sind:

    optionen   ALLE Einstellungen eines Auftrags mit Vorgabe, Werten und Hinweis — beim Aufruf aus den Katalogen des Codes gelesen (`Architektur2d3doptionen`), also nie veraltet
    fakten     gemessene Werte, Entscheidungen und Fallen aus den Regeldateien (`Architektur2d3dfaktennetz`, `Architektur2d3dfaktenkoerper`), je mit Quelle; die Zahlen stehen dort mit Datum

Die Fakten sind von Hand gesammelt und tragen ihren Stand (06.10.2026); wer eine Zahl ändert, ändert sie in der Regeldatei UND hier — oder streicht sie hier, wenn die Regeldatei sie nicht mehr trägt.
"""

from .architektur2d3dfaktenkoerper import Architektur2d3dfaktenkoerper
from .architektur2d3dfaktennetz import Architektur2d3dfaktennetz
from .architektur2d3doptionen import Architektur2d3doptionen

__all__ = ['Architektur2d3dtechnik']


class Architektur2d3dtechnik:
    STAND = '06.10.2026'
    #: Beschriftung der Arten (`art` der Einträge), in dieser Reihenfolge in der Legende.
    ARTEN = [
        ('parameter', 'Parameter', 'ein Einstellwert, seine Bedeutung und was dazu gemessen ist'),
        ('messung', 'Messung', 'eine Zahl mit Auftrag, Datum und Maß'),
        ('falle', 'Falle', 'ein Fehler, der passiert ist — damit er nicht noch einmal passiert'),
        ('entscheidung', 'Entscheidung', 'warum es so ist und nicht anders'),
    ]

    @classmethod
    def eintraege(cls):
        return Architektur2d3dfaktennetz.eintraege() + Architektur2d3dfaktenkoerper.eintraege()

    @classmethod
    def kontext(cls):
        eintraege = cls.eintraege()
        reihenfolge, bereiche = [], {}
        for e in eintraege:
            if e['bereich'] not in bereiche:
                reihenfolge.append(e['bereich'])
                bereiche[e['bereich']] = []
            bereiche[e['bereich']].append(e)
        zaehler = {art: sum(1 for e in eintraege if e['art'] == art) for art, _t, _w in cls.ARTEN}
        return {
            'stand': cls.STAND,
            'optionen': Architektur2d3doptionen.kontext(),
            'bereiche': [{'bereich': b, 'eintraege': bereiche[b]} for b in reihenfolge],
            'anzahl': len(eintraege),
            'arten': [{'art': a, 'text': t, 'was': w, 'anzahl': zaehler[a]} for a, t, w in cls.ARTEN],
        }
