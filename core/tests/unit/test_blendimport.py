# -*- coding: utf-8 -*-
"""Blender-Import (Charakter → Datei → Modell importieren…, 08.10.2026) — die Teile ohne Blender und ohne GPU.

Edgars Entscheidungen für „cute girl", die als Vorgabe dastehen:

1. Die .blend mit der höchsten FASSUNG im Namen gilt (nicht die jüngste Datei): `cute girl 5.0` vor `4.5`, und `4.10`
   nach `4.9` (Zahlen, nicht Text); Sicherungen (`.blend1`) zählen nicht. Der Name ist der des Ordners.
2. Die höchste Kachelgröße (8192 px, so groß wie das Original) und die Haltung über das Rig sind die Vorgaben;
   Unbekanntes fällt auf die Vorgabe.
3. Die Knochenkarte ARP → Genesis nennt je Gliedmaß eine Richtung (Einheitsvektor), Eltern vor Kindern, links und rechts
   gespiegelt, Arme und Beine zeigen nach unten.
4. Das Umposen dreht jedes Segment so, dass sein Glied danach in Genesis-Richtung zeigt — auch wenn das Elternsegment
   schon gedreht wurde (Kette Oberarm → Unterarm). `blendumposen.py` läuft in Blender; hier mit einem Rig aus
   Attrappen und einem Ersatz für `bpy`.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.blendimportquelle import Blendimportquelle


def _blendumposen():
    """`blendumposen.py` mit einem Ersatz für `bpy` laden (liegt unter `effekte/`, kein Paket)."""
    pfad = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport' / 'blendumposen.py'
    with mock.patch.dict(sys.modules, {'bpy': ModuleType('bpy')}):
        spec = importlib.util.spec_from_file_location('blendumposen_test', pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    return modul.Blendumposen


class BlendimportquelleTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.pfad = Path(self.ordner.name) / 'cute girl'
        self.pfad.mkdir()

    def tearDown(self):
        self.ordner.cleanup()

    def _dateien(self, *namen):
        for name in namen:
            (self.pfad / name).write_bytes(b'BLENDER')

    def test_1_hoechste_fassung_gewinnt_nicht_die_jüngste_datei(self):
        self._dateien('cute girl 5.0.blend', 'cute girl 4.5.blend', 'cute girl 4.0.blend')
        self.assertEqual(Blendimportquelle(self.pfad).datei().name, 'cute girl 5.0.blend')

    def test_2_vier_zehn_kommt_nach_vier_neun(self):
        self._dateien('x 4.9.blend', 'x 4.10.blend')
        self.assertEqual(Blendimportquelle(self.pfad).datei().name, 'x 4.10.blend')

    def test_3_sicherungen_zaehlen_nicht(self):
        self._dateien('cute girl 4.0.blend', 'cute girl 9.0.blend1')
        self.assertEqual(Blendimportquelle(self.pfad).datei().name, 'cute girl 4.0.blend')

    def test_4_name_wie_der_ordner_oder_die_datei_ohne_fassung(self):
        self._dateien('cute girl 5.0.blend')
        self.assertEqual(Blendimportquelle(self.pfad, 'ordner').name(), 'cute girl')
        self.assertEqual(Blendimportquelle(self.pfad, 'datei').name(), 'cute girl')

    def test_5_leerer_pfad_und_ordner_ohne_blend_sind_fehler(self):
        with self.assertRaises(ValueError):
            Blendimportquelle('')
        with self.assertRaises(ValueError):
            Blendimportquelle(self.pfad).datei()

    def test_6_eigener_name_kommt_aus_dem_textfeld_und_verliert_sonderzeichen(self):
        self._dateien('cute girl 5.0.blend')
        self.assertEqual(Blendimportquelle(self.pfad, 'eigen', '  Mila  ').name(), 'Mila')
        self.assertEqual(Blendimportquelle(self.pfad, 'eigen', 'Mila <3>/x\\y').name(), 'Mila 3xy')
        self.assertEqual(Blendimportquelle(self.pfad, 'eigen', 'Mila   Zwei').name(), 'Mila Zwei')
        self.assertEqual(Blendimportquelle(self.pfad, 'eigen', 'a' * 100).name(), 'a' * Blendimportquelle.NAME_MAX)
        self.assertEqual(Blendimportquelle(self.pfad, 'eigen', 'Mila').steckbrief()['name'], 'Mila')

    def test_7_eigener_name_ohne_brauchbaren_text_ist_ein_fehler(self):
        self._dateien('cute girl 5.0.blend')
        for text in ('', '   ', '***/\\<>'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                Blendimportquelle(self.pfad, 'eigen', text).name()

    def test_8_der_text_des_namensfelds_gilt_nur_bei_der_wahl_eigener_name(self):
        self._dateien('cute girl 5.0.blend')
        self.assertEqual(Blendimportquelle(self.pfad, 'ordner', 'Mila').name(), 'cute girl')
        self.assertEqual(Blendimportquelle(self.pfad, 'datei', 'Mila').name(), 'cute girl')


class BlendimporteinstellungenTest(SimpleTestCase):
    databases = set()

    def test_1_vorgaben_sind_die_entscheidungen(self):
        werte = Blendimporteinstellungen.pruefen({})
        # Edgar (08.10.2026): „default für Import: Höchste Auflösung" — gespeichert UND im Browser 8192 px.
        self.assertEqual(werte['kachel_px'], '8192')
        self.assertEqual(werte['browser_px'], '8192')
        self.assertEqual(werte['umposen'], 'rig')
        self.assertEqual(werte['augen'], 'objekt', 'Edgar 08.10.2026: „die augen hast du nicht importiert (als extra objekt)"')
        self.assertEqual(werte['name'], 'ordner')
        self.assertEqual(werte['eigener_name'], '')

    def test_2_unbekanntes_faellt_auf_die_vorgabe(self):
        werte = Blendimporteinstellungen.pruefen({'kachel_px': '123', 'umposen': 'x', 'pfad': ' "A:\\x" '})
        self.assertEqual(werte['kachel_px'], '8192')
        self.assertEqual(werte['umposen'], 'rig')
        self.assertEqual(werte['pfad'], 'A:\\x')

    def test_3_der_katalog_fuer_den_dialog_ist_json(self):
        json.dumps(Blendimporteinstellungen.katalog())

    def test_4_eigener_name_ist_eine_wahl_mit_textfeld_das_nur_dazu_gehoert(self):
        werte = Blendimporteinstellungen.pruefen({'name': 'eigen', 'eigener_name': ' "Mila" '})
        self.assertEqual((werte['name'], werte['eigener_name']), ('eigen', 'Mila'))
        self.assertEqual(Blendimporteinstellungen.pruefen({'name': 'unbekannt'})['name'], 'ordner')
        optionen = {o['schluessel']: o for o in Blendimporteinstellungen.katalog()['optionen']}
        self.assertIn('eigen', [w['wert'] for w in optionen['name']['werte']])
        self.assertEqual(optionen['eigener_name']['nur_wenn'], {'name': 'eigen'})
        self.assertTrue(optionen['eigener_name']['platzhalter'])

    def test_5_beide_stufenlisten_enden_bei_der_hoechsten_aufloesung(self):
        stufen = [w for w, _ in Blendimporteinstellungen.eintrag('browser_px')['werte']]
        self.assertEqual(stufen[-1], '8192')
        gespeichert = [w for w, _ in Blendimporteinstellungen.eintrag('kachel_px')['werte']]
        self.assertEqual(gespeichert[-1], '8192', 'die höchste gespeicherte Auflösung ist die des Originals')


class KnochenkarteTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from Genesis9.arpknochenkarte import G9arpknochenkarte

        cls.karte = G9arpknochenkarte.karte()

    def test_1_je_seite_dreiundzwanzig_segmente_mit_einheitsrichtung(self):
        """8 Gliedmaßen-Segmente + 15 Fingerglieder je Seite."""
        self.assertEqual(len(self.karte), 46)
        for s in self.karte:
            self.assertAlmostEqual(float(np.linalg.norm(s['ziel'])), 1.0, places=4, msg=s['name'])

    def test_2_eltern_stehen_vor_den_kindern(self):
        gesehen = set()
        for s in self.karte:
            self.assertTrue(s['eltern'] is None or s['eltern'] in gesehen, s['name'])
            gesehen.add(s['name'])

    def test_3_links_und_rechts_gespiegelt(self):
        je_name = {s['name']: s['ziel'] for s in self.karte}
        for name, ziel in je_name.items():
            if name.endswith('_l'):
                rechts = je_name[name[:-2] + '_r']
                self.assertAlmostEqual(ziel[0], -rechts[0], places=3, msg=name)
                self.assertAlmostEqual(ziel[2], rechts[2], places=3, msg=name)

    def test_4_arme_und_beine_zeigen_nach_unten(self):
        je_name = {s['name']: s['ziel'] for s in self.karte}
        for name in ('oberarm_l', 'unterarm_l', 'oberschenkel_l', 'unterschenkel_l', 'oberarm_r', 'oberschenkel_r'):
            self.assertLess(je_name[name][2], -0.5, name)


class UmposenTest(SimpleTestCase):
    """Zwei Segmente einer Kette: Oberarm (Schulter → Ellbogen), Unterarm (Ellbogen → Handgelenk)."""

    databases = set()

    def _rig(self, knochen):
        def holen(name):
            if name not in knochen:
                return None
            kopf, schwanz = knochen[name]
            return SimpleNamespace(head_local=kopf, tail_local=schwanz)

        return SimpleNamespace(name='rig', matrix_world=np.eye(4), data=SimpleNamespace(
            bones=SimpleNamespace(get=holen)))

    def _karte(self, ziel_oben, ziel_unten):
        return [
            {'name': 'oben', 'eltern': None, 'arp_von': 'a', 'arp_bis': 'b', 'ziel': ziel_oben, 'gruppen': []},
            {'name': 'unten', 'eltern': 'oben', 'arp_von': 'b', 'arp_bis': 'c', 'ziel': ziel_unten, 'gruppen': []},
        ]

    def test_1_kuerzester_bogen_dreht_a_auf_b(self):
        bogen = _blendumposen().bogen
        a = np.array([0.0, 0.0, -1.0])
        for b in (np.array([1.0, 0.0, 0.0]), np.array([0.6, 0.0, -0.8]), np.array([0.0, 0.0, 1.0])):
            np.testing.assert_allclose(bogen(a, b) @ a, b, atol=1e-9)

    def test_2_beide_segmente_zeigen_danach_in_ihre_zielrichtung(self):
        knochen = {'a': ([0, 0, 1.4], None), 'b': ([0.3, 0, 1.2], None), 'c': ([0.5, 0, 1.0], None)}
        rig = self._rig(knochen)
        oben, unten = np.array([0.8, 0.0, -0.6]), np.array([0.6, -0.2, -0.77])
        oben, unten = oben / np.linalg.norm(oben), unten / np.linalg.norm(unten)
        umposen = _blendumposen()(None, self._karte(list(oben), list(unten)))
        bew = umposen.bewegungen(rig)

        def lage(m, p):
            return m[:3, :3] @ np.asarray(p, dtype=float) + m[:3, 3]

        m_oben, m_unten = bew['oben'][0], bew['unten'][0]
        a, b, c = (np.array(knochen[k][0], dtype=float) for k in 'abc')
        # Das Gelenk b wandert mit dem Oberarm, der Unterarm dreht um das gewanderte Gelenk.
        neu_b = lage(m_oben, b)
        np.testing.assert_allclose(lage(m_unten, b), neu_b, atol=1e-9)
        richtung_oben = (neu_b - lage(m_oben, a)) / np.linalg.norm(neu_b - lage(m_oben, a))
        np.testing.assert_allclose(richtung_oben, oben, atol=1e-9)
        richtung_unten = (lage(m_unten, c) - neu_b) / np.linalg.norm(lage(m_unten, c) - neu_b)
        np.testing.assert_allclose(richtung_unten, unten, atol=1e-9)
        # Starr: die Länge des Gliedes bleibt.
        self.assertAlmostEqual(float(np.linalg.norm(lage(m_unten, c) - neu_b)), float(np.linalg.norm(c - b)), places=9)

    def test_3_fehlender_knochen_laesst_das_segment_beim_eltern(self):
        knochen = {'a': ([0, 0, 1.4], None), 'b': ([0.3, 0, 1.2], None)}   # `c` fehlt
        umposen = _blendumposen()(None, self._karte([0.0, 0.0, -1.0], [0.0, 0.0, -1.0]))
        bew = umposen.bewegungen(self._rig(knochen))
        self.assertIsNone(bew['unten'][1])
        self.assertIn('fehlt', bew['unten'][2])
        np.testing.assert_allclose(bew['unten'][0], bew['oben'][0])


class HautkachelnTest(SimpleTestCase):
    """Die Nägel (Kachel 1005) werden nicht gebacken — Genesis' Nagellack soll sie färben (Edgar, 08.10.2026)."""

    databases = set()

    def test_1_die_naegel_gehoeren_nicht_zu_den_gebackenen_kacheln(self):
        from core.dienste.blendimportlage import Blendimportlage

        self.assertEqual(Blendimportlage.NICHT_GEBACKEN, (1005,))

    def test_2_die_kachelliste_je_kanal_hat_keine_1005(self):
        from core.dienste.blendimporthaut import Blendimporthaut

        haut = Blendimporthaut(None, None, {'netze': []}, [], 8192)
        aus = haut.kacheln([1001, 1002, 1003, 1004])
        self.assertEqual(len(aus), 12)
        self.assertFalse([k for k in aus if k.startswith('1005')])
        self.assertEqual(aus['1002:normalen'], 'haut_1002_normalen.png')
