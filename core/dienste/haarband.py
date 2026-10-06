# -*- coding: utf-8 -*-
"""Haarband — Strähnen als flache Bänder: aus Mittellinien (Punktreihen) Dreiecke (05.10.2026).

Eine Strähne ist eine Punktreihe von der Wurzel zur Spitze. Das Band liegt quer zur Wuchsrichtung und zur Außennormale des Kopfes — die Kreuzprodukt-Richtung (`G9haarprofil.bandnetz` macht es ebenso: kamera-
unabhängig, darum gleich für Masken, Render und GLB). Jedes Band hat zwei Punkte je Reihenpunkt (links, rechts) und zwei Dreiecke je Segment, so gewunden, dass die Fläche nach außen zeigt (die Mitsuba-Materialien sind
einseitig). Ein Band liegt flach an der Kopfhaut: von außen gesehen die ganze Breite, von der Seite ein Strich — wie ein Haarbüschel.

    punkte, dreiecke, normalen = Haarband.baender(reihen (S, K, 3), aussen (S, K, 3) Einheit, halbbreite (S, K))
    index = Haarband.eckpunkte(S, K) → (S · 2K,) Strähne je Eckpunkt (für Haut und Gewichte)
"""

import numpy as np

__all__ = ['Haarband']


class Haarband:
    @staticmethod
    def baender(reihen, aussen, halbbreite):
        """`(punkte (S · 2K, 3), dreiecke (S · 2 (K − 1), 3), normalen (S · 2K, 3))` — Punkt `2 (s K + i)` links, `2 (s K + i) + 1` rechts von Reihenpunkt `i` der Strähne `s`."""
        s, k, _ = reihen.shape
        richtung = np.empty_like(reihen)
        richtung[:, :-1] = reihen[:, 1:] - reihen[:, :-1]
        richtung[:, -1] = richtung[:, -2]
        quer = np.cross(richtung, aussen)
        quer /= np.maximum(np.linalg.norm(quer, axis=2, keepdims=True), 1e-12)
        links = reihen + quer * halbbreite[..., None]
        rechts = reihen - quer * halbbreite[..., None]
        punkte = np.stack([links, rechts], axis=2).reshape(-1, 3)
        normalen = np.repeat(aussen.reshape(-1, 3), 2, axis=0)
        eins = np.arange(s)[:, None] * k * 2 + np.arange(k - 1)[None, :] * 2            # links des Reihenpunkts i: s · 2K + 2 i
        l0, r0, l1, r1 = eins, eins + 1, eins + 2, eins + 3
        dreiecke = np.stack([np.stack([l0, l1, r0], axis=-1), np.stack([r0, l1, r1], axis=-1)], axis=2).reshape(-1, 3)
        return punkte, dreiecke.astype(np.int64), normalen

    @staticmethod
    def eckpunkte(s, k, je=2):
        """Die Strähne je Eckpunkt (S · je · K,) — `je` Eckpunkte je Reihenpunkt (Band 2, Röhre 3)."""
        return np.repeat(np.arange(s), je * k)

    @staticmethod
    def roehren(reihen, aussen, radius):
        """Strähnen als dreiseitige Röhren statt flacher Bänder: `(punkte (S · 3K, 3), dreiecke (S · 6 (K − 1), 3))` — Punkt `3 (s K + i) + j` ist Ecke `j` des Dreiecksquerschnitts am Reihenpunkt `i` der Strähne `s`, `radius` (S, K). Ein
        Band ist von der Kante gesehen unsichtbar: am Rand des Kopfes (von vorn gesehen die Seiten), wo die Bänder dem Blick ihre Kante zeigen, schimmerte der dunkle Grund durch — eine schwarze Franse (Auftrag
        2026.10.04.21.41.43, Kopfbild von vorn). Die Röhre zeigt aus jeder Richtung eine Fläche; die Spitze des Dreiecks zeigt nach außen. Die Dreiecke zeigen nach außen (geprüft je Dreieck)."""
        s, k, _ = reihen.shape
        richtung = np.empty_like(reihen)
        richtung[:, :-1] = reihen[:, 1:] - reihen[:, :-1]
        richtung[:, -1] = richtung[:, -2]
        richtung /= np.maximum(np.linalg.norm(richtung, axis=2, keepdims=True), 1e-12)
        quer = np.cross(richtung, aussen)
        quer /= np.maximum(np.linalg.norm(quer, axis=2, keepdims=True), 1e-12)
        hoch = np.cross(quer, richtung)                                           # senkrecht zur Strähne, nach außen
        winkel = np.radians([90.0, 210.0, 330.0])
        ring = [reihen + radius[..., None] * (np.cos(w) * quer + np.sin(w) * hoch) for w in winkel]
        punkte = np.stack(ring, axis=2).reshape(-1, 3)                            # (S, K, 3 Ecken, 3) → Reihenfolge s, i, j
        ab = (np.arange(s)[:, None] * k + np.arange(k - 1)[None, :]) * 3          # erster Eckpunkt des Rings i
        dreiecke = []
        for j in range(3):
            n = (j + 1) % 3
            a0, a1, b0, b1 = ab + j, ab + n, ab + 3 + j, ab + 3 + n
            dreiecke += [np.stack([a0, a1, b0], axis=-1), np.stack([a1, b1, b0], axis=-1)]
        d = np.stack(dreiecke, axis=2).reshape(-1, 3).astype(np.int64)            # (S, K − 1, 6, 3) → (S · 6 (K − 1), 3)
        achse = reihen[:, :-1].reshape(-1, 3).repeat(6, axis=0)                   # der Reihenpunkt vor dem Segment, je Dreieck
        v0, v1, v2 = punkte[d[:, 0]], punkte[d[:, 1]], punkte[d[:, 2]]
        nach_innen = (np.cross(v1 - v0, v2 - v0) * ((v0 + v1 + v2) / 3.0 - achse)).sum(axis=1) < 0.0
        d[nach_innen] = d[nach_innen][:, ::-1]
        return punkte, d
