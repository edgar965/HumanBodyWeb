# -*- coding: utf-8 -*-
"""Haarablauf — die Attrappen um `Haardynamik.simulieren` für `test_haardynamik.py` (02.10.2026): Käfig, Körper, Kopfhaut,
`G9kleidmorphe.ablegen` und der Solver-Prozess (`_laufen`). Der „Solver“ setzt alles 2 cm nach unten, auch die Wurzeln, und
verschiebt diese noch um 0,1 mm — so zeigt sich, ob die Wurzeln beim Zurückrechnen genau 0 bekommen."""

import json
from pathlib import Path
from unittest import mock

import numpy as np
from Genesis9.kleidmorphe import G9kleidmorphe
from Genesis9.kopfhaut import G9kopfhaut

from core.dienste.haardynamik import Haardynamik

from ._haardaten import Haardaten

__all__ = ['Haarablauf']


class Haarablauf:
    HAUT = Haardaten.haut()

    def __init__(self, teile, eintrag=None, fehler_im_teil=None):
        """`teile`: `[(Teil, None)]` wie `G9garderobe.teile`; `fehler_im_teil`: der Solver scheitert im Lauf mit dieser Nummer."""
        self.teile = teile
        self.eintrag = {'art': 'haar'} if eintrag is None else eintrag
        self.fehler_im_teil = fehler_im_teil
        self.auftraege, self.abgelegt = [], []

    def lauf(self, auftrag_datei, _bericht_datei):
        auftrag = json.loads(Path(auftrag_datei).read_text(encoding='utf-8'))
        if self.fehler_im_teil is not None and len(self.auftraege) == self.fehler_im_teil:
            raise RuntimeError('Haar-Dynamik: Attrappe scheitert')
        self.auftraege.append(auftrag)
        with np.load(auftrag['straehnen']) as d:
            punkte, laengen = d['punkte'], d['laengen']
        nachher = punkte.astype(np.float64) + (0.0, -0.02, 0.0)                       # alles 2 cm nach unten, auch die Wurzeln
        nachher[np.cumsum(laengen) - laengen] += 1e-4                                  # und die Wurzeln noch ein Stück falsch
        np.savez(auftrag['aus'], punkte=nachher.astype(np.float32))
        return {'sekunden': 0.1, 'rechner': 'warp-motor:cuda:0'}

    def ablegen(self, kennung, name, namen, deltas, brief):
        self.abgelegt.append((kennung, name, namen, deltas, brief))
        return brief

    def ausfuehren(self, ordner, **kw):
        """`Haardynamik(ordner).simulieren('frisur', **kw)` mit den Attrappen → der Steckbrief."""
        punkte = Haardaten.punkte()
        kaefig = (self.teile, [punkte.copy() for _ in self.teile], 0.0, 1.0, None, self.eintrag)
        with mock.patch.object(G9kleidmorphe, 'kaefige', return_value=kaefig), \
                mock.patch.object(G9kleidmorphe, 'koerper', return_value=(*Haardaten.KOERPER, None, None, None)), \
                mock.patch.object(G9kleidmorphe, 'ablegen', side_effect=self.ablegen), \
                mock.patch.object(G9kopfhaut, 'aus_teilen', return_value=self.HAUT), \
                mock.patch.object(Haardynamik, '_laufen', side_effect=self.lauf):
            return Haardynamik(ordner).simulieren('frisur', **kw)
