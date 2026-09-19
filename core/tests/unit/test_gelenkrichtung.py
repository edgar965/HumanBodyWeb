# -*- coding: utf-8 -*-
u"""Gelenk zu Gelenk: das Kindgelenk landet dort, wohin die BVH zeigt.

DER BEFUND (19.09.2026, Edgar an Genesis 9: „schultern haengen"): Daz'
`end_point` sitzt nicht am `center_point` des Kindes — das Schluesselbein
zeigt 9 Grad nach oben, das Oberarmgelenk liegt 4 Grad darunter. Die
Richtungskorrektur legte die ACHSE auf die BVH-Richtung, und das
Oberarmgelenk hing 12,7 Grad zu tief, in jedem Bild
(`ProjektTemp/g9_schulter_messung.py`).

HIER MIT KUNSTDATEN, ohne Daz-Bibliothek: ein Zielskelett aus Gelenkpunkten
(`Gelenkskelett`), dessen Schluesselbein-Schwanz 10 Grad ueber, dessen
Oberarmgelenk 5 Grad unter der Waagrechten liegt (15 Grad dazwischen), und
die Mixamo-BVH der UMA-Attrappe (Schluesselbein waagrecht). Gemessen wird
der Winkel zwischen Gelenk -> Kindgelenk im Ziel (Vorwaertskinematik aus den
Spuren) und derselben Richtung in der BVH.

Sabotage-Gegenprobe (baut die Pruefung selbst ein): OHNE `gelenkrichtung`
haengt das Oberarmgelenk um die eingebauten 15 Grad — dieselbe Rechnung,
die bis heute fuer Genesis 9 lief. Faellt der Zweig in
`Richtungskorrektur._gelenkrichtung` weg, wird Fall 1 rot.

Aufruf:  python manage.py test core.tests.unit.test_gelenkrichtung
"""
import math
import shutil
import tempfile
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton import SkeletonGeometry, parse_bvh  # noqa: E402
from humanbody_core.skeleton.gelenkskelett import Gelenkskelett  # noqa: E402
from humanbody_core.skeleton.retarget.motor import retarget_bvh_to_rigify  # noqa: E402

from ._umaattrappe import Umaattrappe

#: Achse des Schluesselbeins ueber, Oberarmgelenk unter der Waagrechten (Grad).
ACHSE_HOCH = 10.0
GELENK_TIEF = 5.0


def _gerade(kette):
    u"""``[(name, eltern, kopf, schwanz)]`` -> Gelenkskelett-Zeilen."""
    return [{'name': n, 'eltern': e, 'kopf': list(k), 'schwanz': list(s)}
            for n, e, k, s in kette]


def zielknochen():
    u"""Rumpf, Arme in A-Pose, Beine — Namen wie in der Mixamo-BVH."""
    s = (0.05, 1.38, 0.0)
    achse = np.array([math.cos(math.radians(ACHSE_HOCH)),
                      math.sin(math.radians(ACHSE_HOCH)), 0.0]) * 0.10
    gelenk = np.array([math.cos(math.radians(GELENK_TIEF)),
                       -math.sin(math.radians(GELENK_TIEF)), 0.0]) * 0.12
    arm = np.array([0.18, -0.18, 0.0])
    la = tuple(np.add(s, gelenk))
    lf = tuple(np.add(la, arm))
    lh = tuple(np.add(lf, arm))
    kette = [
        ('Hips', None, (0, 1.0, 0), (0, 1.1, 0)),
        ('Spine', 'Hips', (0, 1.1, 0), (0, 1.2, 0)),
        ('Spine1', 'Spine', (0, 1.2, 0), (0, 1.3, 0)),
        ('Spine2', 'Spine1', (0, 1.3, 0), (0, 1.4, 0)),
        ('Neck', 'Spine2', (0, 1.4, 0), (0, 1.5, 0)),
        ('Head', 'Neck', (0, 1.5, 0), (0, 1.6, 0)),
        ('LeftShoulder', 'Spine2', s, tuple(np.add(s, achse))),
        ('LeftArm', 'LeftShoulder', la, lf),
        ('LeftForeArm', 'LeftArm', lf, lh),
        ('LeftHand', 'LeftForeArm', lh, tuple(np.add(lh, arm * 0.4))),
        ('LeftUpLeg', 'Hips', (0.1, 1.0, 0), (0.1, 0.55, 0)),
        ('LeftLeg', 'LeftUpLeg', (0.1, 0.55, 0), (0.1, 0.1, 0)),
        ('LeftFoot', 'LeftLeg', (0.1, 0.1, 0), (0.1, 0.05, 0.15)),
    ]
    spiegel = []
    for n, e, k, sch in kette:
        if not n.startswith('Left'):
            continue
        sp = lambda p: (-p[0], p[1], p[2])  # noqa: E731
        spiegel.append(('Right' + n[4:], ('Right' + e[4:]) if e.startswith('Left') else e,
                        sp(k), sp(sch)))
    return _gerade(kette + spiegel)


