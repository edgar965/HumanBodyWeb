# -*- coding: utf-8 -*-
"""Blender-Import löschen, abbrechen, verwaiste finden (Edgar, 10.10.2026).

Anlass: Der Rosemary-Import (Körper ohne Beine, Figur passte nicht) rechnete 22 Minuten ohne Meldung, und es gab keinen Weg, ihn samt
Ordner, Auftrag „Mesh to 3D" und Garderobenstücken zu entfernen. „Mach einen Button zum Löschen eines Imports oder verwaisten Imports" und
„der Abbrechen löscht auch alle Importdaten".

1. Verwaist: ein Ordner ohne Stand, ein „läuft" ohne lebenden Arbeitsprozess, ein gescheiterter oder angehaltener Lauf, ein fertiger ohne
   Modell — nie ein Import, dessen Prozess lebt, und nie einer, dessen Modell noch da ist.
2. Gefunden beim Test der Oberfläche: der Lauf 09.54.27 „Fallout ranger" war verwaist (sein Modell gehört dem späteren Lauf 11.42.36), beide
   nennen aber dieselben Stücke `fallout_ranger_*` — das Löschen des alten ließe dem Modell die Kleidung nehmen. `benutzer` hält sie fest.
3. Löschen: Ordner weg; rechnet der Import, kommt ohne `anhalten` ein `ImportLaeuft` (409) und es bleibt alles stehen.
4. Die Endpunkte antworten 404 für einen Import, den es nicht gibt, und 409 für einen laufenden.

5. „cute girl" (Edgar, 10.10.2026: „warum wird nicht alles gelöscht? Mach eindeutige Meldung für den Grund, möglichst aber alles weg"): ein Stück, das ein
   Modell oder ein späterer Import braucht, bleibt MIT Name und Grund (`grund_behalten`); nur mit `stuecke_trotzdem` geht es auch in den Papierkorb.
   Die Sammellöschung der Verwaisten meldet, was geblieben ist.

Sabotage-Gegenprobe: in `benutzer` die Schleife über die anderen Importe streichen → `BenutzerTest.test_2` rot; in `loeschen` den Zweig
`if self.laeuft()` streichen → `LoeschenTest.test_2` rot; in `grund_verwaist` die Prüfung `self.laeuft()` streichen → `VerwaistTest.test_1` rot;
in `_stuecke_entfernen` `and not trotzdem` streichen → `LoeschenTest.test_5` rot (das gebrauchte Stück ginge ungefragt weg), `not` davor setzen →
`test_6` rot; in `grund_behalten` den Zweig `Import ` streichen → `BenutzerTest.test_3` rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

import json
from unittest import mock

from django.test import Client, SimpleTestCase, override_settings

from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportloeschen import Blendimportloeschen, ImportLaeuft

from ._pruefablage import Pruefablage


def _anlegen(kennung, status, **zusatz):
    ablage = Blendimportablage(kennung)
    ablage.anlegen()
    (ablage.arbeit() / 'x.bin').write_bytes(b'0' * 1024)
    ablage.stand_schreiben({'kennung': kennung, 'status': status, 'quelle': {'name': 'Figur'}, 'ergebnis': {}, **zusatz})
    return ablage


class VerwaistTest(SimpleTestCase):
    databases = set()

    def _grund(self, stand, laeuft=False, modelle=(), gelesen=()):
        dienst = object.__new__(Blendimportloeschen)
        with mock.patch.object(Blendimportloeschen, 'stand', return_value=stand), \
                mock.patch.object(Blendimportloeschen, 'laeuft', return_value=laeuft):
            return dienst.grund_verwaist(list(modelle), list(gelesen))

    def test_1_ein_laufender_import_ist_nie_verwaist(self):
        self.assertIsNone(self._grund({'status': 'laeuft'}, laeuft=True))

    def test_2_ohne_stand_ohne_prozess_gescheitert_angehalten(self):
        self.assertIn('ohne Stand', self._grund({}))
        self.assertIn('Arbeitsprozess ist weg', self._grund({'status': 'laeuft'}))
        self.assertIn('Gescheitert: Boom', self._grund({'status': 'gescheitert', 'fehler': 'Boom'}))
        self.assertEqual(self._grund({'status': 'angehalten'}), 'Angehalten')

    def test_3_fertig_mit_modell_ist_keine_waise_ohne_modell_schon(self):
        self.assertIsNone(self._grund({'status': 'fertig'}, modelle=['Asian']))
        stand = {'status': 'fertig', 'ergebnis': {'modell': {'name': 'Asian'}}}
        self.assertIn('gibt es nicht mehr', self._grund(stand))
        spaeter = [{'name': 'Asian', 'import': '2026.10.09.99.99.99', 'kleidung': set()}]
        self.assertIn('stammt jetzt aus dem Import 2026.10.09.99.99.99', self._grund(stand, gelesen=spaeter))


class BenutzerTest(SimpleTestCase):
    """Stücke, die ein Modell oder ein anderer Import noch braucht, bleiben beim Löschen stehen."""
    databases = set()

    def test_1_ein_modell_mit_dem_stueck_haelt_es_fest_ausser_es_wird_mitgeloescht(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            dienst = Blendimportloeschen(_anlegen('2026.10.01.00.00.01', 'fertig').kennung)
            gelesen = [{'name': 'M', 'import': dienst.kennung, 'kleidung': {'x_hemd'}},
                       {'name': 'Fremd', 'import': 'anderer', 'kleidung': {'x_hose'}}]
            self.assertEqual(dienst.benutzer('x_hemd', gelesen, mit_modell=False), ['Modell „M"'])
            self.assertEqual(dienst.benutzer('x_hemd', gelesen, mit_modell=True), [], 'das eigene Modell geht mit')
            self.assertEqual(dienst.benutzer('x_hose', gelesen, mit_modell=True), ['Modell „Fremd"'])

    def test_2_ein_anderer_import_mit_demselben_stueck_haelt_es_fest(self):
        """Fallout ranger: der alte, verwaiste Lauf und der spätere nennen dieselben `fallout_ranger_*`."""
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            alt = Blendimportloeschen(_anlegen('2026.10.01.00.00.01', 'fertig').kennung)
            _anlegen('2026.10.01.00.00.02', 'fertig', ergebnis={'stuecke': {'stuecke': {'hemd': 'f_hemd'}}})
            self.assertEqual(alt.benutzer('f_hemd', [], True), ['Import 2026.10.01.00.00.02'])
            self.assertEqual(alt.benutzer('anderes', [], True), [])

    def test_3_der_grund_nennt_modell_und_import(self):
        """„cute girl" (10.10.2026): der spätere Import 19.31.50 hat Haar, Shirt und Shorts unter derselben Kennung neu geschrieben, das Modell trägt sie."""
        text = Blendimportloeschen.grund_behalten(['Modell „cute girl"', 'Import 2026.10.08.19.31.50'])
        self.assertTrue(text.startswith('Das Modell „cute girl" trägt sie als Kleidung'), text)
        self.assertIn('der Import 2026.10.08.19.31.50 hat sie unter derselben Kennung neu geschrieben', text)


