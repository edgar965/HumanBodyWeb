/**
 * HumanBody Character Viewer — Three.js renderer + morph UI + wardrobe + animations.
 * Single-file ES module using importmap.
 *
 * Skinning: 176-bone DEF skeleton (Blender Rigify) with BVH→DEF retargeting.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl } from './retarget_hybrid.js?v=32';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js?v=2';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';

// Register BVH helpers on BufferGeometry (but NOT global raycast override)
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;

// =========================================================================
// Viewer config — overridable via window.VIEWER_CONFIG (set in template)
// =========================================================================
const CFG = window.VIEWER_CONFIG || {};
const API = CFG.apiPrefix || '/api/character';
const WS_PATH = CFG.wsPath || '/ws/character/';
const DEFAULT_BODY = CFG.defaultBodyType || null;  // null = use preset

// =========================================================================
// Global state
// =========================================================================
let scene, camera, renderer, controls;
let keyLight, fillLight, backLight, ambient;
let bodyMesh = null;
let bodyGeometry = null;
let vertexCount = 0;
let ws = null;
let wsReady = false;
let clock = new THREE.Clock();
let frameCount = 0;
let fpsAccum = 0;

// Animation
let mixer = null;
let currentAction = null;
let skeletonHelper = null;
let currentAnimName = '';
let currentAnimFrames = 0;
let currentAnimDuration = 0;

// Wardrobe
const loadedAssets = {};  // name -> THREE.Object3D
const gltfLoader = new GLTFLoader();
const bvhLoader = new BVHLoader();

// GPU Skinning — Rigify skeleton
let skinWeightData = null;   // Raw data from /api/character/skin-weights/
let rigifySkeletonData = null;  // Raw JSON from /api/character/rigify-skeleton/
let rigifySkeleton = null;      // { skeleton, rootBone, bones, boneByName }
let isSkinned = false;       // Flag: Mesh is already SkinnedMesh

// Rig skeleton visualization
let rigVisible = false;

// Cloth — multiple pieces keyed by region
const clothMeshes = {};  // region -> THREE.Mesh
const clothParams = {};  // region -> { params, color }

// Garments — fitted external garments keyed by garment_id
const garmentMeshes = {};  // garment_id -> THREE.Mesh
const garmentState = {};   // garment_id -> {posX,posY,posZ,scaleX,scaleY,scaleZ,color,roughness,metalness}
const garmentOrigPositions = {};  // garment_id -> Float32Array (original vertex positions for buffer transforms)
const garmentRegionWeights = {};  // garment_id -> { top: Float32Array, upper: ..., mid: ..., lower: ..., bottom: ... }
let selectedGarmentId = '';

// Region definitions: each region is a band of the garment's Y extent (Three.js Y = height)
const REGION_DEFS = [
    { id: 'bottom', center: 0.10 },  //  0-20%
    { id: 'lower',  center: 0.30 },  // 20-40%
    { id: 'mid',    center: 0.50 },  // 40-60%
    { id: 'upper',  center: 0.70 },  // 60-80%
    { id: 'top',    center: 0.90 },  // 80-100%
];
const REGION_RADIUS = 0.20;  // half-width of each band (20% → overlaps with neighbors for smooth blending)

// Hair
let hairMesh = null;
let initialBodyTop = null;  // max Y of body at first morph (for hair refit scaling)
let hairColorData = {};  // name -> [r,g,b] (linear sRGB)

// Current preset name (set on load/save)
let currentPresetName = '';

// Skin colors per ethnicity (from API)
let skinColors = {};

// 3D Interaction — raycasting / hover / selection
const _raycaster = new THREE.Raycaster();
const _mouseNDC = new THREE.Vector2();
let _hoveredItem = null;   // { type, id, label, root }
let _selectedItem = null;  // { type, id, label, root }
let _mouseDownPos = null;  // {x, y} for drag detection
let _HOVER_EMISSIVE = new THREE.Color(0x222244);
let _SELECT_EMISSIVE = new THREE.Color(0x4444aa);
const _ZERO_EMISSIVE = new THREE.Color(0x000000);

// =========================================================================
// Expanded panels from settings
// =========================================================================
function applyExpandedPanels() {
    fetch('/api/settings/humanbody/')
        .then(r => r.json())
        .then(s => {
            const expanded = s.expanded_panels_config;
            if (Array.isArray(expanded)) {
                document.querySelectorAll('.panel-section[data-panel-key]').forEach(panel => {
                    const key = panel.dataset.panelKey;
                    if (expanded.includes(key)) {
                        panel.classList.remove('collapsed');
                    } else {
                        panel.classList.add('collapsed');
                    }
                });
            }
            // Dynamic selection opacity
            if (typeof s.selection_opacity === 'number') {
                const o = s.selection_opacity;
                _SELECT_EMISSIVE = new THREE.Color(o * 0.267, o * 0.267, o * 0.667);
                _HOVER_EMISSIVE = new THREE.Color(o * 0.133, o * 0.133, o * 0.333);
            }
        })
        .catch(() => {});
}

// =========================================================================
// Initialization
// =========================================================================
async function init() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;

    // Compute initial size from canvas wrapper
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Camera — character centered at ~1m height
    camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    camera.position.set(0, 1.0, 3.5);

    // Controls
    controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 0.5;
    controls.maxDistance = 15;
    controls.update();

    // Lighting — bright, even illumination from front + back
    keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    scene.add(keyLight);

    fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    scene.add(fillLight);

    backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    scene.add(backLight);

    ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);

    // Apply scene settings from localStorage (configured on /humanbody/scene/)
    applySceneSettings();

    // Ground grid
    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    scene.add(grid);

    // Resize
    window.addEventListener('resize', onResize);

    // Panel toggle
    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => {
            h3.closest('.panel-section').classList.toggle('collapsed');
        });
    });

    // Apply expanded panels from settings
    applyExpandedPanels();

    // Load mesh first, then start render loop (avoids blank screen on first visit)
    loadMorphs();
    loadMesh().then(() => {
        animate();
    });
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

    // Demo animation button — Play/Pause toggle
    const demoBtn = document.getElementById('play-demo-anim');
    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            if (!currentAction) {
                // First click: load animation, open Animations panel
                const animSection = document.getElementById('animation-panel')?.closest('.panel-section');
                if (animSection && animSection.classList.contains('collapsed')) {
                    animSection.classList.remove('collapsed');
                }
                loadBVHAnimation('/api/character/bvh/Mixamo/Catwalk_Idle_02/', 'Catwalk Idle 02', 0);
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            } else if (playing) {
                // Pause
                currentAction.paused = true;
                playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i>';
                demoBtn.classList.remove('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            } else {
                // Resume
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
                playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }
        });
    }

    // Rig toggle — single SkeletonHelper from rigifySkeleton (animates automatically)
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigVisible) {
                // Create helper if needed (from DEF skeleton when available)
                if (!skeletonHelper && rigifySkeleton) {
                    skeletonHelper = new THREE.SkeletonHelper(rigifySkeleton.rootBone);
                    skeletonHelper.material.depthTest = false;
                    skeletonHelper.material.depthWrite = false;
                    skeletonHelper.material.color.set(0x00ffaa);
                    skeletonHelper.material.linewidth = 2;
                    skeletonHelper.renderOrder = 999;
                    scene.add(skeletonHelper);
                }
                if (skeletonHelper) skeletonHelper.visible = true;
            } else {
                if (skeletonHelper) skeletonHelper.visible = false;
            }
            rigToggle.classList.toggle('active', rigVisible);
        });
    }

    // Model toggle
    const modelToggle = document.getElementById('model-toggle');
    if (modelToggle) {
        modelToggle.addEventListener('click', () => {
            if (bodyMesh) bodyMesh.visible = !bodyMesh.visible;
            modelToggle.classList.toggle('active', bodyMesh && bodyMesh.visible);
        });
    }

    // Clothes toggle — hide/show all assets (cloth, wardrobe, hair)
    const clothesToggle = document.getElementById('clothes-toggle');
    if (clothesToggle) {
        let clothesVisible = true;
        clothesToggle.addEventListener('click', () => {
            clothesVisible = !clothesVisible;
            for (const m of Object.values(clothMeshes)) {
                if (m) m.visible = clothesVisible;
            }
            for (const m of Object.values(loadedAssets)) {
                if (m) m.visible = clothesVisible;
            }
            for (const m of Object.values(garmentMeshes)) {
                if (m) m.visible = clothesVisible;
            }
            if (hairMesh) hairMesh.visible = clothesVisible;
            clothesToggle.classList.toggle('active', clothesVisible);
        });
    }

    // Global refit — refit all garments + reposition hair to current morphs
    const refitAllGlobal = document.getElementById('refit-all-btn');
    if (refitAllGlobal) {
        refitAllGlobal.addEventListener('click', async () => {
            refitAllGlobal.disabled = true;
            refitAllGlobal.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
            // Refit garments
            const gids = Object.keys(garmentMeshes);
            for (const gid of gids) _saveGarmentState(gid);
            for (const gid of gids) await loadGarment(gid);
            // Refit hair — scale to match body size change
            refitHairToBody();
            refitAllGlobal.disabled = false;
            refitAllGlobal.innerHTML = '<i class="fas fa-sync"></i> Refit';
        });
    }

    // ---- Custom viewer-action events (dispatched from scene_model.html menus) ----
    document.addEventListener('viewer-action', (e) => {
        const action = e.detail?.action;
        switch (action) {
            case 'new': {
                // Reset morphs via hidden button
                document.getElementById('reset-morphs')?.click();
                // Remove all garments, cloth, hair
                removeAllGarments();
                removeAllCloth();
                removeHair();
                const hs = document.getElementById('hair-style-select');
                if (hs) hs.value = '';
                // Clear selection
                if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
                _selectedItem = null;
                _hoveredItem = null;
                const rb = document.getElementById('selection-remove-btn');
                if (rb) rb.style.display = 'none';
                updateEquippedList();
                currentPresetName = '';
                // Stop animation if playing
                if (currentAction) { currentAction.stop(); currentAction = null; }
                break;
            }
            case 'deselect': {
                if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
                _selectedItem = null;
                _hoveredItem = null;
                const rb2 = document.getElementById('selection-remove-btn');
                if (rb2) rb2.style.display = 'none';
                break;
            }
            case 'delete':
                _removeSelectedItem();
                break;
            case 'clear-all': {
                if (!confirm('Alle Kleidung, Haare und Garments entfernen?')) break;
                removeAllGarments();
                removeAllCloth();
                removeHair();
                const hs2 = document.getElementById('hair-style-select');
                if (hs2) hs2.value = '';
                if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
                _selectedItem = null;
                _hoveredItem = null;
                const rb3 = document.getElementById('selection-remove-btn');
                if (rb3) rb3.style.display = 'none';
                updateEquippedList();
                break;
            }
            case 'export-model-json': {
                const state = gatherModelState();
                const json = JSON.stringify(state, null, 2);
                const blob = new Blob([json], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = (currentPresetName || 'model') + '.json';
                a.click();
                URL.revokeObjectURL(url);
                break;
            }
            case 'reset-camera':
                camera.fov = 35;
                camera.updateProjectionMatrix();
                camera.position.set(0, 1.0, 3.5);
                controls.target.set(0, 0.9, 0);
                controls.update();
                break;
            case 'reset-lighting':
                keyLight.color.setHex(0xffffff);  keyLight.intensity = 3.0;  keyLight.position.set(2, 4, -5);
                fillLight.color.setHex(0xeeeeff); fillLight.intensity = 2.0; fillLight.position.set(-3, 3, -4);
                backLight.color.setHex(0xffeedd); backLight.intensity = 2.5; backLight.position.set(0, 4, 5);
                ambient.color.setHex(0xffffff);   ambient.intensity = 0.8;
                break;
            case 'reset-scene':
                if (!confirm('Szene komplett zurücksetzen? (Modell, Beleuchtung, Kamera)')) break;
                document.dispatchEvent(new CustomEvent('viewer-action', { detail: { action: 'new' } }));
                document.dispatchEvent(new CustomEvent('viewer-action', { detail: { action: 'reset-lighting' } }));
                document.dispatchEvent(new CustomEvent('viewer-action', { detail: { action: 'reset-camera' } }));
                break;
        }
    });

    // 3D hover + click interaction
    _initInteraction();
}

function onResize() {
    const container = renderer.domElement.parentElement;
    const w = Math.max(container.clientWidth, 100);
    const h = container.clientHeight || window.innerHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
}

function animate() {
    requestAnimationFrame(animate);

    const dt = clock.getDelta();
    controls.update();

    if (mixer && playing) {
        mixer.update(dt);
        // Update timeline slider + info text
        if (currentAction && currentAnimDuration > 0) {
            const t = currentAction.time;
            const pct = Math.min(100, (t / currentAnimDuration) * 100);
            const tl = document.getElementById('anim-timeline');
            if (tl) tl.value = Math.round(pct);
            const curSec = Math.floor(t);
            const totSec = Math.floor(currentAnimDuration);
            const curFrame = Math.round((t / currentAnimDuration) * currentAnimFrames);
            const info = document.getElementById('anim-info');
            if (info) info.textContent = `${currentAnimName} \u2014 ${curSec}/${totSec}s  ${curFrame}/${currentAnimFrames}f`;
        }
    }

    renderer.render(scene, camera);

    // FPS counter
    frameCount++;
    fpsAccum += dt;
    if (fpsAccum >= 1.0) {
        const fpsEl = document.getElementById('fps-display');
        if (fpsEl) fpsEl.textContent = frameCount;
        frameCount = 0;
        fpsAccum = 0;
    }
}

// =========================================================================
// Mesh loading — full-mesh subdivision preserving all material groups
// =========================================================================
const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 0 Skin
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 1 Censor
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },  // 2 Eyelash
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },  // 3 Pupil
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },  // 4 Sclera
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true },  // 5 Cornea
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },  // 6 Iris
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },  // 7 Tongue
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },  // 8 Teeth
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 9 Nails Hand
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 10 Nails Feet
];

function getSkinMat() {
    if (!bodyMesh || !bodyMesh.material) return null;
    return Array.isArray(bodyMesh.material) ? bodyMesh.material[0] : bodyMesh.material;
}

function applySkinColor() {
    const select = document.getElementById('body-type-select');
    const bodyType = select?.value || '';
    if (!bodyType || !Object.keys(skinColors).length) return;
    const parts = bodyType.split('_');
    const ethnicity = parts[1] || parts[0];
    const colors = skinColors[ethnicity];
    const mat = getSkinMat();
    if (colors && mat) {
        mat.color.setRGB(
            Math.pow(colors[0], 1/2.2),
            Math.pow(colors[1], 1/2.2),
            Math.pow(colors[2], 1/2.2)
        );
        syncSkinUI(mat);
    }
}

async function loadMesh() {
    try {
        const resp = await fetch(`${API}/mesh/`);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        vertexCount = data.vertex_count;
        { const el = document.getElementById('vertex-count'); if (el) el.textContent = vertexCount.toLocaleString(); }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            const faceBuf = base64ToUint32(data.faces);
            index = new THREE.BufferAttribute(faceBuf, 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            const uvBuf = base64ToFloat32(data.uvs);
            uvAttr = new THREE.BufferAttribute(uvBuf, 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        // Server sends Catmull-Clark subdivided geometry — render directly.
        let geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        // Use server-computed normals (quad-topology based, no triangulation artifacts)
        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];

        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        bodyGeometry = geo;
        scene.add(bodyMesh);
        // Record initial body top for hair refit
        if (initialBodyTop === null) initialBodyTop = _getBodyTop();

        { const el = document.getElementById('vertex-count'); if (el) el.textContent = geo.attributes.position.count.toLocaleString(); }

        applySceneSkinSettings();
        applySkinColor();
        onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

function _getBodyTop() {
    if (!bodyGeometry) return null;
    const pos = bodyGeometry.attributes.position.array;
    let maxY = -Infinity;
    for (let i = 1; i < pos.length; i += 3) {
        if (pos[i] > maxY) maxY = pos[i];
    }
    return maxY;
}

function updateMeshVertices(float32Buffer) {
    if (!bodyGeometry) return;
    const positions = bodyGeometry.attributes.position;
    const newData = new Float32Array(float32Buffer);
    blenderToThreeCoords(newData);
    positions.array.set(newData);
    positions.needsUpdate = true;
    bodyGeometry.computeBoundingSphere();
    // Record initial body height for hair refit
    if (initialBodyTop === null) {
        initialBodyTop = _getBodyTop();
    }
}

async function reloadMeshForBodyType(bodyType, gender) {
    console.log('Reloading mesh for', bodyType, '(gender:', gender, ')');
    // Remove old mesh
    if (bodyMesh) {
        scene.remove(bodyMesh);
        bodyMesh.geometry?.dispose();
        bodyMesh = null;
        bodyGeometry = null;
    }
    isSkinned = false;
    rigifySkeleton = null;
    skinWeightData = null;
    initialBodyTop = null;  // reset for new body type

    // Fetch new mesh with body_type param
    try {
        const resp = await fetch(`${API}/mesh/?body_type=${encodeURIComponent(bodyType)}`);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        vertexCount = data.vertex_count;
        { const el = document.getElementById('vertex-count'); if (el) el.textContent = vertexCount.toLocaleString(); }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            const faceBuf = base64ToUint32(data.faces);
            index = new THREE.BufferAttribute(faceBuf, 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            const uvBuf = base64ToFloat32(data.uvs);
            uvAttr = new THREE.BufferAttribute(uvBuf, 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        let geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];
        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        bodyGeometry = geo;
        scene.add(bodyMesh);
        initialBodyTop = _getBodyTop();

        { const el = document.getElementById('vertex-count'); if (el) el.textContent = geo.attributes.position.count.toLocaleString(); }

        applySceneSkinSettings();
        applySkinColor();

        // Reload skin weights for new gender
        const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);
        skinWeightData = await swResp.json();

        // Remove clothing (topology mismatch)
        if (typeof removeAllCloth === 'function') removeAllCloth();
    } catch (e) {
        console.error('Failed to reload mesh:', e);
    }
}

// =========================================================================
// GPU Skinning — 176-bone DEF skeleton + BVH retargeting
// =========================================================================

async function loadSkinWeights() {
    try {
        const resp = await fetch(`${API}/skin-weights/`);
        if (resp.ok) skinWeightData = await resp.json();
    } catch (e) {
        console.warn('Skin weights not available:', e);
    }
}

async function loadRigifySkeleton() {
    try {
        const resp = await fetch(`${API}/rigify-skeleton/`);
        if (resp.ok) {
            rigifySkeletonData = await resp.json();
            console.log(`DEF skeleton loaded: ${rigifySkeletonData.bone_count} bones`);
        }
    } catch (e) {
        console.warn('DEF skeleton not available:', e);
    }
}

// buildRigifySkeleton() imported from rigify_skeleton_builder.js

/**
 * Convert bodyMesh to SkinnedMesh using DEF skeleton.
 * Skin indices come directly from skin_weights.json (no remapping needed).
 */
function convertToRigifySkinnedMesh(rigifySkel, swData) {
    if (isSkinned || !bodyMesh || !bodyGeometry) return;

    // Clone geometry — the original has stale WebGL VAO state from non-skinned rendering
    bodyGeometry = bodyGeometry.clone();

    const vCount = bodyGeometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);

    for (let v = 0; v < vCount; v++) {
        const infs = swData.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }

    bodyGeometry.setAttribute('skinIndex',
        new THREE.Float32BufferAttribute(skinIndices, 4));
    bodyGeometry.setAttribute('skinWeight',
        new THREE.Float32BufferAttribute(skinWeights, 4));

    // Rebuild skeleton — reusing a Skeleton whose bones were created before
    // parenting to SkinnedMesh causes stale boneTexture/boneMatrices state.
    rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, swData);

    // Replace Mesh with SkinnedMesh
    const mat = bodyMesh.material;
    const pos = bodyMesh.position.clone();
    const vis = bodyMesh.visible;
    scene.remove(bodyMesh);

    bodyMesh = new THREE.SkinnedMesh(bodyGeometry, mat);
    bodyMesh.position.copy(pos);
    bodyMesh.visible = vis;
    bodyMesh.add(rigifySkeleton.rootBone);
    bodyMesh.bind(rigifySkeleton.skeleton);

    scene.add(bodyMesh);
    isSkinned = true;
    console.log('SkinnedMesh created:', bodyMesh.isSkinnedMesh,
                'bones:', rigifySkeleton.skeleton.bones.length,
                'skinIndex:', !!bodyGeometry.attributes.skinIndex,
                'skinWeight:', !!bodyGeometry.attributes.skinWeight);
}

/**
 * Ensure body mesh is converted to SkinnedMesh (if skeleton data available).
 * Call before creating cloth/hair SkinnedMeshes that share the skeleton.
 */
function ensureSkinned() {
    if (isSkinned) return;
    if (!rigifySkeletonData || !skinWeightData || !bodyMesh) return;
    convertToRigifySkinnedMesh(null, skinWeightData);
}

// Retarget via server-side API (retarget_hybrid.js)

