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
import { detectBVHFormat, retargetBVHToDefClip } from './retarget.js';

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
let rigGroup = null;
let rigVisible = false;
let rigData = null;

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

    // Start render loop
    animate();

    // Load data
    loadMorphs();
    loadMesh();
    loadSkinWeights();
    loadDefSkeleton();
    loadWardrobe();
    loadAnimations();
    loadRig();
    connectWebSocket();

    // Rig toggle (floating button)
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigGroup) rigGroup.visible = rigVisible;
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

    if (mixer) mixer.update(dt);

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
// Animation UI
// =========================================================================
async function loadAnimations() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const panel = document.getElementById('animation-panel');
        panel.innerHTML = '';

        // API returns { categories: { Walk: [...], Dance: [...], ... } }
        const categories = data.categories || {};
        const allAnims = [];
        for (const [cat, list] of Object.entries(categories)) {
            for (const a of list) allAnims.push({ ...a, category: cat });
        }

        if (allAnims.length === 0) {
            panel.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;">No animations available</div>';
            return;
        }

        const select = document.createElement('select');
        select.className = 'viewer-select';
        select.id = 'animation-select';
        const none = document.createElement('option');
        none.value = '';
        none.textContent = '\u2014 Select Animation \u2014';
        select.appendChild(none);

        // Group by category
        for (const [cat, list] of Object.entries(categories)) {
            const group = document.createElement('optgroup');
            group.label = cat;
            for (const a of list) {
                const opt = document.createElement('option');
                opt.value = a.url;
                opt.textContent = `${a.name} (${a.frames} frames)`;
                group.appendChild(opt);
            }
            select.appendChild(group);
        }
        panel.appendChild(select);

        // Speed slider
        const speedRow = document.createElement('div');
        speedRow.className = 'anim-speed';
        const speedLabel = document.createElement('label');
        speedLabel.textContent = 'Speed: 1.0x';
        const speedSlider = document.createElement('input');
        speedSlider.type = 'range';
        speedSlider.min = 10;
        speedSlider.max = 300;
        speedSlider.value = 100;
        speedSlider.step = 10;
        speedSlider.addEventListener('input', () => {
            const speed = parseInt(speedSlider.value) / 100;
            speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`;
            if (mixer) mixer.timeScale = speed;
        });
        speedRow.appendChild(speedLabel);
        speedRow.appendChild(speedSlider);
        panel.appendChild(speedRow);

        // Controls
        const ctrls = document.createElement('div');
        ctrls.className = 'anim-controls';

        const playBtn = document.createElement('button');
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
        playBtn.title = 'Play/Pause';

        const stopBtn = document.createElement('button');
        stopBtn.innerHTML = '<i class="fas fa-stop"></i>';
        stopBtn.title = 'Stop';

        const timeline = document.createElement('input');
        timeline.type = 'range';
        timeline.min = 0;
        timeline.max = 100;
        timeline.value = 0;
        timeline.step = 1;

        ctrls.appendChild(playBtn);
        ctrls.appendChild(stopBtn);
        ctrls.appendChild(timeline);
        panel.appendChild(ctrls);

        let playing = false;

        select.addEventListener('change', () => {
            if (!select.value) {
                stopAnimation(true);
                return;
            }
            loadBVHAnimation(select.value);
        });

        playBtn.addEventListener('click', () => {
            if (!currentAction) return;
            playing = !playing;
            if (playing) {
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                currentAction.paused = true;
                playBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        });

        stopBtn.addEventListener('click', () => {
            stopAnimation();
            playBtn.innerHTML = '<i class="fas fa-play"></i>';
            playing = false;
            timeline.value = 0;
        });

        // Scrub timeline
        timeline.addEventListener('input', () => {
            if (currentAction && mixer) {
                const clip = currentAction.getClip();
                const time = (parseInt(timeline.value) / 100) * clip.duration;
                mixer.setTime(time);
            }
        });
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

let skelWrapper = null;

function loadBVHAnimation(url) {
    stopAnimation(true);

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

            // SkeletonHelper
            if (skeletonHelper) scene.remove(skeletonHelper);
            skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
            skeletonHelper.material.depthTest = false;
            skeletonHelper.material.depthWrite = false;
            skeletonHelper.material.color.set(0x00ffaa);
            skeletonHelper.material.linewidth = 2;
            skeletonHelper.renderOrder = 999;
            scene.add(skeletonHelper);

            // Play on SkinnedMesh
            mixer = new THREE.AnimationMixer(bodyMesh);
            currentAction = mixer.clipAction(clip);
            currentAction.play();
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
            scene.add(skeletonHelper);

            mixer = new THREE.AnimationMixer(rootBone);
            currentAction = mixer.clipAction(result.clip);
            currentAction.play();
        }
    }, undefined, (err) => {
        console.error('Failed to load BVH:', err);
    });
}

function stopAnimation(destroy = false) {
    if (currentAction) {
        currentAction.stop();
        if (destroy) currentAction = null;
    }
    if (mixer) {
        mixer.stopAllAction();
        if (destroy) mixer = null;
    }
    // Reset skinned mesh back to bind pose
    if (isSkinned && bodyMesh && bodyMesh.isSkinnedMesh) {
        bodyMesh.skeleton.pose();
    }
    if (destroy) {
        if (skelWrapper) {
            scene.remove(skelWrapper);
            skelWrapper = null;
        }
        if (skeletonHelper) {
            scene.remove(skeletonHelper);
            skeletonHelper = null;
        }
    }
}

// =========================================================================
// Rig skeleton visualization
// =========================================================================
async function loadRig() {
    try {
        const resp = await fetch('/api/character/rig/');
        rigData = await resp.json();
        if (!rigData.bones || rigData.bones.length === 0) {
            console.warn('No rig data available');
            return;
        }
        buildRigVisualization();
    } catch (e) {
        console.error('Failed to load rig:', e);
    }
}

function buildRigVisualization() {
    if (rigGroup) {
        scene.remove(rigGroup);
        rigGroup = null;
    }
    if (!rigData || !rigData.bones) return;

    rigGroup = new THREE.Group();
    rigGroup.visible = rigVisible;

    const boneMat = new THREE.LineBasicMaterial({ color: 0x00ff88, linewidth: 2, depthTest: false });
    const jointMat = new THREE.MeshBasicMaterial({ color: 0x00ffaa, depthTest: false });
    const jointGeo = new THREE.SphereGeometry(0.006, 6, 4);

    // Only show deform bones for cleaner display
    const deformBones = rigData.bones.filter(b => b.deform);

    deformBones.forEach(bone => {
        const h = bone.head;
        const t = bone.tail;
        // Convert Blender coords to Three.js: (x,y,z) -> (x,z,-y)
        const head = new THREE.Vector3(h[0], h[2], -h[1]);
        const tail = new THREE.Vector3(t[0], t[2], -t[1]);

        // Bone line
        const lineGeo = new THREE.BufferGeometry().setFromPoints([head, tail]);
        const line = new THREE.Line(lineGeo, boneMat);
        rigGroup.add(line);

        // Joint sphere at head
        const joint = new THREE.Mesh(jointGeo, jointMat);
        joint.position.copy(head);
        rigGroup.add(joint);
    });

    scene.add(rigGroup);
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
// Boot
// =========================================================================
init();
