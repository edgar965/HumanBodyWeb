# -*- coding: utf-8 -*-
"""Das Scham-Stück glänzt wie die Haut um es herum (`Blendimportschamrauheit`) — an Kunstmaterialien, ohne Django-Datenbank und Blender.

Edgar, 10.10.2026: „Rauheit: Der Körper hat eine Rauheitskarte, das Stück nicht." Gemessen am BodyParts3D-Körper (OBJ `Ns 30`): Blender kennt
dort keine Karte, nur die Zahl 0,827 am Eingang „Roughness"; der Schritt „haut" backt sie in die Kacheln (211 von 255), der Hautshader nimmt
Karte mal 1,0. Das Stück fiel im Browser auf den Vorgabewert 0,6 zurück.

1. Ohne Rauheitskarte und mit `rauheit_wert` 0,827 bekommt das Material `shininess` = 1 − 0,827; `G9materialkanaele.animationen` schreibt daraus
   „Glossy Roughness" 0,827 — den Wert, den der Browser ohne Rauheitskarte als Rauheit nimmt.
2. Mit Rauheitskarte (Character-Creator-Körper) bleibt das Material unberührt: die Karte des Atlas gilt.
3. Ohne Zahl bleibt es, wie es war (`shininess` None); Unsinn (Text, Wahrheitswert) wird nicht zur Rauheit; Werte außerhalb 0 … 1 werden begrenzt.

Sabotage-Gegenprobe (nicht gelaufen): die Bedingung `quelle.get('rauheit')` weglassen macht Fall 2 rot; `1.0 -` weglassen macht Fall 1 rot.
"""

from django.test import SimpleTestCase
from Genesis9.materialkanaele import G9materialkanaele

from core.dienste.blendimportschamrauheit import Blendimportschamrauheit as R


class SchamrauheitTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _material():
        return {'name': 'X_Mat', 'farbe': (1.0, 1.0, 1.0), 'bild': 'farbe.jpg', 'shininess': None, 'opacity': None}

    def test_1_ohne_karte_geht_die_zahl_der_haut_ins_material(self):
        material = R.anwenden(self._material(), {'farbe': 'f.jpg', 'rauheit_wert': 0.827})
        self.assertAlmostEqual(material['shininess'], 0.173, places=6)
        animationen = G9materialkanaele.animationen('Gruppe', material, False)
        werte = {a['url'].rsplit('/channels/', 1)[1]: a['keys'][0][1] for a in animationen}
        self.assertAlmostEqual(werte['Glossy Roughness/value'], 0.827, places=4)

    def test_2_mit_karte_bleibt_das_material_unberuehrt(self):
        material = R.anwenden(self._material(), {'rauheit': 'rauheit.png', 'rauheit_wert': 0.5})
        self.assertIsNone(material['shininess'])

    def test_3_ohne_zahl_unsinn_und_grenzen(self):
        self.assertIsNone(R.anwenden(self._material(), {})['shininess'])
        self.assertIsNone(R.anwenden(self._material(), {'rauheit_wert': 'rau'})['shininess'])
        self.assertIsNone(R.anwenden(self._material(), {'rauheit_wert': True})['shininess'])
        self.assertEqual(R.anwenden(self._material(), {'rauheit_wert': 1.7})['shininess'], 0.0)
        self.assertEqual(R.anwenden(self._material(), {'rauheit_wert': -0.2})['shininess'], 1.0)
