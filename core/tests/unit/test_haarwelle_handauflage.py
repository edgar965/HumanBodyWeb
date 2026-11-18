"""Welligkeit des Haars (`Haarwelle`, Schalter `Fotogenesispshuman.haar_welle`), Wahl der Kategorie (`Haarengine.wahl`) und Stab in der
Faust (`Stabfaust`, gedreht statt geschoben) — 16.11.2026, Edgar zur Goldprinzessin: „3: mach b,c,d“, „4. Fixe“, „mach auch …“.

Kunstdaten, keine echten Netze, kleine Tensoren auf der Karte (ohne Karte übersprungen). Schreibt nichts.

Sabotage, je Fall rot:
  - in `Haarwelle.entscheiden` `form and band` durch `form or band` → test_2 (uneins → wellig).
  - in `Haarengine.wahl` die Zeile `if stufe != 'kurz' and wellig is not None` streichen → test_3 (lang bleibt glatt).
  - in `Fotogenesispshuman.setzen` die Prüfung von `haar_welle` streichen → test_4 (kein ValueError).
  - in `Stabfaust.ausrichten` `dreh + (w - dreh) @ r.T` durch `w + (ziel - cl)` → test_6 (Kopf wandert mit).

Geschrieben am 16.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
import sys
from pathlib import Path
from unittest import mock, skipUnless

import torch
from django.conf import settings
from django.test import SimpleTestCase

MESHGENESIS = str(Path(settings.TOOLS_ROOT) / 'meshgenesis')
if MESHGENESIS not in sys.path:
    sys.path.insert(0, MESHGENESIS)

KARTE = torch.cuda.is_available()


class HaarwelleTest(SimpleTestCase):
    def test_1_schalter_entscheidet(self):
        from haar_Bart.haarwelle import Haarwelle
        self.assertEqual(Haarwelle.entscheiden(None, 'wellig')[0], True)
        self.assertEqual(Haarwelle.entscheiden({'form': 9.0, 'baender': 9.0}, 'glatt')[0], False)
        self.assertIsNone(Haarwelle.entscheiden(None, 'auto')[0])

    def test_2_beide_messungen_muessen_wellig_sagen(self):
        from haar_Bart.haarwelle import Haarwelle
        f, b = Haarwelle.FORM, Haarwelle.BAENDER
        self.assertTrue(Haarwelle.entscheiden({'form': f + 0.1, 'baender': b + 0.1})[0])
        self.assertFalse(Haarwelle.entscheiden({'form': f + 0.1, 'baender': b - 0.1})[0])
        self.assertFalse(Haarwelle.entscheiden({'form': f - 0.1, 'baender': b - 0.1})[0])

    def test_3_wahl_lang_wellig_nur_mit_messung(self):
        from haar_Bart.haar_engine import Haarengine
        masse = {'hat_haar': 1.0, 'laenge': 2.3, 'volumen': 0.5}
        with mock.patch.object(Haarengine, 'kennwerte', return_value=({}, [])):
            self.assertEqual(Haarengine.wahl(masse, None, True), 'lang_wellig')
            self.assertEqual(Haarengine.wahl(masse, None, False), 'lang_glatt')
            self.assertEqual(Haarengine.wahl(masse, None, None), 'lang_glatt')
            self.assertEqual(Haarengine.wahl(dict(masse, volumen=1.5), None, False), 'lang_dicht')
            self.assertEqual(Haarengine.wahl(dict(masse, laenge=0.3), None, True), 'kurz_glatt')       # kurzes Haar misst Haarwelle nicht

    def test_4_schalter_am_job(self):
        from core.dienste.fotogenesispshuman import Fotogenesispshuman
        self.assertEqual(Fotogenesispshuman.lesen({})['haar_welle'], 'auto')
        self.assertEqual(Fotogenesispshuman.lesen({'pshuman': {'haar_welle': 'wellig'}})['haar_welle'], 'wellig')
        self.assertEqual(Fotogenesispshuman.lesen({'pshuman': {'haar_welle': 'kraus'}})['haar_welle'], 'auto')
        with self.assertRaises(ValueError):
            Fotogenesispshuman.setzen({'art': 'foto', 'ordner': Path('gibt_es_nicht')}, {'haar_welle': 'kraus'})


@skipUnless(KARTE, 'ohne Karte')
class LockeFeinTest(SimpleTestCase):
    def test_7_leitstraehne_feiner(self):
        # 16.11.2026, Edgar: „Du machst ganz kurze Stücke, die einfach in dem Raum hängen“ — die Schraube braucht Punkte je Windung (`Haarstraehnen.FEIN`)
        # Sabotage: in `_feiner` `(k1 - 1) * faktor + 1` durch `k1 * faktor` → Endpunkt verschoben, rot
        from haar_Bart.haarstraehnen import Haarstraehnen
        gs = torch.stack([torch.zeros(17, dtype=torch.float64, device='cuda'), -torch.linspace(0, 0.48, 17, dtype=torch.float64, device='cuda'),
                          torch.zeros(17, dtype=torch.float64, device='cuda')], 1)[None].repeat(3, 1, 1)
        gn = torch.tensor([0.0, 0.0, 1.0], dtype=torch.float64, device='cuda').expand(3, 17, 3).contiguous()
        aus = Haarstraehnen._feiner({'spur': gs, 'normale': gn, 'auf': torch.tensor([10.0, 16.0, 0.0], dtype=torch.float64, device='cuda'), 'laenge_mm': [1, 2]}, 2)
        self.assertEqual(tuple(aus['spur'].shape), (3, 33, 3))
        self.assertTrue(torch.allclose(aus['spur'][:, ::2], gs))                  # alte Punkte bleiben
        self.assertTrue(torch.allclose(aus['spur'][:, 1, 1], torch.full((3,), -0.015, dtype=torch.float64, device='cuda')))   # Mitte dazwischen
        self.assertTrue(torch.allclose(aus['normale'].norm(dim=2), torch.ones((3, 33), dtype=torch.float64, device='cuda')))
        self.assertEqual(aus['auf'].tolist(), [20.0, 32.0, 0.0])
        self.assertEqual(aus['laenge_mm'], [1, 2])


@skipUnless(KARTE, 'ohne Karte')
class SaumStabTest(SimpleTestCase):
    def test_6_stab_dreht_um_das_ferne_ende(self):
        from meshgenesis_stabfaust import Stabfaust
        # Stab längs y von 0 bis 0,5 m, Dicke 2 cm; die Faust liegt 2 cm neben dem unteren Ende → gedreht um das obere Ende, das bleibt
        y = torch.linspace(0.0, 0.5, 400, dtype=torch.float64, device='cuda')
        phi = torch.arange(8, dtype=torch.float64, device='cuda') * (torch.pi / 4)
        w = torch.cat([torch.stack([0.01 * torch.cos(f).expand_as(y), y, 0.01 * torch.sin(f).expand_as(y)], 1) for f in phi])         # Ringe um die y-Achse
        hoehle = (torch.tensor([0.02, 0.05, 0.0], dtype=torch.float64, device='cuda'), torch.tensor([0.0, 1.0, 0.0], dtype=torch.float64, device='cuda'))
        with mock.patch.object(Stabfaust, 'hoehle', side_effect=lambda q, s: hoehle if s == 'r' else None):
            neu, bericht = Stabfaust.ausrichten(w, None)
        self.assertTrue(bericht['verschoben'])
        self.assertIsNotNone(bericht['gedreht_grad'])
        oben = w[:, 1] > 0.49
        self.assertLess(float((neu[oben] - w[oben]).norm(dim=1).max()), 0.002)
        unten = (w[:, 1] - 0.05).abs() < 0.02
        self.assertLess(abs(float(neu[unten, 0].mean()) - 0.02), 0.004)
