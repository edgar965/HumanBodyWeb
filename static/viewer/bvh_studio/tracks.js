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

// Erzeugt Helper-Group für beliebigen Licht-Typ. Enthält:
//   - .spotHelper: Three.js-Wireframe-Helfer (Toggle "Helfer-Linien")
//   - .originCone: solide Form, die den Licht-Typ visuell symbolisiert (Toggle "Lichtkegel")
//
// Formen pro Typ (immer: Spitze/Ursprung am Licht, Form zeigt IN die Szene):
//   - Spot:        Kegel, Radius aus light.angle (breiter Angle = breiter Kegel)
//   - Directional: Zylinder (parallele Strahlen)
//   - Point:       Kugel (omnidirektional)
//   - Ambient:     flaches Rechteck (ungerichtet)
const _LIGHT_SHAPE_HEIGHT = 0.6;

function _buildLightIndicator(light) {
    const color = light.color.clone();
    const mat = new THREE.MeshBasicMaterial({
        color, transparent: true, opacity: 0.45, side: THREE.DoubleSide, depthWrite: false,
    });
    const h = _LIGHT_SHAPE_HEIGHT;
    let geo;
    if (light.isSpotLight) {
        const angle = light.angle ?? Math.PI / 6;
        const radius = Math.min(Math.max(h * Math.tan(angle), 0.05), 1.0);
        geo = new THREE.ConeGeometry(radius, h, 24, 1, true);  // offene Unterseite
        geo.translate(0, -h / 2, 0);  // Spitze → Ursprung, Basis bei (0,-h,0)
    } else if (light.isDirectionalLight) {
        const r = 0.08;
        geo = new THREE.CylinderGeometry(r, r, h, 16, 1, true);
        geo.translate(0, -h / 2, 0);
    } else if (light.isPointLight) {
        geo = new THREE.SphereGeometry(0.12, 20, 14);
    } else if (light.isAmbientLight) {
        geo = new THREE.PlaneGeometry(0.5, 0.3);
        geo.rotateX(-Math.PI / 2);  // horizontal
    } else {
        return null;
    }
    const mesh = new THREE.Mesh(geo, mat);
    mesh._lightShapeKind = light.isSpotLight ? 'spot'
        : light.isDirectionalLight ? 'directional'
        : light.isPointLight ? 'point'
        : light.isAmbientLight ? 'ambient' : 'unknown';
    mesh._lastAngle = light.angle ?? null;
    return mesh;
}

export function createLightHelper(light) {
    if (!light) return null;
    const group = new THREE.Group();
    let typeHelper = null;
    if (light.isSpotLight) typeHelper = new THREE.SpotLightHelper(light, 0xffc107);
    else if (light.isDirectionalLight) typeHelper = new THREE.DirectionalLightHelper(light, 0.6, 0xffc107);
    else if (light.isPointLight) typeHelper = new THREE.PointLightHelper(light, 0.12, 0xffc107);
    // Ambient: kein Wireframe-Helfer vorhanden (→ null)
    if (typeHelper) {
        typeHelper.visible = false;  // Default: Helfer-Linien aus
        group.add(typeHelper);
    }

    const indicator = _buildLightIndicator(light);
    if (indicator) {
        indicator.visible = true;  // Default: an
        group.add(indicator);
    }

    group.spotHelper = typeHelper;
    group.originCone = indicator;  // Name bleibt für Abwärtskompatibilität

    group.update = function() {
        typeHelper?.update?.();
        if (!indicator) return;
        indicator.position.copy(light.position);
        // Ausrichtung: lokale -Y-Achse zeigt in Richtung Target (für Spot/Directional).
        // Point ist omnidirektional, Ambient ungerichtet → keine Rotation.
        if (light.target && (light.isSpotLight || light.isDirectionalLight)) {
            const dir = new THREE.Vector3().subVectors(light.target.position, light.position);
            if (dir.lengthSq() > 1e-6) {
                dir.normalize();
                indicator.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir);
            }
        } else if (light.isAmbientLight) {
            // Ambient: etwas erhöht platzieren damit vom Boden abhebt
            indicator.position.set(light.position.x, (light.position.y || 0) + 0.05, light.position.z);
            indicator.quaternion.identity();
        } else {
            indicator.quaternion.identity();
        }
        // Spot-Winkel geändert → Geometrie neu bauen
        if (light.isSpotLight && indicator._lastAngle !== light.angle) {
            indicator._lastAngle = light.angle;
            const h = _LIGHT_SHAPE_HEIGHT;
            const angle = light.angle ?? Math.PI / 6;
            const radius = Math.min(Math.max(h * Math.tan(angle), 0.05), 1.0);
            indicator.geometry.dispose();
            const geo = new THREE.ConeGeometry(radius, h, 24, 1, true);
            geo.translate(0, -h / 2, 0);
            indicator.geometry = geo;
        }
        indicator.material.color.copy(light.color);
    };
    group.update();
    return group;
}

