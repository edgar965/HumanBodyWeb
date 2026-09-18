# -*- coding: utf-8 -*-
"""`Bodenstand`: der Bodenfix gilt der ANIMIERTEN Figur, nicht der gewählten.

WARUM (Edgar, 13.09.2026: „Animation immer auf Bodenniveau funktioniert
nicht"): `Szenenschleife.aufDenBoden` nahm `fn._selectedInst()`. Wer
während der Wiedergabe eine zweite Figur anklickte oder Escape drückte,
sah die Tänzerin versinken. Geprüft mit Attrappen (ohne Netz → tiefster
Knochen, siehe `test_js_koerpertiefe`):

1. Die animierte Figur (`_animatedCharId`) wird um ihren tiefsten Punkt
   gehoben — auch wenn eine andere gewählt ist; die gewählte bleibt.
2. Ohne `_animatedCharId` gilt die gewählte; ohne beide das Skelett der
   Seite (Einzelkörper-Weg).
3. `skelett` geht vor `rigifySkeleton` (SMPL/MakeHuman/UMA haben nur das eine).

Sabotage-Gegenprobe: in `figur()` `zustand.selectedCharacterId` zuerst →
Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul("scene", "bodenstand.js")

SKRIPT = """
const { Bodenstand: B } = await import(MODUL);
const nah = (was, a, b) => {
    if (Math.abs(a - b) > 1e-9) throw new Error(was + ': ' + a + ' statt ' + b);
};
// Eine Figur ohne Netz: Wurzel bei y, tiefster Knochen `tief` darunter.
const figur = (y, tief, feld = 'skelett') => {
    const wurzel = { isBone: true, position: { y }, updateWorldMatrix() {},
        getWorldPosition(v) { v.y = this.position.y; },
        traverse(f) { f(this); f({ isBone: true, getWorldPosition(v) { v.y = wurzel.position.y - tief; } }); } };
    return { bodyMesh: null, [feld]: { rootBone: wurzel } };
};
const v = { y: 0 };
// 1. animiert ≠ gewaehlt
const taenzerin = figur(0.9, 1.0), stehend = figur(1.0, 1.0);
const zustand = { _animatedCharId: 't', selectedCharacterId: 's',
    characters: new Map([['t', taenzerin], ['s', stehend]]) };
nah('verschoben', B.richten(zustand, v), -0.1);
nah('taenzerin', taenzerin.skelett.rootBone.position.y, 1.0);
nah('stehend unveraendert', stehend.skelett.rootBone.position.y, 1.0);
nah('zweiter Takt tut nichts', B.richten(zustand, v), 0);
// 2. ohne _animatedCharId die gewaehlte; ohne beide die Seite
const z2 = { _animatedCharId: null, selectedCharacterId: 's', characters: new Map([['s', figur(1.2, 1.0)]]) };
nah('gewaehlt', B.richten(z2, v), 0.2);
const seite = figur(0.7, 1.0, 'rigifySkeleton');
const z3 = { _animatedCharId: null, selectedCharacterId: null, characters: new Map(),
             rigifySkeleton: seite.rigifySkeleton };
nah('seite', B.richten(z3, v), -0.3);
nah('ohne alles', B.richten({ _animatedCharId: null, selectedCharacterId: null, characters: new Map() }, v), 0);
// 3. skelett vor rigifySkeleton
const beide = figur(1.0, 1.0);
beide.rigifySkeleton = { rootBone: { position: { y: 5 }, updateWorldMatrix() {}, traverse() {} } };
if (B.wurzel(zustand, beide) !== beide.skelett.rootBone) throw new Error('skelett zuerst');
const nurRig = figur(1.0, 1.0, 'rigifySkeleton');
if (B.wurzel(zustand, nurRig) !== nurRig.rigifySkeleton.rootBone) throw new Error('rigify als Ersatz');
console.log(JSON.stringify({ ok: true }));
"""


class BodenstandTest(SimpleTestCase):
    def test_die_animierte_figur_kommt_auf_den_boden(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get("ok"))
