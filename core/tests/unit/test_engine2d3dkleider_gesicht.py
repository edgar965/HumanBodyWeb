# -*- coding: utf-8 -*-
"""Reiter „Gesicht" von 2D3D Kleider (07.10.2026): `Engine2d3dKleiderGesichtslage` (Kopfhaltung, Abweichung, Landmarken auf der Fläche), `Meshfigurlandmarkmorphe` (Klemme, Gauß-RBF), `Engine2d3dKleiderGesichtsdetail`
(Dateiname mit Fassung, Aufräumen) — Kunstdaten, kein Render, keine echte Ablage."""
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from core.dienste.engine2d3dkleidergesichtsdetail import Engine2d3dKleiderGesichtsdetail
from core.dienste.engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage as Lage
from core.dienste.meshfigurlandmarkmorphe import Meshfigurlandmarkmorphe
from django.test import SimpleTestCase

from ._pruefablage import Pruefablage


def _drehung_y(grad):
    a = np.radians(grad)
    return np.array([[np.cos(a), 0.0, np.sin(a)], [0.0, 1.0, 0.0], [-np.sin(a), 0.0, np.cos(a)]])


class DieGesichtslage(SimpleTestCase):
    def test_1_kabsch_findet_drehung_und_versatz(self):
        zufall = np.random.default_rng(3)
        a = zufall.normal(size=(60, 3))
        r, t = _drehung_y(25.0), np.array([0.3, -0.2, 0.1])
        drehung, versatz = Lage._kabsch(a, a @ r.T + t)
        self.assertLess(float(np.abs(drehung - r).max()), 1e-9)
        self.assertLess(float(np.abs(versatz - t).max()), 1e-9)
        self.assertAlmostEqual(float(np.linalg.det(drehung)), 1.0, places=9)           # nie eine Spiegelung

    def test_2_anwenden_ist_matrix_mal_punkt(self):
        m = np.eye(4)
        m[:3, :3], m[:3, 3] = _drehung_y(90.0), [1.0, 0.0, 0.0]
        aus = Lage._anwenden(np.array([[0.0, 0.0, 1.0]]), m)
        self.assertTrue(np.allclose(aus, [[2.0, 0.0, 0.0]]))

    def test_3_die_haltung_wird_zurueckgedreht(self):
        zufall = np.random.default_rng(5)
        ruhe = zufall.normal(size=(1500, 3)) * 0.04 + np.array([0.0, 1.6, 0.0])
        r, t = _drehung_y(10.0), np.array([0.2, 0.0, 0.05])
        posiert = ruhe @ r.T + t
        with Pruefablage.ordner('gesicht_') as ordner:
            np.save(Path(ordner) / 'posiert.npy', posiert)
            ablage = SimpleNamespace(arbeit=lambda name: Path(ordner) / name)
            zurueck, befund = Lage._haltung(ablage, posiert[:478], ruhe)
        self.assertAlmostEqual(befund['drehung_grad'], 10.0, places=1)
        self.assertLess(befund['rest_rms_mm'], 0.01)
        self.assertLess(float(np.abs(Lage._anwenden(posiert, zurueck) - ruhe).max()), 1e-6)

    def test_4_ohne_posiert_bleibt_die_lage_und_der_grund_steht_im_befund(self):
        with Pruefablage.ordner('gesicht_') as ordner:
            ablage = SimpleNamespace(arbeit=lambda name: Path(ordner) / name)
            zurueck, befund = Lage._haltung(ablage, np.zeros((478, 3)), np.zeros((10, 3)))
        self.assertTrue(np.allclose(zurueck, np.eye(4)))
        self.assertIn('posiert.npy', befund['aus'])

    def test_5_die_abweichung_je_gruppe_in_mm(self):
        gesicht = np.zeros((478, 3))
        lage = {'gesicht': gesicht, 'modell_gesicht': gesicht + np.array([0.001, 0.0, 0.0])}
        z = Lage.abweichung(lage)
        self.assertEqual(z['alle']['median_mm'], 1.0)
        self.assertEqual(z['gruppen']['Lippen']['median_mm'], 1.0)
        self.assertIsNone(Lage.abweichung({'gesicht': gesicht, 'modell_gesicht': None}))
        lage['modell_gesicht'] = lage['modell_gesicht'].copy()
        lage['modell_gesicht'][Lage.GRUPPEN['Nase']] = np.nan                            # NaN (kein Punkt in der Tabelle) zählt nicht mit
        self.assertEqual(Lage.abweichung(lage)['gruppen']['Lippen']['median_mm'], 1.0)
        self.assertIsNone(Lage.abweichung(lage)['gruppen']['Nase'])

    def test_6_ohne_netz_bleiben_die_landmarken_wie_sie_sind_als_kopie(self):
        gesicht = np.random.default_rng(1).normal(size=(478, 3))
        aus = Lage.auf_flaeche({'netz_pfad': None, 'gesicht': gesicht})
        self.assertTrue(np.array_equal(aus, gesicht))
        aus[0] += 1.0
        self.assertFalse(np.array_equal(aus, gesicht))                                   # eine Kopie, das Original bleibt


