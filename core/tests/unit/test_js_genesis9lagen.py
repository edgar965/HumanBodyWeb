# -*- coding: utf-8 -*-
u"""`Genesis9lagen` (Anziehreihenfolge und Lagen der Daz-Stücke, 19.09.2026).

In Node mit einer Figur-Attrappe, die `anziehen` nur mitschreibt:

1. `anfrage`: die anderen Stücke in Anziehreihenfolge, `rang` = eigener Platz;
   ein Stück, das noch nicht in `kleidung` steht, bekommt den Platz am Ende.
2. `nachziehen` merkt `innen`/`aussen` und holt die äußeren Stücke neu — ohne
   Kaskade (`false`), damit kein Kreis entsteht; ohne `kaskade` holt es nichts.
3. `nachAusziehen` holt genau die Stücke neu, die das ausgezogene als `innen`
   führten, und vergisst dessen Lagen.

Sabotage-Gegenprobe: `kaskade` in `nachziehen` ignorieren → Fall 2 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9lagen.js')

SKRIPT = """
const { Genesis9lagen } = await import(MODUL);
const kleidung = { jeans: { variante: 'navy', stil: 'a', stile: { pose: 'p' }, regler: { w: 1 } },
                   hemd: { variante: '' }, hut: {} };

// 1. Anfrage
let a = Genesis9lagen.anfrage(kleidung, 'hemd');
pruefe('rang', a.rang, 1);
pruefe('getragen', a.getragen, [
    { kennung: 'jeans', stil: ['a', 'p'], regler_stueck: { w: 1 } },
    { kennung: 'hut', stil: [], regler_stueck: {} }]);
pruefe('neu am Ende', Genesis9lagen.anfrage(kleidung, 'schal').rang, 3);
pruefe('leer', Genesis9lagen.anfrage({}, 'x'), { rang: 0, getragen: [] });

// 2. nachziehen
const rufe = [];
const inst = { kleidung, lagen: {},
               anziehen: async (k, w, s, kaskade) => { rufe.push([k, s, kaskade]); } };
await Genesis9lagen.nachziehen(inst, 'jeans', { innen: [], aussen: ['hemd', 'weg'] }, 2, true);
pruefe('lagen gemerkt', inst.lagen.jeans, { innen: [], aussen: ['hemd', 'weg'] });
pruefe('aeussere neu, ohne Kaskade, nur getragene', rufe, [['hemd', 2, false]]);
rufe.length = 0;
await Genesis9lagen.nachziehen(inst, 'hemd', { innen: ['jeans'], aussen: ['hut'] }, null, false);
pruefe('ohne Kaskade nichts', rufe, []);
pruefe('hemd liegt ueber jeans', inst.lagen.hemd.innen, ['jeans']);

// 3. nachAusziehen
inst.lagen.hut = { innen: ['hemd'], aussen: [] };
delete kleidung.jeans;
await Genesis9lagen.nachAusziehen(inst, 'jeans', 1);
pruefe('ueber der jeans lag das hemd', rufe, [['hemd', 1, false]]);
pruefe('lagen der jeans vergessen', 'jeans' in inst.lagen, false);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9lagenTest(SimpleTestCase):
    databases = set()

    def test_anfrage_nachziehen_nachausziehen(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})
