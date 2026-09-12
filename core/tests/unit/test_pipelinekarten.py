# -*- coding: utf-8 -*-
u"""Die Karten der 3D-Uploadseite stehen in der Folge des Rangs.

`Pipelinekarten` nimmt den Rang aus `Pipelinevergleich` (Hilfe -> Video to
BVH). Hier steht, was die Seite versprechen darf: jede 3D-Pipeline hat eine
Karte, Rang 1 steht vorn, wer keinen Rang hat, steht hinten, und zu jeder
Karte gibt es eine Vorlage.
"""
from django.template.loader import get_template
from django.test import SimpleTestCase

from core.api.auftraege import PIPELINES_3D
from core.dienste.pipelinekarten import Pipelinekarten
from core.dienste.pipelinevergleich import Pipelinevergleich


class DieKarten(SimpleTestCase):

    databases = set()

    def test_die_3d_pipelines_sind_die_der_uploadseite(self):
        self.assertEqual(sorted(Pipelinekarten.dreid()), sorted(PIPELINES_3D))

    def test_jede_3d_pipeline_hat_genau_eine_karte(self):
        karten = Pipelinekarten.reihenfolge()
        self.assertEqual(len(karten), len(set(karten)))
        self.assertEqual(set(karten),
                         {Pipelinekarten.karte(p) for p in PIPELINES_3D})

    def test_rang_eins_steht_vorn(self):
        erste = next(e for e in Pipelinevergleich.mit_rang() if e['rang'] == 1)
        self.assertEqual(Pipelinekarten.reihenfolge()[0],
                         Pipelinekarten.karte(erste['schluessel']))

    def test_mit_rang_aufsteigend_und_ohne_rang_am_ende(self):
        raenge = [Pipelinekarten.rang(k) for k in Pipelinekarten.reihenfolge()]
        mit = [r for r in raenge if r is not None]
        self.assertEqual(mit, sorted(mit))
        self.assertEqual(raenge[len(mit):], [None] * (len(raenge) - len(mit)))
        self.assertTrue(mit, 'keine Karte mit Rang')

    def test_die_hybrid_karte_steht_bei_ihrer_besseren_haelfte(self):
        u"""hybrid_gvhmr hat einen Rang, hybrid_prompthmr keinen — die eine
        Karte steht beim Rang, nicht am Ende."""
        folge = Pipelinekarten.reihenfolge()
        self.assertEqual(Pipelinekarten.rang('hybrid'),
                         next(e['rang'] for e in Pipelinevergleich.mit_rang()
                              if e['schluessel'] == 'hybrid_gvhmr'))
        self.assertLess(folge.index('hybrid'), len(folge) - 1)

    def test_jede_karte_hat_eine_vorlage(self):
        for vorlage in Pipelinekarten.vorlagen():
            with self.subTest(vorlage=vorlage):
                get_template(vorlage)
