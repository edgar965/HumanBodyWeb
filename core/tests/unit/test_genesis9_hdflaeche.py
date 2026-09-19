# -*- coding: utf-8 -*-
u"""Die Kollisionsflaeche des Koerpers traegt die HD-Morphs (19.09.2026).

WARUM (Edgar: „T-Shirt scheint noch immer die Haut durch bei Standardmodell"):
Ursula traegt `P3DUrsula_body_bs_Body` (HD). `bauen()` legte den Beitrag auf
die Browserpunkte, `koerperflaeche()` nicht — die Haut stand im Browser bis
2,1 mm weiter draussen als die Flaeche, gegen die das Hemd (1 mm Abstand)
gehoben wurde: 8 Hemdpunkte in der Haut, linke aeussere Brust.

Kunstdaten: eine Stufe, die den Kaefig durchreicht, und ein HD-Beitrag von
+2 mm in y. Sabotage-Gegenprobe: `_fein` ohne `+ hd` -> Fall 1 rot.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from Genesis9.koerpernetz import G9koerpernetz


class _Stufe:
    def __init__(self, stufen):
        self.stufen = stufen
        self._cc = object()

    def punkte(self, kaefig):
        return np.asarray(kaefig, dtype=np.float64) * 1.0

    def normalen(self, _kaefig, fein):
        n = np.zeros_like(fein)
        n[:, 1] = 1.0
        return n


class _Basis:
    def __init__(self, stufen):
        self._stufen = stufen

    def netzstufe(self, n):
        return _Stufe(n if n is not None else self._stufen)


class _Formung:
    formeln = object()

    def __init__(self, kennung):
        self.kennung = kennung

    def punkte(self):
        return np.array([[0.0, 1.0, 0.0], [0.1, 1.2, 0.0], [0.0, 1.5, 0.1]])

    def boden(self):
        return 0.0

    def fingerabdruck(self):
        return self.kennung


class HdFlaeche(SimpleTestCase):
    databases = set()

    def setUp(self):
        G9koerpernetz._flaechen.clear()

    def _flaeche(self, stufen, hd):
        beitrag = mock.Mock(return_value=hd)
        with mock.patch('Genesis9.koerpernetz.G9basisnetz.holen', return_value=_Basis(stufen)), \
                mock.patch('Genesis9.koerpernetz.G9hdmorphe.beitrag', beitrag):
            netz = G9koerpernetz(_Formung('f-%d-%s' % (stufen, hd is not None)),
                                 eintrag={}, stufen=stufen)
            punkte, normalen, baum = netz.koerperflaeche()
        return punkte, normalen, baum, beitrag

    def test_1_flaeche_traegt_den_hd_beitrag(self):
        hd = np.full((3, 3), 0.0)
        hd[:, 1] = 0.002
        punkte, _n, baum, beitrag = self._flaeche(2, hd)
        np.testing.assert_allclose(punkte[:, 1], [1.002, 1.202, 1.502])
        self.assertEqual(beitrag.call_count, 1)
        self.assertIsNotNone(baum)

    def test_2_ohne_hd_kanaele_bleibt_der_kaefig(self):
        punkte, _n, _b, beitrag = self._flaeche(1, None)
        np.testing.assert_allclose(punkte[:, 1], [1.0, 1.2, 1.5])
        self.assertEqual(beitrag.call_count, 1)

    def test_3_stufe_null_fragt_keine_hd_morphs(self):
        punkte, _n, _b, beitrag = self._flaeche(0, None)
        np.testing.assert_allclose(punkte[:, 1], [1.0, 1.2, 1.5])
        self.assertEqual(beitrag.call_count, 0)
