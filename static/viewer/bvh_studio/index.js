/**
 * BVH Studio — Multi-track BVH editor with timeline, trim, blend, export.
 * Supports: BVH animation, Camera, Light, Audio tracks.
 *
 * This is the main orchestrator. It imports all modules, wires them together,
 * and contains init(), animate(), onResize().
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import {
    sharedState,
    loadRigifySkeleton, loadSkinWeights, loadSkinColors, loadHairColors,
    createSceneSetup,
} from '../character_core.js?v=1';

// Import all modules so they register their functions in the registry.
// Order matters: foundational modules first, then modules that depend on them.
import { undo, redo, undoStack } from './undo.js';
import { loadLibrary, setupLibraryManagement, setupSidebarResize } from './library.js';
import { addTrack, addSpecialTrack, selectTrack, removeTrack, addClipToTrack } from './tracks.js';
import { setupTimeline, renderTimeline, updateTrackHeaders, updateDuration } from './timeline.js';
import { setupPlayback, togglePlay, stopPlayback, applyPlayhead, updatePlaybackUI } from './playback.js';
import { updateProperties, switchPropsTab } from './properties.js';
import { setupToolbar } from './tools.js';
import { setupExportPanel, exportBVH } from './export_video.js';
import { buildProjectData, saveProject, saveProjectAs, loadProject, restoreProjectData, resetToDefault, loadLastProject, saveSessionState, restoreSessionState, previewAnimation, closePreview } from './project.js';
import { updateDebugPanel } from './debug.js';

console.log('[BVH Studio] v2.0 loaded (ES modules)');

// Server-side logging for important actions
function serverLog(action, detail, level) {
    const msg = detail ? `${action} — ${detail}` : action;
    console.log(`[BVH Studio] ${msg}`);
    fetch('/api/log/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page: 'bvh_studio', action, detail: detail || '', level: level || 'info' }),
    }).catch(() => {});  // fire-and-forget
}

// Register serverLog in registry
fn.serverLog = serverLog;

// GLOBAL keyboard shortcuts — registered immediately at module load, capture phase
// Note: Chrome on QWERTZ swallows Ctrl+Z/Y/M. Only Ctrl+Shift+U works reliably.
window.addEventListener('keydown', (e) => {
    if (!e.ctrlKey) return;
    const inInput = (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable);
    // Ctrl+Shift+U = Undo (fallback für QWERTZ/Chrome-Probleme)
    if (e.shiftKey && e.code === 'KeyU') {
        e.preventDefault();
        e.stopImmediatePropagation();
        undo();
        return;
    }
    // Ctrl+Z = Undo, Ctrl+Shift+Z oder Ctrl+Y = Redo (nicht in Input-Feldern)
    if (!inInput && e.code === 'KeyZ') {
        e.preventDefault();
        e.stopImmediatePropagation();
        if (e.shiftKey) redo();
        else undo();
        return;
    }
    if (!inInput && e.code === 'KeyY') {
        e.preventDefault();
        e.stopImmediatePropagation();
        redo();
        return;
    }
    // Ctrl+S = Save
    if (e.code === 'KeyS') {
        e.preventDefault();
        saveProject();
        return;
    }
    // Ctrl+O = Load
    if (e.code === 'KeyO') {
        e.preventDefault();
        loadProject();
        return;
    }
}, true);
console.log('[BVH Studio] Global keyboard handler registered (Ctrl+Z/Y + Ctrl+Shift+U = Undo/Redo)');

// =========================================================================
// Init
// =========================================================================
async function init() {
    // 3D Setup
    const canvas = document.getElementById('studio-canvas');
    const setup = createSceneSetup(canvas);
    state.renderer = setup.renderer;
    state.scene = setup.scene;
    state.camera = setup.camera;
    state.controls = setup.controls;

    // Load shared data + studio settings
    await Promise.all([
        loadRigifySkeleton(),
        loadSkinWeights(),
        loadSkinColors(),
        loadHairColors(),
    ]);
    // Load studio preferences
    try {
        const prefsResp = await fetch('/api/ui-prefs/');
        const prefs = await prefsResp.json();
        state.project.defaultModel = prefs.studio_default_model || 'Rig2';
        state.project.defaultBodyType = prefs.studio_body_type || 'Female_Caucasian';
        state.project.fps = parseInt(prefs.studio_fps) || 30;
        state.timelineZoom = parseInt(prefs.studio_zoom) || 100;
        state.project.videoOutputPath = prefs.studio_video_output || '';
        state.project.bvhOutputPath = prefs.studio_bvh_output || '';
        state.project.projectPath = prefs.studio_project_path || '';
    } catch (e) { /* use defaults */ }

    // Load BVH library
    await loadLibrary();
    setupLibraryManagement();
    setupSidebarResize();

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

    // Load default project from settings (if no session was restored)
    if (!restored && state.project.tracks.length === 0) {
        try {
            const prefsResp = await fetch('/api/ui-prefs/');
            const prefs = await prefsResp.json();
            const defaultProject = prefs.studio_default_project;
            const projectDir = prefs.studio_project_path || '';
            if (defaultProject) {
                const listResp = await fetch(`/api/studio/project-list/?dir=${encodeURIComponent(projectDir)}`);
                const listData = await listResp.json();
                const match = (listData.files || []).find(f => f.name.replace(/\.studio\.json$/i, '') === defaultProject);
                if (match) {
                    const loadResp = await fetch(`/api/studio/project-load/?path=${encodeURIComponent(match.path)}`);
                    const projectData = await loadResp.json();
                    if (projectData.name) {
                        await restoreProjectData(projectData);
                        console.log(`[BVH Studio] Default project loaded: ${defaultProject}`);
                    }
                }
            }
        } catch(e) { console.warn('[BVH Studio] Default project load failed:', e); }
    }

    // Start render loop
    animate();

    window.__studioProject = state.project;
    window.__studioUndo = undo;
    window.__studioRedo = redo;
    window.__undoStack = undoStack;
    window.__studioState = state;
    console.log(`[BVH Studio] Initialized${restored ? ' (session restored)' : ''}`);
}

// =========================================================================
// Render loop
// =========================================================================
function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(state.clock.getDelta(), 0.1);

    if (state.playing) {
        state.playheadFrame += Math.round(dt * state.project.fps * state.playbackSpeed);
        if (state.playheadFrame >= state.project.duration * state.project.fps) {
            state.playheadFrame = 0;  // loop
        }
        applyPlayhead();
        renderTimeline();
        updatePlaybackUI();
    }

    state.controls.update();
    state.renderer.render(state.scene, state.camera);
    updateDebugPanel();
}

// =========================================================================
// Resize
// =========================================================================
function onResize() {
    const container = document.querySelector('.studio-viewport');
    if (!container) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    state.renderer.setSize(w, h, false);
    state.camera.aspect = w / h;
    state.camera.updateProjectionMatrix();
}
window.addEventListener('resize', onResize);
if (typeof ResizeObserver !== 'undefined') {
    const vp = document.querySelector('.studio-viewport');
    if (vp) new ResizeObserver(onResize).observe(vp);
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
