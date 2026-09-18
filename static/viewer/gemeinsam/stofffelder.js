/**
 * Stofffelder — die Gelenkkorrekturen (JCMs) auf dem Käfig eines dForce-Stücks.
 *
 * WOZU (18.09.2026 abends, „JCMs auf dem dForce-Simulationsnetz"): Beim
 * Abspielen zeigt ein dynamisches Stück sein Simulationsnetz, und das
 * kannte die Felder nicht — die Feder zog zur gehäuteten Lage OHNE
 * Korrektur, während die `SkinnedMesh` im Stand die Felder trug (ein
 * Sprung beim Anhalten). Der Server liefert dieselben Felder auch auf den
 * KÄFIGPUNKTEN (`garderobe/<kennung>/felder/gelenke/?kaefig=1`,
 * `G9stueckfelder` mit `stufen=None`); hier werden sie je Bild mit den
 * Werten des Graphen (`Genesis9gelenke.werte`) auf den Käfig summiert,
 * BEVOR der Worker häutet:
 *
 *     käfig'[p] = käfig[p] + Σ wert(kanal) · d(kanal, p)
 *
 * Ohne Three, prüfbar in Node (`test_js_stoffpendel`). Der Worker hält eine
 * Instanz je Stück (`Stoffarbeiter.felder`).
 */
export class Stofffelder {

    /**
     * @param kaefig  Float32Array (n·3) Daz' Käfigpunkte in Ruhe
     * @param felder  `{kanal: {n: Uint32Array, d: Float32Array (m·3)}}`
     */
    constructor(kaefig, felder = {}) {
        this.kaefig = kaefig;
        this.felder = felder;
        this.aus = new Float32Array(kaefig.length);
        /** Kanäle mit Feld, damit `anwenden` nichts Unnötiges durchläuft. */
        this.kanaele = new Set(Object.keys(felder));
    }

    /** Felder nachreichen (sie kommen asynchron vom Server). */
    setzen(felder) {
        this.felder = felder || {};
        this.kanaele = new Set(Object.keys(this.felder));
    }

    /** Trägt eines der gestellten `werte` ein Feld dieses Stücks? */
    wirkt(werte) {
        if (!werte) return false;
        for (const kanal of Object.keys(werte)) {
            if (werte[kanal] && this.kanaele.has(kanal)) return true;
        }
        return false;
    }

    /**
     * Der Käfig mit den Feldern — oder der Ruhekäfig selbst, wenn kein Wert
     * greift (keine Kopie, keine Rechnung).
     * @param werte  `{kanal: wert}` dieses Bildes
     * @returns {Float32Array} (n·3)
     */
    anwenden(werte) {
        if (!this.wirkt(werte)) return this.kaefig;
        const { aus, kaefig } = this;
        aus.set(kaefig);
        for (const [kanal, w] of Object.entries(werte)) {
            const f = w ? this.felder[kanal] : null;
            if (!f) continue;
            const { n, d } = f;
            for (let i = 0; i < n.length; i++) {
                const p = 3 * n[i], m = 3 * i;
                aus[p] += d[m] * w; aus[p + 1] += d[m + 1] * w; aus[p + 2] += d[m + 2] * w;
            }
        }
        return aus;
    }
}
