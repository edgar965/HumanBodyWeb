# -*- coding: utf-8 -*-
"""Saumband — verdeckte Haut neben der gezeichneten bleibt gezeichnet,
versenkt. Dieselbe Regel wie `static/viewer/gemeinsam/saumband.js`.

BEFUND (Edgar, 13.09.2026, Bild vom Aermel des anliegenden T-Shirts in
einer Tanzpose: „Offenbar wird kein Skin erzeugt unter dem T-Shirt, dann
kommt der Aermel von der anderen Koerperseite durch"): Die Maske entfernt
die Haut unter dem Stoff; in der Pose liegt der Aermel an der Unterseite
des Oberarms nicht mehr vor der Haut, und durch das Loch sieht man die
Innenseite der oberen Aermelwand. Ein Band von 40 mm hinter der
gezeichneten Haut reichte nicht — das Loch begann 5–8 cm vom Saum.

DER WEG: Verdeckte Haut bis `BAND_M` (auf der Haut entlang, Dijkstra ueber
die Netzkanten, Naehte verbunden) neben der gezeichneten Haut wird weiter
gerendert, versenkt um `UNTERKANTE_M + STEIGUNG · Weg`, hoechstens
`TIEFE_M`; erst dahinter fallen Dreiecke aus dem Index. Der Weg wird in
Ruhelage gerechnet, die Versenkung laeuft je Bild entlang der gestellten
Normale.
"""

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from maskengeometrie import Geometrie
from saumschnitt import Saumschnitt


class Saumband:
    """Weg zur gezeichneten Haut, Versenkung und Index-Maske."""

    #: So weit (auf der Haut) neben der gezeichneten Haut bleibt verdeckte
    #: Haut gerendert. 15 cm: Der Aermelsaum liegt 12 cm von der Achsel.
    BAND_M = 0.15
    #: Versenkung je Meter Weg (1 mm je mm).
    STEIGUNG = 1.0
    #: Tiefste Versenkung — der Einzug der Randecken.
    TIEFE_M = 0.010

    @classmethod
    def abstaende(cls, punkte, maske, dreiecke):
        """Je Punkt der Weg auf der Haut zum naechsten gezeichneten Punkt:
        0 fuer gezeichnete, `inf` jenseits von `BAND_M`."""
        P = np.asarray(punkte, dtype=np.float64)
        m = np.asarray(maske, dtype=bool)
        aus = np.zeros(len(P))
        if not m.any():
            return aus
        if m.all():
            aus[:] = np.inf
            return aus
        graph = cls._kanten(P, dreiecke)
        quellen = np.flatnonzero(~m)
        weg = dijkstra(graph, directed=False, indices=quellen, min_only=True, limit=cls.BAND_M)
        aus[:] = np.where(weg <= cls.BAND_M, weg, np.inf)
        aus[~m] = 0.0
        return aus

    @staticmethod
    def _kanten(P, dreiecke):
        """Das Netz als Kantengraph (Laenge als Gewicht); deckungsgleiche
        Punkte (Naht) haengen mit einer Kante der Laenge 0 zusammen — als
        `eps`, weil scipy 0 als „keine Kante" liest."""
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        a = np.concatenate([T[:, 0], T[:, 1], T[:, 2]])
        b = np.concatenate([T[:, 1], T[:, 2], T[:, 0]])
        laenge = np.linalg.norm(P[a] - P[b], axis=1)
        gruppe = Geometrie.naht(P)
        erste = np.full(int(gruppe.max()) + 1, -1)
        for i, g in enumerate(gruppe):
            if erste[g] < 0:
                erste[g] = i
        zwilling = np.flatnonzero(erste[gruppe] != np.arange(len(P)))
        a = np.concatenate([a, zwilling])
        b = np.concatenate([b, erste[gruppe[zwilling]]])
        laenge = np.concatenate([laenge, np.full(len(zwilling), 1e-9)])
        laenge = np.maximum(laenge, 1e-9)
        n = len(P)
        return coo_matrix((laenge, (a, b)), shape=(n, n)).tocsr()

    @classmethod
    def weg(cls, maske, abstaende):
        """Je Punkt True, wenn verdeckt UND jenseits des Bands — nur
        Dreiecke mit drei solchen Ecken fallen aus dem Index."""
        m = np.asarray(maske, dtype=bool)
        return m & ~(np.asarray(abstaende) <= cls.BAND_M)

    @classmethod
    def tiefe(cls, abstaende):
        """Die Versenkung (Meter) je Punkt aus dem Weg."""
        return np.minimum(cls.TIEFE_M, Saumschnitt.UNTERKANTE_M + cls.STEIGUNG * np.asarray(abstaende))
