/**
 * Anatomiehash — woran man erkennt, dass sich die GEOMETRIE nicht geändert hat (12.10.2026, für `Anatomiebacken.zuordnung`).
 *
 * Edgar: „das Backen der neuen Haut soll nur ein paar Sekunden dauern." Gemessen im Chrome (Hintergrund-Tab, Skin 03, 8,2 s je Rechnung): 5,6 s davon die
 * `Anatomiezuordnung` (zu jedem Texel des Stücks die Stelle der Haut), 1,8 s die Karten daraus, 0,6 s das Füllen, 0,2 s die Auswahl der Hautdreiecke. Die Zuordnung hängt
 * aber nur an der LAGE — Punkte, UV, Index und Normalen des Stücks, Punkte und Dreiecke der Haut —, nicht an ihrer Textur. Bei jedem Hautwechsel kommt derselbe Körper neu
 * vom Server (andere Objekte, gleiche Zahlen), also taugt keine Objektgleichheit als Schlüssel; hier wird der Inhalt gezählt.
 *
 * FNV-1a über die Bits der Felder, zweimal mit anderem Startwert (zwei 32 Bit: ein Zufallstreffer bei gleicher Länge ist so gut wie ausgeschlossen). Rund 700.000 Wörter,
 * wenige Millisekunden. Ohne Three.js und ohne DOM (Node-Test `test_js_anatomiehash.py`).
 */
export class Anatomiehash {

    static SEED_A = 2166136261;
    static SEED_B = 5381;

    /**
     * Ein Feld als 32-Bit-Wörter: Float32/Int32/Uint32 ohne Kopie (auch Ausschnitte eines Puffers); Float64 über Float32; 8-/16-Bit-Ganzzahlen (ein kurzer Index)
     * als Ganzzahl kopiert; null/leer → leer.
     */
    static woerter(feld) {
        if (!feld?.length) return new Uint32Array(0);
        if (feld.BYTES_PER_ELEMENT === 4) return new Uint32Array(feld.buffer, feld.byteOffset, feld.length);
        if (feld instanceof Float64Array) return new Uint32Array(Float32Array.from(feld).buffer);
        return Uint32Array.from(feld);
    }

    /** FNV-1a über ein Feld, fortgesetzt von `h`. */
    static feld(h, feld) {
        const w = Anatomiehash.woerter(feld);
        for (let i = 0; i < w.length; i++) h = Math.imul(h ^ w[i], 16777619) >>> 0;
        return Math.imul(h ^ w.length, 16777619) >>> 0;            // die Länge zählt mit: [a][b, c] ≠ [a, b][c]
    }

    /**
     * Der Schlüssel der Geometrie für die Zuordnung.
     * @param stueck  `{pos, uv, index, normal}`
     * @param haut    `{pos, ecken}`
     * @returns Text `breite×hoehe|A|B`
     */
    static schluessel(stueck, haut, breite, hoehe) {
        const felder = [stueck.pos, stueck.uv, stueck.index, stueck.normal, haut.pos, haut.ecken];
        const a = felder.reduce((h, f) => Anatomiehash.feld(h, f), Anatomiehash.SEED_A);
        const b = felder.reduce((h, f) => Anatomiehash.feld(h, f), Anatomiehash.SEED_B);
        return `${breite}×${hoehe}|${a.toString(36)}|${b.toString(36)}`;
    }
}
