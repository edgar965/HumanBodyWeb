# -*- coding: utf-8 -*-
u"""Die schnellere Anatomie-Zuordnung (19.10.2026): Vorfilter, Schranke und Strahlfolge in `Anatomiezuordnung`, Abschnitte in `Anatomiezuordnungsteil`, die Nachricht
`zuordnung` in `anatomiearbeiter.js` — in Node, mit den echten Modulen.

Gemessen an Damira0 (Mesh3D-AI, ultrafein, 1,18 Mio. Texel, 19.012 Hautdreiecke): die Zuordnung 21,5–22,2 s am Stück auf dem Hauptfaden, mit den Vorfiltern 13,5 s, auf
vier Workern 4,5 s; das ganze Backen der Hautfarbe ~35 s → 7,0 s. Jede Abkürzung ist EXAKT gebaut — dieselben Texel, Dreiecke und Gewichte, Bit für Bit. Das prüft dieser Test:

1. Kunstwelt mit Gefälle (gewellte Haut, Stück 4 mm darüber mit gekippten Normalen): `Anatomiezuordnung.rechnen` gegen dieselbe Rechnung mit Referenzfassungen von `_kandidaten`,
   `_strahl`, `_naechster` ohne jede Abkürzung (alle Kandidaten mit vollem Abstand, jeder Strahl gegen jedes Dreieck in Listenreihenfolge, strenges `<`) — bitgleich.
2. Abschnitte (`Anatomiezuordnungsteil.rechnen` je Drittel der Stück-Dreiecke, mit der knappen Haut `knapp`) und `zusammen`: bitgleich zu einem Lauf, `belegt` eingeschlossen.
3. `knapp` behält den Zahlentyp der Punkte und die Nummern der Dreiecke.
4. Der Worker beantwortet `zuordnung` mit `fertig` und genau dem Ergebnis des Abschnitts; `rechnen` bleibt, wie es war (Fremdes wird ignoriert).

Sabotage (von Hand, nicht als Lauf): im Zylindertest `rr` ohne Umkreis (`rad[t]` weg) → Fall 1 rot; in `zusammen` die Prüfung `belegt[nr]` weg → Fall 2 rot; in `knapp`
`Float32Array` statt `haut.pos.constructor` bei Float64-Punkten → Fall 3 rot. Geschrieben am 19.10.2026.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'anatomiezuordnungsteil.js')
ARBEITER = Jsmodul('gemeinsam', 'anatomiearbeiter.js')

WELT = """
// Kunstwelt: gewellte Haut 6 × 6 cm (Kante 2 mm), Stück 4 × 3,4 cm 4 mm darüber, Normalen gekippt
const hoehe = (x, z) => 0.006 * Math.sin(x * 90) * Math.cos(z * 70);
const n = 31, h = 0.002, hp = new Float64Array(n * n * 3), ecken = [];
for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const x = -0.03 + i * h, z = -0.03 + j * h, o = 3 * (j * n + i); hp[o] = x; hp[o + 1] = hoehe(x, z); hp[o + 2] = z; }
for (let j = 0; j < n - 1; j++) for (let i = 0; i < n - 1; i++) { const a = j * n + i; ecken.push(a, a + n, a + 1, a + 1, a + n, a + n + 1); }
const haut = { pos: hp, ecken: Uint32Array.from(ecken) };
const sx = 13, sz = 11, sp = new Float32Array(sx * sz * 3), uv = new Float32Array(sx * sz * 2), sn = new Float32Array(sx * sz * 3), si = [];
for (let j = 0; j < sz; j++) for (let i = 0; i < sx; i++) {
    const x = -0.02 + 0.04 * i / (sx - 1), z = -0.017 + 0.034 * j / (sz - 1), o = j * sx + i;
    sp[3 * o] = x; sp[3 * o + 1] = hoehe(x, z) + 0.004; sp[3 * o + 2] = z;
    const nx = 0.25 * Math.sin(i), nz = 0.2 * Math.cos(j), l = Math.hypot(nx, 1, nz);
    sn[3 * o] = nx / l; sn[3 * o + 1] = 1 / l; sn[3 * o + 2] = nz / l;
    uv[2 * o] = 0.05 + 0.9 * i / (sx - 1); uv[2 * o + 1] = 0.05 + 0.9 * j / (sz - 1);
}
for (let j = 0; j < sz - 1; j++) for (let i = 0; i < sx - 1; i++) { const a = j * sx + i; si.push(a, a + sx, a + 1, a + 1, a + sx, a + sx + 1); }
const stueck = { pos: sp, uv, index: Uint32Array.from(si), normal: sn };
const B = 128;
const gleich = (x, y, felder = ['texel', 'btri', 'l2', 'l3', 'stri', 'belegt']) => felder.every(k => x[k].length === y[k].length && x[k].every((w, i) => Object.is(w, y[k][i])));
const dreiecke = si.length / 3, grenzen = [0, Math.round(dreiecke / 3), Math.round(2 * dreiecke / 3), dreiecke];
"""

SKRIPT = """
const basis = MODUL.replace('anatomiezuordnungsteil.js', '');
const { Anatomiezuordnungsteil: T } = await import(MODUL);
const { Anatomiezuordnung: Z } = await import(basis + 'anatomiezuordnung.js');
const { Strahldreieck: S } = await import(basis + 'strahldreieck.js');
const { Dreiecksabstand: D } = await import(basis + 'dreiecksabstand.js');
""" + WELT + """
// 1. gegen Referenzfassungen ohne Abkürzung
const echt = await Z.rechnen(stueck, haut, B, B);
const ref = {
    _kandidaten(g, ha, p0, ek, ab) {
        const q = ek.map(i => 3 * i), p = ha.pos, e = ha.ecken;
        const m = [0, 1, 2].map(k => (p0[q[0] + k] + p0[q[1] + k] + p0[q[2] + k]) / 3);
        const radius = Math.sqrt(Math.max(...q.map(o => (p0[o] - m[0]) ** 2 + (p0[o + 1] - m[1]) ** 2 + (p0[o + 2] - m[2]) ** 2)));
        const lo = [0, 1, 2].map(k => Math.min(p0[q[0] + k], p0[q[1] + k], p0[q[2] + k])), hi = [0, 1, 2].map(k => Math.max(p0[q[0] + k], p0[q[1] + k], p0[q[2] + k]));
        let ids = [], abstand = [], kleinster = Infinity;
        for (const weite of [Z.NAH, Z.REICHWEITE]) {
            const von = [0, 1, 2].map(k => Math.max(0, Math.floor((lo[k] - weite - g.lo[k]) / Z.ZELLE)));
            const bis = [0, 1, 2].map(k => Math.min(g.n[k] - 1, Math.floor((hi[k] + weite - g.lo[k]) / Z.ZELLE)));
            ids = []; abstand = []; kleinster = Infinity; g.stempel++;
            for (let x = von[0]; x <= bis[0]; x++) for (let y = von[1]; y <= bis[1]; y++) for (let w = von[2]; w <= bis[2]; w++) {
                const zelle = (x * g.n[1] + y) * g.n[2] + w;
                for (let i = g.start[zelle]; i < g.start[zelle + 1]; i++) {
                    const t = g.liste[i];
                    if (g.marke[t] === g.stempel) continue;
                    g.marke[t] = g.stempel;
                    const a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
                    D.naechster(m[0], m[1], m[2], p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], ab);
                    const d = Math.sqrt(ab[0]);
                    ids.push(t); abstand.push(d);
                    if (d < kleinster) kleinster = d;
                }
            }
            if (kleinster + 2 * radius + Z.SCHLEPP <= weite) break;
        }
        if (kleinster > Z.REICHWEITE) return null;
        const reihe = ids.map((t, k) => k).filter(k => abstand[k] <= kleinster + 2 * radius + Z.SCHLEPP + 1e-9).sort((a, b) => abstand[a] - abstand[b]);
        return { ids: Int32Array.from(reihe.map(k => ids[k])), abstand: Float64Array.from(reihe.map(k => abstand[k])), radius };
    },
    _strahl(nn, o, w0, w1, w2, px, py, pz, kand, ha, ab, tr) {
        const mx = w0 * nn[o[0]] + w1 * nn[o[1]] + w2 * nn[o[2]], my = w0 * nn[o[0] + 1] + w1 * nn[o[1] + 1] + w2 * nn[o[2] + 1], mz = w0 * nn[o[0] + 2] + w1 * nn[o[1] + 2] + w2 * nn[o[2] + 2];
        const ml = Math.hypot(mx, my, mz);
        if (!(ml > 1e-9)) return -1;
        const p = ha.pos, e = ha.ecken;
        let grenze = Z.REICHWEITE, bt = -1;
        for (let k = 0; k < kand.ids.length; k++) {
            const t = kand.ids[k], a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            if (S.trifft(px, py, pz, mx / ml, my / ml, mz / ml, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], tr) && tr[0] < grenze) {
                grenze = tr[0]; bt = t; ab[1] = tr[1]; ab[2] = tr[2];
            }
        }
        return bt;
    },
    _naechster(px, py, pz, kand, ha, ab, tr) {
        const p = ha.pos, e = ha.ecken;
        let beste = Z.REICHWEITE ** 2, bt = -1;
        for (let k = 0; k < kand.ids.length; k++) {
            const t = kand.ids[k], a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            D.naechster(px, py, pz, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], tr);
            if (tr[0] < beste) { beste = tr[0]; bt = t; ab[1] = tr[1]; ab[2] = tr[2]; }
        }
        return bt;
    },
};
const echtFn = { _kandidaten: Z._kandidaten, _strahl: Z._strahl, _naechster: Z._naechster };
Object.assign(Z, ref);
const referenz = await Z.rechnen(stueck, haut, B, B);
Object.assign(Z, echtFn);
pruefe('genug Texel', echt.anzahl > 5000, true);
pruefe('wie ohne Abkürzung', gleich(echt, referenz), true);

