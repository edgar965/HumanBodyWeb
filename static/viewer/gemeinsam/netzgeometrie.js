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
 * WARUM SIE JETZT `Netzgeometrie` HEISST (28.08.2026): Sie hiess vorher nach
 * dem Stoff, weil sie aus den Kleidungs-Stellen herausgeloest wurde. Am selben
 * Tag bekam `Koerpernetz` eine Geometrie ohne Materialgruppen — und damit
 * standen ZWEI Bauer nebeneinander, die sich nur noch darin unterschieden, ob
 * sie UVs setzen. Das ist kein Unterschied, sondern ein fehlendes Feld: Ein
 * Kleidungsstueck bringt keine `uvs` mit, und dann passiert nichts.
 *
 * `Koerpernetz` baut darauf auf und legt Materialgruppen und Hautmaterial
 * dazu — das ist der Teil, der wirklich nur den Koerper betrifft.
 */
export class Netzgeometrie {
    /**
     * @param {Object} daten Antwort mit `vertices`, `faces`, `uvs`, `normals`
     *     (Base64, Blender-Achsen) — alles ausser `vertices` ist freiwillig
     * @param {Object} THREE die Three.js-Instanz der Seite
     * @param nachPunkten Eingriff am Punktpuffer, NACH der Drehung und VOR
     *     dem Attribut. Die Foto-Seite richtet die Punkte dort auf SMPL-X aus.
     * @returns {Object} BufferGeometry
     */
    static bauen(daten, THREE, nachPunkten = null) {
        const geo = new THREE.BufferGeometry();
        const punkte = Netzgeometrie.punkte(daten.vertices);
        if (nachPunkten) nachPunkten(punkte);
        geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        if (daten.faces) {
            geo.setIndex(new THREE.BufferAttribute(
                base64ToUint32(daten.faces), 1));
        }
        if (daten.uvs) {
            geo.setAttribute('uv', new THREE.BufferAttribute(
                base64ToFloat32(daten.uvs), 2));
        }
        Netzgeometrie._normalen(geo, daten, THREE);
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
            Netzgeometrie.punkte(daten.normals), 3));
    }
}
