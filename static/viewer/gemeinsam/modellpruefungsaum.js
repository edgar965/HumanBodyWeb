import * as THREE from 'three';
import { Modellpruefungdurchstoss } from './modellpruefungdurchstoss.js';

/**
 * Modellpruefungsaum — sind die Säume der Kleidung glatt? Klasse des Modell Checks (`Modellpruefung`, 02.11.2026, Sitzung roomguest-f0; Edgar: „Zacken beim Ärmel (kein
 * Saum)“, „sind diese Testmethoden für die Figur auch in dem generischen Code … Modell Check? wenn nicht, dann tu das“). Dasselbe Maß wie der Saumtest von Foto-Genesis
 * (`HumanBodyWeb/core/tests/automated/fotogenesis_saummass.py`, torch: `KoerperKI_Fotos/saummass.py`): Randschleifen über die gerichteten Randkanten (Punkte gleicher Lage
 * vorher verschweißt — three.js trennt sie an UV-Nähten), ab LOCH_MM ein Saum, kürzere sind Löcher; je Saum die Schleife auf SCHRITT_MM gleichmäßig umgetastet und
 * kreisförmig mit einem Gauß von GLAETTE_MM geglättet; Zacken = P95 des Abstands der Randpunkte von der geglätteten Schleife an derselben Stelle, Überlänge = Länge /
 * geglättete Länge − 1. Grenzen wie dort: ZACKEN_MM, UEBERLAENGE (gemessen 02.11.2026: Säume der Zeile 1 2,1–3,3 mm, gerade Schnitte 0,8–1,15 mm bei 0,6–1,6 %).
 * Abweichend: Faltung direkt bis 4 σ statt über die FFT, in der gestellten Lage statt der Ruhe. Gegenprobe am selben Kunstnetz (Zylinder, Rand im Zickzack ±3 mm,
 * `ProjektTemp/_wegwerf/ergaenzung/saummass_kunstnetz.py`): hier 856 mm / 3,00 mm / 1,274 und 377 / 0,55 / 0,009, torch 855,5 / 3,0 / 1,274 und 377,0 / 0,55 / 0,009.
 *
 *     const s = Modellpruefungsaum.pruefen(koerper, lage, netze);    // netze: die sichtbaren Netze (Kleidung wie `Modellpruefungdurchstoss.kleider`)
 *     // → {geprueft, saeume: [{name, laenge_mm, zacken_mm, ueberlaenge, punkte: [Punkt des Kleidungsnetzes …]}], zu: [Säume über den Grenzen], loecher}
 */
export class Modellpruefungsaum {

    static LOCH_MM = 150;
    static GLAETTE_MM = 8;
    static SCHRITT_MM = 1;
    static ZACKEN_MM = 1.6;
    static UEBERLAENGE = 0.025;

    static pruefen(koerper, lage, netze) {
        // Starre Stücke (Bauart, `Starrbindung`, 12.11.2026) haben keinen Saum: die Kanten einer Waffe sind Form, kein Stoffrand (Fallout Ranger: Laserwaffe 615 mm „Zacken 6,4 mm“).
        const M = Modellpruefungsaum, saeume = [], kleider = Modellpruefungdurchstoss.kleider(netze.filter((o) => o !== koerper && !o.userData?.starrbindung));
        let loecher = 0;
        for (const o of kleider) {
            const p = M.verschweisst(o);
            for (const k of M.schleifen(p.idx)) {
                const x = k.map((i) => p.pos[i]), laenge = M.laenge(x);
                if (1000 * laenge < M.LOCH_MM) { loecher++; continue; }
                const { an, glatt } = M.glaetten(x, laenge);
                const ab = x.map((q, i) => 1000 * q.distanceTo(an[i])).sort((a, b) => a - b), r = 0.95 * (ab.length - 1), u = Math.floor(r);
                const zacken = ab[u] + (ab[Math.min(u + 1, ab.length - 1)] - ab[u]) * (r - u);
                saeume.push({ name: o.name || o.uuid, laenge_mm: Math.round(1000 * laenge), zacken_mm: +zacken.toFixed(2), ueberlaenge: +(laenge / Math.max(glatt, 1e-9) - 1).toFixed(3),
                              punkte: k.map((i) => p.erster[i]) });
            }
        }
        saeume.sort((a, b) => b.zacken_mm - a.zacken_mm);
        return { geprueft: kleider.length, saeume, zu: saeume.filter((s) => s.zacken_mm > M.ZACKEN_MM || s.ueberlaenge > M.UEBERLAENGE), loecher };
    }

