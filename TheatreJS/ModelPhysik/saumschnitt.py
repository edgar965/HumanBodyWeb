# -*- coding: utf-8 -*-
u"""Saumschnitt — verdeckte Randecken enden an der Stoffkante, nicht ein Zahn
darunter. Dieselbe Regel wie `static/viewer/gemeinsam/saumschnitt.js`.

BEFUND (Edgar, 13.09.2026, Bild vom Bund der Hose von oben: „der Innensaum
der Kleider ist eckig, der soll so sein wie die Aussenhaut"): Der Einzug
der verdeckten Ecke jedes Randdreiecks um 1 cm nach innen kippt das
Dreieck in den Koerper — von oben zeigt es seine Rueckseite, und durch das
Loch sieht man die Innenseite der Hose: ein schwarzer Zahn je Hautdreieck.

DER WEG: Eine verdeckte Ecke eines GEZEICHNETEN Randdreiecks, die nah an
einer Stoffkante liegt, wandert entlang der Haut unter die Kante — auf den
naechsten Punkt der naechsten Kantenstrecke, in die Tangentialebene
projiziert, dazu `UNTERKANTE_M` nach innen. Fern jeder Kante (lockere
Saeume, Maskengrenzen im Stoffinneren) bleibt der Einzug nach innen.

IM FILM je Bild: Die Zuordnung Ecke -> Kantenstrecke (Stueck, a, b, t)
wird EINMAL in Ruhelage bestimmt (dort ist die Maske gerechnet) und je Bild
auf den GESTELLTEN Kanten ausgewertet — die Ecke folgt ihrer Kante, wie im
Browser der Einzug vor dem Skinning mitdreht.
"""
import numpy as np


class Saumschnitt:
    u"""Zuordnung der verdeckten Randecken zu Stoffkanten und ihr Einzug."""

    #: Naeher als das an einer Stoffkante: an die Kante statt nach innen.
    SCHNAPP_M = 0.015
    #: So weit unter die Kante (entlang der Normale nach innen).
    UNTERKANTE_M = 0.001

    def __init__(self, ecken, stueck, a, b, t):
        self.ecken = np.asarray(ecken, dtype=np.int64)
        self.stueck = np.asarray(stueck, dtype=np.int64)
        self.a = np.asarray(a, dtype=np.int64)
        self.b = np.asarray(b, dtype=np.int64)
        self.t = np.asarray(t, dtype=np.float64)

    def __len__(self):
        return len(self.ecken)

    # --------------------------------------------------------------- binden

    @classmethod
    def binden(cls, punkte, dreiecke, maske, stoffe):
        u"""Ruhelage: je verdeckter Randecke die naechste Kantenstrecke.

        `stoffe`: Liste (punkte, dreiecke) der Stuecke DARUEBER, in derselben
        Lage. Ecken ohne Kante binnen `SCHNAPP_M` fehlen im Ergebnis.
        """
        ecken = cls.randecken(maske, dreiecke)
        if not len(ecken):
            return cls([], [], [], [], [])
        P = np.asarray(punkte, dtype=np.float64)[ecken]
        best = np.full(len(ecken), cls.SCHNAPP_M ** 2)
        stueck = np.full(len(ecken), -1)
        A = np.zeros(len(ecken), dtype=np.int64)
        B = np.zeros(len(ecken), dtype=np.int64)
        T = np.zeros(len(ecken))
        for s, (sp, sd) in enumerate(stoffe):
            kanten = cls.kanten(np.asarray(sd))
            if not len(kanten):
                continue
            d2, (t, wahl) = cls._naechste_strecke(P, np.asarray(sp, dtype=np.float64), kanten)
            naeher = d2 < best
            best[naeher] = d2[naeher]
            stueck[naeher] = s
            A[naeher] = kanten[wahl[naeher], 0]
            B[naeher] = kanten[wahl[naeher], 1]
            T[naeher] = t[naeher]
        drin = stueck >= 0
        return cls(ecken[drin], stueck[drin], A[drin], B[drin], T[drin])

    @staticmethod
    def randecken(maske, dreiecke):
        u"""Verdeckte Ecken, die an einem gezeichneten Dreieck haengen."""
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        m = np.asarray(maske, dtype=bool)[T]
        gemischt = m.any(axis=1) & ~m.all(axis=1)
        ecken = T[gemischt][m[gemischt]]
        return np.unique(ecken)

    @staticmethod
    def kanten(dreiecke):
        u"""Offene Kanten (in genau einem Dreieck) als (k, 2) Punktpaare."""
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        if not len(T):
            return np.zeros((0, 2), dtype=np.int64)
        k = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
        k.sort(axis=1)
        _, index, zaehler = np.unique(k, axis=0, return_index=True, return_counts=True)
        return k[index[zaehler == 1]]

    @staticmethod
    def _naechste_strecke(P, S, kanten):
        u"""Je Punkt in P: Quadratabstand zur naechsten Strecke und
        (t, Streckenindex). Dicht genug fuer Hunderte Ecken gegen
        Hunderte Kanten — alles auf einmal."""
        A = S[kanten[:, 0]]
        E = S[kanten[:, 1]] - A
        e2 = np.einsum('ij,ij->i', E, E)
        e2[e2 == 0] = 1.0
        rel = P[:, None, :] - A[None, :, :]                  # (n, k, 3)
        t = np.clip(np.einsum('nkj,kj->nk', rel, E) / e2[None, :], 0.0, 1.0)
        Q = A[None, :, :] + t[:, :, None] * E[None, :, :]
        d2 = np.einsum('nkj,nkj->nk', Q - P[:, None, :], Q - P[:, None, :])
        wahl = np.argmin(d2, axis=1)
        zeilen = np.arange(len(P))
        return d2[zeilen, wahl], (t[zeilen, wahl], wahl)

    # ------------------------------------------------------------- anwenden

    def anwenden(self, punkte, normalen, stoffpunkte):
        u"""Die gebundenen Ecken (an Ort und Stelle in `punkte`) unter ihre
        Kante legen — `stoffpunkte[s]` sind die Punkte des Stuecks s in
        DIESEM Bild. Gibt die Zahl der gelegten Ecken zurueck."""
        if not len(self):
            return 0
        Q = np.zeros((len(self), 3))
        for s in np.unique(self.stueck):
            wer = self.stueck == s
            S = np.asarray(stoffpunkte[s], dtype=np.float64)
            Q[wer] = S[self.a[wer]] + self.t[wer, None] * (S[self.b[wer]] - S[self.a[wer]])
        p = punkte[self.ecken]
        n = normalen[self.ecken]
        d = Q - p
        d -= np.einsum('ij,ij->i', d, n)[:, None] * n
        punkte[self.ecken] = p + d - self.UNTERKANTE_M * n
        return len(self)
