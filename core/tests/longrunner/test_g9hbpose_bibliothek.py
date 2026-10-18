# -*- coding: utf-8 -*-
u"""HumanBody-Posen auf Genesis 9 an der echten Daz-Bibliothek (`G9hbpose`, 17.10.2026).

WARUM (Edgar: „Human Body Poses auf Genesis - funktionieren die nicht?" — „baue die Übertragung"): Die
Pose `hb:<id>` wird zu Daz-Drehwinkeln; gebacken wird sie wie ein Daz-Preset. Von Hand gemessen
(`ProjektTemp/_wegwerf/hbpose_probe.py`): Weltbewegungen auf 0,0°, Glieder auf 0,0° in der
HumanBody-Richtung, 0,03–0,05 s je Pose.

1. T-Pose: Oberarm→Hand waagerecht (±5°), Oberschenkel→Fuß senkrecht (±2°) — in der GEBACKENEN Stellung.
2. sit_basic: die gebackenen Daz-Matrizen treffen die DEF-Weltbewegung von Kopf, Hals, Händen auf 0,5°.
3. `G9figur.formung` mit `hb:` liefert eine gedrehte Stellung; Griffe verändern die gemerkten Winkel nicht.
4. Unbekannte Pose: keine Drehung.

Braucht die Daz-Bibliothek (`G9pfade`) — ohne sie übersprungen, mit Grund.
"""
import unittest

import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.formung import G9formung  # noqa: E402
from Genesis9.pfade import G9pfade  # noqa: E402
from Genesis9.skelett import G9skelett  # noqa: E402

from core.api.g9figur import G9figur  # noqa: E402
from core.dienste.g9hbpose import G9hbpose  # noqa: E402

REGLER = {'BaseMasculine_figure_ctrl_Character': 1}


def gelenke(drehung):
    formung = G9formung.aus_abfrage(REGLER, drehung)
    return {k['name']: np.asarray(k['kopf']) for k in
            G9skelett(formung.formeln.knochen(), 0.0, formung.matrizen()).gelenkknochen()}


def drehwinkel(r):
    return float(np.degrees(np.arccos(np.clip((np.trace(r) - 1) / 2, -1, 1))))


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek mit Genesis 9 fehlt (G9pfade)')
class Bibliothek(SimpleTestCase):
    databases = set()

    def test_tpose(self):
        g = gelenke(G9hbpose.drehung('hb:rest_poses/t-pose', REGLER))
        for seite in 'lr':
            arm = g[seite + '_hand'] - g[seite + '_upperarm']
            self.assertLess(abs(np.degrees(np.arctan2(arm[1], np.hypot(arm[0], arm[2])))), 5, seite)
            bein = g[seite + '_foot'] - g[seite + '_thigh']
            self.assertLess(np.degrees(np.arccos(-bein[1] / np.linalg.norm(bein))), 2, seite)

    def test_sitzen_trifft_die_weltbewegung(self):
        drehung = G9hbpose.drehung('hb:charmorph/sit_basic', REGLER)
        ruhe_m = G9formung.aus_abfrage(REGLER).matrizen().matrizen()
        pose_m = G9formung.aus_abfrage(REGLER, drehung).matrizen().matrizen()
        ruhe, pose = G9hbpose.gestellt(G9hbpose._deltas('charmorph/sit_basic'))
        for d, g in (('DEF-spine.006', 'head'), ('DEF-spine.004', 'neck1'), ('DEF-hand.L', 'l_hand'),
                     ('DEF-hand.R', 'r_hand')):
            ist = pose_m[g][:3, :3] @ np.linalg.inv(ruhe_m[g][:3, :3])
            ist = ist / np.cbrt(np.linalg.det(ist))
            soll = pose[d][0] @ ruhe[d][0].T
            self.assertLess(drehwinkel(ist @ soll.T), 0.5, g)

    def test_formung_und_griffe(self):
        eintrag = G9figur._eintrag('basis') or {}
        vorher = {k: dict(v) for k, v in G9hbpose.drehung('hb:charmorph/sit_basic', REGLER).items()}
        formung = G9figur.formung({'regler': REGLER, 'pose': 'hb:charmorph/sit_basic', 'griffe': []}, eintrag)
        self.assertTrue(formung.drehung)
        self.assertEqual(G9hbpose.drehung('hb:charmorph/sit_basic', REGLER), vorher)

    def test_unbekannt(self):
        self.assertEqual(G9hbpose.drehung('hb:gibt/es_nicht', REGLER), {})
