import { Querschnitthuelle } from './querschnitthuelle.js';

/**
 * Eigenrockhuelle — der Körper unter einem eigenen Rock oder Kleid als Hülle je Höhe (Stufe K3, 25.10.2026 nachts; Konzept
 * `Docu/konzepte/2026-10-25_eigene-kleider-konzept.md`, Abschnitt 3: „Rock/Kleid überbrückt zwischen den Beinen → Hülle je Höhenschnitt über beide Beine“).
 * Ohne Three.js, in Node prüfbar.
 *
 * Waagrechte Scheiben (`SCHEIBE_M`) von `oben` bis `unten` über die Hautpunkte von Rumpf und Beinen (Ketten der Körperkoordinaten 1, 4, 5 — Arme, Hände, Hals,
 * Kopf und Füße nicht), je Scheibe die konvexe Hülle (`Querschnitthuelle`) und ihr Halbmesser in `WINKEL` Richtungen um die Achse `mitte` (Winkel wie die Karte:
 * 0 = vorn +z, 0,25 = links der Figur +x). Zwischen den Beinen spannt die Hülle — der Rock läuft nicht in den Schritt. Je Scheibe und Richtung merkt sie den äußersten
 * Hautpunkt (`stuetze`): dessen Hautgewichte trägt der Rock dort (`Eigenrockgeometrie`). `hinaus` ist dieselbe Hülle als Körper für `Stoffpendel.oberflaeche`.
 */
export class Eigenrockhuelle {

    static KETTEN = new Set([1, 4, 5]);
    static SCHEIBE_M = 0.01;
    static WINKEL = 128;

    /**
     * @param pos    Float32Array (n·3) Hautpunkte in Ruhe (Bindlage des Körpers)
     * @param koord  Float32Array (n·4) Körperkoordinaten (Kette, Anteil, Höhe, Winkel)
     * @param oben   Höhe (m) der obersten Scheibe;  unten: der untersten
     * @param mitte  [x, z] der Achse
     */
    constructor(pos, koord, oben, unten, mitte) {
        const S = Eigenrockhuelle.SCHEIBE_M, W = Eigenrockhuelle.WINKEL;
        this.oben = oben;
        this.mitte = mitte;
        /** Abstand (m), um den `hinaus` über der Hülle hält — der Sitz des Rocks. */
        this.zugabe = 0;
        this.n = Math.max(2, Math.ceil((oben - unten) / S) + 1);
        this.r = new Float32Array(this.n * W);
        this.stuetze = new Int32Array(this.n * W).fill(-1);
        const scheiben = Array.from({ length: this.n }, () => []);
        for (let i = 0; i < koord.length / 4; i++) {
            if (!Eigenrockhuelle.KETTEN.has(Math.round(koord[4 * i]))) continue;
            const s = Math.floor((oben - pos[3 * i + 1]) / S);
            for (const t of [s, s + 1]) if (t >= 0 && t < this.n) scheiben[t].push(i);
        }
        for (let s = 0; s < this.n; s++) this._scheibe(s, scheiben[s], pos);
        for (let s = 1; s < this.n; s++) {
            if (this.r.subarray(s * W, (s + 1) * W).some(v => v > 0)) continue;     // unter den Füßen: die Scheibe darüber
            this.r.copyWithin(s * W, (s - 1) * W, s * W);
            this.stuetze.copyWithin(s * W, (s - 1) * W, s * W);
        }
    }

    _scheibe(s, punkte, pos) {
        const W = Eigenrockhuelle.WINKEL, [cx, cz] = this.mitte;
        if (punkte.length < 3) return;
        const xz = punkte.map(i => [pos[3 * i] - cx, pos[3 * i + 2] - cz]);
        const weit = new Float32Array(W);
        for (let k = 0; k < punkte.length; k++) {
            const [x, z] = xz[k], r = Math.hypot(x, z);
            const w = Eigenrockhuelle.fach(Math.atan2(x, z) / (2 * Math.PI));
            if (r > weit[w]) { weit[w] = r; this.stuetze[s * W + w] = punkte[k]; }
        }
        const h = Querschnitthuelle.huelle(xz);
        if (h.length < 3) return;
        for (let w = 0; w < W; w++) {
            const a = 2 * Math.PI * w / W;
            this.r[s * W + w] = Querschnitthuelle.strahl(h, Math.sin(a), Math.cos(a))[0];
        }
    }

    /** Richtung als Anteil einer Umdrehung → Fach 0 … WINKEL−1. */
    static fach(anteil) {
        const W = Eigenrockhuelle.WINKEL;
        return ((Math.round(anteil * W) % W) + W) % W;
    }

    /** Scheibe zur Höhe y (begrenzt). */
    scheibe(y) {
        return Math.min(this.n - 1, Math.max(0, Math.round((this.oben - y) / Eigenrockhuelle.SCHEIBE_M)));
    }

    /** Halbmesser (m) der Hülle in Höhe y und Richtung `anteil` (Umdrehung), linear zwischen Scheiben und Richtungen. */
    halbmesser(y, anteil) {
        const W = Eigenrockhuelle.WINKEL;
        const f = Math.min(this.n - 1, Math.max(0, (this.oben - y) / Eigenrockhuelle.SCHEIBE_M));
        const s0 = Math.floor(f), s1 = Math.min(this.n - 1, s0 + 1), a = f - s0;
        const g = (((anteil % 1) + 1) % 1) * W, w0 = Math.floor(g) % W, w1 = (w0 + 1) % W, b = g - Math.floor(g);
        const r = (s, w) => this.r[s * W + w];
        return (1 - a) * ((1 - b) * r(s0, w0) + b * r(s0, w1)) + a * ((1 - b) * r(s1, w0) + b * r(s1, w1));
    }

    /** Wie `Stoffoberflaeche.hinaus`: freie Punkte (`frei > 0`) radial aus der Hülle, auf `abstand` + `zugabe` darüber. `x` in place. */
    hinaus(x, frei, n, abstand) {
        const [cx, cz] = this.mitte, zu = abstand + this.zugabe;
        for (let i = 0; i < n; i++) {
            if (frei[i] <= 0) continue;
            const o = 3 * i, dx = x[o] - cx, dz = x[o + 2] - cz, d = Math.hypot(dx, dz);
            if (d < 1e-6) continue;
            const r = this.halbmesser(x[o + 1], Math.atan2(dx, dz) / (2 * Math.PI)) + zu;
            if (d < r) { x[o] = cx + dx * r / d; x[o + 2] = cz + dz * r / d; }
        }
    }
}
