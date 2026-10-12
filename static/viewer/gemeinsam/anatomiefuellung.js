/**
 * Anatomiefuellung — die Lücken gerechneter Karten füllen (11.10.2026, für `Anatomierechnung`; die Textur daraus macht `Anatomietextur`).
 *
 * Reine Zahlen, ohne DOM — läuft im Worker (`anatomiearbeiter.js`).
 *
 * Eine Karte, die nur an den Texeln der Inseln des Stücks gerechnet ist, hat dazwischen Leere. Bilinear gelesen und in den kleinen Stufen der
 * Mip-Kette blutet sie in die Ränder (dunkle Säume an den Inseln). Darum: die belegten Texel greifen `schritte` Texel weit in die Leere
 * (Mittel der belegten Nachbarn), der Rest bekommt den Mittelwert der belegten Texel — so bleibt auch die kleinste Stufe im Ton der Haut.
 * Alle Karten eines Stücks laufen in EINEM Durchgang (dieselben Nachbarn, dieselbe Maske); erste Fassung mit je einer Liste und je Karte einem
 * Durchgang: 4,5 s + 2,5 s für drei Karten auf 1.024² (Chrome im Hintergrund-Tab).
 */
export class Anatomiefuellung {

    /**
     * Die Karten auffüllen. `karten`: `[{rgba, vorgabe}]` — `rgba` hat die Länge `breite · hoehe · 4`, `vorgabe` ist das RGBA für den Rest
     * (null: Mittel der belegten Texel dieser Karte). `belegt` (je Texel 0/1) bleibt unverändert.
     * @returns die Zahl der belegten Texel
     */
    static fuellen(belegt, breite, hoehe, karten, schritte = 6) {
        const stand = Uint8Array.from(belegt), nk = karten.length, summe = new Float64Array(3 * nk);
        let n = 0, x0 = breite, x1 = -1, y0 = hoehe, y1 = -1;
        for (let j = 0; j < hoehe; j++) for (let i = 0; i < breite; i++) {
            const nr = j * breite + i;
            if (!stand[nr]) continue;
            n++;
            for (let k = 0; k < nk; k++) for (let c = 0; c < 3; c++) summe[3 * k + c] += karten[k].rgba[4 * nr + c];
            x0 = Math.min(x0, i); x1 = Math.max(x1, i); y0 = Math.min(y0, j); y1 = Math.max(y1, j);
        }
        const rest = karten.map((karte, k) => karte.vorgabe || (n ? [summe[3 * k] / n, summe[3 * k + 1] / n, summe[3 * k + 2] / n, 255] : [128, 128, 128, 255]));
        const mix = new Float64Array(3 * nk);
        for (let s = 0; s < schritte && n; s++) {
            const j0 = Math.max(0, y0 - s - 1), j1 = Math.min(hoehe - 1, y1 + s + 1), i0 = Math.max(0, x0 - s - 1), i1 = Math.min(breite - 1, x1 + s + 1);
            for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
                const nr = j * breite + i;
                if (stand[nr]) continue;
                let z = 0;
                mix.fill(0);
                for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
                    const jj = j + dj, ii = i + di;
                    if (jj < 0 || jj >= hoehe || ii < 0 || ii >= breite) continue;
                    const m = jj * breite + ii;
                    if (stand[m] !== 1) continue;
                    z++;
                    for (let k = 0; k < nk; k++) for (let c = 0; c < 3; c++) mix[3 * k + c] += karten[k].rgba[4 * m + c];
                }
                if (!z) continue;
                for (let k = 0; k < nk; k++) for (let c = 0; c < 3; c++) karten[k].rgba[4 * nr + c] = mix[3 * k + c] / z;
                for (let k = 0; k < nk; k++) karten[k].rgba[4 * nr + 3] = 255;
                stand[nr] = 2;                                    // erst im nächsten Schritt Quelle
            }
            for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) if (stand[j * breite + i] === 2) stand[j * breite + i] = 1;
        }
        for (let nr = 0; nr < stand.length; nr++) {
            if (stand[nr]) continue;
            for (let k = 0; k < nk; k++) for (let c = 0; c < 4; c++) karten[k].rgba[4 * nr + c] = rest[k][c] ?? 255;
        }
        return n;
    }
}
