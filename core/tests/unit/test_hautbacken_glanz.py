# -*- coding: utf-8 -*-
"""`hautglanzkernel.korrektur_noetig` — wo Cycles beim Backen der Normalen die Normale der Glanz-Closures verändert (`ensure_valid_specular_reflection`, `kernel/closure/bsdf_util.h`).

Die Bedingung (Blender-Quelltext v5.2.2): `R = 2·(N·I)·N − I`, `dot(Ng, R) < min(0,9·dot(I, Ng), 0,01)` — beim Backen ist `I = wi` die geglättete Normale (`init_from_bake.h`: `ray.D = −N`),
also bei glatter Fläche `I = Ng`. Dann gilt `2·cos²θ − 1 < 0,01` für den Winkel θ zwischen N und Ng, das heißt θ > 44,7° (arccos(√0,505) = 44,71°). Die Rechnung ist von Hand nachprüfbar,
darum hier ohne Blender: Fälle um die Grenze, die Rückseite und `N = Ng` (dort greift die Korrektur nie, `isequal(sd->Ng, N)`).

Sabotage-Gegenprobe (11.10.2026): `hautglanzkernel.py` Schwelle `min(0.9·Iz, 0.01)` → `min(0.9·Iz, 0.5)` → Fall 1 und 3 rot (Fall 2 und 4 bleiben grün), danach rückgängig.
"""

import math

import numpy as np
import warp as wp
from django.test import SimpleTestCase

from core.dienste.hautbacken.graph import hautglanzkernel as glanz

GERAET = 'cuda:0'


def _lauf(n, ng, n_glatt, rueck):
    wp.init()
    k = len(n)
    aus = wp.zeros(k, dtype=wp.int32, device=GERAET)
    vec = lambda a: wp.array(np.asarray(a, dtype=np.float32), dtype=wp.vec3, device=GERAET)       # noqa: E731
    wp.launch(glanz.korrektur_noetig, dim=k, inputs=[vec(n), vec(ng), vec(n_glatt), wp.array(np.asarray(rueck, dtype=np.int32), dtype=wp.int32, device=GERAET), aus], device=GERAET)
    return aus.numpy()


def _geneigt(grad):
    """Einheitsvektor, um `grad` von der z-Achse (Ng) geneigt."""
    w = math.radians(grad)
    return (math.sin(w), 0.0, math.cos(w))


class GlanzkorrekturTest(SimpleTestCase):
    databases = set()

    def test_1_die_grenze_liegt_bei_44_7_grad(self):
        grenze = math.degrees(math.acos(math.sqrt(0.505)))
        self.assertAlmostEqual(grenze, 44.71, places=1)
        winkel = [0.5, 10, 30, 44.0, 44.5, 44.9, 45.5, 60, 80, 89]
        z = (0.0, 0.0, 1.0)
        aus = _lauf([_geneigt(w) for w in winkel], [z] * len(winkel), [z] * len(winkel), [0] * len(winkel))
        self.assertEqual(aus.tolist(), [int(w > grenze) for w in winkel])

    def test_2_n_gleich_ng_korrigiert_nie(self):
        z = (0.0, 0.0, 1.0)
        self.assertEqual(_lauf([z], [z], [z], [0]).tolist(), [0])

    def test_3_die_geglaettete_normale_als_blickrichtung(self):
        """Ist die geglättete Normale gegen Ng geneigt (glatte Fläche, Rand eines Dreiecks), ist `I = n_glatt`, nicht Ng: dieselbe Normale kann dann anders ausfallen."""
        ng = (0.0, 0.0, 1.0)
        n = _geneigt(40.0)
        gerade = _lauf([n], [ng], [ng], [0])[0]
        schief = _lauf([n], [ng], [_geneigt(-30.0)], [0])[0]
        self.assertEqual(int(gerade), 0)
        # Hand: I = (−sin30°, 0, cos30°); N·I = sin40°·(−sin30°) + cos40°·cos30° = −0,3214 + 0,6634 = 0,3420; R = 2·0,3420·N − I → R_z = 0,6840·0,7660 − 0,8660 = −0,3421 < 0,01
        self.assertEqual(int(schief), 1)

    def test_4_rueckseite_dreht_die_blickrichtung_zurueck(self):
        """Rückseite: Cycles kehrt Ng und die geglättete Normale um (`shader_setup_from_ray`), die Blickrichtung `wi = −ray.D` bleibt die geglättete Normale VOR der Umkehr.
        Von Hand: Ng0 = (0, 0, 1), N0 = (0,9, 0, −0,4359) (Skalarprodukt < 0: Rückseite) → nach der Umkehr Ng = (0, 0, −1), n_glatt = (−0,9, 0, 0,4359), wi = N0.
        Schattungsnormale N = (−sin60°, 0, −cos60°): N·wi = −0,5614, R = 2·(N·wi)·N − wi = (0,0724, 0, 0,9973), dot(Ng, R) = −0,9973 < 0,01 → Korrektur.
        Mit `wi = n_glatt` (ohne Rückdrehung) wäre R = (−0,0724, 0, −0,9973) und dot(Ng, R) = +0,9973 → keine Korrektur."""
        ng = (0.0, 0.0, -1.0)
        n = (-math.sin(math.radians(60)), 0.0, -math.cos(math.radians(60)))
        n_glatt = (-0.9, 0.0, math.sqrt(1.0 - 0.81))
        self.assertEqual(int(_lauf([n], [ng], [n_glatt], [1])[0]), 1)
        self.assertEqual(int(_lauf([n], [ng], [n_glatt], [0])[0]), 0)
