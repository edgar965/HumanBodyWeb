/**
 * BVH retarget API client.
 *
 * Delegates all quaternion math to the Python backend
 * (/api/character/retarget-bvh/, /api/character/retarget-merge/).
 * This module handles BVH format detection, config caching,
 * and building Three.js AnimationClips from the API response.
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
 */
export async function loadRetargetConfig() {
    if (_retargetConfig) return _retargetConfig;
    const resp = await fetch('/api/character/retarget-config/');
    _retargetConfig = await resp.json();
    return _retargetConfig;
}

/**
 * Get the BVH->DEF mapping for the given format.
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

// =========================================================================
// URL parsing helper
// =========================================================================

/**
 * Extract category and name from a BVH URL.
 * Handles: /api/character/bvh/{category}/{name}/ and /api/character/retarget-bvh/{category}/{name}/
 */
function parseBvhUrl(url) {
    const m = url.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)\/?/);
    if (m) return { category: decodeURIComponent(m[1]), name: decodeURIComponent(m[2]) };
    return null;
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
        } else {
            console.warn('[RETARGET] position_track bone not found:', data.position_track.bone);
        }
    }

    console.log(`[RETARGET] buildClip: ${matched} matched, ${missed} missed, ${tracks.length} tracks, ${times.length} frames, duration=${data.duration}`);
    if (missedNames.length > 0) console.warn('[RETARGET] missed bones:', missedNames);

    return new THREE.AnimationClip('retargeted', data.duration, tracks);
}

// =========================================================================
// Public API — unified retarget (ONE function, ONE endpoint)
// =========================================================================

/**
 * Unified retarget: ONE function for both Job-BVH and Library-BVH.
 * Uses /api/retarget/?job=<id> or /api/retarget/?category=<cat>&name=<name>
 *
 * @param {Object} source - { jobId } OR { category, name } OR { bvhUrl }
 * @param {Object} rigifySkel - { rootBone, boneByName }
 * @param {Object} [opts] - { bodyHeight, footCorrection, format }
 * @returns {Promise<THREE.AnimationClip>}
 */
export async function fetchRetarget(source, rigifySkel, opts = {}) {
    const params = new URLSearchParams();
    if (source.jobId) {
        params.set('job', source.jobId);
    } else if (source.category && source.name) {
        params.set('category', source.category);
        params.set('name', source.name);
    } else if (source.bvhUrl) {
        const parsed = parseBvhUrl(source.bvhUrl);
        if (!parsed) throw new Error(`Cannot parse BVH URL: ${source.bvhUrl}`);
        params.set('category', parsed.category);
        params.set('name', parsed.name);
    } else {
        throw new Error('fetchRetarget: provide { jobId } or { category, name } or { bvhUrl }');
    }
    if (opts.bodyHeight) params.set('body_height', opts.bodyHeight);
    if (opts.footCorrection) params.set('foot_correction', '1');
    if (opts.deltaNorm !== undefined) params.set('delta_norm', opts.deltaNorm ? '1' : '0');
    if (opts.format) params.set('format', opts.format);

    const url = `/api/retarget/?${params}`;
    console.log(`[RETARGET] Fetching: ${url}`);
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Retarget API error: ${resp.status} ${resp.statusText}`);
    const data = await resp.json();
    console.log(`[RETARGET] ${data.mapped_bones?.length || 0} bones, ${data.frame_count} frames, ${data.duration?.toFixed(2)}s`);
    return buildClipFromRetargetData(data, rigifySkel);
}

// Legacy wrappers (for existing callers — will be removed)
export async function fetchRetargetedClip(bvhCategory, bvhName, rigifySkel, opts = {}) {
    return fetchRetarget({ category: bvhCategory, name: bvhName }, rigifySkel, opts);
}
export async function fetchRetargetedClipFromUrl(bvhUrl, rigifySkel, opts = {}) {
    return fetchRetarget({ bvhUrl }, rigifySkel, opts);
}
export async function fetchRetargetedClipForJob(jobId, rigifySkel, opts = {}) {
    return fetchRetarget({ jobId }, rigifySkel, opts);
}

/**
 * Server-side hybrid merge: retarget body + face BVHs and merge on the server.
 */
export async function fetchMergedClip(bodyBvhPath, faceBvhPath, rigifySkel, opts = {}) {
    const resp = await fetch('/api/character/retarget-merge/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            body_bvh: bodyBvhPath,
            face_bvh: faceBvhPath,
            body_height: opts.bodyHeight || 1.68,
            foot_correction: opts.footCorrection || false,
        }),
    });
    if (!resp.ok) throw new Error(`Merge API error: ${resp.status} ${resp.statusText}`);
    const data = await resp.json();
    return buildClipFromRetargetData(data, rigifySkel);
}

/**
 * Server-side retarget + merge for a hybrid pipeline job (body + face BVH).
 */
export async function fetchMergedClipForJob(jobId, rigifySkel, opts = {}) {
    const params = new URLSearchParams();
    if (opts.bodyHeight) params.set('body_height', opts.bodyHeight);
    if (opts.footCorrection) params.set('foot_correction', '1');
    if (opts.deltaNorm !== undefined) params.set('delta_norm', opts.deltaNorm ? '1' : '0');

    const url = `/api/character/retarget-job-merge/${jobId}/?${params}`;
    console.log(`[RETARGET] Fetching job merge: ${url}`);
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Job merge API error: ${resp.status} ${resp.statusText}`);
    const data = await resp.json();
    return buildClipFromRetargetData(data, rigifySkel);
}

// =========================================================================
// Raw BVH text retarget (for edited BVH content)
// =========================================================================

/**
 * Server-side retarget from raw BVH text content (e.g. after ground-fix editing).
 *
 * @param {string} bvhText - Raw BVH file content
 * @param {Object} rigifySkel - { rootBone, boneByName }
 * @param {Object} [opts] - { bodyHeight, footCorrection, format }
 * @returns {Promise<THREE.AnimationClip>}
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
