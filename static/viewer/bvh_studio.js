/**
 * BVH Studio — Multi-track BVH editor with timeline, trim, blend, export.
 * Supports: BVH animation, Camera, Light, Audio tracks.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js?v=2';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    sharedState, BODY_MATERIALS,
    loadRigifySkeleton, loadSkinWeights, loadSkinColors,
    computeSkinAttributes, applySkinColorToMaterials,
    createSceneSetup,
} from './character_core.js?v=1';
import { generateRigBoneMesh, getDefaultRigConfig } from './model_generator.js';

console.log('[BVH Studio] v2.0 loaded');

// =========================================================================
// State
// =========================================================================
const ss = sharedState;
let renderer, scene, camera, controls;
let clock = new THREE.Clock();

const project = {
    name: 'Untitled',
    fps: 30,
    tracks: [],      // Track[]
    duration: 0,     // computed from clips
};

let selectedTrackIdx = -1;
let selectedClipIdx = -1;
let playheadFrame = 0;
let playing = false;
let playbackSpeed = 1;
let timelineZoom = 100;  // pixels per second
let timelineScrollX = 0;

const TRACK_HEIGHT = 40;
const HEADER_WIDTH = 120;
const RULER_HEIGHT = 20;

// =========================================================================
// Track & Clip classes
// =========================================================================
// Track types: 'bvh' | 'camera' | 'light' | 'audio'
const TRACK_COLORS = {
    bvh: null,  // random
    camera: '#00bcd4',
    light: '#ffc107',
    audio: '#4caf50',
};
const TRACK_ICONS = {
    bvh: 'fa-running',
    camera: 'fa-video',
    light: 'fa-lightbulb',
    audio: 'fa-music',
};

class Track {
    constructor(name, preset = 'FemaleGarment', bodyType = 'Female_Caucasian') {
        this.name = name;
        this.type = 'bvh';       // 'bvh' | 'camera' | 'light' | 'audio'
        this.preset = preset;
        this.bodyType = bodyType;
        this.clips = [];
        this.muted = false;
        this.color = `hsl(${Math.random() * 360}, 60%, 50%)`;
        // 3D (BVH only)
        this.mesh = null;
        this.skeleton = null;
        this.mixer = null;
        this.group = new THREE.Group();
        this.position = [0, 0, 0];
        // Camera track
        this.cameraActive = false;     // override viewport camera during playback
        this._savedCamPos = null;
        this._savedCamQuat = null;
        // Light track
        this.light = null;
        this.lightHelper = null;
        this.lightVisible = true;
        // Audio track
        this.audioCtx = null;
        this.gainNode = null;
        this.sourceNode = null;
    }
}

class Clip {
    constructor(category, name, totalFrames, fps) {
        this.type = 'bvh';      // 'bvh' | 'camera_kf' | 'light_kf' | 'audio'
        this.category = category;
        this.name = name;
        this.totalFrames = totalFrames;
        this.fps = fps || 30;
        this.startFrame = 0;     // position on timeline
        this.trimIn = 0;         // frames trimmed from start
        this.trimOut = 0;        // frames trimmed from end
        this.speed = 1.0;
        this.smoothSigma = 0;
        this.groundFix = false;
        this.blendIn = 0;
        this.blendOut = 0;
        this.animClip = null;    // Three.js AnimationClip (retargeted)
        // Type-specific data
        this.data = {};
    }
    get duration() {
        if (this.type === 'camera_kf' || this.type === 'light_kf') return 0;
        if (this.type === 'audio') return (this.data.audioDuration || 0) / this.speed;
        return (this.totalFrames - this.trimIn - this.trimOut) / (this.fps * this.speed);
    }
    get endFrame() {
        if (this.type === 'camera_kf' || this.type === 'light_kf') return this.startFrame;
        return this.startFrame + Math.ceil(this.duration * project.fps);
    }
}

// Camera edit mode state
let cameraEditMode = false;

// GLOBAL keyboard shortcuts — registered immediately at module load, capture phase
// Note: Chrome on QWERTZ swallows Ctrl+Z/Y/M. Only Ctrl+Shift+U works reliably.
window.addEventListener('keydown', (e) => {
    if (!e.ctrlKey) return;
    // Ctrl+Shift+U = Undo
    if (e.shiftKey && e.code === 'KeyU') {
        e.preventDefault();
        e.stopImmediatePropagation();
        if (typeof undo === 'function') undo();
        return;
    }
    // Ctrl+S = Save
    if (e.code === 'KeyS') {
        e.preventDefault();
        if (typeof saveProject === 'function') saveProject();
        return;
    }
    // Ctrl+O = Load
    if (e.code === 'KeyO') {
        e.preventDefault();
        if (typeof loadProject === 'function') loadProject();
        return;
    }
}, true);
console.log('[BVH Studio] Global keyboard handler registered (Ctrl+Shift+U = Undo)');

// =========================================================================
// Undo system (snapshot-based, max 20 steps)
// =========================================================================
const undoStack = [];
const redoStack = [];
const UNDO_MAX = 20;
let _undoSuppressed = false;

function pushUndo(label) {
    if (_undoSuppressed) { console.log(`[Undo] SUPPRESSED: ${label}`); return; }
    try {
        console.log(`[Undo] pushUndo('${label}') — tracks: ${project.tracks.length}, clips: ${project.tracks.map(t=>t.clips.length)}`);
        const snapshot = {
            label,
            data: buildProjectData(),
            playheadFrame,
            selectedTrackIdx,
            selectedClipIdx,
        };
        undoStack.push(snapshot);
        if (undoStack.length > UNDO_MAX) undoStack.shift();
        redoStack.length = 0;
    } catch (e) {
        console.warn('[Undo] Snapshot failed:', e);
    }
}

let _undoInProgress = false;

async function undo() {
    if (_undoInProgress) { console.log('[Undo] Already in progress, skip.'); return; }
    if (undoStack.length === 0) { console.log('[Undo] Nothing to undo. Stack empty.'); return; }
    _undoInProgress = true;
    console.log(`[Undo] Starting. Stack size: ${undoStack.length}, top label: ${undoStack[undoStack.length-1].label}, tracks in snapshot: ${undoStack[undoStack.length-1].data.tracks?.length}`);
    // Save current state to redo
    try {
        redoStack.push({
            label: 'redo',
            data: buildProjectData(),
            playheadFrame,
            selectedTrackIdx,
            selectedClipIdx,
        });
    } catch (e) { console.warn('[Undo] Redo snapshot failed:', e); }
    const snap = undoStack.pop();
    await restoreProjectData(snap.data);
    playheadFrame = snap.playheadFrame || 0;
    selectedTrackIdx = snap.selectedTrackIdx ?? -1;
    selectedClipIdx = snap.selectedClipIdx ?? -1;
    applyPlayhead();
    renderTimeline();
    updatePlaybackUI();
    updateProperties();
    document.getElementById('studio-info').textContent = `Undo: ${snap.label}`;
    console.log(`[Undo] Restored: ${snap.label} (${undoStack.length} left)`);
    _undoInProgress = false;
}

async function redo() {
    if (_undoInProgress) return;
    if (redoStack.length === 0) { console.log('[Redo] Nothing to redo'); return; }
    _undoInProgress = true;
    undoStack.push({
        label: 'undo',
        data: buildProjectData(),
        playheadFrame,
        selectedTrackIdx,
        selectedClipIdx,
    });
    const snap = redoStack.pop();
    await restoreProjectData(snap.data);
    playheadFrame = snap.playheadFrame || 0;
    selectedTrackIdx = snap.selectedTrackIdx ?? -1;
    selectedClipIdx = snap.selectedClipIdx ?? -1;
    applyPlayhead();
    renderTimeline();
    updatePlaybackUI();
    updateProperties();
    document.getElementById('studio-info').textContent = `Redo`;
    console.log(`[Redo] Restored (${redoStack.length} left)`);
    _undoInProgress = false;
}

// =========================================================================
// Init
// =========================================================================
async function init() {
    // 3D Setup
    const canvas = document.getElementById('studio-canvas');
    const setup = createSceneSetup(canvas);
    renderer = setup.renderer;
    scene = setup.scene;
    camera = setup.camera;
    controls = setup.controls;

    // Load shared data + studio settings
    await Promise.all([
        loadRigifySkeleton(),
        loadSkinWeights(),
        loadSkinColors(),
    ]);
    // Load studio preferences
    try {
        const prefsResp = await fetch('/api/ui-prefs/');
        const prefs = await prefsResp.json();
        project.defaultModel = prefs.studio_default_model || 'Rig2';
        project.defaultBodyType = prefs.studio_body_type || 'Female_Caucasian';
        project.fps = parseInt(prefs.studio_fps) || 30;
        timelineZoom = parseInt(prefs.studio_zoom) || 100;
        project.videoOutputPath = prefs.studio_video_output || '';
        project.bvhOutputPath = prefs.studio_bvh_output || '';
        project.projectPath = prefs.studio_project_path || '';
    } catch (e) { /* use defaults */ }

    // Load BVH library
    await loadLibrary();
    setupLibraryManagement();

    // Setup timeline canvas
    setupTimeline();

    // Setup playback controls
    setupPlayback();

    // Setup toolbar
    setupToolbar();

    // Setup export panel
    setupExportPanel();

    // Restore session state (if returning from another page)
    const restored = await restoreSessionState();

    // Start render loop
    animate();

    window.__studioProject = project;
    window.__studioUndo = undo;
    window.__studioRedo = redo;
    window.__undoStack = undoStack;
    console.log(`[BVH Studio] Initialized${restored ? ' (session restored)' : ''}`);
}

// =========================================================================
// BVH Library
// =========================================================================
// Track which category was open and which item selected so we can restore after reload
let _libOpenCats = new Set();
let _libSelectedItem = null;  // { category, name }

async function loadLibrary(selectAfter) {
    if (selectAfter) _libSelectedItem = selectAfter;
    try {
        // Remember open categories before rebuild
        const tree0 = document.getElementById('lib-tree');
        if (tree0) tree0.querySelectorAll('.lib-cat.open').forEach(el => {
            if (el.dataset.category) _libOpenCats.add(el.dataset.category);
        });

        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('lib-tree');
        if (!tree) return;
        tree.innerHTML = '';

        const categories = data.categories || {};
        for (const cat of Object.keys(categories).sort()) {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'lib-cat';
            catDiv.dataset.category = cat;

            const header = document.createElement('div');
            header.className = 'lib-cat-header';
            header.innerHTML = `<span class="lib-chevron"><i class="fas fa-chevron-right"></i></span> ${cat} <span style="color:var(--text-muted);font-size:0.7rem;">(${anims.length})</span>`;
            header.addEventListener('click', () => { catDiv.classList.toggle('open'); if (catDiv.classList.contains('open')) _libOpenCats.add(cat); else _libOpenCats.delete(cat); });
            // Restore open state
            if (_libOpenCats.has(cat)) catDiv.classList.add('open');
            // Also open if selected item is in this category
            if (_libSelectedItem && _libSelectedItem.category === cat) catDiv.classList.add('open');
            // Right-click on folder
            header.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                _libCtxTarget = { type: 'folder', category: cat };
                showLibCtx('lib-ctx-folder', e.clientX, e.clientY);
            });
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'lib-cat-body';
            for (const anim of anims) {
                const item = document.createElement('div');
                item.className = 'lib-item';
                item.dataset.category = cat;
                item.dataset.name = anim.name;
                item.textContent = `${anim.name} (${anim.frames || '?'}f)`;
                item.draggable = true;
                item.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('application/json', JSON.stringify({
                        category: cat, name: anim.name, frames: anim.frames || 0,
                    }));
                    item.classList.add('dragging');
                });
                item.addEventListener('dragend', () => item.classList.remove('dragging'));
                // Double-click: add to selected track
                item.addEventListener('dblclick', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    addClipToTrack(selectedTrackIdx, cat, anim.name, anim.frames || 0);
                });
                // Click: select
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.lib-item.selected').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    _libSelectedItem = { category: cat, name: anim.name };
                });
                // Restore selection
                if (_libSelectedItem && _libSelectedItem.category === cat && _libSelectedItem.name === anim.name) {
                    item.classList.add('selected');
                }
                // Right-click on file
                item.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    tree.querySelectorAll('.lib-item.selected').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    _libCtxTarget = { type: 'file', category: cat, name: anim.name, frames: anim.frames || 0 };
                    showLibCtx('lib-ctx-file', e.clientX, e.clientY);
                });
                body.appendChild(item);
            }
            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        }
    } catch (e) {
        console.error('[BVH Studio] Library load failed:', e);
    }
}

// =========================================================================
// Library file management
// =========================================================================
let _libCtxTarget = null;

function showLibCtx(menuId, x, y) {
    document.querySelectorAll('.lib-ctx').forEach(m => m.style.display = 'none');
    const menu = document.getElementById(menuId);
    if (!menu) return;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

async function libManage(action, data) {
    try {
        const resp = await fetch('/api/character/bvh-manage/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, ...data }),
        });
        const result = await resp.json();
        if (!resp.ok) { alert(result.error || 'Fehler'); return null; }
        return result;
    } catch (e) {
        alert('Fehler: ' + e.message);
        return null;
    }
}

function renameSelectedLibItem() {
    const sel = document.querySelector('.lib-item.selected');
    if (!sel) return;
    const cat = sel.dataset.category, name = sel.dataset.name;
    const newName = prompt('Neuer Name:', name);
    if (newName && newName !== name) {
        libManage('rename', { category: cat, name, new_name: newName }).then(r => {
            if (r) loadLibrary({ category: cat, name: newName });
        });
    }
}

function removeClipsFromTracks(category, name) {
    // Remove all clips referencing this BVH from all tracks
    let removed = 0;
    for (const track of project.tracks) {
        if (track.type !== 'bvh') continue;
        for (let i = track.clips.length - 1; i >= 0; i--) {
            if (track.clips[i].category === category && track.clips[i].name === name) {
                if (track.mixer) {
                    track.mixer.stopAllAction();
                    if (track.clips[i].animClip) track.mixer.uncacheClip(track.clips[i].animClip);
                }
                track.clips.splice(i, 1);
                removed++;
            }
        }
        // Hide mesh if no clips left
        if (track.clips.length === 0 && track.mesh) track.mesh.visible = false;
        track._activeClip = null;
        track._activeAction = null;
    }
    if (removed > 0) {
        selectedClipIdx = -1;
        // Stop playback if no clips left
        const anyClips = project.tracks.some(t => t.clips.length > 0);
        if (!anyClips && playing) {
            playing = false;
            const icon = document.getElementById('pb-play-icon');
            if (icon) icon.className = 'fas fa-play';
        }
        updateDuration();
        renderTimeline();
        updateProperties();
        console.log(`[BVH Studio] Removed ${removed} clip(s) of ${category}/${name} from tracks`);
    }
}

function deleteSelectedLibItem() {
    const sel = document.querySelector('.lib-item.selected');
    if (!sel) return;
    const cat = sel.dataset.category, name = sel.dataset.name;
    if (confirm(`"${name}" wirklich loeschen?`)) {
        _libOpenCats.add(cat);
        _libSelectedItem = null;
        libManage('delete', { category: cat, name }).then(r => {
            if (r) {
                removeClipsFromTracks(cat, name);
                loadLibrary();
            }
        });
    }
}

