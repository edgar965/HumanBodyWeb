# -*- coding: utf-8 -*-
u"""Normalen und Strahltests der Masken — reine Rechnung.

Herausgeloest aus `hautmaske.py` (12.09.2026, vier Klassen in einer Datei).
Die Normalen kommen von der HAUT (Vorzeichen ueber das signierte Volumen —
die Mehrheit gegen den Schwerpunkt kippte in manchen Posen), der Strahl
ist Moeller-Trumbore, beidseitig.
"""
import numpy as np

from streusumme import Streusumme


class Geometrie:
    u"""Normalen und Strahltests — reine Rechnung."""

    @staticmethod
    def normalen(P, T):
        u"""Punktnormalen nach aussen (Vorzeichen ueber das signierte Volumen)."""
        P = np.asarray(P, dtype=np.float64)
        T = np.asarray(T, dtype=np.int64).reshape(-1, 3)
        a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        fn = np.cross(b - a, c - a)
        vol = float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum())
        N = np.zeros_like(P)
        for k in range(3):
            Streusumme.dazu(N, T[:, k], fn)
        N *= 1.0 if vol >= 0 else -1.0
        laenge = np.linalg.norm(N, axis=1, keepdims=True)
        return N / np.maximum(laenge, 1e-12)

    @staticmethod
    def strahl_dreiecke(P, T, kandidaten, p, r):
        u"""Moeller-Trumbore fuer (M, K) Kandidaten je Strahl — t oder NaN.

        `kandidaten` traegt -1 als Fuellwert. Beidseitig, `r` normiert."""
        gueltig = kandidaten >= 0
        kk = np.where(gueltig, kandidaten, 0)
        a = P[T[kk, 0]]
        e1 = P[T[kk, 1]] - a
        e2 = P[T[kk, 2]] - a
        rr = r[:, None, :]
        h = np.cross(rr, e2)
        det = np.einsum('mkj,mkj->mk', e1, h)
        gut = gueltig & (np.abs(det) > 1e-12)
        f = 1.0 / np.where(gut, det, 1.0)
        s = p[:, None, :] - a
        u = f * np.einsum('mkj,mkj->mk', s, h)
        q = np.cross(s, e1)
        v = f * np.einsum('mkj,mkj->mk', rr, q)
        t = f * np.einsum('mkj,mkj->mk', e2, q)
        innen = gut & (u >= 0) & (u <= 1) & (v >= 0) & (u + v <= 1)
        return np.where(innen, t, np.nan)
