# -*- coding: utf-8 -*-
"""Fotokacheln gespeicherter Genesis-Modelle (`Modelltexturen`) und die Bildspalten der Tabelle
„Mesh to 3D" (Edgar, 27.09.2026: „die Szene soll natürlich mit Textur gezeigt und gespeichert
werden. Speichere die Textur gleich so, dass sie mit dem Genesis Export verfügbar ist" und „eine
Spalte für die Vorlage, eine Spalte für das Mesh, mit einem Bild vom 3D Genesis Figur").

1. Speichern aus dem Auftrag kopiert die Kacheln nach `Texturen/<Modell>/`, die Adresse im Modell
   zeigt dorthin, und sie liefert noch, wenn der Auftrag gelöscht ist.
2. „Modell speichern" der Szene unter NEUEM Namen legt eine eigene Kopie an; unter demselben Namen
   wird nichts kopiert, eine veraltete Kachel fällt weg.
3. Fremde und bösartige Adressen bleiben unangetastet, der Endpunkt liefert nur Bilder im Ordner.
4. Umbenennen nimmt Ordner und Adressen mit, Löschen entfernt die Kacheln.
5. Die Tabelle zeigt Vorlage und Figur mit Stand in der Adresse, ohne Bild den Platzhalter.

Alles unter `ProjektTemp/pruefungen` (`Pruefablage`): `OBJECTS_ROOT` und `HUMANBODY_MODELS_DIR`
werden umgelenkt — nie `HumanBody/data/models`.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock
from urllib.parse import quote

from django.test import Client, TestCase, override_settings

from core.daten.meshfigurablage import Meshfigurablage
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.meshfigurtabelle import Meshfigurtabelle
from core.dienste.modellablage import Modellablage
from core.dienste.modelltexturen import Modelltexturen
from core.models import Meshfigurauftrag

from ._pruefablage import Pruefablage

JPG = b'\xff\xd8\xff\xe0' + b'kachel' * 20


class ModelltexturenTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='modelltextur_', dir=Pruefablage.wurzel()))
        self.modelle = self.tmp / 'modelle'
        self.modelle.mkdir()
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.referenzen = mock.patch.object(Meshfiguroptionen, '_referenzen', return_value=[('', '—')])
        self.referenzen.start()
        self.umlenken = override_settings(OBJECTS_ROOT=self.tmp, HUMANBODY_MODELS_DIR=self.modelle)
        self.umlenken.enable()

    def tearDown(self):
        self.umlenken.disable()
        self.referenzen.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _auftrag(self, kennung='2026.09.27.00.00.02', **ergebnis):
        job = Meshfigurauftrag.objects.create(
            kennung=kennung, name='ZZ', eingang={}, optionen={}, status='fertig',
            ergebnis=dict({'regler': {'stellung': {'body_bs_BodyMass': 0.3}},
                           'fototextur': {'kacheln': {'1001': 'meshfigur_1001.jpg'}}}, **ergebnis),
        )
        ablage = Meshfigurablage(kennung)
        ablage.anlegen()
        ablage.ergebnis('meshfigur_1001.jpg').write_bytes(JPG)
        return job, ablage

    def _modell(self, name):
        return json.loads((self.modelle / (name + '.json')).read_text(encoding='utf-8'))

    def _speichern(self, job, name):
        return self.client.post('/api/meshfigur/%s/modell/' % job.id, json.dumps({'name': name}),
                                content_type='application/json')

    def test_1_auftrag_speichert_kacheln_neben_das_modell(self):
        job, ablage = self._auftrag()
        self.assertEqual(self._speichern(job, 'ZZ Tex').status_code, 200)
        adresse = self._modell('ZZ Tex')['figur']['fototextur']['1001']
        vorn = Modelltexturen.ADRESSE + quote('ZZ Tex') + '/meshfigur_1001.jpg/?v='
        self.assertTrue(adresse.startswith(vorn), adresse)
        self.assertEqual((self.modelle / 'Texturen' / 'ZZ Tex' / 'meshfigur_1001.jpg').read_bytes(), JPG)
        ablage.loeschen()
        antwort = self.client.get(adresse)
        self.assertEqual((antwort.status_code, antwort['Content-Type']), (200, 'image/jpeg'),
                         'die Kachel überlebt das Löschen des Auftrags')
        self.assertEqual(b''.join(antwort.streaming_content), JPG)
        antwort.close()  # Windows: eine offene Datei lässt sich nicht löschen

    def test_2_szene_speichert_unter_neuem_namen_eine_eigene_kopie(self):
        job, _ = self._auftrag()
        self._speichern(job, 'ZZ Tex')
        figur = self._modell('ZZ Tex')['figur']
        rumpf = {'name': 'ZZ Kopie', 'data': {'name': 'ZZ Kopie', 'quelle': 'genesis9', 'figur': figur}}
        self.assertEqual(self.client.post('/api/character/model/save/', json.dumps(rumpf),
                                          content_type='application/json').status_code, 200)
        kopie = self._modell('ZZ Kopie')['figur']['fototextur']['1001']
        self.assertIn('/ZZ%20Kopie/meshfigur_1001.jpg/', kopie)
        self.assertTrue((self.modelle / 'Texturen' / 'ZZ Kopie' / 'meshfigur_1001.jpg').is_file())
        # Unter demselben Namen: nichts kopiert, eine Kachel eines früheren Stands fällt weg.
        alt = self.modelle / 'Texturen' / 'ZZ Tex' / 'meshfigur_1009.jpg'
        alt.write_bytes(JPG)
        gleich = Modelltexturen.sichern('ZZ Tex', figur)
        self.assertEqual(gleich['fototextur'], figur['fototextur'])
        self.assertFalse(alt.exists(), 'veraltete Kachel entfernt')

    def test_3_fremde_und_boese_adressen_bleiben_stehen(self):
        figur = {'fototextur': {
            '1001': 'https://example.org/haut.jpg',
            '1002': '/api/meshfigur/00000000-0000-0000-0000-000000000000/datei/ergebnis/a.jpg',
            '1003': Modelltexturen.ADRESSE + '..%5C..%5Cx/a.jpg/',
            '1004': '/api/meshfigur/00000000-0000-0000-0000-000000000000/datei/arbeit/a.npz',
        }}
        self.assertEqual(Modelltexturen.sichern('ZZ', figur), figur)
        self.assertFalse((self.modelle / 'Texturen').exists(), 'nichts angelegt')
        self.assertIsNone(Modelltexturen.datei('..', 'a.jpg'))
        self.assertIsNone(Modelltexturen.datei('ZZ', 'a.json'), 'nur Bilder')
        self.assertIsNone(Modelltexturen.datei('ZZ', '..\\a.jpg'))
        self.assertEqual(self.client.get(Modelltexturen.ADRESSE + 'ZZ/fehlt.jpg/').status_code, 404)

    def test_4_umbenennen_und_loeschen_nehmen_die_kacheln_mit(self):
        job, _ = self._auftrag()
        self._speichern(job, 'ZZ Tex')
        Modellablage.umbenennen('ZZ Tex', 'ZZ Neu')
        adresse = self._modell('ZZ Neu')['figur']['fototextur']['1001']
        self.assertIn('/ZZ%20Neu/meshfigur_1001.jpg/', adresse)
        self.assertFalse((self.modelle / 'Texturen' / 'ZZ Tex').exists())
        antwort = self.client.get(adresse)
        self.assertEqual(antwort.status_code, 200)
        antwort.close()  # Windows: eine offene Datei lässt sich nicht löschen
        Modellablage.loeschen('ZZ Neu')
        self.assertFalse((self.modelle / 'Texturen' / 'ZZ Neu').exists())
        self.assertFalse((self.modelle / 'ZZ Neu.json').exists())

    def test_5_tabelle_zeigt_vorlage_und_figur(self):
        mit, _ = self._auftrag(vorlage='vorlage.png', vorschau={'dateien': {'icon': 'icon.png'}})
        ohne, _ = self._auftrag(kennung='2026.09.27.00.00.03')
        tabelle = Meshfigurtabelle(Meshfigurauftrag.objects.all())
        self.assertEqual([s['label'] for s in tabelle.SPALTEN[1:3]], ['Vorlage', 'Figur'])
        html = tabelle.zeile(mit)['html']
        self.assertIn('/ergebnis/vorlage.png?v=', html)
        self.assertIn('/ergebnis/icon.png?v=', html)
        leer = tabelle.zeile(ohne)['html']
        self.assertIn('noch kein Bild des Netzes', leer)
        self.assertIn('noch keine Vorschau', leer)
