/**
 * Hautwege — kürzeste Wege auf einem Dreiecksnetz von vielen Quellen aus
 * (Dijkstra über die Netzkanten, Kantenlänge als Gewicht).
 *
 * Für das `Saumband` (13.09.2026): Wie weit liegt ein verdeckter Hautpunkt
 * von der gezeichneten Haut — auf der Haut entlang, nicht durch den Körper.
 * Ein Raumabstand misst über die Achsel oder den Schritt hinweg zu kurz,
 * und mit 15 cm Reichweite wäre ein Suchgitter zu teuer (Zellen von 15 cm
 * halten Tausende Punkte). Dijkstra mit Halde: 74.128 Punkte, 220.000
 * Kanten, Abbruch an der Reichweite.
 *
 * NÄHTE: Der Körper hat doppelte Punkte an der Rückenmitte. Ohne
 * Verbindung wären die Hälften getrennte Graphen; deckungsgleiche Punkte
 * bekommen deshalb eine Kante der Länge 0.
 *
 * DIE WEGE IN DOUBLE, NICHT FLOAT32 (13.09.2026, Szene eingefroren): Mit
 * `weg` als Float32Array rundete der gespeicherte Weg auf, die Halde
 * rechnete in double — an einer Naht (Länge 0) blieb `d < weg[j]` für
 * beide Zwillinge wahr, und sie schoben sich endlos gegenseitig in die
 * Halde (332 Einträge, nie leer). Dazu ein Wächter: Mehr Entnahmen als
 * Quellen + Kanten kann ein Dijkstra nicht brauchen; darüber ist es ein
 * Fehler, kein Warten.
 *
 * Ohne Three.js und ohne DOM (`test_js_saumband`).
 */
export class Hautwege {

    /**
     * Je Punkt der kürzeste Weg zu einer Quelle, höchstens `reichweite`
     * (darüber `Infinity`); Quellen 0.
     * @param pos        Punkte xyz
     * @param dreiecke   Index (drei Einträge je Dreieck)
     * @param quellen    Punktnummern mit Weg 0
     * @param reichweite Meter — weiter wird nicht gesucht
     */
    static wege(pos, dreiecke, quellen, reichweite) {
        const n = pos.length / 3;
        const { anfang, nachbar } = Hautwege.nachbarn(pos, dreiecke);
        const weg = new Float64Array(n).fill(Infinity);
        const halde = new Hautwege.Halde(n);
        for (const q of quellen) { weg[q] = 0; halde.setzen(q, 0); }
        const hoechstens = n + nachbar.length;
        let entnommen = 0;
        while (halde.groesse) {
            if (++entnommen > hoechstens) throw new Error('Hautwege: Endlosschleife');
            const [i, d] = halde.nehmen();
            if (d > weg[i]) continue;
            if (d > reichweite) break;
            const px = pos[3 * i], py = pos[3 * i + 1], pz = pos[3 * i + 2];
            for (let k = anfang[i]; k < anfang[i + 1]; k++) {
                const j = nachbar[k];
                const dj = d + Math.hypot(pos[3 * j] - px, pos[3 * j + 1] - py, pos[3 * j + 2] - pz);
                if (dj < weg[j]) { weg[j] = dj; halde.setzen(j, dj); }
            }
        }
        for (let i = 0; i < n; i++) if (weg[i] > reichweite) weg[i] = Infinity;
        return weg;
    }

    /** Nachbarn je Punkt als CSR (`anfang`, `nachbar`), Nähte verbunden. */
    static nachbarn(pos, dreiecke) {
        const n = pos.length / 3;
        const paare = [];
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            paare.push(a, b, b, c, c, a);
        }
        const erste = new Map();
        for (let i = 0; i < n; i++) {
            const s = `${pos[3 * i]},${pos[3 * i + 1]},${pos[3 * i + 2]}`;
            const j = erste.get(s);
            if (j === undefined) erste.set(s, i); else paare.push(i, j);
        }
        const grad = new Uint32Array(n + 1);
        for (let k = 0; k < paare.length; k += 2) { grad[paare[k] + 1]++; grad[paare[k + 1] + 1]++; }
        for (let i = 0; i < n; i++) grad[i + 1] += grad[i];
        const anfang = grad, nachbar = new Uint32Array(anfang[n]), stand = anfang.slice(0, n);
        for (let k = 0; k < paare.length; k += 2) {
            const a = paare[k], b = paare[k + 1];
            nachbar[stand[a]++] = b; nachbar[stand[b]++] = a;
        }
        return { anfang, nachbar };
    }

    /** Binäre Halde mit Schlüssel je Punkt — `setzen` senkt oder fügt ein. */
    static Halde = class {
        constructor(n) {
            this.knoten = new Uint32Array(n); this.wert = new Float64Array(n);
            this.platz = new Int32Array(n).fill(-1); this.groesse = 0;
        }
        setzen(i, d) {
            let p = this.platz[i];
            if (p < 0) { p = this.groesse++; this.knoten[p] = i; this.platz[i] = p; }
            this.wert[p] = d;
            this._hoch(p);
        }
        nehmen() {
            const i = this.knoten[0], d = this.wert[0];
            this.platz[i] = -1;
            this.groesse--;
            if (this.groesse > 0) {
                this.knoten[0] = this.knoten[this.groesse]; this.wert[0] = this.wert[this.groesse];
                this.platz[this.knoten[0]] = 0;
                this._runter(0);
            }
            return [i, d];
        }
        _tausch(a, b) {
            const k = this.knoten[a], w = this.wert[a];
            this.knoten[a] = this.knoten[b]; this.wert[a] = this.wert[b];
            this.knoten[b] = k; this.wert[b] = w;
            this.platz[this.knoten[a]] = a; this.platz[this.knoten[b]] = b;
        }
        _hoch(p) {
            while (p > 0) {
                const o = (p - 1) >> 1;
                if (this.wert[o] <= this.wert[p]) break;
                this._tausch(o, p); p = o;
            }
        }
        _runter(p) {
            for (;;) {
                const l = 2 * p + 1, r = l + 1;
                let m = p;
                if (l < this.groesse && this.wert[l] < this.wert[m]) m = l;
                if (r < this.groesse && this.wert[r] < this.wert[m]) m = r;
                if (m === p) break;
                this._tausch(m, p); p = m;
            }
        }
    };
}
