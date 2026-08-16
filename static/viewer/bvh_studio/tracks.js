/**
 * BVH Studio — Track management (add, remove, select, clip operations).
 */
import * as THREE from 'three';
import { state, TRACK_COLORS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track, Clip } from './models.js';
import { pushUndo } from './undo.js';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    BODY_MATERIALS,
    computeSkinAttributes, applySkinColorToMaterials,
} from '../character_core.js?v=1';
import { createLightHelper, addLightKeyframePair, addLightKeyframe } from './spur_lichter.js';
import { addClipToTrack, loadClipAnimation, buildClipFromData, duplicateSelectedClip, deleteSelectedClip, trimSelectedClip, splitClipAtPlayhead } from './spur_clips.js';
import { loadTrackCharacter } from './spur_charakter.js';


export function addTrack(name, _skipModelTrack) {
    pushUndo('Spur hinzufügen');
    const bvhCount = state.project.animations.length;
    const track = new Track(
        name || `Animation ${bvhCount + 1}`,
        state.project.defaultModel || 'Rig2',
        state.project.defaultBodyType || 'Female_Caucasian'
    );
    state.project.addTrack(track);
    state.scene.add(track.group);
    const bvhTrackIdx = state.project.tracks.length - 1;

    // Mesh wird von loadClipAnimation geladen wenn der erste BVH-Clip kommt

    fn.updateTrackHeaders();
    fn.renderTimeline();
    selectTrack(bvhTrackIdx);
    return track;
}

export function addModelTrack(name) {
    pushUndo('Modell-Spur hinzufügen');
    const track = new Track(name || `Modell ${state.project.modelTracks.length + 1}`);
    track.type = 'model';
    track.color = TRACK_COLORS.model;
    track.muted = false;
    track._currentPreset = null;
    track._linkedAnimIdx = -1;
    state.project.addTrack(track);
    const idx = state.project.tracks.length - 1;
    fn.updateTrackHeaders();
    fn.renderTimeline();
    selectTrack(idx);
    return track;
}








export function addSpecialTrack(type, name) {
    pushUndo('Spur hinzufügen');
    const defaults = { camera: 'Kamera', light: 'Licht', audio: 'Audio' };
    const track = new Track(name || defaults[type] || type);
    track.type = type;
    track.color = TRACK_COLORS[type] || track.color;

    if (type === 'camera') {
        track.cameraActive = true;
    } else if (type === 'light') {
        // User-erzeugte Licht-Spur = SpotLight (neu erstellt)
        track.light = new THREE.SpotLight(0xffffff, 2.0, 50, Math.PI / 6, 0.3, 1);
        track.light.position.set(2, 3, 2);
        track.light.target.position.set(0, 0, 0);
        state.scene.add(track.light);
        state.scene.add(track.light.target);
        track.lightType = 'spot';
        track.lightHelper = createLightHelper(track.light);
        if (track.lightHelper) state.scene.add(track.lightHelper);
        track.lightVisible = false;  // Helfer-Linien: default aus
        track.coneVisible = true;    // Lichtkegel: default an
    } else if (type === 'audio') {
        track.audioCtx = state.project._audioCtx || (state.project._audioCtx = new (window.AudioContext || window.webkitAudioContext)());
        track.gainNode = track.audioCtx.createGain();
        track.gainNode.connect(track.audioCtx.destination);
    } else if (type === 'scene_object') {
        track.subtype = 'custom';
        track.color = '#7c5cbf';
        track.mesh = null;  // Leerer Track — Mesh wird via Context-Menu "Hinzufügen" geladen
        track.objectTint = '#ffffff';
        // Szene-Gruppe aufklappen damit der neue Track sofort sichtbar ist
        state.sceneGroupCollapsed = false;
    }

    state.project.addTrack(track);
    fn.updateTrackHeaders();
    selectTrack(state.project.tracks.length - 1);
    return track;
}

