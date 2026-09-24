import { Punktgitter } from './punktgitter.js';

/**
 * Bindungsrechner — die Ruhe-Zuordnung Stoffpunkt → Körperdreieck im BROWSER,
 * für Figuren, deren Kleidung der Server nicht bindet (HumanBody, 24.09.2026,
 * Auftrag Edgar „Implementiere das auch für HumanBody").
 *
 * Dieselbe Rechnung wie `Genesis9/oberflaechenbindung.py` (`G9oberflaechenbindung`),
 * dieselben Felder und Grenzen — der Shader (`oberflaecheglsl.js`) unterscheidet
 * nicht, woher sie kommen:
 *
 *     dreieck   die drei Körperpunkte des nächsten Dreiecks (−1: frei)
 *     bary      Baryzentrik des nächsten Punkts q darauf
 *     abstand   Ruheabstand (P − q)·n entlang der gemischten Normale (außen)
 *     mischung  1 bis NAH, linear 0 bei FERN
 *
 * KANDIDATEN: die Dreiecke um den nächsten Körperpunkt (`Punktgitter`). Der
 * Server nimmt die Dreiecke um die DREI nächsten; einer genügt hier, weil die
 * HumanBody-Haut gleichmäßig ist (Catmull-Clark, 70.851 Punkte auf Stufe 2).
 * Der nächste Punkt auf jedem Dreieck nach Ericson, „Real-Time Collision
 * Detection" 5.1.5.
 *
 * OHNE THREE.JS — Zahlenfelder rein, Zahlenfelder raus; in Node prüfbar.
 */
export class Bindungsrechner {

    /** Wie `G9oberflaechenbindung.NAH_M` / `FERN_M`. */
    static NAH = 0.025;
    static FERN = 0.08;

    /**
     * @param punkte   Körper in Ruhe, Float32Array n*3
     * @param index    Dreiecke (voller Index, nicht der maskierte), n_d*3
     * @param normalen AUSWÄRTS zeigende Punktnormalen, n*3
     */
    constructor(punkte, index, normalen) {
        this.punkte = punkte;
        this.index = index;
        this.normalen = normalen;
        this.gitter = new Punktgitter(punkte);
        this._faecher();
    }

    /** Dreiecke je Punkt als CSR: `start[i] .. start[i+1]` in `dreiecke`. */
    _faecher() {
        const n = this.punkte.length / 3, d = this.index.length / 3;
        const start = new Int32Array(n + 1);
        for (let k = 0; k < 3 * d; k++) start[this.index[k] + 1] += 1;
        for (let i = 0; i < n; i++) start[i + 1] += start[i];
        const stand = start.slice(0, n);
        const dreiecke = new Int32Array(3 * d);
        for (let t = 0; t < d; t++) {
            for (let e = 0; e < 3; e++) dreiecke[stand[this.index[3 * t + e]]++] = t;
        }
        this.start = start;
        this.dreiecke = dreiecke;
    }

    /** @param stoff Stoffpunkte in Ruhe, im Raum des Körpers, Float32Array k*3 */
    fuer(stoff) {
        const k = stoff.length / 3;
        const aus = {
            dreieck: new Float32Array(3 * k).fill(-1), bary: new Float32Array(3 * k),
            abstand: new Float32Array(k), mischung: new Float32Array(k),
        };
        const q = [0, 0, 0], b = [0, 0, 0];
        for (let i = 0; i < k; i++) {
            const x = stoff[3 * i], y = stoff[3 * i + 1], z = stoff[3 * i + 2];
            const v = this.gitter.naechster(x, y, z);
            if (v < 0) continue;
            let beste = -1, besteD = Infinity;
            const bb = [0, 0, 0];
            for (let s = this.start[v]; s < this.start[v + 1]; s++) {
                const t = this.dreiecke[s];
                const d2 = this.naechsterAufDreieck(x, y, z, t, q, b);
                if (d2 < besteD) { besteD = d2; beste = t; bb[0] = b[0]; bb[1] = b[1]; bb[2] = b[2]; }
            }
            if (beste < 0) continue;
            const weg = Math.sqrt(besteD);
            const mischung = Math.min(1, Math.max(0, (Bindungsrechner.FERN - weg) / (Bindungsrechner.FERN - Bindungsrechner.NAH)));
            if (!(mischung > 0)) continue;
            this._eintragen(aus, i, beste, bb, x, y, z, mischung);
        }
        return aus;
    }

