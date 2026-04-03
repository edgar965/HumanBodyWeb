/**
 * BVH Studio — Track management (add, remove, select, clip operations).
 */
import * as THREE from 'three';
import { state, TRACK_COLORS } from './state.js';
import { fn } from './registry.js';
import { Track, Clip } from './models.js';
import { pushUndo } from './undo.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js?v=2';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    sharedState, BODY_MATERIALS,
    computeSkinAttributes, applySkinColorToMaterials,
} from '../character_core.js?v=1';
import { generateRigBoneMesh } from '../model_generator.js';

const ss = sharedState;

export function addTrack(name) {
    const track = new Track(
        name || `Track ${state.project.tracks.length + 1}`,
        state.project.defaultModel || 'Rig2',
        state.project.defaultBodyType || 'Female_Caucasian'
    );
    state.project.tracks.push(track);
    state.scene.add(track.group);
    fn.updateTrackHeaders();
    selectTrack(state.project.tracks.length - 1);
    return track;
}

export function addSpecialTrack(type, name) {
    const defaults = { camera: 'Kamera', light: 'Licht', audio: 'Audio' };
    const track = new Track(name || defaults[type] || type);
    track.type = type;
    track.color = TRACK_COLORS[type] || track.color;

    if (type === 'camera') {
        track.cameraActive = true;
    } else if (type === 'light') {
        track.light = new THREE.PointLight(0xffffff, 2.0, 50);
        track.light.position.set(2, 3, 2);
        state.scene.add(track.light);
        // Helper sphere
        const helperGeo = new THREE.SphereGeometry(0.08, 8, 8);
        const helperMat = new THREE.MeshBasicMaterial({ color: 0xffc107 });
        track.lightHelper = new THREE.Mesh(helperGeo, helperMat);
        track.lightHelper.position.copy(track.light.position);
        state.scene.add(track.lightHelper);
    } else if (type === 'audio') {
        track.audioCtx = state.project._audioCtx || (state.project._audioCtx = new (window.AudioContext || window.webkitAudioContext)());
        track.gainNode = track.audioCtx.createGain();
        track.gainNode.connect(track.audioCtx.destination);
    }

    state.project.tracks.push(track);
    fn.updateTrackHeaders();
    selectTrack(state.project.tracks.length - 1);
    return track;
}

// Camera keyframe helpers
export function addCameraKeyframe(trackIdx) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'camera') return;
    pushUndo('Kamera Keyframe');
    const kf = new Clip(null, `KF ${track.clips.length + 1}`, 0, state.project.fps);
    kf.type = 'camera_kf';
    kf.startFrame = state.playheadFrame;
    kf.data = {
        position: { x: state.camera.position.x, y: state.camera.position.y, z: state.camera.position.z },
        rotation: { x: state.camera.rotation.x, y: state.camera.rotation.y, z: state.camera.rotation.z },
        fov: state.camera.fov,
        interpolation: 'smooth',  // 'linear' | 'smooth' | 'step'
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    console.log(`[BVH Studio] Camera keyframe added at frame ${state.playheadFrame}`);
}

// Light keyframe helpers
export function addLightKeyframe(trackIdx) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'light' || !track.light) return;
    pushUndo('Licht Keyframe');
    const kf = new Clip(null, `LKF ${track.clips.length + 1}`, 0, state.project.fps);
    kf.type = 'light_kf';
    kf.startFrame = state.playheadFrame;
    kf.data = {
        position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
        color: '#' + track.light.color.getHexString(),
        intensity: track.light.intensity,
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    console.log(`[BVH Studio] Light keyframe added at frame ${state.playheadFrame}`);
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
    pushUndo('Track loeschen');
    const track = state.project.tracks[idx];

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

    // Cleanup special tracks
    if (track.light) { state.scene.remove(track.light); track.light.dispose(); }
    if (track.lightHelper) { state.scene.remove(track.lightHelper); track.lightHelper.geometry.dispose(); }
    if (track.type === 'audio') fn.stopAudioTrack(track);

    state.project.tracks.splice(idx, 1);
    if (state.selectedTrackIdx >= state.project.tracks.length) state.selectedTrackIdx = state.project.tracks.length - 1;
    state.selectedClipIdx = -1;
    fn.updateTrackHeaders();
    fn.updateProperties();
    fn.renderTimeline();
}

export function selectTrack(idx) {
    state.selectedTrackIdx = idx;
    state.selectedClipIdx = -1;
    fn.updateTrackHeaders();
    fn.updateProperties();
}

