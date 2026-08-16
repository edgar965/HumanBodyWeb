/**
 * BVH Studio — Multi-track BVH editor with timeline, trim, blend, export.
 * Supports: BVH animation, Camera, Light, Audio tracks.
 *
 * This is the main orchestrator. It imports all modules, wires them together,
 * and contains init(), animate(), onResize().
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import {
    sharedState,
    loadRigifySkeleton, loadSkinWeights, loadSkinColors, loadHairColors,
    createSceneSetup,
} from '../character_core.js?v=1';

// Import all modules so they register their functions in the registry.
// Order matters: foundational modules first, then modules that depend on them.
import { undo, redo, undoStack } from './undo.js';
import { loadLibrary, setupLibraryManagement, setupSidebarResize } from './library.js';
import './tracks.js';
import { createSceneLightTracks } from './spur_lichter.js';
import { setupTimeline } from './timeline.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { setupPlayback, applyPlayhead, updatePlaybackUI, syncLightVisibility } from './playback.js';
import './properties.js';   // meldet updateProperties/switchPropsTab in der Registry an
import { setupToolbar } from './tools.js';
import { setupExportPanel } from './export_video.js';
import { bindClothExportButtons } from './export1.js';
import { Projektdatei } from './project.js';
import { Projektwiederherstellung } from './projekt_wiederherstellung.js';
import { Sitzung } from './sitzung.js';
import './vorschau.js';       // meldet previewAnimation/getPreviewInfo in der Registry an
import { updateDebugPanel } from './debug.js';
import { createFloorTrack } from './spur_boden.js';
import { setupTheatreMenu } from './theatre_lichter.js';
import { setupSceneObjectImport } from './objektimport.js';
import { Anfasser } from './anfasser.js';
import { setupViewportContextMenu } from './szenenmenue.js';

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
        Projektdatei.speichern();
        return;
    }
    // Ctrl+O = Load
    if (e.code === 'KeyO') {
        e.preventDefault();
        Projektdatei.laden();
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
    Anfasser.aufbauen();

    // Restore session state (if returning from another page)
    const restored = await Sitzung.wiederherstellen();

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
                        await Projektwiederherstellung.uebernehmen(projectData);
                        console.log(`[BVH Studio] Default project loaded: ${defaultProject}`);
                        // UI-State (Playhead/Zoom/Selection) aus verworfener Session übernehmen
                        try {
                            const uiStateRaw = sessionStorage.getItem('bvhStudio_sessionState__ui');
                            if (uiStateRaw) {
                                const ui = JSON.parse(uiStateRaw);
                                state.playheadFrame = ui.playheadFrame ?? 0;
                                state.timelineZoom = ui.timelineZoom ?? 100;
                                state.timelineScrollX = ui.timelineScrollX ?? 0;
                                state.selectedTrackIdx = ui.selectedTrackIdx ?? -1;
                                state.selectedClipIdx = ui.selectedClipIdx ?? -1;
                                sessionStorage.removeItem('bvhStudio_sessionState__ui');
                                const zoomSlider = document.getElementById('tl-zoom');
                                if (zoomSlider) zoomSlider.value = state.timelineZoom;
                                fn.applyPlayhead?.();
                            }
                        } catch (e) { /* ignore */ }
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
window.addEventListener('beforeunload', Sitzung.sichern);
// Also save periodically (every 30s) in case of crash
setInterval(Sitzung.sichern, 30000);

// =========================================================================
// Start (guard against double init)
// =========================================================================
if (!window.__bvhStudioInitialized) {
    window.__bvhStudioInitialized = true;
    init();
}
