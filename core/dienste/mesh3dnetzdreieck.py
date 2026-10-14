# -*- coding: utf-8 -*-
"""Mesh3dnetzdreieck — Abstand eines Punkts zu Dreiecken (14.10.2026, „Netz bearbeiten“).

Anlass (Edgar, 14.10.2026: „nach dem Entfernen per Auswahl aus Ballerina hast du einen Teil des Arms entfernt“): die Auswahl nach Farbe brauchte die Startfläche des Klicks und prüfte die vom Browser genannte Fläche am Abstand ihrer
MITTE zum Klickpunkt (höchstens 3 cm). Gemessen an der Spiralballerina (`ProjektTemp/_wegwerf/mesh3d/ballerina_startflaeche.py`, `ballerina_dreieckabstand.py`): der Flügel besteht aus Dreiecken mit bis zu 0,40 m langen Kanten, die Mitte liegt
0,037 und 0,038 vom Klickpunkt entfernt, der Punkt selbst aber 0,00002 vom Dreieck — der Raycast hatte es getroffen. Der Server verwarf die Fläche des Browsers, nahm die nächste MITTE (eine Fläche des Unterarms, 5 mm unter dem Flügel), und die Hautfarbe
war die Referenz: 435 Flächen des Unterarms wurden entfernt. Ob ein Klick auf einem Dreieck liegt, sagt der Abstand zum Dreieck, nicht der zur Mitte.
"""

import numpy as np

__all__ = ['Mesh3dnetzdreieck']


class Mesh3dnetzdreieck:
    @staticmethod
    def abstand(punkt, dreiecke):
        """(N,) Abstand des Punkts `(3,)` zu jedem der Dreiecke `(N, 3, 3)`: zur Fläche, wenn die Projektion hineinfällt, sonst zur nächsten Kante. Ein entartetes Dreieck zählt über seine Kanten."""
        p = np.asarray(punkt, dtype=np.float64)
        t = np.asarray(dreiecke, dtype=np.float64)
        a, b, c = t[:, 0], t[:, 1], t[:, 2]
        kante = np.minimum.reduce([Mesh3dnetzdreieck._strecke(p, a, b), Mesh3dnetzdreieck._strecke(p, b, c), Mesh3dnetzdreieck._strecke(p, c, a)])
        ab, ac, ap = b - a, c - a, p - a
        normale = np.cross(ab, ac)
        flaeche2 = (normale * normale).sum(axis=1)
        ok = flaeche2 > 1e-24
        # Schwerpunktkoordinaten der Projektion: u + v <= 1, u, v >= 0 heißt innen
        d00, d01, d11 = (ab * ab).sum(axis=1), (ab * ac).sum(axis=1), (ac * ac).sum(axis=1)
        d20, d21 = (ap * ab).sum(axis=1), (ap * ac).sum(axis=1)
        nenner = d00 * d11 - d01 * d01
        nenner = np.where(np.abs(nenner) > 1e-30, nenner, 1.0)
        v = (d11 * d20 - d01 * d21) / nenner
        w = (d00 * d21 - d01 * d20) / nenner
        innen = ok & (v >= 0) & (w >= 0) & (v + w <= 1)
        ebene = np.abs((ap * normale).sum(axis=1)) / np.sqrt(np.where(ok, flaeche2, 1.0))
        return np.where(innen, ebene, kante)

    @staticmethod
    def _strecke(p, a, b):
        """Abstand des Punkts zu den Strecken a–b."""
        ab = b - a
        laenge2 = (ab * ab).sum(axis=1)
        s = np.clip(((p - a) * ab).sum(axis=1) / np.where(laenge2 > 0, laenge2, 1.0), 0.0, 1.0)
        return np.linalg.norm(p - (a + ab * s[:, None]), axis=1)
