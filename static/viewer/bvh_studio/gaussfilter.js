/**
 * Gaussfilter — Bewegungswerte glätten, EINE Fassung.
 *
 * Herausgelöst aus `werkzeug_glaettung.js` (250 Zeilen). Dort stand der Filter
 * ZWEIMAL: einmal als `_gaussFilter` und einmal ausgeschrieben in
 * `smoothSelectedClip` — Kernel-Bau, Faltung und Quaternionen-Normierung, je
 * vierzig Zeilen. Wer den Filter verbessert hätte, hätte eine Fassung übersehen.
 *
 * GEGLÄTTET WERDEN QUATERNIONEN, NICHT EULERWINKEL
 * ================================================
 * Eulerwinkel springen bei jedem Umlauf (359° -> 1°); eine Glättung darüber
 * erzeugt genau an dieser Stelle einen Ausschlag durch die halbe Drehung. Der
 * Preis dafür: Nach der Faltung ist ein Quaternion nicht mehr auf Länge 1 — und
 * ein nicht normiertes Quaternion verzerrt (skaliert) das Skelett. Deshalb wird
 * bei `stride === 4` immer nachnormiert.
 *
 * DIE RÄNDER WERDEN GEHALTEN, NICHT UMGEKLAPPT
 * ============================================
 * `Math.max(0, Math.min(n-1, …))` heißt: Am Anfang und Ende wird der erste bzw.
 * letzte Wert wiederholt. Ein Umklappen (Spiegeln) würde die Bewegung dort
 * zurücklaufen lassen, ein Nullwert würde die Figur in die Ruhelage ziehen.
 */
export class Gaussfilter {

    /** Kernradius als Vielfaches von Sigma — darüber ist das Gewicht ~0. */
    static RADIUSFAKTOR = 3;
    /** Kürzer als das gilt ein Quaternion als entartet und bleibt, wie es ist. */
    static MINDESTLAENGE = 1e-8;

    constructor(sigma) {
        this.sigma = sigma;
        this.radius = Math.ceil(sigma * Gaussfilter.RADIUSFAKTOR);
        this.kern = Gaussfilter.kern(sigma, this.radius);
    }

    /** Normierter Gauß-Kern der Länge `2·radius + 1`. */
    static kern(sigma, radius) {
        const werte = [];
        let summe = 0;
        for (let i = -radius; i <= radius; i++) {
            const wert = Math.exp(-0.5 * (i / sigma) ** 2);
            werte.push(wert);
            summe += wert;
        }
        return werte.map(wert => wert / summe);
    }

    /**
     * Eine Wertereihe glätten — IN PLACE.
     *
     * @param werte   Float32Array einer Keyframe-Spur
     * @param stride  Werte je Keyframe (4 = Quaternion, 3 = Position)
     */
    anwenden(werte, stride) {
        const anzahl = werte.length / stride;
        const alt = new Float32Array(werte);
        for (let spalte = 0; spalte < stride; spalte++) {
            for (let bild = 0; bild < anzahl; bild++) {
                werte[bild * stride + spalte] =
                    this._falten(alt, anzahl, stride, spalte, bild);
            }
        }
        if (stride === 4) Gaussfilter.normieren(werte);
        return werte;
    }

    _falten(alt, anzahl, stride, spalte, bild) {
        let summe = 0;
        for (let i = 0; i < this.kern.length; i++) {
            // Ränder halten (siehe Modul-Docstring).
            const stelle = Math.max(0, Math.min(anzahl - 1,
                                                bild + i - this.radius));
            summe += this.kern[i] * alt[stelle * stride + spalte];
        }
        return summe;
    }

    /** Alle Quaternionen einer Reihe auf Länge 1 bringen. */
    static normieren(werte) {
        for (let i = 0; i < werte.length; i += 4) {
            const laenge = Math.sqrt(werte[i] ** 2 + werte[i + 1] ** 2
                                     + werte[i + 2] ** 2 + werte[i + 3] ** 2);
            if (laenge <= Gaussfilter.MINDESTLAENGE) continue;
            for (let k = 0; k < 4; k++) werte[i + k] /= laenge;
        }
    }

    /** Kurzform für einen einzelnen Aufruf (der alte `_gaussFilter`). */
    static glaetten(werte, stride, sigma) {
        return new Gaussfilter(sigma).anwenden(werte, stride);
    }
}