export async function addClipToTrack(trackIdx, category, name, frames) {
    pushUndo('Clip hinzufuegen');
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
    if (track.mesh) track.mesh.visible = true;  // re-show if was hidden
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

        // Build character if not yet loaded
        if (!track.skeleton && ss.rigifySkeletonData && ss.skinWeightData) {
            await loadTrackCharacter(track);
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

export async function loadTrackCharacter(track) {
    try {
        // Check if preset is a generated model (Rig1-4)
        const modelResp = await fetch(`/api/character/model/${encodeURIComponent(track.preset)}/`);
        const modelData = await modelResp.json();

        if (modelData.type === 'generated_model') {
            // Generated model: use model_generator.js
            let rigBonesData = null;
            try {
                const rigResp = await fetch('/api/character/rig/');
                if (rigResp.ok) rigBonesData = await rigResp.json();
            } catch (e) {}

            if (rigBonesData && ss.rigifySkeletonData && ss.skinWeightData) {
                const result = generateRigBoneMesh(rigBonesData, modelData, ss.rigifySkeletonData, ss.skinWeightData);
                if (result && result.mesh) {
                    track.mesh = result.mesh;
                    track.group.add(track.mesh);
                    if (result.skeleton) {
                        track.skeleton = result.skeleton;
                        // Rename bones: dots -> underscores so Three.js AnimationMixer
                        // can parse track names correctly (DEF-spine_001.quaternion)
                        if (result.skeleton.skeleton) {
                            for (const bone of result.skeleton.skeleton.bones) {
                                bone.name = bone.name.replace(/\./g, '_');
                            }
                        }
                        // Also update boneByName map
                        const newMap = {};
                        for (const [k, v] of Object.entries(result.skeleton.boneByName)) {
                            newMap[k.replace(/\./g, '_')] = v;
                        }
                        result.skeleton.boneByName = newMap;
                        track.mixer = new THREE.AnimationMixer(track.mesh);
                    } else {
                        track.mixer = new THREE.AnimationMixer(track.mesh);
                    }
                    console.log(`[BVH Studio] Generated model loaded: ${track.preset}`);
                    return;
                }
            }
        }

        // Fallback: standard mesh API
        const resp = await fetch(`/api/character/mesh/?body_type=${encodeURIComponent(track.bodyType)}`);
        const data = await resp.json();
        if (data.error) return;

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        if (data.faces) geo.setIndex(new THREE.BufferAttribute(base64ToUint32(data.faces), 1));
        if (data.normals) {
            const nb = base64ToFloat32(data.normals);
            blenderToThreeCoords(nb);
            geo.setAttribute('normal', new THREE.BufferAttribute(nb, 3));
        } else {
            geo.computeVertexNormals();
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide, transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));
        applySkinColorToMaterials(materials, track.bodyType, ss.skinColors);

        const groups = data.groups || [];
        if (groups.length > 0) {
            for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
            track.mesh = new THREE.Mesh(geo, materials);
        } else {
            track.mesh = new THREE.Mesh(geo, materials[0]);
        }

        // Skin
        const { skinIndices, skinWeights } = computeSkinAttributes(geo, ss.skinWeightData);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

        track.skeleton = buildRigifySkeleton(ss.rigifySkeletonData, ss.skinWeightData);
        const mat = track.mesh.material;
        const skinnedMesh = new THREE.SkinnedMesh(geo, mat);
        skinnedMesh.add(track.skeleton.rootBone);
        skinnedMesh.bind(track.skeleton.skeleton);

        track.mesh = skinnedMesh;
        track.group.add(skinnedMesh);
        track.mixer = new THREE.AnimationMixer(skinnedMesh);

        console.log(`[BVH Studio] Character loaded for track: ${track.name}`);
    } catch (e) {
        console.error('[BVH Studio] Character load failed:', e);
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
    pushUndo('Clip loeschen');
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
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();

    // If no more clips on this BVH track, hide the model and stop playback
    if (track.type === 'bvh' && track.clips.length === 0) {
        if (track.mesh) track.mesh.visible = false;
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

    if (mode === 'start') {
        clip.trimIn = Math.min(maxTrim - clip.trimOut, clip.trimIn + frames);
    } else if (mode === 'end') {
        clip.trimOut = Math.min(maxTrim - clip.trimIn, clip.trimOut + frames);
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
            clip2.startFrame = state.playheadFrame;
            clip2.trimIn = splitFrame;
            clip2.trimOut = clip.trimOut;
            clip2.speed = clip.speed;
            clip2.animClip = clip.animClip;
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

// Register functions in registry
fn.addTrack = addTrack;
fn.addSpecialTrack = addSpecialTrack;
fn.addClipToTrack = addClipToTrack;
fn.addCameraKeyframe = addCameraKeyframe;
fn.addLightKeyframe = addLightKeyframe;
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
