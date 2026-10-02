# -*- coding: utf-8 -*-
"""Huellenschnitt — wo ein Fotostück der Hülle (`Fotohuelle`) endet: Säume als glatte, ebene Linien (01.10.2026 nachts).

Befund Edgar (Bild der Seite, Testauftrag 2026.10.01.12.38.09): Ausschnitt, Ärmel- und Hosensaum gezackt, Loch an der
Hüfte. Die Zugehörigkeit kommt je Figurfläche aus dem Netz — eine Treppe aus Flächen (Kanten ~1,8 cm). Geglättet und an
der Linie 0,5 geschnitten blieb sie gezackt: Ein Feld je Figurpunkt ist auf jeder Fläche linear und knickt an jeder
Kante (gemessen: Hosensaum 0,665–0,699 m, Zickzack |Δy|/Umfang 0,29). Ein Saum ist eine EBENE Linie. Deshalb:

1. `feld`: Anteil gewählter Flächen je Punkt, `RUNDEN` Runden über die Figur geglättet — füllt kleine Löcher, glättet
   den groben Verlauf
2. `eben`: je Randlinie (Kreuzungen der Linie 0,5 auf den Figurkanten, über gemeinsame Flächen verbunden) die Ebene
   durch ihre Punkte (kleinste Hauptachse); im Umkreis `NAH` der Linie wird das Feld zum Abstand von dieser Ebene —
   linear im Raum, also ohne Knick auf irgendeiner Fläche; Linien, die keine Ebene sind (RMS > `EBEN_RMS`), bleiben
3. `schneiden`: Flächen an der Linie durchtrennt (Kantenpunkte geteilt, Umlaufsinn bleibt)

    Huellenschnitt(ruhe, dreiecke).feld(wahl) → (V,)        .schneiden(lagen, flaechen, spalte) → (lagen, flaechen)
"""

import numpy as np

__all__ = ['Huellenschnitt']