// =========================================================================
// WebSocket for live morphing
// =========================================================================
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}${WS_PATH}`;

    ws = new WebSocket(url);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
        wsReady = true;
        const wsEl = document.getElementById('ws-status');
        if (wsEl) { wsEl.textContent = 'Connected'; wsEl.className = 'connected'; }
        // Sync current body type to WebSocket on connect
        const btSelect = document.getElementById('body-type-select');
        if (btSelect && btSelect.value) {
            wsSend({ type: 'body_type', value: btSelect.value });
        }
        // Re-sync all morph + meta values (server state is fresh after reconnect)
        _resyncMorphsOnReconnect();
    };

    ws.onclose = () => {
        wsReady = false;
        const wsEl = document.getElementById('ws-status');
        if (wsEl) { wsEl.textContent = 'Disconnected'; wsEl.className = 'disconnected'; }
        // Reconnect after delay
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (e) => {
        console.error('WebSocket error:', e);
    };

    ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
            // Binary: updated vertices
            updateMeshVertices(event.data);
        } else {
            // JSON message
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'error') {
                    console.error('Server error:', msg.message);
                } else if (msg.type === 'reload_mesh') {
                    reloadMeshForBodyType(msg.body_type, msg.gender);
                }
            } catch (e) {
                // ignore
            }
        }
    };
}

function wsSend(msg) {
    if (ws && wsReady) {
        ws.send(JSON.stringify(msg));
    }
}

/**
 * Re-send all current morph + meta slider values after WebSocket reconnect.
 * The server creates a fresh CharacterState on reconnect, so all state is lost.
 */
function _resyncMorphsOnReconnect() {
    // Batch all morph slider values
    const morphBatch = {};
    document.querySelectorAll('#morphs-panel input[type="range"][data-morph]').forEach(s => {
        const v = parseInt(s.value) / 100.0;
        if (Math.abs(v) > 0.001) morphBatch[s.dataset.morph] = v;
    });
    if (Object.keys(morphBatch).length > 0) {
        wsSend({ type: 'morph_batch', morphs: morphBatch });
    }
    // Re-send meta values
    ['age', 'mass', 'tone', 'height'].forEach(name => {
        const el = document.getElementById(`meta-${name}`);
        if (!el) return;
        const dv = parseInt(el.value);
        const mn = parseInt(el.min), mx = parseInt(el.max);
        const neutral = (mn + mx) / 2;
        const half = (mx - mn) / 2;
        const internal = half ? (dv - neutral) / half : 0;
        if (Math.abs(internal) > 0.001) {
            wsSend({ type: 'meta', name, value: internal });
        }
    });
}

// Throttle morph sends (max ~30 per second)
let morphTimer = null;
let pendingMorphs = {};

function sendMorphThrottled(key, value) {
    pendingMorphs[key] = value;
    if (!morphTimer) {
        morphTimer = setTimeout(() => {
            if (Object.keys(pendingMorphs).length === 1) {
                const [k, v] = Object.entries(pendingMorphs)[0];
                wsSend({ type: 'morph', key: k, value: v });
            } else {
                wsSend({ type: 'morph_batch', morphs: pendingMorphs });
            }
            pendingMorphs = {};
            morphTimer = null;
        }, 33);
    }
}

// =========================================================================
// Morph UI
// =========================================================================
let morphCategories = {};

async function loadMorphs() {
    try {
        const resp = await fetch(`${API}/morphs/`);
        const data = await resp.json();
        skinColors = data.skin_colors || {};

        // Body type dropdown
        const select = document.getElementById('body-type-select');
        data.body_types.forEach(bt => {
            const opt = document.createElement('option');
            opt.value = bt;
            opt.textContent = bt.replace('_', ' ');
            select.appendChild(opt);
        });
        select.addEventListener('change', () => {
            wsSend({ type: 'body_type', value: select.value });
            // Update skin color
            const parts = select.value.split('_');
            const ethnicity = parts[1] || parts[0];
            const colors = data.skin_colors[ethnicity];
            const skinMat = getSkinMat();
            if (colors && skinMat) {
                skinMat.color.setRGB(
                    Math.pow(colors[0], 1/2.2),
                    Math.pow(colors[1], 1/2.2),
                    Math.pow(colors[2], 1/2.2)
                );
                syncSkinUI(skinMat);
            }
            // Remove clothing for male body types (no bra/pants on male characters)
            if (select.value.startsWith('Male_')) {
                removeAllCloth();
            }
        });

        // Meta sliders (Age, Mass, Tone, Height)
        const metaSliders = ['age', 'mass', 'tone', 'height'];
        metaSliders.forEach(name => {
            const slider = document.getElementById(`meta-${name}`);
            const valSpan = document.getElementById(`meta-${name}-val`);
            if (!slider) return;
            const meta = data.meta_sliders?.[name];
            if (meta) {
                slider.min = meta.min;
                slider.max = meta.max;
                slider.value = meta.default;
                valSpan.textContent = meta.default;
            }
            slider.addEventListener('input', () => {
                const displayVal = parseInt(slider.value);
                valSpan.textContent = displayVal;
                const min = parseInt(slider.min), max = parseInt(slider.max);
                const neutral = (min + max) / 2;
                const half = (max - min) / 2;
                const internal = half ? (displayVal - neutral) / half : 0;
                wsSend({ type: 'meta', name: name, value: internal });
            });
        });

        // Skin color + material controls (in Body Type panel)
        const skinColorInput = document.getElementById('skin-color-viewer');
        if (skinColorInput) {
            skinColorInput.addEventListener('input', e => {
                const mat = getSkinMat();
                if (mat) mat.color.set(e.target.value);
            });
        }
        const skinRoughSlider = document.getElementById('skin-roughness-viewer');
        const skinRoughVal = document.getElementById('skin-roughness-viewer-val');
        if (skinRoughSlider) {
            skinRoughSlider.addEventListener('input', () => {
                const v = parseFloat(skinRoughSlider.value) / 100;
                skinRoughVal.textContent = v.toFixed(2);
                const mat = getSkinMat();
                if (mat) mat.roughness = v;
            });
        }
        const skinMetalSlider = document.getElementById('skin-metalness-viewer');
        const skinMetalVal = document.getElementById('skin-metalness-viewer-val');
        if (skinMetalSlider) {
            skinMetalSlider.addEventListener('input', () => {
                const v = parseFloat(skinMetalSlider.value) / 100;
                skinMetalVal.textContent = v.toFixed(2);
                const mat = getSkinMat();
                if (mat) mat.metalness = v;
            });
        }

        // Group morphs by category
        morphCategories = {};
        data.morphs.forEach(m => {
            if (!morphCategories[m.category]) morphCategories[m.category] = [];
            morphCategories[m.category].push(m);
        });

        const panel = document.getElementById('morphs-panel');
        panel.innerHTML = '';

        data.categories.sort().forEach(cat => {
            const morphs = morphCategories[cat];
            if (!morphs || morphs.length === 0) return;

            const div = document.createElement('div');
            div.className = 'morph-category';

            const header = document.createElement('div');
            header.className = 'morph-category-header';
            header.textContent = `${cat} (${morphs.length})`;
            header.addEventListener('click', () => div.classList.toggle('open'));
            div.appendChild(header);

            const body = document.createElement('div');
            body.className = 'morph-category-body';

            morphs.forEach(m => {
                const row = document.createElement('div');
                row.className = 'slider-row';

                const label = document.createElement('label');
                label.textContent = m.name.split('_').slice(1).join(' ') || m.name;
                label.title = m.name;

                const slider = document.createElement('input');
                slider.type = 'range';
                slider.min = -100;
                slider.max = 100;
                slider.value = 0;
                slider.step = 1;
                slider.dataset.morph = m.name;

                const valSpan = document.createElement('span');
                valSpan.className = 'slider-val';
                valSpan.textContent = '0';

                slider.addEventListener('input', () => {
                    const v = parseInt(slider.value) / 100.0;
                    valSpan.textContent = slider.value;
                    sendMorphThrottled(m.name, v);
                });

                row.appendChild(label);
                row.appendChild(slider);
                row.appendChild(valSpan);
                body.appendChild(row);
            });

            div.appendChild(body);
            panel.appendChild(div);
        });

        // Reset button
        document.getElementById('reset-morphs').addEventListener('click', () => {
            // Reset all morph sliders to 0
            panel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                s.nextElementSibling.textContent = '0';
            });
            // Reset meta sliders to defaults
            metaSliders.forEach(name => {
                const slider = document.getElementById(`meta-${name}`);
                const valSpan = document.getElementById(`meta-${name}-val`);
                if (!slider) return;
                const meta = data.meta_sliders?.[name];
                if (meta) {
                    slider.value = meta.default;
                    valSpan.textContent = meta.default;
                }
            });
            // Reset skin material to current body-type ethnicity color
            const skinMat = getSkinMat();
            if (skinMat) {
                const parts = select.value.split('_');
                const ethnicity = parts[1] || parts[0];
                const colors = data.skin_colors[ethnicity];
                if (colors) {
                    skinMat.color.setRGB(
                        Math.pow(colors[0], 1/2.2),
                        Math.pow(colors[1], 1/2.2),
                        Math.pow(colors[2], 1/2.2)
                    );
                } else {
                    skinMat.color.setHex(0xd4a574);
                }
                skinMat.roughness = 0.55;
                skinMat.metalness = 0.0;
                syncSkinUI(skinMat);
            }
            if (skinRoughSlider) { skinRoughSlider.value = 55; skinRoughVal.textContent = '0.55'; }
            if (skinMetalSlider) { skinMetalSlider.value = 0; skinMetalVal.textContent = '0.00'; }
            wsSend({ type: 'reset', body_type: select.value });
        });

        // Apply initial skin color (mesh may already be loaded)
        applySkinColor();

    } catch (e) {
        console.error('Failed to load morphs:', e);
    }
}

// =========================================================================
// Wardrobe UI
// =========================================================================
async function loadWardrobe() {
    try {
        const resp = await fetch('/api/character/wardrobe/');
        const data = await resp.json();
        const panel = document.getElementById('wardrobe-panel');
        panel.innerHTML = '';

        if (!data.assets || data.assets.length === 0) {
            panel.innerHTML += '<div style="color:var(--text-muted);font-size:0.8rem;">No assets available</div>';
            return;
        }

        // Group by category
        const cats = {};
        data.assets.forEach(a => {
            if (!cats[a.category]) cats[a.category] = [];
            cats[a.category].push(a);
        });

        Object.keys(cats).sort().forEach(cat => {
            const label = document.createElement('div');
            label.style.cssText = 'font-size:0.78rem;color:var(--text-muted);margin:8px 0 4px;';
            label.textContent = cat;
            panel.appendChild(label);

            const grid = document.createElement('div');
            grid.className = 'asset-grid';

            cats[cat].forEach(asset => {
                const btn = document.createElement('div');
                btn.className = 'asset-btn';
                if (asset.has_glb === false) btn.classList.add('disabled');
                btn.textContent = asset.name.replace(/_/g, ' ');
                btn.title = asset.name;
                btn.dataset.asset = asset.name;
                btn.dataset.url = asset.glb_url;

                btn.addEventListener('click', () => {
                    if (btn.classList.contains('disabled')) return;
                    toggleAsset(asset.name, asset.glb_url, btn);
                });

                grid.appendChild(btn);
            });
            panel.appendChild(grid);
        });
    } catch (e) {
        console.error('Failed to load wardrobe:', e);
    }
}

function toggleAsset(name, url, btn) {
    if (loadedAssets[name]) {
        // Remove
        scene.remove(loadedAssets[name]);
        loadedAssets[name] = null;
        btn.classList.remove('active');
        updateEquippedList();
    } else {
        // Load GLB
        btn.textContent = 'Loading...';
        gltfLoader.load(url, (gltf) => {
            const model = gltf.scene;
            scene.add(model);
            loadedAssets[name] = model;
            btn.classList.add('active');
            btn.textContent = name.replace(/_/g, ' ');
            updateEquippedList();
        }, undefined, (err) => {
            console.error(`Failed to load ${name}:`, err);
            btn.textContent = name.replace(/_/g, ' ');
        });
    }
}

// =========================================================================
// Animation UI — tree-based (matching Animations page)
// =========================================================================
let playing = false;

async function loadAnimations() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('anim-tree');
        if (!tree) return;
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'anim-category';

            const header = document.createElement('div');
            header.className = 'anim-category-header';
            header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
                <span>${cat}</span>
                <span class="cat-count">${anims.length}</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'anim-category-body';

            anims.forEach(anim => {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.dataset.url = anim.url;
                item.innerHTML = `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    loadBVHAnimation(anim.url, anim.name, anim.frames);
                });
                body.appendChild(item);
            });

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        });

        // Bind playback controls (static HTML elements)
        bindPlaybackControls();
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

