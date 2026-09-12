# -*- coding: utf-8 -*-
u"""`pants.rise` setzt den Bund wirklich tiefer (11.09.2026).

Edgar, mit Bild: „ich habe die Bundhoehe der Leggins schon beim Minimum,
trotzdem ist der Bund noch so hoch!" Der Upstream haelt die Bundoberkante
in der Simulation an `_waist_level` fest (`garment.py`, `lower_interface`),
gleich was `rise` sagt. `bundhoehe.py` senkt den Schnitt UND die
Anlagehoehe um `(1 - min(rise + bundbreite, 1)) * hips_line`.
"""
import io
import json
import os

import yaml
from django.conf import settings
from django.test import SimpleTestCase

from ._pruefablage import Pruefablage

from GarmentCode.bundhoehe import Bundhoehe
from GarmentCode.bundmaske import Bundmaske
from GarmentCode.schnittvorschau import Schnittvorschau

HIPS_LINE = 25.0


def _entwurf(upper=None, wb='StraightWB', bottom='Pants', breite=0.232):
    return {'meta': {'upper': {'v': upper}, 'wb': {'v': wb}, 'bottom': {'v': bottom}},
            'waistband': {'width': {'v': breite}}}


class _Unterteil:
    def __init__(self, rise):
        self._rise = rise

    def get_rise(self):
        return self._rise


class _Stueck:
    def __init__(self, *subs):
        self.subs = list(subs)


def _rechteck(tx, ty, tz, breite, hoehe):
    return {'translation': [tx, ty, tz], 'rotation': [0, 0, 0],
            'vertices': [[0, 0], [breite, 0], [breite, hoehe], [0, hoehe]],
            'edges': [{'endpoints': [0, 1]}, {'endpoints': [1, 2]},
                      {'endpoints': [2, 3]}, {'endpoints': [3, 0]}]}


def _spezifikation():
    u"""Wie Edgars Hose: Bund 104,9..110,6, Hose bis 99,9 (5 cm Luecke)."""
    muster = {
        'panels': {'pant_f_r': _rechteck(-20, 11, 25, 20, 88.9),
                   'wb_front': _rechteck(-18, 104.9, 20, 36, 5.8)},
        'panel_order': ['pant_f_r', 'wb_front'],
        'stitches': [[{'panel': 'wb_front', 'edge': 0},
                      {'panel': 'pant_f_r', 'edge': 2}]]}
    return {'pattern': muster, 'parameters': {}, 'parameter_order': [],
            'properties': {}}


class VersatzTest(SimpleTestCase):

    databases = set()

    def test_rise_eins_aendert_nichts(self):
        self.assertEqual(Bundhoehe.versatz_cm(_entwurf(), 1.0, HIPS_LINE), 0.0)

    def test_halber_rise_mit_bund(self):
        # Bundoberkante gehoert auf rise + Bundbreite = 0,732 der Hueftlinie
        self.assertAlmostEqual(Bundhoehe.versatz_cm(_entwurf(), 0.5, HIPS_LINE),
                               (1 - 0.732) * 25, places=6)

    def test_halber_rise_ohne_bund(self):
        self.assertAlmostEqual(Bundhoehe.versatz_cm(_entwurf(wb=None), 0.5, HIPS_LINE),
                               12.5, places=6)

    def test_mit_oberteil_bleibt_der_upstream(self):
        u"""Kleid: der Bund haengt am Oberteil — nicht senken."""
        self.assertEqual(Bundhoehe.versatz_cm(_entwurf(upper='FittedShirt'),
                                              0.5, HIPS_LINE), 0.0)

    def test_ohne_unterteil_kein_versatz(self):
        self.assertEqual(Bundhoehe.versatz_cm(_entwurf(), None, HIPS_LINE), 0.0)
        self.assertIsNone(Bundhoehe.rise_von(_Stueck(_Unterteil(0.5)),
                                             _entwurf(bottom=None)))

    def test_der_rise_kommt_vom_letzten_baustein(self):
        self.assertEqual(Bundhoehe.rise_von(_Stueck(_Unterteil(0.6)), _entwurf()), 0.6)
        self.assertIsNone(Bundhoehe.rise_von(_Stueck(), _entwurf()))


class DateienTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.ordner = self.enterContext(Pruefablage.ordner('bundhoehe_'))
        self.spez = os.path.join(self.ordner, 'probe_specification.json')
        with io.open(self.spez, 'w', encoding='utf-8') as datei:
            json.dump(_spezifikation(), datei)
        self.koerper = os.path.join(self.ordner, 'figur.yaml')
        with io.open(self.koerper, 'w', encoding='utf-8') as datei:
            yaml.safe_dump({'body': {'height': 168.0, 'head_l': 25.8,
                                     'waist_line': 32.3, 'hips_line': HIPS_LINE}},
                           datei)

    def test_senken_verschiebt_alle_panels_und_vermerkt(self):
        Bundhoehe.senken(self.spez, 6.7, rise=0.5)
        spez = json.load(io.open(self.spez, encoding='utf-8'))
        panels = spez['pattern']['panels']
        self.assertAlmostEqual(panels['wb_front']['translation'][1], 104.9 - 6.7, places=6)
        self.assertAlmostEqual(panels['pant_f_r']['translation'][1], 11 - 6.7, places=6)
        self.assertEqual(panels['wb_front']['translation'][0], -18)   # x, z bleiben
        self.assertEqual(Bundhoehe.vermerk(self.spez), {'versatz_cm': 6.7, 'rise': 0.5})
        # und die 2D-Vorschau sieht den gesenkten Bund (plus Bundlage auf die Hose)
        netz = Schnittvorschau(spez).netz(bund_senken=True)
        bund = netz['punkte'][netz['panels'][1]['ab']:, 1]
        self.assertAlmostEqual(float(bund.min()), (99.9 - 6.7) / 100, places=4)

    def test_anwenden_senkt_die_spezifikation_im_ordner(self):
        koerper = {'hips_line': HIPS_LINE}
        versatz = Bundhoehe.anwenden(self.ordner, _entwurf(),
                                     _Stueck(_Unterteil(0.5)), koerper)
        self.assertAlmostEqual(versatz, 6.7, places=6)
        self.assertAlmostEqual(Bundhoehe.vermerk(self.spez)['versatz_cm'], 6.7, places=3)
        # rise 1: nichts angefasst
        with io.open(self.spez, 'w', encoding='utf-8') as datei:
            json.dump(_spezifikation(), datei)
        self.assertEqual(Bundhoehe.anwenden(self.ordner, _entwurf(),
                                            _Stueck(_Unterteil(1.0)), koerper), 0.0)
        self.assertEqual(Bundhoehe.vermerk(self.spez), {})

    def test_die_koerperdatei_der_simulation_traegt_die_anlagehoehe(self):
        # ohne Vermerk: die Datei des Koerperordners selbst
        self.assertEqual(Bundhoehe.koerperdatei(self.spez, self.koerper), self.koerper)
        Bundhoehe.senken(self.spez, 6.7, rise=0.5)
        ziel = Bundhoehe.koerperdatei(self.spez, self.koerper)
        self.assertEqual(os.path.basename(str(ziel)), 'probe_koerper_anlage.yaml')
        self.assertEqual(os.path.dirname(str(ziel)), self.ordner)
        werte = yaml.safe_load(io.open(str(ziel), encoding='utf-8'))['body']
        # wie garment.py rechnet: height - head_l - waist_line = 109,9
        self.assertAlmostEqual(werte['_waist_level'], 109.9 - 6.7, places=6)
        self.assertAlmostEqual(werte['_bund_versatz'], 6.7, places=6)
        self.assertEqual(werte['hips_line'], HIPS_LINE)
        # die geteilte Koerperdatei bleibt unberuehrt
        original = yaml.safe_load(io.open(self.koerper, encoding='utf-8'))['body']
        self.assertNotIn('_waist_level', original)

    def test_die_vereinigung_nimmt_den_groessten_versatz(self):
        vereint = Bundhoehe.uebernehmen({}, [{'bundhoehe': {'versatz_cm': 2.0}},
                                             {'bundhoehe': {'versatz_cm': 6.7, 'rise': 0.5}},
                                             {}])
        self.assertEqual(vereint['bundhoehe']['versatz_cm'], 6.7)
        self.assertEqual(Bundhoehe.uebernehmen({}, [{}, {}]), {})


