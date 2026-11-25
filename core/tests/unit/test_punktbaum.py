# -*- coding: utf-8 -*-
u"""`G9rasternachbarn` über den Punktbaum (`G9punktbaum`, 25.11.2026): dieselben Nachbarn wie die volle Abstandsmatrix — Abstand, Nummer, Gleichstand nach kleinerer Nummer.

1. k = 1, 4 und 12 an dichten, weit verstreuten und doppelten Punkten; Anfragen weit außerhalb.
2. Wenige Punkte (weniger als ein Blatt) und ein einziger Punkt.
3. Über `BAUM_BIS` rechnet das Raster — mit demselben Ergebnis.

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `g9_pb_suche` (`g9kerne_cu/punktbaum.cu`) die Schranke des Kastens ohne den Rundungszuschlag → Fall 1 rot (Gleichstände);
`BAUM_BIS` in `G9rasternachbarn` auf 0 → Fall 1 bleibt grün, Fall 3 prüft dann nichts mehr. Geschrieben, nicht gelaufen.
"""
import unittest
from unittest import mock

import torch

from Genesis9.rasternachbarn import G9rasternachbarn
from Genesis9.rechenkarte import G9rechenkarte

KARTE = 'cuda'


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class PunktbaumTest(unittest.TestCase):

    @staticmethod
    def karte():
        return G9rechenkarte.an() or G9rechenkarte(torch)

    @staticmethod
    def bezug(daten, anfrage, k):
        d = anfrage[:, None, :] - daten[None, :, :]
        w = (d[..., 0] * d[..., 0] + d[..., 1] * d[..., 1]) + d[..., 2] * d[..., 2]
        w_s, o = torch.sort(w, dim=1, stable=True)
        return w_s[:, :k], o[:, :k]

    @staticmethod
    def wolken(saat):
        g = torch.Generator(device=KARTE).manual_seed(saat)
        dicht = torch.rand(1500, 3, device=KARTE, dtype=torch.float64, generator=g) * 0.1
        grob = torch.rand(40, 3, device=KARTE, dtype=torch.float64, generator=g) + 0.5
        daten = torch.cat([dicht, grob, dicht[:30]])
        weit = torch.full((3, 3), 40.0, device=KARTE, dtype=torch.float64)
        return daten, torch.cat([torch.rand(800, 3, device=KARTE, dtype=torch.float64, generator=g) * 1.6, dicht[:50], weit])

    def pruefen(self, daten, anfrage, k):
        w, i = G9rasternachbarn(self.karte(), daten).naechste(anfrage, k)
        w_b, i_b = self.bezug(daten, anfrage, k)
        self.assertTrue(torch.equal(w, w_b))
        self.assertTrue(torch.equal(i, i_b))

    def test_1_wie_die_volle_matrix(self):
        for saat, k in ((1, 1), (2, 4), (3, 12)):
            with self.subTest(k=k):
                self.pruefen(*self.wolken(saat), k)

    def test_2_wenige_punkte(self):
        daten, anfrage = self.wolken(4)
        self.pruefen(daten[:5], anfrage, 3)
        self.pruefen(daten[:1], anfrage, 1)

    def test_3_raster_gibt_dasselbe(self):
        daten, anfrage = self.wolken(5)
        baum = G9rasternachbarn(self.karte(), daten).naechste(anfrage, 4)
        with mock.patch.object(G9rasternachbarn, 'BAUM_BIS', 0):
            raster = G9rasternachbarn(self.karte(), daten).naechste(anfrage, 4)
        self.assertTrue(all(torch.equal(a, b) for a, b in zip(baum, raster, strict=True)))
