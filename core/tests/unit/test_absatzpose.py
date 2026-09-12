# -*- coding: utf-8 -*-
u"""Der Absatz als Teil der Pose — gerechnet vom Server, nicht vom Betrachter.

WARUM (11.09.2026, Edgar: „der Betrachter soll bei einem Absatzschuh gar
nichts tun, sondern das Programm soll die Pose ändern!")
======================================================================
`Absatzpose` rechnet die Fussbeugung als Knochendeltas in jede Pose
hinein (`Posen.pose`, `?winkel_grad=…`). Geprüft wird die RECHNUNG, nicht
das Bild: Ein Delta im Knochenraum muss, in die Welt zurückübersetzt,
genau die Drehung um die Querachse ergeben — für den Fuss um den Winkel,
für die Zehen zurück und um die Sprengung weiter. Und die Ruhelage ohne
Absatz bleibt leer.
"""
import json
import math
import os
import shutil

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from core.dienste.absatzpose import Absatzpose


def _skelett(ordner):
    u"""Ein Kunstskelett: Bein senkrecht, Fuss um 90° nach vorn gekippt,
    Zehen daran — mit ECHTEN Ruhedrehungen, damit die Umbasierung zählt."""
    def um_x(grad):
        h = math.radians(grad) / 2.0
        return [math.cos(h), math.sin(h), 0.0, 0.0]
    knochen = [
        {'name': 'DEF-spine', 'parent': None, 'local_position': [0, 0, 0.8],
         'local_quaternion': um_x(90.0)},
        {'name': 'DEF-shin.L', 'parent': 'DEF-spine', 'local_position': [0, 0.4, 0],
         'local_quaternion': um_x(-30.0)},
        {'name': 'DEF-foot.L', 'parent': 'DEF-shin.L', 'local_position': [0, 0.4, 0],
         'local_quaternion': um_x(75.0)},
        {'name': 'DEF-toe.L', 'parent': 'DEF-foot.L', 'local_position': [0, 0.15, 0],
         'local_quaternion': um_x(-20.0)},
        {'name': 'DEF-foot.R', 'parent': 'DEF-spine', 'local_position': [0, 0.8, 0],
         'local_quaternion': um_x(45.0)},
        {'name': 'DEF-toe.R', 'parent': 'DEF-foot.R', 'local_position': [0, 0.15, 0],
         'local_quaternion': um_x(-20.0)},
    ]
    os.makedirs(ordner, exist_ok=True)
    with open(os.path.join(ordner, 'def_skeleton.json'), 'w', encoding='utf-8') as datei:
        json.dump({'bone_count': len(knochen), 'bones': knochen}, datei)


class AbsatzposeTest(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = os.path.join(settings.BASE_DIR, '_wegwerf', 'test_absatzpose')
        _skelett(cls.ordner)
        cls._settings = override_settings(HUMANBODY_DATA_DIR=cls.ordner)
        cls._settings.enable()
        Absatzpose._skelette.clear()

    @classmethod
    def tearDownClass(cls):
        cls._settings.disable()
        Absatzpose._skelette.clear()
        shutil.rmtree(cls.ordner, ignore_errors=True)
        super().tearDownClass()

    @staticmethod
    def _winkel_um_x(q):
        u"""Drehwinkel (Grad, mit Vorzeichen) einer [w,x,y,z] um die x-Achse."""
        w, x, y, z = q
        assert abs(y) < 1e-9 and abs(z) < 1e-9, q
        return math.degrees(2.0 * math.atan2(x, w))

    def test_das_delta_ergibt_in_der_welt_die_drehung_um_die_querachse(self):
        pose = Absatzpose(winkel_grad=25.0, sprengung_grad=8.0)
        welt = Absatzpose.ruhelagen('female')
        deltas = pose.deltas()
        self.assertEqual(set(deltas), {'DEF-foot.L', 'DEF-foot.R', 'DEF-toe.L', 'DEF-toe.R'})
        for name, soll in (('DEF-foot.L', 25.0), ('DEF-foot.R', 25.0),
                           ('DEF-toe.L', -33.0), ('DEF-toe.R', -33.0)):
            q = welt[name]
            # q_welt * delta * q_welt^-1 = R  (die Drehung in der Welt)
            r = Absatzpose.mal(Absatzpose.mal(q, deltas[name]), Absatzpose.invers(q))
            self.assertAlmostEqual(self._winkel_um_x(r), soll, places=6, msg=name)

    def test_die_ruhelagen_sind_die_elternketten(self):
        welt = Absatzpose.ruhelagen('female')
        # Fuss L: 90 - 30 + 75 = 135 Grad um x; Zehe L: 135 - 20 = 115.
        self.assertAlmostEqual(self._winkel_um_x(welt['DEF-foot.L']), 135.0, places=6)
        self.assertAlmostEqual(self._winkel_um_x(welt['DEF-toe.L']), 115.0, places=6)
        self.assertAlmostEqual(self._winkel_um_x(welt['DEF-foot.R']), 135.0, places=6)

    def test_einrechnen_haengt_hinter_die_pose_und_laesst_den_rest(self):
        pose = Absatzpose(winkel_grad=10.0)
        vorher = {'DEF-spine': [0.9, 0.1, 0.0, 0.0], 'DEF-foot.L': [1.0, 0.0, 0.0, 0.0]}
        nachher = pose.einrechnen(vorher)
        self.assertEqual(nachher['DEF-spine'], vorher['DEF-spine'])
        self.assertEqual(vorher['DEF-foot.L'], [1.0, 0.0, 0.0, 0.0])   # Kopie
        self.assertEqual(nachher['DEF-foot.L'], pose.deltas()['DEF-foot.L'])
        self.assertIn('DEF-toe.R', nachher)

    def test_aus_anfrage_ohne_absatz_ist_nichts(self):
        self.assertIsNone(Absatzpose.aus_anfrage({}))
        self.assertIsNone(Absatzpose.aus_anfrage({'winkel_grad': 'x'}))
        pose = Absatzpose.aus_anfrage({'winkel_grad': '7', 'hebung_cm': '4.9',
                                       'plateau_cm': '1'})
        self.assertAlmostEqual(pose.hebung_m, 0.059)
        self.assertEqual(Absatzpose.to_threejs({'a': [1, 2, 3, 4]}), {'a': [2, 4, -3, 1]})

    def test_der_endpunkt_liefert_die_ruhelage_mit_und_ohne_absatz(self):
        leer = self.client.get('/api/character/pose/ruhelage/').json()
        self.assertEqual(leer['threejs'], {})
        self.assertIsNone(leer['absatz'])
        self.assertEqual(leer['hebung_m'], 0.0)
        mit = self.client.get('/api/character/pose/ruhelage/?winkel_grad=25'
                              '&sprengung_grad=8&hebung_cm=4.9').json()
        self.assertEqual(len(mit['threejs']), 4)
        self.assertAlmostEqual(mit['hebung_m'], 0.049)
        self.assertEqual(mit['absatz']['winkel_grad'], 25.0)
        self.assertEqual(self.client.get('/api/character/pose/gibtsnicht/').status_code, 404)