function setupLibraryManagement() {
    // Close context menus
    document.addEventListener('click', () => {
        document.querySelectorAll('.lib-ctx').forEach(m => m.style.display = 'none');
    });

    // File context menu
    document.querySelectorAll('#lib-ctx-file .lib-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _libCtxTarget;
            if (!t) return;
            const action = item.dataset.action;
            if (action === 'add') {
                addClipToTrack(selectedTrackIdx, t.category, t.name, t.frames);
            } else if (action === 'preview') {
                previewAnimation(t.category, t.name);
            } else if (action === 'rename') {
                const newName = prompt('Neuer Name:', t.name);
                if (newName && newName !== t.name) {
                    if (await libManage('rename', { category: t.category, name: t.name, new_name: newName }))
                        loadLibrary({ category: t.category, name: newName });
                }
            } else if (action === 'move') {
                const newCat = prompt('In welchen Ordner verschieben?', t.category);
                if (newCat && newCat !== t.category) {
                    if (await libManage('move', { category: t.category, name: t.name, new_category: newCat })) loadLibrary();
                }
            } else if (action === 'delete') {
                if (confirm(`"${t.name}" wirklich loeschen?`)) {
                    _libOpenCats.add(t.category);
                    _libSelectedItem = null;
                    if (await libManage('delete', { category: t.category, name: t.name })) {
                        removeClipsFromTracks(t.category, t.name);
                        loadLibrary();
                    }
                }
            }
        });
    });

    // Folder context menu
    document.querySelectorAll('#lib-ctx-folder .lib-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _libCtxTarget;
            if (!t) return;
            const action = item.dataset.action;
            if (action === 'rename-folder') {
                const newName = prompt('Neuer Ordnername:', t.category);
                if (newName && newName !== t.category) {
                    if (await libManage('rename_folder', { category: t.category, new_name: newName })) loadLibrary();
                }
            } else if (action === 'new-folder') {
                const name = prompt('Name des neuen Ordners:');
                if (name) {
                    if (await libManage('create_folder', { folder_name: name })) loadLibrary();
                }
            } else if (action === 'delete-folder') {
                if (confirm(`Ordner "${t.category}" wirklich loeschen?\n(Nur wenn leer)`)) {
                    if (await libManage('delete_folder', { category: t.category })) loadLibrary();
                }
            }
        });
    });

    // Library toolbar buttons
    document.getElementById('lib-new-folder')?.addEventListener('click', async () => {
        const name = prompt('Name des neuen Ordners:');
        if (name) { if (await libManage('create_folder', { folder_name: name })) loadLibrary(); }
    });
    document.getElementById('lib-rename')?.addEventListener('click', () => renameSelectedLibItem());
    document.getElementById('lib-delete')?.addEventListener('click', () => deleteSelectedLibItem());
    document.getElementById('lib-refresh')?.addEventListener('click', () => loadLibrary());
}

// =========================================================================
// Track management
// =========================================================================
function addTrack(name) {
    const track = new Track(
        name || `Track ${project.tracks.length + 1}`,
        project.defaultModel || 'Rig2',
        project.defaultBodyType || 'Female_Caucasian'
    );
    project.tracks.push(track);
    scene.add(track.group);
    updateTrackHeaders();
    selectTrack(project.tracks.length - 1);
    return track;
}

function addSpecialTrack(type, name) {
    const defaults = { camera: 'Kamera', light: 'Licht', audio: 'Audio' };
    const track = new Track(name || defaults[type] || type);
    track.type = type;
    track.color = TRACK_COLORS[type] || track.color;

    if (type === 'camera') {
        track.cameraActive = true;
    } else if (type === 'light') {
        track.light = new THREE.PointLight(0xffffff, 2.0, 50);
        track.light.position.set(2, 3, 2);
        scene.add(track.light);
        // Helper sphere
        const helperGeo = new THREE.SphereGeometry(0.08, 8, 8);
        const helperMat = new THREE.MeshBasicMaterial({ color: 0xffc107 });
        track.lightHelper = new THREE.Mesh(helperGeo, helperMat);
        track.lightHelper.position.copy(track.light.position);
        scene.add(track.lightHelper);
    } else if (type === 'audio') {
        track.audioCtx = project._audioCtx || (project._audioCtx = new (window.AudioContext || window.webkitAudioContext)());
        track.gainNode = track.audioCtx.createGain();
        track.gainNode.connect(track.audioCtx.destination);
    }

    project.tracks.push(track);
    updateTrackHeaders();
    selectTrack(project.tracks.length - 1);
    return track;
}

// Camera keyframe helpers
function addCameraKeyframe(trackIdx) {
    const track = project.tracks[trackIdx];
    if (!track || track.type !== 'camera') return;
    pushUndo('Kamera Keyframe');
    const kf = new Clip(null, `KF ${track.clips.length + 1}`, 0, project.fps);
    kf.type = 'camera_kf';
    kf.startFrame = playheadFrame;
    kf.data = {
        position: { x: camera.position.x, y: camera.position.y, z: camera.position.z },
        rotation: { x: camera.rotation.x, y: camera.rotation.y, z: camera.rotation.z },
        fov: camera.fov,
        interpolation: 'smooth',  // 'linear' | 'smooth' | 'step'
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    updateDuration();
    renderTimeline();
    updateProperties();
    console.log(`[BVH Studio] Camera keyframe added at frame ${playheadFrame}`);
}

// Light keyframe helpers
function addLightKeyframe(trackIdx) {
    const track = project.tracks[trackIdx];
    if (!track || track.type !== 'light' || !track.light) return;
    pushUndo('Licht Keyframe');
    const kf = new Clip(null, `LKF ${track.clips.length + 1}`, 0, project.fps);
    kf.type = 'light_kf';
    kf.startFrame = playheadFrame;
    kf.data = {
        position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
        color: '#' + track.light.color.getHexString(),
        intensity: track.light.intensity,
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    updateDuration();
    renderTimeline();
    updateProperties();
    console.log(`[BVH Studio] Light keyframe added at frame ${playheadFrame}`);
}

// Audio clip helpers
async function loadAudioFile(trackIdx) {
    const track = project.tracks[trackIdx];
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
            const clip = new Clip(null, file.name, Math.round(audioBuffer.duration * project.fps), project.fps);
            clip.type = 'audio';
            clip.startFrame = playheadFrame;
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
            updateDuration();
            renderTimeline();
            updateProperties();
            console.log(`[BVH Studio] Audio loaded: ${file.name} (${audioBuffer.duration.toFixed(1)}s)`);
        } catch (e) {
            console.error('[BVH Studio] Audio decode failed:', e);
            alert('Audio laden fehlgeschlagen: ' + e.message);
        }
    });
    input.click();
}

function removeTrack(idx) {
    if (idx < 0 || idx >= project.tracks.length) return;
    pushUndo('Track loeschen');
    const track = project.tracks[idx];

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
    scene.remove(track.group);
    track.group = null;

    // Cleanup special tracks
    if (track.light) { scene.remove(track.light); track.light.dispose(); }
    if (track.lightHelper) { scene.remove(track.lightHelper); track.lightHelper.geometry.dispose(); }
    if (track.type === 'audio') stopAudioTrack(track);

    project.tracks.splice(idx, 1);
    if (selectedTrackIdx >= project.tracks.length) selectedTrackIdx = project.tracks.length - 1;
    selectedClipIdx = -1;
    updateTrackHeaders();
    updateProperties();
    renderTimeline();
}

function selectTrack(idx) {
    selectedTrackIdx = idx;
    selectedClipIdx = -1;
    updateTrackHeaders();
    updateProperties();
}

async function addClipToTrack(trackIdx, category, name, frames) {
    pushUndo('Clip hinzufuegen');
    console.log(`[BVH Studio] addClipToTrack: trackIdx=${trackIdx}, ${category}/${name}, existingTracks=${project.tracks.length}`);
    if (trackIdx < 0 || !project.tracks[trackIdx]) {
        if (project.tracks.length === 0) addTrack();
        trackIdx = project.tracks.length - 1;
    }
    const track = project.tracks[trackIdx];
    if (!track) { console.error('[BVH Studio] addClipToTrack: no track!'); return; }

    // Reset mixer state so new clip plays cleanly
    if (track.mixer) {
        track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
    }

    const clip = new Clip(category, name, frames || 3000, project.fps);

    // Place after last clip on this track
    const lastClip = track.clips[track.clips.length - 1];
    clip.startFrame = lastClip ? lastClip.endFrame : 0;

    track.clips.push(clip);
    if (track.mesh) track.mesh.visible = true;  // re-show if was hidden
    updateDuration();
    renderTimeline();

    // Load retargeted animation
    await loadClipAnimation(track, clip);
    console.log(`[BVH Studio] addClipToTrack done: clips=${track.clips.length}, hasMixer=${!!track.mixer}, hasSkeleton=${!!track.skeleton}`);
    updateProperties();
}

async function loadClipAnimation(track, clip) {
    try {
        const url = `/api/retarget/?category=${encodeURIComponent(clip.category)}&name=${encodeURIComponent(clip.name)}`;
        const resp = await fetch(url);
        if (!resp.ok) {
            console.error(`[BVH Studio] Retarget failed for ${clip.category}/${clip.name}: ${resp.status}`);
            clip._loadError = true;
            renderTimeline();
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
            console.log(`[BVH Studio] Clip loaded: ${clip.name} (${clip.totalFrames}f, ${clip.duration.toFixed(1)}s)`);
        }

        updateDuration();
        renderTimeline();
    } catch (e) {
        console.error('[BVH Studio] Clip load failed:', e);
    }
}

function buildClipFromData(data, skel) {
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

async function loadTrackCharacter(track) {
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
                        // Rename bones: dots → underscores so Three.js AnimationMixer
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

// =========================================================================
// Timeline
// =========================================================================
let tlCanvas, tlCtx;

function setupTimeline() {
    tlCanvas = document.getElementById('timeline-canvas');
    if (!tlCanvas) return;
    tlCtx = tlCanvas.getContext('2d');

    const wrap = tlCanvas.parentElement;
    const resize = () => {
        tlCanvas.width = wrap.clientWidth;
        tlCanvas.height = wrap.clientHeight;
        renderTimeline();
    };
    resize();
    new ResizeObserver(resize).observe(wrap);

    // Zoom slider
    const zoomSlider = document.getElementById('tl-zoom');
    if (zoomSlider) {
        zoomSlider.addEventListener('input', () => {
            timelineZoom = parseInt(zoomSlider.value);
            document.getElementById('tl-zoom-label').textContent = `Zoom: ${timelineZoom}%`;
            renderTimeline();
        });
    }

    // --- Clip hit-testing ---
    function hitTestClip(mx, my) {
        const pps = timelineZoom;
        for (let ti = 0; ti < project.tracks.length; ti++) {
            const track = project.tracks[ti];
            const y = RULER_HEIGHT + ti * TRACK_HEIGHT;
            for (let ci = 0; ci < track.clips.length; ci++) {
                const clip = track.clips[ci];
                const cx = HEADER_WIDTH + (clip.startFrame / project.fps) * pps - timelineScrollX;

                if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
                    // Keyframe marker: hit area 16x16 around point
                    const my2 = y + TRACK_HEIGHT / 2;
                    if (mx >= cx - 8 && mx <= cx + 8 && my >= my2 - 8 && my <= my2 + 8) {
                        return { trackIdx: ti, clipIdx: ci, clipX: cx, clipW: 0 };
                    }
                } else {
                    const cw = Math.max(clip.duration * pps, 4);
                    const cy = y + 4;
                    const ch = TRACK_HEIGHT - 8;
                    if (mx >= cx && mx <= cx + cw && my >= cy && my <= cy + ch) {
                        // Detect edge: 6px grab zone at left/right edge
                        let edge = null;
                        if (mx - cx < 6 && cw > 16) edge = 'left';
                        else if (cx + cw - mx < 6 && cw > 16) edge = 'right';
                        return { trackIdx: ti, clipIdx: ci, clipX: cx, clipW: cw, edge };
                    }
                }
            }
        }
        return null;
    }

    // --- Mouse interactions ---
    // Modes: 'none' | 'clip-drag' | 'trim-left' | 'trim-right' | 'scrub' | 'pan'
    let dragMode = 'none';
    let draggingClip = null;
    let dragStartX = 0;
    let dragOrigFrame = 0;
    let dragOrigTrimIn = 0;
    let dragOrigTrimOut = 0;
    let panStartScrollX = 0;

    function setPlayheadFromMouse(mx) {
        const x = mx - HEADER_WIDTH + timelineScrollX;
        playheadFrame = Math.max(0, Math.round((x / timelineZoom) * project.fps));
        renderTimeline();
        updatePlaybackUI();
        applyPlayhead();
    }

    tlCanvas.addEventListener('mousedown', (e) => {
        const rect = tlCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Middle mouse button or Alt+click → pan
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            dragMode = 'pan';
            dragStartX = e.clientX;
            panStartScrollX = timelineScrollX;
            e.preventDefault();
            return;
        }

        // Hit test clips (left button only)
        if (e.button === 0) {
            const hit = hitTestClip(mx, my);
            // Clear library selection when clicking in timeline
            document.querySelectorAll('.lib-item.selected').forEach(el => el.classList.remove('selected'));
            _libSelectedItem = null;
            if (hit) {
                selectedTrackIdx = hit.trackIdx;
                selectedClipIdx = hit.clipIdx;
                updateProperties();
                renderTimeline();
                const clip = project.tracks[hit.trackIdx].clips[hit.clipIdx];
                draggingClip = hit;
                dragStartX = mx;
                dragOrigFrame = clip.startFrame;
                dragOrigTrimIn = clip.trimIn;
                dragOrigTrimOut = clip.trimOut;
                // Edge drag = trim, center drag = move
                if (hit.edge === 'left') { pushUndo('Trim links'); dragMode = 'trim-left'; }
                else if (hit.edge === 'right') { pushUndo('Trim rechts'); dragMode = 'trim-right'; }
                else { pushUndo('Clip verschieben'); dragMode = 'clip-drag'; }
                e.preventDefault();
                return;
            }

            // No clip hit — start scrubbing (playhead follows mouse)
            if (mx > HEADER_WIDTH) {
                dragMode = 'scrub';
                dragStartX = mx;

                // Select track by Y position
                if (my > RULER_HEIGHT) {
                    const ti = Math.floor((my - RULER_HEIGHT) / TRACK_HEIGHT);
                    if (ti >= 0 && ti < project.tracks.length) {
                        selectedTrackIdx = ti;
                        selectedClipIdx = -1;
                        updateProperties();
                    }
                }

                setPlayheadFromMouse(mx);
                e.preventDefault();
            }
        }
    });

    tlCanvas.addEventListener('mousemove', (e) => {
        // Update cursor on hover
        if (dragMode === 'none') {
            const rect = tlCanvas.getBoundingClientRect();
            const hit = hitTestClip(e.clientX - rect.left, e.clientY - rect.top);
            if (hit?.edge) tlCanvas.style.cursor = 'ew-resize';
            else if (hit) tlCanvas.style.cursor = 'grab';
            else tlCanvas.style.cursor = 'default';
        }
        if (dragMode === 'none') return;
        const rect = tlCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;

        if (dragMode === 'clip-drag' && draggingClip) {
            const dx = mx - dragStartX;
            const frameDelta = Math.round((dx / timelineZoom) * project.fps);
            const clip = project.tracks[draggingClip.trackIdx].clips[draggingClip.clipIdx];
            clip.startFrame = Math.max(0, dragOrigFrame + frameDelta);
            updateDuration();
            renderTimeline();
        } else if (dragMode === 'trim-left' && draggingClip) {
            const dx = mx - dragStartX;
            const frameDelta = Math.round((dx / timelineZoom) * project.fps);
            const clip = project.tracks[draggingClip.trackIdx].clips[draggingClip.clipIdx];
            const newTrimIn = Math.max(0, Math.min(clip.totalFrames - clip.trimOut - 1, dragOrigTrimIn + frameDelta));
            clip.trimIn = newTrimIn;
            // Shift start so the visible clip stays aligned
            clip.startFrame = Math.max(0, dragOrigFrame + (newTrimIn - dragOrigTrimIn));
            updateDuration();
            renderTimeline();
        } else if (dragMode === 'trim-right' && draggingClip) {
            const dx = mx - dragStartX;
            const frameDelta = Math.round((dx / timelineZoom) * project.fps);
            const clip = project.tracks[draggingClip.trackIdx].clips[draggingClip.clipIdx];
            clip.trimOut = Math.max(0, Math.min(clip.totalFrames - clip.trimIn - 1, dragOrigTrimOut - frameDelta));
            updateDuration();
            renderTimeline();
        } else if (dragMode === 'scrub') {
            if (mx > HEADER_WIDTH) setPlayheadFromMouse(mx);
        } else if (dragMode === 'pan') {
            const dx = e.clientX - dragStartX;
            timelineScrollX = Math.max(0, panStartScrollX - dx);
            renderTimeline();
        }
    });

    tlCanvas.addEventListener('mouseup', () => {
        if (dragMode === 'clip-drag' || dragMode === 'trim-left' || dragMode === 'trim-right') {
            draggingClip = null;
            updateProperties();
        }
        dragMode = 'none';
        tlCanvas.style.cursor = 'default';
    });

    tlCanvas.addEventListener('mouseleave', () => {
        if (dragMode === 'clip-drag') draggingClip = null;
        dragMode = 'none';
    });

    // Prevent default middle-click paste/autoscroll
    tlCanvas.addEventListener('auxclick', (e) => { if (e.button === 1) e.preventDefault(); });

    // Context menu (right-click on clip)
    const ctxMenu = document.getElementById('clip-context-menu');
    tlCanvas.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        const rect = tlCanvas.getBoundingClientRect();
        const hit = hitTestClip(e.clientX - rect.left, e.clientY - rect.top);
        if (hit) {
            selectedTrackIdx = hit.trackIdx;
            selectedClipIdx = hit.clipIdx;
            updateProperties();
            renderTimeline();
            ctxMenu.style.display = '';
            ctxMenu.style.left = e.clientX + 'px';
            ctxMenu.style.top = e.clientY + 'px';
        } else {
            ctxMenu.style.display = 'none';
        }
    });
    document.addEventListener('click', () => { if (ctxMenu) ctxMenu.style.display = 'none'; });

    ctxMenu?.querySelectorAll('.ctx-item').forEach(item => {
        item.addEventListener('click', () => {
            ctxMenu.style.display = 'none';
            const action = item.dataset.action;
            if (action === 'ctx-split') splitClipAtPlayhead();
            else if (action === 'ctx-delete') deleteSelectedClip();
            else if (action === 'ctx-duplicate') duplicateSelectedClip();
            else if (action === 'ctx-save-bvh') saveBvhAs();
            else if (action === 'ctx-smooth') smoothSelectedClip();
            else if (action === 'ctx-ground') groundFixSelectedClip();
            else if (action === 'ctx-trim-start') trimSelectedClip('start', 10);
            else if (action === 'ctx-trim-end') trimSelectedClip('end', 10);
            else if (action === 'ctx-trim-reset') trimSelectedClip('reset');
        });
    });

    // Drop clips on timeline
    tlCanvas.addEventListener('dragover', (e) => { e.preventDefault(); });
    tlCanvas.addEventListener('drop', (e) => {
        e.preventDefault();
        try {
            const data = JSON.parse(e.dataTransfer.getData('application/json'));
            const rect = tlCanvas.getBoundingClientRect();
            const y = e.clientY - rect.top - RULER_HEIGHT;
            const trackIdx = Math.floor(y / TRACK_HEIGHT);
            if (trackIdx >= 0 && trackIdx < project.tracks.length) {
                addClipToTrack(trackIdx, data.category, data.name, data.frames);
            } else {
                // New track
                const track = addTrack();
                addClipToTrack(project.tracks.length - 1, data.category, data.name, data.frames);
            }
        } catch (err) { console.warn('Drop failed:', err); }
    });

    // Scroll
    tlCanvas.addEventListener('wheel', (e) => {
        if (e.ctrlKey) {
            timelineZoom = Math.max(10, Math.min(500, timelineZoom + (e.deltaY > 0 ? -10 : 10)));
            const zoomSlider = document.getElementById('tl-zoom');
            if (zoomSlider) zoomSlider.value = timelineZoom;
            document.getElementById('tl-zoom-label').textContent = `Zoom: ${timelineZoom}%`;
        } else {
            timelineScrollX = Math.max(0, timelineScrollX + e.deltaX + e.deltaY);
        }
        renderTimeline();
        e.preventDefault();
    });
}

