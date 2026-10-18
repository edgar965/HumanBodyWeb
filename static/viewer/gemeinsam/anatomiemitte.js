import { Dreiecksabstand } from './dreiecksabstand.js';

/**
 * Anatomiemitte — ein Stück, das weit vor der Haut hängt (Penis), von einer Mitte im Becken aus auf die Haut abbilden (18.10.2026, für `Anatomiezuordnung`).
 *
 * Edgar, 18.10.2026: „ob diese Matt-Änderungen mit den männlichen Genitalien damit kaputt sind". Gemessen im Chrome an Matt0 („Daz Anatomie Mann", Lage mit `einzug`,
 * `Anatomielage`): Punkte des Stücks über der Haut Median 23,9 mm, p90 52,7, größte 57,6; 54 % weiter als 20 mm, 26 % weiter als 40 mm (`REICHWEITE`). Unter einem
 * Penis liegt keine Haut: der nächste Punkt hängt an Kanten und Ecken der Haut (Kachelmuster auf dem Schaft), jenseits der Reichweite blieb die Karte leer (Eichel
 * einfarbig). Ohne Einzug fiel das nicht auf — das Stück lag 31 mm verschoben in der Haut, der Schaft fand dort zufällig Haut. Das Genital der Frau liegt höchstens
 * 17,5 mm über der Haut (DamiraAlt) und bleibt bei der Zuordnung nach der Haut darunter (`fern` zählt dort kein Dreieck).
 *
 * HIER: Die Mitte C liegt hinter dem Ring des Stücks (Randpunkte nahe der Haut), `TIEFE` Ringradien entgegen der Hautnormale. Jeder Punkt des Stücks bekommt die
 * Stelle, an der der Strahl von ihm zu C die Haut zuerst trifft — stetig, ohne Kanten-Blöcke; am Ring liegt das Stück auf der Haut, die Naht bleibt dicht. Verfehlt
 * er sie, gilt der nächste Hautpunkt. Je Texel wird die Stelle aus den drei Ecken gemischt und auf die Haut gelegt (nächster Punkt aus nächster Nähe, dort ohne
 * Blöcke). Die Abbildung staucht: der Penis landet auf der Haut um den Ansatz, die Poren werden größer.
 */
export class Anatomiemitte {

    /** Ab so weit (m) über der Haut zählt ein Dreieck des Stücks als fern (Frau höchstens 17,5 mm). */
    static FERN = 0.02;
    /** Ist mehr als dieser Anteil der Dreiecke fern, wird das ganze Stück von der Mitte aus abgebildet (Matt0: 54 % der Punkte). */
    static ANTEIL = 0.1;
    /** Die Mitte liegt so viele Ringradien hinter dem Ring. */
    static TIEFE = 2;
    /** Randpunkte, die näher als dies (m) an der Haut liegen, bilden den Ring (die Naht legt sie auf die Haut, gemessen bis 3,8 mm). */
    static RING_M = 0.006;
    /** So weit (m) darf die Haut auf dem Strahl HINTER dem Punkt liegen (der Ring sitzt bis 3,8 mm in der Haut). */
    static VOR = 0.006;
    /** Um so viel (m) wird der Kasten der drei Stellen eines Dreiecks für die Suche je Texel größer. */
    static NAEHE = 0.004;

    /** Zählt das Dreieck als fern? `kand` aus `Anatomiezuordnung._kandidaten` (null: weiter als die Reichweite). */
    static fern(kand) {
        return !kand || kand.abstand[0] > Anatomiemitte.FERN;
    }

    /** Die Stelle auf der Haut je Punkt des Stücks (`Float64Array`, xyz) — null ohne Ring. `g`: Gitter aus `Anatomiezuordnung._gitter`. */
    static stellen(stueck, haut, g) {
        const C = Anatomiemitte.mitte(stueck, haut, g);
        if (!C) return null;
        const p = stueck.pos, n = p.length / 3, aus = new Float64Array(3 * n), ab = new Float64Array(3);
        for (let i = 0; i < n; i++) {
            const t = Anatomiemitte._strahl(p[3 * i], p[3 * i + 1], p[3 * i + 2], C, haut, g, ab);
            const bt = t >= 0 ? t : Anatomiemitte._nah(p[3 * i], p[3 * i + 1], p[3 * i + 2], Infinity, haut, g, ab);
            Anatomiemitte._punkt(haut, bt, ab, aus, 3 * i);
        }
        return aus;
    }

