import { Anatomierahmen } from './anatomierahmen.js';

/**
 * Anatomiedreiecke — je Dreieck einer Fläche das, was `Anatomiebild` für jedes Texel braucht, einmal gerechnet und gemerkt (11.10.2026).
 *
 * Gemerkt wird erst beim ersten Zugriff: von den 200.000 Dreiecken der Haut wird nur ein paar Tausend gebraucht.
 * - `rahmen(t)`: Tangentenrahmen `[∇u, ∇v, N]` (`Anatomierahmen`), bei entarteten Dreiecken die Einheitsmatrix.
 * - `gram(t)`: die Größen, mit denen sich eine Verschiebung in der Fläche in eine Änderung der UV umrechnen lässt
 *   (`[g11, g12, g22, det, du1, dv1, du2, dv2]`, `det` = 0 bei einem entarteten Dreieck).
 * - `proPixel(t)` (nur Stück): die Verschiebung im Raum je Pixel der Atlas-Karte (`[dPdx(3), dPdy(3)]`), für die Mittelung im Texel.
 */
export class Anatomiedreiecke {

    /** @param ecken  Punktnummern, drei je Dreieck;  @param normal  Normalen je Punkt oder null */
    constructor(pos, uv, normal, ecken) {
        this.pos = pos; this.uv = uv; this.normal = normal; this.ecken = ecken;
        const n = Math.floor(ecken.length / 3);
        this._rahmen = new Float64Array(9 * n); this._rahmenGern = new Uint8Array(n);
        this._gram = new Float64Array(8 * n); this._gramGern = new Uint8Array(n);
        this._pixel = new Float64Array(6 * n); this._pixelGern = new Uint8Array(n);
        this._invers = new Float64Array(9 * n); this._inversGern = new Uint8Array(n);
    }

    /** Anfang (in `matrix`) des Rahmens von Dreieck `t`. */
    rahmen(t) {
        if (!this._rahmenGern[t]) {
            const e = this.ecken;
            if (!Anatomierahmen.rahmen(this.pos, this.uv, this.normal, e[3 * t], e[3 * t + 1], e[3 * t + 2], this._rahmen, 9 * t)) Anatomierahmen.eins(this._rahmen, 9 * t);
            this._rahmenGern[t] = 1;
        }
        return 9 * t;
    }

    get matrix() {
        return this._rahmen;
    }

    /** Anfang (in `umkehr`) der Umkehrmatrix des Rahmens von `t` (Einheitsmatrix, wenn sie nicht existiert). */
    umkehrung(t) {
        if (!this._inversGern[t]) {
            const o = this.rahmen(t);
            if (!Anatomierahmen.invers(this._rahmen, o, this._invers, 9 * t)) Anatomierahmen.eins(this._invers, 9 * t);
            this._inversGern[t] = 1;
        }
        return 9 * t;
    }

    get umkehr() {
        return this._invers;
    }

    /** Die Größen für die UV-Umrechnung von Dreieck `t` (Anfang in `gramm`). */
    gram(t) {
        if (!this._gramGern[t]) {
            const [a, b, c] = [this.ecken[3 * t], this.ecken[3 * t + 1], this.ecken[3 * t + 2]], p = this.pos, uv = this.uv, o = 8 * t;
            const e1 = [0, 1, 2].map(k => p[3 * b + k] - p[3 * a + k]), e2 = [0, 1, 2].map(k => p[3 * c + k] - p[3 * a + k]);
            const g11 = e1[0] * e1[0] + e1[1] * e1[1] + e1[2] * e1[2], g12 = e1[0] * e2[0] + e1[1] * e2[1] + e1[2] * e2[2], g22 = e2[0] * e2[0] + e2[1] * e2[1] + e2[2] * e2[2];
            const det = g11 * g22 - g12 * g12;
            this._gram.set([g11, g12, g22, det > 1e-30 ? det : 0, uv[2 * b] - uv[2 * a], uv[2 * b + 1] - uv[2 * a + 1], uv[2 * c] - uv[2 * a], uv[2 * c + 1] - uv[2 * a + 1]], o);
            this._gramGern[t] = 1;
        }
        return 8 * t;
    }

    get gramm() {
        return this._gram;
    }

    /**
     * Die UV-Änderung (`aus[0]` = du, `aus[1]` = dv) von Dreieck `t`, wenn man sich um `(dx, dy, dz)` im Raum bewegt (in der Fläche; was senkrecht
     * dazu steht, geht nicht ein). Ein entartetes Dreieck ändert nichts.
     */
    uvAenderung(t, dx, dy, dz, aus) {
        const o = this.gram(t), g = this._gram, e = this.ecken, p = this.pos, a = e[3 * t];
        aus[0] = aus[1] = 0;
        if (g[o + 3] === 0) return aus;
        const b = e[3 * t + 1], c = e[3 * t + 2];
        const d1 = (p[3 * b] - p[3 * a]) * dx + (p[3 * b + 1] - p[3 * a + 1]) * dy + (p[3 * b + 2] - p[3 * a + 2]) * dz;
        const d2 = (p[3 * c] - p[3 * a]) * dx + (p[3 * c + 1] - p[3 * a + 1]) * dy + (p[3 * c + 2] - p[3 * a + 2]) * dz;
        const s = (g[o + 2] * d1 - g[o + 1] * d2) / g[o + 3], r = (g[o] * d2 - g[o + 1] * d1) / g[o + 3];
        aus[0] = s * g[o + 4] + r * g[o + 6];
        aus[1] = s * g[o + 5] + r * g[o + 7];
        return aus;
    }

    /**
     * Die Verschiebung im Raum je Pixel der Atlas-Karte von Dreieck `t` (Anfang in `pixel`); `breite`, `hoehe`: Größe der Karte.
     * `uvKarte`: die UV in Zeilen der Karte (bei einer Karte mit `flipY` gegenüber der UV des Netzes gewendet), sonst `uv`.
     */
    proPixel(t, breite, hoehe, uvKarte = this.uv) {
        if (!this._pixelGern[t]) {
            const [a, b, c] = [this.ecken[3 * t], this.ecken[3 * t + 1], this.ecken[3 * t + 2]], p = this.pos, uv = uvKarte, o = 6 * t;
            const a1x = (uv[2 * b] - uv[2 * a]) * breite, a1y = (uv[2 * b + 1] - uv[2 * a + 1]) * hoehe;
            const a2x = (uv[2 * c] - uv[2 * a]) * breite, a2y = (uv[2 * c + 1] - uv[2 * a + 1]) * hoehe;
            const det = a1x * a2y - a1y * a2x;
            for (let k = 0; k < 3; k++) {
                const e1 = p[3 * b + k] - p[3 * a + k], e2 = p[3 * c + k] - p[3 * a + k];
                this._pixel[o + k] = Math.abs(det) > 1e-12 ? (e1 * a2y - e2 * a1y) / det : 0;
                this._pixel[o + 3 + k] = Math.abs(det) > 1e-12 ? (e2 * a1x - e1 * a2x) / det : 0;
            }
            this._pixelGern[t] = 1;
        }
        return 6 * t;
    }

    get pixel() {
        return this._pixel;
    }
}
