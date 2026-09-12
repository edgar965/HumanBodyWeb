# -*- coding: utf-8 -*-
u"""Kunstkörper für Masken-, Vorschau- und Nachführungstests.

`zylinder`: ein Zylinder um die y-Achse mit `ringe` Reihen zu `n` Punkten,
nach außen gewickelt — dieselbe Bauvorschrift wie `zylinder()` in
`test_js_hautmaske.py` (JS).

`wuerfel`: ein geschlossener Quader 1 m, Y oben, je Seite `n` × `n` Felder.
UNTERTEILT, nicht mit 12 Dreiecken: `DreiecksProjektion` fragt den KD-Baum
nach `KANDIDATEN = 32` Nachbarn. Ein Netz mit weniger Dreiecken läuft dort
aus dem Feld (IndexError). Körpernetze haben 17.288 Dreiecke; ein zu grobes
Testnetz prüft also einen Fall, den es nicht gibt. Stand bis zum 12.09.2026
in `test_stoffvorschau` und wurde von zwei anderen Tests importiert.
"""
import numpy as np


class Kunstkoerper:
    u"""Geschlossene Netze mit bekannter Form — `(punkte, dreiecke)`."""

    @staticmethod
    def zylinder(radius, y0, y1, ringe, n):
        P, T = [], []
        for r in range(ringe):
            y = y0 + (y1 - y0) * r / (ringe - 1)
            for i in range(n):
                w = 2 * np.pi * i / n
                P.append((radius * np.cos(w), y, radius * np.sin(w)))
        for r in range(ringe - 1):
            for i in range(n):
                a, b = r * n + i, r * n + (i + 1) % n
                c, d = (r + 1) * n + i, (r + 1) * n + (i + 1) % n
                T.append((a, c, b))
                T.append((b, c, d))
        return np.array(P, dtype=np.float32), np.array(T, dtype=np.int64)

    @staticmethod
    def wuerfel(n=6):
        punkte, dreiecke = [], []
        # Sechs Seiten, jede als Gitter. `achse` ist die feste Richtung.
        seiten = [(0, -.5), (0, .5), (1, 0.), (1, 1.), (2, -.5), (2, .5)]
        for achse, wert in seiten:
            ab = len(punkte)
            frei = [i for i in range(3) if i != achse]
            for a in range(n + 1):
                for b in range(n + 1):
                    p = [0.0, 0.0, 0.0]
                    p[achse] = wert
                    p[frei[0]] = -.5 + a / n if frei[0] != 1 else a / n
                    p[frei[1]] = -.5 + b / n if frei[1] != 1 else b / n
                    punkte.append(p)
            for a in range(n):
                for b in range(n):
                    i = ab + a * (n + 1) + b
                    j = i + (n + 1)
                    dreiecke.append([i, j, i + 1])
                    dreiecke.append([i + 1, j, j + 1])
        return np.asarray(punkte, dtype=float), np.asarray(dreiecke, dtype=int)
