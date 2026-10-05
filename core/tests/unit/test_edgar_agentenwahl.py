# -*- coding: utf-8 -*-
"""Paket `Edgar`: die Auswahl der KI (`Agentenwahl`) und ihre drei Aufrufer — `Agentenaufruf` (Claude), `Ollamaaufruf` (Qwen 3.8 lokal), `Openrouteraufruf` (Nemotron, kostenlos) — mit
`Httpanfrage` und `Bildkodierung` (05.10.2026). Kein echter Dienst: Antworten werden den `auswerten`-Methoden als Wörterbuch gegeben, `Httpanfrage` spricht mit einem Dienst auf 127.0.0.1
(Port vom System), Bilder liegen unter `ProjektTemp`. Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

import json
import shutil
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Edgar.agentenaufruf import Agentenaufruf
from Edgar.agentenwahl import Agentenwahl
from Edgar.auftragsfehler import Agentenfehler, Angehalten
from Edgar.bildkodierung import Bildkodierung
from Edgar.httpanfrage import Httpanfrage
from Edgar.ollamaaufruf import Ollamaaufruf
from Edgar.openrouteraufruf import Openrouteraufruf

PROJEKTTEMP = Path(__file__).resolve().parents[3] / 'ProjektTemp'


class DieAgentenwahl(SimpleTestCase):
    def test_der_katalog_hat_lokal_mit_qwen_und_remote_mit_sonnet_und_nemotron(self):
        katalog = Agentenwahl.katalog()
        self.assertEqual([o['wert'] for o in katalog['orte']], ['lokal', 'remote'])
        je_ort = {o: [m['wert'] for m in katalog['modelle'] if m['ort'] == o] for o in ('lokal', 'remote')}
        self.assertEqual(je_ort, {'lokal': ['qwen'], 'remote': ['sonnet', 'nemotron']})
        self.assertEqual([s['text'] for s in katalog['stufen']], ['gering', 'mittel', 'hoch', 'extra hoch'])
        self.assertTrue(Agentenwahl.pruefen(katalog['vorgabe']))

    def test_ohne_angaben_gilt_die_vorgabe_und_ein_modell_ohne_stufen_hat_keine(self):
        self.assertEqual(Agentenwahl.pruefen(), {'ort': 'remote', 'modell': 'sonnet', 'stufe': 'mittel', 'text': 'Claude Sonnet 5.5 · mittel'})
        lokal = Agentenwahl.pruefen({'ort': 'lokal', 'stufe': 'hoch'})
        self.assertEqual((lokal['modell'], lokal['stufe']), ('qwen', None))                 # ohne Modell das erste des Orts; die Stufe fällt weg

    def test_unbekanntes_wird_mit_dem_grund_abgelehnt(self):
        for falsch in ({'ort': 'mond'}, {'ort': 'lokal', 'modell': 'sonnet'}, {'ort': 'remote', 'modell': 'qwen'}, {'modell': 'gpt'}, {'stufe': 'max'}):
            with self.assertRaises(ValueError, msg=str(falsch)):
                Agentenwahl.pruefen(falsch)

    def test_bauen_gibt_den_richtigen_aufrufer_mit_der_stufe_des_dienstes(self):
        claude = Agentenwahl.bauen({'ort': 'remote', 'modell': 'sonnet', 'stufe': 'extra'}, ['A:/auftrag'])
        self.assertIsInstance(claude, Agentenaufruf)
        self.assertEqual((claude.modell, claude.effort, claude.BILDER), ('claude-sonnet-5-5', 'xhigh', 'datei'))
        nemotron = Agentenwahl.bauen({'ort': 'remote', 'modell': 'nemotron', 'stufe': 'gering'})
        self.assertIsInstance(nemotron, Openrouteraufruf)
        self.assertEqual((nemotron.modell, nemotron.stufe, nemotron.BILDER), ('nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free', 'low', 'eingebettet'))
        qwen = Agentenwahl.bauen({'ort': 'lokal'})
        self.assertIsInstance(qwen, Ollamaaufruf)
        self.assertEqual((qwen.modell, qwen.BILDER), ('qwen3.8:27b', 'eingebettet'))


class DerOllamaaufruf(SimpleTestCase):
    def test_die_anfrage_erzwingt_das_schema_gibt_den_speicher_frei_und_haengt_die_bilder_an(self):
        ordner = Path(tempfile.mkdtemp(prefix='edgar_bild_', dir=str(PROJEKTTEMP)))
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        from PIL import Image
        Image.new('RGB', (40, 20), 'red').save(ordner / 'a.png')
        daten = Ollamaaufruf('qwen3.8:27b').daten('Frage', {'type': 'object'}, [('Bild', ordner / 'a.png', 1, 1)])
        self.assertEqual((daten['stream'], daten['think'], daten['keep_alive'], daten['format']), (False, False, 0, {'type': 'object'}))
        self.assertEqual(len(daten['messages'][0]['images']), 1)
        self.assertEqual(daten['options']['num_ctx'], Ollamaaufruf.NUM_CTX)

    def test_auswerten_nimmt_den_text_und_meldet_fehler_leere_antwort_und_ein_volles_fenster(self):
        agent = Ollamaaufruf('m')
        ok = agent.auswerten(200, {'message': {'content': '{"a": 1}'}, 'prompt_eval_count': 500, 'eval_count': 20, 'total_duration': 2_000_000_000, 'model': 'm'})
        self.assertEqual((ok['antwort'], ok['kosten_usd'], ok['dauer_api_s']), ('{"a": 1}', 0.0, 2.0))
        for status, antwort in ((404, {'error': 'model not found'}), (200, {'message': {'content': ' '}}), (200, {'message': {'content': 'x'}, 'prompt_eval_count': Ollamaaufruf.NUM_CTX})):
            with self.assertRaises(Agentenfehler):
                agent.auswerten(status, antwort)


class DerOpenrouteraufruf(SimpleTestCase):
    def test_die_stufe_geht_als_reasoning_effort_und_die_bilder_als_data_url(self):
        ordner = Path(tempfile.mkdtemp(prefix='edgar_bild_', dir=str(PROJEKTTEMP)))
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        from PIL import Image
        Image.new('RGB', (40, 20), 'blue').save(ordner / 'b.png')
        daten = Openrouteraufruf('nvidia/x:free', stufe='high').daten('Frage', [('Bild', ordner / 'b.png', 1, 1)])
        self.assertEqual(daten['reasoning'], {'effort': 'high'})
        teile = daten['messages'][0]['content']
        self.assertEqual((teile[0]['type'], teile[1]['type']), ('text', 'image_url'))
        self.assertTrue(teile[1]['image_url']['url'].startswith('data:image/jpeg;base64,'))
        self.assertNotIn('reasoning', Openrouteraufruf('x').daten('Frage', []))

    def test_auswerten_auch_der_fehler_mit_http_200_wird_zur_meldung(self):
        agent = Openrouteraufruf('x')
        ok = agent.auswerten(200, {'choices': [{'message': {'content': '{"a": 1}'}}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'cost': 0}, 'model': 'x'})
        self.assertEqual((ok['antwort'], ok['kosten_usd']), ('{"a": 1}', 0.0))
        for status, antwort in ((200, {'error': {'message': 'Rate limit'}}), (401, {'error': {'message': 'No auth'}}), (200, {'choices': [{'message': {'content': None}, 'finish_reason': 'length'}]})):
            with self.assertRaises(Agentenfehler):
                agent.auswerten(status, antwort)

    def test_ohne_schluesseldatei_steht_der_pfad_in_der_meldung_und_nie_der_schluessel(self):
        agent = Openrouteraufruf('x', schluessel_datei=PROJEKTTEMP / 'gibt_es_nicht.key')
        with self.assertRaises(Agentenfehler) as fehler:
            agent.fragen('Frage')
        self.assertIn('gibt_es_nicht.key', str(fehler.exception))


class _Dienst(BaseHTTPRequestHandler):
    schlaf_s = 0.0

    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length') or 0))
        time.sleep(self.schlaf_s)
        koerper = json.dumps({'ok': True}).encode()
        self.send_response(200)
        self.send_header('Content-Length', str(len(koerper)))
        self.end_headers()
        self.wfile.write(koerper)

    def log_message(self, *args):
        pass


class DieHttpanfrage(SimpleTestCase):
    def _dienst(self, schlaf_s=0.0):
        _Dienst.schlaf_s = schlaf_s
        server = ThreadingHTTPServer(('127.0.0.1', 0), _Dienst)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.shutdown)
        return 'http://127.0.0.1:%d/api' % server.server_address[1]

    def test_ein_post_liefert_status_und_json(self):
        self.assertEqual(Httpanfrage(self._dienst(), 10).senden({'a': 1}), (200, {'ok': True}))

    def test_anhalten_beendet_das_warten(self):
        anfrage = Httpanfrage(self._dienst(schlaf_s=5), 30)
        with mock.patch.object(Httpanfrage, 'TAKT_S', 0.05), self.assertRaises(Angehalten):
            anfrage.senden({}, abbrechen=lambda: True)

    def test_das_zeitlimit_wird_zum_fehler(self):
        anfrage = Httpanfrage(self._dienst(schlaf_s=5), 0.2)
        with mock.patch.object(Httpanfrage, 'TAKT_S', 0.05), self.assertRaises(Agentenfehler):
            anfrage.senden({})

    def test_ein_nicht_erreichbarer_dienst_ist_ein_fehler_mit_der_adresse(self):
        with self.assertRaises(Agentenfehler) as fehler:
            Httpanfrage('http://127.0.0.1:1/api', 5).senden({})
        self.assertIn('127.0.0.1', str(fehler.exception))


class DieBildkodierung(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='edgar_bild_', dir=str(PROJEKTTEMP)))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)

    def test_eine_breite_tafel_wird_in_teile_geschnitten_nicht_verkleinert(self):
        from PIL import Image
        Image.new('RGB', (3072, 100), 'white').save(self.ordner / 'tafel.png')
        self.assertEqual(Bildkodierung.teile(self.ordner / 'tafel.png'), 2)
        import base64
        import io
        with Image.open(io.BytesIO(base64.b64decode(Bildkodierung.kodieren(self.ordner / 'tafel.png', 2, 2)))) as teil:
            self.assertEqual(teil.size, (1536, 100))

    def test_ein_schmales_bild_bleibt_ganz(self):
        from PIL import Image
        Image.new('RGB', (800, 50), 'white').save(self.ordner / 'kopf.png')
        self.assertEqual(Bildkodierung.teile(self.ordner / 'kopf.png'), 1)

    def test_eine_fehlende_datei_ist_ein_fehler(self):
        with self.assertRaises(Agentenfehler):
            Bildkodierung.kodieren(self.ordner / 'nicht_da.png')
