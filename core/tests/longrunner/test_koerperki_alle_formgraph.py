# -*- coding: utf-8 -*-
"""`KoerperKI_alle.formgraph.Formgraph` gegen `G9formeln` an der echten Daz-Bibliothek (27.10.2026,
Besitzer Mesh3D-AI).

WARUM: Die Formrechnung der Regler-KI lag an den Vorhersagen 13–17 mm neben G9formung, obwohl jeder
Regler einzeln stimmte: Daz klemmt einen Kanal NACH der Summe aller Formeln. Der Graph rechnet das
nach; weicht er still ab, lernt die KI wieder an einer falschen Figur.

1. Acht Charaktere zugleich, vier Formregler über Daz' Grenze (Spielraum) und ein Familienregler:
   jeder Kanalwert des Graphen gleich `G9formeln.wert` (1e-4) — und die Stellung ist NICHT additiv
   (sonst prüfte der Fall die Klemme nicht).
2. Grundstellung (x = 0): Morph und Knochenkanäle 0.

Sabotage-Gegenprobe (von Hand): in `Formgraph.werte` die Klemme durch `s * f` ersetzen → Fall 1 rot;
in `_kanalangaben` `weit_*` = eigene Grenze für alle Kanäle → Fall 1 rot (Formregler jenseits von
Daz' Grenze).
"""
import sys
import unittest

import numpy as np
import torch
from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.pfade import G9pfade

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.formgraph import Formgraph  # noqa: E402


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek fehlt')
class FormgraphTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from Genesis9.morphablage import G9morphablage
        from Genesis9.skelett import G9skelett
        cls.ablage = a = G9morphablage.holen()
        figuren = sorted(k for k in a.kanaele if k.endswith('_figure_ctrl_Character'))[:8]
        formen = sorted(k for k, x in a.kanaele.items() if 'weit_max' in x and a.hat_deltas(k))[:4]
        cls.daz = figuren + formen
        cls.namen = cls.daz + ['hb:Body_Size']                     # Familienregler: kein Eingang des Graphen
        cls.werte = [0.7] * len(figuren) + [1.6, -1.6, 0.5, -0.3] + [0.3]
        knoten = ['Genesis9'] + [k['name'] for k in G9skelett.roh()]
        cls.fg = Formgraph(cls.namen, np.arange(200), knoten, torch.device('cpu'), log=lambda *_: None)

    def _g9(self, gesetzt):
        from Genesis9.formeln import G9formeln
        f = G9formeln(gesetzt, self.ablage)
        return np.array([f.wert(k) for k in self.fg.kanaele])

    def test_kanalwerte_wie_g9formeln_und_nicht_additiv(self):
        self.assertNotIn(len(self.daz), self.fg.spalten, 'der Familienregler darf kein Eingang sein')
        x = torch.tensor([self.werte], dtype=torch.float32)
        graph = self.fg.werte(x)[0].double().numpy()
        gesetzt = dict(zip(self.daz, self.werte, strict=False))
        soll = self._g9(gesetzt)
        self.assertLess(float(np.abs(graph - soll).max()), 1e-4)
        grund = self._g9({})
        additiv = grund + sum(self._g9({n: v}) - grund for n, v in gesetzt.items())
        self.assertGreater(float(np.abs(soll - additiv).max()), 1e-2,
                           'die Stellung prüft das Zusammenspiel nicht')

    def test_grundstellung_null(self):
        m, k = self.fg(torch.zeros((1, len(self.namen))))
        self.assertLess(float(m.abs().max()), 1e-9)
        self.assertLess(float(k.abs().max()), 1e-6)


if __name__ == '__main__':
    unittest.main()
