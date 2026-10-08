# -*- coding: utf-8 -*-
"""Bereich „2D3D Kleider" (30.09.2026) — Endpunkte: Anlegen, Seite, Bildauswahl, Lauf, Runden, gemeinsame
Register.

Die Auftragsordner liegen während der Prüfung in `ProjektTemp/pruefungen` (`Pruefablage`), nie unter
`3DObjects` — `OBJECTS_ROOT` wird umgelenkt. Gestartet wird nichts (`starten=0`): kein Arbeitsprozess, keine
Grafikkarte. Ein laufender Auftrag wird mit der PID dieses Prozesses vorgetäuscht (`Prozesspruefung.lebt`).
Optionen, Lauf und Ablage: `test_engine2d3dkleider.py`.
"""

import io
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from PIL import Image

from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from core.daten.texturquelle import Texturquelle
from core.dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from core.dienste.engine2d3dkleidergpu import Engine2d3dKleidergpu
from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
from core.dienste.engine2d3dkleidertabelle import Engine2d3dKleidertabelle
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.ollamamodelle import Ollamamodelle
from core.models import Blendermodellauftrag, Engine2d3dKleiderauftrag

from ._pruefablage import Pruefablage


def png(farbe=(120, 130, 140)):
    puffer = io.BytesIO()
    Image.new('RGB', (40, 60), farbe).save(puffer, 'PNG')
    return puffer.getvalue()


def datei(name, farbe=(120, 130, 140)):
    return SimpleUploadedFile(name, png(farbe), content_type='image/png')


