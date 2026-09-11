# -*- coding: utf-8 -*-
u"""Der Einzelbau baut ueber die getragenen Stuecke (11.09.2026).

Edgar: „kannst du das normale Bauen mit garmentCode nicht umstellen, dass
es auch die aktuell vorhandenen GarmentCode beruecksichtigt, und dann die
neuen Garments UEBER den alten baut, falls sie ueber dem Koerper liegen?"

Die Simulation kennt einen Kollisionskoerper; `Koerpermitstoff` haengt die
getragenen Stuecke an ihn an (`Assets/GarmentCode/koerpermitstoff.py`).
Gemessen (`ProjektTemp/ueber_getragene_probe.py`, T-Shirt ueber einer
weiten Hose): Hose in 7 von 160 Faechern aussen (10,2 mm) ohne, 0 von 164
(0,6 mm) mit dem erweiterten Koerper.

Was hier haelt — je Fall eine Sabotage macht ihn rot:

1. Die Stoffpunkte haengen HINTER den Koerperpunkten, die Dreiecke sind
   versetzt, Vierecke des Koerpers werden geteilt.
2. Jeder Stoffpunkt bekommt die Segmente seines naechsten Koerperpunkts —
   sonst zaehlt er bei `panel_assignment` nicht.
3. Stoff unter der Sohle wird geklemmt (`garment.py` hebt sonst alles an).
4. Der Fingerabdruck haengt am Stoff: dieselbe Figur mit anderem Stueck
   bekommt einen anderen Ordner (`artefakte-benennen`).
5. Der Endpunkt nimmt nur `*_rig.json` unterhalb des Ausgabeordners.
6. Der Browser schickt die getragenen Stuecke ohne das, das neu entsteht,
   und nur mit gesetztem Haekchen.
"""
import io
import json
import os
import tempfile

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from GarmentCode.koerpermitstoff import Koerpermitstoff
from core.api.garmentcode import Garmentcode


def _lies(*teile):
    return io.open(settings.BASE_DIR.joinpath(*teile), encoding='utf-8').read()


