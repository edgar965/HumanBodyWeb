/**
 * Gelenkformeln — Daz' Formelgraph der Gelenkkorrekturen, je Bild gerechnet.
 *
 * Der Graph kommt vom Server (`Genesis9/gelenkkorrekturen.py`, GET
 * `felder/gelenke/`): `kanaele[schluessel] = {vorgabe, min, max, clamped,
 * formeln: [{stufe: 'sum'|'mult', ops: [{op, kanal?, val?}]}]}`, `morphe`
 * = die Kanäle mit Deltas. Eine Knocheneingabe heißt `l_thigh?rotation/x`
 * (Grad) und kommt aus `eingaben`; alles andere ist ein Kanal des Graphen:
 *
 *     wert(k) = clamp((vorgabe + Σ sum-Formeln) × Π mult-Formeln)
 *
 * Die Stapelmaschine ist die von `G9formeln.rechnen`: `push` (Zahl, Kanal
 * oder Spline-Knoten `[x, y, t, c, b]`), `mult`/`add`/`sub`/`div`/`neg`,
 * `spline_tcb` (linear zwischen den Knoten; die Knotenzahl liegt als letzte
 * Zahl auf dem Stapel, `x` als erste). 157 Kanäle, 117 Morphe — unter 0,1 ms
 * je Bild. Ohne Importe: `test_js_gelenkformeln` rechnet in Node.
 */
export class Gelenkformeln {

    /** `{morph: wert}` aller Morphe mit Wert ≠ 0. */
    static werte(graph, eingaben) {
        const rechner = new Gelenkrechner(graph.kanaele, eingaben);
        /** @type {Object<string, number>} */
        const aus = {};
        for (const name of graph.morphe || []) {
            const w = rechner.wert(name);
            if (Math.abs(w) > 1e-6) aus[name] = w;
        }
        return aus;
    }

    /** `{'l_thigh?rotation/x': Grad, …}` aus `{l_thigh: [x, y, z]}`. */
    static eingaben(winkel) {
        /** @type {Object<string, number>} */
        const aus = {};
        for (const [knochen, xyz] of Object.entries(winkel || {})) {
            aus[`${knochen}?rotation/x`] = xyz[0];
            aus[`${knochen}?rotation/y`] = xyz[1];
            aus[`${knochen}?rotation/z`] = xyz[2];
        }
        return aus;
    }
}

class Gelenkrechner {

    constructor(kanaele, eingaben) {
        this.kanaele = kanaele || {};
        this.eingaben = eingaben || {};
        this.werte = new Map();
        this.offen = new Set();
    }

    wert(kanal) {
        if (this.werte.has(kanal)) return this.werte.get(kanal);
        if (kanal.includes('?')) return this.eingaben[kanal] || 0;
        const angaben = this.kanaele[kanal];
        if (!angaben) return 0;
        if (this.offen.has(kanal)) return angaben.vorgabe || 0;
        this.offen.add(kanal);
        let summe = angaben.vorgabe || 0, faktor = 1;
        for (const f of angaben.formeln || []) {
            const ergebnis = this.rechnen(f.ops);
            if (f.stufe === 'mult') faktor *= ergebnis;
            else summe += ergebnis;
        }
        this.offen.delete(kanal);
        let wert = summe * faktor;
        if (angaben.clamped) wert = Math.min(angaben.max, Math.max(angaben.min, wert));
        this.werte.set(kanal, wert);
        return wert;
    }

    rechnen(ops) {
        /** @type {Array<number|number[]>} */
        let stapel = [];
        for (const o of ops || []) {
            const op = o.op;
            if (op === 'push') {
                if (o.kanal !== undefined) stapel.push(this.wert(o.kanal));
                else if (Array.isArray(o.val)) stapel.push(o.val);
                else stapel.push(Number(o.val) || 0);
            } else if (op === 'mult' || op === 'add' || op === 'sub' || op === 'div') {
                if (stapel.length < 2) return 0;
                const b = Number(stapel.pop()), a = Number(stapel.pop());
                if (op === 'mult') stapel.push(a * b);
                else if (op === 'add') stapel.push(a + b);
                else if (op === 'sub') stapel.push(a - b);
                else stapel.push(b ? a / b : 0);
            } else if (op === 'neg') {
                if (stapel.length) stapel.push(-Number(stapel.pop()));
            } else if (op === 'spline_linear' || op === 'spline_tcb' || op === 'spline_constant') {
                const aufStapel = stapel.filter(k => Array.isArray(k));
                const knoten = aufStapel.length ? aufStapel : (Array.isArray(o.val) ? o.val : []);
                const zahlen = stapel.filter(k => !Array.isArray(k));
                stapel = [Gelenkrechner.spline(knoten, zahlen.length ? Number(zahlen[0]) : 0)];
            }
        }
        const ergebnis = stapel.length ? stapel[stapel.length - 1] : 0;
        return typeof ergebnis === 'number' ? ergebnis : 0;
    }

    static spline(knoten, x) {
        const punkte = knoten.filter(k => k.length >= 2).map(k => [Number(k[0]), Number(k[1])])
            .sort((a, b) => a[0] - b[0]);
        if (!punkte.length) return 0;
        if (x <= punkte[0][0]) return punkte[0][1];
        for (let i = 0; i + 1 < punkte.length; i++) {
            const [x0, y0] = punkte[i], [x1, y1] = punkte[i + 1];
            if (x <= x1) return x1 === x0 ? y0 : y0 + (y1 - y0) * (x - x0) / (x1 - x0);
        }
        return punkte[punkte.length - 1][1];
    }
}
