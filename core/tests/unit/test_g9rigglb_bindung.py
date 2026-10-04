# -*- coding: utf-8 -*-
"""Bindematrizen des GLB-Schreibers `G9rigglb` (03.10.2026): „Knotenwelt × Bindematrix" ist in der Ruhelage die Einheitsmatrix.

Bis 03.10.2026 schrieb `G9rigglb.skelett` nur die Verschiebung um das negative Weltgelenk. Mit den Ruhedrehungen der Knoten (`quat`) ergab das
in der Ruhelage keine Einheitsmatrix, sondern eine Drehung um das Gelenk: in Blender lagen 22.511 von 27.087 Punkten der Grundfigur mehr als 1 cm
neben ihrer Lage im Netz (höchstens 687 mm), die Figur „zerriss" im Film. Kunstskelett, keine Daz-Bibliothek, keine Datenbank."""

import numpy as np
from django.test import SimpleTestCase
from Genesis9.rigglb import G9rigglb


class G9rigglbBindungTest(SimpleTestCase):
    #: Hüfte, Wirbel um 90° um Z gedreht, Kopf 0,3 m entlang der gedrehten x-Achse (Welt: nach oben) — `pos`/`quat` elternrelativ wie
    #: `Gelenkskelett.bauplan()`, `kopf` die Weltlage des Gelenks.
    KNOCHEN = [
        {'name': 'hip', 'eltern': None, 'kopf': [0.0, 1.0, 0.0], 'pos': [0.0, 1.0, 0.0], 'quat': [0, 0, 0, 1]},
        {'name': 'spine1', 'eltern': 'hip', 'kopf': [0.0, 1.2, 0.0], 'pos': [0.0, 0.2, 0.0], 'quat': [0, 0, 0.7071068, 0.7071068]},
        {'name': 'head', 'eltern': 'spine1', 'kopf': [0.0, 1.5, 0.0], 'pos': [0.3, 0.0, 0.0], 'quat': [0, 0, 0, 1]},
    ]

    def _binden(self, knochen):
        glb = G9rigglb()
        gelenke, wurzel, bind = glb.skelett(knochen)
        return glb, gelenke, wurzel, bind

    def test_knotenwelt_mal_bindematrix_ist_die_einheit(self):
        glb, gelenke, _wurzel, bind = self._binden(self.KNOCHEN)
        lage = glb.welt(gelenke)
        self.assertEqual(bind.shape, (3, 16))
        for i, g in enumerate(gelenke):
            # glTF speichert spaltenweise: die gelesene Matrix ist die transponierte
            np.testing.assert_allclose(lage[g] @ bind[i].reshape(4, 4).T, np.eye(4), atol=1e-5)

    def test_die_ruhedrehung_steckt_in_der_bindematrix(self):
        """Gegenprobe: die reine Verschiebung (der alte Stand) wäre für den gedrehten Wirbel keine Einheit."""
        glb, gelenke, _wurzel, _bind = self._binden(self.KNOCHEN)
        lage = glb.welt(gelenke)
        alt = np.eye(4)
        alt[:3, 3] = -np.asarray(self.KNOCHEN[1]['kopf'])
        self.assertGreater(np.abs(lage[gelenke[1]] @ alt - np.eye(4)).max(), 0.5)

    def test_das_weltgelenk_liegt_am_kopf_des_knochens(self):
        glb, gelenke, _wurzel, _bind = self._binden(self.KNOCHEN)
        lage = glb.welt(gelenke)
        for g, k in zip(gelenke, self.KNOCHEN):
            np.testing.assert_allclose(lage[g][:3, 3], k['kopf'], atol=1e-6)
