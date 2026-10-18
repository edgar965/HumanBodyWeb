# -*- coding: utf-8 -*-
u"""Mhklonuebertragung — ein MakeHuman-Verschiebungsfeld (hm08) auf den Genesis-9-Kaefig legen (17.10.2026).

Edgar, 17.10.2026: „du solltest ALLE Morphs und Regler aus den anderen Projekten portieren und als neue Morphs fuer Genesis nachbauen“.

DER WEG
=======
1. **Der Klon** (`G9mhklon`, 25.09.2026 fuer Kleider gebaut): das MakeHuman-Netz in der Gestalt von Genesis 9 — jeder hm08-Hautpunkt liegt auf der
   Genesis-Flaeche. Hier aus der **weiblichen Vorgabefigur** gebaut (Geschlecht 0), nicht aus `base.obj`: Die Morphs sind Differenzen gegen diese
   Figur, und Genesis 9 ist eine Frau; ein Klon aus der Mischfigur (Geschlecht 0,5) legte Brust und Hueften neben die Genesis-Brust.
   **Mit ausgerichtetem Kopf** (`Mhkopfklon`, 17.10.2026): der Rumpfklon legte MakeHumans Gesicht 26–30 mm hinter Genesis' Gesicht (gemessen an Nasenspitze
   und Kinn) — fuer Kleider unerheblich, fuer Nasen-, Mund- und Augenregler nicht.
2. **Das Delta wandert mit dem Klon**: `abbilden` ist der LINEARE Teil von `G9mhklon.geschaetzt` (Rahmen der Glieder, Aehnlichkeit des Rumpfs) — ein
   Delta am Unterarm dreht und streckt sich wie der Unterarm, ohne dass die ICP-Anpassung an die Haut mitspielt (die ist nichtlinear und gilt der Lage,
   nicht der Verschiebung).
3. **Auf den Kaefig**: je Kaefigpunkt die `KANDIDATEN` naechsten Hautpunkte des Klons mit gleichsinniger Normale (Skalarprodukt > `EINIG`), gewichtet
   1/Abstand. Punkte ohne Treffer (Mundinnenraum, Augenhoehlen — hm08 hat dort nichts) sind `ungueltig` und werden aus den Nachbarn gefuellt
   (`G9feldputz`), dann geglaettet und geputzt wie bei den HumanBody-Morphs (`Hbmorphuebertragung`).

EINHEITEN: MakeHuman rechnet in Dezimetern; `Mhformung`-Deltas gehen mit 0,1 in Meter. Das Skelett-Mass (`Mhrigmass`) rechnet in dm und rechnet selbst um.
"""
import numpy as np
from Genesis9.basisnetz import G9basisnetz
from Genesis9.feldputz import G9feldputz
from Genesis9.kollision import G9kollision

from .mhkopfklon import Mhkopfklon

__all__ = ['Mhklonuebertragung']


