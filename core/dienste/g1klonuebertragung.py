# -*- coding: utf-8 -*-
u"""G1klonuebertragung — ein Genesis-1-Verschiebungsfeld über Daz' Klon auf den Genesis-9-Käfig legen (18.10.2026).

Edgar, 17./18.10.2026: Genesis 1 „Basic Child“ und „Kids 4“ als Regler bei „Alter“ (`G9g1morphe`). Genesis 9 bringt einen Klon von Genesis 1 mit (`CloneGenesis.dsf`: G9 in der Gestalt von
Genesis 1) und die Auto-Fit-Schablone (`Base/Tools/Clones/CloneGenesis.dsj`, `G9autofit`). Damit braucht es keine eigene Zuordnung der Netze wie bei MakeHuman:

1. STELLUNG: Genesis 1 steht in T-Stellung (Schultern 45°, Unterarm, Hand, Finger: 40 gedrehte Knochen). `stellen` dreht das Netz mit seiner EIGENEN Hautbindung über die Schablone in die
   A-Stellung von Genesis 9. Gemessen (`ProjektTemp/_wegwerf/hautebenen/g1_ausrichtung.py`): danach liegt es auf dem Klon — Rumpf/Beine/Kopf Median 0,36 cm, 95 % 1,19 cm; Arme Median 0,24 cm,
   höchstens 2,55 cm (ungedreht standen die Arme 38 cm daneben).
2. FORM: Eine Form (Kind) dreht genauso, aber mit IHREN Gelenken (`versatz`, cm; `ausrichtung`, Grad) — sonst drehte der Arm des Kindes um die Schulter der Erwachsenen.
   Wo Daz keine Gelenkformeln mitgibt (Kids 4), schätzt `gelenke_schaetzen` sie aus der Haut um das Gelenk.
3. ZUORDNUNG: Jeder Käfigpunkt in Klon-Gestalt bekommt den nächsten Punkt auf der gedrehten Haut von Genesis 1 (Dreieck, Schwerpunktkoordinaten) — nur Haut (`HAUT`), nicht Augen, Zähne,
   Mundraum, Wimpern, Tränen. Das Feld dort ist der gewichtete Mittelwert der drei Ecken; Käfigpunkte weiter als `WEIT_M` von der Haut bekommen ihr Feld aus den Nachbarn (`G9feldputz`).
"""
import numpy as np
from Genesis9.autofit import G9autofit
from Genesis9.dson import G9dson
from Genesis9.feldputz import G9feldputz
from Genesis9.haut import G9haut
from Genesis9.knochenmatrizen import G9knochenmatrizen
from Genesis9.pfade import G9pfade
from scipy.spatial import cKDTree

__all__ = ['G1klonuebertragung']