function bindPlaybackControls() {
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');
    const speedSlider = document.getElementById('anim-speed');
    const speedLabel = document.getElementById('speed-label');

    if (speedSlider && speedLabel) {
        speedSlider.addEventListener('input', () => {
            const speed = parseInt(speedSlider.value) / 100;
            speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`;
            if (mixer) mixer.timeScale = speed;
        });
    }

    if (playBtn) {
        playBtn.addEventListener('click', () => {
            if (!currentAction) return;
            playing = !playing;
            if (playing) {
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
            } else {
                currentAction.paused = true;
            }
            playBtn.innerHTML = playing
                ? '<i class="fas fa-pause"></i>'
                : '<i class="fas fa-play"></i>';
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            stopAnimation();
            if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            if (timeline) timeline.value = 0;
            currentAnimName = '';
            currentAnimFrames = 0;
            currentAnimDuration = 0;
            const info = document.getElementById('anim-info');
            if (info) info.textContent = '\u2014';
        });
    }

    if (timeline) {
        timeline.addEventListener('input', () => {
            if (currentAction && mixer) {
                const wasPaused = currentAction.paused;
                currentAction.paused = false;
                const clip = currentAction.getClip();
                const time = (parseInt(timeline.value) / 100) * clip.duration;
                mixer.setTime(time);
                currentAction.paused = wasPaused;
                // Update info during scrub
                if (currentAnimDuration > 0) {
                    const curSec = Math.floor(time);
                    const totSec = Math.floor(currentAnimDuration);
                    const curFrame = Math.round((time / currentAnimDuration) * currentAnimFrames);
                    const info = document.getElementById('anim-info');
                    if (info) info.textContent = `${currentAnimName} \u2014 ${curSec}/${totSec}s  ${curFrame}/${currentAnimFrames}f`;
                }
            }
        });
    }
}

let skelWrapper = null;

async function loadBVHAnimation(url, name, fc) {
    stopAnimation(true);

    const info = document.getElementById('anim-info');
    if (info) info.textContent = `Lade ${name || 'Animation'}...`;

    // DEF skeleton path: server-side retarget
    if (rigifySkeletonData && skinWeightData && bodyMesh) {
        if (!isSkinned) {
            convertToRigifySkinnedMesh(null, skinWeightData);
        }
        let bodyH = 1.68;
        const bb = new THREE.Box3().setFromObject(bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;

        try {
            const clip = await fetchRetargetedClipFromUrl(url, rigifySkeleton, { bodyHeight: bodyH });
            console.log(`Retargeted clip: ${clip.tracks.length} tracks, ${clip.duration.toFixed(2)}s`);

            // Ensure SkeletonHelper exists for DEF skeleton
            if (!skeletonHelper) {
                skeletonHelper = new THREE.SkeletonHelper(rigifySkeleton.rootBone);
                skeletonHelper.material.depthTest = false;
                skeletonHelper.material.depthWrite = false;
                skeletonHelper.material.color.set(0x00ffaa);
                skeletonHelper.material.linewidth = 2;
                skeletonHelper.renderOrder = 999;
                skeletonHelper.visible = rigVisible;
                scene.add(skeletonHelper);
            }

            // Play on SkinnedMesh
            mixer = new THREE.AnimationMixer(bodyMesh);
            const ss = document.getElementById('anim-speed');
            if (ss) mixer.timeScale = parseInt(ss.value) / 100;
            currentAction = mixer.clipAction(clip);
            currentAction.play();
            playing = true;

            // Store clip info for live timeline updates
            currentAnimName = name || 'Animation';
            currentAnimFrames = fc || 0;
            currentAnimDuration = currentAction ? currentAction.getClip().duration : clip.duration;

            const playBtn = document.getElementById('anim-play');
            if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            if (info) info.textContent = `${currentAnimName} \u2014 0/${Math.floor(currentAnimDuration)}s  0/${currentAnimFrames}f`;
            return;
        } catch (e) {
            console.error('Server retarget failed:', e);
            // Fall through to BVH skeleton fallback
        }
    }

    // Fallback: separate BVH skeleton visualization (no mesh deformation)
    bvhLoader.load(url, (result) => {
        const bvhBones = result.skeleton.bones;
        if (bvhBones.length === 0) return;

        const rootBone = bvhBones[0];

        // Measure and scale
        rootBone.updateWorldMatrix(true, true);
        const skelBox = new THREE.Box3();
        const tmpVec = new THREE.Vector3();
        bvhBones.forEach(b => {
            b.updateWorldMatrix(true, false);
            b.getWorldPosition(tmpVec);
            skelBox.expandByPoint(tmpVec);
        });
        const skelHeight = skelBox.max.y - skelBox.min.y;
        let bodyHeight = 1.75;
        if (bodyMesh) {
            const bodyBox = new THREE.Box3().setFromObject(bodyMesh);
            if (!bodyBox.isEmpty()) bodyHeight = bodyBox.max.y - bodyBox.min.y;
        }
        const scale = bodyHeight / Math.max(skelHeight, 0.01);

        skelWrapper = new THREE.Group();
        skelWrapper.scale.set(scale, scale, scale);
        skelWrapper.add(rootBone);
        scene.add(skelWrapper);

        if (skeletonHelper) scene.remove(skeletonHelper);
        skeletonHelper = new THREE.SkeletonHelper(rootBone);
        skeletonHelper.material.depthTest = false;
        skeletonHelper.material.depthWrite = false;
        skeletonHelper.material.color.set(0x00ffaa);
        skeletonHelper.material.linewidth = 2;
        skeletonHelper.renderOrder = 999;
        skeletonHelper.visible = rigVisible;
        scene.add(skeletonHelper);

        mixer = new THREE.AnimationMixer(rootBone);
        const ss2 = document.getElementById('anim-speed');
        if (ss2) mixer.timeScale = parseInt(ss2.value) / 100;
        currentAction = mixer.clipAction(result.clip);
        currentAction.play();
        playing = true;

        // Store clip info for live timeline updates
        currentAnimName = name || 'Animation';
        currentAnimFrames = fc || 0;
        currentAnimDuration = currentAction ? currentAction.getClip().duration : result.clip.duration;

        const playBtn = document.getElementById('anim-play');
        if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
        if (info) info.textContent = `${currentAnimName} \u2014 0/${Math.floor(currentAnimDuration)}s  0/${currentAnimFrames}f`;
    }, undefined, (err) => {
        console.error('Failed to load BVH:', err);
        if (info) info.textContent = `Fehler: ${name || url}`;
    });
}

function stopAnimation(destroy = false) {
    if (currentAction) {
        currentAction.stop();
        currentAction.reset();
        if (destroy) currentAction = null;
    }
    if (mixer && destroy) {
        mixer.stopAllAction();
        mixer = null;
    }
    // Reset skinned mesh back to bind pose
    if (isSkinned && bodyMesh && bodyMesh.isSkinnedMesh) {
        bodyMesh.skeleton.pose();
    }
    // Clean up BVH fallback wrapper
    if (skelWrapper) {
        scene.remove(skelWrapper);
        skelWrapper = null;
    }
    // Remove animation skeleton helper; recreate from DEF skeleton if rig is visible
    if (skeletonHelper) {
        scene.remove(skeletonHelper);
        skeletonHelper = null;
    }
    if (rigVisible && rigifySkeleton) {
        skeletonHelper = new THREE.SkeletonHelper(rigifySkeleton.rootBone);
        skeletonHelper.material.depthTest = false;
        skeletonHelper.material.depthWrite = false;
        skeletonHelper.material.color.set(0x00ffaa);
        skeletonHelper.material.linewidth = 2;
        skeletonHelper.renderOrder = 999;
        scene.add(skeletonHelper);
    }
    playing = false;
}

// (Rig visualization now uses SkeletonHelper from rigifySkeleton — no separate rigGroup)

// =========================================================================
// Cloth
// =========================================================================
async function loadClothUI() {
    try {
        const resp = await fetch('/api/character/cloth/regions/');
        const data = await resp.json();

        // --- Template UI ---
        const tplSelect = document.getElementById('cloth-tpl-type');
        if (tplSelect) {
            (data.templates || []).forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.key;
                opt.textContent = t.label;
                tplSelect.appendChild(opt);
            });
        }

        _bindSlider('cloth-tpl-segments', 'cloth-tpl-segments-val', v => v);
        _bindSlider('cloth-tpl-tightness', 'cloth-tpl-tightness-val', v => (v / 100).toFixed(2));
        _bindSlider('cloth-tpl-top-ext', 'cloth-tpl-top-ext-val', v => (v / 100).toFixed(2) + ' m');
        _bindSlider('cloth-tpl-bot-ext', 'cloth-tpl-bot-ext-val', v => (v / 100).toFixed(2) + ' m');

        // Helper: gather current template params
        function _tplParams() {
            const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
            return {
                key: `tpl_${tpl}`,
                params: {
                    method: 'template', template: tpl,
                    segments: _sliderVal('cloth-tpl-segments'),
                    tightness: _sliderVal('cloth-tpl-tightness') / 100,
                    top_extend: _sliderVal('cloth-tpl-top-ext') / 100,
                    bottom_extend: _sliderVal('cloth-tpl-bot-ext') / 100,
                },
            };
        }

        // --- Template Preset UI ---
        const TPL_CATEGORY = {
            TPL_TSHIRT: 'Top', TPL_DRESS: 'Top',
            TPL_PANTS: 'Pants', TPL_SKIRT: 'Pants',
        };
        const presetSelect = document.getElementById('cloth-tpl-preset');

        async function refreshClothPresets() {
            if (!presetSelect || !tplSelect) return;
            const cat = TPL_CATEGORY[tplSelect.value] || 'Top';
            try {
                const r = await fetch(`/api/character/cloth/presets/?category=${cat}`);
                const d = await r.json();
                // Keep first option (-- none --)
                while (presetSelect.options.length > 1) presetSelect.remove(1);
                (d.presets || []).forEach(p => {
                    const o = document.createElement('option');
                    o.value = p.name;
                    o.textContent = p.name;
                    presetSelect.appendChild(o);
                });
            } catch (e) {
                console.warn('Failed to load cloth presets:', e);
            }
        }

        // Refresh presets when template changes
        if (tplSelect) {
            tplSelect.addEventListener('change', () => refreshClothPresets());
            refreshClothPresets();  // initial load
        }

        // Helper: save preset via API
        async function _saveClothPreset(name) {
            const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
            const colorPicker = document.getElementById('cloth-color');
            const presetData = {
                template: tpl,
                segments: _sliderVal('cloth-tpl-segments'),
                tightness: _sliderVal('cloth-tpl-tightness') / 100,
                top_extend: _sliderVal('cloth-tpl-top-ext') / 100,
                bottom_extend: _sliderVal('cloth-tpl-bot-ext') / 100,
                color: colorPicker ? colorPicker.value : '#404870',
            };
            try {
                const r = await fetch('/api/character/cloth/presets/save/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, data: presetData }),
                });
                const res = await r.json();
                if (res.ok) {
                    await refreshClothPresets();
                    const safeName = res.filename.replace('.json', '');
                    if (presetSelect) presetSelect.value = safeName;
                    console.log('Cloth preset saved:', res.filename);
                    return true;
                } else {
                    alert('Fehler: ' + (res.error || 'Unbekannt'));
                }
            } catch (e) {
                alert('Fehler: ' + e.message);
            }
            return false;
        }

        // Save preset (overwrite selected, or prompt if none selected)
        const presetSaveBtn = document.getElementById('cloth-tpl-preset-save');
        if (presetSaveBtn) {
            presetSaveBtn.addEventListener('click', async () => {
                let name = presetSelect ? presetSelect.value : '';
                if (!name) {
                    name = prompt('Preset-Name:');
                    if (!name || !name.trim()) return;
                    name = name.trim();
                }
                await _saveClothPreset(name);
            });
        }

        // Save-As preset (always prompt for new name)
        const presetSaveAsBtn = document.getElementById('cloth-tpl-preset-saveas');
        if (presetSaveAsBtn) {
            presetSaveAsBtn.addEventListener('click', async () => {
                const suggested = presetSelect ? presetSelect.value : '';
                const name = prompt('Preset-Name:', suggested);
                if (!name || !name.trim()) return;
                await _saveClothPreset(name.trim());
            });
        }

        // Load preset
        const presetLoadBtn = document.getElementById('cloth-tpl-preset-load');
        if (presetLoadBtn) {
            presetLoadBtn.addEventListener('click', async () => {
                if (!presetSelect || !presetSelect.value) return;
                const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
                const cat = TPL_CATEGORY[tpl] || 'Top';
                try {
                    const r = await fetch(`/api/character/cloth/presets/${cat}/${encodeURIComponent(presetSelect.value)}/`);
                    const d = await r.json();
                    if (d.error) { alert(d.error); return; }
                    // Apply values to sliders + color picker
                    if (d.template && tplSelect) tplSelect.value = d.template;
                    const seg = document.getElementById('cloth-tpl-segments');
                    const segVal = document.getElementById('cloth-tpl-segments-val');
                    if (seg && d.segments !== undefined) {
                        seg.value = d.segments;
                        if (segVal) segVal.textContent = d.segments;
                    }
                    const tight = document.getElementById('cloth-tpl-tightness');
                    const tightVal = document.getElementById('cloth-tpl-tightness-val');
                    if (tight && d.tightness !== undefined) {
                        tight.value = Math.round(d.tightness * 100);
                        if (tightVal) tightVal.textContent = d.tightness.toFixed(2);
                    }
                    const topExt = document.getElementById('cloth-tpl-top-ext');
                    const topExtVal = document.getElementById('cloth-tpl-top-ext-val');
                    if (topExt && d.top_extend !== undefined) {
                        topExt.value = Math.round(d.top_extend * 100);
                        if (topExtVal) topExtVal.textContent = d.top_extend.toFixed(2) + ' m';
                    }
                    const botExt = document.getElementById('cloth-tpl-bot-ext');
                    const botExtVal = document.getElementById('cloth-tpl-bot-ext-val');
                    if (botExt && d.bottom_extend !== undefined) {
                        botExt.value = Math.round(d.bottom_extend * 100);
                        if (botExtVal) botExtVal.textContent = d.bottom_extend.toFixed(2) + ' m';
                    }
                    const colorPicker = document.getElementById('cloth-color');
                    if (colorPicker && d.color) colorPicker.value = d.color;
                    console.log('Cloth preset loaded:', presetSelect.value);
                } catch (e) {
                    alert('Fehler beim Laden: ' + e.message);
                }
            });
        }

        const tplCreate = document.getElementById('cloth-tpl-create');
        if (tplCreate) {
            tplCreate.addEventListener('click', () => {
                const { key, params } = _tplParams();
                loadCloth(key, params);
            });
        }

        // Update button — re-generates the currently selected template cloth
        const tplUpdate = document.getElementById('cloth-tpl-update');
        if (tplUpdate) {
            tplUpdate.addEventListener('click', () => {
                const { key, params } = _tplParams();
                if (!clothMeshes[key]) {
                    console.warn(`No cloth "${key}" to update — use Create first`);
                    return;
                }
                // Use color from color picker (not from existing mesh)
                loadCloth(key, params);
            });
        }

        // Delete current template
        const tplDelete = document.getElementById('cloth-tpl-delete');
        if (tplDelete) {
            tplDelete.addEventListener('click', () => {
                const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
                const key = `tpl_${tpl}`;
                if (clothMeshes[key]) {
                    removeClothRegion(key);
                    console.log(`Cloth "${key}" removed`);
                }
            });
        }

        // --- Builder UI ---
        const bldSelect = document.getElementById('cloth-bld-region');
        if (bldSelect) {
            (data.builder_regions || []).forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.key;
                opt.textContent = r.label;
                bldSelect.appendChild(opt);
            });
        }
        _bindSlider('cloth-bld-looseness', 'cloth-bld-looseness-val', v => (v / 100).toFixed(2));

        const bldCreate = document.getElementById('cloth-bld-create');
        if (bldCreate) {
            bldCreate.addEventListener('click', () => {
                const region = bldSelect ? bldSelect.value : 'TOP';
                const loose = _sliderVal('cloth-bld-looseness') / 100;
                loadCloth(`bld_${region}`, {
                    method: 'builder', region: region, looseness: loose,
                });
            });
        }

        // --- Primitive UI ---
        const primSelect = document.getElementById('cloth-prim-type');
        if (primSelect) {
            (data.primitives || []).forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.key;
                opt.textContent = p.label;
                primSelect.appendChild(opt);
            });
            primSelect.addEventListener('change', () => {
                const flareRow = document.getElementById('cloth-prim-flare-row');
                if (flareRow) flareRow.style.display =
                    primSelect.value === 'PRIM_SKIRT' ? 'flex' : 'none';
            });
        }
        _bindSlider('cloth-prim-segments', 'cloth-prim-segments-val', v => v);
        _bindSlider('cloth-prim-length', 'cloth-prim-length-val', v => (v / 100).toFixed(2));
        _bindSlider('cloth-prim-flare', 'cloth-prim-flare-val', v => (v / 100).toFixed(2));

        const primCreate = document.getElementById('cloth-prim-create');
        if (primCreate) {
            primCreate.addEventListener('click', () => {
                const pt = primSelect ? primSelect.value : 'PRIM_SKIRT';
                const segs = _sliderVal('cloth-prim-segments');
                const len = _sliderVal('cloth-prim-length') / 100;
                const flare = _sliderVal('cloth-prim-flare') / 100;
                loadCloth(`prim_${pt}`, {
                    method: 'primitive', prim_type: pt,
                    segments: segs, length: len, flare: flare,
                });
            });
        }

        // --- Remove All button ---
        const removeBtn = document.getElementById('cloth-remove-all');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => removeAllCloth());
        }
    } catch (e) {
        console.warn('Cloth UI not available:', e);
    }
}

function _bindSlider(sliderId, valId, fmt) {
    const slider = document.getElementById(sliderId);
    const val = document.getElementById(valId);
    if (slider && val) {
        slider.addEventListener('input', () => {
            val.textContent = fmt(parseInt(slider.value));
        });
    }
}

function _sliderVal(sliderId) {
    const el = document.getElementById(sliderId);
    return el ? parseInt(el.value) : 0;
}

function _buildBodyQueryString() {
    const bodySelect = document.getElementById('body-type-select');
    const bodyType = bodySelect ? bodySelect.value : 'Female_Caucasian';
    let qs = `body_type=${encodeURIComponent(bodyType)}`;
    // Morph sliders
    document.querySelectorAll('#morphs-panel input[type="range"]').forEach(slider => {
        const mName = slider.dataset.morph || slider.dataset.morphName || slider.id.replace('morph-', '');
        if (mName && slider.value !== undefined) {
            qs += `&morph_${mName}=${slider.value / 100}`;
        }
    });
    // Meta sliders (display → internal)
    ['age', 'mass', 'tone', 'height'].forEach(m => {
        const el = document.getElementById(`meta-${m}`);
        if (el) {
            const dv = parseInt(el.value);
            const mn = parseInt(el.min), mx = parseInt(el.max);
            const neutral = (mn + mx) / 2;
            const half = (mx - mn) / 2;
            const internal = half ? (dv - neutral) / half : 0;
            qs += `&meta_${m}=${internal}`;
        }
    });
    return qs;
}

async function loadCloth(key, params, color) {
    const createBtns = document.querySelectorAll('#cloth-tpl-create, #cloth-bld-create, #cloth-prim-create');
    createBtns.forEach(b => b.disabled = true);

    // Ensure skinning is ready so cloth can share the skeleton
    ensureSkinned();

    try {
        const qs = Object.entries(params)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        const resp = await fetch(`/api/character/cloth/?${qs}`);
        const data = await resp.json();
        if (data.error) {
            console.error('Cloth error:', data.error);
            return;
        }

        // Remove previous mesh with same key
        removeClothRegion(key);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        let matColor;
        if (color) {
            matColor = new THREE.Color(color);
        } else {
            const colorPicker = document.getElementById('cloth-color');
            matColor = colorPicker
                ? new THREE.Color(colorPicker.value)
                : new THREE.Color(data.color[0], data.color[1], data.color[2]);
        }

        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0,
            side: THREE.DoubleSide,
        });

        // Create as SkinnedMesh if skin data available + body is skinned
        let mesh;
        if (isSkinned && rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        clothMeshes[key] = mesh;
        clothParams[key] = { params, color: '#' + mesh.material.color.getHexString() };
        scene.add(mesh);

        console.log(`Cloth ${key}: ${data.vertex_count} verts, ${data.face_count} tris, skinned=${mesh.isSkinnedMesh || false}`);
        updateEquippedList();
    } catch (e) {
        console.error('Failed to load cloth:', e);
    }
    createBtns.forEach(b => b.disabled = false);
}

function removeClothRegion(key) {
    const m = clothMeshes[key];
    if (m) {
        scene.remove(m);
        m.geometry.dispose();
        m.material.dispose();
        delete clothMeshes[key];
        delete clothParams[key];
        updateEquippedList();
    }
}

function removeAllCloth() {
    for (const key of Object.keys(clothMeshes)) {
        removeClothRegion(key);
    }
}

// =========================================================================
// Pattern Editor
// =========================================================================

let pePattern = { panels: {}, stitches: [] };
let peActivePanel = null;
let peMode = 'select';       // 'select' | 'draw' | 'stitch' | 'region'
let peSelectedVertex = null;  // {panel, index}
let peSelectedEdge = null;    // {panel, index}
let peStitchFirst = null;     // first edge in stitch mode
let pePan = {x: 144, y: 200};
let peZoom = 2.0;             // pixels per cm
let pePreviewKey = 'pe_preview';
let peDragging = null;        // vertex being dragged
let pePanning = false;
let pePanStart = null;
const PE_COLORS = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c'];

// =========================================================================
// Vertex Editor (3D) — BVH raycast + TransformControls gizmo
// =========================================================================
let veActive = false;
let veTargetMesh = null;       // The cloth/garment mesh being edited
let veTargetKey = null;        // Key in clothMeshes or garmentMeshes
let vePointsOverlay = null;    // THREE.Points overlay
let veSelectedIndices = new Set();
let veOrigPositions = null;    // Float32Array — original positions backup
let veGizmo = null;            // TransformControls
let veGizmoHelper = null;      // Object3D — gizmo target
let veGizmoLastPos = new THREE.Vector3();
let veBoxSelecting = false;    // Alt+drag box select
let veBoxStart = { x: 0, y: 0 };
let veBoxEnd = { x: 0, y: 0 };
let veOrigRaycast = null;      // Original raycast to restore on exit
const VE_COLOR_DEFAULT  = new THREE.Color(0.35, 0.45, 0.65);
const VE_COLOR_SELECTED = new THREE.Color(1.0, 0.9, 0.2);

function veEnterEditMode() {
    // Find target mesh
    let mesh = null;
    let key = null;
    if (_selectedItem && (_selectedItem.type === 'cloth' || _selectedItem.type === 'garment')) {
        mesh = clothMeshes[_selectedItem.id] || garmentMeshes[_selectedItem.id];
        key = _selectedItem.id;
    }
    if (!mesh) {
        mesh = clothMeshes[pePreviewKey];
        key = pePreviewKey;
    }
    if (!mesh) {
        console.warn('Vertex Edit: no cloth/garment mesh found');
        peMode = 'select';
        _peSetModeButtons();
        return;
    }

    veActive = true;
    veTargetMesh = mesh;
    veTargetKey = key;
    veSelectedIndices.clear();

    // Get position attribute & save original
    const posAttr = mesh.geometry.getAttribute('position');
    posAttr.setUsage(THREE.DynamicDrawUsage);
    veOrigPositions = new Float32Array(posAttr.array);

    // Build BVH for accelerated raycasting (only on this mesh)
    mesh.geometry.computeBoundsTree();
    veOrigRaycast = mesh.raycast;
    mesh.raycast = acceleratedRaycast;

    // Create Points overlay for visualization
    const pointsGeo = new THREE.BufferGeometry();
    const count = posAttr.count;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
        positions[i * 3]     = posAttr.getX(i);
        positions[i * 3 + 1] = posAttr.getY(i);
        positions[i * 3 + 2] = posAttr.getZ(i);
        colors[i * 3]     = VE_COLOR_DEFAULT.r;
        colors[i * 3 + 1] = VE_COLOR_DEFAULT.g;
        colors[i * 3 + 2] = VE_COLOR_DEFAULT.b;
    }
    pointsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    pointsGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const pointSize = parseFloat(document.getElementById('ve-point-size')?.value || '5');
    const pointsMat = new THREE.PointsMaterial({
        size: pointSize,
        sizeAttenuation: false,
        vertexColors: true,
        depthTest: true,
        depthWrite: false,
    });
    vePointsOverlay = new THREE.Points(pointsGeo, pointsMat);
    vePointsOverlay.matrixAutoUpdate = false;
    vePointsOverlay.matrix.copy(mesh.matrixWorld);
    vePointsOverlay.matrixWorld.copy(mesh.matrixWorld);
    vePointsOverlay.renderOrder = 999;
    scene.add(vePointsOverlay);

    // Create TransformControls gizmo
    veGizmoHelper = new THREE.Object3D();
    scene.add(veGizmoHelper);
    veGizmo = new TransformControls(camera, renderer.domElement);
    veGizmo.attach(veGizmoHelper);
    veGizmo.setMode('translate');
    veGizmo.setSize(0.6);
    veGizmo.visible = false;
    veGizmo.enabled = false;
    scene.add(veGizmo.getHelper());

    // Gizmo events
    veGizmo.addEventListener('dragging-changed', (ev) => {
        controls.enabled = !ev.value;
    });
    veGizmo.addEventListener('objectChange', () => {
        _veApplyGizmoDelta();
    });

    // Show edit controls, hide pattern/region
    const editCtrl = document.getElementById('pe-edit-controls');
    if (editCtrl) editCtrl.style.display = '';
    const patternCtrl = document.getElementById('pe-pattern-controls');
    if (patternCtrl) patternCtrl.style.display = 'none';
    const regionCtrl = document.getElementById('pe-region-controls');
    if (regionCtrl) regionCtrl.style.display = 'none';
    const wrapSection = document.getElementById('pe-wrap-section');
    if (wrapSection) wrapSection.style.display = 'none';

    _veUpdateSelectionInfo();
}

function veExitEditMode() {
    // Restore original raycast + dispose BVH
    if (veTargetMesh && veOrigRaycast) {
        veTargetMesh.raycast = veOrigRaycast;
        veOrigRaycast = null;
    }
    if (veTargetMesh?.geometry?.disposeBoundsTree) {
        veTargetMesh.geometry.disposeBoundsTree();
    }
    // Remove gizmo
    if (veGizmo) {
        scene.remove(veGizmo.getHelper());
        veGizmo.detach();
        veGizmo.dispose();
        veGizmo = null;
    }
    if (veGizmoHelper) {
        scene.remove(veGizmoHelper);
        veGizmoHelper = null;
    }
    // Remove Points overlay
    if (vePointsOverlay) {
        scene.remove(vePointsOverlay);
        vePointsOverlay.geometry.dispose();
        vePointsOverlay.material.dispose();
        vePointsOverlay = null;
    }
    veActive = false;
    veTargetMesh = null;
    veTargetKey = null;
    veSelectedIndices.clear();
    veOrigPositions = null;
    veBoxSelecting = false;

    // Hide box select overlay
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) boxEl.style.display = 'none';

    const editCtrl = document.getElementById('pe-edit-controls');
    if (editCtrl) editCtrl.style.display = 'none';
}

function _veSyncOverlayTransform() {
    if (!vePointsOverlay || !veTargetMesh) return;
    vePointsOverlay.matrix.copy(veTargetMesh.matrixWorld);
    vePointsOverlay.matrixWorld.copy(veTargetMesh.matrixWorld);
}

function _veUpdateVertexColor(idx) {
    if (!vePointsOverlay) return;
    const colorAttr = vePointsOverlay.geometry.getAttribute('color');
    const c = veSelectedIndices.has(idx) ? VE_COLOR_SELECTED : VE_COLOR_DEFAULT;
    colorAttr.setXYZ(idx, c.r, c.g, c.b);
    colorAttr.needsUpdate = true;
}

function _veUpdateAllColors() {
    if (!vePointsOverlay) return;
    const colorAttr = vePointsOverlay.geometry.getAttribute('color');
    const count = colorAttr.count;
    for (let i = 0; i < count; i++) {
        const c = veSelectedIndices.has(i) ? VE_COLOR_SELECTED : VE_COLOR_DEFAULT;
        colorAttr.setXYZ(i, c.r, c.g, c.b);
    }
    colorAttr.needsUpdate = true;
}

function _veUpdateSelectionInfo() {
    const info = document.getElementById('ve-selection-info');
    const posFields = document.getElementById('ve-pos-fields');
    if (!info) return;
    const n = veSelectedIndices.size;
    if (n === 0) {
        info.textContent = 'No vertices selected';
        if (posFields) posFields.style.display = 'none';
    } else {
        info.textContent = `${n} ${n === 1 ? 'vertex' : 'vertices'} selected`;
        if (posFields) {
            posFields.style.display = '';
            _veUpdatePosInputs();
        }
    }
}

function _veUpdatePosInputs() {
    if (!veTargetMesh || veSelectedIndices.size === 0) return;
    const posAttr = veTargetMesh.geometry.getAttribute('position');
    let cx = 0, cy = 0, cz = 0;
    for (const idx of veSelectedIndices) {
        cx += posAttr.getX(idx);
        cy += posAttr.getY(idx);
        cz += posAttr.getZ(idx);
    }
    const n = veSelectedIndices.size;
    const px = document.getElementById('ve-pos-x');
    const py = document.getElementById('ve-pos-y');
    const pz = document.getElementById('ve-pos-z');
    if (px) px.value = (cx / n).toFixed(4);
    if (py) py.value = (cy / n).toFixed(4);
    if (pz) pz.value = (cz / n).toFixed(4);
}

function _veMoveSelectedByDelta(dx, dy, dz) {
    if (!veTargetMesh || !vePointsOverlay) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const overlayPos = vePointsOverlay.geometry.getAttribute('position');
    for (const idx of veSelectedIndices) {
        meshPos.setXYZ(idx, meshPos.getX(idx) + dx, meshPos.getY(idx) + dy, meshPos.getZ(idx) + dz);
        overlayPos.setXYZ(idx, overlayPos.getX(idx) + dx, overlayPos.getY(idx) + dy, overlayPos.getZ(idx) + dz);
    }
    meshPos.needsUpdate = true;
    overlayPos.needsUpdate = true;
    veTargetMesh.geometry.computeVertexNormals();
    veTargetMesh.geometry.computeBoundingSphere();
}

// --- Gizmo delta application ---
function _veApplyGizmoDelta() {
    if (!veGizmoHelper || !veTargetMesh || veSelectedIndices.size === 0) return;
    const newPos = veGizmoHelper.position.clone();
    const worldDelta = newPos.clone().sub(veGizmoLastPos);
    veGizmoLastPos.copy(newPos);

    // Convert world delta to mesh local space
    const invMat = new THREE.Matrix4().copy(veTargetMesh.matrixWorld).invert();
    const localDelta = worldDelta.applyMatrix4(new THREE.Matrix4().extractRotation(invMat));

    _veMoveSelectedByDelta(localDelta.x, localDelta.y, localDelta.z);
    _veUpdatePosInputs();
}

// --- Update gizmo position to centroid of selection ---
function _veUpdateGizmo() {
    if (!veGizmo || !veGizmoHelper || !veTargetMesh) return;
    if (veSelectedIndices.size === 0) {
        veGizmo.visible = false;
        veGizmo.enabled = false;
        return;
    }
    // Compute centroid in local space, then transform to world
    const posAttr = veTargetMesh.geometry.getAttribute('position');
    let cx = 0, cy = 0, cz = 0;
    for (const idx of veSelectedIndices) {
        cx += posAttr.getX(idx);
        cy += posAttr.getY(idx);
        cz += posAttr.getZ(idx);
    }
    const n = veSelectedIndices.size;
    const localCentroid = new THREE.Vector3(cx / n, cy / n, cz / n);
    const worldCentroid = localCentroid.applyMatrix4(veTargetMesh.matrixWorld);

    veGizmoHelper.position.copy(worldCentroid);
    veGizmoLastPos.copy(worldCentroid);
    veGizmo.visible = true;
    veGizmo.enabled = true;
}

// --- BVH surface click → nearest vertex ---
function _veHandleClick(e) {
    if (!veActive || !veTargetMesh) return;
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    _mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    _mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    _raycaster.setFromCamera(_mouseNDC, camera);

    // BVH-accelerated raycast on the cloth mesh surface
    const intersects = _raycaster.intersectObject(veTargetMesh);
    if (intersects.length > 0) {
        const hit = intersects[0];
        const face = hit.face;
        // Find the closest vertex of the hit face to the hit point
        const posAttr = veTargetMesh.geometry.getAttribute('position');
        const hitLocal = hit.point.clone().applyMatrix4(
            new THREE.Matrix4().copy(veTargetMesh.matrixWorld).invert()
        );
        let bestIdx = face.a;
        let bestDist = Infinity;
        for (const vi of [face.a, face.b, face.c]) {
            const vp = new THREE.Vector3(posAttr.getX(vi), posAttr.getY(vi), posAttr.getZ(vi));
            const d = vp.distanceTo(hitLocal);
            if (d < bestDist) { bestDist = d; bestIdx = vi; }
        }

        if (e.shiftKey) {
            if (veSelectedIndices.has(bestIdx)) veSelectedIndices.delete(bestIdx);
            else veSelectedIndices.add(bestIdx);
        } else {
            veSelectedIndices.clear();
            veSelectedIndices.add(bestIdx);
        }
    } else if (!e.shiftKey) {
        veSelectedIndices.clear();
    }
    _veUpdateAllColors();
    _veUpdateGizmo();
    _veUpdateSelectionInfo();
}

// --- Box selection (Alt+drag) ---
function _veBoxSelectStart(e) {
    if (!veActive) return;
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    veBoxSelecting = true;
    veBoxStart = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    veBoxEnd = { ...veBoxStart };
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) {
        boxEl.style.display = 'block';
        boxEl.style.left = veBoxStart.x + 'px';
        boxEl.style.top = veBoxStart.y + 'px';
        boxEl.style.width = '0px';
        boxEl.style.height = '0px';
    }
    controls.enabled = false;
}

function _veBoxSelectMove(e) {
    if (!veBoxSelecting) return;
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    veBoxEnd = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) {
        const x = Math.min(veBoxStart.x, veBoxEnd.x);
        const y = Math.min(veBoxStart.y, veBoxEnd.y);
        const w = Math.abs(veBoxEnd.x - veBoxStart.x);
        const h = Math.abs(veBoxEnd.y - veBoxStart.y);
        boxEl.style.left = x + 'px';
        boxEl.style.top = y + 'px';
        boxEl.style.width = w + 'px';
        boxEl.style.height = h + 'px';
    }
}

function _veBoxSelectEnd(e) {
    if (!veBoxSelecting) return;
    veBoxSelecting = false;
    controls.enabled = true;
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) boxEl.style.display = 'none';

    if (!veTargetMesh || !vePointsOverlay) return;
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    const w = rect.width, h = rect.height;

    // Screen-space bounding box (in pixels, relative to canvas)
    const minX = Math.min(veBoxStart.x, veBoxEnd.x);
    const maxX = Math.max(veBoxStart.x, veBoxEnd.x);
    const minY = Math.min(veBoxStart.y, veBoxEnd.y);
    const maxY = Math.max(veBoxStart.y, veBoxEnd.y);

    // Ignore tiny boxes (accidental clicks)
    if ((maxX - minX) < 3 && (maxY - minY) < 3) return;

    if (!e.shiftKey) veSelectedIndices.clear();

    // Project all vertices to screen and select those inside rectangle
    const posAttr = veTargetMesh.geometry.getAttribute('position');
    const count = posAttr.count;
    const v = new THREE.Vector3();
    for (let i = 0; i < count; i++) {
        v.set(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
        v.applyMatrix4(veTargetMesh.matrixWorld);
        v.project(camera);
        const sx = (v.x * 0.5 + 0.5) * w;
        const sy = (-v.y * 0.5 + 0.5) * h;
        if (sx >= minX && sx <= maxX && sy >= minY && sy <= maxY && v.z > 0 && v.z < 1) {
            veSelectedIndices.add(i);
        }
    }

    _veUpdateAllColors();
    _veUpdateGizmo();
    _veUpdateSelectionInfo();
}

// --- Base64 helpers for sending buffers to server ---
function _float32ToBase64(f32) {
    const bytes = new Uint8Array(f32.buffer, f32.byteOffset, f32.byteLength);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    return btoa(binary);
}

function _uint32ToBase64(u32) {
    const bytes = new Uint8Array(u32.buffer, u32.byteOffset, u32.byteLength);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    return btoa(binary);
}

// Three.js→Blender: (x, y, z) → (x, -z, y)
function _threeToBlenderCoords(buf) {
    const out = new Float32Array(buf.length);
    for (let i = 0; i < buf.length; i += 3) {
        out[i]     = buf[i];
        out[i + 1] = -buf[i + 2];
        out[i + 2] = buf[i + 1];
    }
    return out;
}

// --- Server tool calls ---
async function _veSmooth() {
    if (!veActive || !veTargetMesh || veSelectedIndices.size === 0) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const posArr = new Float32Array(meshPos.array);
    const blenderVerts = _threeToBlenderCoords(posArr);

    // Build faces array
    const indexAttr = veTargetMesh.geometry.getIndex();
    if (!indexAttr) { console.warn('No index buffer for smooth'); return; }
    const facesArr = new Uint32Array(indexAttr.array);

    const selected = Array.from(veSelectedIndices);

    const statusEl = document.getElementById('ve-selection-info');
    if (statusEl) statusEl.textContent = 'Smoothing...';

    try {
        const resp = await fetch('/api/character/vertex-edit/smooth/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                vertices: _float32ToBase64(blenderVerts),
                faces: _uint32ToBase64(facesArr),
                selected: selected,
                iterations: 3,
                factor: 0.3,
            })
        });
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        const updatedBlender = base64ToFloat32(data.vertices);
        const updatedThree = new Float32Array(updatedBlender.length);
        blenderToThreeCoords(updatedBlender);
        // Apply only selected vertices back
        const overlayPos = vePointsOverlay.geometry.getAttribute('position');
        for (const idx of selected) {
            const x = updatedBlender[idx * 3];
            const y = updatedBlender[idx * 3 + 1];
            const z = updatedBlender[idx * 3 + 2];
            meshPos.setXYZ(idx, x, y, z);
            overlayPos.setXYZ(idx, x, y, z);
        }
        meshPos.needsUpdate = true;
        overlayPos.needsUpdate = true;
        veTargetMesh.geometry.computeVertexNormals();
        veTargetMesh.geometry.computeBoundingSphere();
    } catch (err) {
        console.error('Smooth failed:', err);
    }
    _veUpdateGizmo();
    _veUpdateSelectionInfo();
}

async function _vePushOutside() {
    if (!veActive || !veTargetMesh || veSelectedIndices.size === 0) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const posArr = new Float32Array(meshPos.array);
    const blenderVerts = _threeToBlenderCoords(posArr);
    const selected = Array.from(veSelectedIndices);

    const bodyQs = _buildBodyQueryString();
    const statusEl = document.getElementById('ve-selection-info');
    if (statusEl) statusEl.textContent = 'Pushing outside...';

    try {
        const resp = await fetch(`/api/character/vertex-edit/push-outside/?${bodyQs}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                vertices: _float32ToBase64(blenderVerts),
                selected: selected,
                min_dist: 0.006,
            })
        });
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        const updatedBlender = base64ToFloat32(data.vertices);
        blenderToThreeCoords(updatedBlender);
        const overlayPos = vePointsOverlay.geometry.getAttribute('position');
        for (const idx of selected) {
            const x = updatedBlender[idx * 3];
            const y = updatedBlender[idx * 3 + 1];
            const z = updatedBlender[idx * 3 + 2];
            meshPos.setXYZ(idx, x, y, z);
            overlayPos.setXYZ(idx, x, y, z);
        }
        meshPos.needsUpdate = true;
        overlayPos.needsUpdate = true;
        veTargetMesh.geometry.computeVertexNormals();
        veTargetMesh.geometry.computeBoundingSphere();
    } catch (err) {
        console.error('Push outside failed:', err);
    }
    _veUpdateGizmo();
    _veUpdateSelectionInfo();
}

function _veReset() {
    if (!veActive || !veTargetMesh || !veOrigPositions) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const overlayPos = vePointsOverlay.geometry.getAttribute('position');
    const indices = veSelectedIndices.size > 0 ? veSelectedIndices : null;

    if (indices) {
        for (const idx of indices) {
            const x = veOrigPositions[idx * 3];
            const y = veOrigPositions[idx * 3 + 1];
            const z = veOrigPositions[idx * 3 + 2];
            meshPos.setXYZ(idx, x, y, z);
            overlayPos.setXYZ(idx, x, y, z);
        }
    } else {
        // Reset all
        meshPos.array.set(veOrigPositions);
        overlayPos.array.set(veOrigPositions);
    }
    meshPos.needsUpdate = true;
    overlayPos.needsUpdate = true;
    veTargetMesh.geometry.computeVertexNormals();
    veTargetMesh.geometry.computeBoundingSphere();
    _veUpdateGizmo();
    _veUpdatePosInputs();
}

// --- Coordinate transforms ---
function peWorldToCanvas(wx, wy) { return [pePan.x + wx * peZoom, pePan.y - wy * peZoom]; }
function peCanvasToWorld(cx, cy) { return [(cx - pePan.x) / peZoom, (pePan.y - cy) / peZoom]; }

// --- Canvas rendering ---
function peRender() {
    const canvas = document.getElementById('pe-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Grid
    ctx.strokeStyle = '#333'; ctx.lineWidth = 0.5;
    const step = peZoom;  // 1cm grid
    const ox = pePan.x % step, oy = pePan.y % step;
    for (let x = ox; x < W; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy; y < H; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    // Major grid (10cm)
    ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
    const step10 = peZoom * 10;
    const ox10 = pePan.x % step10, oy10 = pePan.y % step10;
    for (let x = ox10; x < W; x += step10) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy10; y < H; y += step10) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // Origin crosshair
    const [zx, zy] = peWorldToCanvas(0, 0);
    ctx.strokeStyle = '#666'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(zx - 8, zy); ctx.lineTo(zx + 8, zy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(zx, zy - 8); ctx.lineTo(zx, zy + 8); ctx.stroke();

    // Draw panels
    const panelNames = Object.keys(pePattern.panels);
    panelNames.forEach((name, pi) => {
        const panel = pePattern.panels[name];
        const color = PE_COLORS[pi % PE_COLORS.length];
        const isActive = (name === peActivePanel);

        // Edges
        panel.edges.forEach((edge, ei) => {
            const p0 = peWorldToCanvas(...panel.vertices[edge.endpoints[0]]);
            const p1 = peWorldToCanvas(...panel.vertices[edge.endpoints[1]]);
            ctx.strokeStyle = (isActive && peSelectedEdge && peSelectedEdge.panel === name && peSelectedEdge.index === ei)
                ? '#fff' : color;
            ctx.lineWidth = isActive ? 2.5 : 1.5;
            ctx.beginPath();
            if (edge.curvature) {
                const cp = peWorldToCanvas(...edge.curvature);
                ctx.moveTo(p0[0], p0[1]);
                ctx.quadraticCurveTo(cp[0], cp[1], p1[0], p1[1]);
            } else {
                ctx.moveTo(p0[0], p0[1]);
                ctx.lineTo(p1[0], p1[1]);
            }
            ctx.stroke();
        });

        // Vertices
        panel.vertices.forEach((v, vi) => {
            const [cx, cy] = peWorldToCanvas(v[0], v[1]);
            const isSel = isActive && peSelectedVertex && peSelectedVertex.panel === name && peSelectedVertex.index === vi;
            ctx.fillStyle = isSel ? '#fff' : color;
            ctx.beginPath();
            ctx.arc(cx, cy, isSel ? 5 : 3.5, 0, Math.PI * 2);
            ctx.fill();
        });

        // Control points for curvature
        panel.edges.forEach((edge, ei) => {
            if (!edge.curvature) return;
            const cp = peWorldToCanvas(...edge.curvature);
            ctx.fillStyle = '#888';
            ctx.beginPath();
            ctx.arc(cp[0], cp[1], 3, 0, Math.PI * 2);
            ctx.fill();
        });
    });

    // Stitch indicators
    pePattern.stitches.forEach((st, si) => {
        const pA = pePattern.panels[st.panelA];
        const pB = pePattern.panels[st.panelB];
        if (!pA || !pB) return;
        const eA = pA.edges[st.edgeA];
        const eB = pB.edges[st.edgeB];
        if (!eA || !eB) return;
        const midA = _peMidpoint(pA, eA);
        const midB = _peMidpoint(pB, eB);
        const cA = peWorldToCanvas(...midA);
        const cB = peWorldToCanvas(...midB);
        ctx.strokeStyle = '#f1c40f';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 3]);
        ctx.beginPath(); ctx.moveTo(cA[0], cA[1]); ctx.lineTo(cB[0], cB[1]); ctx.stroke();
        ctx.setLineDash([]);
    });

    // Status
    const statusEl = document.getElementById('pe-status');
    if (statusEl) {
        const [wx, wy] = peCanvasToWorld(peLastMouse.x, peLastMouse.y);
        statusEl.textContent = `${wx.toFixed(1)}, ${wy.toFixed(1)} cm    ${Math.round(peZoom / 2 * 100)}%`;
    }
}

let peLastMouse = {x: 0, y: 0};

function _peMidpoint(panel, edge) {
    const v0 = panel.vertices[edge.endpoints[0]];
    const v1 = panel.vertices[edge.endpoints[1]];
    return [(v0[0] + v1[0]) / 2, (v0[1] + v1[1]) / 2];
}

// --- Hit testing ---
function _peHitVertex(cx, cy, threshold) {
    const thr = threshold || 8;
    for (const name of Object.keys(pePattern.panels)) {
        const panel = pePattern.panels[name];
        for (let i = 0; i < panel.vertices.length; i++) {
            const [vx, vy] = peWorldToCanvas(...panel.vertices[i]);
            if (Math.hypot(cx - vx, cy - vy) < thr) return {panel: name, index: i};
        }
    }
    return null;
}

function _peHitEdge(cx, cy, threshold) {
    const thr = threshold || 6;
    for (const name of Object.keys(pePattern.panels)) {
        const panel = pePattern.panels[name];
        for (let i = 0; i < panel.edges.length; i++) {
            const edge = panel.edges[i];
            const p0 = peWorldToCanvas(...panel.vertices[edge.endpoints[0]]);
            const p1 = peWorldToCanvas(...panel.vertices[edge.endpoints[1]]);
            const dist = _pePointToSegDist(cx, cy, p0[0], p0[1], p1[0], p1[1]);
            if (dist < thr) return {panel: name, index: i};
        }
    }
    return null;
}

