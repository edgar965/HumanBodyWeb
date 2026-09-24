# -*- coding: utf-8 -*-
"""Durchsichtiger Boden mit Platte darunter — versunkene Füße bleiben sichtbar.

WARUM (Edgar, 13.09.2026: „gibt es eine Möglichkeit, beim Boden eine
Transparenzeinstellung zu machen? Die Füße des Modells versinken immer noch
im Boden, die sollen dann nicht verschwinden, sondern noch sichtbar sein.
Vielleicht zwei Balken — Transparenz in % und Transparenz bis zu wieviel cm"):
`studio/bodenuntergrund.js` setzt `opacity = 1 − Transparenz` am Boden
und legt `Tiefe` cm darunter eine undurchsichtige Platte (Kind des Bodens,
gleiche Geometrie). Geprüft am Text, weil die Module `three` importieren:

1. Die Felder `floorTransparenz`/`floorTiefe` gehen durch alle vier Schichten:
   Anlegen (`createFloorTrack`), Laden zur Laufzeit (`applyFloorOverride`),
   Speichern (`Projektdaten._boden`) und Maske (zwei Regler mit Wertanzeige).
2. Material und Größe ziehen die Platte nach (`updateFloorMaterial`,
   `setFloorGeometry` rufen `Bodenuntergrund.nachziehen`).
3. Die Platte ist ein Kind des Bodennetzes, teilt seine Geometrie und trägt
   NICHT `isFloor` (sonst träfe die Bodenauswahl die Platte).

Sabotage-Gegenprobe: `transparenz:` aus `_boden()` nehmen → Fall 1 rot;
`Bodenuntergrund.nachziehen(track)` aus `setFloorGeometry` → Fall 2 rot.
"""

import re

from django.conf import settings
from django.test import SimpleTestCase

STUDIO = settings.BASE_DIR / 'static' / 'viewer' / 'studio'


class BodendurchsichtTest(SimpleTestCase):
    databases = set()

    def test_felder_gehen_durch_alle_schichten(self):
        boden = BodendurchsichtTest._text('spur_boden.js')
        anlegen = boden[
            boden.index('export function createFloorTrack') : boden.index(
                'export function applyFloorOverride'
            )
        ]
        laden = boden[
            boden.index('export function applyFloorOverride') : boden.index(
                'export function updateFloorMaterial'
            )
        ]
        for rumpf in (anlegen, laden):
            self.assertIn('track.floorTransparenz = override', rumpf)
            self.assertIn('track.floorTiefe = override', rumpf)
        speichern = BodendurchsichtTest._text('projekt_daten.js')
        self.assertIn('transparenz: t.floorTransparenz', speichern)
        self.assertIn('tiefe: t.floorTiefe', speichern)
        maske = BodendurchsichtTest._text('eigenschaften/boden.js')
        regler = re.findall(r"_regler\('(prop-floor-[a-z]+)'", maske)
        self.assertEqual(regler, ['prop-floor-transparenz', 'prop-floor-tiefe'])
        self.assertIn("['prop-floor-transparenz', 'floorTransparenz']", maske)
        self.assertIn("['prop-floor-tiefe', 'floorTiefe']", maske)
        self.assertIn('type="range"', maske)

    def test_material_und_groesse_ziehen_die_platte_nach(self):
        boden = BodendurchsichtTest._text('spur_boden.js')
        material = boden[
            boden.index('export function updateFloorMaterial') : boden.index(
                'export async function applyFloorTexture'
            )
        ]
        groesse = boden[
            boden.index('export function setFloorGeometry') : boden.index('export function setFloorSize')
        ]
        self.assertIn('Bodenuntergrund.nachziehen(track)', material)
        self.assertIn('Bodenuntergrund.nachziehen(track)', groesse)

    def test_platte_ist_kind_des_bodens_ohne_isfloor(self):
        platte = BodendurchsichtTest._text('bodenuntergrund.js')
        self.assertIn('track.mesh.add(platte)', platte)
        self.assertIn('platte.geometry = boden.geometry', platte)
        self.assertIn('m.opacity = 1 - durch', platte)
        self.assertNotIn('isFloor = true', platte)

    @staticmethod
    def _text(name):
        return (STUDIO / name).read_text(encoding='utf-8')
