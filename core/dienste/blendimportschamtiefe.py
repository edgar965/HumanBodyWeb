# -*- coding: utf-8 -*-
"""Blendimportschamtiefe — wie weit das Scham-Stück nach hinten und vorn reicht (09.10.2026).

WARUM (Edgar, 09.10.2026, mit Bild: „der ‚Steg' am Ende der Vulva, zum Anus, der muss weg"): Das Stück endete hinten bei der Saat − 20 mm. Dort
liegt das Original aber noch weit von der Figur: gemessen an „cute girl" (`ProjektTemp/_wegwerf/scham_naht/tiefe_proto.py`, Original-Punkte in
der Hülle, Scheiben von 4 mm in z, Abstand zur Figurfläche): bei z = −21…−17 mm Median 11,6 mm, bei −17…−13 mm 15,7 mm; erst bei z ≈ −49 mm unter
2 mm. Der Rand des Stücks lag also 10 mm neben dem Ring des Lochs, und das Verschweißen zog ihn dorthin — vor dem Verschweißen lag er bei 17 mm
(`rand_vor_weld.py`), danach standen zum Anus hin lang gezogene Dreiecke mit verschmierter Textur: der „Steg".

HIER: Jede Grenze (hinten, vorn) rückt von „Saat ± `TIEFE_RAND_MM`" so weit nach außen, bis das Original in der Scheibe innen an der Grenze höchstens
`FLACH_MM` von der Figur abweicht — `FOLGE` Scheiben hintereinander —, höchstens `MAX_MM` weiter. Liegt in der Scheibe kein Original (`MINDEST`
Punkte), wird dort nichts geschnitten: die Grenze gilt. Der Rand liegt dann dort, wo Stück und Haut aufeinander liegen — der Ring des Lochs und der
Rand des Stücks sind dieselbe Linie.
"""

import numpy as np

__all__ = ['Blendimportschamtiefe']


class Blendimportschamtiefe:
    #: Scheibendicke (mm) und größte Verschiebung der Grenze über das Mindestmaß hinaus (mm).
    SCHRITT_MM = 4.0
    MAX_MM = 40.0
    #: So wenig (mm, Median) weicht das Original in der Scheibe von der Figur ab, damit es dort als aufliegend gilt; so viele Scheiben nacheinander.
    FLACH_MM = 2.0
    FOLGE = 2
    #: Scheiben mit weniger Original-Punkten gelten als leer (der Schnitt geht durch nichts).
    MINDEST = 3

    @classmethod
    def grenzen(cls, ruhe, innen, z_saat, zugabe_mm, flaeche):
        """`(hinten, vorn)` — die Grenzen in z (m): Saat ∓ `zugabe_mm`, nach außen gerückt, bis das Original dort flach auf der Figur liegt.

        `ruhe`: Punkte des Originals; `innen`: Maske der Punkte, deren Lage in der Vorderansicht im Schnittbereich liegt; `z_saat`: z der Saat;
        `flaeche`: Haut der Figur (trimesh)."""
        hinten = cls._grenze(ruhe, innen, float(np.min(z_saat)) - zugabe_mm / 1000.0, -1, flaeche)
        vorn = cls._grenze(ruhe, innen, float(np.max(z_saat)) + zugabe_mm / 1000.0, 1, flaeche)
        return hinten, vorn

    @classmethod
    def _grenze(cls, ruhe, innen, start, richtung, flaeche):
        import trimesh

        schritt = cls.SCHRITT_MM / 1000.0
        z, flach, erste = start, 0, start
        for _ in range(int(cls.MAX_MM / cls.SCHRITT_MM) + 1):
            lo, hi = sorted((z, z - richtung * schritt))                 # die Scheibe innen an der Grenze: dort liegt der Rand des Stücks
            scheibe = np.flatnonzero(innen & (ruhe[:, 2] >= lo) & (ruhe[:, 2] < hi))
            leer = len(scheibe) < cls.MINDEST
            if leer or float(np.median(trimesh.proximity.closest_point(flaeche, ruhe[scheibe])[1])) * 1000.0 <= cls.FLACH_MM:
                if flach == 0:
                    erste = z
                flach += 1
                if leer or flach >= cls.FOLGE:
                    return erste
            else:
                flach = 0
            z += richtung * schritt
        return z
