/**
 * Feldpaket — ein Objekt mit Zahlenfeldern (Typed Arrays) als EIN Byteblock und zurück, wahlweise mit gzip (19.10.2026, für `Hautmaskenvorrat`).
 *
 * Aufbau: `HBF1` · Länge des Kopfes (uint32, little endian) · Kopf (JSON) · die Felder, jedes auf 8 Bytes ausgerichtet. Der Kopf trägt das Gerüst des Objekts
 * (an der Stelle eines Feldes `{"$f": i}`) und je Feld Typ, Versatz und Länge. Beim Auspacken sind die Felder Ansichten auf DENSELBEN Puffer — keine Kopie.
 * Ohne Three.js und ohne DOM (Node-Test `test_js_hautmaskenvorrat.py`); `CompressionStream` gibt es in Chrome und in Node ab 18.
 */
export class Feldpaket {

    static MARKE = 'HBF1';
    static TYPEN = { Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array, Float32Array, Float64Array };

    /** Das Objekt als Bytes (die Felder werden kopiert — wer sie danach ändert, ändert das Paket nicht). */
    static packen(objekt) {
        const felder = [];
        const geruest = Feldpaket._geruest(objekt, felder);
        let versatz = 0;
        const liste = felder.map((f) => {
            const eintrag = { typ: Feldpaket._typ(f), versatz, laenge: f.length };
            versatz += Feldpaket._rund(f.byteLength);
            return eintrag;
        });
        const kopf = new TextEncoder().encode(JSON.stringify({ geruest, felder: liste }));
        const start = Feldpaket._rund(8 + kopf.length);
        const aus = new Uint8Array(start + versatz);
        for (let i = 0; i < 4; i++) aus[i] = Feldpaket.MARKE.charCodeAt(i);
        new DataView(aus.buffer).setUint32(4, kopf.length, true);
        aus.set(kopf, 8);
        felder.forEach((f, i) => aus.set(new Uint8Array(f.buffer, f.byteOffset, f.byteLength), start + liste[i].versatz));
        return aus;
    }

    /** Aus einem `ArrayBuffer` (Versatz 0, wie ihn `Response.arrayBuffer()` liefert) das Objekt; wirft bei fremden Bytes. */
    static entpacken(puffer) {
        const bytes = new Uint8Array(puffer);
        if (bytes.length < 8 || String.fromCharCode(...bytes.subarray(0, 4)) !== Feldpaket.MARKE) throw new Error('kein Feldpaket');
        const laenge = new DataView(puffer).getUint32(4, true);
        const { geruest, felder } = JSON.parse(new TextDecoder().decode(bytes.subarray(8, 8 + laenge)));
        const start = Feldpaket._rund(8 + laenge);
        const ansichten = felder.map((f) => {
            const Typ = Feldpaket.TYPEN[f.typ];
            if (!Typ || start + f.versatz + f.laenge * Typ.BYTES_PER_ELEMENT > puffer.byteLength) throw new Error(`Feld ${f.typ} passt nicht`);
            return new Typ(puffer, start + f.versatz, f.laenge);
        });
        return Feldpaket._fuellen(geruest, ansichten);
    }

    /** Gepackt und mit gzip, als Blob (zum Hochladen). */
    static async gzip(objekt) {
        const strom = new Blob([Feldpaket.packen(objekt)]).stream().pipeThrough(new CompressionStream('gzip'));
        return new Response(strom).blob();
    }

    /** Aus einem gzip-Strom (`Response.body`, `Blob.stream()`) das Objekt. */
    static async ungzip(strom) {
        return Feldpaket.entpacken(await new Response(strom.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
    }

    static _geruest(wert, felder) {
        if (ArrayBuffer.isView(wert) && Feldpaket._typ(wert)) {
            felder.push(wert);
            return { $f: felder.length - 1 };
        }
        if (Array.isArray(wert)) return wert.map((w) => Feldpaket._geruest(w, felder));
        if (wert && typeof wert === 'object') {
            const aus = {};
            for (const [k, w] of Object.entries(wert)) if (w !== undefined) aus[k] = Feldpaket._geruest(w, felder);
            return aus;
        }
        return wert;
    }

    static _fuellen(wert, ansichten) {
        if (Array.isArray(wert)) return wert.map((w) => Feldpaket._fuellen(w, ansichten));
        if (wert && typeof wert === 'object') {
            if (typeof wert.$f === 'number' && Object.keys(wert).length === 1) return ansichten[wert.$f];
            const aus = {};
            for (const [k, w] of Object.entries(wert)) aus[k] = Feldpaket._fuellen(w, ansichten);
            return aus;
        }
        return wert;
    }

    static _typ(feld) {
        for (const [name, Typ] of Object.entries(Feldpaket.TYPEN)) if (feld instanceof Typ) return name;
        return null;
    }

    static _rund(n) {
        return Math.ceil(n / 8) * 8;
    }
}
