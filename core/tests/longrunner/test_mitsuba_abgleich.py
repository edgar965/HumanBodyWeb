# -*- coding: utf-8 -*-
"""Mitsuba gegen pyrender über `Genesishaarrender` (01.10.2026) — braucht Mitsuba mit CUDA und die Grafikkarte.

Dieselbe Kamera (Fotoprojektion und Sichtkörper rechnen sie nach), dieselbe UV-Richtung, Kennbild mit genau den
Kennfarben, Punktetausch = Neubau. Gemessen bei der Einführung: IoU 0,984–0,988 (Grundfigur + Viereck), am gebauten
Modell 0,991; Schwerpunkt ≤ 0,3 Pixel daneben.
"""
import tempfile
from pathlib import Path
from unittest import TestCase, skipUnless

import numpy as np
from django.conf import settings
from PIL import Image

from core.dienste.genesishaarrender import Genesishaarrender
from core.dienste.mitsubaszene import Mitsubaszene


def _bereit():
    try:
        return Mitsubaszene.mitsuba() is not None
    except Exception:  # noqa: BLE001 — ohne Mitsuba/CUDA wird übersprungen, nicht rot
        return False


def _figur():
    """Eine Kunstfigur: Säule mit asymmetrischem Arm (Umriss je Ansicht verschieden)."""
    import trimesh
    rumpf = trimesh.creation.cylinder(radius=0.15, height=1.6, sections=24)
    rumpf.apply_translation([0, 0, 0.8])
    arm = trimesh.creation.box(extents=[0.5, 0.08, 0.08])
    arm.apply_translation([0.35, 0.1, 1.3])
    netz = trimesh.util.concatenate([rumpf, arm])
    p = np.asarray(netz.vertices)[:, [0, 2, 1]] * np.array([1, 1, -1])      # Z oben → Y oben
    return p, np.asarray(netz.faces)


@skipUnless(_bereit(), 'Mitsuba (cuda_ad_rgb) nicht verfügbar')
class MitsubaAbgleichTest(TestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(dir=settings.MITSUBA_CACHE))
        self.p, self.d = _figur()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _maske(self, motor, winkel, kennung=False, teile=None):
        r = Genesishaarrender(None, motor=motor)
        pfad = self.ordner / ('%s_%d.png' % (motor, winkel))
        r.bild_teile(teile or [(self.p, self.d, (0.8, 0.7, 0.6))], winkel, pfad, groesse=(256, 384), kennung=kennung)
        r.schliessen()
        with Image.open(pfad) as b:
            return np.asarray(b.convert('RGBA'))

    def test_kamera_wie_pyrender(self):
        for winkel in (0, 30, 90, 180):
            a = self._maske('pyrender', winkel)[..., 3] > 127
            b = self._maske('mitsuba', winkel)[..., 3] > 127
            self.assertGreater((a & b).sum() / (a | b).sum(), 0.97, winkel)
            ya, xa = np.nonzero(a)
            yb, xb = np.nonzero(b)
            self.assertLess(abs(xa.mean() - xb.mean()), 1.0, winkel)
            self.assertLess(abs(ya.mean() - yb.mean()), 1.0, winkel)

    def test_kennbild_traegt_nur_kennfarben(self):
        bild = self._maske('mitsuba', 30, kennung=True, teile=[(self.p, self.d, (1.0, 0.0, 0.0))])
        drin = bild[..., 3] > 127
        self.assertEqual({tuple(int(c) for c in f) for f in np.unique(bild[drin][:, :3], axis=0)}, {(255, 0, 0)})
        self.assertEqual(set(np.unique(bild[..., 3]).tolist()), {0, 255})

    def test_punktetausch_gleich_neubau(self):
        r = Genesishaarrender(None, motor='mitsuba')
        verschoben = self.p + np.array([0.05, 0.0, 0.0])
        r.bild_teile([(self.p, self.d, (0.8, 0.7, 0.6))], 0, self.ordner / 'a.png', groesse=(256, 384))
        r.bild_teile([(verschoben, self.d, (0.8, 0.7, 0.6))], 0, self.ordner / 'b.png', groesse=(256, 384))
        r.schliessen()
        neu = Genesishaarrender(None, motor='mitsuba')
        neu.bild_teile([(verschoben, self.d, (0.8, 0.7, 0.6))], 0, self.ordner / 'c.png', groesse=(256, 384))
        neu.schliessen()
        with Image.open(self.ordner / 'b.png') as b, Image.open(self.ordner / 'c.png') as c:
            x, y = np.asarray(b)[..., 3] > 127, np.asarray(c)[..., 3] > 127
        self.assertGreater((x & y).sum() / (x | y).sum(), 0.99)
