# -*- coding: utf-8 -*-
"""`G9rasternachbarn.naechste` seit 12.11.2026: offene Zeilen erst mit größerem Block (`RINGE`), k = 1 ohne Sortieren (kleinster Wert, bei Gleichstand kleinster Index). Anlass: Abstimm-Netz
→ volles Netz des Zauberers 16,3 s, der Baum auf der CPU 0,8 s (`ProjektTemp/_wegwerf/genesis_zuerst/umbau/naechste_zelle.py`); Gegenprobe gegen die alte Fassung
`rasternachbarn_probe.py` (8 Fälle bitgleich, Sabotage rot).

Bezug hier: die volle Abstandsmatrix in derselben Formel ((dx² + dy²) + dz², float64), kleinste Zeile zuerst. Braucht die Grafikkarte (sonst übersprungen). Nicht gelaufen — läuft nur auf Ansage.
Sabotage: in `_block` beim k = 1-Weg `'amin'` des Index durch `'amax'` ersetzen → `test_2` rot; `RINGE = ()` → `test_3` rot (Zeilen in der Vollsuche).
"""
import unittest

import torch

from Genesis9.rasternachbarn import G9rasternachbarn
from Genesis9.rechenkarte import G9rechenkarte


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class RingeTest(unittest.TestCase):

    @staticmethod
    def _karte():
        return G9rechenkarte.an() or G9rechenkarte(torch)

    @staticmethod
    def _bezug(daten, anfrage, k):
        d = anfrage[:, None, :] - daten[None, :, :]
        w = (d[..., 0] * d[..., 0] + d[..., 1] * d[..., 1]) + d[..., 2] * d[..., 2]
        idx = torch.arange(len(daten), device=daten.device).expand_as(w)
        # stabil nach Wert sortieren, Gleichstand → kleinerer Index (der Index steht schon aufsteigend)
        w_s, o = torch.sort(w, dim=1, stable=True)
        return w_s[:, :k], idx.gather(1, o)[:, :k]

    def _wolken(self, saat):
        g = torch.device('cuda')
        gen = torch.Generator(device=g).manual_seed(saat)
        dicht = torch.rand(1500, 3, device=g, dtype=torch.float64, generator=gen) * 0.1
        grob = torch.rand(40, 3, device=g, dtype=torch.float64, generator=gen) * 1.0 + 0.5      # weit verstreut: dort liegt der Nächste weit außerhalb einer Zelle
        daten = torch.cat([dicht, grob, dicht[:30]])                                                # 30 doppelte Punkte: Gleichstand
        anfrage = torch.cat([torch.rand(2000, 3, device=g, dtype=torch.float64, generator=gen) * 1.6, dicht[:50]])
        return daten, anfrage

    def test_1_k1_wie_die_volle_matrix(self):
        daten, anfrage = self._wolken(1)
        w, i = G9rasternachbarn(self._karte(), daten).naechste(anfrage, 1)
        w_b, i_b = self._bezug(daten, anfrage, 1)
        self.assertTrue(torch.equal(w, w_b))
        self.assertTrue(torch.equal(i, i_b))

    def test_2_gleichstand_nimmt_den_kleineren_index(self):
        daten, anfrage = self._wolken(2)
        _w, i = G9rasternachbarn(self._karte(), daten).naechste(anfrage[-50:-20], 1)
        # die Anfragen SIND die ersten 30 Datenpunkte, die je eine Kopie mit Index ≥ 1540 haben → der kleinere Index gewinnt
        self.assertTrue(torch.equal(i[:, 0], torch.arange(30, device=daten.device)))

    def test_3_offene_zeilen_gehen_in_die_ringe_nicht_in_die_vollsuche(self):
        daten, anfrage = self._wolken(3)
        raster = G9rasternachbarn(self._karte(), daten)
        w, i = raster.naechste(anfrage, 3)
        w_b, i_b = self._bezug(daten, anfrage, 3)
        self.assertTrue(torch.equal(w, w_b))
        self.assertTrue(torch.equal(i, i_b))
        self.assertGreater(raster.ringe[0], 0, 'die Wolke soll offene Zeilen erzeugen, sonst prüft der Test die Ringe nicht')
        self.assertLess(raster.offen, raster.ringe[0], 'die Ringe sollen offene Zeilen beweisen')

    def test_4_grenze_wie_distance_upper_bound(self):
        daten, anfrage = self._wolken(4)
        grenze = 0.02
        w, i = G9rasternachbarn(self._karte(), daten).naechste(anfrage, 1, grenze=grenze)
        w_b, i_b = self._bezug(daten, anfrage, 1)
        weit = w_b[:, 0] > grenze ** 2
        self.assertTrue(torch.isinf(w[weit, 0]).all())
        self.assertTrue((i[weit, 0] == len(daten)).all())
        self.assertTrue(torch.equal(w[~weit], w_b[~weit]))
        self.assertTrue(torch.equal(i[~weit], i_b[~weit]))


if __name__ == '__main__':
    unittest.main()
