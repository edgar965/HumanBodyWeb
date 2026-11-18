# -*- coding: utf-8 -*-
"""Drei Fehler, die erst die Genesis-8-Stücke kaos Pajamas2 und KomyFly Barbossa zeigten (18.11.2026, Edgar: „fixe das: pajamas2, pajamas2ex und die
vier Barbossa-Teile … Daz-Datei fehlt #default“).

1. `G9dson.aus_url('#default', doc)`: eine Adresse ohne Pfad zeigt in das Dokument, in dem sie steht — die sechs Stücke tragen Geometrie und UV-Satz in der
   .duf selbst. Ohne `doc` bleibt es „Daz-Datei fehlt“.
2. `G9autofit.fusspose`: eine Pose, die nur Fuß und Zehen dreht (Bardot `!FootPose`), ist eine Fußpose; eine, die auch Beine und Becken dreht (kaos
   `Poses/X Morph Pose.duf`), nicht — sonst stand die Figur mit gebeugtem Bein in der Hose.
3. `G9stoffentspannung._bau`: die Kanten werden mit `torch.sort(…, dim=1, stable=True)` geordnet (positional `1` mit `stable` warf TypeError: 500 für jedes
   Stück unter einer Haltung). Braucht die Grafikkarte.

Kunstdaten, keine Bibliothek. Nicht gelaufen — Tests laufen nur auf Ansage.
Sabotage: in `aus_url` die Zeile mit `doc` weglassen → Fall 1 rot; in `fusspose` wieder `any(… NAMEN …)` → Fall 2b rot; `dim=1` wieder positional → Fall 3 rot.
"""
import json
import tempfile
import unittest
from pathlib import Path

import torch
from django.test import SimpleTestCase
from Genesis9.autofit import G9autofit
from Genesis9.dson import G9dson


def pose(knochen):
    """Ein `preset_pose`-Dokument, das jeden Knochen um 10° um x dreht (Form wie Bardot `!FootPose.duf`)."""
    return {'asset_info': {'type': 'preset_pose'},
            'scene': {'animations': [{'url': '%s:/data/DAZ%%203D/Genesis%%208/Female/Genesis8Female.dsf#%s?rotation/x/value' % (k, k), 'keys': [[0, 10.0]]}
                                     for k in knochen]}}


class LokaleAdresseTest(SimpleTestCase):

    def test_1_raute_zeigt_ins_eigene_dokument(self):
        doc = G9dson('stueck.duf', {'uv_set_library': [{'id': 'default', 'uvs': {'values': [[0, 0]]}}]})
        gefunden, kennung = G9dson.aus_url('#default', doc)
        self.assertIs(gefunden, doc)
        self.assertEqual(kennung, 'default')
        with self.assertRaises(FileNotFoundError):
            G9dson.aus_url('#default')


class FussposeTest(SimpleTestCase):

    def _ordner(self, posen):
        tmp = Path(tempfile.mkdtemp(prefix='g9_fusspose_'))
        (tmp / 'Stueck.duf').write_text('{}', encoding='utf-8')
        for name, knochen in posen.items():
            (tmp / name).parent.mkdir(parents=True, exist_ok=True)
            (tmp / name).write_text(json.dumps(pose(knochen)), encoding='utf-8')
        return tmp / 'Stueck.duf'

    def test_2a_nur_fuss_und_zehen(self):
        datei = self._ordner({'!FootPose.duf': ['lFoot', 'lToe', 'rFoot', 'rBigToe', 'rSmallToe4']})
        self.assertEqual(G9autofit.fusspose(datei), '!FootPose.duf')

    def test_2b_figurpose_ist_keine_fusspose(self):
        datei = self._ordner({'Poses/X Morph Pose.duf': ['pelvis', 'lThighBend', 'lShin', 'lFoot', 'rFoot']})
        self.assertIsNone(G9autofit.fusspose(datei))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class StoffentspannungTest(SimpleTestCase):

    def test_3_bau_mit_stabiler_sortierung(self):
        from Genesis9.stoffentspannung import G9stoffentspannung

        class Folger:
            name = 'test_stoffentspannung'
            polys = [[0, 0, 0, 1, 2, 3], [0, 0, 1, 4, 5, 2]]            # zwei Vierecke (Gruppe, Material, Punkte)

            @staticmethod
            def projektionsabstand():
                return torch.tensor([0.0, 0.0, 0.5, 0.5, 0.5, 0.5], dtype=torch.float64, device='cuda')

        bau = G9stoffentspannung._bau(Folger(), 6)
        self.assertIsNotNone(bau)
        i, j = bau[0], bau[1]
        self.assertEqual(len(i), 7)                                     # 8 Kanten, die gemeinsame (1, 2) einmal
        self.assertTrue(bool((i < j).all()))