    /** Die Mitte C (xyz) hinter dem Ring — null, wenn kein Randpunkt nahe der Haut liegt. */
    static mitte(stueck, haut, g) {
        const p = stueck.pos, ab = new Float64Array(3), hn = haut.normal, e = haut.ecken;
        const ring = Anatomiemitte._rand(p, stueck.index), R = [0, 0, 0], N = [0, 0, 0], liste = [];
        for (const i of ring) {
            const t = Anatomiemitte._nah(p[3 * i], p[3 * i + 1], p[3 * i + 2], Anatomiemitte.RING_M, haut, g, ab);
            if (t < 0) continue;
            liste.push(i);
            for (let k = 0; k < 3; k++) { R[k] += p[3 * i + k]; if (hn) N[k] += hn[3 * e[3 * t] + k]; }
        }
        if (!liste.length) return null;
        const r = R.map(w => w / liste.length), nl = Math.hypot(...N) || 1;
        const radius = liste.reduce((s, i) => s + Math.hypot(p[3 * i] - r[0], p[3 * i + 1] - r[1], p[3 * i + 2] - r[2]), 0) / liste.length;
        return r.map((w, k) => w - Anatomiemitte.TIEFE * radius * N[k] / nl);
    }

    /** Die Punkte auf dem Rand des Stücks (Kanten mit einem Dreieck; Punkte an UV-Nähten auf 0,01 mm zusammengelegt). */
    static _rand(p, index) {
        const id = new Map(), wer = [];
        for (let i = 0; i < p.length / 3; i++) {
            const s = `${Math.round(p[3 * i] * 1e5)},${Math.round(p[3 * i + 1] * 1e5)},${Math.round(p[3 * i + 2] * 1e5)}`;
            if (!id.has(s)) id.set(s, i);
            wer.push(id.get(s));
        }
        const kanten = new Map();
        for (let s = 0; 3 * s + 2 < index.length; s++) for (let k = 0; k < 3; k++) {
            const a = wer[index[3 * s + k]], b = wer[index[3 * s + (k + 1) % 3]], key = a < b ? `${a}_${b}` : `${b}_${a}`;
            kanten.set(key, (kanten.get(key) || 0) + 1);
        }
        const aus = new Set();
        for (const [key, z] of kanten) if (z === 1) for (const i of key.split('_')) aus.add(Number(i));
        return aus;
    }

