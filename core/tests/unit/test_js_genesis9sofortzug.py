# -*- coding: utf-8 -*-
u"""`Genesis9sofortzug` — ein Reglerzug an der stehenden Figur (25.11.2026, Edgar: „alle regler unter 0,2 s“), geprüft in Node.

1. `wege`: plus und minus getrennt ab 0, ein Weg über die Null in zwei Teilen; `alter:` ein Weg (`n`).
2. `zeigen`: Stand → `inst.regler` mit dem Gewicht Weg / (bis − von), je Netz gegen SEINEN Stand; ein Feld mit anderer Punktzahl zählt nicht; zurück auf dem Stand steht die Ruhelage.
3. `plan`: nur, wenn zu jedem gezogenen Kanal beide Hälften da sind und der Server `genau` sagt — dann die berührten Stücke; mit GarmentCode-Stück oder unvollständigem Feld null.
4. `unberuehrt`/`bleibt`: nur bei `ruhig` und lauter `null`-Feldern; `offen` (Strang, Requisit) ist berührt; `bleibt` setzt den Stand des Stücks weiter und seinen Lauf.

Sabotage-Gegenprobe (nicht gefahren): in `wege` das `Math.max(a, 0)` streichen → Fall 1 rot; in `_netz` die Punktzahl nicht vergleichen → Fall 2 rot; in `plan` `genau` nicht prüfen →
Fall 3 rot; in `unberuehrt` `=== null` durch `!f` ersetzen → Fall 4 rot (ein fehlendes Feld gälte als unberührt). Geschrieben, nicht gelaufen (nur auf Ansage).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9sofortzug.js')

SKRIPT = """
const { Genesis9sofortzug: S } = await import(MODUL);
const rund = liste => Array.from(liste).map(x => Math.round(x * 1e4) / 1e4);

// 1. Wege
pruefe('plus', S.wege('a', 0.2, 0.5).map(([s, w]) => [s, rund([w])[0]]), [['+', 0.3]]);
pruefe('minus', S.wege('a', 0, -0.5), [['-', -0.5]]);
pruefe('über die Null', S.wege('a', -0.5, 0.25), [['+', 0.25], ['-', 0.5]]);
pruefe('unlinear', S.wege('alter:gesamt', -0.5, 0.25), [['n', 0.75]]);

// Ein Netz aus zwei Punkten, ohne Normalen (`Genesis9normalen` braucht einen Index: es gibt keinen)
const netz = (stand) => {
    const lage = { array: Float32Array.from([0, 0, 0, 1, 1, 1]), count: 2, needsUpdate: false };
    const geo = { userData: {}, index: null, boundingSphere: 'alt', boundingBox: 'alt', getAttribute: n => (n === 'position' ? lage : null), attributes: { position: lage } };
    S.merken([{ geometry: geo }], stand);
    return { geometry: geo, userData: {}, lage };
};
const feld = (d, punkte = 2) => ({ n: Uint32Array.from([1]), d: Float32Array.from(d), punkte });
const koerper = netz({ nase: 0.1 }), hose = netz({ nase: 0.3 }), haar = netz({ nase: 0.1 });
const inst = { bodyMesh: koerper, anhangNetze: {}, clothMeshes: { 'hose/0': hose, 'haar/0': haar }, regler: { nase: 0.6 }, _lauf: 7, getragen: () => ['hose', 'haar'] };

// 2. zeigen
S.eintragen(inst, 'nase', '+', { ziel: 1, koerper: { von: 0.1, bis: 1.1, fassung: 1, genau: true, ruhig: true, wechsel: { m: 0.5 }, feld: feld([1, 0, 0]) } });
S.eintragen(inst, 'nase', '+', { rest: { von: 0.1, bis: 1.1, fassung: 2, ruhig: true, anhaenge: {}, stuecke: { hose: [feld([0, 2, 0])], haar: [null] } } });
S.zeigen(inst);
pruefe('Körper: 0,1 → 0,6 ist der halbe Weg', rund(koerper.lage.array), [0, 0, 0, 1.5, 1, 1]);
pruefe('Hose gegen ihren Stand 0,3', rund(hose.lage.array), [0, 0, 0, 1, 1.6, 1]);
pruefe('Haar unberührt', rund(haar.lage.array), [0, 0, 0, 1, 1, 1]);
pruefe('trägt die Sofortschau', [S.zeigt(koerper), S.zeigt(haar)], [true, false]);
inst.regler.nase = 0.1;
S.zeigen(inst);
pruefe('zurück auf dem Stand', rund(koerper.lage.array), [0, 0, 0, 1, 1, 1]);
const fremd = netz({ nase: 0.1 });
inst.clothMeshes['hose/0'] = Object.assign(fremd, {});
fremd.geometry.attributes.position.count = 3;
inst.regler.nase = 0.6;
S.zeigen(inst);
pruefe('andere Punktzahl: kein Feld', rund(fremd.lage.array), [0, 0, 0, 1, 1, 1]);
inst.clothMeshes['hose/0'] = hose;

// 3. plan
pruefe('berührt ist nur die Hose', S.plan(inst).stuecke, ['hose']);
S.werte(inst, S.plan(inst).eintraege);
pruefe('Morphwerte mitgezogen', rund([inst.morphwerte.m]), [0.25]);
inst.gcStuecke = { gc: {} };
pruefe('mit GarmentCode-Stück: der ganze Zug', S.plan(inst), null);
inst.gcStuecke = {};
inst.regler.kinn = 0.2;
pruefe('ein Kanal ohne Feld: der ganze Zug', S.plan(inst), null);
delete inst.regler.kinn;
S.feld(inst, 'nase', '+').koerper.genau = false;
pruefe('nicht bescheinigt: der ganze Zug', S.plan(inst), null);

// 4. unberührt
pruefe('Haar unberührt, Hose nicht', [S.unberuehrt(inst, 'haar'), S.unberuehrt(inst, 'hose')], [true, false]);
pruefe('Haar bleibt stehen', S.bleibt(inst, 'haar'), true);
pruefe('mit dem neuen Stand und Lauf', [haar.geometry.userData.reglerstand.nase, haar.geometry.userData.lauf], [0.6, 7]);
S.merken([haar], { nase: 0.1 });
S.feld(inst, 'nase', '+').rest.stuecke.haar = [{ offen: true }];
pruefe('offen ist berührt', S.unberuehrt(inst, 'haar'), false);
S.feld(inst, 'nase', '+').rest.stuecke.haar = [null];
S.feld(inst, 'nase', '+').rest.ruhig = false;
pruefe('Knochen bewegt: berührt', S.unberuehrt(inst, 'haar'), false);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9sofortzugTest(SimpleTestCase):
    databases = set()

    def test_sofortzug(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