function renderTimeline() {
    if (!tlCtx || !tlCanvas) return;
    const w = tlCanvas.width, h = tlCanvas.height;
    const pps = timelineZoom;  // pixels per second at current zoom

    tlCtx.clearRect(0, 0, w, h);

    // Ruler
    tlCtx.fillStyle = '#1a1a2e';
    tlCtx.fillRect(0, 0, w, RULER_HEIGHT);
    tlCtx.strokeStyle = '#334155';
    tlCtx.lineWidth = 1;
    tlCtx.beginPath();
    tlCtx.moveTo(0, RULER_HEIGHT);
    tlCtx.lineTo(w, RULER_HEIGHT);
    tlCtx.stroke();

    // Time markers
    tlCtx.fillStyle = '#64748b';
    tlCtx.font = '10px monospace';
    const secStep = Math.max(1, Math.floor(50 / pps));
    for (let s = 0; s < project.duration + 10; s += secStep) {
        const x = HEADER_WIDTH + s * pps - timelineScrollX;
        if (x < HEADER_WIDTH || x > w) continue;
        tlCtx.fillText(`${s}s`, x + 2, 12);
        tlCtx.beginPath();
        tlCtx.moveTo(x, 14);
        tlCtx.lineTo(x, RULER_HEIGHT);
        tlCtx.stroke();
    }

    // Tracks + Clips
    for (let ti = 0; ti < project.tracks.length; ti++) {
        const track = project.tracks[ti];
        const y = RULER_HEIGHT + ti * TRACK_HEIGHT;

        // Track background
        tlCtx.fillStyle = ti === selectedTrackIdx ? 'rgba(124,92,191,0.1)' : 'rgba(0,0,0,0.2)';
        tlCtx.fillRect(HEADER_WIDTH, y, w - HEADER_WIDTH, TRACK_HEIGHT);
        tlCtx.strokeStyle = '#1e293b';
        tlCtx.beginPath();
        tlCtx.moveTo(HEADER_WIDTH, y + TRACK_HEIGHT);
        tlCtx.lineTo(w, y + TRACK_HEIGHT);
        tlCtx.stroke();

        // Clips
        // Draw interpolation lines for camera/light keyframe tracks first
        if ((track.type === 'camera' || track.type === 'light') && track.clips.length > 1) {
            tlCtx.strokeStyle = track.color;
            tlCtx.lineWidth = 1.5;
            tlCtx.globalAlpha = 0.4;
            tlCtx.beginPath();
            for (let ci = 0; ci < track.clips.length; ci++) {
                const cx = HEADER_WIDTH + (track.clips[ci].startFrame / project.fps) * pps - timelineScrollX;
                if (ci === 0) tlCtx.moveTo(cx, y + TRACK_HEIGHT / 2);
                else tlCtx.lineTo(cx, y + TRACK_HEIGHT / 2);
            }
            tlCtx.stroke();
            tlCtx.globalAlpha = 1.0;
        }

        for (let ci = 0; ci < track.clips.length; ci++) {
            const clip = track.clips[ci];
            const cx = HEADER_WIDTH + (clip.startFrame / project.fps) * pps - timelineScrollX;
            const isSelected = (ti === selectedTrackIdx && ci === selectedClipIdx);

            if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
                // Keyframe marker: diamond (camera) or circle (light)
                const my = y + TRACK_HEIGHT / 2;
                const sz = isSelected ? 8 : 6;
                tlCtx.fillStyle = track.color;
                tlCtx.globalAlpha = isSelected ? 1.0 : 0.8;
                if (clip.type === 'camera_kf') {
                    // Diamond
                    tlCtx.beginPath();
                    tlCtx.moveTo(cx, my - sz);
                    tlCtx.lineTo(cx + sz, my);
                    tlCtx.lineTo(cx, my + sz);
                    tlCtx.lineTo(cx - sz, my);
                    tlCtx.closePath();
                    tlCtx.fill();
                } else {
                    // Circle
                    tlCtx.beginPath();
                    tlCtx.arc(cx, my, sz, 0, Math.PI * 2);
                    tlCtx.fill();
                }
                if (isSelected) {
                    tlCtx.strokeStyle = '#fff';
                    tlCtx.lineWidth = 2;
                    tlCtx.stroke();
                }
                tlCtx.globalAlpha = 1.0;
            } else {
                // Rectangle clips (BVH, Audio)
                const cw = Math.max(clip.duration * pps, 4);
                const cy = y + 4;
                const ch = TRACK_HEIGHT - 8;

                tlCtx.fillStyle = track.color;
                tlCtx.globalAlpha = isSelected ? 1.0 : 0.7;
                tlCtx.fillRect(cx, cy, cw, ch);
                tlCtx.globalAlpha = 1.0;

                // Audio waveform indicator
                if (clip.type === 'audio') {
                    tlCtx.strokeStyle = 'rgba(255,255,255,0.3)';
                    tlCtx.lineWidth = 1;
                    for (let wx = cx + 4; wx < cx + cw - 2; wx += 6) {
                        const wh = 3 + Math.random() * (ch - 8);
                        tlCtx.beginPath();
                        tlCtx.moveTo(wx, cy + ch / 2 - wh / 2);
                        tlCtx.lineTo(wx, cy + ch / 2 + wh / 2);
                        tlCtx.stroke();
                    }
                }

                // Clip border
                tlCtx.strokeStyle = '#fff';
                tlCtx.lineWidth = isSelected ? 2 : 0.5;
                tlCtx.strokeRect(cx, cy, cw, ch);

                // Clip label
                tlCtx.fillStyle = '#fff';
                tlCtx.font = '10px sans-serif';
                tlCtx.fillText(clip.name, cx + 4, cy + ch / 2 + 3, cw - 8);
            }
        }
    }

    // Playhead
    const phX = HEADER_WIDTH + (playheadFrame / project.fps) * pps - timelineScrollX;
    if (phX >= HEADER_WIDTH) {
        tlCtx.strokeStyle = '#ef4444';
        tlCtx.lineWidth = 2;
        tlCtx.beginPath();
        tlCtx.moveTo(phX, 0);
        tlCtx.lineTo(phX, h);
        tlCtx.stroke();
        // Playhead handle
        tlCtx.fillStyle = '#ef4444';
        tlCtx.beginPath();
        tlCtx.moveTo(phX - 6, 0);
        tlCtx.lineTo(phX + 6, 0);
        tlCtx.lineTo(phX, 10);
        tlCtx.fill();
    }

    // Update frame info
    const info = document.getElementById('tl-frame-info');
    if (info) info.textContent = `Frame ${playheadFrame} / ${Math.round(project.duration * project.fps)}`;
}

function updateTrackHeaders() {
    const container = document.getElementById('track-headers');
    if (!container) return;
    container.innerHTML = '';
    // Ruler space
    const ruler = document.createElement('div');
    ruler.style.cssText = `height:${RULER_HEIGHT}px;border-bottom:1px solid var(--border);`;
    container.appendChild(ruler);

    for (let i = 0; i < project.tracks.length; i++) {
        const track = project.tracks[i];
        const el = document.createElement('div');
        el.className = 'track-header' + (i === selectedTrackIdx ? ' selected' : '');
        const icon = TRACK_ICONS[track.type] || 'fa-running';
        el.innerHTML = `<i class="fas ${icon}" style="color:${track.color};margin-right:6px;font-size:0.75rem;width:14px;text-align:center;"></i>${track.name}`;
        el.addEventListener('click', () => selectTrack(i));
        // Right-click: track context menu
        el.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            selectTrack(i);
            const ctx = document.getElementById('track-context-menu');
            if (ctx) { ctx.style.display = ''; ctx.style.left = e.clientX + 'px'; ctx.style.top = e.clientY + 'px'; }
        });
        // Drop target
        el.addEventListener('dragover', (e) => { e.preventDefault(); el.classList.add('drop-target'); });
        el.addEventListener('dragleave', () => el.classList.remove('drop-target'));
        el.addEventListener('drop', (e) => {
            e.preventDefault();
            el.classList.remove('drop-target');
            try {
                const data = JSON.parse(e.dataTransfer.getData('application/json'));
                addClipToTrack(i, data.category, data.name, data.frames);
            } catch (err) {}
        });
        container.appendChild(el);
    }
}

function updateDuration() {
    let maxEnd = 0;
    for (const track of project.tracks) {
        for (const clip of track.clips) {
            const end = clip.endFrame / project.fps;
            if (end > maxEnd) maxEnd = end;
        }
    }
    project.duration = maxEnd;
}

// =========================================================================
// Playback
// =========================================================================
function setupPlayback() {
    document.getElementById('pb-play')?.addEventListener('click', togglePlay);
    document.getElementById('pb-stop')?.addEventListener('click', stopPlayback);
    document.getElementById('pb-prev')?.addEventListener('click', () => stepFrame(-1));
    document.getElementById('pb-next')?.addEventListener('click', () => stepFrame(1));
    document.getElementById('pb-speed')?.addEventListener('change', (e) => {
        playbackSpeed = parseFloat(e.target.value);
    });

    // Ctrl shortcuts registered globally at module top level
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
            if (selectedClipIdx >= 0) deleteSelectedClip();
            else if (document.querySelector('.lib-item.selected')) deleteSelectedLibItem();
        }
        if (e.code === 'KeyS' && !e.ctrlKey) {
            e.preventDefault();
            splitClipAtPlayhead();
        }
        if (e.code === 'KeyK') {
            e.preventDefault();
            if (selectedTrackIdx >= 0) {
                const t = project.tracks[selectedTrackIdx];
                if (t.type === 'camera') addCameraKeyframe(selectedTrackIdx);
                else if (t.type === 'light') addLightKeyframe(selectedTrackIdx);
            }
        }
        // Ctrl shortcuts handled in capture-phase handler above
        if (e.key === 'F2') {
            e.preventDefault();
            const sel = document.querySelector('.lib-item.selected');
            if (sel) renameSelectedLibItem();
        }
        if (e.code === 'KeyA' && !e.ctrlKey) {
            e.preventDefault();
            const sel = document.querySelector('.lib-item.selected');
            if (sel) previewAnimation(sel.dataset.category, sel.dataset.name);
        }
    });
}

function togglePlay() {
    playing = !playing;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = playing ? 'fas fa-pause' : 'fas fa-play';
    if (playing) {
        startAudioPlayback();
    } else {
        stopAllAudio();
        controls.enabled = true;  // re-enable OrbitControls when pausing camera playback
    }
}

function stopPlayback() {
    playing = false;
    playheadFrame = 0;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = 'fas fa-play';
    stopAllAudio();
    controls.enabled = true;  // re-enable OrbitControls
    applyPlayhead();
    renderTimeline();
    updatePlaybackUI();
}

function stepFrame(delta) {
    playheadFrame = Math.max(0, playheadFrame + delta);
    applyPlayhead();
    renderTimeline();
    updatePlaybackUI();
}

