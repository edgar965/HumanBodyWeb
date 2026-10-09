# -*- coding: utf-8 -*-
"""Scham-Stück aus einem Körper mit mehreren Materialien (Edgar, 09.10.2026: „ich importiere gleich ein Mesh mit Penis" — `Daven.blend`).

Character-Creator-Körper tragen die Haut in VIER Materialien (`Std_Skin_Head`, `…_Body`, `…_Arm`, `…_Leg`, je eigene Bilder 2048²;
gemessen an `Daven.blend`: Körper 14.164 Punkte, 1.946 Flächen `Body`, 2.264 `Leg`). `Blendimportscham` nahm bisher die Bilder des
ERSTEN Materials (der Kopfhaut) für jedes Dreieck — das Stück hätte die Haut des Gesichts getragen. Jetzt gilt das Material, das die
meisten Dreiecke der Auswahl tragen; Dreiecke eines anderen Materials fallen aus dem Stück (ihre UV gehören zu anderen Bildern) und
stehen im Bericht (`material_fremd`).

1. `material_slot` nimmt das häufigste Material der gewählten Dreiecke und zählt die übrigen.
2. Ohne `material` im Körper (ältere Läufe) ist es Material 0, ohne Fremde.
3. Eine Liste von Materialien wird angenommen, ein einzelnes Dict (wie bisher) auch; `material` ist das gewählte.

Sabotage-Gegenprobe: in `material_slot` `argmax` durch `0` ersetzen → Fall 1 rot; die Zählung `fremd` auf 0 → Fall 1 rot; den Zweig für
Listen streichen → Fall 3 rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportscham import Blendimportscham


class SchamMaterialTest(SimpleTestCase):
    databases = set()

    def test_1_das_haeufigste_material_der_auswahl_gilt_und_fremde_werden_gezaehlt(self):
        scham = Blendimportscham(None, {'material': np.array([0, 0, 1, 1, 1, 1, 3])}, [{'n': 'kopf'}, {'n': 'body'}, {}, {'n': 'bein'}])
        je_dreieck = np.array([False, False, True, True, True, True, True])     # gewählt: 4 × Material 1 und 1 × Material 3
        slot, fremd = scham.material_slot(je_dreieck)
        self.assertEqual(slot, 1)
        self.assertEqual(fremd, 1, 'das eine Dreieck von Material 3 fällt aus (die zwei von Material 0 sind nicht gewählt)')

    def test_2_ohne_material_im_koerper_gilt_das_erste(self):
        scham = Blendimportscham(None, {}, {'n': 'einzig'})
        slot, fremd = scham.material_slot(np.array([True, True, False]))
        self.assertEqual((slot, fremd), (0, 0))

    def test_3_liste_und_einzelnes_dict_werden_angenommen(self):
        liste = Blendimportscham(None, {}, [{'n': 'a'}, {'n': 'b'}])
        self.assertEqual(liste.material, {'n': 'a'})
        self.assertEqual(liste.waehle_material(1), {'n': 'b'})
        self.assertEqual(liste.waehle_material(7), {'n': 'b'}, 'ein Index über die Liste hinaus nimmt das letzte')
        einzeln = Blendimportscham(None, {}, {'n': 'x'})
        self.assertEqual(einzeln.material, {'n': 'x'})
        self.assertEqual(einzeln.waehle_material(3), {'n': 'x'})
        leer = Blendimportscham(None, {}, None)
        self.assertEqual(leer.material, {})