class LoeschenTest(SimpleTestCase):
    databases = set()

    def test_1_ein_gescheiterter_import_verschwindet_mit_dem_ordner(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            ablage = _anlegen('2026.10.01.00.00.03', 'gescheitert', fehler='Boom')
            with mock.patch.object(Blendimportloeschen, 'modelle_lesen', return_value=[]), \
                    mock.patch.object(Blendimportloeschen, 'stuecke', return_value=[]):
                ergebnis = Blendimportloeschen(ablage.kennung).loeschen()
            self.assertFalse(ablage.ordner().exists())
            self.assertEqual(ergebnis['kennung'], ablage.kennung)

    def test_2_ein_laufender_import_wird_ohne_anhalten_nicht_geloescht(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            ablage = _anlegen('2026.10.01.00.00.04', 'laeuft', schritt='haut')
            with mock.patch.object(Blendimportloeschen, 'laeuft', return_value=True):
                with self.assertRaises(ImportLaeuft):
                    Blendimportloeschen(ablage.kennung).loeschen()
            self.assertTrue(ablage.ordner().is_dir(), 'nichts angefasst')

    def test_3_nur_die_genannten_verwaisten_gehen(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            a = _anlegen('2026.10.01.00.00.05', 'gescheitert')
            b = _anlegen('2026.10.01.00.00.06', 'gescheitert')
            with mock.patch.object(Blendimportloeschen, 'modelle_lesen', return_value=[]), \
                    mock.patch.object(Blendimportloeschen, 'stuecke', return_value=[]):
                ergebnis = Blendimportloeschen.verwaiste_loeschen({a.kennung})
            self.assertEqual(ergebnis['geloescht'], [a.kennung])
            self.assertFalse(a.ordner().exists())
            self.assertTrue(b.ordner().is_dir())

    def test_4_der_ordner_muss_direkt_unter_der_wurzel_liegen(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            dienst = Blendimportloeschen(_anlegen('2026.10.01.00.00.07', 'gescheitert').kennung)
            self.assertEqual(dienst._sicherer_ordner(), dienst.ablage.ordner())

    @staticmethod
    def _stuecke_entfernen(trotzdem):
        """Ein Stück, das ein Modell braucht, und ein freies — `_stuecke_entfernen` mit und ohne `trotzdem`. → (weg, behalten, Papierkorb-Aufrufe)."""
        stuecke = [{'kennung': 'x_hemd', 'name': 'X Hemd', 'eintrag': {'id': 'x_hemd'}, 'benutzer': ['Modell „M"']},
                   {'kennung': 'x_frei', 'name': 'X Frei', 'eintrag': {'id': 'x_frei'}, 'benutzer': []}]
        dienst = object.__new__(Blendimportloeschen)
        dienst.kennung = '2026.10.01.00.00.09'
        with mock.patch.object(Blendimportloeschen, 'stuecke', return_value=stuecke), \
                mock.patch('Genesis9.garderobepflege.G9garderobepflege.loeschen') as papierkorb:
            weg, behalten = dienst._stuecke_entfernen(True, trotzdem)
        return weg, behalten, [aufruf.args[0]['id'] for aufruf in papierkorb.call_args_list]

    def test_5_ein_gebrauchtes_stueck_bleibt_mit_name_und_grund(self):
        weg, behalten, papierkorb = self._stuecke_entfernen(False)
        self.assertEqual(weg, ['x_frei'])
        self.assertEqual(papierkorb, ['x_frei'], 'nur das freie Stück geht in den Papierkorb')
        self.assertEqual([b['kennung'] for b in behalten], ['x_hemd'])
        self.assertEqual(behalten[0]['name'], 'X Hemd')
        self.assertIn('Modell „M" trägt sie', behalten[0]['grund'])

    def test_6_auf_wunsch_geht_auch_das_gebrauchte_stueck_in_den_papierkorb(self):
        """Edgar, 10.10.2026: „möglichst alles weg" — nur mit ausdrücklicher Zusage (`stuecke_trotzdem`)."""
        weg, behalten, papierkorb = self._stuecke_entfernen(True)
        self.assertEqual(weg, ['x_hemd', 'x_frei'])
        self.assertEqual(papierkorb, ['x_hemd', 'x_frei'])
        self.assertEqual(behalten, [])

    def test_7_die_verwaisten_melden_was_geblieben_ist(self):
        with mock.patch.object(Blendimportloeschen, 'verwaiste', return_value=[{'kennung': 'a'}, {'kennung': 'b'}]), \
                mock.patch.object(Blendimportloeschen, '__init__', return_value=None), \
                mock.patch.object(Blendimportloeschen, 'loeschen', autospec=True,
                                  side_effect=[{'behalten': [{'kennung': 'k', 'name': 'K', 'benutzer': [], 'grund': 'G'}]}, {'behalten': []}]):
            ergebnis = Blendimportloeschen.verwaiste_loeschen()
        self.assertEqual(ergebnis['geloescht'], ['a', 'b'])
        self.assertEqual(list(ergebnis['behalten']), ['a'], 'nur der Import mit bleibenden Stücken steht drin')
        self.assertEqual(ergebnis['behalten']['a'][0]['grund'], 'G')


class EndpunkteTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')

    def test_1_unbekannter_import_404_laufender_409(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(self.client.get('/api/character/blendimport/2026.10.01.00.00.99/loeschplan/').status_code, 404)
            self.assertEqual(self.client.post('/api/character/blendimport/2026.10.01.00.00.99/loeschen/', '{}',
                                              content_type='application/json').status_code, 404)
            ablage = _anlegen('2026.10.01.00.00.08', 'laeuft')
            with mock.patch.object(Blendimportloeschen, 'laeuft', return_value=True):
                antwort = self.client.post('/api/character/blendimport/%s/loeschen/' % ablage.kennung, '{}', content_type='application/json')
            self.assertEqual(antwort.status_code, 409)
            self.assertIn('rechnet noch', json.loads(antwort.content)['error'])

    def test_2_stuecke_trotzdem_geht_nur_auf_ausdrueckliches_true_durch(self):
        with Pruefablage.ordner() as wurzel, override_settings(OBJECTS_ROOT=wurzel):
            ablage = _anlegen('2026.10.01.00.00.10', 'gescheitert')
            adresse = '/api/character/blendimport/%s/loeschen/' % ablage.kennung
            with mock.patch.object(Blendimportloeschen, 'loeschen', autospec=True,
                                   return_value={'kennung': ablage.kennung, 'behalten': []}) as dienst:
                self.client.post(adresse, '{}', content_type='application/json')
                self.assertIs(dienst.call_args.kwargs['stuecke_trotzdem'], False)
                self.client.post(adresse, '{"stuecke_trotzdem": "ja"}', content_type='application/json')
                self.assertIs(dienst.call_args.kwargs['stuecke_trotzdem'], False, 'nur ein echtes true zählt')
                self.client.post(adresse, '{"stuecke_trotzdem": true}', content_type='application/json')
                self.assertIs(dienst.call_args.kwargs['stuecke_trotzdem'], True)
