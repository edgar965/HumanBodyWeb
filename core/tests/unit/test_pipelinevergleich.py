# -*- coding: utf-8 -*-
u"""Der Pipelinevergleich (Hilfe -> Video to BVH) ist vollstaendig und stimmig.

* Jede Pipeline aus `BVHJob.PIPELINE_CHOICES` hat genau einen Eintrag —
  eine neue Pipeline ohne Eintrag faellt hier auf, nicht erst auf der Seite.
* Die Raenge sind 1..n ohne Luecke und ohne Doppel.
* Jeder Eintrag traegt alle Felder; wer laeuft, hat Messwerte; wer nicht
  laeuft, hat einen Grund.
"""
import unittest

from core.dienste.pipelinevergleich import Pipelinevergleich
from core.models import BVHJob


class DerVergleich(unittest.TestCase):

    def test_jede_pipeline_des_modells_hat_genau_einen_eintrag(self):
        erwartet = sorted(wahl[0] for wahl in BVHJob.PIPELINE_CHOICES)
        self.assertEqual(sorted(Pipelinevergleich.schluessel()), erwartet)
        self.assertEqual(len(Pipelinevergleich.schluessel()), len(set(erwartet)))

    def test_raenge_sind_eins_bis_n_ohne_luecke(self):
        raenge = sorted(e['rang'] for e in Pipelinevergleich.alle())
        self.assertEqual(raenge, list(range(1, len(raenge) + 1)))

    def test_rangfolge_ist_nach_rang_sortiert(self):
        folge = [e['rang'] for e in Pipelinevergleich.rangfolge()]
        self.assertEqual(folge, sorted(folge))

    def test_jeder_eintrag_traegt_alle_felder(self):
        for e in Pipelinevergleich.alle():
            with self.subTest(pipeline=e['schluessel']):
                for feld in Pipelinevergleich.FELDER:
                    self.assertIn(feld, e)
                self.assertIn(e['zustand'], Pipelinevergleich.ZUSTAND)
                self.assertEqual(e['zustand_text'],
                                 Pipelinevergleich.ZUSTAND[e['zustand']])
                self.assertTrue(e['vorteile'] and e['nachteile'] and e['begruendung'])

    def test_wer_laeuft_hat_messwerte_wer_nicht_hat_einen_grund(self):
        for e in Pipelinevergleich.alle():
            with self.subTest(pipeline=e['schluessel']):
                if e['zustand'] == 'laeuft':
                    self.assertIsNotNone(e['dauer_s'])
                    self.assertIsNotNone(e['ueberlagerung_px'])
                    self.assertIsNotNone(e['gelenke'])
                else:
                    self.assertTrue(e['zustand_grund'])

    def test_namen_kommen_aus_dem_modell(self):
        namen = dict(BVHJob.PIPELINE_CHOICES)
        for e in Pipelinevergleich.alle():
            self.assertEqual(e['name'], namen[e['schluessel']])

    def test_nicht_gelaufen_nennt_nur_die_ohne_bvh(self):
        for e in Pipelinevergleich.nicht_gelaufen():
            self.assertNotEqual(e['zustand'], 'laeuft')