function applyPlayhead() {
    const t = playheadFrame / project.fps;
    for (const track of project.tracks) {
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
        const clipStart = clip.startFrame / project.fps;
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
    if (!track.cameraActive || !playing || track.clips.length === 0) return;
    const frame = playheadFrame;
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
        camera.position.set(prev.data.position.x, prev.data.position.y, prev.data.position.z);
        camera.rotation.set(prev.data.rotation.x, prev.data.rotation.y, prev.data.rotation.z);
        camera.fov = prev.data.fov;
    } else {
        const alpha = (frame - prev.startFrame) / (next.startFrame - prev.startFrame);
        const interp = prev.data.interpolation || 'linear';
        const t = interp === 'smooth' ? alpha * alpha * (3 - 2 * alpha) : (interp === 'step' ? 0 : alpha);
        camera.position.lerpVectors(
            new THREE.Vector3(prev.data.position.x, prev.data.position.y, prev.data.position.z),
            new THREE.Vector3(next.data.position.x, next.data.position.y, next.data.position.z), t);
        // Slerp rotation via quaternions
        const qPrev = new THREE.Quaternion().setFromEuler(new THREE.Euler(prev.data.rotation.x, prev.data.rotation.y, prev.data.rotation.z));
        const qNext = new THREE.Quaternion().setFromEuler(new THREE.Euler(next.data.rotation.x, next.data.rotation.y, next.data.rotation.z));
        const qResult = new THREE.Quaternion().slerpQuaternions(qPrev, qNext, t);
        camera.quaternion.copy(qResult);
        camera.fov = prev.data.fov + (next.data.fov - prev.data.fov) * t;
    }
    camera.updateProjectionMatrix();
    controls.enabled = false;
}

function applyLightTrack(track, t) {
    if (!track.light || track.clips.length === 0) return;
    const frame = playheadFrame;
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
        const clipStart = clip.startFrame / project.fps;
        const clipEnd = clipStart + clip.duration;
        if (t >= clipStart && t < clipEnd) {
            track.gainNode.gain.value = clip.data.volume || 1;
            // Audio playback is managed in togglePlay/stopPlayback
            return;
        }
    }
}

// Audio play/stop helpers
function startAudioPlayback() {
    for (const track of project.tracks) {
        if (track.type !== 'audio' || track.muted || !track.audioCtx) continue;
        stopAudioTrack(track);
        const t = playheadFrame / project.fps;
        for (const clip of track.clips) {
            if (clip.type !== 'audio' || !clip.data.audioBuffer) continue;
            const clipStart = clip.startFrame / project.fps;
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

function stopAudioTrack(track) {
    if (track.sourceNode) {
        try { track.sourceNode.stop(); } catch(e) {}
        track.sourceNode = null;
        track._audioClip = null;
    }
}

function stopAllAudio() {
    for (const track of project.tracks) {
        if (track.type === 'audio') stopAudioTrack(track);
    }
}

function updatePlaybackUI() {
    const t = playheadFrame / project.fps;
    const el = document.getElementById('pb-time');
    if (el) el.textContent = formatTime(t);
    const fr = document.getElementById('pb-frame');
    if (fr) fr.textContent = `F: ${playheadFrame}`;
    const dur = document.getElementById('pb-duration');
    if (dur) dur.textContent = formatTime(project.duration);
}

function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = (s % 60).toFixed(2);
    return `${m.toString().padStart(2, '0')}:${sec.padStart(5, '0')}`;
}

// =========================================================================
// Properties panel
// =========================================================================
function updateProperties() {
    const content = document.getElementById('props-content');
    if (!content) return;

    if (selectedTrackIdx < 0 || selectedTrackIdx >= project.tracks.length) {
        content.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;">Track oder Clip auswaehlen</div>';
        return;
    }

    const track = project.tracks[selectedTrackIdx];
    const clip = selectedClipIdx >= 0 ? track.clips[selectedClipIdx] : null;
    let html = '';

    // --- Track header (common) ---
    const icon = TRACK_ICONS[track.type] || 'fa-running';
    html += `<div class="prop-group">
        <h3 style="font-size:0.85rem;color:var(--accent);margin-bottom:6px;"><i class="fas ${icon}"></i> ${track.name}</h3>
        <div class="prop-row"><label>Name:</label><input type="text" value="${track.name}" id="prop-track-name"></div>
        <div class="prop-row"><label>Muted:</label><input type="checkbox" ${track.muted?'checked':''} id="prop-track-mute"></div>
    </div>`;

    // --- Type-specific track props ---
    if (track.type === 'bvh') {
        html += `<div class="prop-group">
            <div class="prop-row"><label>Modell:</label><span style="font-size:0.8rem;color:var(--accent);">${track.preset}</span></div>
            <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${track.position[0]}" id="prop-pos-x"></div>
            <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${track.position[2]}" id="prop-pos-z"></div>
        </div>`;
    } else if (track.type === 'camera') {
        html += `<div class="prop-group">
            <div class="prop-row"><label>Aktiv:</label><input type="checkbox" ${track.cameraActive?'checked':''} id="prop-cam-active"></div>
            <div style="margin-top:6px;">
                <button id="prop-cam-add-kf" style="padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;"><i class="fas fa-key"></i> Keyframe setzen (K)</button>
            </div>
            <div style="margin-top:4px;font-size:0.72rem;color:var(--text-muted);">Setzt aktuelle Kamera-Position als Keyframe am Playhead.</div>
        </div>`;
    } else if (track.type === 'light') {
        const lp = track.light?.position || {x:0,y:0,z:0};
        const lc = track.light ? '#' + track.light.color.getHexString() : '#ffffff';
        html += `<div class="prop-group">
            <div class="prop-row"><label>Farbe:</label><input type="color" value="${lc}" id="prop-light-color"></div>
            <div class="prop-row"><label>Intensitaet:</label><input type="number" value="${track.light?.intensity||2}" id="prop-light-intensity" min="0" max="20" step="0.1"></div>
            <div class="prop-row"><label>Sichtbar:</label><input type="checkbox" ${track.lightVisible?'checked':''} id="prop-light-visible"></div>
            <h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Position</h3>
            <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${lp.x.toFixed(2)}" id="prop-light-x"></div>
            <div class="prop-row"><label>Y:</label><input type="number" step="0.1" value="${lp.y.toFixed(2)}" id="prop-light-y"></div>
            <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${lp.z.toFixed(2)}" id="prop-light-z"></div>
            <div style="margin-top:6px;">
                <button id="prop-light-add-kf" style="padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;"><i class="fas fa-key"></i> Keyframe setzen</button>
            </div>
        </div>`;
    } else if (track.type === 'audio') {
        html += `<div class="prop-group">
            <div style="margin-bottom:6px;">
                <button id="prop-audio-load" style="padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;"><i class="fas fa-folder-open"></i> Audio laden</button>
            </div>
        </div>`;
    }

    // --- Clips/Keyframes list ---
    const clipLabel = (track.type === 'camera' || track.type === 'light') ? 'Keyframes' : 'Clips';
    html += `<div class="prop-group">
        <h3 style="font-size:0.85rem;color:var(--text-muted);">${clipLabel} (${track.clips.length})</h3>
        ${track.clips.map((c, i) => {
            const dur = c.type === 'camera_kf' || c.type === 'light_kf' ? `F${c.startFrame}` : `${c.duration.toFixed(1)}s`;
            return `<div class="prop-clip-item" data-clip="${i}" style="font-size:0.78rem;padding:4px 6px;margin:2px 0;border-radius:3px;cursor:pointer;background:${i===selectedClipIdx?'rgba(124,92,191,0.3)':'transparent'};color:${i===selectedClipIdx?'var(--accent)':'var(--text)'};">${c.name} (${dur})</div>`;
        }).join('')}
    </div>`;

    // --- Selected clip/keyframe details ---
    if (clip) {
        if (clip.type === 'camera_kf') {
            const d = clip.data;
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Kamera Keyframe</h3>
                <div class="prop-row"><label>Frame:</label><input type="number" value="${clip.startFrame}" id="prop-kf-frame" min="0"></div>
                <div class="prop-row"><label>Pos X:</label><input type="number" value="${d.position?.x?.toFixed(3)||0}" id="prop-kf-px" step="0.1"></div>
                <div class="prop-row"><label>Pos Y:</label><input type="number" value="${d.position?.y?.toFixed(3)||0}" id="prop-kf-py" step="0.1"></div>
                <div class="prop-row"><label>Pos Z:</label><input type="number" value="${d.position?.z?.toFixed(3)||0}" id="prop-kf-pz" step="0.1"></div>
                <div class="prop-row"><label>Rot X:</label><input type="number" value="${((d.rotation?.x||0)*180/Math.PI).toFixed(1)}" id="prop-kf-rx" step="1"> °</div>
                <div class="prop-row"><label>Rot Y:</label><input type="number" value="${((d.rotation?.y||0)*180/Math.PI).toFixed(1)}" id="prop-kf-ry" step="1"> °</div>
                <div class="prop-row"><label>Rot Z:</label><input type="number" value="${((d.rotation?.z||0)*180/Math.PI).toFixed(1)}" id="prop-kf-rz" step="1"> °</div>
                <div class="prop-row"><label>FOV:</label><input type="number" value="${d.fov||50}" id="prop-kf-fov" min="10" max="120"></div>
                <div class="prop-row"><label>Interp.:</label>
                    <select id="prop-kf-interp">
                        <option value="linear" ${d.interpolation==='linear'?'selected':''}>Linear</option>
                        <option value="smooth" ${d.interpolation==='smooth'?'selected':''}>Smooth</option>
                        <option value="step" ${d.interpolation==='step'?'selected':''}>Step</option>
                    </select>
                </div>
                <div style="margin-top:6px;">
                    <button id="prop-kf-set-view" style="padding:3px 8px;font-size:0.75rem;background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:3px;cursor:pointer;">Aktuelle Ansicht uebernehmen</button>
                </div>
            </div>`;
        } else if (clip.type === 'light_kf') {
            const d = clip.data;
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Licht Keyframe</h3>
                <div class="prop-row"><label>Frame:</label><input type="number" value="${clip.startFrame}" id="prop-lkf-frame" min="0"></div>
                <div class="prop-row"><label>Pos X:</label><input type="number" value="${d.position?.x?.toFixed(2)||0}" id="prop-lkf-px" step="0.1"></div>
                <div class="prop-row"><label>Pos Y:</label><input type="number" value="${d.position?.y?.toFixed(2)||0}" id="prop-lkf-py" step="0.1"></div>
                <div class="prop-row"><label>Pos Z:</label><input type="number" value="${d.position?.z?.toFixed(2)||0}" id="prop-lkf-pz" step="0.1"></div>
                <div class="prop-row"><label>Farbe:</label><input type="color" value="${d.color||'#ffffff'}" id="prop-lkf-color"></div>
                <div class="prop-row"><label>Intensitaet:</label><input type="number" value="${d.intensity||2}" id="prop-lkf-intensity" min="0" max="20" step="0.1"></div>
            </div>`;
        } else if (clip.type === 'audio') {
            const d = clip.data;
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Audio: ${d.fileName||'?'}</h3>
                <div class="prop-row"><label>Datei:</label><span style="font-size:0.75rem;color:var(--text-muted);">${d.fileName||'—'}</span></div>
                <div class="prop-row"><label>Dauer:</label><span style="font-size:0.8rem;">${(d.audioDuration||0).toFixed(1)}s</span></div>
                <div class="prop-row"><label>Start:</label><input type="number" value="${clip.startFrame}" id="prop-audio-start" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Lautstaerke:</label><input type="range" value="${(d.volume||1)*100}" id="prop-audio-vol" min="0" max="100"> <span id="prop-audio-vol-label" style="font-size:0.75rem;">${Math.round((d.volume||1)*100)}%</span></div>
                <div class="prop-row"><label>Fade In:</label><input type="number" value="${d.fadeIn||0}" id="prop-audio-fadein" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Fade Out:</label><input type="number" value="${d.fadeOut||0}" id="prop-audio-fadeout" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Offset:</label><input type="number" value="${d.offset||0}" id="prop-audio-offset" min="0" step="0.1"> <span style="font-size:0.7rem;">s</span></div>
            </div>`;
        } else {
            // BVH clip
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Clip: ${clip.name}</h3>
                <div class="prop-row"><label>Start:</label><input type="number" value="${clip.startFrame}" id="prop-clip-start" min="0"> <span style="font-size:0.7rem;color:var(--text-muted);">frames</span></div>
                <div class="prop-row"><label>Trim In:</label><input type="number" value="${clip.trimIn}" id="prop-clip-trim-in" min="0"></div>
                <div class="prop-row"><label>Trim Out:</label><input type="number" value="${clip.trimOut}" id="prop-clip-trim-out" min="0"></div>
                <div class="prop-row"><label>Speed:</label><input type="number" value="${clip.speed}" id="prop-clip-speed" min="0.1" max="4" step="0.1"></div>
                <div class="prop-row"><label>Smooth:</label><input type="number" value="${clip.smoothSigma}" id="prop-clip-smooth" min="0" max="10" step="0.5"></div>
                <div class="prop-row"><label>Boden:</label><input type="checkbox" ${clip.groundFix?'checked':''} id="prop-clip-ground"></div>
                <div class="prop-row"><label>Blend In:</label><input type="number" value="${clip.blendIn}" id="prop-clip-blend-in" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Blend Out:</label><input type="number" value="${clip.blendOut}" id="prop-clip-blend-out" min="0"> <span style="font-size:0.7rem;">f</span></div>
            </div>`;
        }
    }

    content.innerHTML = html;

    // --- Wire up events ---
    document.getElementById('prop-track-name')?.addEventListener('change', (e) => { track.name = e.target.value; updateTrackHeaders(); });
    document.getElementById('prop-track-mute')?.addEventListener('change', (e) => { track.muted = e.target.checked; });
    document.getElementById('prop-pos-x')?.addEventListener('change', (e) => { track.position[0] = parseFloat(e.target.value)||0; track.group.position.x = track.position[0]; });
    document.getElementById('prop-pos-z')?.addEventListener('change', (e) => { track.position[2] = parseFloat(e.target.value)||0; track.group.position.z = track.position[2]; });

    // Camera track
    document.getElementById('prop-cam-active')?.addEventListener('change', (e) => { track.cameraActive = e.target.checked; });
    document.getElementById('prop-cam-add-kf')?.addEventListener('click', () => addCameraKeyframe(selectedTrackIdx));

    // Light track
    document.getElementById('prop-light-color')?.addEventListener('input', (e) => { if (track.light) track.light.color.set(e.target.value); });
    document.getElementById('prop-light-intensity')?.addEventListener('change', (e) => { if (track.light) track.light.intensity = parseFloat(e.target.value)||2; });
    document.getElementById('prop-light-visible')?.addEventListener('change', (e) => { track.lightVisible = e.target.checked; if (track.lightHelper) track.lightHelper.visible = e.target.checked; });
    ['x','y','z'].forEach(axis => {
        document.getElementById(`prop-light-${axis}`)?.addEventListener('change', (e) => {
            if (track.light) { track.light.position[axis] = parseFloat(e.target.value)||0; if (track.lightHelper) track.lightHelper.position.copy(track.light.position); }
        });
    });
    document.getElementById('prop-light-add-kf')?.addEventListener('click', () => addLightKeyframe(selectedTrackIdx));

    // Audio track
    document.getElementById('prop-audio-load')?.addEventListener('click', () => loadAudioFile(selectedTrackIdx));

    // Clip selection
    document.querySelectorAll('.prop-clip-item').forEach(el => {
        el.addEventListener('click', () => { selectedClipIdx = parseInt(el.dataset.clip); updateProperties(); renderTimeline(); });
    });

    // Camera keyframe editors
    if (clip?.type === 'camera_kf') {
        document.getElementById('prop-kf-frame')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; track.clips.sort((a,b)=>a.startFrame-b.startFrame); renderTimeline(); });
        ['px','py','pz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-kf-${id}`)?.addEventListener('change', (e) => { clip.data.position[axis] = parseFloat(e.target.value)||0; });
        });
        ['rx','ry','rz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-kf-${id}`)?.addEventListener('change', (e) => { clip.data.rotation[axis] = (parseFloat(e.target.value)||0)*Math.PI/180; });
        });
        document.getElementById('prop-kf-fov')?.addEventListener('change', (e) => { clip.data.fov = parseFloat(e.target.value)||50; });
        document.getElementById('prop-kf-interp')?.addEventListener('change', (e) => { clip.data.interpolation = e.target.value; });
        document.getElementById('prop-kf-set-view')?.addEventListener('click', () => {
            clip.data.position = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
            clip.data.rotation = { x: camera.rotation.x, y: camera.rotation.y, z: camera.rotation.z };
            clip.data.fov = camera.fov;
            updateProperties();
        });
    }

    // Light keyframe editors
    if (clip?.type === 'light_kf') {
        document.getElementById('prop-lkf-frame')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; track.clips.sort((a,b)=>a.startFrame-b.startFrame); renderTimeline(); });
        ['px','py','pz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-lkf-${id}`)?.addEventListener('change', (e) => { clip.data.position[axis] = parseFloat(e.target.value)||0; });
        });
        document.getElementById('prop-lkf-color')?.addEventListener('input', (e) => { clip.data.color = e.target.value; });
        document.getElementById('prop-lkf-intensity')?.addEventListener('change', (e) => { clip.data.intensity = parseFloat(e.target.value)||2; });
    }

    // Audio clip editors
    if (clip?.type === 'audio') {
        document.getElementById('prop-audio-start')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; updateDuration(); renderTimeline(); });
        document.getElementById('prop-audio-vol')?.addEventListener('input', (e) => {
            clip.data.volume = parseInt(e.target.value)/100;
            document.getElementById('prop-audio-vol-label').textContent = e.target.value + '%';
        });
        document.getElementById('prop-audio-fadein')?.addEventListener('change', (e) => { clip.data.fadeIn = parseInt(e.target.value)||0; });
        document.getElementById('prop-audio-fadeout')?.addEventListener('change', (e) => { clip.data.fadeOut = parseInt(e.target.value)||0; });
        document.getElementById('prop-audio-offset')?.addEventListener('change', (e) => { clip.data.offset = parseFloat(e.target.value)||0; });
    }

    // BVH clip editors
    if (clip && !clip.type || clip?.type === 'bvh') {
        document.getElementById('prop-clip-start')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; updateDuration(); renderTimeline(); });
        document.getElementById('prop-clip-trim-in')?.addEventListener('change', (e) => { clip.trimIn = Math.max(0, Math.min(clip.totalFrames-1, parseInt(e.target.value)||0)); updateDuration(); renderTimeline(); });
        document.getElementById('prop-clip-trim-out')?.addEventListener('change', (e) => { clip.trimOut = Math.max(0, parseInt(e.target.value)||0); updateDuration(); renderTimeline(); });
        document.getElementById('prop-clip-speed')?.addEventListener('change', (e) => { clip.speed = Math.max(0.1, parseFloat(e.target.value)||1); updateDuration(); renderTimeline(); });
        document.getElementById('prop-clip-smooth')?.addEventListener('change', (e) => { clip.smoothSigma = Math.max(0, parseFloat(e.target.value)||0); });
        document.getElementById('prop-clip-ground')?.addEventListener('change', (e) => { clip.groundFix = e.target.checked; });
        document.getElementById('prop-clip-blend-in')?.addEventListener('change', (e) => { clip.blendIn = Math.max(0, parseInt(e.target.value)||0); });
        document.getElementById('prop-clip-blend-out')?.addEventListener('change', (e) => { clip.blendOut = Math.max(0, parseInt(e.target.value)||0); });
    }
}

