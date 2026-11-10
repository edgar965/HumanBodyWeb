# -*- coding: utf-8 -*-
"""`Fotogenesishautangleich`: Original, Speichern, Zurücksetzen und neu gerechnete Haut (05.11.2026). Geschrieben, nicht gelaufen."""
import json
import os
import shutil
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock

from django.test import override_settings
from PIL import Image

from core.dienste.fotogenesishautangleich import Fotogenesishautangleich

from ._pruefablage import Pruefablage

SEITE = 8
REGLER = {'dunkel': 0.5, 'hell': 1.0, 'unsichtbar': 0.0, 'zeichnung': 0.25, 'bezug': -0.5, 'reichweite': 0.5}


def jpeg(farbe):
    aus = BytesIO()
    Image.new('RGB', (SEITE, SEITE), farbe).save(aus, 'JPEG')
    return aus.getvalue()


class HautangleichAblageTest(unittest.TestCase):
    databases = []

    def setUp(self):
        ablage = Pruefablage.ordner()
        self.wurzel = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        self.a = Fotogenesishautangleich.__new__(Fotogenesishautangleich)
        self.a.kennung, self.a.g, self.a.haut = 't', 'maennlich', self.wurzel
        self.a.ablage = self.wurzel / 'angleich'
        self.a.original = self.a.ablage / 'original'
        self.a.original.mkdir(parents=True)
        for name in ('1001.jpg', '1002.jpg'):
            (self.wurzel / name).write_bytes(jpeg((200, 150, 120)))
            shutil.copy2(self.wurzel / name, self.a.original / name)
        (self.a.ablage / 'felder.json').write_text(json.dumps({'fassung': Fotogenesishautangleich.FASSUNG, 'seite': SEITE}), encoding='utf-8')

    def test_kopie_des_originals_gilt(self):
        self.assertTrue(self.a._basis_gilt())

    def test_stand_nennt_die_adresse_der_seite(self):
        adresse = '/api/meshgenesis/test/t/hautangleich/'
        s = self.a.stand(adresse)
        self.assertTrue(s['felder'].startswith(adresse + 'daten/felder/'))
        self.assertTrue(s['original'])
        self.assertTrue(all(a.startswith(adresse + 'original/') for a in s['original'].values()))

    def test_fuer_test_nimmt_die_fotos_des_jobs(self):
        job = self.wurzel / 'fotogenesis' / 'J'
        job.mkdir(parents=True)
        (job / 'job.json').write_text(json.dumps({'meshgenesis_test': 't', 'fotos': [{'winkel': 90}]}), encoding='utf-8')
        with override_settings(OBJECTS_ROOT=self.wurzel), mock.patch.object(Fotogenesishautangleich, '_zum_test', side_effect=lambda k, f: (k, f)):
            self.assertEqual(Fotogenesishautangleich.fuer_test('t'), ('t', [{'winkel': 90}]))
            self.assertEqual(Fotogenesishautangleich.fuer_test('andere'), ('andere', None))

    def test_speichern_gilt_und_neue_haut_nicht(self):
        self.a.speichern({'1001': jpeg((10, 20, 30)), '1002': jpeg((10, 20, 30))}, REGLER)
        self.assertTrue(self.a._basis_gilt())
        self.assertEqual(self.a._gespeichert()['regler'], REGLER)
        (self.wurzel / '1001.jpg').write_bytes(jpeg((1, 2, 3)))
        os.utime(self.wurzel / '1001.jpg', ns=(1, 1))
        self.assertFalse(self.a._basis_gilt())

    def test_zuruecksetzen_bringt_das_original(self):
        original = (self.a.original / '1001.jpg').read_bytes()
        self.a.speichern({'1001': jpeg((10, 20, 30)), '1002': jpeg((10, 20, 30))}, REGLER)
        self.a.zuruecksetzen()
        self.assertEqual((self.wurzel / '1001.jpg').read_bytes(), original)
        self.assertFalse((self.a.ablage / 'stand.json').exists())

    def test_falsche_kachel_aendert_nichts(self):
        vorher = (self.wurzel / '1001.jpg').read_bytes()
        with self.assertRaises(ValueError):
            self.a.speichern({'1001': jpeg((10, 20, 30))}, REGLER)
        with self.assertRaises(ValueError):
            self.a.speichern({'1001': jpeg((10, 20, 30)), '1002': jpeg((10, 20, 30))}, dict(REGLER, dunkel=-0.5))
        self.assertEqual((self.wurzel / '1001.jpg').read_bytes(), vorher)
