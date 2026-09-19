# -*- coding: utf-8 -*-
u"""`G9garmentfigur.sichtbar()` ist die Flaeche, die der Browser zeigt.

Befund (Edgar, 19.09.2026, Bild vom Aermelsaum des GarmentCode-Oberteils auf
Ursula): Die Nacharbeit rechnete gegen Stufe 1 OHNE HD-Morphs — der Stoff lag
1,74 mm ueber dieser Flaeche, aber nur 1,02 mm ueber der gezeigten (Stufe 1
mit HD) und 1,33 mm ueber Stufe 2 (`_wegwerf/mess_g9stoffhaut.py`). Seither
kommt die Flaeche aus `G9koerpernetz.koerperflaeche` (mit HD, wie die
Daz-Kleidung) auf der Stufe des Browsers.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste import g9garmentfigur
from core.dienste.g9garmentfigur import G9garmentfigur


class _Stufe:
    def __init__(self, stufen):
        self.stufen = stufen
        self.dreiecke = [[0, 1, 2]] * (stufen + 1)


class _Netz:
    aufrufe = []

    def __init__(self, formung, stufen=0, **_):
        _Netz.aufrufe.append(stufen)
        self.stufen = stufen

    def koerperflaeche(self):
        fein = np.full((3, 3), 0.5 + self.stufen, dtype=np.float64)
        return fein, None, None


class G9garmentfigurSichtbarTest(SimpleTestCase):
    databases = set()

    def _figur(self):
        figur = G9garmentfigur.__new__(G9garmentfigur)
        figur.regler, figur.formung, figur._roh = {}, object(), None
        figur.stufe = lambda stufen=0: _Stufe(stufen)
        return figur

    def test_die_flaeche_kommt_mit_hd_aus_der_koerperflaeche(self):
        _Netz.aufrufe = []
        with mock.patch.object(g9garmentfigur, 'G9koerpernetz', _Netz), \
                mock.patch.object(G9garmentfigur, 'sichtbare_stufe', classmethod(lambda cls: 2)):
            punkte, dreiecke = self._figur().sichtbar()
        self.assertEqual(_Netz.aufrufe, [2])
        self.assertTrue(np.allclose(punkte, 2.5))
        self.assertEqual(dreiecke.shape, (3, 3))

    def test_ohne_anfrage_gilt_die_ansichtsstufe(self):
        with mock.patch.object(g9garmentfigur.G9netzstufe, 'browser',
                               classmethod(lambda cls: (_ for _ in ()).throw(RuntimeError('kein Keks')))):
            self.assertEqual(G9garmentfigur.sichtbare_stufe(), G9garmentfigur.SICHTBAR)

    def test_der_keks_entscheidet(self):
        with mock.patch.object(g9garmentfigur.G9netzstufe, 'browser', classmethod(lambda cls: 2)):
            self.assertEqual(G9garmentfigur.sichtbare_stufe(), 2)

    def test_die_nacharbeit_bekommt_diese_flaeche(self):
        """`Genesis9drapierung._anziehen` reicht `figur.sichtbar()` als
        `sichtbar=` an den Traeger — die Flaeche der Korrektur."""
        from GarmentCode import genesis9drapierung
        quelle = open(genesis9drapierung.__file__, encoding='utf-8').read()
        self.assertIn('fein_p, fein_f = figur.sichtbar()', quelle)
        self.assertIn('sichtbar=(figur.projekt(fein_p), np.asarray(fein_f))', quelle)
