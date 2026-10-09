# -*- coding: utf-8 -*-
"""Blendimportschamgewichte — die Hautgewichte des Scham-Stücks (09.10.2026).

BEFUND (Edgar: „gespreizte Beine: das Stück ist starr", Chrome, „cute girl", Oberschenkel um 25° gespreizt, `__pose`): Das Stück
bewegte sich im Median 0 mm (p90 3,2 mm), es hing zu 98,1 % am Becken (`pelvis`); die Haut seitlich daneben ging mit den Beinen — die Lücke
öffnete sich zu dunklen Löchern in den Leisten (Bild). Die Gewichte, die das Stück schreibt, kamen im Browser nie an: `G9garderobe.teile`
fragt jedes Kleidungsstück mit `koerperhaut=True`, und `G9folger` ersetzt dann die Gewichte der Datei durch die der drei im Raum nächsten
Punkte der GRUNDFIGUR (`G9stueckersatz`, Zeichen `eigene_gewichte`). Das Stück liegt aber im Median 18 mm HINTER der Figurfläche
(Furche); die Grundfigur ist auch nicht die Figur dieses Imports.

HIER: Jeder Stückpunkt bekommt die Gewichte der Hautpunkte, die ihn VERDECKEN — die, in deren Richtung nach innen (gegen die
Hautnormale) er liegt. Gemessen wird der Querabstand des Stückpunkts zur Geraden durch den Hautpunkt entlang seiner Normale; ein
Hautpunkt zählt nur, wenn der Stückpunkt höchstens `DAVOR_M` davor und höchstens `DAHINTER_M` hinter ihm liegt (die Innenseite des
Oberschenkels, die zur Lücke zeigt, fällt so weg). Die besten `NACHBARN` werden nach Kehrwert der Kosten gemischt und auf die
stärksten `KNOCHEN_JE_PUNKT` Knochen gekürzt. Über das Netz des Stücks glätten (`GLAETTEN`) ist möglich, aber aus: gemessen im Chrome
(25° gespreizt, Pixel der Lücken seitlich des Stücks, `__loecher`) verdünnt jedes Glätten die Gewichte am Rand und öffnet die Lücke wieder —
ohne Glätten 111.704 / 110.725 Pixel, mit zwei Durchgängen 123.315 / 121.930, mit den Gewichten der Grundfigur (alt) 169.009 / 158.297.

Haut und Gewichte sind die der FIGUR, die der Browser zeigt (Stufe 1, Regler wie `Blendimportlage.genesis`): beim Bau mit dem Eigenmorph
`_scham` = 1 (alter Stand von „cute girl") und 0 im Browser lagen es 176.694 / 159.297 Pixel — der Verdecker saß 20 mm neben der angezeigten
Haut. Bei `scham = objekt` entfällt die Nachformung (`Blendimportlauf._nachformung`), die Figur ist dann dieselbe. Ohne Django und ohne
Genesis9 prüfbar (`test_blendimport_schamgewichte.py`).
"""

import numpy as np

__all__ = ['Blendimportschamgewichte']