// Bestimmt lightType-String aus einem THREE.Light-Objekt
export function detectLightType(light) {
    if (!light) return 'spot';
    if (light.isSpotLight) return 'spot';
    if (light.isDirectionalLight) return 'directional';
    if (light.isPointLight) return 'point';
    if (light.isAmbientLight) return 'ambient';
    return 'spot';
}

// Legt Standard-Keyframes an Frame 0 UND am Ende der Timeline an, die die
// aktuellen Licht-Properties einfrieren. Ohne Keyframe ist das Licht aus —
// die Start+End-Paare halten das Licht per Default im gewünschten Zustand.
export function addStandardLightKeyframes(track) {
    _addStandardKeyframe(track);
}
function _addStandardKeyframe(track) {
    if (!track.light) return;
    const light = track.light;
    const tgt = light.target?.position || { x: 0, y: 0, z: 0 };
    const fps = state.project.fps;
    // Ende der Timeline: project.duration * fps, Fallback 10s wenn leer
    const endFrame = Math.max(Math.round((state.project.duration || 10) * fps), 10);

    const makeKF = (name, startFrame) => {
        const kf = new Clip(null, name, 0, fps);
        kf.type = 'light_kf';
        kf.startFrame = startFrame;
        kf.data = {
            position: { x: light.position.x, y: light.position.y, z: light.position.z },
            target:   { x: tgt.x, y: tgt.y, z: tgt.z },
            color: '#' + light.color.getHexString(),
            intensity: light.intensity,
            angle: light.angle ?? null,
            penumbra: light.penumbra ?? null,
            distance: light.distance ?? null,
            fade: true,
            visible: !track.muted,
        };
        return kf;
    };
    // Nur durchnummerierte Namen — keine "Standard Start/Ende" mehr
    track.clips.push(makeKF('1', 0));
    if (endFrame > 0) track.clips.push(makeKF('2', endFrame));
}

// Wendet eine Szenen-Licht-Override-Map auf existierende _sceneLight-Tracks an
// (inkl. Clips). Nutzbar direkt nach createSceneLightTracks() oder bei mid-session
// Project-Load wo die Tracks bereits existieren.
export function applySceneLightOverrides(overrides) {
    if (!overrides) return;
    for (const track of state.project.tracks) {
        if (!track._sceneLight || !track.light) continue;
        const o = overrides[track.name];
        if (!o) continue;
        const light = track.light;
        if (o.color) light.color.set(o.color);
        if (o.intensity != null) light.intensity = o.intensity;
        if (o.position) light.position.set(o.position.x, o.position.y, o.position.z);
        if (o.target && light.target) {
            light.target.position.set(o.target.x, o.target.y, o.target.z);
            light.target.updateMatrixWorld();
        }
        if (o.angle != null && 'angle' in light) light.angle = o.angle;
        if (o.penumbra != null && 'penumbra' in light) light.penumbra = o.penumbra;
        if (o.distance != null && 'distance' in light) light.distance = o.distance;
        track.lightVisible = o.visible ?? false;  // Helfer-Linien: default aus
        track.muted = o.muted ?? false;
        light.visible = !track.muted;
        if (track.lightHelper) {
            track.lightHelper.visible = track.lightVisible && !track.muted;
            track.lightHelper.update?.();
        }
        // Clips nur ersetzen wenn Overrides welche haben, sonst Standard-KFs behalten
        // (Pre-0.40 Saves haben keine clips-Array → Standard Start+Ende bleibt intakt)
        if (Array.isArray(o.clips) && o.clips.length > 0) {
            track.clips = o.clips.map(cd => {
                const kf = new Clip(null, cd.name || 'Licht', 0, state.project.fps);
                kf.type = 'light_kf';
                kf.startFrame = cd.startFrame || 0;
                kf.data = cd.data || {};
                return kf;
            }).sort((a, b) => a.startFrame - b.startFrame);
        }
    }
}