    /** Erster Treffer des Strahls vom Punkt zur Mitte C auf der Haut: Dreieck (`ab[1]`, `ab[2]` Gewichte) oder −1. Gelaufen wird durch die Zellen des Gitters. */
    static _strahl(px, py, pz, C, haut, g, ab) {
        let dx = C[0] - px, dy = C[1] - py, dz = C[2] - pz;
        const L = Math.hypot(dx, dy, dz), z = 0.5 * g.zelle;
        if (!(L > 1e-9)) return -1;
        dx /= L; dy /= L; dz /= L;
        const p = haut.pos, e = haut.ecken;
        let beste = Infinity, bt = -1;
        g.stempel++;
        for (let s = -Anatomiemitte.VOR; s <= L && s <= beste + 4 * z; s += z) {
            const zelle = Anatomiemitte._zelleVon(g, px + s * dx, py + s * dy, pz + s * dz);
            if (zelle < 0) continue;
            for (let i = g.start[zelle]; i < g.start[zelle + 1]; i++) {
                const t = g.liste[i];
                if (g.marke[t] === g.stempel) continue;
                g.marke[t] = g.stempel;
                const a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
                const w = Anatomiemitte._schnitt(px, py, pz, dx, dy, dz, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2]);
                if (w && w[0] >= -Anatomiemitte.VOR && w[0] < beste) { beste = w[0]; bt = t; ab[1] = w[1]; ab[2] = w[2]; }
            }
        }
        return bt;
    }

    /** Möller–Trumbore mit Vorzeichen: `[t, Gewicht b, Gewicht c]` oder null. */
    static _schnitt(px, py, pz, dx, dy, dz, ax, ay, az, bx, by, bz, cx, cy, cz) {
        const e1x = bx - ax, e1y = by - ay, e1z = bz - az, e2x = cx - ax, e2y = cy - ay, e2z = cz - az;
        const hx = dy * e2z - dz * e2y, hy = dz * e2x - dx * e2z, hz = dx * e2y - dy * e2x, det = e1x * hx + e1y * hy + e1z * hz;
        if (Math.abs(det) < 1e-14) return null;
        const inv = 1 / det, sx = px - ax, sy = py - ay, sz = pz - az, u = (sx * hx + sy * hy + sz * hz) * inv;
        if (u < -1e-4 || u > 1 + 1e-4) return null;
        const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = (dx * qx + dy * qy + dz * qz) * inv;
        if (v < -1e-4 || u + v > 1 + 1e-4) return null;
        return [(e2x * qx + e2y * qy + e2z * qz) * inv, Math.min(1, Math.max(0, u)), Math.min(1, Math.max(0, v))];
    }

    /** Das Hautdreieck mit dem nächsten Punkt höchstens `r` (m) entfernt (Infinity: alle): Nummer, `ab` wie `Dreiecksabstand`; sonst −1. */
    static _nah(x, y, z, r, haut, g, ab) {
        const p = haut.pos, e = haut.ecken, nt = e.length / 3, hilf = new Float64Array(3);
        const alle = !Number.isFinite(r), zellen = alle ? null : Anatomiemitte._zellen(g, [x - r, y - r, z - r], [x + r, y + r, z + r]);
        let beste = alle ? Infinity : r * r, bt = -1;
        const pruefen = (t) => {
            const a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            Dreiecksabstand.naechster(x, y, z, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], hilf);
            if (hilf[0] < beste) { beste = hilf[0]; bt = t; ab[0] = hilf[0]; ab[1] = hilf[1]; ab[2] = hilf[2]; }
        };
        if (alle) for (let t = 0; t < nt; t++) pruefen(t);
        else for (const t of zellen) pruefen(t);
        return bt;
    }

    /** Die Hautdreiecke (Nummern, ohne Doppel) in den Zellen des Gitters, die den Kasten `lo … hi` berühren. */
    static _zellen(g, lo, hi) {
        const z = g.zelle, von = [0, 1, 2].map(k => Math.max(0, Math.floor((lo[k] - g.lo[k]) / z)));
        const bis = [0, 1, 2].map(k => Math.min(g.n[k] - 1, Math.floor((hi[k] - g.lo[k]) / z)));
        const aus = [];
        g.stempel++;
        for (let x = von[0]; x <= bis[0]; x++) for (let y = von[1]; y <= bis[1]; y++) for (let w = von[2]; w <= bis[2]; w++) {
            const zelle = (x * g.n[1] + y) * g.n[2] + w;
            for (let i = g.start[zelle]; i < g.start[zelle + 1]; i++) {
                const t = g.liste[i];
                if (g.marke[t] !== g.stempel) { g.marke[t] = g.stempel; aus.push(t); }
            }
        }
        return aus;
    }

    /** Nummer der Gitterzelle, in der der Punkt liegt — −1 außerhalb. */
    static _zelleVon(g, x, y, z) {
        const w = [x, y, z].map((v, k) => Math.floor((v - g.lo[k]) / g.zelle));
        if (w.some((v, k) => v < 0 || v >= g.n[k])) return -1;
        return (w[0] * g.n[1] + w[1]) * g.n[2] + w[2];
    }

    /** Der Punkt im Hautdreieck `t` mit den Gewichten aus `ab` nach `aus[o … o + 2]`. */
    static _punkt(haut, t, ab, aus, o) {
        const p = haut.pos, e = haut.ecken, a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2], l1 = 1 - ab[1] - ab[2];
        for (let k = 0; k < 3; k++) aus[o + k] = l1 * p[a + k] + ab[1] * p[b + k] + ab[2] * p[c + k];
    }

    /**
     * Die Texel des Stück-Dreiecks `s` belegen: Stelle = Mischung der Stellen seiner Ecken, darauf der nächste Hautpunkt unter den Dreiecken um die drei Stellen.
     * `dazu(nr, bt, l2, l3, s)` legt ein Texel ab (`Anatomiezuordnung._dazu`).
     */
    static rastern(stueck, ecken, s, stellen, haut, g, breite, hoehe, belegt, dazu) {
        const uv = stueck.uv, x = ecken.map(i => uv[2 * i] * breite), y = ecken.map(i => uv[2 * i + 1] * hoehe), o = ecken.map(i => 3 * i);
        const flaeche = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0]);
        if (Math.abs(flaeche) < 1e-9) return;
        const d = Anatomiemitte.NAEHE, lo = [0, 1, 2].map(k => Math.min(...o.map(q => stellen[q + k])) - d), hi = [0, 1, 2].map(k => Math.max(...o.map(q => stellen[q + k])) + d);
        const kand = Anatomiemitte._zellen(g, lo, hi), p = haut.pos, e = haut.ecken, hilf = new Float64Array(3), eps = 0.002;
        for (let j = Math.max(0, Math.floor(Math.min(...y))); j <= Math.min(hoehe - 1, Math.floor(Math.max(...y))); j++) {
            for (let i = Math.max(0, Math.floor(Math.min(...x))); i <= Math.min(breite - 1, Math.floor(Math.max(...x))); i++) {
                const nr = j * breite + i;
                if (belegt[nr]) continue;
                const cx = i + 0.5, cy = j + 0.5;
                const w1 = ((cx - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (cy - y[0])) / flaeche, w2 = ((x[1] - x[0]) * (cy - y[0]) - (cx - x[0]) * (y[1] - y[0])) / flaeche, w0 = 1 - w1 - w2;
                if (w0 < -eps || w1 < -eps || w2 < -eps) continue;
                const q = [0, 1, 2].map(k => w0 * stellen[o[0] + k] + w1 * stellen[o[1] + k] + w2 * stellen[o[2] + k]);
                let beste = Infinity, bt = -1, l2 = 0, l3 = 0;
                for (const t of kand) {
                    const a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
                    Dreiecksabstand.naechster(q[0], q[1], q[2], p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], hilf);
                    if (hilf[0] < beste) { beste = hilf[0]; bt = t; l2 = hilf[1]; l3 = hilf[2]; }
                }
                if (bt < 0) continue;
                belegt[nr] = 1;
                dazu(nr, bt, l2, l3, s);
            }
        }
    }
}
