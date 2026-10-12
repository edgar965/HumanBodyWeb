# -*- coding: utf-8 -*-
"""`Anatomiehash` und der Zwischenspeicher der Zuordnung in `Anatomiebacken` (12.10.2026), in Node mit den echten Modulen.

Edgar: „das Backen der neuen Haut soll nur ein paar Sekunden dauern." Gemessen im Chrome (Skin 03, 8,2 s je Rechnung): 5,6 s `Anatomiezuordnung` (Texel des Stücks → Stelle der Haut), 1,8 s
Karten, 0,6 s Füllen. Die Zuordnung hängt nur an der LAGE (Punkte, UV, Index, Normalen des Stücks; Punkte und Dreiecke der Haut), nicht an der Textur — bei jedem Hautwechsel kommt derselbe Körper
neu vom Server (andere Objekte, gleiche Zahlen). Seither: Schlüssel aus dem INHALT (`Anatomiehash`), die Zuordnung liegt am Stück (`userData.anatomieZuordnung`); mit Zwischenspeicher dauert die
Rechnung 1,5–2 s, Klick bis Karten 2,2–4,8 s (vorher 8–23 s).

Kunstwelt wie in `test_js_anatomiezuordnung.py`: Haut = Quadrat 50 × 50 mm aus zwei Dreiecken, Stück = Quadrat 30 × 30 mm 2 mm darüber, im Atlas 16 × 16 Texel.

`Anatomiehash`:
1. Gleicher Inhalt in anderen Objekten (auch ein Ausschnitt eines größeren Puffers, auch ein 16-Bit-Index) → gleicher Schlüssel; jede Änderung an einem der sechs Felder oder der Kartengröße → anderer Schlüssel.
2. Die Länge zählt: `[1, 2] + [3]` ≠ `[1] + [2, 3]`.

`Anatomiebacken.zuordnung`:
3. Gleicher Inhalt → DASSELBE Versprechen (auch ein zweiter Aufruf, solange der erste noch rechnet: ein Lauf); geänderte Haut → neue Rechnung.
4. Im Schlüssel zählen die Ruhe-Normalen (`geometry.userData.nahtRuhe`), nicht die von der Naht angeglichenen: andere `normal` bei gleicher Ruhe → Treffer; andere Ruhe → Fehlschlag des Schlüssels.
5. Ein gescheiterter Lauf bleibt nicht liegen: danach rechnet der nächste Aufruf neu.

`Anatomiebacken.vorrechnen`:
6. Rechnet die Zuordnung in die Ablage; zwei Aufrufe zugleich → ein Lauf (`Anatomiezuordnung.rechnen` zählt 1); danach ist die Sperre `anatomieVorrechnet` wieder frei; ein Fehler bricht nichts ab.

Sabotage-Gegenprobe: in `Anatomiehash.feld` die Länge streichen → Fall 2 rot; `haut.ecken` aus der Feldliste → Fall 1 rot; in `zuordnung` `alt?.schluessel === schluessel` auf `false` → Fall 3 rot; `ruhe ||` streichen → Fall 4 rot; das `zu.catch(...)` streichen →
Fall 5 rot; in `vorrechnen` die Sperre streichen → Fall 6 rot. Gelaufen 12.10.2026 (3 Tests, grün); die Sabotage-Gegenprobe ist nicht gefahren.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

HASH = Jsmodul('gemeinsam', 'anatomiehash.js')
BACKEN = Jsmodul('gemeinsam', 'anatomiebacken.js')

WELT = """
const haut = () => ({ pos: Float32Array.from([0, 0, 0,  0.05, 0, 0,  0.05, 0.05, 0,  0, 0.05, 0]), ecken: Uint32Array.from([0, 1, 2,  0, 2, 3]) });
const stueck = () => ({
    pos: Float32Array.from([0.01, 0.01, 0.002,  0.04, 0.01, 0.002,  0.01, 0.04, 0.002,  0.04, 0.04, 0.002]),
    uv: Float32Array.from([0.125, 0.125,  0.875, 0.125,  0.125, 0.875,  0.875, 0.875]),
    index: Uint32Array.from([0, 1, 2,  1, 3, 2]),
    normal: Float32Array.from([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1]),
});
"""


class AnatomiehashTest(SimpleTestCase):
    databases = set()

    def test_der_schluessel_zaehlt_den_inhalt_nicht_das_objekt(self):
        skript = WELT + """
const { Anatomiehash: H } = await import(MODUL);
const schluessel = (s = stueck(), h = haut(), b = 16, hoehe = 16) => H.schluessel(s, h, b, hoehe);
const grund = schluessel();

// 1. gleicher Inhalt, andere Objekte
pruefe('gleicher Inhalt', schluessel(stueck(), haut()), grund);
const grossPuffer = new Float32Array(20); grossPuffer.set(haut().pos, 5);
pruefe('Ausschnitt eines Puffers', schluessel(stueck(), { ...haut(), pos: grossPuffer.subarray(5, 17) }), grund);
pruefe('16-Bit-Index', schluessel({ ...stueck(), index: Uint16Array.from([0, 1, 2, 1, 3, 2]) }), grund);
// jede Änderung → anderer Schlüssel
const aendern = (feld, wo, wert) => { const s = stueck(), h = haut(); const ziel = feld.startsWith('h.') ? h : s; ziel[feld.slice(2)][wo] = wert; return schluessel(s, h); };
for (const [feld, wo, wert] of [['s.pos', 0, 0.011], ['s.uv', 3, 0.5], ['s.index', 4, 0], ['s.normal', 2, 0.99], ['h.pos', 5, 0.001], ['h.ecken', 1, 2]]) {
    if (aendern(feld, wo, wert) === grund) throw new Error('Änderung an ' + feld + ' bleibt ohne Wirkung auf den Schlüssel');
}
pruefe('andere Kartengröße', schluessel(stueck(), haut(), 32, 16) !== grund, true);
pruefe('ohne Normalen anders als mit', schluessel({ ...stueck(), normal: null }) !== grund, true);

