# -*- coding: utf-8 -*-
u"""Streusumme — Werte nach Index aufsummieren, in einem Zug.

`np.add.at(ziel, index, werte)` arbeitet elementweise und ist auf grossen
Feldern um ein Vielfaches langsamer als `np.bincount(index, weights=…)`
(Lehre `bincount-statt-add-at`, Befund `lehren-treue` 12.09.2026). Der
Unterschied zaehlt hier: `Hautbahn._lbs` laeuft je Videobild ueber alle
Punkt-Knochen-Paare, die Normalen der Hautmaske und der Stoffgrenze ueber
138.304 Dreiecke.

Fuer ein Feld mit Spalten (N, 3) laeuft `bincount` je Spalte — drei Aufrufe
sind immer noch ein Bruchteil der elementweisen Schleife.
"""
import numpy as np


class Streusumme:
    u"""`summe[i] = Σ werte[k] fuer alle k mit index[k] == i`."""

    @staticmethod
    def zeilen(index, werte, anzahl):
        u"""Summe je Zeile; `werte` eindimensional oder (K, S)."""
        index = np.asarray(index, dtype=np.int64).ravel()
        werte = np.asarray(werte, dtype=np.float64)
        if werte.ndim == 1:
            return np.bincount(index, weights=werte, minlength=anzahl)[:anzahl]
        spalten = werte.reshape(len(index), -1)
        aus = np.empty((anzahl, spalten.shape[1]), dtype=np.float64)
        for s in range(spalten.shape[1]):
            aus[:, s] = np.bincount(index, weights=spalten[:, s],
                                    minlength=anzahl)[:anzahl]
        return aus.reshape((anzahl,) + werte.shape[1:])

    @classmethod
    def dazu(cls, ziel, index, werte):
        u"""Wie `np.add.at(ziel, index, werte)` — addiert auf `ziel`."""
        ziel += cls.zeilen(index, werte, len(ziel)).astype(ziel.dtype, copy=False)
        return ziel
