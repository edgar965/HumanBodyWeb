# -*- coding: utf-8 -*-
"""Kopfwarp — Dünnplattenspline zwischen den Landmarken des Modell-Renders und denen des Fotos (06.10.2026).

Ein Punkt der Kopfhaut geht in den Kopf-Render (Kamera bekannt), und der Warp sagt, wo derselbe Gesichtspunkt im Foto liegt: Die 478 Landmarken auf BEIDEN Bildern sind die Paare (derselbe Detektor, seine Eigenheiten kürzen sich
— wie bei `Gesichtsmasse`). Eine einzige Verschiebung und Skalierung reicht nicht: gemessen an der Kopftafel von „Edgar - 7" liegen die Augen im Render 14 mm tiefer als im Foto, die Nasenspitze 8 mm höher, Mund und Kinn gleich.

Die Glättung (Detektorrauschen) wird nicht geraten, sondern durch Kreuzprüfung gewählt: je Faltung ein Zehntel der Paare weglassen, aus dem Rest vorhersagen, Fehler der weggelassenen messen — der kleinste gewinnt.
`fehler_px` ist der Vorhersagefehler an UNGESEHENEN Landmarken (Pixel des Fotos), `fehler_mm` rechnet ihn mit der Skalierung des Warps auf Modellmillimeter um.
"""

import numpy as np

__all__ = ['Kopfwarp']


class Kopfwarp:
    GLAETTUNGEN = (0.0, 1e-4, 1e-3, 1e-2, 1e-1, 1.0)
    FALTUNGEN = 10
    #: Die Pixel werden vor der Anpassung durch diese Zahl geteilt (Zahlen der Größe 1; die Glättung hängt sonst an der Bildgröße).
    NORM = 1000.0

    def __init__(self, von, nach, glaettung):
        from scipy.interpolate import RBFInterpolator
        self.von = np.asarray(von, dtype=np.float64)
        self.nach = np.asarray(nach, dtype=np.float64)
        self.glaettung = float(glaettung)
        self._f = RBFInterpolator(self.von / self.NORM, self.nach / self.NORM, kernel='thin_plate_spline', smoothing=self.glaettung)
        self.fehler_px = None
        self.fehler_mm = None

    @classmethod
    def _vorhersage_fehler(cls, von, nach, glaettung, faltungen, saat=7):
        """Quadratisches Mittel der Abstände weggelassener Paare zur Vorhersage (Pixel von `nach`)."""
        from scipy.interpolate import RBFInterpolator
        n = len(von)
        reihenfolge = np.random.default_rng(saat).permutation(n)
        fehler = np.zeros(n)
        for f in range(faltungen):
            raus = reihenfolge[f::faltungen]
            rest = np.setdiff1d(np.arange(n), raus)
            warp = RBFInterpolator(von[rest] / cls.NORM, nach[rest] / cls.NORM, kernel='thin_plate_spline', smoothing=glaettung)
            fehler[raus] = np.hypot(*(warp(von[raus] / cls.NORM) * cls.NORM - nach[raus]).T)
        return float(np.sqrt(np.mean(fehler ** 2)))

    @classmethod
    def passen(cls, von, nach, mm_je_px=None):
        """Warp aus den Paaren `von` → `nach` (je (N, 2)), mit der Glättung der kleinsten Kreuzprüfung. `mm_je_px`: Millimeter je Pixel von `von` (Modell-Render), für `fehler_mm`."""
        von, nach = np.asarray(von, dtype=np.float64), np.asarray(nach, dtype=np.float64)
        if len(von) != len(nach) or len(von) < 20:
            raise ValueError('Zu wenige Landmarkenpaare (%d)' % len(von))
        fehler = {g: cls._vorhersage_fehler(von, nach, g, cls.FALTUNGEN) for g in cls.GLAETTUNGEN}
        beste = min(fehler, key=fehler.get)
        warp = cls(von, nach, beste)
        warp.fehler_px = fehler[beste]
        warp.massstab = warp._massstab()
        if mm_je_px is not None and warp.massstab > 0:
            warp.fehler_mm = fehler[beste] / warp.massstab * float(mm_je_px)
        warp.fehler_je_glaettung = fehler
        return warp

    def _massstab(self):
        """Pixel von `nach` je Pixel von `von` (Mittel der besten Ähnlichkeit über alle Paare)."""
        a = self.von - self.von.mean(axis=0)
        b = self.nach - self.nach.mean(axis=0)
        return float(np.sqrt((b ** 2).sum() / max((a ** 2).sum(), 1e-12)))

    def anwenden(self, punkte):
        """(N, 2) Punkte im Bild `von` → (N, 2) im Bild `nach`."""
        punkte = np.asarray(punkte, dtype=np.float64).reshape(-1, 2)
        return self._f(punkte / self.NORM) * self.NORM

    def rest_px(self):
        """Abstand der angepassten Paare von ihren Zielen (Pixel von `nach`): quadratisches Mittel und Höchstwert — bei Glättung 0 genau 0."""
        d = np.hypot(*(self.anwenden(self.von) - self.nach).T)
        return float(np.sqrt(np.mean(d ** 2))), float(d.max())
