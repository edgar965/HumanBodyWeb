# -*- coding: utf-8 -*-
"""Kunstnetz für die Tests der Kleidungsmaske (`test_kleidungsbereinigung`, `test_kleidungsrunden`): ein Gitter aus Dreiecken, je Zelle zwei."""

import numpy as np
from scipy.sparse import coo_matrix


def _gitter(n):
    """`(dreiecke (T, 3), nachbarn (T, T), zelle (T,))` — n × n Zellen, je zwei Dreiecke; Nachbarn = gemeinsame Kante."""
    dreiecke, zelle = [], []
    for y in range(n):
        for x in range(n):
            a, b, c, d = y * (n + 1) + x, y * (n + 1) + x + 1, (y + 1) * (n + 1) + x, (y + 1) * (n + 1) + x + 1
            dreiecke += [(a, b, c), (b, d, c)]
            zelle += [y * n + x] * 2
    f = np.asarray(dreiecke)
    kanten = np.sort(f[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
    schluessel = kanten[:, 0] * (f.max() + 1) + kanten[:, 1]
    flaeche = np.repeat(np.arange(len(f)), 3)
    ordnung = np.argsort(schluessel, kind='stable')
    s, i = schluessel[ordnung], flaeche[ordnung]
    gleich = s[1:] == s[:-1]
    a, b = i[:-1][gleich], i[1:][gleich]
    m = coo_matrix((np.ones(len(a) * 2), (np.r_[a, b], np.r_[b, a])), shape=(len(f), len(f))).tocsr()
    return f, m, np.asarray(zelle)


def _bau(n=20, cm2_je_flaeche=0.01):
    f, nachbarn, zelle = _gitter(n)
    inhalt = np.full(len(f), cm2_je_flaeche * 1e-4)
    hoehe = np.zeros(len(f))                                      # alles unter dem Kopf
    return f, nachbarn, zelle, inhalt, hoehe