// 2. Abschnitte mit knapper Haut
const knapp = T.knapp(haut);
const teile = [0, 1, 2].map(i => T.rechnen(stueck, knapp, B, B, grenzen[i], grenzen[i + 1]));
pruefe('Abschnitte zusammen wie ein Lauf', gleich(echt, T.zusammen(teile, B, B)), true);

// 3. knapp
pruefe('knapp: Zahlentyp', knapp.pos instanceof Float64Array, true);
pruefe('knapp: weniger oder gleich viele Punkte', knapp.pos.length <= hp.length, true);
const ecke = (ha, t, k) => Array.from(ha.pos.subarray(3 * ha.ecken[3 * t + k], 3 * ha.ecken[3 * t + k] + 3));
pruefe('knapp: dieselben Dreiecke', [0, 17, 999].every(t => [0, 1, 2].every(k => ecke(knapp, t, k).join() === ecke(haut, t, k).join())), true);
console.log(JSON.stringify({ ok: true, texel: echt.anzahl }));
"""

WORKER = """
const gesendet = [];
globalThis.self = { postMessage: (m) => gesendet.push(m) };
await import(MODUL);
const { Anatomiezuordnungsteil: T } = await import(MODUL.replace('anatomiearbeiter.js', 'anatomiezuordnungsteil.js'));
""" + WELT + """
// 4. der Worker
const knapp = T.knapp(haut), teil = T.rechnen(stueck, knapp, B, B, grenzen[1], grenzen[2]);
await self.onmessage({ data: { typ: 'zuordnung', id: 7, st: stueck, ha: knapp, breite: B, hoehe: B, von: grenzen[1], bis: grenzen[2] } });
pruefe('Worker: fertig mit Nummer', [gesendet[0]?.typ, gesendet[0]?.id], ['fertig', 7]);
pruefe('Worker: Ergebnis des Abschnitts', gleich(gesendet[0].ergebnis, teil, ['texel', 'btri', 'l2', 'l3', 'stri']) && gesendet[0].ergebnis.fern === teil.fern, true);
pruefe('Worker: Fremdes ignoriert', self.onmessage({ data: { typ: 'anders' } }), undefined);
console.log(JSON.stringify({ ok: true }));
"""


class AnatomiezuordnungsteilTest(SimpleTestCase):
    databases = set()

    def test_abkuerzungen_und_abschnitte_sind_exakt(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_der_worker_rechnet_einen_abschnitt(self):
        ausgabe = ARBEITER.laufen(WORKER)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