// =========================================================================
// Toolbar
// =========================================================================
function setupToolbar() {
    // Track dropdown
    const trackDD = document.getElementById('track-dropdown');
    document.getElementById('btn-add-track')?.addEventListener('click', (e) => { e.stopPropagation(); trackDD?.classList.toggle('open'); });
    document.getElementById('dd-add-bvh')?.addEventListener('click', () => { trackDD?.classList.remove('open'); addTrack(); });
    document.getElementById('dd-add-camera')?.addEventListener('click', () => { trackDD?.classList.remove('open'); addSpecialTrack('camera'); });
    document.getElementById('dd-add-light')?.addEventListener('click', () => { trackDD?.classList.remove('open'); addSpecialTrack('light'); });
    document.getElementById('dd-add-audio')?.addEventListener('click', () => { trackDD?.classList.remove('open'); addSpecialTrack('audio'); });

    document.getElementById('btn-undo')?.addEventListener('click', () => undo());
    document.getElementById('btn-redo')?.addEventListener('click', () => redo());
    document.getElementById('btn-delete-track')?.addEventListener('click', () => removeTrack(selectedTrackIdx));
    document.getElementById('btn-delete-clip')?.addEventListener('click', () => deleteSelectedClip());
    document.getElementById('btn-split')?.addEventListener('click', splitClipAtPlayhead);
    document.getElementById('btn-export-bvh')?.addEventListener('click', exportBVH);
    document.getElementById('btn-export-video')?.addEventListener('click', () => {
        // Switch to Export tab and update range
        switchPropsTab('export');
        const toEl = document.getElementById('export-to');
        if (toEl && (toEl.value === '0' || !toEl.value)) toEl.value = Math.round(project.duration * project.fps);
    });
    // File dropdown
    const fileDD = document.getElementById('file-dropdown');
    document.getElementById('btn-file')?.addEventListener('click', (e) => { e.stopPropagation(); fileDD?.classList.toggle('open'); });
    document.getElementById('dd-file-save')?.addEventListener('click', () => { fileDD?.classList.remove('open'); saveProject(); });
    document.getElementById('dd-file-save-as')?.addEventListener('click', () => { fileDD?.classList.remove('open'); saveProjectAs(); });
    document.getElementById('dd-file-load')?.addEventListener('click', () => { fileDD?.classList.remove('open'); loadProject(); });
    document.getElementById('dd-file-load-last')?.addEventListener('click', () => { fileDD?.classList.remove('open'); loadLastProject(); });
    document.getElementById('dd-file-default')?.addEventListener('click', () => { fileDD?.classList.remove('open'); resetToDefault(); });

    // Tools dropdown
    const toolsDD = document.getElementById('tools-dropdown');
    const toolsBtn = document.getElementById('btn-tools');
    toolsBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        toolsDD.classList.toggle('open');
    });
    document.addEventListener('click', () => {
        fileDD?.classList.remove('open');
        toolsDD?.classList.remove('open');
        trackDD?.classList.remove('open');
        document.getElementById('help-dropdown')?.classList.remove('open');
    });
    document.getElementById('dd-smooth')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        switchPropsTab('tools');
        smoothSelectedClip();
    });
    document.getElementById('dd-ground')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        switchPropsTab('tools');
        groundFixSelectedClip();
    });

    // Properties panel tabs
    document.querySelectorAll('.props-tab').forEach(tab => {
        tab.addEventListener('click', () => switchPropsTab(tab.dataset.tab));
    });

    // Tools panel buttons
    document.getElementById('tool-smooth-apply')?.addEventListener('click', smoothSelectedClip);
    document.getElementById('tool-ground-apply')?.addEventListener('click', groundFixSelectedClip);
    document.getElementById('tool-smooth-sigma')?.addEventListener('input', (e) => {
        const sigma = parseFloat(e.target.value) || 2;
        const radiusEl = document.getElementById('tool-smooth-radius');
        if (radiusEl) radiusEl.textContent = Math.ceil(sigma * 3);
    });

    // Track context menu
    const trackCtx = document.getElementById('track-context-menu');
    document.addEventListener('click', () => { if (trackCtx) trackCtx.style.display = 'none'; });
    document.getElementById('track-ctx-delete')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (selectedTrackIdx >= 0) removeTrack(selectedTrackIdx);
    });
    document.getElementById('track-ctx-rename')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (selectedTrackIdx >= 0) {
            const track = project.tracks[selectedTrackIdx];
            const newName = prompt('Neuer Track-Name:', track.name);
            if (newName && newName !== track.name) { track.name = newName; updateTrackHeaders(); updateProperties(); }
        }
    });
    document.getElementById('track-ctx-mute')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (selectedTrackIdx >= 0) {
            const track = project.tracks[selectedTrackIdx];
            track.muted = !track.muted;
            updateProperties();
        }
    });

    // Help dropdown
    const helpDD = document.getElementById('help-dropdown');
    document.getElementById('btn-help')?.addEventListener('click', (e) => { e.stopPropagation(); helpDD?.classList.toggle('open'); });
    document.getElementById('dd-help-tracks')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('tracks'); });
    document.getElementById('dd-help-camera')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('camera'); });
    document.getElementById('dd-help-light')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('light'); });
    document.getElementById('dd-help-audio')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('audio'); });
    document.getElementById('dd-help-shortcuts')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('shortcuts'); });
    document.getElementById('dd-help-animations')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('animations'); });
    document.getElementById('help-modal-close')?.addEventListener('click', () => { document.getElementById('help-modal').style.display = 'none'; });
    document.getElementById('help-modal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) e.currentTarget.style.display = 'none'; });
}

// =========================================================================
// Help system
// =========================================================================
const HELP_CONTENT = {
    tracks: {
        title: 'Tracks',
        body: `
<p><b>BVH Studio</b> arbeitet mit verschiedenen Track-Typen in einer gemeinsamen Timeline:</p>
<h4 style="color:var(--accent);margin:12px 0 6px;"><i class="fas fa-running"></i> BVH Track</h4>
<ul>
<li>Enthaelt Skelett-Animationen (BVH-Dateien)</li>
<li>Clips aus der <b>BVH Bibliothek</b> per Doppelklick oder Drag & Drop hinzufuegen</li>
<li>Clips koennen <b>verschoben</b> (Drag), <b>gesplittet</b> (S), <b>dupliziert</b> und <b>geloescht</b> (Del) werden</li>
<li>Rechtsklick auf Clip fuer Kontextmenue</li>
<li>Standard-Modell: Rig2 (konfigurierbar in Einstellungen)</li>
</ul>
<h4 style="color:#00bcd4;margin:12px 0 6px;"><i class="fas fa-video"></i> Kamera Track</h4>
<ul>
<li>Steuert die Kameraposition waehrend der Wiedergabe</li>
<li>Keyframes setzen: <b>K</b> druecken oder Button im Eigenschaften-Tab</li>
<li>Zwischen Keyframes wird interpoliert (Linear / Smooth / Step)</li>
</ul>
<h4 style="color:#ffc107;margin:12px 0 6px;"><i class="fas fa-lightbulb"></i> Licht Track</h4>
<ul>
<li>Erzeugt ein Punktlicht in der Szene</li>
<li>Position, Farbe und Intensitaet ueber Eigenschaften-Panel aendern</li>
<li>Keyframes fuer animiertes Licht</li>
</ul>
<h4 style="color:#4caf50;margin:12px 0 6px;"><i class="fas fa-music"></i> Audio Track</h4>
<ul>
<li>Audio-Datei (MP3/WAV/OGG) laden und zur Timeline synchronisieren</li>
<li>Lautstaerke, Fade In/Out und Offset konfigurierbar</li>
</ul>
<p style="margin-top:12px;"><b>Track hinzufuegen:</b> Klick auf "+ Track" in der Toolbar, dann Typ waehlen.</p>
<p><b>Track loeschen:</b> Track auswaehlen, dann Papierkorb-Button.</p>
`},
    camera: {
        title: 'Kamera',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">Kamera-Track Funktionen</h4>
<p>Der Kamera-Track steuert die 3D-Kamera waehrend der Wiedergabe. Im Stopp-Modus bleibt die normale Maussteuerung (OrbitControls) aktiv.</p>

<h4 style="margin:14px 0 6px;">Keyframe setzen</h4>
<ol>
<li>Kamera-Track in der Timeline auswaehlen</li>
<li>Kamera mit Maus in die gewuenschte Position bewegen</li>
<li><b>K</b> druecken oder "Keyframe setzen" Button klicken</li>
<li>Die aktuelle Kameraposition, Rotation und FOV werden als Keyframe am Playhead gespeichert</li>
</ol>

<h4 style="margin:14px 0 6px;">Keyframe bearbeiten</h4>
<p>Klick auf einen Keyframe (Raute ◇) in der Timeline. Im Eigenschaften-Panel erscheinen:</p>
<ul>
<li><b>Position X/Y/Z</b> — Kameraposition in Metern</li>
<li><b>Rotation X/Y/Z</b> — Kamerarotation in Grad</li>
<li><b>FOV</b> — Sichtfeld (10-120 Grad)</li>
<li><b>Interpolation</b> — Linear / Smooth (weich) / Step (sprunghaft)</li>
<li><b>"Aktuelle Ansicht uebernehmen"</b> — ueberschreibt den Keyframe mit der aktuellen Kameraansicht</li>
</ul>

<h4 style="margin:14px 0 6px;">Wiedergabe</h4>
<p>Bei <b>Play</b> wird die Kamera automatisch zwischen den Keyframes interpoliert. Die Maussteuerung wird waehrend der Wiedergabe deaktiviert und beim Stopp wieder aktiviert.</p>
<p><b>"Aktiv" Checkbox</b>: Deaktivieren um den Kamera-Track temporaer zu ignorieren.</p>
`},
    light: {
        title: 'Licht',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">Licht-Track Funktionen</h4>
<p>Ein Licht-Track erzeugt ein <b>Punktlicht</b> in der 3D-Szene. Mehrere Licht-Tracks koennen gleichzeitig aktiv sein.</p>

<h4 style="margin:14px 0 6px;">Licht konfigurieren</h4>
<p>Im <b>Eigenschaften-Tab</b> (rechts) bei ausgewaehltem Licht-Track:</p>
<ul>
<li><b>Farbe</b> — Lichtfarbe (Color Picker)</li>
<li><b>Intensitaet</b> — Helligkeit (0-20)</li>
<li><b>Sichtbar</b> — Zeigt/versteckt die Lichtposition als gelbe Kugel in der Szene</li>
<li><b>Position X/Y/Z</b> — Lichtposition in Metern</li>
</ul>

<h4 style="margin:14px 0 6px;">Licht-Keyframes</h4>
<ol>
<li>Licht-Track auswaehlen</li>
<li>Position/Farbe/Intensitaet einstellen</li>
<li><b>K</b> druecken oder "Keyframe setzen" Button klicken</li>
<li>Bei Wiedergabe wird zwischen Keyframes interpoliert (Position, Farbe, Intensitaet)</li>
</ol>

<h4 style="margin:14px 0 6px;">Lichtposition-Helper</h4>
<p>Die gelbe Kugel zeigt die aktuelle Lichtposition in der Szene. Ueber die Checkbox "Sichtbar" kann sie ein- und ausgeblendet werden.</p>
`},
    audio: {
        title: 'Audio',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">Audio-Track Funktionen</h4>
<p>Audio-Tracks synchronisieren Audiodateien zur Timeline-Wiedergabe.</p>

<h4 style="margin:14px 0 6px;">Audio laden</h4>
<ol>
<li>Audio-Track hinzufuegen (+ Track > Audio Track)</li>
<li>Im Eigenschaften-Tab: "Audio laden" Button klicken</li>
<li>MP3, WAV oder OGG Datei auswaehlen</li>
<li>Der Audio-Clip erscheint als gruenes Rechteck in der Timeline</li>
</ol>

<h4 style="margin:14px 0 6px;">Audio bearbeiten</h4>
<p>Klick auf den Audio-Clip in der Timeline. Im Eigenschaften-Panel:</p>
<ul>
<li><b>Lautstaerke</b> — Schieberegler 0-100%</li>
<li><b>Fade In</b> — Einblende-Dauer in Frames</li>
<li><b>Fade Out</b> — Ausblende-Dauer in Frames</li>
<li><b>Offset</b> — Startpunkt innerhalb der Audiodatei (Sekunden)</li>
<li><b>Start</b> — Position auf der Timeline (Frame)</li>
</ul>

<h4 style="margin:14px 0 6px;">Wiedergabe</h4>
<p>Audio wird automatisch zur Timeline synchronisiert. Bei <b>Play</b> startet die Audiowiedergabe am aktuellen Playhead. Bei <b>Pause/Stop</b> wird die Audiowiedergabe gestoppt.</p>
<p>Audio-Clips koennen wie BVH-Clips <b>verschoben</b> und <b>geloescht</b> werden.</p>
`},
    shortcuts: {
        title: 'Tastenkuerzel',
        body: `
<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Space</kbd></td><td>Play / Pause</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">&#8592;</kbd> <kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">&#8594;</kbd></td><td>Frame vor / zurueck</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">S</kbd></td><td>Clip splitten am Playhead</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Del</kbd></td><td>Ausgewaehlten Clip loeschen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">K</kbd></td><td>Kamera/Licht Keyframe setzen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Ctrl+Shift+U</kbd></td><td>Undo (bis zu 20 Schritte)</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Redo</kbd></td><td>Redo (nur per Button)</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Mausrad</b></td><td>Timeline scrollen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Ctrl + Mausrad</b></td><td>Timeline zoomen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Mittlere Maustaste</b></td><td>Timeline pannen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Alt + Klick</b></td><td>Timeline pannen</td></tr>
<tr><td style="padding:6px 0;"><b>Rechtsklick auf Clip</b></td><td>Kontextmenue</td></tr>
</table>
`},
    animations: {
        title: 'BVH Bibliothek verwalten',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">BVH Bibliothek im Studio</h4>
<p>Die BVH Bibliothek links zeigt alle BVH-Dateien gruppiert nach Ordnern. Animationen koennen per <b>Doppelklick</b> oder <b>Drag &amp; Drop</b> zum ausgewaehlten Track hinzugefuegt werden.</p>

<h4 style="margin:14px 0 6px;">Bibliothek-Toolbar</h4>
<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
<tr style="border-bottom:1px solid var(--border);"><td style="padding:5px 0;width:40px;text-align:center;"><i class="fas fa-folder-plus"></i></td><td><b>Neuer Ordner</b> — Erstellt einen neuen Kategorie-Ordner</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:5px 0;text-align:center;"><i class="fas fa-pen"></i></td><td><b>Umbenennen</b> — Benennt die ausgewaehlte Animation um</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:5px 0;text-align:center;"><i class="fas fa-trash"></i></td><td><b>Loeschen</b> — Loescht die ausgewaehlte Animation</td></tr>
<tr><td style="padding:5px 0;text-align:center;"><i class="fas fa-sync-alt"></i></td><td><b>Aktualisieren</b> — Laedt die Bibliothek neu</td></tr>
</table>

<h4 style="margin:14px 0 6px;">Kontextmenue (Rechtsklick)</h4>
<p><b>Auf eine Animation:</b></p>
<ul style="margin:4px 0;">
<li><b>Zum Track hinzufuegen</b> — Fuegt die Animation als Clip zum ausgewaehlten Track hinzu</li>
<li><b>Umbenennen</b> — Aendert den Dateinamen der BVH-Datei</li>
<li><b>Verschieben nach...</b> — Verschiebt die Datei in einen anderen Ordner</li>
<li><b>Loeschen</b> — Entfernt die BVH-Datei (mit Bestaetigung)</li>
</ul>
<p><b>Auf einen Ordner:</b></p>
<ul style="margin:4px 0;">
<li><b>Ordner umbenennen</b> — Aendert den Ordnernamen</li>
<li><b>Neuer Ordner</b> — Erstellt einen neuen Ordner</li>
<li><b>Ordner loeschen</b> — Entfernt einen leeren Ordner</li>
</ul>

<h4 style="margin:14px 0 6px;">Animation hinzufuegen</h4>
<ul style="margin:4px 0;">
<li><b>Doppelklick</b> auf eine Animation — fuegt sie zum ausgewaehlten Track hinzu</li>
<li><b>Drag &amp; Drop</b> — ziehe eine Animation auf einen Track-Header oder in die Timeline</li>
<li>Wird auf leere Stelle in der Timeline gezogen, wird automatisch ein neuer Track erstellt</li>
</ul>

<h4 style="margin:14px 0 6px;">Clips in der Timeline bearbeiten</h4>
<p>Clips koennen direkt in der Timeline per Maus bearbeitet werden:</p>
<ul style="margin:4px 0;">
<li><b>Verschieben</b> — Clip in der Mitte greifen und nach links/rechts ziehen</li>
<li><b>Trimmen (Anfang)</b> — Linken Rand des Clips greifen und ziehen → kuerzt die Animation von vorne</li>
<li><b>Trimmen (Ende)</b> — Rechten Rand des Clips greifen und ziehen → kuerzt die Animation von hinten</li>
<li>Der Cursor wechselt zu <b>↔</b> am Clip-Rand und zu <b>✋</b> in der Mitte</li>
</ul>
<p><b>Kontextmenue (Rechtsklick auf Clip):</b></p>
<ul style="margin:4px 0;">
<li><b>Split an Playhead (S)</b> — Teilt den Clip an der Playhead-Position</li>
<li><b>Duplizieren</b> — Erstellt eine Kopie hinter dem Clip</li>
<li><b>Loeschen (Del)</b> — Entfernt den Clip</li>
<li><b>Anfang trimmen (+10f)</b> — Kuerzt den Clip um 10 Frames von vorne</li>
<li><b>Ende trimmen (+10f)</b> — Kuerzt den Clip um 10 Frames von hinten</li>
<li><b>Trim zuruecksetzen</b> — Stellt die volle Laenge wieder her</li>
<li><b>BVH speichern unter...</b> — Speichert die BVH-Datei</li>
<li><b>Smooth / Bodenniveau</b> — Tools auf den Clip anwenden</li>
</ul>

<h4 style="margin:14px 0 6px;">Hinweise</h4>
<ul style="margin:4px 0;">
<li>Klick auf eine Animation markiert sie (lila) fuer Toolbar-Aktionen</li>
<li>Ordner koennen nur geloescht werden wenn sie leer sind</li>
<li>Beim Umbenennen/Verschieben wird auch die Retarget-Cache-Datei (.json) mitverschoben</li>
<li>Alle Aenderungen werden sofort auf der Festplatte ausgefuehrt</li>
<li>Wird der letzte Clip eines Tracks geloescht, verschwindet das 3D-Modell automatisch</li>
</ul>
`},
};

