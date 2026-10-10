# -*- coding: utf-8 -*-
"""Hüftverankerung: die Wurzel wandert so, dass die HÜFTGELENKE der Quelle folgen.

Befund (09.10.2026): Auf Genesis 9 und SMPL liegen die Hüftgelenke anders um das Wurzelgelenk
als in der Quelle (Rest der Wurzelbasis 50° Hüfte → Oberschenkel); kippt das Becken, schwingen sie
um einen anderen Hebel. Gemessen (`ProjektTemp/_wegwerf/staystill_ziele/huefte_messen.py`, vorher):
Hüftmitte gegen die skalierte Quelle bis 28 cm (SMPL-X-Tanz auf DEF). `retarget/huefteverankerung.py`.

KUNSTFIGUR MIT BEKANNTER WAHRHEIT: Quelle und Ziel sind zwei Dreiergruppen (Wurzel + zwei Hüften),
die Hüften der Quelle 2 cm unter dem Wurzelgelenk, die des Ziels 8 cm. Bild 1 kippt beide Becken
um 90° um X. Die Hüftmitte wandert in der Quelle um (0; 0,02; −0,02), im Ziel um (0; 0,08; −0,08);
mit Hoehenfaktor 2 muss die Wurzel des Ziels um (0; −0,04; 0,04) ausweichen, dann liegt die
Zielmitte bei (0; 0,04; −0,04) = 2 × Quelle.

Sabotage-Gegenprobe: in `Huefteverankerung.merken` den Faktor weglassen → Fall 1 rot; `korrektur`
ohne Abzug von Bild 0 → Fall 2 rot.

GESCHRIEBEN 09.10.2026, NICHT GELAUFEN (Tests nur auf Ansage).
"""

from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton.retarget.huefteverankerung import Huefteverankerung  # noqa: E402
from humanbody_core.skeleton.retarget.wurzelspur import Wurzelspur  # noqa: E402

ID = np.array([0.0, 0.0, 0.0, 1.0])
#: 90° um X.
KIPPEN = np.array([np.sin(np.pi / 4), 0.0, 0.0, np.cos(np.pi / 4)])


def knochen(eltern, ort):
    return SimpleNamespace(parent_name=eltern, local_pos=np.array(ort, dtype=float))


class Kunstfigur:
    u"""Wurzel mit zwei Hüften in Quelle und Ziel, wie in der Beschreibung oben."""

    def __init__(self, eltern_links='root'):
        self.skel = SimpleNamespace(bones={
            'root': knochen(None, (0, 1, 0)),
            'thigh.L': knochen(eltern_links, (0.11, -0.08, 0)),
            'thigh.R': knochen('root', (-0.11, -0.08, 0)),
        })
        versaetze = [np.zeros(3), np.array([0.1, -0.02, 0]), np.array([-0.1, -0.02, 0])]
        self.bvh = SimpleNamespace(names=['Hips', 'LUp', 'RUp'], offsets=versaetze)
        self.bvh_idx = {'Hips': 0, 'LUp': 1, 'RUp': 2}
        self.bvh_eltern = {'Hips': None, 'LUp': 'Hips', 'RUp': 'Hips'}
        self.rig_to_bvh = {'root': 'Hips', 'thigh.L': 'LUp', 'thigh.R': 'RUp'}

    def verankerung(self, hueften=('thigh.L', 'thigh.R'), faktor=2.0):
        return Huefteverankerung(self.skel, self.bvh, self.rig_to_bvh, self.bvh_idx, self.bvh_eltern, 'root',
                                 faktor, hueften=list(hueften))

    @staticmethod
    def bild(drehung):
        quelle = {n: drehung for n in ('Hips', 'LUp', 'RUp')}
        ziel = {n: drehung for n in ('root', 'thigh.L', 'thigh.R')}
        return quelle, ziel


class HuefteverankerungTest(SimpleTestCase):

    def _gerechnet(self, drehungen):
        figur = Kunstfigur()
        v = figur.verankerung()
        for d in drehungen:
            v.merken(*figur.bild(d))
        return v

    def test_hueftmitte_folgt_der_skalierten_quelle(self):
        korrektur = self._gerechnet([ID, KIPPEN]).korrektur()
        np.testing.assert_allclose(korrektur[1], [0.0, -0.04, 0.04], atol=1e-9)

    def test_bild_null_bleibt_unveraendert(self):
        korrektur = self._gerechnet([ID, KIPPEN]).korrektur()
        np.testing.assert_allclose(korrektur[0], [0.0, 0.0, 0.0], atol=1e-12)

    def test_ohne_kippen_keine_verschiebung(self):
        korrektur = self._gerechnet([ID, ID, ID]).korrektur()
        np.testing.assert_allclose(korrektur, np.zeros((3, 3)), atol=1e-12)

    def test_oberschenkel_nicht_unter_der_wurzel_gibt_keine_verschiebung(self):
        figur = Kunstfigur(eltern_links=None)
        v = figur.verankerung()
        v.merken(*figur.bild(ID))
        self.assertFalse(v.aktiv)
        self.assertIsNone(v.korrektur())

    def test_zielnamen_ueber_die_def_tabelle(self):
        def_tabelle = {'LeftUpLeg': 'DEF-thigh.L', 'RightUpLeg': 'DEF-thigh.R', 'Hips': 'DEF-spine'}
        ziel = {'LeftUpLeg': 'Left_hip', 'RightUpLeg': 'Right_hip'}
        self.assertEqual(Huefteverankerung.zielnamen(def_tabelle, ziel), ['Left_hip', 'Right_hip'])
        self.assertIsNone(Huefteverankerung.zielnamen(def_tabelle, {'LeftUpLeg': 'Left_hip'}))


class WurzelspurMitVerschiebungTest(SimpleTestCase):

    def test_die_verschiebung_wird_auf_den_weg_addiert(self):
        bvh = SimpleNamespace(names=['Hips'], children={}, positions=np.array([[[0.0, 0, 0]], [[1.0, 2, 3]]]))
        skel = SimpleNamespace(bones={'root': SimpleNamespace(local_pos=np.array([0.0, 1, 0]))})
        verschiebung = np.array([[0.0, 0, 0], [0.5, 0.25, -0.5]])
        spur = Wurzelspur(bvh, skel, {'Hips': 'root'}, 2.0, 2, verschiebung=verschiebung).spur()
        np.testing.assert_allclose(spur['values'], [0, 1, 0, 2.5, 5.25, 5.5], atol=1e-12)