function _pePointToSegDist(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1, dy = y2 - y1;
    const lenSq = dx * dx + dy * dy;
    if (lenSq < 1e-6) return Math.hypot(px - x1, py - y1);
    let t = ((px - x1) * dx + (py - y1) * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
}

function _peHitControlPoint(cx, cy, threshold) {
    const thr = threshold || 8;
    for (const name of Object.keys(pePattern.panels)) {
        const panel = pePattern.panels[name];
        for (let i = 0; i < panel.edges.length; i++) {
            const edge = panel.edges[i];
            if (!edge.curvature) continue;
            const cp = peWorldToCanvas(...edge.curvature);
            if (Math.hypot(cx - cp[0], cy - cp[1]) < thr) return {panel: name, edgeIndex: i};
        }
    }
    return null;
}

// --- Mouse/Input handling ---
function _peInitCanvas() {
    const canvas = document.getElementById('pe-canvas');
    if (!canvas) return;

    canvas.addEventListener('mousedown', (e) => {
        const rect = canvas.getBoundingClientRect();
        const cx = e.offsetX, cy = e.offsetY;

        // Pan: middle mouse or ctrl+left
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) {
            pePanning = true;
            pePanStart = {x: e.clientX, y: e.clientY, px: pePan.x, py: pePan.y};
            e.preventDefault();
            return;
        }

        if (e.button !== 0) return;

        if (peMode === 'select') {
            // Check control point first
            const cpHit = _peHitControlPoint(cx, cy);
            if (cpHit) {
                peDragging = {type: 'cp', panel: cpHit.panel, edgeIndex: cpHit.edgeIndex};
                return;
            }
            const vHit = _peHitVertex(cx, cy);
            if (vHit) {
                peSelectedVertex = vHit;
                peSelectedEdge = null;
                peActivePanel = vHit.panel;
                peDragging = {type: 'vertex', panel: vHit.panel, index: vHit.index};
                peRender();
                peUpdatePanelList();
                return;
            }
            const eHit = _peHitEdge(cx, cy);
            if (eHit) {
                peSelectedEdge = eHit;
                peSelectedVertex = null;
                peActivePanel = eHit.panel;
                peRender();
                peUpdatePanelList();
                return;
            }
            peSelectedVertex = null;
            peSelectedEdge = null;
            peRender();
        } else if (peMode === 'draw') {
            if (!peActivePanel || !pePattern.panels[peActivePanel]) return;
            const panel = pePattern.panels[peActivePanel];
            const [wx, wy] = peCanvasToWorld(cx, cy);

            // Check if clicking near first vertex to close
            if (panel.vertices.length >= 3) {
                const [fx, fy] = peWorldToCanvas(...panel.vertices[0]);
                if (Math.hypot(cx - fx, cy - fy) < 10) {
                    // Close the panel
                    panel.edges.push({endpoints: [panel.vertices.length - 1, 0], curvature: null});
                    panel.closed = true;
                    peMode = 'select';
                    _peSetModeButtons();
                    peRender();
                    peUpdatePanelList();
                    return;
                }
            }

            const vi = panel.vertices.length;
            panel.vertices.push([wx, wy]);
            if (vi > 0) {
                panel.edges.push({endpoints: [vi - 1, vi], curvature: null});
            }
            peRender();
        } else if (peMode === 'stitch') {
            const eHit = _peHitEdge(cx, cy);
            if (!eHit) return;
            if (!peStitchFirst) {
                peStitchFirst = eHit;
                peSelectedEdge = eHit;
                peActivePanel = eHit.panel;
                peRender();
            } else {
                // Second edge — create stitch (must be different panels)
                if (eHit.panel !== peStitchFirst.panel) {
                    pePattern.stitches.push({
                        panelA: peStitchFirst.panel, edgeA: peStitchFirst.index,
                        panelB: eHit.panel, edgeB: eHit.index,
                    });
                    peUpdateStitchList();
                }
                peStitchFirst = null;
                peSelectedEdge = null;
                peRender();
            }
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        const cx = e.offsetX, cy = e.offsetY;
        peLastMouse = {x: cx, y: cy};

        if (pePanning && pePanStart) {
            pePan.x = pePanStart.px + (e.clientX - pePanStart.x);
            pePan.y = pePanStart.py + (e.clientY - pePanStart.y);
            peRender();
            return;
        }

        if (peDragging) {
            const [wx, wy] = peCanvasToWorld(cx, cy);
            if (peDragging.type === 'vertex') {
                pePattern.panels[peDragging.panel].vertices[peDragging.index] = [wx, wy];
            } else if (peDragging.type === 'cp') {
                pePattern.panels[peDragging.panel].edges[peDragging.edgeIndex].curvature = [wx, wy];
            }
            peRender();
        }

        // Update status
        const statusEl = document.getElementById('pe-status');
        if (statusEl) {
            const [wx, wy] = peCanvasToWorld(cx, cy);
            statusEl.textContent = `${wx.toFixed(1)}, ${wy.toFixed(1)} cm    ${Math.round(peZoom / 2 * 100)}%`;
        }
    });

    canvas.addEventListener('mouseup', () => {
        peDragging = null;
        pePanning = false;
        pePanStart = null;
    });

    canvas.addEventListener('mouseleave', () => {
        peDragging = null;
        pePanning = false;
        pePanStart = null;
    });

    canvas.addEventListener('dblclick', (e) => {
        if (peMode !== 'select') return;
        const cx = e.offsetX, cy = e.offsetY;
        const eHit = _peHitEdge(cx, cy);
        if (eHit) {
            const edge = pePattern.panels[eHit.panel].edges[eHit.index];
            if (edge.curvature) {
                edge.curvature = null;  // Remove curvature
            } else {
                // Add curvature control point at edge midpoint
                const panel = pePattern.panels[eHit.panel];
                const v0 = panel.vertices[edge.endpoints[0]];
                const v1 = panel.vertices[edge.endpoints[1]];
                const mx = (v0[0] + v1[0]) / 2, my = (v0[1] + v1[1]) / 2;
                // Offset perpendicular
                const dx = v1[0] - v0[0], dy = v1[1] - v0[1];
                const len = Math.hypot(dx, dy) || 1;
                edge.curvature = [mx + (-dy / len) * 5, my + (dx / len) * 5];
            }
            peRender();
        }
    });

    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const cx = e.offsetX, cy = e.offsetY;
        const [wx, wy] = peCanvasToWorld(cx, cy);
        const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
        peZoom = Math.max(0.5, Math.min(20, peZoom * factor));
        // Adjust pan so world point under cursor stays fixed
        pePan.x = cx - wx * peZoom;
        pePan.y = cy + wy * peZoom;
        peRender();
    }, {passive: false});

    canvas.addEventListener('contextmenu', e => e.preventDefault());
}

const PE_REGION_PRESETS = {
    custom:    {z_min: 60, z_max: 140, arms: false, grow: 2, looseness: 30},
    top:       {z_min: 80, z_max: 155, arms: true,  grow: 2, looseness: 30},
    pants:     {z_min: 0,  z_max: 105, arms: false, grow: 2, looseness: 30},
    skirt:     {z_min: 55, z_max: 100, arms: false, grow: 3, looseness: 40},
    full:      {z_min: 0,  z_max: 155, arms: true,  grow: 2, looseness: 30},
    underwear: {z_min: 55, z_max: 100, arms: false, grow: 1, looseness: 20},
    shoes:     {z_min: 0,  z_max: 15,  arms: false, grow: 2, looseness: 20},
};

function _peSetRegionMode(active) {
    const patternControls = document.getElementById('pe-pattern-controls');
    const regionControls = document.getElementById('pe-region-controls');
    const wrapSection = document.getElementById('pe-wrap-section');

    if (active) {
        if (patternControls) patternControls.style.display = 'none';
        if (wrapSection) wrapSection.style.display = 'none';
        if (regionControls) regionControls.style.display = '';
    } else {
        if (patternControls) patternControls.style.display = '';
        if (wrapSection) wrapSection.style.display = '';
        if (regionControls) regionControls.style.display = 'none';
    }
}

function _peSetModeButtons() {
    document.querySelectorAll('#pe-mode-btns .btn-toggle').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === peMode);
    });
    // Exit vertex edit when switching away
    if (peMode !== 'edit' && veActive) veExitEditMode();
    // Enter/exit modes
    if (peMode === 'edit') {
        veEnterEditMode();
    } else {
        _peSetRegionMode(peMode === 'region');
    }
}

// --- Panel/Stitch list ---
function peUpdatePanelList() {
    const list = document.getElementById('pe-panel-list');
    if (!list) return;
    const names = Object.keys(pePattern.panels);
    const PLACEMENT_BADGES = {flat:'',front:'[F]',back:'[B]',left:'[L]',right:'[R]',sleeve_L:'[SL]',sleeve_R:'[SR]'};
    list.innerHTML = names.map((name, i) => {
        const color = PE_COLORS[i % PE_COLORS.length];
        const active = name === peActivePanel;
        const p = pePattern.panels[name];
        const nv = p.vertices.length;
        const closed = p.closed ? 'closed' : 'open';
        const badge = PLACEMENT_BADGES[p.placement || 'flat'] || '';
        return `<div class="pe-panel-item${active ? ' active' : ''}" data-name="${name}" style="cursor:pointer;padding:3px 6px;border-left:3px solid ${color};margin-bottom:2px;background:${active ? 'var(--bg-highlight)' : 'transparent'};border-radius:2px;font-size:0.8rem;">
            <span style="color:${color};">&#9679;</span> ${name} ${badge ? `<span style="color:#f39c12;font-size:0.7rem;">${badge}</span> ` : ''}<span style="color:var(--text-muted);font-size:0.72rem;">(${nv}v, ${closed})</span>
        </div>`;
    }).join('');
    list.querySelectorAll('.pe-panel-item').forEach(el => {
        el.addEventListener('click', () => {
            peActivePanel = el.dataset.name;
            peSelectedVertex = null;
            peSelectedEdge = null;
            peUpdatePanelList();
            _peSyncPlacementDropdown();
            peRender();
        });
    });
}

function peUpdateStitchList() {
    const list = document.getElementById('pe-stitch-list');
    const countEl = document.getElementById('pe-stitch-count');
    if (!list) return;
    if (countEl) countEl.textContent = `(${pePattern.stitches.length})`;
    list.innerHTML = pePattern.stitches.map((st, i) =>
        `<div style="font-size:0.78rem;padding:2px 4px;color:var(--text-muted);">${st.panelA}.e${st.edgeA} ↔ ${st.panelB}.e${st.edgeB}
            <span class="pe-stitch-del" data-idx="${i}" style="cursor:pointer;color:#e74c3c;margin-left:4px;" title="Remove">✕</span>
        </div>`
    ).join('');
    list.querySelectorAll('.pe-stitch-del').forEach(el => {
        el.addEventListener('click', () => {
            pePattern.stitches.splice(parseInt(el.dataset.idx), 1);
            peUpdateStitchList();
            peRender();
        });
    });
}

function _peSyncPlacementDropdown() {
    const dd = document.getElementById('pe-placement');
    if (!dd || !peActivePanel) return;
    const p = pePattern.panels[peActivePanel];
    dd.value = (p && p.placement) || 'flat';
}

// --- Region Generate ---
async function peRegionGenerate() {
    const genBtn = document.getElementById('pe-generate');
    if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status');
    if (statusEl) statusEl.textContent = 'Generating region...';

    ensureSkinned();

    const bodyQs = _buildBodyQueryString();
    const zMin = (_sliderVal('pe-region-zmin') / 100).toFixed(3);
    const zMax = (_sliderVal('pe-region-zmax') / 100).toFixed(3);
    const arms = document.getElementById('pe-region-arms')?.checked ? '1' : '0';
    const grow = _sliderVal('pe-region-grow');
    const looseness = (_sliderVal('pe-region-looseness') / 100).toFixed(3);
    const category = document.getElementById('pe-region-category')?.value || 'custom';

    const regionQs = `z_min=${zMin}&z_max=${zMax}&include_arms=${arms}&grow=${grow}&looseness=${looseness}&category=${category}`;

    try {
        const resp = await fetch(`/api/character/pattern/region/generate/?${bodyQs}&${regionQs}`);
        const data = await resp.json();
        if (data.error) {
            if (statusEl) statusEl.textContent = `Error: ${data.error}`;
            if (genBtn) genBtn.disabled = false;
            return;
        }

        removeClothRegion(pePreviewKey);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const colorPicker = document.getElementById('pe-color');
        const matColor = colorPicker ? new THREE.Color(colorPicker.value) : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (_sliderVal('pe-roughness') / 100);
        const metalness = (_sliderVal('pe-metalness') / 100);

        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness, metalness,
            side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
        });

        let mesh;
        if (isSkinned && rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        clothMeshes[pePreviewKey] = mesh;
        clothParams[pePreviewKey] = {params: {}, color: '#' + mesh.material.color.getHexString()};
        scene.add(mesh);
        updateEquippedList();

        if (statusEl) statusEl.textContent = `Region: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) {
        if (statusEl) statusEl.textContent = `Error: ${e.message}`;
    }
    if (genBtn) genBtn.disabled = false;
}

// --- Generate 3D + Save ---
async function peGenerate3D() {
    const genBtn = document.getElementById('pe-generate');
    if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status');
    if (statusEl) statusEl.textContent = 'Generating...';

    ensureSkinned();

    const bodyQs = _buildBodyQueryString();
    try {
        const wrapCb = document.getElementById('pe-wrap');
        const wrap = wrapCb ? wrapCb.checked : false;
        const wrapOffset = (_sliderVal('pe-wrap-offset') || 6) / 1000;  // mm → m
        const wrapStiffness = (_sliderVal('pe-wrap-stiffness') ?? 50) / 100;

        const resp = await fetch(`/api/character/pattern/generate/?${bodyQs}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pattern: pePattern, wrap, offset: wrapOffset, stiffness: wrapStiffness}),
        });
        const data = await resp.json();
        if (data.error) {
            if (statusEl) statusEl.textContent = `Error: ${data.error}`;
            if (genBtn) genBtn.disabled = false;
            return;
        }

        // Remove previous preview
        removeClothRegion(pePreviewKey);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const colorPicker = document.getElementById('pe-color');
        const matColor = colorPicker ? new THREE.Color(colorPicker.value) : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (_sliderVal('pe-roughness') / 100);
        const metalness = (_sliderVal('pe-metalness') / 100);

        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness, metalness,
            side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
        });

        let mesh;
        if (isSkinned && rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        clothMeshes[pePreviewKey] = mesh;
        clothParams[pePreviewKey] = {params: {}, color: '#' + mesh.material.color.getHexString()};
        scene.add(mesh);
        updateEquippedList();

        if (statusEl) statusEl.textContent = `Generated: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) {
        if (statusEl) statusEl.textContent = `Error: ${e.message}`;
    }
    if (genBtn) genBtn.disabled = false;
}

async function peSaveToLibrary() {
    const name = document.getElementById('pe-save-name')?.value?.trim();
    const category = document.getElementById('pe-save-category')?.value || 'custom';
    const statusEl = document.getElementById('pe-save-status');

    if (!name) { if (statusEl) statusEl.textContent = 'Name is required'; return; }

    if (statusEl) statusEl.textContent = 'Saving...';

    const colorPicker = document.getElementById('pe-color');
    const colorHex = colorPicker ? colorPicker.value : '#404870';
    const cr = parseInt(colorHex.slice(1, 3), 16) / 255;
    const cg = parseInt(colorHex.slice(3, 5), 16) / 255;
    const cb = parseInt(colorHex.slice(5, 7), 16) / 255;

    const bodyQs = _buildBodyQueryString();
    try {
        const resp = await fetch(`/api/character/pattern/save/?${bodyQs}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                pattern: pePattern,
                name, category,
                color: [cr, cg, cb],
                roughness: _sliderVal('pe-roughness') / 100,
                metalness: _sliderVal('pe-metalness') / 100,
                wrap: document.getElementById('pe-wrap')?.checked || false,
                offset: (_sliderVal('pe-wrap-offset') || 6) / 1000,
                stiffness: (_sliderVal('pe-wrap-stiffness') ?? 50) / 100,
            }),
        });
        const data = await resp.json();
        if (data.ok) {
            if (statusEl) statusEl.textContent = `Saved: ${data.garment_id}`;
        } else {
            if (statusEl) statusEl.textContent = `Error: ${data.error || 'Unknown'}`;
        }
    } catch (e) {
        if (statusEl) statusEl.textContent = `Error: ${e.message}`;
    }
}

// --- Load pattern from garment library ---
async function peLoadFromGarment(garmentId) {
    try {
        const resp = await fetch(`/api/character/pattern/specification/?garment_id=${encodeURIComponent(garmentId)}`);
        const data = await resp.json();
        if (!data.ok || !data.pattern) {
            console.warn('No specification found for', garmentId, data.error);
            return false;
        }
        // Load pattern data into editor
        pePattern = data.pattern;
        // Ensure stitches array exists
        if (!pePattern.stitches) pePattern.stitches = [];

        // Set active panel to first
        const names = Object.keys(pePattern.panels || {});
        peActivePanel = names.length > 0 ? names[0] : null;
        peSelectedVertex = null;
        peSelectedEdge = null;
        peStitchFirst = null;
        peMode = 'select';
        _peSetModeButtons();

        // Auto-fit zoom/pan to show all vertices
        _peAutoFit();

        peUpdatePanelList();
        peUpdateStitchList();
        peRender();

        // Switch to Pattern tab
        const tabBtn = document.querySelector('.panel-tab[data-tab="tab-creator"]');
        if (tabBtn) tabBtn.click();

        // Pre-fill save name from garment id
        const nameEl = document.getElementById('pe-save-name');
        if (nameEl) {
            const parts = garmentId.split('/');
            nameEl.value = parts[parts.length - 1];
        }
        const catEl = document.getElementById('pe-save-category');
        if (catEl) {
            const parts = garmentId.split('/');
            if (parts.length > 1) {
                const cat = parts[0];
                for (const opt of catEl.options) {
                    if (opt.value === cat) { catEl.value = cat; break; }
                }
            }
        }

        console.log(`Pattern loaded from ${garmentId}: ${names.length} panels`);
        return true;
    } catch (e) {
        console.error('Failed to load pattern:', e);
        return false;
    }
}

function _peAutoFit() {
    const canvas = document.getElementById('pe-canvas');
    if (!canvas) return;
    const W = canvas.width, H = canvas.height;

    // Collect all vertices
    const allVerts = [];
    for (const panel of Object.values(pePattern.panels || {})) {
        for (const v of (panel.vertices || [])) {
            allVerts.push(v);
        }
    }
    if (allVerts.length === 0) { pePan = {x: W/2, y: H/2}; peZoom = 2.0; return; }

    const xs = allVerts.map(v => v[0]), ys = allVerts.map(v => v[1]);
    const xMin = Math.min(...xs), xMax = Math.max(...xs);
    const yMin = Math.min(...ys), yMax = Math.max(...ys);
    const pw = xMax - xMin || 20, ph = yMax - yMin || 20;

    // Fit with 15% margin
    const margin = 0.15;
    const zoomX = W * (1 - 2 * margin) / pw;
    const zoomY = H * (1 - 2 * margin) / ph;
    peZoom = Math.min(zoomX, zoomY);
    peZoom = Math.max(0.5, Math.min(20, peZoom));

    // Center on pattern
    const cx = (xMin + xMax) / 2;
    const cy = (yMin + yMax) / 2;
    pePan.x = W / 2 - cx * peZoom;
    pePan.y = H / 2 + cy * peZoom;
}

// --- Init ---
function initPatternEditor() {
    const canvas = document.getElementById('pe-canvas');
    if (!canvas) return;

    _peInitCanvas();

    // Mode buttons
    document.querySelectorAll('#pe-mode-btns .btn-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            peMode = btn.dataset.mode;
            peStitchFirst = null;
            _peSetModeButtons();
        });
    });

    // Add panel
    document.getElementById('pe-add-panel')?.addEventListener('click', () => {
        const names = Object.keys(pePattern.panels);
        const defaultName = `Panel${names.length + 1}`;
        const name = prompt('Panel name:', defaultName);
        if (!name || !name.trim()) return;
        const trimmed = name.trim();
        if (pePattern.panels[trimmed]) { alert('Panel already exists'); return; }
        pePattern.panels[trimmed] = {vertices: [], edges: [], closed: false};
        peActivePanel = trimmed;
        peMode = 'draw';
        _peSetModeButtons();
        peUpdatePanelList();
        peRender();
    });

    // Delete panel
    document.getElementById('pe-del-panel')?.addEventListener('click', () => {
        if (!peActivePanel) return;
        // Remove stitches referencing this panel
        pePattern.stitches = pePattern.stitches.filter(
            s => s.panelA !== peActivePanel && s.panelB !== peActivePanel);
        delete pePattern.panels[peActivePanel];
        const names = Object.keys(pePattern.panels);
        peActivePanel = names.length > 0 ? names[0] : null;
        peSelectedVertex = null;
        peSelectedEdge = null;
        peUpdatePanelList();
        peUpdateStitchList();
        peRender();
    });

    // Placement dropdown
    document.getElementById('pe-placement')?.addEventListener('change', (e) => {
        if (peActivePanel && pePattern.panels[peActivePanel]) {
            pePattern.panels[peActivePanel].placement = e.target.value;
            peUpdatePanelList();
        }
    });

    // Wrap checkbox → show/hide offset+stiffness sliders
    document.getElementById('pe-wrap')?.addEventListener('change', (e) => {
        const sliders = document.getElementById('pe-wrap-sliders');
        if (sliders) sliders.style.display = e.target.checked ? '' : 'none';
    });
    _bindSlider('pe-wrap-offset', 'pe-wrap-offset-val', v => v);
    _bindSlider('pe-wrap-stiffness', 'pe-wrap-stiffness-val', v => (v / 100).toFixed(2));

    // Region controls
    _bindSlider('pe-region-zmin', 'pe-region-zmin-val', v => (v / 100).toFixed(2));
    _bindSlider('pe-region-zmax', 'pe-region-zmax-val', v => (v / 100).toFixed(2));
    _bindSlider('pe-region-grow', 'pe-region-grow-val', v => v);
    _bindSlider('pe-region-looseness', 'pe-region-looseness-val', v => (v / 100).toFixed(2));

    // Region category preset auto-fill
    document.getElementById('pe-region-category')?.addEventListener('change', (e) => {
        const preset = PE_REGION_PRESETS[e.target.value];
        if (!preset) return;
        const setSlider = (id, val) => {
            const el = document.getElementById(id);
            if (el) { el.value = val; el.dispatchEvent(new Event('input')); }
        };
        setSlider('pe-region-zmin', preset.z_min);
        setSlider('pe-region-zmax', preset.z_max);
        setSlider('pe-region-grow', preset.grow);
        setSlider('pe-region-looseness', preset.looseness);
        const armsEl = document.getElementById('pe-region-arms');
        if (armsEl) armsEl.checked = preset.arms;
        // Auto-regenerate when preset changes
        if (peMode === 'region') peRegionGenerate();
    });

    // Auto-regenerate on region slider release (change event)
    ['pe-region-zmin', 'pe-region-zmax', 'pe-region-grow', 'pe-region-looseness'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', () => {
            if (peMode === 'region') peRegionGenerate();
        });
    });
    document.getElementById('pe-region-arms')?.addEventListener('change', () => {
        if (peMode === 'region') peRegionGenerate();
    });

    // Material sliders
    _bindSlider('pe-roughness', 'pe-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('pe-metalness', 'pe-metalness-val', v => (v / 100).toFixed(2));

    // Live material update on preview mesh
    ['pe-color', 'pe-roughness', 'pe-metalness'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', () => {
            let mesh = null;
            if (_selectedItem && (_selectedItem.type === 'cloth' || _selectedItem.type === 'garment')) {
                mesh = clothMeshes[_selectedItem.id] || garmentMeshes[_selectedItem.id];
            }
            if (!mesh) mesh = clothMeshes[pePreviewKey];
            if (!mesh) return;
            if (id === 'pe-color') mesh.material.color.set(el.value);
            else if (id === 'pe-roughness') mesh.material.roughness = parseInt(el.value) / 100;
            else if (id === 'pe-metalness') mesh.material.metalness = parseInt(el.value) / 100;
        });
    });

    // Generate 3D — route to region or pattern based on mode
    document.getElementById('pe-generate')?.addEventListener('click', () => {
        if (peMode === 'region') peRegionGenerate();
        else peGenerate3D();
    });

    // Delete preview
    document.getElementById('pe-delete')?.addEventListener('click', () => {
        removeClothRegion(pePreviewKey);
    });

    // Save to library
    document.getElementById('pe-save')?.addEventListener('click', () => peSaveToLibrary());

    // Edit Pattern button (in Garment Fit panel)
    document.getElementById('garment-edit-pattern')?.addEventListener('click', () => {
        if (selectedGarmentId) peLoadFromGarment(selectedGarmentId);
    });

    // --- Vertex Editor sidebar bindings ---
    document.getElementById('ve-select-all')?.addEventListener('click', () => {
        if (!veActive || !vePointsOverlay) return;
        const count = vePointsOverlay.geometry.getAttribute('position').count;
        for (let i = 0; i < count; i++) veSelectedIndices.add(i);
        _veUpdateAllColors();
        _veUpdateGizmo();
        _veUpdateSelectionInfo();
    });
    document.getElementById('ve-deselect-all')?.addEventListener('click', () => {
        if (!veActive) return;
        veSelectedIndices.clear();
        _veUpdateAllColors();
        _veUpdateGizmo();
        _veUpdateSelectionInfo();
    });
    document.getElementById('ve-smooth')?.addEventListener('click', () => _veSmooth());
    document.getElementById('ve-push-outside')?.addEventListener('click', () => _vePushOutside());
    document.getElementById('ve-reset')?.addEventListener('click', () => _veReset());

    // Point size slider
    const veSizeSlider = document.getElementById('ve-point-size');
    const veSizeVal = document.getElementById('ve-point-size-val');
    if (veSizeSlider) {
        veSizeSlider.addEventListener('input', () => {
            const sz = parseInt(veSizeSlider.value);
            if (veSizeVal) veSizeVal.textContent = sz;
            if (vePointsOverlay) vePointsOverlay.material.size = sz;
        });
    }

    // Position inputs
    ['ve-pos-x', 've-pos-y', 've-pos-z'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', () => {
            if (!veActive || !veTargetMesh || veSelectedIndices.size === 0) return;
            const posAttr = veTargetMesh.geometry.getAttribute('position');
            let cx = 0, cy = 0, cz = 0;
            for (const idx of veSelectedIndices) {
                cx += posAttr.getX(idx);
                cy += posAttr.getY(idx);
                cz += posAttr.getZ(idx);
            }
            const n = veSelectedIndices.size;
            const newX = parseFloat(document.getElementById('ve-pos-x')?.value || 0);
            const newY = parseFloat(document.getElementById('ve-pos-y')?.value || 0);
            const newZ = parseFloat(document.getElementById('ve-pos-z')?.value || 0);
            _veMoveSelectedByDelta(newX - cx / n, newY - cy / n, newZ - cz / n);
            _veUpdateGizmo();
        });
    });

    peRender();
    console.log('Pattern Editor initialized');
}


