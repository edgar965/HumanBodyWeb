# -*- coding: utf-8 -*-
u"""Der Bund sitzt in der 2D-Vorschau auf dem Unterteil (11.09.2026).

Edgar, mit Bild der Panel-Vorschau: „bundhoehe bei Leggins falsch - der
Guertel oder was das ist, wird nicht nach unten verschoben". Der Upstream
setzt den Bund fest auf die Taille und die Hose 5 cm darunter — mit
kleinerer Bundhoehe (`pants.rise`) waechst die Luecke. Die Vorschau senkt
den Bund auf die Oberkante der unten angenaehten Panels; die Spezifikation
und die Boxmesh-Gegenprobe bleiben unveraendert.
"""
import io

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from GarmentCode.bundlage import Bundlage
from GarmentCode.schnittvorschau import Schnittvorschau


def _rechteck(name, x0, x1, y0, y1, z=0.0):
    return {'name': name, 'label': name,
            'punkte': np.array([[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z]]),
            'dreiecke': np.array([[0, 1, 2], [0, 2, 3]])}


def _naht(a, b):
    return [{'panel': a, 'edge': 0}, {'panel': b, 'edge': 0}]


class BundlageTest(SimpleTestCase):

    databases = set()

    def test_der_bund_faellt_auf_die_oberkante_der_hose(self):
        # Wie Edgars Hose: Hose bis 1,00 m, Bund ab 1,05 m — 5 cm Luft.
        panels = [_rechteck('pant_f_r', -0.2, 0.0, 0.08, 1.00, 0.25),
                  _rechteck('pant_b_r', -0.2, 0.0, 0.08, 1.00, -0.2),
                  _rechteck('wb_front', -0.18, 0.18, 1.05, 1.108, 0.2),
                  _rechteck('wb_back', -0.15, 0.15, 1.05, 1.108, -0.15)]
        naehte = [_naht('wb_front', 'pant_f_r'), _naht('wb_back', 'pant_b_r'),
                  _naht('wb_front', 'wb_back')]
        hub = Bundlage.senken(panels, naehte)
        self.assertAlmostEqual(hub, 0.05, places=6)
        self.assertAlmostEqual(float(panels[2]['punkte'][:, 1].min()), 1.00, places=6)
        self.assertAlmostEqual(float(panels[3]['punkte'][:, 1].max()), 1.058, places=6)
        # die Hose selbst bleibt, wo sie war
        self.assertAlmostEqual(float(panels[0]['punkte'][:, 1].max()), 1.00, places=6)

    def test_ein_bund_ueber_dem_rumpf_wird_nicht_an_den_rumpf_gezogen(self):
        u"""Kleid: der Bund haengt oben am Rumpf UND unten am Rock. Er faellt
        auf den Rock, nicht an den Rumpf (der liegt ueber ihm)."""
        panels = [_rechteck('ftorso', -0.2, 0.2, 1.10, 1.40),
                  _rechteck('skirt_f', -0.2, 0.2, 0.60, 1.02),
                  _rechteck('wb_front', -0.2, 0.2, 1.05, 1.10)]
        naehte = [_naht('wb_front', 'ftorso'), _naht('wb_front', 'skirt_f')]
        hub = Bundlage.senken(panels, naehte)
        self.assertAlmostEqual(hub, 0.03, places=6)
        self.assertEqual(Bundlage.partner_unten(panels, naehte), {'wb_front': {'skirt_f'}})

    def test_ohne_luecke_oder_ohne_naehte_passiert_nichts(self):
        panels = [_rechteck('pant_f_r', -0.2, 0.0, 0.08, 1.06),
                  _rechteck('wb_front', -0.18, 0.18, 1.05, 1.108)]
        self.assertEqual(Bundlage.senken(panels, [_naht('wb_front', 'pant_f_r')]), 0.0)
        self.assertEqual(Bundlage.senken(panels, []), 0.0)
        self.assertEqual(Bundlage.senken(panels, [['muell'], [{'x': 1}]]), 0.0)
        self.assertAlmostEqual(float(panels[1]['punkte'][:, 1].min()), 1.05, places=6)

    def test_die_vorschau_senkt_nur_auf_wunsch(self):
        spez = {'pattern': {
            'panels': {
                'pant_f_r': {'translation': [0, 8, 25], 'rotation': [0, 0, 0],
                             'vertices': [[-20, 0], [0, 0], [0, 92], [-20, 92]],
                             'edges': [{'endpoints': [0, 1]}, {'endpoints': [1, 2]},
                                       {'endpoints': [2, 3]}, {'endpoints': [3, 0]}]},
                'wb_front': {'translation': [-18, 105, 20], 'rotation': [0, 0, 0],
                             'vertices': [[0, 0], [36, 0], [36, 6], [0, 6]],
                             'edges': [{'endpoints': [0, 1]}, {'endpoints': [1, 2]},
                                       {'endpoints': [2, 3]}, {'endpoints': [3, 0]}]}},
            'panel_order': ['pant_f_r', 'wb_front'],
            'stitches': [_naht('wb_front', 'pant_f_r')]}}
        roh = Schnittvorschau(spez).netz()
        gesenkt = Schnittvorschau(spez).netz(bund_senken=True)
        bund_roh = roh['punkte'][roh['panels'][1]['ab']:, 1]
        bund_neu = gesenkt['punkte'][gesenkt['panels'][1]['ab']:, 1]
        self.assertAlmostEqual(float(bund_roh.min()), 1.05, places=6)
        self.assertAlmostEqual(float(bund_neu.min()), 1.00, places=6)
        # und der Endpunkt der Szene nimmt die gesenkte Fassung
        quelle = io.open(settings.BASE_DIR / 'core' / 'api' / 'schnittvorschau.py',
                         encoding='utf-8').read()
        self.assertIn('.netz(bund_senken=True)', quelle)
