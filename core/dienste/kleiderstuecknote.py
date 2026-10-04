# -*- coding: utf-8 -*-
"""Kleiderstuecknote — wie gut ein aus dem Foto-Netz gebautes Kleidungsstück (Fotostück) ist: eine Messgröße in Metern, ohne Render (04.10.2026).

Edgar: „Ein Schritt, der Modell und Kleider ‚besser als Assets' macht: dafür fehlt mir eine Messgröße. Überleg dir was." Die Iterationen messen das Modell als Ganzes gegen das Netz
(`Iterationsnetznote`: mittlerer Abstand und EINE Deckung über alle Netzproben, ohne Stück). Ein Asset wird je Stück beurteilt, und zwei Fragen sind verschieden:

    deckung    Anteil der Bezugsfläche (die Netzflächen, die die Maske diesem Stück zuordnet), die näher als `NAH_M` an einem Punkt des Stücks liegt — fehlt Stoff?
    treue      Anteil der Stückfläche, die näher als `NAH_M` an der Bezugsfläche liegt — hat das Stück Stoff, den das Foto nicht zeigt (Hülle, die über die Maske hinausläuft)?
    f          Harmonisches Mittel beider (der F-Wert der 3D-Rekonstruktion, Schwelle `NAH_M` = die der Iterationen) — beide müssen stimmen, eine Seite allein ist leicht zu erreichen
    abweichung `1 − f`, kleiner ist besser wie die Fotonote und die Netznote
    abstand_mm mittlerer Abstand Stück → Bezug

Dazu der AUFBAU des Netzes (Zahlen, keine Note): Flächen, Fläche in cm², `inseln` (zusammenhängende Teile), `randschleifen` (offene Ränder: Ausschnitt, Saum, Ärmel — ein Riss ist eine
zusätzliche), `entartet` (Anteil der Flächen ohne Fläche).

Gemessen wird in der RUHELAGE der Figur (Y oben, Füße 0): das Stück liegt dort, das Foto-Netz kommt über `Kleiderstueckbezug` dorthin zurück. Die Proben sind fest gesät (`SAAT`), damit zwei
Läufe vergleichbar sind. Diese Klasse kennt keinen Auftrag und keine Datei — sie rechnet auf Punkten und Flächen; das Laden steht in `Kleiderstueckbezug`.
"""

import numpy as np

__all__ = ['Kleiderstuecknote']


class Kleiderstuecknote:
    #: Dieselbe Schwelle wie `Iterationsnetznote.NAH_M` (15 mm) — eine Deckung der Stücke ist mit der der Iterationen vergleichbar.
    NAH_M = 0.015
    PROBEN = 20000
    SAAT = 20261004
    #: Flächen unter diesem Inhalt (m²) zählen als entartet.
    ENTARTET_M2 = 1e-9

    @classmethod
    def proben(cls, punkte, flaechen, anzahl=None):
        """(N, 3) Proben auf der Oberfläche, nach Fläche verteilt und fest gesät."""
        import trimesh
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64), faces=np.asarray(flaechen, dtype=np.int64), process=False)
        p, _ = trimesh.sample.sample_surface(netz, int(anzahl or cls.PROBEN), seed=cls.SAAT)
        return np.asarray(p, dtype=np.float64)

    @classmethod
    def vergleichen(cls, bezug, stueck):
        """`bezug`, `stueck`: je `(punkte, flaechen)` → {deckung, treue, f, abweichung, abstand_mm}. Leer (keine Fläche) auf einer Seite: deckung/treue 0."""
        from scipy.spatial import cKDTree
        if bezug is None or stueck is None or not len(bezug[1]) or not len(stueck[1]):
            return {'deckung': 0.0, 'treue': 0.0, 'f': 0.0, 'abweichung': 1.0, 'abstand_mm': None}
        b, s = cls.proben(*bezug), cls.proben(*stueck)
        a_bs, _ = cKDTree(s).query(b)            # Bezug → Stück
        a_sb, _ = cKDTree(b).query(s)            # Stück → Bezug
        deckung = float(np.mean(a_bs < cls.NAH_M))
        treue = float(np.mean(a_sb < cls.NAH_M))
        f = 2.0 * deckung * treue / (deckung + treue) if deckung + treue > 0 else 0.0
        return {'deckung': round(deckung, 4), 'treue': round(treue, 4), 'f': round(f, 4), 'abweichung': round(1.0 - f, 4),
                'abstand_mm': round(float(np.mean(a_sb)) * 1000.0, 2)}

    @classmethod
    def haut_abstand(cls, haut, koerper):
        """Wie dicht liegt der Körper der Figur an der nackten Haut des Foto-Netzes? `haut`, `koerper`: je `(punkte, flaechen)` → {haut_mm, haut_p95_mm, deckung}.
        Mittel und 95. Perzentil des Abstands Haut → Körper (Millimeter); `deckung`: Anteil der Hautproben unter `NAH_M`."""
        from scipy.spatial import cKDTree
        if haut is None or koerper is None or not len(haut[1]):
            return {'haut_mm': None, 'haut_p95_mm': None, 'deckung': 0.0}
        h = cls.proben(*haut)
        k = cls.proben(*koerper, anzahl=4 * cls.PROBEN)
        abstand, _ = cKDTree(k).query(h)
        return {'haut_mm': round(float(np.mean(abstand)) * 1000.0, 2), 'haut_p95_mm': round(float(np.percentile(abstand, 95)) * 1000.0, 2),
                'deckung': round(float(np.mean(abstand < cls.NAH_M)), 4)}

    @classmethod
    def aufbau(cls, punkte, flaechen):
        """Zahlen zum Netz des Stücks: Flächen, cm², Inseln, Randschleifen, entartete Flächen."""
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        p = np.asarray(punkte, dtype=np.float64)
        f = np.asarray(flaechen, dtype=np.int64).reshape(-1, 3)
        if not len(f):
            return {'flaechen': 0, 'cm2': 0.0, 'inseln': 0, 'randschleifen': 0, 'entartet': 0.0}
        e = p[f]
        inhalt = 0.5 * np.linalg.norm(np.cross(e[:, 1] - e[:, 0], e[:, 2] - e[:, 0]), axis=1)
        n = int(f.max()) + 1
        # Inseln: Flächen über gemeinsame Punkte verbunden.
        zeilen = np.repeat(np.arange(len(f)), 3)
        inzidenz = coo_matrix((np.ones(len(zeilen)), (zeilen, f.reshape(-1))), shape=(len(f), n)).tocsr()
        inseln = int(connected_components((inzidenz @ inzidenz.T).tocoo(), directed=False)[0])
        # Randschleifen: Kanten, die nur EINE Fläche haben, bilden Schleifen; gezählt werden die Zusammenhangsteile dieser Kanten.
        kanten = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)      # (3F, 2), je Kante kleiner Index zuerst
        einmalig, anzahl = np.unique(kanten, axis=0, return_counts=True)
        rand = einmalig[anzahl == 1]
        schleifen = 0
        if len(rand):
            g = coo_matrix((np.ones(len(rand)), (rand[:, 0], rand[:, 1])), shape=(n, n))
            _, teil = connected_components(g, directed=False)
            schleifen = int(len(np.unique(teil[np.unique(rand)])))
        return {'flaechen': int(len(f)), 'cm2': round(float(inhalt.sum()) * 1e4, 1), 'inseln': inseln, 'randschleifen': schleifen,
                'entartet': round(float(np.mean(inhalt < cls.ENTARTET_M2)), 4)}
