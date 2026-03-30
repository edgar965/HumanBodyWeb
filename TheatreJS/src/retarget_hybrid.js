/**
 * BVH retarget API client for Theatre.js.
 *
 * Delegates all quaternion math to the Python backend
 * (/api/character/retarget-bvh/).
 * This module handles BVH format detection and
 * building Three.js AnimationClips from the API response.
 */
import * as THREE from 'three';

// =========================================================================
// BVH format detection
// =========================================================================

export function detectBVHFormat(bones) {
    const names = new Set(bones.map(b => b.name));
    if (names.has('Pelvis') && names.has('Left_hip')) return 'AIST';
    if (names.has('Chest') && names.has('UpperArm_L')) return 'BANDAI';
    if (names.has('Hips') && names.has('LeftArm')) {
        return names.has('Spine2') ? 'MIXAMO' : 'CMU';
    }
    if (names.has('hip') && names.has('rShldr')) return 'OPENPOSE';
    if (names.has('hip') || names.has('rshoulder')) return 'MOCAPNET';
    return 'UNKNOWN';
}

// =========================================================================
// AnimationClip builder
// =========================================================================

/**
 * Build Three.js AnimationClip from Python retarget JSON response.
 * Python SkeletonGeometry already works in Three.js coordinate space,
 * so no coordinate conversion is needed here.
 */
function buildClipFromRetargetData(data, rigifySkel) {
    const times = new Float32Array(data.times);
    const tracks = [];
    let matched = 0, missed = 0;
    const missedNames = [];

    for (const [boneName, values] of Object.entries(data.tracks)) {
        const bone = rigifySkel.boneByName[boneName];
        if (!bone) { missed++; missedNames.push(boneName); continue; }
        matched++;
        tracks.push(new THREE.QuaternionKeyframeTrack(
            `${bone.name}.quaternion`, times, new Float32Array(values)));
    }

    if (data.position_track) {
        const bone = rigifySkel.boneByName[data.position_track.bone];
        if (bone) {
            tracks.push(new THREE.VectorKeyframeTrack(
                `${bone.name}.position`, times, new Float32Array(data.position_track.values)));
        }
    }

    console.log(`[RETARGET] buildClip: ${matched} matched, ${missed} missed, ${tracks.length} tracks, ${times.length} frames`);
    return new THREE.AnimationClip('retargeted', data.duration, tracks);
}

// =========================================================================
// Public API — server-side retarget
// =========================================================================

/**
 * Server-side retarget by category/name.
 */
export async function fetchRetargetedClip(bvhCategory, bvhName, rigifySkel, opts = {}) {
    const params = new URLSearchParams();
    if (opts.bodyHeight) params.set('body_height', opts.bodyHeight);
    if (opts.footCorrection) params.set('foot_correction', '1');
    if (opts.format) params.set('format', opts.format);

    const url = `/api/character/retarget-bvh/${encodeURIComponent(bvhCategory)}/${encodeURIComponent(bvhName)}/?${params}`;
    console.log(`[RETARGET] Fetching: ${url}`);
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Retarget API error: ${resp.status} ${resp.statusText}`);
    const data = await resp.json();
    return buildClipFromRetargetData(data, rigifySkel);
}

/**
 * Server-side retarget from raw BVH text.
 */
export async function fetchRetargetedClipFromText(bvhText, rigifySkel, opts = {}) {
    const resp = await fetch('/api/character/retarget-bvh-text/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            bvh_text: bvhText,
            body_height: opts.bodyHeight || 1.68,
            foot_correction: opts.footCorrection || false,
            format: opts.format || null,
        }),
    });
    if (!resp.ok) throw new Error(`Text retarget API error: ${resp.status} ${resp.statusText}`);
    const data = await resp.json();
    return buildClipFromRetargetData(data, rigifySkel);
}