function showHelp(topic) {
    const h = HELP_CONTENT[topic];
    if (!h) return;
    document.getElementById('help-modal-title').innerHTML = `<i class="fas fa-question-circle"></i> ${h.title}`;
    document.getElementById('help-modal-body').innerHTML = h.body;
    document.getElementById('help-modal').style.display = 'flex';
}

function switchPropsTab(tabName) {
    document.querySelectorAll('.props-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    document.querySelectorAll('.props-tab-content').forEach(c => c.classList.toggle('active', c.id === `props-tab-${tabName}`));
}

function duplicateSelectedClip() {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) return;
    pushUndo('Duplizieren');
    const track = project.tracks[selectedTrackIdx];
    const orig = track.clips[selectedClipIdx];
    const copy = new Clip(orig.category, orig.name, orig.totalFrames, orig.fps);
    copy.startFrame = orig.endFrame;  // place after original
    copy.trimIn = orig.trimIn;
    copy.trimOut = orig.trimOut;
    copy.speed = orig.speed;
    copy.smoothSigma = orig.smoothSigma;
    copy.groundFix = orig.groundFix;
    copy.animClip = orig.animClip;  // share the same clip data
    track.clips.push(copy);
    updateDuration();
    renderTimeline();
    updateProperties();
    console.log('[BVH Studio] Clip duplicated');
}

async function saveBvhAs() {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) { alert('Clip auswaehlen.'); return; }
    const clip = project.tracks[selectedTrackIdx].clips[selectedClipIdx];
    try {
        const url = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
        const resp = await fetch(url);
        const text = await resp.text();
        const blob = new Blob([text], { type: 'text/plain' });
        const defaultName = `${clip.name}.bvh`;

        // Use File System Access API for native "Save As" dialog
        if (window.showSaveFilePicker) {
            try {
                const handle = await window.showSaveFilePicker({
                    suggestedName: defaultName,
                    types: [{
                        description: 'BVH Motion Capture',
                        accept: { 'text/plain': ['.bvh'] },
                    }],
                });
                const writable = await handle.createWritable();
                await writable.write(blob);
                await writable.close();
                console.log(`[BVH Studio] BVH saved via picker: ${handle.name}`);
                return;
            } catch (pickerErr) {
                if (pickerErr.name === 'AbortError') return;  // user cancelled
                console.warn('[BVH Studio] File picker failed, fallback to download:', pickerErr);
            }
        }

        // Fallback: classic download
        const dlUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = dlUrl;
        a.download = defaultName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(dlUrl);
        console.log(`[BVH Studio] BVH downloaded: ${defaultName}`);
    } catch (e) {
        alert('BVH speichern fehlgeschlagen: ' + e.message);
    }
}

function deleteSelectedClip() {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) return;
    const track = project.tracks[selectedTrackIdx];
    if (!track || selectedClipIdx >= track.clips.length) return;
    pushUndo('Clip loeschen');
    const clip = track.clips[selectedClipIdx];

    // Uncache the AnimationClip from the mixer so it doesn't linger
    if (track.mixer) {
        track.mixer.stopAllAction();
        if (clip.animClip) track.mixer.uncacheClip(clip.animClip);
    }
    track._activeClip = null;
    track._activeAction = null;

    track.clips.splice(selectedClipIdx, 1);
    selectedClipIdx = -1;
    updateDuration();
    renderTimeline();
    updateProperties();

    // If no more clips on this BVH track, hide the model and stop playback
    if (track.type === 'bvh' && track.clips.length === 0) {
        if (track.mesh) track.mesh.visible = false;
        if (track.skeleton) track.skeleton.skeleton.pose();
    }

    // Stop playback if no clips left anywhere
    const anyClips = project.tracks.some(t => t.clips.length > 0);
    if (!anyClips && playing) {
        playing = false;
        const icon = document.getElementById('pb-play-icon');
        if (icon) icon.className = 'fas fa-play';
    }
    // Reset skeleton to rest pose
    if (track.skeleton) track.skeleton.skeleton.pose();

    console.log('[BVH Studio] Clip deleted');
}

function trimSelectedClip(mode, frames = 10) {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) return;
    pushUndo('Trim');
    const clip = project.tracks[selectedTrackIdx].clips[selectedClipIdx];
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
    updateDuration();
    renderTimeline();
    updateProperties();
    console.log(`[BVH Studio] Trim ${mode}: in=${clip.trimIn}, out=${clip.trimOut}`);
}

function splitClipAtPlayhead() {
    if (selectedTrackIdx < 0) return;
    pushUndo('Split');
    const track = project.tracks[selectedTrackIdx];
    const t = playheadFrame / project.fps;
    for (let i = 0; i < track.clips.length; i++) {
        const clip = track.clips[i];
        const cs = clip.startFrame / project.fps;
        const ce = cs + clip.duration;
        if (t > cs && t < ce) {
            const splitFrame = Math.round((t - cs) * clip.fps * clip.speed) + clip.trimIn;
            // Clone clip
            const clip2 = new Clip(clip.category, clip.name, clip.totalFrames, clip.fps);
            clip2.startFrame = playheadFrame;
            clip2.trimIn = splitFrame;
            clip2.trimOut = clip.trimOut;
            clip2.speed = clip.speed;
            clip2.animClip = clip.animClip;
            // Trim original
            clip.trimOut = clip.totalFrames - splitFrame;
            track.clips.splice(i + 1, 0, clip2);
            updateDuration();
            renderTimeline();
            console.log(`[BVH Studio] Split clip at frame ${splitFrame}`);
            break;
        }
    }
}

// =========================================================================
// Smoothing
// =========================================================================
function smoothSelectedClip() {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) { alert('Clip auswaehlen.'); return; }
    pushUndo('Smooth');
    const clip = project.tracks[selectedTrackIdx].clips[selectedClipIdx];
    if (!clip.animClip) { alert('Clip hat keine Animation.'); return; }

    // Read sigma from tools panel, fallback to clip property
    const sigmaInput = document.getElementById('tool-smooth-sigma');
    const sigma = sigmaInput ? parseFloat(sigmaInput.value) || 2 : (clip.smoothSigma || 2);
    if (sigma <= 0) { alert('Sigma muss > 0 sein.'); return; }

    const mode = document.getElementById('tool-smooth-mode')?.value || 'all';

    const radius = Math.ceil(sigma * 3);
    const kernel = [];
    let ksum = 0;
    for (let i = -radius; i <= radius; i++) {
        const v = Math.exp(-0.5 * (i / sigma) ** 2);
        kernel.push(v); ksum += v;
    }
    for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;

    // Filter bone names by mode
    const HAND_BONES = ['hand', 'finger', 'thumb', 'palm'];
    const BODY_ONLY_SKIP = [...HAND_BONES];

    let smoothedCount = 0;
    for (const track of clip.animClip.tracks) {
        const tn = track.name.toLowerCase();
        if (mode === 'body' && HAND_BONES.some(h => tn.includes(h))) continue;
        if (mode === 'hands' && !HAND_BONES.some(h => tn.includes(h))) continue;

        const stride = track.getValueSize();
        const nKeys = track.values.length / stride;
        const orig = new Float32Array(track.values);
        for (let c = 0; c < stride; c++) {
            for (let k = 0; k < nKeys; k++) {
                let sum = 0;
                for (let j = 0; j < kernel.length; j++) {
                    const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                    sum += kernel[j] * orig[idx * stride + c];
                }
                track.values[k * stride + c] = sum;
            }
        }
        // Re-normalize quaternions
        if (stride === 4) {
            for (let k = 0; k < nKeys; k++) {
                const i = k * 4;
                const len = Math.sqrt(track.values[i]**2 + track.values[i+1]**2 + track.values[i+2]**2 + track.values[i+3]**2);
                if (len > 1e-8) { track.values[i]/=len; track.values[i+1]/=len; track.values[i+2]/=len; track.values[i+3]/=len; }
            }
        }
        smoothedCount++;
    }
    // Update clip property
    clip.smoothSigma = sigma;
    updateProperties();
    console.log(`[BVH Studio] Smoothed ${clip.name}: sigma=${sigma}, mode=${mode}, ${smoothedCount} tracks`);
}

