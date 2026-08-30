/**
 * Hautgewichte — die vier stärksten Knocheneinflüsse je Punkt, normiert.
 *
 * WARUM DAS EINMAL DASTEHT (17.08.2026, Befund `doppelcode`)
 * =========================================================
 * Dieselbe Schleife stand VIERMAL: `animation/netz.js`, `character_core.js`,
 * `scene/skeleton.js`, `viewer/skinning.js`. Sie ist der Übergang von unserer
 * Datenform (`weights[v] = [[knochen, gewicht], …]`, beliebig viele Einträge)
 * auf die von Three.js (`skinIndex`/`skinWeight` als Vierervektor).
 *
 * Drei Regeln stecken darin, und alle drei sind leicht falsch zu kopieren:
 *
 *   1. **Die vier STÄRKSTEN**, nicht die ersten vier. Ohne das Sortieren
 *      bekommt ein Punkt den Einfluss, der zufällig zuerst gespeichert wurde.
 *   2. **Normieren auf Summe 1** — nach dem Abschneiden auf vier fehlt sonst
 *      Gewicht, und der Punkt bleibt beim Verformen hinter dem Knochen zurück.
 *   3. **Summe 0 abfangen.** Ein Punkt ohne jeden Einfluss (Wimpern, innere
 *      Flächen) würde sonst durch Null geteilt: `NaN` in der Geometrie, und
 *      Three.js zeichnet die ganze Figur nicht mehr.
 *
 * Die Reihenfolge der Gewichte ist in diesem Projekt heikel — siehe die Lehre
 * „Skin Weights + CC Subdivision" im Projektgedächtnis: Das unterteilte Netz hat
 * eine ANDERE Punktreihenfolge als das Grundnetz. Diese Klasse rechnet
 * ausschließlich innerhalb einer gegebenen Reihenfolge; sie ordnet nichts um.
 */

export class Hautgewichte {

    /** So viele Knochen kann Three.js je Punkt mischen. */
    static VIER = 4;

    /** Unter dieser Summe gilt ein Punkt als ohne Einfluss. */
    static MINDESTSUMME = 1e-6;

    /**
     * @param {{weights: Array<Array<[number, number]>>}} daten Rohgewichte vom Server
     * @param {number} punkte Anzahl der Punkte der Zielgeometrie
     * @returns {{indices: Float32Array, gewichte: Float32Array}}
     */
    static vierervektoren(daten, punkte) {
        const indices = new Float32Array(punkte * Hautgewichte.VIER);
        const gewichte = new Float32Array(punkte * Hautgewichte.VIER);
        const alle = daten?.weights || [];
        for (let v = 0; v < punkte; v++) {
            const stärkste = Hautgewichte.staerkste(alle[v] || []);
            let summe = stärkste.reduce((s, e) => s + e[1], 0);
            if (summe < Hautgewichte.MINDESTSUMME) summe = 1;
            for (let i = 0; i < Hautgewichte.VIER; i++) {
                const stelle = v * Hautgewichte.VIER + i;
                indices[stelle] = i < stärkste.length ? stärkste[i][0] : 0;
                gewichte[stelle] = i < stärkste.length ? stärkste[i][1] / summe : 0;
            }
        }
        return { indices, gewichte };
    }

    /** Die vier größten Einflüsse eines Punktes, absteigend. */
    static staerkste(einfluesse) {
        return einfluesse.slice()
            .sort((a, b) => b[1] - a[1])
            .slice(0, Hautgewichte.VIER);
    }

    /**
     * Setzt `skinIndex` und `skinWeight` an einer Three.js-Geometrie.
     *
     * @param {THREE.BufferGeometry} geometrie muss `position` haben
     * @param {object} daten Rohgewichte vom Server
     * @param {typeof THREE.BufferAttribute} Attribut Three.js-Klasse (die Seiten
     *        bringen ihre eigene Three-Instanz mit; ein Import hier würde eine
     *        ZWEITE Fassung laden — siehe `_importmap.html`)
     */
    /**
     * Die beiden Felder ans Netz haengen.
     *
     * BEFUND `doppelcode` (30.08.2026): Diese sechs Zeilen standen in beiden
     * oeffentlichen Methoden. Beide Felder MUESSEN zusammen gesetzt werden und
     * beide mit derselben Breite — ein Netz mit `skinIndex`, aber ohne
     * `skinWeight` faellt in Three.js im Ursprung zusammen, ohne Meldung.
     */
    static _anhaengen(geometrie, indices, gewichte, Attribut) {
        geometrie.setAttribute('skinIndex',
            new Attribut(indices, Hautgewichte.VIER));
        geometrie.setAttribute('skinWeight',
            new Attribut(gewichte, Hautgewichte.VIER));
        return geometrie;
    }

    static anGeometrie(geometrie, daten, Attribut) {
        const punkte = geometrie.attributes.position.count;
        const { indices, gewichte } = Hautgewichte.vierervektoren(daten, punkte);
        return Hautgewichte._anhaengen(geometrie, indices, gewichte, Attribut);
    }

    /**
     * Alles an EINEN Knochen binden — für Haare und Zubehör.
     *
     * Haare, Brillen, Hüte hängen komplett am Kopf: Jeder Punkt bekommt den
     * einen Knochen mit Gewicht 1, die anderen drei Plätze bleiben 0. Auch das
     * stand dreimal im Projekt (`character_core.js`, `scene/skeleton.js`,
     * `viewer/hair.js`) — mit der stillen Falle, dass ein FEHLENDES Gewicht
     * (alle vier 0) das Teil im Ursprung zusammenfallen lässt.
     *
     * @param {THREE.BufferGeometry} geometrie
     * @param {number} knochen Index im Skelett
     * @param {typeof THREE.BufferAttribute} Attribut
     */
    static anEinenKnochen(geometrie, knochen, Attribut) {
        const punkte = geometrie.attributes.position.count;
        const indices = new Float32Array(punkte * Hautgewichte.VIER);
        const gewichte = new Float32Array(punkte * Hautgewichte.VIER);
        for (let v = 0; v < punkte; v++) {
            indices[v * Hautgewichte.VIER] = knochen;
            gewichte[v * Hautgewichte.VIER] = 1.0;
        }
        return Hautgewichte._anhaengen(geometrie, indices, gewichte, Attribut);
    }
}
