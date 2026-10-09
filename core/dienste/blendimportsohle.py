# -*- coding: utf-8 -*-
"""Blendimportsohle — um wie viel muss ein Schuh um die Querachse gedreht werden, damit seine Sohle waagrecht liegt?

Warum (09.10.2026, „der Stiefel soll flach am Boden sitzen" — und die Gegenprobe am dritten Modell): Die erste Fassung (`Blendimportfuss.waagrecht`) teilte die Schuhlänge
in Drittel ENTLANG DER FUSSACHSE DES KÖRPERS und suchte die Drehung, bei der der tiefste Punkt hinten und vorn gleich tief liegt. Das passt, wo der Körperfuß im Schuh
steckt (Asian Female: Stiefel auf Zehenspitzen). Beim Fallout ranger hat der Körper keine Füße — im Fußteil liegen 333 Körperpunkte gegen 2.166 Käfigpunkte, der
Fußwinkel von 57° ist erfunden, der Stiefel steht flach auf dem Boden. Die Drittel lagen schief zum Schuh, die Lücke hinten−vorn hatte nur eine Nullstelle bei −75°, und
die Sohle wurde zerstört (Sohlenprofil 3 2 1 2 11 2 0 0 1 4 8 14 mm → 34 50 50 45 39 28 21 9 6 0 23 105 mm; Kantenverzerrung 0,00 → 7,9 %, Haltungstreue p99 5,9 → 28,4 mm).

Die Sohle ist dort, wo der Schuh auf dem Boden steht — das sagt seine Form, nicht der Fuß. Sagittalprofil der Schuhpunkte (Länge z nach vorn, Höhe y) im Rahmen des
Unterschenkels; die untere konvexe Hülle; eine Kante der unteren Hülle ist die Sohle, wenn
  · sie höchstens `GRENZE_GRAD` gegen die Waagrechte geneigt ist (steilere Kanten sind Schaftrückseite oder Kappe, keine Sohle) und
  · die Punkte in einem Streifen von `band` Dicke über ihr die längste Strecke abdecken (Ferse und Ballen stehen auf ihr; ein Zehenspitzenstiefel auf der
    Kante Ferse → Ballen, nicht auf der winzigen Kante an der Spitze) — mindestens `SPANNE_ANTEIL` der Schuhlänge, sonst gibt es keine Sohle.
Gemessen (09.10.2026, `ProjektTemp/_wegwerf/sohle_verfahren.py`): Fallout ranger −0,9° / −1,0° (flach, richtig); Asian Female −37,2° / −38,1° (die Endlage nach der
Nachstellung war −35,5° / −36,0°). Die alte Fassung kam an Asian Female auf −38° / −44°, an Fallout auf −75° / −70°.
"""

import numpy as np

__all__ = ['Blendimportsohle']


class Blendimportsohle:
    #: Eine Kante der unteren Hülle zählt nur als Sohle, wenn sie höchstens so viel (Grad) gegen die Waagrechte geneigt ist.
    GRENZE_GRAD = 60.0
    #: Die Sohle deckt mindestens diesen Anteil der Schuhlänge ab (der Streifen über ihr, in der Länge der Kante gemessen).
    SPANNE_ANTEIL = 0.4

    @classmethod
    def neigung(cls, schuh, band):
        """Winkel (Grad, + = Spitze nach unten) der Drehung um die Querachse, bei der die Sohle waagrecht liegt — `None`, wenn der Schuh keine Sohle hat.
        `schuh` (S, 3): die Schuhpunkte im Rahmen des Unterschenkels (Länge z nach vorn, Höhe y); `band` (m): Dicke des Streifens über der Sohle,
        in dem Punkte noch „auf ihr stehen" (Vielfaches der Käfigeinheit `h`, `Blendimportfuss.SOHLE_BAND_H`)."""
        from scipy.spatial import ConvexHull, QhullError

        p = np.column_stack([schuh[:, 2], schuh[:, 1]])
        if len(p) < 4 or float(np.ptp(p[:, 0])) < 1e-6:
            return None
        try:
            huelle = ConvexHull(p)
        except QhullError:
            return None
        laenge = float(np.ptp(p[:, 0]))
        waagrecht = np.cos(np.radians(cls.GRENZE_GRAD))
        beste = None
        for gleichung in huelle.equations:
            nz, ny = float(gleichung[0]), float(gleichung[1])          # nach außen zeigende Normale der Kante
            if ny > -waagrecht:                                        # nicht untere Hülle, oder steiler als GRENZE_GRAD
                continue
            winkel = float(np.arctan2(nz, -ny))                        # Neigung der Kante: Spitze tiefer als Ferse → negativ
            u = p[:, 0] * np.cos(winkel) + p[:, 1] * np.sin(winkel)    # entlang der Kante
            v = -p[:, 0] * np.sin(winkel) + p[:, 1] * np.cos(winkel)   # Höhe über der Kante
            auf = v <= v.min() + band
            spanne = float(np.ptp(u[auf]))
            if beste is None or spanne > beste[0] + 1e-9 or (abs(spanne - beste[0]) <= 1e-9 and abs(winkel) < abs(beste[1])):
                beste = (spanne, winkel)
        if beste is None or beste[0] < cls.SPANNE_ANTEIL * laenge:
            return None
        return float(np.degrees(beste[1]))
