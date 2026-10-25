# -*- coding: utf-8 -*-
"""Haut der KI und Bilderkennung im Prozess (24.10.2026, Edgar: „Verbessere noch die Haut KI“ und „die andere Session hat sapiens2 und Sam3 auf python14 gehoben, checke nach und merge“).

    1  `Kostuemhautzeichnung`: der Eingang selbst als KI → Zeichnung 1, Wolken 0 (grün)
    2  ein konstanter Hautton → Zeichnung 0, also rot, wo der Eingang Zeichnung hat; Wolken 0
    3  der Eingang mit aufgelegten Wolken (4 L*, σ 12 Texel) → Wolken rot, Zeichnung grün
    4  ein Eingang ohne Zeichnung (glatt) → „Zeichnung“ wird nicht geprüft
    5  `Sam3port` nimmt die Ersatzmodule (`timm`, `torchvision` ohne `__spec__`) aus `sys.modules`, echte Module bleiben
    6  `Kostuemerkennung` liest die Segmentierung aus `kostuem/segmentierung.json` → `ordner`, wenn kein Mesh-3D-Lauf genannt ist
Die Maße an edgar (Lauf `…04.19_hautwechsel`: Zeichnung 0,08–0,18, Wolken 2,5–2,7) misst `ProjektTemp/_wegwerf/haut_ki/masse.py`; die Bitgleichheit der Ports `…/dienst/bilderkennung/gegenprobe_ports.py`.
Sabotage-Gegenprobe (von Hand): in `_zerlegen` den Rest ohne Abzug der Projektion (`b` statt `b - beta * a`) → Fall 2 meldet Wolken; `FEIN_MIN = 0` → Fall 4 rot; in `Sam3port.__init__`
die Schleife über `ERSATZ` streichen → Fall 5 rot.
"""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


@unittest.skipUnless(_cuda(), 'keine CUDA')
class HautzeichnungTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mesh3dai_kostuem_hautzeichnung import Kostuemhautzeichnung
        cls.K = Kostuemhautzeichnung
        z = np.random.default_rng(3)
        h = 256
        grund = np.array([210.0, 160.0, 135.0])
        fein = z.normal(0, 14, (h, h))                         # Zeichnung: Haare/Poren
        cls.eingang = np.clip(grund + fein[..., None], 0, 255)
        cls.maske = np.zeros((h, h), bool)
        cls.maske[20:236, 20:236] = True

    def _messen(self, ki, eingang=None):
        e = self.eingang if eingang is None else eingang
        hz = self.K({1002: (e, ki, self.maske)})
        a = hz.messen()[1002]
        return hz, a

    def test_1_eingang_selbst(self):
        hz, a = self._messen(self.eingang)
        self.assertAlmostEqual(a['zeichnung'], 1.0, places=3)
        self.assertLess(a['wolken_L'], 1e-6)
        self.assertFalse(hz.zu_glatt(a) or hz.zu_wolkig(a))

    def test_2_konstanter_ton(self):
        hz, a = self._messen(np.full_like(self.eingang, 200.0))
        self.assertTrue(a['zeichnung_geprueft'])
        self.assertTrue(hz.zu_glatt(a))
        self.assertFalse(hz.zu_wolkig(a))

    def test_3_wolken(self):
        from scipy.ndimage import gaussian_filter
        z = np.random.default_rng(4)
        wolken = gaussian_filter(z.normal(0, 1, self.eingang.shape[:2]), 12)
        wolken = wolken / wolken.std() * 10.0                 # ~4 L* in der Helligkeit
        hz, a = self._messen(np.clip(self.eingang + wolken[..., None], 0, 255))
        self.assertTrue(hz.zu_wolkig(a), a)
        self.assertFalse(hz.zu_glatt(a), a)

    def test_4_glatter_eingang(self):
        glatt = np.full_like(self.eingang, 205.0)
        hz, a = self._messen(np.full_like(self.eingang, 200.0), eingang=glatt)
        self.assertFalse(a['zeichnung_geprueft'])
        self.assertFalse(hz.zu_glatt(a))


class Sam3portErsatzTest(unittest.TestCase):
    def test_5_ersatz_raus_echte_bleiben(self):
        import mesh3dai_sam3port
        ersatz = types.ModuleType('torchvision')                # ohne __spec__ wie `S3attrappen._modul`
        echt = types.ModuleType('timm')
        echt.__spec__ = SimpleNamespace(name='timm')
        attrappe = SimpleNamespace(fehlend=[])
        begriffe = types.ModuleType('Sam3Torch.begriffe')
        begriffe.S3begriffe = lambda geraet='cuda': attrappe
        with mock.patch.dict(sys.modules, {'torchvision': ersatz, 'timm': echt, 'Sam3Torch': types.ModuleType('Sam3Torch'), 'Sam3Torch.begriffe': begriffe}):
            mesh3dai_sam3port.Sam3port()
            self.assertNotIn('torchvision', sys.modules)
            self.assertIs(sys.modules['timm'], echt)


class SegmentierungsordnerTest(unittest.TestCase):
    def test_6_ordner_aus_dem_vermerk(self):
        from mesh3dai_kostuem_erkennen import Kostuemerkennung
        with tempfile.TemporaryDirectory(dir=str(settings.TOOLS_ROOT / 'ProjektTemp')) as d:
            test = Path(d)
            (test / 'kostuem').mkdir()
            seg = test / 'kostuem' / 'segmentierung'
            (test / 'kostuem' / 'segmentierung.json').write_text(json.dumps({'mesh3d': None, 'ordner': str(seg)}), encoding='utf-8')
            with mock.patch('mesh3dai_kostuem_erkennen.Kostuemgpu.an', return_value=SimpleNamespace()):
                e = Kostuemerkennung(test, SimpleNamespace(info={}), None)
            self.assertEqual(e.seg, seg)


if __name__ == '__main__':
    unittest.main()
