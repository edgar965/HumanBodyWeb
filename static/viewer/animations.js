/**
 * HumanBody Animations — Three.js viewer with BVH animation tree + playback.
 * Loads the character mesh statically, plays BVH skeletons overlaid.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl } from './retarget_hybrid.js?v=32';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js?v=2';

// =========================================================================
// Tone mapping lookup (for scene settings)
// =========================================================================
const TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

// =========================================================================
// Global state
// =========================================================================
let scene, camera, renderer, controls;
let bodyMesh = null;
let bodyGeometry = null;
let clock = new THREE.Clock();
let frameCount = 0;
let fpsAccum = 0;

// Animation
let mixer = null;
let currentAction = null;
let skeletonHelper = null;
let playing = false;
const bvhLoader = new BVHLoader();

// Rigify Skeleton + Skinning
let rigifySkeletonData = null;
let skinWeightData = null;
let rigifySkeleton = null;
let isSkinned = false;

// Rig
let rigVisible = false;

// Skin colors per ethnicity (from API)
let skinColors = {};

// =========================================================================
// Initialization
// =========================================================================
async function init() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
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

    // Camera
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

    // Lighting
    const keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    scene.add(backLight);

    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);

    // Apply scene settings from localStorage
    applySceneSettings(keyLight, fillLight, backLight, ambient);

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

    // Animation controls
    bindPlaybackControls();

    // Demo animation button — Play/Pause toggle
    const demoBtn = document.getElementById('play-demo-anim');
    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            if (!currentAction) {
                loadBVHAnimation('/api/character/bvh/Mixamo/Catwalk_Idle_02/', 'Catwalk Idle 02', 0);
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            } else if (playing) {
                currentAction.paused = true;
                playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i>';
                demoBtn.classList.remove('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            } else {
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

    // Rig toggle — single SkeletonHelper from rigifySkeleton
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigVisible) {
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

    // Save buttons
    initSaveButtons();

    // Start render loop
    animate();

    // Load data
    loadMesh();
    loadRigifySkeleton();
    loadSkinWeights();
    loadSkinColors();
    loadAnimationTree();
    setupAnimManagement();
}

function onResize() {
    const container = renderer.domElement.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
}

function animate() {
    requestAnimationFrame(animate);
    const dt = clock.getDelta();
    controls.update();

    if (mixer && playing) mixer.update(dt);

    renderer.render(scene, camera);

    // FPS counter
    frameCount++;
    fpsAccum += dt;
    if (fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = frameCount;
        frameCount = 0;
        fpsAccum = 0;
    }
}

// =========================================================================
// Scene settings from localStorage
// =========================================================================
function applySceneSettings(keyLight, fillLight, backLight, ambient) {
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
            if (s.renderer.toneMapping && TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) {
                renderer.toneMapping = TONE_MAPPINGS[s.renderer.toneMapping];
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
        }
    } catch (e) { /* ignore */ }
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
    if (!Object.keys(skinColors).length) return;
    const colors = skinColors['Caucasian'];  // default body type is Female_Caucasian
    const mat = getSkinMat();
    if (colors && mat) {
        mat.color.setRGB(
            Math.pow(colors[0], 1/2.2),
            Math.pow(colors[1], 1/2.2),
            Math.pow(colors[2], 1/2.2)
        );
    }
}

async function loadSkinColors() {
    try {
        const resp = await fetch('/api/character/morphs/');
        const data = await resp.json();
        skinColors = data.skin_colors || {};
        applySkinColor();
    } catch (e) { /* optional */ }
}