// =========================================================================
// Ground Fix (Bodenniveau)
// =========================================================================
async function groundFixSelectedClip() {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) { alert('Clip auswaehlen.'); return; }
    pushUndo('Bodenniveau');
    const track = project.tracks[selectedTrackIdx];
    const clip = track.clips[selectedClipIdx];
    if (!clip.animClip || !track.skeleton) { alert('Clip oder Skeleton nicht geladen.'); return; }

    // Read desired ground offset from Tools panel (default 0.03m = 3cm)
    const groundOffset = parseFloat(document.getElementById('tool-ground-offset')?.value) || 0.03;

    const skel = track.skeleton;
    const bones = skel.skeleton.bones;
    const rootBone = skel.rootBone;

    // Create temporary mixer to evaluate each frame
    const tmpMixer = new THREE.AnimationMixer(track.mesh);
    const tmpAction = tmpMixer.clipAction(clip.animClip);
    tmpAction.play();

    const tmpV = new THREE.Vector3();

    // Find position track for root bone
    let posTrack = null;
    for (const t of clip.animClip.tracks) {
        if (t.name.includes('.position')) { posTrack = t; break; }
    }
    if (!posTrack) {
        alert('Kein Position-Track gefunden.');
        tmpAction.stop(); tmpMixer.stopAllAction();
        return;
    }

    // Identify foot bones (left + right)
    const footBones = bones.filter(b => {
        const n = b.name.toLowerCase();
        return n.includes('foot') || n.includes('toe') || n.includes('heel');
    });
    if (footBones.length === 0) {
        alert('Keine Fuss-Knochen gefunden.');
        tmpAction.stop(); tmpMixer.stopAllAction();
        return;
    }
    console.log(`[BVH Studio] Ground fix: ${footBones.length} foot bones: ${footBones.map(b => b.name).join(', ')}`);

    const nKeys = posTrack.times.length;
    let corrected = 0;

    for (let f = 0; f < nKeys; f++) {
        const t = posTrack.times[f];
        tmpMixer.setTime(t);
        rootBone.updateWorldMatrix(true, true);

        // Find lowest foot bone Y (considering both left and right)
        let minY = Infinity;
        for (const b of footBones) {
            b.getWorldPosition(tmpV);
            if (tmpV.y < minY) minY = tmpV.y;
        }

        // If foot is below ground (minY < 0): correct to exactly 0
        // If foot is above ground (minY >= 0): correct to groundOffset
        const target = minY < 0 ? 0 : groundOffset;
        const correction = minY - target;
        if (Math.abs(correction) > 0.001) {
            const idx = f * 3 + 1;  // Y component (position is vec3: x,y,z)
            posTrack.values[idx] -= correction;
            corrected++;
        }
    }

    tmpAction.stop();
    tmpMixer.stopAllAction();

    clip.groundFix = true;
    updateProperties();

    if (corrected === 0) {
        console.log(`[BVH Studio] ${clip.name}: bereits auf Bodenniveau.`);
        applyPlayhead();
        return;
    }

    console.log(`[BVH Studio] Ground fix: ${corrected}/${nKeys} Frames korrigiert fuer ${clip.name}`);
    applyPlayhead();

    // Save corrected BVH to disk
    try {
        // Fetch original BVH text
        const bvhUrl = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
        const bvhResp = await fetch(bvhUrl);
        const bvhText = await bvhResp.text();
        const lines = bvhText.split('\n');

        // Find Yposition channel index
        let yPosChannel = -1, foundRoot = false;
        for (let i = 0; i < lines.length; i++) {
            const trimmed = lines[i].trim();
            if (trimmed.startsWith('ROOT ')) { foundRoot = true; continue; }
            if (foundRoot && trimmed.startsWith('CHANNELS')) {
                const parts = trimmed.split(/\s+/);
                for (let c = 2; c < parts.length; c++) {
                    if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; }
                }
                break;
            }
        }

        if (yPosChannel < 0) {
            console.warn('[BVH Studio] Yposition channel not found in BVH, skip save.');
            return;
        }

        // Find motion data lines
        const motionIdx = lines.findIndex(l => l.trim() === 'MOTION');
        if (motionIdx < 0) return;
        let dataStart = motionIdx + 1;
        while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) dataStart++;

        const frameLines = [];
        for (let i = dataStart; i < lines.length; i++) {
            if (lines[i].trim().match(/^[\d\-\.]/)) frameLines.push(i);
        }

        // Apply corrections from posTrack to BVH text
        for (let f = 0; f < Math.min(nKeys, frameLines.length); f++) {
            const li = frameLines[f];
            const vals = lines[li].trim().split(/\s+/);
            vals[yPosChannel] = posTrack.values[f * 3 + 1].toFixed(6);
            lines[li] = vals.join(' ');
        }

        // Save via API
        const saveResp = await fetch('/api/character/save-bvh-text/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: clip.category, name: clip.name, bvh_text: lines.join('\n') }),
        });
        if (saveResp.ok) {
            console.log(`[BVH Studio] BVH saved: ${clip.category}/${clip.name}`);
        } else {
            console.warn(`[BVH Studio] BVH save failed: ${await saveResp.text()}`);
        }
    } catch (e) {
        console.error('[BVH Studio] BVH save error:', e);
    }
}

// =========================================================================
// Export (Phase 4)
// =========================================================================
async function exportBVH() {
    if (selectedTrackIdx < 0) { alert('Track auswaehlen.'); return; }
    const track = project.tracks[selectedTrackIdx];
    if (track.clips.length === 0) { alert('Track hat keine Clips.'); return; }

    // For each clip, fetch the original BVH text and concatenate
    const bvhTexts = [];
    for (const clip of track.clips) {
        try {
            const url = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
            const resp = await fetch(url);
            const text = await resp.text();
            bvhTexts.push({ clip, text });
        } catch (e) {
            console.error(`Failed to fetch BVH for ${clip.name}:`, e);
        }
    }

    if (bvhTexts.length === 0) { alert('Keine BVH Daten.'); return; }

    // For single clip: trim and download
    // For multiple clips: download each separately (BVH doesn't support multi-skeleton)
    if (bvhTexts.length === 1) {
        const blob = new Blob([bvhTexts[0].text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url;
        a.download = `${track.name}_${bvhTexts[0].clip.name}.bvh`;
        a.click(); URL.revokeObjectURL(url);
    } else {
        // Download all as individual files
        for (const { clip, text } of bvhTexts) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url;
            a.download = `${track.name}_${clip.name}.bvh`;
            a.click(); URL.revokeObjectURL(url);
            await new Promise(r => setTimeout(r, 500));
        }
    }
    console.log(`[BVH Studio] Exported ${bvhTexts.length} BVH file(s) for track "${track.name}"`);
}

// =========================================================================
// Video Export (non-blocking, offscreen renderer)
// =========================================================================
let exportCancelled = false;

function setupExportPanel() {
    // Pre-fill target dir from prefs
    const dirEl = document.getElementById('export-target-dir');
    if (dirEl && project.videoOutputPath) dirEl.value = project.videoOutputPath;

    // Set default range from project duration
    const updateRange = () => {
        const toEl = document.getElementById('export-to');
        if (toEl && toEl.value === '0') toEl.value = Math.round(project.duration * project.fps);
        const fpsEl = document.getElementById('export-fps');
        if (fpsEl) fpsEl.value = String(project.fps);
    };
    // Update range on tab switch
    const origSwitch = switchPropsTab;

    document.getElementById('export-start')?.addEventListener('click', startExport);
    document.getElementById('export-cancel')?.addEventListener('click', () => { exportCancelled = true; });

    // Export engine info
    document.getElementById('export-engine')?.addEventListener('change', (e) => {
        console.log(`[BVH Studio] Export engine: ${e.target.value}`);
    });

    // Auto-update frame range + target dir when export tab opens
    document.querySelectorAll('.props-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            if (tab.dataset.tab === 'export') {
                updateRange();
                const dirEl = document.getElementById('export-target-dir');
                if (dirEl && !dirEl.value) dirEl.value = project.videoOutputPath || '';
            }
        });
    });
}

async function startExport() {
    const fromFrame = parseInt(document.getElementById('export-from')?.value) || 0;
    let toFrame = parseInt(document.getElementById('export-to')?.value) || 0;
    const fps = parseInt(document.getElementById('export-fps')?.value) || project.fps;
    const resolution = parseInt(document.getElementById('export-resolution')?.value) || 1080;
    const crf = document.getElementById('export-quality')?.value || '18';
    const engine = document.getElementById('export-engine')?.value || 'server';
    const filename = document.getElementById('export-filename')?.value || 'bvh_studio_export.mp4';

    if (toFrame <= fromFrame) toFrame = Math.round(project.duration * project.fps);
    if (toFrame <= fromFrame) { alert('Keine Frames zum Exportieren.'); return; }

    const totalFrames = toFrame - fromFrame;
    exportCancelled = false;

    // UI: show progress, cancel button
    const progressDiv = document.getElementById('export-progress');
    const statusText = document.getElementById('export-status-text');
    const progressBar = document.getElementById('export-progress-bar');
    const startBtn = document.getElementById('export-start');
    const cancelBtn = document.getElementById('export-cancel');
    progressDiv.style.display = '';
    cancelBtn.style.display = '';
    startBtn.disabled = true;
    startBtn.style.opacity = '0.5';

    // Create offscreen renderer (same size as export resolution)
    const aspect = 16 / 9;
    const expW = Math.round(resolution * aspect);
    const expH = resolution;
    const offCanvas = document.createElement('canvas');
    offCanvas.width = expW;
    offCanvas.height = expH;
    const offRenderer = new THREE.WebGLRenderer({ canvas: offCanvas, antialias: true, preserveDrawingBuffer: true });
    offRenderer.setSize(expW, expH, false);
    offRenderer.setPixelRatio(1);

    // Use same camera with adjusted aspect
    const origAspect = camera.aspect;
    camera.aspect = expW / expH;
    camera.updateProjectionMatrix();

    const wasPlaying = playing;
    playing = false;

    if (engine === 'server') {
        await exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, crf, filename, statusText, progressBar);
    } else {
        await exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText, progressBar);
    }

    // Cleanup
    offRenderer.dispose();
    camera.aspect = origAspect;
    camera.updateProjectionMatrix();
    if (wasPlaying) playing = true;

    // Reset UI
    progressDiv.style.display = 'none';
    cancelBtn.style.display = 'none';
    startBtn.disabled = false;
    startBtn.style.opacity = '1';
}

/** Save blob with native "Save As" dialog, fallback to download */
async function saveBlobAs(blob, suggestedName, mimeType) {
    if (window.showSaveFilePicker) {
        try {
            const ext = '.' + suggestedName.split('.').pop();
            const handle = await window.showSaveFilePicker({
                suggestedName,
                types: [{ description: 'Video', accept: { [mimeType]: [ext] } }],
            });
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            console.log(`[BVH Studio] Saved via picker: ${handle.name}`);
            return;
        } catch (e) {
            if (e.name === 'AbortError') return;
            console.warn('[BVH Studio] Picker failed, fallback:', e);
        }
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = suggestedName;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, crf, filename, statusText, progressBar) {
    const totalFrames = toFrame - fromFrame;
    const frames = [];

    // Phase 1: Capture frames
    for (let f = fromFrame; f < toFrame; f++) {
        if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }

        playheadFrame = f;
        applyPlayhead();
        offRenderer.render(scene, camera);

        const blob = await new Promise(r => offCanvas.toBlob(r, 'image/png'));
        frames.push(blob);

        const pct = ((f - fromFrame) / totalFrames * 100).toFixed(0);
        statusText.textContent = `Aufnahme: Frame ${f - fromFrame + 1}/${totalFrames} (${pct}%)`;
        progressBar.style.width = `${pct * 0.8}%`;  // 80% for capture, 20% for encoding

        // Yield to keep UI responsive
        if ((f - fromFrame) % 5 === 0) await new Promise(r => setTimeout(r, 0));
    }

    if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }

    // Phase 2: Send to server
    statusText.textContent = 'Encoding auf Server...';
    progressBar.style.width = '85%';

    const formData = new FormData();
    frames.forEach((blob, i) => formData.append('frames', blob, `${String(i).padStart(6, '0')}.png`));
    formData.append('fps', fps);
    formData.append('format', 'mp4');
    formData.append('crf', crf);

    // Build save path — always save to server disk
    const outputDir = (document.getElementById('export-target-dir')?.value || '').trim()
        || 'A:/3DTools/HumanBodyWeb/media/output';
    const sep = outputDir.includes('\\') ? '\\' : '/';
    const savePath = outputDir.replace(/[/\\]$/, '') + sep + filename;
    formData.append('save_path', savePath);

    try {
        const resp = await fetch('/api/theatre/encode-frames/', { method: 'POST', body: formData });
        if (resp.ok) {
            progressBar.style.width = '100%';
            const ct = resp.headers.get('content-type') || '';
            if (ct.includes('application/json')) {
                // Server saved to disk
                const data = await resp.json();
                statusText.textContent = `Gespeichert: ${data.saved}`;
            } else {
                // Server returned file blob (no save_path configured)
                statusText.textContent = 'Fertig! Speichern...';
                const blob = await resp.blob();
                await saveBlobAs(blob, filename, 'video/mp4');
            }
        } else {
            statusText.textContent = 'Encoding fehlgeschlagen: ' + await resp.text();
        }
    } catch (e) {
        statusText.textContent = 'Fehler: ' + e.message;
    }

    console.log(`[BVH Studio] Server export done: ${totalFrames} frames, crf=${crf}, save_path=${formData.get('save_path')}`);
}

async function exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText, progressBar) {
    const totalFrames = toFrame - fromFrame;
    const stream = offCanvas.captureStream(0);  // 0 = manual frame push
    const chunks = [];

    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
    const recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 8_000_000 });
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };

    const done = new Promise(resolve => { recorder.onstop = resolve; });
    recorder.start();

    const frameInterval = 1000 / fps;
    for (let f = fromFrame; f < toFrame; f++) {
        if (exportCancelled) { recorder.stop(); statusText.textContent = 'Abgebrochen.'; return; }

        playheadFrame = f;
        applyPlayhead();
        offRenderer.render(scene, camera);

        // Push frame to stream
        const track = stream.getVideoTracks()[0];
        if (track && track.requestFrame) track.requestFrame();

        const pct = ((f - fromFrame) / totalFrames * 100).toFixed(0);
        statusText.textContent = `Aufnahme: Frame ${f - fromFrame + 1}/${totalFrames} (${pct}%)`;
        progressBar.style.width = `${pct}%`;

        await new Promise(r => setTimeout(r, frameInterval));
    }

    recorder.stop();
    await done;

    const blob = new Blob(chunks, { type: mimeType });
    statusText.textContent = 'Fertig! Speichern...';
    await saveBlobAs(blob, filename.replace('.mp4', '.webm'), mimeType);
    statusText.textContent = 'Fertig!';
    progressBar.style.width = '100%';
    console.log(`[BVH Studio] Browser export: ${totalFrames} frames`);
}

// =========================================================================
// Save / Load Project (Phase 4)
// =========================================================================
function buildProjectData() {
    return {
        name: project.name,
        fps: project.fps,
        tracks: project.tracks.map(t => {
            const td = {
                name: t.name, type: t.type, preset: t.preset, bodyType: t.bodyType,
                color: t.color, muted: t.muted, position: t.position,
            };
            if (t.type === 'camera') td.cameraActive = t.cameraActive;
            if (t.type === 'light' && t.light) {
                td.lightColor = '#' + t.light.color.getHexString();
                td.lightIntensity = t.light.intensity;
                td.lightPosition = { x: t.light.position.x, y: t.light.position.y, z: t.light.position.z };
                td.lightVisible = t.lightVisible;
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
                else if (c.type === 'audio') cd.data = { fileName: c.data.fileName, audioDuration: c.data.audioDuration, volume: c.data.volume, fadeIn: c.data.fadeIn, fadeOut: c.data.fadeOut, offset: c.data.offset };
                return cd;
            });
            return td;
        }),
    };
}

async function saveProject() {
    // Save to configured project path on server
    const dir = project.projectPath;
    if (!dir) { saveProjectAs(); return; }
    const filename = (project.name || 'project').replace(/[^a-zA-Z0-9_\-]/g, '_') + '.studio.json';
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
            project._lastSavePath = result.path;
            try { localStorage.setItem('bvhStudio_lastProject', result.path); } catch(e) {}
            console.log(`[BVH Studio] Project saved: ${result.path}`);
            document.getElementById('studio-info').textContent = `Gespeichert: ${filename}`;
        } else {
            alert('Speichern fehlgeschlagen: ' + (result.error || 'Unbekannter Fehler'));
        }
    } catch (e) {
        alert('Speichern fehlgeschlagen: ' + e.message);
    }
}

