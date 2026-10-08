# -*- coding: utf-8 -*-
"""Standhaut — Hautsatz nach Grundfigur, Normalenkarten der Haut, Dünnheitskarte des Durchlichts (07.10.2026, Edgar: „mach alle 5").

Kleine Kunstbilder aus Zahlenfeldern, keine Netze, keine Daz-Dateien (der Hautsatz kommt aus einer Attrappe des Auftrags). Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.standdurchlicht import Standdurchlicht
from core.dienste.standhaut import Standhaut


def _normale(n=8, neigung=0.0):
    """Eine Normalenkarte (Tangentenraum): überall dieselbe Neigung in +u (R), sonst flach."""
    a = np.zeros((n, n, 3), dtype=np.float64)
    a[..., 0] = neigung
    a[..., 2] = np.sqrt(1.0 - neigung ** 2)
    return Image.fromarray(np.rint((a * 0.5 + 0.5) * 255.0).astype(np.uint8), 'RGB')


class DerHautsatz(SimpleTestCase):
    def _job(self, basis):
        return SimpleNamespace(optionen={'figur': {'basis': basis}})

    def test_die_maennliche_grundfigur_bekommt_die_maennerhaut(self):
        self.assertEqual(Standhaut.preset(self._job('masculine')), 'G9 Masculine Skin 01 MAT')

    def test_die_uebrigen_grundfiguren_behalten_die_vorgabe(self):
        self.assertIsNone(Standhaut.preset(self._job('feminine')))
        self.assertIsNone(Standhaut.preset(self._job('neutral')))

    def test_die_fassung_haengt_am_hautsatz(self):
        self.assertNotEqual(Standhaut.fassung(self._job('masculine')), Standhaut.fassung(self._job('feminine')))

    def test_ein_auftrag_ohne_optionen_behaelt_die_vorgabe(self):
        """Die Attrappen der Standmodell-Tests tragen keine Optionen."""
        self.assertIsNone(Standhaut.preset(SimpleNamespace(kennung='probe')))


class DieNormalenkarten(SimpleTestCase):
    def test_flach_auf_flach_bleibt_flach(self):
        n = np.asarray(Standhaut.verrechnen(_normale(), _normale()), dtype=np.int64)
        self.assertLessEqual(np.abs(n - np.array([128, 128, 255])).max(), 1)

    def test_die_neigungen_addieren_sich(self):
        unten, oben = _normale(neigung=0.2), _normale(neigung=0.2)
        n = np.asarray(Standhaut.verrechnen(unten, oben), dtype=np.float64) / 127.5 - 1.0
        self.assertAlmostEqual(float(n[0, 0, 0]), 0.4 / np.linalg.norm([0.4, 0.0, np.sqrt(1 - 0.04)]), delta=0.02)

    def test_die_untere_karte_wird_auf_die_groesse_der_oberen_gebracht(self):
        n = Standhaut.verrechnen(_normale(16), _normale(8))
        self.assertEqual(n.size, (8, 8))

    def test_ohne_normalenangabe_gibt_es_kein_bild(self):
        self.assertIsNone(Standhaut.normalenbild({}))
        self.assertIsNone(Standhaut.normalenbild({'albedo': 'x.jpg'}))

    def test_eine_nicht_lesbare_karte_laesst_die_kachel_glatt(self):
        with mock.patch('Genesis9.material.G9material.datei', return_value=None):
            self.assertIsNone(Standhaut.normalenbild({'normalen': '/Runtime/Textures/x.jpg'}))


class DieDuennheitskarte(SimpleTestCase):
    def test_ohne_dicke_im_netz_gibt_es_keine_karte(self):
        self.assertEqual(Standdurchlicht.karten({'gruppen': []}), {})

    def test_die_schluessel_aendern_sich_mit_der_duennheit(self):
        netz = {'dreiecke': np.array([[0, 1, 2]]), 'uv': np.array([[0, 0], [1, 0], [0, 1.0]]), 'dicke': np.array([0.0, 0.5, 1.0])}
        a = Standdurchlicht._schluessel(netz)
        b = Standdurchlicht._schluessel(dict(netz, dicke=np.array([0.0, 0.5, 0.9])))
        self.assertNotEqual(a, b)
        self.assertEqual(a, Standdurchlicht._schluessel(dict(netz)))

    def test_anhaengen_legt_die_textur_in_die_extras_des_materials(self):
        glb = SimpleNamespace(gltf={'materials': [{'name': 'a'}, {'name': 'b'}]})
        Standdurchlicht.anhaengen(glb, 1, 7)
        self.assertEqual(glb.gltf['materials'][1]['extras']['figurfilm'], {'durchlicht_textur': 7})
        self.assertNotIn('extras', glb.gltf['materials'][0])

    def test_ohne_textur_aendert_anhaengen_nichts(self):
        glb = SimpleNamespace(gltf={'materials': [{'name': 'a'}]})
        Standdurchlicht.anhaengen(glb, 0, None)
        self.assertNotIn('extras', glb.gltf['materials'][0])
