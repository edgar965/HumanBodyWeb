/**
 * BVH Studio — Project save/load, session state, animation preview.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { state, SESSION_KEY } from './state.js';
import { fn } from './registry.js';
import { Timeline, Clip } from './models.js';
import { undoStack, redoStack } from './undo.js';
import { sharedState } from '../character_core.js?v=1';
import { generateRigBoneMesh } from '../model_generator.js';
import { _gaussSmooth, _gaussFilter } from './tools.js';

const ss = sharedState;

// =========================================================================
// Studio-Info (top-right label): always shows the current project name;
// transient messages (save/load/undo) flash briefly and revert.
// =========================================================================
let _studioInfoFlashTimer = null;
export function updateStudioInfo() {
    const el = document.getElementById('studio-info');
    if (!el) return;
    if (_studioInfoFlashTimer) return;  // a flash is active; respect it
    const name = state.project?.name || 'Untitled';
    el.textContent = `Projekt: ${name}`;
}
export function flashStudioInfo(text, ms = 2500) {
    const el = document.getElementById('studio-info');
    if (!el) return;
    el.textContent = text;
    if (_studioInfoFlashTimer) clearTimeout(_studioInfoFlashTimer);
    _studioInfoFlashTimer = setTimeout(() => {
        _studioInfoFlashTimer = null;
        updateStudioInfo();
    }, ms);
}
fn.updateStudioInfo = updateStudioInfo;
fn.flashStudioInfo = flashStudioInfo;

// Preview system variables
let _previewModal = null;
let _previewRenderer = null;
let _previewScene = null;
let _previewCamera = null;
let _previewControls = null;
let _previewMixer = null;
let _previewAction = null;
let _previewClock = null;
let _previewAnimId = null;
let _previewCategory = null;
let _previewName = null;

// Sammelt Licht-Properties der Szenen-Lichter (Key/Fill/Back/Ambient + Theatre-Presets)
// als Dictionary {name: {props, clips}} für Save-Roundtrip.
function _buildSceneLightOverrides() {
    const out = {};
    for (const t of state.project.tracks) {
        if (t.type !== 'light' || !t._sceneLight || !t.light) continue;
        out[t.name] = {
            color: '#' + t.light.color.getHexString(),
            intensity: t.light.intensity,
            position: { x: t.light.position.x, y: t.light.position.y, z: t.light.position.z },
            target: t.light.target ? { x: t.light.target.position.x, y: t.light.target.position.y, z: t.light.target.position.z } : null,
            angle: t.light.angle ?? null,
            penumbra: t.light.penumbra ?? null,
            distance: t.light.distance ?? null,
            visible: t.lightVisible,
            coneVisible: t.coneVisible !== false,
            muted: t.muted,
            clips: t.clips.map(c => {
                if (c.type !== 'light_kf') return null;
                return {
                    type: 'light_kf', name: c.name, startFrame: c.startFrame,
                    data: c.data,
                };
            }).filter(Boolean),
        };
    }
    return out;
}

function _buildSceneFloorOverrides() {
    for (const t of state.project.tracks) {
        if (t.type === 'scene_object' && t.subtype === 'floor') {
            const w = t.floorWidth ?? t.floorSize ?? 6;
            const l = t.floorLength ?? t.floorSize ?? 6;
            return {
                color: t.floorColor || '#3a3a4a',
                texture: t.floorTexture || 'none',
                roughness: t.floorRoughness ?? 0.9,
                metalness: t.floorMetalness ?? 0.05,
                width: w,
                length: l,
                centerX: t.mesh?.position?.x ?? 0,
                centerZ: t.mesh?.position?.z ?? 0,
                size: Math.max(w, l),  // Legacy-Feld für Abwärtskompatibilität
                muted: t.muted,
                gridVisible: state.gridVisible !== false,
            };
        }
    }
    return null;
}

export function buildProjectData() {
    return {
        name: state.project.name,
        fps: state.project.fps,
        // Szenen-Lichter + Boden werden SEPARAT (nicht in tracks[]) gespeichert
        // damit User-Tracks keine Index-Drift erleiden (_linkedAnimIdx bleibt stabil).
        sceneLights: _buildSceneLightOverrides(),
        sceneFloor: _buildSceneFloorOverrides(),
        tracks: state.project.tracks.filter(t => !t._sceneLight && !t._sceneItem).map(t => {
            const td = {
                name: t.name, type: t.type, preset: t.preset, bodyType: t.bodyType,
                color: t.color, muted: t.muted, position: t.position,
            };
            if (t.type === 'model') { td._linkedAnimIdx = t._linkedAnimIdx; td._currentPreset = t._currentPreset; }
            if (t.type === 'camera') td.cameraActive = t.cameraActive;
            if (t.type === 'light' && t.light) {
                td.lightColor = '#' + t.light.color.getHexString();
                td.lightIntensity = t.light.intensity;
                td.lightPosition = { x: t.light.position.x, y: t.light.position.y, z: t.light.position.z };
                if (t.light.target) {
                    td.lightTarget = { x: t.light.target.position.x, y: t.light.target.position.y, z: t.light.target.position.z };
                }
                if (t.light.angle != null) td.lightAngle = t.light.angle;
                if (t.light.penumbra != null) td.lightPenumbra = t.light.penumbra;
                if (t.light.distance != null) td.lightDistance = t.light.distance;
                td.lightVisible = t.lightVisible;
                td.coneVisible = t.coneVisible !== false;  // default true
                td.lightType = t.lightType;
                td._sceneLight = !!t._sceneLight;
            }
            if (t.type === 'scene_object' && t.subtype === 'custom' && t.mesh) {
                td.objectTint = t.objectTint || '#ffffff';
                td.objectPosition = { x: t.mesh.position.x, y: t.mesh.position.y, z: t.mesh.position.z };
                td.objectRotation = { x: t.mesh.rotation.x, y: t.mesh.rotation.y, z: t.mesh.rotation.z };
                td.objectScale = t.mesh.scale.x;  // uniform scale
            }
            td.clips = t.clips.map(c => {
                const cd = {
                    type: c.type, category: c.category, name: c.name,
                    totalFrames: c.totalFrames, fps: c.fps, startFrame: c.startFrame,
                    trimIn: c.trimIn, trimOut: c.trimOut, speed: c.speed,
                    smoothSigma: c.smoothSigma, groundFix: c.groundFix,
                    blendIn: c.blendIn, blendOut: c.blendOut,
                };
                if (c.type === 'camera_kf' || c.type === 'light_kf') cd.data = c.data;
                else if (c.type === 'model') cd.data = { preset: c.data.preset, bodyType: c.data.bodyType };
                else if (c.type === 'audio') cd.data = { fileName: c.data.fileName, audioUrl: c.data.audioUrl, audioDuration: c.data.audioDuration, volume: c.data.volume, fadeIn: c.data.fadeIn, fadeOut: c.data.fadeOut, offset: c.data.offset };
                else if (c.type === 'object_clip') cd.data = { url: c.data?.url, ext: c.data?.ext, fileName: c.data?.fileName, mtlUrl: c.data?.mtlUrl || null };
                return cd;
            });
            return td;
        }),
    };
}

export async function saveProject() {
    // Save to configured project path on server
    const dir = state.project.projectPath;
    if (!dir) { saveProjectAs(); return; }
    const filename = (state.project.name || 'project').replace(/[^a-zA-Z0-9_\-]/g, '_') + '.studio.json';
    const sep = dir.includes('\\') ? '\\' : '/';
    const fullPath = dir.replace(/[/\\]$/, '') + sep + filename;

    try {
        const resp = await fetch('/api/studio/project-save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: fullPath, project: buildProjectData() }),
        });
        const result = await resp.json();
        if (result.ok) {
            state.project._lastSavePath = result.path;
            try { localStorage.setItem('bvhStudio_lastProject', result.path); } catch(e) {}
            console.log(`[BVH Studio] Project saved: ${result.path}`);
            flashStudioInfo(`Gespeichert: ${filename}`);
        } else {
            alert('Speichern fehlgeschlagen: ' + (result.error || 'Unbekannter Fehler'));
        }
    } catch (e) {
        alert('Speichern fehlgeschlagen: ' + e.message);
    }
}

export async function saveProjectAs() {
    const dir = state.project.projectPath || '';
    const name = prompt(`Projektname speichern unter:\n(Ordner: ${dir || 'nicht konfiguriert'})`, state.project.name || 'project');
    if (!name) return;
    state.project.name = name;
    await saveProject();
}

export async function loadProject() {
    const dir = state.project.projectPath;
    if (dir) {
        // Show project list from configured directory
        try {
            const resp = await fetch(`/api/studio/project-list/?dir=${encodeURIComponent(dir)}`);
            const result = await resp.json();
            if (result.files && result.files.length > 0) {
                const names = result.files.map(f => f.name);
                const choice = prompt(`Projekte in ${dir}:\n\n${names.map((n, i) => `${i + 1}. ${n}`).join('\n')}\n\nNummer eingeben:`, '1');
                if (!choice) return;
                const idx = parseInt(choice) - 1;
                if (idx < 0 || idx >= result.files.length) { alert('Ungueltige Auswahl.'); return; }
                const loadResp = await fetch(`/api/studio/project-load/?path=${encodeURIComponent(result.files[idx].path)}`);
                const loadResult = await loadResp.json();
                if (loadResult.ok) {
                    await restoreProjectData(loadResult.project);
                    state.project._lastSavePath = loadResult.path;
                    try { localStorage.setItem('bvhStudio_lastProject', loadResult.path); } catch(e) {}
                    flashStudioInfo(`Geladen: ${result.files[idx].name}`);
                    updateStudioInfo();
                    return;
                } else {
                    alert('Laden fehlgeschlagen: ' + (loadResult.error || ''));
                }
            } else {
                alert(`Keine Projekte in ${dir} gefunden.\nDatei manuell wählen...`);
            }
        } catch (e) { /* fall through to file picker */ }
    }

    // Fallback: browser file picker
    const input = document.createElement('input');
    input.type = 'file'; input.accept = '.json,.studio.json';
    input.addEventListener('change', async () => {
        const file = input.files[0];
        if (!file) return;
        try {
            const data = JSON.parse(await file.text());
            await restoreProjectData(data);
        } catch (e) {
            alert('Projekt laden fehlgeschlagen: ' + e.message);
        }
    });
    input.click();
}

