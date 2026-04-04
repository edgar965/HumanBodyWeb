/**
 * Result Character — Main orchestrator (ES module entry point).
 *
 * Result-page 3D Character viewer -- syncs to video.currentTime.
 * Full controls: model preset, morphs (via WebSocket), cloth template/builder/primitive,
 * model/rig/clothes toggles, face bones checkbox.
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
import { applySceneSettings, applySceneSkinSettings } from './scene_setup.js';
import { connectWebSocket, wsSend, sendMorphThrottled } from './websocket.js';
import { loadMesh, convertToRigifySkinnedMesh, applySkinColor, reloadBodyMesh } from './mesh_loading.js';
import { loadCloth, removeClothRegion, removeAllCloth, loadGarment, removeGarment, removeAllGarments } from './cloth_garments.js';
import { loadHair, removeHair } from './hair.js';
import { loadBVH, positionCameraAfterRetarget } from './bvh_animation.js';
import { loadPresetClothAndHair, reloadForPreset } from './presets.js';
import { buildControlPanel } from './ui_panel.js';

const ss = sharedState;

/**
 * @param {Object} opts
 * @param {string} opts.canvasId  - id of the <canvas> element
 * @param {string} opts.videoId   - id of the <video> element (master clock)
 * @param {string} opts.bvhUrl    - URL to the job-specific BVH file
 * @param {string} opts.panelId   - id of the side panel container
 * @param {string} opts.modelSelectId - id of the header model preset <select>
 */
