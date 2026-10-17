/**
 * Meshfighautstueck — das Kleidungsobjekt aus dem Netz als Stück für die Haut-Verdeckung (`Hautverdeckung`, 14.10.2026).
 *
 * WARUM NICHT DAS NETZ SELBST: Das Objekt hat je (Punkt, UV)-Paar einen Punkt (`Kleidungsobjekt.schreiben`), an jeder UV-Naht stehen die Punkte doppelt. Die Maske
 * (`Hautmaske._einStueck`) hält jede Kante, die in genau einem Dreieck liegt, für den Rand des Stoffs und lässt um jeden LOCKEREN Randpunkt (mehr als 4 mm über der Haut — die
 * Mindestluft der Anpassung ist 4 mm) zwei Ringe Haut stehen. Gemessen an der Ballerina (Chrome, 14.10.2026): von 29.366 Punkten galten 24.242 als Rand, die Maske verdeckte
 * 248 von 104.480 Körperpunkten; nach dem Verschweißen deckungsgleicher Punkte sind es 16.016 Punkte und 3.021 echte Randpunkte.
 *
 * Diese Hülle gibt der Maske die Form eines Stücks (`geometry.attributes.position`, `geometry.index`, `visible`, `userData`) mit verschweißten Punkten; Lage und Reihenfolge der
 * Dreiecke bleiben, nur die Nummern der Punkte werden zusammengelegt. `visible` fragt das Netz zur Zeit der Frage (es wird beim Binden an die Knochen durch ein `SkinnedMesh` ersetzt,
 * und das Kästchen „Kleider“ schaltet es).
 */
export class Meshfighautstueck {

    /** Punkte, die auf diesen Wert (Meter) gerundet gleich sind, gelten als derselbe — Nahtkopien sind bitgleich, 0,01 mm lässt Rundung zu. */
    static RASTER_M = 1e-5;

    /**
     * @param geometrie  die `BufferGeometry` des Netzes (Punkte in der Ruhelage, Index)
     * @param netz       Funktion → das Netz, das gerade in der Szene steht (oder null)
     */
    constructor(geometrie, netz, punkte = null) {
        this._netz = netz;
        // `punkte`: die Punkte des Netzes in der Ruhelage, wenn die rohen im Raum der Haltung liegen (`Meshfighaut.ruheposition`).
        const { punkte: verschweisst, dreiecke } = Meshfighautstueck.verschweissen(punkte || geometrie.getAttribute('position').array, geometrie.index.array);
        this.geometry = { attributes: { position: { array: verschweisst } }, index: { array: dreiecke }, userData: {} };
        this.userData = { art: 'kleidung' };
    }

    /** Wie das Netz: ausgeblendet verdeckt nichts (`Hautverdeckung.zaehlt`). */
    get visible() {
        return this._netz()?.visible !== false;
    }

    /**
     * Punkte mit gleicher Lage zusammenlegen; Dreiecke, die dabei zwei gleiche Ecken bekommen, fallen weg.
     * @returns {{punkte: Float32Array, dreiecke: Uint32Array}}
     */
    static verschweissen(punkte, index) {
        const n = punkte.length / 3;
        const raster = 1 / Meshfighautstueck.RASTER_M;
        const nummer = new Map();
        const neu = new Uint32Array(n);
        const behalten = [];
        for (let i = 0; i < n; i++) {
            const schluessel = `${Math.round(punkte[3 * i] * raster)},${Math.round(punkte[3 * i + 1] * raster)},${Math.round(punkte[3 * i + 2] * raster)}`;
            let w = nummer.get(schluessel);
            if (w === undefined) {
                w = behalten.length;
                nummer.set(schluessel, w);
                behalten.push(i);
            }
            neu[i] = w;
        }
        const ausgabe = new Float32Array(3 * behalten.length);
        behalten.forEach((alt, w) => ausgabe.set(punkte.subarray(3 * alt, 3 * alt + 3), 3 * w));
        const dreiecke = [];
        for (let k = 0; k + 2 < index.length; k += 3) {
            const a = neu[index[k]], b = neu[index[k + 1]], c = neu[index[k + 2]];
            if (a !== b && b !== c && a !== c) dreiecke.push(a, b, c);
        }
        return { punkte: ausgabe, dreiecke: Uint32Array.from(dreiecke) };
    }
}