class DieLandmarkmorphe(SimpleTestCase):
    def test_1_die_klemme_kappt_lange_reste_und_laesst_kurze(self):
        reste = np.array([[0.0, 0.0, 0.020], [0.003, 0.0, 0.0]])
        aus = Meshfigurlandmarkmorphe._klemmen(reste)
        self.assertAlmostEqual(float(np.linalg.norm(aus[0])), Meshfigurlandmarkmorphe.KLEMME, places=9)
        self.assertTrue(np.allclose(aus[0] / np.linalg.norm(aus[0]), [0.0, 0.0, 1.0]))   # die Richtung bleibt
        self.assertTrue(np.array_equal(aus[1], reste[1]))
        self.assertEqual(float(reste[0, 2]), 0.020)                                      # das Original bleibt

    def test_2_das_feld_trifft_die_reste_nahe_den_landmarken_und_ist_fern_null(self):
        zentren = np.array([[0.0, 0.0, 0.0], [0.008, 0.0, 0.0], [0.016, 0.0, 0.0], [0.0, 0.008, 0.0], [0.008, 0.008, 0.0]])
        reste = np.tile([0.0, 0.0, 0.004], (len(zentren), 1))
        orte = np.vstack([zentren, [[1.0, 1.0, 1.0], [0.0, 0.0, 0.0 + 5 * Meshfigurlandmarkmorphe.SIGMA]]])
        feld = Meshfigurlandmarkmorphe._feld(zentren, reste, orte)
        an_den_zentren = feld[:len(zentren), 2]
        self.assertTrue((an_den_zentren > 0.5 * 0.004).all() and (an_den_zentren <= 1.2 * 0.004).all())   # Regularisierung 0,1: nahe, nicht genau
        self.assertTrue(np.allclose(feld[len(zentren):], 0.0))                           # weit weg und jenseits der Reichweite: 0


class DieBilderreihen(SimpleTestCase):
    def test_1_der_dateiname_traegt_bereich_und_fassung(self):
        self.assertEqual(Engine2d3dKleiderGesichtsdetail.dateiname('mund', 'v3_k_abc_1f'), 'gesicht_mund_v3_k_abc_1f.png')

    def test_2_ohne_stand_json_gibt_es_keine_fassung(self):
        with Pruefablage.ordner('gesicht_') as ordner:
            ablage = SimpleNamespace(ergebnis=lambda name=None: Path(ordner) / name if name else Path(ordner))
            with self.assertRaises(ValueError):
                Engine2d3dKleiderGesichtsdetail.fassung(SimpleNamespace(), ablage)

    def test_3_aufraeumen_nimmt_nur_aeltere_bilder_dieses_reiters_weg(self):
        with Pruefablage.ordner('gesicht_') as ordner:
            wurzel = Path(ordner)
            ablage = SimpleNamespace(ergebnis=lambda name=None: wurzel / name if name else wurzel)
            for name in ('gesicht_augen_alt.png', 'gesicht_augen_neu.png', 'gesicht_nase_alt.png', 'gesicht_mund_neu.png', 'gesicht_hals_alt.png', 'andere.png'):
                (wurzel / name).write_bytes(b'PNG')
            Engine2d3dKleiderGesichtsdetail._aufraeumen(ablage, 'neu')
            self.assertEqual(sorted(p.name for p in wurzel.iterdir()), ['andere.png', 'gesicht_augen_neu.png', 'gesicht_hals_alt.png', 'gesicht_mund_neu.png'])
