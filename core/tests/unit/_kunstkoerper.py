# -*- coding: utf-8 -*-
u"""Kunstkörper für die Masken-Tests: ein Zylinder um die y-Achse mit
`ringe` Reihen zu `n` Punkten, nach außen gewickelt — dieselbe Bauvorschrift
wie `zylinder()` in `test_js_hautmaske.py` (JS)."""
import numpy as np


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
