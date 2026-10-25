# -*- coding: utf-8 -*-
"""MIA-Nachbau (`A:\\3DTools\\mesh3dai\\mesh3dai_miaeigen*.py`, 24.10.2026): die Teile, die ohne Karte und ohne MIAs Gewichte prüfbar sind.
Die Bitgleichheit des Ganzen gegen das Original (python11_mia) misst `ProjektTemp/_wegwerf/mia_port/alle_testnetze.py` (31 von 31 Testnetzen, 24.10.2026) — das braucht die Karte und
python11_mia und gehört nicht in die Suite.
    1  Sortierung: `aquicksort` (numpy 1.26.4) sortiert aufsteigend; ohne Gleichstand dieselbe Folge wie `np.argsort`
    2  Gleichstand: dieselbe Folge wie ein von Hand nachgerechneter Fall (Einfügesortierung, ≤ 16 Werte: stabil)
    3  Transformation: Verschiebung + Skalierung + Matrix, `inverse` bringt die Punkte zurück; Verschiebung und Skalierung umkehrbar ohne `torch.inverse`
    4  Würfelschnitt: mit und ohne Vorauswahl dieselben Punkte und Flächen (bitgleich)
    5  Konflikttabelle: Stichproben aus `bw_post_process` (Seiten, Finger, Rumpf gegen Unterarm), Diagonale frei
    6  Abtastung: `Miaeigenflaeche.proben` = `trimesh.sample.sample_surface` mit demselben Samen; `normalen_von` = `face_normals[idx]`
Sabotage-Gegenprobe (von Hand): in `Miaeigensortierung.aquicksort` `KLEIN` auf 0 → Fall 2 rot (Gleichstand anders geordnet); in `Miaeigenschnitt.wuerfel` `== 0` durch `!= 0` → Fall 4 rot;
in `Miaeigengewichte.tabelle` die Schleife über `KONFLIKTE` streichen → Fall 5 rot; in `Miaeigenflaeche.proben` `random_lengths -= 1.0` streichen → Fall 6 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

import torch  # noqa: E402
import trimesh  # noqa: E402

from mesh3dai_miaeigen_flaeche import Miaeigenflaeche  # noqa: E402
from mesh3dai_miaeigen_gewichte import Miaeigengewichte  # noqa: E402
from mesh3dai_miaeigen_knochen import Miaeigenknochen  # noqa: E402
from mesh3dai_miaeigen_schnitt import Miaeigenschnitt  # noqa: E402
from mesh3dai_miaeigen_sortierung import Miaeigensortierung  # noqa: E402
from mesh3dai_miaeigen_transform import Miatransform  # noqa: E402


class MiaeigenTest(unittest.TestCase):
    def test_1_sortierung_wie_argsort(self):
        rng = np.random.default_rng(3)
        for _ in range(50):
            v = rng.random(52).astype(np.float32)
            a = Miaeigensortierung.aquicksort(v)
            self.assertEqual(a, np.argsort(v, kind='stable').tolist())

    def test_2_gleichstand_einfuegesortierung(self):
        # ≤ 16 Werte: nur Einfügesortierung — gleich große bleiben in ihrer Reihenfolge
        v = np.array([0.5, 0.2, 0.5, 0.1, 0.2], dtype=np.float32)
        self.assertEqual(Miaeigensortierung.aquicksort(v), [3, 1, 4, 0, 2])

    def test_3_transformation_umkehrbar(self):
        p = torch.rand(1, 200, 3)
        verschiebung = Miatransform.verschiebung(torch.tensor([[0.3, -0.2, 0.1]]))
        t = verschiebung.compose(Miatransform.skalierung(torch.tensor([[2.0, 2.0, 2.0]])))
        dreh = [[0.0, -1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        g = t.compose(Miatransform(matrix=torch.tensor([dreh])))
        q = g.transform_points(p)
        torch.testing.assert_close(g.inverse().transform_points(q), p, rtol=0, atol=1e-6)
        kehr = Miatransform.skalierung(torch.tensor([[2.0, 4.0, 8.0]])).inverse().get_matrix()[0].diagonal()
        self.assertTrue(torch.equal(kehr, torch.tensor([0.5, 0.25, 0.125, 1.0])))

    def test_4_wuerfelschnitt_vorauswahl_gleich(self):
        kugel = trimesh.creation.icosphere(subdivisions=4)
        for mitte in ([0.9, 0.0, 0.0], [0.0, 0.5, 0.7]):
            m = np.array(mitte)
            v1, f1 = Miaeigenschnitt.wuerfel(kugel.vertices, kugel.faces, m, 0.6, vorauswahl=True)
            v2, f2 = Miaeigenschnitt.wuerfel(kugel.vertices, kugel.faces, m, 0.6, vorauswahl=False)
            self.assertTrue(len(f1) > 0)
            self.assertTrue(np.array_equal(v1, v2) and np.array_equal(f1, f2), mitte)

    def test_5_konflikttabelle(self):
        t = Miaeigengewichte.tabelle()
        k = Miaeigenknochen.index
        self.assertEqual(tuple(t.shape), (52, 52))
        self.assertTrue(bool(t[k('LeftHand'), k('RightHand')]))             # andere Hand
        self.assertTrue(bool(t[k('LeftHandIndex2'), k('LeftHandThumb1')]))  # anderer Finger derselben Hand
        self.assertTrue(bool(t[k('Hips'), k('LeftForeArm')]))               # Rumpf gegen Unterarm
        self.assertTrue(bool(t[k('LeftLeg'), k('Head')]))                   # Bein gegen Kopf
        self.assertFalse(bool(t[k('LeftHandIndex2'), k('LeftHandIndex1')]))  # derselbe Finger
        self.assertFalse(bool(t.diagonal().any()))

    def test_6_abtastung_wie_trimesh(self):
        kugel = trimesh.creation.icosphere(subdivisions=3)
        netz = Miaeigenflaeche(kugel.vertices, kugel.faces)
        s1, f1 = netz.proben(500, 1234)
        s2, f2 = trimesh.sample.sample_surface(kugel, 500, seed=1234)
        self.assertTrue(np.array_equal(f1, f2) and np.array_equal(s1, np.asarray(s2)))
        self.assertTrue(np.array_equal(netz.normalen_von(f1[:40]), kugel.face_normals[f1[:40]]))
        self.assertTrue(np.array_equal(netz.vertex_normals, kugel.vertex_normals))
