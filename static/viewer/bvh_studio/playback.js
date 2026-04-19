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

// Preload-Cache: lädt Preset-Assets im Hintergrund via Shadow-Track.
// Resolved zu {group, mesh, skeleton, mixer}. Beim Switch wird die vorbereitete
// Gruppe atomic in den echten Track übernommen.
async function _preloadPreset(animTrack, preset) {
    if (!animTrack._preloadCache) animTrack._preloadCache = {};
    if (animTrack._preloadCache[preset]) return animTrack._preloadCache[preset];
    const shadow = {
        name: `${animTrack.name}_preload_${preset}`,
        type: animTrack.type,
        preset: preset,
        bodyType: animTrack.bodyType,
        group: new THREE.Group(),
    };
    shadow.group.visible = false;
    state.scene.add(shadow.group);
    const promise = fn.loadTrackCharacter(shadow).then(() => ({
        group: shadow.group, mesh: shadow.mesh, skeleton: shadow.skeleton, mixer: shadow.mixer,
    })).catch(e => {
        state.scene.remove(shadow.group);
        delete animTrack._preloadCache[preset];
        throw e;
    });
    animTrack._preloadCache[preset] = promise;
    return promise;
}

function _swapToPreloaded(animTrack, assets, activePreset) {
    // Alte Group aus Szene entfernen (Meshes werden weiter unten disposed bei Bedarf)
    if (animTrack.group) {
        state.scene.remove(animTrack.group);
        // Dispose alte Kinder (altes Preset wird nicht mehr gebraucht)
        animTrack.group.traverse?.(obj => {
            if (obj.geometry) obj.geometry.dispose?.();
            if (obj.material) {
                if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose?.());
                else obj.material.dispose?.();
            }
        });
    }
    animTrack.group = assets.group;
    animTrack.group.visible = true;
    animTrack.mesh = assets.mesh;
    animTrack.skeleton = assets.skeleton;
    animTrack.mixer = assets.mixer;
    animTrack._activeClip = null;
    animTrack._activeAction = null;
    animTrack.meshActive = activePreset;
    animTrack._loadingPreset = null;
    if (animTrack._preloadCache) delete animTrack._preloadCache[activePreset];
    fn.serverLog('preset_swap_preloaded', `track=${animTrack.name} preset=${activePreset}`);
}

// Prüft Model-Tracks: startet Preload für Presets die demnächst aktiv werden.
function _schedulePreloads(t) {
    const lookahead = state.project.preloadSeconds;
    if (!lookahead || lookahead <= 0) return;
    for (const track of state.project.tracks) {
        if (track.type !== 'model') continue;
        const animTrack = state.project.getLinkedAnimation(track);
        if (!animTrack) continue;
        for (const clip of track.clips) {
            if (clip.type !== 'model' || !clip.data?.preset) continue;
            const cs = clip.startFrame / state.project.fps;
            // Clip beginnt innerhalb lookahead-Fensters — bereits geladen oder am Laden? Skip.
            if (cs > t && cs - t <= lookahead) {
                const preset = clip.data.preset;
                if (animTrack.meshActive === preset) continue;
                if (animTrack._loadingPreset === preset) continue;
                if (animTrack._preloadCache?.[preset]) continue;
                _preloadPreset(animTrack, preset).catch(() => {});
            }
        }
    }
}

export function applyPlayhead() {
    const t = state.playheadFrame / state.project.fps;

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

    for (const track of state.project.tracks) {
        if (track.muted) continue;
        if (track.type === 'bvh') applyBvhTrack(track, t);
        else if (track.type === 'model') applyModelTrack(track, t);
        else if (track.type === 'camera') applyCameraTrack(track, t);
        else if (track.type === 'light') applyLightTrack(track, t);
        else if (track.type === 'audio') applyAudioTrack(track, t);
    }
}

function applyBvhTrack(track, t) {
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
    // OrbitControls NICHT deaktivieren — User möchte während Play die Kamera manuell bewegen können.
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

    const lerp = (a, b, al) => a + (b - a) * al;
    if (prev === next) {
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

function applyModelTrack(track, t) {
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
                    console.warn(`[Audio] "${clip.data?.fileName}" nicht geladen — bitte Audio-Datei erneut hinzufügen`);
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
