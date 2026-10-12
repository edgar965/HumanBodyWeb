# -*- coding: utf-8 -*-
"""`Dazgeograftnachformung` — Nachformung und Unterkleid für das angepasste Daz-Geograft (11.10.2026), mit Attrappen für Import, Morphe und Daz-Bibliothek.

Befund an „cute girl" (Import 08:45, `scham = objekt`): der Import brachte keinen `…_scham`-Morph mit (der Bau lief still ohne Nachformung: Form p90 3,69 statt 2,92 mm, 4 Ringkanten über 60°), und sein
Unterkleid-Morph war ohne Nachformung und mit den Lochpunkten gerechnet (bis 33,9 mm, Knick über die Naht Median 22° statt 9,8°).

1. Sind Nachformung und Unterkleid des Imports da, legt das Daz-Modell Nachformung (mit dem Wert) und `…_unterkleid_daz` (1) auf die Figur und lässt `…_unterkleid` des Imports weg; gerechnet wird nur das
   Unterkleid, die Nachformung nicht noch einmal.
2. Fehlt der `…_scham`-Morph und gehört der Körper-Regler zum letzten Lauf des Imports, wird die Nachformung gerechnet — danach gilt Fall 1.
3. Fehlt der Morph und der Import wurde ersetzt (`_lauf` → `None`): nichts wird gerechnet, nichts gelegt, nichts entfernt — der Bau läuft ohne Nachformung (mit Warnung im Bau).
4. Hat das Modell kein Unterkleid, entsteht keins; liefert die Rechnung keins („keine Haut vor der Kleidung"), fällt das des Imports trotzdem weg.
5. Nur Körper-Regler zählen: `…_scham`, `…_unterkleid`, `…_unterkleid_daz` und Regler ohne `eigen:` nicht.
6. `_lauf` gibt `None` (mit Warnung) ohne Import im Modell und bei einem Körper-Regler, der nicht der des letzten Laufs ist; sonst `(Lauf, Auftrag)`.
7. `_lochpunkte`: die Punkte im Loch ohne die auf dem Ring (Kunsthaut: 4 × 4 Zellen → 25 Punkte im Viereck, 16 auf dem Ring, 9 innen).
8. `Dazgeograftangepasst.modell_abgleichen`: das Modell bekommt die Regler des Baus, verliert die entfernten, die Datei sonst bleibt; ein zweiter Aufruf ändert nichts.
9. `modell_ableiten`: „cute girl Daz" wird frisch aus „cute girl" abgeleitet (Name, Daz-Stück statt Blender-Scham, sonst alles wie im Import); ein altes Ziel-Modell wird ersetzt, nicht gemischt, das Quell-Modell bleibt.

Sabotage (im Kopf, nicht gelaufen): `entfernen.append` streichen → Fall 1 und 4 rot; `not k.endswith(cls.ENDUNGEN)` zu `True` → Fall 5 rot; `innen[ring] = False` streichen → Fall 7 rot.
"""
import json
import logging
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase, override_settings

from core.dienste.dazgeograftangepasst import Dazgeograftangepasst
from core.dienste.dazgeograftnachformung import Dazgeograftnachformung as N

from ._nahtwelt import Nahtwelt
from ._pruefablage import Pruefablage

K = 'eigen:k'


def daten(regler, importkennung='2026.10.08.x'):
    return {'figur': {'regler': dict(regler), 'herkunft': {'import': importkennung} if importkennung else {}}}


