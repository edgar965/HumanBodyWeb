# -*- coding: utf-8 -*-
u"""Kollision Stueck gegen Stueck (`Genesis9/lagen.py`, `G9lagenanfrage`).

WARUM (Edgar, 19.09.2026): „das genesis T-Shirt ist an einigen Stellen
kaputt" — der Bund der Jeans stach durch den Saum des Hemds, weil jedes
Stueck nur aus der HAUT gehoben wurde. Jetzt liegt das Stueck, das in der
Ueberlappung weiter von der Haut steht, aussen und wird ueber das innere
gehoben; die Regel ist an acht Paaren der Bibliothek gemessen
(`ProjektTemp/g9_lagen_messung.py`).

Kunstdaten ohne Daz-Bibliothek: die „Haut" ist eine Ebene y = 0 mit
Normale +y, die Stuecke sind Punktgitter darueber.

1. Einordnen: das hoehere Gitter liegt aussen, das tiefere innen; ohne
   Ueberlappung steht ein Stueck in keiner Liste; bei Gleichstand gilt
   die Reihenfolge (spaeter = aussen).
2. Flaeche: unter dem inneren Stueck ersetzt sein Kaefig die Haut (mit der
   Hautnormale), daneben bleibt die Haut — und ein Punkt des aeusseren
   Stuecks, der IM inneren steckt, wird darueber gehoben (Gegenprobe: gegen
   die nackte Haut bliebe er stecken).
3. `G9lagenanfrage`: `getragen`/`rang` aus dem Rumpf, das eigene Stueck und
   Unbekanntes fallen heraus, `spaeter` folgt dem Rang; ein gemerkter Kaefig
   wird nicht zweimal gerechnet (Vorrat je Kennung und Stellung).
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.kollision import G9kollision  # noqa: E402
from Genesis9.lagen import G9lagen  # noqa: E402
from core.dienste.g9lagenanfrage import G9lagenanfrage  # noqa: E402


def gitter(hoehe, x0=-0.5, x1=0.5, z0=-0.5, z1=0.5, schritt=0.01):
    xs = np.arange(x0, x1, schritt)
    zs = np.arange(z0, z1, schritt)
    x, z = np.meshgrid(xs, zs)
    return np.column_stack([x.ravel(), np.full(x.size, hoehe), z.ravel()])


class Kunsthaut:
    @staticmethod
    def koerper():
        haut = gitter(0.0, -1.0, 1.0, -1.0, 1.0)
        normalen = np.tile([0.0, 1.0, 0.0], (len(haut), 1))
        return haut, normalen, G9kollision.baum(haut)


class Einordnen(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.lagen = G9lagen(Kunsthaut.koerper())

    def test_das_hoehere_stueck_liegt_aussen(self):
        hemd, jeans = gitter(0.012), gitter(0.007)
        self.assertEqual(self.lagen.einordnen(hemd, [('jeans', jeans, False)]), (['jeans'], []))
        self.assertEqual(self.lagen.einordnen(jeans, [('hemd', hemd, True)]), ([], ['hemd']))

    def test_ohne_ueberlappung_steht_ein_stueck_in_keiner_liste(self):
        hemd, schuh = gitter(0.012), gitter(0.005, 2.0, 2.4, 2.0, 2.4)
        self.assertEqual(self.lagen.einordnen(hemd, [('schuh', schuh, False)]), ([], []))

    def test_bei_gleichstand_entscheidet_die_reihenfolge(self):
        a, b = gitter(0.0100), gitter(0.0102)
        self.assertEqual(self.lagen.einordnen(a, [('b', b, True)]), ([], ['b']))
        self.assertEqual(self.lagen.einordnen(a, [('b', b, False)]), (['b'], []))


class Flaeche(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.koerper = Kunsthaut.koerper()
        self.lagen = G9lagen(self.koerper)

    def test_ohne_innere_bleibt_die_haut_mit_baum(self):
        self.assertIs(self.lagen.flaeche([]), self.koerper)
        self.assertIs(self.lagen.flaeche([np.zeros((0, 3))]), self.koerper)

    def test_unter_dem_inneren_stueck_ersetzt_sein_kaefig_die_haut(self):
        jeans = gitter(0.007)                       # bedeckt x, z in [-0.5, 0.5)
        punkte, normalen, baum = self.lagen.flaeche([jeans])
        self.assertIsNone(baum)
        self.assertEqual(len(punkte), len(normalen))
        haut_uebrig = punkte[np.abs(punkte[:, 1]) < 1e-9]
        self.assertFalse(((np.abs(haut_uebrig[:, 0]) < 0.45) & (np.abs(haut_uebrig[:, 2]) < 0.45)).any())
        self.assertTrue((np.abs(haut_uebrig[:, 0]) > 0.6).any())
        np.testing.assert_allclose(normalen, np.tile([0.0, 1.0, 0.0], (len(normalen), 1)))

    def test_ein_saum_in_der_jeans_wird_darueber_gehoben(self):
        jeans = gitter(0.007)
        saum = np.array([[0.0, 0.004, 0.0], [0.1, 0.005, 0.1]])   # ueber der Haut, IN der Jeans
        p, n, _ = self.lagen.flaeche([jeans])
        gehoben = G9kollision.hinaus(saum, p, n)
        self.assertTrue((gehoben[:, 1] >= 0.007 + G9kollision.ABSTAND - 1e-9).all(), gehoben)
        haut, hn, hb = self.koerper                # Gegenprobe: nackte Haut hebt nicht
        np.testing.assert_allclose(G9kollision.hinaus(saum, haut, hn, baum=hb), saum)


class Anfrage(SimpleTestCase):
    databases = set()

    def test_getragen_und_rang_aus_dem_rumpf(self):
        rumpf = {'getragen': [{'kennung': 'jeans', 'stil': ['a']}, {'kennung': 'hemd'},
                              {'kennung': 'hut', 'stil': 'x'}, 'unsinn'], 'rang': 1}
        koerper = Kunsthaut.koerper()
        gesehen = []

        def kaefig(kennung, formung, stile, regler):
            gesehen.append((kennung, stile))
            if kennung == 'hut':
                raise ValueError('unbekannt')
            return gitter(0.007 if kennung == 'jeans' else 0.02)

        anfrage = G9lagenanfrage(rumpf, formung=mock.Mock(fingerabdruck=lambda: 'f'),
                                 koerper=koerper, grob=koerper)
        with mock.patch.object(G9lagen, 'kaefig', side_effect=kaefig):
            flaeche, innen, aussen = anfrage.vorbereiten('hemd', [(mock.Mock(koerperhaut=False),
                                                                  gitter(0.012))])
        self.assertEqual(gesehen, [('jeans', ['a']), ('hut', ['x'])])
        self.assertEqual((innen, aussen), (['jeans'], []))
        self.assertIsNone(flaeche[2])          # Haut plus Jeans, Baum neu
        # Vorrat: dieselbe Jeans in derselben Stellung kommt aus dem Speicher.
        with mock.patch.object(G9lagen, 'kaefig', side_effect=kaefig):
            anfrage.vorbereiten('hemd', [(mock.Mock(koerperhaut=False), gitter(0.012))])
        self.assertEqual([k for k, _s in gesehen], ['jeans', 'hut', 'hut'])

    def test_ohne_getragene_stuecke_die_haut_selbst(self):
        koerper = Kunsthaut.koerper()
        anfrage = G9lagenanfrage({}, formung=None, koerper=koerper)
        self.assertEqual(anfrage.vorbereiten('hemd', []), (koerper, [], []))

    def test_spaeter_folgt_dem_rang(self):
        rumpf = {'getragen': [{'kennung': 'a'}, {'kennung': 'b'}], 'rang': 1}
        koerper = Kunsthaut.koerper()
        anfrage = G9lagenanfrage(rumpf, formung=mock.Mock(fingerabdruck=lambda: 'g'),
                                 koerper=koerper, grob=koerper)
        with mock.patch.object(G9lagen, 'kaefig', return_value=gitter(0.0100)), \
                mock.patch.object(G9lagen, 'einordnen', return_value=([], [])) as ein:
            anfrage.vorbereiten('x', [(mock.Mock(koerperhaut=False), gitter(0.01))])
        andere = ein.call_args[0][1]
        self.assertEqual([(k, s) for k, _p, s in andere], [('a', False), ('b', True)])
