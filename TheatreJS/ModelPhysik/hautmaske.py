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
* Stoff unter Stoff (`Lagenmaske`): Wer aussen liegt, wird gezaehlt; die
  Normalen kommen von der Haut, nie vom Stoffnetz.
"""
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, identity
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


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
            np.add.at(N, T[:, k], fn)
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
        abstand = cls.ABSTAND_M if abstand is None else abstand
        tiefe = cls.TIEFE_M if tiefe is None else tiefe
        ringe = cls.RANDRINGE if randringe is None else randringe
        eng = cls.ENG_M if eng is None else eng
        suchweite = max(abstand, tiefe) if suchweite is None else suchweite
        inseln = cls.INSEL_MAX if inseln is None else inseln
        koerper = np.asarray(koerper, dtype=np.float64)
        if normalen is None:
            normalen = Geometrie.normalen(koerper, dreiecke)
        normalen = np.asarray(normalen, dtype=np.float64)
        baum = cKDTree(koerper)
        maske = np.zeros(len(koerper), dtype=bool)
        for punkte, tris in stoffe:
            if punkte is None or tris is None or not len(punkte) or not len(tris):
                continue
            cls._ein_stueck(koerper, normalen, baum, maske,
                            np.asarray(punkte, dtype=np.float64),
                            np.asarray(tris, dtype=np.int64).reshape(-1, 3),
                            abstand, tiefe, ringe, eng, suchweite)
        if inseln > 0 and dreiecke is not None:
            Maskeninseln.schliessen(maske, dreiecke, inseln)
        return maske

    @classmethod
    def _ein_stueck(cls, koerper, normalen, baum, maske, P, T,
                    abstand, tiefe, ringe, eng, suchweite):
        rand, nachbarn = cls.randpunkte(T, len(P))
        locker = cls.lockere_randpunkte(P, rand, koerper, normalen, baum, eng)
        gesperrt = cls.ringe_um(locker, nachbarn, ringe)
        ok = ~gesperrt[T].any(axis=1)
        umkreis = cls.dreiecke_im_umkreis(T, len(P), ok, nachbarn)
        d, j = cKDTree(P).query(koerper, distance_upper_bound=suchweite)
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
        d, i = baum.query(P[wo], distance_upper_bound=0.09)
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
        b_ueber_a = int(Hautmaske.verdeckt(A[1], None, [(B[1], B[2])], normalen=nA, **o).sum())
        a_ueber_b = int(Hautmaske.verdeckt(B[1], None, [(A[1], A[2])], normalen=nB, **o).sum())
        if not b_ueber_a and not a_ueber_b:
            return 0
        return 1 if b_ueber_a >= a_ueber_b else -1

    @staticmethod
    def normalen_von_haut(P, N, baum):
        d, i = baum.query(P, distance_upper_bound=0.09)
        aus = np.zeros_like(P)
        nah = np.isfinite(d)
        aus[nah] = N[i[nah]]
        return aus
