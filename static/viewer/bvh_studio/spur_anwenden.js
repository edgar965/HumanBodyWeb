/**
 * Spuren am Abspielkopf anwenden: BVH, Kamera, Licht, Ton, Modell, Objekt.
 *
 * Aus playback.js herausgeloest (Umbau 16.08.2026): Die Datei hatte 637 Zeilen
 * und zwei Aufgaben — die Wiedergabe steuern und je Spurart auswerten, was an
 * dieser Stelle der Zeitleiste gilt. Das Zweite ist der groessere Teil.
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _swapToPreloaded } from './vorladen.js';


export function applySceneObjectTrack(track, t) {
    if (!track.mesh) return;
    // Boden ist immer sichtbar (außer muted)
    if (track.subtype === 'floor') {
        track.mesh.visible = !track.muted;
        return;
    }
    // Custom 3D-Objekte: visible solange mindestens ein Clip existiert
    // (ermöglicht Click-Selection + Alt+Klick-Positionierung auch ohne Play)
    const hasClips = track.clips.some(c => c.type === 'object_clip');
    track.mesh.visible = hasClips && !track.muted;
}

export function applyBvhTrack(track, t) {
    if (!track.mixer) {
        // Status-Log nur wenn sich Zustand geändert hat
        if (track._lastLogState !== 'no-mixer') {
            track._lastLogState = 'no-mixer';
            fn.serverLog('bvh_no_mixer', `track=${track.name} mesh=${!!track.mesh} preset=${track.preset}`);
        }
        return;
    }
    let found = false;
    for (const clip of track.clips) {
        if (!clip.animClip) {
            // Diagnose: clip ohne animClip = Retarget fehlgeschlagen oder noch nicht geladen
            if (!clip._noAnimClipLogged) {
                clip._noAnimClipLogged = true;
                fn.serverLog('bvh_clip_no_animclip', `track=${track.name} clip=${clip.name} cat=${clip.category}`);
            }
            continue;
        }
        const clipStart = clip.startFrame / state.project.fps;
        const clipEnd = clipStart + clip.duration;
        if (t >= clipStart && t < clipEnd) {
            const localT = (t - clipStart) * clip.speed + clip.trimIn / clip.fps;
            if (track._activeClip !== clip) {
                track.mixer.stopAllAction();
                if (track._activeClip?.animClip) track.mixer.uncacheClip(track._activeClip.animClip);
                track._activeAction = track.mixer.clipAction(clip.animClip);
                track._activeAction.setLoop(THREE.LoopRepeat, Infinity);
                track._activeAction.clampWhenFinished = false;
                track._activeAction.play();
                track._activeClip = clip;
                fn.serverLog('bvh_action_start',
                    `track=${track.name} clip=${clip.name} t=${t.toFixed(2)}s localT=${localT.toFixed(2)}s ` +
                    `trackCount=${clip.animClip.tracks.length} mixerRoot=${track.mixer.getRoot()?.name||'?'} ` +
                    `meshSkel=${!!track.mesh?.skeleton}`);
            } else if (!track._activeAction.isRunning()) {
                track._activeAction.reset();
                track._activeAction.play();
                fn.serverLog('bvh_action_resume', `track=${track.name} clip=${clip.name}`);
            }
            track._activeAction.time = localT;
            track.mixer.setTime(localT);
            found = true;
            track._lastLogState = 'playing';
            break;
        }
    }
    if (!found && track._activeClip) {
        track.mixer.stopAllAction();
        const stoppedClip = track._activeClip;
        track._activeClip = null;
        track._activeAction = null;
        if (track.skeleton) track.skeleton.skeleton.pose();
        fn.serverLog('bvh_action_stop', `track=${track.name} clip=${stoppedClip.name} t=${t.toFixed(2)}s (out of range)`);
        track._lastLogState = 'stopped';
    } else if (!found && track._lastLogState !== 'no-clip-in-range') {
        // Nichts in Range, kein active clip
        const ranges = track.clips.map(c => `${c.name}@${(c.startFrame/state.project.fps).toFixed(1)}-${((c.startFrame/state.project.fps)+c.duration).toFixed(1)}s`).join(',');
        fn.serverLog('bvh_no_clip_in_range', `track=${track.name} t=${t.toFixed(2)}s clips=[${ranges||'none'}]`);
        track._lastLogState = 'no-clip-in-range';
    }
    if (!track._modelControlled && track.group) {
        track.group.visible = found;
    }
}

export function applyCameraTrack(track, t) {
    if (!track.cameraActive || track.clips.length === 0) return;
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

    // Fade-Effekt aus = Sprung bei diesem KF (keine Interpolation vom prev zu diesem)
    const noFade = prev.data.fade === false;
    const getQuat = (d) => {
        // Prefer the stored quaternion — it is unambiguous. Fall back to
        // the Euler values for older projects that only wrote x/y/z.
        if (d.quaternion) {
            return new THREE.Quaternion(d.quaternion.x, d.quaternion.y, d.quaternion.z, d.quaternion.w);
        }
        return new THREE.Quaternion().setFromEuler(
            new THREE.Euler(d.rotation.x, d.rotation.y, d.rotation.z),
        );
    };
    // LookAt-Interpolation: wenn beide Keyframes ein lookAt-Target haben,
    // fahren wir die Kamera so, dass sie während des Flugs auf den
    // interpolierten Target-Punkt schaut (position + target linear lerp,
    // dann camera.lookAt(target)). Das ist die "Maya-Cam"-Semantik und
    // verhindert, dass die Kamera mitten im Flug am Motiv vorbeischaut —
    // der Hauptgrund für "Kamera bewegt sich wirr durch die Szene".
    const hasLookAt = prev.data.lookAt && next.data.lookAt;
    if (prev === next || noFade) {
        // Exakt auf prev (kein Interpolieren)
        state.camera.position.set(prev.data.position.x, prev.data.position.y, prev.data.position.z);
        if (prev.data.lookAt) {
            state.camera.lookAt(prev.data.lookAt.x, prev.data.lookAt.y, prev.data.lookAt.z);
        } else {
            state.camera.quaternion.copy(getQuat(prev.data));
        }
        state.camera.fov = prev.data.fov;
    } else {
        const alpha = (frame - prev.startFrame) / (next.startFrame - prev.startFrame);
        const interp = prev.data.interpolation || 'linear';
        const t = interp === 'smooth' ? alpha * alpha * (3 - 2 * alpha) : (interp === 'step' ? 0 : alpha);
        state.camera.position.lerpVectors(
            new THREE.Vector3(prev.data.position.x, prev.data.position.y, prev.data.position.z),
            new THREE.Vector3(next.data.position.x, next.data.position.y, next.data.position.z), t);
        if (hasLookAt) {
            const target = new THREE.Vector3().lerpVectors(
                new THREE.Vector3(prev.data.lookAt.x, prev.data.lookAt.y, prev.data.lookAt.z),
                new THREE.Vector3(next.data.lookAt.x, next.data.lookAt.y, next.data.lookAt.z), t,
            );
            state.camera.lookAt(target);
        } else {
            // Legacy-Fallback: Quaternion-Slerp mit Short-Arc-Korrektur
            const qPrev = getQuat(prev.data);
            const qNext = getQuat(next.data);
            if (qPrev.dot(qNext) < 0) {
                qNext.set(-qNext.x, -qNext.y, -qNext.z, -qNext.w);
            }
            const qResult = new THREE.Quaternion().slerpQuaternions(qPrev, qNext, t);
            state.camera.quaternion.copy(qResult);
        }
        state.camera.fov = prev.data.fov + (next.data.fov - prev.data.fov) * t;
    }
    state.camera.updateProjectionMatrix();
    // OrbitControls NICHT deaktivieren — User möchte während Play die Kamera manuell bewegen können.
}

export function applyLightTrack(track, t) {
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

    const lerp = (a, b, al) => a + (b - a) * al;
    // Fade-Effekt aus = Sprung (kein Interpolieren vom prev zu diesem KF)
    // Gleicher Frame (Pair upper+lower) = keine Interpolation möglich → prev-Werte
    const noFade = prev.data.fade === false;
    const sameFrame = prev.startFrame === next.startFrame;
    if (prev === next || noFade || sameFrame) {
        const d = prev.data;
        track.light.position.set(d.position.x, d.position.y, d.position.z);
        if (d.target && track.light.target) track.light.target.position.set(d.target.x, d.target.y, d.target.z);
        track.light.color.set(d.color);
        track.light.intensity = d.intensity;
        if (d.angle != null) track.light.angle = d.angle;
        if (d.penumbra != null) track.light.penumbra = d.penumbra;
        if (d.distance != null) track.light.distance = d.distance;
    } else {
        const alpha = (frame - prev.startFrame) / (next.startFrame - prev.startFrame);
        const pp = prev.data, nn = next.data;
        track.light.position.lerpVectors(
            new THREE.Vector3(pp.position.x, pp.position.y, pp.position.z),
            new THREE.Vector3(nn.position.x, nn.position.y, nn.position.z), alpha);
        if (pp.target && nn.target && track.light.target) {
            track.light.target.position.lerpVectors(
                new THREE.Vector3(pp.target.x, pp.target.y, pp.target.z),
                new THREE.Vector3(nn.target.x, nn.target.y, nn.target.z), alpha);
        }
        track.light.color.lerpColors(new THREE.Color(pp.color), new THREE.Color(nn.color), alpha);
        track.light.intensity = lerp(pp.intensity, nn.intensity, alpha);
        if (pp.angle != null && nn.angle != null) track.light.angle = lerp(pp.angle, nn.angle, alpha);
        if (pp.penumbra != null && nn.penumbra != null) track.light.penumbra = lerp(pp.penumbra, nn.penumbra, alpha);
        if (pp.distance != null && nn.distance != null) track.light.distance = lerp(pp.distance, nn.distance, alpha);
    }
    if (track.light.target) track.light.target.updateMatrixWorld();
    if (track.lightHelper && track.lightHelper.update) track.lightHelper.update();
}

export function applyModelTrack(track, t) {
    const animTrack = state.project.getLinkedAnimation(track);
    if (!animTrack) return;

    // Welches Preset ist gerade aktiv?
    let activePreset = null;
    for (const clip of track.clips) {
        if (clip.type !== 'model') continue;
        const cs = clip.startFrame / state.project.fps;
        const ce = cs + clip.duration;
        if (t >= cs && t < ce) { activePreset = clip.data?.preset; break; }
    }

    // Während eines asynchronen Ladevorgangs nichts tun — sonst setzen wir
    // die alte Group fälschlich auf visible, bevor das neue Preset fertig ist.
    if (animTrack._loadingPreset) {
        if (animTrack.group) animTrack.group.visible = false;
        return;
    }

    // Nichts geändert → Sichtbarkeit der Group an aktives Preset angleichen.
    if (activePreset === animTrack.meshActive) {
        if (animTrack.group) animTrack.group.visible = !!activePreset;
        return;
    }

    // Preset hat gewechselt → Group verstecken
    if (animTrack.group) animTrack.group.visible = false;

    if (!activePreset) {
        animTrack.meshActive = null;
        return;
    }

    // Preload-Cache prüfen: ist Preset bereits vorbereitet?
    const cached = animTrack._preloadCache?.[activePreset];
    if (cached) {
        animTrack._loadingPreset = activePreset;
        Promise.resolve(cached).then(assets => {
            if (animTrack._loadingPreset !== activePreset) return;  // überholt
            _swapToPreloaded(animTrack, assets, activePreset);
        }).catch(e => {
            animTrack._loadingPreset = null;
            fn.serverLog('preset_load_failed', `track=${animTrack.name} preset=${activePreset} err=${e.message}`);
        });
        return;
    }

    // Kein Preload → normaler async Load in die echte Track-Group
    animTrack._loadingPreset = activePreset;
    animTrack.preset = activePreset;
    if (animTrack.group) animTrack.group.visible = false;
    fn.serverLog('preset_load_start', `track=${animTrack.name} preset=${activePreset}`);
    fn.loadTrackCharacter(animTrack).then(() => {
        if (animTrack._loadingPreset !== activePreset) {
            fn.serverLog('preset_load_superseded', `track=${animTrack.name} preset=${activePreset} now=${animTrack._loadingPreset}`);
            return;
        }
        animTrack._loadingPreset = null;
        if (animTrack.mesh) {
            if (animTrack.group) animTrack.group.visible = true;
            animTrack._activeClip = null;
            animTrack._activeAction = null;
            animTrack.meshActive = activePreset;
            fn.serverLog('preset_load_done',
                `track=${animTrack.name} preset=${activePreset} ` +
                `mesh=${!!animTrack.mesh} skel=${!!animTrack.skeleton} mix=${!!animTrack.mixer} ` +
                `meshSkel=${!!animTrack.mesh?.skeleton} bones=${animTrack.skeleton?.skeleton?.bones?.length||'?'}`);
        } else {
            fn.serverLog('preset_load_no_mesh', `track=${animTrack.name} preset=${activePreset}`);
        }
    }).catch(e => {
        animTrack._loadingPreset = null;
        fn.serverLog('preset_load_failed', `track=${animTrack.name} preset=${activePreset} err=${e.message}`);
    });
}
