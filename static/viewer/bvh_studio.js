/**
 * BVH Studio — Multi-track BVH editor with timeline, trim, blend, export.
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

console.log('[BVH Studio] v1.0 loaded');

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
class Track {
    constructor(name, preset = 'FemaleGarment', bodyType = 'Female_Caucasian') {
        this.name = name;
        this.preset = preset;
        this.bodyType = bodyType;
        this.clips = [];
        this.muted = false;
        this.color = `hsl(${Math.random() * 360}, 60%, 50%)`;
        // 3D
        this.mesh = null;
        this.skeleton = null;
        this.mixer = null;
        this.group = new THREE.Group();
        this.position = [0, 0, 0];
    }
}

class Clip {
    constructor(category, name, totalFrames, fps) {
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
    }
    get duration() { return (this.totalFrames - this.trimIn - this.trimOut) / (this.fps * this.speed); }
    get endFrame() { return this.startFrame + Math.ceil(this.duration * project.fps); }
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
    } catch (e) { /* use defaults */ }

    // Load BVH library
    await loadLibrary();

    // Setup timeline canvas
    setupTimeline();

    // Setup playback controls
    setupPlayback();

    // Setup toolbar
    setupToolbar();

    // Setup export panel
    setupExportPanel();

    // Start render loop
    animate();

    window.__studioProject = project;
    console.log('[BVH Studio] Initialized');
}

