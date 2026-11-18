"""Lagen der Garderobe (`Garderobelagen`), Prüfung „Untere Lage durch Stück“ (`Kostuemlagedurch`), Rumpfkapseln (`Koerperkollision`) und Handton (`Hautgrundhand` Fassung 2) —
16.11.2026, Edgar zur Goldprinzessin: „Die Hose scheint noch über das Oberteil durch“, „Die Hand unter den Handschuhen ist blau“, „ja, mach beides“ (Rumpfkapsel).

Kunstdaten auf der Karte (ohne Karte übersprungen), keine echten Netze. Schreibt nichts.

Sabotage, je Fall rot:
  - in `Garderobelagen.senken` `lg['flaeche'] - lg['normale'] * tiefe` durch `+` → test_1 (Hose landet über der Jacke).
  - in `Garderobelagen.senken` `0.5 * platz` durch `platz` → test_2 (Hose bis auf die Haut statt in die Mitte).
  - in `Kostuemlagedurch.messen` `l2 > l1` durch `l2 >= l1` → test_3 (Jacke vor Jacke zählt als Durchstechen).
  - `'rumpf'` aus `Koerperkollision.GRUPPEN` nehmen → test_5 (keine Kapsel um spine3).
  - in `Eigentrennung.schoss` `& (hoehe > hoehe[bein].median())` streichen → test_6 (das Weiß des Stiefels wächst mit).
test_4 prüft nur das Maß (`Hautgrund.locker`), mit dem `Hautgrundhand` den Ton der Fotohand verwirft — nicht `anwenden` selbst (braucht `Stufe2haut`).

Geschrieben am 16.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import skipUnless

import torch
from django.conf import settings
from django.test import SimpleTestCase

for _pfad in (str(Path(settings.TOOLS_ROOT) / 'meshgenesis'), str(Path(settings.TOOLS_ROOT))):
    if _pfad not in sys.path:
        sys.path.insert(0, _pfad)

KARTE = torch.cuda.is_available()


def _ebene(z, halb=0.1, n=11):
    """Gitter n × n in der Höhe z (m) über x, y ∈ [−halb, halb] → (Punkte (n², 3), Dreiecke)."""
    s = torch.linspace(-halb, halb, n, dtype=torch.float64, device='cuda')
    x, y = torch.meshgrid(s, s, indexing='ij')
    p = torch.stack([x.reshape(-1), y.reshape(-1), torch.full((n * n,), z, dtype=torch.float64, device='cuda')], 1)
    i = torch.arange(n - 1, device='cuda')
    a = (i[:, None] * n + i[None, :]).reshape(-1)
    f = torch.cat([torch.stack([a, a + n, a + 1], 1), torch.stack([a + 1, a + n, a + n + 1], 1)])
    return p, f


@skipUnless(KARTE, 'braucht die Karte')
class LagenTest(SimpleTestCase):
    def _senken(self, z_aussen, punkte):
        from meshgenesis_flaechenlage import Flaechenlage
        from meshgenesis_garderobe_lagen import Garderobelagen
        figur, _f = _ebene(0.0, 0.15, 31)
        lagen = Garderobelagen(None, figur)
        return lagen.senken(Flaechenlage([_ebene(z_aussen)], figur), torch.tensor(punkte, dtype=torch.float64, device='cuda'))

    def test_1_hose_unter_jacke(self):
        """Jacke 2 cm über der Haut: Hosenpunkte darüber und knapp darunter kommen 4 mm unter die Jacke; ein Punkt neben der Jacke bleibt."""
        neu, bewegt = self._senken(0.02, [[0.0, 0.0, 0.021], [0.03, -0.02, 0.019], [0.3, 0.0, 0.021]])
        self.assertTrue(bool(bewegt[0]) and bool(bewegt[1]) and not bool(bewegt[2]))
        self.assertAlmostEqual(float(neu[0, 2]), 0.016, delta=5e-4)
        self.assertAlmostEqual(float(neu[1, 2]), 0.016, delta=5e-4)
        self.assertAlmostEqual(float(neu[2, 2]), 0.021, delta=1e-9)

    def test_2_platz_halb(self):
        """Jacke nur 4 mm über der Haut: die Hose kommt in die Mitte (2 mm), nicht auf oder unter die Haut."""
        neu, _bewegt = self._senken(0.004, [[0.0, 0.0, 0.005]])
        self.assertAlmostEqual(float(neu[0, 2]), 0.002, delta=3e-4)


@skipUnless(KARTE, 'braucht die Karte')
class LagedurchTest(SimpleTestCase):
    def test_3_durchstechen_zaehlen(self):
        """Links sticht die Hose durch die Jacke (vorn Hose, zurückgeschoben Jacke), rechts liegt die Jacke vorn: Anteil der Jacke 0,5, darunter Hose."""
        from meshgenesis_kostuem_lagedurch import Kostuemlagedurch
        from meshgenesis_kostuemarten import Kostuemarten
        p = torch.zeros((3, 3), device='cuda')
        f = torch.tensor([[0, 1, 2]], device='cuda')
        szene = SimpleNamespace(koerper=(p, f, None), teile=[{'art': 'hose', 'punkte': p, 'dreiecke': f}, {'art': 'kleid', 'punkte': p, 'dreiecke': f}])
        hose, kleid = Kostuemarten.ARTEN.index('hose'), Kostuemarten.ARTEN.index('kleid')
        a1 = torch.full((32, 32), kleid, dtype=torch.int64, device='cuda')
        a1[:, :16] = hose
        a2 = torch.full((32, 32), kleid, dtype=torch.int64, device='cuda')

        class Fest(Kostuemlagedurch):
            def _arten(self, bild, ansicht, zurueck, blick):
                return a2 if zurueck else a1

        aus = Fest(szene, 16).messen(None, ('vorne', (0, 0, 1.0), (1.0, 0, 0)))
        self.assertEqual(aus['kleid'][1], 'hose')
        self.assertAlmostEqual(aus['kleid'][0], 0.5, delta=1e-6)


class HandtonTest(SimpleTestCase):
    def test_4_handschuh_kein_hautton(self):
        """Der Ton der Fotohand der Goldprinzessin (Handschuh, Lab 23,5 / 9,4 / −27,3) ist nicht locker hautfarben, der Hautton der Person (57,7 / 15,6 / 22,6) schon."""
        from meshgenesis_hautgrund import Hautgrund
        lab = torch.tensor([[23.5, 9.4, -27.3], [57.7, 15.6, 22.6]], dtype=torch.float64)  # cpu gewollt: drei Zahlen, ohne Karte prüfbar
        self.assertEqual(Hautgrund.locker(lab).tolist(), [False, True])


@skipUnless(KARTE, 'braucht die Karte')
class SchossTest(SimpleTestCase):
    def test_6_schoss_zurueck_stiefel_bleibt(self):
        """Jacke oben weiß; im Beinteil links weiß (hängt am Weiß der Jacke: Schoß), rechts Hosenblau; darunter ein Stiefel für sich, unten außerhalb, oben im Beinteil, weiß.
        Zurück ans Oberteil geht nur der Schoß."""
        from meshgenesis_eigentrennung import Eigentrennung
        weiss, blau = [85.0, 2.0, 6.0], [27.0, 6.0, -15.0]
        p_j, f_j = _ebene(0.0, 0.5, 11)                                    # Jacke + Bein: x, y ∈ [−0,5, 0,5]
        p_j = p_j + torch.tensor([0.0, 0.5, 0.0], dtype=torch.float64, device='cuda')                   # stehend (y = Höhe): 0 … 1 m
        p_s, f_s = _ebene(0.0, 0.05, 3)                                     # Stiefel: 10 cm, weit unten
        p_s = p_s + torch.tensor([0.0, -0.3, 0.0], dtype=torch.float64, device='cuda')
        sp, sd = torch.cat([p_j, p_s]), torch.cat([f_j, f_s + len(p_j)])
        m = sp[sd].mean(1)
        jacke = torch.arange(len(sd), device='cuda') < len(f_j)
        bein = (jacke & (m[:, 1] < 0.5)) | (~jacke & (m[:, 1] > -0.3))
        lab = torch.tensor(blau, dtype=torch.float64, device='cuda').repeat(len(sd), 1)
        weiss_t = torch.tensor(weiss, dtype=torch.float64, device='cuda')
        lab[jacke & ((m[:, 1] >= 0.5) | (m[:, 0] < -0.25))] = weiss_t       # Schoß: ein Viertel des Beinteils — die Hosenfarbe (Median des Beinteils) bleibt blau
        lab[~jacke] = weiss_t
        schoss = Eigentrennung.schoss(sp, sd, bein, lab)
        self.assertTrue(bool(schoss[jacke & bein & (m[:, 0] < -0.35)].all()))
        self.assertFalse(bool(schoss[jacke & bein & (m[:, 0] > 0.1)].any()))
        self.assertFalse(bool(schoss[~jacke].any()))


@skipUnless(KARTE, 'braucht die Karte')
class RumpfkapselTest(SimpleTestCase):
    def test_5_kapsel_um_spine3(self):
        """Ein Rumpfknochen (Gruppe `rumpf`) mit 400 Punkten auf einem Zylinder von 12 cm bekommt eine Kapsel mit Halbmesser um 12 cm."""
        from KoerperKI_alle.koerperkollision import Koerperkollision
        w = torch.linspace(0, 6.283, 40, device='cuda').repeat(10)
        y = torch.linspace(1.11, 1.24, 10, device='cuda').repeat_interleave(40)
        ruhe = torch.stack([0.12 * torch.cos(w), y, 0.12 * torch.sin(w)], 1).double()
        kn = torch.zeros((400, 4), dtype=torch.int64, device='cuda')
        gw = torch.tensor([[1.0, 0.0, 0.0, 0.0]], device='cuda').expand(400, 4).double()
        kin = [{'name': 'spine3', 'gruppe': 'rumpf', 'zentrum': [0.0, 1.1, 0.0], 'ende': [0.0, 1.25, 0.0]}]
        kap = Koerperkollision.bauen(ruhe, kn, gw, kin)['kapseln']
        self.assertEqual([k['knochen'] for k in kap], ['spine3'])
        self.assertAlmostEqual(kap[0]['ra'], 0.12 + Koerperkollision.MARGE_M, delta=0.005)
