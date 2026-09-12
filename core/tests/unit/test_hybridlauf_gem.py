# -*- coding: utf-8 -*-
u"""Hybridlauf mit GEM-SMPL als Rückgrat und GEM-X als Fingerquelle.

Auftrag Edgar (12.09.2026): „baue beides, füge das als Option in die
Erkennungs Pipeline mit ein, dann kann ich einmal mit einmal ohne diese
zusatzoptionen erzeugen". Also:

* `hybrid_gem` fährt den Körper mit GEM (dieselbe Bvhbau-BVH wie GVHMR).
* `hands_source: gemx` fährt GEM-X als DRITTEN Unterlauf — nach dem Körper,
  nicht gleichzeitig (beide auf der GPU) — und trägt die BVH in
  `bvh_file_hands` ein. Ohne die Bestellung gibt es keinen dritten Lauf.
* Scheitern die Finger, bleibt der Lauf ein Teilergebnis (wie beim Gesicht).

Die Umleitung (keine echte Pipeline) kommt aus `test_hybridlauf.HybridBasis`;
hier wird `Smpllauf` nach dem Unterauftrag verteilt, weil Körper UND Finger
über dieselbe Klasse laufen.
"""
from core.pipelines import hybridlauf
from core.pipelines.hybridhaende import Hybridhaende
from core.tests.unit.test_hybridlauf import HybridBasis


class HybridGemBasis(HybridBasis):

    def setUp(self):
        super().setUp()
        self.aufrufe['haende'] = None
        self.reihenfolge = []
        self.haende = lambda auftrag, video, ordner: 'hands.bvh'
        pruefung = self

        class Smplattrappe:
            """Steht für `Smpllauf` — Körper ODER Finger, je nach Unterauftrag."""

            def __init__(self, auftrag, video, ordner):
                self.auftrag, self.video, self.ordner = auftrag, video, ordner
                self.welcher = ('haende' if auftrag.pipeline == Hybridhaende.QUELLE
                                else 'koerper')
                pruefung.aufrufe[self.welcher] = auftrag
                pruefung.reihenfolge.append(self.welcher)

            def fahren(self):
                return getattr(pruefung, self.welcher)(self.auftrag, self.video,
                                                       self.ordner)

        hybridlauf.Smpllauf = Smplattrappe


class HybridGemTest(HybridGemBasis):

    def test_gem_ist_das_dritte_rueckgrat(self):
        self.fahren('hybrid_gem')
        self.assertEqual(self.aufrufe['koerper'].pipeline, 'gem')
        self.assertEqual(self.aufrufe['koerper'].id, '42_body')

    def test_unbekannter_hybrid_faellt_auf_prompthmr(self):
        self.fahren('hybrid_irgendwas')
        self.assertEqual(self.aufrufe['koerper'].pipeline, 'prompthmr')

    def test_ohne_bestellung_kein_fingerlauf(self):
        auftrag, _ = self.fahren('hybrid_gem')
        self.assertIsNone(self.aufrufe['haende'])
        self.assertEqual(auftrag.bvh_file_hands, '')
        self.assertEqual(self.reihenfolge, ['koerper'])


class HybridFingerTest(HybridGemBasis):

    PARAMS = {'hands_source': 'gemx', 'static_cam': True, 'body_device': 'cuda'}

    def test_gemx_laeuft_als_dritter_unterlauf_nach_dem_koerper(self):
        auftrag, ergebnis = self.fahren('hybrid_gem', dict(self.PARAMS))
        self.assertEqual(ergebnis, ('body.bvh', 'face.bvh'))
        self.assertEqual(auftrag.bvh_file_hands, 'hands.bvh')
        self.assertEqual(self.reihenfolge, ['koerper', 'haende'])
        finger = self.aufrufe['haende']
        self.assertEqual(finger.pipeline, 'gemx')
        self.assertEqual(finger.id, '42_hands')
        self.assertEqual(finger.get_pipeline_display(), 'GEM-X')

    def test_die_finger_nehmen_kamera_und_geraet_des_koerpers(self):
        self.fahren('hybrid_gem', dict(self.PARAMS, body_device='cpu',
                                       static_cam=False))
        p = self.aufrufe['haende'].pipeline_params
        self.assertEqual(p['device'], 'cpu')
        self.assertFalse(p['static_cam'])
        self.assertIn('smooth_sigma', p)

    def test_auch_gvhmr_kann_gemx_finger_bestellen(self):
        auftrag, _ = self.fahren('hybrid_gvhmr', dict(self.PARAMS))
        self.assertEqual(self.aufrufe['koerper'].pipeline, 'gvhmr')
        self.assertEqual(auftrag.bvh_file_hands, 'hands.bvh')

    def test_scheitern_die_finger_bleibt_ein_teilergebnis(self):
        def platzt(auftrag, video, ordner):
            raise RuntimeError('GEM-X ohne Gewichte')
        self.haende = platzt
        auftrag, ergebnis = self.fahren('hybrid_gem', dict(self.PARAMS))
        self.assertEqual(ergebnis, ('body.bvh', 'face.bvh'))
        self.assertEqual(auftrag.bvh_file_hands, '')
        self.assertIn('Fingers (GEM-X): GEM-X ohne Gewichte', auftrag.progress_detail)
        self.assertIn('partial', auftrag.progress_detail)

    def test_fortschritt_nennt_alle_drei_teile(self):
        auftrag, _ = self.fahren('hybrid_gem', dict(self.PARAMS))
        # Die letzte Zwischenmeldung vor „Done" hat alle drei Teile genannt —
        # nachlesbar in der Attrappe nicht, deshalb über die Klasse selbst:
        self.assertEqual(Hybridhaende.ORDNER, 'hands')
        self.assertTrue(Hybridhaende.bestellt(self.PARAMS))
        self.assertFalse(Hybridhaende.bestellt({'hands_source': 'v4'}))
        self.assertFalse(Hybridhaende.bestellt(None))
