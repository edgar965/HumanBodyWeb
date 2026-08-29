/**
 * Rigformen — je Rig-Knochen ein Geometriestueck bauen.
 *
 * Aus rignetz.js herausgeloest (Umbau 16.08.2026): `generateRigBoneMesh` war
 * 318 Zeilen. Die Formenschleife ist mit 155 Zeilen der groesste Teil und die
 * Zwillingsschwester von Knochenformen — dort fuer das DEF-Skelett, hier fuer
 * das Rigify-Rig mit seinen vier Knochenebenen.
 *
 * Die Formen-Weiche und das Einpassen zwischen Kopf und Spitze stehen seit
 * dem 29.08.2026 in `formstueck.js` — sie standen hier und in `knochenformen.js`
 * zeichengleich doppelt (Befund `doppelcode`, 82 Zeilen).
 */

import * as THREE from 'three';
import { Formstueck } from './formstueck.js';
import { computeRigBoneWorldTransforms } from './knochenmatrizen.js';

//: Greift nur, wenn Kopf und Spitze eines Rig-Knochens zusammenfallen.
//: Beim DEF-Skelett ist das die Knochenrichtung, hier schlicht die Y-Achse.
const ERSATZRICHTUNG = new THREE.Vector3(0, 1, 0);

export class Rigformen {
    /** @returns {Array} [{geometry, boneIndex, color, texture}] */
    static sammeln(rigData, config, boneIndexMap, worldTransforms, swData,
                   canSkin) {
        const geoChunks = [];
        const segments = config.segments || 8;
        for (const [boneName, part] of Object.entries(config.bone_parts)) {
            if (!part.visible) continue;
            const wt = worldTransforms.get(boneName);
            if (!wt) continue;
        
            const radius = part.radius || config.default_radius || 0.03;
            const color = part.color || config.default_color || '#4488cc';
            let boneLen = wt.length;
            if (boneLen < 0.001) boneLen = 0.02;
        
            // Apply head/tail offsets in bone-local space
            let effectiveHead = wt.worldPos.clone();
            let effectiveTail = wt.tailPos.clone();
            if (part.headOffset || part.tailOffset) {
                // Derive bone orientation quaternion from head→tail direction
                const rawDir = new THREE.Vector3().subVectors(wt.tailPos, wt.worldPos);
                if (rawDir.length() > 0.0001) rawDir.normalize(); else rawDir.set(0, 1, 0);
                const boneQuat = new THREE.Quaternion();
                const yUp = new THREE.Vector3(0, 1, 0);
                if (Math.abs(rawDir.dot(yUp)) < 0.9999) boneQuat.setFromUnitVectors(yUp, rawDir);
                else if (rawDir.y < 0) boneQuat.setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI);
                if (part.headOffset) {
                    effectiveHead.add(new THREE.Vector3(
                        part.headOffset.x || 0, part.headOffset.y || 0, part.headOffset.z || 0
                    ).applyQuaternion(boneQuat));
                }
                if (part.tailOffset) {
                    effectiveTail.add(new THREE.Vector3(
                        part.tailOffset.x || 0, part.tailOffset.y || 0, part.tailOffset.z || 0
                    ).applyQuaternion(boneQuat));
                }
                const effLen = effectiveHead.distanceTo(effectiveTail);
                if (effLen > 0.001) boneLen = effLen;
            }
        
            const shapeGeo = Formstueck.geometrie(part, radius, boneLen, segments);
            Formstueck.einpassen(shapeGeo, effectiveHead, effectiveTail,
                                 ERSATZRICHTUNG, part);
        
            // Determine skin bone index: DEF bones map to their skeleton index, others to root (0)
            const boneIdx = canSkin ? (boneIndexMap[boneName] !== undefined ? boneIndexMap[boneName] : 0) : 0;
            geoChunks.push({ geometry: shapeGeo, color, boneIndex: boneIdx, boneName, texture: part.texture || null });
        }
        
        if (geoChunks.length === 0) return null;
        
        return geoChunks;
    }
}
