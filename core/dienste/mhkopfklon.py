# -*- coding: utf-8 -*-
u"""Mhkopfklon — der MakeHuman-Klon (`G9mhklon`) mit ausgerichtetem Kopf, fuer die Morph-Uebertragung (17.10.2026).

Der Klon der Kleiderbibliothek bleibt, wie er ist (Kleider sitzen nicht am Gesicht). Hier wird `geschaetzt()` — die Lage nach den Rahmen, VOR der ICP-Anpassung —
um die Kopfausrichtung (`Mhkopfausrichtung`) ergaenzt; ICP, Hautpunkte und die abgeleiteten Punkte (Helfer, Gelenkwuerfel) folgen von selbst, weil alle `geschaetzt()` rufen.
`kopf_linear` nimmt Morph-Deltas mit demselben linearen Teil mit.
"""
import numpy as np
from Genesis9.mhklon import G9mhklon

from .mhkopfausrichtung import Mhkopfausrichtung

__all__ = ['Mhkopfklon']


class Mhkopfklon(G9mhklon):
    u"""`G9mhklon` + `kopf` (die Ausrichtung) — erst nach dem ersten `geschaetzt()` da."""

    HALS = 'neck01'
    AUGEN = (('eye.L', 'l_eye'), ('eye.R', 'r_eye'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kopf = None
        self._ausgerichtet = None
        self._kopfhoehe = None

    def geschaetzt(self):
        if self._ausgerichtet is None:
            roh = super().geschaetzt()
            self._kopfhoehe = roh[:, 1].copy()
            self.kopf = self._ausrichten(roh)
            self._ausgerichtet = self.kopf.anwenden(roh)
        return self._ausgerichtet

    def _ausrichten(self, roh):
        quelle = roh[self.koerper]
        ziel = np.asarray(self.flaeche[0], dtype=np.float64)
        a_mh = [self.rumpf(np.asarray(self.mh_k[m]['kopf'], dtype=np.float64)[None, :])[0] for m, _g in self.AUGEN]
        a_g9 = [np.asarray(self.g9_k[g]['kopf'], dtype=np.float64) for _m, g in self.AUGEN]
        hals = float(self.rumpf(np.asarray(self.mh_k[self.HALS]['kopf'], dtype=np.float64)[None, :])[0][1])
        return Mhkopfausrichtung.berechnen(quelle, ziel, a_mh, a_g9, hals)

    def kopf_linear(self, delta):
        u"""(M, 3) Verschiebungen im Raum von Genesis, mit dem linearen Teil der Kopfausrichtung mitgenommen."""
        self.geschaetzt()
        return self.kopf.linear(delta, self._kopfhoehe)
