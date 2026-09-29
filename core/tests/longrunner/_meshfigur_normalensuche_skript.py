# -*- coding: utf-8 -*-
"""Skript für `test_meshfigur_normalensuche` (läuft unter python10, dort liegen torch und pytorch3d) — 29.09.2026.

Ein Kunstnetz mit Außenhaut (Normale +z, z = 0) und Innenwand 3 mm darunter (Normale −z), Käfigpunkte 2,1 mm unter der Haut:
näher an der Innenwand (0,9 mm) als an der Außenhaut. Gemessen wird für `kandidaten` = 1 (Verhalten bis 29.09.2026) und 16
(Vorgabe): welcher Anteil der Punkte die Außenhaut trifft, und welcher Anteil den Normalentest besteht (`figur_zu_netz`).

Aufruf: python10 _meshfigur_normalensuche_skript.py <pfad zu VideoToBVH/wrappers>
Ausgabe: eine Zeile `ERGEBNIS {"1": {"aussen": …, "passt": …}, "16": {…}}`.
"""
import json
import sys

import numpy as np
import torch

sys.path.insert(0, sys.argv[1])

from meshfigur_abstand import Meshfigurabstand  # noqa: E402

g = np.linspace(-0.03, 0.03, 61)
gx, gy = np.meshgrid(g, g)
n = gx.size
aussen = np.stack([gx.ravel(), gy.ravel(), np.zeros(n)], axis=1)
innen = np.stack([gx.ravel(), gy.ravel(), np.full(n, -0.003)], axis=1)
proben = np.concatenate([aussen, innen])
normalen = np.concatenate([np.tile([0.0, 0.0, 1.0], (n, 1)), np.tile([0.0, 0.0, -1.0], (n, 1))])
farben = np.full((len(proben), 3), 128, dtype=np.uint8)

gc = np.linspace(-0.02, 0.02, 9)
cx, cy = np.meshgrid(gc, gc)
punkte = np.stack([cx.ravel(), cy.ravel(), np.full(cx.size, -0.0021)], axis=1)
punktnormalen = np.tile([0.0, 0.0, 1.0], (len(punkte), 1))

ergebnis = {}
for k in (1, 16):
    abstand = Meshfigurabstand(
        proben, normalen, farben, np.zeros((1, 3), dtype=np.int64), np.zeros(len(punkte), dtype=np.int8),
        np.zeros(len(punkte), dtype=np.int64), torch.device('cpu'), kandidaten=k,
    )
    v = torch.as_tensor(punkte, dtype=torch.float32)
    vn = torch.as_tensor(punktnormalen, dtype=torch.float32)
    index = abstand._passende(v, vn, k).numpy()
    _, _, passt, _ = abstand.figur_zu_netz(v, vn, 0.03)
    ergebnis[str(k)] = {'aussen': float((normalen[index][:, 2] > 0).mean()), 'passt': float(passt.float().mean())}
print('ERGEBNIS ' + json.dumps(ergebnis))
