# -*- coding: utf-8 -*-
u"""GarmentCode auf Genesis 9: die Figur als Koerper (`G9garmentfigur`) und die
Anfrage (`Garmentanfrage`, `figurart`/`regler_figur`), 19.09.2026.

WARUM (Edgar): „garment Code Assets funktioniert nicht auf Genesis, kann man
das evtl. anpassen?" Eine Genesis-Figur schickte weder Bauart noch Morphs;
vermessen wurde der HumanBody-Grundkoerper, das Rig trug DEF-Namen.

Ohne Daz-Bibliothek (Kunstdaten): Netzstufe und Haut sind Attrappen.

1. `knochenteil`: Daz-Namen -> GarmentCode-Teile (`l_forearm` -> left_arm,
   `r_toes` -> right_leg, `l_shoulder`/`hip`/`head` -> Rumpf).
2. `segmente`: staerkster Knochen je Punkt; `Mouth Cavity` -> face_internal;
   jeder Punkt genau einmal.
3. `geschlecht` aus Feminine/Masculine; `projekt` dreht Y oben -> Z oben.
4. `Garmentanfrage.lesen`: `figurart=genesis9` mit `regler_figur`; eine
   unbekannte Figurart faellt auf None; ohne Feld bleibt der alte Weg.
"""
from unittest import mock

import numpy as np
from django.test import RequestFactory, SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from core.api.garmentanfrage import Garmentanfrage  # noqa: E402
from core.dienste.g9garmentfigur import G9garmentfigur  # noqa: E402


class Stufenattrappe:
    u"""Acht Punkte, zwei Dreiecke, Haut auf vier Knochen, eine Mundgruppe."""

    def __init__(self):
        knochen = ['hip', 'l_forearm', 'r_thigh', 'lowerjaw']
        self.haut = {
            'knochen': knochen,
            'index': np.array([[0, 1, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0], [0, 2, 0, 0],
                               [3, 0, 0, 0], [3, 0, 0, 0], [3, 0, 0, 0], [1, 2, 0, 0]]),
            'gewicht': np.array([[0.9, 0.1, 0, 0], [1, 0, 0, 0], [0.7, 0.3, 0, 0],
                                 [0.4, 0.6, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0],
                                 [1, 0, 0, 0], [0.5, 0.5, 0, 0]], dtype=float),
        }
        self.dreiecke = np.array([[0, 1, 2], [4, 5, 6]])
        self.gruppen = [{'name': 'Body', 'index_ab': 0, 'index_anzahl': 3},
                        {'name': 'Mouth Cavity', 'index_ab': 3, 'index_anzahl': 3}]


def figur(regler=None):
    with mock.patch.object(G9garmentfigur, '__init__', lambda self, r: None):
        f = G9garmentfigur(None)
    f.regler = dict(regler or {})
    f.stufe = lambda stufen=0: Stufenattrappe()
    return f


class Knochenteile(SimpleTestCase):
    databases = set()

    def test_daz_namen_werden_garmentcode_teile(self):
        self.assertEqual(G9garmentfigur.knochenteil('l_forearm'), 'left_arm')
        self.assertEqual(G9garmentfigur.knochenteil('r_toes'), 'right_leg')
        self.assertEqual(G9garmentfigur.knochenteil('l_pinkymetacarpal'), 'left_arm')
        self.assertEqual(G9garmentfigur.knochenteil('r_thightwist2'), 'right_leg')
        for rumpf in ('l_shoulder', 'hip', 'head', 'spine3', 'l_pectoral', 'l_eye', ''):
            self.assertIsNone(G9garmentfigur.knochenteil(rumpf), rumpf)

    def test_segmente_aus_staerkstem_knochen_und_mundhoehle(self):
        segmente = figur().segmente()
        self.assertEqual(segmente['body'], [0])                # hip gewinnt (0,9 gegen 0,1)
        self.assertEqual(segmente['left_arm'], [1, 7])         # 7: Gleichstand -> erster Knochen
        self.assertEqual(segmente['right_leg'], [2, 3])        # 3: r_thigh 0,6 gegen hip 0,4
        self.assertEqual(segmente['face_internal'], [4, 5, 6])
        alle = sorted(sum(segmente.values(), []))
        self.assertEqual(alle, list(range(8)))
        self.assertEqual(set(segmente), set(G9garmentfigur.SEGMENTE))


class Vorgaben(SimpleTestCase):
    databases = set()

    def test_geschlecht_aus_den_reglern(self):
        self.assertEqual(figur({}).geschlecht(), 'female')
        self.assertEqual(figur({G9garmentfigur.MASKULIN: 1.0}).geschlecht(), 'male')
        self.assertEqual(figur({G9garmentfigur.MASKULIN: 0.4,
                                G9garmentfigur.FEMININ: 0.6}).geschlecht(), 'female')
        self.assertEqual(figur({G9garmentfigur.MASKULIN: 'x'}).geschlecht(), 'female')

    def test_projekt_dreht_y_oben_nach_z_oben(self):
        np.testing.assert_allclose(G9garmentfigur.projekt([[1.0, 2.0, 3.0]]), [[1.0, -3.0, 2.0]])


class Anfrage(SimpleTestCase):
    databases = set()

    def _anfrage(self, **felder):
        return Garmentanfrage.lesen(RequestFactory().post('/api/garmentcode/masse/', felder))

    def test_genesis9_mit_reglern(self):
        a = self._anfrage(figurart='genesis9', regler_figur='{"BaseFeminine_figure_ctrl_Character": 1}',
                          geschlecht='female', morphs='{}')
        self.assertEqual(a.figurart, 'genesis9')
        self.assertEqual(a.regler_figur, {'BaseFeminine_figure_ctrl_Character': 1})
        self.assertIsNone(a.koerper)
        self.assertFalse(a.smpl)

    def test_unbekannte_figurart_faellt_auf_none(self):
        self.assertIsNone(self._anfrage(figurart='klingone').figurart)

    def test_ohne_feld_der_alte_weg(self):
        a = self._anfrage(geschlecht='male', bauart='Male_Caucasian', morphs='{"a": 1}')
        self.assertIsNone(a.figurart)
        self.assertEqual(a.regler_figur, {})
        self.assertEqual((a.geschlecht, a.bauart, a.morphs), ('male', 'Male_Caucasian', {'a': 1}))
