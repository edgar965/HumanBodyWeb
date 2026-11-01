# -*- coding: utf-8 -*-
"""Exportleisteinseln — freie Inseln in der Hautmaske schließen, nach der Regel des Browsers (`static/viewer/gemeinsam/maskeninseln.js`, 31.10.2026).

Die Python-Fassung des Server-Videowegs (`TheatreJS/ModelPhysik/maskeninseln.py`) schließt JEDE freie Gruppe bis `INSEL_MAX` Punkte außer der größten. Der Browser hat seit dem
12./13./24.09.2026 drei Regeln mehr, und alle drei treffen den Körper der Exportleiste:
  Küste    nur eine Gruppe, die über eine Kante an Verdecktes grenzt, ist eine Insel; ein Teil für sich (Zähne, Nägel hinter einer Naht) nicht
  Lage     Punkte gleicher Lage sind ein Punkt — hier erfüllt, weil `Exportleistehautmaske.maske` den Körper vorher verschweißt
  Fläche   eine Gruppe gilt auch als klein, wenn ihre ganz freien Dreiecke höchstens `FLAECHE_M2` groß sind (Achsel unter dem Ärmel bei Genesis 9: 298 Punkte, 38 cm²)
Gemessen 31.10.2026 an der Browser-GLB des Renders Test edgar (`ProjektTemp/_wegwerf/exportleiste/maske_neu_vergleich.py`, `maske_unterschied.py`): Der Render-Körper
(Grundstufe, 50.312 Dreiecke) zerfällt roh in 31 Teile, 20 davon unter 200 Punkten — die Finger- und Zehennägel (je 79, 104 oder 131 Punkte), 10 bis 75 cm vom nächsten Stoff.
Die alte Regel nahm sie alle weg (5.037 Dreiecke weg, die neue 1.471). In der feinen Stufe der GLB sind die Teile größer als 200 Punkte (4.624 gegen 4.594 Dreiecke weg).
Dazu 181 Punkte im Schritt unter der lockeren Hose: alt schnitt sie die UV-Naht Rumpf/Bein als Insel ab, neu hängen sie an der freien Haut der Beine (7.416 Punkte).

    Exportleisteinseln.schliessen(maske, punkte, dreiecke)      # maske (bool je Punkt) an Ort und Stelle → Zahl der neu verdeckten Punkte
"""

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

__all__ = ['Exportleisteinseln']


class Exportleisteinseln:
    #: wie `Hautmaske.INSEL_MAX` in `hautmaske.js` / `hautmaske.py`
    PUNKTE = 200
    #: wie `Hautmaske.INSEL_FLAECHE_M2` in `hautmaske.js`
    FLAECHE_M2 = 0.005

    @classmethod
    def schliessen(cls, maske, punkte, dreiecke, punkte_max=None, flaeche_max=None):
        punkte_max = cls.PUNKTE if punkte_max is None else punkte_max
        flaeche_max = cls.FLAECHE_M2 if flaeche_max is None else flaeche_max
        P = np.asarray(punkte, dtype=np.float64).reshape(-1, 3)
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        n = len(maske)
        k = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
        frei = ~maske[k[:, 0]] & ~maske[k[:, 1]]
        anzahl, marke = connected_components(coo_matrix((np.ones(int(frei.sum()), dtype=np.int8), (k[frei, 0], k[frei, 1])), shape=(n, n)), directed=False)
        groesse = np.bincount(marke[~maske], minlength=anzahl)
        if not groesse.any():
            return 0
        rand = k[maske[k[:, 0]] != maske[k[:, 1]]]
        kueste = np.zeros(anzahl, dtype=bool)
        kueste[marke[np.where(maske[rand[:, 0]], rand[:, 1], rand[:, 0])]] = True
        klein = groesse <= punkte_max
        if flaeche_max > 0:
            tf = T[~maske[T].any(axis=1)]
            a = 0.5 * np.linalg.norm(np.cross(P[tf[:, 1]] - P[tf[:, 0]], P[tf[:, 2]] - P[tf[:, 0]]), axis=1)
            klein |= np.bincount(marke[tf[:, 0]], weights=a, minlength=anzahl) <= flaeche_max
        insel = klein & kueste & (groesse > 0) & (groesse < groesse.max())
        neu = ~maske & insel[marke]
        maske[neu] = True
        return int(neu.sum())
