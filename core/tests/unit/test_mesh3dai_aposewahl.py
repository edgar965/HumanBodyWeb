# -*- coding: utf-8 -*-
"""Einstellung „Zwischenschritt A-Pose“ von Mesh3D-AI (18.10.2026, `Mesh3daiaposewahl`): der Wert, die Vorgabe der Jobseite (`Mesh3daiwege`) und die Datei der Testseite (`Mesh3daitest.endung`).
Ohne Datenbank (die Wahl wird je Fall umgebogen), Dateien nur in einem eigenen Ordner unter ProjektTemp.

Seit 18.10.2026 abends zeigt die Jobseite den jüngsten Lauf DER eingestellten Methode (MeshToRigToPose_MIA / MeshToRigToPose, `MethodeTest`, Fälle 8–13).

Sabotage-Gegenprobe (von Hand): in `Mesh3daiwege.lesen` die Zeile `standard = 'direkt'` streichen → Fall 4 rot; in `Mesh3daiwege.stand` die Wahl aus dem Tupel nehmen → Fall 5 rot;
in `Mesh3daitest.endung` die Bedingung `(p / 'test_direkt.json').is_file()` streichen → Fall 7 rot; in `Mesh3daiwege.gewaehlt` die Schleife durch `return (*alle[0], False)` ersetzen → Fall 8 und 11 rot;
`Mesh3daiaposewahl.rueckfall` immer `False` → Fall 10 rot; `Mesh3daiapose._gewaehlt` wieder `wege.json` lesen lassen → Fall 12 rot.
"""

import json
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.mesh3daiapose import Mesh3daiapose
from core.dienste.mesh3daiaposewahl import Mesh3daiaposewahl
from core.dienste.mesh3daitest import Mesh3daitest
from core.dienste.mesh3daiwege import Mesh3daiwege

from ._pruefablage import Pruefablage


def _wahl(wert):
    return mock.patch.object(Mesh3daiaposewahl, 'gewaehlt', classmethod(lambda cls: wert))


class WertTest(SimpleTestCase):
    def test_1_gueltige_werte(self):
        for wert, _text in Mesh3daiaposewahl.WERTE:
            self.assertEqual(Mesh3daiaposewahl.aus({Mesh3daiaposewahl.SCHLUESSEL: wert}), wert)

    def test_2_unbekanntes_ist_die_vorgabe(self):
        for prefs in (None, {}, {Mesh3daiaposewahl.SCHLUESSEL: 'quatsch'}, {Mesh3daiaposewahl.SCHLUESSEL: ''}, {Mesh3daiaposewahl.SCHLUESSEL: 3}):
            self.assertEqual(Mesh3daiaposewahl.aus(prefs), Mesh3daiaposewahl.VORGABE)
        self.assertEqual(Mesh3daiaposewahl.VORGABE, 'mia')


class JobseiteTest(SimpleTestCase):
    """Ein Lauf mit drei Wegen (wie `Vorstufenkette.wege` sie schreibt): Vorgabe `vorstufe`."""

    def _lauf(self, ordner):
        lauf = Path(ordner)
        wege = [{'schluessel': k, 'name': k, 'text': ''} for k in ('vorstufe', 'direkt', 'rig')]
        (lauf / 'wege.json').write_text(json.dumps({'fassung': Mesh3daiwege.FASSUNG, 'standard': 'vorstufe', 'wege': wege}), encoding='utf-8')
        np.savez(lauf / 'wege.npz', nr=np.array([1]), **{'%s_rig' % k: np.zeros((1, 3, 3), np.float32) for k in ('vorstufe', 'direkt', 'rig')},
                 **{'%s_dreh' % k: np.tile(np.eye(3, dtype=np.float32), (1, 3, 1, 1)) for k in ('vorstufe', 'direkt', 'rig')})
        return lauf

    def test_3_mia_und_rig_behalten_die_vorgabe_des_laufs(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o)
            for wert in ('mia', 'rig'):
                with _wahl(wert):
                    self.assertEqual(Mesh3daiwege.lesen(lauf, 3)['standard'], 'vorstufe', wert)

    def test_4_aus_zeigt_zuerst_das_netz_direkt(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o)
            with _wahl('aus'):
                w = Mesh3daiwege.lesen(lauf, 3)
            self.assertEqual(w['standard'], 'direkt')
            self.assertEqual([x['schluessel'] for x in w['wege']], ['vorstufe', 'direkt', 'rig'])

    def test_5_der_stand_wechselt_mit_der_einstellung(self):
        """Sonst behielte `Mesh3daidaten` die alte Vorgabe in seiner Ablage, bis sich eine Datei ändert."""
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o)
            with _wahl('mia'):
                a = Mesh3daiwege.stand(lauf)
            with _wahl('aus'):
                b = Mesh3daiwege.stand(lauf)
            self.assertNotEqual(a, b)
            self.assertEqual(a[:2], b[:2])


