# -*- coding: utf-8 -*-
"""Tests für die Kamera von `KoerperKI_Fotos.fotoeinpassung.Fotoeinpassung` (24.10.2026, 2d-3d-AI): Drehung, Bild, Profilseite, Startkamera.

WARUM: Bild = s · (x′, −y′) + t mit x′ = R_x(φ) · R_y(w + δ) · x muss dieselbe Kamera sein wie in `Koerperlage` (Profil 90° = linke Seite zur Kamera), sonst passt das Einpassen die
Gegenseite ein. Das Einpassen eines Kunstkörpers (über 1 s) steht in `longrunner/test_koerperki_fotos_einpassen.py`.
Perspektive (24.10.2026, Edgar: „mach B“): die Lochkamera muss für große Brennweite in die orthografische übergehen, die Startkamera dieselbe sein wie die eingepasste, und der Kameraort
(Probe gegen eine unabhängige Größe) über dem Drehpunkt liegen, wenn sie nach unten schaut. Das perspektivische Einpassen: `longrunner/test_koerperki_fotos_perspektive.py`.
"""
import math
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.fotobrennweite import Fotobrennweite  # noqa: E402
from KoerperKI_Fotos.fotoeinpassung import Fotoeinpassung  # noqa: E402
from KoerperKI_Fotos.koerperlage import Koerperlage  # noqa: E402

from ._einpasskoerper import Einpasskoerper  # noqa: E402


