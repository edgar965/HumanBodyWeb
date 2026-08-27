import { base64ToFloat32, base64ToUint32,
         blenderToThreeCoords } from './kodierung.js';

/**
 * Geometrie eines Kleidungs- oder Zubehörnetzes aus der Serverantwort.
 *
 * WARUM (Befund `doppelcode`, 27.08.2026): Diese sieben Zeilen standen an
 * SECHS Stellen wortgleich —
 *
 *     const vertBuf = base64ToFloat32(data.vertices);
 *     blenderToThreeCoords(vertBuf);
 *     const faceBuf = base64ToUint32(data.faces);
 *     const normalBuf = base64ToFloat32(data.normals);
 *     blenderToThreeCoords(normalBuf);
 *     const geo = new THREE.BufferGeometry();
 *     …setAttribute / setIndex / setAttribute
 *
 * Wer eine davon vergisst zu drehen (`blenderToThreeCoords`), bekommt ein
 * Kleidungsstück, das um 90° verdreht neben der Figur schwebt — und zwar nur
 * auf DER einen Seite. Genau das ist hier schon passiert.
 *
 * `Koerpernetz` daneben macht dasselbe für den KÖRPER; das ist ein anderer
 * Fall: UVs, Materialgruppen, Hautmaterial. Ein Kleidungsstück hat nichts
 * davon.
 */
export class Stoffgeometrie {
    /**
     * @param {Object} daten Antwort mit `vertices`, `faces`, `normals`
     *     (Base64, Blender-Achsen)
     * @param {Object} THREE die Three.js-Instanz der Seite
     * @returns {Object} BufferGeometry
     */
    static bauen(daten, THREE) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position',
                         new THREE.BufferAttribute(
                             Stoffgeometrie.punkte(daten.vertices), 3));
        if (daten.faces) {
            geo.setIndex(new THREE.BufferAttribute(
                base64ToUint32(daten.faces), 1));
        }
        Stoffgeometrie._normalen(geo, daten, THREE);
        return geo;
    }

    /**
     * Punktlagen, in Three.js-Achsen gedreht.
     * @param {string} b64
     * @returns {Float32Array}
     */
    static punkte(b64) {
        const puffer = base64ToFloat32(b64);
        blenderToThreeCoords(puffer);
        return puffer;
    }

    /** Normalen vom Server — fehlen sie, werden sie gerechnet. */
    static _normalen(geo, daten, THREE) {
        if (!daten.normals) {
            geo.computeVertexNormals();
            return;
        }
        geo.setAttribute('normal', new THREE.BufferAttribute(
            Stoffgeometrie.punkte(daten.normals), 3));
    }
}
