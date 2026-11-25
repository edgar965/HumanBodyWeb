# -*- coding: utf-8 -*-
"""`Umareglerzug` — der Reglerzug einer UMA-Python-Figur gegen die volle Antwort (25.11.2026, Edgar: „alle regler unter 0,2 s“).

1. Punkte bytegleich, Skelett, Bilanz und Stoff gleich wie in `Szenenfigur.alles`, an zwei Stellungen; eine andere Stellung gibt andere Punkte.
2. Die Normalen hängen nicht an der DNA — darum schickt der Zug keine.
3. Der Endpunkt gibt mit `nur: 'form'` das Binärpaket, ohne weiterhin die volle JSON-Antwort.

Langläufer: der Bau der Rasse dauert rund 7 s. Sabotage-Gegenprobe (nicht gefahren): in `Umareglerzug.antwort` `dna` weglassen → Fall 1 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import json
import struct
import unittest
from pathlib import Path

import torch
from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

RASSE = 'Human Female 3.0'


@unittest.skipUnless(torch.cuda.is_available() and Path(settings.UMA_PROJEKT).is_dir(), 'braucht die Grafikkarte und das UMA-Projekt')
class UmareglerzugTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from core.dienste.umapythonfiguren import Umapythonfiguren

        cls.gebaut = Umapythonfiguren.bauen(RASSE)

    def test_1_gleich_der_vollen_antwort(self):
        from UMA_Python.szene import Szenenfigur

        from core.dienste.umareglerzug import Umareglerzug

        for dna in ({'armLength': 0.7}, {'legsSize': 0.2, 'armLength': 0.9}):
            voll, kurz = Szenenfigur.alles(self.gebaut, dna), Umareglerzug.antwort(self.gebaut, dna)
            soll = struct.pack('<%df' % len(voll['netz']['punkte']), *voll['netz']['punkte'])
            self.assertEqual(kurz['netz']['punkte'].rohdaten, soll, dna)
            for feld in ('skelett', 'bilanz', 'stoff', 'rasse'):
                self.assertEqual(kurz[feld], voll[feld], feld)
            andere = Umareglerzug.antwort(self.gebaut, {'armLength': 0.1})
            self.assertNotEqual(andere['netz']['punkte'].rohdaten, soll, 'die Probe bewegt wirklich etwas')

    def test_2_normalen_ohne_dna(self):
        vorher = self.gebaut.normalen().tobytes()
        self.gebaut.punkte({'armLength': 0.9, 'height': 0.9})
        self.assertEqual(self.gebaut.normalen().tobytes(), vorher)

    def test_3_endpunkt(self):
        from core.api.umafigurbau import Umafigurbau
        from core.daten.netzpaket import Netzpaket

        fabrik = RequestFactory()
        rumpf = {'rasse': RASSE, 'dna': {'armLength': 0.6}}
        kurz = Umafigurbau.figur(fabrik.post('/', json.dumps({**rumpf, 'nur': 'form'}), content_type='application/json', headers={'Accept': Netzpaket.INHALTSTYP}))
        self.assertEqual((kurz.status_code, kurz['Content-Type']), (200, Netzpaket.INHALTSTYP))
        voll = json.loads(Umafigurbau.figur(fabrik.post('/', json.dumps(rumpf), content_type='application/json')).content)
        self.assertIn('haut', voll)
        self.assertIn('regler', voll)
