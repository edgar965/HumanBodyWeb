/**
 * Knochenformen — je Knochen ein Geometriestueck bauen.
 *
 * Aus modellnetz.js herausgeloest (Umbau 16.08.2026): `generateModelMesh` war
 * 375 Zeilen in vier Abschnitten — Knochenindex, Formen je Knochen,
 * Materialgruppen, Skelettaufbau. Die Formenschleife allein sind 180 davon.
 *
 * Die Formen-Weiche und das Einpassen zwischen Kopf und Spitze stehen seit
 * dem 29.08.2026 in `formstueck.js` — sie standen hier und in `rigformen.js`
 * zeichengleich doppelt (Befund `doppelcode`, 82 Zeilen).
 */

import * as THREE from 'three';
import { Formstueck } from './formstueck.js';
import { Knochengruppen } from './knochengruppen.js';

export class Knochenformen {
    /**
     * Geometriestuecke aller sichtbaren Knochen.
     * @returns {Array} [{geometry, boneIndex, color, texture}]
     */
    static sammeln(skelData, swData, config, boneIndexMap, childrenMap,
                   skelByName, worldTransforms) {
        const geoChunks = [];
        const segments = config.segments || 8;
        for (const [boneName, part] of Object.entries(config.bone_parts)) {
            if (!part.visible) continue;
            const boneIdx = boneIndexMap[boneName];
            if (boneIdx === undefined) continue;
        
            const wt = worldTransforms.get(boneName);
            if (!wt) continue;
        
            const data = skelByName[boneName];
            if (!data) continue;
        
            const radius = part.radius || config.default_radius || 0.03;
            const color = part.color || config.default_color || '#4488cc';
        
            // Compute bone HEAD→TAIL using the bone's own direction (local Y axis)
            // and determining length from the continuation child projected onto that direction.
            const headPos = wt.worldPos;
            const boneDir = new THREE.Vector3(0, 1, 0).applyQuaternion(wt.worldQuat);
        
            let boneLen = 0;
            const children = childrenMap[boneName];
            if (children && children.length > 0) {
                // Find length by projecting children onto bone direction — pick the best match
                for (const childName of children) {
                    const childWt = worldTransforms.get(childName);
                    if (!childWt) continue;
                    const offset = new THREE.Vector3().subVectors(childWt.worldPos, headPos);
                    const proj = offset.dot(boneDir);
                    if (proj > boneLen) boneLen = proj;
                }
            }
            if (boneLen < 0.001) boneLen = Knochengruppen.ENDLAENGEN[boneName] || 0.03;
        
            const tailPos = headPos.clone().add(boneDir.clone().multiplyScalar(boneLen));
        
            // Apply head/tail position offsets in WORLD space
            let effectiveHead = headPos.clone();
            let effectiveTail = tailPos.clone();
            if (part.headOffset) {
                effectiveHead.add(new THREE.Vector3(
                    part.headOffset.x || 0, part.headOffset.y || 0, part.headOffset.z || 0
                ));
            }
            if (part.tailOffset) {
                effectiveTail.add(new THREE.Vector3(
                    part.tailOffset.x || 0, part.tailOffset.y || 0, part.tailOffset.z || 0
                ));
            }
            // Apply axial scale (stretch/shrink along bone direction)
            if (part.axialScale && part.axialScale !== 1) {
                const mid = effectiveHead.clone().add(effectiveTail).multiplyScalar(0.5);
                const halfDir = effectiveTail.clone().sub(effectiveHead).multiplyScalar(0.5 * part.axialScale);
                effectiveHead = mid.clone().sub(halfDir);
                effectiveTail = mid.clone().add(halfDir);
            }
            const effectiveLen = effectiveHead.distanceTo(effectiveTail);
            if (effectiveLen > 0.001) boneLen = effectiveLen;
        
            const shapeGeo = Formstueck.geometrie(part, radius, boneLen, segments);
            Formstueck.einpassen(shapeGeo, effectiveHead, effectiveTail,
                                 boneDir, part);
        
            geoChunks.push({ geometry: shapeGeo, boneIndex: boneIdx, color, boneName, texture: part.texture || null });
        }
        
        if (geoChunks.length === 0) return null;
        
        return geoChunks;
    }
}
