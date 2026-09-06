# -*- coding: utf-8 -*-
u"""`Retargetwahl.figur` und die Ablage je Figur.

WARUM (06.09.2026, Edgar: „bei der 0101_Boden ist die UMA um 90 Grad
verdreht"): Der Retarget-Motor rechnete jede UMA-Anfrage gegen das Skelett
der Datei aus `aktuell.json` (`UmaKleidung_bewegt.glb`, von Roomguest
gesetzt), nicht gegen die Figur in der Szene. Deren Wurzelknoten ist anders
gedreht, die Hüftspur landete in der falschen Achse (Höhe in X, Y ≈ 0), und
jede Szenenfigur lag bei Clips mit großer Wurzeldrehung flach am Boden.

Seither reicht der Browser `figur=<datei>` mit; hier wird geprüft, dass der
Parameter ankommt, dass Pfade abgewiesen werden und dass die Ablage
(`Retargetdaten.ablage`) je Figur ein eigener Name ist — sonst läse die zweite
Figur den Clip der ersten.
"""
from django.test import SimpleTestCase

from core.daten.retargetwahl import Retargetwahl
from core.dienste.retargetdaten import Retargetdaten


class RetargetwahlFigurTest(SimpleTestCase):

    def test_figur_kommt_an_und_bleibt_ohne_angabe_leer(self):
        self.assertIsNone(Retargetwahl({}, 1.68).figur)
        self.assertIsNone(Retargetwahl({'figur': '  '}, 1.68).figur)
        wahl = Retargetwahl({'target': 'uma', 'figur': 'Uma_HumanFemale30.glb'}, 1.68)
        self.assertEqual(wahl.figur, 'Uma_HumanFemale30.glb')
        self.assertIn('Uma_HumanFemale30.glb', repr(wahl))

    def test_pfade_und_fremde_endungen_werden_abgewiesen(self):
        for schlecht in ('../raus.glb', 'a/b.glb', 'figur.json', '.glb'):
            with self.assertRaises(ValueError, msg=schlecht):
                Retargetwahl({'figur': schlecht}, 1.68)

    def test_ablage_ist_je_figur_eine_eigene(self):
        ohne = Retargetdaten('x/clip.bvh', 1.56, ziel='uma').ablage
        eine = Retargetdaten('x/clip.bvh', 1.56, ziel='uma', figur='A.glb').ablage
        andere = Retargetdaten('x/clip.bvh', 1.56, ziel='uma', figur='B.glb').ablage
        self.assertEqual(len({ohne, eine, andere}), 3)
        # Das DEF-Ziel bleibt beim alten Namen — die Ablagen von vorher gelten weiter.
        self.assertEqual(Retargetdaten('x/clip.bvh', 1.56).ablage,
                         Retargetdaten('x/clip.bvh', 1.56, figur=None).ablage)