class Blendimportschamgewichte:
    #: Hautpunkte, die als Verdecker in Frage kommen: die nächsten im Raum, höchstens so weit (m).
    SUCHE_M = 0.07
    KANDIDATEN = 400
    #: So weit (m) darf der Stückpunkt VOR der Haut liegen (entlang ihrer Normale) und so weit HINTER ihr.
    DAVOR_M = 0.008
    DAHINTER_M = 0.06
    #: Kosten eines Verdeckers: Querabstand (m) + dieser Faktor · Tiefe (m).
    TIEFE_FAKTOR = 0.25
    NACHBARN = 3
    KNOCHEN_JE_PUNKT = 4
    #: Durchgänge, in denen jeder Stückpunkt zu `GLAETTEN_ANTEIL` ins Mittel seiner Netznachbarn rückt.
    GLAETTEN = 0
    GLAETTEN_ANTEIL = 0.5
    #: Ein Punkt, der näher als das (m) an einer Kante des Hautrings liegt, gilt als Randpunkt (`an_ring`); die Gewichte der Haut laufen
    #: über `RING_BAND_M` (m, Weg über das Netz) in die des Stücks aus.
    RING_TOL_M = 1e-6
    RING_BAND_M = 0.006

    def __init__(self, punkte, dreiecke, index, gewicht, knochen):
        """`punkte`/`dreiecke`: die Haut der Figur (Ruhelage); `index`/`gewicht` `(N, 4)`: ihre Gewichte (`netzstufe(1).haut`);
        `knochen`: die Namen, auf die `index` zeigt."""
        self.punkte = np.asarray(punkte, dtype=np.float64)
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        self.index = np.asarray(index, dtype=np.int64)
        self.gewicht = np.asarray(gewicht, dtype=np.float64)
        self.knochen = list(knochen)
        self.normalen = self.punktnormalen(self.punkte, self.dreiecke)
        self.bericht = {}

    # ----------------------------------------------------------- Bausteine

    @staticmethod
    def punktnormalen(punkte, dreiecke):
        """Flächengewichtete Punktnormalen (auf Länge 1)."""
        a, b, c = (punkte[dreiecke[:, i]] for i in range(3))
        flaeche = np.cross(b - a, c - a)
        summe = np.zeros_like(punkte)
        for i in range(3):
            np.add.at(summe, dreiecke[:, i], flaeche)
        laenge = np.linalg.norm(summe, axis=1, keepdims=True)
        return summe / np.maximum(laenge, 1e-12)

    def verdecker(self, p):
        """`(nachbar (m, NACHBARN), kosten (m, NACHBARN))`: je Stückpunkt die Hautpunkte, die ihn verdecken. Wo keiner in Frage
        kommt, sind es die im Raum nächsten (Kosten = Abstand) — `bericht['ohne_verdecker']` zählt sie."""
        from scipy.spatial import cKDTree

        baum = cKDTree(self.punkte)
        k = min(self.KANDIDATEN, len(self.punkte))
        abstand, kand = baum.query(p, k=k)
        c, n = self.punkte[kand], self.normalen[kand]
        v = p[:, None, :] - c
        tiefe = (v * n).sum(-1)                         # > 0: vor der Haut, < 0: dahinter
        quer = np.linalg.norm(v - tiefe[..., None] * n, axis=-1)
        kosten = quer + self.TIEFE_FAKTOR * np.abs(tiefe)
        gilt = (abstand <= self.SUCHE_M) & (tiefe <= self.DAVOR_M) & (tiefe >= -self.DAHINTER_M)
        kosten = np.where(gilt, kosten, np.inf)
        ohne = ~gilt.any(axis=1)
        kosten[ohne] = abstand[ohne]
        wahl = np.argsort(kosten, axis=1)[:, :self.NACHBARN]
        self.bericht['ohne_verdecker'] = int(ohne.sum())
        return np.take_along_axis(kand, wahl, axis=1), np.take_along_axis(kosten, wahl, axis=1)

    def dicht(self, nachbar, kosten):
        """Dichte Gewichte `(m, Knochen)` aus den gewählten Hautpunkten (Mischung nach Kehrwert der Kosten)."""
        anteil = 1.0 / np.maximum(kosten, 1e-3)
        anteil /= anteil.sum(axis=1, keepdims=True)
        dicht = np.zeros((len(nachbar), len(self.knochen)))
        zeilen = np.arange(len(nachbar))
        for k in range(nachbar.shape[1]):
            for j in range(self.index.shape[1]):
                np.add.at(dicht, (zeilen, self.index[nachbar[:, k], j]), anteil[:, k] * self.gewicht[nachbar[:, k], j])
        return dicht

    def glaetten(self, dicht, dreiecke):
        """Jeder Punkt rückt zu `GLAETTEN_ANTEIL` ins Mittel seiner Netznachbarn (Gewichte der Haut sind glatt, die Wahl der
        besten Hautpunkte springt dagegen)."""
        n = len(dicht)
        a = np.concatenate([dreiecke[:, 0], dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 0]])
        b = np.concatenate([dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 0], dreiecke[:, 0], dreiecke[:, 1], dreiecke[:, 2]])
        for _ in range(self.GLAETTEN):
            summe, zahl = np.zeros_like(dicht), np.zeros(n)
            np.add.at(summe, a, dicht[b])
            np.add.at(zahl, a, 1.0)
            mittel = np.where(zahl[:, None] > 0, summe / np.maximum(zahl[:, None], 1.0), dicht)
            dicht = (1.0 - self.GLAETTEN_ANTEIL) * dicht + self.GLAETTEN_ANTEIL * mittel
        return dicht

    def kuerzen(self, dicht):
        """Nur die stärksten `KNOCHEN_JE_PUNKT` Knochen je Punkt bleiben; die Zeilen summieren wieder zu 1."""
        if dicht.shape[1] > self.KNOCHEN_JE_PUNKT:
            schwach = np.argsort(dicht, axis=1)[:, :-self.KNOCHEN_JE_PUNKT]
            np.put_along_axis(dicht, schwach, 0.0, axis=1)
        return dicht / np.maximum(dicht.sum(axis=1, keepdims=True), 1e-12)

    def haut_dicht(self, punkte):
        """Dichte Gewichte `(len(punkte), Knochen)` der Hautpunkte `punkte` (Nummern der Figur)."""
        punkte = np.asarray(punkte, dtype=np.int64)
        dicht = np.zeros((len(punkte), len(self.knochen)))
        zeilen = np.arange(len(punkte))
        for j in range(self.index.shape[1]):
            np.add.at(dicht, (zeilen, self.index[punkte, j]), self.gewicht[punkte, j])
        return dicht

    def an_ring(self, dicht, p, dreiecke, lage, ring_punkte):
        """Der Rand des Stücks trägt die Gewichte der Haut, auf deren Kanten er liegt (`Blendimportschamnaht`): ein Punkt auf einer Kante
        des Rings zwischen den Hautpunkten A und B bekommt `(1 − t)·A + t·B`, ein Punkt auf einer Ecke deren Gewichte — der Rand folgt
        jeder Haltung wie die Haut und der Spalt bleibt zu (Daz: Randpunkte des Geografts SIND Punkte des Körpers). Ins Innere läuft
        das über `RING_BAND_M` (Weg über das Netz) in die Gewichte des Stücks aus. `lage` (k, 3), `ring_punkte` (k,)."""
        from scipy import sparse
        from scipy.sparse import csgraph

        lage = np.asarray(lage, dtype=np.float64)
        seg = np.roll(lage, -1, axis=0) - lage
        v = p[:, None, :] - lage[None]
        t = np.clip((v * seg[None]).sum(-1) / np.maximum((seg ** 2).sum(-1), 1e-18)[None], 0.0, 1.0)
        abstand = np.linalg.norm(p[:, None, :] - (lage[None] + t[..., None] * seg[None]), axis=-1)
        j = abstand.argmin(axis=1)
        zeile = np.arange(len(p))
        t, nah = t[zeile, j], abstand[zeile, j]
        haut = self.haut_dicht(ring_punkte)
        am_ring = np.flatnonzero(nah < self.RING_TOL_M)
        rand = (1.0 - t[am_ring])[:, None] * haut[j[am_ring]] + t[am_ring][:, None] * haut[(j[am_ring] + 1) % len(lage)]
        # Weg über das Netz, Punkte gleicher Lage (UV-Nähte des Stücks) gelten als einer
        _, rep = np.unique(np.round(p / 1e-7).astype(np.int64), axis=0, return_inverse=True)
        rep = rep.ravel()
        pa = np.concatenate([dreiecke[:, 0], dreiecke[:, 1], dreiecke[:, 2]])
        pb = np.concatenate([dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 0]])
        n = int(rep.max()) + 1
        lange = np.maximum(np.linalg.norm(p[pa] - p[pb], axis=1), 1e-9)
        weg, _, quelle = csgraph.dijkstra(sparse.csr_matrix((lange, (rep[pa], rep[pb])), shape=(n, n)), directed=False,
                                          indices=np.unique(rep[am_ring]), min_only=True, return_predecessors=True)
        rand_je_lage = np.zeros((n, dicht.shape[1]))
        rand_je_lage[rep[am_ring]] = rand
        s = np.clip(weg[rep] / self.RING_BAND_M, 0.0, 1.0)
        s = s * s * (3.0 - 2.0 * s)
        erreicht = np.isfinite(weg[rep])
        neu = dicht.copy()
        neu[erreicht] = ((1.0 - s[erreicht, None]) * rand_je_lage[quelle[rep[erreicht]]] + s[erreicht, None] * dicht[erreicht])
        self.bericht['ring'] = {'punkte': int(len(am_ring)), 'band': int((erreicht & (s < 1.0)).sum())}
        return neu

    # ----------------------------------------------------------------- Lauf

    def gewichte(self, p, dreiecke, ring=None):
        """`{knochen: [[punkt, gewicht], …]}` für die Stückpunkte `p` mit dem Netz `dreiecke` (Format von
        `G9mbstuecke.gewichte`, wie es `G9dsonschreiber` liest). `ring`: `(lage, ring_punkte)` des Hautlochs — der Rand des Stücks
        trägt dann die Gewichte der Haut auf diesem Ring (`an_ring`)."""
        p = np.asarray(p, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        nachbar, kosten = self.verdecker(p)
        dicht = self.kuerzen(self.glaetten(self.dicht(nachbar, kosten), dreiecke))
        if ring is not None:
            dicht = self.kuerzen(self.an_ring(dicht, p, dreiecke, *ring))
        self.bericht['punkte'] = int(len(p))
        aus = {}
        for spalte, name in enumerate(self.knochen):
            wo = np.nonzero(dicht[:, spalte] > 1e-4)[0]
            if len(wo):
                aus[name] = [[int(i), round(float(dicht[i, spalte]), 5)] for i in wo]
        return aus

    @classmethod
    def fuer_figur(cls, figur):
        """Aus der Figur des Imports (`Blendimportlage.genesis()`): die Haut der Stufe 1 mit den Gewichten derselben Stufe."""
        from Genesis9.basisnetz import G9basisnetz

        haut = G9basisnetz.holen().netzstufe(1).haut
        return cls(figur['punkte'], figur['dreiecke'], haut['index'], haut['gewicht'], haut['knochen'])
