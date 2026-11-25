# -*- coding: utf-8 -*-
u"""`G9formungsfolge` und `G9reglerzugfeld` — die Sofortschau eines Reglerzugs (25.11.2026, Edgar: „alle regler unter 0,2 s“) gegen die volle Rechnung, an der Grundfigur.

1. Die Folge gibt dieselben Morphwerte und Posenkanäle wie die volle Stellung und dieselben Punkte (unter 1e-6 mm) — Daz-Regler mit Formeln, Proportion mit Knochenskalierung, hb:- und mh:-Regler.
2. Ohne Knochenänderung sind es dieselben Matrizen (`gleiche_knochen`), mit einer Proportion nicht.
3. Das Feld des Körpers ist der Unterschied der Browserpunkte der vollen Antwort (unter 0,02 mm); was er nicht berührt, fehlt (Nase: keine Augen, kein Mund).
4. `G9morphsumme.feld` gibt die Summe von `addieren` (auch bei mehrfach genannten Punkten, Nummern über der Punktzahl zählen nicht).

Sabotage-Gegenprobe (nicht gefahren): in `G9formelleser.erreicht` nur die geänderten Kanäle selbst zurückgeben → Fall 1 rot (Steuerregler); in `matrizen` immer die alten nehmen → Fall 1 rot
(Proportion); in `duenn` die Schwelle auf 1 m → Fall 3 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import unittest

import torch
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.formung import G9formung  # noqa: E402
from Genesis9.formungsfolge import G9formungsfolge  # noqa: E402
from Genesis9.koerpernetz import G9koerpernetz  # noqa: E402
from Genesis9.morphablage import G9morphablage  # noqa: E402
from Genesis9.morphsumme import G9morphsumme  # noqa: E402
from Genesis9.pfade import G9pfade  # noqa: E402
from Genesis9.reglerzugfeld import G9reglerzugfeld  # noqa: E402

BASIS = {'BaseMasculine_figure_ctrl_Character': 1.0}


@unittest.skipUnless(torch.cuda.is_available() and G9pfade.vorhanden(), 'braucht die Grafikkarte und Daz’ Bibliothek')
class FormungsfolgeTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def namen():
        u"""Regler, die es in der Ablage gibt: einer mit Formeln, eine Proportion, dazu die Nasen der Familien."""
        kanaele = G9morphablage.holen().kanaele
        return [n for n in ('body_bs_ProportionLegsLength', 'body_bs_BodyTone', 'body_ctrl_BodyMuscular') if n in kanaele] + ['hb:Nose_BaseSizeX', 'mh:nose_nose-trans-in_out']

    def paar(self, name, wert=0.4):
        voll = G9formung(dict(BASIS, **{name: wert}))
        return voll, G9formungsfolge(dict(BASIS, **{name: wert}), self.alt)

    def setUp(self):
        self.alt = G9formung(dict(BASIS))

    def test_1_folge_gleich_voll(self):
        for name in self.namen():
            voll, folge = self.paar(name)
            self.assertEqual(voll.morphwerte(), folge.morphwerte(), name)
            self.assertEqual(voll.formeln.posen(), folge.formeln.posen(), name)
            self.assertLess(float((voll.punkte() - folge.punkte()).abs().max()), 1e-9, name)

    def test_2_gleiche_knochen(self):
        self.assertTrue(self.paar('hb:Nose_BaseSizeX')[1].gleiche_knochen)
        self.assertFalse(self.paar('body_bs_ProportionLegsLength')[1].gleiche_knochen)

    def test_3_feld_gleich_der_vollen_antwort(self):
        voll, folge = self.paar('hb:Nose_BaseSizeX')
        feld = G9reglerzugfeld(self.alt, folge).rechnen()
        a, b = (G9koerpernetz(f).bauen() for f in (self.alt, voll))
        soll = b['punkte'] - a['punkte']
        ist = torch.zeros_like(soll)
        ist[feld['koerper'][0].long()] = feld['koerper'][1].to(soll.dtype)
        self.assertLess(float((soll - ist).norm(dim=1).max()), 2e-5)
        self.assertGreater(float(soll.norm(dim=1).max()), 1e-4, 'die Probe bewegt wirklich etwas')
        self.assertNotIn('augen', feld['anhaenge'])
        self.assertNotIn('mund', feld['anhaenge'])

    def test_4_summe(self):
        g = torch.Generator(device='cuda').manual_seed(3)
        paare = [(torch.sort(torch.randperm(60, device='cuda', generator=g)[:20])[0].to(torch.int32), torch.rand((20, 3), device='cuda', generator=g), w) for w in (0.3, -1.2, 0.0, 2.0)]
        soll = torch.zeros((50, 3), dtype=torch.float64, device='cuda')
        for nummern, deltas, wert in paare:
            G9morphsumme.addieren(soll, nummern, deltas, wert)
        self.assertLess(float((G9morphsumme.feld(50, paare, soll.device) - soll).abs().max()), 1e-6)
