# -*- coding: utf-8 -*-
u"""Umabauer und die Bau-Endpunkte — mit einer Unity-Attrappe im Auftragsmodus (06.09.2026).

Die Attrappe ist ein Python-Skript hinter einer `.cmd`, das wie der Exporter
arbeitet: `-auftraege <ordner>` lesen, jede `<name>.auftrag.json` „bauen"
(eine Sekunde), `<name>.glb` in den Katalog legen, `<name>.ergebnis.json`
schreiben, `bauer.json` als Lebenszeichen, nach vier Sekunden Leerlauf enden.
Alles unter `ProjektTemp/`; nichts hier fasst das echte Unity oder den echten
Katalog an.
"""
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from core.dienste.umabauer import Umabauer, UmabauerFehlt

ATTRAPPE = u'''# -*- coding: utf-8 -*-
import json, os, sys, time
args = sys.argv[1:]
ordner = args[args.index('-auftraege') + 1]
katalog = %(katalog)r
os.makedirs(ordner, exist_ok=True)
with open(os.path.join(ordner, 'argv.json'), 'w') as d:
    json.dump(args, d)
RASSEN = [{"name": "ElfFemale30", "kompatibel": ["Human Female 3.0"]},
          {"name": "Human Female 3.0", "kompatibel": []}, "HumanMale"]


def leben(stand):
    with open(os.path.join(ordner, 'bauer.json'), 'w') as d:
        json.dump({'pid': os.getpid(), 'stand': stand, 'zeit': time.time()}, d)


ende = time.time() + 4
while time.time() < ende:
    leben('bereit')
    for f in sorted(os.listdir(ordner)):
        if not f.endswith('.auftrag.json'):
            continue
        with open(os.path.join(ordner, f)) as d:
            a = json.load(d)
        leben('baut')
        time.sleep(1.0)
        name, datei = a.get('name'), ''
        if a.get('rassenliste'):
            with open(a['rassenliste'], 'w') as d:
                json.dump(RASSEN, d)
        elif name:
            pfad = a.get('ziel') or os.path.join(katalog, name + '.glb')
            with open(pfad, 'w') as d:
                d.write('glb')
            datei = os.path.basename(pfad)
        with open(os.path.join(ordner, f[:-len('.auftrag.json')] + '.ergebnis.json'), 'w') as d:
            json.dump({'name': name, 'exit': 0, 'zeiten': 'bau 1.00 s', 'datei': datei, 'auftrag': a}, d)
        os.remove(os.path.join(ordner, f))
        ende = time.time() + 4
    time.sleep(0.2)
leben('beendet')
'''