async function loadMesh() {
    try {
        const resp = await fetch('/api/character/mesh/');
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        document.getElementById('vertex-count').textContent =
            data.vertex_count.toLocaleString();

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

        const groups = data.groups || [];

        // Use server-computed normals (quad-topology based, no triangulation artifacts)
        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

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

        document.getElementById('vertex-count').textContent =
            geo.attributes.position.count.toLocaleString();

        applySceneSkinSettings();
        applySkinColor();
        onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

// =========================================================================
// Animation tree
// =========================================================================
async function loadAnimationTree() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('anim-tree');
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:16px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'anim-category';
            catDiv.dataset.category = cat;

            const header = document.createElement('div');
            header.className = 'anim-category-header';
            header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
                <span>${cat}</span>
                <span class="cat-count">${anims.length}</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            // Right-click on folder
            header.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                _animCtxTarget = { type: 'folder', category: cat };
                showAnimCtx('anim-ctx-folder', e.clientX, e.clientY);
            });
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'anim-category-body';

            anims.forEach(anim => {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.dataset.url = anim.url;
                item.dataset.category = cat;
                item.dataset.name = anim.name;
                item.innerHTML = `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
                item.addEventListener('click', () => {
                    // Deselect all
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    loadBVHAnimation(anim.url, anim.name, anim.frames);
                });
                // Right-click on file
                item.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    _animCtxTarget = { type: 'file', category: cat, name: anim.name, url: anim.url };
                    showAnimCtx('anim-ctx-file', e.clientX, e.clientY);
                });
                body.appendChild(item);
            });

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        });
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

// =========================================================================
// Animation file management
// =========================================================================
let _animCtxTarget = null;

function showAnimCtx(menuId, x, y) {
    document.querySelectorAll('.anim-ctx').forEach(m => m.style.display = 'none');
    const menu = document.getElementById(menuId);
    if (!menu) return;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

async function bvhManage(action, data) {
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

function setupAnimManagement() {
    // Close context menus on click
    document.addEventListener('click', () => {
        document.querySelectorAll('.anim-ctx').forEach(m => m.style.display = 'none');
    });

    // File context menu actions
    document.querySelectorAll('#anim-ctx-file .anim-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _animCtxTarget;
            if (!t) return;
            const action = item.dataset.action;

            if (action === 'play') {
                loadBVHAnimation(t.url, t.name, 0);
            } else if (action === 'rename') {
                const newName = prompt('Neuer Name:', t.name);
                if (newName && newName !== t.name) {
                    const r = await bvhManage('rename', { category: t.category, name: t.name, new_name: newName });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'move') {
                const newCat = prompt('In welchen Ordner verschieben?', t.category);
                if (newCat && newCat !== t.category) {
                    const r = await bvhManage('move', { category: t.category, name: t.name, new_category: newCat });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'delete') {
                if (confirm(`"${t.name}" wirklich loeschen?`)) {
                    const r = await bvhManage('delete', { category: t.category, name: t.name });
                    if (r?.ok) loadAnimationTree();
                }
            }
        });
    });

    // Folder context menu actions
    document.querySelectorAll('#anim-ctx-folder .anim-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _animCtxTarget;
            if (!t) return;
            const action = item.dataset.action;

            if (action === 'rename-folder') {
                const newName = prompt('Neuer Ordnername:', t.category);
                if (newName && newName !== t.category) {
                    const r = await bvhManage('rename_folder', { category: t.category, new_name: newName });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'new-folder') {
                const name = prompt('Name des neuen Unterordners:');
                if (name) {
                    const r = await bvhManage('create_folder', { folder_name: name });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'delete-folder') {
                if (confirm(`Ordner "${t.category}" wirklich loeschen?\n(Nur wenn leer)`)) {
                    const r = await bvhManage('delete_folder', { category: t.category });
                    if (r?.ok) loadAnimationTree();
                }
            }
        });
    });

    // Toolbar buttons
    document.getElementById('anim-new-folder')?.addEventListener('click', async () => {
        const name = prompt('Name des neuen Ordners:');
        if (name) {
            const r = await bvhManage('create_folder', { folder_name: name });
            if (r?.ok) loadAnimationTree();
        }
    });

    document.getElementById('anim-rename')?.addEventListener('click', () => {
        const active = document.querySelector('.anim-item.active');
        if (active) {
            const cat = active.dataset.category;
            const name = active.dataset.name;
            const newName = prompt('Neuer Name:', name);
            if (newName && newName !== name) {
                bvhManage('rename', { category: cat, name, new_name: newName }).then(r => { if (r?.ok) loadAnimationTree(); });
            }
        } else {
            alert('Bitte zuerst eine Animation auswaehlen.');
        }
    });

    document.getElementById('anim-move')?.addEventListener('click', () => {
        const active = document.querySelector('.anim-item.active');
        if (active) {
            const cat = active.dataset.category;
            const name = active.dataset.name;
            const newCat = prompt('In welchen Ordner verschieben?', cat);
            if (newCat && newCat !== cat) {
                bvhManage('move', { category: cat, name, new_category: newCat }).then(r => { if (r?.ok) loadAnimationTree(); });
            }
        } else {
            alert('Bitte zuerst eine Animation auswaehlen.');
        }
    });

    document.getElementById('anim-delete')?.addEventListener('click', () => {
        const active = document.querySelector('.anim-item.active');
        if (active) {
            const cat = active.dataset.category;
            const name = active.dataset.name;
            if (confirm(`"${name}" wirklich loeschen?`)) {
                bvhManage('delete', { category: cat, name }).then(r => { if (r?.ok) loadAnimationTree(); });
            }
        } else {
            alert('Bitte zuerst eine Animation auswaehlen.');
        }
    });

    document.getElementById('anim-refresh')?.addEventListener('click', () => loadAnimationTree());

    // Help dropdown + modal
    const helpDD = document.getElementById('anim-help-dropdown');
    const helpMenu = document.getElementById('anim-help-menu');
    document.getElementById('anim-help-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        helpMenu.style.display = helpMenu.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', () => { if (helpMenu) helpMenu.style.display = 'none'; });
    document.getElementById('anim-help-animations')?.addEventListener('click', () => {
        helpMenu.style.display = 'none';
        document.getElementById('anim-help-modal')?.classList.add('open');
    });
    document.getElementById('anim-help-close')?.addEventListener('click', () => {
        document.getElementById('anim-help-modal')?.classList.remove('open');
    });
    document.getElementById('anim-help-modal')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) e.currentTarget.classList.remove('open');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return;
        if (e.key === 'F2') {
            e.preventDefault();
            document.getElementById('anim-rename')?.click();
        }
        if (e.key === 'Delete') {
            const active = document.querySelector('.anim-item.active');
            if (active) {
                e.preventDefault();
                document.getElementById('anim-delete')?.click();
            }
        }
    });
}

// =========================================================================
// DEF Skeleton + Skin Weights
// =========================================================================

async function loadRigifySkeleton() {
    try {
        const resp = await fetch('/api/character/rigify-skeleton/');
        if (resp.ok) {
            rigifySkeletonData = await resp.json();
            console.log(`DEF skeleton loaded: ${rigifySkeletonData.bone_count} bones`);
        }
    } catch (e) {
        console.warn('DEF skeleton not available:', e);
    }
}

async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) skinWeightData = await resp.json();
    } catch (e) {
        console.warn('Skin weights not available:', e);
    }
}

// buildRigifySkeleton() imported from rigify_skeleton_builder.js

function convertToRigifySkinnedMesh(rigifySkel, swData) {
    if (isSkinned || !bodyMesh || !bodyGeometry) return;

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

    bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
    bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

    rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, swData);

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
    console.log('SkinnedMesh created:', bodyMesh.isSkinnedMesh, 'bones:', rigifySkeleton.skeleton.bones.length);
}

// Retarget via server-side API (retarget_hybrid.js)

// =========================================================================
// BVH animation playback
// =========================================================================
// Skeleton wrapper for scaling
let skelWrapper = null;

async function loadBVHAnimation(url, name, fc) {
    stopAnimation(true);

    document.getElementById('anim-info').textContent = `Lade ${name}...`;

    if (rigifySkeletonData && skinWeightData && bodyMesh) {
        // Server-side retarget path: skin mesh + retarget BVH via API
        if (!isSkinned) convertToRigifySkinnedMesh(null, skinWeightData);

        let bodyH = 1.68;
        const bb = new THREE.Box3().setFromObject(bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;

        try {
            const clip = await fetchRetargetedClipFromUrl(url, rigifySkeleton, { bodyHeight: bodyH });

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

            // Play retargeted clip on the SkinnedMesh
            mixer = new THREE.AnimationMixer(bodyMesh);
            const ss = document.getElementById('anim-speed');
            if (ss) mixer.timeScale = parseInt(ss.value) / 100;
            currentAction = mixer.clipAction(clip);
            currentAction.play();
            playing = true;

            document.getElementById('anim-play').innerHTML = '<i class="fas fa-pause"></i>';
            document.getElementById('anim-info').textContent =
                `${name} — ${fc}f — ${clip.duration.toFixed(1)}s`;
        } catch (e) {
            console.error('Server retarget failed:', e);
            document.getElementById('anim-info').textContent = `Fehler: ${name}`;
        }
    } else {
        // Fallback: BVH skeleton overlay (no skinning data available)
        bvhLoader.load(url, (result) => {
            const bones = result.skeleton.bones;
            if (bones.length === 0) return;

            const rootBone = bones[0];
            rootBone.updateWorldMatrix(true, true);
            const skelBox = new THREE.Box3();
            const tmpVec = new THREE.Vector3();
            bones.forEach(b => {
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

            skelWrapper = new THREE.Group();
            const scale = bodyHeight / Math.max(skelHeight, 0.01);
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

            document.getElementById('anim-play').innerHTML = '<i class="fas fa-pause"></i>';
            document.getElementById('anim-info').textContent =
                `${name} — ${fc}f — ${result.clip.duration.toFixed(1)}s`;
        }, undefined, (err) => {
            console.error('Failed to load BVH:', err);
            document.getElementById('anim-info').textContent = `Fehler: ${name}`;
        });
    }
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
    // Reset DEF skeleton to rest pose so mesh returns to T-pose
    if (isSkinned && rigifySkeleton) {
        rigifySkeleton.skeleton.pose();
    }
    // Clean up animation skeleton; recreate from DEF skeleton if rig visible
    if (skelWrapper) { scene.remove(skelWrapper); skelWrapper = null; }
    if (skeletonHelper) { scene.remove(skeletonHelper); skeletonHelper = null; }
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

function bindPlaybackControls() {
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');
    const speedSlider = document.getElementById('anim-speed');
    const speedLabel = document.getElementById('speed-label');

    if (speedSlider) {
        speedSlider.addEventListener('input', () => {
            const speed = parseInt(speedSlider.value) / 100;
            speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`;
            if (mixer) mixer.timeScale = speed;
        });
    }

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

    stopBtn.addEventListener('click', () => {
        stopAnimation();
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
        timeline.value = 0;
    });

    timeline.addEventListener('input', () => {
        if (currentAction && mixer) {
            const wasPaused = currentAction.paused;
            currentAction.paused = false;
            const clip = currentAction.getClip();
            const time = (parseInt(timeline.value) / 100) * clip.duration;
            mixer.setTime(time);
            currentAction.paused = wasPaused;
        }
    });
}

