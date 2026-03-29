/**
 * Shared DEF skeleton builder — single source of truth.
 *
 * Build 176-bone THREE.Skeleton from DEF skeleton data + skin weight bone order.
 * Bone indices match skinWeightData.bone_names (authoritative for skinIndex).
 */
import * as THREE from 'three';

export function buildDefSkeleton(skelData, swData) {
    const skelByName = {};
    for (const b of skelData.bones) skelByName[b.name] = b;

    const bones = [];
    const boneByName = {};
    let rootBone = null;

    // Create bones in skin weight order (= authoritative index order)
    // Sanitize names: Three.js PropertyBinding uses dots as separators,
    // so bone names like "DEF-upper_arm.L" break track name parsing.
    for (const name of swData.bone_names) {
        const bone = new THREE.Bone();
        bone.name = name.replace(/\./g, '_');  // DEF-upper_arm.L -> DEF-upper_arm_L
        bones.push(bone);
        boneByName[name] = bone;  // Original name as key for mapping lookups
    }

    // Set local transforms and build parent-child hierarchy
    for (let i = 0; i < swData.bone_names.length; i++) {
        const name = swData.bone_names[i];
        const bone = bones[i];
        const data = skelByName[name];
        if (!data) continue;

        // Convert Blender local position (x,y,z) -> Three.js (x,z,-y)
        const p = data.local_position;
        bone.position.set(p[0], p[2], -p[1]);

        // Convert Blender quaternion [w,x,y,z] -> Three.js Quaternion(x,z,-y,w)
        const q = data.local_quaternion;
        bone.quaternion.set(q[1], q[3], -q[2], q[0]);

        // Parent-child (lookup by original name)
        if (data.parent && boneByName[data.parent]) {
            boneByName[data.parent].add(bone);
        } else {
            if (!rootBone) rootBone = bone;
        }
    }

    // Collect orphan roots (bones without skinning parent that aren't the main root)
    for (let i = 0; i < bones.length; i++) {
        const name = swData.bone_names[i];
        const data = skelByName[name];
        if (!data) continue;
        if (!data.parent && bones[i] !== rootBone) {
            if (rootBone) rootBone.add(bones[i]);
        }
    }

    if (!rootBone && bones.length > 0) rootBone = bones[0];

    // Update world matrices before creating skeleton
    rootBone.updateWorldMatrix(true, true);

    const skeleton = new THREE.Skeleton(bones);

    return { skeleton, rootBone, bones, boneByName };
}
