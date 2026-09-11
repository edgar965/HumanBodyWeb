/**
 * Hautmaskegeometrie — die Bausteine der `Hautmaske`: Punktnormalen,
 * Suchgitter, nächster Punkt, Strahl gegen Dreieck.
 *
 * Aus `hautmaske.js` abgeteilt (11.09.2026, Dateigrenze), als dort die
 * Entscheidung „anliegende Kante — kein freier Randstreifen" dazukam. Hier
 * steht nur Geometrie, keine Entscheidung; ohne Three.js und ohne DOM,
 * damit es in Node läuft (`core/tests/unit/test_js_hautmaske.py`).
 */
export class Hautmaskegeometrie {

    /** Zellgröße des Suchgitters — größer als der Suchabstand. */
    static ZELLE_M = 0.03;

    /** Punktnormalen aus den Dreiecken; nach außen über das signierte Volumen
     *  (die Mehrheit gegen den Schwerpunkt kippt in manchen Posen). */
    static normalen(P, T) {
        const n = P.length / 3, N = new Float64Array(n * 3);
        let vol = 0;
        for (let k = 0; k + 2 < T.length; k += 3) {
            const a = T[k], b = T[k + 1], c = T[k + 2];
            const ax = P[3 * a], ay = P[3 * a + 1], az = P[3 * a + 2];
            const bx = P[3 * b], by = P[3 * b + 1], bz = P[3 * b + 2];
            const cx = P[3 * c], cy = P[3 * c + 1], cz = P[3 * c + 2];
            const ux = bx - ax, uy = by - ay, uz = bz - az, vx = cx - ax, vy = cy - ay, vz = cz - az;
            const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            vol += ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx);
            for (const i of [a, b, c]) { N[3 * i] += nx; N[3 * i + 1] += ny; N[3 * i + 2] += nz; }
        }
        const vz = vol >= 0 ? 1 : -1;
        for (let i = 0; i < n; i++) {
            const l = Math.hypot(N[3 * i], N[3 * i + 1], N[3 * i + 2]) || 1;
            N[3 * i] = vz * N[3 * i] / l; N[3 * i + 1] = vz * N[3 * i + 1] / l; N[3 * i + 2] = vz * N[3 * i + 2] / l;
        }
        return N;
    }

    /** Achsenparallele Hülle der Punkte, um `rand` erweitert. */
    static huelle(P, rand) {
        const h = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
        for (let i = 0; i < P.length; i += 3) for (let d = 0; d < 3; d++) {
            if (P[i + d] < h[d]) h[d] = P[i + d];
            if (P[i + d] > h[3 + d]) h[3 + d] = P[i + d];
        }
        return [h[0] - rand, h[1] - rand, h[2] - rand, h[3] + rand, h[4] + rand, h[5] + rand];
    }

    /** Zellschlüssel als Zahl — Zeichenketten kosteten bei 70.851 Punkten
     *  mal 27 Zellen den Großteil der Rechenzeit. Reicht für ±1.000 Zellen. */
    static zelle(i, j, k) {
        return ((i + 1024) * 2048 + (j + 1024)) * 2048 + (k + 1024);
    }

    /** Zelle → Punktnummern. */
    static punktgitter(P, h) {
        const g = new Map();
        for (let i = 0; i < P.length / 3; i++) {
            const s = Hautmaskegeometrie.zelle(Math.floor(P[3 * i] / h), Math.floor(P[3 * i + 1] / h),
                                               Math.floor(P[3 * i + 2] / h));
            const liste = g.get(s);
            if (liste) liste.push(i); else g.set(s, [i]);
        }
        return g;
    }

    /** Nächster Punkt in den 27 Zellen um (px, py, pz) — `{j, d2}` oder null. */
    static naechsterPunkt(P, gitter, h, px, py, pz) {
        const ci = Math.floor(px / h), cj = Math.floor(py / h), ck = Math.floor(pz / h);
        let best = Infinity, bj = -1;
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            const L = gitter.get(Hautmaskegeometrie.zelle(ci + a, cj + b, ck + c));
            if (!L) continue;
            for (let l = 0; l < L.length; l++) {
                const j = L[l];
                const dx = P[3 * j] - px, dy = P[3 * j + 1] - py, dz = P[3 * j + 2] - pz;
                const d2 = dx * dx + dy * dy + dz * dz;
                if (d2 < best) { best = d2; bj = j; }
            }
        }
        return bj < 0 ? null : { j: bj, d2: best };
    }

    /**
     * Schnitt des Strahls p + t·r mit dem Dreieck abc (Möller–Trumbore) —
     * t, oder null. `r` muss nicht normiert sein; t ist dann in Vielfachen
     * von r. Beidseitig: Die Wicklung des Stoffs ist gleichgültig.
     */
    static strahlDreieck(P, a, b, c, px, py, pz, rx, ry, rz) {
        const ax = P[3 * a], ay = P[3 * a + 1], az = P[3 * a + 2];
        const e1x = P[3 * b] - ax, e1y = P[3 * b + 1] - ay, e1z = P[3 * b + 2] - az;
        const e2x = P[3 * c] - ax, e2y = P[3 * c + 1] - ay, e2z = P[3 * c + 2] - az;
        const hx = ry * e2z - rz * e2y, hy = rz * e2x - rx * e2z, hz = rx * e2y - ry * e2x;
        const det = e1x * hx + e1y * hy + e1z * hz;
        if (det > -1e-12 && det < 1e-12) return null;
        const f = 1 / det;
        const sx = px - ax, sy = py - ay, sz = pz - az;
        const u = f * (sx * hx + sy * hy + sz * hz);
        if (u < 0 || u > 1) return null;
        const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x;
        const v = f * (rx * qx + ry * qy + rz * qz);
        if (v < 0 || u + v > 1) return null;
        return f * (e2x * qx + e2y * qy + e2z * qz);
    }
}
