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

# 4. `gcGetragen` (24.09.2026): die GarmentCode-Stuecke einer Genesis-9-Figur fuer die
# Lagenrechnung — nur Genesis 9, nur Stuecke, deren Netz noch haengt (die Ablage
# vergisst geloeschte nicht), Ordner und Datei aus der Rig-Adresse, `stand` mit.
# Sabotage: den Haengt-Filter weglassen -> 'geloeschtes faellt heraus' rot.
GC = """
const { Genesis9lagen } = await import(MODUL);
const inst = { quelle: 'genesis9', clothMeshes: { gc_hose: {} },
    gcStuecke: {
        gc_hose: { stueck: "hose", stand: "7",
                   rig_url: "/api/garmentcode/datei/hose_g9/hose_g9_sim_rig.json/" },
        gc_rock: { stueck: 'rock', rig_url: '/api/garmentcode/datei/rock_g9/rock_g9_sim_rig.json/' } } };
pruefe('geloeschtes faellt heraus', Genesis9lagen.gcGetragen(inst),
       [{ stueck: 'hose', ordner: 'hose_g9', rig_datei: 'hose_g9_sim_rig.json', stand: '7' }]);
pruefe('nur Genesis 9', Genesis9lagen.gcGetragen({ ...inst, quelle: 'modell' }), []);
pruefe('ohne Stuecke leer', Genesis9lagen.gcGetragen({ quelle: 'genesis9' }), []);
console.log(JSON.stringify({ ok: true }));
"""

# 5. `nachGcBau` (24.09.2026): nach einem GarmentCode-Bau jedes Daz-Stueck neu holen, das
# NICHT als innere Lage in den Bau einging (`ueber_getragene`) — auch das Haar (Edgar: Damiras
# Haare lagen unter dem Kleid); mit Kaskade; ohne Stueck oder auf HumanBody nichts.
# Sabotage: den Filter weglassen -> 'bh blieb darunter' rot; nur Kleidung -> Haar fehlt, rot.
NACH_GC = """
const { Genesis9lagen } = await import(MODUL);
const rufe = [];
const inst = { quelle: 'genesis9', kleidung: { bh: {}, slip: {}, kin_hair: {}, schuhe: {} }, lagen: {},
    anziehen: async (k, w, s, kaskade) => { rufe.push([k, s, kaskade]); } };
const unter = ['/pfad/hose_rig.json', 'bh', 'slip'];
const neu = await Genesis9lagen.nachGcBau(inst, ['anzug'], unter);
pruefe('bh blieb darunter, haar und schuhe neu', neu, ['kin_hair', 'schuhe']);
pruefe('mit Kaskade', rufe, [['kin_hair', null, true], ['schuhe', null, true]]);
const alle = ['bh', 'slip', 'kin_hair', 'schuhe'];
pruefe('ohne Haken alles', await Genesis9lagen.nachGcBau(inst, 'anzug'), alle);
pruefe('ohne Stueck nichts', await Genesis9lagen.nachGcBau(inst, [], []), []);
pruefe('HumanBody: nichts', await Genesis9lagen.nachGcBau({ ...inst, quelle: 'modell' }, 'anzug', []), []);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9lagenTest(SimpleTestCase):
    databases = set()

    def test_anfrage_nachziehen_nachausziehen(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})

    def test_garmentcode_stuecke_fuer_die_lagen(self):
        self.assertEqual(MODUL.laufen(GC), {'ok': True})

    def test_nach_einem_garmentcode_bau_kommen_die_aeusseren_daz_stuecke_neu(self):
        self.assertEqual(MODUL.laufen(NACH_GC), {'ok': True})
