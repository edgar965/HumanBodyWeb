# -*- coding: utf-8 -*-
"""Gelenkquelle — EIN Leser für zwei Maßstäbe, geprüft mit gerechneten Werten.

WARUM (17.08.2026)
=================
Die 2D-Punkte wurden an zwei Stellen gelesen: normalisiert (0..1) für die
Canvas-Überlagerung und in Pixeln für das gerenderte Skelettvideo. Dieselbe
Dateiwahl, dieselben Spalten, dieselben OpenPose-JSONs — zweimal geschrieben.
Beim Zusammenlegen ist der Maßstab die gefährliche Stelle: Wird die CSV nicht
hochgerechnet, sitzt das Skelett in der Bildecke; wird OpenPose zusätzlich
geteilt, verschwindet es ganz.

Deshalb hier nachgerechnete Zahlen:

    Video 200 × 100 Pixel
    CSV   `2DX_head = 0,5`, `2DY_head = 0,25`
          -> Überlagerung  (0,5 | 0,25)      (unverändert)
          -> Skelettvideo  (100 | 25)        (× Breite, × Höhe)
    OpenPose liefert PIXEL `[100, 25, 0.9]`
          -> Überlagerung  (0,5 | 0,25)      (÷ Breite, ÷ Höhe)
          -> Skelettvideo  (100 | 25)        (unverändert)

Dazu die Namensfrage: OpenPose nennt den Kopf `nose` und die Hüftmitte `midhip`.
Beides wird auf `head`/`hip` umgeschrieben — vorher tat das nur der eine der
beiden Leser, und `skelettvideo` führte deshalb jede Kante in zwei Schreibweisen.
"""

import json

from django.test import TestCase, override_settings

from core.daten.gelenknamen import Gelenknamen
from core.dienste.gelenkquelle import Gelenkquelle
from core.tests.attrappen import AuftragsAttrappe


class QuellenBasis(TestCase):

    def setUp(self):
        from django.conf import settings
        from pathlib import Path
        self.wurzel = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'gqtest'
        self.ordner = self.wurzel / 'output' / 'gq'
        (self.ordner / 'openpose_json').mkdir(parents=True, exist_ok=True)
        # Aufräumen, nicht nur anlegen: Ohne das sah der Test „ohne Rohdatei"
        # die CSV eines vorangegangenen Tests und war grün, ohne zu prüfen.
        for datei in list(self.ordner.glob('*.csv')) \
                + list((self.ordner / 'openpose_json').glob('*.json')):
            datei.unlink()
        umgebung = override_settings(MEDIA_ROOT=str(self.wurzel))
        umgebung.enable()
        self.addCleanup(umgebung.disable)

    def quelle(self, pipeline='v4'):
        return Gelenkquelle(AuftragsAttrappe(pipeline, kennung='gq'))

    def csv_ablegen(self, name='2dJoints_v4_raw.csv'):
        pfad = self.ordner / name
        pfad.write_text(
            'frameNumber,2DX_head,2DY_head,visible_head,2DX_neck,2DY_neck,'
            'visible_neck\n'
            '0,0.5,0.25,0.9,,,\n'
            '1,0.5,0.25,0.9,0.5,0.4,0.8\n', encoding='utf-8')
        return pfad

    def openpose_ablegen(self):
        punkte = [0.0] * 75
        punkte[0:3] = [100.0, 25.0, 0.9]          # nose
        punkte[3:6] = [100.0, 40.0, 0.8]          # neck
        punkte[24:27] = [100.0, 60.0, 0.7]        # midhip
        datei = self.ordner / 'openpose_json' / 'frame_000_keypoints.json'
        datei.write_text(json.dumps({'people': [
            {'pose_keypoints_2d': punkte}]}), encoding='utf-8')


