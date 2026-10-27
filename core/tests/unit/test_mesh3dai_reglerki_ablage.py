# -*- coding: utf-8 -*-
"""Mesh3D-AI, Regler-KI (26.10.2026 nachts): Drehungen der `Aposehaltung`, Ablage für die Seite „Formvariante“ (`Reglerkiablage`) und Regler der Seite (`Mesh3daiformvariantefigur.regler`)
an Kunstdaten, ohne Karte und ohne Figur:

    1  `_kabsch_np` findet eine zufällige Drehung aus drei gewichteten Versätzen wieder; `_bogen_np` dreht a auf b; `_bogen` (torch) = `_bogen_np`
    2  `Reglerkiablage.liste`: nur Anfasser tragen `faktor` (cm → m) und `schwelle` (1e-5 m in cm)
    3  `Reglerkiablage.schreiben`: Zeilen je Posengruppe in der Reihenfolge von `proben.json`, nur Wolke 0, fehlende Proben in `ausgelassen`
    4  `Mesh3daiformvariantefigur.regler`: Anfasser unter der alten Schwelle 0,01 bleiben und kommen in m an; Regler ohne Angabe wie bisher
Sabotage (von Hand): in `_kabsch_np` die Vorzeichen-Korrektur streichen (`np.sign(…)` → 1.0) → Fall 1 rot, sobald die Spiegelung gewählt wird; in `Reglerkiablage.liste` `if i >= raum.a0`
→ `if True` → Fall 2 rot; in `schreiben` `if k == 0` streichen → Fall 3 rot; in `Mesh3daiformvariantefigur.regler` `* r.get('faktor', 1.0)` streichen → Fall 4 rot.
Nicht gelaufen (Tests nur auf Ansage).
"""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.conf import settings

from ._pruefablage import Pruefablage

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _torch():
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_torch(), 'kein torch')
class ReglerkiablageTest(unittest.TestCase):
    def test_1_drehungen(self):
        import torch
        from mesh3dai_aposehaltung import _bogen, _bogen_np, _kabsch_np
        z = np.random.default_rng(3)
        q, _r = np.linalg.qr(z.normal(size=(3, 3)))
        r = q * np.sign(np.linalg.det(q))
        o = z.normal(size=(3, 3))
        o /= np.linalg.norm(o, axis=1, keepdims=True)
        np.testing.assert_allclose(_kabsch_np(o, o @ r.T, np.array([1.0, 2.0, 0.5])), r, atol=1e-9)
        a, b = o[0], o[1]
        np.testing.assert_allclose(_bogen_np(a, b) @ a, b, atol=1e-9)
        t = _bogen(torch.tensor(a[None]), torch.tensor(b[None]))[0].numpy()
        np.testing.assert_allclose(t, _bogen_np(a, b), atol=1e-6)

    @staticmethod
    def _raum():
        import torch
        return SimpleNamespace(namen=['daz_a', 'eigen:regler_b', 'anfasser_c'], lo=torch.tensor([-1.0, -1.0, -2.0]), hi=torch.tensor([1.0, 1.0, 2.0]), a0=2,
                               einheit_m=0.01, KLEIN_M=1e-5, art=lambda i: ('daz', 'haupt', 'anfasser')[i])

    def test_2_liste(self):
        from mesh3dai_reglerki_ablage import Reglerkiablage
        liste = Reglerkiablage.liste(self._raum())
        self.assertNotIn('faktor', liste[0])
        self.assertNotIn('faktor', liste[1])
        self.assertEqual(liste[2]['faktor'], 0.01)
        self.assertAlmostEqual(liste[2]['schwelle'], 1e-3)

    def test_3_schreiben(self):
        import torch
        import mesh3dai_reglerki_ablage as m
        with Pruefablage.ordner('reglerki_') as tmp:
            wurzel, ordner = Path(tmp) / 'daten', Path(tmp) / 'lauf'
            (wurzel / 'FormX').mkdir(parents=True)
            ordner.mkdir()
            (wurzel / 'FormX' / 'proben.json').write_text(json.dumps([{'nr': 1, 'gruppe': 'pruefung'}, {'nr': 2, 'gruppe': 'training'}, {'nr': 3, 'gruppe': 'pruefung'},
                                                                      {'nr': 4, 'gruppe': 'pruefung'}]), encoding='utf-8')
            daten = SimpleNamespace(namen=[('FormX', 3, 0), ('FormX', 1, 0), ('FormX', 1, 1), ('FormX', 2, 0)], w=torch.ones((4, 3)),
                                    nm=SimpleNamespace(fr=SimpleNamespace(raum=self._raum())))
            vor = torch.tensor([[3.0, 0, 0], [1.0, 0, 0], [9.0, 0, 0], [2.0, 0, 0]])
            alt, m.WURZEL = m.WURZEL, wurzel
            try:
                ergebnis = {}
                self.assertEqual(m.Reglerkiablage.schreiben(ordner, daten, vor, ergebnis), 1)
            finally:
                m.WURZEL = alt
            with np.load(ordner / 'formen_vorhersagen.npz') as z:
                np.testing.assert_array_equal(z['FormX_pruefung_form'][:, 0], [1.0, 3.0])
                np.testing.assert_array_equal(z['FormX_training_form'][:, 0], [2.0])
                np.testing.assert_array_equal(z['FormX_soll_form'], [1.0, 1.0, 1.0])
            self.assertEqual(ergebnis['ausgelassen'], {'FormX/4/k0': 'keine taugliche Wolke 0'})
            self.assertEqual(ergebnis['eingang'], 'apose_v9')
            self.assertEqual(len(json.loads((ordner / 'formregler_liste.json').read_text(encoding='utf-8'))['regler']), 3)

    def test_4_regler_der_seite(self):
        from core.dienste.mesh3daiformvariantefigur import Mesh3daiformvariantefigur as F
        liste = [{'name': 'daz_a', 'min': -1, 'max': 1}, {'name': 'anfasser_c', 'min': -2, 'max': 2, 'faktor': 0.01, 'schwelle': 1e-3}]
        self.assertEqual(F.regler([0.005, 0.5], liste), {'anfasser_c': 0.005})
        self.assertEqual(F.regler([0.5, 0.0005], liste), {'daz_a': 0.5})
