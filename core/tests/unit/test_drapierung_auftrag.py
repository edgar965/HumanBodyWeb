# -*- coding: utf-8 -*-
"""Der Auftrag von `kleid_drapieren` an Blender und an den Stoffsolver (02.10.2026).

WARUM: `drapieren.py` setzte keine Schwerkraft — Blenders Szene fällt nach −Z, die Bühne hat Y oben (gemessen: ein Tuch auf Y = 1 m
fiel in 11 Bildern 533 mm nach −Z), und nichts war angeheftet, ein Stück rutschte die Beine hinunter (Hose: 400 mm in 24 Bildern).
Beide Motoren bekommen jetzt Schwerkraft entlang −Y und das obere Band fest (`fest_oben`, wie bei Newton). Die Tests halten fest,
was im Auftrag steht und dass die festen Punkte kein Delta bekommen. Blender und der Solver laufen hier nicht: `_laufen` ist eine
Attrappe, die ein Ergebnis schreibt."""

import inspect
import json
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.kleidmorphe import G9kleidmorphe
from Genesis9.rezeptumgebung import Rezeptumgebung

from core.dienste.engine2d3dkleiderblender import Engine2d3dKleiderblender
from core.dienste.stoffsolverdrapierung import Stoffsolverdrapierung


class Folger:
    """Ein Teil des Stücks: nur das, was `_dreiecke` liest."""
    kennung = 'teil0'
    ursprung = None
    dreiecke = np.array([[0, 1, 2], [1, 3, 2], [2, 3, 4], [3, 5, 4]])


PUNKTE = np.array([(0.0, 0.0, 0.0), (0.1, 0.0, 0.0), (0.0, 0.5, 0.0), (0.1, 0.5, 0.0), (0.0, 1.0, 0.0), (0.1, 1.0, 0.0)])
Y0, Y1 = 0.0, 1.0


class DrapierauftragTest(SimpleTestCase):
    """Beide Arbeiter schreiben denselben Auftrag; getestet wird, was drinsteht."""

    def abgelegt(self, drapierer, **kw):
        """`drapieren` mit Attrappen für Käfig, Körper, Ablage und den Lauf → (Auftrag, Deltas)."""
        aufrufe = {}

        def lauf(auftrag_datei, bericht_datei):
            auftrag = json.loads(Path(auftrag_datei).read_text(encoding='utf-8'))
            aufrufe['auftrag'] = auftrag
            np.savez(auftrag['aus'], punkte=(PUNKTE + (0.0, -0.02, 0.0)).astype(np.float32))      # alles 2 cm nach unten
            return {'sekunden': 0.1}

        def ablegen(_kennung, _name, _teile, deltas, brief):
            aufrufe['deltas'], aufrufe['brief'] = deltas, brief
            return brief

        kaefig = ([(Folger(), None)], [PUNKTE], Y0, Y1, None, {})
        with mock.patch.object(G9kleidmorphe, 'kaefige', return_value=kaefig), \
                mock.patch.object(G9kleidmorphe, 'koerper', return_value=(PUNKTE, Folger.dreiecke, None, None, None)), \
                mock.patch.object(G9kleidmorphe, 'ablegen', side_effect=ablegen), \
                mock.patch.object(type(drapierer), '_laufen', side_effect=lauf):
            drapierer.drapieren('shirt', **kw)
        return aufrufe

    def test_blender_bekommt_schwerkraft_entlang_minus_y_und_das_obere_band_fest(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as ordner:
            a = self.abgelegt(Engine2d3dKleiderblender(ordner), bilder=12, druck=0.5)
        auftrag = a['auftrag']
        self.assertEqual(auftrag['schwerkraft'], [0.0, -9.81, 0.0])
        self.assertEqual(auftrag['anheften'], [4, 5])                       # y ≥ 1,0 − 0,08 · 1,0 = 0,92
        self.assertEqual((auftrag['bilder'], auftrag['druck']), (12, 0.5))
        self.assertEqual(a['brief']['schwerkraft'], 'Y unten')

    def test_der_solver_bekommt_denselben_auftrag_und_rechnet_auf_dem_geraet(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as ordner:
            a = self.abgelegt(Stoffsolverdrapierung(ordner), bilder=12, druck=0.5, steifigkeit=15.0)
        auftrag = a['auftrag']
        self.assertEqual(auftrag['schwerkraft'], [0.0, -9.81, 0.0])
        self.assertEqual(auftrag['anheften'], [4, 5])
        self.assertEqual((auftrag['bilder'], auftrag['druck'], auftrag['steifigkeit']), (12, 0.5, 15.0))
        self.assertEqual(auftrag['rechner'], 'warp')              # ohne CUDA-GPU ein Fehler statt Minuten auf dem Host
        self.assertEqual(a['brief']['motor'], 'stoffsolver')

    def test_die_festen_punkte_bekommen_kein_delta_die_anderen_die_verschiebung(self):
        for klasse in (Engine2d3dKleiderblender, Stoffsolverdrapierung):
            with self.subTest(klasse.__name__), tempfile.TemporaryDirectory(dir=Path(__file__).parent) as ordner:
                delta = self.abgelegt(klasse(ordner))['deltas'][0]
                np.testing.assert_allclose(delta[[4, 5]], 0.0, atol=1e-12)
                np.testing.assert_allclose(delta[[0, 1, 2, 3]], (0.0, -0.02, 0.0), atol=1e-6)

    def test_ein_breiteres_band_haelt_mehr_punkte_fest(self):
        """`fest_oben` ist ein Anteil der Höhe: 0,5 hält die obere Hälfte (y ≥ 0,5) — wie bei Newton."""
        for klasse in (Engine2d3dKleiderblender, Stoffsolverdrapierung):
            with self.subTest(klasse.__name__), tempfile.TemporaryDirectory(dir=Path(__file__).parent) as ordner:
                a = self.abgelegt(klasse(ordner), fest_oben=0.5)
                self.assertEqual(a['auftrag']['anheften'], [2, 3, 4, 5])
                np.testing.assert_allclose(a['deltas'][0][[2, 3, 4, 5]], 0.0, atol=1e-12)
                np.testing.assert_allclose(a['deltas'][0][[0, 1], 1], -0.02, atol=1e-6)

    def test_der_vorgabewert_fest_oben_ist_der_von_newton(self):
        from core.dienste.kleiddrapierung import Kleiddrapierung
        newton = inspect.signature(Kleiddrapierung.drapieren).parameters['fest_oben'].default
        self.assertEqual(Engine2d3dKleiderblender.FEST_OBEN, newton)
        self.assertEqual(Stoffsolverdrapierung.FEST_OBEN, newton)


class MotorwahlTest(SimpleTestCase):
    def test_der_stoffsolver_ist_ein_motor_des_rezepts(self):
        self.assertIn('stoffsolver', Rezeptumgebung.MOTOREN)
        drapierer = object()
        umgebung = Rezeptumgebung(drapierer={'stoffsolver': drapierer})
        self.assertIs(umgebung.drapierung('stoffsolver'), drapierer)

    def test_ein_unbekannter_motor_nennt_die_gueltigen(self):
        with self.assertRaises(ValueError) as fehler:
            Rezeptumgebung().drapierung('unity')
        for motor in Rezeptumgebung.MOTOREN:
            self.assertIn(motor, str(fehler.exception))

    def test_ohne_registrierten_drapierer_ist_es_ein_klarer_fehler(self):
        with self.assertRaises(ValueError) as fehler:
            Rezeptumgebung().drapierung('stoffsolver')
        self.assertIn('Stoffsolver', str(fehler.exception))
