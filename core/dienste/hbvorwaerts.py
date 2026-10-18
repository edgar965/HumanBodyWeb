# -*- coding: utf-8 -*-
u"""Hbvorwaerts — ein HumanBody-Delta VORWAERTS auf den Genesis-Kaefig legen (17.10.2026, aus `Hbmorphuebertragung` heraus).

Die Rueckwaerts-Uebertragung (`Hbmorphuebertragung.uebertragen`) fragt je Genesis-Punkt: „Welche HumanBody-Punkte liegen hier?" — liegt ein kleines Merkmal (Brustwarze, Mundwinkelfalte) in
HumanBody woanders als in Genesis, liest kein Genesis-Punkt die Quellpunkte, und das Delta geht verloren: `hb:Torso_BreastNipple` kam mit 0,000 mm an (Quelle 5,9 mm; der naechste
Genesis-Punkt liegt 40 mm neben der Brustwarze), `hb:Mouth_Protusion` mit 0,04 (Quelle 3,8). Vorwaerts fragt jeder BEWEGTE HumanBody-Punkt: „Welche Genesis-Punkte liegen hier?" — und legt sein
Delta (im Rahmen des Quellpunkts zerlegt, im Rahmen des Zielpunkts aufgebaut, wie rueckwaerts) auf die `K` naechsten Genesis-Punkte DESSELBEN Koerperteils mit gleichsinniger Normale. Kein bewegter
Punkt geht mehr verloren; das Merkmal landet auf dem naechsten gleichartigen Stueck Haut.

Dann wird gemittelt (summierte Delta / summiertes Gewicht, „normalisierte Faltung" ueber die Kaefignachbarn), damit die Luecken zwischen den Treffern geschlossen werden und der Rand sanft ausklingt:
Je Kaefigpunkt `S = Σ w·δ` und `W = Σ w`; nach `GLAETTEN` Durchgaengen ueber die Nachbarn ist das Feld `S / max(W, W_BEZUG)`, `W_BEZUG` das mittlere Gewicht eines getroffenen Punkts — im Kern ist es das
mittlere Delta, am Rand faellt es mit der Dichte der Treffer ab. Die Staerke kann dabei nie ueber der Quelle liegen.

Nur Koerperteile mit Haut: `face_internal` (Mundinnenraum, Augen, Zaehne — bei Genesis Anhaenge) bleibt aussen vor, sonst landeten Iris- und Zahnregler auf dem Lid.
"""
import numpy as np
from Genesis9.kollision import G9kollision

__all__ = ['Hbvorwaerts']


class Hbvorwaerts:
    u"""Vorwaertsuebertragung zu einer Paarung, mit oder ohne Kopfausrichtung der Suchpunkte."""

    K = 3
    SUCHE = 8
    EINIG = 0.3
    #: Weiter als das (m) vom Quellpunkt liegt kein Genesis-Gegenstueck mehr.
    NAEHE_M = 0.05
    #: Quellpunkte mit weniger als dieser Teil der groessten Verschiebung zaehlen nicht (Rauschen der Paarung).
    QUELLE_ANTEIL = 0.02
    #: Durchgaenge der normalisierten Faltung. Gemessen 17.10.2026 (`ProjektTemp/_wegwerf/hautebenen/vorwaerts_glaetten.py`): Brustwarze 80 / 47 / 30 / 21 % des Hubs bei 0 / 1 / 2 / 3 Durchgaengen,
    #: Rauheit (Abweichung vom Mittel der Nachbarn) 56 / 38 / 32 / 26 %; Lippenvorstand 52 / 37 / 33 / 28 % bei Rauheit 66 / 38 / 18 / 10 %. Zwei ist der Kompromiss: ein Stueck Haut, kein Rauschen.
    GLAETTEN = 2
    AUSSEN = ('face_internal',)

    def __init__(self, paar, hb, suche, ursprung, zahl, nachbar):
        u"""`suche`: Genesis-Browserpunkte im HumanBody-Raum (`Hbzuordnung.suchpunkte`), `nachbar`: (Kaefigpunkte, k) naechste Kaefigpunkte."""
        self.paar, self.hb, self.suche = paar, hb, np.asarray(suche, dtype=np.float64)
        self.ursprung = np.asarray(ursprung, dtype=np.int64)
        self.zahl, self.nachbar = int(zahl), np.asarray(nachbar, dtype=np.int64)
        self._baeume = {}

    def _baum(self, teil, g9_idx):
        if teil not in self._baeume:
            self._baeume[teil] = G9kollision.baum(self.suche[g9_idx])
        return self._baeume[teil]

    def treffer(self, hb_delta):
        u"""`(S (Kaefig, 3), W (Kaefig,))` — die summierten Deltas und Gewichte; `W` ist null, wo nichts getroffen wurde."""
        paar, hb = self.paar, self.hb
        delta = np.asarray(hb_delta, dtype=np.float64)
        betrag = np.linalg.norm(delta, axis=1)
        quelle = betrag > self.QUELLE_ANTEIL * max(float(betrag.max()), 1e-12)
        summe = np.zeros((len(paar['g9_punkte']), 3))
        gewicht = np.zeros(len(paar['g9_punkte']))
        for teil, (g9_idx, hb_idx) in paar['segmente'].items():
            if teil in self.AUSSEN or not len(g9_idx):
                continue
            hb_idx = np.asarray(hb_idx)
            q = hb_idx[quelle[hb_idx]]
            if not len(q):
                continue
            g9_idx = np.asarray(g9_idx)
            k = min(self.SUCHE, len(g9_idx))
            abstand, nr = G9kollision.naechste(self._baum(teil, g9_idx), hb['punkte'][q], k=k)
            abstand, nr = np.asarray(abstand, dtype=np.float64).reshape(len(q), -1), np.asarray(nr).reshape(len(q), -1)
            ziel = g9_idx[nr]
            einig = np.einsum('ik,ijk->ij', hb['normalen'][q], paar['g9_normalen'][ziel]) > self.EINIG
            nah = abstand <= self.NAEHE_M
            gut = einig & nah
            rang = np.cumsum(gut, axis=1)
            gut &= rang <= self.K                                   # die K naechsten mit gleichsinniger Normale
            w = np.where(gut, 1.0 / np.maximum(abstand, 1e-3), 0.0)
            anteile = np.einsum('iaj,ij->ia', hb['rahmen'][q], delta[q])         # Delta in den Rahmen des Quellpunkts
            im_ziel = np.einsum('ia,ikaj->ikj', anteile, paar['g9_rahmen'][ziel]) / paar['massstab']
            np.add.at(summe, ziel, w[..., None] * im_ziel)
            np.add.at(gewicht, ziel, w)
        kaefig_s, kaefig_w = np.zeros((self.zahl, 3)), np.zeros(self.zahl)
        np.add.at(kaefig_s, self.ursprung, summe)
        np.add.at(kaefig_w, self.ursprung, gewicht)
        return kaefig_s, kaefig_w

    def uebertragen(self, hb_delta):
        u"""(Kaefig, 3) das Feld — oder Nullen, wenn nichts getroffen wurde."""
        s, w = self.treffer(hb_delta)
        getroffen = w[w > 0]
        if not len(getroffen):
            return np.zeros((self.zahl, 3))
        bezug = float(np.median(getroffen))
        for _ in range(self.GLAETTEN):
            s, w = s[self.nachbar].mean(axis=1), w[self.nachbar].mean(axis=1)
        return s / np.maximum(w, bezug)[:, None]
