# -*- coding: utf-8 -*-
u"""`G9charakterapply` und `G9charakterpresets` an Kunstdaten (18.11.2026).

Apply-Name, gesteuerte Morphs, Morphordner, Presettyp. Sabotage: `_mit_gesteuerten` ohne zweite Stufe
→ `test_zwei_stufen` rot; `_TYP` nur `character` → `test_scene_subset_ist_preset` rot.
"""
import gzip
import tempfile
from pathlib import Path

from django.test import SimpleTestCase
from Genesis9.charakterapply import G9charakterapply
from Genesis9.charakterpresets import G9charakterpresets


def _formel(ziel, *quellen):
    ops = [{'op': 'push', 'kanal': q} for q in quellen]
    return {'ziel': ['morph', ziel, 'value'], 'stufe': 'sum', 'ops': ops}


class CharakterapplyTest(SimpleTestCase):
    def test_apply_name(self):
        self.assertEqual(G9charakterapply.APPLY.match('Seratin Body Apply').group(1), 'Seratin')
        self.assertEqual(G9charakterapply.APPLY.match('Damira - Head Apply').group(1), 'Damira -')
        self.assertIsNone(G9charakterapply.APPLY.match('Seratin Body Remove'))

    def test_zwei_stufen(self):
        kanaele = {'ctrl': {'formeln': [_formel('koerper', 'ctrl')]},
                   'koerper': {'formeln': [_formel('detail', 'koerper')]},
                   'fremd': {'formeln': [_formel('anderes', 'niemand')]}}
        self.assertEqual(G9charakterapply._mit_gesteuerten({'ctrl'}, kanaele), {'ctrl', 'koerper', 'detail'})

    def test_morphordner(self):
        kanaele = {'a': {'datei': 'P3Design\\Ursula\\P3DUrsula_body_bs_Body_HD4.dsf'},
                   'b': {'datei': 'lose.dsf'}}
        self.assertEqual(G9charakterapply._morphordner('a', kanaele), 'p3design/ursula')
        self.assertEqual(G9charakterapply._morphordner('b', kanaele), '')
        self.assertEqual(G9charakterapply._morphordner('fehlt', kanaele), '')

    def test_scene_subset_ist_preset(self):
        with tempfile.TemporaryDirectory(dir=r'A:\3DTools\ProjektTemp') as ordner:
            pfade = {}
            for typ in ('character', 'scene_subset', 'preset_material'):
                pfade[typ] = Path(ordner) / ('%s.duf' % typ)
                with gzip.open(pfade[typ], 'wb') as datei:
                    datei.write(('{"asset_info": {"type": "%s"}}' % typ).encode('utf-8'))
            self.assertTrue(G9charakterpresets.ist_preset(pfade['character']))
            self.assertTrue(G9charakterpresets.ist_preset(pfade['scene_subset']))
            self.assertFalse(G9charakterpresets.ist_preset(pfade['preset_material']))