    _eintragen(aus, i, t, bb, x, y, z, mischung) {
        const I = this.index, P = this.punkte, N = this.normalen;
        let qx = 0, qy = 0, qz = 0, nx = 0, ny = 0, nz = 0;
        for (let e = 0; e < 3; e++) {
            const p = I[3 * t + e];
            aus.dreieck[3 * i + e] = p;
            aus.bary[3 * i + e] = bb[e];
            qx += bb[e] * P[3 * p]; qy += bb[e] * P[3 * p + 1]; qz += bb[e] * P[3 * p + 2];
            nx += bb[e] * N[3 * p]; ny += bb[e] * N[3 * p + 1]; nz += bb[e] * N[3 * p + 2];
        }
        const laenge = Math.hypot(nx, ny, nz) || 1;
        aus.abstand[i] = ((x - qx) * nx + (y - qy) * ny + (z - qz) * nz) / laenge;
        aus.mischung[i] = mischung;
    }

    /**
     * Nächster Punkt auf Dreieck t zu (x, y, z) — Ericson 5.1.5. Schreibt ihn
     * nach `q` und die Baryzentrik (u, v, w) nach `b`; gibt das Abstandsquadrat.
     */
    naechsterAufDreieck(x, y, z, t, q, b) {
        const I = this.index, P = this.punkte;
        const a = 3 * I[3 * t], bi = 3 * I[3 * t + 1], c = 3 * I[3 * t + 2];
        const abx = P[bi] - P[a], aby = P[bi + 1] - P[a + 1], abz = P[bi + 2] - P[a + 2];
        const acx = P[c] - P[a], acy = P[c + 1] - P[a + 1], acz = P[c + 2] - P[a + 2];
        const apx = x - P[a], apy = y - P[a + 1], apz = z - P[a + 2];
        const d1 = abx * apx + aby * apy + abz * apz, d2 = acx * apx + acy * apy + acz * apz;
        let v, w;
        if (d1 <= 0 && d2 <= 0) { v = 0; w = 0; } else {
            const bpx = x - P[bi], bpy = y - P[bi + 1], bpz = z - P[bi + 2];
            const d3 = abx * bpx + aby * bpy + abz * bpz, d4 = acx * bpx + acy * bpy + acz * bpz;
            const cpx = x - P[c], cpy = y - P[c + 1], cpz = z - P[c + 2];
            const d5 = abx * cpx + aby * cpy + abz * cpz, d6 = acx * cpx + acy * cpy + acz * cpz;
            const vc = d1 * d4 - d3 * d2, vb = d5 * d2 - d1 * d6, va = d3 * d6 - d5 * d4;
            if (d3 >= 0 && d4 <= d3) { v = 1; w = 0; }
            else if (vc <= 0 && d1 >= 0 && d3 <= 0) { v = d1 / (d1 - d3); w = 0; }
            else if (d6 >= 0 && d5 <= d6) { v = 0; w = 1; }
            else if (vb <= 0 && d2 >= 0 && d6 <= 0) { v = 0; w = d2 / (d2 - d6); }
            else if (va <= 0 && (d4 - d3) >= 0 && (d5 - d6) >= 0) {
                w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); v = 1 - w;
            } else {
                const summe = va + vb + vc || 1;
                v = vb / summe; w = vc / summe;
            }
        }
        b[0] = 1 - v - w; b[1] = v; b[2] = w;
        q[0] = P[a] + v * abx + w * acx; q[1] = P[a + 1] + v * aby + w * acy; q[2] = P[a + 2] + v * abz + w * acz;
        const dx = q[0] - x, dy = q[1] - y, dz = q[2] - z;
        return dx * dx + dy * dy + dz * dz;
    }

    /**
     * +1, wenn die Normalen nach außen zeigen, sonst −1: die Summe von n·(p − Mitte).
     * HumanBodys `normal`-Attribut zeigt nach innen (`hauteinzug.js`,
     * `catmull_clark.py` negiert sie); Genesis 9 nach außen.
     */
    static vorzeichen(punkte, normalen) {
        const n = punkte.length / 3;
        let mx = 0, my = 0, mz = 0;
        for (let i = 0; i < n; i++) { mx += punkte[3 * i]; my += punkte[3 * i + 1]; mz += punkte[3 * i + 2]; }
        mx /= n || 1; my /= n || 1; mz /= n || 1;
        let summe = 0;
        for (let i = 0; i < n; i++) {
            summe += normalen[3 * i] * (punkte[3 * i] - mx) + normalen[3 * i + 1] * (punkte[3 * i + 1] - my)
                + normalen[3 * i + 2] * (punkte[3 * i + 2] - mz);
        }
        return summe < 0 ? -1 : 1;
    }
}