class BundmaskeTest(SimpleTestCase):
    u"""Der Bund bleibt beim Hochziehen — die Maske kommt aus der Segmentierung."""

    databases = set()

    def setUp(self):
        self.ordner = self.enterContext(Pruefablage.ordner('bundhoehe_'))
        self.netz = os.path.join(self.ordner, 'probe_sim.obj')
        with io.open(os.path.join(self.ordner, 'probe_sim_segmentation.txt'),
                     'w', encoding='utf-8') as datei:
            datei.write('\n'.join(['pant_f_r', 'wb_front', 'stitch_3',
                                   'hose__wb_back,stitch_1', 'shirt__ftorso', '']))

    def test_marken(self):
        self.assertTrue(Bundmaske.ist_bund('wb_front'))
        self.assertTrue(Bundmaske.ist_bund('hose__wb_back'))
        self.assertFalse(Bundmaske.ist_bund('pant_f_r'))
        self.assertFalse(Bundmaske.ist_bund('stitch_4'))
        self.assertFalse(Bundmaske.ist_bund('wbx__pant'))

    def test_die_maske_liegt_neben_dem_netz(self):
        maske = Bundmaske.neben_netz(self.netz, 5)
        self.assertEqual(maske.tolist(), [False, True, False, True, False])
        # fehlende Datei oder falsche Punktzahl: keine Maske, kein Absturz
        self.assertIsNone(Bundmaske.neben_netz(self.netz, 4))
        self.assertIsNone(Bundmaske.neben_netz(os.path.join(self.ordner, 'x_sim.obj')))
        self.assertIsNone(Bundmaske.neben_netz(None))

    def test_eintragen_je_teilnetz(self):
        teile = {'hose': {'indizes': [0, 1, 3]}, 'shirt': {'indizes': [4]}, 'leer': {}}
        Bundmaske.eintragen(teile, os.path.join(self.ordner, 'probe_sim_segmentation.txt'))
        self.assertEqual(teile['hose']['bund'].tolist(), [False, True, True])
        self.assertEqual(teile['shirt']['bund'].tolist(), [False])
        self.assertIsNone(teile['leer']['bund'])


class VerdrahtungTest(SimpleTestCase):

    databases = set()

    def _quelle(self, *teile):
        return io.open(os.path.join(settings.ASSETS_ROOT, 'GarmentCode', *teile),
                       encoding='utf-8').read()

    def test_schnitt_drapierung_und_vereinigung_rufen_die_bundhoehe(self):
        self.assertIn('Bundhoehe.anwenden(ordner, entwurf, stueck, koerper)',
                      self._quelle('lauf.py'))
        self.assertIn('pfade.in_body_mes = Bundhoehe.koerperdatei(spez, pfade.in_body_mes)',
                      self._quelle('drapierlauf.py'))
        self.assertIn('Bundhoehe.uebernehmen(vereint,', self._quelle('schnittvereinigung.py'))
        self.assertIn('Bundhoehe.loggen(', self._quelle('entwurf.py'))

    def test_beide_bauwege_geben_die_bundmaske_ans_anlegen(self):
        self.assertIn('Stoffnacharbeit(fein_p, fein_f, dreiecke, getragen, netzdatei)',
                      self._quelle('drapierdienst.py'))
        self.assertIn('anleger.anlegen(punkte, anliegen_mm, fest)',
                      self._quelle('stoffnacharbeit.py'))
        gemeinsam = self._quelle('gemeinsamablage.py')
        self.assertIn('Bundmaske.eintragen(', gemeinsam)
        self.assertIn("teil.get('bund'))", gemeinsam)
        self.assertIn('anleger.anlegen(punkte, anliegen_mm, fest)', gemeinsam)