// =========================================================================
// Hair
// =========================================================================
async function loadHairUI() {
    try {
        const resp = await fetch('/api/character/hairstyles/');
        const data = await resp.json();
        const select = document.getElementById('hair-style-select');
        const colorSelect = document.getElementById('hair-color-select');
        if (!select) return;

        hairColorData = data.colors || {};

        // Populate hairstyle dropdown
        (data.hairstyles || []).forEach(h => {
            const opt = document.createElement('option');
            opt.value = h.url;
            opt.textContent = h.label;
            opt.dataset.name = h.name;
            select.appendChild(opt);
        });

        // Populate hair color dropdown
        if (colorSelect) {
            Object.keys(hairColorData).forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                colorSelect.appendChild(opt);
            });
        }

        select.addEventListener('change', () => {
            if (!select.value) {
                removeHair();
                return;
            }
            loadHair(select.value);
        });

        if (colorSelect) {
            colorSelect.addEventListener('change', () => {
                applyHairColor(colorSelect.value);
            });
        }
    } catch (e) {
        console.warn('Hair UI not available:', e);
    }
}

function loadHair(url) {
    removeHair();
    ensureSkinned();

    gltfLoader.load(url, (gltf) => {
        let hairGroup = gltf.scene;

        // Convert hair meshes to SkinnedMesh bound to head bone
        if (isSkinned && rigifySkeleton && skinWeightData) {
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
        }

        hairMesh = hairGroup;
        // Apply current hair color
        const colorSelect = document.getElementById('hair-color-select');
        if (colorSelect && colorSelect.value) {
            applyHairColorToObject(hairMesh, colorSelect.value);
        }
        scene.add(hairMesh);
        console.log('Hair loaded:', url, 'skinned=' + (isSkinned && rigifySkeleton ? 'yes' : 'no'));
        updateEquippedList();
    }, undefined, (err) => {
        console.error('Failed to load hair:', err);
    });
}

function _findHeadBoneIndex() {
    if (!skinWeightData) return -1;
    const names = skinWeightData.bone_names;
    for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
        const idx = names.indexOf(tryName);
        if (idx >= 0) return idx;
    }
    return -1;
}

function _skinifyHairGroup(gltfScene, headBoneIdx) {
    // Collect all meshes from the GLB scene
    const meshChildren = [];
    gltfScene.traverse(child => {
        if (child.isMesh) meshChildren.push(child);
    });

    const group = new THREE.Group();
    for (const child of meshChildren) {
        const geo = child.geometry.clone();
        const vCount = geo.attributes.position.count;
        const si = new Float32Array(vCount * 4);
        const sw = new Float32Array(vCount * 4);
        for (let v = 0; v < vCount; v++) {
            si[v * 4] = headBoneIdx;
            sw[v * 4] = 1.0;
        }
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(si, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));

        const skinnedChild = new THREE.SkinnedMesh(geo, child.material);
        // Apply the child's world transform so position is correct
        child.updateWorldMatrix(true, false);
        skinnedChild.applyMatrix4(child.matrixWorld);
        skinnedChild.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
        group.add(skinnedChild);
    }
    return group;
}

function removeHair() {
    if (hairMesh) {
        scene.remove(hairMesh);
        hairMesh.traverse(child => {
            if (child.isMesh) {
                child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(m => m.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            }
        });
        hairMesh = null;
        updateEquippedList();
    }
}

function refitHairToBody() {
    if (!bodyGeometry || initialBodyTop === null) return;
    const hairSelect = document.getElementById('hair-style-select');
    if (!hairSelect || !hairSelect.value) return;
    if (!hairMesh) return;

    const currentTop = _getBodyTop();
    if (currentTop === null || Math.abs(currentTop - initialBodyTop) < 0.001) return;
    const scale = currentTop / initialBodyTop;

    // Reload hair WITHOUT skinning — scale to match morphed body
    const hairUrl = hairSelect.value;
    const colorSelect = document.getElementById('hair-color-select');
    const colorName = colorSelect ? colorSelect.value : '';
    removeHair();

    gltfLoader.load(hairUrl, (gltf) => {
        let hairGroup = gltf.scene;

        // Scale geometry vertices before skinning so bone binding stays correct
        hairGroup.traverse(child => {
            if (child.isMesh) {
                child.geometry.scale(scale, scale, scale);
            }
        });

        // Re-bind to skeleton (same as loadHair)
        if (isSkinned && rigifySkeleton && skinWeightData) {
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
        }

        hairMesh = hairGroup;
        if (colorName) applyHairColorToObject(hairMesh, colorName);
        scene.add(hairMesh);
        updateEquippedList();
        console.log(`[Hair refit] scale=${scale.toFixed(4)} (initial=${initialBodyTop.toFixed(4)}, current=${currentTop.toFixed(4)})`);
    }, undefined, (err) => {
        console.error('[Hair refit] failed to reload:', err);
    });
}

function applyHairColor(colorName) {
    if (hairMesh) applyHairColorToObject(hairMesh, colorName);
}

function applyHairColorToObject(obj, colorName) {
    const rgb = hairColorData[colorName];
    if (!rgb) return;
    const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
    obj.traverse(child => {
        if (child.isMesh && child.material) {
            const mats = Array.isArray(child.material) ? child.material : [child.material];
            mats.forEach(m => { m.color.copy(color); });
        }
    });
}

// =========================================================================
// Garment Fitter
// =========================================================================

let _garmentCatalog = [];  // full catalog from API

async function loadGarmentUI() {
    // --- DOM setup (always runs, independent of API) ---

    // Slider display bindings
    _bindSlider('garment-offset', 'garment-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('garment-stiffness', 'garment-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-min-dist', 'garment-min-dist-val', v => v + ' mm');
    _bindSlider('garment-crotch-floor', 'garment-crotch-floor-val', v => v + ' mm');
    _bindSlider('garment-lift', 'garment-lift-val', v => v + ' mm');
    _bindSlider('garment-crotch-depth', 'garment-crotch-depth-val', v => v + ' mm');
    _bindSlider('garment-roughness', 'garment-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-metalness', 'garment-metalness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-pos-x', 'garment-pos-x-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('garment-pos-y', 'garment-pos-y-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('garment-pos-z', 'garment-pos-z-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('garment-scale-x', 'garment-scale-x-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-scale-y', 'garment-scale-y-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-scale-z', 'garment-scale-z-val', v => (v / 100).toFixed(2));
    for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
        _bindSlider(`garment-region-${rid}`, `garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
    }

    // Live garment adjustment handlers (client-side, no server call)
    // Position/Scale: modify vertex buffer via _applyGarmentState (mesh.position/scale ignored for shared-skeleton SkinnedMesh)
    _garmentLiveSlider('garment-pos-x');
    _garmentLiveSlider('garment-pos-y');
    _garmentLiveSlider('garment-pos-z');
    _garmentLiveSlider('garment-scale-x');
    _garmentLiveSlider('garment-scale-y');
    _garmentLiveSlider('garment-scale-z');
    _garmentLiveSlider('garment-roughness');
    _garmentLiveSlider('garment-metalness');
    for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
        _garmentLiveSlider(`garment-region-${rid}`);
    }

    // Debounced server re-fit for Offset / Stiffness sliders
    _garmentRefitSlider('garment-offset');
    _garmentRefitSlider('garment-stiffness');
    _garmentRefitSlider('garment-min-dist');
    _garmentRefitSlider('garment-crotch-floor');
    _garmentRefitSlider('garment-lift');
    _garmentRefitSlider('garment-crotch-depth');

    // Live color picker
    const garmentColorEl = document.getElementById('garment-color');
    if (garmentColorEl) {
        garmentColorEl.addEventListener('input', () => {
            if (!selectedGarmentId || !garmentMeshes[selectedGarmentId]) return;
            garmentMeshes[selectedGarmentId].material.color.set(garmentColorEl.value);
            _saveGarmentState(selectedGarmentId);
        });
    }

    // Create button
    const createBtn = document.getElementById('garment-create');
    if (createBtn) {
        createBtn.addEventListener('click', () => {
            if (!selectedGarmentId) {
                console.warn('No garment selected');
                return;
            }
            loadGarment(selectedGarmentId);
        });
    }

    // Update button — re-fit on server, preserve client transforms
    const updateBtn = document.getElementById('garment-update');
    if (updateBtn) {
        updateBtn.addEventListener('click', () => {
            if (!selectedGarmentId || !garmentMeshes[selectedGarmentId]) {
                console.warn('No active garment to update');
                return;
            }
            _saveGarmentState(selectedGarmentId);
            loadGarment(selectedGarmentId);
        });
    }

    // Refit all garments — re-fit every equipped garment with current morphs
    const refitAllBtn = document.getElementById('garment-refit-all');
    if (refitAllBtn) {
        refitAllBtn.addEventListener('click', async () => {
            const ids = Object.keys(garmentMeshes);
            if (ids.length === 0) { console.warn('No garments to refit'); return; }
            refitAllBtn.disabled = true;
            refitAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
            for (const gid of ids) {
                _saveGarmentState(gid);
            }
            for (const gid of ids) {
                await loadGarment(gid);
            }
            refitAllBtn.disabled = false;
            refitAllBtn.innerHTML = '<i class="fas fa-sync"></i> Refit';
        });
    }

    // Remove single garment
    const removeBtn = document.getElementById('garment-remove');
    if (removeBtn) {
        removeBtn.addEventListener('click', () => {
            if (selectedGarmentId && garmentMeshes[selectedGarmentId]) {
                removeGarment(selectedGarmentId);
                _updateGarmentAdjustmentsVisibility();
            }
        });
    }

    // Remove all garments
    const removeAllBtn = document.getElementById('garment-remove-all');
    if (removeAllBtn) {
        removeAllBtn.addEventListener('click', () => {
            removeAllGarments();
            _updateGarmentAdjustmentsVisibility();
        });
    }

    // Category filter
    const catSelect = document.getElementById('garment-category');
    if (catSelect) {
        catSelect.addEventListener('change', () => _renderGarmentList());
    }

    // Download panel toggle
    const dlBtn = document.getElementById('garment-download-btn');
    const dlPanel = document.getElementById('garment-download-panel');
    if (dlBtn && dlPanel) {
        dlBtn.addEventListener('click', async () => {
            const isOpen = dlPanel.style.display !== 'none';
            dlPanel.style.display = isOpen ? 'none' : 'block';
            if (!isOpen) await _loadDownloadPacks();
        });
    }

    // Pack download button
    const packDlBtn = document.getElementById('garment-pack-download');
    if (packDlBtn) {
        packDlBtn.addEventListener('click', () => _downloadPack());
    }

    // --- API-dependent catalog loading ---
    try {
        const resp = await fetch('/api/character/garment/library/');
        const data = await resp.json();
        _garmentCatalog = [];

        const listEl = document.getElementById('garment-list');

        // Populate categories
        if (catSelect && data.categories) {
            data.categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                catSelect.appendChild(opt);
            });
        }

        // Flatten catalog
        if (data.garments) {
            for (const cat of Object.keys(data.garments)) {
                for (const g of data.garments[cat]) {
                    _garmentCatalog.push(g);
                }
            }
        }

        _renderGarmentList();
    } catch (e) {
        console.warn('Garment UI not available:', e);
        const listEl = document.getElementById('garment-list');
        if (listEl) listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garment-Library</div>';
    }
}

function _renderGarmentList() {
    const listEl = document.getElementById('garment-list');
    const catSelect = document.getElementById('garment-category');
    if (!listEl) return;

    const filterCat = catSelect ? catSelect.value : '';
    const filtered = filterCat
        ? _garmentCatalog.filter(g => g.category === filterCat)
        : _garmentCatalog;

    if (filtered.length === 0) {
        listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments gefunden</div>';
        return;
    }

    // Group by category
    const byCat = {};
    for (const g of filtered) {
        if (!byCat[g.category]) byCat[g.category] = [];
        byCat[g.category].push(g);
    }

    listEl.innerHTML = '';
    for (const cat of Object.keys(byCat).sort()) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-category open';
        const header = document.createElement('div');
        header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${cat.toUpperCase()} <span class="cat-count">${byCat[cat].length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open'));
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'anim-category-body';
        for (const g of byCat[cat]) {
            const item = document.createElement('div');
            item.className = 'anim-item garment-item';
            if (g.id === selectedGarmentId) item.classList.add('active');
            // Thumbnail + name
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.alt = g.name;
                img.className = 'garment-thumb';
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;';
                item.appendChild(img);
            }
            const nameSpan = document.createElement('span');
            nameSpan.textContent = g.name;
            nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            item.appendChild(nameSpan);
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.dataset.garmentId = g.id;
            item.addEventListener('click', () => {
                selectedGarmentId = g.id;
                // Update selection highlight
                listEl.querySelectorAll('.anim-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');

                // If garment is in scene and has saved state, load that; otherwise use catalog defaults
                const st = garmentState[g.id];
                if (st && garmentMeshes[g.id]) {
                    _setSlider('garment-color', st.color);
                    _setSlider('garment-offset', Math.round(st.offset * 1000), v => (v / 1000).toFixed(3));
                    _setSlider('garment-stiffness', Math.round(st.stiffness * 100), v => (v / 100).toFixed(2));
                    _setSlider('garment-min-dist', st.minDist !== undefined ? st.minDist : 3, v => v + ' mm');
                    _setSlider('garment-crotch-floor', st.crotchFloor !== undefined ? st.crotchFloor : 0, v => v + ' mm');
                    _setSlider('garment-lift', st.lift !== undefined ? st.lift : 0, v => v + ' mm');
                    _setSlider('garment-crotch-depth', st.crotchDepth !== undefined ? st.crotchDepth : 0, v => v + ' mm');
                    _setSlider('garment-roughness', Math.round(st.roughness * 100), v => (v / 100).toFixed(2));
                    _setSlider('garment-metalness', Math.round(st.metalness * 100), v => (v / 100).toFixed(2));
                    _setSlider('garment-pos-x', Math.round(st.posX * 100), v => (v / 100).toFixed(2) + ' m');
                    _setSlider('garment-pos-y', Math.round(st.posY * 100), v => (v / 100).toFixed(2) + ' m');
                    _setSlider('garment-pos-z', Math.round(st.posZ * 100), v => (v / 100).toFixed(2) + ' m');
                    _setSlider('garment-scale-x', Math.round(st.scaleX * 100), v => (v / 100).toFixed(2));
                    _setSlider('garment-scale-y', Math.round(st.scaleY * 100), v => (v / 100).toFixed(2));
                    _setSlider('garment-scale-z', Math.round(st.scaleZ * 100), v => (v / 100).toFixed(2));
                    for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
                        const key = 'region' + rid[0].toUpperCase() + rid.slice(1);
                        _setSlider(`garment-region-${rid}`, Math.round((st[key] || 0) * 100), v => (v / 100).toFixed(2) + ' m');
                    }
                } else {
                    // Catalog defaults
                    const colorPicker = document.getElementById('garment-color');
                    if (colorPicker && g.color) {
                        const hex = '#' + g.color.map(c =>
                            Math.round(c * 255).toString(16).padStart(2, '0')
                        ).join('');
                        colorPicker.value = hex;
                    }
                    const offSlider = document.getElementById('garment-offset');
                    const stiffSlider = document.getElementById('garment-stiffness');
                    if (offSlider && g.offset !== undefined) {
                        offSlider.value = Math.round(g.offset * 1000);
                        const v = document.getElementById('garment-offset-val');
                        if (v) v.textContent = g.offset.toFixed(3);
                    }
                    if (stiffSlider && g.stiffness !== undefined) {
                        stiffSlider.value = Math.round(g.stiffness * 100);
                        const v = document.getElementById('garment-stiffness-val');
                        if (v) v.textContent = g.stiffness.toFixed(2);
                    }
                    // Reset material/position/scale/min-dist/crotch-floor to defaults
                    _setSlider('garment-min-dist', 3, v => v + ' mm');
                    _setSlider('garment-crotch-floor', 0, v => v + ' mm');
                    _setSlider('garment-lift', 0, v => v + ' mm');
                    _setSlider('garment-crotch-depth', 0, v => v + ' mm');
                    _setSlider('garment-roughness', 80, v => (v / 100).toFixed(2));
                    _setSlider('garment-metalness', 0, v => (v / 100).toFixed(2));
                    _setSlider('garment-pos-x', 0, v => (v / 100).toFixed(2) + ' m');
                    _setSlider('garment-pos-y', 0, v => (v / 100).toFixed(2) + ' m');
                    _setSlider('garment-pos-z', 0, v => (v / 100).toFixed(2) + ' m');
                    _setSlider('garment-scale-x', 100, v => (v / 100).toFixed(2));
                    _setSlider('garment-scale-y', 100, v => (v / 100).toFixed(2));
                    _setSlider('garment-scale-z', 100, v => (v / 100).toFixed(2));
                    for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
                        _setSlider(`garment-region-${rid}`, 0, v => (v / 100).toFixed(2) + ' m');
                    }
                }
                _updateGarmentAdjustmentsVisibility();

                // Show/hide "Edit Pattern" button based on source
                const editBtn = document.getElementById('garment-edit-pattern');
                if (editBtn) {
                    editBtn.style.display = (g.source === 'pattern-editor') ? '' : 'none';
                }
            });
            body.appendChild(item);
        }
        catDiv.appendChild(body);
        listEl.appendChild(catDiv);
    }
}

// --- Garment adjustment helpers ---

/** Bind a slider for live garment transforms (client-side only, vertex buffer) */
function _garmentLiveSlider(sliderId) {
    const el = document.getElementById(sliderId);
    if (!el) { console.warn(`[Garment] slider not found: ${sliderId}`); return; }
    el.addEventListener('input', () => {
        if (!selectedGarmentId || !garmentMeshes[selectedGarmentId]) return;
        _saveGarmentState(selectedGarmentId);
        _applyGarmentState(selectedGarmentId);
    });
}

/** Server re-fit on slider release (change event) */
function _garmentRefitSlider(sliderId) {
    const el = document.getElementById(sliderId);
    if (!el) return;
    el.addEventListener('change', () => {
        if (!selectedGarmentId || !garmentMeshes[selectedGarmentId]) return;
        console.log(`[Garment] refit on ${sliderId} change, gid=${selectedGarmentId}`);
        _saveGarmentState(selectedGarmentId);
        loadGarment(selectedGarmentId);
    });
}

/** Set a slider value + update its display label */
function _setSlider(sliderId, value, fmt) {
    const el = document.getElementById(sliderId);
    if (!el) return;
    if (el.type === 'color') {
        el.value = value;
        return;
    }
    el.value = value;
    const valEl = document.getElementById(sliderId + '-val');
    if (valEl && fmt) valEl.textContent = fmt(parseInt(value));
}

/** Save current slider state for a garment */
function _saveGarmentState(gid) {
    const colorPicker = document.getElementById('garment-color');
    garmentState[gid] = {
        posX: _sliderVal('garment-pos-x') / 100,
        posY: _sliderVal('garment-pos-y') / 100,
        posZ: _sliderVal('garment-pos-z') / 100,
        scaleX: _sliderVal('garment-scale-x') / 100,
        scaleY: _sliderVal('garment-scale-y') / 100,
        scaleZ: _sliderVal('garment-scale-z') / 100,
        color: colorPicker ? colorPicker.value : '#4d5980',
        roughness: _sliderVal('garment-roughness') / 100,
        metalness: _sliderVal('garment-metalness') / 100,
        offset: _sliderVal('garment-offset') / 1000,
        stiffness: _sliderVal('garment-stiffness') / 100,
        minDist: _sliderVal('garment-min-dist'),
        crotchFloor: _sliderVal('garment-crotch-floor'),
        lift: _sliderVal('garment-lift'),
        crotchDepth: _sliderVal('garment-crotch-depth'),
        regionTop: _sliderVal('garment-region-top') / 100,
        regionUpper: _sliderVal('garment-region-upper') / 100,
        regionMid: _sliderVal('garment-region-mid') / 100,
        regionLower: _sliderVal('garment-region-lower') / 100,
        regionBottom: _sliderVal('garment-region-bottom') / 100,
    };
}

/** Compute per-vertex region weights for a garment (cosine blending) */
function _computeRegionWeights(gid) {
    const orig = garmentOrigPositions[gid];
    if (!orig) return;
    const n = orig.length / 3;
    // Find Y extent of the garment
    let yMin = Infinity, yMax = -Infinity;
    for (let i = 0; i < n; i++) {
        const y = orig[i * 3 + 1];
        if (y < yMin) yMin = y;
        if (y > yMax) yMax = y;
    }
    const yRange = yMax - yMin || 1e-6;
    const weights = {};
    for (const def of REGION_DEFS) {
        weights[def.id] = new Float32Array(n);
    }
    for (let i = 0; i < n; i++) {
        const t = (orig[i * 3 + 1] - yMin) / yRange;  // normalized 0..1
        for (const def of REGION_DEFS) {
            const dist = Math.abs(t - def.center);
            if (dist < REGION_RADIUS) {
                weights[def.id][i] = 0.5 * (1 + Math.cos(Math.PI * dist / REGION_RADIUS));
            }
            // else stays 0
        }
    }
    garmentRegionWeights[gid] = weights;
}

/** Apply saved state to a garment mesh (after creation / re-fit).
 *  Position/Scale are applied as vertex buffer transforms (mesh.position/scale
 *  are ignored by Three.js for SkinnedMesh sharing another mesh's skeleton). */
function _applyGarmentState(gid) {
    const mesh = garmentMeshes[gid];
    const st = garmentState[gid];
    const orig = garmentOrigPositions[gid];
    if (!mesh || !st || !orig) return;

    // Material properties (work fine on SkinnedMesh)
    mesh.material.color.set(st.color);
    mesh.material.roughness = st.roughness;
    mesh.material.metalness = st.metalness;

    // Position/Scale: modify vertex buffer directly
    const positions = mesh.geometry.attributes.position.array;
    const n = orig.length / 3;

    // Compute center of original mesh for scaling pivot
    let cx = 0, cy = 0, cz = 0;
    for (let i = 0; i < orig.length; i += 3) {
        cx += orig[i]; cy += orig[i + 1]; cz += orig[i + 2];
    }
    cx /= n; cy /= n; cz /= n;

    // Apply scale around center, then position offset
    for (let i = 0; i < orig.length; i += 3) {
        positions[i]     = (orig[i]     - cx) * st.scaleX + cx + st.posX;
        positions[i + 1] = (orig[i + 1] - cy) * st.scaleY + cy + st.posY;
        positions[i + 2] = (orig[i + 2] - cz) * st.scaleZ + cz + st.posZ;
    }

    // Per-region Y-offsets (cosine-blended)
    const rw = garmentRegionWeights[gid];
    if (rw) {
        for (const def of REGION_DEFS) {
            const key = 'region' + def.id[0].toUpperCase() + def.id.slice(1);
            const offset = st[key] || 0;
            if (Math.abs(offset) < 1e-6) continue;
            const w = rw[def.id];
            for (let i = 0; i < n; i++) {
                positions[i * 3 + 1] += offset * w[i];
            }
        }
    }

    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.computeBoundingSphere();
}

/** No-op — Position/Scale section is always visible now */
function _updateGarmentAdjustmentsVisibility() {}

/**
 * Build query string with body state (body_type, morphs, meta, offset, stiffness, color).
 * Shared by loadGarment() and loadSmplGarment() for the fit endpoint.
 */
function _buildBodyFitQueryString() {
    const bodySelect = document.getElementById('body-type-select');
    const bodyType = bodySelect ? bodySelect.value : 'Female_Caucasian';

    const offset = (_sliderVal('garment-offset') / 1000);
    const stiffness = (_sliderVal('garment-stiffness') / 100);
    const colorPicker = document.getElementById('garment-color');
    const colorHex = colorPicker ? colorPicker.value : '#4d5980';
    const cr = parseInt(colorHex.slice(1, 3), 16) / 255;
    const cg = parseInt(colorHex.slice(3, 5), 16) / 255;
    const cb = parseInt(colorHex.slice(5, 7), 16) / 255;

    let qs = `body_type=${encodeURIComponent(bodyType)}`;
    const minDist = _sliderVal('garment-min-dist');
    const crotchFloor = _sliderVal('garment-crotch-floor');
    const lift = _sliderVal('garment-lift');
    const crotchDepth = _sliderVal('garment-crotch-depth');
    qs += `&offset=${offset}&stiffness=${stiffness}&min_dist=${minDist}&crotch_floor=${crotchFloor}&lift=${lift}&crotch_depth=${crotchDepth}`;
    qs += `&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;

    // Append current morph values
    document.querySelectorAll('#morphs-panel input[type="range"][data-morph]').forEach(slider => {
        const mName = slider.dataset.morph;
        if (mName) {
            qs += `&morph_${mName}=${slider.value / 100}`;
        }
    });
    // Append meta sliders (convert display value → internal -1..1)
    ['age', 'mass', 'tone', 'height'].forEach(m => {
        const el = document.getElementById(`meta-${m}`);
        if (el) {
            const dv = parseInt(el.value);
            const mn = parseInt(el.min), mx = parseInt(el.max);
            const neutral = (mn + mx) / 2;
            const half = (mx - mn) / 2;
            const internal = half ? (dv - neutral) / half : 0;
            qs += `&meta_${m}=${internal}`;
        }
    });
    return qs;
}

async function loadGarment(garmentId) {
    const createBtn = document.getElementById('garment-create');
    if (createBtn) createBtn.disabled = true;

    ensureSkinned();

    try {
        const bodyQs = _buildBodyFitQueryString();
        let qs = `garment_id=${encodeURIComponent(garmentId)}&${bodyQs}`;

        const resp = await fetch(`/api/character/garment/fit/?${qs}`);
        const data = await resp.json();
        if (data.error) {
            console.error('Garment fit error:', data.error);
            return;
        }

        // Remove previous mesh but keep saved state for re-apply
        removeGarment(garmentId, true);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        const faceBuf = base64ToUint32(data.faces);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        // Let Three.js compute smooth vertex normals — visually hides
        // small geometric bumps from the fitting pipeline
        geo.computeVertexNormals();

        const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0,
            side: THREE.DoubleSide,
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnit: -1,
        });

        let mesh;
        if (isSkinned && rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        garmentMeshes[garmentId] = mesh;
        scene.add(mesh);

        // Store original vertex positions for buffer-level transforms
        garmentOrigPositions[garmentId] = new Float32Array(vertBuf);
        _computeRegionWeights(garmentId);

        // Save current slider state and apply client-side transforms
        _saveGarmentState(garmentId);
        _applyGarmentState(garmentId);

        console.log(`Garment ${garmentId}: ${data.vertex_count} verts, skinned=${mesh.isSkinnedMesh || false}`);

        // Auto-select the newly created garment in the 3D scene
        if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
        _selectedItem = { root: mesh, type: 'garment', id: garmentId, label: garmentId.split('/').pop() };
        _setEmissiveOnItem(_selectedItem, _SELECT_EMISSIVE);
        const rb = document.getElementById('selection-remove-btn');
        if (rb) rb.style.display = '';

        updateEquippedList();
    } catch (e) {
        console.error('Failed to load garment:', e);
    }
    if (createBtn) createBtn.disabled = false;
}

function removeGarment(garmentId, keepState) {
    const m = garmentMeshes[garmentId];
    if (m) {
        scene.remove(m);
        m.geometry.dispose();
        m.material.dispose();
        delete garmentMeshes[garmentId];
        if (!keepState) {
            delete garmentState[garmentId];
            delete garmentOrigPositions[garmentId];
            delete garmentRegionWeights[garmentId];
        }
        updateEquippedList();
    }
}

function removeAllGarments() {
    for (const id of Object.keys(garmentMeshes)) {
        removeGarment(id);
    }
    updateEquippedList();
}

// =========================================================================
// 3D Interaction — hover highlight, click-to-select, equipped list
// =========================================================================

/** Collect all selectable 3D targets (garments, cloth, wardrobe, hair, SMPL garments) */
function getSelectableTargets() {
    const targets = [];
    for (const [id, m] of Object.entries(garmentMeshes)) {
        if (m) targets.push({ root: m, type: 'garment', id, label: id.split('/').pop() });
    }
    for (const [key, m] of Object.entries(clothMeshes)) {
        if (m) targets.push({ root: m, type: 'cloth', id: key, label: key });
    }
    for (const [name, obj] of Object.entries(loadedAssets)) {
        if (obj) targets.push({ root: obj, type: 'wardrobe', id: name, label: name.replace(/_/g, ' ') });
    }
    if (hairMesh) {
        const hs = document.getElementById('hair-style-select');
        const label = hs ? (hs.options[hs.selectedIndex]?.textContent || 'Hair') : 'Hair';
        targets.push({ root: hairMesh, type: 'hair', id: 'hair', label });
    }
    // Add SMPL garments (standalone meshes at SMPL body position)
    if (typeof smplGarmentMeshes !== 'undefined') {
        for (const [id, m] of Object.entries(smplGarmentMeshes)) {
            if (m) targets.push({ root: m, type: 'smpl_garment', id, label: 'SMPL: ' + id });
        }
    }
    return targets;
}

function _getMeshesOfRoot(root) {
    const meshes = [];
    if (root.isMesh) {
        meshes.push(root);
    } else {
        root.traverse(child => { if (child.isMesh) meshes.push(child); });
    }
    return meshes;
}

function _setEmissiveOnItem(item, color) {
    for (const m of _getMeshesOfRoot(item.root)) {
        if (m.material && m.material.emissive) {
            m.material.emissive.copy(color);
        }
    }
}

function _findItemForObject(obj, targets) {
    for (const t of targets) {
        let cur = obj;
        while (cur) {
            if (cur === t.root) return t;
            cur = cur.parent;
        }
    }
    return null;
}

function _sameItem(a, b) {
    if (!a || !b) return false;
    return a.type === b.type && a.id === b.id;
}

/** Called when selection changes — sync Pattern Editor sliders to selected mesh */
function _onSelectionChanged(item) {
    if (!item) return;
    // Sync Pattern Editor material sliders to selected cloth mesh
    if (item.type === 'cloth' || item.type === 'garment') {
        const mesh = clothMeshes[item.id] || garmentMeshes[item.id];
        if (!mesh || !mesh.material) return;
        const mat = mesh.material;
        const peColor = document.getElementById('pe-color');
        const peRough = document.getElementById('pe-roughness');
        const peMetal = document.getElementById('pe-metalness');
        if (peColor) peColor.value = '#' + mat.color.getHexString();
        if (peRough) { peRough.value = Math.round(mat.roughness * 100); peRough.dispatchEvent(new Event('input')); }
        if (peMetal) { peMetal.value = Math.round(mat.metalness * 100); peMetal.dispatchEvent(new Event('input')); }
    }
}

/** Initialize hover/click/selection handlers on the canvas */
function _initInteraction() {
    const canvas = renderer.domElement;
    const tooltip = document.getElementById('garment-tooltip');
    const removeBtn = document.getElementById('selection-remove-btn');

    // Throttled hover raycasting via requestAnimationFrame
    let _hoverPending = false;
    let _lastMouseEvent = null;

    canvas.addEventListener('mousemove', (e) => {
        // Box select drag
        if (veActive && veBoxSelecting) {
            _veBoxSelectMove(e);
            return;
        }
        _lastMouseEvent = e;
        if (!_hoverPending) {
            _hoverPending = true;
            requestAnimationFrame(() => {
                _hoverPending = false;
                if (_lastMouseEvent) {
                    if (veActive) {
                        // In VE mode, cursor hint for cloth surface
                        const rect = canvas.getBoundingClientRect();
                        _mouseNDC.x = ((_lastMouseEvent.clientX - rect.left) / rect.width) * 2 - 1;
                        _mouseNDC.y = -((_lastMouseEvent.clientY - rect.top) / rect.height) * 2 + 1;
                        _raycaster.setFromCamera(_mouseNDC, camera);
                        const hits = _raycaster.intersectObject(veTargetMesh);
                        canvas.style.cursor = hits.length > 0 ? 'pointer' : '';
                    } else {
                        _doHover(_lastMouseEvent);
                    }
                }
            });
        }
    });

    canvas.addEventListener('mouseleave', () => {
        if (_hoveredItem && !_sameItem(_hoveredItem, _selectedItem)) {
            _setEmissiveOnItem(_hoveredItem, _ZERO_EMISSIVE);
        }
        _hoveredItem = null;
        if (tooltip) tooltip.style.display = 'none';
    });

    // Click detection (distinguish from drag for OrbitControls compatibility)
    canvas.addEventListener('mousedown', (e) => {
        if (e.button === 0) {
            _mouseDownPos = { x: e.clientX, y: e.clientY };
            // Alt+click starts box select
            if (veActive && e.altKey) {
                _veBoxSelectStart(e);
            }
        }
    });

    canvas.addEventListener('mouseup', (e) => {
        if (veActive && veBoxSelecting) {
            _veBoxSelectEnd(e);
            _mouseDownPos = null;
            return;
        }
        if (e.button !== 0 || !_mouseDownPos) return;
        const dx = e.clientX - _mouseDownPos.x;
        const dy = e.clientY - _mouseDownPos.y;
        _mouseDownPos = null;
        if (Math.sqrt(dx * dx + dy * dy) > 3) return; // was a drag
        if (veActive) {
            _veHandleClick(e);
            return;
        }
        _doClick();
    });

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
        if (e.target.closest('input, select, textarea')) return;
        if (e.key === 'Delete' && _selectedItem) {
            _removeSelectedItem();
            return;
        }
        if (veActive) {
            if (e.key === 'Escape') {
                peMode = 'select'; _peSetModeButtons();
                return;
            }
            if (e.key === 'a' || e.key === 'A') {
                if (veSelectedIndices.size > 0 && vePointsOverlay) {
                    veSelectedIndices.clear();
                } else if (vePointsOverlay) {
                    const count = vePointsOverlay.geometry.getAttribute('position').count;
                    for (let i = 0; i < count; i++) veSelectedIndices.add(i);
                }
                _veUpdateAllColors();
                _veUpdateGizmo();
                _veUpdateSelectionInfo();
                return;
            }
        }
    });

    // Floating remove button
    if (removeBtn) {
        removeBtn.addEventListener('click', () => _removeSelectedItem());
    }

    function _doHover(e) {
        const rect = canvas.getBoundingClientRect();
        _mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        _mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        _raycaster.setFromCamera(_mouseNDC, camera);

        const targets = getSelectableTargets();
        const roots = targets.map(t => t.root);
        const intersects = _raycaster.intersectObjects(roots, true);

        let newItem = null;
        if (intersects.length > 0) {
            newItem = _findItemForObject(intersects[0].object, targets);
        }

        // Update tooltip
        if (newItem && tooltip) {
            tooltip.textContent = newItem.label;
            tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
            tooltip.style.display = 'block';
            canvas.style.cursor = 'pointer';
        } else {
            if (tooltip) tooltip.style.display = 'none';
            canvas.style.cursor = '';
        }

        // Update highlight
        if (!_sameItem(_hoveredItem, newItem)) {
            if (_hoveredItem && !_sameItem(_hoveredItem, _selectedItem)) {
                _setEmissiveOnItem(_hoveredItem, _ZERO_EMISSIVE);
            }
            _hoveredItem = newItem;
            if (_hoveredItem && !_sameItem(_hoveredItem, _selectedItem)) {
                _setEmissiveOnItem(_hoveredItem, _HOVER_EMISSIVE);
            }
        }
    }

    function _doClick() {
        const prev = _selectedItem;
        if (_hoveredItem) {
            if (_sameItem(_selectedItem, _hoveredItem)) {
                // Deselect
                _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
                _selectedItem = null;
                if (removeBtn) removeBtn.style.display = 'none';
            } else {
                // Select new
                if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
                _selectedItem = _hoveredItem;
                _setEmissiveOnItem(_selectedItem, _SELECT_EMISSIVE);
                if (removeBtn) removeBtn.style.display = '';
            }
        } else {
            // Click on empty → deselect
            if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
            _selectedItem = null;
            if (removeBtn) removeBtn.style.display = 'none';
        }
        if (!_sameItem(prev, _selectedItem)) _onSelectionChanged(_selectedItem);
    }
}

/** Remove the currently selected item */
function _removeSelectedItem() {
    if (!_selectedItem) return;
    const { type, id } = _selectedItem;
    switch (type) {
        case 'garment':
            removeGarment(id);
            break;
        case 'cloth':
            removeClothRegion(id);
            break;
        case 'hair': {
            removeHair();
            const hs = document.getElementById('hair-style-select');
            if (hs) hs.value = '';
            break;
        }
        case 'wardrobe': {
            const btn = document.querySelector(`.asset-btn[data-asset="${id}"]`);
            if (btn) btn.click();
            break;
        }
        case 'smpl_garment':
            if (typeof removeSmplGarment === 'function') {
                removeSmplGarment(id);
            }
            break;
    }
    _selectedItem = null;
    _hoveredItem = null;
    const removeBtn = document.getElementById('selection-remove-btn');
    if (removeBtn) removeBtn.style.display = 'none';
    updateEquippedList();
}

// --- Equipped Items Panel ---
let _equippedListTimer = null;
function updateEquippedList() {
    clearTimeout(_equippedListTimer);
    _equippedListTimer = setTimeout(_buildEquippedList, 100);
}

function _buildEquippedList() {
    const list = document.getElementById('equipped-items-list');
    if (!list) return;
    list.innerHTML = '';

    const targets = getSelectableTargets();
    if (targets.length === 0) {
        list.innerHTML = '<li style="color:var(--text-muted);font-size:0.78rem;padding:4px 0;">No items equipped</li>';
        return;
    }

    for (const t of targets) {
        const li = document.createElement('li');
        li.className = 'equipped-item';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'equipped-item-name';
        nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => {
            // Highlight in 3D
            if (_selectedItem) _setEmissiveOnItem(_selectedItem, _ZERO_EMISSIVE);
            // Refresh target reference in case mesh was re-created
            const fresh = getSelectableTargets().find(x => x.type === t.type && x.id === t.id);
            if (!fresh) return;
            _selectedItem = fresh;
            _setEmissiveOnItem(_selectedItem, _SELECT_EMISSIVE);
            const rb = document.getElementById('selection-remove-btn');
            if (rb) rb.style.display = '';
        });

        const rmBtn = document.createElement('button');
        rmBtn.className = 'equipped-item-remove';
        rmBtn.innerHTML = '&#10005;';
        rmBtn.title = 'Remove';
        rmBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            switch (t.type) {
                case 'garment': removeGarment(t.id); break;
                case 'cloth': removeClothRegion(t.id); break;
                case 'hair': {
                    removeHair();
                    const hs2 = document.getElementById('hair-style-select');
                    if (hs2) hs2.value = '';
                    break;
                }
                case 'wardrobe': {
                    const btn = document.querySelector(`.asset-btn[data-asset="${t.id}"]`);
                    if (btn) btn.click();
                    break;
                }
                case 'smpl_garment':
                    if (typeof removeSmplGarment === 'function') {
                        removeSmplGarment(t.id);
                    }
                    break;
            }
            if (_sameItem(_selectedItem, t)) {
                _selectedItem = null;
                const rb = document.getElementById('selection-remove-btn');
                if (rb) rb.style.display = 'none';
            }
            updateEquippedList();
        });

        li.appendChild(nameSpan);
        li.appendChild(rmBtn);
        list.appendChild(li);
    }
}