class Engine2d3dKleideraufbau:
    """Auftragsordner, abgefangene Kataloge und ein Client — für beide Klassen unten.

    AUFGETEILT AM 30.09.2026: Die Fälle liefen alle als `TransactionTestCase`, weil EINER davon
    es braucht (`zustand` ist async und liest die Datenbank in einem eigenen Faden). Ein
    `TransactionTestCase` leert nach jedem Fall alle Tabellen, statt eine Transaktion
    zurückzudrehen — das Modul stand damit bei 1,33 s und riss die 1-Sekunden-Schwelle aus
    `projekt.md`. Die 22 übrigen Fälle laufen jetzt als gewöhnlicher `TestCase`.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='engine2d3dkleider_', dir=Pruefablage.wurzel()))
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
        antwort = self.client.post('/api/engine2d3dkleider/anlegen/', daten)
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        return Engine2d3dKleiderauftrag.objects.get(pk=antwort.json()['id']), antwort.json()

    def _post(self, adresse, daten=None, **weitere):
        return self.client.post(adresse, json.dumps(daten or {}), content_type='application/json', **weitere)


class Engine2d3dKleiderzustandTest(Engine2d3dKleideraufbau, TransactionTestCase):
    """Der eine Fall, der echte Tabellen braucht: `zustand` ist async und liest die Datenbank in
    einem eigenen Faden — der sähe von einer offenen Transaktion nichts."""

    def test_seite_und_zustand(self):
        job, _ = self._anlegen()
        seite = self.client.get(reverse('engine2d3dkleider_auftrag', args=[job.kennung]))        # `/2d3dKleider/<kennung>/` (Umbenennung der Seiten, Oktober 2026)
        self.assertEqual(seite.status_code, 200)
        self.assertContains(seite, 'engine2d3dkleider-daten')
        zustand = self.client.get('/api/engine2d3dkleider/%s/zustand/' % job.id).json()
        self.assertEqual(zustand['schritte'], list(Engine2d3dKleiderlauf.SCHRITTE))
        self.assertEqual(zustand['status'], 'angelegt')
        self.assertEqual(len(zustand['bilder']), 2)
        self.assertEqual({p['art'] for p in zustand['pfade']}, {'ordner', 'ablage'})
        liste = self.client.get('/2d3dKleider/')
        self.assertEqual(liste.status_code, 200)
        self.assertContains(liste, 'engine2d3dkleider-form', msg_prefix='das Formular „Neuer Auftrag"')
        self.assertContains(liste, 'engine2d3dkleider-rollen')


class Engine2d3dKleiderendpunkteTest(Engine2d3dKleideraufbau, TestCase):
    """Alles übrige — rollt nach jedem Fall eine Transaktion zurück, statt die Tabellen zu leeren."""

    # ---------------------------------------------------------------- Anlegen

    def test_anlegen_legt_fotos_rollen_und_vorlage_an_und_startet_nicht(self):
        job, antwort = self._anlegen()
        self.assertFalse(antwort['gestartet'])
        self.assertEqual((job.status, job.progress), ('angelegt', 0))
        self.assertEqual(
            [(b['datei'], b['rolle'], b['gewicht']) for b in job.bilder],
            [('vorn.png', 'vorne', 100), ('hinten.png', 'hinten', 100)],
        )
        ablage = Engine2d3dKleiderablage(job.kennung)
        self.assertEqual(ablage.eingaenge(), ['hinten.png', 'vorn.png'])
        self.assertTrue(ablage.vorlage('vorlage.png').is_file(), 'das kleine Bild der Tabelle')
        self.assertEqual(job.ergebnis, {'vorlage_foto': 'vorlage.png'})
        self.assertEqual(job.optionen, Engine2d3dKleideroptionen.pruefen({}))

    def test_anlegen_ohne_name_oder_bilder_ist_400(self):
        self.assertEqual(
            self.client.post('/api/engine2d3dkleider/anlegen/', {'name': ' ', 'bilder': datei('a.png')}).status_code,
            400,
        )
        self.assertEqual(self.client.post('/api/engine2d3dkleider/anlegen/', {'name': 'X'}).status_code, 400)
        self.assertEqual(
            self.client.post(
                '/api/engine2d3dkleider/anlegen/', {'name': 'X', 'bilder': SimpleUploadedFile('a.txt', b'kein bild')}
            ).status_code,
            400,
        )
        self.assertEqual(Engine2d3dKleiderauftrag.objects.count(), 0)

    # --------------------------------------------------------- Bildauswahl

    def test_rolle_gewicht_und_reihenfolge(self):
        job, _ = self._anlegen()
        self.assertEqual(
            self._post('/api/engine2d3dkleider/%s/rolle/vorn.png/' % job.id, {'rolle': 'aus'}).status_code, 200
        )
        self._post('/api/engine2d3dkleider/%s/gewicht/hinten.png/' % job.id, {'gewicht': 250})
        antwort = self._post('/api/engine2d3dkleider/%s/reihenfolge/' % job.id, {'datei': 'hinten.png', 'index': 1})
        self.assertEqual(antwort.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(
            [(b['datei'], b['rolle'], b['gewicht']) for b in job.bilder],
            [('hinten.png', 'hinten', 100), ('vorn.png', 'aus', 100)],
            'Gewicht wird auf 0…100 begrenzt, Platz 1 ist jetzt das Rückenfoto',
        )
        self.assertEqual(
            self._post('/api/engine2d3dkleider/%s/rolle/gibtsnicht.png/' % job.id, {'rolle': 'vorne'}).status_code,
            404,
        )

    def test_fotos_hinzufuegen_ersetzen_und_entfernen(self):
        job, _ = self._anlegen()
        ablage = Engine2d3dKleiderablage(job.kennung)
        antwort = self.client.post('/api/engine2d3dkleider/%s/fotos/' % job.id, {'bilder': datei('seite.png')})
        self.assertEqual(
            [(b['datei'], b['rolle']) for b in antwort.json()['bilder']][-1], ('seite.png', 'aus')
        )
        self._post('/api/engine2d3dkleider/%s/gewicht/hinten.png/' % job.id, {'gewicht': 40})
        antwort = self.client.post(
            '/api/engine2d3dkleider/%s/foto/hinten.png/ersetzen/' % job.id, {'bild': datei('neu.png')}
        )
        ersetzt = next(b for b in antwort.json()['bilder'] if b['datei'] == 'neu.png')
        self.assertEqual((ersetzt['rolle'], ersetzt['gewicht']), ('hinten', 40), 'Rolle und Gewicht bleiben')
        self.assertFalse((ablage.unter('eingang') / 'hinten.png').exists(), 'die alte Datei ist weg')
        for name in ('neu.png', 'seite.png'):
            self.assertEqual(
                self._post('/api/engine2d3dkleider/%s/foto/%s/loeschen/' % (job.id, name)).status_code, 200
            )
        self.assertEqual(
            self._post('/api/engine2d3dkleider/%s/foto/vorn.png/loeschen/' % job.id).status_code,
            400,
            'das letzte Foto bleibt',
        )
        self.assertEqual(self._post('/api/engine2d3dkleider/%s/foto/x.png/loeschen/' % job.id).status_code, 404)

    def test_waehrend_des_laufs_geht_die_bildauswahl_die_einstellungen_und_ein_neuer_start_nicht(self):
        """Die Fotos sind nur Referenz für die Note, kein Live-Eingang: Hinzufügen, Ersetzen, Entfernen und
        Rolle gehen auch während eines Laufs. Gesperrt bleiben nur Einstellungen (der Lauf liest sie) und
        ein zweiter Start."""
        job, _ = self._anlegen()
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(status='laeuft', pid=os.getpid())
        antwort = self.client.post('/api/engine2d3dkleider/%s/fotos/' % job.id, {'bilder': datei('x.png')})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(self._post('/api/engine2d3dkleider/%s/foto/hinten.png/loeschen/' % job.id).status_code, 200)
        self.assertEqual(
            self._post('/api/engine2d3dkleider/%s/rolle/vorn.png/' % job.id, {'rolle': 'aus'}).status_code, 200
        )
        self.assertEqual(
            self._post('/api/engine2d3dkleider/%s/einstellungen/' % job.id, {'optionen': {}}).status_code, 409
        )
        self.assertEqual(self._post('/api/engine2d3dkleider/%s/starten/' % job.id).status_code, 409)

    # ------------------------------------------------- Optionen und Lauf

    def test_einstellungen_mischen_die_gruppen(self):
        job, _ = self._anlegen()
        self._post('/api/engine2d3dkleider/%s/einstellungen/' % job.id, {'optionen': {'iterationen': {'runden': 7}}})
        self._post(
            '/api/engine2d3dkleider/%s/einstellungen/' % job.id, {'optionen': {'figur': {'basis': 'masculine'}}}
        )
        job.refresh_from_db()
        self.assertEqual(
            (job.optionen['iterationen']['runden'], job.optionen['figur']['basis']), (7, 'masculine')
        )

    def test_ab_einem_spaeteren_schritt_geht_es_nur_mit_grundfigur(self):
        job, _ = self._anlegen()
        antwort = self._post(
            '/api/engine2d3dkleider/%s/starten/' % job.id, {'ab': 'iterationen', 'bis': 'iterationen'}
        )
        self.assertEqual(antwort.status_code, 409)
        self.assertIn('keine Grundfigur', antwort.json()['error'])
        job.refresh_from_db()
        self.assertEqual(job.status, 'angelegt', 'nichts gestartet')

    def test_die_grafikkarte_gehoert_einem_auftrag_nach_dem_anderen(self):
        job, _ = self._anlegen('Erster')
        anderer, _ = self._anlegen('Zweiter')
        self.assertEqual(Engine2d3dKleidergpu.belegt_durch(job), '')
        Engine2d3dKleiderauftrag.objects.filter(pk=anderer.pk).update(status='laeuft', pid=os.getpid())
        self.assertIn('Zweiter', Engine2d3dKleidergpu.belegt_durch(job))
        self.assertEqual(Engine2d3dKleidergpu.belegt_durch(anderer), '', 'ein Lauf blockiert sich nicht selbst')
        self.assertEqual(self._post('/api/engine2d3dkleider/%s/starten/' % job.id).status_code, 409)

    def test_ein_laufender_blendermodell_auftrag_haelt_die_karte_auch(self):
        job, _ = self._anlegen()
        fremd = Blendermodellauftrag.objects.create(
            kennung='2026.09.30.00.00.01', name='Zauberer', status='laeuft', pid=os.getpid()
        )
        hinweis = Engine2d3dKleidergpu.belegt_durch(job)
        self.assertIn('Zauberer', hinweis)
        self.assertIn('BlenderModel', hinweis)
        fremd.delete()

    # ----------------------------------------- gemeinsame Register aller Bereiche

    def test_name_duplizieren_und_laufende_kennen_den_bereich(self):
        job, _ = self._anlegen()
        antwort = self._post('/api/modell-aus-dateien/engine2d3dkleider/%s/name/' % job.id, {'name': 'Umbenannt'})
        self.assertEqual(antwort.status_code, 200)
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            ergebnis={'kreislauf': {'runde_bester': 3}},
            optionen=Engine2d3dKleideroptionen.pruefen({'figur': {'basis': 'masculine'}}),
        )
        antwort = self._post('/api/modell-aus-dateien/engine2d3dkleider/duplizieren/', {'ids': [str(job.id)]})
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        kopie = Engine2d3dKleiderauftrag.objects.get(pk=antwort.json()['auftraege'][0]['id'])
        self.assertEqual(kopie.name, 'Umbenannt (Kopie)')
        self.assertEqual(kopie.optionen['figur']['basis'], 'masculine')
        self.assertEqual(kopie.ergebnis, {}, 'die Ausgabe wird nicht kopiert')
        self.assertEqual(
            [(b['datei'], b['rolle']) for b in kopie.bilder],
            [('vorn.png', 'vorne'), ('hinten.png', 'hinten')],
        )
        self.assertTrue((Engine2d3dKleiderablage(kopie.kennung).unter('eingang') / 'vorn.png').is_file())
        self.assertFalse(Engine2d3dKleiderablage(kopie.kennung).vorlage('vorlage.png').exists())
        self.assertEqual(antwort.json()['auftraege'][0]['url'], reverse('engine2d3dkleider_auftrag', args=[kopie.kennung]))
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            status='laeuft', progress=40, progress_detail='iterationen'
        )
        laufende = self.client.get('/api/modell-aus-dateien/laufende/').json()
        self.assertEqual([z['id'] for z in laufende['engine2d3dkleider']], [str(job.id)])

    def test_texturquelle_findet_die_kacheln_eines_engine2d3dkleider_auftrags(self):
        job, _ = self._anlegen()
        ziel = Engine2d3dKleiderablage(job.kennung).ergebnis('meshfigur_1001.jpg')
        ziel.write_bytes(b'kachel')
        adresse = '/api/engine2d3dkleider/%s/datei/ergebnis/meshfigur_1001.jpg?t=1' % job.id
        self.assertEqual(Texturquelle.pfad(adresse), ziel.resolve())

    # ------------------------------------------------ Dateien, Tabelle, Löschen

    def test_datei_liefert_nur_lesbare_ordner_ohne_pfad(self):
        job, _ = self._anlegen()
        Engine2d3dKleiderablage(job.kennung).arbeit('auftrag.json').write_text('{}')
        self.assertEqual(
            self.client.get('/api/engine2d3dkleider/%s/datei/eingang/vorn.png' % job.id).status_code, 200
        )
        self.assertEqual(
            self.client.get('/api/engine2d3dkleider/%s/datei/vorlage/vorlage.png' % job.id).status_code, 200
        )
        for adresse in (
            'arbeit/auftrag.json',
            'netz/vorlage.png',
            'vorbereitet/vorn.png',
            'eingang/gibtsnicht.png',
            'eingang/..%2Fauftrag.log',
        ):
            self.assertEqual(
                self.client.get('/api/engine2d3dkleider/%s/datei/%s' % (job.id, adresse)).status_code, 404, adresse
            )

    def test_die_tabelle_zeigt_zeile_link_und_bilder(self):
        job, _ = self._anlegen()
        tabelle = Engine2d3dKleidertabelle(Engine2d3dKleiderauftrag.objects.all()).tabelle()
        self.assertEqual(tabelle['key'], 'engine2d3dkleider')
        self.assertEqual(
            [s['key'] for s in tabelle['spalten']],
            ['wahl', 'vorlage', 'name', 'bilder', 'ki', 'status', 'runden', 'abweichung', 'qualitaet_mesh', 'qualitaet_3d', 'qualitaet_textur',
             'qualitaet_mesh_gesamt', 'qualitaet_kleider', 'qualitaet_haar', 'qualitaet_gesicht', 'qualitaet_koerper', 'dauer', 'erstellt'],
        )
        zeile = tabelle['zeilen'][0]
        self.assertEqual(zeile['id'], str(job.id))
        self.assertIn('href="%s"' % reverse('engine2d3dkleider_auftrag', args=[job.kennung]), zeile['html'])
        self.assertIn('/api/engine2d3dkleider/%s/datei/vorlage/vorlage.png?v=' % job.id, zeile['html'])
        self.assertEqual(len(tabelle['spalten']), zeile['html'].count('<td'), 'eine Zelle je Spalte')

    def test_die_tabelle_zeigt_runden_abweichung_und_dauer(self):
        job, _ = self._anlegen()
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            ergebnis={
                'iterationen': [{'runde': 1}, {'runde': 2}],
                'kreislauf': {'note': {'abweichung': 0.12346}},
                'dauer_s': 61,
            }
        )
        zeile = Engine2d3dKleidertabelle(Engine2d3dKleiderauftrag.objects.all()).tabelle()['zeilen'][0]['html']
        self.assertIn('<td class="num" data-sort="2">2</td>', zeile)
        self.assertIn('0,1235', zeile, 'vier Stellen mit Komma')
        self.assertIn('1:01 min', zeile)

    def test_runden_loeschen_ohne_lauf_sofort_mit_lauf_vorgemerkt(self):
        job, _ = self._anlegen()
        ablage = Engine2d3dKleiderablage(job.kennung)
        for n in (1, 2):
            ablage.iterationen('runde_%03d_vergleich.png' % n).write_bytes(b'x')
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            ergebnis={
                'iterationen': [
                    {'runde': n, 'dateien': {'vergleich': 'runde_%03d_vergleich.png' % n}, 'je_ansicht': []}
                    for n in (1, 2)
                ],
                'kreislauf': {'verlauf': [[1, 0.5, 0.5], [2, 0.4, 0.4]]},
            }
        )
        antwort = self._post('/api/engine2d3dkleider/%s/runden/loeschen/' % job.id, {'runden': [1]})
        self.assertEqual(antwort.json(), {'ok': True, 'geloescht': [1], 'vorgemerkt': []})
        job.refresh_from_db()
        self.assertEqual([r['runde'] for r in job.ergebnis['iterationen']], [2])
        self.assertFalse(ablage.iterationen('runde_001_vergleich.png').exists())
        self.assertEqual(len(job.ergebnis['kreislauf']['verlauf']), 2, 'die Kurve bleibt')
        # Mit Lauf schreibt nur der Lauf in `ergebnis`: Die Runde wird vorgemerkt, die Datei bleibt bis dahin.
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(status='laeuft', pid=os.getpid())
        antwort = self._post('/api/engine2d3dkleider/%s/runden/loeschen/' % job.id, {'runden': [2]})
        self.assertEqual((antwort.json()['geloescht'], antwort.json()['vorgemerkt']), ([], [2]))
        self.assertTrue(ablage.iterationen('runde_002_vergleich.png').exists())
        self.assertEqual(
            self._post('/api/engine2d3dkleider/%s/runden/loeschen/' % job.id, {'runden': []}).status_code, 400
        )

    def test_loeschen_entfernt_ordner_und_eintrag(self):
        job, _ = self._anlegen()
        ordner = Engine2d3dKleiderablage(job.kennung).ordner()
        self.assertTrue(ordner.is_dir())
        self.assertEqual(
            self._post('/api/engine2d3dkleider/loeschen/', {'ids': [str(job.id)]}).json()['geloescht'], 1
        )
        self.assertFalse(ordner.exists())
        self.assertFalse(Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).exists())

    # ------------------------------------------- die Knöpfe ohne eigenen Fall (30.09.2026)

    def test_der_knopf_anhalten_beendet_den_lauf(self):
        """„Anhalten" steht zweimal auf der Seite (im Laufband und neben „Neu berechnen") und
        geht beide Male hierher."""
        job, _ = self._anlegen()
        with mock.patch.object(Engine2d3dKleiderarbeiter, 'anhalten') as gestoppt:
            antwort = self._post('/api/engine2d3dkleider/%s/anhalten/' % job.id)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json(), {'ok': True})
        self.assertEqual(gestoppt.call_args[0][0].pk, job.pk)

    def test_anhalten_eines_unbekannten_auftrags_ist_404(self):
        self.assertEqual(
            self._post('/api/engine2d3dkleider/00000000-0000-0000-0000-000000000000/anhalten/').status_code,
            404)

    def test_der_katalog_liefert_die_optionen_der_seite(self):
        """Die Auswahlfelder der Karte „Optionen" werden daraus gebaut."""
        antwort = self.client.get('/api/engine2d3dkleider/katalog/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(sorted(antwort.json()), sorted(Engine2d3dKleideroptionen.katalog()))

    def test_modell_speichern_erst_wenn_die_figur_fertig_ist(self):
        """Der Knopf schreibt in Edgars Bibliothek (`data/models/`) — hier nur der Vertrag, die
        Ablage selbst ist abgefangen (`projekt.md`: Prüfungen schreiben nicht in seine Daten)."""
        job, _ = self._anlegen()
        # Frisch angelegt gibt es noch keine Stellung: der Knopf ist gesperrt.
        self.assertEqual(self._post('/api/engine2d3dkleider/%s/modell/' % job.id,
                                    {'name': '_test_haar'}).status_code, 409)
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            ergebnis={'regler': {'stellung': {'kopf': 1.0}}})
        with mock.patch.object(Engine2d3dKleiderspeichern, 'fuer') as speichern:
            speichern.return_value.modell_speichern.return_value = '_test_haar'
            antwort = self._post('/api/engine2d3dkleider/%s/modell/' % job.id, {'name': '_test_haar'})
        self.assertEqual(antwort.json(), {'ok': True, 'modell': '_test_haar'})
        speichern.return_value.modell_speichern.assert_called_once_with('_test_haar')

    def test_modell_speichern_geht_nicht_waehrend_der_lauf_rechnet(self):
        job, _ = self._anlegen()
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            status='laeuft', pid=os.getpid(), ergebnis={'regler': {'stellung': {'kopf': 1.0}}})
        self.assertEqual(self._post('/api/engine2d3dkleider/%s/modell/' % job.id,
                                    {'name': '_test_haar'}).status_code, 409)

    def test_ein_leerer_name_kommt_als_klartext_zurueck_nicht_als_absturz(self):
        job, _ = self._anlegen()
        Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(
            ergebnis={'regler': {'stellung': {'kopf': 1.0}}})
        with mock.patch.object(Engine2d3dKleiderspeichern, 'fuer') as speichern:
            speichern.return_value.modell_speichern.side_effect = ValueError('Name fehlt')
            antwort = self._post('/api/engine2d3dkleider/%s/modell/' % job.id, {'name': ''})
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(antwort.json()['error'], 'Name fehlt')
