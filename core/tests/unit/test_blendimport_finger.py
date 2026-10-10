# -*- coding: utf-8 -*-
u"""Blender-Import: die Finger der Figur an die Hände des Originals anpassen (Schritt „finger", 10.10.2026, Rosemary Winters).

Edgar: „Texturprobleme bei der Hand, und die Waffe geht durch die Hand hindurch". Die Figur hatte immer die gestreckte Ruhehand; das Original greift.
`Blendimportfinger` legt die Winkel (`finger.json`) und die Käfigkorrektur (`finger_kaefig.npz`) neben `posiert.npy`; ohne beide ändert sich nichts.

1. `_probe`: die Winkel gelten nur, wenn Median UND p90 in der RUHELAGE unter `RUHE_VORTEIL` × vorher liegen (das Maß, das Backen und Entposen
   entscheidet); ein besserer Median allein (linke Hand von Rosemary, falsche Faust) genügt nicht.
2. `_ablegen` + `kaefig`: ein Punkt, den beide Hände bewegen, bekommt die SUMME; ohne angenommene Hand wird eine alte Käfigdatei entfernt.
3. `haltung` und `griff` lesen nur angenommene Seiten; `griff('r_hand')` ist die rechte Hand, ein Nicht-Hand-Teil bekommt keinen.
4. `requisit_griff` schreibt den Griff in die `.ersetzt.json` des Requisits (auch leer — sonst bliebe der Griff eines früheren Laufs stehen), nur für Hände.
5. Ohne Datei: `kaefig` None, `haltung` und `griff` leer (Imports vor dem 10.10.2026).
6. `Blendimportlauf`: der Schritt „finger" steht hinter „figur", und sein Band schließt lückenlos an.

Sabotage: `RUHE_VORTEIL` auf 2.0 → Fall 1 rot; in `_ablegen` die Summe durch Überschreiben ersetzen → Fall 2 rot; in `griff` die Prüfung `uebernommen`
streichen → Fall 3 rot; in `requisit_griff` `schreiben` nur bei nicht leerem Griff → Fall 4 rot. Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportfinger import Blendimportfinger as F
from core.dienste.blendimportlauf import Blendimportlauf


class Ablage(object):
    u"""Eine Ablage wie `Meshfigurablage`: `arbeit(name)` gibt einen Pfad im Ordner."""

    def __init__(self, ordner):
        self.ordner = Path(ordner)

    def arbeit(self, name):
        return self.ordner / name


class Finger(F):
    u"""Ohne Auftrag und Django-Modell: nur Ablage und Bericht."""

    def __init__(self, ablage):
        self.ablage = mock.Mock(kennung='test')
        self._ablage = ablage

    def job_ablage(self):
        return self._ablage


GRIFF_R = {'r_index1': {'rotation/z': 80.0}, 'r_thumb1': {'rotation/y': 30.0}}
GRIFF_L = {'l_index1': {'rotation/z': -70.0}}


class FingerProbe(SimpleTestCase):

    def test_1_die_winkel_gelten_nur_bei_klarem_gewinn_in_ruhe(self):
        f = F.__new__(F)
        vorher = np.full(200, 9.0)
        gut = f._probe(vorher, np.full(200, 3.0))
        gleich = f._probe(vorher, np.full(200, 8.5))
        schlechter = f._probe(vorher, np.full(200, 12.0))
        self.assertTrue(gut['gilt'], gut)
        self.assertFalse(gleich['gilt'], gleich)
        self.assertFalse(schlechter['gilt'], schlechter)
        self.assertEqual((gut['vorher_median_mm'], gut['nachher_median_mm']), (9.0, 3.0))

    def test_1b_ein_besserer_median_ohne_besseren_rand_gilt_nicht(self):
        u"""Die linke Hand von Rosemary: Median 0,71, p90 0,89 des Früheren — die Faust war falsch."""
        f = F.__new__(F)
        vorher = np.concatenate([np.full(180, 4.0), np.full(20, 11.5)])
        nachher = np.concatenate([np.full(180, 2.8), np.full(20, 10.3)])
        probe = f._probe(vorher, nachher)
        self.assertLess(probe['nachher_median_mm'], F.RUHE_VORTEIL * probe['vorher_median_mm'])
        self.assertFalse(probe['gilt'], probe)


class FingerAblage(SimpleTestCase):

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.addCleanup(self.ordner.cleanup)
        self.ablage = Ablage(self.ordner.name)
        self.f = Finger(self.ablage)

    def _schreiben(self, bericht, idx, delta):
        self.f._ablegen(bericht, idx, delta)

    def test_2_ein_punkt_beider_haende_bekommt_die_summe(self):
        bericht = {'r': {'uebernommen': True, 'griff': GRIFF_R}, 'l': {'uebernommen': True, 'griff': GRIFF_L}}
        self._schreiben(bericht, [np.array([3, 5]), np.array([5, 9])],
                        [np.array([[1.0, 0, 0], [0, 2.0, 0]]), np.array([[0, 1.0, 0], [0, 0, 4.0]])])
        idx, delta = F.kaefig(self.ablage)
        self.assertEqual(list(idx), [3, 5, 9])
        self.assertTrue(np.allclose(delta[1], [0.0, 3.0, 0.0]), delta)      # der Punkt 5: (0,2,0) + (0,1,0)

    def test_2b_ohne_angenommene_hand_verschwindet_eine_alte_kaefigdatei(self):
        self._schreiben({'r': {'uebernommen': True, 'griff': GRIFF_R}}, [np.array([1])], [np.array([[0.0, 0.0, 1.0]])])
        self.assertIsNotNone(F.kaefig(self.ablage))
        self._schreiben({'r': {'uebernommen': False, 'griff': {}}}, [], [])
        self.assertIsNone(F.kaefig(self.ablage))
        self.assertEqual(F.haltung(self.ablage), {})

    def test_3_haltung_und_griff_lesen_nur_angenommene_seiten(self):
        bericht = {'r': {'uebernommen': True, 'griff': GRIFF_R}, 'l': {'uebernommen': False, 'griff': GRIFF_L}}
        self._schreiben(bericht, [np.array([1])], [np.array([[0.0, 0.0, 1.0]])])
        self.assertEqual(F.haltung(self.ablage), GRIFF_R)
        self.assertEqual(F.griff(self.ablage, 'r_hand'), GRIFF_R)
        self.assertEqual(F.griff(self.ablage, 'l_hand'), {})
        self.assertEqual(F.griff(self.ablage, 'r_thigh'), {})

    def test_4_das_requisit_bekommt_den_griff_auch_leer_und_nur_an_der_hand(self):
        bericht = {'r': {'uebernommen': True, 'griff': GRIFF_R}}
        self._schreiben(bericht, [np.array([1])], [np.array([[0.0, 0.0, 1.0]])])
        with mock.patch('Genesis9.stueckersatz.G9stueckersatz.schreiben') as schreiben:
            self.assertEqual(F.requisit_griff(self.ablage, 'katana.duf', 'r_hand'), {'seite': 'r', 'knochen': 2})
            schreiben.assert_called_once_with('katana.duf', [], griff=GRIFF_R)
        with mock.patch('Genesis9.stueckersatz.G9stueckersatz.schreiben') as schreiben:
            self.assertEqual(F.requisit_griff(self.ablage, 'katana.duf', 'l_hand'), {'seite': 'l', 'knochen': 0})
            schreiben.assert_called_once_with('katana.duf', [], griff=None)       # leer: ein alter Griff wird überschrieben
        with mock.patch('Genesis9.stueckersatz.G9stueckersatz.schreiben') as schreiben:
            self.assertIsNone(F.requisit_griff(self.ablage, 'helm.duf', 'head'))
            schreiben.assert_not_called()

    def test_5_ohne_dateien_aendert_sich_nichts(self):
        self.assertIsNone(F.kaefig(self.ablage))
        self.assertEqual(F.haltung(self.ablage), {})
        self.assertEqual(F.griff(self.ablage, 'r_hand'), {})
        (Path(self.ordner.name) / F.DATEI).write_text('kaputt', encoding='utf-8')
        self.assertEqual(F.haltung(self.ablage), {})
        (Path(self.ordner.name) / F.DATEI).write_text(json.dumps([1, 2]), encoding='utf-8')
        self.assertEqual(F.haltung(self.ablage), {})


class FingerSchritt(SimpleTestCase):

    def test_6_der_schritt_steht_hinter_der_figur_und_das_band_ist_lueckenlos(self):
        schritte = list(Blendimportlauf.SCHRITTE)
        self.assertEqual(schritte[schritte.index('figur') + 1], 'finger')
        von, bis = Blendimportlauf.BAENDER['figur'][1], Blendimportlauf.BAENDER['finger'][0]
        self.assertEqual(von, bis)
