/**
 * Hautstellengitter — dichtes Gitter über die Hautdreiecke von `Genesis9hautebenenstueck` für die Stückpunkte FERN der Haut (21.11.2026).
 *
 * Ladezeit /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/ (Edgar: „ladezeit ewig! fixe"): Am Glied von „Daz Anatomie Mann" lagen 3.798 von 6.979
 * Stückpunkten mehr als eine Zelle vor der Haut; `_stelle` prüfte für jeden alle 3.668 Hautdreiecke, zweimal (im Tab 4,5–6,4 s auf dem Hauptfaden). Hier
 * liefert das Gitter je Punkt nur die Dreiecke, die gewinnen KÖNNEN — aufsteigend nach Nummer, damit bei Gleichstand dasselbe Dreieck gewinnt wie beim
 * Durchlauf über alle:
 *   `kugel`    alle, deren Kasten in der Kugel um den Punkt liegt (der nächste Punkt liegt höchstens `schranke` entfernt),
 *   `strecke`  alle in den Zellen, durch die die Strahlstrecke läuft (Amanatides/Woo) — ein Treffer liegt auf der Strecke und in seinem Kasten.
 * Die Kästen sind die erweiterten aus `Genesis9hautebenenstueck._vorauswahl` (Treffer bis `Strahldreieck.RAND` neben dem Dreieck, +1e-9 m Rand gegen Rundung);
 * eingetragen wird jedes Dreieck in jede Zelle, die sein Kasten berührt. Ohne Three.js und ohne DOM (Node-Tests).
 */
export class Hautstellengitter {

    /** Höchstens so viele Zellen; darüber wird die Zelle größer. */
    static ZELLEN_MAX = 2_000_000;

