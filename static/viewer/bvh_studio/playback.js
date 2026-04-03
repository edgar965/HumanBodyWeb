/**
 * BVH Studio — Playback controls, audio, apply playhead to tracks.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

export function setupPlayback() {
    document.getElementById('pb-play')?.addEventListener('click', togglePlay);
    document.getElementById('pb-stop')?.addEventListener('click', stopPlayback);
    document.getElementById('pb-prev')?.addEventListener('click', () => stepFrame(-1));
    document.getElementById('pb-next')?.addEventListener('click', () => stepFrame(1));
    document.getElementById('pb-speed')?.addEventListener('change', (e) => {
        state.playbackSpeed = parseFloat(e.target.value);
    });

    // Ctrl shortcuts registered globally at module top level (index.js)
    // Other keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        const inInput = (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT');
        if (inInput) return;
        if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
        if (e.code === 'ArrowLeft') { e.preventDefault(); stepFrame(-1); }
        if (e.code === 'ArrowRight') { e.preventDefault(); stepFrame(1); }
        if (e.code === 'Delete' || e.code === 'Backspace') {
            e.preventDefault();
            // Timeline clip has priority over library selection
            if (state.selectedClipIdx >= 0) fn.deleteSelectedClip();
            else if (document.querySelector('.lib-item.selected')) fn.deleteSelectedLibItem();
        }
        if (e.code === 'KeyS' && !e.ctrlKey) {
            e.preventDefault();
            fn.splitClipAtPlayhead();
        }
        if (e.code === 'KeyK') {
            e.preventDefault();
            if (state.selectedTrackIdx >= 0) {
                const t = state.project.tracks[state.selectedTrackIdx];
                if (t.type === 'camera') fn.addCameraKeyframe(state.selectedTrackIdx);
                else if (t.type === 'light') fn.addLightKeyframe(state.selectedTrackIdx);
            }
        }
        // Ctrl shortcuts handled in capture-phase handler above
        if (e.key === 'F2') {
            e.preventDefault();
            const sel = document.querySelector('.lib-item.selected');
            if (sel) fn.renameSelectedLibItem();
        }
        if (e.code === 'KeyA' && !e.ctrlKey) {
            e.preventDefault();
            const sel = document.querySelector('.lib-item.selected');
            if (sel) fn.previewAnimation(sel.dataset.category, sel.dataset.name);
        }
        if (e.code === 'KeyQ') {
            e.preventDefault();
            fn.closePreview();
        }
    });
}

export function togglePlay() {
    state.playing = !state.playing;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = state.playing ? 'fas fa-pause' : 'fas fa-play';
    if (state.playing) {
        startAudioPlayback();
    } else {
        stopAllAudio();
        state.controls.enabled = true;  // re-enable OrbitControls when pausing camera playback
    }
}

export function stopPlayback() {
    state.playing = false;
    state.playheadFrame = 0;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = 'fas fa-play';
    stopAllAudio();
    state.controls.enabled = true;  // re-enable OrbitControls
    applyPlayhead();
    fn.renderTimeline();
    updatePlaybackUI();
}

export function stepFrame(delta) {
    state.playheadFrame = Math.max(0, state.playheadFrame + delta);
    applyPlayhead();
    fn.renderTimeline();
    updatePlaybackUI();
}

export function applyPlayhead() {
    const t = state.playheadFrame / state.project.fps;
    for (const track of state.project.tracks) {
        if (track.muted) continue;
        if (track.type === 'bvh') applyBvhTrack(track, t);
        else if (track.type === 'camera') applyCameraTrack(track, t);
        else if (track.type === 'light') applyLightTrack(track, t);
        else if (track.type === 'audio') applyAudioTrack(track, t);
    }
}

let _applyBvhLog = 0;
function applyBvhTrack(track, t) {
    if (!track.mixer) { if (_applyBvhLog++ < 3) console.warn('[applyBvh] no mixer'); return; }
    let found = false;
    for (const clip of track.clips) {
        if (!clip.animClip) { if (_applyBvhLog++ < 3) console.warn(`[applyBvh] clip ${clip.name} has no animClip`); continue; }
        const clipStart = clip.startFrame / state.project.fps;
        const clipEnd = clipStart + clip.duration;
        if (t >= clipStart && t < clipEnd) {
            const localT = (t - clipStart) * clip.speed + clip.trimIn / clip.fps;
            if (track._activeClip !== clip) {
                track.mixer.stopAllAction();
                if (track._activeClip?.animClip) track.mixer.uncacheClip(track._activeClip.animClip);
                track._activeAction = track.mixer.clipAction(clip.animClip);
                track._activeAction.setLoop(THREE.LoopOnce);
                track._activeAction.clampWhenFinished = true;
                track._activeAction.play();
                track._activeClip = clip;
            }
            track._activeAction.time = localT;
            track.mixer.setTime(localT);
            found = true;
            break;
        }
    }
    if (!found && track._activeClip) {
        track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
        if (track.skeleton) track.skeleton.skeleton.pose();
    }
}

function applyCameraTrack(track, t) {
    if (!track.cameraActive || !state.playing || track.clips.length === 0) return;
    const frame = state.playheadFrame;
    const kfs = track.clips;
    // Find surrounding keyframes
    let prev = null, next = null;
    for (let i = 0; i < kfs.length; i++) {
        if (kfs[i].startFrame <= frame) prev = kfs[i];
        if (kfs[i].startFrame >= frame && !next) next = kfs[i];
    }
    if (!prev && !next) return;
    if (!prev) prev = next;
    if (!next) next = prev;

    if (prev === next) {
        // Exactly on or beyond last keyframe
        state.camera.position.set(prev.data.position.x, prev.data.position.y, prev.data.position.z);
        state.camera.rotation.set(prev.data.rotation.x, prev.data.rotation.y, prev.data.rotation.z);
        state.camera.fov = prev.data.fov;
    } else {
        const alpha = (frame - prev.startFrame) / (next.startFrame - prev.startFrame);
        const interp = prev.data.interpolation || 'linear';
        const t = interp === 'smooth' ? alpha * alpha * (3 - 2 * alpha) : (interp === 'step' ? 0 : alpha);
        state.camera.position.lerpVectors(
            new THREE.Vector3(prev.data.position.x, prev.data.position.y, prev.data.position.z),
            new THREE.Vector3(next.data.position.x, next.data.position.y, next.data.position.z), t);
        // Slerp rotation via quaternions
        const qPrev = new THREE.Quaternion().setFromEuler(new THREE.Euler(prev.data.rotation.x, prev.data.rotation.y, prev.data.rotation.z));
        const qNext = new THREE.Quaternion().setFromEuler(new THREE.Euler(next.data.rotation.x, next.data.rotation.y, next.data.rotation.z));
        const qResult = new THREE.Quaternion().slerpQuaternions(qPrev, qNext, t);
        state.camera.quaternion.copy(qResult);
        state.camera.fov = prev.data.fov + (next.data.fov - prev.data.fov) * t;
    }
    state.camera.updateProjectionMatrix();
    state.controls.enabled = false;
}

function applyLightTrack(track, t) {
    if (!track.light || track.clips.length === 0) return;
    const frame = state.playheadFrame;
    const kfs = track.clips;
    let prev = null, next = null;
    for (let i = 0; i < kfs.length; i++) {
        if (kfs[i].startFrame <= frame) prev = kfs[i];
        if (kfs[i].startFrame >= frame && !next) next = kfs[i];
    }
    if (!prev && !next) return;
    if (!prev) prev = next;
    if (!next) next = prev;

    if (prev === next) {
        track.light.position.set(prev.data.position.x, prev.data.position.y, prev.data.position.z);
        track.light.color.set(prev.data.color);
        track.light.intensity = prev.data.intensity;
    } else {
        const alpha = (frame - prev.startFrame) / (next.startFrame - prev.startFrame);
        track.light.position.lerpVectors(
            new THREE.Vector3(prev.data.position.x, prev.data.position.y, prev.data.position.z),
            new THREE.Vector3(next.data.position.x, next.data.position.y, next.data.position.z), alpha);
        const cPrev = new THREE.Color(prev.data.color);
        const cNext = new THREE.Color(next.data.color);
        track.light.color.lerpColors(cPrev, cNext, alpha);
        track.light.intensity = prev.data.intensity + (next.data.intensity - prev.data.intensity) * alpha;
    }
    if (track.lightHelper) track.lightHelper.position.copy(track.light.position);
}

function applyAudioTrack(track, t) {
    if (!track.audioCtx || !track.gainNode) return;
    for (const clip of track.clips) {
        if (clip.type !== 'audio' || !clip.data.audioBuffer) continue;
        const clipStart = clip.startFrame / state.project.fps;
        const clipEnd = clipStart + clip.duration;
        if (t >= clipStart && t < clipEnd) {
            track.gainNode.gain.value = clip.data.volume || 1;
            // Audio playback is managed in togglePlay/stopPlayback
            return;
        }
    }
}

// Audio play/stop helpers
export function startAudioPlayback() {
    for (const track of state.project.tracks) {
        if (track.type !== 'audio' || track.muted || !track.audioCtx) continue;
        stopAudioTrack(track);
        const t = state.playheadFrame / state.project.fps;
        for (const clip of track.clips) {
            if (clip.type !== 'audio' || !clip.data.audioBuffer) continue;
            const clipStart = clip.startFrame / state.project.fps;
            const clipEnd = clipStart + clip.duration;
            if (t >= clipStart && t < clipEnd) {
                const source = track.audioCtx.createBufferSource();
                source.buffer = clip.data.audioBuffer;
                source.connect(track.gainNode);
                track.gainNode.gain.value = clip.data.volume || 1;
                const offset = (t - clipStart) + (clip.data.offset || 0);
                source.start(0, offset);
                track.sourceNode = source;
                track._audioClip = clip;
            }
        }
    }
}

export function stopAudioTrack(track) {
    if (track.sourceNode) {
        try { track.sourceNode.stop(); } catch(e) {}
        track.sourceNode = null;
        track._audioClip = null;
    }
}

export function stopAllAudio() {
    for (const track of state.project.tracks) {
        if (track.type === 'audio') stopAudioTrack(track);
    }
}

export function updatePlaybackUI() {
    const t = state.playheadFrame / state.project.fps;
    const el = document.getElementById('pb-time');
    if (el) el.textContent = formatTime(t);
    const fr = document.getElementById('pb-frame');
    if (fr) fr.textContent = `F: ${state.playheadFrame}`;
    const dur = document.getElementById('pb-duration');
    if (dur) dur.textContent = formatTime(state.project.duration);
}

export function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = (s % 60).toFixed(2);
    return `${m.toString().padStart(2, '0')}:${sec.padStart(5, '0')}`;
}

// Register functions in registry
fn.applyPlayhead = applyPlayhead;
fn.updatePlaybackUI = updatePlaybackUI;
fn.formatTime = formatTime;
fn.togglePlay = togglePlay;
fn.stopPlayback = stopPlayback;
fn.stepFrame = stepFrame;
fn.stopAudioTrack = stopAudioTrack;
fn.stopAllAudio = stopAllAudio;
fn.startAudioPlayback = startAudioPlayback;
fn.setupPlayback = setupPlayback;
