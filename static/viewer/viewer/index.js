/**
 * HumanBody Character Viewer — ES module entry point.
 * Imports all modules so they register their functions, then calls init().
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { state } from './state.js';
import { fn } from './registry.js';

// Import all modules (order: foundational first, then dependent)
import './utils.js';
import './scene_settings.js';
import './mesh.js';
import './skinning.js';
import './websocket.js';
import './morphs.js';
import './wardrobe.js';
import './animation.js';
import './cloth.js';
import './hair.js';
import './garment.js';
import './vertex_editor.js';
import './pattern_editor.js';
import './interaction.js';
import './presets.js';
import './smpl.js';

import { applySceneSettings, applyExpandedPanels } from './scene_settings.js';
import { loadMesh } from './mesh.js';
import { loadSkinWeights, loadRigifySkeleton } from './skinning.js';
import { connectWebSocket } from './websocket.js';
import { loadMorphs } from './morphs.js';
import { loadWardrobe } from './wardrobe.js';
import { loadAnimations, loadBVHAnimation, stopAnimation } from './animation.js';
import { loadClothUI, removeAllCloth } from './cloth.js';
import { loadHairUI, removeHair, refitHairToBody } from './hair.js';
import { loadGarmentUI, removeAllGarments } from './garment.js';
import { initPatternEditor } from './pattern_editor.js';
import { initInteraction, updateEquippedList, _setEmissiveOnItem } from './interaction.js';
import { initLoadPreset, initSaveButtons, gatherModelState } from './presets.js';
import { loadSmplGarmentUI, initSmplBodyUI } from './smpl.js';
import { isVeActive } from './vertex_editor.js';

console.log('[Viewer] v2.0 loaded (ES modules)');

// =========================================================================
// Initialization
// =========================================================================
async function init() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    // Renderer
    state.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    state.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    state.renderer.setSize(w, h);
    state.renderer.outputColorSpace = THREE.SRGBColorSpace;
    state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    state.renderer.toneMappingExposure = 1.6;

    // Scene
    state.scene = new THREE.Scene();
    state.scene.background = new THREE.Color(0x1a1a2e);

    // Camera
    state.camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    state.camera.position.set(0, 1.0, 3.5);

    // Controls
    state.controls = new OrbitControls(state.camera, canvas);
    state.controls.target.set(0, 0.9, 0);
    state.controls.enableDamping = true;
    state.controls.dampingFactor = 0.08;
    state.controls.minDistance = 0.5;
    state.controls.maxDistance = 15;
    state.controls.update();

    // Lighting
    state.keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    state.keyLight.position.set(2, 4, -5);
    state.scene.add(state.keyLight);

    state.fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    state.fillLight.position.set(-3, 3, -4);
    state.scene.add(state.fillLight);

    state.backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    state.backLight.position.set(0, 4, 5);
    state.scene.add(state.backLight);

    state.ambient = new THREE.AmbientLight(0xffffff, 0.8);
    state.scene.add(state.ambient);

    applySceneSettings();

    // Ground grid
    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    state.scene.add(grid);

    // Resize
    window.addEventListener('resize', onResize);

    // Panel toggle
    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => {
            h3.closest('.panel-section').classList.toggle('collapsed');
        });
    });

    applyExpandedPanels();

    // Load everything
    loadMorphs();
    loadMesh().then(() => { animate(); });
    loadSkinWeights();
    loadRigifySkeleton();
    loadWardrobe();
    loadAnimations();
    loadClothUI();
    loadHairUI();
    initPatternEditor();
    loadGarmentUI();
    loadSmplGarmentUI();
    initSmplBodyUI();
    initLoadPreset();
    initSaveButtons();
    connectWebSocket();

    // Demo animation button
    const demoBtn = document.getElementById('play-demo-anim');
    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            if (!state.currentAction) {
                const animSection = document.getElementById('animation-panel')?.closest('.panel-section');
                if (animSection && animSection.classList.contains('collapsed')) animSection.classList.remove('collapsed');
                loadBVHAnimation('/api/character/bvh/Mixamo/Catwalk_Idle_02/', 'Catwalk Idle 02', 0);
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            } else if (state.playing) {
                state.currentAction.paused = true;
                state.playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i>';
                demoBtn.classList.remove('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            } else {
                if (!state.currentAction.isRunning()) state.currentAction.play();
                state.currentAction.paused = false;
                state.playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }
        });
    }

    // Rig toggle
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            state.rigVisible = !state.rigVisible;
            if (state.rigVisible) {
                if (!state.skeletonHelper && state.rigifySkeleton) {
                    state.skeletonHelper = new THREE.SkeletonHelper(state.rigifySkeleton.rootBone);
                    state.skeletonHelper.material.depthTest = false;
                    state.skeletonHelper.material.depthWrite = false;
                    state.skeletonHelper.material.color.set(0x00ffaa);
                    state.skeletonHelper.material.linewidth = 2;
                    state.skeletonHelper.renderOrder = 999;
                    state.scene.add(state.skeletonHelper);
                }
                if (state.skeletonHelper) state.skeletonHelper.visible = true;
            } else {
                if (state.skeletonHelper) state.skeletonHelper.visible = false;
            }
            rigToggle.classList.toggle('active', state.rigVisible);
        });
    }

    // Model toggle
    const modelToggle = document.getElementById('model-toggle');
    if (modelToggle) {
        modelToggle.addEventListener('click', () => {
            if (state.bodyMesh) state.bodyMesh.visible = !state.bodyMesh.visible;
            modelToggle.classList.toggle('active', state.bodyMesh && state.bodyMesh.visible);
        });
    }

    // Clothes toggle
    const clothesToggle = document.getElementById('clothes-toggle');
    if (clothesToggle) {
        let clothesVisible = true;
        clothesToggle.addEventListener('click', () => {
            clothesVisible = !clothesVisible;
            for (const m of Object.values(state.clothMeshes)) { if (m) m.visible = clothesVisible; }
            for (const m of Object.values(state.loadedAssets)) { if (m) m.visible = clothesVisible; }
            for (const m of Object.values(state.garmentMeshes)) { if (m) m.visible = clothesVisible; }
            if (state.hairMesh) state.hairMesh.visible = clothesVisible;
            clothesToggle.classList.toggle('active', clothesVisible);
        });
    }

    // Global refit
    const refitAllGlobal = document.getElementById('refit-all-btn');
    if (refitAllGlobal) {
        refitAllGlobal.addEventListener('click', async () => {
            refitAllGlobal.disabled = true;
            refitAllGlobal.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
            const gids = Object.keys(state.garmentMeshes);
            for (const gid of gids) fn._saveGarmentState(gid);
            for (const gid of gids) await fn.loadGarment(gid);
            refitHairToBody();
            refitAllGlobal.disabled = false;
            refitAllGlobal.innerHTML = '<i class="fas fa-sync"></i> Refit';
        });
    }

    // Viewer-action events
    document.addEventListener('viewer-action', (e) => {
        const action = e.detail?.action;
        switch (action) {
            case 'new':
                document.getElementById('reset-morphs')?.click();
                removeAllGarments(); removeAllCloth(); removeHair();
                const hs = document.getElementById('hair-style-select'); if (hs) hs.value = '';
                if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
                state._selectedItem = null; state._hoveredItem = null;
                const rb = document.getElementById('selection-remove-btn'); if (rb) rb.style.display = 'none';
                updateEquippedList(); state.currentPresetName = '';
                if (state.currentAction) { state.currentAction.stop(); state.currentAction = null; }
                break;
            case 'deselect':
                if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
                state._selectedItem = null; state._hoveredItem = null;
                const rb2 = document.getElementById('selection-remove-btn'); if (rb2) rb2.style.display = 'none';
                break;
            case 'delete': fn._removeSelectedItem ? fn._removeSelectedItem() : null; break;
            case 'clear-all':
                if (!confirm('Alle Kleidung, Haare und Garments entfernen?')) break;
                removeAllGarments(); removeAllCloth(); removeHair();
                const hs2 = document.getElementById('hair-style-select'); if (hs2) hs2.value = '';
                if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
                state._selectedItem = null; state._hoveredItem = null;
                const rb3 = document.getElementById('selection-remove-btn'); if (rb3) rb3.style.display = 'none';
                updateEquippedList();
                break;
            case 'export-model-json': {
                const ms = gatherModelState();
                const json = JSON.stringify(ms, null, 2);
                const blob = new Blob([json], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a'); a.href = url; a.download = (state.currentPresetName || 'model') + '.json'; a.click();
                URL.revokeObjectURL(url);
                break;
            }
            case 'reset-camera':
                state.camera.fov = 35; state.camera.updateProjectionMatrix();
                state.camera.position.set(0, 1.0, 3.5); state.controls.target.set(0, 0.9, 0); state.controls.update();
                break;
            case 'reset-lighting':
                state.keyLight.color.setHex(0xffffff); state.keyLight.intensity = 3.0; state.keyLight.position.set(2, 4, -5);
                state.fillLight.color.setHex(0xeeeeff); state.fillLight.intensity = 2.0; state.fillLight.position.set(-3, 3, -4);
                state.backLight.color.setHex(0xffeedd); state.backLight.intensity = 2.5; state.backLight.position.set(0, 4, 5);
                state.ambient.color.setHex(0xffffff); state.ambient.intensity = 0.8;
                break;
            case 'reset-scene':
                if (!confirm('Szene komplett zur\u00FCcksetzen? (Modell, Beleuchtung, Kamera)')) break;
                document.dispatchEvent(new CustomEvent('viewer-action', { detail: { action: 'new' } }));
                document.dispatchEvent(new CustomEvent('viewer-action', { detail: { action: 'reset-lighting' } }));
                document.dispatchEvent(new CustomEvent('viewer-action', { detail: { action: 'reset-camera' } }));
                break;
        }
    });

    // 3D hover + click interaction
    initInteraction();
}

function onResize() {
    const container = state.renderer.domElement.parentElement;
    const w = Math.max(container.clientWidth, 100);
    const h = container.clientHeight || window.innerHeight;
    state.renderer.setSize(w, h);
    state.camera.aspect = w / h;
    state.camera.updateProjectionMatrix();
}
fn.onResize = onResize;

function animate() {
    requestAnimationFrame(animate);
    const dt = state.clock.getDelta();
    state.controls.update();

    if (state.mixer && state.playing) {
        state.mixer.update(dt);
        if (state.currentAction && state.currentAnimDuration > 0) {
            const t = state.currentAction.time;
            const pct = Math.min(100, (t / state.currentAnimDuration) * 100);
            const tl = document.getElementById('anim-timeline');
            if (tl) tl.value = Math.round(pct);
            const curSec = Math.floor(t);
            const totSec = Math.floor(state.currentAnimDuration);
            const curFrame = Math.round((t / state.currentAnimDuration) * state.currentAnimFrames);
            const info = document.getElementById('anim-info');
            if (info) info.textContent = `${state.currentAnimName} \u2014 ${curSec}/${totSec}s  ${curFrame}/${state.currentAnimFrames}f`;
        }
    }

    state.renderer.render(state.scene, state.camera);

    state.frameCount++;
    state.fpsAccum += dt;
    if (state.fpsAccum >= 1.0) {
        const fpsEl = document.getElementById('fps-display');
        if (fpsEl) fpsEl.textContent = state.frameCount;
        state.frameCount = 0;
        state.fpsAccum = 0;
    }
}

// =========================================================================
// Debug access for Playwright tests
// =========================================================================
window.__viewer = {
    get scene() { return state.scene; },
    get bodyMesh() { return state.bodyMesh; },
    get garmentMeshes() { return state.garmentMeshes; },
    get garmentState() { return state.garmentState; },
    get selectedGarmentId() { return state.selectedGarmentId; },
    get clothMeshes() { return state.clothMeshes; },
    get smplGarmentMeshes() { return state.smplGarmentMeshes; },
    get smplBodyMesh() { return state.smplBodyMesh; },
    get camera() { return state.camera; },
    get controls() { return state.controls; },
    get rigifySkeleton() { return state.rigifySkeleton; },
    get isSkinned() { return state.isSkinned; },
    get selectedItem() { return state._selectedItem; },
    getSelectableTargets: fn.getSelectableTargets,
    updateEquippedList,
    _buildBodyQueryString: fn.buildBodyQueryString,
    peRegionGenerate: fn.peRegionGenerate,
    peGenerate3D: fn.peGenerate3D,
    get peMode() { return fn.getPeMode(); },
    set peMode(v) { fn.setPeMode(v); },
    get veActive() { return isVeActive(); },
    get veSelectedIndices() { return fn.getVeSelectedIndices(); },
    get veTargetMesh() { return fn.getVeTargetMesh(); },
    veEnterEditMode: fn.veEnterEditMode,
    veExitEditMode: fn.veExitEditMode,
};

// =========================================================================
// Boot
// =========================================================================
init();
