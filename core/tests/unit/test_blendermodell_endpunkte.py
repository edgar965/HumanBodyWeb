# -*- coding: utf-8 -*-
"""Bereich „BlenderModel" (29.09.2026) — Endpunkte: Anlegen, Seite, Bildauswahl, Lauf, gemeinsame Register.

Die Auftragsordner liegen während der Prüfung in `ProjektTemp/pruefungen` (`Pruefablage`), nie unter
`3DObjects` — `OBJECTS_ROOT` wird umgelenkt. Gestartet wird nichts (`starten=0`): kein Arbeitsprozess, keine
Grafikkarte. Ein laufender Auftrag wird mit der PID dieses Prozesses vorgetäuscht (`Prozesspruefung.lebt`).
Optionen, Lauf und Ablage: `test_blendermodell.py`.
"""

import io
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TransactionTestCase, override_settings
from PIL import Image

from core.daten.blendermodellablage import Blendermodellablage
from core.daten.texturquelle import Texturquelle
from core.dienste.blendermodellgpu import Blendermodellgpu
from core.dienste.blendermodelllauf import Blendermodelllauf
from core.dienste.blendermodelloptionen import Blendermodelloptionen
from core.dienste.blendermodelltabelle import Blendermodelltabelle
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.ollamamodelle import Ollamamodelle
from core.models import Blendermodellauftrag

from ._pruefablage import Pruefablage


def png(farbe=(120, 130, 140)):
    puffer = io.BytesIO()
    Image.new('RGB', (40, 60), farbe).save(puffer, 'PNG')
    return puffer.getvalue()


def datei(name, farbe=(120, 130, 140)):
    return SimpleUploadedFile(name, png(farbe), content_type='image/png')


