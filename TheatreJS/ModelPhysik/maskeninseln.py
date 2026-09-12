# -*- coding: utf-8 -*-
u"""Freie Inseln im Verdeckten schliessen (Achselfalte).

Herausgeloest aus `hautmaske.py` (12.09.2026). In der Achselfalte zeigt die
Hautnormale in den Arm, der Strahl trifft keinen Stoff, drei Punkte bleiben
frei — und der Faecher von Dreiecken um sie steht als Splitter aus dem
Aermel. Freie Gruppen bis `INSEL_MAX` Punkte, die ringsum an Verdecktes
grenzen, gelten deshalb als verdeckt.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


class Maskeninseln:
    u"""Freie Inseln im Verdeckten schliessen (Achselfalte)."""

    @staticmethod
    def schliessen(maske, dreiecke, hoechstens):
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        n = len(maske)
        kanten = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
        frei = ~maske[kanten].any(axis=1)
        kanten = kanten[frei]
        graph = coo_matrix((np.ones(len(kanten), dtype=np.int8),
                            (kanten[:, 0], kanten[:, 1])), shape=(n, n))
        anzahl, marke = connected_components(graph, directed=False)
        groesse = np.bincount(marke, minlength=anzahl)
        groesse_frei = np.where(np.bincount(marke, weights=~maske,
                                            minlength=anzahl) > 0, groesse, 0)
        groesste = groesse_frei.max() if len(groesse_frei) else 0
        insel = (groesse_frei <= hoechstens) & (groesse_frei < groesste) \
            & (groesse_frei > 0)
        neu = ~maske & insel[marke]
        maske[neu] = True
        return int(neu.sum())
