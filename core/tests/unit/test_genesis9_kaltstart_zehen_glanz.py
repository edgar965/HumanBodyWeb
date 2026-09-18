# -*- coding: utf-8 -*-
u"""Der Abend des 18.09.2026 (Edgar: „performance schlecht … lädt die Figur 2 Mal
… volle Auflösung immer noch mehr als 5 s" und „mach alle offenen Punkte"):

1. `G9aufwaermen.angebracht`: nur im Serverprozess (`runserver` mit
   `RUN_MAIN=true` oder `--noreload`), nie bei `test`/`migrate`.
2. `G9anhangmorphe._abgelegt`: ein Kunstordner mit einer `.dsf` wird gelesen
   und als `anhangmorphe_*.npz/.json` abgelegt; der zweite Aufruf liest die
   Ablage (Sabotage: `_lesen` wirft → trotzdem dasselbe Ergebnis); eine
   geaenderte Datei (Bestand) baut neu.
3. `G9netzstufe._teilungabgelegt`: Rundlauf ueber die Ablage, bitgleich.
4. `G9stueckfelder.pfad(…, None)` heisst `_kaefig`, `__init__` haelt None.
5. Zehen und Kiefer: `retargetknochen` fuehrt `DAZU`; `SkeletonGenesis9`
   ordnet `lowerjaw` auf `DEF-jaw`, die Zehen nur auf Genesis 9 (`DIREKT`,
   `G9zuordnung.fuer`), und laesst Fuesse/Kopf/Kiefer ohne Richtungskorrektur.
6. `G9material._wert`: Glanzwerte aus `…/channels/<Kanal>/value`, bool nicht.
7. `G9hautwahl.kategorie_von`: Metallkarte auf dem Kopf = `hautglanz`.
"""
import gzip
import json
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.g9aufwaermen import G9aufwaermen
from Genesis9 import netzstufe, pfade
from Genesis9.anhangmorphe import G9anhangmorphe
from Genesis9.bewegungbvh import G9bewegungbvh
from Genesis9.hautwahl import G9hautwahl
from Genesis9.material import G9material
from Genesis9.netzstufe import G9netzstufe
from Genesis9.stueckfelder import G9stueckfelder
from humanbody_core.skeleton.formats.g9_zuordnung import DEF_ZU_G9, G9zuordnung
from humanbody_core.skeleton.formats.genesis9 import SkeletonGenesis9

TEMP = Path(settings.BASE_DIR) / 'ProjektTemp'


