# -*- coding: utf-8 -*-
"""Modell aus Bildern — Optionen, Sichtung-Übernahme, Körperteile, Endpunkte.

Ohne Daz-Bibliothek und ohne Schätzer: Attrappen, Kunstdaten, ein 8×8-PNG.
Was die Bibliothek braucht (Anpassung an den Ursula-Käfig), steht in
`longrunner/test_genesis9_formanpassung.py`.
"""

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from django.test import Client, TestCase, override_settings

from core.dienste.bildmodelloptionen import Bildmodelloptionen
from core.dienste.bildmodellsichtung import Bildmodellsichtung
from core.models import Bildmodellauftrag


class OptionenTest(unittest.TestCase):
    def test_vorgaben_und_pruefen(self):
        v = Bildmodelloptionen.vorgaben()
        self.assertEqual(v['koerper'], 'smplest_x')
        self.assertEqual(v['reglersatz'], 'charaktere')
        g = Bildmodelloptionen.pruefen(
            {'koerper': 'quatsch', 'reglersatz': 'alle', 'groesse_cm': '172.5', 'unbekannt': 1}
        )
        self.assertEqual(g['koerper'], 'smplest_x', 'unbekannter Wert → Vorgabe')
        self.assertEqual(g['reglersatz'], 'alle')
        self.assertEqual(g['groesse_cm'], 172.5)
        self.assertNotIn('unbekannt', g)
        self.assertEqual(Bildmodelloptionen.pruefen({'groesse_cm': 999})['groesse_cm'], 250.0)

    def test_katalog_traegt_jeden_schritt(self):
        Bildmodelloptionen._zustand = {}
        try:
            k = Bildmodelloptionen.katalog()
        finally:
            Bildmodelloptionen.vergessen()
        self.assertEqual([s['schluessel'] for s in k['schritte']], Bildmodelloptionen.REIHENFOLGE)
        felder = {f['feld'] for s in k['schritte'] for f in s['felder']}
        self.assertTrue({'koerper', 'reglersatz', 'restmorph', 'zuschnitt'} <= felder)
        for s in k['schritte']:
            for f in s['felder']:
                self.assertIn(f['vorgabe'], [a['wert'] for a in f['alternativen']])

    def test_daempfung_und_glaettung_sind_zahlen(self):
        self.assertEqual(Bildmodelloptionen.DAEMPFUNG['gering'], 0.02)
        self.assertEqual(Bildmodelloptionen.GLAETTUNG['viel'], 12)


class _Ablage:
    def __init__(self):
        self._z = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))

    def zuschnitt(self):
        return self._z

    def original(self):
        return self._z

    def originale(self):
        return [self._z / 'a.jpg']

    def anlegen(self):
        return self._z

    def weg(self):
        shutil.rmtree(self._z, ignore_errors=True)


