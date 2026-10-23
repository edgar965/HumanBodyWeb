# -*- coding: utf-8 -*-
"""Kleider und Bestandteile der Testnetze von Mesh3D-AI (17.10.2026 nachts): welcher Weg je Stück gilt, wie die Wahl in `einstellung.json` landet, wie das Modell aussieht (`Mesh3daitestkleider`,
`Mesh3daitestmodell`). Ohne Datenbank, ohne Garderobe; Dateien nur in einem eigenen Ordner unter ProjektTemp.

Sabotage-Gegenprobe (von Hand): in `Mesh3daitestkleider.wirksam` die Zeile `if eigene == 'aus'` streichen → Fall 2 rot; in `einstellung_aendern` `wert = {}` statt Lesen → Fall 5 rot;
in `freier_name` die Prüfung `_eigenes` streichen → Fall 7 rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.mesh3daitestkleider import Mesh3daitestkleider
from core.dienste.mesh3daitestmodell import Mesh3daitestmodell

from ._pruefablage import Pruefablage

ABLAGE = Path(Pruefablage.wurzel())


class WirksamTest(SimpleTestCase):
    STUECK = {'id': 'hose', 'a': {'kennung': 'g9_base_shorts'}, 'b': {'dreiecke': 10}}

    def test_1_eigene_wahl_vor_vorgabe(self):
        self.assertEqual(Mesh3daitestkleider.wirksam(self.STUECK, 'a', 'b'), 'a')

    def test_2_aus_bleibt_aus(self):
        self.assertEqual(Mesh3daitestkleider.wirksam(self.STUECK, 'aus', 'b'), 'aus')

    def test_3_fehlender_weg_faellt_auf_den_anderen(self):
        st = {'id': 'krone', 'a': {'fehler': 'Kein passendes Katalogstück'}, 'b': {'dreiecke': 5}}
        self.assertEqual(Mesh3daitestkleider.wirksam(st, None, 'a'), 'b')
        self.assertEqual(Mesh3daitestkleider.wirksam(st, 'a', 'a'), 'b')

    def test_4_ohne_beide_wege_aus(self):
        self.assertEqual(Mesh3daitestkleider.wirksam({'id': 'x', 'a': None, 'b': {'fehler': 'x'}}, None, 'b'), 'aus')


class EinstellungTest(SimpleTestCase):
    def setUp(self):
        ABLAGE.mkdir(parents=True, exist_ok=True)
        self.ordner = Path(tempfile.mkdtemp(dir=ABLAGE))

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def test_5_aendern_behaelt_das_geschlecht(self):
        (self.ordner / 'einstellung.json').write_text(json.dumps({'geschlecht': 'maennlich'}), encoding='utf-8')
        Mesh3daitestkleider.einstellung_aendern(self.ordner, kleider_vorgabe='a')
        wert = json.loads((self.ordner / 'einstellung.json').read_text(encoding='utf-8'))
        self.assertEqual(wert, {'geschlecht': 'maennlich', 'kleider_vorgabe': 'a'})
        self.assertEqual(Mesh3daitestkleider.vorgabe(self.ordner), 'a')

    def test_6_vorgabe_ohne_datei(self):
        self.assertEqual(Mesh3daitestkleider.vorgabe(self.ordner), Mesh3daitestkleider.VORGABE)


class ModellTest(SimpleTestCase):
    def setUp(self):
        ABLAGE.mkdir(parents=True, exist_ok=True)
        self.ordner = Path(tempfile.mkdtemp(dir=ABLAGE))

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def test_7_fremdes_modell_wird_nicht_ueberschrieben(self):
        (self.ordner / 'Edgar KI.json').write_text(json.dumps({'figur': {'herkunft': {'art': 'blend import'}}}), encoding='utf-8')
        self.assertEqual(Mesh3daitestmodell.freier_name('Edgar KI', 'edgar', 'maennlich', self.ordner), 'Edgar KI 2')
        eigenes = {'figur': {'herkunft': {'art': Mesh3daitestmodell.HERKUNFT, 'test': 'edgar', 'geschlecht': 'maennlich'}}}
        (self.ordner / 'Edgar KI.json').write_text(json.dumps(eigenes), encoding='utf-8')
        self.assertEqual(Mesh3daitestmodell.freier_name('Edgar KI', 'edgar', 'maennlich', self.ordner), 'Edgar KI')

    def test_8_modelldaten(self):
        form = {'quelle': 'probe', 'figur': {'figur': 'masculine', 'regler': {'Height': 0.2}}}
        with mock.patch('core.dienste.blendimportmodell.Blendimportmodell.griff', return_value=False):
            d = Mesh3daitestmodell.modelldaten('Probe', 'edgar', 'maennlich', form, {'g9_base_shorts': {'farbe': '#7b7b94'}})
        self.assertEqual(d['quelle'], 'genesis9')
        self.assertEqual(d['figur']['regler'], {'Height': 0.2})
        self.assertEqual(d['figur']['kleidung']['g9_base_shorts']['farbe'], '#7b7b94')
        self.assertEqual(d['figur']['herkunft']['test'], 'edgar')

    def test_9_name_ohne_sonderzeichen(self):
        self.assertEqual(Mesh3daitestmodell.name_saeubern('  Edgar/../KI: 1 '), 'EdgarKI 1')

    def test_10_haut_b_wird_fotohaut(self):
        # Sabotage: `modelldaten` ohne den Zweig für `fototextur` → das Modell trüge die Haut der Figur, der Bart fehlte.
        form = {'quelle': 'probe', 'figur': {'figur': 'masculine', 'regler': {}}}
        haut = {'1001': '/api/meshfigur/x/datei/ergebnis/meshfigur_1001.jpg', 'augen': '/api/meshfigur/x/datei/ergebnis/meshfigur_augen.jpg'}
        with mock.patch('core.dienste.blendimportmodell.Blendimportmodell.griff', return_value=False):
            mit = Mesh3daitestmodell.modelldaten('Probe', 'edgar', 'maennlich', form, {}, haut)
            ohne = Mesh3daitestmodell.modelldaten('Probe', 'edgar', 'maennlich', form, {})
        self.assertEqual(mit['figur']['fototextur'], haut)
        self.assertNotIn('fototextur', ohne['figur'])


class ListeTest(SimpleTestCase):
    """Eine Netz-Adresse nur, wo ein Anzeigenetz liegt — „Haut a“ ist die Figur selbst (`mesh3dai_kleider_haut.py`)."""

    def setUp(self):
        ABLAGE.mkdir(parents=True, exist_ok=True)
        self.test = Path(tempfile.mkdtemp(dir=ABLAGE))
        ordner = self.test / 'kleider_maennlich'
        (ordner / 'b' / 'haut' / 'anzeige').mkdir(parents=True)
        (ordner / 'b' / 'haut' / 'anzeige' / 'netz.npz').write_bytes(b'x')
        haut = {'id': 'haut', 'name': 'Haut', 'art': 'haut', 'region': 'haut', 'a': {'kennung': 'masculine'}, 'b': {'kacheln': {'1001': 'meshfigur_1001.jpg'}}}
        (ordner / 'stuecke.json').write_text(json.dumps({'stuecke': [haut]}), encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test, ignore_errors=True)

    def test_11_haut_a_ohne_netz_b_mit(self):
        # Sabotage: die Prüfung auf `anzeige/netz.npz` in `liste` weglassen → „a“ bekommt eine Adresse ins Leere (404 im Browser).
        with mock.patch('core.dienste.mesh3daitest.Mesh3daitest.pfad', return_value=self.test):
            st = Mesh3daitestkleider.liste('probe', 'maennlich')['stuecke'][0]
        self.assertNotIn('netz', st['a'])
        self.assertIn('/kleid/maennlich/b/haut', st['b']['netz'])
        # Seit 20.10.2026 ist die Vorgabe „ki“ (das Ergebnis kommt aus der KI): die Haut zeigt dann die Haut der Figur (a), nicht die gebackene des Mesh-3D-Laufs.
        self.assertEqual(st['wahl'], 'a')

    def test_12_ki_zeilen_aus_ki_json(self):
        # KI-Zeilen kommen aus `ki.json`, bei Vorgabe „ki“ in ihrer Reihenfolge (`ki_vorgabe`); Weg ohne Netz bekommt keine Adresse.
        # Sabotage: in `wirksam` den Zweig `if ki:` unter `vorgabe == 'ki'` weglassen → „aus“ statt „s“.
        ordner = self.test / 'kleider_maennlich'
        for weg in ('k', 's'):
            (ordner / weg / 'ki_oberteil' / 'anzeige').mkdir(parents=True)
            (ordner / weg / 'ki_oberteil' / 'anzeige' / 'netz.npz').write_bytes(b'x')
        zeile = {'id': 'ki_oberteil', 'name': 'Oberteil', 'art': 'oberteil', 'quelle': 'ki', 'ki_vorgabe': ['s', 'k'], 'k': {'punkte': 10}, 's': {'punkte': 12}, 'h': {'fehler': 'x'}}
        (ordner / 'ki.json').write_text(json.dumps({'stuecke': [zeile]}), encoding='utf-8')
        with mock.patch('core.dienste.mesh3daitest.Mesh3daitest.pfad', return_value=self.test):
            liste = Mesh3daitestkleider.liste('probe', 'maennlich')
        ki = next(s for s in liste['stuecke'] if s['id'] == 'ki_oberteil')
        self.assertEqual(ki['wahl'], 's')
        self.assertIn('/kleid/maennlich/s/ki_oberteil', ki['s']['netz'])
        self.assertNotIn('netz', ki['h'])

    def test_13_vorgabe_b_schaltet_ki_aus(self):
        st = {'id': 'ki_hose', 'quelle': 'ki', 'ki_vorgabe': ['k'], 'k': {'punkte': 3}}
        self.assertEqual(Mesh3daitestkleider.wirksam(st, None, 'b'), 'aus')
        self.assertEqual(Mesh3daitestkleider.wirksam(st, 'k', 'b'), 'k')
        self.assertEqual(Mesh3daitestkleider.wirksam({'id': 'hose', 'b': {'punkte': 1}}, None, 'ki'), 'aus')

    def test_14_vorgabe_ki_nimmt_keine_frisur_der_bibliothek(self):
        # Edgar 20.10.2026: Haar nicht aus der Bibliothek. Auch eine alte `ki.json` mit h vorn zeigt k; ohne k bleibt das Haar aus; die eigene Wahl h gilt.
        # Sabotage: in `wirksam` den Filter `AUS_DER_BIBLIOTHEK` weglassen → „h“ statt „k“.
        haar = {'id': 'ki_haar', 'quelle': 'ki', 'art': 'haar', 'ki_vorgabe': ['h', 'k', 's'], 'k': {'punkte': 5}, 'h': {'punkte': 9}}
        self.assertEqual(Mesh3daitestkleider.wirksam(haar, None, 'ki'), 'k')
        self.assertEqual(Mesh3daitestkleider.wirksam(dict(haar, k=None), None, 'ki'), 'aus')
        self.assertEqual(Mesh3daitestkleider.wirksam(haar, 'h', 'ki'), 'h')
