# -*- coding: utf-8 -*-
u"""Eigene Haut (18.10.2026): Rezept speichern, als Hautsatz anbieten, Bilder des Grundsatzes — und die Gebietskarte Fassung 2 (Wangenröte, Augenringe). Kunstdaten, Wegwerfordner,
keine Daz-Bibliothek. Geschrieben, nicht gelaufen.

Edgar, 18.10.2026: „Auch Button zum speichern der Neuen Haut, mit hautnamen, die soll dann auch in die Haut Combo box erscheinen".

1. Schlüssel: Umlaute umschrieben, Sonderzeichen zu `_`, nur ASCII; ein Name ohne Buchstaben oder Ziffern ist ein Fehler, ein leerer Name auch.
2. Speichern legt `<schluessel>.json` an; der Eintrag heißt „Eigene Haut · Name", Kennung `eigen:<schluessel>`, mit Rezept; ein zweites Speichern unter demselben Schlüssel
   überschreibt und meldet es.
3. Werte werden bereinigt: keine Texte, keine Wahrheitswerte, keine unendlichen Zahlen; Hautebenen gerundet, Texturmischung ohne 0 %.
4. Keine Kette: Speichern auf einer eigenen Haut nimmt deren Grundsatz; ohne Grundsatz wird nicht gespeichert.
5. Als Anbieter: eingetragen in `G9hautpresets.ANBIETER`; `bilder('eigen:…')` sind die Bilder des Grundsatzes; `praesets()` führt den Eintrag; fremde Kennungen gehören nicht dazu;
   eine unbekannte oder kaputte Datei ergibt kein Rezept.
6. Endpunkt: POST speichert, ein leerer Grundsatz nimmt die Haut des Katalogeintrags der Figur; ein ungültiger Name → 400 mit Meldung; GET → 405; Adresse im Router.
7. Gebietskarte Fassung 2: am Wangen-Landmark Röte 1, 20 cm daneben 0, am Rumpf nie; unter dem unteren Lid Augenringe über 0,5, über dem Auge fast 0.

Sabotage-Gegenprobe (nicht gefahren): `grund` in `speichern` nicht über `cls.grund` auflösen → Fall 4 rot; `gehoert` immer wahr → Fall 5 rot; in `gesichtsfelder` den Kopf nicht
ausnehmen → Fall 7 rot.
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from core.projekt_temp import ProjektTemp

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.hautpresets import G9hautpresets  # noqa: E402
from Genesis9.koerperteile import G9koerperteile  # noqa: E402

from core.api.g9eigenehautapi import G9eigenehautapi  # noqa: E402
from core.dienste.g9eigenehaut import G9eigenehaut  # noqa: E402
from core.dienste.g9hautebenen import G9hautebenen  # noqa: E402

GRUND = 'G9 Feminine Skin 01 MAT'


class Ablage:
    """Ein Wegwerfordner als Ablage der eigenen Häute."""

    def __init__(self):
        self._ordner = ProjektTemp.wegwerfordner(prefix='g9eigenehaut_')

    def __enter__(self):
        self.pfad = Path(self._ordner.__enter__())
        self._patch = mock.patch.object(G9eigenehaut, 'ordner', staticmethod(lambda: self.pfad))
        self._patch.start()
        return self.pfad

    def __exit__(self, *fehler):
        self._patch.stop()
        return self._ordner.__exit__(*fehler)


class EigeneHautTest(SimpleTestCase):
    databases = set()

    def test_1_schluessel_und_name(self):
        self.assertEqual(G9eigenehaut.schluessel('Sommerhaut Ä-ß 2'), 'sommerhaut_ae_ss_2')
        self.assertEqual(G9eigenehaut.schluessel('  Über/..\\böse  '), 'ueber_boese')
        with self.assertRaises(ValueError):
            G9eigenehaut.schluessel('!!! ---')
        with self.assertRaises(ValueError):
            G9eigenehaut.name('   ')
        self.assertEqual(len(G9eigenehaut.name('x' * 200)), G9eigenehaut.NAME_MAX)

    def test_2_speichern_und_ueberschreiben(self):
        with Ablage() as ordner:
            eintrag, ueberschrieben = G9eigenehaut.speichern('Sommerhaut', GRUND, {'sommer': 60.4}, {'glanz': 0.3}, {'G9 Feminine Skin 02 MAT': 40})
            self.assertFalse(ueberschrieben)
            self.assertTrue((ordner / 'sommerhaut.json').is_file())
            self.assertEqual(eintrag['id'], 'eigen:sommerhaut')
            self.assertEqual(eintrag['name'], 'Eigene Haut · Sommerhaut')
            self.assertEqual(eintrag['rezept']['grund'], GRUND)
            self.assertEqual(eintrag['rezept']['hautebenen'], {'sommer': 60})
            _eintrag, ueberschrieben = G9eigenehaut.speichern('sommerhaut', GRUND, {'sommer': 10})
            self.assertTrue(ueberschrieben, 'gleicher Schlüssel')
            self.assertEqual(G9eigenehaut.rezept('eigen:sommerhaut')['hautebenen'], {'sommer': 10})

    def test_3_werte_bereinigt(self):
        with Ablage():
            eintrag, _u = G9eigenehaut.speichern('Bereinigt', GRUND, {'a': 'text', 'b': True, 'c': float('inf'), 'd': 5000, 'e': -12.6},
                                                 {'glanz': 99}, {'x': 0, 'y': 30})
            rezept = eintrag['rezept']
            self.assertEqual(rezept['hautebenen'], {'d': 1000, 'e': -13})
            self.assertEqual(rezept['teilmaterial'], {'glanz': 10.0})
            self.assertEqual(rezept['hautmischung'], {'y': 30.0})

    def test_4_keine_kette_und_kein_grund(self):
        with Ablage():
            G9eigenehaut.speichern('Erste', GRUND)
            eintrag, _u = G9eigenehaut.speichern('Zweite', 'eigen:erste')
            self.assertEqual(eintrag['rezept']['grund'], GRUND)
            with self.assertRaises(ValueError):
                G9eigenehaut.speichern('Ohne', '')
            with self.assertRaises(ValueError):
                G9eigenehaut.speichern('Unbekannt', 'eigen:gibtsnicht')

    def test_5_anbieter(self):
        self.assertIn(G9eigenehaut, G9hautpresets.ANBIETER)
        self.assertTrue(G9eigenehaut.gehoert('eigen:x'))
        self.assertFalse(G9eigenehaut.gehoert('bedlam:skin_f_x_1_ALB'))
        self.assertFalse(G9eigenehaut.gehoert(GRUND))
        with Ablage() as ordner:
            G9eigenehaut.speichern('Probe', GRUND)
            bilder = {'Head': {'albedo': 'a.jpg'}}
            with mock.patch.object(G9hautpresets, 'haut', side_effect=lambda p: bilder if p == GRUND else {}) as haut:
                self.assertEqual(G9eigenehaut.bilder('eigen:probe'), bilder)
                haut.assert_called_with(GRUND)
            self.assertEqual([e['id'] for e in G9eigenehaut.praesets()], ['eigen:probe'])
            (ordner / 'kaputt.json').write_text('{kein json', encoding='utf-8')
            self.assertIsNone(G9eigenehaut.rezept('eigen:kaputt'))
            self.assertIsNone(G9eigenehaut.rezept('eigen:../probe'), 'Pfadzeichen')
            self.assertEqual(G9eigenehaut.bilder('eigen:gibtsnicht'), {}, 'leer: der Server nimmt die Haut der Figur')

    def test_6_endpunkt(self):
        self.assertEqual(reverse('g9_figur_eigenehaut'), '/api/character/genesis9-figur/eigenehaut/')
        fabrik = RequestFactory()
        adresse = '/api/character/genesis9-figur/eigenehaut/'
        with Ablage(), mock.patch.object(G9eigenehautapi, '_katalogHaut', staticmethod(lambda figur: GRUND)):
            antwort = G9eigenehautapi.speichern(fabrik.post(adresse, json.dumps({'name': 'Über', 'grund': '', 'figur': 'basis', 'hautebenen': {'wangen': 40}}),
                                                            content_type='application/json'))
            self.assertEqual(antwort.status_code, 200)
            daten = json.loads(antwort.content)
            self.assertEqual(daten['eintrag']['id'], 'eigen:ueber')
            self.assertEqual(daten['eintrag']['rezept']['grund'], GRUND, 'leerer Grundsatz: Haut des Katalogeintrags')
            antwort = G9eigenehautapi.speichern(fabrik.post(adresse, json.dumps({'name': '', 'grund': GRUND}), content_type='application/json'))
            self.assertEqual(antwort.status_code, 400)
            self.assertIn('Namen', json.loads(antwort.content)['fehler'])
            self.assertEqual(G9eigenehautapi.speichern(fabrik.get(adresse)).status_code, 405)


class GesichtsfelderTest(SimpleTestCase):
    """Fassung 2 der Gebietskarte: Kanäle B (Röte) und A (Augenringe), nur am Kopf."""
    databases = set()

    KOPF = G9koerperteile.NUMMER['kopf']
    RUMPF = G9koerperteile.NUMMER['rumpf']
    #: ein Auge: Oberlid 1,605 m, Unterlid 1,595 m, Breite 3 cm, z = 0,09
    AUGE = np.array([[x, y, 0.09] for x in (0.02, 0.03, 0.04, 0.05) for y in (1.595, 1.605)])
    GESICHT = {'wange': np.array([[0.04, 1.55, 0.09]]), 'auge_r': AUGE}

    def felder(self, pos, teil):
        return G9hautebenen('female').gesichtsfelder(np.array([pos], dtype=float), np.array([teil]), self.GESICHT)

    def test_7_roete_und_augenringe(self):
        self.assertEqual(G9hautebenen.FASSUNG, 2)
        roete, _r = self.felder((0.04, 1.55, 0.09), self.KOPF)
        self.assertAlmostEqual(float(roete[0]), 1.0, places=6)
        roete, _r = self.felder((0.24, 1.55, 0.09), self.KOPF)
        self.assertLess(float(roete[0]), 1e-6, '20 cm daneben')
        roete, ringe = self.felder((0.04, 1.55, 0.09), self.RUMPF)
        self.assertEqual((float(roete[0]), float(ringe[0])), (0.0, 0.0), 'nie am Rumpf')
        unter = 1.595 - G9hautebenen.RING_VERSATZ
        _r, ringe = self.felder((0.035, unter, 0.09), self.KOPF)
        self.assertGreater(float(ringe[0]), 0.5, 'unter dem Unterlid')
        _r, ringe = self.felder((0.035, 1.625, 0.09), self.KOPF)
        self.assertLess(float(ringe[0]), 0.01, 'über dem Auge')
        self.assertIsNone(G9hautebenen.lidbogen({}), 'ohne Landmarken kein Bogen')
