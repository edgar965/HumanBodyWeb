# -*- coding: utf-8 -*-
"""Jobs und Tests von Mesh-Genesis umbenennen (`Meshgenesisname`, `Meshgenesisnameendpunkte`, 19.10.2026). Ohne Datenbank, Ordner in `Pruefablage`.

1. `name.json` im Jobordner legt sich über den Namen der Stammdaten; `name_vorgabe` behält den ursprünglichen; Kennung, Ordner und Modell bleiben. Ohne Datei bleibt der Name, eine kaputte Datei warnt.
2. `setzen` säubert den Text (Rand, Zeilenumbruch, Mehrfach-Leerzeichen), wirft bei leerem, und wer auf den ursprünglichen Namen zurückstellt, löscht die Datei.
3. Nach `setzen` gilt der neue Name sofort, auch innerhalb der Frist des Zwischenspeichers (sonst zeigte das Menü 30 s lang den alten).
4. Ein Test (`_test/<kennung>/`) nimmt den Namen aus `name.json` vor dem aus `test.json` — den schreibt jeder Neulauf neu.
5. Endpunkt der Tests: 200 mit dem gesäuberten Namen und der Datei; unbekannter Test 404; leerer Name 400 ohne Datei.

Sabotage-Gegenprobe (von Hand): in `jobs` `namen[...] or zeile['name']` durch `zeile['name']` ersetzen → Fall 1 rot; `datei.unlink` streichen → Fall 2 rot; `cls._ablage.clear()` in `setzen`
streichen → Fall 3 rot; in `Meshgenesistest._mit_name` die Reihenfolge tauschen → Fall 4 rot.
"""

import json
from pathlib import Path

from django.test import RequestFactory, SimpleTestCase, override_settings

from core.api.meshgenesisname import Meshgenesisnameendpunkte
from core.dienste.meshgenesisname import Meshgenesisname
from core.dienste.meshgenesistest import Meshgenesistest

from ._pruefablage import Pruefablage


class MeshgenesisnameTest(SimpleTestCase):
    def setUp(self):
        Meshgenesisname._ablage.clear()

    def tearDown(self):
        Meshgenesisname._ablage.clear()

    @staticmethod
    def _stamm():
        return [{'id': 'damira0tripo', 'name': 'Damira0Tripo', 'modell': 'Damira0Tripo', 'ordner': 'Damira0Tripo'},
                {'id': 'ursula1', 'name': 'Ursula1', 'modell': 'Ursula1', 'ordner': 'Ursula1'}]

    @staticmethod
    def _name(ordner, inhalt):
        ordner.mkdir(parents=True, exist_ok=True)
        (ordner / 'name.json').write_text(inhalt if isinstance(inhalt, str) else json.dumps(inhalt, ensure_ascii=False), encoding='utf-8')

    def test_1_eigener_name_ueber_den_stammdaten(self):
        with Pruefablage.ordner('m3dainame_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            self._name(Path(o) / 'meshgenesis' / 'Damira0Tripo', {'name': 'Damira Tripo-Paar'})
            jobs = Meshgenesisname.jobs(self._stamm())
        self.assertEqual([(j['id'], j['name'], j['name_vorgabe'], j['ordner'], j['modell']) for j in jobs],
                         [('damira0tripo', 'Damira Tripo-Paar', 'Damira0Tripo', 'Damira0Tripo', 'Damira0Tripo'), ('ursula1', 'Ursula1', 'Ursula1', 'Ursula1', 'Ursula1')])

    def test_1b_kaputte_datei_warnt_und_laesst_den_namen(self):
        with Pruefablage.ordner('m3dainame_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            self._name(Path(o) / 'meshgenesis' / 'Ursula1', '{kaputt')
            with self.assertLogs('core', level='WARNING') as log:
                jobs = Meshgenesisname.jobs(self._stamm())
        self.assertEqual(jobs[1]['name'], 'Ursula1')
        self.assertIn('nicht lesbar', log.output[0])

    def test_2_saeubern_leer_und_zuruecksetzen(self):
        with Pruefablage.ordner('m3dainame_') as o:
            ordner = Path(o) / 'Job'
            ordner.mkdir()
            self.assertEqual(Meshgenesisname.setzen(ordner, '  Neuer\n  Name ', 'Alt'), 'Neuer Name')
            self.assertEqual(Meshgenesisname.lesen(ordner), 'Neuer Name')
            with self.assertRaises(ValueError):
                Meshgenesisname.setzen(ordner, ' \n ', 'Alt')
            self.assertEqual(Meshgenesisname.setzen(ordner, 'Alt', 'Alt'), 'Alt')
            self.assertFalse((ordner / 'name.json').exists())
            self.assertEqual(len(Meshgenesisname.setzen(ordner, 'x' * 500, 'Alt')), Meshgenesisname.LAENGE)

    def test_3_neuer_name_gilt_sofort(self):
        with Pruefablage.ordner('m3dainame_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            ordner = Path(o) / 'meshgenesis' / 'Ursula1'
            ordner.mkdir(parents=True)
            self.assertEqual(Meshgenesisname.jobs(self._stamm())[1]['name'], 'Ursula1')
            Meshgenesisname.setzen(ordner, 'Ursula Grundjob', 'Ursula1')
            self.assertEqual(Meshgenesisname.jobs(self._stamm())[1]['name'], 'Ursula Grundjob')

    def test_4_test_nimmt_eigenen_namen_vor_test_json(self):
        with Pruefablage.ordner('m3dainame_') as o:
            p = Path(o) / 'edgar'
            self._name(p, {'name': 'Edgar im Mantel'})
            self.assertEqual(Meshgenesistest._mit_name(p, {'name': 'Edgar'})['name'], 'Edgar im Mantel')
            (p / 'name.json').unlink()
            self.assertEqual(Meshgenesistest._mit_name(p, {'name': 'Edgar'})['name'], 'Edgar')
            self.assertEqual(Meshgenesistest._mit_name(p, {})['name'], 'edgar')

    def test_5_endpunkt_der_tests(self):
        fabrik = RequestFactory()
        with Pruefablage.ordner('m3dainame_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            p = Path(o) / 'meshgenesis' / '_test' / 'edgar'
            p.mkdir(parents=True)
            (p / 'test.json').write_text(json.dumps({'kennung': 'edgar', 'name': 'Edgar'}), encoding='utf-8')
            post = lambda kennung, name: Meshgenesisnameendpunkte.test(fabrik.post('/', json.dumps({'name': name}), content_type='application/json'), kennung)  # noqa: E731
            antwort = post('edgar', ' Edgar  2 ')
            self.assertEqual((antwort.status_code, json.loads(antwort.content)['name']), (200, 'Edgar 2'))
            self.assertEqual(Meshgenesisname.lesen(p), 'Edgar 2')
            self.assertEqual(post('gibtesnicht', 'X').status_code, 404)
            (p / 'name.json').unlink()
            self.assertEqual(post('edgar', '').status_code, 400)
            self.assertFalse((p / 'name.json').exists())
