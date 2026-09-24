import { Bindungsrechner } from './bindungsrechner.js';

/**
 * Gcnachformung — Stoffpunkte vom alten auf den neuen Körper umsetzen.
 *
 * WARUM (24.09.2026, Edgar: „fixe auch dies" — GarmentCode-Stücke auf Genesis 9
 * folgten keinem Reglerzug): Daz-Stücke rechnet der Server je Zug neu, ein
 * GarmentCode-Stück ist eine Simulation von 20–30 s. Die Stoffvorschau für
 * HumanBody (`Stoffnachfuehrung`) bindet an das MakeHuman-Grundnetz und passt
 * nicht. Hier dasselbe Prinzip im Browser: Jeder Stoffpunkt merkt sich das
 * nächste Dreieck des ALTEN Körpers, die Baryzentrik seines Fußpunkts und den
 * Versatz im Rahmen des Dreiecks (Kante, Querrichtung, Flächennormale) — und
 * wird auf dem NEUEN Körper (gleiche Topologie) daraus wieder zusammengesetzt.
 * Mit dem vollen Rahmen statt nur der Normale ist die Umsetzung auf einem
 * unveränderten Körper exakt; viele Züge hintereinander wandern nicht.
 *
 * OHNE THREE.JS — Zahlenfelder rein und raus; in Node prüfbar
 * (`test_js_gcnachformung`).
 */
export class Gcnachformung {

    /**
     * @param alt      Körper vorher, Float32Array n*3
     * @param neu      Körper nachher, dieselben n Punkte
     * @param index    Dreiecke (voller Index), n_d*3
     * @param stoff    Stoffpunkte im Raum des Körpers, k*3
     * @param normalen Stoffnormalen k*3 oder null — werden mitgedreht
     * @returns {punkte, normalen} (normalen null ohne Eingabe) oder null bei ungleicher Topologie
     */
    static umsetzen(alt, neu, index, stoff, normalen = null) {
        if (!alt?.length || alt.length !== neu?.length || !index?.length) return null;
        const rechner = new Bindungsrechner(alt, index, null);
        const k = stoff.length / 3;
        const punkte = Float32Array.from(stoff);
        const aus = normalen ? Float32Array.from(normalen) : null;
        const q = [0, 0, 0], b = [0, 0, 0], bb = [0, 0, 0];
        const ra = new Float64Array(9), rn = new Float64Array(9);
        for (let i = 0; i < k; i++) {
            const x = stoff[3 * i], y = stoff[3 * i + 1], z = stoff[3 * i + 2];
            const t = Gcnachformung._dreieck(rechner, x, y, z, q, b, bb);
            if (t < 0) continue;
            Gcnachformung._rahmen(alt, index, t, ra);
            Gcnachformung._rahmen(neu, index, t, rn);
            const fuss = Gcnachformung._fuss(neu, index, t, bb);
            const dx = x - q[0], dy = y - q[1], dz = z - q[2];
            for (let e = 0; e < 3; e++) {
                const o0 = dx * ra[0] + dy * ra[1] + dz * ra[2];
                const o1 = dx * ra[3] + dy * ra[4] + dz * ra[5];
                const o2 = dx * ra[6] + dy * ra[7] + dz * ra[8];
                punkte[3 * i + e] = fuss[e] + o0 * rn[e] + o1 * rn[3 + e] + o2 * rn[6 + e];
            }
            if (aus) Gcnachformung._drehen(aus, i, ra, rn);
        }
        return { punkte, normalen: aus };
    }

    /** Nächstes Dreieck um den nächsten Körperpunkt; Fußpunkt nach q, Baryzentrik nach bb. */
    static _dreieck(rechner, x, y, z, q, b, bb) {
        const v = rechner.gitter.naechster(x, y, z);
        if (v < 0) return -1;
        let beste = -1, besteD = Infinity;
        const fq = [0, 0, 0];
        for (let s = rechner.start[v]; s < rechner.start[v + 1]; s++) {
            const t = rechner.dreiecke[s];
            const d2 = rechner.naechsterAufDreieck(x, y, z, t, q, b);
            if (d2 < besteD) {
                besteD = d2; beste = t;
                bb[0] = b[0]; bb[1] = b[1]; bb[2] = b[2]; fq[0] = q[0]; fq[1] = q[1]; fq[2] = q[2];
            }
        }
        q[0] = fq[0]; q[1] = fq[1]; q[2] = fq[2];
        return beste;
    }

    /** Orthonormaler Rahmen des Dreiecks t: e1 (Kante ab), e2 = n × e1, n (Fläche). */
    static _rahmen(P, I, t, r) {
        const a = 3 * I[3 * t], b = 3 * I[3 * t + 1], c = 3 * I[3 * t + 2];
        const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2];
        const vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
        let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
        const ln = Math.hypot(nx, ny, nz) || 1, lu = Math.hypot(ux, uy, uz) || 1;
        nx /= ln; ny /= ln; nz /= ln;
        const ex = ux / lu, ey = uy / lu, ez = uz / lu;
        r[0] = ex; r[1] = ey; r[2] = ez;
        r[3] = ny * ez - nz * ey; r[4] = nz * ex - nx * ez; r[5] = nx * ey - ny * ex;
        r[6] = nx; r[7] = ny; r[8] = nz;
    }

    static _fuss(P, I, t, bb) {
        const f = [0, 0, 0];
        for (let e = 0; e < 3; e++) {
            const p = 3 * I[3 * t + e];
            f[0] += bb[e] * P[p]; f[1] += bb[e] * P[p + 1]; f[2] += bb[e] * P[p + 2];
        }
        return f;
    }

    /** Eine Normale vom alten in den neuen Rahmen drehen. */
    static _drehen(n, i, ra, rn) {
        const x = n[3 * i], y = n[3 * i + 1], z = n[3 * i + 2];
        const o = [x * ra[0] + y * ra[1] + z * ra[2], x * ra[3] + y * ra[4] + z * ra[5],
                   x * ra[6] + y * ra[7] + z * ra[8]];
        for (let e = 0; e < 3; e++) n[3 * i + e] = o[0] * rn[e] + o[1] * rn[3 + e] + o[2] * rn[6 + e];
    }
}