// =========================================================================
// BVH Library
// =========================================================================
async function loadLibrary() {
    try {
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

            const header = document.createElement('div');
            header.className = 'lib-cat-header';
            header.innerHTML = `<span class="lib-chevron"><i class="fas fa-chevron-right"></i></span> ${cat} <span style="color:var(--text-muted);font-size:0.7rem;">(${anims.length})</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'lib-cat-body';
            for (const anim of anims) {
                const item = document.createElement('div');
                item.className = 'lib-item';
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
                item.addEventListener('dblclick', () => {
                    addClipToTrack(selectedTrackIdx >= 0 ? selectedTrackIdx : 0, cat, anim.name, anim.frames || 0);
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

function removeTrack(idx) {
    if (idx < 0 || idx >= project.tracks.length) return;
    const track = project.tracks[idx];
    scene.remove(track.group);
    if (track.mesh) { track.mesh.geometry.dispose(); }
    project.tracks.splice(idx, 1);
    if (selectedTrackIdx >= project.tracks.length) selectedTrackIdx = project.tracks.length - 1;
    updateTrackHeaders();
    renderTimeline();
}

function selectTrack(idx) {
    selectedTrackIdx = idx;
    selectedClipIdx = -1;
    updateTrackHeaders();
    updateProperties();
}

async function addClipToTrack(trackIdx, category, name, frames) {
    if (trackIdx < 0) {
        if (project.tracks.length === 0) addTrack();
        trackIdx = 0;
    }
    const track = project.tracks[trackIdx];
    if (!track) return;

    const clip = new Clip(category, name, frames || 3000, project.fps);

    // Place after last clip on this track
    const lastClip = track.clips[track.clips.length - 1];
    clip.startFrame = lastClip ? lastClip.endFrame : 0;

    track.clips.push(clip);
    updateDuration();
    renderTimeline();

    // Load retargeted animation
    await loadClipAnimation(track, clip);
    updateProperties();
}

async function loadClipAnimation(track, clip) {
    try {
        const url = `/api/retarget/?category=${encodeURIComponent(clip.category)}&name=${encodeURIComponent(clip.name)}`;
        const resp = await fetch(url);
        const data = await resp.json();

        if (!data.tracks || !data.frame_count) return;

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
                const cw = clip.duration * pps;
                const cy = y + 4;
                const ch = TRACK_HEIGHT - 8;
                if (mx >= cx && mx <= cx + cw && my >= cy && my <= cy + ch) {
                    return { trackIdx: ti, clipIdx: ci, clipX: cx, clipW: cw };
                }
            }
        }
        return null;
    }

    // --- Mouse interactions ---
    // Modes: 'none' | 'clip-drag' | 'scrub' | 'pan'
    let dragMode = 'none';
    let draggingClip = null;
    let dragStartX = 0;
    let dragOrigFrame = 0;
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
            if (hit) {
                selectedTrackIdx = hit.trackIdx;
                selectedClipIdx = hit.clipIdx;
                updateProperties();
                renderTimeline();
                dragMode = 'clip-drag';
                draggingClip = hit;
                dragStartX = mx;
                dragOrigFrame = project.tracks[hit.trackIdx].clips[hit.clipIdx].startFrame;
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
        } else if (dragMode === 'scrub') {
            if (mx > HEADER_WIDTH) setPlayheadFromMouse(mx);
        } else if (dragMode === 'pan') {
            const dx = e.clientX - dragStartX;
            timelineScrollX = Math.max(0, panStartScrollX - dx);
            renderTimeline();
        }
    });

    tlCanvas.addEventListener('mouseup', () => {
        if (dragMode === 'clip-drag') {
            draggingClip = null;
            updateProperties();
        }
        dragMode = 'none';
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
        for (let ci = 0; ci < track.clips.length; ci++) {
            const clip = track.clips[ci];
            const cx = HEADER_WIDTH + (clip.startFrame / project.fps) * pps - timelineScrollX;
            const cw = clip.duration * pps;
            const cy = y + 4;
            const ch = TRACK_HEIGHT - 8;

            // Clip body
            tlCtx.fillStyle = track.color;
            tlCtx.globalAlpha = (ti === selectedTrackIdx && ci === selectedClipIdx) ? 1.0 : 0.7;
            tlCtx.fillRect(cx, cy, cw, ch);
            tlCtx.globalAlpha = 1.0;

            // Clip border
            tlCtx.strokeStyle = '#fff';
            tlCtx.lineWidth = (ti === selectedTrackIdx && ci === selectedClipIdx) ? 2 : 0.5;
            tlCtx.strokeRect(cx, cy, cw, ch);

            // Clip label
            tlCtx.fillStyle = '#fff';
            tlCtx.font = '10px sans-serif';
            tlCtx.fillText(clip.name, cx + 4, cy + ch / 2 + 3, cw - 8);
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
        el.innerHTML = `<span style="width:8px;height:8px;border-radius:50%;background:${track.color};margin-right:6px;flex-shrink:0;"></span>${track.name}`;
        el.addEventListener('click', () => selectTrack(i));
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

    // Keyboard
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
        if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
        if (e.code === 'ArrowLeft') { e.preventDefault(); stepFrame(-1); }
        if (e.code === 'ArrowRight') { e.preventDefault(); stepFrame(1); }
        if (e.code === 'Delete' || e.code === 'Backspace') {
            e.preventDefault();
            deleteSelectedClip();
        }
        if (e.code === 'KeyS' && !e.ctrlKey) {
            e.preventDefault();
            splitClipAtPlayhead();
        }
    });
}

function togglePlay() {
    playing = !playing;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = playing ? 'fas fa-pause' : 'fas fa-play';
}

function stopPlayback() {
    playing = false;
    playheadFrame = 0;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = 'fas fa-play';
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
        if (track.muted || !track.mixer) continue;
        // Find active clip at this time
        let found = false;
        for (const clip of track.clips) {
            if (!clip.animClip) continue;
            const clipStart = clip.startFrame / project.fps;
            const clipEnd = clipStart + clip.duration;
            if (t >= clipStart && t < clipEnd) {
                const localT = (t - clipStart) * clip.speed + clip.trimIn / clip.fps;
                // Only create action once per clip, reuse it
                if (track._activeClip !== clip) {
                    track.mixer.stopAllAction();
                    // Uncache previous clip to avoid stale data
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
            // No clip at this time — reset to rest pose
            track.mixer.stopAllAction();
            track._activeClip = null;
            track._activeAction = null;
            if (track.skeleton) track.skeleton.skeleton.pose();
        }
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

    if (selectedTrackIdx >= 0 && selectedTrackIdx < project.tracks.length) {
        const track = project.tracks[selectedTrackIdx];
        content.innerHTML = `
            <div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);margin-bottom:6px;">Track: ${track.name}</h3>
                <div class="prop-row"><label>Name:</label><input type="text" value="${track.name}" id="prop-track-name"></div>
                <div class="prop-row"><label>Modell:</label><span style="font-size:0.8rem;color:var(--accent);">${track.preset}</span></div>
                <div class="prop-row"><label>Muted:</label><input type="checkbox" ${track.muted?'checked':''} id="prop-track-mute"></div>
            </div>
            <div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--text-muted);">Position</h3>
                <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${track.position[0]}" id="prop-pos-x"></div>
                <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${track.position[2]}" id="prop-pos-z"></div>
            </div>
            <div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--text-muted);">Clips (${track.clips.length})</h3>
                ${track.clips.map((c, i) => `<div class="prop-clip-item" data-clip="${i}" style="font-size:0.78rem;padding:4px 6px;margin:2px 0;border-radius:3px;cursor:pointer;background:${i===selectedClipIdx?'rgba(124,92,191,0.3)':'transparent'};color:${i===selectedClipIdx?'var(--accent)':'var(--text)'};">${c.name} (${c.totalFrames}f, ${c.duration.toFixed(1)}s)</div>`).join('')}
            </div>
            ${selectedClipIdx >= 0 && track.clips[selectedClipIdx] ? (() => {
                const c = track.clips[selectedClipIdx];
                return `<div class="prop-group">
                    <h3 style="font-size:0.85rem;color:var(--accent);">Clip: ${c.name}</h3>
                    <div class="prop-row"><label>Start:</label><input type="number" value="${c.startFrame}" id="prop-clip-start" min="0"> <span style="font-size:0.7rem;color:var(--text-muted);">frames</span></div>
                    <div class="prop-row"><label>Trim In:</label><input type="number" value="${c.trimIn}" id="prop-clip-trim-in" min="0"></div>
                    <div class="prop-row"><label>Trim Out:</label><input type="number" value="${c.trimOut}" id="prop-clip-trim-out" min="0"></div>
                    <div class="prop-row"><label>Speed:</label><input type="number" value="${c.speed}" id="prop-clip-speed" min="0.1" max="4" step="0.1"></div>
                    <div class="prop-row"><label>Smooth:</label><input type="number" value="${c.smoothSigma}" id="prop-clip-smooth" min="0" max="10" step="0.5"></div>
                    <div class="prop-row"><label>Boden:</label><input type="checkbox" ${c.groundFix?'checked':''} id="prop-clip-ground"></div>
                    <div class="prop-row"><label>Blend In:</label><input type="number" value="${c.blendIn}" id="prop-clip-blend-in" min="0"> <span style="font-size:0.7rem;">f</span></div>
                    <div class="prop-row"><label>Blend Out:</label><input type="number" value="${c.blendOut}" id="prop-clip-blend-out" min="0"> <span style="font-size:0.7rem;">f</span></div>
                </div>`;
            })() : ''}
        `;
        document.getElementById('prop-track-name')?.addEventListener('change', (e) => {
            track.name = e.target.value;
            updateTrackHeaders();
        });
        document.getElementById('prop-track-mute')?.addEventListener('change', (e) => {
            track.muted = e.target.checked;
        });
        document.getElementById('prop-pos-x')?.addEventListener('change', (e) => {
            track.position[0] = parseFloat(e.target.value) || 0;
            track.group.position.x = track.position[0];
        });
        document.getElementById('prop-pos-z')?.addEventListener('change', (e) => {
            track.position[2] = parseFloat(e.target.value) || 0;
            track.group.position.z = track.position[2];
        });
        // Clip selection
        document.querySelectorAll('.prop-clip-item').forEach(el => {
            el.addEventListener('click', () => {
                selectedClipIdx = parseInt(el.dataset.clip);
                updateProperties();
                renderTimeline();
            });
        });
        // Clip property editors
        const clip = selectedClipIdx >= 0 ? track.clips[selectedClipIdx] : null;
        if (clip) {
            document.getElementById('prop-clip-start')?.addEventListener('change', (e) => {
                clip.startFrame = parseInt(e.target.value) || 0;
                updateDuration(); renderTimeline();
            });
            document.getElementById('prop-clip-trim-in')?.addEventListener('change', (e) => {
                clip.trimIn = Math.max(0, Math.min(clip.totalFrames - 1, parseInt(e.target.value) || 0));
                updateDuration(); renderTimeline();
            });
            document.getElementById('prop-clip-trim-out')?.addEventListener('change', (e) => {
                clip.trimOut = Math.max(0, parseInt(e.target.value) || 0);
                updateDuration(); renderTimeline();
            });
            document.getElementById('prop-clip-speed')?.addEventListener('change', (e) => {
                clip.speed = Math.max(0.1, parseFloat(e.target.value) || 1);
                updateDuration(); renderTimeline();
            });
            document.getElementById('prop-clip-smooth')?.addEventListener('change', (e) => {
                clip.smoothSigma = Math.max(0, parseFloat(e.target.value) || 0);
            });
            document.getElementById('prop-clip-ground')?.addEventListener('change', (e) => {
                clip.groundFix = e.target.checked;
            });
            document.getElementById('prop-clip-blend-in')?.addEventListener('change', (e) => {
                clip.blendIn = Math.max(0, parseInt(e.target.value) || 0);
            });
            document.getElementById('prop-clip-blend-out')?.addEventListener('change', (e) => {
                clip.blendOut = Math.max(0, parseInt(e.target.value) || 0);
            });
        }
    } else {
        content.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;">Track oder Clip auswaehlen</div>';
    }
}

// =========================================================================
// Toolbar
// =========================================================================
function setupToolbar() {
    document.getElementById('btn-add-track')?.addEventListener('click', () => addTrack());
    document.getElementById('btn-delete-track')?.addEventListener('click', () => removeTrack(selectedTrackIdx));
    document.getElementById('btn-delete-clip')?.addEventListener('click', () => {
        if (selectedTrackIdx >= 0 && selectedClipIdx >= 0) {
            project.tracks[selectedTrackIdx].clips.splice(selectedClipIdx, 1);
            selectedClipIdx = -1;
            updateDuration();
            renderTimeline();
        }
    });
    document.getElementById('btn-split')?.addEventListener('click', splitClipAtPlayhead);
    document.getElementById('btn-export-bvh')?.addEventListener('click', exportBVH);
    document.getElementById('btn-export-video')?.addEventListener('click', () => {
        // Switch to Export tab and update range
        switchPropsTab('export');
        const toEl = document.getElementById('export-to');
        if (toEl && (toEl.value === '0' || !toEl.value)) toEl.value = Math.round(project.duration * project.fps);
    });
    document.getElementById('btn-save')?.addEventListener('click', saveProject);
    document.getElementById('btn-load')?.addEventListener('click', loadProject);

    // Tools dropdown
    const toolsDD = document.getElementById('tools-dropdown');
    const toolsBtn = document.getElementById('btn-tools');
    toolsBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        toolsDD.classList.toggle('open');
    });
    document.addEventListener('click', () => toolsDD?.classList.remove('open'));
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
}

function switchPropsTab(tabName) {
    document.querySelectorAll('.props-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    document.querySelectorAll('.props-tab-content').forEach(c => c.classList.toggle('active', c.id === `props-tab-${tabName}`));
}

function duplicateSelectedClip() {
    if (selectedTrackIdx < 0 || selectedClipIdx < 0) return;
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

    // Reset skeleton to rest pose
    if (track.skeleton) track.skeleton.skeleton.pose();

    console.log('[BVH Studio] Clip deleted');
}

function splitClipAtPlayhead() {
    if (selectedTrackIdx < 0) return;
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
function saveProject() {
    const data = {
        name: project.name,
        fps: project.fps,
        tracks: project.tracks.map(t => ({
            name: t.name,
            preset: t.preset,
            bodyType: t.bodyType,
            color: t.color,
            muted: t.muted,
            position: t.position,
            clips: t.clips.map(c => ({
                category: c.category,
                name: c.name,
                totalFrames: c.totalFrames,
                fps: c.fps,
                startFrame: c.startFrame,
                trimIn: c.trimIn,
                trimOut: c.trimOut,
                speed: c.speed,
                smoothSigma: c.smoothSigma,
                groundFix: c.groundFix,
                blendIn: c.blendIn,
                blendOut: c.blendOut,
            })),
        })),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url;
    a.download = `${project.name || 'project'}.studio.json`;
    a.click(); URL.revokeObjectURL(url);
    console.log('[BVH Studio] Project saved');
}

function loadProject() {
    const input = document.createElement('input');
    input.type = 'file'; input.accept = '.json,.studio.json';
    input.addEventListener('change', async () => {
        const file = input.files[0];
        if (!file) return;
        try {
            const text = await file.text();
            const data = JSON.parse(text);

            // Clear existing
            while (project.tracks.length > 0) removeTrack(0);

            project.name = data.name || 'Untitled';
            project.fps = data.fps || 30;

            for (const td of (data.tracks || [])) {
                const track = addTrack(td.name);
                track.preset = td.preset || 'FemaleGarment';
                track.bodyType = td.bodyType || 'Female_Caucasian';
                track.color = td.color || track.color;
                track.muted = td.muted || false;
                track.position = td.position || [0, 0, 0];
                track.group.position.set(track.position[0], 0, track.position[2]);

                for (const cd of (td.clips || [])) {
                    const clip = new Clip(cd.category, cd.name, cd.totalFrames || 100, cd.fps || 30);
                    clip.startFrame = cd.startFrame || 0;
                    clip.trimIn = cd.trimIn || 0;
                    clip.trimOut = cd.trimOut || 0;
                    clip.speed = cd.speed || 1;
                    clip.smoothSigma = cd.smoothSigma || 0;
                    clip.groundFix = cd.groundFix || false;
                    clip.blendIn = cd.blendIn || 0;
                    clip.blendOut = cd.blendOut || 0;
                    track.clips.push(clip);
                    loadClipAnimation(track, clip);
                }
            }
            updateDuration();
            renderTimeline();
            updateTrackHeaders();
            console.log(`[BVH Studio] Project loaded: ${project.name}`);
        } catch (e) {
            alert('Projekt laden fehlgeschlagen: ' + e.message);
        }
    });
    input.click();
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
// Start
// =========================================================================
init();
