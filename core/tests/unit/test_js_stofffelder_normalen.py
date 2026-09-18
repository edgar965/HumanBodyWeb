# -*- coding: utf-8 -*-
u"""`Stofffelder` (Kaefigfelder der JCMs im Stoff-Worker) und `Genesis9normalen`
(Normalen der beruehrten Punkte ueber die Nahtkopien) — 18.09.2026 abends.

Stofffelder: ein Kaefig aus vier Punkten, ein Feld auf Punkt 1 und 2.
1. Ohne Werte (null, leer, 0) kommt der Ruhekaefig selbst zurueck (keine Kopie).
2. Mit Wert 0,5 verschiebt sich Punkt 1 um 0,5 · d, Punkt 0 und 3 nicht;
   ein zweiter Aufruf mit anderen Werten faengt wieder von der Ruhe an.
3. `setzen` reicht Felder nach; ein Kanal ohne Feld wirkt nicht.

Genesis9normalen: ein Streifen aus zwei Vierecken (6 Punkte) plus eine
NAHTKOPIE von Punkt 2 (Punkt 6 mit derselben Ruhelage, eigenes Dreieck).
4. In Ruhe (Verschiebung 0) bleiben die Normalen bitgleich die Ruhenormalen.
5. Hebt man Punkt 2 und seine Kopie 6 an, kippen beide Normalen GLEICH
   (die Kopie sieht alle Dreiecke der Gruppe) — und die Normale eines
   unberuehrten Punkts bleibt die Ruhe.
6. Nach dem Zuruecksetzen (vorher-Liste) steht die Ruhenormale wieder.

Sabotage: in `_summe` die Schleife nur ueber die eigenen Dreiecke des Punkts
(statt der Gruppe) → Fall 5 rot (Kopie kippt anders); in `anwenden` `aus.set`
weglassen → Fall 2 rot (zweiter Aufruf summiert auf).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

FELDER = Jsmodul('gemeinsam', 'stofffelder.js')
NORMALEN = Jsmodul('gemeinsam', 'genesis9normalen.js')

SKRIPT_FELDER = """
const { Stofffelder } = await import(MODUL);
const kaefig = Float32Array.from([0,0,0, 1,0,0, 2,0,0, 3,0,0]);
const felder = { a: { n: Uint32Array.from([1, 2]), d: Float32Array.from([0,1,0, 0,0,2]) } };
const f = new Stofffelder(kaefig, felder);
// 1.
if (f.anwenden(null) !== kaefig || f.anwenden({}) !== kaefig || f.anwenden({ a: 0 }) !== kaefig) {
    throw new Error('ohne Werte nicht der Ruhekaefig');
}
// 2.
let aus = f.anwenden({ a: 0.5 });
if (aus === kaefig) throw new Error('keine Kopie');
if (Math.abs(aus[4] - 0.5) > 1e-6 || Math.abs(aus[8] - 1.0) > 1e-6) throw new Error('Feld falsch: ' + aus[4] + ' ' + aus[8]);
if (aus[0] !== 0 || aus[9] !== 3 || aus[1] !== 0) throw new Error('unberuehrte Punkte bewegt');
aus = f.anwenden({ a: 1.0 });
if (Math.abs(aus[4] - 1.0) > 1e-6) throw new Error('zweiter Aufruf summiert auf: ' + aus[4]);
// 3.
const g = new Stofffelder(kaefig, {});
if (g.anwenden({ a: 1 }) !== kaefig) throw new Error('ohne Feld verformt');
g.setzen(felder);
if (g.anwenden({ b: 1 }) !== kaefig) throw new Error('fremder Kanal wirkt');
if (Math.abs(g.anwenden({ a: 1 })[4] - 1.0) > 1e-6) throw new Error('setzen wirkt nicht');
console.log(JSON.stringify({ ok: true, p1y: +aus[4].toFixed(3) }));
"""

SKRIPT_NORMALEN = """
const { Genesis9normalen: N } = await import(MODUL);
// Streifen in der xz-Ebene, Normale +y: Punkte 0..5, Kopie 6 = Punkt 2.
//   3---4---5
//   |   |   |
//   0---1---2   (6 liegt auf 2; Dreieck 6-5-... haengt an der Kopie)
const ruhe = Float32Array.from([0,0,0, 1,0,0, 2,0,0, 0,0,1, 1,0,1, 2,0,1, 2,0,0]);
const index = Uint32Array.from([0,1,4, 0,4,3, 1,2,5, 1,5,4, 6,5,2]);   // letztes: entartet gleich, aber mit Kopie
// Ersatz: ein echtes Dreieck an der Kopie, Punkt 7 rechts davon.
const ruhe2 = Float32Array.from([...ruhe, 3,0,0.5]);
const index2 = Uint32Array.from([0,1,4, 0,4,3, 1,2,5, 1,5,4, 6,7,5]);
const n = ruhe2.length / 3;
const normal = new Float32Array(n * 3); for (let i = 0; i < n; i++) normal[3 * i + 1] = 1;
const attr = (arr, size) => ({ array: arr, count: arr.length / size, itemSize: size, needsUpdate: false });
const pos = attr(Float32Array.from(ruhe2), 3), nrm = attr(normal, 3);
const geo = { userData: {}, index: { array: index2 }, getAttribute: (k) => k === 'position' ? pos : (k === 'normal' ? nrm : null) };
const v = N.vorbereiten(geo, ruhe2);
if (v.gruppe[2] !== v.gruppe[6]) throw new Error('Kopie nicht in der Gruppe');
if (v.gruppe[2] === v.gruppe[1]) throw new Error('fremder Punkt in der Gruppe');
// 4. Ruhe: alle Punkte "beruehrt", Verschiebung 0
const alle = Uint32Array.from([0, 1, 2, 3, 4, 5, 6, 7]);
N.nachziehen(geo, alle, 8, alle, 0, ruhe2);
for (let i = 0; i < n * 3; i++) if (Math.abs(nrm.array[i] - normal[i]) > 1e-6) throw new Error('Ruhe veraendert bei ' + i);
// 5. Punkt 2 und Kopie 6 um 0,5 anheben
pos.array[3 * 2 + 1] = 0.5; pos.array[3 * 6 + 1] = 0.5;
const ber = Uint32Array.from([2, 6]);
N.nachziehen(geo, ber, 2, alle, 8, ruhe2);
const n2 = [nrm.array[6], nrm.array[7], nrm.array[8]], n6 = [nrm.array[18], nrm.array[19], nrm.array[20]];
const gleich = Math.hypot(n2[0] - n6[0], n2[1] - n6[1], n2[2] - n6[2]);
if (gleich > 1e-6) throw new Error('Kopie kippt anders: ' + n2 + ' / ' + n6);
if (!(n2[1] < 0.999)) throw new Error('Normale kippt nicht: ' + n2);
if (Math.abs(nrm.array[3 * 0 + 1] - 1) > 1e-6) throw new Error('unberuehrter Punkt veraendert');
// 6. Zuruecksetzen
pos.array[3 * 2 + 1] = 0; pos.array[3 * 6 + 1] = 0;
N.nachziehen(geo, ber, 0, ber, 2, ruhe2);
if (Math.abs(nrm.array[7] - 1) > 1e-6 || Math.abs(nrm.array[19] - 1) > 1e-6) throw new Error('nicht zurueckgesetzt');
console.log(JSON.stringify({ ok: true, kipp_y: +n2[1].toFixed(3), gruppen: v.mitgliedZahl.length - 1 }));
"""


class StofffelderNormalenTest(SimpleTestCase):

    databases = set()

    def test_stofffelder(self):
        ausgabe = FELDER.laufen(SKRIPT_FELDER)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['p1y'], 1.0)

    def test_normalen_ueber_nahtkopien(self):
        ausgabe = NORMALEN.laufen(SKRIPT_NORMALEN)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertLess(ausgabe['kipp_y'], 0.999)
        self.assertEqual(ausgabe['gruppen'], 7)     # 8 Punkte, 2 und 6 sind eine Gruppe
