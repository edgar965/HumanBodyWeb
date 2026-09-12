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

    def test_jede_pipeline_des_modells_hat_genau_einen_grundeintrag(self):
        u"""Varianten (12.09.2026, `hybrid_gem` mit GEM-X-Fingern) sind
        Zusatzzeilen — der Grundeintrag je Pipeline bleibt genau einer."""
        erwartet = sorted(wahl[0] for wahl in BVHJob.PIPELINE_CHOICES)
        self.assertEqual(sorted(Pipelinevergleich.schluessel()), erwartet)
        grund = sorted(e['schluessel'] for e in Pipelinevergleich.grundeintraege())
        self.assertEqual(grund, erwartet)

    def test_eine_variante_traegt_namen_und_kennung_ihrer_bestellung(self):
        varianten = [e for e in Pipelinevergleich.alle() if e['variante']]
        self.assertTrue(varianten)
        for e in varianten:
            with self.subTest(pipeline=e['schluessel']):
                self.assertIn(' · ' + e['variante'], e['name'])
                self.assertIn(e['variante_kennung'], e['kennung'])
                self.assertNotEqual(e['rang'], next(
                    g['rang'] for g in Pipelinevergleich.grundeintraege()
                    if g['schluessel'] == e['schluessel']))

    def test_raenge_sind_eins_bis_n_ohne_luecke_nur_fuer_die_mit_ergebnis(self):
        u"""Rang 1..10 fuer die, die ein BVH liefern; die anderen haben keinen
        (Edgar, 12.09.2026: „das ranking von 1-10")."""
        raenge = sorted(e['rang'] for e in Pipelinevergleich.mit_rang())
        self.assertEqual(raenge, list(range(1, len(raenge) + 1)))
        for e in Pipelinevergleich.alle():
            with self.subTest(pipeline=e['schluessel']):
                self.assertEqual(e['rang'] is None, e['zustand'] != 'laeuft')

    def test_rangfolge_ist_nach_rang_sortiert_und_ohne_rang_am_ende(self):
        folge = [e['rang'] for e in Pipelinevergleich.rangfolge()]
        mit = [r for r in folge if r is not None]
        self.assertEqual(mit, sorted(mit))
        self.assertEqual(folge[len(mit):], [None] * (len(folge) - len(mit)))

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
        u"""Eine Variante haengt ihren Zusatz an den Modellnamen an."""
        namen = dict(BVHJob.PIPELINE_CHOICES)
        for e in Pipelinevergleich.alle():
            self.assertTrue(e['name'].startswith(namen[e['schluessel']]), e['name'])
            if not e['variante']:
                self.assertEqual(e['name'], namen[e['schluessel']])

    def test_nicht_gelaufen_nennt_nur_die_ohne_bvh(self):
        for e in Pipelinevergleich.nicht_gelaufen():
            self.assertNotEqual(e['zustand'], 'laeuft')