// Camera keyframe helpers
export function addCameraKeyframe(trackIdx, frame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'camera') return;
    pushUndo('Kamera Keyframe');
    const targetFrame = (frame != null) ? frame : state.playheadFrame;
    const kf = new Clip(null, `Kameraposition ${track.clips.length + 1}`, 0, state.project.fps);
    kf.type = 'camera_kf';
    kf.startFrame = targetFrame;
    // LookAt-Target = OrbitControls.target beim Anlegen. So kann die
    // Playback-Seite zwischen zwei Keyframes sauber interpolieren: Position
    // linear, Target linear, dann camera.lookAt(target). Das hält das
    // Motiv mittig, während die Kamera durch die Szene fliegt — auch wenn
    // Start- und End-Orientierung stark unterschiedlich sind.
    const lookAt = state.controls && state.controls.target
        ? { x: state.controls.target.x, y: state.controls.target.y, z: state.controls.target.z }
        : null;
    kf.data = {
        position: { x: state.camera.position.x, y: state.camera.position.y, z: state.camera.position.z },
        rotation: { x: state.camera.rotation.x, y: state.camera.rotation.y, z: state.camera.rotation.z },
        // Store quaternion alongside Euler: quaternion is the canonical
        // representation that slerp can safely interpolate between; Euler
        // values can be equivalent-but-different for the same orientation
        // (e.g. after successive OrbitControls moves) which makes a naive
        // euler→quaternion round-trip pick the wrong hemisphere and drag
        // the camera through the scene.
        quaternion: { x: state.camera.quaternion.x, y: state.camera.quaternion.y, z: state.camera.quaternion.z, w: state.camera.quaternion.w },
        lookAt,
        fov: state.camera.fov,
        interpolation: 'smooth',  // 'linear' | 'smooth' | 'step'
        fade: true,  // Fade-Effekt: true = interpolieren zum nächsten KF, false = Sprung
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    console.log(`[BVH Studio] Kameraposition gespeichert bei Frame ${targetFrame}`);
}



// Audio clip helpers
export async function loadAudioFile(trackIdx) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'audio') return;

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.addEventListener('change', async () => {
        const file = input.files[0];
        if (!file) return;
        try {
            const arrayBuf = await file.arrayBuffer();
            const audioBuffer = await track.audioCtx.decodeAudioData(arrayBuf);
            const clip = new Clip(null, file.name, Math.round(audioBuffer.duration * state.project.fps), state.project.fps);
            clip.type = 'audio';
            clip.startFrame = state.playheadFrame;
            clip.data = {
                fileName: file.name,
                audioBuffer: audioBuffer,
                audioDuration: audioBuffer.duration,
                volume: 1.0,
                fadeIn: 0,
                fadeOut: 0,
                offset: 0,
            };
            // Upload audio to server for persistence across refreshes
            try {
                const formData = new FormData();
                formData.append('audio', file);
                const uploadResp = await fetch('/api/studio/audio-upload/', { method: 'POST', body: formData });
                const uploadData = await uploadResp.json();
                if (uploadData.ok) {
                    clip.data.audioUrl = uploadData.url;
                    console.log(`[BVH Studio] Audio uploaded: ${uploadData.url}`);
                } else {
                    console.warn('[BVH Studio] Audio upload failed:', uploadData.error);
                }
            } catch (uploadErr) {
                console.warn('[BVH Studio] Audio upload error:', uploadErr);
            }
            track.clips.push(clip);
            fn.updateDuration();
            fn.renderTimeline();
            fn.updateProperties();
            console.log(`[BVH Studio] Audio loaded: ${file.name} (${audioBuffer.duration.toFixed(1)}s)`);
        } catch (e) {
            console.error('[BVH Studio] Audio decode failed:', e);
            alert('Audio laden fehlgeschlagen: ' + e.message);
        }
    });
    input.click();
}

