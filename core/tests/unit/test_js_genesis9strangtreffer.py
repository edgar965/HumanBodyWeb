# -*- coding: utf-8 -*-
u"""Stranghaar ist anklickbar (20.09.2026), am Quelltext geprüft.

Edgar: „HS Viola Haar ist nicht auswählbar (wenn ich im Modell view darauf
klicke, ist das Modell ausgewählt)". Strähnen sind entartete Dreiecke
`[a, b, b]`; Threes Dreiecksprobe trifft sie nie, der Klick ging auf die
Kopfhaut. `Genesis9strangtreffer` prüft Strecken — als EIGENE Eigenschaft
des Netzes (`netz.raycast`), und die muss jeden Neubau des Netzes überleben:

1. `Genesis9strang.bauen` bringt sie an.
2. `Eigenhaut.binden` (neues SkinnedMesh) und `Genesis9Modell._kleiderBinden`
   (neues Mesh nach dem Skelettbau) ziehen sie mit — ohne das Zweite war
   Viola nach dem Laden der Szene wieder unwählbar (gemessen im Chrome:
   `Object.hasOwn(netz, 'raycast')` false).
3. Die Auswahl zeigt sich auch an einem Material ohne `emissive`
   (`_setSubMeshEmissive`: Grundfarbe der Strähnen).
4. Die gehäuteten Weltpunkte liegen mit Stempel im Netz — 360 ms je Prüfung
   ohne, 15–26 ms mit (Viola, gemessen im Chrome).

Warum Quelltext statt Node: `genesis9strangtreffer.js` hängt an `three`, der
Node-Harness löst das nicht auf (wie `test_genesis9haut_shader`).
Sabotage: `anbringen`-Aufruf aus `Genesis9strang.bauen` nehmen -> Fall 1 rot;
eine der beiden `hasOwn`-Zeilen entfernen -> Fall 2 rot.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class StrangtrefferTest(SimpleTestCase):
    databases = set()

    def test_1_strang_bringt_die_pruefung_an(self):
        text = quelltext('gemeinsam', 'genesis9strang.js')
        self.assertIn("import { Genesis9strangtreffer } from './genesis9strangtreffer.js';", text)
        self.assertIn('return Genesis9strangtreffer.anbringen(netz);', text)
        treffer = quelltext('gemeinsam', 'genesis9strangtreffer.js')
        self.assertRegex(treffer, r'static anbringen\(netz\)\s*\{\s*netz\.raycast = function')
        self.assertIn('distanceSqToSegment(a, b, aufStrahl, aufStrecke)', treffer)

    def test_2_die_pruefung_ueberlebt_jeden_neubau(self):
        haut = quelltext('gemeinsam', 'eigenhaut.js')
        rumpf = re.search(r'gebunden\.userData = netz\.userData;(.*?)return gebunden;', haut, re.S)
        self.assertIsNotNone(rumpf)
        self.assertIn("if (Object.hasOwn(netz, 'raycast')) gebunden.raycast = netz.raycast;", rumpf.group(1))
        modell = quelltext('gemeinsam', 'genesis9modell.js')
        rumpf = re.search(r'const roh = new THREE\.Mesh\(altes\.geometry, altes\.material\);(.*?)'
                          r'this\.clothMeshes\[schluessel\] = this\._einhaengen\(roh, haut\);', modell, re.S)
        self.assertIsNotNone(rumpf, '_kleiderBinden baut das Netz nicht mehr so neu')
        self.assertIn("if (Object.hasOwn(altes, 'raycast')) roh.raycast = altes.raycast;", rumpf.group(1))

    def test_3_auswahl_sichtbar_ohne_emissive(self):
        text = quelltext('scene', 'teilnetz_auswahl.js')
        rumpf = re.search(r'export function _setSubMeshEmissive\(target, color\) \{(.*?)\n\}', text, re.S)
        self.assertIsNotNone(rumpf)
        self.assertIn('if (mat.wireframe && mat.vertexColors)', rumpf.group(1))
        self.assertIn('mat.color.setRGB(1 + 20 * color.r, 1 + 20 * color.g, 1 + 20 * color.b);',
                      rumpf.group(1))

    def test_4_weltpunkte_mit_stempel(self):
        treffer = quelltext('gemeinsam', 'genesis9strangtreffer.js')
        self.assertIn('netz.userData._strangwelt = frisch;', treffer)
        stempel = re.search(r'static _stempel\(netz, lage\) \{(.*?)\n    \}', treffer, re.S)
        self.assertIsNotNone(stempel)
        for quelle in ('lage.version', 'netz.matrixWorld.elements', 'netz.skeleton?.boneMatrices'):
            self.assertIn(quelle, stempel.group(1), f'Stempel ohne {quelle}')