class Huellenschnitt:
    RUNDEN = 40
    SCHNITT = 0.5
    #: Umkreis um eine Randlinie, in dem ihre Ebene gilt (m), und Feldgefälle dort (Feld 0,5 ± Abstand / `STEIL`).
    NAH = 0.06
    STEIL = 0.16
    #: Eine Linie mit mehr mittlerem Abstand von ihrer Ebene ist kein Saum (m) — sie bleibt, wie das Feld sie zieht.
    EBEN_RMS = 0.02
    PUNKTE_MIN = 8

    def __init__(self, ruhe, dreiecke, halsgewicht=None):
        self.ruhe = np.asarray(ruhe, dtype=np.float64)
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64)
        #: (V,) Hautgewicht der Halsknochen und ihrer Kinder je Figurpunkt (`_rundhals`); None = kein Rundhals.
        self.halsgewicht = None if halsgewicht is None else np.asarray(halsgewicht, dtype=np.float64)

    @staticmethod
    def halsgewichte(datei, wurzel='neck1'):
        """(V,) aus einer Figurdatei (`genesis_ende.npz`: knochen, eltern, haut_index, haut_gewicht); None ohne
        Knochen."""
        if not {'knochen', 'eltern', 'haut_index', 'haut_gewicht'} <= set(datei.files):
            return None
        knochen, eltern = [str(k) for k in datei['knochen']], np.asarray(datei['eltern'])
        if wurzel not in knochen:
            return None
        drin = np.zeros(len(knochen), bool)
        drin[knochen.index(wurzel)] = True
        for _ in range(len(knochen)):                       # Kinder erben (Eltern stehen nicht immer vorn)
            neu = drin | ((eltern >= 0) & drin[np.maximum(eltern, 0)])
            if (neu == drin).all():
                break
            drin = neu
        index, gewicht = np.asarray(datei['haut_index']), np.asarray(datei['haut_gewicht'], dtype=np.float64)
        return (gewicht * drin[np.clip(index, 0, len(knochen) - 1)] * (index >= 0)).sum(axis=1)

    def _mittel(self, werte, runden):
        from scipy.sparse import coo_matrix
        zeilen = np.repeat(np.arange(len(self.dreiecke)), 3)
        inzidenz = coo_matrix((np.ones(len(zeilen)), (zeilen, self.dreiecke.reshape(-1))),
                              shape=(len(self.dreiecke), len(self.ruhe))).tocsr()
        nachbar = (inzidenz.T @ inzidenz).tocsr()
        anzahl = np.maximum(np.asarray(nachbar.sum(axis=1)).ravel(), 1e-12)
        for _ in range(runden):
            werte = (nachbar @ werte) / anzahl
        return werte

    def feld(self, wahl, hals=False):
        anteil, zahl = np.zeros(len(self.ruhe)), np.zeros(len(self.ruhe))
        np.add.at(anteil, self.dreiecke, np.repeat(np.asarray(wahl, np.float64)[:, None], 3, axis=1))
        np.add.at(zahl, self.dreiecke, 1.0)
        return self.eben(self._mittel(anteil / np.maximum(zahl, 1.0), self.RUNDEN), hals)

    # ------------------------------------------------------------ Ebenen

    def _linien(self, f):
        """Kreuzungspunkte der Linie `SCHNITT` auf den Figurkanten, je Randlinie → [(N, 3) Punkte]."""
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        kanten = np.sort(np.concatenate([self.dreiecke[:, [0, 1]], self.dreiecke[:, [1, 2]],
                                         self.dreiecke[:, [2, 0]]]), axis=1)
        einzig, zurueck = np.unique(kanten, axis=0, return_inverse=True)
        zurueck = zurueck.reshape(3, -1).T                                  # (F, 3) Kantennummern je Fläche
        u, v = einzig[:, 0], einzig[:, 1]
        kreuzt = (f[u] - self.SCHNITT) * (f[v] - self.SCHNITT) < 0
        nummer = np.full(len(einzig), -1)
        nummer[kreuzt] = np.arange(kreuzt.sum())
        if not kreuzt.any():
            return []
        t = (self.SCHNITT - f[u[kreuzt]]) / (f[v[kreuzt]] - f[u[kreuzt]])
        punkte = self.ruhe[u[kreuzt]] + t[:, None] * (self.ruhe[v[kreuzt]] - self.ruhe[u[kreuzt]])
        je_flaeche = nummer[zurueck]                                         # (F, 3), −1 = kreuzt nicht
        paare = [je_flaeche[:, [i, j]] for i, j in ((0, 1), (1, 2), (0, 2))]
        paare = np.vstack([p[(p >= 0).all(axis=1)] for p in paare])
        n = len(punkte)
        graph = coo_matrix((np.ones(len(paare)), (paare[:, 0], paare[:, 1])), shape=(n, n))
        anzahl, teil = connected_components(graph, directed=False)
        return [punkte[teil == k] for k in range(anzahl) if (teil == k).sum() >= self.PUNKTE_MIN]

    #: Rundhals (Befund Edgar 01.10.2026 nachts: Shirt „kaputt", Ausschnitt weit über die Schultern). Das Netz kennt das
    #: Shirt rundum nur bis 1,40 m — waagrecht, auch über den Schultern (gemessen an fünf Abständen von der Mitte, alle
    #: 1,399–1,402 m); auf den Fotos sitzt der Kragen eng am Halsansatz. Die oberste Randlinie eines Oberteils folgt
    #: deshalb dem Halsansatz der Figur: dem Hautgewicht der Halsknochen (`neck1` und alles darunter, `halsgewicht`).
    #: Shirt ist oberhalb der Linie, was weniger als `HALS_SCHWELLE` am Hals hängt. (Ein Zylinder um eine geschätzte
    #: Halsachse lief hinten den Hals hinauf und legte ein Band unters Kinn.)
    HALS_SCHWELLE = 0.15
    HALS_UNTER = 0.03

    def _rundhals(self, f, punkte, aus, besetzt):
        if self.halsgewicht is None:
            return False
        oben = (self.ruhe[:, 1] >= punkte[:, 1].min() - self.HALS_UNTER) & (
            np.linalg.norm(self.ruhe[:, [0, 2]] - punkte[:, [0, 2]].mean(axis=0), axis=1) < self.SCHULTER)
        aus[oben] = self.SCHNITT + (self.HALS_SCHWELLE - self.halsgewicht[oben])
        besetzt[oben] = 0.0
        return True

    #: Halbe Schulterbreite um die Halslinie, in der der Rundhals gilt (m) — die Ärmel liegen weiter außen.
    SCHULTER = 0.17

    def eben(self, f, hals=False):
        """Das Feld nahe jeder ebenen Randlinie durch den Abstand von ihrer Ebene ersetzen; `hals`: die oberste Linie
        ist ein Rundhals (`_rundhals`)."""
        from scipy.spatial import cKDTree
        aus = f.copy()
        besetzt = np.full(len(f), np.inf)
        linien = sorted(self._linien(f), key=lambda p: -p[:, 1].mean())
        if hals and linien and self._rundhals(f, linien[0], aus, besetzt):
            linien = linien[1:]
        for punkte in linien:
            mitte = punkte.mean(axis=0)
            _w, achsen = np.linalg.eigh(np.cov((punkte - mitte).T))
            normale = achsen[:, 0]
            if np.sqrt(np.mean(((punkte - mitte) @ normale) ** 2)) > self.EBEN_RMS:
                continue
            abstand, _ = cKDTree(punkte).query(self.ruhe, distance_upper_bound=self.NAH)
            nah = np.isfinite(abstand) & (abstand < besetzt)
            if not nah.any():
                continue
            seite = (self.ruhe[nah] - mitte) @ normale
            if np.sum((f[nah] - self.SCHNITT) * seite) < 0:              # Normale zeigt ins Stück
                normale, seite = -normale, -seite
            aus[nah] = self.SCHNITT + seite / self.STEIL
            besetzt[nah] = abstand[nah]
        return aus

    # ---------------------------------------------------------- Schneiden

    def schneiden(self, lagen, flaechen, spalte):
        """Flächen an der Linie `lagen[:, spalte] == SCHNITT` schneiden → (lagen, flaechen) nur mit der Innenseite."""
        f = lagen[:, spalte]
        innen = f >= self.SCHNITT
        k = innen[flaechen].sum(axis=1)
        ganz = flaechen[k == 3]
        rand = flaechen[(k == 1) | (k == 2)]
        km = k[(k == 1) | (k == 2)]
        # die Ecke, die allein auf ihrer Seite liegt, nach vorn drehen (Umlaufsinn bleibt)
        einzeln = np.where(km == 1, np.argmax(innen[rand], axis=1), np.argmin(innen[rand], axis=1))
        reihe = (einzeln[:, None] + np.arange(3)[None, :]) % 3
        a, b, c = (np.take_along_axis(rand, reihe, axis=1)[:, i] for i in range(3))
        kanten = np.sort(np.concatenate([np.stack([a, b], 1), np.stack([a, c], 1)]), axis=1)
        einzig, zurueck = np.unique(kanten, axis=0, return_inverse=True)
        zurueck = zurueck.reshape(-1)
        u, v = einzig[:, 0], einzig[:, 1]
        t = np.clip((self.SCHNITT - f[u]) / np.where(f[v] != f[u], f[v] - f[u], 1e-12), 0.02, 0.98)
        neu = lagen[u] + t[:, None] * (lagen[v] - lagen[u])
        p_ab, p_ac = len(lagen) + zurueck[:len(a)], len(lagen) + zurueck[len(a):]
        eins = km == 1
        teile = [ganz, np.stack([a, p_ab, p_ac], 1)[eins],
                 np.stack([p_ab, b, c], 1)[~eins], np.stack([p_ab, c, p_ac], 1)[~eins]]
        alle = np.vstack([lagen, neu])
        genutzt, index = np.unique(np.vstack(teile).reshape(-1), return_inverse=True)
        return alle[genutzt], index.reshape(-1, 3)
