/**
 * HumanBody Character Viewer — Three.js renderer + morph UI + wardrobe + animations.
 * Single-file ES module using importmap.
 *
 * Skinning: 176-bone DEF skeleton (Blender Rigify) with BVH→DEF retargeting.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { detectBVHFormat, retargetBVHToDefClip } from './retarget_hybrid.js?v=7';

// =========================================================================
// Global state
// =========================================================================
let scene, camera, renderer, controls;
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

// Wardrobe
const loadedAssets = {};  // name -> THREE.Object3D
const gltfLoader = new GLTFLoader();
const bvhLoader = new BVHLoader();

// GPU Skinning — DEF skeleton
let skinWeightData = null;   // Raw data from /api/character/skin-weights/
let defSkeletonData = null;  // Raw JSON from /api/character/def-skeleton/
let defSkeleton = null;      // { skeleton, rootBone, bones, boneByName }
let isSkinned = false;       // Flag: Mesh is already SkinnedMesh

// Rig skeleton visualization
let rigVisible = false;

// Cloth — multiple pieces keyed by region
const clothMeshes = {};  // region -> THREE.Mesh
const clothParams = {};  // region -> { params, color }

// Hair
let hairMesh = null;
let hairColorData = {};  // name -> [r,g,b] (linear sRGB)

// Current preset name (set on load/save)
let currentPresetName = '';

// =========================================================================
// Expanded panels from settings
// =========================================================================
function applyExpandedPanels() {
    fetch('/api/settings/humanbody/')
        .then(r => r.json())
        .then(s => {
            const expanded = s.expanded_panels_config;
            if (!Array.isArray(expanded)) return;
            document.querySelectorAll('.panel-section[data-panel-key]').forEach(panel => {
                const key = panel.dataset.panelKey;
                if (expanded.includes(key)) {
                    panel.classList.remove('collapsed');
                } else {
                    panel.classList.add('collapsed');
                }
            });
        })
        .catch(() => {});
}

// =========================================================================
// Initialization
// =========================================================================
function init() {
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

    // Apply scene settings from localStorage (configured on /humanbody/scene/)
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

    // Apply expanded panels from settings
    applyExpandedPanels();

    // Start render loop
    animate();

    // Load data
    loadMorphs();
    loadMesh();
    loadSkinWeights();
    loadDefSkeleton();
    loadWardrobe();
    loadAnimations();
    loadClothUI();
    loadHairUI();
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
                demoBtn.innerHTML = '<i class="fas fa-pause"></i> Catwalk';
                demoBtn.classList.add('active');
            } else if (playing) {
                // Pause
                currentAction.paused = true;
                playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i> Catwalk';
                demoBtn.classList.remove('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            } else {
                // Resume
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
                playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i> Catwalk';
                demoBtn.classList.add('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }
        });
    }

    // Rig toggle — single SkeletonHelper from defSkeleton (animates automatically)
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigVisible) {
                // Create helper if needed (from DEF skeleton when available)
                if (!skeletonHelper && defSkeleton) {
                    skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
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

async function loadMesh() {
    try {
        const resp = await fetch('/api/character/mesh/');
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        vertexCount = data.vertex_count;
        document.getElementById('vertex-count').textContent = vertexCount.toLocaleString();

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

        document.getElementById('vertex-count').textContent =
            geo.attributes.position.count.toLocaleString();

        applySceneSkinSettings();
        onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

function updateMeshVertices(float32Buffer) {
    if (!bodyGeometry) return;
    const positions = bodyGeometry.attributes.position;
    const newData = new Float32Array(float32Buffer);
    blenderToThreeCoords(newData);
    positions.array.set(newData);
    positions.needsUpdate = true;
    bodyGeometry.computeBoundingSphere();
}

// =========================================================================
// GPU Skinning — 176-bone DEF skeleton + BVH retargeting
// =========================================================================

async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) skinWeightData = await resp.json();
    } catch (e) {
        console.warn('Skin weights not available:', e);
    }
}

async function loadDefSkeleton() {
    try {
        const resp = await fetch('/api/character/def-skeleton/');
        if (resp.ok) {
            defSkeletonData = await resp.json();
            console.log(`DEF skeleton loaded: ${defSkeletonData.bone_count} bones`);
        }
    } catch (e) {
        console.warn('DEF skeleton not available:', e);
    }
}

/**
 * Build 176-bone THREE.Skeleton from DEF skeleton data + skin weight bone order.
 * Bone indices match skinWeightData.bone_names (authoritative for skinIndex).
 */