export async function restoreProjectData(data) {
    console.log(`[Restore] Starting. Input tracks: ${data.tracks?.length}, clips: ${data.tracks?.map(t=>t.clips?.length)}`);
    // Suppress undo for the ENTIRE restore operation
    state._undoSuppressed = true;

    // Alte Saves könnten _sceneLight-/_sceneItem-Tracks enthalten — filtern wir raus,
    // damit createSceneLightTracks/createFloorTrack die Szenen-Elemente frisch anlegen.
    const inputTracks = (data.tracks || []).filter(td => !(td._sceneLight || td._sceneItem));

    // Clear existing tracks (including any old scene lights aus vorheriger Init-Reihenfolge)
    for (let i = state.project.tracks.length - 1; i >= 0; i--) {
        fn.removeTrack(i);
    }

    state.project.name = data.name || 'Untitled';
    state.project.fps = data.fps || 30;

    // Szenen-Overrides stashen — werden in createSceneLightTracks/createFloorTrack angewandt.
    // WICHTIG: undefined (Legacy-Save ohne sceneLights-Feld) → Defaults erzeugen.
    //          {} (Save mit explizit leerem Licht-Dict) → ALLE Lichter gelöscht, nichts erzeugen.
    state.project._pendingSceneOverrides = {
        sceneLights: data.sceneLights,   // undefined bleibt undefined
        sceneFloor: data.sceneFloor || null,
    };

    // Remap-Tabelle: alte Save-Indizes (inkl. ggf. Szenen-Lichtern) → neue Indizes
    // nach Filtern. Wird später auf _linkedAnimIdx angewandt.
    const oldIndexToNew = {};
    let newIdx = 0;
    for (let oldIdx = 0; oldIdx < (data.tracks || []).length; oldIdx++) {
        const td = data.tracks[oldIdx];
        if (td._sceneLight || td._sceneItem) {
            oldIndexToNew[oldIdx] = -1;  // rausgefiltert
        } else {
            oldIndexToNew[oldIdx] = newIdx++;
        }
    }

    const loadPromises = [];

    for (const td of inputTracks) {
        const trackType = td.type || 'bvh';
        // Rename old "Track X" names to "Animation X"
        let trackName = td.name;
        if (trackType === 'bvh' && trackName && /^Track \d+$/.test(trackName)) {
            trackName = trackName.replace('Track', 'Animation');
        }
        let track;
        if (trackType === 'bvh') {
            track = fn.addTrack(trackName, true);  // skip auto model track during restore
            track.preset = td.preset || 'FemaleGarment';
            track.bodyType = td.bodyType || 'Female_Caucasian';
        } else if (trackType === 'model') {
            track = fn.addModelTrack(td.name);
            // Remap saved index → new index (entfernt Scene-Light-Drift)
            const savedLinkIdx = td._linkedAnimIdx ?? -1;
            track._linkedAnimIdx = (savedLinkIdx >= 0 && oldIndexToNew[savedLinkIdx] != null)
                ? oldIndexToNew[savedLinkIdx]
                : -1;
            track._currentPreset = td._currentPreset || null;
        } else {
            track = fn.addSpecialTrack(trackType, td.name);
        }
        track.color = td.color || track.color;
        track.muted = td.muted || false;
        track.position = td.position || [0, 0, 0];
        if (track.group) track.group.position.set(track.position[0], 0, track.position[2]);

        if (trackType === 'camera') track.cameraActive = td.cameraActive ?? true;
        if (trackType === 'light' && track.light && td.lightPosition) {
            track.light.color.set(td.lightColor || '#ffffff');
            track.light.intensity = td.lightIntensity ?? 2;
            track.light.position.set(td.lightPosition.x, td.lightPosition.y, td.lightPosition.z);
            if (track.light.target && td.lightTarget) {
                track.light.target.position.set(td.lightTarget.x, td.lightTarget.y, td.lightTarget.z);
                track.light.target.updateMatrixWorld();
            }
            if (td.lightAngle != null) track.light.angle = td.lightAngle;
            if (td.lightPenumbra != null) track.light.penumbra = td.lightPenumbra;
            if (td.lightDistance != null) track.light.distance = td.lightDistance;
            // Helfer-Linien IMMER aus beim Laden (ignoriert gespeicherten Wert —
            // User will sie per Default off sehen, kann einzeln per Toggle einschalten)
            track.lightVisible = false;
            track.coneVisible = td.coneVisible ?? true;    // default an (Lichtkegel)
            if (track.lightHelper?.update) track.lightHelper.update();
        }

        for (const cd of (td.clips || [])) {
            const clip = new Clip(cd.category, cd.name, cd.totalFrames || 100, cd.fps || 30);
            clip.type = cd.type || 'bvh';
            // Fix broken clips from old splits: clips on model tracks must be type 'model'
            if (trackType === 'model' && clip.type === 'bvh') {
                clip.type = 'model';
                if (!clip.data?.preset) clip.data = { preset: td.preset || 'Rig1', bodyType: td.bodyType || 'Female_Caucasian' };
            }
            clip.startFrame = cd.startFrame || 0;
            clip.trimIn = cd.trimIn || 0;
            clip.trimOut = cd.trimOut || 0;
            clip.speed = cd.speed || 1;
            clip.smoothSigma = cd.smoothSigma || 0;
            clip.groundFix = cd.groundFix || false;
            clip.blendIn = cd.blendIn || 0;
            clip.blendOut = cd.blendOut || 0;
            if (cd.data) clip.data = cd.data;
            track.clips.push(clip);
            if (clip.type === 'bvh') loadPromises.push(fn.loadClipAnimation(track, clip));
            if (clip.type === 'object_clip' && clip.data?.url && track.type === 'scene_object') {
                // 3D-Objekt aus Save wieder laden — _loadSceneObjectIntoTrack erzeugt Mesh + Clip,
                // aber wir HABEN schon einen Clip (gerade eben pushed). Darum: Mesh separat laden
                // und gespeicherte Position/Rotation/Scale anwenden, dann overcounting-Clip entfernen.
                loadPromises.push((async () => {
                    try {
                        const se = await import('./scene_extras.js');
                        // _loadSceneObjectIntoTrack pusht einen NEUEN Clip — wir merken uns den bestehenden
                        // und entfernen den neuen (Duplikat-Schutz).
                        const clipsBefore = track.clips.length;
                        await se._loadSceneObjectIntoTrack(
                            track, clip.data.url, clip.data.fileName || 'object',
                            clip.data.ext || 'obj', clip.startFrame, clip.data.mtlUrl || null
                        );
                        // _loadSceneObjectIntoTrack pushed einen neuen object_clip — entfernen
                        if (track.clips.length > clipsBefore) {
                            track.clips.pop();  // Duplikat weg
                        }
                        // Gespeicherte Transform anwenden (überschreibt Auto-Normalize)
                        if (track.mesh) {
                            if (td.objectPosition) track.mesh.position.set(td.objectPosition.x, td.objectPosition.y, td.objectPosition.z);
                            if (td.objectRotation) track.mesh.rotation.set(td.objectRotation.x, td.objectRotation.y, td.objectRotation.z);
                            if (td.objectScale != null) track.mesh.scale.setScalar(td.objectScale);
                            if (td.objectTint) fn.setObjectTint?.(track, td.objectTint);
                        }
                    } catch (e) {
                        console.warn('[Restore] 3D-Objekt reload failed:', clip.data?.fileName, e);
                    }
                })());
            }
            if (clip.type === 'audio' && clip.data?.audioUrl) {
                // Fix double-slash from old saves
                if (clip.data.audioUrl.startsWith('//')) clip.data.audioUrl = clip.data.audioUrl.substring(1);
                loadPromises.push((async () => {
                    try {
                        if (!track.audioCtx) {
                            track.audioCtx = state.project._audioCtx || (state.project._audioCtx = new (window.AudioContext || window.webkitAudioContext)());
                            track.gainNode = track.audioCtx.createGain();
                            track.gainNode.connect(track.audioCtx.destination);
                        }
                        const resp = await fetch(clip.data.audioUrl);
                        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                        const arrayBuf = await resp.arrayBuffer();
                        clip.data.audioBuffer = await track.audioCtx.decodeAudioData(arrayBuf);
                        clip._needsReload = false;
                        console.log('[Restore] Audio reloaded:', clip.data.fileName);
                    } catch (e) {
                        console.warn('[Restore] Audio reload failed:', clip.data?.fileName, e);
                        clip._needsReload = true;
                    }
                })());
            } else if (clip.type === 'audio') {
                clip._needsReload = true;
                console.warn(`[Restore] Audio "${clip.data?.fileName}" has no server URL — needs manual reload`);
            }
        }
    }

    // Wait for ALL clip animations to load before continuing
    await Promise.all(loadPromises);

    // Fallback: Model-Tracks mit ungültigem _linkedAnimIdx auf ersten BVH-Track linken
    // (z.B. alte Saves wo der Link durch Szenen-Licht-Insertion kaputt ging)
    const firstBvhIdx = state.project.tracks.findIndex(t => t.type === 'bvh');
    if (firstBvhIdx >= 0) {
        for (const t of state.project.tracks) {
            if (t.type !== 'model') continue;
            const linked = state.project.tracks[t._linkedAnimIdx];
            if (!linked || linked.type !== 'bvh') {
                console.log(`[Restore] Model-Track "${t.name}" neu verlinkt (war ${t._linkedAnimIdx}) → ${firstBvhIdx}`);
                t._linkedAnimIdx = firstBvhIdx;
            }
        }
    }

    state._undoSuppressed = false;

    fn.updateDuration();
    fn.renderTimeline();
    fn.updateTrackHeaders();
    fn.applyPlayhead();  // Activate model tracks + show meshes
    console.log(`[BVH Studio] Project restored: ${state.project.name} (${state.project.tracks.length} tracks)`);
    updateStudioInfo();
}

