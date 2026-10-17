# -*- coding: utf-8 -*-
"""Mesh3dairausch — das Rauschen der „Ausgabe des Netzes" in der ATTRAPPE der Seite „Mesh3D-AI" (14.10.2026).

Die Ausgabe des Netzes ist Soll plus Rauschen — nichts ist trainiert. Zwei Arten, beide deterministisch (feste Zufallszahlen):

- Probe (`Mesh3dairausch(seed)`): ein Gauß-Rauschen je Punkt und Achse, bei jedem Aufruf mit demselben Seed dasselbe.
- Bewegung (`Mesh3dairausch(seed, weich=True)` mit `t`): ein weicher Sinus je Punkt und Achse (Frequenz 0,3–1,6 Hz, Effektivwert gleich dem Pegel) — die Ausgabe zittert nicht von Bild zu Bild, sie schwankt wie ein
  Fehler, der sich mit der Pose ändert.

    r = Mesh3dairausch(7)
    r.werte('koerper', sigma)        -> (n, 3) in m, `sigma`: Skalar oder (n,) Pegel je Punkt
    r.t = 1.5                         # nur bei `weich=True`: der Zeitpunkt in s
"""

import math
import zlib

import numpy as np

__all__ = ['Mesh3dairausch']


class Mesh3dairausch:
    HZ = (0.3, 1.6)

    def __init__(self, seed, weich=False):
        self.seed = int(seed)
        self.weich = weich
        self.t = 0.0
        self._phasen = {}

    def _erzeuger(self, schluessel):
        return np.random.default_rng([self.seed, zlib.crc32(schluessel.encode('utf-8'))])

    def werte(self, schluessel, sigma):
        """Das Rauschen für `schluessel` (eine Zeile oder ein Teil der Probe) bei dem Pegel `sigma` (m, Skalar oder (n,))."""
        sigma = np.atleast_1d(np.asarray(sigma, dtype=float))
        n = len(sigma)
        s = sigma[:, None]
        if not self.weich:
            return self._erzeuger(schluessel).normal(0.0, 1.0, (n, 3)) * s
        if schluessel not in self._phasen:
            z = self._erzeuger(schluessel)
            self._phasen[schluessel] = (z.uniform(*self.HZ, (n, 3)), z.uniform(0.0, 2 * math.pi, (n, 3)))
        f, phase = self._phasen[schluessel]
        return s * math.sqrt(2.0) * np.sin(2 * math.pi * f * self.t + phase)
