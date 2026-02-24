/**
 * Shared BVH → DEF retarget module.
 *
 * Hybrid approach (mirrors Blender's retarget_rokoko):
 *   CONJUGATION: spine, legs — local delta via M·q·M⁻¹
 *   WORLD_COPY:  arms, hands, fingers, face — direct world quaternion copy
 *   SKIP:        head, shoulders — stay at rest pose
 */
import * as THREE from 'three';
alert('retarget.js v2 LOADED');

// =========================================================================
// BVH format detection
// =========================================================================

export function detectBVHFormat(bones) {
    const names = new Set(bones.map(b => b.name));
    if (names.has('Hips') && names.has('LeftArm')) return 'CMU';
    if (names.has('hip') || names.has('rshoulder')) return 'MOCAPNET';
    return 'UNKNOWN';
}

// =========================================================================
// Mapping tables: BVH bone name → DEF bone name (null = skip)
// =========================================================================

export const BVH_TO_DEF_CMU = {
    'Hips':           'DEF-spine',
    'Spine':          'DEF-spine.001',
    'Spine1':         'DEF-spine.003',
    'Neck':           null,
    'Neck1':          'DEF-spine.004',
    'Head':           'DEF-spine.006',
    'LeftShoulder':   'DEF-shoulder.L',
    'LeftArm':        'DEF-upper_arm.L',
    'LeftForeArm':    'DEF-forearm.L',
    'LeftHand':       'DEF-hand.L',
    'RightShoulder':  'DEF-shoulder.R',
    'RightArm':       'DEF-upper_arm.R',
    'RightForeArm':   'DEF-forearm.R',
    'RightHand':      'DEF-hand.R',
    'LeftUpLeg':      'DEF-thigh.L',
    'LeftLeg':        'DEF-shin.L',
    'LeftFoot':       'DEF-foot.L',
    'LeftToeBase':    'DEF-toe.L',
    'RightUpLeg':     'DEF-thigh.R',
    'RightLeg':       'DEF-shin.R',
    'RightFoot':      'DEF-foot.R',
    'RightToeBase':   'DEF-toe.R',
    'LHipJoint':      null,
    'RHipJoint':      null,
    'LowerBack':      null,
    'LeftFingerBase':  null,
    'RightFingerBase': null,
    'LThumb':         null,
    'RThumb':         null,
};