    /** Gestellte Punkte (Welt), gleiche Lage zu einem Punkt verschweißt (0,01 mm), die Dreiecke darauf und je verschweißtem Punkt sein erster Punkt im Netz (`erster`). */
    static verschweisst(o) {
        const g = o.geometry, m = g.attributes.position.count, q = new THREE.Vector3(), nummer = new Map(), pos = [], erster = [], neu = new Int32Array(m);
        for (let i = 0; i < m; i++) {
            o.getVertexPosition(i, q).applyMatrix4(o.matrixWorld);
            const s = `${Math.round(q.x * 1e5)},${Math.round(q.y * 1e5)},${Math.round(q.z * 1e5)}`;
            if (!nummer.has(s)) { nummer.set(s, pos.length); pos.push(q.clone()); erster.push(i); }
            neu[i] = nummer.get(s);
        }
        const alt = g.index ? g.index.array : Uint32Array.from({ length: m }, (_, i) => i);
        return { pos, erster, idx: Int32Array.from(alt, (i) => neu[i]) };
    }

    /** [Punktnummern in Reihenfolge] je Randschleife — gerichtete Kanten, die genau einmal vorkommen (wie `Saummass.schleifen`). */
    static schleifen(idx) {
        const zahl = new Map(), gerichtet = [];
        for (let t = 0; t < idx.length; t += 3) {
            for (const [a, b] of [[idx[t], idx[t + 1]], [idx[t + 1], idx[t + 2]], [idx[t + 2], idx[t]]]) {
                if (a === b) continue;
                const s = a < b ? `${a},${b}` : `${b},${a}`;
                zahl.set(s, (zahl.get(s) || 0) + 1);
                gerichtet.push([a, b, s]);
            }
        }
        const weiter = new Map();
        for (const [a, b, s] of gerichtet) if (zahl.get(s) === 1) { if (!weiter.has(a)) weiter.set(a, []); weiter.get(a).push(b); }
        const aus = [];
        while (weiter.size) {
            const start = weiter.keys().next().value, kette = [start];
            let p = start;
            for (;;) {
                const nach = weiter.get(p);
                if (!nach) break;
                const q = nach.pop();
                if (!nach.length) weiter.delete(p);
                if (q === start) break;
                kette.push(q);
                p = q;
            }
            if (kette.length >= 3) aus.push(kette);
        }
        return aus;
    }

    static laenge(x) {
        let l = 0;
        for (let i = 0; i < x.length; i++) l += x[i].distanceTo(x[(i + 1) % x.length]);
        return l;
    }

    /** Geglättete Schleife an den Stellen der Randpunkte (`an`) und ihre Länge (`glatt`), wie `Saummass.glaetten`. */
    static glaetten(x, laenge) {
        const M = Modellpruefungsaum, n = Math.max(16, Math.ceil(laenge / (M.SCHRITT_MM / 1000))), s = [0];
        for (let i = 0; i < x.length; i++) s.push(s[i] + x[i].distanceTo(x[(i + 1) % x.length]));
        const an = (werte, stellen, fragen) => {                     // lineare Interpolation wie np.interp, Stellen und Fragen aufsteigend
            let j = 1;
            return fragen.map((u) => {
                while (j < stellen.length - 1 && stellen[j] <= u) j++;
                return werte[j - 1].clone().lerp(werte[j], (u - stellen[j - 1]) / Math.max(stellen[j] - stellen[j - 1], 1e-30));
            });
        };
        const u = Array.from({ length: n }, (_, i) => (i * laenge) / n), g = an([...x, x[0]], s, u);
        const sigma = M.GLAETTE_MM / 1000 / (laenge / n), rad = Math.ceil(4 * sigma), kern = [];
        for (let k = -rad; k <= rad; k++) kern.push(Math.exp(-(k * k) / (2 * sigma * sigma)));
        const summe = kern.reduce((a, b) => a + b, 0);
        const glatt = g.map((_, i) => {
            const v = new THREE.Vector3();
            for (let k = -rad; k <= rad; k++) v.addScaledVector(g[(((i + k) % n) + n) % n], kern[k + rad] / summe);
            return v;
        });
        return { an: an([...glatt, glatt[0]], [...u, laenge], s.slice(0, -1)), glatt: M.laenge(glatt) };
    }
}
