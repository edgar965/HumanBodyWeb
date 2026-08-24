/**
 * Tonspuren abspielen und anhalten.
 *
 * Aus playback.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


export function applyAudioTrack(track, t) {
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
    // Resume AudioContext if suspended (Chrome auto-suspends after inactivity)
    if (state.project._audioCtx && state.project._audioCtx.state === 'suspended') {
        state.project._audioCtx.resume();
    }
    for (const track of state.project.tracks) {
        if (track.type !== 'audio' || track.muted || !track.audioCtx) continue;
        if (track.audioCtx.state === 'suspended') track.audioCtx.resume();
        stopAudioTrack(track);
        const t = state.playheadFrame / state.project.fps;
        for (const clip of track.clips) {
            if (clip.type !== 'audio') continue;
            if (!clip.data.audioBuffer) {
                if (clip._needsReload && !clip._reloadWarned) {
                    clip._reloadWarned = true;
                    Protokoll.warnung('Audio', `"${clip.data?.fileName}" nicht geladen — bitte Audio-Datei erneut hinzufügen`);
                }
                continue;
            }
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
        // stumm gewollt: Ein Tonknoten, der schon zu Ende gelaufen ist, wirft beim
        // Stoppen — genau der Normalfall beim Anhalten.
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