class CsvTest(QuellenBasis):

    def test_ueberlagerung_laesst_die_werte_stehen(self):
        bilder = self.quelle().aus_csv(self.csv_ablegen())
        self.assertEqual(len(bilder), 2)
        self.assertEqual(bilder[0]['head'], [0.5, 0.25, 0.9])

    def test_video_rechnet_in_pixel(self):
        bilder = self.quelle().aus_csv(self.csv_ablegen(), 200, 100, tupel=True)
        self.assertEqual(bilder[0]['head'], (100.0, 25.0, 0.9))

    def test_leere_zelle_wird_uebersprungen(self):
        """Bild 0 hat keinen Hals — das Gelenk fehlt, das Bild bleibt."""
        bilder = self.quelle().aus_csv(self.csv_ablegen())
        self.assertNotIn('neck', bilder[0])
        self.assertIn('neck', bilder[1])

    def test_fehlende_datei_gibt_keine_bilder(self):
        self.assertEqual(self.quelle().aus_csv(self.ordner / 'weg.csv'), [])

    def test_tupel_nur_auf_wunsch(self):
        """JSON kann keine Tupel — die Überlagerung braucht Listen."""
        bilder = self.quelle().aus_csv(self.csv_ablegen())
        self.assertIsInstance(bilder[0]['head'], list)


class OpenposeTest(QuellenBasis):

    def test_ueberlagerung_teilt_durch_die_bildmasse(self):
        self.openpose_ablegen()
        bilder = self.quelle('openpose').aus_openpose(200, 100)
        self.assertEqual(bilder[0]['head'], [0.5, 0.25, 0.9])

    def test_video_laesst_die_pixel_stehen(self):
        self.openpose_ablegen()
        bilder = self.quelle('openpose').aus_openpose(tupel=True, alle=True)
        self.assertEqual(bilder[0]['head'], (100.0, 25.0, 0.9))

    def test_namen_werden_umgeschrieben(self):
        """`nose` -> `head`, `midhip` -> `hip` — in BEIDEN Maßstäben."""
        self.openpose_ablegen()
        for bilder in (self.quelle('openpose').aus_openpose(200, 100),
                       self.quelle('openpose').aus_openpose(tupel=True,
                                                            alle=True)):
            self.assertNotIn('nose', bilder[0])
            self.assertNotIn('midhip', bilder[0])
            self.assertIn('head', bilder[0])
            self.assertIn('hip', bilder[0])

    def test_ohne_person_bleibt_das_bild_leer(self):
        datei = self.ordner / 'openpose_json' / 'frame_001_keypoints.json'
        datei.write_text(json.dumps({'people': []}), encoding='utf-8')
        bilder = self.quelle('openpose').aus_openpose(200, 100)
        self.assertEqual(bilder[-1], {}, 'ein Bild ohne erkannte Person')

    def test_ueberlagerung_liest_nur_die_koerpergelenke(self):
        """15 Namen für die Überlagerung, 25 fürs Video — Reihenfolge zählt."""
        self.assertEqual(Gelenknamen.OPENPOSE_BODY25[14], 'lfoot')
        self.assertEqual(len(Gelenknamen.OPENPOSE_BODY25), 25)


class DateiwahlTest(QuellenBasis):

    def test_v4_nimmt_die_rohdatei(self):
        pfad = self.csv_ablegen()
        self.assertEqual(self.quelle('v4').csv_pfad(), pfad)

    def test_smpl_nimmt_auch_die_rohdatei(self):
        """Vorher suchte der Videorenderer für GVHMR die MediaPipe-CSV, die es
        dort nicht gibt — das Skelett blieb leer."""
        pfad = self.csv_ablegen()
        self.assertEqual(self.quelle('gvhmr').csv_pfad(), pfad)

    def test_eigene_erkenner_haben_eigene_datei(self):
        self.assertTrue(str(self.quelle('rtmpose').csv_pfad())
                        .endswith('rtmpose_2d.csv'))

    def test_vorgabe_ist_die_mediapipe_datei(self):
        self.assertTrue(str(self.quelle('mocapnet').csv_pfad())
                        .endswith('2dJoints_mediapipe.csv'))

    def test_ohne_rohdatei_wird_nicht_heimlich_erkannt(self):
        """Die Neuerkennung liest das ganze Video — sie muss abschaltbar sein."""
        self.assertIsNone(self.quelle('v4').csv_pfad(neu_erkennen=False))