class NachformungTest(SimpleTestCase):
    databases = set()

    def _sichern(self, regler, vorhanden, lauf=('lauf', 'job'), unter=K + '_unterkleid_daz', importkennung='2026.10.08.x'):
        """`(Ergebnis, nachformung-Mock, unterkleid-Mock)`: `vorhanden` = Namen der Morphe, die es gibt."""
        with mock.patch('Genesis9.eigenmorphe.G9eigenmorphe.vorhanden', side_effect=lambda name: name in vorhanden), \
                mock.patch.object(N, '_lauf', return_value=lauf), \
                mock.patch.object(N, '_nachformung', return_value=True) as nachformung, \
                mock.patch.object(N, '_unterkleid', return_value=unter) as unterkleid:
            return N.sichern(daten(regler, importkennung), 0.4), nachformung, unterkleid

    def test_1_nachformung_und_daz_unterkleid_kommen_dazu_das_des_imports_geht(self):
        (regler, entfernen), nachformung, unterkleid = self._sichern({K: 1.0, K + '_unterkleid': 1.0}, vorhanden={K + '_scham'})
        self.assertEqual(regler, {K + '_scham': 0.4, K + '_unterkleid_daz': 1.0})
        self.assertEqual(entfernen, [K + '_unterkleid'])
        nachformung.assert_not_called()
        # Dahinter folgen `loch_maske` und `name` (hier beide None, `_unterkleid(lauf, job, regler, zusatzregler, loch_maske, name)`).
        self.assertEqual(unterkleid.call_args[0][2:4], ({K: 1.0, K + '_unterkleid': 1.0}, {K + '_scham': 0.4}))

    def test_2_fehlt_der_scham_morph_wird_die_nachformung_gerechnet(self):
        (regler, entfernen), nachformung, _unterkleid = self._sichern({K: 1.0}, vorhanden=set())
        nachformung.assert_called_once_with('lauf', 'job')
        self.assertEqual(regler, {K + '_scham': 0.4})
        self.assertEqual(entfernen, [])

    def test_3_ist_der_import_ersetzt_wird_nichts_gerechnet_gelegt_oder_entfernt(self):
        ergebnis, nachformung, unterkleid = self._sichern({K: 1.0, K + '_unterkleid': 1.0}, vorhanden=set(), lauf=None)
        self.assertEqual(ergebnis, ({}, []))
        nachformung.assert_not_called()
        unterkleid.assert_not_called()

    def test_4_ohne_unterkleid_im_modell_keins_und_ohne_ergebnis_faellt_das_des_imports_weg(self):
        (regler, entfernen), _n, unterkleid = self._sichern({K: 1.0}, vorhanden={K + '_scham'})
        self.assertEqual((regler, entfernen), ({K + '_scham': 0.4}, []))
        unterkleid.assert_not_called()
        (regler, entfernen), _n, _u = self._sichern({K: 1.0, K + '_unterkleid': 1.0}, vorhanden={K + '_scham'}, unter=None)
        self.assertEqual((regler, entfernen), ({K + '_scham': 0.4}, [K + '_unterkleid']))

    def test_5_nur_koerper_regler_zaehlen(self):
        fremd = {K + '_scham': 0.4, K + '_unterkleid': 1.0, K + '_unterkleid_daz': 1.0, 'sch_hoehe': 0.5, 'x:y': 1.0}
        ergebnis, nachformung, unterkleid = self._sichern(fremd, vorhanden={K + '_scham'})
        self.assertEqual(ergebnis, ({}, []))
        nachformung.assert_not_called()
        unterkleid.assert_not_called()

    def test_6_lauf_verlangt_einen_import_und_den_koerper_regler_seines_letzten_laufs(self):
        with self.assertLogs('core', level=logging.WARNING):
            self.assertIsNone(N._lauf(None, K))
        job = mock.Mock()
        job.ergebnis = {'rest': {'regler': 'eigen:anderer'}}
        with mock.patch('core.dienste.blendimportlauf.Blendimportlauf') as lauf_klasse:
            lauf_klasse.return_value.job.return_value = job
            with self.assertLogs('core', level=logging.WARNING):
                self.assertIsNone(N._lauf('2026.10.08.x', K))
            job.ergebnis = {'rest': {'regler': K}}
            lauf, auftrag = N._lauf('2026.10.08.x', K)
        self.assertIs(lauf, lauf_klasse.return_value)
        self.assertIs(auftrag, job)

    def test_7_lochpunkte_sind_die_im_loch_ohne_den_ring(self):
        figur, loch = Nahtwelt.haut()
        maske = np.zeros(len(figur['dreiecke']), dtype=bool)
        maske[loch['dreiecke']] = True
        with mock.patch('core.dienste.dazgeografthaut.Dazgeografthaut.grundfigur', return_value=figur), \
                mock.patch('core.dienste.dazgeografthaut.Dazgeografthaut.loch', return_value=(maske, {})), \
                mock.patch('core.dienste.dazgeograftquelle.Dazgeograftquelle'):
            innen = N._lochpunkte({K: 1.0, K + '_unterkleid': 1.0})
        self.assertEqual(len(innen), len(figur['punkte']))
        self.assertEqual(int(innen.sum()), 9, '25 Punkte im Viereck, 16 davon auf dem Ring')
        self.assertFalse(innen[loch['ring_punkte']].any())
        self.assertLess(float(np.abs(figur['punkte'][innen][:, :2]).max()), 0.020)

    def test_7b_mit_dem_loch_des_blender_stuecks_zaehlt_dessen_haut_und_das_loch_des_geografts_nicht(self):
        figur, loch = Nahtwelt.haut()
        maske = np.zeros(len(figur['dreiecke']), dtype=bool)
        maske[loch['dreiecke']] = True
        with mock.patch('core.dienste.dazgeografthaut.Dazgeografthaut.grundfigur', return_value=figur), \
                mock.patch('core.dienste.dazgeografthaut.Dazgeografthaut.loch') as geograft_loch:
            innen = N._lochpunkte({K: 1.0}, maske)
        geograft_loch.assert_not_called()
        self.assertEqual(int(innen.sum()), 9, 'dieselbe Haut wie mit dem Loch des Geografts, wenn die Löcher gleich sind')
        self.assertTrue(N.ist_zusatz(K + '_unterkleid_umriss'), 'der Morph zum Loch des Blender-Stücks ist kein Körper-Regler')
        self.assertTrue(N.ist_zusatz(K + '_unterkleid_umriss_cute_girl_alt2_scham'), 'auch mit dem Namen eines fremden Umrisses (UMRISS_VON) nicht')
        self.assertFalse(N.ist_zusatz(K), 'der Körper-Regler selbst schon')

    def test_7c_ein_fremder_umriss_legt_den_morph_unter_eigenem_namen_ab(self):
        """Am 11.10.2026 überschrieb „cute girl daz2" (Loch von alt2) den Morph `…_unterkleid_umriss` von „Daz3": der Name des Umrisses gehört an den Morph."""
        with mock.patch.object(N, '_unterkleid', return_value='x') as unterkleid, \
                mock.patch.object(N, '_lauf', return_value=('lauf', 'job')), \
                mock.patch('Genesis9.eigenmorphe.G9eigenmorphe.vorhanden', return_value=True):
            N.sichern({'figur': {'regler': {K: 1.0, K + '_unterkleid': 1.0}, 'herkunft': {'import': 'i'}}}, 0.4, np.zeros(3, dtype=bool), 'cute_girl_alt2_scham')
        self.assertEqual(unterkleid.call_args.args[-1], 'cute_girl_alt2_scham')


