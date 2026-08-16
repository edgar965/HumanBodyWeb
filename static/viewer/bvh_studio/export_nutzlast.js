import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
/**
 * Nutzlast des Stoff-Exports zusammenstellen: Bilder abtasten, Lichter, Ton.
 *
 * Aus export1.js herausgeloest (Umbau 16.08.2026).
 */


export function _encodeFloat32(a) {
    const u8 = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
    let bin = '';
    const step = 32768;
    for (let i = 0; i < u8.length; i += step) {
        bin += String.fromCharCode.apply(null, u8.subarray(i, Math.min(i + step, u8.length)));
    }
    return btoa(bin);
}

export function _encodeUint32(a) { return _encodeFloat32(a); }

export function _pickAnimTrack() {
    // Animation tracks (type 'bvh') carry the actual Three.js mesh + skeleton.
    // Model tracks (type 'model') are meta-selectors pointing to a preset.
    const pick = (t) => t && t.type === 'bvh' && t.mesh?.skeleton && t.skeleton;
    const sel = state.project.tracks[state.selectedTrackIdx];
    if (pick(sel)) return sel;
    for (const t of state.project.tracks) {
        if (pick(t)) return t;
    }
    return null;
}

export function _dumpTracksForDebug() {
    const info = (state.project?.tracks || []).map((t, i) => ({
        i, type: t.type, name: t.name,
        hasMesh: !!t.mesh, hasSkel: !!t.skeleton,
        hasBVR: !!t.mesh?.userData?.boneVertexRanges,
        preset: t.preset, currentPreset: t._currentPreset,
        clips: (t.clips || []).length,
    }));
    console.table(info);
    return info;
}

export async function _ensureModelData(track) {
    // `track` is an animation track (type 'bvh'). The linked preset is held
    // on `track.preset` (set by loadTrackCharacter) OR on the linked
    // model track via `_currentPreset`.
    if (track.modelData) return track.modelData;
    let preset = track.preset;
    if (!preset && state.project.getLinkedModel) {
        const linked = state.project.getLinkedModel(track);
        preset = linked?._currentPreset;
    }
    if (!preset) throw new Error('Kein Preset auf der Animations-Spur gefunden. Ziehe ein Modell-Preset auf die Modell-Spur oben.');
    const resp = await fetch(`/api/character/model/${encodeURIComponent(preset)}/`);
    if (!resp.ok) throw new Error(`Modell-Preset "${preset}" nicht gefunden (HTTP ${resp.status}).`);
    const data = await resp.json();
    track.modelData = data;
    return data;
}

export function _activeAnimationClip(track) {
    // Prefer the clip under the current playhead; fall back to the first.
    const pf = state.playheadFrame || 0;
    for (const c of track.clips || []) {
        if (!c.animClip) continue;
        const end = (c.startFrame || 0) + (c.totalFrames || 0);
        if (pf >= (c.startFrame || 0) && pf < end) return c;
    }
    return (track.clips || []).find(c => c.animClip) || null;
}

export function _snapshotLights() {
    // Snapshot of all active light tracks at the current playhead.
    const lights = [];
    for (const t of state.project.tracks) {
        if (t.type !== 'light' || !t.light) continue;
        if (t.muted) continue;
        const L = t.light;
        const entry = { type: L.type || 'SpotLight', name: t.name || L.type };
        L.updateMatrixWorld(true);
        const pos = L.getWorldPosition(new THREE.Vector3());
        entry.position = [pos.x, pos.y, pos.z];
        entry.color = [L.color.r, L.color.g, L.color.b];
        entry.intensity = L.intensity || 1.0;
        if (L.target) {
            const tgt = L.target.getWorldPosition(new THREE.Vector3());
            entry.target = [tgt.x, tgt.y, tgt.z];
        }
        if (L.angle != null) entry.angle = L.angle;
        if (L.penumbra != null) entry.penumbra = L.penumbra;
        if (L.distance != null) entry.distance = L.distance;
        lights.push(entry);
    }
    return lights;
}

export function _collectAudio() {
    const audio = [];
    const fps = state.project.fps || 30;
    for (const t of state.project.tracks) {
        if (t.type !== 'audio' || t.muted) continue;
        for (const c of t.clips || []) {
            const url = c.audioUrl || c.url || c.src;
            if (!url) continue;
            audio.push({
                url, name: c.name || t.name,
                start_sec: (c.startFrame || 0) / fps,
                volume: c.volume != null ? c.volume : 1.0,
            });
        }
    }
    return audio;
}