export function resetToDefault() {
    // Clear everything: tracks, session, undo
    state._undoSuppressed = true;
    while (state.project.tracks.length > 0) fn.removeTrack(0);
    state._undoSuppressed = false;

    state.project.name = 'Untitled';
    state.selectedTrackIdx = -1;
    state.selectedClipIdx = -1;
    state.playheadFrame = 0;
    state.playing = false;

    undoStack.length = 0;
    redoStack.length = 0;

    sessionStorage.removeItem(SESSION_KEY);

    fn.updateDuration();
    fn.renderTimeline();
    fn.updateTrackHeaders();
    fn.updatePlaybackUI();
    fn.updateProperties();

    updateStudioInfo();
    fn.serverLog('reset_to_default');
}

export async function loadLastProject() {
    let lastPath = '';
    try { lastPath = localStorage.getItem('bvhStudio_lastProject') || ''; } catch(e) {}
    if (!lastPath) { alert('Kein letztes Projekt gespeichert.'); return; }

    try {
        const resp = await fetch(`/api/studio/project-load/?path=${encodeURIComponent(lastPath)}`);
        const result = await resp.json();
        if (result.ok) {
            await restoreProjectData(result.project);
            state.project._lastSavePath = result.path;
            const name = lastPath.split(/[/\\]/).pop().replace('.studio.json', '');
            flashStudioInfo(`Geladen: ${name}`);
            updateStudioInfo();
            console.log(`[BVH Studio] Last project loaded: ${lastPath}`);
        } else {
            alert('Laden fehlgeschlagen: ' + (result.error || lastPath));
        }
    } catch (e) {
        alert('Laden fehlgeschlagen: ' + e.message);
    }
}

