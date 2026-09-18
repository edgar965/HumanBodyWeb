# -*- coding: utf-8 -*-
u"""Genesis 9: Knochenskalierung aus Posenformeln (`G9knochenmatrizen`), an
Kunstdaten — ohne Daz-Bibliothek.

Skelett der Probe: Figur → `hip` (erbt) → `pelvis` (erbt nicht) → `l_thigh`
(erbt nicht), Gelenke auf der y-Achse. Daz' Regel, wie sie hier steht: ein
nicht erbender Knochen uebernimmt die LAGE seines Gelenks aus dem
Elternteil, nicht dessen Skalierung — die Skalierung des Figurknotens
erreicht aber alle.

Sabotage-Gegenproben (17.09.2026): Figurfaktor nicht durchgereicht
(`s / eigene[eltern]` → `s`) → Fall 2 und 3 rot; Gelenk nicht mit der
Elternmatrix bewegt → Fall 3 rot; Verschiebung nicht addiert → Fall 4 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.formeln import G9formeln                        # noqa: E402
from Genesis9.knochenmatrizen import G9knochenmatrizen        # noqa: E402
from Genesis9.morphablage import G9morphablage                # noqa: E402


def skelett():
    return [
        {'name': 'hip', 'eltern': None, 'kopf': np.array([0., 100., 0.]),
         'schwanz': np.array([0., 90., 0.]), 'erbt': True},
        {'name': 'pelvis', 'eltern': 'hip', 'kopf': np.array([0., 100., 0.]),
         'schwanz': np.array([0., 80., 0.]), 'erbt': False},
        {'name': 'l_thigh', 'eltern': 'pelvis', 'kopf': np.array([10., 90., 0.]),
         'schwanz': np.array([10., 50., 0.]), 'erbt': False},
    ]


class Haut:
    def __init__(self, knochen, index, gewicht):
        self.knochen, self.index, self.gewicht = knochen, index, gewicht


class Knochenmatrizen(SimpleTestCase):

    def test_1_ohne_posen_bleibt_alles(self):
        m = G9knochenmatrizen({}, roh=skelett())
        self.assertTrue(m.leer)
        punkte = np.array([[0.1, 0.9, 0.0]])
        np.testing.assert_array_equal(m.anwenden(punkte, None), punkte)
        kopf, schwanz = m.gelenk('hip', np.array([0., 100., 0.]),
                                 np.array([0., 90., 0.]))
        np.testing.assert_array_equal(kopf, [0., 100., 0.])

    def test_2_figurskalierung_erreicht_jeden_knochen(self):
        m = G9knochenmatrizen({'Genesis9': {'scale/general': 2.0}}, roh=skelett())
        haut = Haut(['hip', 'pelvis', 'l_thigh'],
                    np.array([[0, 0, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0]]),
                    np.array([[1., 0, 0, 0], [1., 0, 0, 0], [1., 0, 0, 0]]))
        punkte = np.array([[0.0, 0.95, 0.0], [0.0, 0.85, 0.0], [0.1, 0.6, 0.0]])
        neu = m.anwenden(punkte, haut)
        np.testing.assert_allclose(neu, punkte * 2.0, atol=1e-9)

    def test_3_knochen_erbt_lage_aber_nicht_skalierung(self):
        m = G9knochenmatrizen({'pelvis': {'scale/general': 1.5}}, roh=skelett())
        haut = Haut(['pelvis', 'l_thigh'],
                    np.array([[0, 0, 0, 0], [1, 0, 0, 0]]),
                    np.array([[1., 0, 0, 0], [1., 0, 0, 0]]))
        punkte = np.array([[0.0, 0.80, 0.0], [0.10, 0.50, 0.0]])
        neu = m.anwenden(punkte, haut)
        # Beckenpunkt: um das Beckengelenk (1,00 m) mit 1,5 → 0,70 m.
        np.testing.assert_allclose(neu[0], [0.0, 0.70, 0.0], atol=1e-9)
        # Oberschenkel: nicht skaliert, aber sein Gelenk (0,90) wandert mit
        # dem Becken auf 1,00 − 1,5·0,10 = 0,85 → der Punkt 0,05 tiefer,
        # x bleibt 0,10 + (1,5 − 1)·0,10 = 0,15 (das Gelenk rueckt seitlich).
        np.testing.assert_allclose(neu[1], [0.15, 0.45, 0.0], atol=1e-9)
        kopf, schwanz = m.gelenk('l_thigh', np.array([10., 90., 0.]),
                                 np.array([10., 50., 0.]))
        np.testing.assert_allclose(kopf, [15., 85., 0.], atol=1e-9)
        np.testing.assert_allclose(schwanz, [15., 45., 0.], atol=1e-9)

    def test_4_verschiebung_der_huefte_nimmt_alles_mit(self):
        m = G9knochenmatrizen({'hip': {'translation/y': 22.95}}, roh=skelett())
        haut = Haut(['l_thigh'], np.array([[0, 0, 0, 0]]), np.array([[1., 0, 0, 0]]))
        neu = m.anwenden(np.array([[0.1, 0.5, 0.0]]), haut)
        np.testing.assert_allclose(neu, [[0.1, 0.7295, 0.0]], atol=1e-9)

    def test_5_posen_aus_dem_formelgraphen(self):
        u"""`G9formeln.posen`: Summenformeln auf die Vorgabe 1 (Skalierung)."""
        kanaele = {
            'hoehe': {'id': 'hoehe', 'label': 'Height', 'gruppe': '/Body',
                      'min': -1.0, 'max': 1.0, 'vorgabe': 0.0, 'sichtbar': True,
                      'formeln': [
                          {'ziel': ['pose', 'Genesis9', 'scale/general'],
                           'stufe': 'sum',
                           'ops': [{'op': 'push', 'kanal': 'hoehe'},
                                   {'op': 'push', 'val': 0.25}, {'op': 'mult'}]},
                          {'ziel': ['pose', 'hip', 'translation/y'],
                           'stufe': 'sum',
                           'ops': [{'op': 'push', 'kanal': 'hoehe'},
                                   {'op': 'push', 'val': 10.0}, {'op': 'mult'}]},
                          {'ziel': ['pose', 'head', 'rotation/y'],
                           'stufe': 'sum',
                           'ops': [{'op': 'push', 'val': 5.0}]},
                      ]},
        }
        ablage = G9morphablage(kanaele, np.zeros(0, dtype=np.int32),
                               np.zeros((0, 3), dtype=np.float32), {}, {})
        G9formeln.vergessen()
        try:
            posen = G9formeln({'hoehe': 1.0}, ablage).posen()
        finally:
            G9formeln.vergessen()
        self.assertAlmostEqual(posen['Genesis9']['scale/general'], 1.25)
        self.assertAlmostEqual(posen['hip']['translation/y'], 10.0)
        # Seit 18.09.2026 (Daz-Posen) auch die Drehung, in Grad.
        self.assertAlmostEqual(posen['head']['rotation/y'], 5.0)
        # Ohne Regler bleibt nur die Konstantenformel (5° am Kopf).
        self.assertEqual(G9formeln({}, ablage).posen(), {'head': {'rotation/y': 5.0}})
