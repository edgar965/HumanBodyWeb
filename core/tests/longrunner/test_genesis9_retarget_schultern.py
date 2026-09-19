# -*- coding: utf-8 -*-
u"""Genesis 9 an der Bibliothek: die Schultern haengen nicht mehr (19.09.2026).

Edgar, mit Bildschirmfoto einer Bewegung aus `A_Results`: „retarget zwischen
dem DEF und dem DAZ skeleton ist nicht richtig - schultern haengen".
Gemessen (`ProjektTemp/g9_schulter_messung.py`): das Oberarmgelenk lag in
jedem Bild 12,7 Grad unter der Richtung, die die BVH vorgibt — bei SMPL-X
(`A_Results/Dance1_smplx.bvh`, `0001_Dance.bvh`) wie bei CMU
(`A_Pose/13_07.bvh`). Ursache: Daz' `end_point` des Schluesselbeins liegt
12,5 Grad ueber dem `center_point` des Oberarms, die Richtungskorrektur
richtete die Achse aus, nicht das Gelenk (`Richtungskorrektur.
_gelenkrichtung`, `G9skelett.kette(gelenkrichtung=True)`).

Hier das Mass am ECHTEN Skelett: je zugeordnetem Paar (Knochen, Kind) der
Winkel zwischen Gelenk -> Kindgelenk in der BVH und im retargeteten
Genesis-9-Skelett. Nach der Aenderung 0,0 Grad auf allen Kettenpaaren;
die Sabotage-Gegenprobe rechnet ohne die Regel und muss die 12,7 wiederfinden.

Aufruf:  python manage.py test core.tests.longrunner.test_genesis9_retarget_schultern
"""
import os
import unittest

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from humanbody_core.quaternion import Quat
from humanbody_core.skeleton import Skeleton, SkeletonRigify
from humanbody_core.skeleton.formats.g9_zuordnung import G9zuordnung
from humanbody_core.skeleton.gelenkskelett import Gelenkskelett
from Genesis9.formung import G9formung
from Genesis9.pfade import G9pfade

BVH_WURZEL = os.path.join(str(settings.OBJECTS_ROOT), 'animations', 'bvh')
DATEIEN = [os.path.join(BVH_WURZEL, 'A_Results', 'Dance1_smplx.bvh'),
           os.path.join(BVH_WURZEL, 'A_Pose', '13_07.bvh')]
#: Gemessen am 19.09.2026 vor der Aenderung — mit Achse statt Gelenk.
HING = 12.7


class Gelenkpaare:
    u"""Winkel je (Knochen, Kind) zwischen BVH und retargetetem Ziel."""

    def __init__(self, bvh, zuordnung, kette, spuren):
        self.bvh = bvh
        self.zuordnung = zuordnung
        self.plan = kette.bauplan()
        self.spuren = spuren

    def messen(self, bilder):
        aus = {}
        for bild in bilder:
            q = self._bvh_welt(bild)
            z = self._ziel_welt(bild)
            for i, name in enumerate(self.bvh.names):
                g9 = self.zuordnung.get(name)
                if not g9 or g9 not in z:
                    continue
                for k in range(len(self.bvh.names)):
                    g9k = self.zuordnung.get(self.bvh.names[k])
                    if self.bvh.parents[k] != i or not g9k or g9k not in z:
                        continue
                    a, b = q[k] - q[i], z[g9k] - z[g9]
                    if np.linalg.norm(a) < 1e-9 or np.linalg.norm(b) < 1e-9:
                        continue
                    c = float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b))
                    aus.setdefault((g9, g9k), []).append(
                        float(np.degrees(np.arccos(np.clip(c, -1, 1)))))
        return {paar: max(werte) for paar, werte in aus.items()}

    def _bvh_welt(self, bild):
        welt_q = [None] * len(self.bvh.names)
        welt_p = [None] * len(self.bvh.names)
        for i in range(len(self.bvh.names)):
            e = self.bvh.parents[i]
            lokal = self.bvh.quats[bild][i]
            versatz = np.asarray(self.bvh.offsets[i], dtype=float)
            if e < 0:
                welt_q[i], welt_p[i] = lokal, versatz
            else:
                welt_q[i] = Quat.mul(welt_q[e], lokal)
                welt_p[i] = welt_p[e] + Quat.rotate(welt_q[e], versatz)
        return welt_p

    def _ziel_welt(self, bild):
        welt_q, welt_p = {}, {}
        for k in self.plan:
            lokal = np.asarray(k['quat'], dtype=float)
            spur = self.spuren.get(k['name'])
            if spur is not None:
                lokal = np.asarray(spur[bild * 4:bild * 4 + 4], dtype=float)
            eq = welt_q.get(k['eltern'], Quat.ID)
            ep = welt_p.get(k['eltern'], np.zeros(3))
            welt_q[k['name']] = Quat.norm(Quat.mul(eq, lokal))
            welt_p[k['name']] = ep + Quat.rotate(eq, np.asarray(k['pos'], dtype=float))
        return welt_p