class DieKamera(unittest.TestCase):
    def test_profil_90_sieht_die_linke_seite_wie_der_kopf(self):
        """90° („links“): Kamera bei +X, die linke Körperseite (+x) zeigt zur Kamera (z′ > 0), der Blick der Figur (+z) geht im Bild nach LINKS — dieselbe Drehung wie die Kopflage der
        KopfKI (`Kopflagen.drehung_profil`, deren Lagen an den Fotos geprüft sind). Bis 24.10.2026 abends stand hier das Gegenteil (Kamera bei −X): im perspektivischen Lauf lag der ferne Fuß
        unter dem Bild, die Profile waren gespiegelt (`ProjektTemp/_wegwerf/ai2d3d/profilseite_probe.py`)."""
        from KopfKI.kopflagen import Kopflagen
        r = Fotoeinpassung._dreh(torch.tensor(math.pi / 2), torch.tensor(0.0))
        self.assertTrue(torch.allclose(r @ torch.tensor([1.0, 0, 0]), torch.tensor([0.0, 0, 1]), atol=1e-6))
        self.assertTrue(torch.allclose(r @ torch.tensor([0.0, 0, 1]), torch.tensor([-1.0, 0, 0]), atol=1e-6))
        for grad, richtung in ((90, 'links'), (270, 'rechts')):
            kopf = Kopflagen.drehung_profil(torch.eye(2), richtung, 'cpu')
            self.assertTrue(torch.allclose(Fotoeinpassung._dreh(torch.tensor(math.radians(grad)), torch.tensor(0.0)), kopf, atol=1e-5), richtung)

    def test_drehung_wie_koerperlage(self):
        n = Fotoeinpassung._dreh(torch.tensor(0.0), torch.tensor(0.3))
        self.assertTrue(torch.allclose(n @ torch.tensor([0.0, 1, 0]), torch.tensor([0.0, math.cos(0.3), math.sin(0.3)]), atol=1e-6))
        q = Fotoeinpassung._dreh(torch.tensor(1.1), torch.tensor(-0.4))
        self.assertTrue(torch.allclose(q @ q.T, torch.eye(3), atol=1e-6))
        self.assertAlmostEqual(float(torch.det(q)), 1.0, places=5)
        self.assertTrue(torch.allclose(Fotoeinpassung._dreh(torch.tensor(1.1), torch.tensor(0.0)), Koerperlage.r_y(torch.tensor(1.1)), atol=1e-6))

    def test_erst_ansicht_dann_nicken(self):
        """x′ = R_x(φ) · R_y(−w) · x: die Ansicht dreht den Körper, das Nicken die Kamera — im Profil (90°) kippt das Nicken die Tiefe, nicht die Breite."""
        r = Fotoeinpassung._dreh(torch.tensor(math.pi / 2), torch.tensor(0.3))
        self.assertTrue(torch.allclose(r @ torch.tensor([1.0, 0, 0]), torch.tensor([0.0, -math.sin(0.3), math.cos(0.3)]), atol=1e-6))

    def test_bild_y_nach_unten(self):
        uv = Fotoeinpassung.bild(torch.tensor([[1.0, 2.0, 3.0]]), torch.eye(3), 10.0, torch.tensor([5.0, 7.0]))
        self.assertEqual(uv.tolist(), [[15.0, -13.0]])

    def test_im_profil_nur_die_seite_zur_kamera(self):
        n = Fotoeinpassung._nahe_seite
        self.assertEqual((n(90, 'knie_l'), n(90, 'knie_r')), (True, False))
        self.assertEqual((n(270, 'knie_l'), n(270, 'knie_r')), (False, True))
        self.assertEqual((n(100, 'knie_l'), n(450, 'knie_r')), (True, False))
        for w in (0, 180, 45):
            self.assertEqual((n(w, 'knie_l'), n(w, 'knie_r')), (True, True), w)

    def test_perspektive_ist_die_lochkamera(self):
        """Kamera im Abstand Z = f / s vor dem Drehpunkt: Bild = f · (x′, −y′) / (Z − z′) + t — ein Punkt 0,5 m näher an der Kamera wird größer abgebildet (EdgarTrip: Kopf näher als Füße)."""
        f, s, mitte = 1000.0, 500.0, torch.tensor([0.0, 1.0, 0.0])           # Z = 2 m
        x = torch.tensor([[0.1, 1.2, 0.0], [0.1, 1.2, 0.5]])
        uv = Fotoeinpassung.bild(x, torch.eye(3), s, torch.tensor([5.0, 7.0]), f, mitte)
        self.assertTrue(torch.allclose(uv, torch.tensor([[5 + 1000 * 0.1 / 2, 7 - 1000 * 0.2 / 2], [5 + 1000 * 0.1 / 1.5, 7 - 1000 * 0.2 / 1.5]]), atol=1e-3))

    def test_perspektive_mit_grosser_brennweite_wird_orthografisch(self):
        x = torch.tensor([[0.3, -0.7, 0.2], [-0.1, 0.4, -0.25]])
        r = Fotoeinpassung._dreh(torch.tensor(0.7), torch.tensor(0.2))
        ortho = Fotoeinpassung.bild(x, r, 80.0, torch.tensor([1.0, 2.0]))
        fern = Fotoeinpassung.bild(x, r, 80.0, torch.tensor([1.0, 2.0]), 1e9, torch.zeros(3))
        self.assertTrue(torch.allclose(ortho, fern, atol=1e-3))

    def test_kameraort_ueber_dem_drehpunkt_wenn_sie_nach_unten_schaut(self):
        """φ > 0: die Kamera steht über dem Drehpunkt (z′ zeigt zur Kamera, oben ist näher) — Höhe = Mitte + Z · sin φ."""
        r = Fotoeinpassung._dreh(torch.tensor(0.0), torch.tensor(0.3))
        ort = Fotoeinpassung.ort((r, 500.0, torch.zeros(2), 1000.0, torch.tensor([0.0, 0.9, 0.0])))
        self.assertAlmostEqual(ort['abstand_m'], 2.0, places=3)
        self.assertAlmostEqual(ort['hoehe_m'], 0.9 + 2.0 * math.sin(0.3), places=3)
        self.assertEqual(Fotoeinpassung.ort((r, 500.0, torch.zeros(2))), {})

    def test_perspektivische_startkamera_gleich_kamera_aus(self):
        a = {'name': 'a', 'winkel': 0, 'ziel': None, 'gelenke': {}, 's': 300.0, 't': np.array([30.0, 40.0], np.float32), 's_fest': False, 'delta': 0.02, 'nick': 0.1, 'f': 4290.0}
        mitte = torch.tensor([0.0, 0.925, 0.0])
        e = Fotoeinpassung(Einpasskoerper(), [a], mitte=mitte)
        e._kameras()
        ist, soll = e.kamera(0), Fotoeinpassung.kamera_aus(a, 'cpu', mitte)
        self.assertEqual((len(ist), len(soll)), (5, 5))
        x = torch.tensor([[0.2, 1.7, 0.1], [0.1, 0.05, 0.0]])
        self.assertTrue(torch.allclose(Fotoeinpassung.bild(x, *ist), Fotoeinpassung.bild(x, *soll), atol=1e-3))

    def test_pruefprojektion_bildet_ab_wie_die_einpassung(self):
        """Die Deckung der gebauten Figur misst `Koerperprojektion` — sie muss dieselbe Kamera rechnen wie die Einpassung, sonst prüft die Runde etwas anderes, als eingepasst wurde."""
        from KoerperKI_Fotos.koerperprojektion import Koerperprojektion
        ecken = torch.tensor([[-0.3, 0.6, 0.4], [0.3, 0.6, 0.4], [0.3, 1.4, 0.4], [-0.3, 1.4, 0.4], [0.0, 1.0, -0.3]])
        dreiecke = torch.tensor([[0, 1, 2], [0, 2, 3], [0, 1, 4]])
        kam = (Fotoeinpassung._dreh(torch.tensor(0.2), torch.tensor(0.25)), 150.0, torch.tensor([120.0, 160.0]), 300.0, torch.tensor([0.0, 0.9, 0.0]))
        pr = Koerperprojektion(ecken, dreiecke, kam, torch.zeros((320, 240, 3), dtype=torch.uint8))
        self.assertTrue(torch.allclose(pr.abbilden(ecken), Fotoeinpassung.bild(ecken, *kam), atol=1e-3))
        xy, _sicht, _cos = pr.sehen(ecken, torch.zeros_like(ecken))
        self.assertTrue(torch.allclose(xy, Fotoeinpassung.bild(ecken, *kam), atol=1e-3))
        x0, y0, x1, y1 = pr.kasten
        uv = Fotoeinpassung.bild(ecken, *kam)
        self.assertLessEqual(abs(x0 + pr.RAND_PX - int(uv[:, 0].min())), 1)
        self.assertLessEqual(abs(y1 - pr.RAND_PX - int(uv[:, 1].max())), 1)
        self.assertGreater(int(pr.bedeckt.sum()), 100)

    def test_aufnahmegroesse_aus_dem_xmp(self):
        """Ausschnitt: die Brennweite gilt für die ganze Aufnahme — iOS schreibt deren Größe ins XMP (EdgarTrip 1.jpg: 5712 × 4284 bei 1894 × 4406)."""
        xmp = b'<mwg-rs:AppliedToDimensions stDim:h="4284" stDim:w="5712" stDim:unit="pixel"/>'
        self.assertEqual(Fotobrennweite.aufnahme(xmp), (5712, 4284))
        self.assertIsNone(Fotobrennweite.aufnahme(b''))
        self.assertAlmostEqual(26 * math.hypot(5712, 4284) / Fotobrennweite.KB_DIAGONALE_MM, 4290.3, places=1)

    def test_startkamera_gleich_kamera_aus(self):
        a = {'name': 'a', 'winkel': 90, 'ziel': None, 'gelenke': {}, 's': 120.0, 't': np.array([30.0, 40.0], np.float32), 's_fest': True, 'delta': 0.05, 'nick': -0.1}
        e = Fotoeinpassung(Einpasskoerper(), [a])
        e._kameras()
        for ist, soll in zip(e.kamera(0), Fotoeinpassung.kamera_aus(a, 'cpu'), strict=True):
            self.assertTrue(torch.allclose(torch.as_tensor(ist), torch.as_tensor(soll), atol=1e-5))