export const BVH_TO_DEF_MOCAPNET = {
    // Body
    'hip':        'DEF-spine',
    'abdomen':    'DEF-spine.001',
    'chest':      'DEF-spine.003',
    'neck1':      'DEF-spine.004',
    'head':       'DEF-spine.006',
    'lcollar':    'DEF-shoulder.L',
    'rcollar':    'DEF-shoulder.R',
    'lshoulder':  'DEF-upper_arm.L',
    'rshoulder':  'DEF-upper_arm.R',
    'lelbow':     'DEF-forearm.L',
    'relbow':     'DEF-forearm.R',
    'lhand':      'DEF-hand.L',
    'rhand':      'DEF-hand.R',
    'lhip':       'DEF-thigh.L',
    'rhip':       'DEF-thigh.R',
    'lknee':      'DEF-shin.L',
    'rknee':      'DEF-shin.R',
    'lfoot':      'DEF-foot.L',
    'rfoot':      'DEF-foot.R',
    'toe1-1.l':   'DEF-toe.L',
    'toe1-1.r':   'DEF-toe.R',

    // Fingers left
    'lthumb':       'DEF-thumb.01.L',
    'finger1-2.l':  'DEF-thumb.02.L',
    'finger1-3.l':  'DEF-thumb.03.L',
    'finger2-1.l':  'DEF-f_index.01.L',
    'finger2-2.l':  'DEF-f_index.02.L',
    'finger2-3.l':  'DEF-f_index.03.L',
    'finger3-1.l':  'DEF-f_middle.01.L',
    'finger3-2.l':  'DEF-f_middle.02.L',
    'finger3-3.l':  'DEF-f_middle.03.L',
    'finger4-1.l':  'DEF-f_ring.01.L',
    'finger4-2.l':  'DEF-f_ring.02.L',
    'finger4-3.l':  'DEF-f_ring.03.L',
    'finger5-1.l':  'DEF-f_pinky.01.L',
    'finger5-2.l':  'DEF-f_pinky.02.L',
    'finger5-3.l':  'DEF-f_pinky.03.L',

    // Fingers right
    'rthumb':       'DEF-thumb.01.R',
    'finger1-2.r':  'DEF-thumb.02.R',
    'finger1-3.r':  'DEF-thumb.03.R',
    'finger2-1.r':  'DEF-f_index.01.R',
    'finger2-2.r':  'DEF-f_index.02.R',
    'finger2-3.r':  'DEF-f_index.03.R',
    'finger3-1.r':  'DEF-f_middle.01.R',
    'finger3-2.r':  'DEF-f_middle.02.R',
    'finger3-3.r':  'DEF-f_middle.03.R',
    'finger4-1.r':  'DEF-f_ring.01.R',
    'finger4-2.r':  'DEF-f_ring.02.R',
    'finger4-3.r':  'DEF-f_ring.03.R',
    'finger5-1.r':  'DEF-f_pinky.01.R',
    'finger5-2.r':  'DEF-f_pinky.02.R',
    'finger5-3.r':  'DEF-f_pinky.03.R',

    // Palms
    'metacarpal1.l': 'DEF-palm.01.L',
    'metacarpal2.l': 'DEF-palm.02.L',
    'metacarpal3.l': 'DEF-palm.03.L',
    'metacarpal4.l': 'DEF-palm.04.L',
    'metacarpal1.r': 'DEF-palm.01.R',
    'metacarpal2.r': 'DEF-palm.02.R',
    'metacarpal3.r': 'DEF-palm.03.R',
    'metacarpal4.r': 'DEF-palm.04.R',

    // Face
    'jaw':       'DEF-jaw',
    'tongue01':  'DEF-tongue',
    'tongue02':  'DEF-tongue.001',
    'tongue03':  'DEF-tongue.002',
    'eye.l':     'MCH-eye.L',
    'eye.r':     'MCH-eye.R',

    // Lips
    'oris04.l':  'DEF-lip.T.L',
    'oris04.r':  'DEF-lip.T.R',
    'oris03.l':  'DEF-lip.T.L.001',
    'oris03.r':  'DEF-lip.T.R.001',
    'oris06.l':  'DEF-lip.B.L',
    'oris06.r':  'DEF-lip.B.R',
    'oris07.l':  'DEF-lip.B.L.001',
    'oris07.r':  'DEF-lip.B.R.001',

    // Eyelids
    'orbicularis03.l': 'DEF-lid.T.L',
    'orbicularis03.r': 'DEF-lid.T.R',
    'orbicularis04.l': 'DEF-lid.B.L',
    'orbicularis04.r': 'DEF-lid.B.R',
};

// =========================================================================
// Per-bone retarget mode classification
// =========================================================================

// CONJUGATION: localQ = defLocalRestQ * M * bvhLocalQ * M⁻¹
//   where M = defWorldRestQ⁻¹
// These bones need local delta transfer (spine chain, legs).
const CONJUGATION_BONES = new Set([
    'DEF-spine', 'DEF-spine.001', 'DEF-spine.003', 'DEF-spine.004',
    'DEF-thigh.L', 'DEF-thigh.R', 'DEF-shin.L', 'DEF-shin.R',
    'DEF-foot.L', 'DEF-foot.R', 'DEF-toe.L', 'DEF-toe.R',
]);

// SKIP: keep at rest pose (head gets motion from neck chain, shoulders are identity).
const SKIP_BONES = new Set([
    'DEF-spine.006',   // head
    'DEF-shoulder.L', 'DEF-shoulder.R',
]);

// Everything else mapped → WORLD_COPY: worldQ = bvhWorldQ

// =========================================================================
// Main retarget function
// =========================================================================

/**
 * Retarget a BVH animation clip to the DEF skeleton.
 *
 * @param {Object} bvhResult - { skeleton, clip } from BVHLoader
 * @param {Object} defSkel - { rootBone, boneByName } from buildDefSkeleton()
 * @param {string} format - 'CMU' or 'MOCAPNET'
 * @param {Object} [opts] - { bodyMesh } for height measurement
 * @returns {THREE.AnimationClip}
 */