export async function _sampleFrames(track, clip, duration, fps) {
    // Sample bones + camera + light state per-frame. Uses the user's playhead
    // system (fn.applyPlayhead) so that camera/light tracks contribute
    // naturally. Restores playhead state after sampling.
    const mesh = track.mesh;
    const skel = mesh.skeleton;
    const bones = skel.bones;
    const N = Math.max(1, Math.ceil(duration * fps));
    const boneMats = new Float32Array(N * bones.length * 16);
    const camMats = new Float32Array(N * 16);
    const camParams = new Float32Array(N * 2);  // fov, aspect per frame

    const origPlayhead = state.playheadFrame;
    const origPlaying = state.playing;
    state.playing = false;  // don't advance on animate()
    const projFps = state.project.fps || fps;
    // Map export frame → project frame (clip-relative)
    const baseFrame = clip.startFrame || 0;
    const ratio = projFps / fps;

    try {
        for (let f = 0; f < N; f++) {
            state.playheadFrame = Math.round(baseFrame + f * ratio);
            if (fn.applyPlayhead) fn.applyPlayhead();
            // Make sure transforms propagate (applyPlayhead should already, belt+suspenders)
            mesh.updateMatrixWorld(true);
            state.camera.updateMatrixWorld(true);
            for (let b = 0; b < bones.length; b++) {
                bones[b].updateMatrixWorld(true);
                bones[b].matrixWorld.toArray(boneMats, (f * bones.length + b) * 16);
            }
            state.camera.matrixWorld.toArray(camMats, f * 16);
            camParams[f * 2 + 0] = state.camera.fov || 45;
            camParams[f * 2 + 1] = state.camera.aspect || 1.777;
        }
    } finally {
        state.playheadFrame = origPlayhead;
        state.playing = origPlaying;
        if (fn.applyPlayhead) fn.applyPlayhead();
    }
    // Snapshot lights at the first sampled frame (user's scene lights live
    // after applyPlayhead). We use the post-restore scene which matches the
    // viewport; for per-frame light keyframes we'd sample inside the loop.
    const lights = _snapshotLights();
    return { matrices: boneMats, frameCount: N, camMats, camParams, lights };
}

export async function _buildPayload({ duration, fps }) {
    const track = _pickAnimTrack();
    if (!track) {
        _dumpTracksForDebug();
        throw new Error('Kein Animations-Track mit Mesh + Skelett. Im BVH Studio: Animations-Spur anlegen + BVH-Clip drauf, Modell-Spur mit Preset verbinden, abspielen, dann Export. (Track-Dump in Console)');
    }
    const clip = _activeAnimationClip(track);
    if (!clip || !clip.animClip) throw new Error('Kein animierter Clip gefunden. Zieh eine BVH-Animation (z.B. AIST/d01_mJS3_ch07) auf einen Animations-Track.');

    const modelData = await _ensureModelData(track);
    if (modelData.type !== 'generated_model') {
        throw new Error(`Modell "${track.preset}" ist kein generiertes Rig-Modell (type="${modelData.type}"). Cloth-Sim braucht ein Modell mit bone_parts (z.B. TriadischRock).`);
    }

    const mesh = track.mesh;
    const geo = mesh.geometry;
    const skel = mesh.skeleton;
    if (!mesh.userData?.boneVertexRanges) throw new Error('boneVertexRanges fehlen auf dem Mesh — Modell muss neu geladen werden (Studio neu starten oder Track entfernen + neu anlegen).');

    const positions = new Float32Array(geo.attributes.position.array);
    const faces = new Uint32Array(geo.index.array);
    const skinI = new Uint32Array(geo.attributes.skinIndex.array);
    const skinW = new Float32Array(geo.attributes.skinWeight.array);
    const boneNames = skel.bones.map(b => b.name);
    const invBind = new Float32Array(skel.boneInverses.length * 16);
    skel.boneInverses.forEach((m, i) => m.toArray(invBind, i * 16));

    const { matrices, frameCount, camMats, camParams, lights } =
        await _sampleFrames(track, clip, duration, fps);
    const audioClips = _collectAudio();

    return {
        scene_name: modelData.name || track.preset || track.name || 'studio_scene',
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
        bone_vertex_ranges: mesh.userData.boneVertexRanges,
        bone_parts: modelData.bone_parts || {},
        camera_matrices: _encodeFloat32(camMats),
        camera_params: _encodeFloat32(camParams),
        lights: lights,
        audio: audioClips,
    };
}