class KaltstartZehenGlanzTest(SimpleTestCase):

    databases = set()

    def test_1_aufwaermen_nur_im_serverprozess(self):
        self.assertTrue(G9aufwaermen.angebracht(['manage.py', 'runserver', '8081'],
                                                {'RUN_MAIN': 'true'}))
        self.assertFalse(G9aufwaermen.angebracht(['manage.py', 'runserver', '8081'],
                                                 {}))
        self.assertTrue(G9aufwaermen.angebracht(
            ['manage.py', 'runserver', '--noreload'], {}))
        self.assertFalse(G9aufwaermen.angebracht(['manage.py', 'test'],
                                                 {'RUN_MAIN': 'true'}))

    def test_2_anhangmorphe_ablage(self):
        TEMP.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP) as wurzel:
            ordner = Path(wurzel) / 'Morphs'
            ordner.mkdir()
            ablage = Path(wurzel) / 'ablage'
            doc = {'modifier_library': [{
                'id': 'body_bs_X-0x1', 'name': 'body_bs_X', 'group': '/Actor',
                'channel': {'label': 'X', 'min': 0, 'max': 1},
                'morph': {'deltas': {'values': [[3, 1.0, 2.0, 3.0],
                                                [7, 0.0, 0.5, 0.0]]}},
            }]}

            def schreiben():
                (ordner / 'x.dsf').write_bytes(
                    gzip.compress(json.dumps(doc).encode('utf-8')))
            schreiben()
            with mock.patch.object(pfade.G9pfade, 'ablage', return_value=ablage):
                erst = G9anhangmorphe._abgelegt(str(ordner))
                dateien = sorted(p.name for p in ablage.iterdir())
                self.assertEqual(len(dateien), 2, dateien)
                self.assertTrue(dateien[0].startswith('anhangmorphe_'))
                with mock.patch.object(G9anhangmorphe, '_lesen',
                                       side_effect=AssertionError('gelesen')):
                    zweit = G9anhangmorphe._abgelegt(str(ordner))
                self.assertEqual(list(zweit[0]), ['body_bs_X'])
                a, b = zweit[0]['body_bs_X'], erst[0]['body_bs_X']
                np.testing.assert_array_equal(a[0], b[0])
                np.testing.assert_allclose(a[1], b[1])
                self.assertAlmostEqual(float(a[1][0][0]), 0.01)      # cm -> m
                self.assertEqual(zweit[1]['body_bs_X']['label'], 'X')
                # Bestand geaendert: neue Ablage, alte bleibt liegen
                doc['modifier_library'][0]['morph']['deltas']['values'].append(
                    [9, 1, 1, 1])
                schreiben()
                dritt = G9anhangmorphe._abgelegt(str(ordner))
                self.assertEqual(len(dritt[0]['body_bs_X'][0]), 3)
                self.assertEqual(len(list(ablage.iterdir())), 4)

    def test_3_nahtteilung_ablage(self):
        TEMP.mkdir(exist_ok=True)
        polys = [[0, 0, 0, 1, 2, 3], [0, 1, 1, 4, 5, 2]]
        uvs = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [2, 0], [2, 1]], dtype=float)
        ueber = {(1, 1): 4}
        with tempfile.TemporaryDirectory(dir=TEMP) as wurzel:
            with mock.patch.object(pfade.G9pfade, 'ablage',
                                   return_value=Path(wurzel)):
                a = G9netzstufe._teilungabgelegt('probe', polys, ['m0', 'm1'], uvs,
                                                 ueber)
                self.assertEqual(len(list(Path(wurzel).glob('naht_probe_*.npz'))), 1)
                with mock.patch.object(netzstufe.G9netzteilung, 'teilen',
                                       side_effect=AssertionError('geteilt')):
                    b = G9netzstufe._teilungabgelegt('probe', polys, ['m0', 'm1'],
                                                     uvs, ueber)
        for x, y in zip(a[:3], b[:3]):
            np.testing.assert_array_equal(x, y)
        self.assertEqual(a[3], b[3])
        self.assertEqual(len(a[0]), 7)          # 6 Punkte + eine Nahtkopie

    def test_4_kaefigfelder_pfad(self):
        self.assertTrue(str(G9stueckfelder.pfad('gelenke', 'rock', None, 'npz'))
                        .endswith('felder_gelenke_rock_kaefig.npz'))
        self.assertTrue(str(G9stueckfelder.pfad('gelenke', 'rock', 2, 'npz'))
                        .endswith('felder_gelenke_rock_s2.npz'))
        self.assertIsNone(G9stueckfelder('gelenke', 'rock', None, [], []).stufen)

    def test_5_zehen_und_kiefer(self):
        knochen = G9bewegungbvh.retargetknochen()
        for name in G9bewegungbvh.DAZU:
            self.assertIn(name, knochen)
        self.assertEqual(SkeletonGenesis9.BONE_MAP_TO_RIGIFY['lowerjaw'], 'DEF-jaw')
        self.assertEqual(DEF_ZU_G9['DEF-jaw'], 'lowerjaw')
        self.assertIsNone(SkeletonGenesis9.BONE_MAP_TO_RIGIFY['l_bigtoe1'])
        zuordnung = G9zuordnung.fuer(SkeletonGenesis9)
        self.assertEqual(zuordnung['l_bigtoe1'], 'l_bigtoe1')
        self.assertEqual(zuordnung['lowerjaw'], 'lowerjaw')
        self.assertEqual(zuordnung['pelvis'], None)
        ausnahmen = G9zuordnung.ausnahmen(SkeletonGenesis9)
        self.assertIn('r_pinkytoe1', ausnahmen)
        for defname in ('DEF-toe.L', 'DEF-spine.006', 'DEF-jaw'):
            self.assertIn(defname, SkeletonGenesis9.SKIP_DIR_CORRECTION)

    def test_6_glanzwerte(self):
        def wert(kanal, v):
            return G9material._wert({
                'url': ('name://@selection#materials/hair1:?extra/'
                        'studio_material_channels/channels/%s/value'
                        % kanal.replace(' ', '%20')),
                'keys': [[0, v]]})
        self.assertEqual(wert('Glossy Roughness', 0.42), ('hair1', 'rauheitwert', 0.42))
        self.assertEqual(wert('Dual Lobe Specular Weight', 0.3),
                         ('hair1', 'glanzgewicht', 0.3))
        self.assertEqual(wert('Metallic Weight', 0.8), ('hair1', 'metallgewicht', 0.8))
        self.assertEqual(wert('Metallicity Enable', True), (None, None, None))
        self.assertEqual(wert('Tags', 'Hair'), (None, None, None))
        self.assertEqual(G9material.KANAELE['Metallic Weight'], 'metall')

    def test_7_metallkarte_ist_hautglanz(self):
        self.assertEqual(G9hautwahl.kategorie_von({'Head': {'metall': 'x.jpg'}}),
                         'hautglanz')
        self.assertEqual(G9hautwahl.kategorie_von({'Head': {'albedo': 'x.jpg'}}),
                         'kopf')
