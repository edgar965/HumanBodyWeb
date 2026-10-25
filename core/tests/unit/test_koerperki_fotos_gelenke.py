# -*- coding: utf-8 -*-
"""Tests für die Gelenke aus den Fotos (24.10.2026, 2d-3d-AI): `Posenpunkte` (ViTPose → Gelenke der Körperlage), `Fotogelenke` (Quelle nach Einstellung) und `Ai2d3dposewahl.aus`.

WARUM: Edgar, 24.10.2026: „wenn du meinst, ViTPose ist besser, kannst du das auch ausprobieren, ggf. optional? … damit man das später beides ausprobieren kann“. Beide Quellen müssen dasselbe
liefern — {Gelenk: (xy, Gewicht)} mit „_l“ = linke Körperseite der Person —, sonst passt das Einpassen je nach Einstellung spiegelverkehrt ein. ViTPose und SAM 3D Body laufen hier nicht:
an ihrer Stelle stehen Attrappen mit der Signatur der Originale (`Vppunkte.punkte`, `Posebestimmung` über `autospec`).
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import torch
from django.conf import settings
from PIL import Image

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.fotogelenke import Fotogelenke  # noqa: E402
from KoerperKI_Fotos.posenpunkte import Posenpunkte  # noqa: E402
from VitposeTorch.punkte import Vppunkte  # noqa: E402

from core.dienste.ai2d3dposewahl import Ai2d3dposewahl  # noqa: E402
from core.dienste.engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke  # noqa: E402


class VitposeAttrappe:
    """Wie `Vppunkte`: `punkte(rgb, kasten)` → (133, 2) Bildpunkte und (133,) Zuversicht, `index(name)` — ohne Gewichte. Punkt i liegt bei (2i, 2i + 1)."""

    def __init__(self, geraet='cpu', wert=None):
        self.wert = torch.full((133,), 0.9) if wert is None else wert
        self.kaesten = []

    def punkte(self, rgb, kasten):
        self.kaesten.append(tuple(kasten))
        return torch.arange(266).float().reshape(133, 2), self.wert

    def index(self, name):
        return Vppunkte.index(name)


class DiePosenpunkte(unittest.TestCase):
    def test_gewicht_ist_zuversicht_mal_faktor_und_schwache_fallen_weg(self):
        wert = torch.full((133,), 0.9)
        wert[Vppunkte.index('knie_l')] = 0.2
        g = Posenpunkte(VitposeAttrappe(wert=wert)).aus_foto(np.zeros((8, 8, 3), np.uint8), (0, 0, 7, 7))
        self.assertNotIn('knie_l', g)
        self.assertEqual(len(g), 11)
        self.assertAlmostEqual(g['schulter_l'][1], 0.45)
        self.assertAlmostEqual(g['huefte_r'][1], 0.45)
        self.assertAlmostEqual(g['ellbogen_r'][1], 0.9)
        i = Vppunkte.index('knie_r')
        self.assertEqual(g['knie_r'][0].tolist(), [2.0 * i, 2.0 * i + 1])

    def test_jedes_gelenk_hat_einen_vitpose_punkt_derselben_seite(self):
        for gelenk, _knochen, punkt, _f in Posenpunkte.GELENKE:
            self.assertIn(punkt, Vppunkte.NAMEN.values())
            self.assertEqual(gelenk[-2:], punkt[-2:])

    def test_knochen_der_gleichen_seite(self):
        for gelenk, knochen, _p, _f in Posenpunkte.GELENKE:
            self.assertEqual(knochen[:2], gelenk[-1] + '_', (gelenk, knochen))


class DieFotogelenke(unittest.TestCase):
    def setUp(self):
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'tests'
        wurzel.mkdir(parents=True, exist_ok=True)
        self.ordner = Path(tempfile.mkdtemp(prefix='fotogelenke_', dir=wurzel))
        self.person = torch.zeros((50, 30), dtype=torch.bool)
        self.person[10:41, 5:21] = True
        self.rgb = torch.full((50, 30, 3), 128, dtype=torch.uint8)

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def test_mhr_namen_gibt_es_und_seiten_stimmen(self):
        self.assertEqual(sorted(Fotogelenke.MHR), sorted(g for g, _k, _p, _f in Posenpunkte.GELENKE))
        self.assertEqual(sorted(Fotogelenke.MHR.values()), sorted(Engine2d3dKleiderposegelenke.HAUPT))
        for gelenk, mhr in Fotogelenke.MHR.items():
            self.assertEqual(gelenk.endswith('_l'), mhr.startswith('left-'), gelenk)

    def test_vitpose_mit_kasten_der_personenmaske(self):
        attrappe = VitposeAttrappe()
        with mock.patch('VitposeTorch.punkte.Vppunkte', return_value=attrappe):
            g = Fotogelenke('vitpose').holen({'a.jpg': self.rgb}, {'a.jpg': {'person': self.person}}, self.ordner, log=lambda *_: None)
        self.assertEqual(attrappe.kaesten, [(5, 10, 20, 40)])
        self.assertEqual(sorted(g), ['a.jpg'])
        self.assertEqual(len(g['a.jpg']), 12)

    def _sam(self, k2, namen):
        return {'namen': namen, 'drehungen': {'0': {'k2': k2}}}

    def test_sam3dbody_bildpunkte_nach_namen_gewicht_faktor(self):
        namen = ['nose'] + list(reversed(Engine2d3dKleiderposegelenke.HAUPT))
        k2 = [[float(i), 100.0 + i] for i in range(len(namen))]
        k2[namen.index('left-knee')] = [float('nan'), float('nan')]
        with mock.patch('core.dienste.posebestimmung.Posebestimmung', autospec=True) as pb:
            pb.return_value.sam.return_value = (self._sam(k2, namen), True)
            g = Fotogelenke('sam3dbody').holen({'a.jpg': self.rgb}, {'a.jpg': {'person': self.person}}, self.ordner, log=lambda *_: None)['a.jpg']
        ziel = self.ordner / 'sam3d_a'
        self.assertEqual(pb.call_args.args[0], ziel)
        self.assertEqual(pb.return_value.sam.call_args.kwargs, {'drehungen': (0,)})
        self.assertNotIn('knie_l', g)
        self.assertEqual(len(g), 11)
        i = namen.index('left-shoulder')
        self.assertEqual(g['schulter_l'][0].tolist(), [float(i), 100.0 + i])
        self.assertEqual(g['schulter_l'][1], 0.5)
        self.assertEqual(g['knoechel_r'][1], 1.0)
        rgba = np.asarray(Image.open(ziel / 'eingabe.png'))
        self.assertEqual(rgba.shape, (50, 30, 4))
        self.assertTrue(np.array_equal(rgba[..., 3] > 0, self.person.numpy()))

    def test_sam3dbody_gleiches_bild_nicht_neu_geschrieben(self):
        namen = list(Engine2d3dKleiderposegelenke.HAUPT)
        with mock.patch('core.dienste.posebestimmung.Posebestimmung', autospec=True) as pb:
            pb.return_value.sam.return_value = (self._sam([[1.0, 2.0]] * 12, namen), False)
            fg = Fotogelenke('sam3dbody')
            fg.holen({'a.jpg': self.rgb}, {'a.jpg': {'person': self.person}}, self.ordner, log=lambda *_: None)
            png = self.ordner / 'sam3d_a' / 'eingabe.png'
            vorher = png.stat().st_mtime_ns
            fg.holen({'a.jpg': self.rgb}, {'a.jpg': {'person': self.person}}, self.ordner, log=lambda *_: None)
        self.assertEqual(png.stat().st_mtime_ns, vorher)

    def test_sam3dbody_ohne_ergebnis_meldet_das_foto(self):
        with mock.patch('core.dienste.posebestimmung.Posebestimmung', autospec=True) as pb:
            pb.return_value.sam.return_value = ({'namen': [], 'drehungen': {'0': {'fehler': 'keine Person'}}}, True)
            with self.assertRaisesRegex(RuntimeError, 'a.jpg.*keine Person'):
                Fotogelenke('sam3dbody').holen({'a.jpg': self.rgb}, {'a.jpg': {'person': self.person}}, self.ordner, log=lambda *_: None)


class DiePosewahl(unittest.TestCase):
    def test_vorgabe_bei_fehlendem_oder_unbekanntem_wert(self):
        self.assertEqual(Ai2d3dposewahl.aus(None), 'vitpose')
        self.assertEqual(Ai2d3dposewahl.aus({}), 'vitpose')
        self.assertEqual(Ai2d3dposewahl.aus({Ai2d3dposewahl.SCHLUESSEL: 'sapiens'}), 'vitpose')

    def test_gespeicherter_wert_ohne_leerraum(self):
        self.assertEqual(Ai2d3dposewahl.aus({Ai2d3dposewahl.SCHLUESSEL: ' sam3dbody '}), 'sam3dbody')

    def test_jeder_wert_hat_text_beschreibung_und_einen_weg(self):
        """Ein neuer Wert braucht eine Beschreibung für die Seite und einen eigenen Zweig in `Fotogelenke.holen` (sonst nähme er stumm ViTPose)."""
        werte = [w for w, _t in Ai2d3dposewahl.WERTE]
        self.assertEqual(sorted(werte), ['sam3dbody', 'vitpose'])
        self.assertEqual(sorted(Ai2d3dposewahl.BESCHREIBUNG), sorted(werte))
        self.assertIn(Ai2d3dposewahl.VORGABE, werte)
        self.assertEqual(Ai2d3dposewahl.text('vitpose'), dict(Ai2d3dposewahl.WERTE)['vitpose'])
