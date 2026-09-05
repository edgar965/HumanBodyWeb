# -*- coding: utf-8 -*-
u"""`Gltfskelett` — das Skelett aus einer GLB, ohne das Netz zu lesen.

WARUM (05.09.2026): Die UMA-GLB hat drei Eigenheiten, die ein naiver Leser
falsch macht — Joints doppelt in der Liste, Nicht-Joint-Vorfahren mit einer
halben Drehung, und eine Bindpose, die nicht die Knotenpose ist. Jede davon
ergibt keinen Fehler, sondern ein Skelett, das „irgendwie schief" steht.

Die GLB hier ist synthetisch (`Umaattrappe.glb_beispiel`) und wird in ein
Wegwerf-Verzeichnis unter `ProjektTemp/` geschrieben — nie ins System-Temp.

Aufruf:  python manage.py test core.tests.unit.test_gltfskelett
"""
import shutil
import tempfile
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._umaattrappe import Umaattrappe
from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton import SkeletonGeometry  # noqa: E402
from humanbody_core.skeleton.gltfskelett import Gltfskelett  # noqa: E402


class GltfskelettTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.ordner = tempfile.mkdtemp(prefix='gltfskelett_', dir=str(basis))
        gltf, binaer = Umaattrappe.glb_beispiel()
        cls.pfad = Path(cls.ordner) / 'probe.glb'
        cls.pfad.write_bytes(Umaattrappe.glb_bytes(gltf, binaer))
        cls.skelett = Gltfskelett(cls.pfad)
        cls.anzahl = len(Umaattrappe.uma_knochen())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.ordner, True)
        super().tearDownClass()

    def _knochen(self, pose=Gltfskelett.KNOTENPOSE):
        return {k['name']: k for k in self.skelett.knochen(pose)}

    # ------------------------------------------------------------- Struktur

    def test_joints_kommen_einmal(self):
        u"""`Hips` steht zweimal in der Joint-Liste — und einmal im Skelett."""
        namen = self.skelett.namen()
        self.assertEqual(len(namen), len(set(namen)))
        self.assertEqual(len(namen), self.anzahl)

    def test_nicht_joints_gehoeren_nicht_dazu(self):
        namen = set(self.skelett.namen())
        self.assertNotIn('Avatar', namen)
        self.assertNotIn('Root', namen)
        self.assertNotIn('Netz', namen)

    def test_eltern_vor_kindern(self):
        gesehen = set()
        for k in self.skelett.knochen():
            if k['parent']:
                self.assertIn(k['parent'], gesehen, k['name'])
            gesehen.add(k['name'])

    def test_eine_datei_ohne_magie_ist_keine_glb(self):
        falsch = Path(self.ordner) / 'falsch.glb'
        falsch.write_bytes(b'{"nicht": "glb"}')
        with self.assertRaises(ValueError):
            Gltfskelett(falsch)

    def test_eine_zu_kurze_datei_ist_ein_valueerror_kein_struct_error(self):
        u"""9 Byte: `struct` wuerde einen eigenen Fehler werfen, und der
        Endpunkt faengt nur ValueError — die Seite saehe einen Stack."""
        kurz = Path(self.ordner) / 'kurz.glb'
        kurz.write_bytes(b'kein glTF')
        with self.assertRaises(ValueError):
            Gltfskelett(kurz)

    # ----------------------------------------------------------- Knotenpose

    def test_die_wurzel_traegt_die_drehung_der_vorfahren(self):
        u"""`Avatar` (halbe Drehung um Y) ist kein Joint — seine Drehung
        landet in `Global`, sonst stuende das Skelett verkehrt herum."""
        wurzel = self._knochen()['Global']
        self.assertIsNone(wurzel['parent'])
        q = np.array(wurzel['local_quaternion'])
        self.assertTrue(np.allclose(np.abs(q), np.abs(Umaattrappe.YAW_180),
                                    atol=1e-6), q)

    def test_kinder_behalten_ihre_lokale_lage(self):
        knochen = self._knochen()
        self.assertEqual(knochen['Hips']['parent'], 'Position')
        self.assertTrue(np.allclose(knochen['Hips']['local_position'], [0, 1.0, 0]))
        self.assertTrue(np.allclose(knochen['LeftArm']['local_position'],
                                    [0, 0.1, 0], atol=1e-6))

    def test_skalierung_geht_in_die_positionen(self):
        u"""`LeftFoot` ist um 2 in Y skaliert: `LeftToeBase` sitzt doppelt
        so weit — und die Skalierung selbst verschwindet."""
        zehe = self._knochen()['LeftToeBase']
        self.assertTrue(np.allclose(zehe['local_position'], [0, 0.2, 0.05],
                                    atol=1e-6), zehe['local_position'])

    def test_die_weltlage_stimmt_mit_der_attrappe_ueberein(self):
        u"""Linke Hand: bei ungedrehter Wurzel bei +X, mit der Avatar-Drehung
        bei -X — wie in der echten GLB (x = -0,34)."""
        welt = SkeletonGeometry.from_three(self.skelett.knochen()) \
            .compute_world_transforms()
        self.assertLess(welt['LeftHand']['world_pos'][0], -0.5)
        soll = SkeletonGeometry.from_three(Umaattrappe.gedreht()) \
            .compute_world_transforms()
        self.assertTrue(np.allclose(welt['LeftHand']['world_pos'],
                                    soll['LeftHand']['world_pos'], atol=1e-6))

    # ------------------------------------------------------------- Bindpose

    def test_bindpose_ist_nicht_knotenpose(self):
        u"""Ab den Hueften ist die Bindpose um BIND_VERSATZ verschoben:
        Der Versatz sitzt in `Hips`, alle Kinder darunter bleiben gleich."""
        knoten = self._knochen(Gltfskelett.KNOTENPOSE)
        bind = self._knochen(Gltfskelett.BINDPOSE)
        eltern_rot = np.array(bind['Global']['local_quaternion'])
        erwartet = (np.array(knoten['Hips']['local_position'])
                    + Quat.rotate(Quat.inv(eltern_rot), Umaattrappe.BIND_VERSATZ))
        self.assertTrue(np.allclose(bind['Hips']['local_position'], erwartet,
                                    atol=1e-5), bind['Hips']['local_position'])
        for name in ('LowerBack', 'LeftArm', 'LeftUpLeg', 'LeftToeBase'):
            self.assertTrue(np.allclose(bind[name]['local_position'],
                                        knoten[name]['local_position'], atol=1e-5),
                            name)

    def test_unbekannte_pose_wirft(self):
        with self.assertRaises(ValueError):
            self.skelett.knochen('ruhe')

    def test_nur_der_json_chunk_wird_beim_oeffnen_gelesen(self):
        u"""Der Binaerteil ist bei der echten GLB 27 MB — er darf erst fuer
        die Bindpose angefasst werden."""
        gltf, _binaer = Umaattrappe.glb_beispiel()
        ohne = Path(self.ordner) / 'ohne_binaer.glb'
        ohne.write_bytes(Umaattrappe.glb_bytes(gltf, b''))
        skelett = Gltfskelett(ohne)
        self.assertEqual(len(skelett.knochen()), self.anzahl)
        with self.assertRaises(ValueError):
            skelett.knochen(Gltfskelett.BINDPOSE)
