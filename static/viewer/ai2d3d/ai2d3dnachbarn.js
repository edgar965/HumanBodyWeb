/**
 * Ai2d3dnachbarn — Punkte einer Wolke in einem Gitter, und für einen beliebigen Punkt die Nachbarn daraus mit weichen Gewichten (31.10.2026 nachts, aus `Ai2d3dzeile1`
 * herausgelöst; dort und in `Ai2d3dzeile1form` verteilt es die Verschiebung der Käfigpunkte auf Netze mit anderen Punkten).
 *
 * Gewicht exp(−(d/σ)²) bis `RADIUS`, Summe 1; ohne Nachbarn im Radius der nächste in bis zu drei Ringen, sonst []. Weich statt nur der nächste: mit einem Punkt rissen die
 * Seiten des T-Shirts an der Achsel auf, wo der nächste Körperpunkt zwischen Arm und Rumpf springt (31.10.2026).
 */
export class Ai2d3dnachbarn {
    static ZELLE = 0.015;
    static RADIUS = 0.03;
    static SIGMA = 0.012;

    /** @param punkte Float32Array (x, y, z …) @param n die ersten n Punkte kommen ins Gitter */
    constructor(punkte, n = punkte.length / 3) {
        this.punkte = punkte;
        this.gitter = new Map();
        for (let i = 0; i < n; i++) {
            const k = Ai2d3dnachbarn.zelle(punkte, i).join(',');
            if (!this.gitter.has(k)) this.gitter.set(k, []);
            this.gitter.get(k).push(i);
        }
    }

    static zelle(a, i) {
        return [0, 1, 2].map(c => Math.floor(a[i * 3 + c] / Ai2d3dnachbarn.ZELLE));
    }

    /** Nachbarn von a[i] → [[j, w], …]. */
    gewichte(a, i) {
        const [x, y, z] = Ai2d3dnachbarn.zelle(a, i), s2 = Ai2d3dnachbarn.SIGMA ** 2, r2 = Ai2d3dnachbarn.RADIUS ** 2, p = this.punkte;
        for (let r = 2; r <= 3; r++) {
            const liste = [];
            let best = -1, bd = Infinity, summe = 0;
            for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) for (let dz = -r; dz <= r; dz++) {
                for (const j of this.gitter.get(`${x + dx},${y + dy},${z + dz}`) || []) {
                    const d = (a[i * 3] - p[j * 3]) ** 2 + (a[i * 3 + 1] - p[j * 3 + 1]) ** 2 + (a[i * 3 + 2] - p[j * 3 + 2]) ** 2;
                    if (d < bd) { bd = d; best = j; }
                    if (d < r2) { const w = Math.exp(-d / s2); liste.push([j, w]); summe += w; }
                }
            }
            if (summe > 1e-6) return liste.map(([j, w]) => [j, w / summe]);
            if (best >= 0) return [[best, 1]];
        }
        return [];
    }
}