function buildDefSkeleton(skelData, swData) {
    // Build lookup: bone name -> skeleton data entry
    const skelByName = {};
    for (const b of skelData.bones) {
        skelByName[b.name] = b;
    }

    const bones = [];
    const boneByName = {};
    let rootBone = null;

    // Create bones in skin weight order (= authoritative index order)
    // Sanitize names: Three.js PropertyBinding uses dots as separators,
    // so bone names like "DEF-upper_arm.L" break track name parsing.
    for (const name of swData.bone_names) {
        const bone = new THREE.Bone();
        bone.name = name.replace(/\./g, '_');  // DEF-upper_arm.L -> DEF-upper_arm_L
        bones.push(bone);
        boneByName[name] = bone;  // Original name as key for mapping lookups
    }

    // Set local transforms and build parent-child hierarchy
    for (let i = 0; i < swData.bone_names.length; i++) {
        const name = swData.bone_names[i];
        const bone = bones[i];
        const data = skelByName[name];

        if (!data) continue;

        // Convert Blender local position (x,y,z) -> Three.js (x,z,-y)
        const p = data.local_position;
        bone.position.set(p[0], p[2], -p[1]);

        // Convert Blender quaternion [w,x,y,z] -> Three.js Quaternion(x,z,-y,w)
        const q = data.local_quaternion;
        bone.quaternion.set(q[1], q[3], -q[2], q[0]);

        // Parent-child (lookup by original name)
        if (data.parent && boneByName[data.parent]) {
            boneByName[data.parent].add(bone);
        } else {
            // Root bone (no skinning parent)
            if (!rootBone) rootBone = bone;
        }
    }

    // Collect orphan roots (bones without skinning parent that aren't the main root)
    for (let i = 0; i < bones.length; i++) {
        const name = swData.bone_names[i];
        const data = skelByName[name];
        if (!data) continue;
        if (!data.parent && bones[i] !== rootBone) {
            // Attach to main root
            if (rootBone) rootBone.add(bones[i]);
        }
    }

    if (!rootBone && bones.length > 0) rootBone = bones[0];

    // Update world matrices before creating skeleton
    rootBone.updateWorldMatrix(true, true);

    const skeleton = new THREE.Skeleton(bones);

    return { skeleton, rootBone, bones, boneByName };
}

/**
 * Convert bodyMesh to SkinnedMesh using DEF skeleton.
 * Skin indices come directly from skin_weights.json (no remapping needed).
 */
function convertToDefSkinnedMesh(defSkel, swData) {
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
    defSkeleton = buildDefSkeleton(defSkeletonData, swData);

    // Replace Mesh with SkinnedMesh
    const mat = bodyMesh.material;
    const pos = bodyMesh.position.clone();
    const vis = bodyMesh.visible;
    scene.remove(bodyMesh);

    bodyMesh = new THREE.SkinnedMesh(bodyGeometry, mat);
    bodyMesh.position.copy(pos);
    bodyMesh.visible = vis;
    bodyMesh.add(defSkeleton.rootBone);
    bodyMesh.bind(defSkeleton.skeleton);

    scene.add(bodyMesh);
    isSkinned = true;
    console.log('SkinnedMesh created:', bodyMesh.isSkinnedMesh,
                'bones:', defSkeleton.skeleton.bones.length,
                'skinIndex:', !!bodyGeometry.attributes.skinIndex,
                'skinWeight:', !!bodyGeometry.attributes.skinWeight);
}