async function _loadDownloadPacks() {
    const packSelect = document.getElementById('garment-pack-select');
    if (!packSelect) return;
    try {
        const resp = await fetch('/api/character/garment/download/available/');
        const data = await resp.json();
        packSelect.innerHTML = '';
        (data.packs || []).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.name;
            opt.textContent = `${p.label} (${p.category})`;
            packSelect.appendChild(opt);
        });
    } catch (e) {
        console.warn('Failed to load download packs:', e);
    }
}

async function _downloadPack() {
    const packSelect = document.getElementById('garment-pack-select');
    const statusEl = document.getElementById('garment-download-status');
    const dlBtn = document.getElementById('garment-pack-download');
    if (!packSelect || !packSelect.value) return;

    const packName = packSelect.value;
    if (dlBtn) dlBtn.disabled = true;
    if (statusEl) statusEl.textContent = `Lade ${packName}...`;

    try {
        const resp = await fetch('/api/character/garment/download/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pack_name: packName }),
        });
        const data = await resp.json();
        if (data.ok) {
            if (statusEl) statusEl.textContent = `${data.count} Garments installiert!`;
            // Refresh library
            const resp2 = await fetch('/api/character/garment/library/');
            const lib = await resp2.json();
            _garmentCatalog = [];
            if (lib.garments) {
                for (const cat of Object.keys(lib.garments)) {
                    for (const g of lib.garments[cat]) _garmentCatalog.push(g);
                }
            }
            // Refresh category dropdown
            const catSelect = document.getElementById('garment-category');
            if (catSelect && lib.categories) {
                while (catSelect.options.length > 1) catSelect.remove(1);
                lib.categories.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat;
                    opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                    catSelect.appendChild(opt);
                });
            }
            _renderGarmentList();
        } else {
            if (statusEl) statusEl.textContent = `Fehler: ${data.error || 'Unbekannt'}`;
        }
    } catch (e) {
        if (statusEl) statusEl.textContent = `Fehler: ${e.message}`;
    }
    if (dlBtn) dlBtn.disabled = false;
}

// =========================================================================
// Scene settings from /humanbody/scene/ page (localStorage)
// =========================================================================
const VIEWER_TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

function applySceneSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    if (!saved) return;
    try {
        const s = JSON.parse(saved);
        if (s.lighting) {
            if (s.lighting.key) {
                keyLight.intensity = s.lighting.key.intensity;
                keyLight.color.set(s.lighting.key.color);
                keyLight.position.set(...s.lighting.key.pos);
            }
            if (s.lighting.fill) {
                fillLight.intensity = s.lighting.fill.intensity;
                fillLight.color.set(s.lighting.fill.color);
                fillLight.position.set(...s.lighting.fill.pos);
            }
            if (s.lighting.back) {
                backLight.intensity = s.lighting.back.intensity;
                backLight.color.set(s.lighting.back.color);
                backLight.position.set(...s.lighting.back.pos);
            }
            if (s.lighting.ambient) {
                ambient.intensity = s.lighting.ambient.intensity;
                ambient.color.set(s.lighting.ambient.color);
            }
        }
        if (s.renderer) {
            if (s.renderer.toneMapping && VIEWER_TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) {
                renderer.toneMapping = VIEWER_TONE_MAPPINGS[s.renderer.toneMapping];
            }
            if (s.renderer.exposure !== undefined) {
                renderer.toneMappingExposure = s.renderer.exposure;
            }
            if (s.renderer.background) {
                scene.background.set(s.renderer.background);
            }
        }
        if (s.camera && s.camera.fov) {
            camera.fov = s.camera.fov;
            camera.updateProjectionMatrix();
        }
    } catch (e) {
        console.warn('Failed to load scene settings:', e);
    }
}

function applySceneSkinSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    const mat = getSkinMat();
    if (!saved || !mat) return;
    try {
        const s = JSON.parse(saved);
        if (s.skin) {
            // NOTE: skin COLOR is NOT applied from scene settings —
            // it comes from SKIN_COLORS per ethnicity (body type).
            if (s.skin.roughness !== undefined) mat.roughness = s.skin.roughness;
            if (s.skin.metalness !== undefined) mat.metalness = s.skin.metalness;
            syncSkinUI(mat);
        }
    } catch (e) { /* ignore */ }
}

function syncSkinUI(mat) {
    if (!mat) return;
    const colorInput = document.getElementById('skin-color-viewer');
    if (colorInput) colorInput.value = '#' + mat.color.getHexString();
    const roughSlider = document.getElementById('skin-roughness-viewer');
    const roughVal = document.getElementById('skin-roughness-viewer-val');
    if (roughSlider) { roughSlider.value = Math.round(mat.roughness * 100); roughVal.textContent = mat.roughness.toFixed(2); }
    const metalSlider = document.getElementById('skin-metalness-viewer');
    const metalVal = document.getElementById('skin-metalness-viewer-val');
    if (metalSlider) { metalSlider.value = Math.round(mat.metalness * 100); metalVal.textContent = mat.metalness.toFixed(2); }
}

// =========================================================================
// Utility
// =========================================================================
function base64ToFloat32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

function base64ToUint32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

/**
 * Convert Blender coordinate system to Three.js in-place.
 * Blender: X-right, Y-forward, Z-up
 * Three.js: X-right, Y-up, Z-forward (toward camera)
 * Transform: (x, y, z) -> (x, z, -y)
 */
function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// =========================================================================
// Model Presets (Laden — File Dialog)
// =========================================================================
function initLoadPreset() {
    const btn = document.getElementById('load-preset-btn');
    if (!btn) return;

    // "Laden" — show dialog listing models from server directory
    btn.addEventListener('click', async () => {
        const name = await showLoadDialog();
        if (!name) return;
        try {
            const resp = await fetch(`/api/character/model/${encodeURIComponent(name)}/`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const preset = await resp.json();
            applyModelPreset(preset);
            currentPresetName = preset.name || name;
            btn.innerHTML = '<i class="fas fa-check"></i> Geladen!';
            setTimeout(() => { btn.innerHTML = '<i class="fas fa-folder-open"></i> Laden'; }, 1500);
            console.log(`Preset loaded: ${name}`);
        } catch (err) {
            console.error('Load preset error:', err);
            alert('Fehler beim Laden: ' + err.message);
        }
    });

    // Auto-load default preset after mesh is ready
    loadDefaultPreset();
}

async function loadDefaultPreset() {
    // Wait until mesh is loaded
    const maxWait = 15000;
    const start = Date.now();
    while (!bodyMesh && Date.now() - start < maxWait) {
        await new Promise(r => setTimeout(r, 200));
    }
    if (!bodyMesh) {
        console.warn('Default preset: mesh not ready, skipping');
        return;
    }
    // Small extra delay to ensure UI (cloth/hair dropdowns) is populated
    await new Promise(r => setTimeout(r, 500));

    // If VIEWER_CONFIG specifies a default body type, use that directly
    // (test page — skip settings API / preset loading)
    if (DEFAULT_BODY) {
        try {
            const bodySelect = document.getElementById('body-type-select');
            if (bodySelect) {
                bodySelect.value = DEFAULT_BODY;
                bodySelect.dispatchEvent(new Event('change'));
            }
            console.log(`Default body type applied: ${DEFAULT_BODY}`);
        } catch (e) {
            console.warn('Failed to apply default body type:', e);
        }
        return;
    }

    try {
        // Determine default settings from settings API
        let presetName = 'femaleWithClothes';
        let showRig = false;
        let defaultAnim = '';

        // On SMPL test page, use SMPL-specific humanbody preset
        const isSmplPage = !!document.getElementById('smpl-body-panel');
        if (isSmplPage) {
            try {
                const smplResp = await fetch('/api/settings/smpl/');
                if (smplResp.ok) {
                    const smplCfg = await smplResp.json();
                    if (smplCfg.humanbody_preset) {
                        presetName = smplCfg.humanbody_preset;
                    }
                }
            } catch (e) { /* fallback to default */ }
        } else {
            try {
                const settingsResp = await fetch('/api/settings/humanbody/');
                if (settingsResp.ok) {
                    const s = await settingsResp.json();
                    if (s.config) presetName = s.config;
                    showRig = !!s.show_rig_config;
                    defaultAnim = s.default_anim_config || '';
                }
            } catch (e) { /* fallback to default */ }
        }

        // Apply rig visibility from settings
        if (showRig) {
            rigVisible = true;
            const rigToggle = document.getElementById('rig-toggle');
            if (rigToggle) rigToggle.classList.add('active');
        }

        const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
        if (!resp.ok) return;
        const preset = await resp.json();
        applyModelPreset(preset);
        // Re-apply scene skin settings after preset (roughness/metalness only)
        setTimeout(() => applySceneSkinSettings(), 200);
        console.log(`Default preset loaded: ${presetName}`);

        // Auto-play default animation after preset is applied
        if (defaultAnim) {
            setTimeout(() => {
                loadBVHAnimation(defaultAnim, 'Default', 0);
                const demoBtn = document.getElementById('play-demo-anim');
                if (demoBtn) {
                    demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                    demoBtn.classList.add('active');
                }
            }, 1500);
        }
    } catch (e) {
        console.warn('Failed to load default preset:', e);
    }
}

function applyModelPreset(preset) {
    // 1. Body Type
    const bodySelect = document.getElementById('body-type-select');
    if (bodySelect && preset.body_type) {
        bodySelect.value = preset.body_type;
        bodySelect.dispatchEvent(new Event('change'));
    }

    // 2. Meta sliders — restore age, mass, tone, height (stored as internal -1..1)
    if (preset.meta) {
        ['age', 'mass', 'tone', 'height'].forEach(name => {
            const el = document.getElementById(`meta-${name}`);
            const valSpan = document.getElementById(`meta-${name}-val`);
            if (el && preset.meta[name] !== undefined) {
                const internal = preset.meta[name];
                // Convert internal -1..1 back to display value
                const min = parseInt(el.min), max = parseInt(el.max);
                const neutral = (min + max) / 2;
                const half = (max - min) / 2;
                const displayVal = Math.round(internal * half + neutral);
                el.value = displayVal;
                if (valSpan) valSpan.textContent = displayVal;
                wsSend({ type: 'meta', name: name, value: internal });
            }
        });
    }

    // 3. Morphs — set slider values and send via WebSocket
    if (preset.morphs) {
        const morphBatch = {};
        const panel = document.getElementById('morphs-panel');
        if (panel) {
            panel.querySelectorAll('input[type="range"][data-morph]').forEach(slider => {
                const morphName = slider.dataset.morph;
                const val = preset.morphs[morphName];
                if (val !== undefined) {
                    const intVal = Math.round(val * 100);
                    slider.value = intVal;
                    slider.nextElementSibling.textContent = intVal;
                    morphBatch[morphName] = val;
                } else {
                    slider.value = 0;
                    slider.nextElementSibling.textContent = '0';
                }
            });
        }
        if (Object.keys(morphBatch).length > 0) {
            wsSend({ type: 'morph_batch', morphs: morphBatch });
        }
    }

    // 4. Wardrobe — toggle asset buttons matching preset
    if (preset.wardrobe && preset.wardrobe.length > 0) {
        const wardrobePanel = document.getElementById('wardrobe-panel');
        if (wardrobePanel) {
            // First remove any currently active assets not in preset
            wardrobePanel.querySelectorAll('.asset-btn.active').forEach(btn => {
                if (!preset.wardrobe.includes(btn.dataset.asset)) {
                    btn.click();
                }
            });
            // Then activate preset assets
            preset.wardrobe.forEach(assetName => {
                const btn = wardrobePanel.querySelector(`.asset-btn[data-asset="${assetName}"]`);
                if (btn && !btn.classList.contains('active') && !btn.classList.contains('disabled')) {
                    btn.click();
                }
            });
        }
    }

    // 5. Cloth — generate one or more cloth pieces (skip for male body types)
    const isMalePreset = preset.body_type && preset.body_type.startsWith('Male_');
    if (preset.cloth && !isMalePreset) {
        removeAllCloth();
        const clothList = (Array.isArray(preset.cloth) ? preset.cloth : [preset.cloth]).filter(Boolean);
        clothList.forEach((c, i) => {
            if (!c) return;
            setTimeout(() => {
                // Support both old format (region) and new format (template)
                const tpl = c.template || (c.region ? {
                    TOP: 'TPL_TSHIRT', PANTS: 'TPL_PANTS',
                    SKIRT: 'TPL_SKIRT', DRESS: 'TPL_DRESS'
                }[c.region] : 'TPL_TSHIRT');
                const tight = c.tightness !== undefined ? c.tightness : 0.5;
                loadCloth(`tpl_${tpl}`, {
                    method: 'template', template: tpl,
                    tightness: tight,
                    segments: c.segments || 32,
                    top_extend: c.top_extend || 0,
                    bottom_extend: c.bottom_extend || 0,
                }, c.color || null);
            }, 500 + i * 300);
        });
        // Update template UI to show last piece
        const last = clothList[clothList.length - 1];
        const tplSelect = document.getElementById('cloth-tpl-type');
        const tplTight = document.getElementById('cloth-tpl-tightness');
        const tplTightVal = document.getElementById('cloth-tpl-tightness-val');
        const colorPicker = document.getElementById('cloth-color');
        const tpl = last ? (last.template || (last.region ? {
            TOP: 'TPL_TSHIRT', PANTS: 'TPL_PANTS',
            SKIRT: 'TPL_SKIRT', DRESS: 'TPL_DRESS'
        }[last.region] : 'TPL_TSHIRT')) : 'TPL_TSHIRT';
        if (tplSelect) {
            tplSelect.value = tpl;
            tplSelect.dispatchEvent(new Event('change'));
        }
        const tight = (last && last.tightness !== undefined) ? last.tightness : 0.5;
        if (tplTight) { tplTight.value = Math.round(tight * 100); }
        if (tplTightVal) tplTightVal.textContent = tight.toFixed(2);
        if (colorPicker && last && last.color) colorPicker.value = last.color;
    }

    // 6. Hair — select style and color
    if (preset.hair_style) {
        const hairSelect = document.getElementById('hair-style-select');
        const hairColorSelect = document.getElementById('hair-color-select');

        if (hairSelect && preset.hair_style.url) {
            // Find matching option by url
            for (const opt of hairSelect.options) {
                if (opt.value === preset.hair_style.url) {
                    hairSelect.value = opt.value;
                    break;
                }
            }
            loadHair(preset.hair_style.url);
        }
        if (hairColorSelect && preset.hair_style.color) {
            hairColorSelect.value = preset.hair_style.color;
            // Apply color after hair loads
            setTimeout(() => applyHairColor(preset.hair_style.color), 1000);
        }
    }

    // 7. Garments — fitted external garments
    if (preset.garments && preset.garments.length > 0) {
        removeAllGarments();
        const _setEl = (id, v) => { const e = document.getElementById(id); if (e) e.value = v; };
        const loadGarments = async () => {
            for (const g of preset.garments) {
                // Set sliders to match saved state before calling loadGarment
                _setEl('garment-offset', Math.round((g.offset || 0.006) * 1000));
                _setEl('garment-stiffness', Math.round((g.stiffness || 0.8) * 100));
                _setEl('garment-min-dist', g.minDist !== undefined ? g.minDist : 3);
                _setEl('garment-crotch-floor', g.crotchFloor !== undefined ? g.crotchFloor : 0);
                _setEl('garment-lift', g.lift !== undefined ? g.lift : 0);
                _setEl('garment-crotch-depth', g.crotchDepth !== undefined ? g.crotchDepth : 0);
                _setEl('garment-color', g.color || '#4d5980');
                _setEl('garment-roughness', Math.round((g.roughness || 0.8) * 100));
                _setEl('garment-metalness', Math.round((g.metalness || 0) * 100));
                _setEl('garment-pos-x', Math.round((g.posX || 0) * 100));
                _setEl('garment-pos-y', Math.round((g.posY || 0) * 100));
                _setEl('garment-pos-z', Math.round((g.posZ || 0) * 100));
                _setEl('garment-scale-x', Math.round((g.scaleX || 1) * 100));
                _setEl('garment-scale-y', Math.round((g.scaleY || 1) * 100));
                _setEl('garment-scale-z', Math.round((g.scaleZ || 1) * 100));
                selectedGarmentId = g.id;
                await loadGarment(g.id);
            }
            updateEquippedList();
        };
        setTimeout(() => loadGarments(), 800);
    }

    currentPresetName = preset.name || '';
    // Store model state so other pages (Szene, Animationen) can read it
    setTimeout(() => {
        try {
            localStorage.setItem('humanbody_current_model', JSON.stringify(gatherModelState()));
        } catch (e) { /* ignore */ }
    }, 2000);
    console.log(`Preset "${preset.name || 'unknown'}" applied`);
}

// =========================================================================
// Save Model
// =========================================================================
function gatherModelState() {
    const state = {};

    // Body type
    const bodySelect = document.getElementById('body-type-select');
    if (bodySelect) state.body_type = bodySelect.value;

    // Meta sliders (age, mass, tone, height) — save as internal -1..1 values
    const meta = {};
    ['age', 'mass', 'tone', 'height'].forEach(name => {
        const el = document.getElementById(`meta-${name}`);
        if (el) {
            const displayVal = parseInt(el.value);
            const min = parseInt(el.min), max = parseInt(el.max);
            const neutral = (min + max) / 2;
            const half = (max - min) / 2;
            meta[name] = half ? (displayVal - neutral) / half : 0;
        }
    });
    state.meta = meta;

    // Morphs
    const morphs = {};
    const panel = document.getElementById('morphs-panel');
    if (panel) {
        panel.querySelectorAll('input[type="range"][data-morph]').forEach(slider => {
            const val = parseInt(slider.value);
            if (val !== 0) {
                morphs[slider.dataset.morph] = val / 100;
            }
        });
    }
    state.morphs = morphs;

    // Cloth — reconstruct from clothParams
    const clothList = [];
    for (const [key, cp] of Object.entries(clothParams)) {
        const p = cp.params;
        const entry = {};
        if (p.method === 'template') {
            entry.template = p.template;
            entry.tightness = p.tightness !== undefined ? p.tightness : 0.5;
            entry.segments = p.segments || 32;
            if (p.top_extend) entry.top_extend = p.top_extend;
            if (p.bottom_extend) entry.bottom_extend = p.bottom_extend;
        } else if (p.method === 'builder') {
            entry.method = 'builder';
            entry.region = p.region;
            entry.looseness = p.looseness;
        } else if (p.method === 'primitive') {
            entry.method = 'primitive';
            entry.prim_type = p.prim_type;
            entry.segments = p.segments;
            entry.length = p.length;
            if (p.flare) entry.flare = p.flare;
        }
        entry.color = cp.color;
        clothList.push(entry);
    }
    state.cloth = clothList;

    // Hair
    const hairSelect = document.getElementById('hair-style-select');
    const hairColorSelect = document.getElementById('hair-color-select');
    if (hairSelect && hairSelect.value) {
        state.hair_style = {
            url: hairSelect.value,
            name: hairSelect.options[hairSelect.selectedIndex]?.textContent || '',
            color: hairColorSelect ? hairColorSelect.value : '',
        };
    }

    // Wardrobe
    const wardrobePanel = document.getElementById('wardrobe-panel');
    const activeAssets = [];
    if (wardrobePanel) {
        wardrobePanel.querySelectorAll('.asset-btn.active').forEach(btn => {
            activeAssets.push(btn.dataset.asset);
        });
    }
    state.wardrobe = activeAssets;

    // Garments (fitted external garments)
    const garments = [];
    for (const [gid, st] of Object.entries(garmentState)) {
        if (garmentMeshes[gid]) {
            garments.push({
                id: gid,
                offset: st.offset, stiffness: st.stiffness,
                color: st.color, roughness: st.roughness, metalness: st.metalness,
                posX: st.posX, posY: st.posY, posZ: st.posZ,
                scaleX: st.scaleX, scaleY: st.scaleY, scaleZ: st.scaleZ,
            });
        }
    }
    state.garments = garments;

    // Scene settings from localStorage
    const sceneSaved = localStorage.getItem('humanbody_scene_settings');
    if (sceneSaved) {
        try { state.scene = JSON.parse(sceneSaved); } catch (e) { /* ignore */ }
    }

    return state;
}

async function saveModel(name) {
    const data = gatherModelState();
    data.name = name;
    try {
        const resp = await fetch('/api/character/model/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, data }),
        });
        const result = await resp.json();
        if (result.ok) {
            currentPresetName = name;
            console.log(`Model saved: ${result.filename}`);
            return true;
        } else {
            alert('Fehler beim Speichern: ' + (result.error || 'Unbekannt'));
            return false;
        }
    } catch (e) {
        alert('Fehler beim Speichern: ' + e.message);
        return false;
    }
}

