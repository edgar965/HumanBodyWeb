/**
 * Kleiderwerkstoff — das Material eines Kleidungsstücks auf der Haut.
 *
 * BEFUND `doppelcode` (31.08.2026): Dieselben sieben Angaben standen in
 * `scene/charakter_zubehoer.js` und `scene/prop_garments.js`. Aufgefallen
 * ist es erst, als die zweite Fassung aus einer 187-Zeichen-Zeile in
 * mehrere Zeilen gebrochen wurde — vorher sah der Vergleich zwei
 * verschiedene Blöcke.
 *
 * DIE DREI `polygonOffset`-ANGABEN sind der eigentliche Grund für diese
 * Datei. Kleidung liegt geometrisch fast auf der Haut; ohne den Versatz
 * flimmern beide Flächen gegeneinander (Z-Fighting), und zwar nur aus
 * bestimmten Kamerawinkeln. Wer ein drittes Kleidungsstück baut und die
 * Zeilen von Hand abschreibt, vergisst leicht eine davon — der Fehler
 * zeigt sich dann sporadisch und sieht aus wie ein Treiberproblem.
 */
export class Kleiderwerkstoff {

    /** Vorgabe, wenn das Kleidungsstück keine eigene Farbe mitbringt. */
    static GRUNDFARBE = [0.3, 0.35, 0.5];

    /**
     * Ein `MeshStandardMaterial` für ein Kleidungsstück.
     *
     * @param THREE    das Three.js-Modul der Seite
     * @param farbe    [r, g, b] in 0..1, oder null für die Grundfarbe
     * @param glanz    `roughness`; ohne Angabe 0.8
     * @param metall   `metalness`; ohne Angabe 0.0
     * @returns {*} das Material
     */
    static bauen(THREE, farbe, glanz, metall) {
        const rgb = farbe || Kleiderwerkstoff.GRUNDFARBE;
        return new THREE.MeshStandardMaterial({
            color: new THREE.Color(rgb[0], rgb[1], rgb[2]),
            roughness: glanz ?? 0.8,
            metalness: metall ?? 0.0,
            side: THREE.DoubleSide,
            // Gegen das Flimmern auf der Haut — siehe oben.
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnit: -1,
        });
    }
}