async function saveProjectAs() {
    const dir = project.projectPath || '';
    const name = prompt(`Projektname speichern unter:\n(Ordner: ${dir || 'nicht konfiguriert'})`, project.name || 'project');
    if (!name) return;
    project.name = name;
    await saveProject();
}

async function loadProject() {
    const dir = project.projectPath;
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
                    project._lastSavePath = loadResult.path;
                    try { localStorage.setItem('bvhStudio_lastProject', loadResult.path); } catch(e) {}
                    document.getElementById('studio-info').textContent = `Geladen: ${result.files[idx].name}`;
                    return;
                } else {
                    alert('Laden fehlgeschlagen: ' + (loadResult.error || ''));
                }
            } else {
                alert(`Keine Projekte in ${dir} gefunden.\nDatei manuell waehlen...`);
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

// =========================================================================
// Animation Preview Popup (A key)
// =========================================================================
let _previewModal = null;
let _previewRenderer = null;
let _previewScene = null;
let _previewCamera = null;
let _previewControls = null;
let _previewMixer = null;
let _previewAction = null;
let _previewClock = null;
let _previewAnimId = null;

function previewAnimation(category, name) {
    // Create or reuse modal
    if (!_previewModal) {
        _previewModal = document.createElement('div');
        _previewModal.id = 'preview-modal';
        _previewModal.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;';
        _previewModal.innerHTML = `
            <div style="background:var(--bg-secondary,#1a1a2e);border:1px solid var(--border,#334);border-radius:10px;width:700px;height:520px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 16px 48px rgba(0,0,0,0.5);">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border,#334);">
                    <span id="preview-title" style="font-size:0.9rem;color:#ccc;"></span>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <button id="preview-play" style="background:none;border:1px solid var(--border,#334);border-radius:4px;color:#ccc;cursor:pointer;padding:4px 10px;font-size:0.8rem;"><i class="fas fa-play" id="preview-play-icon"></i></button>
                        <span id="preview-frame" style="font-size:0.75rem;color:#888;">0 / 0</span>
                        <button id="preview-close" style="background:none;border:none;color:#888;cursor:pointer;font-size:1.2rem;">&times;</button>
                    </div>
                </div>
                <canvas id="preview-canvas" style="flex:1;width:100%;"></canvas>
            </div>`;
        document.body.appendChild(_previewModal);

        // Close handlers
        document.getElementById('preview-close').addEventListener('click', closePreview);
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
        _previewCamera = new THREE.PerspectiveCamera(50, 700/440, 0.1, 100);
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

    // Resize canvas
    const canvas = document.getElementById('preview-canvas');
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width || 700;
    canvas.height = (rect.height - 45) || 440;
    _previewRenderer.setSize(canvas.width, canvas.height, false);
    _previewCamera.aspect = canvas.width / canvas.height;
    _previewCamera.updateProjectionMatrix();

    // Clean previous
    if (_previewMixer) { _previewMixer.stopAllAction(); _previewMixer = null; }
    _previewScene.children.forEach(c => { if (c.userData._preview) _previewScene.remove(c); });
    // Remove old skeleton meshes
    const toRemove = _previewScene.children.filter(c => c.userData._preview);
    toRemove.forEach(c => { _previewScene.remove(c); if (c.geometry) c.geometry.dispose(); });

    // Load BVH via Three.js BVHLoader for quick preview (no retarget needed)
    const url = `/api/character/bvh/${encodeURIComponent(category)}/${encodeURIComponent(name)}/`;
    fetch(url).then(r => r.text()).then(bvhText => {
        const loader = new THREE.BVHLoader ? new THREE.BVHLoader() : null;
        // BVHLoader might not be imported — use the one from Three.js addons
        import('three/addons/loaders/BVHLoader.js').then(({ BVHLoader }) => {
            const bvhLoader = new BVHLoader();
            const result = bvhLoader.parse(bvhText);

            // Create skeleton helper
            const skeletonHelper = new THREE.SkeletonHelper(result.skeleton.bones[0]);
            skeletonHelper.userData._preview = true;
            _previewScene.add(skeletonHelper);
            _previewScene.add(result.skeleton.bones[0]);
            result.skeleton.bones[0].userData._preview = true;

            // Animation
            _previewMixer = new THREE.AnimationMixer(result.skeleton.bones[0]);
            _previewAction = _previewMixer.clipAction(result.clip);
            _previewAction.play();

            const totalFrames = Math.round(result.clip.duration * 30);
            document.getElementById('preview-frame').textContent = `0 / ${totalFrames}`;

            // Start render loop
            if (_previewAnimId) cancelAnimationFrame(_previewAnimId);
            _previewClock.start();

            function animatePreview() {
                _previewAnimId = requestAnimationFrame(animatePreview);
                if (!_previewModal || _previewModal.style.display === 'none') return;
                const dt = _previewClock.getDelta();
                if (_previewMixer) _previewMixer.update(dt);
                _previewControls.update();
                _previewRenderer.render(_previewScene, _previewCamera);
                // Update frame counter
                if (_previewAction) {
                    const f = Math.round(_previewAction.time * 30);
                    document.getElementById('preview-frame').textContent = `${f} / ${totalFrames}`;
                }
            }
            animatePreview();
        });
    }).catch(e => {
        console.error('[Preview] Load failed:', e);
        document.getElementById('preview-title').textContent = `Fehler: ${e.message}`;
    });
}

function closePreview() {
    if (_previewModal) _previewModal.style.display = 'none';
    if (_previewAnimId) { cancelAnimationFrame(_previewAnimId); _previewAnimId = null; }
    if (_previewMixer) { _previewMixer.stopAllAction(); }
    if (_previewAction) { _previewAction = null; }
}

function resetToDefault() {
    // Clear everything: tracks, session, undo
    _undoSuppressed = true;
    while (project.tracks.length > 0) removeTrack(0);
    _undoSuppressed = false;

    project.name = 'Untitled';
    project.duration = 0;
    selectedTrackIdx = -1;
    selectedClipIdx = -1;
    playheadFrame = 0;
    playing = false;

    undoStack.length = 0;
    redoStack.length = 0;

    sessionStorage.removeItem(SESSION_KEY);

    updateDuration();
    renderTimeline();
    updateTrackHeaders();
    updatePlaybackUI();
    updateProperties();

    document.getElementById('studio-info').textContent = 'BVH Studio v2.0';
    console.log('[BVH Studio] Reset to default');
}

async function loadLastProject() {
    let lastPath = '';
    try { lastPath = localStorage.getItem('bvhStudio_lastProject') || ''; } catch(e) {}
    if (!lastPath) { alert('Kein letztes Projekt gespeichert.'); return; }

    try {
        const resp = await fetch(`/api/studio/project-load/?path=${encodeURIComponent(lastPath)}`);
        const result = await resp.json();
        if (result.ok) {
            await restoreProjectData(result.project);
            project._lastSavePath = result.path;
            const name = lastPath.split(/[/\\]/).pop().replace('.studio.json', '');
            document.getElementById('studio-info').textContent = `Geladen: ${name}`;
            console.log(`[BVH Studio] Last project loaded: ${lastPath}`);
        } else {
            alert('Laden fehlgeschlagen: ' + (result.error || lastPath));
        }
    } catch (e) {
        alert('Laden fehlgeschlagen: ' + e.message);
    }
}

async function restoreProjectData(data) {
    console.log(`[Restore] Starting. Input tracks: ${data.tracks?.length}, clips: ${data.tracks?.map(t=>t.clips?.length)}`);
    // Suppress undo for the ENTIRE restore operation
    _undoSuppressed = true;

    // Clear existing
    while (project.tracks.length > 0) removeTrack(0);

    project.name = data.name || 'Untitled';
    project.fps = data.fps || 30;

    const loadPromises = [];

    for (const td of (data.tracks || [])) {
        const trackType = td.type || 'bvh';
        let track;
        if (trackType === 'bvh') {
            track = addTrack(td.name);
            track.preset = td.preset || 'FemaleGarment';
            track.bodyType = td.bodyType || 'Female_Caucasian';
        } else {
            track = addSpecialTrack(trackType, td.name);
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
            track.lightVisible = td.lightVisible ?? true;
            if (track.lightHelper) { track.lightHelper.position.copy(track.light.position); track.lightHelper.visible = track.lightVisible; }
        }

        for (const cd of (td.clips || [])) {
            const clip = new Clip(cd.category, cd.name, cd.totalFrames || 100, cd.fps || 30);
            clip.type = cd.type || 'bvh';
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
            if (clip.type === 'bvh') loadPromises.push(loadClipAnimation(track, clip));
        }
    }

    // Wait for ALL clip animations to load before continuing
    await Promise.all(loadPromises);

    _undoSuppressed = false;

    updateDuration();
    renderTimeline();
    updateTrackHeaders();
    console.log(`[BVH Studio] Project restored: ${project.name} (${project.tracks.length} tracks)`);
}

// =========================================================================
// Render loop
// =========================================================================
function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.1);

    if (playing) {
        playheadFrame += Math.round(dt * project.fps * playbackSpeed);
        if (playheadFrame >= project.duration * project.fps) {
            playheadFrame = 0;  // loop
        }
        applyPlayhead();
        renderTimeline();
        updatePlaybackUI();
    }

    controls.update();
    renderer.render(scene, camera);
    updateDebugPanel();
}

const _dbgV = new THREE.Vector3();
let _dbgThrottle = 0;

function updateDebugPanel() {
    // Throttle to ~10 fps
    if (++_dbgThrottle % 6 !== 0) return;

    const elDist = document.getElementById('debug-ground-dist');
    const elBone = document.getElementById('debug-lowest-bone');
    const elFootL = document.getElementById('debug-foot-l');
    const elFootR = document.getElementById('debug-foot-r');
    const elRoot = document.getElementById('debug-root-pos');
    const elFrame = document.getElementById('debug-frame');
    if (!elDist) return;

    elFrame.textContent = `Frame: ${playheadFrame}`;

    // Find active track with skeleton
    let found = false;
    for (const track of project.tracks) {
        if (track.muted || !track.skeleton) continue;
        const bones = track.skeleton.skeleton.bones;
        if (!bones || bones.length === 0) continue;

        let minY = Infinity;
        let lowestName = '';
        let minYL = Infinity, lowestL = '';
        let minYR = Infinity, lowestR = '';

        for (const b of bones) {
            b.getWorldPosition(_dbgV);
            const y = _dbgV.y;
            const n = b.name.toLowerCase();

            if (y < minY) { minY = y; lowestName = b.name; }

            // Left foot bones (foot, toe, heel)
            const isLeft = n.includes('_l') || n.includes('.l') || n.includes('left');
            const isRight = n.includes('_r') || n.includes('.r') || n.includes('right');
            const isFoot = n.includes('foot') || n.includes('toe') || n.includes('heel');

            if (isFoot && isLeft && y < minYL) { minYL = y; lowestL = b.name; }
            if (isFoot && isRight && y < minYR) { minYR = y; lowestR = b.name; }
        }

        // Root position
        const root = track.skeleton.rootBone;
        if (root) {
            root.getWorldPosition(_dbgV);
            elRoot.textContent = `Root: ${_dbgV.x.toFixed(3)}, ${_dbgV.y.toFixed(3)}, ${_dbgV.z.toFixed(3)} m`;
        }

        elDist.textContent = `Boden-Abstand: ${minY.toFixed(4)} m`;
        elBone.textContent = `Tiefster: ${lowestName}`;
        elFootL.textContent = minYL < Infinity ? `Fuss L: ${minYL.toFixed(4)} m (${lowestL})` : 'Fuss L: —';
        elFootR.textContent = minYR < Infinity ? `Fuss R: ${minYR.toFixed(4)} m (${lowestR})` : 'Fuss R: —';
        found = true;
        break;  // first active track
    }

    if (!found) {
        elDist.textContent = 'Boden-Abstand: —';
        elBone.textContent = 'Tiefster Knochen: —';
        elFootL.textContent = 'Fuss L: —';
        elFootR.textContent = 'Fuss R: —';
        elRoot.textContent = 'Root Position: —';
    }
}

// =========================================================================
// Resize
// =========================================================================
function onResize() {
    const container = document.querySelector('.studio-viewport');
    if (!container) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
}
window.addEventListener('resize', onResize);
if (typeof ResizeObserver !== 'undefined') {
    const vp = document.querySelector('.studio-viewport');
    if (vp) new ResizeObserver(onResize).observe(vp);
}

// =========================================================================
// Session state: auto-save on leave, auto-restore on return
// =========================================================================
const SESSION_KEY = 'bvhStudio_sessionState';

function saveSessionState() {
    try {
        if (project.tracks.length === 0) {
            sessionStorage.removeItem(SESSION_KEY);
            return;
        }
        const state = {
            project: buildProjectData(),
            playheadFrame,
            selectedTrackIdx,
            selectedClipIdx,
            timelineZoom,
            timelineScrollX,
        };
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(state));
    } catch (e) { /* storage full or unavailable */ }
}

async function restoreSessionState() {
    try {
        const raw = sessionStorage.getItem(SESSION_KEY);
        if (!raw) return false;
        const state = JSON.parse(raw);
        if (!state.project || !state.project.tracks || state.project.tracks.length === 0) return false;

        // Only restore BVH tracks that actually have clips
        const validTracks = state.project.tracks.filter(t => t.type !== 'bvh' || (t.clips && t.clips.length > 0));
        if (validTracks.length === 0) {
            sessionStorage.removeItem(SESSION_KEY);
            return false;
        }
        state.project.tracks = validTracks;

        await restoreProjectData(state.project);

        // Verify restore succeeded: remove tracks that ended up with no working clips
        const brokenTracks = [];
        for (let i = project.tracks.length - 1; i >= 0; i--) {
            const t = project.tracks[i];
            if (t.type === 'bvh' && t.clips.length === 0 && !t.mesh) {
                brokenTracks.push(i);
            }
        }
        if (brokenTracks.length > 0) {
            _undoSuppressed = true;
            for (const idx of brokenTracks) removeTrack(idx);
            _undoSuppressed = false;
            console.warn(`[BVH Studio] Removed ${brokenTracks.length} broken tracks from session`);
        }

        if (project.tracks.length === 0) {
            sessionStorage.removeItem(SESSION_KEY);
            return false;
        }

        playheadFrame = state.playheadFrame || 0;
        selectedTrackIdx = state.selectedTrackIdx ?? -1;
        selectedClipIdx = state.selectedClipIdx ?? -1;
        timelineZoom = state.timelineZoom || 100;
        timelineScrollX = state.timelineScrollX || 0;

        const zoomSlider = document.getElementById('tl-zoom');
        if (zoomSlider) zoomSlider.value = timelineZoom;
        const zoomLabel = document.getElementById('tl-zoom-label');
        if (zoomLabel) zoomLabel.textContent = `Zoom: ${timelineZoom}%`;

        applyPlayhead();
        renderTimeline();
        updatePlaybackUI();
        updateProperties();
        console.log(`[BVH Studio] Session restored: ${project.tracks.length} tracks`);
        return true;
    } catch (e) {
        console.warn('[BVH Studio] Session restore failed, clearing:', e);
        sessionStorage.removeItem(SESSION_KEY);
        // Clean up any half-loaded state
        _undoSuppressed = true;
        while (project.tracks.length > 0) removeTrack(0);
        _undoSuppressed = false;
        return false;
    }
}

// Auto-save on page leave
window.addEventListener('beforeunload', saveSessionState);
// Also save periodically (every 30s) in case of crash
setInterval(saveSessionState, 30000);

// =========================================================================
// Start (guard against double init)
// =========================================================================
if (!window.__bvhStudioInitialized) {
    window.__bvhStudioInitialized = true;
    init();
}
