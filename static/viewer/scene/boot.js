/**
 * Scene Editor -- init(), animate(), onResize().
 * Entry point that imports and wires everything together.
 */
import { THREE, OrbitControls, TransformControls, SESSION_KEY, buildRigifySkeleton } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';

// Import all modules so they register their functions in the registry.
import './undo.js';
import './session.js';
import './utils.js';
import './skeleton.js';
import './character.js';
import './interaction.js';
import './lighting.js';
import './menubar.js';
import './save_load.js';
import './properties.js';
import './garments.js';
import './prop_garments.js';
import './pose_apply.js';
import './hair.js';
import './cloth.js';
import './animation.js';
import './kleider.js';
import './mh_proxy.js';
import './model_generator.js';
import './rigging.js';
import './charmorph.js';
import { loadCharmorphHairUI } from './charmorph_hair.js';
import { initFinalizeTab } from './finalize.js';

// Also register buildRigifySkeleton for menubar toggle-rig
fn.buildRigifySkeleton = buildRigifySkeleton;

console.log('[Scene Editor] v2.0 loaded (ES modules)');

// GLOBAL Undo handler
window.addEventListener('keydown', (e) => {
    if (!e.ctrlKey || !e.shiftKey) return;
    if (e.code === 'KeyU') { e.preventDefault(); e.stopImmediatePropagation(); if (fn.sceneUndo) fn.sceneUndo(); }
}, true);

// Init dialog close handlers at module load
fn.initDialogCloseHandlers();

// =========================================================================
// Skin colors + hair colors (legacy)
// =========================================================================
async function loadSkinColors() {
    try { const data = await fn.fetchMorphDefs(); state.skinColors = data.skin_colors || {}; } catch (e) { /* optional */ }
}
async function loadHairColors() {
    try { const resp = await fetch('/api/character/hairstyles/'); const data = await resp.json(); state.hairColorData = data.colors || {}; } catch (e) { /* optional */ }
}

// =========================================================================
// init
// =========================================================================
export async function init() {
    state.canvas = document.getElementById('viewer-canvas');
    const container = state.canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    state.renderer = new THREE.WebGLRenderer({ canvas: state.canvas, antialias: true });
    state.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    state.renderer.setSize(w, h);
    state.renderer.outputColorSpace = THREE.SRGBColorSpace;
    state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    state.renderer.toneMappingExposure = 1.6;

    state.scene = new THREE.Scene();
    state.scene.background = new THREE.Color(0x1a1a2e);

    state.camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    state.camera.position.set(0, 1.0, 3.5);

    state.controls = new OrbitControls(state.camera, state.canvas);
    state.controls.target.set(0, 0.9, 0);
    state.controls.enableDamping = true;
    state.controls.dampingFactor = 0.08;
    state.controls.minDistance = 0.5;
    state.controls.maxDistance = 15;
    state.controls.update();

    state.keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    state.keyLight.position.set(2, 4, -5); state.scene.add(state.keyLight);
    state.fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    state.fillLight.position.set(-3, 3, -4); state.scene.add(state.fillLight);
    state.backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    state.backLight.position.set(0, 4, 5); state.scene.add(state.backLight);
    state.ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    state.scene.add(state.ambientLight);

    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    state.scene.add(grid);

    state.transformControls = new TransformControls(state.camera, state.canvas);
    state.transformControls.setMode('translate');
    state.transformControls.setSpace('world');
    state.transformControls.enabled = false;
    state.transformHelper = state.transformControls.getHelper();
    state.transformHelper.visible = false;
    state.scene.add(state.transformHelper);

    state.transformControls.addEventListener('dragging-changed', (e) => {
        state.controls.enabled = !e.value;
        state.transformDragging = e.value;
    });
    state.transformControls.addEventListener('objectChange', () => {
        fn.updateCharacterListUI();
        fn.markDirty();
    });

    window.addEventListener('resize', onResize);

    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => h3.closest('.panel-section').classList.toggle('collapsed'));
    });

    const _settingsReady = fetch('/api/settings/humanbody/')
        .then(r => r.json())
        .then(s => {
            if (s.scene) state.defaultPresetName = s.scene;
            window._defaultPose = s.ui_prefs?.default_pose || 'a_pose';
            if (s.default_anim_scene) state._defaultAnimUrl = s.default_anim_scene;
            const expanded = s.expanded_panels_scene;
            if (Array.isArray(expanded)) {
                document.querySelectorAll('.panel-section[data-panel-key]').forEach(panel => {
                    if (panel.closest('#tab-modell') || panel.closest('#tab-kleider')) return;
                    if (expanded.includes(panel.dataset.panelKey)) panel.classList.remove('collapsed');
                    else panel.classList.add('collapsed');
                });
            }
            if (typeof s.selection_opacity === 'number') {
                const o = s.selection_opacity;
                state._SELECT_EMISSIVE = new THREE.Color(o * 0.071, o * 0.071, o * 0.227);
                state._HOVER_EMISSIVE = new THREE.Color(o * 0.031, o * 0.031, o * 0.102);
            }
        }).catch(() => {});

    fn.bindLightingUI();
    fn.bindRendererUI();
    fn.bindCameraUI();
    fn.bindActions();
    fn.bindMenubar();
    fn.initCharacterDialog();
    fn.initSceneDialogs();
    fn._initSaveAnimDialog();
    fn.bindKeyboardShortcuts();
    fn.bindCanvasClick();
    fn.initSubMeshInteraction();
    fn.initTabs();
    fn.bindVisibilityToggles();
    fn.initPropGarmentControls();
    fn._initPropMHControls();
    fn.initPropHairControls();
    fn.loadPoseUI();
    fn.loadMHProxyUI();
    fn.loadGarmentUI();
    fn.loadKleiderUI();
    fn.loadHairUI();
    fn.loadClothUI();
    fn.loadAnimationUI();
    fn.initRiggingTab(fn.toggleRigVisibility);
    fn.loadCharmorphAssets();
    loadCharmorphHairUI();
    initFinalizeTab();

    const demoBtn = document.getElementById('play-demo-anim');
    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            if (!state.currentAction) {
                const inst = fn._selectedInst();
                if (!inst && !state.bodyMesh) return;
                fn.loadBVHAnimation('/api/character/bvh/Mixamo/Catwalk_Idle_02/', 'Catwalk Idle 02', 0);
            } else if (state.playing) {
                state.currentAction.paused = true; state.playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i>'; demoBtn.classList.remove('active');
            } else {
                if (!state.currentAction.isRunning()) state.currentAction.play();
                state.currentAction.paused = false; state.playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>'; demoBtn.classList.add('active');
            }
        });
    }

    fn.loadSettings();
    window.addEventListener('beforeunload', () => { fn.saveSessionState(); });
    animate();

    Promise.all([loadSkinColors(), loadHairColors(), fn.loadRigifySkeleton(), fn.loadSkinWeights(), _settingsReady]).then(async () => {
        if (sessionStorage.getItem(SESSION_KEY)) {
            await fn.restoreSessionState();
        }
        if (state.characters.size === 0) {
            try { await fn.loadDefaultCharacter(); } catch(e) { /* ignore */ }
        }
        // Apply default pose from settings (e.g. T-Pose)
        if (window._defaultPose && window._defaultPose !== 'a_pose' && state.characters.size > 0) {
            const poseMap = { 't_pose': 'rest_poses/t-pose' };
            const poseId = poseMap[window._defaultPose] || window._defaultPose;
            try { await fn.applyPoseFromServer(poseId); } catch(e) { console.warn('[Pose] Default pose failed:', e); }
        }
    });
}

