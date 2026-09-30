# -*- coding: utf-8 -*-
"""Kostuemfrontborte — der Besatz an den beiden Rändern der Mantelöffnung.

Am Mantel der Vorlage laufen vorn zwei breite verzierte Bänder (Gold auf Nachtblau) vom Kragen bis zum Saum —
sie geben der Öffnung ihre Kante. Bis 30.09.2026 hatte das Modell nur die Borte am Saum. Hier ein Streifen je
Rand, aus den äußersten Punkten der Mantelringe: der erste und der letzte Punkt jedes Rings bilden mit ihrem
Nachbarn ein Viereck, das mit dem nächsten Ring zum Band wird (ein Segment breit, am Rock etwa 5 cm). Es folgt
dem Mantel, auch wenn die Ringe von der Umriss-Hülle bewegt wurden (`Kostuemhuelle`), und liegt knapp außen.
"""

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemfrontborte']


class Kostuemfrontborte:
    AUSSEN = 1.008
    #: Wie viele Segmente breit das Band ist.
    BREITE = 1

    def __init__(self, ringe, farbe):
        """`ringe`: die Ringe des offenen Mantels (`Rohr.ringe`, oben nach unten), `farbe`: sRGB."""
        self.ringe = ringe
        self.farbe = farbe

    def _band(self, name, aussen, innen):
        """`aussen`/`innen`: Ringindex des Randpunkts und seines Nachbarn (Vorzeichen wie bei Listen)."""
        rohr = Rohr(name, self.farbe, offen_grad=1.0)
        rohr.SEGMENTE = 2
        for ring in self.ringe:
            mitte = ring[:, :2].mean(axis=0)
            paar = ring[[aussen, innen]].copy()
            paar[:, :2] = mitte + (paar[:, :2] - mitte) * self.AUSSEN
            rohr.ringe.append(paar)
        return rohr.bauen(dicke=0.004, glaetten=0)

    def bauen(self):
        n = len(self.ringe[0])
        if n < 2 + 2 * self.BREITE:
            return []
        return [
            self._band('Frontborte_A', 0, self.BREITE),
            self._band('Frontborte_B', n - 1, n - 1 - self.BREITE),
        ]
