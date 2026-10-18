# -*- coding: utf-8 -*-
u"""Hbzuordnung — je Genesis-Browserpunkt seine HumanBody-Punkte (aus `Hbmorphuebertragung` herausgeloest, 17.10.2026).

Zu jedem Punkt der Genesis-Grundfigur (im HumanBody-Massstab, `paar['skaliert']`) werden die `KANDIDATEN` naechsten HumanBody-Punkte DESSELBEN Koerperteils gesucht,
gewichtet mit 1/Abstand, nur mit gleichsinniger Normale (Skalarprodukt > `EINIG`). Fehlt so ein Gegenstueck (Mundinnenraum, Augenhoehlen, gespreizte Zehen), steht der
Punkt in `ungueltig` und wird bei der Uebertragung aus seinen Nachbarn gefuellt.

AUSGERICHTET (17.10.2026): Genesis' Gesicht sitzt 9–25 mm anders als das von HumanBody (Anker Nase, Kinn, Scheitel, Hinterkopf, Ohren; gemessen mit
`ProjektTemp/_wegwerf/hautebenen/quelle_schwach_ausrichten.py`). Ein Regler mit 3 mm Hub auf 1–2 cm Flaeche (Augeninnenwinkel, Nasenfluegelfalte) fiel deshalb zwischen die Punkte:
`hb:Eyes_innerSinus` kam mit 0,000 mm an, `hb:Eyes_InnerPosZ` mit 0,19 statt 2,9 mm. Die ausgerichtete Zuordnung legt den Kopf der Suchpunkte mit `Mhkopfausrichtung` (dieselbe
Abbildung wie beim MakeHuman-Klon) auf HumanBodys Kopf. Sie ist NICHT besser fuer alle Regler (Mund: `Mouth_UpperlipVolume` 0,94 → 0,03 mm) — `Hbmorphuebertragung`
nimmt sie nur als Rueckfall fuer Regler, die sonst verschluckt wuerden.
"""
import numpy as np
from Genesis9.kollision import G9kollision

from .g9aufhumanbody import G9aufhumanbody
from .mhkopfanker import Mhkopfanker
from .mhkopfausrichtung import Mhkopfausrichtung

__all__ = ['Hbzuordnung']


class Hbzuordnung:
    u"""Kandidaten und Gewichte einer Paarung, mit oder ohne Kopfausrichtung."""

    KANDIDATEN = 6
    EINIG = G9aufhumanbody.EINIG
    #: Weiter als das (m) vom Kaefigpunkt entfernt liegt kein HumanBody-Gegenstueck mehr (gemessen 17.10.2026: 572 von 25.182 Punkten).
    LUECKE_M = 0.05
    #: Wie weit unter dem Kinn die Ausrichtung ausgelaufen ist (m).
    HALS_M = 0.12

    def __init__(self, paar, hb, ursprung, zahl, ausgerichtet=False):
        u"""`paar`: Paarung (`G9aufhumanbody`), `hb`: `{punkte, normalen}` der Grundfigur, `ursprung`: Browserpunkt -> Kaefigpunkt, `zahl`: Kaefigpunkte."""
        self.paar = paar
        self.hb = hb
        self.ursprung = np.asarray(ursprung, dtype=np.int64)
        self.zahl = int(zahl)
        self.ausgerichtet = bool(ausgerichtet)
        self._suche = None
        self._kand = None
        self._gewicht = None
        self._naehe = None
        self._ohne = None
        self._luecke = None

    def suchpunkte(self):
        u"""(27087, 3) die Genesis-Browserpunkte im HumanBody-Raum, an denen gesucht wird."""
        if self._suche is None:
            suche = np.asarray(self.paar['skaliert'], dtype=np.float64)
            if self.ausgerichtet:
                hb = np.asarray(self.hb['punkte'], dtype=np.float64)
                kinn = Mhkopfanker.finden(hb)['kinn'][1]
                suche = Mhkopfausrichtung.berechnen(suche, hb, [], [], y_null=kinn - self.HALS_M).anwenden(suche)
            self._suche = suche
        return self._suche

    def kandidaten(self):
        u"""`(kandidaten (27087, K), gewichte (27087, K))` — Gewichte summieren zu 1."""
        if self._kand is None:
            self._rechnen()
        return self._kand, self._gewicht

    def ungueltig(self):
        u"""(Kaefigpunkte,) True, wo es kein HumanBody-Gegenstueck gibt: naechster Kandidat weiter als `LUECKE_M` oder nur mit gegenlaeufiger Normale."""
        if self._luecke is None:
            self.kandidaten()
            kaefig = np.zeros(self.zahl)
            np.maximum.at(kaefig, self.ursprung, np.where(np.isfinite(self._naehe), self._naehe, 9.0))
            ohne = np.zeros(self.zahl)
            np.maximum.at(ohne, self.ursprung, self._ohne.astype(float))
            self._luecke = (kaefig > self.LUECKE_M) | (ohne > 0)
        return self._luecke

    def _rechnen(self):
        paar, hb, suche = self.paar, self.hb, self.suchpunkte()
        zahl = len(paar['g9_punkte'])
        kand = np.tile(paar['zu'][:, None], (1, self.KANDIDATEN))
        gewicht = np.zeros((zahl, self.KANDIDATEN))
        gewicht[:, 0] = 1.0
        #: Abstand (m, HumanBody-Lage) des naechsten Kandidaten je Genesis-Browserpunkt — gross = kein Gegenstueck (Mundinnenraum, Zehen).
        self._naehe = np.full(zahl, np.inf)
        self._ohne = np.zeros(zahl, dtype=bool)
        for _teil, (g9_idx, hb_idx) in paar['segmente'].items():
            if not len(g9_idx) or len(hb_idx) < self.KANDIDATEN:
                continue
            abstand, nr = G9kollision.naechste(G9kollision.baum(hb['punkte'][hb_idx]), suche[g9_idx], k=self.KANDIDATEN)
            self._naehe[g9_idx] = np.asarray(abstand, dtype=np.float64)[:, 0]
            nr = hb_idx[np.asarray(nr)]
            w = 1.0 / np.maximum(np.asarray(abstand, dtype=np.float64), 1e-4)
            einig = np.einsum('ik,ijk->ij', paar['g9_normalen'][g9_idx], hb['normalen'][nr]) > self.EINIG
            keiner = ~einig.any(axis=1)
            einig[keiner, 0] = True                 # sonst der naechste, wie `zu`
            # ... aber mit gegenlaeufiger Normale kippt das Vorzeichen jedes Deltas entlang der Normale — fuer Felder zaehlt so ein Punkt als „ohne Gegenstueck“.
            self._ohne[np.asarray(g9_idx)[keiner]] = True
            w = np.where(einig, w, 0.0)
            kand[g9_idx] = nr
            gewicht[g9_idx] = w / w.sum(axis=1, keepdims=True)
        self._kand, self._gewicht = kand, gewicht
