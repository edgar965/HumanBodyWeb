# -*- coding: utf-8 -*-
"""Hals und Kopf folgen auf UMA und Genesis 9 der Quelle — nicht der eigenen Ruhelage.

WARUM (Edgar, 19.09.2026, Vergleichsseite mit `A_Results/Dance1_smplx`):
„fixe retarget für UMA und Genesis. Der Halswirbel macht einen Knick".
`FUESSE_UND_KOPF` nimmt Hals und Kopf aus der Richtungskorrektur, weil
Rigify drei Halsknochen hat, wo die Videoformate zwei haben. UMA und
Genesis 9 übersetzten die Liste mit — und behielten damit ihre eigene
Halsform (Kopf 6 bzw. 9 Grad vor dem Hals) statt die der Quelle (SMPL-X:
20 Grad): Hals 13 bzw. 8 Grad neben der Quelle, Kopfachse 21 bzw. 18 —
in jedem Bild. Seither lässt `ausnahmen()` beider Ziele
`HALS_NUR_RIGIFY` weg (`richtungsausnahmen.py`).

Geprüft an einer synthetischen Kette ohne Produktivdaten: eine SMPL-X-BVH,
deren Kopf 20 Grad vor dem Hals sitzt, auf ein Ziel, dessen Hals gerade
steht. Mit der neuen Liste zeigt der Zielhals dorthin, wo der Quellhals
zeigt (< 1 Grad); mit der alten (Gegenprobe) bleibt er 20 Grad daneben.

Aufruf:  python manage.py test core.tests.unit.test_halsknick_fremde_ziele
"""

import math

import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton import Skeleton  # noqa: E402
from humanbody_core.skeleton.formats.g9_zuordnung import G9zuordnung  # noqa: E402
from humanbody_core.skeleton.formats.richtungsausnahmen import (  # noqa: E402
    FUESSE_UND_KOPF,
    HALS_NUR_RIGIFY,
)
from humanbody_core.skeleton.formats.uma_knochen import Umazuordnung  # noqa: E402
from humanbody_core.skeleton.retarget.bvhdaten import BVHData  # noqa: E402
from humanbody_core.skeleton.skeleton_geometry import SkeletonGeometry  # noqa: E402

#: Der Kopf sitzt in der Quelle 20 Grad vor dem Hals (SMPL-X: 20,4).
NEIGUNG = math.radians(20.0)
QUELLKETTE = ['Pelvis', 'Spine1', 'Spine2', 'Spine3', 'Neck', 'Head']
ZIELKETTEN = {
    'uma': (['Hips', 'LowerBack', 'Spine', 'Spine1', 'Neck', 'Head'], Umazuordnung, False),
    'genesis9': (['hip', 'spine1', 'spine2', 'spine3', 'spine4', 'neck1', 'neck2', 'head'],
                 G9zuordnung, True),
}
IDENTITAET = [0.0, 0.0, 0.0, 1.0]


class Halskette:
    """Quelle und Ziel als gerade Ketten — nur der Quellkopf lehnt nach vorn."""

    @staticmethod
    def bvh(bilder=2):
        namen = QUELLKETTE
        eltern = np.array([-1, 0, 1, 2, 3, 4])
        versaetze = np.array([[0.0, 100.0, 0.0]] + [[0.0, 20.0, 0.0]] * 4
                             + [[0.0, 10.0 * math.cos(NEIGUNG), 10.0 * math.sin(NEIGUNG)]])
        quats = np.tile(np.array(IDENTITAET), (bilder, len(namen), 1))
        positionen = np.zeros((bilder, len(namen), 3))
        kinder = {i: [i + 1] for i in range(len(namen) - 1)}
        return BVHData(namen, eltern, versaetze, quats, positionen, 1 / 30, bilder, kinder)

    @staticmethod
    def ziel(namen, gelenkrichtung):
        knochen = [{'name': name, 'parent': namen[i - 1] if i else None,
                    'local_position': [0.0, 1.0 if i else 0.0, 0.0],
                    'local_quaternion': IDENTITAET}
                   for i, name in enumerate(namen)]
        return SkeletonGeometry.from_three(knochen, richtungsachse=[0, 1, 0],
                                           gelenkrichtung=gelenkrichtung)

    @staticmethod
    def halsrichtung(skel, spuren, hals, kopf, bild=1):
        """Welt-Richtung Halsgelenk -> Kopfgelenk im Ziel."""
        welt_q, welt_p = {}, {}
        for name in skel.bone_order:
            bone = skel.bones[name]
            spur = spuren.get(name)
            lokal = np.asarray(spur[bild * 4:bild * 4 + 4]) if spur else bone.local_quat
            eq = welt_q.get(bone.parent_name, Quat.ID)
            ep = welt_p.get(bone.parent_name, np.zeros(3))
            welt_q[name] = Quat.norm(Quat.mul(eq, lokal))
            welt_p[name] = ep + Quat.rotate(eq, bone.local_pos)
        weg = welt_p[kopf] - welt_p[hals]
        return weg / np.linalg.norm(weg)


