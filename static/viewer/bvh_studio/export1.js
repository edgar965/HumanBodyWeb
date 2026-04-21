/**
 * BVH Studio — Export1 tab: cloth-simulation MP4 export via the 3 engines.
 *
 * Gathers the currently visible Modell track's mesh + skeleton + cached
 * modelData, samples the active animation per-frame, and POSTs everything
 * to /api/cloth/export/. No popup, no Scene page.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';


function _setStatus(text, color) {
    const box = document.getElementById('cloth-export-status');
    const el = document.getElementById('cloth-export-status-text');
    if (!box || !el) return;
    box.style.display = text ? 'block' : 'none';
    el.textContent = text || '';
    el.style.color = color || 'var(--text-muted)';
}

function _setButtonsEnabled(enabled) {
    document.querySelectorAll('.cloth-export-btn').forEach(b => {
        b.disabled = !enabled;
        b.style.opacity = enabled ? '1' : '0.5';
        b.style.cursor = enabled ? 'pointer' : 'wait';
    });
}

function _progress(engine, pct, text, color) {
    const bar = document.querySelector(`.cloth-progress[data-engine="${engine}"]`);
    if (!bar) return;
    if (pct === null) { bar.style.display = 'none'; return; }
    bar.style.display = 'block';
    const fill = bar.querySelector('.cloth-progress-fill');
    const label = bar.querySelector('.cloth-progress-text');
    if (fill) fill.style.width = Math.max(0, Math.min(100, pct)) + '%';
    if (label) {
        label.textContent = text || '';
        if (color) label.style.color = color;
    }
}

// Monotonic ramp, 25% → 95%, labelled with elapsed seconds.
// Per-engine singleton: starting a new one stops the previous.
const _progressTimers = {};
function _startProgress(engine, expectedSeconds = 30, label = 'Sim + Render läuft') {
    if (_progressTimers[engine]) {
        clearInterval(_progressTimers[engine].t);
        _progressTimers[engine] = null;
    }
    const t0 = performance.now();
    let lastPct = 25;
    const tick = () => {
        const elapsed = (performance.now() - t0) / 1000;
        let target;
        if (elapsed < expectedSeconds) target = 25 + (elapsed / expectedSeconds) * 60;
        else target = 85 + Math.min(10, ((elapsed - expectedSeconds) / expectedSeconds) * 10);
        // Strict monotonic: never decrease
        lastPct = Math.max(lastPct, target);
        _progress(engine, lastPct, `${label} — ${elapsed.toFixed(0)}s`);
    };
    tick();
    const t = setInterval(tick, 500);
    _progressTimers[engine] = { t };
    return () => {
        if (_progressTimers[engine]) { clearInterval(_progressTimers[engine].t); _progressTimers[engine] = null; }
    };
}

function _encodeFloat32(a) {
    const u8 = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
    let bin = '';
    const step = 32768;
    for (let i = 0; i < u8.length; i += step) {
        bin += String.fromCharCode.apply(null, u8.subarray(i, Math.min(i + step, u8.length)));
    }
    return btoa(bin);
}
function _encodeUint32(a) { return _encodeFloat32(a); }

function _pickAnimTrack() {
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

function _dumpTracksForDebug() {
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

async function _ensureModelData(track) {
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

function _activeAnimationClip(track) {
    // Prefer the clip under the current playhead; fall back to the first.
    const pf = state.playheadFrame || 0;
    for (const c of track.clips || []) {
        if (!c.animClip) continue;
        const end = (c.startFrame || 0) + (c.totalFrames || 0);
        if (pf >= (c.startFrame || 0) && pf < end) return c;
    }
    return (track.clips || []).find(c => c.animClip) || null;
}

function _snapshotLights() {
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

function _collectAudio() {
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

async function _sampleFrames(track, clip, duration, fps) {
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

async function _buildPayload({ duration, fps }) {
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

async function _runClothExport(engine) {
    const duration = parseFloat(document.getElementById('cloth-duration')?.value || '3.0');
    const fps = parseInt(document.getElementById('cloth-fps')?.value || '30');
    const qualityIdMap = {
        'blender_eevee': 'cloth-quality-blender-eevee',
        'warp_blender':  'cloth-quality-warp-blender',
        'warp_only':     'cloth-quality-warp-only',
    };
    const quality = document.getElementById(qualityIdMap[engine])?.value || 'medium';
    const resolutionHeight = parseInt(document.getElementById('cloth-resolution')?.value || '1080');
    const resolutionMap = {720: [1280, 720], 1080: [1920, 1080], 1440: [2560, 1440], 2160: [3840, 2160]};
    const [width, height] = resolutionMap[resolutionHeight] || [1920, 1080];
    const outputDir = (document.getElementById('cloth-target-dir')?.value || '').trim();
    let filename = (document.getElementById('cloth-filename')?.value || '').trim() || 'cloth_export.mp4';
    if (!filename.toLowerCase().endsWith('.mp4')) filename += '.mp4';

    _setButtonsEnabled(false);
    _progress(engine, 5, 'Daten aus BVH Studio sammeln…');
    _setStatus(`Daten sammeln für ${engine}…`, 'var(--accent)');

    let payload;
    try {
        payload = await _buildPayload({ duration, fps });
    } catch (e) {
        _progress(engine, 100, `Fehler: ${e.message}`, '#e74c3c');
        _setStatus(`Fehler: ${e.message}`, '#e74c3c');
        _setButtonsEnabled(true);
        setTimeout(() => _progress(engine, null), 6000);
        return;
    }
    payload.engine = engine;
    payload.quality = quality;
    payload.width = width;
    payload.height = height;
    if (outputDir) payload.output_dir = outputDir;
    if (filename) payload.filename = filename;

    _progress(engine, 25, `POST ${payload.anim_frames} Frames → Server`);
    _setStatus(`Läuft: ${engine}, ${payload.anim_frames} Frames…`, 'var(--accent)');

    const expectedSec = { blender_eevee: 60, warp_blender: 30, warp_only: 20 }[engine] || 30;
    const stopPulse = _startProgress(engine, expectedSec, `${engine}: Sim + Render`);
    const t0 = performance.now();
    try {
        const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
        const resp = await fetch('/api/cloth/export/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
            body: JSON.stringify(payload),
        });
        stopPulse();
        const data = await resp.json();
        const elapsed = ((performance.now() - t0) / 1000).toFixed(1);
        if (data.ok) {
            const t = Math.round(data.elapsed_sec || elapsed);
            const href = data.url || data.output || '';
            _progress(engine, 100, `✓ ${t}s → ${href.split(/[/\\]/).pop()}`, '#4caf50');
            _setStatus(`✓ Fertig in ${t}s → ${href}`, '#4caf50');
            if (href) window.open(href, '_blank');
        } else {
            console.error('[Cloth Export] failed:', data);
            _progress(engine, 100, `Fehler — siehe Console`, '#e74c3c');
            _setStatus(`Fehler: ${data.error || 'siehe Console'} (log: ${(data.log || '').slice(-200)})`, '#e74c3c');
        }
    } catch (e) {
        stopPulse();
        _progress(engine, 100, `Netzwerkfehler: ${e.message}`, '#e74c3c');
        _setStatus(`Netzwerkfehler: ${e.message}`, '#e74c3c');
    } finally {
        _setButtonsEnabled(true);
        setTimeout(() => _progress(engine, null), 15000);
    }
}

async function _autofillTargetDir() {
    const el = document.getElementById('cloth-target-dir');
    if (!el || el.value) return;
    try {
        const r = await fetch('/api/ui-prefs/');
        const prefs = await r.json();
        el.value = prefs.studio_video_output || '';
    } catch (e) { /* ignore */ }
}

export function bindClothExportButtons() {
    _autofillTargetDir();
    document.querySelectorAll('.props-tab').forEach(tab => {
        if (tab.dataset.tab === 'export1') tab.addEventListener('click', _autofillTargetDir);
    });
    document.querySelectorAll('.cloth-export-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const engine = btn.dataset.engine;
            if (!engine) return;
            console.log(`[Cloth Export] click engine=${engine}`);
            _runClothExport(engine);
        });
    });
    console.log('[Cloth Export] bound ' + document.querySelectorAll('.cloth-export-btn').length + ' buttons');
}
