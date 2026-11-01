# -*- coding: utf-8 -*-
"""`KoerperKI_Fotos.Fotosaum` (Fassung 9 der Foto-Schale, 31.10.2026; Edgar, Job EdgarTrip: „Socken gehen über die Haut wo sie nicht sollten“, „Hose hat keinen Saum unten“) — an einem
Kunstglied (Zylinder 0,4 m, 41 Ringe × 16), ohne Figur und ohne Fotos.

1. Ein Bündchen am Unterschenkel endet mit EINEM Schnitt quer zur Achse: eine Zacke falscher Etiketten weit unter dem Schnitt verschwindet, alle neuen Randpunkte liegen genau auf der
   Schnitthöhe (zerschnittene Dreiecke statt einer Treppe über die Punkte).
2. Am Rumpf (kein Glied) bleibt das Etikett je Punkt, die Kante liegt zwischen den Punkten.
3. Das Saumband nimmt die Farbe von innen (nicht die Franse am Rand), etwas dunkler, mit Wulst nach außen.

Sabotage-Gegenprobe (31.10.2026): `FEHLER_MAX = -1` (kein Schnitt) → 1 rot; in `band` die Füllung weg (`wert = farbe`) → 3 rot.
"""
import math
import sys
import unittest
from types import SimpleNamespace

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))         # `Fotosaum` nutzt seit 01.11.2026 `Kostuemgpu` (Zusammenhang, Normalen)

from KoerperKI_Fotos.fotosaum import Fotosaum  # noqa: E402

RINGE, UM, LAENGE, RADIUS = 41, 16, 0.4, 0.05


def glied(name):
    """Kunstglied: Punkte (P,3), Dreiecke, t = y / LAENGE, ein Segment `name` mit Knochen 0 → LAENGE."""
    p = torch.tensor([[RADIUS * math.cos(2 * math.pi * k / UM), LAENGE * i / (RINGE - 1), RADIUS * math.sin(2 * math.pi * k / UM)]
                      for i in range(RINGE) for k in range(UM)], dtype=torch.float32)
    d = []
    for i in range(RINGE - 1):
        for k in range(UM):
            a, b, c, e = i * UM + k, i * UM + (k + 1) % UM, (i + 1) * UM + k, (i + 1) * UM + (k + 1) % UM
            d += [[a, c, b], [b, c, e]]
    knochen = [{'name': name, 'zentrum': [0.0, 0.0, 0.0], 'ende': [0.0, LAENGE, 0.0]}]
    return SimpleNamespace(g='cpu', d=torch.tensor(d), ruhe_p=p, segment=torch.zeros(len(p), dtype=torch.long), segment_namen=[name],
                           achse_t=p[:, 1] / LAENGE, n=SimpleNamespace(kin={'knochen': knochen}))


class Fotosaumtest(unittest.TestCase):

    def test_1_buendchen_mit_einem_schnitt_ohne_zacke(self):
        s = glied('l_shin')
        t = s.achse_t
        roh = t > 0.6
        roh[(t > 0.28) & (t < 0.33) & (torch.arange(len(t)) % UM < 3)] = True        # Zacke: drei Punkte je Ring, weit unter dem Bündchen
        alle = torch.ones(len(t), dtype=torch.bool)
        saum = Fotosaum(s, 'schuh')
        feld, befund = saum.feld(roh.float(), roh, alle, alle)
        self.assertTrue(befund['l_shin']['genommen'])
        self.assertFalse(bool((feld[(t > 0.28) & (t < 0.33)] > 0).any()), 'die Zacke gehört noch zum Stück')
        netz = saum.schneiden(feld, s.d, {'ruhe': s.ruhe_p}, torch.arange(len(t)))
        rand_t = netz['ruhe'][netz['rand'], 1] / LAENGE
        schnitt = befund['l_shin']['schnitt_t']
        self.assertGreater(len(rand_t), 0)
        self.assertLess(float((rand_t - schnitt).abs().max()), 1e-3, 'der Rand liegt nicht auf der Schnitthöhe')
        self.assertTrue(bool((netz['ruhe'][:, 1] / LAENGE >= schnitt - 1e-3).all()))

    def test_2_rumpf_behaelt_das_etikett(self):
        s = glied('chest_upper')
        t = s.achse_t
        roh = t > 0.5
        alle = torch.ones(len(t), dtype=torch.bool)
        saum = Fotosaum(s, 'oberteil')
        feld, befund = saum.feld(roh.float(), roh, alle, alle)
        self.assertEqual(sorted(befund), ['geschlossene_loecher'])                    # kein Glied, kein Schnitt
        netz = saum.schneiden(feld, s.d, {'ruhe': s.ruhe_p}, torch.arange(len(t)))
        rand_t = netz['ruhe'][netz['rand'], 1] / LAENGE
        self.assertLess(float((rand_t - 0.5).abs().max()), 1 / (RINGE - 1), 'die Kante liegt nicht zwischen den Ringen am Etikettwechsel')

    def test_4_kleines_loch_im_stueck_wird_geschlossen_der_offene_rest_nicht(self):
        """Lauf saum1 (31.10.2026): Hautfleck oben auf dem Fuß in der Socke. Ein Loch von zwei Ringen × vier Punkten (≈ 6 cm²) schließt sich; das freie Ende des Glieds (≫ 50 cm²) bleibt frei."""
        s = glied('l_foot')
        t = s.achse_t
        roh = t > 0.3
        loch = (t > 0.6) & (t < 0.63) & (torch.arange(len(t)) % UM < 4)
        roh[loch] = False
        alle = torch.ones(len(t), dtype=torch.bool)
        feld, befund = Fotosaum(s, 'schuh').feld(roh.float(), roh, alle, alle)
        self.assertTrue(bool((feld[loch] > 0).all()), 'das Loch ist offen geblieben')
        self.assertFalse(bool((feld[t < 0.25] > 0).any()), 'das offene Ende wurde mit geschlossen')
        self.assertEqual(befund['geschlossene_loecher']['zahl'], 1)

    def test_3_saumband_farbe_von_innen_und_wulst(self):
        s = glied('r_thigh')
        t = s.achse_t
        roh = t < 0.7
        alle = torch.ones(len(t), dtype=torch.bool)
        saum = Fotosaum(s, 'hose')
        feld, _ = saum.feld(roh.float(), roh, alle, alle)
        farbe = torch.full((len(t), 3), 0.2)
        farbe[t > 0.66] = 0.9                                                        # Franse: am Rand traf das Foto die Haut
        netz = saum.schneiden(feld, s.d, {'ruhe': s.ruhe_p, 'haltung': s.ruhe_p.clone(), 'farbe': farbe}, torch.arange(len(t)))
        aus = saum.band(netz)
        rand = aus['farbe'][netz['rand']]
        self.assertLess(float(rand.max()), 0.2 * 1.01, 'am Rand bleibt die Franse')
        self.assertAlmostEqual(float(rand.mean()), 0.2 * Fotosaum.SAUM_HELL, places=3)
        radius = aus['ruhe'][netz['rand']][:, [0, 2]].norm(dim=1)
        self.assertGreater(float(radius.min()), RADIUS * math.cos(math.pi / UM) + 0.5 * Fotosaum.WULST_M)
        self.assertEqual(aus['saum']['breite_mm'], 20.0)


if __name__ == '__main__':
    unittest.main()