export function removeTrack(idx) {
    if (idx < 0 || idx >= state.project.tracks.length) return;
    pushUndo('Track löschen');
    const track = state.project.tracks[idx];

    // If removing a model track, hide linked animation track's mesh + accessories
    if (track.type === 'model') {
        const animTrack = state.project.getLinkedAnimation(track);
        if (animTrack?.group) animTrack.group.visible = false;
    }

    // Stop mixer
    if (track.mixer) {
        track.mixer.stopAllAction();
        track.mixer = null;
    }
    track._activeClip = null;
    track._activeAction = null;

    // Dispose mesh + materials
    if (track.mesh) {
        track.group.remove(track.mesh);
        if (track.mesh.geometry) track.mesh.geometry.dispose();
        if (Array.isArray(track.mesh.material)) {
            track.mesh.material.forEach(m => m.dispose());
        } else if (track.mesh.material) {
            track.mesh.material.dispose();
        }
        track.mesh = null;
    }

    // Remove group from scene (removes all children)
    state.scene.remove(track.group);
    track.group = null;

    // Cleanup special tracks — Boden ist geschützt, Lichter (auch Szenen-Lichter) dürfen weg
    if (track._sceneItem) {
        console.warn(`[BVH Studio] Szenen-Element "${track.name}" kann nicht gelöscht werden.`);
        return;
    }
    if (track.light) {
        if (track.light.target) state.scene.remove(track.light.target);
        state.scene.remove(track.light);
        track.light.dispose();
        // Szenen-Licht-Referenz nullen, damit createSceneLightTracks es nicht wieder anlegt
        if (track._sceneLight) {
            if (state.sceneKeyLight === track.light)  state.sceneKeyLight = null;
            if (state.sceneFillLight === track.light) state.sceneFillLight = null;
            if (state.sceneBackLight === track.light) state.sceneBackLight = null;
            if (state.sceneAmbient === track.light)   state.sceneAmbient = null;
        }
    }
    if (track.lightHelper) {
        state.scene.remove(track.lightHelper);
        track.lightHelper.traverse?.(obj => {
            if (obj.geometry) obj.geometry.dispose?.();
            if (obj.material) obj.material.dispose?.();
        });
    }
    if (track.type === 'audio') fn.stopAudioTrack(track);

    // Scene-Objects (custom 3D): Mesh aus Szene entfernen + disposen
    if (track.type === 'scene_object' && track.mesh) {
        state.scene.remove(track.mesh);
        track.mesh.traverse?.(obj => {
            if (obj.geometry) obj.geometry.dispose?.();
            if (obj.material) {
                if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose?.());
                else obj.material.dispose?.();
            }
        });
    }

    state.project.removeTrackAt(idx);  // handles _linkedAnimIdx fixup
    if (state.selectedTrackIdx >= state.project.tracks.length) state.selectedTrackIdx = state.project.tracks.length - 1;
    state.selectedClipIdx = -1;
    fn.updateTrackHeaders();
    fn.updateProperties();
    fn.renderTimeline();
}

export function selectTrack(idx) {
    state.selectedTrackIdx = idx;
    state.selectedClipIdx = -1;
    const t = state.project.tracks[idx];
    // TransformControls an Custom-3D-Objekt anhängen, sonst detachen
    if (t?.type === 'scene_object' && t.subtype === 'custom' && t.mesh) {
        fn.attachTransformControls?.(t);
    } else {
        fn.detachTransformControls?.();
    }
    fn.updateTrackHeaders();
    fn.updateProperties();
    fn.switchPropsTab?.('props');
}











// Register functions in registry
fn.addTrack = addTrack;
fn.addModelTrack = addModelTrack;
fn.addSpecialTrack = addSpecialTrack;
fn.addClipToTrack = addClipToTrack;
fn.addCameraKeyframe = addCameraKeyframe;
fn.addLightKeyframe = addLightKeyframe;
fn.addLightKeyframePair = addLightKeyframePair;
fn.loadAudioFile = loadAudioFile;
fn.removeTrack = removeTrack;
fn.selectTrack = selectTrack;
fn.loadClipAnimation = loadClipAnimation;
fn.buildClipFromData = buildClipFromData;
fn.loadTrackCharacter = loadTrackCharacter;
fn.duplicateSelectedClip = duplicateSelectedClip;
fn.deleteSelectedClip = deleteSelectedClip;
fn.trimSelectedClip = trimSelectedClip;
fn.splitClipAtPlayhead = splitClipAtPlayhead;