/**
 * Ensure body mesh is converted to SkinnedMesh (if skeleton data available).
 * Call before creating cloth/hair SkinnedMeshes that share the skeleton.
 */
function ensureSkinned() {
    if (isSkinned) return;
    if (!defSkeletonData || !skinWeightData || !bodyMesh) return;
    convertToDefSkinnedMesh(null, skinWeightData);
}

// Retarget imports from shared module (retarget.js)

// =========================================================================
// WebSocket for live morphing
// =========================================================================
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/character/`;

    ws = new WebSocket(url);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
        wsReady = true;
        document.getElementById('ws-status').textContent = 'Connected';
        document.getElementById('ws-status').className = 'connected';
    };

    ws.onclose = () => {
        wsReady = false;
        document.getElementById('ws-status').textContent = 'Disconnected';
        document.getElementById('ws-status').className = 'disconnected';
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
        const resp = await fetch('/api/character/morphs/');
        const data = await resp.json();

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
            }
        });

        // Gender slider
        const genderSlider = document.getElementById('gender-slider');
        const genderVal = document.getElementById('gender-val');
        genderSlider.addEventListener('input', () => {
            const v = parseInt(genderSlider.value);
            genderVal.textContent = v;
            wsSend({ type: 'gender', value: v / 100.0 });
        });

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
            // Reset all sliders to 0
            panel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                s.nextElementSibling.textContent = '0';
            });
            genderSlider.value = 0;
            genderVal.textContent = '0';
            wsSend({ type: 'reset', body_type: select.value });
        });

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
    } else {
        // Load GLB
        btn.textContent = 'Loading...';
        gltfLoader.load(url, (gltf) => {
            const model = gltf.scene;
            scene.add(model);
            loadedAssets[name] = model;
            btn.classList.add('active');
            btn.textContent = name.replace(/_/g, ' ');
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
            }
        });
    }
}

let skelWrapper = null;

function loadBVHAnimation(url, name, fc) {
    stopAnimation(true);

    const info = document.getElementById('anim-info');
    if (info) info.textContent = `Lade ${name || 'Animation'}...`;

    bvhLoader.load(url, (result) => {
        const bvhBones = result.skeleton.bones;
        if (bvhBones.length === 0) return;

        // DEF skeleton path: retarget BVH to 176-bone DEF skeleton
        if (defSkeletonData && skinWeightData && bodyMesh) {
            // Convert mesh to SkinnedMesh first (builds defSkeleton internally)
            if (!isSkinned) {
                convertToDefSkinnedMesh(null, skinWeightData);
            }

            const format = detectBVHFormat(bvhBones);
            console.log(`BVH format: ${format}, retargeting to DEF skeleton...`);
            const clip = retargetBVHToDefClip(result, defSkeleton, format, { bodyMesh });
            console.log(`Retargeted clip: ${clip.tracks.length} tracks, ${clip.duration.toFixed(2)}s`);

            // Ensure SkeletonHelper exists for DEF skeleton
            if (!skeletonHelper) {
                skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
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
        } else {
            // Fallback: separate BVH skeleton visualization (no mesh deformation)
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
        }

        const playBtn = document.getElementById('anim-play');
        if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
        if (info) info.textContent = `${name || 'Animation'} — ${fc || '?'}f — ${result.clip.duration.toFixed(1)}s`;
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
    if (rigVisible && defSkeleton) {
        skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
        skeletonHelper.material.depthTest = false;
        skeletonHelper.material.depthWrite = false;
        skeletonHelper.material.color.set(0x00ffaa);
        skeletonHelper.material.linewidth = 2;
        skeletonHelper.renderOrder = 999;
        scene.add(skeletonHelper);
    }
    playing = false;
}

// (Rig visualization now uses SkeletonHelper from defSkeleton — no separate rigGroup)

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
        if (isSkinned && defSkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(defSkeleton.skeleton, bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        clothMeshes[key] = mesh;
        clothParams[key] = { params, color: '#' + mesh.material.color.getHexString() };
        scene.add(mesh);

        console.log(`Cloth ${key}: ${data.vertex_count} verts, ${data.face_count} tris, skinned=${mesh.isSkinnedMesh || false}`);
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
    }
}

function removeAllCloth() {
    for (const key of Object.keys(clothMeshes)) {
        removeClothRegion(key);
    }
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
        if (isSkinned && defSkeleton && skinWeightData) {
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
        console.log('Hair loaded:', url, 'skinned=' + (isSkinned && defSkeleton ? 'yes' : 'no'));
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
        skinnedChild.bind(defSkeleton.skeleton, bodyMesh.bindMatrix);
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
    }
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
// Scene settings from /humanbody/scene/ page (localStorage)
// =========================================================================
const VIEWER_TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

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
            if (s.skin.color) mat.color.set(s.skin.color);
            if (s.skin.roughness !== undefined) mat.roughness = s.skin.roughness;
            if (s.skin.metalness !== undefined) mat.metalness = s.skin.metalness;
        }
    } catch (e) { /* ignore */ }
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
    const fileInput = document.getElementById('load-preset-file');
    if (!btn || !fileInput) return;

    btn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const preset = JSON.parse(e.target.result);
                applyModelPreset(preset);
            } catch (err) {
                console.error('Invalid preset JSON:', err);
            }
        };
        reader.readAsText(file);
        fileInput.value = '';  // allow re-selecting same file
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

    try {
        // Determine default settings from settings API
        let presetName = 'femaleWithClothes';
        let showRig = false;
        let defaultAnim = '';
        try {
            const settingsResp = await fetch('/api/settings/humanbody/');
            if (settingsResp.ok) {
                const s = await settingsResp.json();
                if (s.config) presetName = s.config;
                showRig = !!s.show_rig_config;
                defaultAnim = s.default_anim_config || '';
            }
        } catch (e) { /* fallback to default */ }

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
        console.log(`Default preset loaded: ${presetName}`);

        // Auto-play default animation after preset is applied
        if (defaultAnim) {
            setTimeout(() => {
                loadBVHAnimation(defaultAnim, 'Default', 0);
                const demoBtn = document.getElementById('play-demo-anim');
                if (demoBtn) {
                    demoBtn.innerHTML = '<i class="fas fa-pause"></i> Catwalk';
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

    // 2. Gender
    const genderSlider = document.getElementById('gender-slider');
    const genderVal = document.getElementById('gender-val');
    if (genderSlider && preset.gender !== undefined) {
        genderSlider.value = preset.gender;
        if (genderVal) genderVal.textContent = preset.gender;
        genderSlider.dispatchEvent(new Event('input'));
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

    // 5. Cloth — generate one or more cloth pieces
    if (preset.cloth) {
        removeAllCloth();
        const clothList = Array.isArray(preset.cloth) ? preset.cloth : [preset.cloth];
        clothList.forEach((c, i) => {
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
        const tpl = last.template || {
            TOP: 'TPL_TSHIRT', PANTS: 'TPL_PANTS',
            SKIRT: 'TPL_SKIRT', DRESS: 'TPL_DRESS'
        }[last.region] || 'TPL_TSHIRT';
        if (tplSelect) {
            tplSelect.value = tpl;
            tplSelect.dispatchEvent(new Event('change'));
        }
        const tight = last.tightness !== undefined ? last.tightness : 0.5;
        if (tplTight) { tplTight.value = Math.round(tight * 100); }
        if (tplTightVal) tplTightVal.textContent = tight.toFixed(2);
        if (colorPicker && last.color) colorPicker.value = last.color;
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

    // Gender
    const genderSlider = document.getElementById('gender-slider');
    if (genderSlider) state.gender = parseInt(genderSlider.value);

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
// Boot
// =========================================================================
init();
