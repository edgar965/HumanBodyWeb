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
import { addTrack, addSpecialTrack, selectTrack, removeTrack, addClipToTrack, createSceneLightTracks } from './tracks.js';
import { setupTimeline, renderTimeline, updateTrackHeaders, updateDuration } from './timeline.js';
import { setupPlayback, togglePlay, stopPlayback, applyPlayhead, updatePlaybackUI, syncLightVisibility } from './playback.js';
import { updateProperties, switchPropsTab } from './properties.js';
import { setupToolbar } from './tools.js';
import { setupExportPanel, exportBVH } from './export_video.js';
import { bindClothExportButtons } from './export1.js';
import { buildProjectData, saveProject, saveProjectAs, loadProject, restoreProjectData, resetToDefault, loadLastProject, saveSessionState, restoreSessionState, previewAnimation, closePreview } from './project.js';
import { updateDebugPanel } from './debug.js';
import {
    createFloorTrack, setupTheatreMenu, setupSceneObjectImport, setupTransformControls,
    attachTransformControls, detachTransformControls,
} from './scene_extras.js';

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
// Viewport context menu — right-click in 3D scene to set light position
// =========================================================================
function setupViewportContextMenu() {
    const menu = document.getElementById('viewport-context-menu');
    if (menu) menu.style.display = 'none';

    const canvas = state.renderer?.domElement || document.getElementById('studio-canvas');
    if (!canvas) return;

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    // Alt+Click in 3D-Szene: Licht oder Scene-Object an Klick-Position setzen
    canvas.addEventListener('click', (e) => {
        if (!e.altKey || e.button !== 0) return;
        const track = state.project.tracks[state.selectedTrackIdx];
        if (!track) return;
        const isLight = track.type === 'light' && track.light && !track.light.isAmbientLight;
        const isSceneObj = track.type === 'scene_object' && track.subtype === 'custom' && track.mesh;
        if (!isLight && !isSceneObj) return;

        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, state.camera);
        // Gegen Mesh-Szene raycasten (ohne Lichter/Helper/Grid/selbst)
        const selfMesh = isSceneObj ? track.mesh : null;
        const intersects = raycaster.intersectObjects(state.scene.children, true).filter(h => {
            const o = h.object;
            if (!o.visible || o.isLight) return false;
            if (o.type?.includes('Helper')) return false;
            if (o.type === 'GridHelper') return false;
            // Bei Scene-Object: eigenes Mesh ignorieren (würde sich selbst treffen)
            if (selfMesh && (o === selfMesh || selfMesh.getObjectById?.(o.id))) return false;
            return true;
        });
        let hitPoint = null;
        if (intersects.length > 0) hitPoint = intersects[0].point.clone();
        else {
            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
            const hit = new THREE.Vector3();
            if (raycaster.ray.intersectPlane(plane, hit)) hitPoint = hit;
        }
        if (!hitPoint) return;

        if (isLight) {
            track.light.position.copy(hitPoint);
            if (hitPoint.y < 0.5) track.light.position.y = Math.max(hitPoint.y + 2, 2);
            track.light.target?.updateMatrixWorld();
            track.lightHelper?.update?.();
            fn.serverLog?.('light_moved', `track=${track.name}`);
        } else if (isSceneObj) {
            track.mesh.position.copy(hitPoint);
            fn.serverLog?.('object_moved', `track=${track.name}`);
        }
        fn.updateProperties();
    });

    // Links-Klick: Licht-Helper oder Scene-Object auswählen. Wir sammeln ALLE Kandidaten
    // und wählen den NÄCHSTEN Treffer — sonst "gewinnt" ein Licht-Cone weit hinten gegen
    // den Boden direkt vor der Kamera.
    canvas.addEventListener('mousedown', (e) => {
        if (e.button !== 0 || e.altKey || e.shiftKey || e.ctrlKey) return;
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, state.camera);

        // Filtert Raycast-Hits: Objekt und alle Vorfahren müssen visible sein.
        // Three.js raycast matcht auch visible=false Objekte (by design).
        const isVisibleInTree = (obj) => {
            for (let o = obj; o; o = o.parent) if (o.visible === false) return false;
            return true;
        };
        let best = null;  // { dist, trackIdx }
        for (let i = 0; i < state.project.tracks.length; i++) {
            const t = state.project.tracks[i];
            let hits = null;
            // Licht-Helper nur wenn User die Helfer-Linien eingeschaltet hat (track.lightVisible).
            // Für den Kegel (indicator) reicht ein Hit — er ist immer da wenn coneVisible.
            if (t.type === 'light' && t.lightHelper) {
                const targets = [];
                if (t.lightVisible && t.lightHelper.spotHelper) targets.push(t.lightHelper.spotHelper);
                if (t.coneVisible !== false && t.lightHelper.originCone) targets.push(t.lightHelper.originCone);
                for (const tgt of targets) {
                    const h = raycaster.intersectObject(tgt, true).filter(x => isVisibleInTree(x.object) && x.distance > 0.01);
                    if (h.length > 0 && (!hits || h[0].distance < hits[0].distance)) hits = h;
                }
            } else if (t.type === 'scene_object' && t.mesh) {
                hits = raycaster.intersectObject(t.mesh, true).filter(x => isVisibleInTree(x.object) && x.distance > 0.01);
            }
            if (!hits || hits.length === 0) continue;
            const d = hits[0].distance;
            if (best === null || d < best.dist) best = { dist: d, trackIdx: i };
        }
        if (best) fn.selectTrack?.(best.trackIdx);
    });
}

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
    // BVH Studio: keine automatischen Licht-TRACKS. Die 3 Directional-Lichter werden
    // entfernt (User soll per Theatre-Preset / Menü "Hinzufügen > Licht" eigenes Setup
    // anlegen). Ambient-Licht bleibt ALS SZENEN-ELEMENT (nicht als Track) erhalten, damit
    // importierte 3D-Objekte und Modelle nicht komplett schwarz erscheinen.
    for (const l of [setup.keyLight, setup.fillLight, setup.backLight]) {
        if (l) { setup.scene.remove(l); l.dispose?.(); }
    }
    state.sceneKeyLight = null;
    state.sceneFillLight = null;
    state.sceneBackLight = null;
    state.sceneAmbient = null;  // kein Track, auch wenn setup.ambient in der Szene bleibt

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
        state.project.preloadSeconds = parseFloat(prefs.studio_preload_seconds ?? '3');
    } catch (e) { /* use defaults */ }

    // BVH-Library-Setup. Management + Resize sofort, eigentliches Scannen der 7000+
    // Dateien im Hintergrund (lazy), damit Init nicht blockiert wird. Platzhalter "wird
    // geladen" bleibt bis loadLibrary() fertig ist.
    setupLibraryManagement();
    setupSidebarResize();
    const tree = document.getElementById('lib-tree');
    if (tree) {
        tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.78rem;"><i class="fas fa-spinner fa-spin" style="margin-right:6px;"></i>BVH-Library wird geladen...</div>';
    }
    // Fire-and-forget: blockiert Init nicht
    loadLibrary().catch(e => {
        console.warn('[BVH Studio] Library load failed:', e);
        if (tree) tree.innerHTML = '<div style="padding:12px;color:var(--danger);font-size:0.78rem;">Library-Load fehlgeschlagen. <a href="#" id="lib-retry" style="color:var(--accent);">Erneut versuchen</a></div>';
        document.getElementById('lib-retry')?.addEventListener('click', (ev) => { ev.preventDefault(); loadLibrary(); });
    });

    // Setup timeline canvas
    setupTimeline();

    // Setup playback controls
    setupPlayback();

    // Setup toolbar
    setupToolbar();

    // Setup export panel
    setupExportPanel();
    bindClothExportButtons();

    // Viewport right-click → Licht-Position setzen (nur wenn Licht-Track ausgewählt)
    setupViewportContextMenu();

    // Theatre-Presets Menü, 3D-Objekt-Import, TransformControls
    setupTheatreMenu();
    setupSceneObjectImport();
    setupTransformControls();

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
                    const payload = await loadResp.json();
                    // API liefert { ok, project, path } — Projekt ist verschachtelt
                    const projectData = payload.project || payload;
                    if (projectData?.name) {
                        await restoreProjectData(projectData);
                        console.log(`[BVH Studio] Default project loaded: ${defaultProject}`);
                    } else {
                        console.warn('[BVH Studio] project-load returned no project:', payload);
                    }
                }
            }
        } catch(e) { console.warn('[BVH Studio] Default project load failed:', e); }
    }

    // Szenen-Elemente als Tracks registrieren (Boden, Licht) — NACH
    // restore, damit user-track-Indizes stabil bleiben (_linkedAnimIdx bricht sonst).
    createFloorTrack();
    createSceneLightTracks();
    // Pending overrides sind jetzt konsumiert
    delete state.project._pendingSceneOverrides;
    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
    fn.updateProperties?.();

    // Start render loop
    animate();

    window.__studioProject = state.project;
    window.__studioUndo = undo;
    window.__studioRedo = redo;
    window.__undoStack = undoStack;
    window.__studioState = state;
    window.__studioFn = fn;
    fn.updateStudioInfo?.();
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
    } else {
        // Auch ohne Play: An/Aus-Status der Lichter live synchronisieren
        syncLightVisibility();
    }

    // When a Kamera-Track drives the camera, OrbitControls would overwrite
    // the interpolated pose on update(). Skip controls while playing + an
    // active camera track exists.
    const cameraTrackActive = state.playing && state.project.tracks.some(
        t => t.type === 'camera' && t.cameraActive && (t.clips?.length || 0) > 0
    );
    if (!cameraTrackActive) state.controls.update();
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
