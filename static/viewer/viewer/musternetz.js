import * as THREE from 'three';
import { base64ToFloat32 } from '../gemeinsam/kodierung.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';
import { fn } from '../gemeinsam/registrierung.js';
import { sliderVal } from './utils.js';
import { state } from './state.js';
import { removeClothRegion } from './cloth.js';
import { pePreviewKey } from './pattern_editor.js';

/**
 * Musternetz — aus der Serverantwort die Muster-Vorschau in der Szene.
 *
 * BEFUND `doppelcode` (29.08.2026): Diese sechzehn Zeilen standen wortgleich
 * in `peRegionGenerate` und `peGenerate3D` (`muster_erzeugen.js`). Die beiden
 * unterscheiden sich nur darin, WOHER die Daten kommen und was danach in der
 * Statuszeile steht.
 *
 * Die Fallunterscheidung am Ende ist der Grund, warum es EINE Stelle sein
 * muss: Ohne Hautdaten wird ein gewöhnliches Netz gebaut, mit ihnen ein
 * gebundenes. Wer das an einer der beiden Stellen anpasst, bekommt eine
 * Vorschau, die auf dem einen Weg der Figur folgt und auf dem anderen im Raum
 * stehen bleibt.
 */
export class Musternetz {
    /**
     * @param {Object} daten Serverantwort mit `vertices`, `faces` und
     *     wahlweise `skin_indices` / `skin_weights`
     * @returns {Object} das eingesetzte Netz
     */
    static einsetzen(daten) {
        removeClothRegion(pePreviewKey);
        const geo = Netzgeometrie.bauen(daten, THREE);
        const colorPicker = document.getElementById('pe-color');
        const matColor = colorPicker ? new THREE.Color(colorPicker.value)
                                     : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (sliderVal('pe-roughness') / 100);
        const metalness = (sliderVal('pe-metalness') / 100);
        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness, metalness, side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
        });
        let mesh;
        if (state.isSkinned && state.rigifySkeleton && daten.skin_indices && daten.skin_weights) {
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(
                base64ToFloat32(daten.skin_indices), 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(
                base64ToFloat32(daten.skin_weights), 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }
        state.clothMeshes[pePreviewKey] = mesh;
        state.clothParams[pePreviewKey] = {
            params: {}, color: '#' + mesh.material.color.getHexString(),
        };
        state.scene.add(mesh);
        fn.updateEquippedList();
        return mesh;
    }
}
