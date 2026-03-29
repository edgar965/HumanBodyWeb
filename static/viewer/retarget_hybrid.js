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
    // OpenPose: hip + rShldr (capitalized, distinct from MocapNET's rshoulder)
    if (names.has('hip') && names.has('rShldr')) return 'OPENPOSE';
    if (names.has('hip') || names.has('rshoulder')) return 'MOCAPNET';
    return 'UNKNOWN';
}

// =========================================================================
// API config loader — single source of truth for mapping data
// =========================================================================

let _retargetConfig = null;

/**
 * Load retarget configuration (mappings, skip lists, face/hand bones) from
 * the Python backend.  Returns cached data on subsequent calls.
 * Must be called before retargetBVHToDefClip / mergeRetargetedClips.
 */
export async function loadRetargetConfig() {
    if (_retargetConfig) return _retargetConfig;
    const resp = await fetch('/api/character/retarget-config/');
    _retargetConfig = await resp.json();
    return _retargetConfig;
}

/**
 * Get the BVH→DEF mapping for the given format.
 * Requires loadRetargetConfig() to have been called first.
 */
export function getMappingForFormat(format) {
    if (!_retargetConfig) throw new Error('loadRetargetConfig() must be called before getMappingForFormat()');
    return _retargetConfig.mappings[format] || _retargetConfig.mappings['MOCAPNET'];
}

/**
 * Get the skip-dir-correction list for the given format.
 */
export function getSkipDirCorrection(format) {
    if (!_retargetConfig) return [];
    return _retargetConfig.skip_dir_correction[format] || [];
}

/**
 * Get the face/hand bone set (Three.js underscore names).
 */
export function getFaceHandBones() {
    if (!_retargetConfig) return new Set();
    return new Set(_retargetConfig.face_hand_bones);
}

// Mapping tables removed — canonical data served by /api/character/retarget-config/
// Use loadRetargetConfig() + getMappingForFormat(format) instead.


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
 * @param {Object} [opts] - { bodyMesh, footCorrection, skipDefBones }
 * @returns {THREE.AnimationClip}
 */
