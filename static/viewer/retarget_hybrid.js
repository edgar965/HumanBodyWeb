/**
 * Shared BVH → DEF retarget module.
 *
 * Approach: For each frame, compute the BVH bone's WORLD animation Q
 * (product of parent chain), then map to DEF:
 *   defWorldQ = bvhWorldAnimQ × defWorldRestQ
 *   defLocalQ = defParentAnimWQ⁻¹ × defWorldQ
 *
 * This works because BVH bones in Three.js have identity rest Qs, so
 * bvhWorldAnimQ IS the cumulative world rotation. Multiplying by the
 * DEF rest Q applies the BVH rotation on top of the DEF rest orientation.
 */
import * as THREE from 'three';

// =========================================================================
// BVH format detection
// =========================================================================

export function detectBVHFormat(bones) {
    const names = new Set(bones.map(b => b.name));
    // AIST: Pelvis + Left_hip (underscore naming, no Chest)
    if (names.has('Pelvis') && names.has('Left_hip')) return 'AIST';
    // Bandai: uses Chest + UpperArm_L (underscore naming)
    if (names.has('Chest') && names.has('UpperArm_L')) return 'BANDAI';
    if (names.has('Hips') && names.has('LeftArm')) {
        // Mixamo has Spine2, CMU does not (CMU uses LowerBack instead)
        return names.has('Spine2') ? 'MIXAMO' : 'CMU';
    }
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

export const BVH_TO_DEF_MIXAMO = {
    // Spine chain: Mixamo has Spine/Spine1/Spine2, CMU skips .002
    'Hips':           'DEF-spine',
    'Spine':          'DEF-spine.001',
    'Spine1':         'DEF-spine.002',
    'Spine2':         'DEF-spine.003',
    'Neck':           null,
    'Neck1':          'DEF-spine.004',
    'Head':           'DEF-spine.006',

    // Arms
    'LeftShoulder':   'DEF-shoulder.L',
    'LeftArm':        'DEF-upper_arm.L',
    'LeftForeArm':    'DEF-forearm.L',
    'LeftHand':       'DEF-hand.L',
    'RightShoulder':  'DEF-shoulder.R',
    'RightArm':       'DEF-upper_arm.R',
    'RightForeArm':   'DEF-forearm.R',
    'RightHand':      'DEF-hand.R',

    // Legs
    'LeftUpLeg':      'DEF-thigh.L',
    'LeftLeg':        'DEF-shin.L',
    'LeftFoot':       'DEF-foot.L',
    'LeftToeBase':    'DEF-toe.L',
    'RightUpLeg':     'DEF-thigh.R',
    'RightLeg':       'DEF-shin.R',
    'RightFoot':      'DEF-foot.R',
    'RightToeBase':   'DEF-toe.R',

    // Fingers left — Thumb
    'LeftHandThumb1':  'DEF-thumb.01.L',
    'LeftHandThumb2':  'DEF-thumb.02.L',
    'LeftHandThumb3':  'DEF-thumb.03.L',
    // Fingers left — Index
    'LeftHandIndex1':  'DEF-f_index.01.L',
    'LeftHandIndex2':  'DEF-f_index.02.L',
    'LeftHandIndex3':  'DEF-f_index.03.L',
    // Fingers left — Middle
    'LeftHandMiddle1': 'DEF-f_middle.01.L',
    'LeftHandMiddle2': 'DEF-f_middle.02.L',
    'LeftHandMiddle3': 'DEF-f_middle.03.L',
    // Fingers left — Ring
    'LeftHandRing1':   'DEF-f_ring.01.L',
    'LeftHandRing2':   'DEF-f_ring.02.L',
    'LeftHandRing3':   'DEF-f_ring.03.L',
    // Fingers left — Pinky
    'LeftHandPinky1':  'DEF-f_pinky.01.L',
    'LeftHandPinky2':  'DEF-f_pinky.02.L',
    'LeftHandPinky3':  'DEF-f_pinky.03.L',

    // Fingers right — Thumb
    'RightHandThumb1': 'DEF-thumb.01.R',
    'RightHandThumb2': 'DEF-thumb.02.R',
    'RightHandThumb3': 'DEF-thumb.03.R',
    // Fingers right — Index
    'RightHandIndex1': 'DEF-f_index.01.R',
    'RightHandIndex2': 'DEF-f_index.02.R',
    'RightHandIndex3': 'DEF-f_index.03.R',
    // Fingers right — Middle
    'RightHandMiddle1':'DEF-f_middle.01.R',
    'RightHandMiddle2':'DEF-f_middle.02.R',
    'RightHandMiddle3':'DEF-f_middle.03.R',
    // Fingers right — Ring
    'RightHandRing1':  'DEF-f_ring.01.R',
    'RightHandRing2':  'DEF-f_ring.02.R',
    'RightHandRing3':  'DEF-f_ring.03.R',
    // Fingers right — Pinky
    'RightHandPinky1': 'DEF-f_pinky.01.R',
    'RightHandPinky2': 'DEF-f_pinky.02.R',
    'RightHandPinky3': 'DEF-f_pinky.03.R',
};

export const BVH_TO_DEF_MOCAPNET = {
    // Body (normalized MocapNET names — lowercase)
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

    // Body (OpenPose-style names — capitalized, as in testOpenPose.bvh)
    'lCollar':    'DEF-shoulder.L',
    'rCollar':    'DEF-shoulder.R',
    'lShldr':     'DEF-upper_arm.L',
    'rShldr':     'DEF-upper_arm.R',
    'lForeArm':   'DEF-forearm.L',
    'rForeArm':   'DEF-forearm.R',
    'lHand':      'DEF-hand.L',
    'rHand':      'DEF-hand.R',
    'lThigh':     'DEF-thigh.L',
    'rThigh':     'DEF-thigh.R',
    'lShin':      'DEF-shin.L',
    'rShin':      'DEF-shin.R',
    'lFoot':      'DEF-foot.L',
    'rFoot':      'DEF-foot.R',
    'lButtock':   null,
    'rButtock':   null,
    'toe1-1.L':   'DEF-toe.L',
    'toe1-1.R':   'DEF-toe.R',

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

export const BVH_TO_DEF_AIST = {
    // AIST skeleton (Pelvis → Spine1/2/3 → Neck → Head, Left_hip/knee/ankle/foot)
    'Pelvis':          'DEF-spine',
    'Spine1':          'DEF-spine.001',
    'Spine2':          'DEF-spine.002',
    'Spine3':          'DEF-spine.003',
    'Neck':            'DEF-spine.004',
    'Head':            'DEF-spine.006',
    'Left_collar':     'DEF-shoulder.L',
    'Left_shoulder':   'DEF-upper_arm.L',
    'Left_elbow':      'DEF-forearm.L',
    'Left_wrist':      'DEF-hand.L',
    'Left_palm':       null,
    'Right_collar':    'DEF-shoulder.R',
    'Right_shoulder':  'DEF-upper_arm.R',
    'Right_elbow':     'DEF-forearm.R',
    'Right_wrist':     'DEF-hand.R',
    'Right_palm':      null,
    'Left_hip':        'DEF-thigh.L',
    'Left_knee':       'DEF-shin.L',
    'Left_ankle':      'DEF-foot.L',
    'Left_foot':       'DEF-toe.L',
    'Right_hip':       'DEF-thigh.R',
    'Right_knee':      'DEF-shin.R',
    'Right_ankle':     'DEF-foot.R',
    'Right_foot':      'DEF-toe.R',
};

export const BVH_TO_DEF_BANDAI = {
    // Bandai Namco skeleton (joint_Root → Hips → Spine → Chest → ...)
    'Hips':        'DEF-spine',
    'Spine':       'DEF-spine.001',
    'Chest':       'DEF-spine.003',
    'Neck':        'DEF-spine.004',
    'Head':        'DEF-spine.006',
    'Shoulder_L':  'DEF-shoulder.L',
    'UpperArm_L':  'DEF-upper_arm.L',
    'LowerArm_L':  'DEF-forearm.L',
    'Hand_L':      'DEF-hand.L',
    'Shoulder_R':  'DEF-shoulder.R',
    'UpperArm_R':  'DEF-upper_arm.R',
    'LowerArm_R':  'DEF-forearm.R',
    'Hand_R':      'DEF-hand.R',
    'UpperLeg_L':  'DEF-thigh.L',
    'LowerLeg_L':  'DEF-shin.L',
    'Foot_L':      'DEF-foot.L',
    'Toes_L':      'DEF-toe.L',
    'UpperLeg_R':  'DEF-thigh.R',
    'LowerLeg_R':  'DEF-shin.R',
    'Foot_R':      'DEF-foot.R',
    'Toes_R':      'DEF-toe.R',
    'joint_Root':  null,
};

// =========================================================================
// Main retarget function
// =========================================================================

/**
 * Retarget a BVH animation clip to the DEF skeleton.
 *
 * For each frame:
 *   1. Compute bvhWorldAnimQ for every BVH bone (product of parent chain)
 *   2. For mapped DEF bones: defWorldQ = bvhWorldAnimQ × defWorldRestQ
 *   3. Convert to local: defLocalQ = defParentAnimWQ⁻¹ × defWorldQ
 *   4. Unmapped bones propagate at rest
 *
 * @param {Object} bvhResult - { skeleton, clip } from BVHLoader
 * @param {Object} defSkel - { rootBone, boneByName } from buildDefSkeleton()
 * @param {string} format - 'CMU', 'MIXAMO', or 'MOCAPNET'
 * @param {Object} [opts] - { bodyMesh } for height measurement
 * @returns {THREE.AnimationClip}
 */
export function retargetBVHToDefClip(bvhResult, defSkel, format, opts = {}) {
    const bvhBones = bvhResult.skeleton.bones;
    const bvhClip = bvhResult.clip;
    const mapping = format === 'CMU' ? BVH_TO_DEF_CMU
                  : format === 'MIXAMO' ? BVH_TO_DEF_MIXAMO
                  : format === 'BANDAI' ? BVH_TO_DEF_BANDAI
                  : format === 'AIST' ? BVH_TO_DEF_AIST
                  : BVH_TO_DEF_MOCAPNET;

    // --- DEF rest-pose world quaternions ---
    defSkel.rootBone.updateWorldMatrix(true, true);

    const defWorldRestQ = {};       // bone's world Q at rest
    const defParentWorldRestQ = {}; // bone's PARENT world Q at rest

    // Reverse lookup: bone Object3D → original DEF name
    const origNameByBone = new Map();
    for (const [origName, bone] of Object.entries(defSkel.boneByName))
        origNameByBone.set(bone, origName);

    for (const [origName, bone] of Object.entries(defSkel.boneByName)) {
        defWorldRestQ[origName] = new THREE.Quaternion();
        bone.getWorldQuaternion(defWorldRestQ[origName]);

        const parentName = origNameByBone.get(bone.parent);
        if (parentName && defWorldRestQ[parentName]) {
            defParentWorldRestQ[origName] = defWorldRestQ[parentName];
        } else if (bone.parent) {
            defParentWorldRestQ[origName] = new THREE.Quaternion();
            bone.parent.getWorldQuaternion(defParentWorldRestQ[origName]);
        }
    }

    // --- BVH bone lookup ---
    const bvhBoneByName = {};
    for (const b of bvhBones) bvhBoneByName[b.name] = b;

    // Build BVH bone hierarchy order (for world Q accumulation per frame)
    const bvhRoot = bvhBones[0];
    const bvhBonesSorted = [];
    const bvhBoneParentName = {};
    function collectBvhHierarchy(bone) {
        bvhBonesSorted.push(bone.name);
        for (const child of bone.children) {
            if (child.isBone) {
                bvhBoneParentName[child.name] = bone.name;
                collectBvhHierarchy(child);
            }
        }
    }
    collectBvhHierarchy(bvhRoot);

    // --- Mapping ---
    const skipDefBones = opts.skipDefBones || new Set();
    const defToBvhName = {};
    for (const [bvhName, defName] of Object.entries(mapping)) {
        if (defName && bvhBoneByName[bvhName] && defSkel.boneByName[defName]
            && !skipDefBones.has(defName))
            defToBvhName[defName] = bvhName;
    }
    const mappedDefNames = new Set(Object.keys(defToBvhName));
    console.log(`[RETARGET] ${mappedDefNames.size} bones mapped`);

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
    // Compute bounding box from bone hierarchy (position + quaternion chain) without
    // any wrapper/group transforms. This is essential for Bandai BVH where frame-0
    // quaternions define the standing pose — raw offset accumulation misses this.
    const skelBox = new THREE.Box3();
    const _tmpQ2 = new THREE.Quaternion();
    const _tmpV2 = new THREE.Vector3();
    function accBvhWorldPos(bone, parentWQ, parentWP) {
        _tmpV2.copy(bone.position).applyQuaternion(parentWQ);
        const wp = parentWP.clone().add(_tmpV2);
        skelBox.expandByPoint(wp);
        _tmpQ2.copy(parentWQ).multiply(bone.quaternion);
        for (const c of bone.children) {
            if (c.isBone) accBvhWorldPos(c, _tmpQ2.clone(), wp);
        }
    }
    accBvhWorldPos(bvhRoot, new THREE.Quaternion(), new THREE.Vector3());
    const bvhHeight = Math.max(skelBox.max.y - skelBox.min.y, 0.01);
    let bodyH = 1.68;
    if (opts.bodyMesh) {
        const bb = new THREE.Box3().setFromObject(opts.bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
    }
    const heightScale = bodyH / bvhHeight;

    // --- Rest local Q for every DEF bone (for unmapped propagation) ---
    const defRestLocalQ = {};
    for (const [origName, bone] of Object.entries(defSkel.boneByName)) {
        if (defParentWorldRestQ[origName]) {
            defRestLocalQ[origName] = defParentWorldRestQ[origName].clone().invert()
                .multiply(defWorldRestQ[origName]);
        } else {
            defRestLocalQ[origName] = defWorldRestQ[origName].clone();
        }
    }

    // --- For Bandai: compute frame-0 BVH world Qs BEFORE direction correction ---
    // Bandai encodes the standing pose in frame-0 rotations (not identity rest).
    // We need frame-0 world Qs to compute correct bone directions for direction correction.
    // AIST uses standard retarget (like CMU) — frame-0 world directions give 45-114°
    // corrections with L/R asymmetry, which is wrong. Standard formula handles it correctly.
    const bvhRestWorldQ = {};
    const useDeltaRetarget = (format === 'BANDAI');
    if (useDeltaRetarget) {
        const _tq = new THREE.Quaternion();
        for (const bvhName of bvhBonesSorted) {
            const track = bvhQuatTracks[bvhName];
            if (track) {
                _tq.set(track.values[0], track.values[1],
                        track.values[2], track.values[3]);
            } else {
                _tq.set(0, 0, 0, 1);
            }
            const parentName = bvhBoneParentName[bvhName];
            if (parentName && bvhRestWorldQ[parentName]) {
                bvhRestWorldQ[bvhName] = bvhRestWorldQ[parentName].clone().multiply(_tq);
            } else {
                bvhRestWorldQ[bvhName] = _tq.clone();
            }
        }
    }

    // --- Offset Q per mapped bone (with direction correction) ---
    // Direction correction aligns BVH bone directions with DEF bone directions.
    // Standard (CMU/Mixamo/MocapNET): BVH rest is identity, use local offsets.
    // Delta (Bandai/AIST): use frame-0 WORLD directions (local offsets rotated
    // by frame-0 world Q) since frame-0 has non-identity rotations.
    const _NEG_Z = new THREE.Vector3(0, 0, -1);
    const offsetQ = {};

    // Identify root DEF bone (no mapped parent → skip direction correction)
    const rootDefName = Object.values(mapping).find(d => d && defSkel.boneByName[d]);

    // Bones where direction correction should be skipped.
    // AIST: ankle→foot offset points downward (-Y,-Z) while DEF-foot points forward.
    // Direction correction maps forward→down causing "ballerina feet".
    const skipDirCorrectionBones = new Set();
    if (format === 'AIST') {
        skipDirCorrectionBones.add('DEF-foot.L');
        skipDirCorrectionBones.add('DEF-foot.R');
        skipDirCorrectionBones.add('DEF-toe.L');
        skipDirCorrectionBones.add('DEF-toe.R');
        // AIST has 2-bone neck (Neck→Head) but DEF has 3-bone chain
        // (spine.004→spine.005→spine.006). Topology mismatch causes
        // direction correction to bend the head at unnatural angles.
        skipDirCorrectionBones.add('DEF-spine.004');
        skipDirCorrectionBones.add('DEF-spine.006');
    }
    if (format === 'MOCAPNET') {
        skipDirCorrectionBones.add('DEF-foot.L');
        skipDirCorrectionBones.add('DEF-foot.R');
        skipDirCorrectionBones.add('DEF-toe.L');
        skipDirCorrectionBones.add('DEF-toe.R');
        skipDirCorrectionBones.add('DEF-jaw');
        skipDirCorrectionBones.add('DEF-spine.004');
        skipDirCorrectionBones.add('DEF-spine.006');
    }

    for (const [defName, bvhName] of Object.entries(defToBvhName)) {
        // Skip direction correction for root bone — root has multiple children
        // with divergent directions, causing erroneous correction
        if (defName === rootDefName || skipDirCorrectionBones.has(defName)) {
            offsetQ[defName] = defWorldRestQ[defName].clone();
            continue;
        }

        // DEF bone direction at rest (world space)
        const defRestDir = _NEG_Z.clone().applyQuaternion(defWorldRestQ[defName]).normalize();

        const bvhBone = bvhBoneByName[bvhName];

        // Find BVH bone direction from best-aligned child
        let bvhDir = null;
        let bestDot = -Infinity;
        for (const child of bvhBone.children) {
            if (child.isBone && child.position.lengthSq() > 1e-10) {
                let dir;
                if (useDeltaRetarget && bvhRestWorldQ[bvhName]) {
                    // Delta retarget: rotate local offset by frame-0 world Q
                    // to get the actual world-space direction at frame 0
                    dir = child.position.clone()
                        .applyQuaternion(bvhRestWorldQ[bvhName]).normalize();
                } else {
                    // Standard retarget: BVH rest is identity, local = world
                    dir = child.position.clone().normalize();
                }
                const dot = dir.dot(defRestDir);
                if (dot > bestDot) { bestDot = dot; bvhDir = dir; }
            }
        }
        // Fallback to own position offset
        if (!bvhDir && bvhBone.position.lengthSq() > 1e-10) {
            if (useDeltaRetarget) {
                const parentName = bvhBoneParentName[bvhName];
                if (parentName && bvhRestWorldQ[parentName]) {
                    bvhDir = bvhBone.position.clone()
                        .applyQuaternion(bvhRestWorldQ[parentName]).normalize();
                } else {
                    bvhDir = bvhBone.position.clone().normalize();
                }
            } else {
                bvhDir = bvhBone.position.clone().normalize();
            }
        }

        if (!bvhDir || bvhDir.lengthSq() < 1e-10) {
            offsetQ[defName] = defWorldRestQ[defName].clone();
        } else {
            const dirCorr = new THREE.Quaternion().setFromUnitVectors(defRestDir, bvhDir);
            offsetQ[defName] = dirCorr.multiply(defWorldRestQ[defName]);
        }
    }


    // --- Sort ALL DEF bones by depth (parent before child) ---
    const allDefBonesSorted = Object.keys(defSkel.boneByName).sort((a, b) => {
        let da = 0, ca = defSkel.boneByName[a];
        while (ca.parent) { da++; ca = ca.parent; }
        let db = 0, cb = defSkel.boneByName[b];
        while (cb.parent) { db++; cb = cb.parent; }
        return da - db;
    });

    // --- Frame data ---
    const firstTrack = Object.values(bvhQuatTracks)[0];
    if (!firstTrack) return new THREE.AnimationClip('retargeted', 0, []);
    const times = firstTrack.times;
    const fc = times.length;

    const outputQuats = {};
    for (const defName of mappedDefNames) {
        outputQuats[defName] = new Float32Array(fc * 4);
    }

    const tmpQ = new THREE.Quaternion();
    const desiredWorldQ = new THREE.Quaternion();
    const defAnimWorldQ = {};   // per-frame animated world Q cache
    const bvhWorldAnimQ = {};   // per-frame BVH world Q cache

    // --- Per-frame retarget ---
    for (let f = 0; f < fc; f++) {
        const ti = f * 4;

        // Step 1: Compute BVH world anim Q for every BVH bone
        for (const bvhName of bvhBonesSorted) {
            const track = bvhQuatTracks[bvhName];
            if (track) {
                tmpQ.set(track.values[ti], track.values[ti+1],
                         track.values[ti+2], track.values[ti+3]);
            } else {
                tmpQ.set(0, 0, 0, 1);
            }
            const parentName = bvhBoneParentName[bvhName];
            if (parentName && bvhWorldAnimQ[parentName]) {
                bvhWorldAnimQ[bvhName] = bvhWorldAnimQ[parentName].clone().multiply(tmpQ);
            } else {
                bvhWorldAnimQ[bvhName] = tmpQ.clone();
            }
        }

        // Step 2: Compute DEF local Qs in hierarchy order
        for (const defName of allDefBonesSorted) {
            const bone = defSkel.boneByName[defName];
            const parentOrigName = origNameByBone.get(bone.parent);
            const parentAnimWQ = (parentOrigName && defAnimWorldQ[parentOrigName])
                ? defAnimWorldQ[parentOrigName]
                : new THREE.Quaternion();

            if (mappedDefNames.has(defName)) {
                const bvhName = defToBvhName[defName];

                if (useDeltaRetarget) {
                    // Delta + direction correction:
                    // desiredWorldQ = (bvhWAQ × bvhRWQ⁻¹) × offsetQ
                    // where offsetQ uses frame-0 posed bone directions for correction.
                    // At frame 0: delta=identity → desiredWorldQ = offsetQ (direction-aligned rest)
                    // At frame N: delta rotates from frame-0 to frame-N applied to aligned DEF
                    const bvhWAQ = bvhWorldAnimQ[bvhName];
                    const bvhRWQ = bvhRestWorldQ[bvhName];
                    if (bvhWAQ && bvhRWQ) {
                        desiredWorldQ.copy(bvhWAQ)
                            .multiply(bvhRWQ.clone().invert())
                            .multiply(offsetQ[defName])
                            .normalize();
                        // defLocalQ = parentAnimWQ⁻¹ × desiredWorldQ
                        tmpQ.copy(parentAnimWQ).invert().multiply(desiredWorldQ).normalize();
                    } else {
                        tmpQ.copy(defRestLocalQ[defName] || new THREE.Quaternion());
                    }
                } else {
                    // Standard: desiredWorldQ = bvhWorldAnimQ × offsetQ
                    const bvhWAQ = bvhWorldAnimQ[bvhName];
                    if (bvhWAQ) {
                        desiredWorldQ.copy(bvhWAQ).multiply(offsetQ[defName]).normalize();
                        // defLocalQ = parentAnimWQ⁻¹ × desiredWorldQ
                        tmpQ.copy(parentAnimWQ).invert().multiply(desiredWorldQ).normalize();
                    } else {
                        tmpQ.copy(defRestLocalQ[defName] || new THREE.Quaternion());
                    }
                }

                const out = outputQuats[defName];
                out[ti] = tmpQ.x; out[ti+1] = tmpQ.y;
                out[ti+2] = tmpQ.z; out[ti+3] = tmpQ.w;
                defAnimWorldQ[defName] = parentAnimWQ.clone().multiply(tmpQ);
            } else {
                // Unmapped: rest local Q, propagate animated world Q
                defAnimWorldQ[defName] = parentAnimWQ.clone()
                    .multiply(defRestLocalQ[defName] || new THREE.Quaternion());
            }
        }
    }

    // --- Build output tracks ---
    const newTracks = [];
    for (const defName of mappedDefNames) {
        const bone = defSkel.boneByName[defName];
        newTracks.push(new THREE.QuaternionKeyframeTrack(
            `${bone.name}.quaternion`, times, outputQuats[defName]));
    }

    // Root position track
    const rootBvhName = bvhBones[0].name;
    let rootPosDef = mapping[rootBvhName];
    const rootPosTrack = bvhPosTracks[rootBvhName];
    // If BVH root maps to null (e.g. Bandai joint_Root), apply position to first mapped child
    if (!rootPosDef && rootPosTrack) {
        for (const child of bvhBones[0].children) {
            if (child.isBone && mapping[child.name]) {
                rootPosDef = mapping[child.name];
                break;
            }
        }
    }
    if (rootPosDef && rootPosTrack) {
        const defBone = defSkel.boneByName[rootPosDef];
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

    console.log(`[RETARGET] ${newTracks.length} tracks, ${fc} frames`);
    return new THREE.AnimationClip('retargeted', bvhClip.duration, newTracks);
}
