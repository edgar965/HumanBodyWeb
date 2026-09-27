# -*- coding: utf-8 -*-
"""„Job duplizieren" (28.09.2026): Eingabedateien und Parameter kommen mit, die Ausgabe nicht.

Je Bereich ein Auftrag mit Eingang UND Ausgabe (Ordner und Felder) — die Kopie muss den Eingang
haben, die Ausgabe nicht, und darf nicht starten. Die Ordner liegen in `ProjektTemp/pruefungen`
(`Pruefablage`), `OBJECTS_ROOT` wird umgelenkt; kein Arbeitsprozess, keine Grafikkarte.
"""

import json
import shutil
import tempfile
from pathlib import Path

from django.test import Client, TestCase, override_settings

from core.dienste.auftragsduplikat import Auftragsduplikat
from core.models import Bildmodellauftrag, Meshauftrag, Meshfigurauftrag

from ._pruefablage import Pruefablage


class AuftragsduplikatTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='duplikat_', dir=Pruefablage.wurzel()))
        self.umlenkung = override_settings(OBJECTS_ROOT=self.tmp)
        self.umlenkung.enable()
        self.client = Client(HTTP_HOST='127.0.0.1')

    def tearDown(self):
        self.umlenkung.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _datei(self, bereich, kennung, pfad, inhalt=b'x'):
        ziel = self.tmp / bereich / kennung / pfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(inhalt)

    def _duplizieren(self, bereich, job):
        antwort = self.client.post('/api/modell-aus-dateien/%s/duplizieren/' % bereich,
                                   json.dumps({'ids': [str(job.id)]}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        daten = antwort.json()
        self.assertEqual(daten['dupliziert'], 1)
        return daten['auftraege'][0]

    def test_mesh_fotos_und_nutzerwerte_ohne_befund_und_ergebnis(self):
        job = Meshauftrag.objects.create(
            kennung='2026.09.27.10.00.00', name='Damira', status='fertig', progress=100,
            optionen={'formmodell': 'trellis2', 'verwendung': 'kopf'},
            bilder=[{'datei': 'vorn.jpg', 'original': 'Vorn.JPG', 'rolle': 'vorne', 'gewicht': 40,
                     'bereich': [0, 0, 1, 0.5], 'freigestellt': 'vorn.png', 'breite': 1200}],
            ergebnis={'flaechen': 400000, 'dateien': {'glb': 'mesh.glb'}})
        self._datei('meshauftraege', job.kennung, 'eingang/vorn.jpg', b'FOTO')
        self._datei('meshauftraege', job.kennung, 'ergebnis/mesh.glb')
        self._datei('meshauftraege', job.kennung, 'vorbereitet/vorn.png')
        neu_daten = self._duplizieren('mesh', job)
        neu = Meshauftrag.objects.get(pk=neu_daten['id'])
        self.assertNotEqual(neu.kennung, job.kennung)
        self.assertEqual(neu.name, 'Damira (Kopie)')
        self.assertEqual(neu_daten['url'], '/modell-aus-dateien/mesh/%s/' % neu.kennung)
        self.assertEqual((neu.status, neu.progress, neu.ergebnis), ('angelegt', 0, {}),
                         'keine Ausgabe, kein Start')
        self.assertEqual(neu.optionen, job.optionen)
        self.assertEqual(neu.bilder, [{'datei': 'vorn.jpg', 'original': 'Vorn.JPG', 'rolle': 'vorne',
                                       'gewicht': 40, 'bereich': [0, 0, 1, 0.5]}],
                         'Befund der Vorbereitung (freigestellt, breite) ist Ausgabe')
        ordner = self.tmp / 'meshauftraege' / neu.kennung
        self.assertEqual((ordner / 'eingang' / 'vorn.jpg').read_bytes(), b'FOTO')
        self.assertFalse((ordner / 'ergebnis' / 'mesh.glb').exists())
        self.assertFalse((ordner / 'vorbereitet' / 'vorn.png').exists())
        self.assertTrue((self.tmp / 'meshauftraege' / job.kennung / 'ergebnis' / 'mesh.glb').is_file(),
                        'das Original bleibt unangetastet')

    def test_meshfigur_koerper_und_kopfnetz_ohne_figur(self):
        eingang = {'datei': 'koerper.obj', 'original': 'Koerper.obj', 'bytes': 4, 'beilagen': ['koerper.mtl'],
                   'kopf': {'datei': 'kopf.glb', 'original': 'kopf.glb', 'bytes': 4, 'beilagen': []}}
        job = Meshfigurauftrag.objects.create(
            kennung='2026.09.27.11.00.00', name='Ursula', status='fertig', optionen={'runden': '3'},
            eingang=eingang, ergebnis={'regler': {'stellung': {'a': 1.0}}}, modell='Ursula Mesh')
        for pfad in ('eingang/koerper.obj', 'eingang/koerper.mtl', 'eingang_kopf/kopf.glb',
                     'arbeit/auftrag.json', 'ergebnis/icon.png'):
            self._datei('meshfigurauftraege', job.kennung, pfad)
        neu = Meshfigurauftrag.objects.get(pk=self._duplizieren('meshfigur', job)['id'])
        self.assertEqual((neu.eingang, neu.optionen), (eingang, {'runden': '3'}))
        self.assertEqual((neu.ergebnis, neu.modell, neu.status), ({}, '', 'angelegt'))
        ordner = self.tmp / 'meshfigurauftraege' / neu.kennung
        for pfad in ('eingang/koerper.obj', 'eingang/koerper.mtl', 'eingang_kopf/kopf.glb'):
            self.assertTrue((ordner / pfad).is_file(), pfad)
        self.assertEqual(list((ordner / 'arbeit').iterdir()), [])
        self.assertEqual(list((ordner / 'ergebnis').iterdir()), [])

    def test_bildmodell_originale_ohne_ausschnitte(self):
        job = Bildmodellauftrag.objects.create(
            kennung='2026.09.27.12.00.00', name='Mila', typ='genesis9', status='fertig',
            optionen={'einordnung': 'manuell', 'bildtypen': {'a.jpg': {'kategorie': 'koerper'}}},
            bilder=[{'datei': 'a_0.jpg', 'quelle': 'a.jpg', 'kategorie': 'koerper'}],
            ergebnis={'anpassung': {'punkte_rms_mm': 4.2}}, modell='Mila')
        for pfad in ('original/a.jpg', 'original/dreh.mp4', 'zuschnitt/a_0.jpg', 'ergebnis/icon.png'):
            self._datei('modellauftraege', job.kennung, pfad)
        neu = Bildmodellauftrag.objects.get(pk=self._duplizieren('bildmodell', job)['id'])
        self.assertEqual((neu.typ, neu.optionen), ('genesis9', job.optionen))
        self.assertEqual((neu.bilder, neu.ergebnis, neu.modell), ([], {}, ''),
                         'die Ausschnitte entstehen erst in der Sichtung')
        ordner = self.tmp / 'modellauftraege' / neu.kennung
        self.assertEqual(sorted(p.name for p in (ordner / 'original').iterdir()), ['a.jpg', 'dreh.mp4'])
        self.assertEqual(list((ordner / 'zuschnitt').iterdir()), [])

    def test_unbekannter_bereich_und_leere_wahl(self):
        antwort = self.client.post('/api/modell-aus-dateien/bvh/duplizieren/', '{"ids": []}',
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 404)
        antwort = self.client.post('/api/modell-aus-dateien/mesh/duplizieren/', '{"ids": ["keine-uuid"]}',
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        with self.assertRaises(ValueError):
            Auftragsduplikat('gibtsnicht')

    def test_mehrere_bekommen_je_eine_eigene_kennung(self):
        a = Meshauftrag.objects.create(kennung='2026.09.27.13.00.00', name='A', bilder=[])
        b = Meshauftrag.objects.create(kennung='2026.09.27.13.00.01', name='B', bilder=[])
        antwort = self.client.post('/api/modell-aus-dateien/mesh/duplizieren/',
                                   json.dumps({'ids': [str(a.id), str(b.id)]}),
                                   content_type='application/json')
        kennungen = [x['kennung'] for x in antwort.json()['auftraege']]
        self.assertEqual(len(set(kennungen)), 2)
        self.assertEqual(Meshauftrag.objects.count(), 4)