export function retargetBVHToDefClip(bvhResult, defSkel, format, opts = {}) {
    console.log('%c[RETARGET] Hybrid: CONJUGATION spine/legs + WORLD_COPY arms',
                'color: lime; font-weight: bold');

    const bvhBones = bvhResult.skeleton.bones;
    const bvhClip = bvhResult.clip;
    const mapping = format === 'CMU' ? BVH_TO_DEF_CMU : BVH_TO_DEF_MOCAPNET;

    // --- DEF rest-pose quaternions ---
    defSkel.rootBone.updateWorldMatrix(true, true);
    const defWorldRestQ = {};
    const defLocalRestQ = {};
    for (const [origName, bone] of Object.entries(defSkel.boneByName)) {
        defWorldRestQ[origName] = new THREE.Quaternion();
        bone.getWorldQuaternion(defWorldRestQ[origName]);
        defLocalRestQ[origName] = bone.quaternion.clone();
    }

    // --- BVH bone lookup + DEF↔BVH mapping ---
    const bvhBoneByName = {};
    for (const b of bvhBones) bvhBoneByName[b.name] = b;

    const defToBvhName = {};
    for (const [bvhName, defName] of Object.entries(mapping)) {
        if (defName && bvhBoneByName[bvhName] && defSkel.boneByName[defName])
            defToBvhName[defName] = bvhName;
    }

    // Reverse lookup: bone Object3D → original DEF name
    const origNameByBone = new Map();
    for (const [origName, bone] of Object.entries(defSkel.boneByName))
        origNameByBone.set(bone, origName);

    // --- BFS hierarchy order ---
    const hierarchyOrder = [];
    const bfsQueue = [defSkel.rootBone];
    while (bfsQueue.length > 0) {
        const bone = bfsQueue.shift();
        const origName = origNameByBone.get(bone);
        if (origName) hierarchyOrder.push(origName);
        for (const child of bone.children) if (child.isBone) bfsQueue.push(child);
    }

    // --- Parse BVH tracks ---
    const bvhQuatTracks = {};
    const bvhPosTracks = {};
    for (const track of bvhClip.tracks) {
        const lastDot = track.name.lastIndexOf('.');
        if (lastDot < 0) continue;
        const boneName = track.name.substring(0, lastDot);
        const prop = track.name.substring(lastDot + 1);
        if (prop === 'quaternion') bvhQuatTracks[boneName] = track;
        if (prop === 'position') bvhPosTracks[boneName] = track;
    }

    // --- Height scale for root position ---
    const bvhRoot = bvhBones[0];
    bvhRoot.updateWorldMatrix(true, true);
    const skelBox = new THREE.Box3();
    const tmpVec = new THREE.Vector3();
    for (const b of bvhBones) { b.getWorldPosition(tmpVec); skelBox.expandByPoint(tmpVec); }
    const bvhHeight = Math.max(skelBox.max.y - skelBox.min.y, 0.01);
    let bodyH = 1.75;
    if (opts.bodyMesh) {
        const bb = new THREE.Box3().setFromObject(opts.bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
    }
    const heightScale = bodyH / bvhHeight;

    // --- Pre-compute conjugation matrices (M = defWorldRestQ⁻¹) ---
    const conjM = {};
    for (const defName of CONJUGATION_BONES) {
        if (defWorldRestQ[defName]) {
            conjM[defName] = defWorldRestQ[defName].clone().invert();
        }
    }

    // --- Frame data ---
    const firstTrack = Object.values(bvhQuatTracks)[0];
    if (!firstTrack) return new THREE.AnimationClip('retargeted', 0, []);
    const times = firstTrack.times;
    const fc = times.length;

    const mappedDefNames = new Set(Object.keys(defToBvhName));
    const outputQuats = {};
    for (const defName of mappedDefNames) {
        if (!SKIP_BONES.has(defName)) {
            outputQuats[defName] = new Float32Array(fc * 4);
        }
    }

    // Animated world quaternion per DEF bone (reused each frame)
    const animWorldQ = {};
    for (const name of hierarchyOrder) animWorldQ[name] = new THREE.Quaternion();

    const tmpQ = new THREE.Quaternion();
    const tmpQ2 = new THREE.Quaternion();

    // --- Per-frame retarget ---
    const _worldCopyNames = [];
    let _worldCopyLogged = false;
    for (let f = 0; f < fc; f++) {
        // 1. Set BVH bones to this frame
        for (const bvhBone of bvhBones) {
            const track = bvhQuatTracks[bvhBone.name];
            if (track) {
                const i = f * 4;
                bvhBone.quaternion.set(
                    track.values[i], track.values[i+1],
                    track.values[i+2], track.values[i+3]);
            }
        }
        bvhRoot.updateWorldMatrix(true, true);

        // 2. Compute animated world Q for each DEF bone (BFS order)
        for (const defName of hierarchyOrder) {
            const bone = defSkel.boneByName[defName];
            const bvhName = defToBvhName[defName];
            const parentName = origNameByBone.get(bone.parent);
            const parentWorldQ = (parentName && animWorldQ[parentName])
                ? animWorldQ[parentName] : null;

            if (!bvhName || SKIP_BONES.has(defName)) {
                // SKIP or unmapped: localQ = defLocalRestQ
                if (parentWorldQ) {
                    animWorldQ[defName].copy(parentWorldQ).multiply(defLocalRestQ[defName]);
                } else {
                    animWorldQ[defName].copy(defWorldRestQ[defName]);
                }

            } else if (CONJUGATION_BONES.has(defName)) {
                // CONJUGATION: delta = M * bvhLocalQ * M⁻¹
                //              localQ = defLocalRestQ * delta
                //              worldQ = parentWorldQ * localQ
                const bvhBone = bvhBoneByName[bvhName];
                // bvhLocalQ = bvhBone.quaternion (already set from track)
                const M = conjM[defName];
                // delta = M * bvhLocalQ * M⁻¹
                tmpQ.copy(M).multiply(bvhBone.quaternion).multiply(tmpQ2.copy(M).invert());
                // localQ = defLocalRestQ * delta
                tmpQ2.copy(defLocalRestQ[defName]).multiply(tmpQ);

                if (parentWorldQ) {
                    animWorldQ[defName].copy(parentWorldQ).multiply(tmpQ2);
                } else {
                    animWorldQ[defName].copy(tmpQ2);
                }

            } else {
                // WORLD_COPY: worldQ = bvhWorldQ
                bvhBoneByName[bvhName].getWorldQuaternion(animWorldQ[defName]);
                // DEBUG: force identity to verify code path
                if (f === 0 && !_worldCopyLogged) {
                    _worldCopyNames.push(defName);
                }
            }

            // 3. Convert world Q to local Q for output track
            if (!mappedDefNames.has(defName) || SKIP_BONES.has(defName)) continue;

            if (parentWorldQ) {
                tmpQ.copy(parentWorldQ).invert().multiply(animWorldQ[defName]).normalize();
            } else {
                tmpQ.copy(animWorldQ[defName]);
            }

            const out = outputQuats[defName];
            const i = f * 4;
            out[i] = tmpQ.x; out[i+1] = tmpQ.y; out[i+2] = tmpQ.z; out[i+3] = tmpQ.w;
        }
    }

    if (_worldCopyNames.length > 0) {
        const el = document.getElementById('anim-info');
        if (el) el.textContent = `WORLD_COPY: ${_worldCopyNames.join(', ')}`;
        console.log('[RETARGET] WORLD_COPY bones:', _worldCopyNames);
    }
    _worldCopyLogged = true;

    // Reset BVH bones to rest pose
    for (const bvhBone of bvhBones) bvhBone.quaternion.set(0, 0, 0, 1);
    bvhRoot.updateWorldMatrix(true, true);

    // --- Build output tracks ---
    const newTracks = [];
    for (const defName of mappedDefNames) {
        if (SKIP_BONES.has(defName)) continue;
        const bone = defSkel.boneByName[defName];
        newTracks.push(new THREE.QuaternionKeyframeTrack(
            `${bone.name}.quaternion`, times, outputQuats[defName]));
    }

    // Root position track
    const rootBvhName = bvhBones[0].name;
    const rootDefName = mapping[rootBvhName];
    const rootPosTrack = bvhPosTracks[rootBvhName];
    if (rootDefName && rootPosTrack) {
        const defBone = defSkel.boneByName[rootDefName];
        if (defBone) {
            const bvhRef = new THREE.Vector3(
                rootPosTrack.values[0], rootPosTrack.values[1], rootPosTrack.values[2]);
            const defRestPos = defBone.position.clone();
            const values = new Float32Array(rootPosTrack.values.length);
            for (let i = 0; i < rootPosTrack.values.length; i += 3) {
                values[i]   = defRestPos.x + (rootPosTrack.values[i]   - bvhRef.x) * heightScale;
                values[i+1] = defRestPos.y + (rootPosTrack.values[i+1] - bvhRef.y) * heightScale;
                values[i+2] = defRestPos.z + (rootPosTrack.values[i+2] - bvhRef.z) * heightScale;
            }
            newTracks.push(new THREE.VectorKeyframeTrack(
                `${defBone.name}.position`, rootPosTrack.times, values));
        }
    }

    const nConj = [...mappedDefNames].filter(n => CONJUGATION_BONES.has(n)).length;
    const nWorld = [...mappedDefNames].filter(n => !CONJUGATION_BONES.has(n) && !SKIP_BONES.has(n)).length;
    const nSkip = [...mappedDefNames].filter(n => SKIP_BONES.has(n)).length;
    console.log(`Retargeted: ${mappedDefNames.size} bones (${nConj} conj, ${nWorld} world, ${nSkip} skip), ${fc} frames`);

    return new THREE.AnimationClip('retargeted', bvhClip.duration, newTracks);
}