class ModellAbgleichTest(SimpleTestCase):
    databases = set()

    def test_8_das_modell_bekommt_die_regler_verliert_die_entfernten_und_bleibt_sonst(self):
        bau = Dazgeograftangepasst.__new__(Dazgeograftangepasst)
        bau.nachformung, bau.entfernen = {K + '_scham': 0.4, K + '_unterkleid_daz': 1.0}, [K + '_unterkleid']
        with Pruefablage.ordner('nachformung_') as ordner, override_settings(HUMANBODY_MODELS_DIR=Path(ordner)):
            pfad = Path(ordner) / 'm.json'
            pfad.write_text(json.dumps({'name': 'm', 'figur': {'regler': {K: 1.0, K + '_unterkleid': 1.0, 'andere': 0.3}, 'haut': 'bleibt'}}), encoding='utf-8')
            geaendert = bau.modell_abgleichen('m')
            gelesen = json.loads(pfad.read_text(encoding='utf-8'))
            self.assertEqual(geaendert, {K + '_scham': 0.4, K + '_unterkleid_daz': 1.0, K + '_unterkleid': None})
            self.assertEqual(gelesen['figur']['regler'], {K: 1.0, 'andere': 0.3, K + '_scham': 0.4, K + '_unterkleid_daz': 1.0})
            self.assertEqual((gelesen['name'], gelesen['figur']['haut']), ('m', 'bleibt'))
            self.assertEqual(bau.modell_abgleichen('m'), {}, 'ein zweiter Aufruf ändert nichts')
            self.assertEqual(bau.modell_abgleichen('gibt_es_nicht'), {})

    def test_9_das_ziel_modell_wird_aus_dem_modell_des_imports_abgeleitet(self):
        bau = Dazgeograftangepasst.__new__(Dazgeograftangepasst)
        bau.modell, bau.scham, bau.anzeige = 'm', 'm Scham', 'm Daz Scham'
        eintrag = {'variante': 'v', 'regler': {'a': 1}}
        quelle = {'name': 'm', 'quelle': 'genesis9', 'figur': {'regler': {K: 1.0}, 'kleidung': {'m_scham': eintrag, 'm_haar': {'stil': 's'}}, 'fototextur': {'1001': 'x?v=2'}}}
        with Pruefablage.ordner('ableiten_') as ordner, override_settings(HUMANBODY_MODELS_DIR=Path(ordner)):
            (Path(ordner) / 'm.json').write_text(json.dumps(quelle), encoding='utf-8')
            (Path(ordner) / 'm Daz.json').write_text(json.dumps({'name': 'm Daz', 'figur': {'alt': True}}), encoding='utf-8')
            self.assertTrue(bau.modell_ableiten('m Daz'))
            abgeleitet = json.loads((Path(ordner) / 'm Daz.json').read_text(encoding='utf-8'))
            self.assertEqual(abgeleitet['name'], 'm Daz')
            self.assertEqual(sorted(abgeleitet['figur']['kleidung']), ['m_daz_scham', 'm_haar'], 'das Blender-Scham-Stück ist durch das Daz-Stück ersetzt')
            self.assertEqual(abgeleitet['figur']['kleidung']['m_daz_scham'], eintrag)
            self.assertEqual(abgeleitet['figur']['herkunft'], {'daz_stuecke': ['m_daz_scham']}, 'das Stück gehört dem Modell: mit ihm geht es in den Papierkorb (`Modellstuecke`)')
            self.assertEqual((abgeleitet['figur']['regler'], abgeleitet['figur']['fototextur']), (quelle['figur']['regler'], quelle['figur']['fototextur']))
            self.assertNotIn('alt', abgeleitet['figur'], 'das alte Ziel-Modell ist ersetzt, nicht gemischt')
            self.assertEqual(json.loads((Path(ordner) / 'm.json').read_text(encoding='utf-8')), quelle, 'das Modell des Imports bleibt unberührt')