class HalsknickFremdeZiele(SimpleTestCase):
    databases = set()

    def _winkel_zur_quelle(self, ziel, ausnahmen):
        namen, zuordnung, gelenkrichtung = ZIELKETTEN[ziel]
        bauart = Skeleton.get_format('SMPLX')
        skel = Halskette.ziel(namen, gelenkrichtung)
        spuren = bauart.retarget_to_rigify(
            Halskette.bvh(), skel, body_height=1.68, mapping=zuordnung.fuer(bauart),
            skip_bones=ausnahmen, def_namen=zuordnung.defnamen()).als_dict()['tracks']
        zu = zuordnung.fuer(bauart)
        richtung = Halskette.halsrichtung(skel, spuren, zu['Neck'], zu['Head'])
        quelle = np.array([0.0, math.cos(NEIGUNG), math.sin(NEIGUNG)])
        return math.degrees(math.acos(float(np.clip(np.dot(richtung, quelle), -1, 1))))

    def test_hals_und_kopf_bleiben_bei_rigify_in_der_liste(self):
        for name in HALS_NUR_RIGIFY:
            self.assertIn(name, FUESSE_UND_KOPF)
            self.assertIn(name, Skeleton.get_format('SMPLX').SKIP_DIR_CORRECTION)

    def test_fremde_ziele_uebersetzen_fuesse_aber_nicht_hals_und_kopf(self):
        for fmt in ('SMPLX', 'AIST', 'MOCAPNET', 'OPENPOSE'):
            bauart = Skeleton.get_format(fmt)
            uma = Umazuordnung.ausnahmen(bauart)
            g9 = G9zuordnung.ausnahmen(bauart)
            self.assertTrue({'LeftFoot', 'RightToeBase'} <= set(uma), (fmt, uma))
            self.assertTrue({'l_foot', 'r_toes'} <= set(g9), (fmt, g9))
            self.assertFalse({'Neck', 'Head'} & set(uma), (fmt, uma))
            self.assertFalse({'neck1', 'head'} & set(g9), (fmt, g9))

    def test_daz_bvh_auf_genesis9_laesst_weiter_alles_aus(self):
        """Gleiches Skelett auf beiden Seiten — dort bleibt die ganze Liste."""
        g9 = G9zuordnung.ausnahmen(Skeleton.get_format('GENESIS9'))
        self.assertTrue({'neck1', 'head', 'l_foot'} <= set(g9))

    def test_der_zielhals_zeigt_wohin_der_quellhals_zeigt(self):
        bauart = Skeleton.get_format('SMPLX')
        for ziel, (_, zuordnung, _) in ZIELKETTEN.items():
            winkel = self._winkel_zur_quelle(ziel, zuordnung.ausnahmen(bauart))
            self.assertLess(winkel, 1.0, (ziel, winkel))

    def test_gegenprobe_mit_der_alten_liste_bleibt_der_knick(self):
        bauart = Skeleton.get_format('SMPLX')
        for ziel, (_, zuordnung, _) in ZIELKETTEN.items():
            zu = zuordnung.fuer(bauart)
            alt = zuordnung.ausnahmen(bauart) + [zu['Neck'], zu['Head']]
            winkel = self._winkel_zur_quelle(ziel, alt)
            self.assertAlmostEqual(winkel, 20.0, delta=0.5, msg=(ziel, winkel))