// Erzeugt Light-Tracks für die von createSceneSetup() angelegten Szenen-Lichter.
// Wird NACH restoreProjectData() aufgerufen; wendet dann etwaige gestashte
// Szenen-Licht-Overrides aus dem Save an.
export function createSceneLightTracks() {
    const overrides = state.project._pendingSceneOverrides?.sceneLights;
    // Wenn ein Save geladen wurde (overrides ist definiert, auch wenn {}): nur
    // Lichter anlegen, die im Save vorkommen. Wenn overrides === undefined (neues
    // Projekt, kein Save): alle Default-Szenen-Lichter anlegen.
    const hasSavedState = overrides !== undefined && overrides !== null;
    const sceneLights = [
        { name: 'Key Light',  light: state.sceneKeyLight,  ref: 'sceneKeyLight' },
        { name: 'Fill Light', light: state.sceneFillLight, ref: 'sceneFillLight' },
        { name: 'Back Light', light: state.sceneBackLight, ref: 'sceneBackLight' },
        { name: 'Ambient',    light: state.sceneAmbient,   ref: 'sceneAmbient' },
    ];
    for (const { name, light, ref } of sceneLights) {
        if (!light) continue;
        // Saved project kennt dieses Licht nicht → User hat es gelöscht → aus Szene entfernen
        if (hasSavedState && !(name in overrides)) {
            if (light.target) state.scene.remove(light.target);
            state.scene.remove(light);
            light.dispose?.();
            state[ref] = null;
            continue;
        }
        if (light.isDirectionalLight && light.target && !light.target.parent) {
            state.scene.add(light.target);
        }
        const track = new Track(name);
        track.type = 'light';
        track.color = TRACK_COLORS.light || track.color;
        track.light = light;
        track.lightType = detectLightType(light);
        track.lightVisible = false;  // Helfer-Linien: default aus
        track.coneVisible = true;    // Lichtkegel: default an
        track._sceneLight = true;
        track.lightHelper = createLightHelper(light);
        if (track.lightHelper) {
            state.scene.add(track.lightHelper);
        }
        state.project.addTrack(track);
    }
    applySceneLightOverrides(overrides);
    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
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
    kf.data = {
        position: { x: state.camera.position.x, y: state.camera.position.y, z: state.camera.position.z },
        rotation: { x: state.camera.rotation.x, y: state.camera.rotation.y, z: state.camera.rotation.z },
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

// Pair-Variante: legt ZWEI Keyframes am gleichen Frame an — 'upper' (vor dem Cut)
// und 'lower' (nach dem Cut). Erlaubt harten Zustandswechsel an einer Stelle.
// Visuell werden sie in der Timeline oben/unten versetzt gerendert.
export function addLightKeyframePair(trackIdx, frame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'light' || !track.light) return;
    pushUndo('Lichteigenschaft-Pair');
    const targetFrame = (frame != null) ? frame : state.playheadFrame;
    const makeKF = (position, nameSuffix) => {
        const kf = new Clip(null, `Licht ${track.clips.length + 1} (${nameSuffix})`, 0, state.project.fps);
        kf.type = 'light_kf';
        kf.startFrame = targetFrame;
        const tgt = track.light.target?.position || { x: 0, y: 0, z: 0 };
        kf.data = {
            position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
            target:   { x: tgt.x, y: tgt.y, z: tgt.z },
            color: '#' + track.light.color.getHexString(),
            intensity: track.light.intensity,
            angle: track.light.angle ?? (Math.PI / 6),
            penumbra: track.light.penumbra ?? 0.3,
            distance: track.light.distance ?? 50,
            fade: position === 'upper' ? false : true,  // vor-KF = harter Cut per default
            visible: !track.muted,
            trackPosition: position,  // 'upper' | 'lower' für Render-Offset
        };
        return kf;
    };
    track.clips.push(makeKF('upper', 'vor'));
    track.clips.push(makeKF('lower', 'nach'));
    track.clips.sort((a, b) => {
        if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
        return (a.data?.trackPosition === 'upper' ? 0 : 1) - (b.data?.trackPosition === 'upper' ? 0 : 1);
    });
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    fn.serverLog?.('light_kf_pair_added', `track=${track.name} frame=${targetFrame}`);
}

// Light keyframe helpers
export function addLightKeyframe(trackIdx, frame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'light' || !track.light) return;
    pushUndo('Licht Keyframe');
    const targetFrame = (frame != null) ? frame : state.playheadFrame;
    const kf = new Clip(null, `Licht ${track.clips.length + 1}`, 0, state.project.fps);
    kf.type = 'light_kf';
    kf.startFrame = targetFrame;
    const tgt = track.light.target?.position || { x: 0, y: 0, z: 0 };
    kf.data = {
        position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
        target:   { x: tgt.x, y: tgt.y, z: tgt.z },
        color: '#' + track.light.color.getHexString(),
        intensity: track.light.intensity,
        angle: track.light.angle ?? (Math.PI / 6),
        penumbra: track.light.penumbra ?? 0.3,
        distance: track.light.distance ?? 50,
        fade: true,  // Fade-Effekt: true = interpolieren zum nächsten KF, false = Sprung
        visible: !track.muted,  // Licht An/Aus-State an diesem Keyframe
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    console.log(`[BVH Studio] Licht-Keyframe gespeichert bei Frame ${targetFrame}`);
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
function _sanitizeBoneNames(skeleton) {
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

async function _loadPresetAccessories(track, modelData) {
    // Garments laden
    for (const g of (modelData.garments || [])) {
        try {
            const params = new URLSearchParams({
                garment_id: g.id,
                body_type: track.bodyType || 'Female_Caucasian',
                offset: g.offset || 0,
                stiffness: g.stiffness || 0.5,
                min_dist: g.minDist || 0,
                crotch_floor: g.crotchFloor || 0,
                lift: g.lift || 0,
                crotch_depth: g.crotchDepth || 0,
            });
            // Morphs aus dem Preset übergeben
            if (modelData.morphs) {
                for (const [k, v] of Object.entries(modelData.morphs)) {
                    params.append(`morph_${k}`, v);
                }
            }
            if (modelData.meta) {
                for (const [k, v] of Object.entries(modelData.meta)) {
                    params.append(`meta_${k}`, v);
                }
            }
            const resp = await fetch(`/api/character/garment/fit/?${params}`);
            const data = await resp.json();
            if (data.error) { console.warn(`[BVH Studio] Garment ${g.id} failed:`, data.error); continue; }

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

            const color = g.color || [0.5, 0.5, 0.5];
            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color(color[0], color[1], color[2]),
                roughness: g.roughness ?? 0.7,
                metalness: g.metalness ?? 0.0,
                side: THREE.DoubleSide,
            });

            // Skinning
            if (data.skin_indices && data.skin_weights && track.skeleton) {
                const siBuf = base64ToFloat32(data.skin_indices);
                const swBuf = base64ToFloat32(data.skin_weights);
                geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
                geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
                const skinnedGarment = new THREE.SkinnedMesh(geo, mat);
                skinnedGarment.bind(track.skeleton.skeleton, track.mesh.bindMatrix);
                track.group.add(skinnedGarment);
            } else {
                track.group.add(new THREE.Mesh(geo, mat));
            }
            console.log(`[BVH Studio] Garment loaded: ${g.id}`);
        } catch (e) {
            console.warn(`[BVH Studio] Garment ${g.id} error:`, e);
        }
    }

    // Hair laden
    if (modelData.hair_style?.url) {
        try {
            const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
            const loader = new GLTFLoader();
            const hairUrl = modelData.hair_style.url;
            const gltf = await new Promise((resolve, reject) => loader.load(hairUrl, resolve, undefined, reject));
            const hairGroup = new THREE.Group();

            // Alle Meshes im GLTF an Head-Bone binden
            const headBoneIdx = track.skeleton?.skeleton?.bones.findIndex(b => b.name.includes('spine_006')) ?? -1;
            gltf.scene.traverse(child => {
                if (!child.isMesh) return;
                const geo = child.geometry.clone();

                // Hair-Farbe
                const colorName = modelData.hair_style.color || 'Silken Black';
                const hairColor = ss.hairColorData?.[colorName] || [0.02, 0.02, 0.02];
                const mat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(hairColor[0], hairColor[1], hairColor[2]),
                    roughness: 0.6, metalness: 0.1, side: THREE.DoubleSide,
                });

                if (headBoneIdx >= 0 && track.skeleton) {
                    // Alle Vertices an Head-Bone pinnen
                    const vCount = geo.attributes.position.count;
                    const si = new Float32Array(vCount * 4);
                    const sw = new Float32Array(vCount * 4);
                    for (let v = 0; v < vCount; v++) { si[v * 4] = headBoneIdx; sw[v * 4] = 1.0; }
                    geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(si, 4));
                    geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
                    const skinnedHair = new THREE.SkinnedMesh(geo, mat);
                    skinnedHair.bind(track.skeleton.skeleton, track.mesh.bindMatrix);
                    hairGroup.add(skinnedHair);
                } else {
                    hairGroup.add(new THREE.Mesh(geo, mat));
                }
            });
            track.group.add(hairGroup);
            console.log(`[BVH Studio] Hair loaded: ${modelData.hair_style.name || hairUrl}`);
        } catch (e) {
            console.warn('[BVH Studio] Hair load error:', e);
        }
    }
}

