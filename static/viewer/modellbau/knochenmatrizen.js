/**
 * Knochenmatrizen — Weltlage jedes Knochens aus den Skelettdaten.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026). Zwei Funktionen mit
 * derselben Aufgabe fuer zwei Datenformen (DEF-Skelett und Rig).
 */

import * as THREE from 'three';
import { Knochengruppen } from './knochengruppen.js';


/**
 * Compute world position, quaternion, and bone length for each bone.
 * Uses the parent chain from skelData (Blender coords) and converts to Three.js.
 * Returns Map<boneName, {worldPos: Vector3, worldQuat: Quaternion, length: number}>
 */
export function computeBoneWorldTransforms(skelData, swData) {
    const skelByName = {};
    for (const b of skelData.bones) skelByName[b.name] = b;

    // Build ordered bone list from swData if available, otherwise from skelData
    const boneNames = swData ? swData.bone_names : skelData.bones.map(b => b.name);

    const result = new Map();
    const _worldPos = {};
    const _worldQuat = {};

    // Recursive compute
    function computeWorld(name) {
        if (_worldPos[name]) return;
        const data = skelByName[name];
        if (!data) return;

        // Blender local -> Three.js local
        const lp = data.local_position;
        const localPos = new THREE.Vector3(lp[0], lp[2], -lp[1]);
        const lq = data.local_quaternion;
        const localQuat = new THREE.Quaternion(lq[1], lq[3], -lq[2], lq[0]);

        if (data.parent && skelByName[data.parent]) {
            computeWorld(data.parent);
            const parentPos = _worldPos[data.parent];
            const parentQuat = _worldQuat[data.parent];
            // worldPos = parentPos + parentQuat * localPos
            const rotatedLocal = localPos.clone().applyQuaternion(parentQuat);
            _worldPos[name] = parentPos.clone().add(rotatedLocal);
            _worldQuat[name] = parentQuat.clone().multiply(localQuat);
        } else {
            _worldPos[name] = localPos.clone();
            _worldQuat[name] = localQuat.clone();
        }
    }

    for (const name of boneNames) {
        computeWorld(name);
        const data = skelByName[name];
        if (!data) continue;

        // Bone length = distance from parent to this bone (length of local_position)
        const lp = data.local_position;
        let len = Math.sqrt(lp[0]*lp[0] + lp[1]*lp[1] + lp[2]*lp[2]);

        // For leaf bones or zero-length, use fixed length
        if (len < 0.001) {
            len = Knochengruppen.ENDLAENGEN[name] || 0.03;
        }

        if (_worldPos[name]) {
            result.set(name, {
                worldPos: _worldPos[name],
                worldQuat: _worldQuat[name],
                length: len,
            });
        }
    }

    return result;
}

/**
 * Compute world transforms for rig bones (head/tail format, Blender Z-up coords).
 * Rig bones have absolute head/tail in Blender world coordinates.
 * Returns Map<boneName, {worldPos: Vector3 (head in Three.js), tailPos: Vector3, length: number}>
 */
export function computeRigBoneWorldTransforms(rigData) {
    const result = new Map();
    for (const b of rigData.bones) {
        const h = b.head; // [x, y, z] Blender coords (Z-up, Y-forward)
        const t = b.tail;
        // Convert Blender→Three.js: (x, z, -y)
        const headPos = new THREE.Vector3(h[0], h[2], -h[1]);
        const tailPos = new THREE.Vector3(t[0], t[2], -t[1]);
        const len = headPos.distanceTo(tailPos);
        result.set(b.name, { worldPos: headPos, tailPos, length: len || 0.02 });
    }
    return result;
}
