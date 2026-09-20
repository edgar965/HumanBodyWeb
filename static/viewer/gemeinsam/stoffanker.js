/**
 * Stoffanker — jeder freie Punkt hängt an seinem nächsten gebundenen Punkt,
 * und weiter als der Stoffweg dorthin darf er nie (Long Range Attachment,
 * Kim, Chentanez, Müller 2012).
 *
 * WARUM (20.09.2026, Edgar: „bei der Jump animation verliert die Person das
 * Kleid!!"): Die Kantenbedingungen des Pendels laufen je Bild vier Durchgänge —
 * vier Kantenreihen folgen dem Bund, der Rest bleibt zurück, und die Kante
 * dazwischen dehnt sich (gemessen am Kunststreifen: auf das 1,89-Fache bei
 * einem Sprung von 0,6 m in 0,3 s). Ein Anker je Punkt ist ein einziger
 * Schritt ohne Schleife: Ist der Punkt weiter vom Anker als sein Stoffweg,
 * wird er auf die Kugel um den Anker gesetzt. Hängt der Stoff straff (der
 * Normalfall eines Rocks), zieht das den ganzen Rock im selben Bild mit.
 *
 * Der Stoffweg ist die kürzeste Kantenfolge in der RUHELAGE (Dijkstra über
 * die Kanten, einmal je Stück). Ohne gebundene Punkte gibt es keine Anker.
 */
export class Stoffanker {

    /**
     * Bis zu dieser Freiheit gilt ein Punkt als gebunden — er folgt der Haut mit
     * `dt·(1 − f)·FEDER_HAFT`, bei 0,5 also zur Hälfte je Bild, praktisch starr.
     * Gemessen am Dancing Queen Dress auf Ursula (20.09.2026): kein Punkt unter
     * 0,067, das Oberteil liegt bei 0,1–0,3 (2.595 Punkte ≤ 0,2, 5.376 ≤ 0,5,
     * 18.979 gesamt). Mit einer Grenze von 0,05 gab es KEINEN Anker, der Rock
     * fiel bis zur Entgleisung (49 cm, fünfmal zurückgesetzt in 3 s).
     */
    static GEBUNDEN = 0.5;

    /**
     * @param n        Punkte
     * @param kanten   `{a, b, l}` wie im Pendel
     * @param frei     Float32Array (n)
     * @returns {{anker: Int32Array, reichweite: Float32Array}|null} null ohne gebundene Punkte
     */
    static rechnen(n, kanten, frei) {
        const nachbarn = Stoffanker._nachbarn(n, kanten);
        const weg = new Float64Array(n).fill(Infinity);
        const anker = new Int32Array(n).fill(-1);
        const heap = new Stoffanker._Heap();
        for (let i = 0; i < n; i++) {
            if (frei[i] <= Stoffanker.GEBUNDEN) { weg[i] = 0; anker[i] = i; heap.push(i, 0); }
        }
        if (heap.leer()) return null;
        while (!heap.leer()) {
            const { index: i, wert: d } = heap.pop();
            if (d > weg[i]) continue;
            const { start, ziel, laenge } = nachbarn;
            for (let k = start[i]; k < start[i + 1]; k++) {
                const j = ziel[k], dj = d + laenge[k];
                if (dj < weg[j]) { weg[j] = dj; anker[j] = anker[i]; heap.push(j, dj); }
            }
        }
        const reichweite = new Float32Array(n);
        for (let i = 0; i < n; i++) reichweite[i] = Number.isFinite(weg[i]) ? weg[i] : -1;
        return { anker, reichweite };
    }

    /** Jeden Punkt, der weiter vom Anker ist als sein Stoffweg, auf die Kugel setzen. */
    static halten(x, frei, n, anker, reichweite) {
        for (let i = 0; i < n; i++) {
            const r = reichweite[i], a = anker[i];
            if (r <= 0 || a < 0 || a === i || frei[i] <= 0) continue;
            const o = 3 * i, p = 3 * a;
            const dx = x[o] - x[p], dy = x[o + 1] - x[p + 1], dz = x[o + 2] - x[p + 2];
            const d = Math.sqrt(dx * dx + dy * dy + dz * dz);   // kein Math.hypot: siehe `Stoffkanten`
            if (d <= r) continue;
            const s = r / d;
            x[o] = x[p] + dx * s; x[o + 1] = x[p + 1] + dy * s; x[o + 2] = x[p + 2] + dz * s;
        }
    }