export function saveSessionState() {
    try {
        if (state.project.tracks.length === 0) {
            sessionStorage.removeItem(SESSION_KEY);
            return;
        }
        const sessionData = {
            project: buildProjectData(),
            playheadFrame: state.playheadFrame,
            selectedTrackIdx: state.selectedTrackIdx,
            selectedClipIdx: state.selectedClipIdx,
            timelineZoom: state.timelineZoom,
            timelineScrollX: state.timelineScrollX,
        };
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    } catch (e) { /* storage full or unavailable */ }
}

export async function restoreSessionState() {
    try {
        const raw = sessionStorage.getItem(SESSION_KEY);
        if (!raw) return false;
        const sessionData = JSON.parse(raw);
        if (!sessionData.project || !sessionData.project.tracks || sessionData.project.tracks.length === 0) return false;

        // Only restore BVH tracks that actually have clips
        const validTracks = sessionData.project.tracks.filter(t => t.type !== 'bvh' || (t.clips && t.clips.length > 0));
        if (validTracks.length === 0) {
            sessionStorage.removeItem(SESSION_KEY);
            return false;
        }
        sessionData.project.tracks = validTracks;

        // Pre-Check: Alle Presets die von Model-Clips referenziert werden müssen existieren.
        // Fehlt auch nur einer (z.B. nach Datei-Delete) → Session wegwerfen und Default-Projekt laden.
        const referencedPresets = new Set();
        for (const t of sessionData.project.tracks) {
            if (t.type === 'model') {
                if (t.preset) referencedPresets.add(t.preset);
                for (const c of (t.clips || [])) {
                    if (c.data?.preset) referencedPresets.add(c.data.preset);
                }
            } else if (t.type === 'bvh' && t.preset) {
                referencedPresets.add(t.preset);
            }
        }
        for (const p of referencedPresets) {
            try {
                const r = await fetch(`/api/character/model/${encodeURIComponent(p)}/`);
                if (r.status === 404) {
                    console.warn(`[BVH Studio] Session-Preset "${p}" nicht mehr vorhanden → Session verworfen, Default-Projekt wird geladen.`);
                    sessionStorage.removeItem(SESSION_KEY);
                    return false;
                }
            } catch (e) {
                // Netzwerkfehler → Session behalten (könnte offline sein); echte 404s dürchgreifen oben
                console.warn(`[BVH Studio] Session-Preset-Check "${p}" network error:`, e);
            }
        }

        await restoreProjectData(sessionData.project);

        // Verify restore succeeded: remove tracks that ended up with no working clips
        const brokenTracks = [];
        for (let i = state.project.tracks.length - 1; i >= 0; i--) {
            const t = state.project.tracks[i];
            if (t.type === 'bvh' && t.clips.length === 0 && !t.mesh) {
                brokenTracks.push(i);
            }
            // scene_object custom bundle mit kaputter URL (Upload nicht mehr da) → mesh fehlt
            if (t.type === 'scene_object' && t.subtype === 'custom' && !t.mesh) {
                brokenTracks.push(i);
            }
        }
        if (brokenTracks.length > 0) {
            state._undoSuppressed = true;
            for (const idx of brokenTracks) fn.removeTrack(idx);
            state._undoSuppressed = false;
            console.warn(`[BVH Studio] Removed ${brokenTracks.length} broken tracks from session`);
        }

        if (state.project.tracks.length === 0) {
            sessionStorage.removeItem(SESSION_KEY);
            return false;
        }

        state.playheadFrame = sessionData.playheadFrame || 0;
        state.selectedTrackIdx = sessionData.selectedTrackIdx ?? -1;
        state.selectedClipIdx = sessionData.selectedClipIdx ?? -1;
        state.timelineZoom = sessionData.timelineZoom || 100;
        state.timelineScrollX = sessionData.timelineScrollX || 0;

        const zoomSlider = document.getElementById('tl-zoom');
        if (zoomSlider) zoomSlider.value = state.timelineZoom;
        const zoomLabel = document.getElementById('tl-zoom-label');
        if (zoomLabel) zoomLabel.textContent = `Zoom: ${state.timelineZoom}%`;

        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updatePlaybackUI();
        fn.updateProperties();
        console.log(`[BVH Studio] Session restored: ${state.project.tracks.length} tracks`);
        return true;
    } catch (e) {
        console.warn('[BVH Studio] Session restore failed, clearing:', e);
        sessionStorage.removeItem(SESSION_KEY);
        // Clean up any half-loaded state
        state._undoSuppressed = true;
        while (state.project.tracks.length > 0) fn.removeTrack(0);
        state._undoSuppressed = false;
        return false;
    }
}

