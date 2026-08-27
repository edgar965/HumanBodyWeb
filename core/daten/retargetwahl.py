# -*- coding: utf-8 -*-
"""Retargetwahl — die vier Stellschrauben einer Retarget-Anfrage.

Sie kamen als Vierertupel aus `_wahlwerte` und wurden beim Aufrufer wieder
auseinandergenommen (Befund `rueckgabetupel`, 27.08.2026) — genau die Bauform,
gegen die `daten/koerperzustand.py` schon einmal getauscht wurde:

    groesse, art, fusskorrektur, delta = cls._wahlwerte(request.GET)

Ein Tupel sagt nicht, was `[2]` bedeutet, und beim Erweitern verschieben sich
alle Stellen stillschweigend.

`delta_norm` ist DREIWERTIG und deshalb kein `bool`: `'1'` schaltet ein, `'0'`
aus, und alles andere (auch ein fehlender Parameter) heisst „wie das Format es
vorsieht". Ein `bool` haette den dritten Fall verschluckt.
"""


class Retargetwahl:
    """Was der Aufrufer am Retarget einstellen darf."""

    __slots__ = ('groesse', 'format', 'fusskorrektur', 'delta_norm')

    #: Werte, die in der Abfragezeichenkette „ja" bedeuten.
    JA = ('1', 'true')

    def __init__(self, werte, vorgabe_groesse):
        self.groesse = float(werte.get('body_height', vorgabe_groesse))
        self.format = werte.get('format', None)
        self.fusskorrektur = (werte.get('foot_correction', '').lower()
                              in self.JA)
        self.delta_norm = self._dreiwertig(werte.get('delta_norm', ''))

    @staticmethod
    def _dreiwertig(roh):
        """`'1'` -> True, `'0'` -> False, sonst None (Format entscheidet)."""
        text = str(roh).lower()
        if text == '1':
            return True
        if text == '0':
            return False
        return None

    def __repr__(self):
        return ('<Retargetwahl %.2f m, %s, Fuss=%s, Delta=%s>'
                % (self.groesse, self.format or 'erkannt', self.fusskorrektur,
                   self.delta_norm))