class _Koerper:
    u"""Vier Punkte als Viereck: zwei links (x -1), zwei rechts (x +1)."""
    punkte = np.array([[-1.0, 0.0, 0.0], [-1.0, 0.0, 1.0],
                       [1.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
    flaechen = [[0, 1, 2, 3]]
    segmente = {'left_leg': [0, 1], 'right_leg': [2, 3], 'body': [1, 2]}


class VereinenTest(SimpleTestCase):

    databases = []

    def _mit(self, stoff, dreiecke=((0, 1, 2),)):
        k = Koerpermitstoff('female', _Koerper.punkte, _Koerper.flaechen,
                            _Koerper.segmente)
        ordner = tempfile.mkdtemp(dir=str(settings.BASE_DIR / 'logs'))
        pfad = os.path.join(ordner, 'x_rig.json')
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump({'punkte': stoff, 'dreiecke': [list(d) for d in dreiecke]}, datei)
        self.assertTrue(k.aufnehmen(pfad))
        os.remove(pfad)
        os.rmdir(ordner)
        return k

    def test_stoff_haengt_hinter_dem_koerper_und_vierecke_werden_geteilt(self):
        k = self._mit([[-1.0, 0.0, 0.5], [-0.9, 0.0, 0.5], [-1.0, 0.0, 0.6]])
        punkte, flaechen, _ = k.vereint()
        self.assertEqual(len(punkte), 7)
        # Das Viereck ist zwei Dreiecke, das Stoffdreieck um 4 versetzt.
        self.assertEqual(flaechen, [[0, 1, 2], [0, 2, 3], [4, 5, 6]])

    def test_jeder_stoffpunkt_bekommt_die_segmente_seines_nachbarn(self):
        k = self._mit([[-1.0, 0.0, 0.5], [1.0, 0.0, 0.9], [0.0, 0.0, 1.0]])
        _, _, segmente = k.vereint()
        # Punkt 4 liegt am linken Bein, Punkt 5 rechts oben (right_leg UND
        # body), Punkt 6 mittig oben — naechster ist 1 oder 2, beide `body`.
        self.assertIn(4, segmente['left_leg'])
        self.assertNotIn(4, segmente['right_leg'])
        self.assertIn(5, segmente['right_leg'])
        self.assertIn(5, segmente['body'])
        self.assertIn(6, segmente['body'])
        # Die Koerperpunkte bleiben, wie sie waren.
        self.assertEqual(segmente['left_leg'][:2], [0, 1])

    def test_stoff_unter_der_sohle_wird_geklemmt(self):
        k = self._mit([[0.0, 0.0, -0.046], [0.1, 0.0, 0.0], [0.0, 0.1, 0.2]])
        punkte, _, _ = k.vereint()
        self.assertGreaterEqual(punkte[:, 2].min(), 0.0)
        self.assertEqual(punkte[4][2], 0.0)
        self.assertEqual(punkte[6][2], 0.2)

    def test_der_fingerabdruck_haengt_am_stoff(self):
        a = self._mit([[0.0, 0.0, 0.5], [0.1, 0.0, 0.5], [0.0, 0.1, 0.5]])
        b = self._mit([[0.0, 0.0, 0.6], [0.1, 0.0, 0.6], [0.0, 0.1, 0.6]])
        self.assertNotEqual(a.name(), b.name())
        self.assertNotEqual(a.ordner('w'), b.ordner('w'))
        self.assertTrue(os.path.basename(a.ordner('w')).startswith('female_mit_'))

    def test_ein_rig_ohne_netz_wird_uebergangen(self):
        k = Koerpermitstoff('female', _Koerper.punkte, _Koerper.flaechen, {})
        ordner = tempfile.mkdtemp(dir=str(settings.BASE_DIR / 'logs'))
        pfad = os.path.join(ordner, 'leer_rig.json')
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump({'punkte': [], 'dreiecke': []}, datei)
        try:
            self.assertFalse(k.aufnehmen(pfad))
            self.assertTrue(k.leer)
        finally:
            os.remove(pfad)
            os.rmdir(ordner)


class EndpunktTest(SimpleTestCase):

    databases = []

    def test_nur_rig_dateien_unterhalb_des_ausgabeordners(self):
        from GarmentCode.entwurf import Entwurf
        wurzel = os.path.abspath(Entwurf.AUSGABE)
        ordner = tempfile.mkdtemp(dir=wurzel, prefix='probe_test_')
        pfad = os.path.join(ordner, 'x_sim_rig.json')
        with open(pfad, 'w', encoding='utf-8') as datei:
            datei.write('{}')
        try:
            name = os.path.basename(ordner)
            roh = json.dumps([
                {'ordner': name, 'rig_datei': 'x_sim_rig.json'},          # ja
                {'ordner': name, 'rig_datei': 'x_sim.obj'},               # kein rig
                {'ordner': '..', 'rig_datei': 'x_sim_rig.json'},          # Ausbruch
                {'ordner': name, 'rig_datei': 'fehlt_rig.json'},          # gibt es nicht
                'muell'])
            self.assertEqual(Garmentcode.getragene(roh), [pfad])
            self.assertEqual(Garmentcode.getragene('kein json'), [])
            self.assertEqual(Garmentcode.getragene(None), [])
        finally:
            os.remove(pfad)
            os.rmdir(ordner)

    def test_der_drapier_endpunkt_reicht_getragene_durch(self):
        quelle = _lies('core', 'api', 'garmentcode.py')
        stelle = quelle.index('def drapieren(request)')
        block = quelle[stelle:quelle.index('def getragene', stelle)]
        self.assertIn("Garmentcode.getragene(request.POST.get('getragen'))", block)
        self.assertIn('getragen=getragen)', block)


class BrowserTest(SimpleTestCase):

    databases = []

    def test_der_browser_schickt_die_getragenen_ohne_das_neue(self):
        drapieren = _lies('static', 'viewer', 'scene', 'garmentcode_drapieren.js')
        self.assertIn("document.getElementById('gc-ueber-getragene')?.checked !== false",
                      drapieren)
        self.assertIn('GarmentcodeAblage.getragen(figur?.inst || figur, stueck)', drapieren)
        ablage = _lies('static', 'viewer', 'scene', 'garmentcode_ablage.js')
        stelle = ablage.index('static getragen(inst, ausser = null)')
        block = ablage[stelle:ablage.index('static vergessen', stelle)]
        self.assertIn('GarmentcodeAnziehen.schluessel(ausser)) continue', block)
        self.assertIn('rig_datei: datei', block)
        vorlage = _lies('templates', '_garmentcode_panel.html')
        self.assertIn('id="gc-ueber-getragene" checked', vorlage)