class Mhklonuebertragung:
    u"""hm08-Delta (Meter) -> Kaefigfeld (Meter)."""

    #: Geschlecht der Bezugsfigur (MakeHuman 0 = Frau).
    GESCHLECHT = 0.0
    KANDIDATEN = 6
    EINIG = 0.3
    #: Weiter als das (m) von einem Klon-Hautpunkt entfernt gilt ein Kaefigpunkt als ohne Gegenstueck.
    LUECKE_M = 0.03
    GLAETTUNG = 6
    #: Deltas unter dieser Laenge (m) gelten als null.
    NULL_M = 2e-5

    def __init__(self):
        self.klon = None
        self.formung = None
        self._w = None
        self._kand = None
        self._gewicht = None
        self._ungueltig = None
        self._nachbar = None
        self._putz = None

    # ---------------------------------------------------------- Vorbereiten

    def vorbereiten(self):
        u"""Bezugsfigur, Klon, Zuordnung — einmal."""
        if self.klon is not None:
            return self
        from MakeHuman.basisnetz import Mhbasisnetz
        from MakeHuman.formung import Mhformung
        from MakeHuman.haut import Mhhaut
        from MakeHuman.skelett import Mhskelett
        from Genesis9.formung import G9formung
        self.formung = Mhformung({'gender': self.GESCHLECHT})
        roh = self.formung.punkte()
        mh = Mhbasisnetz.holen()
        alle = np.arange(len(mh.punkte))
        g9 = G9formung({})
        stufe = G9basisnetz.holen().netzstufe(0)
        grund = g9.punkte() - np.array([0.0, g9.boden(), 0.0])
        flaeche = (np.asarray(stufe.punkte(grund), dtype=np.float64), np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3))
        self.koerper = mh._punktnummern(('koerper',))
        self.klon = Mhkopfklon(mh.punkte_am_boden(alle, roh), self.koerper, Mhskelett(self.formung).bauen()['knochen'], Mhhaut.roh(),
                               g9.skelett().bauen()['knochen'], flaeche, mh.vierecke(('koerper',)))
        self.klon.boden = float(g9.boden())
        self.vierecke = mh.vierecke(('koerper',))
        self._zuordnen(g9)
        return self

    def _zuordnen(self, g9):
        u"""Je Kaefigpunkt die naechsten Klon-Hautpunkte mit gleichsinniger Normale."""
        klon_p = self.klon.punkte()
        haut = klon_p[self.koerper]
        n_klon = self._normalen(klon_p)[self.koerper]
        netz = G9basisnetz.holen()
        kaefig = np.asarray(netz.punkte, dtype=np.float64) - np.array([0.0, g9.boden(), 0.0])
        n_kaefig = netz.normalen()
        abstand, nr = G9kollision.naechste(G9kollision.baum(haut), kaefig, k=self.KANDIDATEN)
        abstand, nr = np.asarray(abstand, dtype=np.float64), np.asarray(nr)
        einig = np.einsum('ik,ijk->ij', n_kaefig, n_klon[nr]) > self.EINIG
        w = np.where(einig, 1.0 / np.maximum(abstand, 1e-4), 0.0)
        summe = w.sum(axis=1)
        self._ungueltig = (summe <= 0) | (abstand[:, 0] > self.LUECKE_M)
        self._kand = nr
        self._gewicht = w / np.maximum(summe, 1e-12)[:, None]

    def _normalen(self, punkte):
        q = self.vierecke
        n = np.cross(punkte[q[:, 2]] - punkte[q[:, 0]], punkte[q[:, 3]] - punkte[q[:, 1]])
        aus = np.zeros_like(punkte)
        for ecke in range(4):
            np.add.at(aus, q[:, ecke], n)
        laenge = np.linalg.norm(aus, axis=1, keepdims=True)
        laenge[laenge < 1e-12] = 1.0
        return aus / laenge

    # ------------------------------------------------------------ Uebertragen

    def abbilden(self, delta):
        u"""(M, 3) hm08-Delta in Metern -> Delta auf dem Klon, im Raum von Genesis (nur der lineare Teil von `G9mhklon.geschaetzt`)."""
        klon = self.klon
        if self._w is None:
            self._w = klon.anteile()
        w, glieder = self._w
        delta = np.asarray(delta, dtype=np.float64)
        aus = w[:, -1:] * (klon.rumpf(delta) - klon.rumpf(np.zeros((1, 3))))
        for i, glied in enumerate(glieder[:-1]):
            if not (w[:, i] > 0).any():
                continue
            (_gk, g_achsen, g_laenge), (_mk, m_achsen, m_laenge) = klon.glieder[glied]
            lokal = delta @ m_achsen.T
            lokal[:, 0] *= g_laenge / m_laenge
            lokal[:, 1:] *= klon.massstab
            aus += w[:, i:i + 1] * (lokal @ g_achsen)
        return klon.kopf_linear(aus)

    def putz(self):
        if self._putz is None:
            self._putz = G9feldputz.vom_kaefig()
        return self._putz

    def nachbarn(self):
        if self._nachbar is None:
            punkte = G9basisnetz.holen().punkte
            _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte, k=self.GLAETTUNG)
            self._nachbar = np.asarray(nachbar, dtype=np.int64)
        return self._nachbar

    def uebertragen(self, delta_m):
        u"""(25182, 3) Kaefigfeld aus einem hm08-Delta (M, 3) in Metern."""
        self.vorbereiten()
        klon_delta = self.abbilden(delta_m)[self.koerper]
        feld = np.einsum('ik,ikj->ij', self._gewicht, klon_delta[self._kand])
        putz = self.putz()
        feld = putz.fuellen(feld, self._ungueltig)
        feld = feld[self.nachbarn()].mean(axis=1)
        feld, _zacken = putz.putzen(feld)
        feld[np.linalg.norm(feld, axis=1) < self.NULL_M] = 0.0
        return feld

    def ungueltig(self):
        self.vorbereiten()
        return self._ungueltig
