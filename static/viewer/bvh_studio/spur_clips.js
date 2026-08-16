/**
 * Clips einer Spur: anlegen, laden, teilen, kuerzen, loeschen.
 *
 * Aus tracks.js herausgeloest (Umbau 15.08.2026).
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';

import { sharedState } from '../character_core.js?v=1';
import { addTrack } from './tracks.js';
import { loadTrackCharacter } from './spur_charakter.js';
const ss = sharedState;


export async function addClipToTrack(trackIdx, category, name, frames) {
    pushUndo('Clip hinzufügen');
    console.log(`[BVH Studio] addClipToTrack: trackIdx=${trackIdx}, ${category}/${name}, existingTracks=${state.project.tracks.length}`);
    if (trackIdx < 0 || !state.project.tracks[trackIdx]) {
        if (state.project.tracks.length === 0) addTrack();
        trackIdx = state.project.tracks.length - 1;
    }
    const track = state.project.tracks[trackIdx];
    if (!track) { console.error('[BVH Studio] addClipToTrack: no track!'); return; }

    // Reset mixer state so new clip plays cleanly
    if (track.mixer) {
        track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
    }

    const clip = new Clip(category, name, frames || 3000, state.project.fps);

    // Place after last clip on this track
    const lastClip = track.clips[track.clips.length - 1];
    clip.startFrame = lastClip ? lastClip.endFrame : 0;

    track.clips.push(clip);
    if (track.group) track.group.visible = true;  // re-show if was hidden
    fn.updateDuration();
    fn.renderTimeline();

    // Load retargeted animation
    await loadClipAnimation(track, clip);
    console.log(`[BVH Studio] addClipToTrack done: clips=${track.clips.length}, hasMixer=${!!track.mixer}, hasSkeleton=${!!track.skeleton}`);
    fn.updateProperties();
}

export async function loadClipAnimation(track, clip) {
    try {
        const url = `/api/retarget/?category=${encodeURIComponent(clip.category)}&name=${encodeURIComponent(clip.name)}`;
        const resp = await fetch(url);
        if (!resp.ok) {
            console.error(`[BVH Studio] Retarget failed for ${clip.category}/${clip.name}: ${resp.status}`);
            clip._loadError = true;
            fn.renderTimeline();
            return;
        }
        const data = await resp.json();

        if (!data.tracks || !data.frame_count) {
            console.warn(`[BVH Studio] No animation data for ${clip.name}`);
            return;
        }

        clip.totalFrames = data.frame_count;
        clip.fps = data.frame_count / data.duration;

        // Modell laden wenn noch nicht vorhanden
        if (!track.mesh && ss.rigifySkeletonData && ss.skinWeightData) {
            await loadTrackCharacter(track);
            if (track.group) track.group.visible = true;
        }

        if (track.skeleton) {
            clip.animClip = buildClipFromData(data, track.skeleton);
            fn.serverLog('clip_loaded', `${clip.name} (${clip.totalFrames}f, ${clip.duration.toFixed(1)}s)`);

            // Auto-apply Gauss smooth if active
            const _gaussSmooth = fn.getGaussSmooth();
            if (_gaussSmooth && _gaussSmooth.active && clip.animClip) {
                const key = `${clip.category}/${clip.name}`;
                const backup = {};
                for (const t of clip.animClip.tracks) backup[t.name] = new Float32Array(t.values);
                _gaussSmooth.origClips.set(key, backup);
                for (const t of clip.animClip.tracks) fn.gaussFilter(t.values, t.getValueSize(), _gaussSmooth.sigma);
                fn.serverLog('gauss_auto_applied', `${clip.name} sigma=${_gaussSmooth.sigma}`);
            }
            // Auto-apply Fixed Position if active
            const _fp = fn.getFixedPos ? fn.getFixedPos() : null;
            if (_fp && _fp.active && clip.animClip) {
                fn.applyFixedPositionAll();
            }
        }

        fn.updateDuration();
        fn.renderTimeline();
    } catch (e) {
        console.error('[BVH Studio] Clip load failed:', e);
    }
}

export function buildClipFromData(data, skel) {
    const tracks = [];
    const times = data.times.map(t => t);
    for (const [boneName, values] of Object.entries(data.tracks)) {
        const jsName = boneName.replace(/\./g, '_');
        const bone = skel.boneByName[jsName];
        if (!bone) continue;
        const kf = new THREE.QuaternionKeyframeTrack(
            bone.name + '.quaternion', times, values
        );
        tracks.push(kf);
    }
    if (data.position_track) {
        const jsName = data.position_track.bone.replace(/\./g, '_');
        const bone = skel.boneByName[jsName];
        if (bone) {
            tracks.push(new THREE.VectorKeyframeTrack(
                bone.name + '.position', times, data.position_track.values
            ));
        }
    }
    return new THREE.AnimationClip('clip', data.duration, tracks);
}

// Three.js PropertyBinding parst Dots als Separator:
// "DEF-spine.001.quaternion" → Objekt "DEF-spine", Property "001" (FALSCH)
// Daher Dots→Underscores in Bone-Namen, damit Track-Namen korrekt geparst werden.
export function _sanitizeBoneNames(skeleton) {
    if (skeleton.skeleton) {
        for (const bone of skeleton.skeleton.bones) {
            bone.name = bone.name.replace(/\./g, '_');
        }
    }
    if (skeleton.boneByName) {
        const fixed = {};
        for (const [k, v] of Object.entries(skeleton.boneByName)) {
            fixed[k.replace(/\./g, '_')] = v;
        }
        skeleton.boneByName = fixed;
    }
}

export function duplicateSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) return;
    pushUndo('Duplizieren');
    const track = state.project.tracks[state.selectedTrackIdx];
    const orig = track.clips[state.selectedClipIdx];
    const copy = new Clip(orig.category, orig.name, orig.totalFrames, orig.fps);
    copy.startFrame = orig.endFrame;  // place after original
    copy.trimIn = orig.trimIn;
    copy.trimOut = orig.trimOut;
    copy.speed = orig.speed;
    copy.smoothSigma = orig.smoothSigma;
    copy.groundFix = orig.groundFix;
    copy.animClip = orig.animClip;  // share the same clip data
    track.clips.push(copy);
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    fn.serverLog('clip_duplicated');
}

export function deleteSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) return;
    const track = state.project.tracks[state.selectedTrackIdx];
    if (!track || state.selectedClipIdx >= track.clips.length) return;
    pushUndo('Clip löschen');
    const clip = track.clips[state.selectedClipIdx];

    // Uncache the AnimationClip from the mixer so it doesn't linger
    if (track.mixer) {
        track.mixer.stopAllAction();
        if (clip.animClip) track.mixer.uncacheClip(clip.animClip);
    }
    track._activeClip = null;
    track._activeAction = null;

    track.clips.splice(state.selectedClipIdx, 1);
    state.selectedClipIdx = -1;

    // If a model clip was deleted, hide the linked animation track's mesh + accessories
    if (clip.type === 'model' && track.type === 'model') {
        track._currentPreset = null;
        const animTrack = state.project.getLinkedAnimation(track);
        if (animTrack?.group) animTrack.group.visible = false;
    }

    // 3D-Objekt-Clip gelöscht und keine weiteren object_clips übrig → Mesh aus Szene entfernen.
    // applyPlayhead() würde nur visible=false setzen; wir wollen das Mesh komplett weg.
    if (clip.type === 'object_clip' && track.type === 'scene_object') {
        const remaining = track.clips.some(c => c.type === 'object_clip');
        if (!remaining && track.mesh) {
            state.scene.remove(track.mesh);
            track.mesh.traverse?.(obj => {
                if (obj.geometry) obj.geometry.dispose?.();
                if (obj.material) {
                    if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose?.());
                    else obj.material.dispose?.();
                }
            });
            track.mesh = null;
            track.objectUrl = null;
            track.objectMtlUrl = null;
            fn.detachTransformControls?.();
        }
    }

    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    fn.applyPlayhead?.();

    // If no more clips on this BVH track, hide the model and stop playback
    if (track.type === 'bvh' && track.clips.length === 0) {
        if (track.group) track.group.visible = false;
        if (track.skeleton) track.skeleton.skeleton.pose();
    }

    // Stop playback if no clips left anywhere
    const anyClips = state.project.tracks.some(t => t.clips.length > 0);
    if (!anyClips && state.playing) {
        state.playing = false;
        const icon = document.getElementById('pb-play-icon');
        if (icon) icon.className = 'fas fa-play';
    }
    // Reset skeleton to rest pose
    if (track.skeleton) track.skeleton.skeleton.pose();

    fn.serverLog('clip_deleted');
}

export function trimSelectedClip(mode, frames = 10) {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) return;
    pushUndo('Trim');
    const clip = state.project.tracks[state.selectedTrackIdx].clips[state.selectedClipIdx];
    if (!clip || clip.type !== 'bvh') return;
    const maxTrim = clip.totalFrames - 1;

    // Math.max(…) um die Begrenzung herum (Review 13.08.2026): `Math.min` allein
    // kann den Wert VERKLEINERN, wenn die Obergrenze schon unter dem aktuellen
    // Stand liegt. Beispiel gerechnet: trimIn=5, trimOut=maxTrim-2 ->
    // maxTrim-trimOut = 2 -> min(2, 15) = 2. Ein Klick auf „Anfang kürzen" hat
    // den Clip am Anfang damit VERLÄNGERT. Jetzt bleibt der Wert stehen, wenn
    // die Grenze erreicht ist — beide Aufrufer übergeben nur positive Frames
    // (timeline.js: ctx-trim-start/-end mit 10).
    if (mode === 'start') {
        clip.trimIn = Math.max(clip.trimIn, Math.min(maxTrim - clip.trimOut, clip.trimIn + frames));
    } else if (mode === 'end') {
        clip.trimOut = Math.max(clip.trimOut, Math.min(maxTrim - clip.trimIn, clip.trimOut + frames));
    } else if (mode === 'reset') {
        clip.trimIn = 0;
        clip.trimOut = 0;
    }
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    console.log(`[BVH Studio] Trim ${mode}: in=${clip.trimIn}, out=${clip.trimOut}`);
}

export function splitClipAtPlayhead() {
    if (state.selectedTrackIdx < 0) return;
    pushUndo('Split');
    const track = state.project.tracks[state.selectedTrackIdx];
    const t = state.playheadFrame / state.project.fps;
    for (let i = 0; i < track.clips.length; i++) {
        const clip = track.clips[i];
        const cs = clip.startFrame / state.project.fps;
        const ce = cs + clip.duration;
        if (t > cs && t < ce) {
            const splitFrame = Math.round((t - cs) * clip.fps * clip.speed) + clip.trimIn;
            // Clone clip
            const clip2 = new Clip(clip.category, clip.name, clip.totalFrames, clip.fps);
            clip2.type = clip.type;
            clip2.startFrame = state.playheadFrame;
            clip2.trimIn = splitFrame;
            clip2.trimOut = clip.trimOut;
            clip2.speed = clip.speed;
            clip2.smoothSigma = clip.smoothSigma;
            clip2.groundFix = clip.groundFix;
            clip2.animClip = clip.animClip;
            if (clip.data) clip2.data = { ...clip.data };
            // Trim original
            clip.trimOut = clip.totalFrames - splitFrame;
            track.clips.splice(i + 1, 0, clip2);
            fn.updateDuration();
            fn.renderTimeline();
            console.log(`[BVH Studio] Split clip at frame ${splitFrame}`);
            break;
        }
    }
}
