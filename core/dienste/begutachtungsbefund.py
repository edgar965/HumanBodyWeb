# -*- coding: utf-8 -*-
"""Begutachtungsbefund — die Messung einer Runde für die automatischen Iterationen (`iterationen2d3d`).

Sammelt je Ansicht das Foto, den Render und ein zweites Bild mit Kennfarben je Teil (`Teilmasken.farben`,
gerendert mit demselben `Genesishaarrender` → gleiche Verdeckung, gleiche Fläche), und gibt am Ende
`Befundmessung.befund` (Abstände zum Netz je Teil und Höhenband, Fotofarben unter den Teilmasken und in den
Körperbändern). Ohne Bezugsnetz bleiben die Netzzahlen None, die Farben werden trotzdem gemessen.

Seit dem 30.09.2026 nachts in zwei Zügen: erst `masken` (Kennfarbenrender je Ansicht — die Teilmasken braucht auch die
Fotoprojektion VOR dem eigentlichen Render), dann `render_dazu` (der Render mit Texturen); `ansicht` tut beides.
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
        self.messung = Befundmessung(proben, normalen if proben is not None else None, sicht,
                                     labels=getattr(netznote, 'labels', None))
        #: `datei → (foto_farbe, foto_maske, render_farbe, render_maske, teilmasken)` in der Reihenfolge der Ansichten.
        self._ansichten = {}

    def masken(self, render, teile, referenz, pfad, groesse):
        """Das Kennfarbenbild dieser Ansicht rendern und die Teilmasken merken → Liste der Masken je Teil."""
        farben = Teilmasken.farben(len(teile))
        render.bild_teile([(t['punkte'], t['dreiecke'], farben[i]) for i, t in enumerate(teile)], referenz.winkel,
                          pfad, groesse=groesse, kennung=True)
        kennbild = Iterationsbild.aus_render(pfad)
        masken = Teilmasken.zuordnen(kennbild.farbe, kennbild.maske, len(teile))
        self._ansichten[referenz.datei] = [referenz.bild.farbe, referenz.bild.maske, None, None, masken]
        return masken

    def render_dazu(self, referenz, renderbild):
        """Der Render (mit Texturen) dieser Ansicht — nach `masken`."""
        eintrag = self._ansichten.get(referenz.datei)
        if eintrag is None:
            raise ValueError('erst masken(), dann render_dazu(): %s' % referenz.datei)
        eintrag[2], eintrag[3] = renderbild.farbe, renderbild.maske

    def ansicht(self, render, teile, referenz, renderbild, pfad, groesse):
        """Kennfarbenbild rendern und den Render merken — beides in einem Zug."""
        self.masken(render, teile, referenz, pfad, groesse)
        self.render_dazu(referenz, renderbild)

    @property
    def ansichten(self):
        return [tuple(a) for a in self._ansichten.values() if a[2] is not None]

    def befund(self, teile):
        return self.messung.befund(teile, self.ansichten)