// =========================================================================
// Animation Preview Popup (A key)
// =========================================================================
export function previewAnimation(category, name) {
    _previewCategory = category;
    _previewName = name;
    // Create or reuse modal
    if (!_previewModal) {
        _previewModal = document.createElement('div');
        _previewModal.id = 'preview-modal';
        _previewModal.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;';
        _previewModal.innerHTML = `
            <div id="preview-box" style="background:var(--bg-secondary,#1a1a2e);border:1px solid var(--border,#334);border-radius:10px;width:1000px;height:700px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 16px 48px rgba(0,0,0,0.5);resize:both;min-width:500px;min-height:400px;max-width:95vw;max-height:90vh;">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border,#334);">
                    <span id="preview-title" style="font-size:0.9rem;color:#ccc;"></span>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <button id="preview-play" style="background:none;border:1px solid var(--border,#334);border-radius:4px;color:#ccc;cursor:pointer;padding:4px 10px;font-size:0.8rem;"><i class="fas fa-play" id="preview-play-icon"></i></button>
                        <span id="preview-frame" style="font-size:0.75rem;color:#888;">0 / 0</span>
                        <button id="preview-save-smooth" style="background:none;border:1px solid var(--border,#334);border-radius:4px;color:#4caf50;cursor:pointer;padding:4px 10px;font-size:0.75rem;" title="Smooth permanent auf BVH speichern"><i class="fas fa-save"></i> Smooth speichern</button>
                        <button id="preview-close" style="background:none;border:none;color:#888;cursor:pointer;font-size:1.2rem;">&times;</button>
                    </div>
                </div>
                <canvas id="preview-canvas" style="flex:1;width:100%;"></canvas>
            </div>`;
        document.body.appendChild(_previewModal);

        // Close handlers
        document.getElementById('preview-close').addEventListener('click', closePreview);
        document.getElementById('preview-save-smooth').addEventListener('click', async () => {
            if (!_gaussSmooth.active) { alert('Smooth ist nicht aktiv.\nBitte erst Tools > Smooth EINSCHALTEN.'); return; }
            if (!_previewCategory || !_previewName) { alert('Keine Animation geladen.'); return; }
            const sigma = _gaussSmooth.sigma;
            try {
                const resp = await fetch('/api/retarget/smooth-bvh/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: _previewCategory, name: _previewName, sigma }),
                });
                const result = await resp.json();
                if (result.ok) {
                    fn.serverLog('gauss_saved_preview', `${_previewCategory}/${_previewName} sigma=${sigma} frames=${result.frames}`);
                    alert(`Smooth (σ=${sigma}) gespeichert: ${_previewCategory}/${_previewName}\n${result.frames} Frames geglättet.`);
                } else {
                    alert('Fehler: ' + (result.error || 'Unbekannt'));
                }
            } catch(e) { alert('Fehler: ' + e.message); }
        });
        _previewModal.addEventListener('click', (e) => { if (e.target === _previewModal) closePreview(); });
        document.getElementById('preview-play').addEventListener('click', () => {
            if (_previewAction) {
                if (_previewAction.paused || !_previewAction.isRunning()) {
                    _previewAction.paused = false;
                    _previewAction.play();
                    document.getElementById('preview-play-icon').className = 'fas fa-pause';
                } else {
                    _previewAction.paused = true;
                    document.getElementById('preview-play-icon').className = 'fas fa-play';
                }
            }
        });

        // Setup Three.js
        const canvas = document.getElementById('preview-canvas');
        _previewRenderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        _previewRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        _previewScene = new THREE.Scene();
        _previewScene.background = new THREE.Color(0x1a1a2e);
        _previewCamera = new THREE.PerspectiveCamera(50, 700/440, 0.01, 500);
        _previewCamera.position.set(0, 1, 3);
        _previewControls = new OrbitControls(_previewCamera, canvas);
        _previewControls.target.set(0, 0.8, 0);
        _previewControls.update();

        // Lights
        const dl = new THREE.DirectionalLight(0xffffff, 2);
        dl.position.set(2, 4, 3);
        _previewScene.add(dl);
        _previewScene.add(new THREE.AmbientLight(0x404060, 1.5));

        // Grid
        _previewScene.add(new THREE.GridHelper(4, 20, 0x333355, 0x222244));

        _previewClock = new THREE.Clock();
    }

    // Show modal
    _previewModal.style.display = 'flex';
    document.getElementById('preview-title').textContent = `${category} / ${name}`;
    document.getElementById('preview-play-icon').className = 'fas fa-pause';

    // Restore saved size
    const box = document.getElementById('preview-box');
    try {
        const saved = JSON.parse(localStorage.getItem('bvhStudio_previewSize'));
        if (saved?.w && saved?.h) { box.style.width = saved.w + 'px'; box.style.height = saved.h + 'px'; }
    } catch(e) {}

    // Resize canvas after a frame so the box has been laid out
    const canvas = document.getElementById('preview-canvas');
    requestAnimationFrame(() => {
        _resizePreviewCanvas();
    });

    // Watch for resize (CSS resize: both)
    if (!box._resizeObserver) {
        box._resizeObserver = new ResizeObserver(() => {
            _resizePreviewCanvas();
            // Save size
            try { localStorage.setItem('bvhStudio_previewSize', JSON.stringify({w: box.clientWidth, h: box.clientHeight})); } catch(e) {}
        });
        box._resizeObserver.observe(box);
    }

    // Clean previous
    if (_previewMixer) { _previewMixer.stopAllAction(); _previewMixer = null; }
    _previewAction = null;
    const toRemove = _previewScene.children.filter(c => c.userData._preview);
    for (const c of toRemove) {
        _previewScene.remove(c);
        if (c.geometry) c.geometry.dispose();
    }

    // Load retargeted animation via API (same as track) + build Rig2 model
    const retargetUrl = `/api/retarget/?category=${encodeURIComponent(category)}&name=${encodeURIComponent(name)}`;
    fetch(retargetUrl).then(r => {
        if (!r.ok) throw new Error(`Retarget API: ${r.status} ${r.statusText}`);
        return r.json();
    }).then(async (data) => {
        if (!data.tracks || !data.frame_count) {
            document.getElementById('preview-title').textContent = `Fehler: Keine Animationsdaten`;
            return;
        }
        console.log(`[Preview] Retarget loaded: ${data.frame_count} frames, ${Object.keys(data.tracks).length} bones`);

        // Build Rig2 model (same as track character loading)
        if (!ss.rigifySkeletonData || !ss.skinWeightData) {
            document.getElementById('preview-title').textContent = `Fehler: Skeleton-Daten nicht geladen`;
            return;
        }

        let rigBonesData = null;
        try {
            const rigResp = await fetch('/api/character/rig/');
            if (rigResp.ok) rigBonesData = await rigResp.json();
        } catch(e) {}

        const modelResp = await fetch('/api/character/model/Rig2/');
        const modelData = await modelResp.json();

        const container = new THREE.Group();
        container.userData._preview = true;
        _previewScene.add(container);

        let previewSkel = null;
        let previewMesh = null;

        if (rigBonesData && modelData.type === 'generated_model') {
            const result = generateRigBoneMesh(rigBonesData, modelData, ss.rigifySkeletonData, ss.skinWeightData);
            if (result?.mesh && result?.skeleton) {
                previewMesh = result.mesh;
                previewSkel = result.skeleton;
                // Rename bones: dots -> underscores
                if (previewSkel.skeleton) {
                    for (const bone of previewSkel.skeleton.bones) bone.name = bone.name.replace(/\./g, '_');
                }
                const newMap = {};
                for (const [k, v] of Object.entries(previewSkel.boneByName)) newMap[k.replace(/\./g, '_')] = v;
                previewSkel.boneByName = newMap;
                container.add(previewMesh);
            }
        }

        if (!previewSkel) {
            document.getElementById('preview-title').textContent = `Fehler: Modell konnte nicht geladen werden`;
            return;
        }

        // Build AnimationClip from retarget data
        const tracks = [];
        const times = data.times;
        for (const [boneName, values] of Object.entries(data.tracks)) {
            const jsName = boneName.replace(/\./g, '_');
            const bone = previewSkel.boneByName[jsName];
            if (!bone) continue;
            tracks.push(new THREE.QuaternionKeyframeTrack(bone.name + '.quaternion', times, values));
        }
        if (data.position_track) {
            const jsName = data.position_track.bone.replace(/\./g, '_');
            const bone = previewSkel.boneByName[jsName];
            if (bone) tracks.push(new THREE.VectorKeyframeTrack(bone.name + '.position', times, data.position_track.values));
        }
        const animClip = new THREE.AnimationClip('preview', data.duration, tracks);

        // Camera
        _previewCamera.position.set(0, 1.0, 3);
        _previewControls.target.set(0, 0.85, 0);
        _previewControls.update();

        // Apply Gauss smooth if active
        if (_gaussSmooth.active) {
            for (const t of animClip.tracks) _gaussFilter(t.values, t.getValueSize(), _gaussSmooth.sigma);
            fn.serverLog('gauss_preview', `${name} sigma=${_gaussSmooth.sigma}`);
        }

        // Play animation
        _previewMixer = new THREE.AnimationMixer(previewMesh);
        _previewAction = _previewMixer.clipAction(animClip);
        _previewAction.play();

        const totalFrames = data.frame_count;
        const fps = data.frame_count / data.duration;
        document.getElementById('preview-frame').textContent = `0 / ${totalFrames}`;

        // Render loop
        if (_previewAnimId) cancelAnimationFrame(_previewAnimId);
        _previewClock.start();

        function animatePreview() {
            _previewAnimId = requestAnimationFrame(animatePreview);
            if (!_previewModal || _previewModal.style.display === 'none') return;
            const dt = _previewClock.getDelta();
            if (_previewMixer) _previewMixer.update(dt);
            _previewControls.update();
            _previewRenderer.render(_previewScene, _previewCamera);
            if (_previewAction) {
                const f = Math.round(_previewAction.time * fps);
                document.getElementById('preview-frame').textContent = `${f} / ${totalFrames}`;
            }
        }
        animatePreview();
        console.log(`[Preview] Rig2 model + retargeted animation ready`);
    }).catch(e => {
        console.error('[Preview] Load failed:', e);
        document.getElementById('preview-title').textContent = `Fehler: ${e.message}`;
    });
}

