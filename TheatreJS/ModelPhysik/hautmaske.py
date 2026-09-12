# -*- coding: utf-8 -*-
u"""Hautmaske fuer den Server-Videoweg — dieselben Regeln wie im Browser.

Der Browser (`static/viewer/gemeinsam/hautmaske.js`, 11.09.2026) zeichnet
die Haut unter dem Stoff nicht mehr: Was nicht gezeichnet wird, kann in
keiner Pose durchkommen. Das Video vom Server rendert seinen eigenen
Koerper, und dort galt die Maske nicht — die Haut kam durch die Leggings,
obwohl die Szene sauber war. Hier steht die Rechnung in NumPy, Regel fuer
Regel gleich (`core/tests/unit/test_hautmaske_python.py` haelt beide
Fassungen am selben Kunstkoerper aneinander):

* VERDECKT ist ein Koerperpunkt, wenn der Strahl entlang seiner Normale ein
  Stoffdreieck trifft — hoechstens `ABSTAND_M` darueber, hoechstens
  `TIEFE_M` in der Haut. Gesucht wird bei den Dreiecken bis zwei Ringe um
  den naechsten Stoffpunkt.
* Ein Randstreifen (`RANDRINGE`) bleibt nur an LOCKEREN Stoffkanten frei
  (mehr als `ENG_M` ueber der Haut); eine anliegende Kante maskiert bis zum
  Rand — der Bund der 2-mm-Leggings war sonst genau die Haut, die herauskam.
* Freie Inseln im Verdeckten (bis `INSEL_MAX` Punkte) gelten als verdeckt
  (Achselfalte: die Normale trifft dort keinen Stoff).
* Ein Dreieck faellt weg, wenn alle drei Ecken verdeckt sind; die
  verdeckten Ecken der Randdreiecke ziehen sich beim Rendern `EINZUG_M`
  nach innen (`Filmrender`).
* Stoff unter Stoff (`lagenmaske.py`): Wer aussen liegt, wird gezaehlt; die
  Normalen kommen von der Haut, nie vom Stoffnetz.

Seit dem 12.09.2026 je Klasse eine Datei: `maskengeometrie.py` (Normalen,
Strahl), `maskeninseln.py`, `lagenmaske.py`.
"""
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, identity
from scipy.spatial import cKDTree

from maskengeometrie import Geometrie
from maskeninseln import Maskeninseln