export async function loadTrackCharacter(track) {
    try {
        const modelResp = await fetch(`/api/character/model/${encodeURIComponent(track.preset)}/`);
        const modelData = await modelResp.json();
        track.modelData = modelData;  // cached so Export1 can read bone_parts

        let newMesh = null;

        // Generated model (Rig1-4): Bone-Mesh aus model_generator
        if (modelData.type === 'generated_model') {
            let rigBonesData = null;
            try {
                const rigResp = await fetch('/api/character/rig/');
                if (rigResp.ok) rigBonesData = await rigResp.json();
            } catch (e) {}

            if (rigBonesData && ss.rigifySkeletonData && ss.skinWeightData) {
                const result = generateRigBoneMesh(rigBonesData, modelData, ss.rigifySkeletonData, ss.skinWeightData);
                if (result?.mesh) {
                    newMesh = result.mesh;
                    if (result.skeleton) {
                        track.skeleton = result.skeleton;
                        _sanitizeBoneNames(track.skeleton);
                    }
                }
            }
        }

        // Standard-Mesh (FemaleGarment etc.): SkinnedMesh mit Skin-Weights.
        // Morphs + Meta-Params aus dem Preset an die Mesh-API weiterreichen,
        // sonst kommt immer das Standard-Mesh zurück (Bug: FrauHaarDünn sah aus
        // wie das Default-Modell weil morphs nicht angewendet wurden).
        if (!newMesh) {
            // Preset kann einen abweichenden bodyType haben (z.B. Female_Asian) —
            // dann überschreibt der Preset den Track-Default.
            const effectiveBodyType = modelData.body_type || track.bodyType;
            track.bodyType = effectiveBodyType;
            const params = new URLSearchParams();
            params.set('body_type', effectiveBodyType);
            const morphs = modelData.morphs || {};
            for (const [k, v] of Object.entries(morphs)) {
                if (v !== 0) params.set(`morph_${k}`, v);
            }
            const meta = modelData.meta || {};
            for (const [k, v] of Object.entries(meta)) {
                if (v !== 0) params.set(`meta_${k}`, v);
            }
            const resp = await fetch(`/api/character/mesh/?${params}`);
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
                newMesh = new THREE.Mesh(geo, materials);
            } else {
                newMesh = new THREE.Mesh(geo, materials[0]);
            }

            const { skinIndices, skinWeights } = computeSkinAttributes(geo, ss.skinWeightData);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

            track.skeleton = buildRigifySkeleton(ss.rigifySkeletonData, ss.skinWeightData);
            _sanitizeBoneNames(track.skeleton);
            const skinnedMesh = new THREE.SkinnedMesh(geo, newMesh.material);
            skinnedMesh.add(track.skeleton.rootBone);
            skinnedMesh.bind(track.skeleton.skeleton);
            newMesh = skinnedMesh;
        }

        // Vorherige Meshes aus Group entfernen (nicht disposen — könnten gecacht sein)
        while (track.group.children.length > 0) track.group.remove(track.group.children[0]);
        track.mesh = newMesh;
        // Mesh selbst immer visible — die track.group.visible wird von
        // applyModelTrack/applyBvhTrack gesteuert (deckt Mesh + Garments + Hair ab).
        track.mesh.visible = true;
        track.group.add(newMesh);
        track.mixer = new THREE.AnimationMixer(newMesh);
        track._activeClip = null;
        track._activeAction = null;

        // Garments und Hair aus Preset laden (falls vorhanden)
        if (modelData.garments || modelData.hair_style) {
            await _loadPresetAccessories(track, modelData);
        }

        console.log(`[BVH Studio] Character loaded: ${track.preset} for ${track.name}`);

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