class Gelenkprobe:
    u"""Gelenklagen in Welt — aus den Spuren (Ziel) und aus der BVH."""

    @staticmethod
    def ziel(kette, spuren, bild):
        welt_q, welt_p = {}, {}
        for k in kette.bauplan():
            lokal = np.asarray(k['quat'], dtype=float)
            spur = spuren.get(k['name'])
            if spur is not None:
                lokal = np.asarray(spur[bild * 4:bild * 4 + 4], dtype=float)
            eq = welt_q.get(k['eltern'], Quat.ID)
            ep = welt_p.get(k['eltern'], np.zeros(3))
            welt_q[k['name']] = Quat.norm(Quat.mul(eq, lokal))
            welt_p[k['name']] = ep + Quat.rotate(eq, np.asarray(k['pos'], dtype=float))
        return welt_p

    @staticmethod
    def bvh(bvh, bild):
        welt_q = [None] * len(bvh.names)
        welt_p = [None] * len(bvh.names)
        for i in range(len(bvh.names)):
            e = bvh.parents[i]
            lokal = bvh.quats[bild][i]
            if e < 0:
                welt_q[i] = lokal
                welt_p[i] = np.asarray(bvh.offsets[i], dtype=float)
            else:
                welt_q[i] = Quat.mul(welt_q[e], lokal)
                welt_p[i] = welt_p[e] + Quat.rotate(
                    welt_q[e], np.asarray(bvh.offsets[i], dtype=float))
        return dict(zip(bvh.names, welt_p))

    @staticmethod
    def winkel(a, b):
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        c = float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b))
        return math.degrees(math.acos(max(-1.0, min(1.0, c))))


class GelenkrichtungTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.ordner = tempfile.mkdtemp(prefix='gelenkrichtung_', dir=str(basis))
        pfad = Path(cls.ordner) / 'probe.bvh'
        pfad.write_text(Umaattrappe.bvh_text(
            [{}, {'LeftShoulder': (0, 0, -20)}, {'LeftArm': (-45, 0, 0)}]),
            encoding='utf-8')
        cls.bvh = parse_bvh(str(pfad))
        cls.mapping = {name: name for name in cls.bvh.names}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.ordner, True)
        super().tearDownClass()

    def _paarfehler(self, gelenkrichtung, eltern, kind):
        u"""Winkel Ziel gegen BVH fuer das Paar, ueber die drei Bilder (max)."""
        kette = Gelenkskelett(zielknochen(), gelenkrichtung=gelenkrichtung)
        spuren = retarget_bvh_to_rigify(
            self.bvh, kette.geometrie(), mapping=self.mapping, skip_bones=[]).tracks
        fehler = []
        for bild in range(self.bvh.frame_count):
            z = Gelenkprobe.ziel(kette, spuren, bild)
            q = Gelenkprobe.bvh(self.bvh, bild)
            fehler.append(Gelenkprobe.winkel(z[kind] - z[eltern], q[kind] - q[eltern]))
        return max(fehler)

    def test_die_attrappe_hat_den_daz_versatz(self):
        u"""Achse des Schluesselbeins gegen Gelenk -> Oberarmgelenk: 15 Grad."""
        knochen = {k['name']: k for k in zielknochen()}
        s = knochen['LeftShoulder']
        achse = np.subtract(s['schwanz'], s['kopf'])
        zum_kind = np.subtract(knochen['LeftArm']['kopf'], s['kopf'])
        self.assertAlmostEqual(Gelenkprobe.winkel(achse, zum_kind),
                               ACHSE_HOCH + GELENK_TIEF, delta=0.01)

    def test_mit_gelenkrichtung_folgt_das_oberarmgelenk_der_bvh(self):
        self.assertLess(self._paarfehler(True, 'LeftShoulder', 'LeftArm'), 0.5)
        self.assertLess(self._paarfehler(True, 'RightShoulder', 'RightArm'), 0.5)

    def test_ohne_gelenkrichtung_haengt_es_um_den_eingebauten_winkel(self):
        u"""Die alte Rechnung — der Befund vom 19.09.2026 in Zahlen."""
        self.assertAlmostEqual(self._paarfehler(False, 'LeftShoulder', 'LeftArm'),
                               ACHSE_HOCH + GELENK_TIEF, delta=0.5)

    def test_der_oberarm_selbst_bleibt_in_beiden_rechnungen_exakt(self):
        u"""Sein Schwanz sitzt am Kindgelenk: Achse = Gelenk -> Gelenk."""
        for gelenkrichtung in (True, False):
            self.assertLess(self._paarfehler(gelenkrichtung, 'LeftArm', 'LeftForeArm'), 0.5)

    def test_die_gegenprobe_bewegt_das_schluesselbein_wirklich(self):
        q0 = Gelenkprobe.bvh(self.bvh, 0)
        q1 = Gelenkprobe.bvh(self.bvh, 1)
        self.assertAlmostEqual(Gelenkprobe.winkel(
            q0['LeftArm'] - q0['LeftShoulder'], q1['LeftArm'] - q1['LeftShoulder']),
            20.0, delta=0.01)

    def test_rigify_fuehrt_die_regel_nicht(self):
        u"""Rigify sitzt verbunden (0,0 Grad, `def_knochenachsen_messung.py`);
        die Vorgabe bleibt aus, damit es bitgleich rechnet."""
        skel = SkeletonGeometry.from_json(
            str(settings.HUMANBODY_DATA_DIR / 'def_skeleton.json'))
        self.assertFalse(skel.gelenkrichtung)
        self.assertFalse(Gelenkskelett(zielknochen()).geometrie().gelenkrichtung)
        self.assertTrue(Gelenkskelett(zielknochen(), gelenkrichtung=True)
                        .geometrie().gelenkrichtung)