class TestseiteTest(SimpleTestCase):
    def test_6_ohne_aus_bleibt_die_fassung_mit_vorstufe(self):
        with Pruefablage.ordner('aposewahl_') as o:
            (Path(o) / 'test_direkt.json').write_text('{}', encoding='utf-8')
            self.assertEqual(Mesh3daitest.endung(Path(o), 'mia'), '')
            self.assertEqual(Mesh3daitest.endung(Path(o), 'rig'), '')
            self.assertEqual(Mesh3daitest.endung(Path(o), 'aus'), '_direkt')

    def test_7_aus_ohne_gesicherte_fassung_zeigt_was_da_ist(self):
        with Pruefablage.ordner('aposewahl_') as o:
            self.assertEqual(Mesh3daitest.endung(Path(o), 'aus'), '')


class MethodeTest(SimpleTestCase):
    """Ein Lauf mit zwei Fassungen wie nach zwei Läufen der Kette: `wege.json` (jünger) und `wege_vor_<Zeit>.json` (älter), jede mit eigener Ablage und `kette.json`."""

    NETZ = 'netz_v'

    def _fassung(self, lauf, datei, ablage, kette, mm):
        ablage.mkdir(parents=True, exist_ok=True)
        (ablage / 'kette.json').write_text(json.dumps(kette), encoding='utf-8')
        (ablage / self.NETZ).mkdir(exist_ok=True)
        np.savez(ablage / self.NETZ / 'anzeige_Figur.npz', punkte=np.zeros((1, 3), np.float32))
        wege = [{'schluessel': k, 'name': 'Rig → A-Pose → Netz' if k == 'vorstufe' else k, 'text': 'Vorstufe: alter Text.'} for k in ('vorstufe', 'direkt', 'rig')]
        (lauf / ('%s.json' % datei)).write_text(json.dumps({'fassung': Mesh3daiwege.FASSUNG, 'standard': 'vorstufe', 'wege': wege, 'ablage': str(ablage), 'netz_vorstufe': self.NETZ,
                                                            'proben': {'1': {'vorstufe': {'mm': mm}}}}), encoding='utf-8')
        np.savez(lauf / ('%s.npz' % datei), nr=np.array([1]), **{'%s_rig' % k: np.full((1, 3, 3), mm, np.float32) for k in ('vorstufe', 'direkt', 'rig')},
                 **{'%s_dreh' % k: np.tile(np.eye(3, dtype=np.float32), (1, 3, 1, 1)) for k in ('vorstufe', 'direkt', 'rig')})

    def _lauf(self, o, alt_kette=None, mit_alt=True):
        wurzel = Path(o)
        lauf = wurzel / 'lauf'
        lauf.mkdir()
        if mit_alt:
            self._fassung(lauf, 'wege_vor_2026.10.18.12.00', wurzel / 'vorstufe' / '0001', alt_kette if alt_kette is not None else {}, 13.0)
        self._fassung(lauf, 'wege', wurzel / 'vorstufe' / '0002', {'weg': 'mia', 'weg_grund': 'MIA OK'}, 17.0)
        return lauf

    def test_8_jede_methode_zeigt_ihren_juengsten_lauf(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o)
            with _wahl('mia'):
                w = Mesh3daiwege.lesen(lauf, 3)
            self.assertEqual((w['datei'], w['methode'], w['fehlt']), ('wege.json', 'MeshToRigToPose_MIA', False))
            self.assertEqual(w['wege'][0]['name'], 'MeshToRigToPose_MIA → Netz')
            self.assertAlmostEqual(float(w['proben'][1]['vorstufe'][0][0, 0]), 17.0, places=4)
            with _wahl('rig'):
                w = Mesh3daiwege.lesen(lauf, 3)
            self.assertEqual((w['datei'], w['methode'], w['fehlt']), ('wege_vor_2026.10.18.12.00.json', 'MeshToRigToPose', False))
            self.assertEqual([x['name'] for x in w['wege']], ['MeshToRigToPose → Netz', 'direkt', 'Rig allein (MeshToRigToPose)'])
            self.assertTrue(w['wege'][0]['text'].startswith('MeshToRigToPose. '))
            self.assertAlmostEqual(float(w['proben'][1]['vorstufe'][0][0, 0]), 13.0, places=4)

    def test_9_ohne_lauf_der_methode_der_juengste_mit_hinweis(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o, mit_alt=False)
            with _wahl('rig'):
                w = Mesh3daiwege.lesen(lauf, 3)
            self.assertEqual((w['datei'], w['methode'], w['fehlt']), ('wege.json', 'MeshToRigToPose_MIA', True))

    def test_10_rueckfall_gehoert_zur_wahl_mia(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o, alt_kette={'weg': 'rig', 'weg_grund': 'MIA DURCHGEFALLEN: Hand'})
            (lauf / 'wege.json').unlink()
            (lauf / 'wege.npz').unlink()
            with _wahl('mia'):
                w = Mesh3daiwege.lesen(lauf, 3)
            self.assertFalse(w['fehlt'])
            self.assertEqual(w['methode'], 'MeshToRigToPose (Rückfall: MIA durchgefallen)')
        self.assertFalse(Mesh3daiaposewahl.rueckfall({'weg': 'rig', 'weg_grund': 'Weg MIA aus (Zwischenschritt A-Pose = rig)'}))
        self.assertFalse(Mesh3daiaposewahl.rueckfall({}))

    def test_11_der_stand_wechselt_mit_der_methode(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o)
            with _wahl('mia'):
                a = Mesh3daiwege.stand(lauf)
            with _wahl('rig'):
                b = Mesh3daiwege.stand(lauf)
            self.assertNotEqual(a[0], b[0])

    def test_12_zwischenbild_aus_der_ablage_der_methode(self):
        with Pruefablage.ordner('aposewahl_') as o:
            lauf = self._lauf(o)
            with _wahl('mia'):
                self.assertEqual(Mesh3daiapose.datei(lauf).parent.parent.name, '0002')
            with _wahl('rig'):
                self.assertEqual(Mesh3daiapose.datei(lauf).parent.parent.name, '0001')

    def test_13_methode_aus_der_kette(self):
        self.assertEqual(Mesh3daiaposewahl.methode({}), 'rig')
        self.assertEqual(Mesh3daiaposewahl.methode(None), 'rig')
        self.assertEqual(Mesh3daiaposewahl.methode({'weg': 'mia'}), 'mia')
        self.assertEqual(Mesh3daiaposewahl.methode({'weg': 'rig'}), 'rig')
        self.assertEqual(set(Mesh3daiaposewahl.NAMEN), {w for w, _t in Mesh3daiaposewahl.WERTE})
        self.assertEqual(set(Mesh3daiaposewahl.BESCHREIBUNG), {w for w, _t in Mesh3daiaposewahl.WERTE})
