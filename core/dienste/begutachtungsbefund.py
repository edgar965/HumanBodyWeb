# -*- coding: utf-8 -*-
"""Begutachtungsbefund — die Messung einer Runde für die automatischen Iterationen (`iterationen2d3d`).

Sammelt je Ansicht das Foto, den Render und ein zweites Bild mit Kennfarben je Teil (`Teilmasken.farben`,
gerendert mit demselben `Genesishaarrender` → gleiche Verdeckung, gleiche Fläche), und gibt am Ende
`Befundmessung.befund` (Abstände zum Netz je Teil und Höhenband, Fotofarben unter den Teilmasken und in den
Körperbändern). Ohne Bezugsnetz bleiben die Netzzahlen None, die Farben werden trotzdem gemessen.
"""

from iterationen2d3d.befundmessung import Befundmessung
from iterationen2d3d.teilmasken import Teilmasken

from .iterationsbild import Iterationsbild

__all__ = ['Begutachtungsbefund']


class Begutachtungsbefund:
    def __init__(self, netznote, sicht=None):
        """`sicht`: der `Sichtkoerper` der Vorlagen (30.09.2026) — dann trägt jeder Teil auch den Abstand seiner
        Ringe zum Umriss der Fotos (`huelle_mm`)."""
        proben = getattr(netznote, 'proben', None)
        normalen = getattr(netznote, 'normalen', None)
        self.messung = Befundmessung(proben, normalen if proben is not None else None, sicht)
        self.ansichten = []

    def ansicht(self, render, teile, referenz, renderbild, pfad, groesse):
        """Das Kennfarbenbild dieser Ansicht rendern und die Ansicht merken."""
        farben = Teilmasken.farben(len(teile))
        render.bild_teile([(t['punkte'], t['dreiecke'], farben[i]) for i, t in enumerate(teile)], referenz.winkel,
                          pfad, groesse=groesse)
        kennbild = Iterationsbild.aus_render(pfad)
        masken = Teilmasken.zuordnen(kennbild.farbe, kennbild.maske, len(teile))
        self.ansichten.append((referenz.bild.farbe, referenz.bild.maske, renderbild.farbe, renderbild.maske, masken))

    def befund(self, teile):
        return self.messung.befund(teile, self.ansichten)
