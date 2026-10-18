# -*- coding: utf-8 -*-
"""Die Morph-Familien (`hb:`, `mh:`, `sx:`, `uma:`) auf dem Genesis-9-Kaefig: eine Basis, vier Vorsilben (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17.10.2026: „du solltest ALLE Morphs und Regler aus den anderen Projekten portieren und als neue Morphs fuer Genesis nachbauen"): Vier Quellen, ein Weg.
Ein Fehler in der Basis (`G9morphfamilie`) trifft alle vier; ein Fehler in der Registry (`G9morphfamilien`) laesst eine Familie unbemerkt aus dem Bedienfeld fallen.
Geprueft mit Kunstdaten in einem Wegwerf-Ordner, ohne Daz-Bibliothek:

1. Jede Familie hat ihre EIGENEN Speicher (`_gemerkt`, `_liste`) — sonst saehe `mh:` die Liste von `hb:`.
2. `G9morphfamilien.von(name)` findet die Familie an der Vorsilbe, nur bei vorhandener Datei gibt `angaben` Grenzen zurueck (`min`/`max` aus dem Steckbrief: einseitige Regler 0…1).
3. Gelenkversaetze: Eine Datei mit `g_*`-Feldern liefert `gelenke(name, wert)` in ZENTIMETERN, mal |wert|, die Seite des Vorzeichens; ohne die Felder leer.
4. `gelenke(regler)` der Registry summiert ueber Familien; `G9formelnfremd.knochen()` mischt sie in die Daz-Knochenversaetze.
5. Die Bereiche jeder Familie erscheinen nur, wenn belegt, in der Reihenfolge von `BEREICHE`; `reihe` sortiert innerhalb des Bereichs.
"""
import shutil
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.formelnfremd import G9formelnfremd
from Genesis9.hbmorphe import G9hbmorphe
from Genesis9.mhmorphe import G9mhmorphe
from Genesis9.morphfamilien import G9morphfamilien
from Genesis9.sxmorphe import G9sxmorphe
from Genesis9.umamorphe import G9umamorphe


class _Ordner:
    """Den Ablageordner EINER Familie fuer die Dauer eines Tests umlenken."""

    def __init__(self, familie, name):
        self.familie = familie
        self.pfad = Path(__file__).parent / ('tmp_familie_' + name)
        self.alt = familie.ordner

    def __enter__(self):
        shutil.rmtree(self.pfad, ignore_errors=True)
        self.familie.ordner = classmethod(lambda cls: self.pfad)
        self.familie.vergessen()
        return self.pfad

    def __exit__(self, *_):
        self.familie.ordner = self.alt
        self.familie.vergessen()
        shutil.rmtree(self.pfad, ignore_errors=True)


GELENKE = (['l_forearm', 'head'], [[0.0, 0.01, 0.0], [0.0, 0.02, 0.0]], [[0.0, 0.03, 0.0], [0.0, 0.04, 0.0]],
           [[0.0, -0.01, 0.0], [0.0, -0.02, 0.0]], [[0.0, -0.03, 0.0], [0.0, -0.04, 0.0]])