// (Rig visualization now uses SkeletonHelper from rigifySkeleton — no separate rigGroup)

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

function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// =========================================================================
// Save Model (scene + model state from localStorage)
// =========================================================================
let currentPresetName = '';

function gatherModelState() {
    // Model body/cloth/hair from localStorage (set by Konfiguration page)
    let model = {};
    const saved = localStorage.getItem('humanbody_current_model');
    if (saved) {
        try { model = JSON.parse(saved); } catch (e) { /* ignore */ }
    }
    // Scene settings from localStorage
    const sceneSaved = localStorage.getItem('humanbody_scene_settings');
    if (sceneSaved) {
        try { model.scene = JSON.parse(sceneSaved); } catch (e) { /* ignore */ }
    }
    return model;
}

function getCSRFToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

async function saveModel(name) {
    const data = gatherModelState();
    data.name = name;
    try {
        const resp = await fetch('/api/character/model/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
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

async function loadDefaultPresetName() {
    try {
        const resp = await fetch('/api/settings/humanbody/');
        if (resp.ok) {
            const s = await resp.json();
            if (s.animations) currentPresetName = s.animations;
            // Apply rig visibility from settings
            if (s.show_rig_animations) {
                rigVisible = true;
                const rigToggle = document.getElementById('rig-toggle');
                if (rigToggle) rigToggle.classList.add('active');
            }
            // Auto-play default animation
            if (s.default_anim_animations) {
                const waitForMesh = async () => {
                    const maxWait = 15000;
                    const start = Date.now();
                    while (!bodyMesh && Date.now() - start < maxWait) {
                        await new Promise(r => setTimeout(r, 200));
                    }
                    if (bodyMesh) {
                        await new Promise(r => setTimeout(r, 1000));
                        loadBVHAnimation(s.default_anim_animations, 'Default', 0);
                    }
                };
                waitForMesh();
            }
        }
    } catch (e) { /* ignore */ }
}

function initSaveButtons() {
    loadDefaultPresetName();
    const saveBtn = document.getElementById('save-model-btn');
    const saveAsBtn = document.getElementById('save-model-as-btn');

    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            if (!currentPresetName) {
                saveAsBtn?.click();
                return;
            }
            const ok = await saveModel(currentPresetName);
            if (ok) {
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                setTimeout(() => { saveBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 1500);
            }
        });
    }

    if (saveAsBtn) {
        saveAsBtn.addEventListener('click', async () => {
            const name = prompt('Modell-Name:', currentPresetName || 'Mein Modell');
            if (!name || !name.trim()) return;
            const ok = await saveModel(name.trim());
            if (ok) {
                saveAsBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                setTimeout(() => { saveAsBtn.innerHTML = '<i class="fas fa-file-export"></i> Speichern unter'; }, 1500);
            }
        });
    }
}

// =========================================================================
// Boot
// =========================================================================
init();
