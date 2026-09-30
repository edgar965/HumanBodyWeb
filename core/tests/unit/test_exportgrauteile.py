# -*- coding: utf-8 -*-
u"""Exportgrauteile: gewollt graue Teile ausnehmen — verlorene Farbe nicht (30.09.2026).

Der Fall „Figur ist nicht farblos" lief rot, weil eine Figur Sneakers mit
weißgrauer Sohle trug (Karte an den belegten Stellen grau, dazu Flachfarben
mit `Kd` 0,58). Die Ausnahme darf aber nicht zu groß werden: die zwei alten
Vorfälle sehen in der Exportdatei so aus wie hier die Gegenproben —

    schneeweiße Brauen  -> `Kd` fehlt oder steht auf (1, 1, 1)
    weiße Augen         -> eine fast durchsichtige Schale (`d` 0,12) vor der Iris

Und die Hautkarten sind zu einem Drittel bis zur Hälfte grau — als leerer Rand
zwischen den UV-Inseln. Der Prüfer darf sie nicht für weiß halten (Fall 8).

Geprüft wird an einer handgeschriebenen `.obj`/`.mtl` mit zwei kleinen Karten,
nicht an einer Exportdatei — der Fall muss in Millisekunden laufen.
Sabotage: in `gewollt_grau` die Bedingung `farbe is None` streichen -> Fall 3
wird rot; `wert['d'] < self.DECKEND` streichen -> Fall 5; in
`werkstoffe_mit_weisser_karte` `>= self.ANTEIL` auf `> 0` setzen -> Fall 8.
"""
from pathlib import Path

from django.test import SimpleTestCase
from PIL import Image

from core.dienste.exportgrauteile import Exportgrauteile
from core.projekt_temp import ProjektTemp

MTL = """\
newmtl sohle
Kd 0.5840 0.5840 0.5840
d 1.0000
newmtl haut
Kd 1.0000 1.0000 1.0000
d 1.0000
map_Kd haut.png
newmtl hautrand
Kd 1.0000 1.0000 1.0000
d 1.0000
map_Kd haut.png
newmtl weisskarte
Kd 1.0000 1.0000 1.0000
d 1.0000
map_Kd weiss.png
newmtl verlorenes_kd
d 1.0000
newmtl standardweiss
Kd 1.0000 1.0000 1.0000
d 1.0000
newmtl hornhaut
Kd 0.6000 0.6000 0.6000
d 0.1200
newmtl rot
Kd 0.8000 0.1000 0.1000
d 1.0000
newmtl brauen
Kd 0.0194 0.0116 0.0097
d 0.8500
newmtl haarkarte
Kd 0.5000 0.5000 0.5000
d 1.0000
map_d haarkarte_alpha.png
newmtl schnuerung
Kd 0.1384 0.1384 0.1384
d 1.0000
"""

#: `vt` 1-3: Dreieck in der LINKEN Kartenhälfte (Haut), 4-6 in der rechten (grau).
OBJ = """\
mtllib test.mtl
v 0 0 0
v 1 0 0
v 0 1 0
vt 0.10 0.10
vt 0.20 0.10
vt 0.10 0.20
vt 0.80 0.10
vt 0.90 0.10
vt 0.80 0.20
o schuh_sohle
usemtl sohle
o koerper_0
usemtl haut
f 1/1 2/2 3/3
o koerper_rand
usemtl hautrand
f 1/4 2/5 3/6
o schuh_tex
usemtl weisskarte
f 1/1 2/2 3/3
o brauen_ohne_kd
usemtl verlorenes_kd
o kugel_weiss
usemtl standardweiss
o hornhaut
usemtl hornhaut
o kleid_rot
usemtl rot
o brauen
usemtl brauen
o haar
usemtl haarkarte
o schuh_schnuerung
usemtl schnuerung
"""


class ExportgrauteileTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ordner = Path(ProjektTemp.ordner('test_exportgrauteile'))
        (ordner / 'test.mtl').write_text(MTL, encoding='utf-8')
        cls.karten_malen(ordner)
        obj = ordner / 'test.obj'
        obj.write_text(OBJ, encoding='utf-8')
        cls.objekte = Exportgrauteile(obj).objekte()

    @staticmethod
    def karten_malen(ordner):
        u"""`haut.png`: links Haut, rechts grauer leerer Rand; `weiss.png`: ganz hellgrau."""
        haut = Image.new('RGB', (8, 8), (200, 200, 200))
        haut.paste((205, 160, 140), (0, 0, 4, 8))
        haut.save(ordner / 'haut.png')
        Image.new('RGB', (8, 8), (230, 230, 230)).save(ordner / 'weiss.png')

    def test_1_flache_graue_teile_sind_gewollt_grau(self):
        self.assertIn('schuh_sohle', self.objekte)
        self.assertIn('schuh_schnuerung', self.objekte, 'auch ein dunkles Grau über DUNKEL')

    def test_2_teile_mit_farbiger_karte_bleiben_im_bild(self):
        self.assertNotIn('koerper_0', self.objekte)
        self.assertNotIn('haar', self.objekte, 'nur `map_d` zählt auch als Karte')

    def test_3_ein_verlorenes_kd_bleibt_im_bild(self):
        u"""Der Vorfall „schneeweiße Brauen": `Kd` fehlt in der `.mtl`."""
        self.assertNotIn('brauen_ohne_kd', self.objekte)

    def test_4_das_standardweiss_bleibt_im_bild(self):
        u"""Ein verlorenes `Kd` kommt als (1, 1, 1) an."""
        self.assertNotIn('kugel_weiss', self.objekte)

    def test_5_eine_durchsichtige_schale_bleibt_im_bild(self):
        u"""Der Vorfall „weiße Augen": die Hornhaut (`d` 0,12) vor der Iris."""
        self.assertNotIn('hornhaut', self.objekte)

    def test_6_farbige_und_dunkle_teile_brauchen_keine_ausnahme(self):
        self.assertNotIn('kleid_rot', self.objekte)
        self.assertNotIn('brauen', self.objekte, 'Kd 0,02 rendert dunkel, nie farblos hell')

    def test_7_ohne_mtl_ist_die_liste_leer(self):
        ordner = Path(ProjektTemp.ordner('test_exportgrauteile'))
        obj = ordner / 'ohne_mtl.obj'
        obj.write_text('o a\nusemtl x\n', encoding='utf-8')
        self.assertEqual(Exportgrauteile(obj).objekte(), [])

    def test_8_eine_weisse_karte_ist_gewollt_weiss_der_leere_rand_nicht(self):
        u"""Die Sneakers: ihre Karte ist dort grau, wo Flächen liegen. Bei der
        Hautkarte ist nur der Rand grau — sitzt eine Fläche mitten darauf
        (`koerper_rand`), ist SIE weiß, die Fläche auf der Haut (`koerper_0`)
        nicht, obwohl beide dieselbe Datei lesen."""
        self.assertIn('schuh_tex', self.objekte)
        self.assertIn('koerper_rand', self.objekte)
        self.assertNotIn('koerper_0', self.objekte)
