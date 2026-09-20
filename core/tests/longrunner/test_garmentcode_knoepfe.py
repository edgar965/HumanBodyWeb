# -*- coding: utf-8 -*-
"""Jeder Knopf des GarmentCode-Reiters — sein Serverweg auf einer Genesis-9-Figur.

Edgar, 20.09.2026: „von einem Bug zum anderen! … mach testcases für alle
Buttons des Garment Code und genesis, führe sie aus, checke die ergebnisse
und fixe die Fehler!"

Was jeder Knopf am Server auslöst (`garmentcode_ablauf.js`,
`garmentcode_schritte.js`), hier mit Kins Reglern (Fixture
`test/gemeinsam_kin/figur_regler.json`) als Figur:

    Reiter öffnen        GET  zustand, regler?vorlage=…, vorbilder?vorlage=…,
                              simulationsregler, absatz?stueck=…
    Vorschau 2D          POST erzeugen, dann POST schnittnetz
    Vorschau 3D          POST erzeugen, dann POST vorschau3d
    Bauen 2D             POST erzeugen (Panels wie Vorschau 2D)
    Bauen 3D / beides    POST drapieren        -> longrunner/test_garmentcode_drapieren.py
    Gemeinsam anziehen   POST gemeinsam        -> unit/test_genesis9gemeinsam.py (Attrappen),
                                                 longrunner/test_gemeinsam_genesis9_hose.py
    Vorbild-Knopf        Werte des Vorbilds -> erzeugen (Höschen-Fall vom 21:26)
    Form-Kästchen        Werte der Form    -> erzeugen (BH, Höschen, Body)
    Antwort verloren     GET  antwort/<kennung>/ (`garmentantwort.py`)

Ein Schnitt braucht 1 bis 6 s (Log 20.09.2026); das Modul erzeugt sechs.
Die Drapierung (25 bis 65 s) gehört nicht hierher.
"""

import json
import os

from django.conf import settings
from django.test import Client, SimpleTestCase

FIXTURE = settings.ASSETS_ROOT / 'GarmentCode' / 'test' / 'gemeinsam_kin'


class GarmentcodeKnoepfeTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.regler_figur = json.load(open(FIXTURE / 'figur_regler.json', encoding='utf-8'))['regler']
        cls.klient = Client()
        cls.zustand = cls.klient.get('/api/garmentcode/zustand/').json()

    # ------------------------------------------------------------ Figur

    def figur(self, **mehr):
        """Was `GarmentcodeFigur.formulardaten` für Genesis 9 schickt."""
        daten = {'figurart': 'genesis9', 'geschlecht': 'female', 'morphs': '{}',
                 'regler_figur': json.dumps(self.regler_figur)}
        daten.update(mehr)
        return daten

    def erzeugen(self, vorlage, regler):
        antwort = self.klient.post('/api/garmentcode/erzeugen/',
                                   self.figur(vorlage=vorlage, regler=json.dumps(regler)))
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        ergebnis = antwort.json()
        self.assertNotIn('fehler', ergebnis, ergebnis)
        self.assertTrue(os.path.isfile(ergebnis['spezifikation']), ergebnis)
        return ergebnis

    # ---------------------------------------------------- Reiter öffnen

    def test_zustand_kennt_vorlagen_und_die_drapierung(self):
        self.assertTrue(self.zustand.get('vorhanden'), self.zustand)
        self.assertTrue(self.zustand.get('drapierbereit'), self.zustand)
        namen = [e['name'] for e in self.zustand['entwuerfe']]
        for erwartet in ('hose', 'oberteil', 'unterwaesche', 'rock', 'kleid'):
            self.assertIn(erwartet, namen)

    def test_jede_vorlage_hat_regler_presets_und_vorbilder(self):
        for eintrag in self.zustand['entwuerfe']:
            vorlage = eintrag['name']
            regler = self.klient.get('/api/garmentcode/regler/', {'vorlage': vorlage})
            self.assertEqual(regler.status_code, 200, vorlage)
            daten = regler.json()
            self.assertTrue(daten['gruppen'], vorlage)
            self.assertIn('presets', daten, vorlage)
            vorbilder = self.klient.get('/api/garmentcode/vorbilder/', {'vorlage': vorlage})
            self.assertEqual(vorbilder.status_code, 200, vorlage)
            self.assertIn('vorbilder', vorbilder.json(), vorlage)

    def test_vorbilder_der_unterwaesche_bringen_die_bausteine_mit(self):
        """Das Höschen-Vorbild (21:26) baute einen BH — der Server liefert die
        Bausteine, der Browser darf sie nicht mehr wegwerfen."""
        liste = self.klient.get('/api/garmentcode/vorbilder/', {'vorlage': 'unterwaesche'}).json()['vorbilder']
        self.assertGreaterEqual(len(liste), 20)
        for vorbild in liste:
            self.assertIn('meta.bottom', vorbild['werte'], vorbild['titel'])
            self.assertIn('meta.upper', vorbild['werte'], vorbild['titel'])
            self.assertTrue(vorbild.get('bild') or vorbild.get('bildadresse'), vorbild['titel'])

    def test_simulationsregler_und_absatz(self):
        sim = self.klient.get('/api/garmentcode/simulationsregler/')
        self.assertEqual(sim.status_code, 200)
        self.assertGreaterEqual(len(sim.json().get('regler') or sim.json().get('gruppen') or []), 1, sim.json())
        absatz = self.klient.get('/api/garmentcode/absatz/', {'stueck': 'hose'})
        self.assertEqual(absatz.status_code, 200, absatz.content[:200])

    def test_masse_der_figur(self):
        antwort = self.klient.post('/api/garmentcode/masse/', self.figur())
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        masse = antwort.json()
        self.assertNotIn('fehler', masse, masse)
        text = json.dumps(masse)
        for name in ('height', 'waist', 'hips'):
            self.assertIn(name, text)

    # ------------------------------------------------- Vorschau / Bauen 2D

    def test_vorschau_2d_hose(self):
        ergebnis = self.erzeugen('hose', {'pants.length': 0.9, 'pants.flare': 0.5})
        netz = self.klient.post('/api/garmentcode/schnittnetz/', {'spezifikation': ergebnis['spezifikation']})
        self.assertEqual(netz.status_code, 200, netz.content[:300])
        panels = netz.json().get('panels') or []
        self.assertGreaterEqual(len(panels), 4, netz.json().keys())     # pant_f_l/r, pant_b_l/r, wb
        self.assertTrue(ergebnis.get('vorschau'), ergebnis)

    def test_vorschau_3d_oberteil(self):
        ergebnis = self.erzeugen('oberteil', {'meta.upper': 'FittedShirt', 'sleeve.length': 0.3})
        antwort = self.klient.post('/api/garmentcode/vorschau3d/', self.figur(ordner=ergebnis['ordner']))
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        vorschau = antwort.json()
        self.assertNotIn('fehler', vorschau, vorschau)
        self.assertGreater(len(vorschau.get('punkte') or []), 100, list(vorschau.keys()))

    # ---------------------------------------------- Form-Kästchen / Vorbild

    def test_hoeschen_ist_eine_kurze_hose_ohne_oberteil(self):
        """Das Form-Kästchen „Höschen" und das Vorbild „Fr Thong" — beide
        müssen eine Hose ergeben, keinen BH (21:26: 3.218 Punkte BH statt
        6.160 Punkte Höschen)."""
        for name, regler in (('Kästchen', {'meta.upper': None, 'meta.wb': 'StraightWB',
                                           'meta.bottom': 'Pants', 'pants.length': 0.2}),
                             ('Vorbild', {'meta.upper': None, 'meta.wb': 'StraightWB',
                                          'meta.bottom': 'Pants', 'pants.length': 0.112})):
            ergebnis = self.erzeugen('unterwaesche', regler)
            spez = json.load(open(ergebnis['spezifikation'], encoding='utf-8'))
            panels = spez['pattern']['panels'].keys()
            self.assertTrue(any(p.startswith('pant_') for p in panels), (name, list(panels)))
            self.assertFalse(any('torso' in p for p in panels), (name, list(panels)))

    def test_bh_ist_ein_oberteil_ohne_hose(self):
        ergebnis = self.erzeugen('unterwaesche', {'meta.upper': 'FittedShirt', 'meta.wb': None,
                                                  'meta.bottom': None, 'sleeve.sleeveless': True,
                                                  'shirt.length': 0.5})
        panels = json.load(open(ergebnis['spezifikation'], encoding='utf-8'))['pattern']['panels'].keys()
        self.assertTrue(any('torso' in p for p in panels), list(panels))
        self.assertFalse(any(p.startswith('pant_') for p in panels), list(panels))

    # ------------------------------------------------- Antwort verloren

    def test_eine_verlorene_antwort_ist_nachzuholen(self):
        """Mit `anfrage=<kennung>` legt der Server seine Antwort ab; ein
        zweiter Abruf bekommt sie ohne neuen Lauf (`garmentantwort.py`)."""
        kennung = 'knoepfe-test-erzeugen-0001'
        antwort = self.klient.post('/api/garmentcode/erzeugen/', self.figur(
            vorlage='hose', regler=json.dumps({'pants.length': 0.9}), anfrage=kennung))
        self.assertEqual(antwort.status_code, 200)
        nachgeholt = self.klient.get('/api/garmentcode/antwort/%s/' % kennung)
        self.assertEqual(nachgeholt.status_code, 200, nachgeholt.content[:200])
        self.assertEqual(nachgeholt.json()['spezifikation'], antwort.json()['spezifikation'])
        self.assertEqual(self.klient.get('/api/garmentcode/antwort/gibt-es-nicht-0001/').status_code, 404)
        self.assertEqual(self.klient.get('/api/garmentcode/antwort/x/').status_code, 400)