class G1klonuebertragung:
    u"""Genesis-1-Feld (T-Stellung) -> Käfigfeld von Genesis 9."""

    KLON = 'CloneGenesis'
    CM = 0.01
    #: Materialgruppen von Genesis 1, die Haut sind (`1_SkinFace`, `2_Nipple`, `1_Lip`, `1_Nostril`, `3_Fingernail` …) — nicht `5_Sclera`, `4_Teeth`, `4_InnerMouth`, `6_Eyelash`, `7_Tear`.
    HAUT = ('Skin', 'Nipple', 'Lip', 'Nostril', 'nail')
    #: Ein Käfigpunkt weiter als das (m) von der Haut von Genesis 1 hat kein Gegenstück.
    WEIT_M = 0.03
    #: Nächste Hautpunkte, deren Dreiecke je Käfigpunkt geprüft werden.
    KANDIDATEN = 4
    #: Hautpunkte um ein Gelenk, aus denen `gelenke_schaetzen` dessen Verschiebung mittelt.
    UM_GELENK = 40

    def __init__(self):
        self.doc = G9dson.lesen(G9pfade.figur_fremd(self.KLON))
        geo = self.doc.geometrie()
        #: (19296, 3) Meter: Genesis 1 in T-Stellung.
        self.grund = np.asarray(geo['vertices']['values'], dtype=np.float64) * self.CM
        self.dreiecke = self.dreiecke_der_haut(geo)
        self.hautpunkte = np.unique(self.dreiecke)
        self.haut = G9haut.aus_dokument(self.doc)
        self.autofit = G9autofit.holen(self.KLON)
        self.reihenfolgen = {k['id']: str(k.get('rotation_order') or 'XYZ') for k in self.doc.knochen()}
        self._zuordnung = None
        self._putz = None

    @classmethod
    def dreiecke_der_haut(cls, geo):
        u"""(T, 3) Punktnummern der Dreiecke aller Hautflächen (Vierecke in zwei Dreiecke geteilt)."""
        gruppen = geo['polygon_material_groups']['values']
        haut = {i for i, name in enumerate(gruppen) if any(t in name for t in cls.HAUT)}
        aus = []
        for p in geo['polylist']['values']:
            if p[1] not in haut:
                continue
            ecken = p[2:]
            for i in range(1, len(ecken) - 1):
                aus.append((ecken[0], ecken[i], ecken[i + 1]))
        return np.asarray(aus, dtype=np.int64)

    # ------------------------------------------------------------ Stellung

    def stellen(self, punkte, versatz=None, ausrichtung=None):
        u"""Punkte (N, 3) Meter in T-Stellung -> A-Stellung von Genesis 9. `versatz` `{knochen: {'center_point': (dx, dy, dz)}}` (cm) und `ausrichtung` `{knochen: (dx, dy, dz)}` (Grad):
        die Gelenke einer Form."""
        ausrichtung = ausrichtung or {}
        roh = []
        for k in self.autofit.roh:
            k = dict(k, reihenfolge=self.reihenfolgen.get(k['name'], 'XYZ'))
            if k['name'] in ausrichtung:
                k['orientation'] = np.asarray(k['orientation'], dtype=np.float64) + np.asarray(ausrichtung[k['name']], dtype=np.float64)
            roh.append(k)
        return G9knochenmatrizen({}, versatz or {}, roh=roh, drehung=self.autofit.drehung).anwenden(np.asarray(punkte, dtype=np.float64), self.haut)

    def gelenke_schaetzen(self, form):
        u"""`{knochen: {'center_point': (dx, dy, dz)}}` (cm) einer Form ohne Gelenkformeln: je Gelenk das Mittel der Form (T-Stellung, m) über die `UM_GELENK` nächsten Hautpunkte."""
        baum = cKDTree(self.grund[self.hautpunkte])
        aus = {}
        for k in self.autofit.roh:
            _d, i = baum.query(np.asarray(k['kopf'], dtype=np.float64) * self.CM, k=self.UM_GELENK)
            aus[k['name']] = {'center_point': tuple(float(x) for x in np.asarray(form)[self.hautpunkte[i]].mean(axis=0) / self.CM)}
        return aus

    # ----------------------------------------------------------- Zuordnung

    @staticmethod
    def schwerpunkt(p, a, b, c):
        u"""`(gewichte (N, 3), abstand (N,))`: der Punkt im Dreieck (a, b, c) nahe p — Projektion in die Ebene, außerhalb auf das Dreieck geklemmt und neu normiert."""
        ab, ac, ap = b - a, c - a, p - a
        d00, d01, d11 = (ab * ab).sum(1), (ab * ac).sum(1), (ac * ac).sum(1)
        d20, d21 = (ap * ab).sum(1), (ap * ac).sum(1)
        nenner = d00 * d11 - d01 * d01
        nenner = np.where(np.abs(nenner) < 1e-20, 1e-20, nenner)
        v = (d11 * d20 - d01 * d21) / nenner
        w = (d00 * d21 - d01 * d20) / nenner
        g = np.stack([1.0 - v - w, v, w], axis=1).clip(0.0, None)
        g /= np.maximum(g.sum(axis=1, keepdims=True), 1e-12)
        q = g[:, :1] * a + g[:, 1:2] * b + g[:, 2:] * c
        return g, np.linalg.norm(p - q, axis=1)

    def zuordnen(self):
        u"""`(dreieck (M,), gewichte (M, 3), abstand (M,))` je Käfigpunkt in Klon-Gestalt auf der gedrehten Haut von Genesis 1 — einmal."""
        if self._zuordnung is not None:
            return self._zuordnung
        haut = self.stellen(self.grund)
        tri = self.dreiecke
        klon = np.asarray(self.autofit.punkte, dtype=np.float64)
        ecken = tri.ravel()
        folge = np.argsort(ecken, kind='stable')
        sortiert = ecken[folge]
        alle = np.arange(len(self.grund))
        start, ende = np.searchsorted(sortiert, alle), np.searchsorted(sortiert, alle, side='right')
        _d, naechste = cKDTree(haut[self.hautpunkte]).query(klon, k=self.KANDIDATEN)
        naechste = self.hautpunkte[naechste]
        dreieck = np.zeros(len(klon), dtype=np.int64)
        gewichte = np.zeros((len(klon), 3))
        abstand = np.full(len(klon), np.inf)
        for j in range(self.KANDIDATEN):
            v = naechste[:, j]
            for r in range(int((ende - start).max())):
                idx = np.nonzero(ende[v] - start[v] > r)[0]
                if not len(idx):
                    break
                t = folge[start[v[idx]] + r] // 3
                g, d = self.schwerpunkt(klon[idx], haut[tri[t, 0]], haut[tri[t, 1]], haut[tri[t, 2]])
                besser = d < abstand[idx]
                i = idx[besser]
                dreieck[i], gewichte[i], abstand[i] = t[besser], g[besser], d[besser]
        self._zuordnung = (dreieck, gewichte, abstand)
        return self._zuordnung

    def uebertragen(self, feld):
        u"""(25182, 3) Käfigfeld aus einem Feld (N, 3) auf den Punkten von Genesis 1 — in der Stellung der Zuordnung (A-Stellung)."""
        dreieck, gewichte, abstand = self.zuordnen()
        f = np.asarray(feld, dtype=np.float64)
        aus = (gewichte[:, :, None] * f[self.dreiecke[dreieck]]).sum(axis=1)
        weit = abstand > self.WEIT_M
        if weit.any():
            if self._putz is None:
                self._putz = G9feldputz.vom_kaefig()
            aus = self._putz.fuellen(aus, weit)
        return aus
