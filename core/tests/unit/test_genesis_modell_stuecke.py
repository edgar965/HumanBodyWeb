# -*- coding: utf-8 -*-
"""Ein gespeichertes Genesis-Modell behält sein GarmentCode-Kleid.

BEFUND (Edgar, 05.10.2026): „Damira1, das Kleid fittet nicht mehr. Hat vor ca. 1 Woche noch
gepasst." Damira1 zeigte auf `kleid_genesis9/kleid_genesis9_sim_rig.json` — den Arbeitsordner, den
JEDER Genesis-9-Kleidbau beschreibt (`GarmentcodeDienst.erzeugen`: Ordner = Vorlage + Figurart). Am
30.09. um 20:35 ersetzte ein Bau für eine 172-cm-Figur Damiras Babydoll (167 cm). Der Schutz dagegen
(`Szenenstuecke.sichern`, seit 10.09.) griff beim Speichern nur für `daten['garmentcode']` — ein
Genesis-Modell führt seine Stücke unter `daten['figur']['garmentcode']`.

Alles unter `ProjektTemp/pruefungen`: `HUMANBODY_MODELS_DIR` und `Entwurf.AUSGABE` werden umgelenkt —
nie `HumanBody/data/models` und nie `Assets/GarmentCode/ausgabe`.
"""

import json
import shutil
import tempfile
from pathlib import Path

from django.test import Client, TestCase, override_settings
from GarmentCode.entwurf import Entwurf
from GarmentCode.szenenstuecke import Szenenstuecke

from ._pruefablage import Pruefablage

ADRESSE = '/api/garmentcode/datei/kleid_genesis9/kleid_genesis9_sim_rig.json/'


class GenesisModellBehaeltSeinKleid(TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='g9stueck_', dir=Pruefablage.wurzel()))
        self.modelle = self.tmp / 'modelle'
        self.modelle.mkdir()
        self.ausgabe = self.tmp / 'ausgabe'
        (self.ausgabe / 'kleid_genesis9').mkdir(parents=True)
        self.geteilt = self.ausgabe / 'kleid_genesis9' / 'kleid_genesis9_sim_rig.json'
        self.geteilt.write_text(json.dumps({'punkte': 'DAMIRA'}), encoding='utf-8')
        self.echte_ausgabe = Entwurf.AUSGABE
        Entwurf.AUSGABE = str(self.ausgabe)
        self.umlenken = override_settings(HUMANBODY_MODELS_DIR=self.modelle)
        self.umlenken.enable()
        self.client = Client(HTTP_HOST='127.0.0.1')

    def tearDown(self):
        self.umlenken.disable()
        Entwurf.AUSGABE = self.echte_ausgabe
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _speichern(self, name, daten):
        antwort = self.client.post('/api/character/model/save/',
                                   json.dumps({'name': name, 'data': daten}),
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        return json.loads((self.modelle / (name + '.json')).read_text(encoding='utf-8'))

    def _genesis_modell(self, name):
        return {'name': name, 'quelle': 'genesis9', 'figur': {
            'quelle': 'genesis9',
            'garmentcode': [{'stueck': 'kleid', 'titel': 'Babydoll', 'rig_url': ADRESSE}],
        }}

    def test_1_der_zeiger_wandert_in_den_szenenordner(self):
        gespeichert = self._speichern('ZZ Damira', self._genesis_modell('ZZ Damira'))
        adresse = gespeichert['figur']['garmentcode'][0]['rig_url']
        self.assertIn(Szenenstuecke.ordnername('ZZ Damira'), adresse)
        self.assertNotEqual(adresse, ADRESSE)

    def test_2_ein_spaeterer_bau_aendert_das_gespeicherte_kleid_nicht(self):
        gespeichert = self._speichern('ZZ Damira', self._genesis_modell('ZZ Damira'))
        adresse = gespeichert['figur']['garmentcode'][0]['rig_url']
        # Der nächste Genesis-Kleidbau — gleich welcher Figur — schreibt dieselbe Datei neu.
        self.geteilt.write_text(json.dumps({'punkte': 'FREMDE_FIGUR'}), encoding='utf-8')
        pfad = Szenenstuecke._quellpfad(adresse)
        self.assertIsNotNone(pfad)
        self.assertEqual(json.loads(Path(str(pfad)).read_text(encoding='utf-8')), {'punkte': 'DAMIRA'})

    def test_3_ein_modell_ohne_stuecke_bleibt_unberuehrt(self):
        daten = {'name': 'ZZ Leer', 'quelle': 'genesis9', 'figur': {'quelle': 'genesis9'}}
        self.assertEqual(self._speichern('ZZ Leer', daten)['figur'], {'quelle': 'genesis9'})
        self.assertFalse((self.ausgabe / Szenenstuecke.ordnername('ZZ Leer')).exists())
