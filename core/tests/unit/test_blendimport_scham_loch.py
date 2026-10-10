# -*- coding: utf-8 -*-
"""Das Loch in der Haut unter dem Scham-Stück (`Blendimportschamloch`) — an einer Kunsthaut, ohne Django, Genesis und trimesh.

Edgar, 09.10.2026, mit Bild: „bei der Scham gibt es immer noch die Probleme an den Rändern. Schau nach, wie Genesis das mit der Nase und
dem Mund macht, und mach es genau so." Bei Genesis ist ein Rand eine Kante, kein Rest einer Rechnung: Das Loch ist eine Menge ganzer
Dreiecke der Haut mit EINEM geschlossenen Kantenring (Daz' Geograft „Anatomical Elements" verschweißt seine Randpunkte damit).

Kunstwelt: Haut = Ebene y = 0, 24 × 24 Zellen von 4 mm (zwei Dreiecke je Zelle), Mitte im Ursprung; Schnittwert = Abstand zur Mitte − 30 mm.

1. Das Loch hat EINEN geschlossenen Ring: jeder Ringpunkt steht einmal da, jeder hat genau zwei Randkanten; die Ringpunkte liegen auf dem Kreis
   (30 mm ± eine Zelle), der Umfang ist der einer Treppe: zwischen dem des Kreises (2π · 30 mm) und dem 1,45-fachen (gemessen 1,28–1,34).
2. Im Loch liegen nur Dreiecke nahe der Scheibe (Mitte höchstens 30 mm + anderthalb Zellen), und die der Scheibe liegen drin.
3. Die Haut an UV-Nähten ist geteilt (Punkte doppelt, gleiche Lage): die Nachbarschaft zählt nach Lage — dasselbe Loch, EIN Ring.
4. Ein eingeschlossenes Loch im Loch (zwei Punkte mit positivem Wert in der Mitte) füllt sich; der Ring bleibt einer.
5. Ein Stück abseits der Scheibe (nicht verbunden) bleibt nicht im Loch; ein Loch aus ein paar Dreiecken ist ein Fehler.
6. `lage` und `ringpunkte` geben je Ringpunkt die Lage und die Nummer eines Punkts der Haut an dieser Lage.

Sabotage-Gegenprobe (nicht gelaufen — Tests laufen nur auf Ansage): in `_kanten` die Verschweißung (`self.rep`) durch `np.arange` ersetzen macht
Fall 3 rot (an der Naht entstünde ein zweiter Ring); `self.groesste(...)` in `loch` weglassen macht Fall 5 rot (das abseitige Stück
bliebe); `_eingeschlossene_fuellen` entfernen macht Fall 4 rot (zwei Ringe).
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportschamloch import Blendimportschamloch


class SchamlochTest(SimpleTestCase):
    databases = set()

    ZELLEN = 24
    ZELLE = 0.004
    RADIUS = 0.030

    def _haut(self, naht=False):
        """`(punkte, dreiecke)`: die Kunsthaut; mit `naht` ist die Spalte x = 0 doppelt (rechte Hälfte hat eigene Punkte)."""
        n = self.ZELLEN + 1
        halb = self.ZELLEN // 2
        punkte = [[(c - halb) * self.ZELLE, 0.0, (r - halb) * self.ZELLE] for r in range(n) for c in range(n)]
        nummer = {(r, c): r * n + c for r in range(n) for c in range(n)}
        if naht:
            for r in range(n):
                punkte.append(list(punkte[nummer[(r, halb)]]))
                nummer[(r, halb, 'rechts')] = len(punkte) - 1
        dreiecke = []
        for r in range(self.ZELLEN):
            for c in range(self.ZELLEN):
                rechts = naht and c >= halb

                def p(rr, cc, rechts=rechts):
                    return nummer[(rr, cc, 'rechts')] if (rechts and cc == halb) else nummer[(rr, cc)]
                a, b, d, e = p(r, c), p(r, c + 1), p(r + 1, c), p(r + 1, c + 1)
                dreiecke += [[a, b, d], [b, e, d]]
        return np.array(punkte), np.array(dreiecke)

    def _werte(self, punkte):
        return np.linalg.norm(punkte[:, [0, 2]], axis=1) - self.RADIUS

    def _mitten(self, punkte, dreiecke):
        return punkte[dreiecke].mean(axis=1)

    def test_1_das_loch_hat_einen_geschlossenen_ring(self):
        punkte, dreiecke = self._haut()
        haut = Blendimportschamloch(punkte, dreiecke)
        im_loch = haut.loch(self._werte(punkte))
        ring = haut.ring(im_loch)
        self.assertEqual(len(set(ring.tolist())), len(ring))
        kanten = haut.randkanten(im_loch)
        self.assertEqual(len(kanten), len(ring))
        # Der Ring liegt auf dem Kreis (gemessen 10.10.2026, `ProjektTemp/_wegwerf/import_serie/scham_loch_ring.py`: Radius der 56 Ringpunkte 28,0–32,2 mm
        # bei Soll 30). Sein UMFANG ist länger als der des Kreises: eine Kette von Dreieckskanten ist eine Treppe (zwischen 1,27 und 1,34 des Kreises bei
        # Zellen von 4, 2 und 1 mm — er konvergiert nicht gegen 1). Die frühere Schranke „± ein Viertel" war zu eng und hatte nie gelaufen.
        radien = np.linalg.norm(punkte[ring][:, [0, 2]], axis=1)
        self.assertLessEqual(float(np.abs(radien - self.RADIUS).max()), self.ZELLE)
        umfang = haut.bericht(im_loch, ring)['ring_mm'] / 1000.0
        kreis = 2 * np.pi * self.RADIUS
        self.assertGreaterEqual(umfang, kreis)
        self.assertLessEqual(umfang, 1.45 * kreis)

    def test_2_im_loch_liegen_nur_dreiecke_nahe_der_scheibe(self):
        punkte, dreiecke = self._haut()
        haut = Blendimportschamloch(punkte, dreiecke)
        im_loch = haut.loch(self._werte(punkte))
        abstand = np.linalg.norm(self._mitten(punkte, dreiecke)[:, [0, 2]], axis=1)
        self.assertLessEqual(float(abstand[im_loch].max()), self.RADIUS + 1.5 * self.ZELLE)
        innen = abstand < self.RADIUS - 2 * self.ZELLE
        self.assertGreater(float(im_loch[innen].mean()), 0.98)

    def test_3_eine_uv_naht_teilt_das_loch_nicht(self):
        punkte, dreiecke = self._haut()
        mit, dreiecke_mit = self._haut(naht=True)
        ohne_loch = Blendimportschamloch(punkte, dreiecke).loch(self._werte(punkte))
        haut = Blendimportschamloch(mit, dreiecke_mit)
        im_loch = haut.loch(self._werte(mit))
        self.assertEqual(int(im_loch.sum()), int(ohne_loch.sum()))
        ring = haut.ring(im_loch)                                   # ein Ring, keine Ausnahme
        self.assertGreater(len(ring), 20)

    def test_4_ein_eingeschlossenes_loch_im_loch_fuellt_sich(self):
        punkte, dreiecke = self._haut()
        werte = self._werte(punkte)
        mitte = np.flatnonzero(np.linalg.norm(punkte[:, [0, 2]], axis=1) < 1e-9)
        werte[mitte] = 1.0                                          # ein Punkt in der Mitte „außerhalb"
        haut = Blendimportschamloch(punkte, dreiecke)
        im_loch = haut.loch(werte)
        ring = haut.ring(im_loch)
        zentrum = np.linalg.norm(self._mitten(punkte, dreiecke)[:, [0, 2]], axis=1) < 2 * self.ZELLE
        self.assertTrue(bool(im_loch[zentrum].all()))
        self.assertEqual(len(haut.randkanten(im_loch)), len(ring))

    def test_5_ein_abseitiges_stueck_bleibt_nicht_und_ein_zu_kleines_loch_ist_ein_fehler(self):
        punkte, dreiecke = self._haut()
        werte = self._werte(punkte)
        haut = Blendimportschamloch(punkte, dreiecke)
        ohne = haut.loch(werte)
        # Ein Dreieck abseits der Scheibe (3–4 Zellen vom Rand), alle drei Punkte „innen" gesetzt: hängt nicht am Loch
        abstand = np.linalg.norm(self._mitten(punkte, dreiecke)[:, [0, 2]], axis=1)
        abseits = int(np.flatnonzero((abstand > self.RADIUS + 3 * self.ZELLE) & (abstand < self.RADIUS + 4 * self.ZELLE))[0])
        werte2 = werte.copy()
        werte2[dreiecke[abseits]] = -1.0
        mit = haut.loch(werte2)
        self.assertFalse(bool(mit[abseits]), 'ein Stück fern der Scheibe gehört nicht zum Loch')
        self.assertEqual(int(mit.sum()), int(ohne.sum()))
        klein = np.full(len(punkte), 1.0)
        klein[dreiecke[0]] = -1.0
        with self.assertRaises(ValueError):
            haut.loch(klein)

    def test_6_lage_und_nummer_der_ringpunkte(self):
        punkte, dreiecke = self._haut(naht=True)
        haut = Blendimportschamloch(punkte, dreiecke)
        ring = haut.ring(haut.loch(self._werte(punkte)))
        lage = haut.lage(ring)
        nummern = haut.ringpunkte(ring)
        self.assertEqual(lage.shape, (len(ring), 3))
        self.assertTrue(np.allclose(punkte[nummern], lage))
        self.assertTrue(np.allclose(lage[:, 1], 0.0))
