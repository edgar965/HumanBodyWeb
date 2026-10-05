# -*- coding: utf-8 -*-
"""Rezeptaufzeichnung — reicht Aufrufe an ein `ModellMitKleidern` weiter und schreibt sie als Zeilen eines Rezepts mit (05.10.2026).

Anlass: Das Standmodell vor den Iterationen (`Standvorabkleider.modell`: Fotostücke, Frisur, Farben) ist die Figur, die Edgar im Viewer sieht — und die Ausgangsrunde der Nachbesserung trug sie nicht
(Edgar: „hier fehlt die Unterhose, die Socken auch, das Haar ist plötzlich blond"). Statt dieselbe Folge von Aufrufen ein zweites Mal von Hand zu schreiben, läuft sie über diese Hülle: dieselben Aufrufe,
einmal als Modell, einmal als Text (`Standvorabkleider.rezept`) — beide können nicht auseinanderlaufen. Aufgezeichnet werden nur Aufrufe, die ein Rezept kennt (`G9rezept.funktionen()`), nicht Abfragen
wie `als_dict`; Aufrufe, die das Modell selbst zurückgibt (Verkettung), geben die Hülle zurück.
"""

__all__ = ['Rezeptaufzeichnung']


class Rezeptaufzeichnung:
    def __init__(self, modell):
        from Genesis9.modellrezept import G9rezept
        self._modell = modell
        self._erlaubt = G9rezept.funktionen()
        self.zeilen = []

    def __getattr__(self, name):
        ziel = getattr(self._modell, name)
        if name.startswith('_') or not callable(ziel):
            return ziel

        def aufruf(*args, **kwargs):
            from Genesis9.modellrezept import G9rezept
            if name in self._erlaubt:
                self.zeilen.append(G9rezept.text(name, args, kwargs))
            ergebnis = ziel(*args, **kwargs)
            return self if ergebnis is self._modell else ergebnis

        return aufruf