export function retargetBVHToDefClip(bvhResult, defSkel, format, opts = {}) {
    const bvhBones = bvhResult.skeleton.bones;
    const bvhClip = bvhResult.clip;
    const mapping = getMappingForFormat(format);

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
    const defToBvhName = {};
    for (const [bvhName, defName] of Object.entries(mapping)) {
        if (defName && bvhBoneByName[bvhName] && defSkel.boneByName[defName])
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

    // --- Compute frame-0 BVH world Qs for delta retarget ---
    // Delta retarget subtracts frame-0 world Q to start from rest pose.
    // Required for Bandai (standing pose in frame-0) AND AIST/GVHMR (some BVH files
    // have non-identity frame-0 rotations despite normalization). Delta retarget is
    // safe for identity frame-0 too (delta = identity → no change).
    const bvhRestWorldQ = {};
    const useDeltaRetarget = (format === 'BANDAI');
    const useDeltaDirCorrection = (format === 'BANDAI');
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
    // Standard (CMU/Mixamo/MocapNET/AIST): BVH rest is identity, use local offsets.
    // Delta dir correction (Bandai only): use frame-0 WORLD directions (local offsets
    // rotated by frame-0 world Q) since frame-0 has non-identity standing pose.
    const _NEG_Z = new THREE.Vector3(0, 0, -1);
    const offsetQ = {};

    // Identify root DEF bone (no mapped parent → skip direction correction)
    const rootDefName = Object.values(mapping).find(d => d && defSkel.boneByName[d]);

    // Bones where direction correction should be skipped (loaded from API).
    const skipDirCorrectionBones = new Set(getSkipDirCorrection(format));

    // Sort mapped DEF bones by hierarchy depth (parents first) so that
    // direction corrections can be propagated down to skip bones.
    const mappedDefSorted = Object.keys(defToBvhName).sort((a, b) => {
        let da = 0, ca = defSkel.boneByName[a];
        while (ca && ca.parent) { da++; ca = ca.parent; }
        let db = 0, cb = defSkel.boneByName[b];
        while (cb && cb.parent) { db++; cb = cb.parent; }
        return da - db;
    });

    // Track dirCorr per mapped bone for propagation to skip bones.
    // When a parent has direction correction but a child skips it, the
    // parent's corrected world Q no longer matches defWorldRestQ. Without
    // propagation, the mismatch "leaks" as an extra rotation into the
    // child's local Q (causing e.g. ape-like forward head tilt).
    const dirCorrMap = {};

    for (const defName of mappedDefSorted) {
        const bvhName = defToBvhName[defName];

        // Find nearest mapped ancestor's dirCorr
        let inheritedDirCorr = new THREE.Quaternion(); // identity
        let pBone = defSkel.boneByName[defName]?.parent;
        while (pBone) {
            const pName = origNameByBone.get(pBone);
            if (pName && dirCorrMap[pName] !== undefined) {
                inheritedDirCorr = dirCorrMap[pName].clone();
                break;
            }
            pBone = pBone.parent;
        }

        // Skip direction correction for root bone — root has multiple children
        // with divergent directions, causing erroneous correction
        if (defName === rootDefName || skipDirCorrectionBones.has(defName)) {
            dirCorrMap[defName] = inheritedDirCorr.clone();
            // Propagate parent's dirCorr so that the corrected→skipped
            // boundary stays consistent at rest pose
            offsetQ[defName] = inheritedDirCorr.clone().multiply(defWorldRestQ[defName]);
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
                if (useDeltaDirCorrection && bvhRestWorldQ[bvhName]) {
                    // Bandai: rotate local offset by frame-0 world Q
                    // to get the actual world-space direction at frame 0
                    dir = child.position.clone()
                        .applyQuaternion(bvhRestWorldQ[bvhName]).normalize();
                } else {
                    // Standard/AIST: BVH rest is identity, local = world
                    dir = child.position.clone().normalize();
                }
                const dot = dir.dot(defRestDir);
                if (dot > bestDot) { bestDot = dot; bvhDir = dir; }
            }
        }
        // Fallback to own position offset
        if (!bvhDir && bvhBone.position.lengthSq() > 1e-10) {
            if (useDeltaDirCorrection) {
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
            dirCorrMap[defName] = new THREE.Quaternion(); // identity
            offsetQ[defName] = defWorldRestQ[defName].clone();
        } else {
            const dirCorr = new THREE.Quaternion().setFromUnitVectors(defRestDir, bvhDir);
            dirCorrMap[defName] = dirCorr.clone();
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

    // --- Foot correction pre-pass ---
    // Detects plantar flexion from the BVH foot bone's world orientation per frame.
    // If the foot already points downward (> threshold), amplify toward en pointe.
    // Stores per-frame slerp amount toward the "foot straight down" target.
    let footCorrection = null;
    if (opts.footCorrection) {
        footCorrection = {};
        const _fq2 = new THREE.Quaternion();
        const _fwd = new THREE.Vector3();
        const DEG = 180 / Math.PI;

        // Only enhance when foot is already pitched down by > threshold
        const THRESHOLD_DEG = 15;
        // Additive boost: targetAngle = downAngle + (downAngle - threshold) × BOOST
        const BOOST = 1.5;

        for (const defFootName of ['DEF-foot.L', 'DEF-foot.R']) {
            const bvhFootName = defToBvhName[defFootName];
            if (!bvhFootName) continue;

            // FK chain to compute foot bone's world Q per frame
            const chain = [];
            let cur = bvhFootName;
            while (cur) { chain.unshift(cur); cur = bvhBoneParentName[cur]; }

            const correction = new Float32Array(fc);
            let maxCorr = 0, maxAngle = 0;
            for (let f = 0; f < fc; f++) {
                const ti = f * 4;
                let worldQ = new THREE.Quaternion();
                for (const bn of chain) {
                    const track = bvhQuatTracks[bn];
                    if (track) {
                        _fq2.set(track.values[ti], track.values[ti+1],
                                 track.values[ti+2], track.values[ti+3]);
                    } else { _fq2.set(0, 0, 0, 1); }
                    worldQ.multiply(_fq2);
                }

                // Foot forward direction in world space (bone -Z)
                _fwd.set(0, 0, -1).applyQuaternion(worldQ);
                // Angle below horizontal: positive = points down
                const downAngle = Math.asin(Math.max(-1, Math.min(1, -_fwd.y))) * DEG;
                if (downAngle > maxAngle) maxAngle = downAngle;

                if (downAngle > THRESHOLD_DEG) {
                    // Target angle: amplify beyond current
                    const targetAngle = Math.min(90, downAngle + (downAngle - THRESHOLD_DEG) * BOOST);
                    // Slerp amount: how far from current toward 90° do we need to go?
                    // (targetAngle - downAngle) is the extra rotation needed.
                    // (90 - downAngle) is the full distance to 90°.
                    const distTo90 = 90 - downAngle;
                    correction[f] = distTo90 > 0.1
                        ? Math.min((targetAngle - downAngle) / distTo90, 1.0)
                        : 0;  // already at ~90°, no correction needed
                }
                if (correction[f] > maxCorr) maxCorr = correction[f];
            }
            footCorrection[defFootName] = correction;
            console.log(`[FOOT-CORRECTION] ${defFootName}: maxAngle=${maxAngle.toFixed(1)}, ` +
                `thresh=${THRESHOLD_DEG}, boost=${BOOST}x, maxCorr=${maxCorr.toFixed(2)}`);
        }
        if (Object.keys(footCorrection).length === 0) footCorrection = null;
    }

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
                    // Delta retarget: desiredWorldQ = (bvhWAQ × bvhRWQ⁻¹) × offsetQ
                    // Subtracts frame-0 world Q to get relative motion from initial pose.
                    // At frame 0: delta=identity → desiredWorldQ = offsetQ (rest pose)
                    // At frame N: delta rotates from frame-0 to frame-N applied to DEF rest
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

                // Foot correction: slerp toward "foot pointing straight down"
                // Uses setFromUnitVectors to naturally rotate from current foot
                // direction to -Y, preserving lateral orientation (no twist).
                if (footCorrection && footCorrection[defName]) {
                    const amount = footCorrection[defName][f];
                    if (amount > 0.01) {
                        // Current foot world Q
                        const footWorldQ = parentAnimWQ.clone().multiply(tmpQ);
                        // Current foot forward in world space
                        const curFwd = new THREE.Vector3(0, 0, -1).applyQuaternion(footWorldQ).normalize();
                        // Target: foot points straight down
                        const tgtFwd = new THREE.Vector3(0, -1, 0);
                        // Rotation from current forward to target forward
                        const rotQ = new THREE.Quaternion().setFromUnitVectors(curFwd, tgtFwd);
                        // Target world Q = rotation applied to current
                        const tgtWorldQ = rotQ.multiply(footWorldQ);
                        // Convert to local
                        const tgtLocalQ = parentAnimWQ.clone().invert().multiply(tgtWorldQ).normalize();
                        tmpQ.slerp(tgtLocalQ, amount);
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


// =========================================================================
// Hybrid merge: combine body clip + face/hands clip
// =========================================================================

// FACE_HAND_BONES loaded from API via getFaceHandBones()

/**
 * Merge two retargeted AnimationClips on the DEF skeleton.
 * Body bones come from bodyClip, face+hand bones from faceHandClip.
 *
 * Both clips must already be retargeted to DEF skeleton (via retargetBVHToDefClip).
 *
 * @param {THREE.AnimationClip} bodyClip - Retargeted SMPL body clip (AIST format)
 * @param {THREE.AnimationClip} faceHandClip - Retargeted MocapNET v4 clip (MOCAPNET format)
 * @returns {THREE.AnimationClip} Merged clip
 */
export function mergeRetargetedClips(bodyClip, faceHandClip) {
    const faceHandBones = getFaceHandBones();

    // Index tracks by bone name (track name format: "DEF-spine_006.quaternion")
    const bodyMap = new Map();
    for (const t of bodyClip.tracks) {
        const boneName = t.name.split('.')[0];  // "DEF-spine_006"
        bodyMap.set(boneName + '.' + t.name.split('.').slice(1).join('.'), t);
    }
    const faceMap = new Map();
    for (const t of faceHandClip.tracks) {
        const boneName = t.name.split('.')[0];
        faceMap.set(boneName + '.' + t.name.split('.').slice(1).join('.'), t);
    }

    const merged = [];

    // Body tracks: everything NOT in FACE_HAND_BONES
    for (const [key, track] of bodyMap) {
        const boneName = key.split('.')[0];
        if (!faceHandBones.has(boneName)) {
            merged.push(track);
        }
    }

    // Face+Hand tracks: everything IN FACE_HAND_BONES
    for (const [key, track] of faceMap) {
        const boneName = key.split('.')[0];
        if (faceHandBones.has(boneName)) {
            merged.push(track);
        }
    }

    // Use shorter duration to keep them in sync
    const duration = Math.min(bodyClip.duration, faceHandClip.duration);
    if (Math.abs(bodyClip.duration - faceHandClip.duration) > 0.5) {
        console.warn(`[HYBRID] Frame mismatch: body=${bodyClip.duration.toFixed(1)}s, face=${faceHandClip.duration.toFixed(1)}s — using ${duration.toFixed(1)}s`);
    }

    console.log(`[HYBRID] Merged: ${merged.length} tracks (body: ${bodyMap.size}, face+hands: ${faceMap.size})`);
    return new THREE.AnimationClip('hybrid', duration, merged);
}
