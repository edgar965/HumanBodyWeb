# -*- coding: utf-8 -*-
"""Scham-Stück aus Karten verschiedener Größe (Edgar: „Gesamtlauf mit Scham: Objekt", 09.10.2026).

Der Lauf „Asian Female" (Import 2026.10.09.00.13.42) lief mit `scham = objekt` durch und brachte kein Scham-Stück hervor: Die Farbkarte
dieser Datei hat 8192², die Normalenkarte 12288² — `Blendimportscham.haut` verlangte gleich große Bilder und warf „Bild normalen: …"; der
Fehler eines einzelnen Stücks beendet den Import nicht (`Blendimportstuecke.bauen`), das Modell stand ohne Scham da. Seither bringt `haut`
jede Karte auf die Größe der Farbkarte (UV gilt je Bild gleich).

1. Farbe 64², Normalen 128², Rauheit 32²: alle drei Atlasbilder entstehen, gleich groß, `quelle_px` nennt die Farbgröße.
2. Eine Karte, die fehlt, bleibt weg (Dateiname `None`) — es gibt dann kein Atlasbild für sie.
3. Gleich große Karten laufen wie vorher (nichts wird skaliert): das Atlasbild der Normalen hat die Größe der Farb-Atlas.

Sabotage-Gegenprobe: das `resize` streichen → Fall 1 rot (`ValueError`, unverändert zu vorher).

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

from pathlib import Path

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.blendimportscham import Blendimportscham
from core.tests.unit._pruefablage import Pruefablage


class SchamBilderTest(SimpleTestCase):
    databases = set()

    UV = np.array([[[0.10, 0.10], [0.50, 0.10], [0.10, 0.50]]])

    @staticmethod
    def _bild(pfad, groesse, modus='RGB', wert=120):
        farbe = wert if modus == 'L' else (wert, wert // 2, 200)
        Image.new(modus, (groesse, groesse), farbe).save(pfad)
        return str(pfad)

    def test_1_karten_verschiedener_groesse_ergeben_gleich_grosse_atlasbilder(self):
        with Pruefablage.ordner('schambilder_') as ordner:
            ordner = Path(ordner)
            material = {'farbe': self._bild(ordner / 'farbe.png', 64), 'normalen': self._bild(ordner / 'normalen.png', 128),
                        'rauheit': self._bild(ordner / 'rauheit.png', 32, 'L')}
            _uv, quelle, bericht = Blendimportscham(None, {}, material).haut(self.UV, ordner, 'k')
            self.assertEqual(bericht['quelle_px'], [64, 64])
            groessen = {k: Image.open(quelle[k]).size for k in ('farbe', 'normalen', 'rauheit')}
            self.assertEqual(len(set(groessen.values())), 1, groessen)

    def test_2_eine_fehlende_karte_bleibt_weg(self):
        with Pruefablage.ordner('schambilder_') as ordner:
            ordner = Path(ordner)
            material = {'farbe': self._bild(ordner / 'farbe.png', 64), 'normalen': self._bild(ordner / 'normalen.png', 128)}
            _uv, quelle, _bericht = Blendimportscham(None, {}, material).haut(self.UV, ordner, 'k')
            self.assertNotIn('rauheit', quelle)
            self.assertEqual(Image.open(quelle['normalen']).size, Image.open(quelle['farbe']).size)

    def test_3_gleich_grosse_karten_werden_nicht_veraendert(self):
        with Pruefablage.ordner('schambilder_') as ordner:
            ordner = Path(ordner)
            quelle_normal = ordner / 'normalen.png'
            Image.fromarray((np.arange(64 * 64 * 3).reshape(64, 64, 3) % 251).astype(np.uint8)).save(quelle_normal)
            material = {'farbe': self._bild(ordner / 'farbe.png', 64), 'normalen': str(quelle_normal)}
            _uv, quelle, _bericht = Blendimportscham(None, {}, material).haut(self.UV, ordner, 'k')
            atlas = np.asarray(Image.open(quelle['normalen']).convert('RGB'))
            ausschnitt = np.asarray(Image.open(quelle_normal).convert('RGB'))
            # Die Insel (UV 0,1 … 0,5) liegt im Atlas wieder als genau dieser Ausschnitt (Zeilen/Spalten von oben links, `RAND_PX` Rand).
            gesucht = ausschnitt[int((1 - 0.5) * 64) + 1:int((1 - 0.1) * 64) - 1, int(0.1 * 64) + 1:int(0.5 * 64) - 1]
            h, b = gesucht.shape[:2]
            treffer = any((atlas[y:y + h, x:x + b] == gesucht).all()
                          for y in range(atlas.shape[0] - h + 1) for x in range(atlas.shape[1] - b + 1))
            self.assertTrue(treffer, 'der Ausschnitt der Normalen steht unverändert im Atlas')