class BlendermodellendpunkteTest(TransactionTestCase):
    """`TransactionTestCase`: `zustand` ist async und liest die Datenbank in einem eigenen Faden."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='blendermodell_', dir=Pruefablage.wurzel()))
        self.umlenkung = override_settings(OBJECTS_ROOT=self.tmp)
        self.umlenkung.enable()
        patcher = mock.patch.object(Meshfiguroptionen, '_referenzen', return_value=[('', '—')])
        patcher.start()
        self.addCleanup(patcher.stop)
        # Die Liste der Prüf-KIs fragt sonst Ollama auf diesem Rechner.
        ollama = mock.patch.object(
            Ollamamodelle, 'mit_bildern', return_value=[('qwen3.8:27b', 'qwen3.8:27b')]
        )
        ollama.start()
        self.addCleanup(ollama.stop)
        self.client = Client(HTTP_HOST='127.0.0.1')

    def tearDown(self):
        self.umlenkung.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _anlegen(self, name='Damira', **weitere):
        daten = {
            'name': name,
            'starten': '0',
            'rollen': json.dumps({'vorn.png': 'vorne', 'hinten.png': 'hinten'}),
            'bilder': [datei('vorn.png'), datei('hinten.png', (10, 20, 30))],
            **weitere,
        }
        antwort = self.client.post('/api/blendermodell/anlegen/', daten)
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        return Blendermodellauftrag.objects.get(pk=antwort.json()['id']), antwort.json()

    def _post(self, adresse, daten=None, **weitere):
        return self.client.post(adresse, json.dumps(daten or {}), content_type='application/json', **weitere)

    # ---------------------------------------------------------------- Anlegen

    def test_anlegen_legt_fotos_rollen_und_vorlage_an_und_startet_nicht(self):
        job, antwort = self._anlegen()
        self.assertFalse(antwort['gestartet'])
        self.assertEqual((job.status, job.progress), ('angelegt', 0))
        self.assertEqual(
            [(b['datei'], b['rolle'], b['gewicht']) for b in job.bilder],
            [('vorn.png', 'vorne', 100), ('hinten.png', 'hinten', 100)],
        )
        ablage = Blendermodellablage(job.kennung)
        self.assertEqual(ablage.eingaenge(), ['hinten.png', 'vorn.png'])
        self.assertTrue(ablage.netz('vorlage.png').is_file(), 'das kleine Bild der Tabelle')
        self.assertEqual(job.ergebnis, {'vorlage_foto': 'vorlage.png'})
        self.assertEqual(job.optionen, Blendermodelloptionen.pruefen({}))

    def test_anlegen_ohne_name_oder_bilder_ist_400(self):
        self.assertEqual(
            self.client.post(
                '/api/blendermodell/anlegen/', {'name': ' ', 'bilder': datei('a.png')}
            ).status_code,
            400,
        )
        self.assertEqual(self.client.post('/api/blendermodell/anlegen/', {'name': 'X'}).status_code, 400)
        self.assertEqual(
            self.client.post(
                '/api/blendermodell/anlegen/',
                {'name': 'X', 'bilder': SimpleUploadedFile('a.txt', b'kein bild')},
            ).status_code,
            400,
        )
        self.assertEqual(Blendermodellauftrag.objects.count(), 0)

    def test_seite_und_zustand(self):
        job, _ = self._anlegen()
        seite = self.client.get('/blendermodell/%s/' % job.kennung)
        self.assertEqual(seite.status_code, 200)
        self.assertContains(seite, 'blendermodell-daten')
        zustand = self.client.get('/api/blendermodell/%s/zustand/' % job.id).json()
        self.assertEqual(zustand['schritte'], list(Blendermodelllauf.SCHRITTE))
        self.assertEqual(zustand['status'], 'angelegt')
        self.assertEqual(len(zustand['bilder']), 2)
        self.assertEqual({p['art'] for p in zustand['pfade']}, {'ordner', 'netz', 'ablage'})
        self.assertEqual(self.client.get('/blendermodell/').status_code, 200)

    # --------------------------------------------------------- Bildauswahl

    def test_rolle_gewicht_und_reihenfolge(self):
        job, _ = self._anlegen()
        self.assertEqual(
            self._post('/api/blendermodell/%s/rolle/vorn.png/' % job.id, {'rolle': 'aus'}).status_code, 200
        )
        self._post('/api/blendermodell/%s/gewicht/hinten.png/' % job.id, {'gewicht': 250})
        antwort = self._post(
            '/api/blendermodell/%s/reihenfolge/' % job.id, {'datei': 'hinten.png', 'index': 1}
        )
        self.assertEqual(antwort.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(
            [(b['datei'], b['rolle'], b['gewicht']) for b in job.bilder],
            [('hinten.png', 'hinten', 100), ('vorn.png', 'aus', 100)],
            'Gewicht wird auf 0…100 begrenzt, Platz 1 ist jetzt das Rückenfoto',
        )
        self.assertEqual(
            self._post(
                '/api/blendermodell/%s/rolle/gibtsnicht.png/' % job.id, {'rolle': 'vorne'}
            ).status_code,
            404,
        )

    def test_fotos_hinzufuegen_ersetzen_und_entfernen(self):
        job, _ = self._anlegen()
        ablage = Blendermodellablage(job.kennung)
        antwort = self.client.post('/api/blendermodell/%s/fotos/' % job.id, {'bilder': datei('seite.png')})
        self.assertEqual(
            [(b['datei'], b['rolle']) for b in antwort.json()['bilder']][-1], ('seite.png', 'aus')
        )
        self._post('/api/blendermodell/%s/gewicht/hinten.png/' % job.id, {'gewicht': 40})
        antwort = self.client.post(
            '/api/blendermodell/%s/foto/hinten.png/ersetzen/' % job.id, {'bild': datei('neu.png')}
        )
        ersetzt = next(b for b in antwort.json()['bilder'] if b['datei'] == 'neu.png')
        self.assertEqual((ersetzt['rolle'], ersetzt['gewicht']), ('hinten', 40), 'Rolle und Gewicht bleiben')
        self.assertFalse((ablage.unter('eingang') / 'hinten.png').exists(), 'die alte Datei ist weg')
        for name in ('neu.png', 'seite.png'):
            self.assertEqual(
                self._post('/api/blendermodell/%s/foto/%s/loeschen/' % (job.id, name)).status_code, 200
            )
        self.assertEqual(
            self._post('/api/blendermodell/%s/foto/vorn.png/loeschen/' % job.id).status_code,
            400,
            'das letzte Foto bleibt',
        )
        self.assertEqual(self._post('/api/blendermodell/%s/foto/x.png/loeschen/' % job.id).status_code, 404)

    def test_waehrend_des_laufs_geht_die_bildauswahl_die_einstellungen_und_ein_neuer_start_nicht(self):
        """Edgar, 29.09.2026: „die sollen nicht gesperrt sein beim Lauf" — die Fotos sind nur Referenz für
        den Bau, kein Live-Eingang eines Netz-Schritts mehr. Gesperrt bleiben nur Einstellungen (der Lauf
        liest sie) und ein zweiter Start."""
        job, _ = self._anlegen()
        Blendermodellauftrag.objects.filter(pk=job.pk).update(status='laeuft', pid=os.getpid())
        antwort = self.client.post('/api/blendermodell/%s/fotos/' % job.id, {'bilder': datei('x.png')})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(
            self._post('/api/blendermodell/%s/foto/hinten.png/loeschen/' % job.id).status_code, 200
        )
        self.assertEqual(
            self._post('/api/blendermodell/%s/rolle/vorn.png/' % job.id, {'rolle': 'aus'}).status_code, 200
        )
        self.assertEqual(
            self._post('/api/blendermodell/%s/einstellungen/' % job.id, {'optionen': {}}).status_code, 409
        )
        self.assertEqual(self._post('/api/blendermodell/%s/starten/' % job.id).status_code, 409)

    # ------------------------------------------------- Optionen und Lauf

    def test_einstellungen_mischen_die_gruppen(self):
        job, _ = self._anlegen()
        self._post('/api/blendermodell/%s/einstellungen/' % job.id, {'optionen': {'kostuem': {'runden': 7}}})
        self._post(
            '/api/blendermodell/%s/einstellungen/' % job.id, {'optionen': {'figur': {'basis': 'masculine'}}}
        )
        job.refresh_from_db()
        self.assertEqual(
            (job.optionen['kostuem']['runden'], job.optionen['figur']['basis']), (7, 'masculine')
        )

    def test_ab_einem_spaeteren_schritt_geht_es_nur_mit_grundfigur(self):
        job, _ = self._anlegen()
        antwort = self._post('/api/blendermodell/%s/starten/' % job.id, {'ab': 'kostuem', 'bis': 'kostuem'})
        self.assertEqual(antwort.status_code, 409)
        self.assertIn('keine Grundfigur', antwort.json()['error'])
        job.refresh_from_db()
        self.assertEqual(job.status, 'angelegt', 'nichts gestartet')

    def test_die_grafikkarte_gehoert_einem_auftrag_nach_dem_anderen(self):
        job, _ = self._anlegen('Erster')
        anderer, _ = self._anlegen('Zweiter')
        self.assertEqual(Blendermodellgpu.belegt_durch(job), '')
        Blendermodellauftrag.objects.filter(pk=anderer.pk).update(status='laeuft', pid=os.getpid())
        self.assertIn('Zweiter', Blendermodellgpu.belegt_durch(job))
        self.assertEqual(Blendermodellgpu.belegt_durch(anderer), '', 'ein Lauf blockiert sich nicht selbst')
        self.assertEqual(self._post('/api/blendermodell/%s/starten/' % job.id).status_code, 409)

    # ----------------------------------------- gemeinsame Register aller Bereiche

    def test_name_duplizieren_und_laufende_kennen_den_bereich(self):
        job, _ = self._anlegen()
        antwort = self._post('/api/modell-aus-dateien/blendermodell/%s/name/' % job.id, {'name': 'Umbenannt'})
        self.assertEqual(antwort.status_code, 200)
        Blendermodellauftrag.objects.filter(pk=job.pk).update(
            ergebnis={'netz': {'flaechen': 5}},
            optionen=Blendermodelloptionen.pruefen({'figur': {'basis': 'masculine'}}),
        )
        antwort = self._post('/api/modell-aus-dateien/blendermodell/duplizieren/', {'ids': [str(job.id)]})
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        kopie = Blendermodellauftrag.objects.get(pk=antwort.json()['auftraege'][0]['id'])
        self.assertEqual(kopie.name, 'Umbenannt (Kopie)')
        self.assertEqual(kopie.optionen['figur']['basis'], 'masculine')
        self.assertEqual(kopie.ergebnis, {}, 'die Ausgabe wird nicht kopiert')
        self.assertEqual(
            [(b['datei'], b['rolle']) for b in kopie.bilder],
            [('vorn.png', 'vorne'), ('hinten.png', 'hinten')],
        )
        self.assertTrue((Blendermodellablage(kopie.kennung).unter('eingang') / 'vorn.png').is_file())
        self.assertFalse(Blendermodellablage(kopie.kennung).netz('vorlage.png').exists())
        Blendermodellauftrag.objects.filter(pk=job.pk).update(
            status='laeuft', progress=40, progress_detail='netz'
        )
        laufende = self.client.get('/api/modell-aus-dateien/laufende/').json()
        self.assertEqual([z['id'] for z in laufende['blendermodell']], [str(job.id)])

    def test_texturquelle_findet_die_kacheln_eines_blendermodell_auftrags(self):
        job, _ = self._anlegen()
        ziel = Blendermodellablage(job.kennung).ergebnis('meshfigur_1001.jpg')
        ziel.write_bytes(b'kachel')
        adresse = '/api/blendermodell/%s/datei/ergebnis/meshfigur_1001.jpg?t=1' % job.id
        self.assertEqual(Texturquelle.pfad(adresse), ziel.resolve())

    # ------------------------------------------------ Dateien, Tabelle, Löschen

    def test_datei_liefert_nur_lesbare_ordner_ohne_pfad(self):
        job, _ = self._anlegen()
        Blendermodellablage(job.kennung).arbeit('auftrag.json').write_text('{}')
        self.assertEqual(
            self.client.get('/api/blendermodell/%s/datei/eingang/vorn.png' % job.id).status_code, 200
        )
        self.assertEqual(
            self.client.get('/api/blendermodell/%s/datei/netz/vorlage.png' % job.id).status_code, 200
        )
        for adresse in ('arbeit/auftrag.json', 'eingang/gibtsnicht.png', 'eingang/..%2Fauftrag.log'):
            self.assertEqual(
                self.client.get('/api/blendermodell/%s/datei/%s' % (job.id, adresse)).status_code,
                404,
                adresse,
            )

    def test_die_tabelle_zeigt_zeile_link_und_bilder(self):
        job, _ = self._anlegen()
        tabelle = Blendermodelltabelle(Blendermodellauftrag.objects.all()).tabelle()
        self.assertEqual(tabelle['key'], 'blendermodell')
        self.assertEqual([s['key'] for s in tabelle['spalten']][:4], ['wahl', 'vorlage', 'netz', 'icon'])
        zeile = tabelle['zeilen'][0]
        self.assertEqual(zeile['id'], str(job.id))
        self.assertIn('href="/blendermodell/%s/"' % job.kennung, zeile['html'])
        self.assertIn('/api/blendermodell/%s/datei/netz/vorlage.png?v=' % job.id, zeile['html'])
        self.assertEqual(len(tabelle['spalten']), zeile['html'].count('<td'), 'eine Zelle je Spalte')

    def test_loeschen_entfernt_ordner_und_eintrag(self):
        job, _ = self._anlegen()
        ordner = Blendermodellablage(job.kennung).ordner()
        self.assertTrue(ordner.is_dir())
        self.assertEqual(
            self._post('/api/blendermodell/loeschen/', {'ids': [str(job.id)]}).json()['geloescht'], 1
        )
        self.assertFalse(ordner.exists())
        self.assertFalse(Blendermodellauftrag.objects.filter(pk=job.pk).exists())
