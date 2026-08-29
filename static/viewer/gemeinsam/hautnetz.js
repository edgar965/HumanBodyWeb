import * as THREE from 'three';
import { base64ToFloat32 } from './kodierung.js';

/**
 * Hautnetz — ein Netz, das der Figur folgt, oder eines, das steht.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Diese elf Zeilen standen dreimal —
 * `viewer/cloth.js`, `viewer/garment.js` und (seit gestern) `viewer/
 * musternetz.js`. Immer dieselbe Fallunterscheidung:
 *
 *     Kommen Hautdaten mit?  ->  SkinnedMesh, an das Skelett gebunden
 *     Kommen keine?          ->  gewöhnliches Mesh
 *
 * DAS IST DIE STELLE, an der ein Kleidungsstück im Raum stehen bleibt, während
 * die Figur davonläuft. Der Fehler sieht nicht nach einem Fehler aus: Das Netz
 * ist da, die Farbe stimmt, die Konsole schweigt — es bewegt sich nur nicht
 * mit. Wer die Bedingung an einer von drei Stellen nachzieht, bekommt genau
 * das, und zwar nur auf einem der drei Wege.
 *
 * `bindMatrix` kommt vom KÖRPER, nicht vom Kleidungsstück: Die Kleidung wurde
 * gegen die Ruhelage des Körpers gerechnet, also muss sie dieselbe
 * Bindematrix benutzen. Mit einer eigenen säße sie doppelt verformt da.
 */
export class Hautnetz {
    /**
     * @param {Object} geometrie BufferGeometry des Netzes
     * @param {Object} material Material (eines oder mehrere)
     * @param {Object} state Seitenzustand — gelesen werden `isSkinned`,
     *     `rigifySkeleton.skeleton` und `bodyMesh.bindMatrix`
     * @param {Object} daten Serverantwort mit `skin_indices`/`skin_weights`
     *     (Base64) — fehlen sie, entsteht ein gewöhnliches Mesh
     * @returns {Object} SkinnedMesh oder Mesh
     */
    static bauen(geometrie, material, state, daten) {
        if (!(state.isSkinned && state.rigifySkeleton
              && daten.skin_indices && daten.skin_weights)) {
            return new THREE.Mesh(geometrie, material);
        }
        geometrie.setAttribute('skinIndex', new THREE.Float32BufferAttribute(
            base64ToFloat32(daten.skin_indices), 4));
        geometrie.setAttribute('skinWeight', new THREE.Float32BufferAttribute(
            base64ToFloat32(daten.skin_weights), 4));
        const netz = new THREE.SkinnedMesh(geometrie, material);
        netz.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        return netz;
    }
}