// 2. die Länge zählt
const eins = H.feld(H.SEED_A, Uint32Array.from([1, 2])), zwei = H.feld(H.feld(H.SEED_A, Uint32Array.from([1])), Uint32Array.from([2]));
pruefe('[1, 2] ≠ [1][2]', eins !== zwei, true);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = HASH.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class ZuordnungsspeicherTest(SimpleTestCase):
    databases = set()

    def test_gleiche_geometrie_rechnet_einmal_und_ein_fehler_bleibt_nicht_liegen(self):
        skript = WELT + """
const { Anatomiebacken: B } = await import(MODUL);
const { Anatomiezuordnung: Z } = await import(new URL('./anatomiezuordnung.js', MODUL).href);
let laeufe = 0;
const echt = Z.rechnen.bind(Z);
Z.rechnen = (...a) => { laeufe++; return echt(...a); };
const netz = (ruhe) => ({ userData: {}, geometry: { userData: ruhe ? { nahtRuhe: ruhe } : {} } });

// 3. gleicher Inhalt → dasselbe Versprechen; während des Laufs geteilt; geänderte Haut → neu
let n = netz();
const p1 = B.zuordnung(n, stueck(), haut(), 16, 16);
const p2 = B.zuordnung(n, stueck(), haut(), 16, 16);
pruefe('zugleich: ein Versprechen', p1 === p2, true);
const z1 = await p1;
pruefe('Ergebnis da', z1.anzahl > 100, true);
pruefe('später: dasselbe', B.zuordnung(n, stueck(), haut(), 16, 16) === p1, true);
pruefe('ein Lauf', laeufe, 1);
const h2 = haut(); h2.pos[2] = 0.0004;
const p3 = B.zuordnung(n, stueck(), h2, 16, 16);
pruefe('geänderte Haut: neue Rechnung', [p3 !== p1, laeufe], [true, 2]);
await p3;

// 4. Ruhe-Normalen im Schlüssel
const ruhe = Float32Array.from([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1]);
n = netz(ruhe);
const q1 = B.zuordnung(n, stueck(), haut(), 16, 16); await q1;
const angeglichen = { ...stueck(), normal: Float32Array.from([0.1, 0, 0.995,  0, 0, 1,  0, 0, 1,  0, 0, 1]) };
pruefe('angeglichene Normalen, gleiche Ruhe: Treffer', B.zuordnung(n, angeglichen, haut(), 16, 16) === q1, true);
n.geometry.userData.nahtRuhe = Float32Array.from([0, 0.3, 0.95,  0, 0, 1,  0, 0, 1,  0, 0, 1]);
pruefe('andere Ruhe: neue Rechnung', B.zuordnung(n, angeglichen, haut(), 16, 16) !== q1, true);

// 5. gescheitert → liegt nicht fest
n = netz();
const kaputt = { ...stueck(), index: null };
let fehler = null;
try { await B.zuordnung(n, kaputt, haut(), 16, 16); } catch (e) { fehler = e.message; }
pruefe('Fehler kommt an', typeof fehler, 'string');
await Promise.resolve();
pruefe('nichts liegt fest', n.userData.anatomieZuordnung, undefined);
const gut = await B.zuordnung(n, stueck(), haut(), 16, 16);
pruefe('danach rechnet es neu', gut.anzahl > 100, true);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = BACKEN.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_vorrechnen_ein_lauf_zugleich_und_ein_fehler_bricht_nichts_ab(self):
        skript = WELT + """
const { Anatomiebacken: B } = await import(MODUL);
const { Anatomiezuordnung: Z } = await import(new URL('./anatomiezuordnung.js', MODUL).href);
let laeufe = 0;
const echt = Z.rechnen.bind(Z);
Z.rechnen = (...a) => { laeufe++; return echt(...a); };
const warnungen = [];
console.warn = (text) => warnungen.push(text);

// 6. rechnet in die Ablage, zwei Aufrufe zugleich → ein Lauf, Sperre danach frei
B.eingabe = () => ({ stueck: stueck(), quelle: { haut: haut() }, breite: 16, hoehe: 16 });
const netz = { userData: {}, geometry: { userData: {} } };
await Promise.all([B.vorrechnen({}, netz, {}, []), B.vorrechnen({}, netz, {}, [])]);
pruefe('ein Lauf', laeufe, 1);
pruefe('Zuordnung liegt am Stück', typeof netz.userData.anatomieZuordnung?.schluessel, 'string');
pruefe('Sperre frei', netz.userData.anatomieVorrechnet, false);
await B.vorrechnen({}, netz, {}, []);
pruefe('später: nichts mehr zu rechnen', laeufe, 1);

// Fehler in der Eingabe: nur eine Warnung
const andere = { userData: {}, geometry: { userData: {} } };
B.eingabe = () => { throw new Error('keine Haut'); };
await B.vorrechnen({}, andere, {}, []);
pruefe('Warnung statt Abbruch', warnungen.length, 1);
pruefe('Sperre frei nach Fehler', andere.userData.anatomieVorrechnet, false);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = BACKEN.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
