# -*- coding: utf-8 -*-
"""Haarstraehnen — die Strähnen EINES Stranghaar-Teils als zusammenhängende Punktfolge für die Haar-Dynamik des Stoffsolvers
(`Haardynamik`, 02.10.2026) und der Rückweg: die Lage danach als Delta je Käfigpunkt.

Der Solver (`Stoffsolver/haarauftrag.py`) will `punkte` (M, 3) aller Strähnen hintereinander, die WURZEL JEDER STRÄHNE ZUERST,
dazu `laengen` (S,) und die Normale der Kopfhaut an der Wurzel. Die Ketten liefert `G9haarzusatz.ketten` aus den Segmenten
des `G9strang`; `reihe` führt jede Stelle der Folge auf den Käfigpunkt zurück (Index-Rückabbildung), so liegt das Ergebnis
wieder auf den Punkten der Bibliothek und wird ein Morph wie jeder andere (`G9kleidmorphe.ablegen`).

**Wurzel zuerst** — an der echten Geometrie gemessen (02.10.2026, Käfig auf der Bühne, Abstand zu den Eckpunkten der Kopfhaut
`G9kopfhaut`): Pixie (21.755 Ketten) und Hime Cut (2.292) liefern `ketten` mit der Wurzel vorn — der erste Punkt liegt bei allen
Ketten höchstens 10,8 mm bzw. 8,7 mm von der Kopfhaut, keine Kette hat ihn weiter als 15 mm, und bei keiner liegt der LETZTE
Punkt an der Haut und der erste nicht. „Erster Punkt näher an der Haut als der letzte“ gilt nur bei 85,8 % bzw. 94,6 % — der
Rest sind Strähnen, die flach auf dem Kopf liegen, deren Ende also auch an der Haut liegt. Deshalb dreht `_wurzel_vorn` eine
Kette nur um, wenn ihr erster Punkt weiter als `FERN_M` von der Haut weg liegt UND der letzte näher; in den beiden gemessenen
Frisuren trifft das keine. Eine andere Frisur der Bibliothek kann es treffen — `umgedreht` und `wurzel_fern` stehen im
Steckbrief des Morphs. (Der Abstand ist der zum nächsten EckPUNKT der Haut: bei einer grob vernetzten Kappe überschätzt er den
Abstand zur Fläche um bis zu einen halben Punktabstand.)

Die Normale an der Wurzel ist die des nächsten Kopfhautpunkts (Flächenmittel der Dreiecke an ihm); Daz-Dreiecke zeigen nicht
verlässlich nach außen, deshalb gilt EIN Vorzeichen für alle: das, bei dem die Normalen im Mittel zur ersten Strecke der
Strähnen zeigen (Haar wächst nach außen). `normalen_ausgerichtet` ist der Anteil der Strähnen, bei denen das stimmt.
"""

import numpy as np
from scipy.spatial import cKDTree

__all__ = ['Haarstraehnen']


class Haarstraehnen:
    #: Eine Wurzel weiter als das von der Kopfhaut gilt als verdächtig (gemessen: Pixie und Hime Cut höchstens 10,8 mm).
    FERN_M = 0.02

    def __init__(self, punkte, ketten, haut):
        """`punkte` (N, 3): die Käfigpunkte des Teils (Bühne, Y oben, m); `ketten`: `[Indexfeld je Strähne]`
        (`G9haarzusatz.ketten`); `haut`: `G9kopfhaut.aus_teilen` → `{punkte, dreiecke, …}`."""
        punkte = np.asarray(punkte, dtype=np.float64)
        baum = cKDTree(np.asarray(haut['punkte'], dtype=np.float64))
        ketten, self.umgedreht = self._wurzel_vorn(ketten, punkte, baum)
        self.groesse = len(punkte)
        self.reihe = np.concatenate(ketten) if ketten else np.zeros(0, dtype=np.int64)
        self.laengen = np.array([len(k) for k in ketten], dtype=np.int32)
        self.punkte = punkte[self.reihe]
        self.wurzeln = np.cumsum(self.laengen) - self.laengen              # Stelle der Wurzel je Strähne in `punkte`
        abstand = baum.query(self.punkte[self.wurzeln])[0] if len(ketten) else np.zeros(0)
        self.wurzel_fern = int((abstand > self.FERN_M).sum())
        self.wurzel_abstand_max_mm = round(float(abstand.max()) * 1e3, 1) if len(abstand) else 0.0
        self.doppelt = int(len(self.reihe) - len(np.unique(self.reihe)))
        self.normalen, self.normalen_ausgerichtet = self._normalen(haut, baum)

    @property
    def anzahl(self):
        return int(len(self.laengen))

    @classmethod
    def _wurzel_vorn(cls, ketten, punkte, baum):
        """→ (Ketten mit der Wurzel vorn, Zahl der umgedrehten): umgedreht wird nur, wo der erste Punkt fern der Haut ist und
        der letzte näher (Moduldoc)."""
        if not ketten:
            return ketten, 0
        erst = baum.query(punkte[[k[0] for k in ketten]])[0]
        letzt = baum.query(punkte[[k[-1] for k in ketten]])[0]
        drehen = (erst > cls.FERN_M) & (letzt < erst)
        return [k[::-1] if d else k for k, d in zip(ketten, drehen, strict=True)], int(drehen.sum())

    def _normalen(self, haut, baum):
        """→ (Normalen (S, 3) der Kopfhaut an den Wurzeln, Anteil der Strähnen, deren Normale zur ersten Strecke zeigt)."""
        if not self.anzahl:
            return np.zeros((0, 3)), 0.0
        p = np.asarray(haut['punkte'], dtype=np.float64)
        d = np.asarray(haut['dreiecke'], dtype=np.int64)
        flaeche = np.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])             # Länge = 2 · Fläche: flächengewichtet
        eck = np.zeros_like(p)
        for k in range(3):
            np.add.at(eck, d[:, k], flaeche)
        eck /= np.maximum(np.linalg.norm(eck, axis=1), 1e-12)[:, None]
        wurzel = self.punkte[self.wurzeln]
        normalen = eck[baum.query(wurzel)[1]]
        strecke = self.punkte[self.wurzeln + 1] - wurzel
        strecke /= np.maximum(np.linalg.norm(strecke, axis=1), 1e-12)[:, None]
        zeigt = np.einsum('ij,ij->i', normalen, strecke)
        if float(zeigt.sum()) < 0.0:
            normalen, zeigt = -normalen, -zeigt
        return normalen, round(float((zeigt > 0.0).mean()), 4)

    def delta(self, lage):
        """Die Lage der Strähnenpunkte nach der Rechnung (M, 3) als Delta je Käfigpunkt (N, 3). Gerechnet gegen die Ausgangslage,
        wie der Solver sie bekam (float32); die Wurzeln bekommen genau 0 — sie sind angeheftet, der Unterschied wäre Rundung."""
        lage = np.asarray(lage, dtype=np.float64)
        if lage.shape != self.punkte.shape:
            raise ValueError('Haar-Dynamik: %s Punkte zurück, erwartet %s' % (lage.shape, self.punkte.shape))
        if not np.isfinite(lage).all():
            raise RuntimeError('Haar-Dynamik: das Ergebnis enthält Punkte, die nicht endlich sind (nan/inf)')
        aus = np.zeros((self.groesse, 3))
        aus[self.reihe] = lage - self.punkte.astype(np.float32).astype(np.float64)
        aus[self.reihe[self.wurzeln]] = 0.0
        return aus