function _resizePreviewCanvas() {
    const canvas = document.getElementById('preview-canvas');
    const box = document.getElementById('preview-box');
    if (!canvas || !box || !_previewRenderer) return;
    const w = box.clientWidth - 2;
    const h = box.clientHeight - 50;  // header height
    if (w > 10 && h > 10) {
        canvas.width = w;
        canvas.height = h;
        _previewRenderer.setSize(w, h, false);
        _previewCamera.aspect = w / h;
        _previewCamera.updateProjectionMatrix();
    }
}

export function closePreview() {
    if (_previewModal) _previewModal.style.display = 'none';
    if (_previewAnimId) { cancelAnimationFrame(_previewAnimId); _previewAnimId = null; }
    if (_previewMixer) { _previewMixer.stopAllAction(); }
    if (_previewAction) { _previewAction = null; }
}

// Register functions in registry
fn.buildProjectData = buildProjectData;
fn.restoreProjectData = restoreProjectData;
fn.saveProject = saveProject;
fn.saveProjectAs = saveProjectAs;
fn.loadProject = loadProject;
fn.resetToDefault = resetToDefault;
fn.loadLastProject = loadLastProject;
fn.saveSessionState = saveSessionState;
fn.restoreSessionState = restoreSessionState;
fn.previewAnimation = previewAnimation;
fn.closePreview = closePreview;
fn.getPreviewInfo = () => ({ category: _previewCategory, name: _previewName });