class SichtungUebernahmeTest(unittest.TestCase):
    def setUp(self):
        self.ablage = _Ablage()

    def tearDown(self):
        self.ablage.weg()

    def _job(self, bilder):
        class Job:
            kennung = 'x'

            def save(self, **_):
                pass

        j = Job()
        j.bilder = bilder
        return j

    def test_manuelle_einordnung_bleibt_und_detail_wird_nebenbild(self):
        job = self._job(
            [
                {'datei': 'a_z1.jpg', 'kategorie': 'kopf', 'gewicht': 0.3, 'manuell': True},
                {'datei': 'b.jpg', 'kategorie': 'koerper', 'gewicht': 1.0, 'schaetzung': {'betas': [1]}},
            ]
        )
        s = Bildmodellsichtung(job, self.ablage, {'zuschnitt': 'yolo', 'einordnung': 'auto'})
        s._uebernehmen(
            [
                {'datei': 'a_z1.jpg', 'kategorie': 'koerper', 'gewicht': 1.0},
                {'datei': 'b.jpg', 'kategorie': 'koerper', 'gewicht': 0.6},
                {'datei': 'c.jpg', 'kategorie': 'leer', 'gewicht': 0.0, 'breite': 2000, 'hoehe': 2667},
                {'datei': 'd.jpg', 'kategorie': 'leer', 'gewicht': 0.0, 'breite': 120, 'hoehe': 90},
            ]
        )
        nach = {b['datei']: b for b in job.bilder}
        self.assertEqual(nach['a_z1.jpg']['kategorie'], 'kopf', 'von Hand gestellt bleibt')
        self.assertEqual(nach['a_z1.jpg']['gewicht'], 0.3)
        self.assertEqual(nach['b.jpg']['schaetzung'], {'betas': [1]}, 'Schätzung bleibt am Bild')
        self.assertEqual(nach['c.jpg']['kategorie'], 'neben', 'großes Bild ohne Befund = Detail')
        self.assertEqual(nach['d.jpg']['kategorie'], 'leer')
        self.assertEqual([b['datei'] for b in job.bilder][0], 'b.jpg', 'Körper zuerst')

    def test_befehl_mit_und_ohne_zuschnitt(self):
        job = self._job([])
        s = Bildmodellsichtung(job, self.ablage, {'zuschnitt': 'yolo'})
        befehl = s.befehl([Path('x.jpg')])
        self.assertIn('--zuschnitt', befehl)
        self.assertTrue(befehl[1].endswith('_run_bildsichtung.py'))
        s = Bildmodellsichtung(job, self.ablage, {'zuschnitt': 'ganz'})
        self.assertNotIn('--zuschnitt', s.befehl([Path('x.jpg')]))
        # Rigs (19.09.2026): Vorgabe alle vier, `mediapipe` fordert keine dazu.
        self.assertIn('yolo,openpifpaf,vitpose', befehl)
        nur_mp = Bildmodellsichtung(job, self.ablage, {'rig': 'mediapipe'}).befehl([Path('x.jpg')])
        self.assertNotIn('--rigs', nur_mp)
        self.assertIn('yolo', Bildmodellsichtung(job, self.ablage, {'rig': 'yolo'}).befehl([Path('x.jpg')]))


class KoerperteileTest(unittest.TestCase):
    def test_genesis_knochen_auf_teile(self):
        from Genesis9.koerperteile import G9koerperteile as K

        erwartet = {
            'l_forearmtwist1': 'l_unterarm',
            'r_upperarm': 'r_oberarm',
            'l_index2': 'l_hand',
            'l_indextoe1': 'l_fuss',
            'r_thightwist2': 'r_oberschenkel',
            'spine3': 'rumpf',
            'l_pectoral': 'rumpf',
            'pelvis': 'becken',
            'neck2': 'hals',
            'lowerjaw': 'kopf',
            'l_eyelidupper': 'kopf',
            'l_eye': 'auge',
            'r_shoulder': 'r_schulter',
            'l_metatarsal': 'l_fuss',
            'r_shin': 'r_unterschenkel',
        }
        for knochen, teil in erwartet.items():
            self.assertEqual(K.genesis(knochen), teil, knochen)

    def test_nachbarn_symmetrisch_und_smplx_vollstaendig(self):
        from Genesis9.koerperteile import G9koerperteile as K

        n = K.nachbarn()
        for a, b in K._GRENZEN:
            self.assertIn(K.NUMMER[b], n[K.NUMMER[a]])
            self.assertIn(K.NUMMER[a], n[K.NUMMER[b]])
        self.assertEqual(set(K.SMPLX), set(range(25)), 'alle 25 Körpergelenke von SMPL-X')
        import numpy as np

        gewichte = np.zeros((3, 55))
        gewichte[0, 1] = 1
        gewichte[1, 30] = 1
        gewichte[2, 23] = 1
        teile = K.smplx_punkte(gewichte)
        self.assertEqual([K.TEILE[t] for t in teile], ['l_oberschenkel', 'l_hand', 'auge'])


def _png():
    from PIL import Image

    puffer = io.BytesIO()
    Image.new('RGB', (8, 8), (120, 90, 70)).save(puffer, 'PNG')
    return puffer.getvalue()


class EndpunkteTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))
        self.client = Client(HTTP_HOST='127.0.0.1')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_anlegen_bild_stellen_zustand_datei_loeschen(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            from django.core.files.uploadedfile import SimpleUploadedFile

            antwort = self.client.post(
                '/api/bildmodell/anlegen/',
                {
                    'name': 'ZZ Test',
                    'typ': 'genesis9',
                    'bilder': [
                        SimpleUploadedFile('a.png', _png(), 'image/png'),
                        SimpleUploadedFile('b.txt', b'x', 'text/plain'),
                    ],
                },
            )
            self.assertEqual(antwort.status_code, 200, antwort.content[:200])
            daten = antwort.json()
            self.assertEqual(daten['bilder'], 1, 'nur Bilddateien')
            job = Bildmodellauftrag.objects.get(pk=daten['id'])
            self.assertEqual(job.status, 'angelegt')
            self.assertTrue((self.tmp / 'modellauftraege' / job.kennung / 'original' / 'a.png').is_file())
            # Bild stellen
            job.bilder = [{'datei': 'a.jpg', 'kategorie': 'neben', 'gewicht': 0.0}]
            job.save()
            antwort = self.client.post(
                '/api/bildmodell/%s/bild/a.jpg/' % job.id,
                data=json.dumps({'kategorie': 'koerper', 'gewicht': 0.7}),
                content_type='application/json',
            )
            self.assertEqual(antwort.status_code, 200)
            job.refresh_from_db()
            self.assertEqual(job.bilder[0]['kategorie'], 'koerper')
            self.assertEqual(job.bilder[0]['gewicht'], 0.7)
            self.assertTrue(job.bilder[0]['manuell'])
            # Zustand und Seite
            z = self.client.get('/api/bildmodell/%s/zustand/' % job.id).json()
            self.assertEqual(z['originale'], ['a.png'])
            self.assertEqual(
                self.client.get('/humanbody/modell-aus-dateien/%s/' % job.kennung).status_code, 200
            )
            self.assertEqual(self.client.get('/humanbody/modell-aus-dateien/').status_code, 200)
            # Datei nur im Auftrag
            datei = self.client.get('/api/bildmodell/%s/datei/original/a.png' % job.id)
            self.assertEqual(datei.status_code, 200)
            self.assertEqual(b''.join(datei.streaming_content), _png())
            datei.close()  # sonst hält Windows die Datei offen, und das Löschen unten scheitert
            self.assertEqual(
                self.client.get('/api/bildmodell/%s/datei/original/..%%2Fa.png' % job.id).status_code, 404
            )
            self.assertEqual(
                self.client.get('/api/bildmodell/%s/datei/geheim/a.png' % job.id).status_code, 404
            )
            # Löschen räumt den Ordner
            self.client.post(
                '/api/bildmodell/loeschen/',
                data=json.dumps({'ids': [str(job.id)]}),
                content_type='application/json',
            )
            self.assertFalse(Bildmodellauftrag.objects.filter(pk=job.id).exists())
            self.assertFalse((self.tmp / 'modellauftraege' / job.kennung).exists())

    def test_starten_verlangt_bekannten_schritt(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            job = Bildmodellauftrag.objects.create(kennung='2026.01.01.00.00.00', name='ZZ')
            from unittest import mock

            with mock.patch('core.api.bildmodell.Bildmodellarbeiter.starten', return_value=4711) as start:
                antwort = self.client.post(
                    '/api/bildmodell/%s/starten/' % job.id,
                    data=json.dumps({'ab': 'quatsch', 'optionen': {'reglersatz': 'alle'}}),
                    content_type='application/json',
                )
            self.assertEqual(antwort.json()['ab'], 'sichtung')
            start.assert_called_once()
            job.refresh_from_db()
            self.assertEqual(job.optionen['reglersatz'], 'alle')
            self.assertEqual(job.optionen['ab'], 'sichtung')  # für den Balken ab Startschritt
