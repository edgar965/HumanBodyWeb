# -*- coding: utf-8 -*-
u"""Objwerkstoffe muss die richtigen Objekte als „ohne Bildkarte" erkennen —
gegen eine kleine, selbst geschriebene .obj/.mtl, kein echtes Modell nötig."""
from pathlib import Path

from django.test import SimpleTestCase

from core.dienste.objwerkstoffe import Objwerkstoffe
from core.projekt_temp import ProjektTemp

OBJ = """mtllib probe.mtl
v 0 0 0
v 1 0 0
v 0 1 0
o haut
usemtl mat_haut
f 1 2 3
o schuh
usemtl mat_schuh
f 1 2 3
o kleid
usemtl mat_schuh
f 1 2 3
"""

MTL = """newmtl mat_haut
Kd 1.0000 1.0000 1.0000
map_Kd haut.png
newmtl mat_schuh
Kd 0.1981 0.0319 0.0319
"""


class ObjwerkstoffeTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ordner = Path(ProjektTemp.ordner('test_objwerkstoffe'))
        (ordner / 'probe.obj').write_text(OBJ, encoding='utf-8')
        (ordner / 'probe.mtl').write_text(MTL, encoding='utf-8')
        cls.w = Objwerkstoffe(ordner / 'probe.obj')

    def test_objekt_werkstoff_liest_die_zuordnung(self):
        self.assertEqual(self.w.objekt_werkstoff(),
                         {'haut': 'mat_haut', 'schuh': 'mat_schuh', 'kleid': 'mat_schuh'})

    def test_werkstoff_mit_karte_zaehlt_nicht_als_ohne(self):
        self.assertEqual(self.w.werkstoffe_ohne_karte(), {'mat_schuh'})

    def test_zwei_objekte_teilen_sich_den_kartenlosen_werkstoff(self):
        u"""Kleid UND Schuh nutzen denselben `mat_schuh` in dieser Probe —
        beide müssen als „ohne Karte" erscheinen, nicht nur der erste."""
        self.assertEqual(self.w.objekte_ohne_karte(), ['kleid', 'schuh'])
