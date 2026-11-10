"""Schritt „fotohaut“ (07.11.2026): Wann er rechnet und welche Fotos er nimmt, dazu das Glätten von `Netzband`.
    1  Job mit Fotos 0°, 45°, 90°, 180°, 270°, 315° und einem ohne Winkel: genau 90°, 180°, 270°
    2  Test ohne Job: nichts zu tun
    3  Job mit `pshuman.up2you`: nichts zu tun
    4  Job mit nur einem Foto: nichts zu tun
    5  `Netzband.feld`: Ein konstantes Feld bleibt konstant, auch mit Lücken im Gewicht (normierte Faltung)
Sabotage (von Hand): `VON` auf 0 setzen → Fall 1 rot; in `Netzband.feld` nicht durch z teilen → Fall 5 rot.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))
from meshgenesis_fotohaut import Meshgenesisfotohaut  # noqa: E402
from meshgenesis_netzband import Netzband  # noqa: E402


class TestFotos(unittest.TestCase):
    databases = []

    def setUp(self):
        self.ablage = tempfile.TemporaryDirectory(dir=settings.TOOLS_ROOT / 'ProjektTemp')
        self.addCleanup(self.ablage.cleanup)
        self.objekte = Path(self.ablage.name)
        self.test = self.objekte / 'meshgenesis' / '_test' / 'probe_mesh_genesis'
        self.test.mkdir(parents=True)

    def _job(self, winkel, **pshuman):
        ordner = self.objekte / 'fotogenesis' / 'Probe'
        ordner.mkdir(parents=True)
        fotos = []
        for i, w in enumerate(winkel):
            datei = ordner / ('%d.png' % i)
            datei.write_bytes(b'x')
            fotos.append({'datei': str(datei), 'winkel': w})
        (ordner / 'job.json').write_text(json.dumps({'fotos': fotos, 'meshgenesis_test': self.test.name, 'pshuman': pshuman}), encoding='utf-8')

    def test_nimmt_nur_fotos_von_der_seite_und_hinten(self):
        self._job([0, 45, 90, 180, 270, 315, None])
        wahl, _grund = Meshgenesisfotohaut.fotos(self.test)
        self.assertEqual([f['winkel'] for f in wahl], [90, 180, 270])

    def test_ohne_job_nichts(self):
        self.assertEqual(Meshgenesisfotohaut.fotos(self.test)[0], [])

    def test_up2you_nichts(self):
        self._job([0, 180], up2you=True)
        self.assertEqual(Meshgenesisfotohaut.fotos(self.test)[0], [])

    def test_ein_foto_nichts(self):
        self._job([0])
        self.assertEqual(Meshgenesisfotohaut.fotos(self.test)[0], [])


class TestNetzband(unittest.TestCase):
    databases = []

    def test_konstantes_feld_bleibt_konstant(self):
        ruhe = torch.tensor([[0.0, 0.0, 0.0], [0.01, 0.0, 0.0], [0.0, 0.01, 0.0], [0.01, 0.01, 0.0]])
        netz = SimpleNamespace(ruhe=ruhe, dreiecke=torch.tensor([[0, 1, 2], [1, 3, 2]]))
        haut = SimpleNamespace(ecken=torch.tensor([[0, 1, 2], [1, 3, 2]]), bary=torch.tensor([[1 / 3] * 3] * 2, dtype=torch.float64))
        band = Netzband(netz, haut)
        idx = torch.tensor([0, 1])
        feld = band.feld(idx, torch.full((2, 1), 0.7), torch.tensor([1.0, 0.0]), 0.02)
        self.assertLess(float((feld - 0.7).abs().max()), 1e-5)
