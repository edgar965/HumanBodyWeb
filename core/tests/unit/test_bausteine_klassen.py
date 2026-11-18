"""Bausteine (18.11.2026): Füllung ungesehener Texel, Inselbereinigung der Klassenkarten, Haarkappe unter
Strähnen — Kunstfälle auf der Karte, keine echten Netze. Nur auf Ansage laufen lassen.

  test_01 `Ungesehen.fuellen`: ein ungesehener Texel links nimmt die Klasse des gesehenen rechts am
          gespiegelten Ort, nicht die des näheren Nachbarn
  test_02 `Ungesehen.fuellen`: am Glied nimmt die Rückseite die Klasse derselben Höhe längs der Achse
  test_03 `Inseln.bereinigen`: ein kleiner Fleck verschwindet, ein langer schmaler Streifen bleibt,
          außerhalb der Insel kommt der Rand dazu
  test_04 `Haarkappe.aus_straehnen`: Kappenpunkte ohne Strähne binnen `DECKT_M` fallen weg, die Farbe
          ist die der nächsten Strähne × `DUNKEL`
"""
import sys
import unittest

import torch

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.append(_pfad)

KARTE = torch.cuda.is_available()
f64 = torch.float64


def _t(x, dtype=f64):
    return torch.tensor(x, dtype=dtype, device='cuda')


@unittest.skipUnless(KARTE, 'braucht CUDA')
class BausteineKlassenTest(unittest.TestCase):
    databases = []

    def test_01_links_rechts(self):
        """Gesehen: rechts bei x = +0,2 Klasse 2, links bei x = −0,15 Klasse 1; ungesehen links bei
        x = −0,2. Gespiegelt liegt +0,2 binnen `NAH_M` → Klasse 2. Sabotage: ohne Spiegel (nächster
        gesehener am eigenen Ort, 5 cm) → Klasse 1 → rot."""
        from bausteine.ungesehen import Ungesehen
        ruhe = _t([[0.2, 1.0, 0.0], [-0.15, 1.0, 0.0], [-0.2, 1.0, 0.0]])
        hat = _t([True, True, False], torch.bool)
        k = _t([2, 1, 0], torch.long)
        aus = Ungesehen.fuellen(ruhe, hat, k, ruhe, 0.0)
        self.assertEqual(int(aus[2]), 2)

    def test_02_ring(self):
        """Glied längs y (Achse von y = 1 nach y = 0, Knochen 0 ist Glied). Gesehen vorn (z = +0,05) bei
        y = 0,5 Klasse 1, seitlich (x = 0,64, z = 0) bei y = 0,52 Klasse 2 — im Raum näher an der
        Rückseite. Ungesehen hinten bei y = 0,5 (z = −0,05, fern der Spiegel): Ring → Klasse 1.
        Sabotage: `RING_M` = 1 m (der Winkel zählt voll) → Klasse 2 → rot."""
        from bausteine.ungesehen import Ungesehen
        ruhe = _t([[0.6, 0.5, 0.05], [0.64, 0.52, 0.0], [0.6, 0.5, -0.05]])
        hat = _t([True, True, False], torch.bool)
        k = _t([1, 2, 0], torch.long)
        achse = _t([[[0.6, 1.0, 0.0], [0.6, 0.0, 0.0]]])
        glied = (_t([0, 0, 0], torch.long), achse, _t([True], torch.bool))
        aus = Ungesehen.fuellen(ruhe, hat, k, ruhe, -5.0, glied)
        self.assertEqual(int(aus[2]), 1)

    def test_03_inseln(self):
        """64 × 64 Karte, Insel 40 × 40 in Klasse 0, darin ein Fleck 3 × 3 in Klasse 1 und ein Streifen
        1 × 36 in Klasse 2; je Texel 1 cm² → Grenze min(10, 1 % von 1600) = 10 cm²: der Fleck (9 cm²)
        wird Klasse 0, der Streifen (36 cm²) bleibt; außerhalb trägt der Rand Klasse 0 statt 1."""
        from bausteine.inseln import Inseln
        k = torch.ones((64, 64), dtype=torch.long, device='cuda')
        innen = torch.zeros((64, 64), dtype=torch.bool, device='cuda')
        innen[10:50, 10:50] = True
        k[10:50, 10:50] = 0
        k[20:23, 20:23] = 1
        k[12:48, 40] = 2
        aus = Inseln.bereinigen(k, innen, 1.0, log=lambda s: None)
        self.assertEqual(int(aus[21, 21]), 0)
        self.assertEqual(int(aus[30, 40]), 2)
        self.assertEqual(int(aus[30, 9]), 0)

    def test_04_kappe(self):
        """Strähnen bei x = 0; Kappenpunkte bei x = 0,01 (binnen `DECKT_M`) und x = 0,2 (nicht). Farbe
        der Strähne (200, 100, 50) → × `DUNKEL`."""
        from haar_Bart.haarkappe import Haarkappe
        haar = _t([[0.0, 1.6, 0.0], [0.0, 1.62, 0.0]])
        farbe = _t([[200, 100, 50], [200, 100, 50]], torch.uint8)
        unter, f = Haarkappe.aus_straehnen(_t([[0.01, 1.6, 0.0], [0.2, 1.6, 0.0]]), haar, farbe)
        self.assertEqual(unter.tolist(), [True, False])
        self.assertEqual(f[0].tolist(), [round(c * Haarkappe.DUNKEL) for c in (200, 100, 50)])


if __name__ == '__main__':
    unittest.main()
