# -*- coding: utf-8 -*-
u"""Das Schnittprogramm des Schuhs, gegen pygarment gebaut.

WARUM DIESE TESTS AN DER GEOMETRIE HÄNGEN (11.09.2026): Der erste Lauf der
Ballerina durch die Simulation brach mit „Invalid stitching. Unable to fix"
ab — die Zehenspitze der Sohle war mit der Ferse verschmolzen. Zwei
Ursachen, beide still, beide hier festgehalten:

1. **Die Aussenseite.** `Panel.autonorm` dreht die Kantenfolge so, dass die
   Aussenseite vom Ursprung weg zeigt. Das innere Quartier des linken
   Schuhs steht bei x = +16 cm, seine Aussenseite zeigt aber zur Mitte —
   pygarment hielt sie für innen und liess die Nähte an diesem Panel
   verdreht laufen (gemessen: 6 von 22 Nähten). `Halbschuh.nach_aussen`
   setzt die Richtung ausdrücklich.
2. **Die Reihenfolge der Nahtstücke.** `StitchingRule` paart die Kanten
   zweier Schnittstellen nach Index und unterteilt entlang ihrer
   Richtung. Beide müssen im Raum gleich laufen; `Nahtrichtung` misst das.

Die Prüfung ist dieselbe, die das Boxmesh später macht — nur ohne die
20 s Simulation dahinter.
"""
import copy
import os

import numpy as np
import yaml
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.entwurf import Entwurf                      # noqa: E402

UPSTREAM = Entwurf.REPO


def _upstream_laden():
    import sys
    if UPSTREAM not in sys.path:
        sys.path.insert(0, UPSTREAM)


