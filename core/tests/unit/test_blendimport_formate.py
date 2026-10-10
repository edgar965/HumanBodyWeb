# -*- coding: utf-8 -*-
"""Modell-Import aus OBJ und FBX (Charakter → Datei → Modell importieren…, Reiter OBJ/FBX, 10.10.2026) — ohne Blender.

Edgar: „einen fbx und obj importer … möglichst gemeinsamen Code mit dem Blender-Import". Darum stehen hier die Nahtstellen der
gemeinsamen Kette, nicht eine zweite Kette:

1. Ein Format wählt Endung, Katalog und gemerkte Werte (`Blendimportformate`, `Fremdimporteinstellungen`); Unbekanntes ist die .blend.
2. Der Katalog von OBJ und FBX IST der der .blend (gleiche Fragen, gleiche Vorgaben) — nur der Pfad und die Haltung weichen ab.
   Das erste Mal gelten die gemerkten Werte der .blend (ohne Pfad).
3. `Blendimportquelle` liest mit der Endung des Formats; `steckbrief` nennt das Format.
4. Der Lauf hat „umwandeln" nur für OBJ/FBX; ab „export" liest alles `quelle.blend` aus der Ablage, die Herkunft bleibt die Datei des
   Nutzers.
5. `blendumwandeln.py` (läuft in Blender; hier mit einem Ersatz für `bpy`) sucht fehlende Bilder im Ordner der Datei und in
   „Textures"-Ordnern DIREKT darüber — nie im Texturordner einer anderen Figur (gemessen an „Rainy": die Zähne lagen im Ordner von
   „Asian Female").

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.blendimportformate import Blendimportformate
from core.dienste.blendimportlauf import Blendimportlauf
from core.dienste.blendimportquelle import Blendimportquelle
from core.dienste.blendimportumwandeln import Blendimportumwandeln
from core.dienste.fremdimporteinstellungen import Fbximporteinstellungen, Objimporteinstellungen


def _blendumwandeln():
    """`blendumwandeln.py` mit einem Ersatz für `bpy` laden (liegt unter `effekte/`, kein Paket)."""
    pfad = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport' / 'blendumwandeln.py'
    bpy = ModuleType('bpy')
    bpy.app = SimpleNamespace(version_string='5.2.2')       # `Blendumwandeln.__init__` schreibt die Fassung in den Bericht
    with mock.patch.dict(sys.modules, {'bpy': bpy}):
        spec = importlib.util.spec_from_file_location('blendumwandeln_test', pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    return modul.Blendumwandeln


class FormateTest(SimpleTestCase):
    databases = set()

    def test_1_unbekanntes_format_ist_die_blend(self):
        for roh in (None, '', 'stl', 'OBJ'):
            self.assertEqual(Blendimportformate.pruefen(roh), 'blend')
        self.assertEqual(Blendimportformate.pruefen('obj'), 'obj')

    def test_2_endung_und_umwandeln(self):
        self.assertEqual([Blendimportformate.endung(f) for f in ('blend', 'obj', 'fbx')], ['.blend', '.obj', '.fbx'])
        self.assertFalse(Blendimportformate.umwandeln('blend'))
        self.assertTrue(Blendimportformate.umwandeln('obj'))
        self.assertTrue(Blendimportformate.umwandeln('fbx'))

    def test_3_die_einstellungen_der_blend_bleiben_die_alte_klasse(self):
        self.assertIs(Blendimportformate.einstellungen('blend'), Blendimporteinstellungen)
        self.assertIs(Blendimportformate.einstellungen('obj'), Objimporteinstellungen)
        self.assertIs(Blendimportformate.einstellungen('fbx'), Fbximporteinstellungen)


class FremdeinstellungenTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _schluessel(klasse):
        return [e['schluessel'] for e in klasse.KATALOG]

    def test_1_derselbe_katalog_wie_die_blend_nur_ohne_haltung_bei_obj(self):
        blend = self._schluessel(Blendimporteinstellungen)
        self.assertEqual(self._schluessel(Fbximporteinstellungen), blend)
        self.assertEqual(self._schluessel(Objimporteinstellungen), [s for s in blend if s != 'umposen'])

    def test_2_vorgaben_sind_die_der_blend_ausser_der_haltung_der_fbx(self):
        blend = Blendimporteinstellungen.pruefen({})
        fbx = Fbximporteinstellungen.pruefen({})
        self.assertEqual({k: v for k, v in fbx.items() if k != 'umposen'}, {k: v for k, v in blend.items() if k != 'umposen'})
        self.assertEqual((blend['umposen'], fbx['umposen']), ('rig', 'aus'), 'ein FBX-Rig ist selten Auto-Rig Pro')
        self.assertNotIn('umposen', Objimporteinstellungen.pruefen({}))

    def test_3_der_pfad_traegt_die_endung_des_formats(self):
        titel = {k.FORMAT: k.eintrag('pfad')['titel'] for k in (Blendimporteinstellungen, Objimporteinstellungen, Fbximporteinstellungen)}
        self.assertEqual(titel, {'blend': 'Ordner oder .blend', 'obj': 'Ordner oder .obj', 'fbx': 'Ordner oder .fbx'})
        self.assertIn('.obj', Objimporteinstellungen.eintrag('pfad')['platzhalter'])

    def test_4_jedes_format_merkt_in_seiner_eigenen_datei(self):
        namen = {k.DATEI for k in (Blendimporteinstellungen, Objimporteinstellungen, Fbximporteinstellungen)}
        self.assertEqual(len(namen), 3)
        self.assertEqual(Blendimporteinstellungen.DATEI, 'einstellungen.json', 'die Datei der .blend darf sich nie ändern')

    def test_5_das_erste_mal_gelten_die_werte_der_blend_ohne_pfad(self):
        with tempfile.TemporaryDirectory(dir=str(Path(__file__).parent)) as ordner:
            neu = Path(ordner) / 'gibt_es_nicht.json'
            blend = {'pfad': 'A:\\blender\\x.blend', 'kachel_px': '4096', 'umposen': 'rig', 'name': 'eigen', 'eigener_name': 'seori'}
            with mock.patch.object(Objimporteinstellungen, 'pfad', return_value=neu), \
                    mock.patch.object(Fbximporteinstellungen, 'pfad', return_value=neu), \
                    mock.patch.object(Blendimporteinstellungen, 'laden', return_value=Blendimporteinstellungen.pruefen(blend)):
                obj = Objimporteinstellungen.laden()
                fbx = Fbximporteinstellungen.laden()
        self.assertEqual(obj['kachel_px'], '4096')
        self.assertEqual(obj['pfad'], '', 'der Pfad der .blend gehört nicht zur OBJ')
        self.assertEqual((obj['name'], obj['eigener_name']), ('ordner', ''), 'der „Eigene Name" der letzten .blend gehört nicht zur OBJ')
        self.assertEqual(fbx['kachel_px'], '4096')
        self.assertEqual(fbx['umposen'], 'aus', 'die Haltung „rig" der .blend gilt für ein FBX-Rig nicht (Vorgabe des Formats)')

    def test_6_katalog_nennt_das_format(self):
        self.assertEqual(Blendimporteinstellungen.katalog()['format'], 'blend')
        self.assertEqual(Fbximporteinstellungen.katalog()['format'], 'fbx')
        json.dumps(Objimporteinstellungen.katalog())


class QuelleEndungTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.pfad = Path(self.ordner.name) / 'Rainy'
        self.pfad.mkdir()

    def tearDown(self):
        self.ordner.cleanup()

    def test_1_der_ordner_wird_nach_der_endung_des_formats_gelesen(self):
        for name in ('Rainy 4.0.blend', 'Rainy.OBJ', 'Rainy.mtl', 'Rainy.Fbx'):
            (self.pfad / name).write_bytes(b'x')
        self.assertEqual(Blendimportquelle(self.pfad).datei().name, 'Rainy 4.0.blend')
        self.assertEqual(Blendimportquelle(self.pfad, endung='.obj').datei().name, 'Rainy.OBJ')
        self.assertEqual(Blendimportquelle(self.pfad, endung='.fbx').datei().name, 'Rainy.Fbx')

    def test_2_eine_datei_mit_falscher_endung_ist_ein_fehler_der_die_endung_nennt(self):
        (self.pfad / 'Rainy.fbx').write_bytes(b'x')
        with self.assertRaisesRegex(ValueError, r'Keine \.obj: Rainy\.fbx'):
            Blendimportquelle(self.pfad / 'Rainy.fbx', endung='.obj').datei()
        with self.assertRaisesRegex(ValueError, r'Keine \.obj im Ordner'):
            Blendimportquelle(self.pfad, endung='.obj').datei()
        with self.assertRaisesRegex(ValueError, r'Pfad fehlt.*\.fbx'):
            Blendimportquelle('', endung='.fbx')

    def test_3_steckbrief_nennt_das_format_und_der_name_bleibt_der_des_ordners(self):
        (self.pfad / 'Rainny DS.obj').write_bytes(b'x')
        brief = Blendimportquelle(self.pfad, 'ordner', '', '.obj').steckbrief()
        self.assertEqual((brief['format'], brief['name']), ('obj', 'Rainy'))
        self.assertEqual(Blendimportquelle(self.pfad, 'datei', '', '.obj').name(), 'Rainny DS')

    def test_4_ohne_endung_wie_bisher_die_blend(self):
        (self.pfad / 'x.blend').write_bytes(b'x')
        self.assertEqual(Blendimportquelle(self.pfad).steckbrief()['format'], 'blend')


class LaufSchritteTest(SimpleTestCase):
    databases = set()

    def test_1_umwandeln_gibt_es_nur_fuer_obj_und_fbx(self):
        blend = Blendimportlauf.schritte_fuer('blend')
        self.assertNotIn('umwandeln', blend)
        for format in ('obj', 'fbx'):
            schritte = Blendimportlauf.schritte_fuer(format)
            self.assertEqual(schritte[0], 'umwandeln')
            self.assertEqual(schritte[1:], blend, 'ab „export" dieselbe Kette')

    def test_2_jeder_schritt_hat_sein_band_und_die_baender_schliessen_aneinander(self):
        self.assertEqual(set(Blendimportlauf.BAENDER), set(Blendimportlauf.SCHRITTE))
        baender = [Blendimportlauf.BAENDER[s] for s in Blendimportlauf.SCHRITTE]
        self.assertEqual(baender[0][0], 0)
        self.assertEqual(baender[-1][1], 100)
        for davor, danach in zip(baender, baender[1:], strict=False):
            self.assertEqual(davor[1], danach[0])

    def test_3_ab_export_liest_alles_die_umgewandelte_blend_die_herkunft_bleibt_die_datei(self):
        lauf = Blendimportlauf.__new__(Blendimportlauf)
        lauf.stand = {'quelle': {'datei': 'A:\\m\\Rainy.fbx', 'format': 'fbx', 'blend': 'A:\\i\\quelle.blend'}}
        self.assertEqual(lauf.blend(), 'A:\\i\\quelle.blend')
        lauf.stand = {'quelle': {'datei': 'A:\\m\\x.blend', 'format': 'blend'}}
        self.assertEqual(lauf.blend(), 'A:\\m\\x.blend')

    def test_4_eine_blend_ueberspringt_umwandeln_und_ruft_blender_nicht(self):
        lauf = Blendimportlauf.__new__(Blendimportlauf)
        lauf.format = 'blend'
        lauf.stand = {'quelle': {'datei': 'x.blend'}}
        gemerkt = {}
        lauf.ergebnis = lambda schritt, wert: gemerkt.update({schritt: wert})
        with mock.patch.object(Blendimportumwandeln, 'wandeln') as wandeln:
            lauf._umwandeln()
        wandeln.assert_not_called()
        self.assertTrue(gemerkt['umwandeln']['aus'])

    def test_5_obj_wandelt_und_merkt_die_blend_im_stand(self):
        lauf = Blendimportlauf.__new__(Blendimportlauf)
        lauf.format = 'obj'
        lauf.stand = {'quelle': {'datei': 'A:\\m\\x.obj', 'format': 'obj'}}
        lauf.ablage = SimpleNamespace(quelle_blend=lambda: Path('A:/i/quelle.blend'))
        lauf.melden = lambda *a: None
        gemerkt = {}
        lauf.ergebnis = lambda schritt, wert: gemerkt.update({schritt: wert})
        lauf.sichern = lambda **felder: lauf.stand.update(felder)
        with mock.patch.object(Blendimportumwandeln, 'wandeln', return_value={'werkzeug': 'wm.obj_import'}) as wandeln:
            lauf._umwandeln()
        wandeln.assert_called_once_with('A:\\m\\x.obj', 'obj')
        self.assertEqual(Path(lauf.stand['quelle']['blend']), Path('A:/i/quelle.blend'))
        self.assertEqual(lauf.stand['quelle']['datei'], 'A:\\m\\x.obj')
        self.assertEqual(gemerkt['umwandeln'], {'werkzeug': 'wm.obj_import'})


class UmwandelnAufrufTest(SimpleTestCase):
    databases = set()

    def test_1_blender_startet_ohne_quell_blend_und_bekommt_quelle_format_ziel_bericht(self):
        with tempfile.TemporaryDirectory(dir=str(Path(__file__).parent)) as ordner:
            ablage = SimpleNamespace(kennung='2026.10.10.00.00.00', quelle_blend=lambda: Path(ordner) / 'quelle.blend',
                                     export=lambda name='': Path(ordner) / name)
            (Path(ordner) / 'umwandeln.json').write_text(json.dumps({'werkzeug': 'import_scene.fbx', 'bilder': {'fehlen': []}}))
            with mock.patch('core.dienste.blendimportumwandeln.Blendimportblender') as blender:
                bericht = Blendimportumwandeln(ablage).wandeln('A:\\m\\Rainy.fbx', 'fbx')
        skript, quelle_blend, argumente, ergebnis = blender.return_value.laufen.call_args.args
        self.assertEqual(skript, 'blendumwandeln.py')
        self.assertIsNone(quelle_blend, 'es gibt keine Quell-.blend')
        self.assertEqual(argumente[argumente.index('--format') + 1], 'fbx')
        self.assertEqual(argumente[argumente.index('--quelle') + 1], 'A:\\m\\Rainy.fbx')
        self.assertEqual(Path(ergebnis).name, 'quelle.blend')
        self.assertEqual(bericht['werkzeug'], 'import_scene.fbx')


class BildersucheTest(SimpleTestCase):
    """`Blendumwandeln.wurzeln` / `bildindex` — nur Dateisystem, `bpy` ist ein Ersatz."""
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.wurzel = Path(self.ordner.name)
        self.klasse = _blendumwandeln()

    def tearDown(self):
        self.ordner.cleanup()

    def _datei(self, *teile):
        pfad = self.wurzel.joinpath(*teile)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b'x')
        return pfad

    def _suche(self, quelle):
        return self.klasse(SimpleNamespace(quelle=str(quelle), format='fbx')).bildindex()

    def test_1_unity_muster_texturen_einen_ordner_ueber_der_fbx(self):
        fbx = self._datei('Asuna', 'Character', 'asuna.fbx')
        bild = self._datei('Asuna', 'Textures', 'AsunaBody', 'AsunaBodyNormal.png')
        self.assertEqual(self._suche(fbx).get('asunabodynormal.png'), str(bild))

    def test_2_ein_texturordner_einer_anderen_figur_wird_nicht_durchsucht(self):
        fbx = self._datei('Blender', 'Rainy', 'Rainny DS.fbx')
        self._datei('Blender', 'Rainy', 'textures', 'body.png')
        self._datei('Blender', 'Asian Female', 'textures', 'teeth_basecolor.png')
        gefunden = self._suche(fbx)
        self.assertIn('body.png', gefunden)
        self.assertNotIn('teeth_basecolor.png', gefunden)

    def test_3_die_suche_ist_gross_klein_egal_und_der_naeher_liegende_fund_gewinnt(self):
        fbx = self._datei('M', 'Figur', 'f.fbx')
        nah = self._datei('M', 'Figur', 'Tex', 'Haut.PNG')
        self._datei('M', 'textures', 'haut.png')
        self.assertEqual(self._suche(fbx)['haut.png'], str(nah))

    def test_4_nicht_bilder_kommen_nicht_in_den_index(self):
        fbx = self._datei('M', 'Figur', 'f.fbx')
        self._datei('M', 'Figur', 'notiz.txt')
        self.assertEqual(self._suche(fbx), {})
