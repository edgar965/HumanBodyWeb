# -*- coding: utf-8 -*-
"""Schritt „Figur aus Zeile 1“ (`Zeile1figur`, 30.10.2026): Rahmen und Umrechnung der Ziele der KI an Kunstdaten, auf der CPU, ohne Figur und ohne Karte.

    1  Rahmen: eine Kunstdatei (Kasten mit Schrägseite) im Rahmen von Zeile 1 (`Vorstufenrahmen.hin` mit Drehung 30°, dann Füße auf 0, wie `Mesh3daimeshziel.ziel`) → `rahmen()`
       bringt jeden Punkt dorthin, wo ihn die Kette mit Höhe = m · Höhe der Datei sieht ((x − B) · m), Probe 0 mm, Höhe m · H
    2  ohne Drehung und mit Mitte 0 (Fall edgar) dasselbe
    3  `schreiben`: Ziele der KI im alten Rahmen ((x · s_f + v_f) · s) → (x − B) · m; `figur_massstab` 1, `rahmen_massstab` m, `rahmen_versatz` −B · m, `zeile1`, Haltung übernommen;
       `form.npz` → hoehe_m = m · H; `test.json` → form.<g>.haltung „zeile1“
Die Haltung selbst (Kinematik auf der Karte) ist am echten Lauf gemessen, nicht hier: edgar 30.10.2026 00:34, Rest je Käfigpunkt Mittel 1,61 mm, max 11,94 mm (`_test/edgar/zeile1/`).
Sabotage (von Hand): in `rahmen` `r = …T` ohne `.T` → Fall 1 rot (Fall 2 bleibt grün, Drehung 0); in `schreiben` `- vf_alt` streichen → Fall 3 rot.
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def datei_punkte():
    """Kunstnetz: Kasten 0,4 × 1,6 × 0,3 m, verschoben, dazu eine schräge Reihe (damit Mitte und Drehung etwas zu tun haben)."""
    g = np.stack(np.meshgrid([0.0, 0.4], [0.0, 1.6], [0.0, 0.3]), -1).reshape(-1, 3)
    schraeg = np.stack([np.linspace(0, 0.4, 7), np.linspace(0.2, 1.4, 7), np.linspace(0, 0.3, 7)], 1)
    return np.concatenate([g, schraeg]) + [0.7, -0.05, -0.2]


def rahmen_zeile1(v, a):
    """Wie `Mesh3daimeshziel.ziel`: `hin`, dann Füße auf 0. → (Punkte, ziel_boden)."""
    c, s = math.cos(a['heading']), math.sin(a['heading'])
    q = v @ np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]]).T
    q = (q - [a['zentrum'][0], a['boden'], a['zentrum'][1]]) * a['massstab'] + [0.0, a['ruhehoehe'], 0.0]
    boden = q[:, 1].min()
    return q - [0.0, boden, 0.0], boden


class Zeile1rahmenTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(Path(settings.TOOLS_ROOT) / 'ProjektTemp'))
        self.test = Path(self._tmp.name) / 'kunst'
        (self.test / 'vorstufe' / '0001').mkdir(parents=True)
        np.savez(self.test / 'vorstufe' / '0001' / 'apose.npz', netz=np.array(str(self.test / 'kunst.glb')))

    def tearDown(self):
        self._tmp.cleanup()

    def _figur(self, a):
        from mesh3dai_zeile1figur import Zeile1figur
        v = datei_punkte()
        punkte, boden = rahmen_zeile1(v, a)
        z = object.__new__(Zeile1figur)
        z.test, z.g, z.log = self.test, 'maennlich', lambda s: None
        z.bericht_ma = {'kette': '0001'}
        z.ma = {'rahmen_heading': np.float64(a['heading']), 'rahmen_zentrum': np.asarray(a['zentrum']), 'rahmen_boden': np.float64(a['boden']),
                'rahmen_massstab': np.float64(a['massstab']), 'rahmen_ruhehoehe': np.float64(a['ruhehoehe']), 'ziel_boden': np.float64(boden), 'netz_punkte': punkte}
        return z, v, punkte

    def _rahmen(self, a):
        z, v, punkte = self._figur(a)
        netz = mock.Mock(vertices=v)
        with mock.patch('mesh3dai_netzvorrat.Netzvorrat.laden', return_value=netz):
            r = z.rahmen()
        lo, hi = v.min(0), v.max(0)
        b = np.array([(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
        np.testing.assert_allclose(punkte @ r['r'].T + r['t'], (v - b) * a['massstab'], atol=1e-9)
        self.assertLess(r['probe_mm'], 1e-6)
        self.assertAlmostEqual(r['hoehe_m'], a['massstab'] * (hi[1] - lo[1]), places=9)
        np.testing.assert_allclose(r['b'], b)
        return r

    def test_1_rahmen_mit_drehung(self):
        self._rahmen({'heading': math.radians(30.0), 'zentrum': [0.81, -0.07], 'boden': -0.04, 'massstab': 1.77, 'ruhehoehe': 0.95})

    def test_2_rahmen_ohne_drehung(self):
        self._rahmen({'heading': 0.0, 'zentrum': [0.0, 0.0], 'boden': -0.53, 'massstab': 1.774205, 'ruhehoehe': 0.0134})

    def test_3_schreiben_rechnet_die_ziele_um(self):
        from mesh3dai_zeile1figur import Zeile1figur
        z = object.__new__(Zeile1figur)
        z.test, z.g, z.log = self.test, 'maennlich', lambda s: None
        z.fig = self.test / 'form_maennlich'
        (z.fig / 'anzeige').mkdir(parents=True)
        np.savez(z.fig / 'anzeige' / 'netz.npz', ruhe=np.array([[0.0, 0.0, 0.0], [0.0, 1.81, 0.0]], dtype=np.float32))
        x = datei_punkte()[:5]
        s_f, v_f, s = 1.74, np.array([0.02, -0.01, 0.03]), 1.012
        alt = ((x * s_f + v_f) * s).astype(np.float32)
        np.savez(self.test / 'ergebnis_Form_maennlich.npz', rig=alt, dreh=np.zeros((5, 3, 3), np.float32), winkel=np.zeros((5, 3), np.float32), stimmen=alt, enden=alt,
                 figur_massstab=np.float64(s), rahmen_massstab=np.float64(s_f), rahmen_versatz=v_f, koerper=np.bool_(True))
        np.savez(self.test / 'form.npz', hoehe_m=np.float32(1.70), massstab=np.float32(1.74), regler=np.zeros(3, np.float32))
        (self.test / 'test.json').write_text(json.dumps({'kennung': 'kunst', 'form': {'maennlich': {'hoehe_m': 1.7}}}), encoding='utf-8')
        b, m = np.array([0.9, -0.05, -0.05]), 1.77
        p, d, w = np.ones((5, 3)), np.tile(np.eye(3), (5, 1, 1)), np.full((5, 3), 2.0)
        h = z.schreiben({'b': b, 'm': m, 'hoehe_m': 2.832}, (p, d, w))
        e = np.load(self.test / 'ergebnis_Form_maennlich.npz')
        np.testing.assert_allclose(e['stimmen'], (x - b) * m, atol=2e-6)
        np.testing.assert_allclose(e['enden'], (x - b) * m, atol=2e-6)
        np.testing.assert_allclose(e['rig'], p)
        self.assertEqual(float(e['figur_massstab']), 1.0)
        self.assertAlmostEqual(float(e['rahmen_massstab']), m)
        np.testing.assert_allclose(e['rahmen_versatz'], -b * m)
        self.assertTrue(bool(e['zeile1']))
        self.assertFalse(bool(e['koerper']))
        self.assertAlmostEqual(float(np.load(self.test / 'form.npz')['hoehe_m']), 2.832, places=5)
        info = json.loads((self.test / 'test.json').read_text(encoding='utf-8'))
        self.assertEqual(info['form']['maennlich']['haltung'], 'zeile1')
        self.assertAlmostEqual(h, 1.81, places=5)


if __name__ == '__main__':
    unittest.main()