class SchuhschnittTest(SimpleTestCase):

    databases = []

    #: Die Fussmasse der Vorgabefigur (11.09.2026, `fussmasse.py`).
    FUSS = {
        'foot_length': 24.41, 'foot_heel_width': 7.08, 'foot_ball_width': 9.14,
        'toe_height': 2.99, 'foot_instep': 21.83, 'instep_angle': 19.63,
        'foot_x': 21.55, 'foot_toe_z': 23.19, 'foot_heel_z': -1.22,
        'foot_yaw': 0.04, 'ankle_circ': 19.23, 'ankle_height': 13.78,
        'calf_circ': 37.8, 'calf_height': 46.64, 'knee_circ': 34.73,
        'knee_height': 53.1,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _upstream_laden()
        alt = os.getcwd()
        os.chdir(UPSTREAM)
        try:
            # Wie `lauf.py`: pygarments Kurvenzerlegung durch die tabellierte
            # ersetzen. Die des Upstream (svgpathtools `ilength`) bricht an
            # der Quartier-Oberkante mit „Maximum iterations reached" ab —
            # im Produktivweg ist sie längst ersetzt (08.09.2026).
            import pygarment.garmentcode.edge as edge_modul
            from GarmentCode.kurvenzerlegung import Kurvenzerlegung
            Kurvenzerlegung.einhaengen(edge_modul)
            from GarmentCode.schuh.schuhentwurf import Schuhentwurf
            pfad = os.path.join(UPSTREAM, 'assets', 'design_params',
                                'default.yaml')
            with open(pfad, 'r', encoding='utf-8') as datei:
                cls.entwurf = yaml.safe_load(datei)['design']
            Schuhentwurf.mischen(cls.entwurf)
            with open(os.path.join(UPSTREAM, 'assets', 'bodies',
                                   'mean_female.yaml'), 'r') as datei:
                cls.body = yaml.safe_load(datei)['body']
            cls.body.update(cls.FUSS)
        finally:
            os.chdir(alt)

    def _bauen(self, art, **regler):
        from GarmentCode.schuh.schuhgarment import Schuhgarment
        entwurf = copy.deepcopy(self.entwurf)
        entwurf['meta']['feet']['v'] = art
        for pfad, wert in regler.items():
            gruppe, feld = pfad.split('.')
            entwurf[gruppe][feld]['v'] = wert
        return Schuhgarment('probe', self.body, entwurf)

    # ------------------------------------------------------------- Aufbau

    def test_ein_halbschuh_hat_vier_panels_je_seite(self):
        muster = self._bauen('Halbschuh').assembly()
        self.assertEqual(len(muster.pattern['panels']), 8)
        self.assertEqual(len(muster.pattern['stitches']), 22)

    def test_ein_stiefel_hat_sechs(self):
        muster = self._bauen('Stiefel').assembly()
        self.assertEqual(len(muster.pattern['panels']), 12)

    def test_kein_panel_durchdringt_sich(self):
        for art in ('Halbschuh', 'Stiefel'):
            self.assertFalse(self._bauen(art).is_self_intersecting(), art)

    def test_der_rechte_schuh_ist_das_spiegelbild(self):
        g = self._bauen('Halbschuh')
        links, rechts = g.links.bbox3D(), g.rechts.bbox3D()
        self.assertAlmostEqual(links[0][0], -rechts[1][0], places=3)
        self.assertAlmostEqual(links[1][0], -rechts[0][0], places=3)
        np.testing.assert_allclose(links[0][1:], rechts[0][1:], atol=1e-6)

    def test_die_sohle_liegt_unter_dem_fuss_und_das_blatt_darueber(self):
        g = self._bauen('Halbschuh')
        sohle = g.links.sohle.bbox3D()
        self.assertLess(sohle[1][1], 0.0)                 # ganz unter y=0
        self.assertGreater(g.links.blatt.bbox3D()[1][1], self.FUSS['toe_height'])
        # Die Sohle ist so lang wie der Fuss mal Regler (1,04).
        self.assertAlmostEqual(sohle[1][2] - sohle[0][2],
                               self.FUSS['foot_length'] * 1.04, delta=0.6)

    # ------------------------------------------------------ Aussenseiten

    def test_jedes_panel_zeigt_mit_der_aussenseite_nach_aussen(self):
        u"""Der Fehler Nr. 1 aus dem Modulkopf — hier für beide Schuhe."""
        g = self._bauen('Stiefel')
        for schuh, spiegel in ((g.links, 1.0), (g.rechts, -1.0)):
            for panel, richtung in schuh.aussenrichtungen():
                soll = np.asarray(richtung, float) * np.array([spiegel, 1, 1])
                self.assertGreater(float(np.dot(panel.norm(), soll)), 0.0,
                                   panel.name)

    # --------------------------------------------------------------- Nähte

    def test_jede_naht_laeuft_in_beiden_panels_gleichgerichtet(self):
        u"""Der Fehler Nr. 2: Anfang an Anfang, nicht Anfang an Ende."""
        from GarmentCode.schuh.nahtrichtung import Nahtrichtung
        g = self._bauen('Stiefel')
        for schuh in (g.links, g.rechts):
            for regel in schuh.stitching_rules.rules:
                a1, e1 = Nahtrichtung.enden(regel.int1)
                a2, e2 = Nahtrichtung.enden(regel.int2)
                gleich = np.linalg.norm(a1 - a2) + np.linalg.norm(e1 - e2)
                gegen = np.linalg.norm(a1 - e2) + np.linalg.norm(e1 - a2)
                self.assertLessEqual(gleich, gegen,
                                     '%s <-> %s' % (regel.int1.panel_names(),
                                                    regel.int2.panel_names()))

    def test_die_nahtstuecke_passen_in_der_zahl(self):
        u"""Nach dem Unterteilen hat jede Naht auf beiden Seiten gleich
        viele Kanten — sonst zippt `assembly` Stücke gegen nichts."""
        g = self._bauen('Halbschuh')
        for regel in g.links.stitching_rules.rules:
            self.assertEqual(len(regel.int1.edges), len(regel.int2.edges))

    # ------------------------------------------------------------- Regler

    def test_der_schaft_folgt_dem_regler(self):
        niedrig = self._bauen('Stiefel', **{'boot.height': 0.1})
        hoch = self._bauen('Stiefel', **{'boot.height': 0.9})
        self.assertGreater(hoch.links.schafthoehe, niedrig.links.schafthoehe + 15)

    def test_ohne_fussmasse_wird_geschaetzt_und_gesagt(self):
        from GarmentCode.schuh.schuhgarment import Schuhgarment
        body = {k: v for k, v in self.body.items() if k not in self.FUSS}
        entwurf = copy.deepcopy(self.entwurf)
        entwurf['meta']['feet']['v'] = 'Halbschuh'
        g = Schuhgarment('probe', body, entwurf)
        self.assertTrue(g.hinweise)
        self.assertIn(u'geschätzt', g.hinweise[0])
        # Und die Schätzung liegt nahe an der Messung (Anteile der Höhe).
        self.assertAlmostEqual(g.links.fuss.foot_length,
                               self.FUSS['foot_length'], delta=1.0)
