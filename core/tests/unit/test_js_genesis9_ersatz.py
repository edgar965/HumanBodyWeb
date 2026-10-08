# -*- coding: utf-8 -*-
"""`Genesis9ersatz`: ein getragenes Ersatz-Stück blendet die Genesis-Augen aus — und wieder ein (08.10.2026), geprüft in Node.

Edgar: „die augen hast du nicht importiert (als extra objekt)". Die Originalaugen kommen als Stück; die Genesis-Augen weichen.

1. Ohne Ersatz-Stück bleibt alles sichtbar, auch Wimpern, Brauen, Mund und Kleidung.
2. Mit einem Stück, dessen Netz `userData.ersetzt = ['augen']` trägt, verschwinden Augäpfel UND Tränenlinie; Wimpern und Brauen bleiben.
3. Zieht man das Stück aus (Netz fehlt in `clothMeshes`), kommen die Augen zurück.
4. Was jemand anders versteckt hat, bleibt versteckt: Die Klasse bringt nur zurück, was sie selbst ausgeblendet hat.
5. Wird die Figur neu gebaut (neue, sichtbare Netze), gilt der Ersatz beim nächsten Aufruf erneut (idempotent).

Sabotage-Gegenprobe: `ersatzVerdeckt` nicht setzen → Fall 3 rot; `traene` aus `NETZE` streichen → Fall 2 rot; die Prüfung
`netz.userData.ersatzVerdeckt` weglassen und immer einblenden → Fall 4 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9ersatz.js')

SKRIPT = """
const { Genesis9ersatz: E } = await import(MODUL);
const netz = (name) => ({ name, visible: true, userData: {} });
const figur = () => ({
    group: { children: ['koerper', 'augen', 'mund', 'wimpern', 'traene', 'brauen'].map(n => netz('genesis9_' + n + '_char_1_x')) },
    clothMeshes: {},
});
const sichtbar = (inst) => inst.group.children.map(n => n.name.split('_')[1] + ':' + (n.visible ? 1 : 0)).join(' ');
const stueck = () => ({ name: 'genesis9_kleid_cute_girl_augen_0', userData: { ersetzt: ['augen'] } });

// 1. Ohne Ersatz-Stück
let inst = figur();
inst.clothMeshes['cute_girl_shirt/0'] = { userData: { ersetzt: [] } };
E.nachziehen(inst);
pruefe('ohne Ersatz', sichtbar(inst), 'koerper:1 augen:1 mund:1 wimpern:1 traene:1 brauen:1');

// 2. Mit Augen-Stück
inst.clothMeshes['cute_girl_augen/0'] = stueck();
E.nachziehen(inst);
pruefe('mit Augen-Stück', sichtbar(inst), 'koerper:1 augen:0 mund:1 wimpern:1 traene:0 brauen:1');
E.nachziehen(inst);
pruefe('idempotent', sichtbar(inst), 'koerper:1 augen:0 mund:1 wimpern:1 traene:0 brauen:1');

// 3. Ausziehen
delete inst.clothMeshes['cute_girl_augen/0'];
E.nachziehen(inst);
pruefe('ausgezogen', sichtbar(inst), 'koerper:1 augen:1 mund:1 wimpern:1 traene:1 brauen:1');

// 4. Von anderen Versteckt bleibt versteckt
inst = figur();
inst.group.children[2].visible = false;                     // jemand versteckt den Mund
inst.group.children[1].visible = false;                     // und die Augen
inst.clothMeshes['cute_girl_augen/0'] = stueck();
E.nachziehen(inst);
delete inst.clothMeshes['cute_girl_augen/0'];
E.nachziehen(inst);
pruefe('fremd versteckt bleibt', sichtbar(inst), 'koerper:1 augen:0 mund:0 wimpern:1 traene:1 brauen:1');

// 5. Neue Netze nach dem Neubau
inst = figur();
inst.clothMeshes['cute_girl_augen/0'] = stueck();
E.nachziehen(inst);
inst.group.children = inst.group.children.map(n => netz(n.name));          // neu gebaut: alles sichtbar
E.nachziehen(inst);
pruefe('nach dem Neubau', sichtbar(inst), 'koerper:1 augen:0 mund:1 wimpern:1 traene:0 brauen:1');
pruefe('ohne inst', E.weg(undefined).size, 0);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9ersatzTest(SimpleTestCase):
    databases = set()

    def test_ein_ersatzstueck_blendet_die_genesis_augen_aus_und_wieder_ein(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
