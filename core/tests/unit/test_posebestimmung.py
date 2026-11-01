# -*- coding: utf-8 -*-
"""Tests für SAM 3D Body im Prozess (01.11.2026): `Posebestimmung.sam` und die Drehungen von `S3dbschaetzer`.

WARUM: Edgar, 01.11.2026: „sam3dbody … läuft als eigener Prozess, das soll möglichst in torch
laufen“ — „mach alles was offen ist“. Bis dahin rechnete `Posebestimmung` (Mesh-3D-Import, 2D3D Kleider,
SAM-Kalibrierung) mit dem Runner `_run_sam3dpose.py` in python12; jetzt mit `S3dbschaetzer` im Prozess.
Die Ablage `sam3d.json` muss das Format des Runners behalten (`drehungen[grad]['k2']`, `k3`, `cam_t`,
`brennweite` lesen Blendimportpose, Engine2d3dKleiderpose und Samkalibrierung), eine Ablage der
Fassung 1 (python12) gilt nicht mehr, und eine Drehung ohne Ausgabe darf die anderen nicht verhindern —
ein Fehler der Karte dagegen bricht ab. SAM läuft hier nicht: die Attrappe hat die Signatur des
Originals (`autospec`); die Drehungen prüft ein Schätzer ohne Modell mit einem aufzeichnenden
`process_one_image`.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings
from PIL import Image

sys.path.insert(0, str(settings.TOOLS_ROOT))

from Sam3dbodyTorch.schaetzer import S3dbschaetzer  # noqa: E402

from core.dienste.posebestimmung import Posebestimmung  # noqa: E402


class _Angehalten(Exception):
    pass


def _ergebnis(grad, b, h):
    """Was `S3dbschaetzer.punkte` liefert, mit Werten, an denen die Rundung des Runners zu sehen ist."""
    return {'namen': [], 'kasten': [8.0, 3.0, 32.0, 27.0], 'k2': np.full((70, 2), grad + 0.123456),
            'k3': np.full((70, 3), 0.1234567), 'cam_t': np.array([0.0, 0.1, 2.3456789]), 'brennweite': 1000.0,
            'bildgroesse_gedreht': [b, h] if grad in (0, 180) else [h, b]}


class PosebestimmungImProzessTest(unittest.TestCase):
    B, H = 40, 30

    def setUp(self):
        wegwerf = str(Path(settings.BASE_DIR) / '_wegwerf')
        self.ordner = Path(tempfile.mkdtemp(prefix='posebestimmung_', dir=wegwerf))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)
        rgba = np.zeros((self.H, self.B, 4), dtype=np.uint8)
        rgba[5:25, 10:30] = (200, 100, 50, 255)
        rgba[5:25, 30] = (200, 100, 50, 100)            # halb durchsichtig: Grau gemischt, nicht in der Maske
        self.png = self.ordner / 'ansicht.png'
        Image.fromarray(rgba).save(self.png)
        self.meldungen = []

    def _patch(self, punkte=None):
        p = mock.patch('Sam3dbodyTorch.schaetzer.S3dbschaetzer', autospec=True)
        klasse = p.start()
        self.addCleanup(p.stop)
        klasse.GRAU, klasse.KeineAusgabe = S3dbschaetzer.GRAU, S3dbschaetzer.KeineAusgabe
        inst = klasse.return_value
        inst.namen = ['punkt_%d' % i for i in range(70)]
        inst.kasten.return_value = [8.0, 3.0, 32.0, 27.0]
        inst.punkte.side_effect = punkte or (
            lambda rgb, maske, grad=0, freistellen=True: _ergebnis(grad, self.B, self.H))
        return klasse, inst

    def _bestimmung(self, angehalten=lambda: False):
        return Posebestimmung(self.ordner / 'pose', 'Test', lambda a, t: self.meldungen.append((a, t)),
                              angehalten, _Angehalten)

    def _abgelegt(self):
        return json.loads((self.ordner / 'pose' / 'sam3d.json').read_text(encoding='utf-8'))

    def test_rechnet_alle_drehungen_im_format_des_runners_und_legt_fassung_2_ab(self):
        klasse, inst = self._patch()
        sam, neu = self._bestimmung().sam(self.png)
        self.assertTrue(neu)
        klasse.assert_called_once_with(gewichte=settings.SAM3DBODY_CHECKPOINT, mhr=settings.SAM3DBODY_MHR)
        self.assertEqual([c.kwargs['grad'] for c in inst.punkte.call_args_list], [0, 90, 180, 270])
        self.assertTrue(all(c.kwargs['freistellen'] is False for c in inst.punkte.call_args_list))
        abgelegt = self._abgelegt()
        self.assertEqual(abgelegt['fassung'], 2)
        self.assertEqual(abgelegt['bildgroesse'], [self.B, self.H])
        self.assertEqual(abgelegt['drehungen']['90']['k2'][0], [90.12, 90.12])      # 2 Stellen wie der Runner
        self.assertEqual(abgelegt['drehungen']['0']['cam_t'], [0.0, 0.1, 2.34568])   # 5 Stellen
        self.assertEqual(abgelegt['drehungen']['270']['bildgroesse_gedreht'], [self.H, self.B])
        felder = {'k2', 'k3', 'cam_t', 'brennweite', 'bildgroesse_gedreht'}
        self.assertEqual(set(abgelegt['drehungen']['0']), felder)
        self.assertEqual(sam['drehungen'], abgelegt['drehungen'])

    def test_foto_liegt_wie_beim_runner_auf_grau_und_die_maske_ist_alpha_ueber_127(self):
        _klasse, inst = self._patch()
        self._bestimmung().sam(self.png, drehungen=(0,))
        rgb, maske = inst.punkte.call_args.args
        self.assertEqual(rgb.shape, (self.H, self.B, 3))
        self.assertEqual(tuple(rgb[0, 0]), (128, 128, 128))
        self.assertEqual(tuple(rgb[10, 15]), (200, 100, 50))
        self.assertTrue(128 < rgb[10, 30, 0] < 200)                 # gemischt wie alpha_composite
        self.assertFalse(maske[10, 30])
        self.assertEqual(int(maske.sum()), 20 * 20)

    def test_zweiter_aufruf_liest_die_ablage_und_laedt_kein_modell(self):
        klasse, _inst = self._patch()
        self._bestimmung().sam(self.png)
        sam, neu = self._bestimmung().sam(self.png)
        self.assertFalse(neu)
        self.assertEqual(klasse.call_count, 1)
        self.assertIn('90', sam['drehungen'])

    def test_ablage_der_fassung_1_aus_python12_gilt_nicht(self):
        klasse, _inst = self._patch()
        (self.ordner / 'pose').mkdir(parents=True)
        alt = {'fassung': 1, 'quelle': Posebestimmung.stand(self.png),
               'drehungen': {str(g): {'k2': []} for g in Posebestimmung.DREHUNGEN}}
        (self.ordner / 'pose' / 'sam3d.json').write_text(json.dumps(alt), encoding='utf-8')
        _sam, neu = self._bestimmung().sam(self.png)
        self.assertTrue(neu)
        self.assertEqual(klasse.call_count, 1)

    def test_drehung_ohne_ausgabe_steht_als_fehler_die_anderen_rechnen_weiter(self):
        def punkte(rgb, maske, grad=0, freistellen=True):
            if grad == 90:
                raise S3dbschaetzer.KeineAusgabe('SAM 3D Body hat nichts geliefert (keine Ausgabe)')
            return _ergebnis(grad, self.B, self.H)
        self._patch(punkte)
        sam, _neu = self._bestimmung().sam(self.png)
        self.assertEqual(sam['drehungen']['90'], {'fehler': 'keine Ausgabe'})
        self.assertEqual(sorted(g for g, d in sam['drehungen'].items() if 'k2' in d), ['0', '180', '270'])

    def test_fehler_der_karte_bricht_ab_statt_als_leere_drehung_zu_gelten(self):
        def punkte(rgb, maske, grad=0, freistellen=True):
            raise RuntimeError('CUDA error: out of memory')
        self._patch(punkte)
        with self.assertRaises(RuntimeError):
            self._bestimmung().sam(self.png)
        self.assertFalse((self.ordner / 'pose' / 'sam3d.json').exists())

    def test_anhalten_zwischen_den_drehungen(self):
        _klasse, inst = self._patch()
        with self.assertRaises(_Angehalten):
            self._bestimmung(angehalten=lambda: inst.punkte.call_count >= 1).sam(self.png)
        self.assertEqual(inst.punkte.call_count, 1)

    def test_fortschritt_bleibt_im_anteil_von_sam_und_steigt(self):
        self._patch()
        self._bestimmung().sam(self.png)
        anteile = [a for a, _t in self.meldungen]
        self.assertEqual(anteile, sorted(anteile))
        self.assertLessEqual(max(anteile), Posebestimmung.ANTEIL_SAM)
        self.assertTrue(all(t.startswith('Pose: ') for _a, t in self.meldungen))


class _Aufzeichner:
    """Wie `SAM3DBodyEstimator.process_one_image(img, bboxes)` → eine Person; `pred_keypoints_2d` = die
    Mitte des übergebenen Kastens (im gedrehten Bild)."""

    def __init__(self):
        self.bild, self.kasten = None, None

    def process_one_image(self, img, bboxes=None):
        self.bild, self.kasten = img, np.asarray(bboxes)[0]
        mitte = [(self.kasten[0] + self.kasten[2]) / 2, (self.kasten[1] + self.kasten[3]) / 2]
        return [{'pred_keypoints_2d': np.array([mitte]), 'pred_keypoints_3d': np.zeros((1, 3)),
                 'pred_cam_t': np.zeros(3), 'focal_length': 1.0}]


class S3dbschaetzerDrehungTest(unittest.TestCase):
    def _schaetzer(self):
        s = S3dbschaetzer.__new__(S3dbschaetzer)          # ohne Modell: Bild, Kasten, Punkte der Drehung
        s.namen, s.schaetzer = ['mitte'], _Aufzeichner()
        return s

    def test_drehen_und_zurueck_heben_sich_auf(self):
        p = np.array([[3.5, 7.25], [0.0, 0.0], [40.0, 30.0]])
        for grad in S3dbschaetzer.DREHUNGEN:
            hin = S3dbschaetzer.drehen(p, grad, 40, 30)
            np.testing.assert_allclose(S3dbschaetzer.zurueck(hin, grad, 40, 30), p)

    def test_bild_gegen_den_uhrzeigersinn_wie_pil_und_punkte_zurueck_im_ungedrehten_foto(self):
        rgb = np.full((30, 40, 3), S3dbschaetzer.GRAU, dtype=np.uint8)               # schon auf Grau
        rgb[2:6, 30:36] = (255, 0, 0)                                                 # Person oben rechts
        maske = rgb[..., 0] == 255
        for grad in S3dbschaetzer.DREHUNGEN:
            s = self._schaetzer()
            e = s.punkte(rgb, maske, grad=grad)
            pil = np.array(Image.fromarray(rgb).rotate(grad, expand=True))
            np.testing.assert_array_equal(s.schaetzer.bild, pil)        # dasselbe Bild wie der Runner
            ys, xs = np.nonzero(pil[..., 0] == 255)
            k = s.schaetzer.kasten
            umfasst = k[0] <= xs.min() and xs.max() + 1 <= k[2] and k[1] <= ys.min() and ys.max() + 1 <= k[3]
            self.assertTrue(umfasst, (grad, k))
            mitte = [(e['kasten'][0] + e['kasten'][2]) / 2, (e['kasten'][1] + e['kasten'][3]) / 2]
            np.testing.assert_allclose(e['k2'][0], mitte, atol=1e-9)

    def test_unbekannte_drehung_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            self._schaetzer().punkte(np.zeros((4, 4, 3), dtype=np.uint8), np.ones((4, 4), dtype=bool),
                                     grad=45)

    def test_keine_ausgabe_ist_ein_eigener_fehler(self):
        s = self._schaetzer()
        s.schaetzer.process_one_image = lambda img, bboxes=None: []
        with self.assertRaises(S3dbschaetzer.KeineAusgabe):
            s.punkte(np.zeros((4, 4, 3), dtype=np.uint8), np.ones((4, 4), dtype=bool))
        self.assertTrue(issubclass(S3dbschaetzer.KeineAusgabe, RuntimeError))   # Fotogelenke fängt das
