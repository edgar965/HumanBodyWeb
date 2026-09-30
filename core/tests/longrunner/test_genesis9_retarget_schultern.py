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
die Sabotage-Gegenprobe rechnet ohne die Regel und muss die Abweichung
wiederfinden.

WAS SEITDEM DAZUKAM (Stand 30.09.2026) — beides bewusst, der Test kennt es:
* Fassung 11 (19.09. nachmittags): die Schluesselbeine gehen NICHT mehr durch die
  Richtungskorrektur (`G9zuordnung.SCHULTERN`, „Stiernacken"). Das Paar
  Schluesselbein -> Oberarm misst seither die Ruhelagen-Differenz (Dance1 8,6/9,1,
  CMU 23/30 Grad) und gehoert nicht mehr in die Kette; die 12,7 Grad der Sabotage
  gibt es dort nicht mehr — sie zeigt sich an der Wirbelsaeule (`spine1 -> spine3`).
* Fassung 12 (24.09.): `Abstandswahrung` dreht den Oberarm je Bild aus dem Bein
  (Dance1 bis 13 Grad). Sie ist Edgars Wunsch, aber nicht die Gelenkrichtung;
  dieser Test misst die Regel und rechnet deshalb ohne sie (`test_abstandswahrung`
  prueft sie selbst).

Aufruf:  python manage.py test core.tests.longrunner.test_genesis9_retarget_schultern
"""
import os
import unittest
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from humanbody_core.quaternion import Quat
from humanbody_core.skeleton import Skeleton, SkeletonRigify
from humanbody_core.skeleton.formats.g9_zuordnung import SCHULTERN, G9zuordnung
from humanbody_core.skeleton.gelenkskelett import Gelenkskelett
from humanbody_core.skeleton.retarget.abstandswahrung import Abstandswahrung
from Genesis9.formung import G9formung
from Genesis9.pfade import G9pfade

BVH_WURZEL = os.path.join(str(settings.OBJECTS_ROOT), 'animations', 'bvh')
DATEIEN = [os.path.join(BVH_WURZEL, 'A_Results', 'Dance1_smplx.bvh'),
           os.path.join(BVH_WURZEL, 'A_Pose', '13_07.bvh')]
#: `spine1 -> spine3` an 13_07 ohne die Regel (Achse statt Gelenk), gemessen 30.09.2026;
#: Daz' `end_point` von `spine2` sitzt 8,8 Grad neben dem Gelenk.
WIRBEL_OHNE_REGEL = 5.44


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
        # Ohne `Abstandswahrung` (Fassung 12): sie dreht den Oberarm bewusst aus der
        # Quellrichtung. Die Umleitung muss greifen, sonst misst der Test wieder mit ihr.
        with mock.patch.object(Abstandswahrung, 'korrigieren', autospec=True) as aus:
            spuren = bauart.retarget_to_rigify(
                bvh, kette.geometrie(), body_height=1.70,
                mapping=zuordnung, skip_bones=G9zuordnung.ausnahmen(bauart),
                def_namen=G9zuordnung.defnamen()).tracks
        self.assertGreater(aus.call_count, 0, 'Abstandswahrung lief nicht ueber die Umleitung')
        bilder = range(0, bvh.frame_count, max(1, bvh.frame_count // 10))
        return Gelenkpaare(bvh, zuordnung, kette, spuren).messen(bilder)

    def test_schultern_und_kette_treffen_die_bvh(self):
        for pfad in DATEIEN:
            paare = self._paare(pfad, True)
            for seite in ('l', 'r'):
                self.assertLess(paare[(seite + '_upperarm', seite + '_forearm')], 0.2)
            # Die Schluesselbeine sind Ausnahme der Richtungskorrektur (Fassung 11): sie
            # behalten Daz' Ruhelage, der Oberarm seine absolute Richtung.
            bauart = Skeleton.detect_format(SkeletonRigify.parse_bvh(pfad).names)
            for seite in SCHULTERN:
                self.assertIn(seite, G9zuordnung.ausnahmen(bauart), os.path.basename(pfad))
            # Alles, was die Richtungskorrektur ausrichtet: Knochen mit EINEM
            # Kind in der Kette — nicht Wurzel, nicht Ausnahmen (Fuesse, Kopf,
            # Schluesselbeine), nicht die Hand (eigener Weg), nicht die Gabel `spine3`
            # (dort zaehlt der Hals; die Schultern haengen an `spine4`, 19 Grad seit je).
            eltern = [a for a, _ in paare]
            kette = [w for (a, b), w in paare.items()
                     if eltern.count(a) == 1
                     and a not in ('hip', 'l_foot', 'r_foot', 'l_hand', 'r_hand',
                                   'head', 'neck1') + SCHULTERN]
            self.assertGreaterEqual(len(kette), 9)   # CMU 9, SMPL-X 31
            self.assertLess(max(kette), 0.1, os.path.basename(pfad))

    def test_ohne_die_regel_knickt_die_wirbelsaeule(self):
        u"""Sabotage-Gegenprobe: Achse statt Gelenk -> die Abweichung ist wieder da.

        Am 19.09. zeigte sie sich an den Schultern (12,7 Grad); die gehen seit Fassung 11
        nicht mehr durch die Korrektur, die Regel wirkt dort nicht mehr — belegt unten.
        """
        mit = self._paare(DATEIEN[1], True)
        ohne = self._paare(DATEIEN[1], False)
        self.assertLess(mit[('spine1', 'spine3')], 0.1)
        self.assertAlmostEqual(ohne[('spine1', 'spine3')], WIRBEL_OHNE_REGEL, delta=0.3)
        for seite in ('l', 'r'):
            paar = (seite + '_shoulder', seite + '_upperarm')
            self.assertAlmostEqual(ohne[paar], mit[paar], delta=1e-3)