class FamilienBasisTest(SimpleTestCase):
    databases = set()

    def test_1_jede_familie_hat_eigene_speicher(self):
        familien = G9morphfamilien.alle()
        self.assertEqual([f.PRAEFIX for f in familien], ['hb:', 'mh:', 'sx:', 'uma:', 'g1:'], 'g1: = Genesis-1-Kinder (18.10.2026)')
        for a in familien:
            for b in familien:
                if a is not b:
                    self.assertIsNot(a._gemerkt, b._gemerkt, a.__name__ + ' teilt den Speicher mit ' + b.__name__)
                    self.assertIsNot(a._schloss, b._schloss)

    def test_2_registry_findet_die_familie_an_der_vorsilbe(self):
        self.assertIs(G9morphfamilien.von('hb:Torso_Mass'), G9hbmorphe)
        self.assertIs(G9morphfamilien.von('mh:macro_Alter_Kind'), G9mhmorphe)
        self.assertIs(G9morphfamilien.von('sx:Form_01'), G9sxmorphe)
        self.assertIs(G9morphfamilien.von('uma:Body_height'), G9umamorphe)
        self.assertIsNone(G9morphfamilien.von('eigen:x'))
        self.assertIsNone(G9morphfamilien.von('body_bs_BodyMass'))
        self.assertFalse(G9morphfamilien.ist_fremd('alter:gesamt'))

    def test_3_angaben_nur_mit_datei_und_aus_dem_steckbrief(self):
        # SMPL-X leer umlenken: seit 17.10.2026 gibt es die echte Ablage, und `sx:Form_01` stünde darin.
        with _Ordner(G9mhmorphe, 'mh'), _Ordner(G9sxmorphe, 'sx_leer'):
            G9mhmorphe.ablegen('macro_Alter_Kind', [1, 2], [[0.1, 0, 0], [0, 0.1, 0]], [[0, 0, 0], [0, 0, 0]], {'min': 0.0, 'max': 1.0, 'bereich': 'mh_makro'})
            G9mhmorphe.ablegen('head_head-age-decr_incr', [3], [[0.01, 0, 0]], [[-0.01, 0, 0]], {'bereich': 'mh_gesicht'})
            self.assertEqual(G9morphfamilien.angaben('mh:macro_Alter_Kind'), {'min': 0.0, 'max': 1.0})
            self.assertEqual(G9morphfamilien.angaben('mh:head_head-age-decr_incr'), {'min': -1.0, 'max': 1.0})
            self.assertIsNone(G9morphfamilien.angaben('mh:gibt_es_nicht'))
            self.assertIsNone(G9morphfamilien.angaben('sx:Form_01'), 'andere Familie, keine Datei')
            n, d = G9morphfamilien.deltas('mh:macro_Alter_Kind', 0.5)
            np.testing.assert_allclose(d, np.array([[0.05, 0, 0], [0, 0.05, 0]]), atol=1e-7)
            self.assertIsNone(G9morphfamilien.deltas('mh:macro_Alter_Kind', 0.0))

    def test_4_gelenke_in_zentimetern_mal_betrag_und_richtung(self):
        with _Ordner(G9sxmorphe, 'sx'):
            G9sxmorphe.ablegen('Mass_armlaenge', [1], [[0.0, 0.0, 0.0]], [[0.0, 0.0, 0.0]], gelenke=GELENKE)
            plus = G9sxmorphe.gelenke('sx:Mass_armlaenge', 0.5)
            self.assertEqual(sorted(plus), ['head', 'l_forearm'])
            np.testing.assert_allclose(plus['l_forearm']['center_point'], [0.0, 0.5, 0.0], atol=1e-6)         # 0,01 m · 100 · 0,5 = 0,5 cm
            np.testing.assert_allclose(plus['l_forearm']['end_point'], [0.0, 1.5, 0.0], atol=1e-6)
            minus = G9sxmorphe.gelenke('sx:Mass_armlaenge', -1.0)
            np.testing.assert_allclose(minus['head']['center_point'], [0.0, -2.0, 0.0], atol=1e-6)
            self.assertEqual(G9sxmorphe.gelenke('sx:Mass_armlaenge', 0.0), {})
            self.assertEqual(G9sxmorphe.gelenke('hb:fremd', 1.0), {}, 'falsche Vorsilbe')

    def test_5_ohne_gelenkfelder_ist_der_morph_ein_reiner_punktmorph(self):
        with _Ordner(G9hbmorphe, 'hb'):
            G9hbmorphe.ablegen('Waist_Size', [1], [[0.01, 0, 0]], [[0, 0, 0]])
            self.assertEqual(G9hbmorphe.gelenke('hb:Waist_Size', 1.0), {})
            self.assertEqual(G9hbmorphe.steckbrief('Waist_Size')['gelenke'], 0)

    def test_6_registry_summiert_die_gelenke_ueber_familien(self):
        with _Ordner(G9sxmorphe, 'sx'), _Ordner(G9umamorphe, 'uma'):
            G9sxmorphe.ablegen('Mass_a', [1], [[0, 0, 0]], [[0, 0, 0]], gelenke=GELENKE)
            G9umamorphe.ablegen('Body_b', [1], [[0, 0, 0]], [[0, 0, 0]], gelenke=GELENKE)
            summe = G9morphfamilien.gelenke({'sx:Mass_a': 1.0, 'uma:Body_b': 0.5, 'alter:gesamt': 1.0})
            np.testing.assert_allclose(summe['head']['center_point'], [0.0, 2.0 + 1.0, 0.0], atol=1e-6)

    def test_7_formelnfremd_mischt_die_gelenke_in_knochen(self):
        f = G9formelnfremd.__new__(G9formelnfremd)
        f._gemerkt, f._knochenformeln, f.fremd = {}, [], {'sx:Mass_a': 1.0}
        daz = {'head': {'center_point': [0.0, 1.0, 0.0]}}
        with mock.patch.object(G9formelnfremd.__mro__[1], '_knochen', return_value=daz), \
                mock.patch('Genesis9.morphfamilien.G9morphfamilien.gelenke',
                           return_value={'head': {'center_point': [0.0, 2.0, 0.0], 'end_point': [0.0, 3.0, 0.0]}, 'l_forearm': {'center_point': [1.0, 0, 0], 'end_point': [0, 0, 0]}}):
            aus = f.knochen()
        self.assertEqual(aus['head']['center_point'], [0.0, 3.0, 0.0], 'Daz-Versatz plus Familienversatz')
        self.assertEqual(aus['head']['end_point'], [0.0, 3.0, 0.0])
        self.assertEqual(aus['l_forearm']['center_point'], [1.0, 0, 0])

    def test_8_bereiche_nur_belegte_und_nach_reihe_sortiert(self):
        with _Ordner(G9mhmorphe, 'mh'):
            self.assertEqual(G9mhmorphe.bereiche(), [])
            G9mhmorphe.ablegen('b', [1], [[0.01, 0, 0]], [[0, 0, 0]], {'bereich': 'mh_gesicht', 'anzeige': 'Zweiter', 'reihe': 2})
            G9mhmorphe.ablegen('a', [1], [[0.01, 0, 0]], [[0, 0, 0]], {'bereich': 'mh_gesicht', 'anzeige': 'Erster', 'reihe': 1})
            G9mhmorphe.ablegen('c', [1], [[0.01, 0, 0]], [[0, 0, 0]], {'bereich': 'mh_makro', 'anzeige': 'Makro', 'reihe': 0})
            bereiche = G9mhmorphe.bereiche()
            self.assertEqual([b['schluessel'] for b in bereiche], ['mh_makro', 'mh_gesicht'], 'Reihenfolge von BEREICHE, unbelegte fehlen')
            self.assertEqual([r['anzeige'] for r in bereiche[1]['regler']], ['Erster', 'Zweiter'])
