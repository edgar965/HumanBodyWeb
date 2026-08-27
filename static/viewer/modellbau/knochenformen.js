/**
 * Knochenformen — je Knochen ein Geometriestueck bauen.
 *
 * Aus modellnetz.js herausgeloest (Umbau 16.08.2026): `generateModelMesh` war
 * 375 Zeilen in vier Abschnitten — Knochenindex, Formen je Knochen,
 * Materialgruppen, Skelettaufbau. Die Formenschleife allein sind 180 davon.
 */

import * as THREE from 'three';
import { _mergeSimpleGeos, _buildPlane, _buildRhombus, _makeDoubleSided } from './formenbauer.js';
import { _buildSpiralTutu, _buildSkirt } from './formen_band.js';
import { Wendelband } from './wendelband.js';
import './knochenmatrizen.js';
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
        
            // Create shape geometry (centered at origin, along Y axis)
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
                    // Tutu: flat disc with drooping outer rim, built as LatheGeometry
                    const thickness = part.tutuThickness ?? 0.01;
                    const droop = part.tutuDroop ?? 0.03;
                    const droopStart = part.tutuDroopStart ?? 0.7;
                    const innerR = radius * 0.08; // small hole in center around bone
                    const outerR = radius;
                    const halfT = thickness * 0.5;
                    const droopR = outerR * droopStart;
                    const radSegs = Math.max(16, segments * 4);
                    // Profile points (in XY plane, X=radius, Y=height), rotated around Y
                    const pts = [
                        new THREE.Vector2(innerR, halfT),    // inner top
                        new THREE.Vector2(droopR, halfT),     // flat top to droop start
                        new THREE.Vector2(outerR, -droop),    // outer edge droops down
                        new THREE.Vector2(outerR - 0.002, -droop - halfT), // outer bottom edge
                        new THREE.Vector2(droopR, -halfT),    // flat bottom from droop start
                        new THREE.Vector2(innerR, -halfT),    // inner bottom
                    ];
                    shapeGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
                    // Apply tutuOffset (shift along bone axis)
                    const tOff = part.tutuOffset ?? 0;
                    if (Math.abs(tOff) > 0.0001) shapeGeo.translate(0, tOff, 0);
                    break;
                }
                case 'spiral_tutu':
                    shapeGeo = _buildSpiralTutu(part, radius);
                    break;
                case 'helix_ribbon':
                    shapeGeo = Wendelband.bauen(part, radius);
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
                default: // cylinder
                    shapeGeo = new THREE.CylinderGeometry(radius, radius, boneLen, segments, 1);
                    break;
            }
        
            // Position shape from effective head to effective tail
            const midpoint = new THREE.Vector3().lerpVectors(effectiveHead, effectiveTail, 0.5);
            const direction = new THREE.Vector3().subVectors(effectiveTail, effectiveHead);
            if (direction.length() > 0.0001) direction.normalize();
            else direction.copy(boneDir);
        
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
        
            geoChunks.push({ geometry: shapeGeo, boneIndex: boneIdx, color, boneName, texture: part.texture || null });
        }
        
        if (geoChunks.length === 0) return null;
        
        return geoChunks;
    }
}