@unittest.skipUnless(G9pfade.vorhanden() and all(os.path.isfile(p) for p in DATEIEN),
                     'Daz-Bibliothek oder die BVH-Dateien fehlen')
class SchulternTest(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.formung = G9formung({'BaseFeminine_figure_ctrl_Character': 1.0})

    def _paare(self, pfad, gelenkrichtung):
        bvh = SkeletonRigify.parse_bvh(pfad)
        bauart = Skeleton.detect_format(bvh.names)
        zuordnung = G9zuordnung.fuer(bauart)
        kette = self.formung.skelett().kette()
        self.assertTrue(kette.gelenkrichtung)   # `G9skelett.kette` setzt sie
        if not gelenkrichtung:
            kette = Gelenkskelett(self.formung.skelett().gelenkknochen())
        spuren = bauart.retarget_to_rigify(
            bvh, kette.geometrie(), body_height=1.70,
            mapping=zuordnung, skip_bones=G9zuordnung.ausnahmen(bauart),
            def_namen=G9zuordnung.defnamen()).tracks
        bilder = range(0, bvh.frame_count, max(1, bvh.frame_count // 10))
        return Gelenkpaare(bvh, zuordnung, kette, spuren).messen(bilder)

    def test_schultern_und_kette_treffen_die_bvh(self):
        for pfad in DATEIEN:
            paare = self._paare(pfad, True)
            for seite in ('l', 'r'):
                self.assertLess(paare[(seite + '_shoulder', seite + '_upperarm')], 0.1,
                                os.path.basename(pfad))
                self.assertLess(paare[(seite + '_upperarm', seite + '_forearm')], 0.2)
            # Alles, was die Richtungskorrektur ausrichtet: Knochen mit EINEM
            # Kind in der Kette — nicht Wurzel, nicht Ausnahmen (Fuesse, Kopf),
            # nicht die Hand (eigener Weg), nicht die Gabel `spine3` (dort zaehlt
            # der Hals; die Schultern haengen an `spine4`, 19 Grad seit je).
            eltern = [a for a, _ in paare]
            kette = [w for (a, b), w in paare.items()
                     if eltern.count(a) == 1
                     and a not in ('hip', 'l_foot', 'r_foot', 'l_hand', 'r_hand',
                                   'head', 'neck1')]
            self.assertGreaterEqual(len(kette), 10)   # CMU 11, SMPL-X 33
            self.assertLess(max(kette), 0.1, os.path.basename(pfad))

    def test_ohne_die_regel_haengen_sie_wie_am_19_09(self):
        u"""Sabotage-Gegenprobe: Achse statt Gelenk -> die 12,7 Grad sind wieder da."""
        paare = self._paare(DATEIEN[1], False)
        self.assertAlmostEqual(paare[('l_shoulder', 'l_upperarm')], HING, delta=0.3)
        self.assertAlmostEqual(paare[('r_shoulder', 'r_upperarm')], HING, delta=0.3)
