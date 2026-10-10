# -*- coding: utf-8 -*-
"""`Genesis9ersatz`: ein getragenes Ersatz-Stück blendet die Genesis-Augen aus — und wieder ein (08.10.2026), geprüft in Node.

Edgar: „die augen hast du nicht importiert (als extra objekt)". Die Originalaugen kommen als Stück; die Genesis-Augen weichen.

1. Ohne Ersatz-Stück bleibt alles sichtbar, auch Wimpern, Brauen, Mund und Kleidung.
2. Mit einem Stück, dessen Netz `userData.ersetzt = ['augen']` trägt, verschwinden Augäpfel UND Tränenlinie; Wimpern und Brauen bleiben.
3. Zieht man das Stück aus (Netz fehlt in `clothMeshes`), kommen die Augen zurück.
4. Was jemand anders versteckt hat, bleibt versteckt: Die Klasse bringt nur zurück, was sie selbst ausgeblendet hat.
5. Wird die Figur neu gebaut (neue, sichtbare Netze), gilt der Ersatz beim nächsten Aufruf erneut (idempotent).
6. (09.10.2026, „alle Modelle sollen alle Augen kriegen können") Wählt der Nutzer ein Augen-Preset (`_augenGewaehlt`), bleiben die Augen
   der Figur sichtbar und das Ersatz-Stück weicht; „Original Augen vom Modell" bringt es zurück.
7. Ein von `_kleiderBinden` neu gesetztes Stücknetz (noch nicht in `clothMeshes`) weicht trotzdem — die Gruppe genügt.
8. `hatAugen` sagt dem Dropdown, ob „Original Augen vom Modell" angeboten wird.

Sabotage-Gegenprobe: `ersatzVerdeckt` nicht setzen → Fall 3 rot; `traene` aus `NETZE` streichen → Fall 2 rot; die Prüfung
`netz.userData.ersatzVerdeckt` weglassen und immer einblenden → Fall 4 rot; `_stueckWeichen` nicht aufrufen → Fall 6 rot;
in `_stuecke` die Gruppe weglassen → Fall 7 rot. Nicht gelaufen (09.10.2026) — läuft nur auf Ansage.
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

// 6. Ausdrückliche Augenwahl (09.10.2026): die Augen der Figur bleiben, das Ersatz-Stück weicht — und kommt mit
//    „Original Augen vom Modell" zurück. Das Stück steht in der Gruppe UND in clothMeshes (wie in der Szene).
inst = figur();
const ersatz = { name: 'genesis9_kleid_cute_girl_augen_0', visible: true, userData: { ersetzt: ['augen'] } };
inst.group.children.push(ersatz);
inst.clothMeshes['cute_girl_augen/0'] = ersatz;
E.nachziehen(inst);
pruefe('Stück ohne Wahl', sichtbar(inst), 'koerper:1 augen:0 mund:1 wimpern:1 traene:0 brauen:1 kleid:1');
inst._augenGewaehlt = true;
E.nachziehen(inst);
pruefe('Augenwahl', sichtbar(inst), 'koerper:1 augen:1 mund:1 wimpern:1 traene:1 brauen:1 kleid:0');
E.nachziehen(inst);
pruefe('Augenwahl idempotent', sichtbar(inst), 'koerper:1 augen:1 mund:1 wimpern:1 traene:1 brauen:1 kleid:0');
inst._augenGewaehlt = false;
E.nachziehen(inst);
pruefe('Original Augen', sichtbar(inst), 'koerper:1 augen:0 mund:1 wimpern:1 traene:0 brauen:1 kleid:1');

// 7. `_kleiderBinden` setzt ein NEUES Objekt (gleiche userData, sichtbar) in die Gruppe, bevor `clothMeshes` es kennt:
//    die Gruppe genügt, das Stück weicht trotzdem (gemessen im Chrome: es blieb sichtbar).
inst._augenGewaehlt = true;
E.nachziehen(inst);
const neu = { name: ersatz.name, visible: true, userData: ersatz.userData };
inst.group.children[inst.group.children.indexOf(ersatz)] = neu;
E.nachziehen(inst);
pruefe('neu gebundenes Stück weicht', neu.visible ? 1 : 0, 0);

// 8. hatAugen: für das Dropdown „Original Augen vom Modell"
pruefe('hatAugen mit Stück', E.hatAugen(inst), true);
pruefe('hatAugen ohne Stück', E.hatAugen(figur()), false);
pruefe('ohne inst', E.weg(undefined).size, 0);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9ersatzTest(SimpleTestCase):
    databases = set()

    def test_ein_ersatzstueck_blendet_die_genesis_augen_aus_und_wieder_ein(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