class UmabauerTest(SimpleTestCase):
    u"""Dienst und Endpunkte gegen die Attrappe."""

    databases = set()
    WARTE_S = 20

    def setUp(self):
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.wurzel = Path(tempfile.mkdtemp(prefix='umabauer_', dir=str(basis)))
        self.katalog = self.wurzel / 'Figuren'
        (self.katalog / 'uma').mkdir(parents=True)
        self.projekt = self.wurzel / 'UMAProject'
        self.projekt.mkdir()
        skript = self.wurzel / 'attrappe.py'
        skript.write_text(ATTRAPPE % {'katalog': str(self.katalog / 'uma')}, encoding='utf-8')
        self.unity = self.wurzel / 'unity.cmd'
        self.unity.write_text('@"%s" "%s" %%*\n' % (sys.executable, skript), encoding='utf-8')
        Umabauer._laeufe.clear()
        Umabauer._prozess = None
        self.umschaltung = override_settings(UNITY_EXE=self.unity, UMA_PROJEKT=self.projekt,
                                             FIGUREN_KATALOG=self.katalog, UMA_BAU_LOGS=self.wurzel / 'logs')
        self.umschaltung.enable()

    def tearDown(self):
        self._abwarten()
        if Umabauer._prozess is not None:
            Umabauer._prozess.wait(timeout=self.WARTE_S)
        self.umschaltung.disable()
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _abwarten(self, name=None):
        u"""Bis kein Lauf mehr läuft; liefert den letzten Stand des genannten Laufs."""
        stand = None
        for _ in range(self.WARTE_S * 10):
            laeuft = False
            for lauf in list(Umabauer._laeufe):
                s = Umabauer.stand(lauf)
                if s['laeuft']:
                    laeuft = True
                if lauf == name:
                    stand = s
            if not laeuft:
                return stand
            time.sleep(0.1)
        self.fail('Attrappe läuft nach %d s noch' % self.WARTE_S)

    # ---------------------------------------------------------------- Dienst

    def test_bauen_legt_die_datei_in_den_katalog(self):
        start = Umabauer.bauen('Human Female 3.0')
        self.assertEqual(start['name'], 'Uma_HumanFemale30')
        self.assertTrue(start['laeuft'])
        self.assertTrue(start['wartet'])
        ende = self._abwarten('Uma_HumanFemale30')
        self.assertEqual(ende['exit'], 0)
        self.assertEqual(ende['datei'], 'Uma_HumanFemale30.glb')
        self.assertEqual(ende['meldung'], 'bau 1.00 s')
        self.assertTrue((self.katalog / 'uma' / 'Uma_HumanFemale30.glb').is_file())
        # Ein neuer Serverprozess kennt den Lauf nur aus der Ablage neben dem Log.
        Umabauer._laeufe.clear()
        self.assertEqual(Umabauer.stand('Uma_HumanFemale30')['datei'], 'Uma_HumanFemale30.glb')

    def test_zwei_auftraege_kommen_nacheinander_dran_ohne_zweiten_start(self):
        erster = Umabauer.bauen('Human Female 3.0')
        zweiter = Umabauer.bauen('Human Male 3.0')
        self.assertTrue(erster['laeuft'] and zweiter['laeuft'])
        self.assertEqual(len(list((self.wurzel / 'logs' / 'bauer').glob('*.auftrag.json'))), 2)
        self._abwarten()
        self.assertEqual(Umabauer.stand('Uma_HumanFemale30')['datei'], 'Uma_HumanFemale30.glb')
        self.assertEqual(Umabauer.stand('Uma_HumanMale30')['datei'], 'Uma_HumanMale30.glb')

    def test_ohne_unity_kommt_fehlt(self):
        with override_settings(UNITY_EXE=self.wurzel / 'gibtsnicht.exe'):
            with self.assertRaises(UmabauerFehlt):
                Umabauer.bauen('Human Female 3.0')

    def test_name_aus_der_rasse_und_ungueltige_namen(self):
        self.assertEqual(Umabauer.name_fuer('Anime Elf Female 3.0'), 'Uma_AnimeElfFemale30')
        with self.assertRaises(ValueError):
            Umabauer.bauen('Human Male 3.0', name='../raus')
        with self.assertRaises(ValueError):
            Umabauer.bauen('')

    def test_rassenliste_kommt_aus_unity(self):
        self.assertIsNone(Umabauer.rassen())
        Umabauer.rassen_ermitteln()
        self._abwarten(Umabauer.RASSENLAUF)
        self.assertEqual(Umabauer.rassen(), ['ElfFemale30', 'Human Female 3.0', 'HumanMale'])
        self.assertEqual(Umabauer.rassen_details()['ElfFemale30'], ['Human Female 3.0'])
        self.assertEqual(Umabauer.rassen_details()['HumanMale'], [])

    def test_bauer_bleibt_fuer_den_naechsten_auftrag_offen(self):
        Umabauer.bauen('Human Female 3.0')
        self._abwarten()
        self.assertTrue(Umabauer.bauer_lebt())
        pid = Umabauer.bauer()['pid']
        Umabauer.bauen('Human Male 3.0')
        self._abwarten()
        self.assertEqual(Umabauer.bauer()['pid'], pid)

    def test_vorwaermen_startet_den_bauer_und_baut_ins_leere(self):
        u"""06.09.2026: Der erste Bau nach einem Start kostet 90 s, jeder weitere
        5 s. Vorwärmen startet den Bauer beim Öffnen der Eigenschaften und baut
        einmal nach `logs/bauer/` — nie in den Katalog — und der Bauer bekommt
        `-leerlauf 0`: Er bleibt offen."""
        self.assertEqual(Umabauer.bauer_stand(), {'lebt': False, 'stand': 'aus', 'startet': False,
                                                  'seit_s': None, 'pid': None})
        self.assertTrue(Umabauer.vorwaermen()['gestartet'])
        self.assertTrue(Umabauer.bauer_stand()['startet'] or Umabauer.bauer_stand()['lebt'])
        self._abwarten(Umabauer.WARMNAME)
        ordner = Path(Umabauer.auftragsordner())
        self.assertTrue((ordner / Umabauer.WARMDATEI).is_file())
        self.assertFalse(list((self.katalog / 'uma').glob('_warm*')))
        stand = Umabauer.bauer_stand()
        self.assertTrue(stand['lebt'])
        # Das Lebenszeichen hinkt dem Ergebnis um einen Takt nach: „baut" ist hier noch erlaubt.
        self.assertIn(stand['stand'], ('bereit', 'baut'))
        self.assertFalse(Umabauer.vorwaermen()['gestartet'])     # lebt schon: nichts zu tun
        argv = json.loads((ordner / 'argv.json').read_text(encoding='utf-8'))
        self.assertEqual(argv[argv.index('-leerlauf') + 1], '0')

    def test_farben_landen_im_auftrag_wie_der_exporter_sie_liest(self):
        Umabauer.bauen('Human Female 3.0', name='Uma_Farbe',
                       farben={'haut': '#E0B090', 'haar': '#302010'})
        self._abwarten('Uma_Farbe')
        ergebnis = json.loads((Path(Umabauer.auftragsordner()) / 'Uma_Farbe.ergebnis.json')
                              .read_text(encoding='utf-8'))
        self.assertEqual(ergebnis['auftrag']['farben'], 'Skin=#e0b090,Hair=#302010')
        for schlecht in ({'haut': 'rot'}, {'augen': '#000000'}, 'Skin=#000000'):
            with self.assertRaises(ValueError, msg=repr(schlecht)):
                Umabauer.bauen('Human Female 3.0', name='Uma_Schlecht', farben=schlecht)
        self.assertFalse((Path(Umabauer.auftragsordner()) / 'Uma_Schlecht.auftrag.json').exists())

    # ------------------------------------------------------------- Endpunkte

    def test_endpunkte_bauen_stand_und_rassen(self):
        antwort = self.client.get('/api/character/uma-rassen/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json(), {'rassen': [], 'ermittelt': False, 'figuren': []})

        antwort = self._bauen('Human Male 3.0')
        self.assertEqual(antwort.status_code, 202, antwort.content)
        name = antwort.json()['name']
        self.assertEqual(name, 'Uma_HumanMale30')
        self.assertEqual(self._bauen('Human Female 3.0').status_code, 202)   # stellt sich an

        self._abwarten(name)
        stand = self.client.get('/api/character/uma-figur/bauen/%s/stand/' % name).json()
        self.assertFalse(stand['laeuft'])
        self.assertEqual(stand['datei'], 'Uma_HumanMale30.glb')
        self.assertEqual(self.client.get('/api/character/uma-figur/bauen/nix/stand/').status_code, 404)

        self._abwarten()
        figuren = self.client.get('/api/character/uma-rassen/').json()['figuren']
        self.assertEqual(sorted(f['name'] for f in figuren), ['Uma_HumanFemale30.glb', 'Uma_HumanMale30.glb'])

    def test_endpunkt_ohne_rasse_und_ohne_unity(self):
        antwort = self.client.post('/api/character/uma-figur/bauen/', '{}', content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        with override_settings(UNITY_EXE=self.wurzel / 'gibtsnicht.exe'):
            antwort = self._bauen('Human Male 3.0')
        self.assertEqual(antwort.status_code, 503)

    def _bauen(self, rasse):
        return self.client.post('/api/character/uma-figur/bauen/', json.dumps({'rasse': rasse}),
                                content_type='application/json')