    /**
     * Biegebedingungen ohne Flächen: je Punkt j und je zwei seiner Nachbarn i, k
     * (nicht selbst durch eine Kante verbunden) der Ruheabstand i–k. Faltet sich
     * das Netz an j, rücken i und k zusammen — die Bedingung schiebt sie sanft
     * auseinander (nur bei Stauchung; länger als in Ruhe können sie durch die
     * Kanten ohnehin nicht werden). Ersetzt die Biegesteifigkeit, die vorher die
     * starke Feder zur gehäuteten Lage gab — ohne die Lage zum Halteseil zu machen.
     * @returns {{a: Uint32Array, b: Uint32Array, l: Float32Array}}
     */
    static biegung(n, kanten, ruhe) {
        const { start, ziel } = Stoffanker._nachbarn(n, kanten);
        const kante = new Set();
        for (let e = 0; e < kanten.a.length; e++) {
            const i = kanten.a[e], j = kanten.b[e];
            kante.add(i < j ? i * n + j : j * n + i);
        }
        const a = [], b = [], l = [];
        for (let j = 0; j < n; j++) {
            for (let p = start[j]; p < start[j + 1]; p++) {
                for (let q = p + 1; q < start[j + 1]; q++) {
                    let i = ziel[p], k = ziel[q];
                    if (i === k) continue;
                    if (i > k) { const s = i; i = k; k = s; }
                    if (kante.has(i * n + k)) continue;
                    a.push(i); b.push(k);
                    l.push(Math.hypot(ruhe[3 * k] - ruhe[3 * i], ruhe[3 * k + 1] - ruhe[3 * i + 1],
                                      ruhe[3 * k + 2] - ruhe[3 * i + 2]));
                }
            }
        }
        return { a: Uint32Array.from(a), b: Uint32Array.from(b), l: Float32Array.from(l) };
    }

    /** Kantenliste als CSR: `start[i] .. start[i+1]` sind die Nachbarn von i. */
    static _nachbarn(n, kanten) {
        const { a, b, l } = kanten, m = a.length;
        const grad = new Int32Array(n + 1);
        for (let e = 0; e < m; e++) { grad[a[e] + 1]++; grad[b[e] + 1]++; }
        for (let i = 0; i < n; i++) grad[i + 1] += grad[i];
        const start = grad, fuell = Int32Array.from(start.subarray(0, n));
        const ziel = new Int32Array(2 * m), laenge = new Float32Array(2 * m);
        for (let e = 0; e < m; e++) {
            let k = fuell[a[e]]++; ziel[k] = b[e]; laenge[k] = l[e];
            k = fuell[b[e]]++; ziel[k] = a[e]; laenge[k] = l[e];
        }
        return { start, ziel, laenge };
    }

    /** Ein kleiner Binärhaufen (index, wert) — Dijkstra braucht nicht mehr. */
    static _Heap = class {
        constructor() { this.i = []; this.w = []; }
        leer() { return this.i.length === 0; }
        push(index, wert) {
            const i = this.i, w = this.w;
            i.push(index); w.push(wert);
            let k = w.length - 1;
            while (k > 0) {
                const e = (k - 1) >> 1;
                if (w[e] <= w[k]) break;
                [w[e], w[k]] = [w[k], w[e]]; [i[e], i[k]] = [i[k], i[e]]; k = e;
            }
        }
        pop() {
            const i = this.i, w = this.w;
            const aus = { index: i[0], wert: w[0] };
            const li = i.pop(), lw = w.pop();
            if (i.length) {
                i[0] = li; w[0] = lw;
                let k = 0;
                for (;;) {
                    const l = 2 * k + 1, r = l + 1;
                    let m = k;
                    if (l < w.length && w[l] < w[m]) m = l;
                    if (r < w.length && w[r] < w[m]) m = r;
                    if (m === k) break;
                    [w[m], w[k]] = [w[k], w[m]]; [i[m], i[k]] = [i[k], i[m]]; k = m;
                }
            }
            return aus;
        }
    };
}
