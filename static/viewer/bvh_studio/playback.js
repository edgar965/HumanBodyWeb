/**
 * BVH Studio — Playback controls, audio, apply playhead to tracks.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { startAudioPlayback, stopAllAudio, stopAudioTrack } from './spur_ton.js';
import { _schedulePreloads } from './vorladen.js';
import { applyAudioTrack } from './spur_ton.js';
import { applyBvhTrack, applyCameraTrack, applyLightTrack, applyModelTrack, applySceneObjectTrack } from './spur_anwenden.js';

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
            // Priorität: Clip-Selektion → Library-Selektion → Track-Selektion
            if (state.selectedClipIdx >= 0) {
                fn.deleteSelectedClip();
            } else if (document.querySelector('.lib-item.selected')) {
                fn.deleteSelectedLibItem();
            } else if (state.selectedTrackIdx >= 0) {
                fn.removeTrack(state.selectedTrackIdx);  // pushUndo intern
            }
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
        // Diagnose-Snapshot: was ist der Zustand beim Play-Start?
        const summary = state.project.tracks.map((tr, i) => {
            const link = tr.type === 'model' ? `→${tr._linkedAnimIdx}` : '';
            const ctrl = tr.type === 'bvh' ? (tr._modelControlled ? 'mctl' : 'free') : '';
            const has = tr.type === 'bvh' ? `mesh=${!!tr.mesh} mix=${!!tr.mixer} skel=${!!tr.skeleton}` : '';
            const clipsInfo = tr.clips.map(c => {
                const cs = c.startFrame, ce = c.startFrame + Math.ceil(c.duration * state.project.fps);
                const ac = (c.type === 'bvh') ? `ac=${!!c.animClip}` : '';
                const preset = c.data?.preset ? ` p=${c.data.preset}` : '';
                return `${c.name}[${cs}-${ce}${preset}${ac?' '+ac:''}]`;
            }).join(',');
            return `T${i}(${tr.type}/${tr.name}${link} ${ctrl} ${has}): [${clipsInfo}]`;
        }).join(' | ');
        fn.serverLog('play_start', `frame=${state.playheadFrame} fps=${state.project.fps} tracks=${state.project.tracks.length} ${summary}`);
        startAudioPlayback();
    } else {
        stopAllAudio();
        state.controls.enabled = true;
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

// Bestimmt den Licht-An/Aus-State am aktuellen Playhead für einen Track.
// Priorität:
//  1. Wenn track.muted=true → immer aus (User-Override via Aus-Button)
//  2. Letzter Keyframe vor/an Playhead mit .data.visible != null → dessen Wert
//  3. Default: an (!track.muted)
function _lightVisibleAtPlayhead(track) {
    if (track.muted) return false;
    const pf = state.playheadFrame;
    const kfs = track.clips.filter(c => c.type === 'light_kf');
    // Ohne Keyframes: Licht im Default-Zustand (an wenn nicht muted).
    // Standard-Keyframes werden NICHT mehr automatisch angelegt — das Licht ist
    // einfach immer aktiv bis der User Keyframes für Animation hinzufügt.
    if (kfs.length === 0) return true;
    // Mit Keyframes: zeitabhängige Animation. Vor erstem/nach letztem KF → Licht aus
    // (sinnvoll nur wenn User explizit Anfang/Ende definiert).
    const sorted = [...kfs].sort((a, b) => {
        if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
        return (a.data?.trackPosition === 'upper' ? 0 : 1) - (b.data?.trackPosition === 'upper' ? 0 : 1);
    });
    if (pf < sorted[0].startFrame || pf > sorted[sorted.length - 1].startFrame) return false;
    let activeKf = sorted[0];
    for (const c of sorted) {
        if (c.startFrame <= pf) activeKf = c;
    }
    return activeKf.data?.visible !== false;
}

// Synchronisiert visible state für alle Lichter — wird JEDEN Frame vom
// Render-Loop aufgerufen, damit An/Aus auch ohne Play sofort wirkt.
// Respektiert track.muted UND per-keyframe .data.visible.
export function syncLightVisibility() {
    for (const track of state.project.tracks) {
        if (track.type !== 'light' || !track.light) continue;
        const visible = _lightVisibleAtPlayhead(track);
        track.light.visible = visible;
        // Helper-Group: Lichtkegel (coneVisible) + Helferlinien (lightVisible)
        // unabhängig voneinander steuerbar. Beide bleiben auch sichtbar wenn Licht aus
        // (damit User weiß wo das Licht steht).
        const lh = track.lightHelper;
        if (lh) {
            lh.visible = true;  // Group immer an, Kinder-Visibility entscheidet
            if (lh.spotHelper) lh.spotHelper.visible = !!track.lightVisible;
            if (lh.originCone) lh.originCone.visible = track.coneVisible !== false;
        }
    }
}

export function applyPlayhead() {
    const t = state.playheadFrame / state.project.fps;

    syncLightVisibility();

    _schedulePreloads(t);

    // Bestimme strukturell (nicht per aktivem Clip!), welche BVH-Tracks einen
    // Model-Track verlinkt haben. Nur dort übergibt Model-Track die Visibility.
    for (const track of state.project.tracks) {
        if (track.type === 'bvh') track._modelControlled = false;
    }
    for (const track of state.project.tracks) {
        if (track.type === 'model') {
            const linked = state.project.getLinkedAnimation(track);
            if (linked) linked._modelControlled = true;
        }
    }

    let cameraApplied = false;
    for (const track of state.project.tracks) {
        if (track.muted) continue;
        if (track.type === 'bvh') applyBvhTrack(track, t);
        else if (track.type === 'model') applyModelTrack(track, t);
        else if (track.type === 'camera') {
            // Only the first active camera track drives the camera; later ones
            // would overwrite and make playback look chaotic.
            if (!cameraApplied && track.cameraActive && track.clips?.length) {
                applyCameraTrack(track, t);
                cameraApplied = true;
            }
        }
        else if (track.type === 'light') applyLightTrack(track, t);
        else if (track.type === 'audio') applyAudioTrack(track, t);
        else if (track.type === 'scene_object') applySceneObjectTrack(track, t);
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
fn.stopAudioTrack = stopAudioTrack;
// FEHLER bis 16.08.2026: Nicht angemeldet, aber in eigenschaften/licht.js als
// `fn.syncLightVisibility?.()` gerufen — nach einem Wechsel der Lichtart wurde
// die Sichtbarkeit still NICHT nachgezogen (ein stummgeschaltetes Licht konnte
// wieder leuchten). Das `?.` verschluckte den fehlenden Namen.
// Gefunden mit Docu/umbau/registrierungspruefung.py.
fn.syncLightVisibility = syncLightVisibility;
