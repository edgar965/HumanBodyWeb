# -*- coding: utf-8 -*-
"""Meshfigurteileanschluss — ein langer, starrer Bestandteil nimmt die Flächen auf, die ihm anliegen und zusammenhängen (14.10.2026).

Anlass (Edgar, Zauberer im Tanz: „Zauberstab … ist nicht durchgängig", unten blieb ein dünner Ast am Boden stehen): SAM 3 findet den Stab nur dort, wo ihn die Masken der Ansichten treffen. Gemessen am Netz
(`ProjektTemp/_wegwerf/mesh3d/stab_reste_*.py`, Haltungsfassungen): **7.434 Flächen der Robe liegen mit allen Ecken höchstens 35 mm vom Stab** (5.351 binnen 6 mm, 1.648 mit allen drei Ecken auf Eckpunkten des Stabs
selbst), 5.586 davon zwischen 0,1 und 0,6 m Höhe — dort hat der Stab 2.400 Flächen je 10 cm, die Robe trägt 600 bis 1.200 Flächen daneben. Der Stab steht dort neben dem Körper, es ist kein Stoff in der Nähe: die
Flächen sind Stab, vom Etikett der Kleidung (Sapiens, Regeln der Maske) mitgenommen. Sie bewegten sich mit den Hautgewichten der Kleidung (Beine), der Stab mit der Hand: der untere Teil blieb als loser Ast zurück.

Die Regel kennt keinen Gegenstand: ist ein Bestandteil lang und dünn (`Meshfigurhalter.stabfoermig`, Stab, Schwert, Schirm), gehören ihm auch Flächen anderer Etiketten, deren Ecken ALLE höchstens `ANSCHLUSS_M` von Punkten
des Bestandteils entfernt liegen — und die über gemeinsame Punkte mit ihm zusammenhängen (Flächen, die nur zufällig vorbeiziehen, bleiben, wo sie sind). Flächen anderer Bestandteile werden nie genommen. `ANSCHLUSS_M` 12 mm ist eine
Setzung (an einem Modell gemessen, ohne die Bedingung des Zusammenhangs: binnen 6 mm 5.351 Flächen, 10 mm 6.250, 20 mm 7.234, 35 mm 7.434 — danach kaum noch mehr).
"""

import numpy as np

__all__ = ['Meshfigurteileanschluss']


class Meshfigurteileanschluss:
    ANSCHLUSS_M = 0.012
    #: Höchstens so viele Runden beim Wachsen über gemeinsame Punkte (ein Stab ist 1–2 m lang, die Flächen sind Zentimeter groß).
    RUNDEN = 400

    @classmethod
    def erweitern(cls, flaechen, punkte, maske, andere):
        """Die Maske `maske` (F,) bool eines stabförmigen Bestandteils um die anliegenden, zusammenhängenden Flächen erweitern; `andere` (F,) bool = Flächen anderer Bestandteile (bleiben draußen).
        Gibt `(neue Maske, Zahl der hinzugekommenen Flächen)` zurück."""
        from scipy.spatial import cKDTree

        flaechen = np.asarray(flaechen)
        punkte = np.asarray(punkte, dtype=np.float64)
        eigene = np.unique(flaechen[maske].reshape(-1))
        if not len(eigene):
            return maske, 0
        kern = punkte[eigene]
        lo, hi = kern.min(axis=0) - cls.ANSCHLUSS_M, kern.max(axis=0) + cls.ANSCHLUSS_M
        kandidaten = np.flatnonzero(~maske & ~np.asarray(andere, dtype=bool))
        ecken = punkte[flaechen[kandidaten]]                                         # (K, 3, 3)
        im_kasten = ((ecken >= lo) & (ecken <= hi)).all(axis=2).all(axis=1)
        kandidaten, ecken = kandidaten[im_kasten], ecken[im_kasten]
        if not len(kandidaten):
            return maske, 0
        abstand, _ = cKDTree(kern).query(ecken.reshape(-1, 3), workers=-1)
        nah = (abstand.reshape(-1, 3) <= cls.ANSCHLUSS_M).all(axis=1)
        kandidaten = kandidaten[nah]
        # Wachsen: nur Flächen, die über einen Punkt mit dem Bestandteil (oder einer schon aufgenommenen Fläche) zusammenhängen.
        bekannt = np.zeros(len(punkte), dtype=bool)
        bekannt[eigene] = True
        genommen = np.zeros(len(kandidaten), dtype=bool)
        ecken_nummern = flaechen[kandidaten]
        for _ in range(cls.RUNDEN):
            neu = ~genommen & bekannt[ecken_nummern].any(axis=1)
            if not neu.any():
                break
            genommen |= neu
            bekannt[ecken_nummern[neu].reshape(-1)] = True
        aus = maske.copy()
        aus[kandidaten[genommen]] = True
        return aus, int(genommen.sum())
