/**
 * Punktgitter — der nächste Punkt einer Wolke, über ein gleichmäßiges Gitter.
 *
 * WOFÜR (11.09.2026): Die Stoffgrenze braucht zu jedem Stoffpunkt den
 * nächsten Körperpunkt. Der Körper der Szene hat 70.851 Punkte, ein
 * T-Shirt 10.814 — jeder gegen jeden wären 766 Millionen Abstände, in
 * JavaScript mehrere Sekunden. Mit dem Gitter sind es je Anfrage die
 * Punkte weniger Zellen.
 *
 * KEIN k-d-Baum: Der ist für 70.000 Punkte in JavaScript langsamer zu
 * bauen als dieses Zählsortieren, und die Punkte liegen ohnehin fast
 * gleichmäßig auf einer Fläche.
 *
 * Abbruch der Ringsuche: Nach dem Würfel aus `r` Zellen um die eigene
 * liegt jeder noch nicht gesehene Punkt mindestens `r * zelle` entfernt
 * (die Anfrage liegt IN ihrer Zelle, der Würfelrand ist `r` Zellen weg).
 * Ist der beste Fund näher, ist er der nächste. Liegt die Anfrage außerhalb
 * des Gitters, wird ihre Zelle an den Rand geklemmt — jenseits des Randes
 * gibt es keine Punkte, die Schranke gilt weiter.
 */
export class Punktgitter {
    /** Zellen je Punkt im Mittel — zwei Punkte je Zelle halten die
     *  Zellenliste kurz und die Ringe klein. */
    static PUNKTE_JE_ZELLE = 2;
    static MINDEST_ZELLE = 0.005;
    static HOECHSTE_ZELLENZAHL = 4_000_000;

    /** @param punkte Float32Array/Float64Array n*3 */
    constructor(punkte, zelle = 0) {
        this.punkte = punkte;
        this.n = punkte.length / 3;
        this.min = [Infinity, Infinity, Infinity];
        this.max = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < this.n; i++) {
            for (let a = 0; a < 3; a++) {
                const v = punkte[3 * i + a];
                if (v < this.min[a]) this.min[a] = v;
                if (v > this.max[a]) this.max[a] = v;
            }
        }
        this.zelle = zelle > 0 ? zelle : this._zellengroesse();
        this.dim = [0, 1, 2].map((a) => Math.max(1, Math.floor((this.max[a] - this.min[a]) / this.zelle) + 1));
        this._sortieren();
    }

    _zellengroesse() {
        const raum = Math.max(this.max[0] - this.min[0], 1e-3)
            * Math.max(this.max[1] - this.min[1], 1e-3)
            * Math.max(this.max[2] - this.min[2], 1e-3);
        let zelle = Math.cbrt(raum * Punktgitter.PUNKTE_JE_ZELLE / Math.max(this.n, 1));
        zelle = Math.max(zelle, Punktgitter.MINDEST_ZELLE);
        // Nie mehr Zellen als erlaubt — ein weit gestreuter Ausreißer
        // ließe das Gitter sonst ins Unermessliche wachsen.
        while (raum / (zelle ** 3) > Punktgitter.HOECHSTE_ZELLENZAHL) zelle *= 2;
        return zelle;
    }

    _zellenkoordinate(v, a) {
        const c = Math.floor((v - this.min[a]) / this.zelle);
        return c < 0 ? 0 : (c >= this.dim[a] ? this.dim[a] - 1 : c);
    }

    _zellennummer(ix, iy, iz) { return ix + this.dim[0] * (iy + this.dim[1] * iz); }

    /** Zählsortieren: `start[z] .. start[z+1]` in `index` sind die Punkte der Zelle z. */
    _sortieren() {
        const zellen = this.dim[0] * this.dim[1] * this.dim[2];
        const zelleVon = new Int32Array(this.n);
        const anzahl = new Int32Array(zellen + 1);
        for (let i = 0; i < this.n; i++) {
            const z = this._zellennummer(
                this._zellenkoordinate(this.punkte[3 * i], 0),
                this._zellenkoordinate(this.punkte[3 * i + 1], 1),
                this._zellenkoordinate(this.punkte[3 * i + 2], 2));
            zelleVon[i] = z;
            anzahl[z + 1] += 1;
        }
        for (let z = 0; z < zellen; z++) anzahl[z + 1] += anzahl[z];
        this.start = anzahl;
        this.index = new Int32Array(this.n);
        const fuellstand = new Int32Array(zellen);
        for (let i = 0; i < this.n; i++) {
            const z = zelleVon[i];
            this.index[this.start[z] + fuellstand[z]] = i;
            fuellstand[z] += 1;
        }
    }

    /** Nummer des nächsten Punktes zu (x, y, z), -1 bei leerer Wolke. */
    naechster(x, y, z) {
        if (!this.n) return -1;
        const ix = this._zellenkoordinate(x, 0), iy = this._zellenkoordinate(y, 1), iz = this._zellenkoordinate(z, 2);
        const p = this.punkte;
        let best = -1, bestD = Infinity;
        const groesster = Math.max(...this.dim);
        for (let r = 0; r <= groesster; r++) {
            const x0 = Math.max(ix - r, 0), x1 = Math.min(ix + r, this.dim[0] - 1);
            const y0 = Math.max(iy - r, 0), y1 = Math.min(iy + r, this.dim[1] - 1);
            const z0 = Math.max(iz - r, 0), z1 = Math.min(iz + r, this.dim[2] - 1);
            for (let cz = z0; cz <= z1; cz++) {
                for (let cy = y0; cy <= y1; cy++) {
                    for (let cx = x0; cx <= x1; cx++) {
                        // Nur die Schale des Rings — das Innere war schon dran.
                        if (r > 0 && cx > x0 && cx < x1 && cy > y0 && cy < y1 && cz > z0 && cz < z1) continue;
                        const zn = this._zellennummer(cx, cy, cz);
                        for (let s = this.start[zn]; s < this.start[zn + 1]; s++) {
                            const i = this.index[s];
                            const dx = p[3 * i] - x, dy = p[3 * i + 1] - y, dz = p[3 * i + 2] - z;
                            const d = dx * dx + dy * dy + dz * dz;
                            if (d < bestD) { bestD = d; best = i; }
                        }
                    }
                }
            }
            if (best >= 0 && Math.sqrt(bestD) <= r * this.zelle) break;
        }
        return best;
    }

    /** Für jeden Punkt einer zweiten Wolke die Nummer des nächsten. */
    alleNaechsten(anfragen) {
        const m = anfragen.length / 3;
        const aus = new Int32Array(m);
        for (let i = 0; i < m; i++) {
            aus[i] = this.naechster(anfragen[3 * i], anfragen[3 * i + 1], anfragen[3 * i + 2]);
        }
        return aus;
    }
}
