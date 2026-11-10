"""`Kostuemohnekleider`: Nur ein ausdrückliches `true` wirkt, alles außer Haar wird Haut. Ohne Karte."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import torch

sys.path.insert(0, r'A:\3DTools\meshgenesis')

from meshgenesis_kostuem_ohnekleider import Kostuemohnekleider  # noqa: E402
from meshgenesis_kostuemarten import Kostuemarten  # noqa: E402


class KostuemohnekleiderTest(unittest.TestCase):
    databases = []

    def _test(self, job=None, einstellung=None, name='n2-mesh-genesis'):
        """Ablage wie `3DObjects`: Test `t` unter `meshgenesis/_test/`, Job `n2` unter `fotogenesis/`."""
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        test = wurzel / 'meshgenesis' / '_test' / 't'
        test.mkdir(parents=True)
        (test / 'anlage.json').write_text(json.dumps({'name': name}), encoding='utf-8')
        if einstellung is not None:
            (test / 'einstellung.json').write_text(json.dumps(einstellung), encoding='utf-8')
        if job is not None:
            (wurzel / 'fotogenesis' / 'n2').mkdir(parents=True)
            (wurzel / 'fotogenesis' / 'n2' / 'job.json').write_text(json.dumps(job), encoding='utf-8')
        return test

    def test_nur_true_wirkt(self):
        self.assertTrue(Kostuemohnekleider.gewuenscht(self._test({'pshuman': {'keine_kleider': True}})))
        self.assertFalse(Kostuemohnekleider.gewuenscht(self._test({'pshuman': {'keine_kleider': False}})))
        self.assertFalse(Kostuemohnekleider.gewuenscht(self._test({'pshuman': {}})))
        self.assertFalse(Kostuemohnekleider.gewuenscht(self._test()))

    def test_job_vor_einstellung(self):
        test = self._test({'pshuman': {'keine_kleider': False}}, {'keine_kleider': True})
        self.assertFalse(Kostuemohnekleider.gewuenscht(test))
        self.assertTrue(Kostuemohnekleider.gewuenscht(self._test(None, {'keine_kleider': True})))

    def test_fremder_job_zaehlt_nicht(self):
        test = self._test({'pshuman': {'keine_kleider': True}}, name='anderer-mesh-genesis')
        self.assertFalse(Kostuemohnekleider.gewuenscht(test))

    def test_ohne_wahl_dasselbe_objekt(self):
        art = torch.tensor([Kostuemarten.nummer('hose')])
        neu, bericht = Kostuemohnekleider.anwenden(self._test(), art)
        self.assertIs(neu, art)
        self.assertIsNone(bericht)

    def test_alles_ausser_haar_wird_haut(self):
        haut, haar = Kostuemarten.nummer('haut'), Kostuemarten.nummer('haar')
        kleider = [Kostuemarten.nummer(a) for a in Kostuemarten.ARTEN if a not in ('haut', 'haar')]
        art = torch.tensor([haut, haar, *kleider])
        neu, bericht = Kostuemohnekleider.anwenden(self._test({'pshuman': {'keine_kleider': True}}), art)
        self.assertEqual(neu.tolist(), [haut, haar] + [haut] * len(kleider))
        self.assertEqual(bericht, {'flaechen': len(kleider)})
        self.assertEqual(art[2:].tolist(), kleider)          # Eingang unberührt