// ---- Save-Dialog (Modal) ----
function createSaveDialog() {
    if (document.getElementById('save-dialog-overlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'save-dialog-overlay';
    overlay.innerHTML = `
        <div class="save-dialog">
            <div class="save-dialog-header">
                <h3><i class="fas fa-file-export"></i> Modell speichern unter</h3>
                <button class="save-dialog-close" title="Schließen">&times;</button>
            </div>
            <div class="save-dialog-body">
                <label>Vorhandene Modelle:</label>
                <div class="save-dialog-list" id="save-dialog-list"></div>
                <label style="margin-top:12px;">Name:</label>
                <input type="text" id="save-dialog-name" placeholder="Neuer Name..." autocomplete="off">
            </div>
            <div class="save-dialog-footer">
                <button class="save-dialog-btn cancel" id="save-dialog-cancel">Abbrechen</button>
                <button class="save-dialog-btn confirm" id="save-dialog-confirm"><i class="fas fa-save"></i> Speichern</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    // Inject styles once
    if (!document.getElementById('save-dialog-styles')) {
        const style = document.createElement('style');
        style.id = 'save-dialog-styles';
        style.textContent = `
            #save-dialog-overlay {
                display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6);
                z-index:10000; align-items:center; justify-content:center;
            }
            #save-dialog-overlay.open { display:flex; }
            .save-dialog {
                background:var(--bg-secondary,#1e1e2e); border:1px solid var(--border,#333);
                border-radius:8px; width:420px; max-height:80vh; display:flex; flex-direction:column;
                box-shadow:0 8px 32px rgba(0,0,0,0.5);
            }
            .save-dialog-header {
                display:flex; align-items:center; justify-content:space-between;
                padding:14px 18px; border-bottom:1px solid var(--border,#333);
            }
            .save-dialog-header h3 { margin:0; font-size:1rem; color:var(--text,#eee); }
            .save-dialog-close {
                background:none; border:none; color:var(--text-muted,#888);
                font-size:1.4rem; cursor:pointer; padding:0 4px; line-height:1;
            }
            .save-dialog-close:hover { color:var(--text,#eee); }
            .save-dialog-body { padding:14px 18px; overflow-y:auto; }
            .save-dialog-body label { display:block; font-size:0.85rem; color:var(--text-muted,#999); margin-bottom:6px; }
            .save-dialog-list {
                max-height:200px; overflow-y:auto; border:1px solid var(--border,#333);
                border-radius:4px; background:var(--bg-primary,#12121e);
            }
            .save-dialog-item {
                padding:8px 12px; cursor:pointer; font-size:0.9rem;
                color:var(--text,#eee); border-bottom:1px solid var(--border,#222);
            }
            .save-dialog-item:last-child { border-bottom:none; }
            .save-dialog-item:hover { background:var(--accent,#5865f2); color:#fff; }
            .save-dialog-item.selected { background:var(--accent,#5865f2); color:#fff; }
            #save-dialog-name {
                width:100%; padding:8px 10px; border:1px solid var(--border,#333);
                border-radius:4px; background:var(--bg-primary,#12121e);
                color:var(--text,#eee); font-size:0.95rem; box-sizing:border-box;
            }
            #save-dialog-name:focus { outline:none; border-color:var(--accent,#5865f2); }
            .save-dialog-footer {
                display:flex; justify-content:flex-end; gap:8px;
                padding:12px 18px; border-top:1px solid var(--border,#333);
            }
            .save-dialog-btn {
                padding:8px 18px; border:1px solid var(--border,#333); border-radius:4px;
                cursor:pointer; font-size:0.9rem;
            }
            .save-dialog-btn.cancel { background:transparent; color:var(--text-muted,#999); }
            .save-dialog-btn.cancel:hover { color:var(--text,#eee); }
            .save-dialog-btn.confirm {
                background:var(--accent,#5865f2); color:#fff; border-color:var(--accent,#5865f2);
            }
            .save-dialog-btn.confirm:hover { filter:brightness(1.15); }
        `;
        document.head.appendChild(style);
    }
}

function showLoadDialog() {
    return new Promise((resolve) => {
        createSaveDialog();  // reuse the same dialog DOM
        const overlay = document.getElementById('save-dialog-overlay');
        const list = document.getElementById('save-dialog-list');
        const nameInput = document.getElementById('save-dialog-name');
        const confirmBtn = document.getElementById('save-dialog-confirm');
        const cancelBtn = document.getElementById('save-dialog-cancel');
        const closeBtn = overlay.querySelector('.save-dialog-close');

        // Adjust header for "Load" mode
        overlay.querySelector('.save-dialog-header h3').innerHTML =
            '<i class="fas fa-folder-open"></i> Modell laden';
        confirmBtn.innerHTML = '<i class="fas fa-folder-open"></i> Laden';
        nameInput.value = '';
        nameInput.placeholder = 'Modellname...';
        list.innerHTML = '<div style="padding:8px 12px;color:var(--text-muted,#888);font-size:0.85rem;">Lade...</div>';
        overlay.classList.add('open');

        // Load existing presets from server (models directory)
        fetch('/api/character/models/')
            .then(r => r.json())
            .then(data => {
                list.innerHTML = '';
                (data.presets || []).forEach(p => {
                    const item = document.createElement('div');
                    item.className = 'save-dialog-item';
                    item.textContent = p.label || p.name;
                    item.dataset.name = p.name;
                    item.addEventListener('click', () => {
                        list.querySelectorAll('.save-dialog-item').forEach(i => i.classList.remove('selected'));
                        item.classList.add('selected');
                        nameInput.value = p.name;
                    });
                    item.addEventListener('dblclick', () => {
                        nameInput.value = p.name;
                        close(p.name);
                    });
                    list.appendChild(item);
                });
                if (list.children.length === 0) {
                    list.innerHTML = '<div style="padding:8px 12px;color:var(--text-muted,#888);font-size:0.85rem;">Keine Modelle vorhanden</div>';
                }
            })
            .catch(() => {
                list.innerHTML = '<div style="padding:8px 12px;color:#f44;font-size:0.85rem;">Fehler beim Laden</div>';
            });

        function close(result) {
            overlay.classList.remove('open');
            // Restore save-dialog header for next use
            overlay.querySelector('.save-dialog-header h3').innerHTML =
                '<i class="fas fa-file-export"></i> Modell speichern unter';
            confirmBtn.innerHTML = '<i class="fas fa-save"></i> Speichern';
            nameInput.placeholder = 'Neuer Name...';
            confirmBtn.removeEventListener('click', onConfirm);
            cancelBtn.removeEventListener('click', onCancel);
            closeBtn.removeEventListener('click', onCancel);
            overlay.removeEventListener('click', onOverlayClick);
            nameInput.removeEventListener('keydown', onKeydown);
            resolve(result);
        }
        function onConfirm() {
            const name = nameInput.value.trim();
            if (name) close(name); else nameInput.focus();
        }
        function onCancel() { close(null); }
        function onOverlayClick(e) { if (e.target === overlay) close(null); }
        function onKeydown(e) {
            if (e.key === 'Enter') onConfirm();
            if (e.key === 'Escape') onCancel();
        }

        confirmBtn.addEventListener('click', onConfirm);
        cancelBtn.addEventListener('click', onCancel);
        closeBtn.addEventListener('click', onCancel);
        overlay.addEventListener('click', onOverlayClick);
        nameInput.addEventListener('keydown', onKeydown);
    });
}

function showSaveDialog() {
    return new Promise((resolve) => {
        createSaveDialog();
        const overlay = document.getElementById('save-dialog-overlay');
        const list = document.getElementById('save-dialog-list');
        const nameInput = document.getElementById('save-dialog-name');
        const confirmBtn = document.getElementById('save-dialog-confirm');
        const cancelBtn = document.getElementById('save-dialog-cancel');
        const closeBtn = overlay.querySelector('.save-dialog-close');

        nameInput.value = currentPresetName || '';
        list.innerHTML = '<div style="padding:8px 12px;color:var(--text-muted,#888);font-size:0.85rem;">Lade...</div>';
        overlay.classList.add('open');
        nameInput.focus();

        // Load existing presets
        fetch('/api/character/models/')
            .then(r => r.json())
            .then(data => {
                list.innerHTML = '';
                (data.presets || []).forEach(p => {
                    const item = document.createElement('div');
                    item.className = 'save-dialog-item';
                    item.textContent = p.label || p.name;
                    item.dataset.name = p.name;
                    item.addEventListener('click', () => {
                        list.querySelectorAll('.save-dialog-item').forEach(i => i.classList.remove('selected'));
                        item.classList.add('selected');
                        nameInput.value = p.name;
                        nameInput.focus();
                    });
                    list.appendChild(item);
                });
                if (list.children.length === 0) {
                    list.innerHTML = '<div style="padding:8px 12px;color:var(--text-muted,#888);font-size:0.85rem;">Keine Modelle vorhanden</div>';
                }
            })
            .catch(() => {
                list.innerHTML = '<div style="padding:8px 12px;color:#f44;font-size:0.85rem;">Fehler beim Laden</div>';
            });

        function close(result) {
            overlay.classList.remove('open');
            confirmBtn.removeEventListener('click', onConfirm);
            cancelBtn.removeEventListener('click', onCancel);
            closeBtn.removeEventListener('click', onCancel);
            overlay.removeEventListener('click', onOverlayClick);
            nameInput.removeEventListener('keydown', onKeydown);
            resolve(result);
        }
        function onConfirm() {
            const name = nameInput.value.trim();
            if (name) close(name); else nameInput.focus();
        }
        function onCancel() { close(null); }
        function onOverlayClick(e) { if (e.target === overlay) close(null); }
        function onKeydown(e) {
            if (e.key === 'Enter') onConfirm();
            if (e.key === 'Escape') onCancel();
        }

        confirmBtn.addEventListener('click', onConfirm);
        cancelBtn.addEventListener('click', onCancel);
        closeBtn.addEventListener('click', onCancel);
        overlay.addEventListener('click', onOverlayClick);
        nameInput.addEventListener('keydown', onKeydown);
    });
}

function initSaveButtons() {
    const saveBtn = document.getElementById('save-model-btn');
    const saveAsBtn = document.getElementById('save-model-as-btn');

    // "Speichern" — save to server (quick save under current name)
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            if (!currentPresetName) {
                // No name yet → open save-as dialog to pick a name first
                const name = await showSaveDialog();
                if (!name) return;
                const ok = await saveModel(name);
                if (ok) {
                    saveBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                    setTimeout(() => { saveBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 1500);
                }
                return;
            }
            const ok = await saveModel(currentPresetName);
            if (ok) {
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                setTimeout(() => { saveBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 1500);
            }
        });
    }

    // "Speichern unter" — server dialog (saves to models directory)
    if (saveAsBtn) {
        saveAsBtn.addEventListener('click', async () => {
            const name = await showSaveDialog();
            if (!name) return;
            const ok = await saveModel(name);
            if (ok) {
                saveAsBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                setTimeout(() => { saveAsBtn.innerHTML = '<i class="fas fa-file-export"></i> Speichern unter'; }, 1500);
            }
        });
    }
}

// =========================================================================
// SMPL Garment Library
// =========================================================================
const smplGarmentMeshes = {};   // garment_id -> THREE.Mesh
let smplBodyMesh = null;        // THREE.Mesh (semi-transparent wireframe)
let smplBodyVisible = false;
let _smplCatalog = [];          // flat list of {id, name, category, has_thumb}
let _smplSelectedId = '';       // currently selected in the list

async function loadSmplGarmentUI() {
    // Guard: only init if the panel exists in the DOM
    const panel = document.getElementById('garment-smpl-panel');
    if (!panel) return;

    // Slider bindings
    _bindSlider('smpl-garment-roughness', 'smpl-garment-roughness-val', v => (v / 100).toFixed(2));

    // Color picker
    const colorEl = document.getElementById('smpl-garment-color');
    if (colorEl) {
        colorEl.addEventListener('input', () => {
            if (!_smplSelectedId || !smplGarmentMeshes[_smplSelectedId]) return;
            smplGarmentMeshes[_smplSelectedId].material.color.set(colorEl.value);
        });
    }

    // Roughness slider live update
    const roughEl = document.getElementById('smpl-garment-roughness');
    if (roughEl) {
        roughEl.addEventListener('input', () => {
            if (!_smplSelectedId || !smplGarmentMeshes[_smplSelectedId]) return;
            smplGarmentMeshes[_smplSelectedId].material.roughness = roughEl.value / 100;
        });
    }

    // Load button
    const loadBtn = document.getElementById('smpl-garment-load');
    if (loadBtn) {
        loadBtn.addEventListener('click', () => {
            if (!_smplSelectedId) return;
            loadSmplGarment(_smplSelectedId);
        });
    }

    // Remove button
    const removeBtn = document.getElementById('smpl-garment-remove');
    if (removeBtn) {
        removeBtn.addEventListener('click', () => {
            if (_smplSelectedId && smplGarmentMeshes[_smplSelectedId]) {
                removeSmplGarment(_smplSelectedId);
            }
        });
    }

    // Remove all button
    const removeAllBtn = document.getElementById('smpl-garment-remove-all');
    if (removeAllBtn) {
        removeAllBtn.addEventListener('click', removeAllSmplGarments);
    }

    // Category filter
    const catSelect = document.getElementById('smpl-garment-category');
    if (catSelect) {
        catSelect.addEventListener('change', () => _renderSmplGarmentList());
    }

    // Fetch library catalog
    try {
        const resp = await fetch('/api/smpl/garment/library/');
        const data = await resp.json();
        _smplCatalog = [];

        // Populate category dropdown
        if (catSelect && data.categories) {
            data.categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                catSelect.appendChild(opt);
            });
        }

        // Flatten catalog
        if (data.garments) {
            for (const cat of Object.keys(data.garments)) {
                for (const g of data.garments[cat]) {
                    _smplCatalog.push(g);
                }
            }
        }

        _renderSmplGarmentList();
    } catch (e) {
        console.error('[SMPL] Error loading library:', e);
        const listEl = document.getElementById('smpl-garment-list');
        if (listEl) listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine SMPL-Library</div>';
    }
}

function _renderSmplGarmentList() {
    const listEl = document.getElementById('smpl-garment-list');
    const catSelect = document.getElementById('smpl-garment-category');
    if (!listEl) return;

    const filterCat = catSelect ? catSelect.value : '';
    const filtered = filterCat
        ? _smplCatalog.filter(g => g.category === filterCat)
        : _smplCatalog;

    if (filtered.length === 0) {
        listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine SMPL-Garments gefunden</div>';
        return;
    }

    // Group by category
    const byCat = {};
    for (const g of filtered) {
        if (!byCat[g.category]) byCat[g.category] = [];
        byCat[g.category].push(g);
    }

    listEl.innerHTML = '';
    for (const cat of Object.keys(byCat).sort()) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-category';  // collapsed by default
        const header = document.createElement('div');
        header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${cat.toUpperCase()} <span class="cat-count">${byCat[cat].length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open'));
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'anim-category-body';
        for (const g of byCat[cat]) {
            const item = document.createElement('div');
            item.className = 'anim-item';
            if (g.id === _smplSelectedId) item.classList.add('active');
            // Thumbnail + name
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/smpl/garment/thumb/${g.id}/`;
                img.alt = g.name;
                img.loading = 'lazy';
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;';
                item.appendChild(img);
            }
            const nameSpan = document.createElement('span');
            nameSpan.textContent = g.name;
            nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            item.appendChild(nameSpan);
            // Show loaded indicator
            if (smplGarmentMeshes[g.id]) {
                const badge = document.createElement('span');
                badge.textContent = '\u2713';
                badge.style.cssText = 'color:var(--success);margin-left:4px;';
                item.appendChild(badge);
            }
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.addEventListener('click', () => {
                _smplSelectedId = g.id;
                listEl.querySelectorAll('.anim-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                // Update color/roughness to match existing mesh if loaded
                if (smplGarmentMeshes[g.id]) {
                    const mat = smplGarmentMeshes[g.id].material;
                    const c = '#' + mat.color.getHexString();
                    const cp = document.getElementById('smpl-garment-color');
                    if (cp) cp.value = c;
                    _setSlider('smpl-garment-roughness', Math.round(mat.roughness * 100), v => (v / 100).toFixed(2));
                }
            });
            // Double-click to load immediately
            item.addEventListener('dblclick', () => {
                _smplSelectedId = g.id;
                loadSmplGarment(g.id);
            });
            body.appendChild(item);
        }
        catDiv.appendChild(body);
        listEl.appendChild(catDiv);
    }
}

async function loadSmplGarment(garmentId) {
    const loadBtn = document.getElementById('smpl-garment-load');
    if (loadBtn) {
        loadBtn.disabled = true;
        loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Laden...';
    }

    try {
        const resp = await fetch(`/api/smpl/garment/mesh/?garment_id=${encodeURIComponent(garmentId)}`);
        const data = await resp.json();
        if (data.error) {
            console.error('SMPL garment load error:', data.error);
            return;
        }

        // Remove previous if exists
        removeSmplGarment(garmentId);

        // Decode binary arrays (already in Three.js coords from server)
        const vertBuf = base64ToFloat32(data.vertices);
        const faceBuf = base64ToUint32(data.faces);
        const normBuf = base64ToFloat32(data.normals);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normBuf, 3));

        const colorEl = document.getElementById('smpl-garment-color');
        const roughEl = document.getElementById('smpl-garment-roughness');
        const color = colorEl ? colorEl.value : '#4d8066';
        const roughness = roughEl ? roughEl.value / 100 : 0.8;

        const mat = new THREE.MeshStandardMaterial({
            color: color,
            roughness: roughness,
            metalness: 0.0,
            side: THREE.DoubleSide,
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnit: -1,
        });

        const mesh = new THREE.Mesh(geo, mat);
        mesh.name = `smpl_garment_${garmentId}`;
        // Match SMPL body position (X offset + Y shift + 180° rotation).
        // The SMPL body generator shifts feet to Y=0 (subtracts ~0.86m),
        // but the garment OBJ is in the original SMPL frame. Apply same shift.
        if (smplBodyMesh) {
            mesh.position.copy(smplBodyMesh.position);
            mesh.rotation.copy(smplBodyMesh.rotation);
            // Compute Y shift: average Y of body verts ≈ pelvis position ≈ shift amount
            const posAttr = smplBodyMesh.geometry.getAttribute('position');
            let sumY = 0;
            for (let i = 0; i < posAttr.count; i++) sumY += posAttr.getY(i);
            mesh.position.y = sumY / posAttr.count;
        } else {
            const xOffsetEl = document.getElementById('smpl-body-xoffset');
            mesh.position.x = xOffsetEl ? xOffsetEl.value / 100 : 1.0;
            mesh.position.y = 0.86;
            mesh.rotation.y = Math.PI;
        }
        smplGarmentMeshes[garmentId] = mesh;
        scene.add(mesh);

        console.log(`SMPL garment loaded: ${garmentId} (${data.vertex_count} verts, ${data.face_count} faces)`);
        _renderSmplGarmentList();  // update checkmarks

        // Also fit to project body as SkinnedMesh (if body is loaded)
        console.log(`SMPL fit check: bodyMesh=${!!bodyMesh}, rigifySkeleton=${!!rigifySkeleton}, isSkinned=${isSkinned}`);
        if (bodyMesh && rigifySkeleton) {
            _fitSmplGarmentToBody(garmentId);
        } else {
            console.warn('SMPL fit skipped: bodyMesh or rigifySkeleton not ready');
        }
    } catch (e) {
        console.error('Failed to load SMPL garment:', e);
    } finally {
        if (loadBtn) {
            loadBtn.disabled = false;
            loadBtn.innerHTML = '<i class="fas fa-plus"></i> Laden';
        }
    }
}

async function _fitSmplGarmentToBody(garmentId) {
    const fitKey = 'smpl:' + garmentId;
    console.log(`_fitSmplGarmentToBody: start (${garmentId}), bodyMesh=${!!bodyMesh}, rigifySkeleton=${!!rigifySkeleton}, isSkinned=${isSkinned}`);
    try {
        ensureSkinned();

        // Build body state query — use _buildBodyFitQueryString if available
        // sliders exist (character_viewer page), else build minimal query
        const bodySelect = document.getElementById('body-type-select');
        const bodyType = bodySelect ? bodySelect.value : 'Female_Caucasian';
        let bodyQs;

        // Check if garment sliders exist (character_viewer page)
        if (document.getElementById('garment-offset')) {
            bodyQs = _buildBodyFitQueryString();
        } else {
            // SMPL test page: build minimal query with body type + morphs + meta
            bodyQs = `body_type=${encodeURIComponent(bodyType)}`;
            document.querySelectorAll('#morphs-panel input[type="range"]').forEach(slider => {
                const mName = slider.dataset.morph || slider.dataset.morphName || slider.id.replace('morph-', '');
                if (mName && slider.value !== undefined) {
                    bodyQs += `&morph_${mName}=${slider.value / 100}`;
                }
            });
            ['age', 'mass', 'tone', 'height'].forEach(m => {
                const el = document.getElementById(`meta-${m}`);
                if (el) {
                    const dv = parseInt(el.value);
                    const mn = parseInt(el.min), mx = parseInt(el.max);
                    const neutral = (mn + mx) / 2;
                    const half = (mx - mn) / 2;
                    const internal = half ? (dv - neutral) / half : 0;
                    bodyQs += `&meta_${m}=${internal}`;
                }
            });
        }

        const colorEl = document.getElementById('smpl-garment-color');
        const colorHex = colorEl ? colorEl.value : '#4d8066';
        const cr = parseInt(colorHex.slice(1, 3), 16) / 255;
        const cg = parseInt(colorHex.slice(3, 5), 16) / 255;
        const cb = parseInt(colorHex.slice(5, 7), 16) / 255;

        const qs = `garment_id=${encodeURIComponent(garmentId)}&${bodyQs}&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;
        const resp = await fetch(`/api/smpl/garment/fit/?${qs}`);
        const data = await resp.json();
        if (data.error) {
            console.error('SMPL garment fit error:', data.error);
            return;
        }

        // Remove previous fitted mesh if exists
        const prev = garmentMeshes[fitKey];
        if (prev) {
            scene.remove(prev);
            prev.geometry.dispose();
            prev.material.dispose();
            delete garmentMeshes[fitKey];
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.computeVertexNormals();

        const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0,
            side: THREE.DoubleSide,
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnit: -1,
        });

        let mesh;
        if (isSkinned && rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        mesh.name = `smpl_garment_fit_${garmentId}`;
        garmentMeshes[fitKey] = mesh;
        scene.add(mesh);

        console.log(`SMPL garment fitted to body: ${garmentId} (${data.vertex_count} verts, skinned=${mesh.isSkinnedMesh || false})`);
    } catch (e) {
        console.error('Failed to fit SMPL garment to body:', e);
    }
}

let _smplBodyUpdateTimer = null;

function _getSmplBetas() {
    const sliders = document.querySelectorAll('.smpl-beta-slider');
    const betas = [];
    sliders.forEach(s => { betas[parseInt(s.dataset.index)] = s.value / 100; });
    return betas;
}

function _getSmplGender() {
    const sel = document.getElementById('smpl-body-gender');
    return sel ? sel.value : 'female';
}

function _scheduleSmplBodyUpdate() {
    if (_smplBodyUpdateTimer) clearTimeout(_smplBodyUpdateTimer);
    _smplBodyUpdateTimer = setTimeout(() => {
        _smplBodyUpdateTimer = null;
        loadSmplBody();
    }, 100);
}

function _updateSmplBodyInfo() {
    const infoSection = document.getElementById('smpl-body-info-section');
    const infoDiv = document.getElementById('smpl-body-info');
    if (!infoSection || !infoDiv) return;

    if (!smplBodyMesh) {
        infoSection.style.display = 'none';
        return;
    }

    infoSection.style.display = '';
    const gender = _getSmplGender();
    const betas = _getSmplBetas();
    const geo = smplBodyMesh.geometry;
    const vCount = geo.getAttribute('position').count;
    const fCount = geo.index ? geo.index.count / 3 : 0;

    const betaNames = ['Height','Weight','Proportions','Torso','Chest','Hips','Waist','Limbs','Arms','Legs'];
    const nonZero = betas.filter(b => Math.abs(b) > 0.005);
    const betaStr = nonZero.length > 0
        ? betas.map((b, i) => Math.abs(b) > 0.005 ? `${betaNames[i]}=${b.toFixed(2)}` : null).filter(Boolean).join(', ')
        : 'Default shape';

    infoDiv.innerHTML = `Gender: <b>${gender}</b> | Vertices: <b>${vCount.toLocaleString()}</b> | Faces: <b>${fCount.toLocaleString()}</b><br>${betaStr}`;
}

async function initSmplBodyUI() {
    const panel = document.getElementById('smpl-body-panel');
    if (!panel) return;

    // Beta sliders
    const betaSliders = document.querySelectorAll('.smpl-beta-slider');
    const betaVals = document.querySelectorAll('.smpl-beta-val');
    betaSliders.forEach((slider, i) => {
        slider.addEventListener('input', () => {
            betaVals[i].textContent = (slider.value / 100).toFixed(2);
            _scheduleSmplBodyUpdate();
        });
    });

    // Gender select
    const genderSel = document.getElementById('smpl-body-gender');
    if (genderSel) {
        genderSel.addEventListener('change', () => loadSmplBody());
    }

    // Reset button
    const resetBtn = document.getElementById('smpl-beta-reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            betaSliders.forEach((s, i) => {
                s.value = 0;
                betaVals[i].textContent = '0.00';
            });
            _scheduleSmplBodyUpdate();
        });
    }

    // Opacity slider
    const opacityEl = document.getElementById('smpl-body-opacity');
    const opacityVal = document.getElementById('smpl-body-opacity-val');
    if (opacityEl) {
        opacityEl.addEventListener('input', () => {
            const v = opacityEl.value / 100;
            if (opacityVal) opacityVal.textContent = v.toFixed(2);
            if (smplBodyMesh) smplBodyMesh.material.opacity = v;
        });
    }

    // Color picker
    const colorEl = document.getElementById('smpl-body-color');
    if (colorEl) {
        colorEl.addEventListener('input', () => {
            if (smplBodyMesh) smplBodyMesh.material.color.set(colorEl.value);
        });
    }

    // Wireframe checkbox
    const wireEl = document.getElementById('smpl-body-wireframe');
    if (wireEl) {
        wireEl.addEventListener('change', () => {
            if (smplBodyMesh) {
                smplBodyMesh.material.wireframe = wireEl.checked;
                smplBodyMesh.material.depthWrite = !wireEl.checked;
            }
        });
    }

    // X Offset slider
    const xOffsetEl = document.getElementById('smpl-body-xoffset');
    const xOffsetVal = document.getElementById('smpl-body-xoffset-val');
    if (xOffsetEl) {
        xOffsetEl.addEventListener('input', () => {
            const v = xOffsetEl.value / 100;
            if (xOffsetVal) xOffsetVal.textContent = v.toFixed(2) + ' m';
            if (smplBodyMesh) smplBodyMesh.position.x = v;
            // Move SMPL garments with the body
            for (const m of Object.values(smplGarmentMeshes)) {
                m.position.x = v;
            }
        });
    }

    // Toggle visibility
    const toggle = document.getElementById('smpl-body-toggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            if (!smplBodyMesh) return;
            smplBodyVisible = !smplBodyVisible;
            smplBodyMesh.visible = smplBodyVisible;
            toggle.classList.toggle('active', smplBodyVisible);
        });
    }

    // Load saved defaults from settings API, then auto-load
    try {
        const resp = await fetch('/api/settings/smpl/');
        const cfg = await resp.json();

        // Apply gender
        if (genderSel && cfg.gender) genderSel.value = cfg.gender;

        // Apply betas
        if (cfg.betas && cfg.betas.length === 10) {
            betaSliders.forEach((s, i) => {
                s.value = Math.round(cfg.betas[i] * 100);
                betaVals[i].textContent = cfg.betas[i].toFixed(2);
            });
        }

        // Apply display settings
        if (opacityEl && cfg.opacity != null) {
            opacityEl.value = Math.round(cfg.opacity * 100);
            if (opacityVal) opacityVal.textContent = cfg.opacity.toFixed(2);
        }
        if (colorEl && cfg.color) colorEl.value = cfg.color;
        if (wireEl && cfg.wireframe != null) wireEl.checked = cfg.wireframe;
        if (xOffsetEl && cfg.xoffset != null) {
            xOffsetEl.value = Math.round(cfg.xoffset * 100);
            if (xOffsetVal) xOffsetVal.textContent = cfg.xoffset.toFixed(2) + ' m';
        }

        // Apply saved scene settings
        if (cfg.scene) {
            _applySmplSceneSettings(cfg.scene);
        }
    } catch (e) {
        console.warn('Could not load SMPL defaults:', e);
    }

    // Init scene UI (Szene tab)
    initSceneUI();

    // Save button
    const saveBtn = document.getElementById('smpl-save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => _saveSmplSettings());
    }

    // Auto-load SMPL body
    loadSmplBody();
}

async function loadSmplBody() {
    const gender = _getSmplGender();
    const betas = _getSmplBetas();
    const betaStr = betas.join(',');

    try {
        const resp = await fetch(`/api/smpl/body/?gender=${gender}&betas=${betaStr}`);
        const data = await resp.json();
        if (data.error) {
            console.warn('SMPL body error:', data.error);
            return;
        }

        const vertBuf = base64ToFloat32(data.vertices);
        const normBuf = base64ToFloat32(data.normals);

        if (smplBodyMesh) {
            // Update existing mesh — just swap vertex + normal buffers
            const posAttr = smplBodyMesh.geometry.getAttribute('position');
            posAttr.array.set(vertBuf);
            posAttr.needsUpdate = true;
            const normAttr = smplBodyMesh.geometry.getAttribute('normal');
            normAttr.array.set(normBuf);
            normAttr.needsUpdate = true;
            smplBodyMesh.geometry.computeBoundingSphere();
        } else {
            // First load — create mesh
            const faceBuf = base64ToUint32(data.faces);
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
            geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
            geo.setAttribute('normal', new THREE.BufferAttribute(normBuf, 3));

            const opacityEl = document.getElementById('smpl-body-opacity');
            const colorEl = document.getElementById('smpl-body-color');
            const wireEl = document.getElementById('smpl-body-wireframe');
            const xOffsetEl = document.getElementById('smpl-body-xoffset');

            const isWire = wireEl ? wireEl.checked : false;
            const mat = new THREE.MeshStandardMaterial({
                color: colorEl ? colorEl.value : 0x88aaff,
                transparent: true,
                opacity: opacityEl ? opacityEl.value / 100 : 1.0,
                wireframe: isWire,
                side: THREE.DoubleSide,
                depthWrite: !isWire,
            });

            smplBodyMesh = new THREE.Mesh(geo, mat);
            smplBodyMesh.name = 'smpl_body';
            smplBodyMesh.rotation.y = Math.PI;  // SMPL faces +Z, Three.js camera looks -Z
            smplBodyMesh.position.x = xOffsetEl ? xOffsetEl.value / 100 : 1.0;
            smplBodyVisible = true;
            scene.add(smplBodyMesh);

            const toggle = document.getElementById('smpl-body-toggle');
            if (toggle) toggle.classList.add('active');
        }

        _updateSmplBodyInfo();
    } catch (e) {
        console.error('Failed to load SMPL body:', e);
    }
}

function removeSmplGarment(garmentId) {
    const mesh = smplGarmentMeshes[garmentId];
    if (mesh) {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
        delete smplGarmentMeshes[garmentId];
    }
    // Also remove fitted project-body mesh
    const fitKey = 'smpl:' + garmentId;
    const fitMesh = garmentMeshes[fitKey];
    if (fitMesh) {
        scene.remove(fitMesh);
        fitMesh.geometry.dispose();
        fitMesh.material.dispose();
        delete garmentMeshes[fitKey];
    }
}

function removeAllSmplGarments() {
    for (const id of Object.keys(smplGarmentMeshes)) {
        removeSmplGarment(id);
    }
    _renderSmplGarmentList();
}

// =========================================================================
// Scene UI (Szene tab on SMPL test page)
// =========================================================================
const SMPL_LIGHT_PRESETS = {
    studio: {
        key:     { intensity: 3.0, color: '#ffffff', pos: [2, 4, -5] },
        fill:    { intensity: 2.0, color: '#eeeeff', pos: [-3, 3, -4] },
        back:    { intensity: 2.5, color: '#ffeedd', pos: [0, 4, 5] },
        ambient: { intensity: 0.8, color: '#ffffff' },
        exposure: 1.6
    },
    outdoor: {
        key:     { intensity: 4.0, color: '#fff5e0', pos: [5, 8, -2] },
        fill:    { intensity: 1.5, color: '#8899cc', pos: [-4, 2, -3] },
        back:    { intensity: 1.0, color: '#ffeedd', pos: [-2, 3, 4] },
        ambient: { intensity: 1.2, color: '#ddeeff' },
        exposure: 1.8
    },
    dramatic: {
        key:     { intensity: 4.5, color: '#ffddaa', pos: [4, 3, -3] },
        fill:    { intensity: 0.5, color: '#4444aa', pos: [-3, 1, -2] },
        back:    { intensity: 3.0, color: '#ff8844', pos: [0, 3, 5] },
        ambient: { intensity: 0.3, color: '#222244' },
        exposure: 1.4
    },
    neutral: {
        key:     { intensity: 2.5, color: '#ffffff', pos: [3, 5, -4] },
        fill:    { intensity: 2.5, color: '#ffffff', pos: [-3, 5, -4] },
        back:    { intensity: 2.0, color: '#ffffff', pos: [0, 4, 5] },
        ambient: { intensity: 1.0, color: '#ffffff' },
        exposure: 1.6
    }
};

function initSceneUI() {
    const pane = document.getElementById('tab-szene');
    if (!pane) return;

    // Light preset select
    const presetSel = document.getElementById('scene-light-preset');
    if (presetSel) {
        presetSel.addEventListener('change', () => {
            const preset = SMPL_LIGHT_PRESETS[presetSel.value];
            if (preset) {
                _applyLightPreset(preset);
                _syncSceneUI();
            }
        });
    }

    // Bind individual light controls
    _bindLightGroup('key', keyLight);
    _bindLightGroup('fill', fillLight);
    _bindLightGroup('back', backLight);

    // Ambient — intensity + color only (no position)
    const ambIntEl = document.getElementById('scene-ambient-intensity');
    const ambColEl = document.getElementById('scene-ambient-color');
    if (ambIntEl) {
        ambIntEl.addEventListener('input', () => {
            const v = ambIntEl.value / 100;
            ambient.intensity = v;
            const valEl = document.getElementById('scene-ambient-intensity-val');
            if (valEl) valEl.textContent = v.toFixed(2);
        });
    }
    if (ambColEl) {
        ambColEl.addEventListener('input', () => {
            ambient.color.set(ambColEl.value);
        });
    }

    // Renderer controls
    const tmSel = document.getElementById('scene-tonemapping');
    if (tmSel) {
        tmSel.addEventListener('change', () => {
            if (VIEWER_TONE_MAPPINGS[tmSel.value] !== undefined) {
                renderer.toneMapping = VIEWER_TONE_MAPPINGS[tmSel.value];
            }
        });
    }

    const expEl = document.getElementById('scene-exposure');
    if (expEl) {
        expEl.addEventListener('input', () => {
            const v = expEl.value / 100;
            renderer.toneMappingExposure = v;
            const valEl = document.getElementById('scene-exposure-val');
            if (valEl) valEl.textContent = v.toFixed(2);
        });
    }

    const bgEl = document.getElementById('scene-background');
    if (bgEl) {
        bgEl.addEventListener('input', () => {
            scene.background.set(bgEl.value);
        });
    }

    // Camera FOV
    const fovEl = document.getElementById('scene-fov');
    if (fovEl) {
        fovEl.addEventListener('input', () => {
            camera.fov = parseFloat(fovEl.value);
            camera.updateProjectionMatrix();
            const valEl = document.getElementById('scene-fov-val');
            if (valEl) valEl.textContent = fovEl.value + '\u00B0';
        });
    }

    // Reset lighting button
    const resetBtn = document.getElementById('scene-reset-lighting');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            _applyLightPreset(SMPL_LIGHT_PRESETS.studio);
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.6;
            scene.background.set(0x1a1a2e);
            camera.fov = 35;
            camera.updateProjectionMatrix();
            _syncSceneUI();
            if (presetSel) presetSel.value = 'studio';
        });
    }

    // Sync UI from current light state
    _syncSceneUI();
}

function _bindLightGroup(name, light) {
    const intEl = document.getElementById(`scene-${name}-intensity`);
    const colEl = document.getElementById(`scene-${name}-color`);
    const posXEl = document.getElementById(`scene-${name}-pos-x`);
    const posYEl = document.getElementById(`scene-${name}-pos-y`);
    const posZEl = document.getElementById(`scene-${name}-pos-z`);

    if (intEl) {
        intEl.addEventListener('input', () => {
            const v = intEl.value / 100;
            light.intensity = v;
            const valEl = document.getElementById(`scene-${name}-intensity-val`);
            if (valEl) valEl.textContent = v.toFixed(2);
        });
    }
    if (colEl) {
        colEl.addEventListener('input', () => light.color.set(colEl.value));
    }
    [['x', posXEl], ['y', posYEl], ['z', posZEl]].forEach(([axis, el]) => {
        if (el) {
            el.addEventListener('input', () => {
                const v = parseFloat(el.value);
                light.position[axis] = v;
                const valEl = document.getElementById(`scene-${name}-pos-${axis}-val`);
                if (valEl) valEl.textContent = v.toFixed(1);
            });
        }
    });
}

function _applyLightPreset(preset) {
    if (preset.key) {
        keyLight.intensity = preset.key.intensity;
        keyLight.color.set(preset.key.color);
        keyLight.position.set(...preset.key.pos);
    }
    if (preset.fill) {
        fillLight.intensity = preset.fill.intensity;
        fillLight.color.set(preset.fill.color);
        fillLight.position.set(...preset.fill.pos);
    }
    if (preset.back) {
        backLight.intensity = preset.back.intensity;
        backLight.color.set(preset.back.color);
        backLight.position.set(...preset.back.pos);
    }
    if (preset.ambient) {
        ambient.intensity = preset.ambient.intensity;
        ambient.color.set(preset.ambient.color);
    }
    if (preset.exposure !== undefined) {
        renderer.toneMappingExposure = preset.exposure;
    }
}

function _syncSceneUI() {
    // Sync light controls from current light state
    _syncLightGroupUI('key', keyLight);
    _syncLightGroupUI('fill', fillLight);
    _syncLightGroupUI('back', backLight);

    // Ambient
    const ambInt = document.getElementById('scene-ambient-intensity');
    const ambCol = document.getElementById('scene-ambient-color');
    if (ambInt) {
        ambInt.value = Math.round(ambient.intensity * 100);
        const v = document.getElementById('scene-ambient-intensity-val');
        if (v) v.textContent = ambient.intensity.toFixed(2);
    }
    if (ambCol) ambCol.value = '#' + ambient.color.getHexString();

    // Renderer
    const tmSel = document.getElementById('scene-tonemapping');
    if (tmSel) {
        for (const [name, val] of Object.entries(VIEWER_TONE_MAPPINGS)) {
            if (renderer.toneMapping === val) { tmSel.value = name; break; }
        }
    }
    const expEl = document.getElementById('scene-exposure');
    if (expEl) {
        expEl.value = Math.round(renderer.toneMappingExposure * 100);
        const v = document.getElementById('scene-exposure-val');
        if (v) v.textContent = renderer.toneMappingExposure.toFixed(2);
    }
    const bgEl = document.getElementById('scene-background');
    if (bgEl && scene.background) bgEl.value = '#' + scene.background.getHexString();

    // Camera
    const fovEl = document.getElementById('scene-fov');
    if (fovEl) {
        fovEl.value = camera.fov;
        const v = document.getElementById('scene-fov-val');
        if (v) v.textContent = Math.round(camera.fov) + '\u00B0';
    }
}

function _syncLightGroupUI(name, light) {
    const intEl = document.getElementById(`scene-${name}-intensity`);
    const colEl = document.getElementById(`scene-${name}-color`);
    const posXEl = document.getElementById(`scene-${name}-pos-x`);
    const posYEl = document.getElementById(`scene-${name}-pos-y`);
    const posZEl = document.getElementById(`scene-${name}-pos-z`);

    if (intEl) {
        intEl.value = Math.round(light.intensity * 100);
        const v = document.getElementById(`scene-${name}-intensity-val`);
        if (v) v.textContent = light.intensity.toFixed(2);
    }
    if (colEl) colEl.value = '#' + light.color.getHexString();
    if (posXEl) {
        posXEl.value = light.position.x;
        const v = document.getElementById(`scene-${name}-pos-x-val`);
        if (v) v.textContent = light.position.x.toFixed(1);
    }
    if (posYEl) {
        posYEl.value = light.position.y;
        const v = document.getElementById(`scene-${name}-pos-y-val`);
        if (v) v.textContent = light.position.y.toFixed(1);
    }
    if (posZEl) {
        posZEl.value = light.position.z;
        const v = document.getElementById(`scene-${name}-pos-z-val`);
        if (v) v.textContent = light.position.z.toFixed(1);
    }
}

function _gatherSceneSettings() {
    return {
        lighting: {
            key:     { intensity: keyLight.intensity, color: '#' + keyLight.color.getHexString(), pos: [keyLight.position.x, keyLight.position.y, keyLight.position.z] },
            fill:    { intensity: fillLight.intensity, color: '#' + fillLight.color.getHexString(), pos: [fillLight.position.x, fillLight.position.y, fillLight.position.z] },
            back:    { intensity: backLight.intensity, color: '#' + backLight.color.getHexString(), pos: [backLight.position.x, backLight.position.y, backLight.position.z] },
            ambient: { intensity: ambient.intensity, color: '#' + ambient.color.getHexString() },
        },
        renderer: {
            toneMapping: (() => {
                for (const [name, val] of Object.entries(VIEWER_TONE_MAPPINGS)) {
                    if (renderer.toneMapping === val) return name;
                }
                return 'ACESFilmic';
            })(),
            exposure: renderer.toneMappingExposure,
            background: '#' + (scene.background ? scene.background.getHexString() : '1a1a2e'),
        },
        camera: {
            fov: camera.fov,
        }
    };
}

function _applySmplSceneSettings(s) {
    if (!s || typeof s !== 'object') return;
    if (s.lighting) {
        if (s.lighting.key) {
            keyLight.intensity = s.lighting.key.intensity;
            keyLight.color.set(s.lighting.key.color);
            keyLight.position.set(...s.lighting.key.pos);
        }
        if (s.lighting.fill) {
            fillLight.intensity = s.lighting.fill.intensity;
            fillLight.color.set(s.lighting.fill.color);
            fillLight.position.set(...s.lighting.fill.pos);
        }
        if (s.lighting.back) {
            backLight.intensity = s.lighting.back.intensity;
            backLight.color.set(s.lighting.back.color);
            backLight.position.set(...s.lighting.back.pos);
        }
        if (s.lighting.ambient) {
            ambient.intensity = s.lighting.ambient.intensity;
            ambient.color.set(s.lighting.ambient.color);
        }
    }
    if (s.renderer) {
        if (s.renderer.toneMapping && VIEWER_TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) {
            renderer.toneMapping = VIEWER_TONE_MAPPINGS[s.renderer.toneMapping];
        }
        if (s.renderer.exposure !== undefined) {
            renderer.toneMappingExposure = s.renderer.exposure;
        }
        if (s.renderer.background) {
            scene.background.set(s.renderer.background);
        }
    }
    if (s.camera && s.camera.fov) {
        camera.fov = s.camera.fov;
        camera.updateProjectionMatrix();
    }
    _syncSceneUI();
}

async function _saveSmplSettings() {
    const btn = document.getElementById('smpl-save-settings');
    const genderSel = document.getElementById('smpl-body-gender');
    const opacityEl = document.getElementById('smpl-body-opacity');
    const colorEl = document.getElementById('smpl-body-color');
    const wireEl = document.getElementById('smpl-body-wireframe');
    const xOffsetEl = document.getElementById('smpl-body-xoffset');

    const body = {
        gender: genderSel ? genderSel.value : 'female',
        betas: _getSmplBetas(),
        opacity: opacityEl ? opacityEl.value / 100 : 1.0,
        color: colorEl ? colorEl.value : '#88aaff',
        wireframe: wireEl ? wireEl.checked : false,
        xoffset: xOffsetEl ? xOffsetEl.value / 100 : 1.0,
        scene: _gatherSceneSettings(),
    };

    try {
        if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Speichern...'; }
        const resp = await fetch('/api/settings/smpl/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await resp.json();
        if (data.ok) {
            if (btn) { btn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!'; btn.style.borderColor = 'var(--success)'; }
            setTimeout(() => {
                if (btn) { btn.innerHTML = '<i class="fas fa-save"></i> Einstellungen speichern'; btn.style.borderColor = ''; btn.disabled = false; }
            }, 2000);
        } else {
            throw new Error(data.error || 'Save failed');
        }
    } catch (e) {
        console.error('Failed to save SMPL settings:', e);
        if (btn) { btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Fehler!'; btn.disabled = false; }
        setTimeout(() => {
            if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Einstellungen speichern';
        }, 2000);
    }
}

// =========================================================================
// Debug access for Playwright tests
// =========================================================================
window.__viewer = {
    get scene() { return scene; },
    get bodyMesh() { return bodyMesh; },
    get garmentMeshes() { return garmentMeshes; },
    get garmentState() { return garmentState; },
    get selectedGarmentId() { return selectedGarmentId; },
    get clothMeshes() { return clothMeshes; },
    get smplGarmentMeshes() { return smplGarmentMeshes; },
    get smplBodyMesh() { return smplBodyMesh; },
    get camera() { return camera; },
    get controls() { return controls; },
    get rigifySkeleton() { return rigifySkeleton; },
    get isSkinned() { return isSkinned; },
    get selectedItem() { return _selectedItem; },
    getSelectableTargets,
    updateEquippedList,
    // Pattern Editor debug
    _buildBodyQueryString,
    peRegionGenerate,
    peGenerate3D,
    get peMode() { return peMode; },
    set peMode(v) { peMode = v; _peSetModeButtons(); },
    // Vertex Editor debug
    get veActive() { return veActive; },
    get veSelectedIndices() { return veSelectedIndices; },
    get veTargetMesh() { return veTargetMesh; },
    veEnterEditMode,
    veExitEditMode,
};

// =========================================================================
// Boot
// =========================================================================
init();
