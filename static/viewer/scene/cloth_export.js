/**
 * Cloth-Export Bridge.
 * Serializes the current generated-model scene + its active animation
 * into a binary payload, POSTs it to the cloth-export API, polls for the
 * rendered MP4, and triggers a download.
 *
 * Usage from console / button:
 *   fn.exportClothMP4({ engine: 'warp_only', quality: 'medium', duration: 3.0 })
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';

function _encodeFloat32(a) {
    const u8 = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
    let bin = '';
    const step = 32768;
    for (let i = 0; i < u8.length; i += step) {
        bin += String.fromCharCode.apply(null, u8.subarray(i, Math.min(i + step, u8.length)));
    }
    return btoa(bin);
}
function _encodeUint32(a) {
    const u8 = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
    let bin = '';
    const step = 32768;
    for (let i = 0; i < u8.length; i += step) {
        bin += String.fromCharCode.apply(null, u8.subarray(i, Math.min(i + step, u8.length)));
    }
    return btoa(bin);
}

function _selectedInstWithGenerated() {
    const inst = state.characters.get(state.selectedCharacterId);
    if (!inst) throw new Error('Kein Charakter ausgewählt.');
    if (!inst.generatedConfig) throw new Error('Charakter ist kein generiertes Rig-Modell.');
    if (!inst.bodyMesh || !inst.bodyMesh.skeleton) throw new Error('bodyMesh ohne Skeleton.');
    const ud = inst.bodyMesh.userData || {};
    if (!ud.boneVertexRanges) throw new Error('boneVertexRanges fehlen (Modell muss regeneriert werden).');
    return inst;
}

/**
 * Sample per-frame bone world matrices while the mixer plays.
 * Returns Float32Array(N * numBones * 16), row-major.
 */
async function _sampleBoneMatrices(inst, duration, fps) {
    const mesh = inst.bodyMesh;
    const skel = mesh.skeleton;
    const bones = skel.bones;
    const N = Math.max(1, Math.ceil(duration * fps));
    const out = new Float32Array(N * bones.length * 16);

    if (!state.mixer || !state.currentAction) {
        // No active animation — emit identity matrix per frame
        const id = new THREE.Matrix4().identity();
        for (let f = 0; f < N; f++) for (let b = 0; b < bones.length; b++) {
            id.toArray(out, (f * bones.length + b) * 16);
        }
        return { matrices: out, frameCount: N };
    }

    const wasPlaying = !!state.playing;
    const origTime = state.currentAction.time;
    const clip = state.currentAction.getClip();
    const dt = 1 / fps;

    state.currentAction.play();
    state.currentAction.paused = true;

    for (let f = 0; f < N; f++) {
        const t = Math.min(f * dt, clip.duration);
        state.currentAction.time = t;
        state.mixer.update(0);
        mesh.updateMatrixWorld(true);
        for (let b = 0; b < bones.length; b++) {
            bones[b].updateMatrixWorld(true);
            bones[b].matrixWorld.toArray(out, (f * bones.length + b) * 16);
        }
    }
    // restore
    state.currentAction.time = origTime;
    state.currentAction.paused = !wasPlaying;
    state.mixer.update(0);
    return { matrices: out, frameCount: N };
}

/**
 * Build the payload the server expects for POST /api/cloth/export/.
 */
export async function buildClothPayload({ duration = 3.0, fps = 30 } = {}) {
    const inst = _selectedInstWithGenerated();
    const mesh = inst.bodyMesh;
    const geo = mesh.geometry;
    const skel = mesh.skeleton;
    const positions = new Float32Array(geo.attributes.position.array);
    const faces = new Uint32Array(geo.index.array);
    const skinI = new Uint32Array(geo.attributes.skinIndex.array); // Three.js stores uint16 but we promote
    const skinW = new Float32Array(geo.attributes.skinWeight.array);
    const boneNames = skel.bones.map(b => b.name);
    // Inverse bind: skel.boneInverses (Matrix4[]), concat into Float32Array(num_bones * 16)
    const invBind = new Float32Array(skel.boneInverses.length * 16);
    skel.boneInverses.forEach((m, i) => m.toArray(invBind, i * 16));

    const { matrices, frameCount } = await _sampleBoneMatrices(inst, duration, fps);

    const ranges = mesh.userData.boneVertexRanges;  // bone_name -> {start, count}
    const bone_parts = inst.generatedConfig.bone_parts || {};

    return {
        scene_name: inst.presetName || 'scene',
        positions: _encodeFloat32(positions),
        vertex_count: positions.length / 3,
        faces: _encodeUint32(faces),
        face_count: faces.length / 3,
        skin_indices: _encodeUint32(skinI),
        skin_weights: _encodeFloat32(skinW),
        bone_names: boneNames,
        inv_bind: _encodeFloat32(invBind),
        anim_matrices: _encodeFloat32(matrices),
        anim_fps: fps,
        anim_frames: frameCount,
        bone_vertex_ranges: ranges,
        bone_parts: bone_parts,
    };
}

/**
 * Export the selected character with the active animation as MP4 via the
 * chosen cloth engine. Returns the download URL.
 */
export async function exportClothMP4({ engine = 'warp_only', quality = 'medium', duration = 3.0, fps = 30, outputDir = '', filename = '', width = 1920, height = 1080 } = {}) {
    const payload = await buildClothPayload({ duration, fps });
    payload.engine = engine;
    payload.quality = quality;
    payload.width = width;
    payload.height = height;
    if (outputDir) payload.output_dir = outputDir;
    if (filename) payload.filename = filename;
    console.log(`[Cloth Export] engine=${engine} quality=${quality} res=${width}x${height} frames=${payload.anim_frames} dir=${outputDir||'(default)'} file=${filename||'(auto)'}`);
    const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    const resp = await fetch('/api/cloth/export/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok || !data.ok) {
        console.error('[Cloth Export] failed', data);
        throw new Error(data.error || data.log || 'Export fehlgeschlagen');
    }
    console.log('[Cloth Export] MP4:', data.url);
    if (data.url) window.open(data.url, '_blank');
    return data;
}

fn.buildClothPayload = buildClothPayload;
fn.exportClothMP4 = exportClothMP4;
window.__exportClothMP4 = exportClothMP4;