    /** @param kaesten Float64Array 6·T `[x0, y0, z0, x1, y1, z1]` je Dreieck @param zelle Kantenlänge (m) */
    constructor(kaesten, zelle) {
        const T = kaesten.length / 6, lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let t = 0; t < T; t++) {
            for (let d = 0; d < 3; d++) {
                if (kaesten[6 * t + d] < lo[d]) lo[d] = kaesten[6 * t + d];
                if (kaesten[6 * t + 3 + d] > hi[d]) hi[d] = kaesten[6 * t + 3 + d];
            }
        }
        let z = zelle;
        const zahl = (k) => [0, 1, 2].map((d) => Math.max(1, Math.floor((hi[d] - lo[d]) / k) + 1));
        while (zahl(z).reduce((a, b) => a * b, 1) > Hautstellengitter.ZELLEN_MAX) z *= 2;
        this.T = T;
        this.z = z;
        this.lo = lo;
        this.n = zahl(z);
        const [n0, n1, n2] = this.n, anfang = new Int32Array(n0 * n1 * n2 + 1), v = new Int32Array(3), b = new Int32Array(3);
        const bereich = (t) => {
            for (let d = 0; d < 3; d++) {
                v[d] = this._zelle(kaesten[6 * t + d], d);
                b[d] = this._zelle(kaesten[6 * t + 3 + d], d);
            }
        };
        for (let t = 0; t < T; t++) {
            bereich(t);
            for (let x = v[0]; x <= b[0]; x++) for (let y = v[1]; y <= b[1]; y++) for (let w = v[2]; w <= b[2]; w++) anfang[(x * n1 + y) * n2 + w + 1]++;
        }
        for (let c = 0; c < n0 * n1 * n2; c++) anfang[c + 1] += anfang[c];
        const eintraege = new Int32Array(anfang[n0 * n1 * n2]), stand = anfang.slice(0, n0 * n1 * n2);
        for (let t = 0; t < T; t++) {                                   // aufsteigend: jede Zellenliste ist nach Nummer sortiert
            bereich(t);
            for (let x = v[0]; x <= b[0]; x++) for (let y = v[1]; y <= b[1]; y++) for (let w = v[2]; w <= b[2]; w++) eintraege[stand[(x * n1 + y) * n2 + w]++] = t;
        }
        this.anfang = anfang;
        this.eintraege = eintraege;
        this.marke = new Int32Array(T);
        this.stempel = 0;
        /** Die Liste der letzten Anfrage (`wuerfel`, `strecke`): die ersten `zahl` Einträge, aufsteigend. */
        this.liste = new Int32Array(T);
    }

    /** Zelle (Achse `d`) einer Koordinate, an den Rand geklemmt. */
    _zelle(w, d) {
        const c = Math.floor((w - this.lo[d]) / this.z);
        return c < 0 ? 0 : (c >= this.n[d] ? this.n[d] - 1 : c);
    }

    /** Die Dreiecke einer Zelle in die Liste, die schon drin sind nicht (`marke`/`stempel`); zurück die neue Zahl. */
    _sammeln(zelle, zahl) {
        for (let e = this.anfang[zelle]; e < this.anfang[zelle + 1]; e++) {
            const t = this.eintraege[e];
            if (this.marke[t] === this.stempel) continue;
            this.marke[t] = this.stempel;
            this.liste[zahl++] = t;
        }
        return zahl;
    }

    /**
     * Obere Schranke für den Abstand² zum nächsten Dreieck: der kleinste `abstand2(t)` (der echte Abstand², `Dreiecksabstand`) über die Dreiecke der ersten Schale
     * von Zellen um den Punkt, die Dreiecke hat. Infinity ohne Dreiecke.
     */
    schranke(x, y, z, abstand2) {
        const [n0, n1, n2] = this.n, c0 = this._zelle(x, 0), c1 = this._zelle(y, 1), c2 = this._zelle(z, 2), rmax = Math.max(n0, n1, n2);
        let beste = Infinity;
        const zelle = (a, b, w) => {
            const k = (a * n1 + b) * n2 + w;
            for (let e = this.anfang[k]; e < this.anfang[k + 1]; e++) {
                const d2 = abstand2(this.eintraege[e]);
                if (d2 < beste) beste = d2;
            }
        };
        for (let r = 0; r <= rmax; r++) {
            for (let a = Math.max(0, c0 - r); a <= Math.min(n0 - 1, c0 + r); a++) {
                for (let b = Math.max(0, c1 - r); b <= Math.min(n1 - 1, c1 + r); b++) {
                    if (r === 0 || Math.abs(a - c0) === r || Math.abs(b - c1) === r) {          // Seitenfläche der Schale: die ganze Säule
                        for (let w = Math.max(0, c2 - r); w <= Math.min(n2 - 1, c2 + r); w++) zelle(a, b, w);
                    } else {                                                                     // innen: nur Boden und Deckel
                        if (c2 - r >= 0) zelle(a, b, c2 - r);
                        if (c2 + r < n2) zelle(a, b, c2 + r);
                    }
                }
            }
            if (beste < Infinity) return beste;
        }
        return Infinity;
    }

    /**
     * Alle Dreiecke, deren Kasten (`kaesten`, dieselben wie beim Bau) höchstens `h` vom Punkt liegt — aufsteigend in `liste`, zurück ihre Zahl. Gelaufen wird nur
     * durch die Zellen, die die Kugel mit Radius `h` berühren.
     */
    kugel(x, y, z, h, kaesten) {
        const [, n1, n2] = this.n, Z = this.z, lo = this.lo, h2 = h * h;
        const v0 = this._zelle(x - h, 0), v1 = this._zelle(y - h, 1), v2 = this._zelle(z - h, 2), b0 = this._zelle(x + h, 0), b1 = this._zelle(y + h, 1), b2 = this._zelle(z + h, 2);
        const weg = (w, a, d) => { const u = lo[d] + a * Z; return w < u ? u - w : (w > u + Z ? w - u - Z : 0); };     // Abstand der Koordinate zur Zellscheibe
        this.stempel++;
        let zahl = 0;
        for (let a = v0; a <= b0; a++) {
            const da = weg(x, a, 0), qa = da * da;
            if (qa > h2) continue;
            for (let b = v1; b <= b1; b++) {
                const db = weg(y, b, 1), qb = qa + db * db;
                if (qb > h2) continue;
                for (let w = v2; w <= b2; w++) {
                    const dw = weg(z, w, 2);
                    if (qb + dw * dw > h2) continue;
                    const k = (a * n1 + b) * n2 + w;
                    for (let e = this.anfang[k]; e < this.anfang[k + 1]; e++) {
                        const t = this.eintraege[e];
                        if (this.marke[t] === this.stempel) continue;
                        this.marke[t] = this.stempel;
                        const o = 6 * t;
                        const ex = Math.max(kaesten[o] - x, 0, x - kaesten[o + 3]), ey = Math.max(kaesten[o + 1] - y, 0, y - kaesten[o + 4]);
                        const ez = Math.max(kaesten[o + 2] - z, 0, z - kaesten[o + 5]);
                        if (ex * ex + ey * ey + ez * ez <= h2) this.liste[zahl++] = t;
                    }
                }
            }
        }
        this.liste.subarray(0, zahl).sort();
        return zahl;
    }

    /**
     * Alle Dreiecke in den Zellen, durch die die Strecke p + s·m, s in [−g, g] läuft (m Einheitsvektor) — aufsteigend in `liste`, zurück ihre Zahl. Die Strecke wird
     * erst an das Gitter geklemmt; gelaufen wird nach Amanatides/Woo von Zellwand zu Zellwand.
     */
    strecke(x, y, z, mx, my, mz, g) {
        const p = [x, y, z], m = [mx, my, mz], Z = this.z;
        let s0 = -g, s1 = g;
        for (let d = 0; d < 3; d++) {
            const a = this.lo[d], b = this.lo[d] + this.n[d] * Z;
            if (m[d] === 0) {
                if (p[d] < a || p[d] > b) return 0;
                continue;
            }
            let ta = (a - p[d]) / m[d], tb = (b - p[d]) / m[d];
            if (ta > tb) [ta, tb] = [tb, ta];
            if (ta > s0) s0 = ta;
            if (tb < s1) s1 = tb;
        }
        if (s0 > s1) return 0;
        const c = [0, 1, 2].map((d) => this._zelle(p[d] + s0 * m[d], d));
        const schritt = m.map((w) => (w > 0 ? 1 : -1)), delta = m.map((w) => (w !== 0 ? Z / Math.abs(w) : Infinity));
        const naechste = [0, 1, 2].map((d) => (m[d] !== 0 ? (this.lo[d] + (c[d] + (m[d] > 0 ? 1 : 0)) * Z - p[d]) / m[d] : Infinity));
        const [, n1, n2] = this.n;
        this.stempel++;
        let zahl = 0;
        for (;;) {
            zahl = this._sammeln((c[0] * n1 + c[1]) * n2 + c[2], zahl);
            const a = naechste[0] < naechste[1] ? (naechste[0] < naechste[2] ? 0 : 2) : (naechste[1] < naechste[2] ? 1 : 2);
            if (naechste[a] > s1) break;
            c[a] += schritt[a];
            if (c[a] < 0 || c[a] >= this.n[a]) break;
            naechste[a] += delta[a];
        }
        this.liste.subarray(0, zahl).sort();
        return zahl;
    }
}