function onResize() {
    const container = state.renderer.domElement.parentElement;
    const w = Math.max(container.clientWidth, 100);
    const h = container.clientHeight || window.innerHeight;
    state.renderer.setSize(w, h);
    state.camera.aspect = w / h;
    state.camera.updateProjectionMatrix();
}

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(state.clock.getDelta(), 0.1);
    state.controls.update();
    if (state.mixer && state.playing) {
        state.mixer.update(dt);
        if (state.currentAction) {
            const clip = state.currentAction.getClip();
            if (clip) {
                const t = state.currentAction.time;
                const dur = clip.duration;
                const ft = clip.tracks[0]?.times?.[1] || (1/30);
                const frame = Math.floor(t / ft);
                const totalFrames = Math.round(dur / ft);
                const el = document.getElementById('anim-time');
                if (el) el.textContent = `Frame ${frame} / ${totalFrames} \u2022 ${t.toFixed(2)}s / ${dur.toFixed(2)}s`;
                const tl = document.getElementById('anim-timeline');
                if (tl) tl.value = Math.round((t / dur) * 100);
            }
        }
        if (state.currentAnimGroundFixed) {
            const inst = fn._selectedInst ? fn._selectedInst() : null;
            const skel = inst ? inst.rigifySkeleton : state.rigifySkeleton;
            if (skel && skel.rootBone) {
                const tmpV = new THREE.Vector3(); let minY = Infinity;
                skel.rootBone.traverse(b => { if (b.isBone) { b.getWorldPosition(tmpV); if (tmpV.y < minY) minY = tmpV.y; } });
                if (isFinite(minY)) skel.rootBone.position.y -= minY;
            }
        }
    }
    state.renderer.render(state.scene, state.camera);

    const p = state.camera.position, t = state.controls.target;
    document.getElementById('cam-pos').textContent = `${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(2)}`;
    document.getElementById('cam-target').textContent = `${t.x.toFixed(2)}, ${t.y.toFixed(2)}, ${t.z.toFixed(2)}`;

    state.frameCount++;
    state.fpsAccum += dt;
    if (state.fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = state.frameCount;
        state.frameCount = 0; state.fpsAccum = 0;
    }
}