export async function initResultCharacter({ canvasId, videoId, bvhUrl, bvhFaceUrl, jobId, panelId, modelSelectId }) {
    const canvas = document.getElementById(canvasId);
    const video  = document.getElementById(videoId);
    const loadingEl = document.getElementById('characterLoading');
    const panel = panelId ? document.getElementById(panelId) : null;
    if (!canvas || !video) {
        console.error('[result_character] Missing elements:', { canvas: !!canvas, video: !!video });
        return;
    }

    // Populate state with init params
    state.canvas = canvas;
    state.video = video;
    state.loadingEl = loadingEl;
    state.panel = panel;
    state.modelSelectId = modelSelectId;
    state.jobId = jobId;
    state.bvhUrl = bvhUrl;
    state.bvhFaceUrl = bvhFaceUrl;

    // Viewport wrapper has fixed CSS height (500px) -- use it for sizing
    const viewport = canvas.parentElement;

    // --- Scene setup (shared with scene_config.js) ---
    const { renderer, scene, camera, controls, keyLight, fillLight, backLight, ambient, grid }
        = createSceneSetup(canvas);
    state.renderer = renderer;
    state.scene = scene;
    state.camera = camera;
    state.controls = controls;
    window._debugScene = scene;

    applySceneSettings(renderer, scene, camera, keyLight, fillLight, backLight, ambient);

    // --- Resize ---
    function onResize() {
        const cw = viewport.clientWidth;
        const ch = viewport.clientHeight || 500;
        renderer.setSize(cw, ch, false);
        camera.aspect = cw / ch;
        camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', onResize);
    if (typeof ResizeObserver !== 'undefined') {
        new ResizeObserver(onResize).observe(viewport);
    }

    // --- Render loop ---
    function _videoOK() {
        return video.duration > 0 && isFinite(video.duration) && !isNaN(video.duration);
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();

        if (state.mixer && state.bvhClipDuration > 0) {
            let progress;
            if (_videoOK()) {
                progress = video.currentTime / video.duration;
            } else if (typeof window.bvhPlayerProgress === 'number') {
                progress = window.bvhPlayerProgress;
            } else {
                progress = 0;
            }

            if (state.currentAction && state.currentAction.paused) {
                state.currentAction.reset();
                state.currentAction.play();
            }
            state.mixer.setTime(progress * state.bvhClipDuration);
        }

        renderer.render(scene, camera);
    }
    animate();

    // --- Fetch default preset name from settings ---
    try {
        const settingsResp = await fetch('/api/settings/humanbody/');
        const settingsData = await settingsResp.json();
        if (settingsData.result) state.defaultPresetName = settingsData.result;
    } catch (e) {
        console.warn('[result_character] Failed to fetch settings, using default preset');
    }

    // --- Fetch preset data ---
    try {
        const presetResp = await fetch(`/api/character/model/${encodeURIComponent(state.defaultPresetName)}/`);
        if (presetResp.ok) {
            state.presetData = await presetResp.json();
            if (state.presetData.body_type) state.currentBodyType = state.presetData.body_type;
            state.currentPresetName = state.defaultPresetName;
            state.currentMorphs = state.presetData.morphs || {};
            state.currentMeta = state.presetData.meta || {};
        }
    } catch (e) {
        console.warn('[result_character] Failed to fetch preset:', state.defaultPresetName);
    }

    // --- Load all data ---
    try {
        const [, , , morphResp, hairResp] = await Promise.all([
            loadMesh(state.currentBodyType),
            loadRigifySkeleton(),
            loadSkinWeights(state.currentBodyType),
            fetch('/api/character/morphs/').then(r => r.json()),
            fetch('/api/character/hairstyles/').then(r => r.json()).catch(() => null),
        ]);
        state.morphData = morphResp;
        state.hairData = hairResp;
        if (state.morphData.skin_colors) ss.skinColors = state.morphData.skin_colors;
        if (state.hairData && state.hairData.colors) ss.hairColorData = state.hairData.colors;
    } catch (e) {
        console.error('[result_character] Data load failed:', e);
        if (loadingEl) loadingEl.textContent = 'Fehler beim Laden';
        return;
    }

    // Convert to skinned mesh
    if (state.bodyMesh && ss.rigifySkeletonData && ss.skinWeightData) {
        convertToRigifySkinnedMesh();
    }

    applySkinColor(state.currentBodyType);

    if (state.isSkinned) {
        loadBVH();
    }

    connectWebSocket();

    if (loadingEl) loadingEl.style.display = 'none';

    // --- Populate model preset dropdown (header) ---
    if (modelSelectId) {
        const extSelect = document.getElementById(modelSelectId);
        if (extSelect) {
            try {
                const modelsResp = await fetch('/api/character/models/');
                const modelsData = await modelsResp.json();
                extSelect.innerHTML = '';
                (modelsData.presets || []).forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.name;
                    opt.textContent = p.label || p.name;
                    if (p.name === state.currentPresetName) opt.selected = true;
                    extSelect.appendChild(opt);
                });
                extSelect.addEventListener('change', () => reloadForPreset(extSelect.value));
            } catch (e) {
                console.warn('[result_character] Failed to load model presets list');
            }
        }
    }

    // --- Foot correction checkbox ---
    const footChk = document.getElementById('footCorrection');
    if (footChk) {
        footChk.addEventListener('change', () => {
            state.enableFootCorrection = footChk.checked;
            if (state.isSkinned) loadBVH();
        });
    }

    // --- Delta normalization select ---
    const deltaNormSel = document.getElementById('deltaNormSelect');
    if (deltaNormSel) {
        deltaNormSel.addEventListener('change', () => {
            const v = deltaNormSel.value;
            state.deltaNormMode = v === 'auto' ? undefined : v === '1';
            if (state.isSkinned) loadBVH();
        });
    }

    // --- Hair toggle button (header) ---
    const btnHair = document.getElementById('btnToggleHair');
    if (btnHair) {
        btnHair.addEventListener('click', () => {
            if (state.hairMesh) {
                state.hairMesh.visible = !state.hairMesh.visible;
                btnHair.classList.toggle('active', state.hairMesh.visible);
            }
        });
    }

    // --- Build UI panel ---
    if (panel && state.morphData) {
        buildControlPanel(panel, state.morphData);
    }

    // Load preset's clothes + hair + garments after skinning
    if (state.isSkinned && state.presetData) {
        loadPresetClothAndHair(state.presetData);
    } else if (state.isSkinned) {
        loadCloth('tpl_TPL_TSHIRT', {
            method: 'template', template: 'TPL_TSHIRT',
            segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
        });
        loadCloth('tpl_TPL_PANTS', {
            method: 'template', template: 'TPL_PANTS',
            segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
        });
        if (state.hairData && state.hairData.hairstyles) {
            const defaultHair = state.hairData.hairstyles.find(h => h.name === 'ballerina')
                             || state.hairData.hairstyles[0];
            if (defaultHair) loadHair(defaultHair.url);
        }
    }
}
