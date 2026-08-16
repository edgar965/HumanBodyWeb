/**
 * Rigformen — je Rig-Knochen ein Geometriestueck bauen.
 *
 * Aus rignetz.js herausgeloest (Umbau 16.08.2026): `generateRigBoneMesh` war
 * 318 Zeilen. Die Formenschleife ist mit 155 Zeilen der groesste Teil und die
 * Zwillingsschwester von Knochenformen — dort fuer das DEF-Skelett, hier fuer
 * das Rigify-Rig mit seinen vier Knochenebenen.
 */

import * as THREE from 'three';
import { _mergeSimpleGeos, _buildPlane, _buildRhombus, _getOrLoadTexture, _makeDoubleSided } from './formenbauer.js';
import { _buildSpiralTutu, _buildSkirt, _buildHelixRibbon } from './formen_band.js';
import { computeRigBoneWorldTransforms } from './knochenmatrizen.js';

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
        
            // Create shape geometry
            let shapeGeo;
            switch (part.shape) {
                case 'box':
                    shapeGeo = new THREE.BoxGeometry(radius * 2, boneLen, radius * 2, 1, 1, 1);
                    break;
                case 'sphere_low':
                    shapeGeo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                    break;
                case 'sphere':
                    shapeGeo = new THREE.SphereGeometry(radius, 24, 16);
                    break;
                case 'cone':
                    shapeGeo = new THREE.ConeGeometry(radius, boneLen, segments);
                    break;
                case 'capsule':
                    shapeGeo = new THREE.CapsuleGeometry(radius, Math.max(0.001, boneLen - radius * 2), segments, Math.max(4, segments >> 1));
                    break;
                case 'oval':
                    shapeGeo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                    shapeGeo.scale(1, boneLen / (radius * 2), 1);
                    break;
                case 'double_oval': {
                    const ov = part.overlap ?? 0.5;
                    const halfLen = boneLen * 0.5;
                    const ovalLen = halfLen + halfLen * ov;
                    const scY = ovalLen / (radius * 2);
                    const sep = halfLen * (1 - ov);
                    const hSegs = Math.max(4, segments >> 1);
                    const g1 = new THREE.SphereGeometry(radius, segments, hSegs);
                    g1.scale(1, scY, 1); g1.translate(0, -sep, 0);
                    const g2 = new THREE.SphereGeometry(radius, segments, hSegs);
                    g2.scale(1, scY, 1); g2.translate(0, sep, 0);
                    shapeGeo = _mergeSimpleGeos(g1, g2);
                    break;
                }
                case 'diamond':
                    shapeGeo = new THREE.OctahedronGeometry(radius);
                    shapeGeo.scale(1, boneLen / (radius * 2), 1);
                    break;
                case 'tutu': {
                    const thickness = part.tutuThickness ?? 0.01;
                    const droop = part.tutuDroop ?? 0.03;
                    const droopStart = part.tutuDroopStart ?? 0.7;
                    const innerR = radius * 0.08;
                    const outerR = radius;
                    const halfT = thickness * 0.5;
                    const droopR = outerR * droopStart;
                    const radSegs = Math.max(16, segments * 4);
                    const pts = [
                        new THREE.Vector2(innerR, halfT),
                        new THREE.Vector2(droopR, halfT),
                        new THREE.Vector2(outerR, -droop),
                        new THREE.Vector2(outerR - 0.002, -droop - halfT),
                        new THREE.Vector2(droopR, -halfT),
                        new THREE.Vector2(innerR, -halfT),
                    ];
                    shapeGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
                    const tOff = part.tutuOffset ?? 0;
                    if (Math.abs(tOff) > 0.0001) shapeGeo.translate(0, tOff, 0);
                    break;
                }
                case 'spiral_tutu':
                    shapeGeo = _buildSpiralTutu(part, radius);
                    break;
                case 'helix_ribbon':
                    shapeGeo = _buildHelixRibbon(part, radius);
                    break;
                case 'skirt':
                    shapeGeo = _buildSkirt(part, radius);
                    break;
                case 'plane':
                    shapeGeo = _buildPlane(part);
                    break;
                case 'rhombus':
                    shapeGeo = _buildRhombus(part);
                    break;
                default:
                    shapeGeo = new THREE.CylinderGeometry(radius, radius, boneLen, segments, 1);
                    break;
            }
        
            // Position between effective head and tail
            const midpoint = new THREE.Vector3().lerpVectors(effectiveHead, effectiveTail, 0.5);
            const direction = new THREE.Vector3().subVectors(effectiveTail, effectiveHead);
            if (direction.length() > 0.0001) direction.normalize();
            else direction.set(0, 1, 0);
        
            const yAxis = new THREE.Vector3(0, 1, 0);
            const shapeQuat = new THREE.Quaternion();
            if (Math.abs(direction.dot(yAxis)) < 0.9999) {
                shapeQuat.setFromUnitVectors(yAxis, direction);
            } else if (direction.y < 0) {
                shapeQuat.setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI);
            }
        
            // World-space rotation around shape center (premultiply = applied after bone alignment)
            if (part.shapeRotation) {
                const sr = part.shapeRotation;
                const rx = sr.x || 0, ry = sr.y || 0, rz = sr.z || 0;
                if (rx || ry || rz) {
                    const deg = Math.PI / 180;
                    const userRot = new THREE.Quaternion().setFromEuler(
                        new THREE.Euler(rx * deg, ry * deg, rz * deg));
                    shapeQuat.premultiply(userRot);
                }
            }
        
            const mat4 = new THREE.Matrix4();
            mat4.compose(midpoint, shapeQuat, new THREE.Vector3(1, 1, 1));
            shapeGeo.applyMatrix4(mat4);
        
            // Determine skin bone index: DEF bones map to their skeleton index, others to root (0)
            const boneIdx = canSkin ? (boneIndexMap[boneName] !== undefined ? boneIndexMap[boneName] : 0) : 0;
            geoChunks.push({ geometry: shapeGeo, color, boneIndex: boneIdx, boneName, texture: part.texture || null });
        }
        
        if (geoChunks.length === 0) return null;
        
        return geoChunks;
    }
}
