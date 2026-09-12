# -*- coding: utf-8 -*-
u"""Stoff unter Stoff: welche Punkte eines Stuecks unter einem anderen liegen.

Herausgeloest aus `hautmaske.py` (12.09.2026). Wer aussen liegt, wird je Paar
GEZAEHLT (Punkte mit dem anderen Stueck mindestens `MINDEST_M` vor sich); die
Normalen kommen von der Haut, nie vom Stoffnetz — dessen Dreiecksorientierung
kann zum Koerper zeigen. Browser-Fassung: `gemeinsam/lagenmaske.js`.
"""
import numpy as np
from scipy.spatial import cKDTree

from hautmaske import Hautmaske
from maskengeometrie import Geometrie


class Lagenmaske:
    u"""Welche Punkte eines Stuecks unter einem anderen liegen."""

    MINDEST_M = 0.001

    @classmethod
    def verdeckt(cls, koerper, koerperdreiecke, stoffe, **optionen):
        u"""`stoffe`: Liste von (name, punkte, dreiecke). Liefert
        {name: (maske, [namen der Stuecke darueber])}."""
        koerper = np.asarray(koerper, dtype=np.float64)
        N = Geometrie.normalen(koerper, koerperdreiecke)
        baum = cKDTree(koerper)
        normalen = [cls.normalen_von_haut(np.asarray(p, dtype=np.float64), N, baum)
                    for _n, p, _t in stoffe]
        aus = {name: (np.zeros(len(p), dtype=bool), [])
               for name, p, _t in stoffe}
        for a in range(len(stoffe)):
            for b in range(a + 1, len(stoffe)):
                lage = cls.lage(stoffe[a], normalen[a], stoffe[b], normalen[b],
                                **optionen)
                if lage == 0:
                    continue
                innen, aussen, n_innen = ((stoffe[a], stoffe[b], normalen[a])
                                          if lage > 0 else
                                          (stoffe[b], stoffe[a], normalen[b]))
                m = Hautmaske.verdeckt(innen[1], innen[2], [(aussen[1], aussen[2])],
                                       normalen=n_innen, **optionen)
                aus[innen[0]][0][:] |= m
                aus[innen[0]][1].append(aussen[0])
        return aus

    @classmethod
    def lage(cls, A, nA, B, nB, **optionen):
        o = dict(optionen)
        o.update(tiefe=-cls.MINDEST_M, randringe=0, inseln=0,
                 suchweite=optionen.get('abstand', Hautmaske.ABSTAND_M))
        b_ueber_a = int(Hautmaske.verdeckt(A[1], None, [(B[1], B[2])],
                                           normalen=nA, **o).sum())
        a_ueber_b = int(Hautmaske.verdeckt(B[1], None, [(A[1], A[2])],
                                           normalen=nB, **o).sum())
        if not b_ueber_a and not a_ueber_b:
            return 0
        return 1 if b_ueber_a >= a_ueber_b else -1

    @staticmethod
    def normalen_von_haut(P, N, baum):
        d, i = baum.query(P, distance_upper_bound=0.09, workers=-1)
        aus = np.zeros_like(P)
        nah = np.isfinite(d)
        aus[nah] = N[i[nah]]
        return aus
