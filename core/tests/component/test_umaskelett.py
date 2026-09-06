# -*- coding: utf-8 -*-
u"""UMA-Skelett aus dem Figurkatalog: Endpunkt, Zeiger, Retarget-Ziel.

WARUM (05.09.2026): Die Vergleichsseite holt das UMA-Skelett ueber
`/api/character/uma-skeleton/` und rechnet Bewegungen mit `target=uma` um.
Geprueft auf einem Wegwerf-Katalog unter `ProjektTemp/` mit einer
synthetischen GLB — nichts hier schreibt in `Figuren/` oder `HumanBody/data/`.

Aufruf:  python manage.py test core.tests.component.test_umaskelett
"""
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from core.daten.retargetwahl import Retargetwahl
from core.dienste.retargetdaten import Retargetdaten
from core.dienste.umaskelett import Umaskelett, UmaskelettFehlt
from ..unit._umaattrappe import Umaattrappe


class UmaskelettTest(TestCase):

    def setUp(self):
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.katalog = Path(tempfile.mkdtemp(prefix='umakatalog_', dir=str(basis)))
        self.addCleanup(shutil.rmtree, self.katalog, True)
        (self.katalog / 'uma').mkdir()
        umschaltung = override_settings(FIGUREN_KATALOG=self.katalog)
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)
        Umaskelett.vergessen()
        self.addCleanup(Umaskelett.vergessen)

    def _glb(self, name='probe.glb'):
        gltf, binaer = Umaattrappe.glb_beispiel()
        (self.katalog / 'uma' / name).write_bytes(Umaattrappe.glb_bytes(gltf, binaer))

    def _zeiger(self, name):
        zeiger = self.katalog / 'aktuell.json'
        zeiger.write_text(json.dumps({'uma': name}), encoding='utf-8')

    def _abruf(self):
        return self.client.get(reverse('character_uma_skeleton'))

    # ------------------------------------------------------------ Endpunkt

    def test_liefert_die_knochen_in_three_form(self):
        self._glb()
        self._zeiger('probe.glb')
        antwort = self._abruf()
        self.assertEqual(antwort.status_code, 200, antwort.content)
        daten = antwort.json()
        self.assertEqual(daten['datei'], 'probe.glb')
        self.assertEqual(daten['quelle'], 'uma')
        namen = [k['name'] for k in daten['bones']]
        self.assertIn('Hips', namen)
        self.assertIn('LeftHandFinger03_01', namen)
        wurzel = daten['bones'][0]
        self.assertIsNone(wurzel['parent'])
        self.assertEqual(len(wurzel['local_quaternion']), 4)

    def test_die_figur_blickt_nach_plus_z(self):
        u"""Die GLB steht um 180 Grad gedreht (`Avatar`); geliefert wird sie
        ausgerichtet wie DEF — linkes Bein bei +X."""
        from humanbody_core.skeleton import SkeletonGeometry
        self._glb()
        daten = self._abruf().json()
        welt = SkeletonGeometry.from_three(daten['bones']).compute_world_transforms()
        self.assertGreater(welt['LeftUpLeg']['world_pos'][0], 0.05)

    def test_ohne_glb_eine_404_mit_klartext(self):
        antwort = self._abruf()
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('Keine UMA-Figur', antwort.json()['error'])

    def test_zeiger_ins_leere_nimmt_die_juengste(self):
        self._glb('alt.glb')
        self._zeiger('fehlt.glb')
        antwort = self._abruf()
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['datei'], 'alt.glb')

    def test_eine_kaputte_glb_ergibt_klartext_statt_stack(self):
        (self.katalog / 'uma' / 'kaputt.glb').write_bytes(b'kein glTF')
        antwort = self._abruf()
        self.assertEqual(antwort.status_code, 500)
        self.assertIn('unlesbar', antwort.json()['error'])

    # ------------------------------------------------------------- Retarget

    def test_retargetwahl_kennt_das_ziel(self):
        self.assertEqual(Retargetwahl({'target': 'uma'}, 1.68).ziel, 'uma')
        self.assertEqual(Retargetwahl({}, 1.68).ziel, 'def')
        with self.assertRaises(ValueError):
            Retargetwahl({'target': 'quatsch'}, 1.68)

    def test_unbekanntes_ziel_am_endpunkt_ist_eine_400(self):
        antwort = self.client.get(
            reverse('retarget'), {'category': 'x', 'name': 'y', 'target': 'quatsch'})
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('Ziel', antwort.json()['error'])

    def test_die_ablage_unterscheidet_die_ziele(self):
        u"""DEF behaelt den alten Namen (die Ablagen von frueher gelten
        weiter), UMA bekommt einen eigenen."""
        pfad = str(self.katalog / 'x.bvh')
        self.assertEqual(Retargetdaten(pfad).ablage,
                         Retargetdaten(pfad, ziel='def').ablage)
        self.assertNotEqual(Retargetdaten(pfad).ablage,
                            Retargetdaten(pfad, ziel='uma').ablage)

    def test_retarget_auf_uma_ueber_retargetdaten(self):
        self._glb()
        bvh = self.katalog / 'probe.bvh'
        bvh.write_text(Umaattrappe.bvh_text([{}, {'LeftArm': (-45, 0, 0)}]),
                       encoding='utf-8')
        ergebnis = Retargetdaten(str(bvh), ziel='uma').holen()
        self.assertEqual(ergebnis.frame_count, 2)
        self.assertIn('LeftArm', ergebnis.mapped_bones)
        self.assertIn('LeftUpLeg', ergebnis.mapped_bones)
        self.assertFalse([n for n in ergebnis.mapped_bones if n.startswith('DEF-')])
        self.assertTrue(np.isfinite(ergebnis.tracks['LeftArm']).all())
        # Die Ablage liegt neben der BVH — im Wegwerf-Katalog, nirgends sonst.
        self.assertTrue(Path(Retargetdaten(str(bvh), ziel='uma').ablage).is_file())

    def test_skelett_je_datei_nicht_nur_das_aus_dem_zeiger(self):
        """06.09.2026: Der Zeiger nannte Roomguests `UmaKleidung_bewegt.glb`
        (anderer Wurzelaufbau), der Motor rechnete jede Szenenfigur dagegen —
        Hüftspur in der falschen Achse. Jetzt liefert `geometrie(name)` das
        Skelett GENAU dieser Datei, je Datei einmal gelesen."""
        self._glb('probe.glb')
        self._glb('zweite.glb')
        self._zeiger('probe.glb')
        self.assertIsNotNone(Umaskelett.geometrie('zweite.glb'))
        self.assertIsNotNone(Umaskelett.geometrie())
        self.assertEqual(len(Umaskelett._bestand), 2)
        self.assertTrue(Umaskelett.glb_pfad('zweite.glb').endswith('zweite.glb'))
        # Dieselbe Datei ein zweites Mal: kein dritter Eintrag.
        Umaskelett.knochen('zweite.glb')
        self.assertEqual(len(Umaskelett._bestand), 2)
        with self.assertRaises(UmaskelettFehlt):
            Umaskelett.geometrie('fehlt.glb')
        # Ein Pfad wird auf den Dateinamen gestutzt — nichts liest außerhalb des Katalogs.
        self.assertTrue(Umaskelett.glb_pfad('../uma/zweite.glb').endswith('zweite.glb'))
        bvh = self.katalog / 'probe.bvh'
        bvh.write_text(Umaattrappe.bvh_text([{}, {'LeftArm': (-45, 0, 0)}]),
                       encoding='utf-8')
        ergebnis = Retargetdaten(str(bvh), ziel='uma', figur='zweite.glb').holen()
        self.assertIn('LeftArm', ergebnis.mapped_bones)
        self.assertNotEqual(Retargetdaten(str(bvh), ziel='uma', figur='zweite.glb').ablage,
                            Retargetdaten(str(bvh), ziel='uma').ablage)
