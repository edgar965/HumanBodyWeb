/**
 * Netzpaket — die Binärantwort des Servers lesen (`core/daten/netzpaket.py`).
 *
 * DAS FORMAT
 *
 *     0 ..  3   'HBM1'                     Magie
 *     4 ..  7   uint32 LE                  Länge des JSON-Kopfes in Bytes
 *     8 ..      JSON-Kopf (UTF-8)          die Antwort, Felder durch Marken ersetzt
 *               Polsterung auf die nächste 8-Byte-Grenze
 *     dann      die Felder, jedes auf 8 Byte ausgerichtet
 *
 * Jede Marke `{"__netzfeld__": {typ, pos, bytes, anzahl}}` wird zu einem TypedArray
 * AUF DEM VORHANDENEN PUFFER — `new Float32Array(puffer, versatz, n)` kopiert nichts.
 *
 * Die Fassade `kodierung.js` gibt davon anschließend eine eigene Kopie heraus, weil
 * mehrere Aufrufer die Punkte in place drehen; die Begründung steht dort. Wer ein Feld
 * NUR liest (Messungen, Vergleiche), kann die Sicht hier direkt nehmen.
 *
 * WAS VORHER GESCHAH: Die Felder kamen als base64 in JSON. Das ist ein Drittel mehr
 * Bytes über die Leitung, dazu auf dem Server das Kodieren und hier das Dekodieren —
 * bei 42 MB gemessen 83 ms allein für `Uint8Array.fromBase64` (mit der alten
 * `atob`-Schleife 955 ms, 18.09.2026). Hier fällt beides weg.
 *
 * WARUM DIE MAGIE GEPRÜFT WIRD: Ohne sie liest ein Fehlerfall (HTML-Fehlerseite,
 * abgeschnittene Antwort) sich als Float32 und ergibt ein Netz aus Rauschen. Den
 * Fehler sucht dann niemand in der Antwort, sondern in der Geometrie.
 */

/** Typname des Servers -> Konstruktor. Muss zu `Netzfeld.ERLAUBT` passen. */
const TYPEN = {
    float32: Float32Array,
    uint32: Uint32Array,
    uint16: Uint16Array,
    uint8: Uint8Array,
    int32: Int32Array,
};

export class Netzpaket {
    /** Der Inhaltstyp, den der Server für ein Paket setzt. */
    static TYP = 'application/x-humanbody-netz';
    static MARKE = '__netzfeld__';
    static MAGIE = 0x314d4248;   // 'HBM1' als uint32 LE gelesen

    /**
     * Ist das ein Binärpaket? Prüft den Inhaltstyp der Antwort.
     * @param {Response} antwort
     */
    static erkannt(antwort) {
        return (antwort.headers.get('Content-Type') || '').includes(Netzpaket.TYP);
    }

    /**
     * `ArrayBuffer` -> das Antwort-Objekt, Felder als TypedArrays.
     * @param {ArrayBuffer} puffer
     */
    static lesen(puffer) {
        const sicht = new DataView(puffer);
        if (puffer.byteLength < 8 || sicht.getUint32(0, true) !== Netzpaket.MAGIE) {
            throw new Error('Netzpaket: keine HBM1-Magie — die Antwort ist kein Netzpaket');
        }
        const kopflaenge = sicht.getUint32(4, true);
        const kopf = JSON.parse(
            new TextDecoder('utf-8').decode(new Uint8Array(puffer, 8, kopflaenge)));
        let beginn = 8 + kopflaenge;
        beginn += (8 - (beginn % 8)) % 8;
        return Netzpaket._einsetzen(kopf, puffer, beginn);
    }

    /** Rekursiv jede Marke durch ihr TypedArray ersetzen. */
    static _einsetzen(wert, puffer, beginn) {
        if (Array.isArray(wert)) {
            return wert.map(w => Netzpaket._einsetzen(w, puffer, beginn));
        }
        if (wert && typeof wert === 'object') {
            const marke = wert[Netzpaket.MARKE];
            if (marke && Object.keys(wert).length === 1) {
                return Netzpaket._feld(marke, puffer, beginn);
            }
            const aus = {};
            for (const [k, v] of Object.entries(wert)) {
                aus[k] = Netzpaket._einsetzen(v, puffer, beginn);
            }
            return aus;
        }
        return wert;
    }

    /** Ein Feld als Sicht auf den Puffer — ohne Kopie. */
    static _feld(marke, puffer, beginn) {
        const Bauart = TYPEN[marke.typ];
        if (!Bauart) throw new Error(`Netzpaket: unbekannter Typ ${marke.typ}`);
        const versatz = beginn + marke.pos;
        if (versatz + marke.bytes > puffer.byteLength) {
            throw new Error(`Netzpaket: Feld ${marke.typ} liegt hinter dem Ende `
                + `(${versatz} + ${marke.bytes} > ${puffer.byteLength})`);
        }
        return new Bauart(puffer, versatz, marke.anzahl);
    }
}