class Hautmaske:
    u"""Welche Koerperpunkte unter einem Stueck liegen."""

    ABSTAND_M = 0.025
    TIEFE_M = 0.005
    RANDRINGE = 2
    ENG_M = 0.004
    INSEL_MAX = 200
    EINZUG_M = 0.010

    @classmethod
    def verdeckt(cls, koerper, dreiecke, stoffe, abstand=None, tiefe=None,
                 randringe=None, eng=None, normalen=None, suchweite=None,
                 inseln=None):
        u"""Bool je Koerperpunkt. `stoffe`: Liste von (punkte, dreiecke)."""
        w = cls.werte(abstand=abstand, tiefe=tiefe, randringe=randringe,
                      eng=eng, suchweite=suchweite, inseln=inseln)
        koerper = np.asarray(koerper, dtype=np.float64)
        if normalen is None:
            normalen = Geometrie.normalen(koerper, dreiecke)
        normalen = np.asarray(normalen, dtype=np.float64)
        baum = cKDTree(koerper)
        maske = np.zeros(len(koerper), dtype=bool)
        for punkte, tris in stoffe:
            if cls._leer(punkte, tris):
                continue
            cls._ein_stueck(koerper, normalen, baum, maske,
                            np.asarray(punkte, dtype=np.float64),
                            np.asarray(tris, dtype=np.int64).reshape(-1, 3),
                            w['abstand'], w['tiefe'], w['randringe'], w['eng'],
                            w['suchweite'])
        if w['inseln'] > 0 and dreiecke is not None:
            Maskeninseln.schliessen(maske, dreiecke, w['inseln'])
        return maske

    @classmethod
    def werte(cls, **wahl):
        u"""Die Masse der Maske: `None` heisst Klassenkonstante; die Suchweite
        folgt ohne Angabe dem groesseren von Abstand und Tiefe."""
        vorgaben = {'abstand': cls.ABSTAND_M, 'tiefe': cls.TIEFE_M,
                    'randringe': cls.RANDRINGE, 'eng': cls.ENG_M,
                    'inseln': cls.INSEL_MAX}
        w = {name: (vorgabe if wahl.get(name) is None else wahl[name])
             for name, vorgabe in vorgaben.items()}
        suchweite = wahl.get('suchweite')
        w['suchweite'] = (max(w['abstand'], w['tiefe']) if suchweite is None
                          else suchweite)
        return w

    @staticmethod
    def _leer(punkte, tris):
        u"""Ein Stueck ohne Punkte oder ohne Dreiecke verdeckt nichts."""
        return (punkte is None or tris is None
                or not len(punkte) or not len(tris))

    @classmethod
    def _ein_stueck(cls, koerper, normalen, baum, maske, P, T,
                    abstand, tiefe, ringe, eng, suchweite):
        rand, nachbarn = cls.randpunkte(T, len(P))
        locker = cls.lockere_randpunkte(P, rand, koerper, normalen, baum, eng)
        gesperrt = cls.ringe_um(locker, nachbarn, ringe)
        ok = ~gesperrt[T].any(axis=1)
        umkreis = cls.dreiecke_im_umkreis(T, len(P), ok, nachbarn)
        d, j = cKDTree(P).query(koerper, distance_upper_bound=suchweite, workers=-1)
        kand = np.where(~maske & np.isfinite(d))[0]
        if not len(kand):
            return
        t = Geometrie.strahl_dreiecke(P, T, umkreis[j[kand]],
                                      koerper[kand], normalen[kand])
        with np.errstate(invalid='ignore'):
            treffer = np.any((t >= -tiefe) & (t <= abstand), axis=1)
        maske[kand[treffer]] = True

    # ---------------------------------------------------------------- Rand

    @staticmethod
    def randpunkte(T, n):
        u"""Bool je Punkt (an einer offenen Kante) und die Nachbarschaft
        als duenn besetzte (n, n)-Matrix."""
        kanten = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
        kanten.sort(axis=1)
        schluessel = kanten[:, 0].astype(np.int64) * n + kanten[:, 1]
        einzig, zaehler = np.unique(schluessel, return_counts=True)
        offen = einzig[zaehler == 1]
        rand = np.zeros(n, dtype=bool)
        rand[offen // n] = True
        rand[offen % n] = True
        a, b = einzig // n, einzig % n
        nachbarn = coo_matrix((np.ones(2 * len(a), dtype=np.int8),
                               (np.concatenate([a, b]), np.concatenate([b, a]))),
                              shape=(n, n)).tocsr()
        return rand, nachbarn

    @staticmethod
    def lockere_randpunkte(P, rand, koerper, normalen, baum, eng):
        u"""Randpunkte, die mehr als `eng` ueber der Haut liegen (oder ohne
        Haut in 9 cm Umkreis)."""
        locker = np.zeros(len(P), dtype=bool)
        wo = np.where(rand)[0]
        if not len(wo):
            return locker
        d, i = baum.query(P[wo], distance_upper_bound=0.09, workers=-1)
        weit = ~np.isfinite(d)
        i = np.where(weit, 0, i)
        tief = np.einsum('ij,ij->i', P[wo] - koerper[i], normalen[i])
        locker[wo] = weit | (np.abs(tief) > eng)
        return locker

    @staticmethod
    def ringe_um(start, nachbarn, ringe):
        menge = start.astype(np.float64)
        for _ in range(int(ringe)):
            menge = np.clip(menge + nachbarn @ menge, 0, 1)
        return menge > 0

    @staticmethod
    def dreiecke_im_umkreis(T, n, ok, nachbarn):
        u"""(n, K)-Feld: je Stoffpunkt die zulaessigen Dreiecke bis zwei
        Ringe weit, mit -1 aufgefuellt."""
        nT = len(T)
        okT = np.where(ok)[0]
        if not len(okT):
            return np.full((n, 1), -1, dtype=np.int64)
        zeilen = np.concatenate([T[okT, 0], T[okT, 1], T[okT, 2]])
        spalten = np.concatenate([okT, okT, okT])
        B = csr_matrix((np.ones(len(zeilen), dtype=np.int8), (zeilen, spalten)),
                       shape=(n, nT))
        R = identity(n, dtype=np.int8, format='csr') + nachbarn
        R = R + R @ nachbarn
        C = (R @ B).tocsr()
        C.sum_duplicates()
        laengen = np.diff(C.indptr)
        K = max(int(laengen.max()), 1)
        aus = np.full((n, K), -1, dtype=np.int64)
        for i in range(n):
            s, e = C.indptr[i], C.indptr[i + 1]
            aus[i, :e - s] = C.indices[s:e]
        return aus

    # --------------------------------------------------------------- Index

    @staticmethod
    def index_ohne(dreiecke, maske):
        u"""Dreiecke ohne die, deren drei Ecken verdeckt sind."""
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        weg = maske[T].all(axis=1)
        return T[~weg], int(weg.sum())

    @classmethod
    def einzug(cls, punkte, dreiecke, maske, betrag=None):
        u"""Die verdeckten Punkte um `betrag` entlang ihrer Normale nach
        innen — fuer das Rendern der Randdreiecke."""
        betrag = cls.EINZUG_M if betrag is None else betrag
        aus = np.array(punkte, dtype=np.float64)
        N = Geometrie.normalen(aus, dreiecke)
        aus[maske] -= betrag * N[maske]
        return aus
