# -*- coding: utf-8 -*-
u"""Zwei Zusagen der Szene an Genesis 9 (20.09.2026), am Quelltext geprüft.

1. `Genesis9lauf` (scene/genesis9/genesis9lauf.js): ein Lauf, dessen Figur
   Rückgängig ersetzt hat, meldet nichts. Edgar: „undo funktioniert nicht bei
   den HB Morphs" — Rückgängig, während der Server noch rechnet, baut die
   Szene aus dem Schnappschuss neu (dieselbe Kennung, ANDERE Instanz); kam
   der alte Lauf zurück, schrieb `danach` (`nachziehen`) die Werte der
   verwaisten Instanz in die Schieber und `markDirty` legte einen Stand davon
   an: Regler „100 %", Figur ohne den Morph (gemessen im Chrome). Jetzt steht
   zwischen `await aktion()` und `markDirty()` der Wächter `inSzene(inst)`,
   der die Instanz mit `state.characters` vergleicht.

2. `Genesis9netz` (gemeinsam/genesis9netz.js): Haarkarten bekommen MSAA-
   Deckung (`alphaToCoverage`) statt eines Alpha-Schnitts bei 0,3. Edgar:
   „Kin Haar ist dünn, das sind ja krebskranke Haare" — Kins Deckkraftbild
   hat im Mittel 0,05, nur 5 % der Texel über 0,5; der Schnitt ließ von jeder
   Karte ein paar Fäden. Brauen und Wimpern (`WEICH`) bleiben weich.

Warum Quelltext statt Node: beide Module hängen an `../undo.js` → `state.js`
→ `three/addons` bzw. an `three` — der Node-Harness löst das nicht auf
(wie `test_genesis9haut_shader`). Sabotage: `inSzene`-Zeile entfernen →
Fall 1 rot; `alphaToCoverage` zurück auf `alphaTest = 0.3` → Fall 2 rot.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class Genesis9laufUndHaarkartenTest(SimpleTestCase):
    databases = set()

    def test_1_verwaiste_figur_meldet_nichts(self):
        text = quelltext('scene', 'genesis9', 'genesis9lauf.js')
        rumpf = re.search(r'await aktion\(\);(.*?)markDirty\(\);', text, re.S)
        self.assertIsNotNone(rumpf, 'markDirty folgt nicht mehr auf aktion()')
        self.assertIn('inSzene(inst)', rumpf.group(1), 'kein Wächter zwischen aktion und markDirty')
        self.assertIn('lauf.nachholen = null; return;', rumpf.group(1), 'der gemerkte Wunsch verfällt nicht')
        self.assertRegex(text, r'static inSzene\(inst\)\s*\{\s*'
                               r'return state\.characters\.get\(inst\.id\) === inst;')
        self.assertIn("import { state } from '../state.js';", text)

    def test_2_haarkarten_mit_msaa_deckung(self):
        text = quelltext('gemeinsam', 'genesis9netz.js')
        zweig = re.search(r'if \(bilder\.alpha\) \{(.*?)\n        \}\n        return material;', text, re.S)
        self.assertIsNotNone(zweig, 'der Alpha-Zweig in material() fehlt')
        alpha = zweig.group(1)
        weich, _, karten = alpha.partition('} else {')
        self.assertIn('WEICH', weich)
        self.assertIn('alphaTest = 0.02', weich)
        self.assertIn('depthWrite = false', weich)
        self.assertIn('material.alphaToCoverage = true;', karten)
        self.assertNotIn('alphaTest = 0.3', alpha)
        self.assertNotIn('material.transparent = true', karten)
        self.assertIn("antialias: true", quelltext('gemeinsam', 'buehne.js'),
                      'alphaToCoverage braucht MSAA — die Bühne muss antialias: true setzen')
