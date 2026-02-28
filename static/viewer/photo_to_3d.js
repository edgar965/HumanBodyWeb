/**
 * Photo To 3D — Two models side-by-side:
 *   Left:  HumanBody (our morph system)
 *   Right: SMPL-X (academic body model with shape betas)
 *
 * Photo analysis sets SMPL-X betas → both models update.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// =========================================================================
// Helpers
// =========================================================================
function base64ToFloat32(b64) {
    const bin = atob(b64);
    const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Float32Array(u8.buffer);
}
function base64ToUint32(b64) {
    const bin = atob(b64);
    const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Uint32Array(u8.buffer);
}
function base64ToUint16(b64) {
    const bin = atob(b64);
    const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Uint16Array(u8.buffer);
}
function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1], z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// =========================================================================
// Materials
// =========================================================================
const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true },
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },
];

// =========================================================================
// Global state
// =========================================================================
const API = '/api/character';
let scene, camera, renderer, controls;
let clock = new THREE.Clock();
let frameCount = 0, fpsAccum = 0;

// --- HumanBody model (left) ---
let bodyMesh = null;
let bodyGeometry = null;
let skeletonHelper = null;
let rigVisible = false;
let defSkeletonData = null;
let defSkeleton = null;
let skinWeightData = null;
const MODEL_OFFSET_X = -0.7;   // HumanBody shifted left

// --- SMPL-X model (right) ---
let smplxGroup = null;          // THREE.Group holding mesh + skeleton
let smplxSkinnedMesh = null;
let smplxSkelHelper = null;
let smplxRigVisible = false;
let smplxBetas = new Array(10).fill(0);
let smplxExpr = new Array(10).fill(0);
let smplxGender = 'female';
const SMPLX_OFFSET_X = 0.7;    // SMPL-X shifted right
let smplxUpdateTimer = null;

// --- Morph state (HumanBody) ---
let currentBodyType = 'Female_Caucasian';
let morphValues = {};
let metaValues = {};
let skinColors = {};
let morphsData = null;
let meshUpdateTimer = null;
let meshUpdatePending = false;

// SMPL-X beta labels (common body shape interpretations)
const SMPLX_BETA_LABELS = [
    'Stature',      // β0: overall height/size
    'Weight',       // β1: heaviness
    'Proportions',  // β2: limb proportions
    'Shoulders',    // β3: shoulder width
    'Waist',        // β4: waist shape
    'Hips',         // β5: hip width
    'Torso',        // β6: torso length
    'Chest',        // β7: chest depth
    'Arms',         // β8: arm thickness
    'Legs',         // β9: leg shape
];
const SMPLX_EXPR_LABELS = [
    'Jaw Open',     // expr0
    'Smile',        // expr1
    'Brow Up',      // expr2
    'Brow Down',    // expr3
    'Lip Up',       // expr4
    'Lip Corner',   // expr5
    'Cheek Puff',   // expr6
    'Squint',       // expr7
    'Nose Wrinkle', // expr8
    'Eye Wide',     // expr9
];

// =========================================================================
// Init
// =========================================================================
function init() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    camera.position.set(0, 1.0, 4.5);

    controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 0.5;
    controls.maxDistance = 15;
    controls.update();

    // Lighting
    scene.add(new THREE.DirectionalLight(0xffffff, 3.0).translateX(2).translateY(4).translateZ(-5));
    scene.add(new THREE.DirectionalLight(0xeeeeff, 2.0).translateX(-3).translateY(3).translateZ(-4));
    scene.add(new THREE.DirectionalLight(0xffeedd, 2.5).translateX(0).translateY(4).translateZ(5));
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));

    // Ground grid
    scene.add(new THREE.GridHelper(6, 30, 0x333355, 0x222244));

    // Labels
    addModelLabel('HumanBody', MODEL_OFFSET_X);
    addModelLabel('SMPL-X', SMPLX_OFFSET_X);

    window.addEventListener('resize', onResize);

    // Panel toggle
    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => {
            h3.closest('.panel-section').classList.toggle('collapsed');
        });
    });

    // Load data
    loadMorphs();
    loadMesh().then(() => animate());
    loadDefSkeleton();
    loadSmplxModel();   // Load default SMPL-X

    // UI bindings
    initModelToggle();
    initRigToggle();
    initSmplxToggle();
    initSmplxRigToggle();
    initPhotoUpload();
    initSaveButton();
    checkSmplxStatus();
    buildSmplxPanel();
}

function addModelLabel(text, xOffset) {
    const canvas2d = document.createElement('canvas');
    canvas2d.width = 256;
    canvas2d.height = 48;
    const ctx = canvas2d.getContext('2d');
    ctx.fillStyle = 'rgba(0,0,0,0)';
    ctx.fillRect(0, 0, 256, 48);
    ctx.font = 'bold 24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#aaaacc';
    ctx.fillText(text, 128, 32);
    const tex = new THREE.CanvasTexture(canvas2d);
    const sprite = new THREE.Sprite(
        new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false })
    );
    sprite.position.set(xOffset, -0.08, 0);
    sprite.scale.set(0.8, 0.15, 1);
    sprite.renderOrder = 100;
    scene.add(sprite);
}

// =========================================================================
// Resize + Render loop
// =========================================================================
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
    controls.update();
    renderer.render(scene, camera);

    frameCount++;
    fpsAccum += clock.getDelta();
    if (fpsAccum >= 1.0) {
        const el = document.getElementById('fps-display');
        if (el) el.textContent = frameCount;
        frameCount = 0;
        fpsAccum = 0;
    }
}

// =========================================================================
// HumanBody skin color
// =========================================================================
function getSkinMat() {
    if (!bodyMesh || !bodyMesh.material) return null;
    return Array.isArray(bodyMesh.material) ? bodyMesh.material[0] : bodyMesh.material;
}

function applySkinColor(bodyType) {
    const parts = bodyType.split('_');
    const ethnicity = parts[1] || parts[0];
    const colors = skinColors[ethnicity];
    const mat = getSkinMat();
    if (colors && mat) {
        mat.color.setRGB(
            Math.pow(colors[0], 1 / 2.2),
            Math.pow(colors[1], 1 / 2.2),
            Math.pow(colors[2], 1 / 2.2)
        );
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = '#' + mat.color.getHexString();
    }
}

// =========================================================================
// HumanBody mesh loading (shifted left)
// =========================================================================
async function loadMesh(bodyType) {
    bodyType = bodyType || currentBodyType;
    let url = `${API}/mesh/?body_type=${encodeURIComponent(bodyType)}`;
    for (const [k, v] of Object.entries(morphValues)) {
        if (Math.abs(v) > 0.001) url += `&morph_${k}=${v}`;
    }

    try {
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        if (bodyMesh) {
            scene.remove(bodyMesh);
            bodyMesh.geometry?.dispose();
            bodyMesh = null;
            bodyGeometry = null;
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        let index = null;
        if (data.faces) index = new THREE.BufferAttribute(base64ToUint32(data.faces), 1);
        let uvAttr = null;
        if (data.uvs) uvAttr = new THREE.BufferAttribute(base64ToFloat32(data.uvs), 2);

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
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
            for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
            bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        bodyMesh.position.x = MODEL_OFFSET_X;
        bodyGeometry = geo;
        scene.add(bodyMesh);

        const vcEl = document.getElementById('vertex-count');
        if (vcEl) vcEl.textContent = geo.attributes.position.count.toLocaleString();

        applySkinColor(bodyType);
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

function requestMeshUpdate() {
    meshUpdatePending = true;
    if (!meshUpdateTimer) {
        meshUpdateTimer = setTimeout(async () => {
            meshUpdateTimer = null;
            if (meshUpdatePending) {
                meshUpdatePending = false;
                await loadMesh(currentBodyType);
            }
        }, 80);
    }
}

// =========================================================================
// HumanBody DEF Skeleton
// =========================================================================
async function loadDefSkeleton() {
    try {
        const resp = await fetch(`${API}/def-skeleton/`);
        if (resp.ok) defSkeletonData = await resp.json();
    } catch (e) { console.warn('DEF skeleton not available:', e); }
    try {
        const resp = await fetch(`${API}/skin-weights/`);
        if (resp.ok) skinWeightData = await resp.json();
    } catch (e) { console.warn('Skin weights not available:', e); }
    if (defSkeletonData && skinWeightData) buildDefSkeleton();
}

function buildDefSkeleton() {
    const skelByName = {};
    for (const b of defSkeletonData.bones) skelByName[b.name] = b;

    const bones = [];
    const boneByName = {};
    let rootBone = null;

    for (const name of skinWeightData.bone_names) {
        const bone = new THREE.Bone();
        bone.name = name.replace(/\./g, '_');
        bones.push(bone);
        boneByName[name] = bone;
    }

    for (let i = 0; i < skinWeightData.bone_names.length; i++) {
        const name = skinWeightData.bone_names[i];
        const bone = bones[i];
        const data = skelByName[name];
        if (!data) continue;

        const p = data.local_position;
        bone.position.set(p[0], p[2], -p[1]);
        const q = data.local_quaternion;
        bone.quaternion.set(q[1], q[3], -q[2], q[0]);

        if (data.parent && boneByName[data.parent]) {
            boneByName[data.parent].add(bone);
        } else if (!rootBone) {
            rootBone = bone;
        }
    }

    for (let i = 0; i < bones.length; i++) {
        if (!bones[i].parent && bones[i] !== rootBone && rootBone) {
            rootBone.add(bones[i]);
        }
    }

    if (rootBone) {
        rootBone.position.x += MODEL_OFFSET_X;
        scene.add(rootBone);
        rootBone.updateWorldMatrix(true, true);
        defSkeleton = { rootBone, bones, boneByName };
    }
}

// =========================================================================
// SMPL-X model loading — full SkinnedMesh + Rig (shifted right)
// =========================================================================
async function loadSmplxModel() {
    const betas = [...smplxBetas];
    // Append expression betas (indices 300-309 in shapedirs)
    // We send combined: first 10 shape + 10 expression at indices 300+
    const allBetas = new Array(310).fill(0);
    for (let i = 0; i < 10; i++) allBetas[i] = betas[i];
    for (let i = 0; i < 10; i++) allBetas[300 + i] = smplxExpr[i];

    try {
        const resp = await fetch(`${API}/smplx-mesh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ betas: allBetas, gender: smplxGender }),
        });
        const data = await resp.json();
        if (!data.ok) { console.warn('SMPL-X mesh:', data.error); return; }

        // Clean up old
        if (smplxGroup) {
            scene.remove(smplxGroup);
            if (smplxSkinnedMesh) {
                smplxSkinnedMesh.geometry?.dispose();
                smplxSkinnedMesh.material?.dispose();
            }
            if (smplxSkelHelper) smplxSkelHelper = null;
        }

        smplxGroup = new THREE.Group();
        smplxGroup.position.x = SMPLX_OFFSET_X;

        // --- Build skeleton from joints + parents ---
        const jointPos = base64ToFloat32(data.joints);
        const parents = data.parents;       // array of ints
        const nJoints = data.n_joints;

        const bones = [];
        for (let i = 0; i < nJoints; i++) {
            const bone = new THREE.Bone();
            bone.name = `smplx_j${i}`;
            bones.push(bone);
        }

        // Set bone positions in local space
        for (let i = 0; i < nJoints; i++) {
            const wx = jointPos[i * 3];
            const wy = jointPos[i * 3 + 1];
            const wz = jointPos[i * 3 + 2];
            const parentIdx = parents[i];
            if (parentIdx < 0) {
                // Root bone — world position
                bones[i].position.set(wx, wy, wz);
            } else {
                // Local = world - parent world
                const px = jointPos[parentIdx * 3];
                const py = jointPos[parentIdx * 3 + 1];
                const pz = jointPos[parentIdx * 3 + 2];
                bones[i].position.set(wx - px, wy - py, wz - pz);
                bones[parentIdx].add(bones[i]);
            }
        }

        const skeleton = new THREE.Skeleton(bones);

        // --- Build geometry ---
        const verts = base64ToFloat32(data.vertices);
        const faces = base64ToUint32(data.faces);
        const skinIdx = base64ToUint16(data.skin_indices);
        const skinWgt = base64ToFloat32(data.skin_weights);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(verts, 3));
        geo.setIndex(new THREE.BufferAttribute(faces, 1));
        geo.computeVertexNormals();

        // Skin attributes (4 bones per vertex)
        geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIdx, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWgt, 4));

        const mat = new THREE.MeshStandardMaterial({
            color: 0xccaa88,
            roughness: 0.55,
            metalness: 0.0,
            side: THREE.DoubleSide,
        });

        smplxSkinnedMesh = new THREE.SkinnedMesh(geo, mat);
        smplxSkinnedMesh.add(bones[0]);  // root bone must be child of mesh
        smplxSkinnedMesh.bind(skeleton);

        smplxGroup.add(smplxSkinnedMesh);
        scene.add(smplxGroup);

        // Update rig helper visibility
        if (smplxRigVisible) showSmplxRig();

        const vcEl = document.getElementById('smplx-vertex-count');
        if (vcEl) vcEl.textContent = data.n_verts.toLocaleString();

        console.log(`SMPL-X model: ${data.n_verts} verts, ${data.n_faces} faces, ${data.n_joints} joints`);
    } catch (e) {
        console.error('Failed to load SMPL-X model:', e);
    }
}

function requestSmplxUpdate() {
    if (smplxUpdateTimer) clearTimeout(smplxUpdateTimer);
    smplxUpdateTimer = setTimeout(() => {
        smplxUpdateTimer = null;
        loadSmplxModel();
    }, 120);
}

function showSmplxRig() {
    if (!smplxSkinnedMesh) return;
    if (smplxSkelHelper) {
        smplxGroup.remove(smplxSkelHelper);
        smplxSkelHelper.dispose();
    }
    smplxSkelHelper = new THREE.SkeletonHelper(smplxSkinnedMesh);
    smplxSkelHelper.material.depthTest = false;
    smplxSkelHelper.material.depthWrite = false;
    smplxSkelHelper.material.color.set(0xff8844);
    smplxSkelHelper.renderOrder = 999;
    smplxGroup.add(smplxSkelHelper);
}

// =========================================================================
// SMPL-X slider panel
// =========================================================================
function buildSmplxPanel() {
    const panel = document.getElementById('smplx-panel');
    if (!panel) return;

    // Gender dropdown
    const genderRow = document.createElement('div');
    genderRow.style.cssText = 'margin-bottom:8px;';
    const genderSel = document.createElement('select');
    genderSel.className = 'viewer-select';
    genderSel.id = 'smplx-gender';
    ['female', 'male', 'neutral'].forEach(g => {
        const opt = document.createElement('option');
        opt.value = g;
        opt.textContent = g.charAt(0).toUpperCase() + g.slice(1);
        genderSel.appendChild(opt);
    });
    genderSel.value = smplxGender;
    genderSel.addEventListener('change', () => {
        smplxGender = genderSel.value;
        requestSmplxUpdate();
    });
    genderRow.appendChild(genderSel);
    panel.appendChild(genderRow);

    // Shape betas
    const shapeHeader = document.createElement('div');
    shapeHeader.className = 'morph-category-header';
    shapeHeader.textContent = 'Shape (Body)';
    shapeHeader.style.cssText = 'cursor:pointer;margin-top:4px;';
    const shapeBody = document.createElement('div');
    shapeBody.style.display = 'block';
    shapeHeader.addEventListener('click', () => {
        shapeBody.style.display = shapeBody.style.display === 'none' ? 'block' : 'none';
    });
    panel.appendChild(shapeHeader);

    for (let i = 0; i < 10; i++) {
        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = SMPLX_BETA_LABELS[i];
        label.title = `Beta ${i}`;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -300;
        slider.max = 300;
        slider.value = 0;
        slider.step = 1;
        slider.dataset.betaIdx = i;

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = '0.0';

        slider.addEventListener('input', () => {
            const v = parseInt(slider.value) / 100.0;
            valSpan.textContent = v.toFixed(1);
            smplxBetas[i] = v;
            requestSmplxUpdate();
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        shapeBody.appendChild(row);
    }
    panel.appendChild(shapeBody);

    // Expression params
    const exprHeader = document.createElement('div');
    exprHeader.className = 'morph-category-header';
    exprHeader.textContent = 'Expression (Face)';
    exprHeader.style.cssText = 'cursor:pointer;margin-top:8px;';
    const exprBody = document.createElement('div');
    exprBody.style.display = 'none';
    exprHeader.addEventListener('click', () => {
        exprBody.style.display = exprBody.style.display === 'none' ? 'block' : 'none';
    });
    panel.appendChild(exprHeader);

    for (let i = 0; i < 10; i++) {
        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = SMPLX_EXPR_LABELS[i];

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -300;
        slider.max = 300;
        slider.value = 0;
        slider.step = 1;

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = '0.0';

        slider.addEventListener('input', () => {
            const v = parseInt(slider.value) / 100.0;
            valSpan.textContent = v.toFixed(1);
            smplxExpr[i] = v;
            requestSmplxUpdate();
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        exprBody.appendChild(row);
    }
    panel.appendChild(exprBody);

    // Reset button
    const resetBtn = document.getElementById('reset-smplx');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            smplxBetas.fill(0);
            smplxExpr.fill(0);
            panel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                const vEl = s.parentElement.querySelector('.slider-val');
                if (vEl) vEl.textContent = '0.0';
            });
            requestSmplxUpdate();
        });
    }
}

// =========================================================================
// HumanBody Morph UI
// =========================================================================
async function loadMorphs() {
    try {
        const resp = await fetch(`${API}/morphs/`);
        morphsData = await resp.json();
    } catch (e) { console.error('Failed to load morphs:', e); return; }

    const data = morphsData;
    skinColors = data.skin_colors || {};

    const select = document.getElementById('body-type-select');
    data.body_types.forEach(bt => {
        const opt = document.createElement('option');
        opt.value = bt;
        opt.textContent = bt.replace('_', ' ');
        select.appendChild(opt);
    });
    select.value = currentBodyType;

    select.addEventListener('change', async () => {
        const oldGender = currentBodyType.startsWith('Male_') ? 'male' : 'female';
        currentBodyType = select.value;
        const newGender = currentBodyType.startsWith('Male_') ? 'male' : 'female';

        if (oldGender !== newGender) {
            try {
                const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(currentBodyType)}`);
                skinWeightData = await swResp.json();
            } catch (e) { /* ignore */ }
        }

        await loadMesh(currentBodyType);
        const mResp = await fetch(`${API}/morphs/?body_type=${encodeURIComponent(currentBodyType)}`);
        morphsData = await mResp.json();
        skinColors = morphsData.skin_colors || {};
        buildMorphPanel(morphsData);
    });

    ['age', 'mass', 'tone', 'height'].forEach(name => {
        const slider = document.getElementById(`meta-${name}`);
        const valSpan = document.getElementById(`meta-${name}-val`);
        if (!slider) return;
        const meta = data.meta_sliders?.[name];
        if (meta) {
            slider.min = meta.min; slider.max = meta.max;
            slider.value = meta.default; valSpan.textContent = meta.default;
        }
        slider.addEventListener('input', () => {
            valSpan.textContent = slider.value;
            const min = parseInt(slider.min), max = parseInt(slider.max);
            const neutral = (min + max) / 2, half = (max - min) / 2;
            metaValues[name] = half ? (parseInt(slider.value) - neutral) / half : 0;
            requestMeshUpdate();
        });
    });

    const skinColorInput = document.getElementById('skin-color-viewer');
    if (skinColorInput) {
        skinColorInput.addEventListener('input', e => {
            const mat = getSkinMat();
            if (mat) mat.color.set(e.target.value);
        });
    }

    buildMorphPanel(data);

    const resetBtn = document.getElementById('reset-morphs');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            morphValues = {};
            document.querySelectorAll('#morphs-panel input[type="range"]').forEach(s => {
                s.value = 0;
                const valEl = s.parentElement.querySelector('.slider-val');
                if (valEl) valEl.textContent = '0';
            });
            requestMeshUpdate();
        });
    }
}

function buildMorphPanel(data) {
    const categories = {};
    data.morphs.forEach(m => {
        if (!categories[m.category]) categories[m.category] = [];
        categories[m.category].push(m);
    });

    const panel = document.getElementById('morphs-panel');
    panel.innerHTML = '';

    data.categories.sort().forEach(cat => {
        const morphs = categories[cat];
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
            slider.type = 'range'; slider.min = -100; slider.max = 100;
            slider.value = Math.round((morphValues[m.name] || 0) * 100);
            slider.step = 1; slider.dataset.morph = m.name;
            const valSpan = document.createElement('span');
            valSpan.className = 'slider-val'; valSpan.textContent = slider.value;
            slider.addEventListener('input', () => {
                const v = parseInt(slider.value) / 100.0;
                valSpan.textContent = slider.value;
                morphValues[m.name] = v;
                requestMeshUpdate();
            });
            row.appendChild(label); row.appendChild(slider); row.appendChild(valSpan);
            body.appendChild(row);
        });
        div.appendChild(body);
        panel.appendChild(div);
    });
}

// =========================================================================
// Toggle buttons
// =========================================================================
function initModelToggle() {
    const btn = document.getElementById('model-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        if (bodyMesh) bodyMesh.visible = !bodyMesh.visible;
        btn.classList.toggle('active', bodyMesh && bodyMesh.visible);
    });
}

function initRigToggle() {
    const btn = document.getElementById('rig-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        rigVisible = !rigVisible;
        if (rigVisible && !skeletonHelper && defSkeleton) {
            skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
            skeletonHelper.material.depthTest = false;
            skeletonHelper.material.depthWrite = false;
            skeletonHelper.material.color.set(0x00ffaa);
            skeletonHelper.renderOrder = 999;
            scene.add(skeletonHelper);
        }
        if (skeletonHelper) skeletonHelper.visible = rigVisible;
        btn.classList.toggle('active', rigVisible);
    });
}

function initSmplxToggle() {
    const btn = document.getElementById('smplx-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        if (smplxGroup) smplxGroup.visible = !smplxGroup.visible;
        btn.classList.toggle('active', smplxGroup && smplxGroup.visible);
    });
}

function initSmplxRigToggle() {
    const btn = document.getElementById('smplx-rig-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        smplxRigVisible = !smplxRigVisible;
        if (smplxRigVisible) {
            showSmplxRig();
        } else if (smplxSkelHelper) {
            smplxGroup?.remove(smplxSkelHelper);
            smplxSkelHelper.dispose();
            smplxSkelHelper = null;
        }
        btn.classList.toggle('active', smplxRigVisible);
    });
}

// =========================================================================
// Photo Upload
// =========================================================================
function initPhotoUpload() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('photo-input');
    const preview = document.getElementById('photo-preview');
    const img = document.getElementById('photo-img');
    const removeBtn = document.getElementById('photo-remove');
    const actions = document.getElementById('photo-actions');
    const analyzeBtn = document.getElementById('btn-analyze');

    zone.addEventListener('click', () => input.click());
    input.addEventListener('change', () => {
        if (input.files.length > 0) showPhoto(input.files[0]);
    });
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', e => {
        e.preventDefault(); zone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) showPhoto(file);
    });
    removeBtn.addEventListener('click', () => {
        preview.style.display = 'none'; actions.style.display = 'none';
        zone.style.display = ''; input.value = '';
        document.getElementById('detection-results').style.display = 'none';
    });
    analyzeBtn.addEventListener('click', () => analyzePhoto());

    function showPhoto(file) {
        const reader = new FileReader();
        reader.onload = e => {
            img.src = e.target.result;
            preview.style.display = 'block'; actions.style.display = 'block';
            zone.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

async function analyzePhoto() {
    const input = document.getElementById('photo-input');
    const btn = document.getElementById('btn-analyze');
    const resultsDiv = document.getElementById('detection-results');
    const paramsDiv = document.getElementById('detection-params');

    let file = input.files[0];
    if (!file) {
        const imgSrc = document.getElementById('photo-img').src;
        if (imgSrc && imgSrc.startsWith('data:')) {
            const resp = await fetch(imgSrc);
            const blob = await resp.blob();
            file = new File([blob], 'photo.jpg', { type: blob.type });
        }
    }
    if (!file) return;

    btn.classList.add('loading');
    btn.disabled = true;

    try {
        const form = new FormData();
        form.append('photo', file);
        const resp = await fetch(`${API}/analyze-photo/`, { method: 'POST', body: form });
        const data = await resp.json();

        if (data.ok) {
            paramsDiv.innerHTML = '';
            const isMock = data.mock === true;
            const modelLabel = isMock ? 'Mock-Daten' : 'SMPL-X + MediaPipe';
            const badgeClass = isMock ? 'mock' : 'real';
            const headerEl = resultsDiv.querySelector('h4');
            if (headerEl) headerEl.innerHTML = `Erkannte Parameter <span class="detection-model-badge ${badgeClass}">${modelLabel}</span>`;

            const params = [
                ['Geschlecht', data.gender === 'male' ? 'Männlich' : 'Weiblich'],
                ['Body Type', data.body_type.replace('_', ' ')],
            ];
            if (!isMock) params.push(['Confidence', (data.confidence * 100).toFixed(0) + '%']);
            if (data.skin_color) {
                params.push(['Hautfarbe', `<span style="display:inline-block;width:16px;height:16px;border-radius:3px;background:${data.skin_color};vertical-align:middle;border:1px solid rgba(255,255,255,0.2);margin-right:4px;"></span>${data.skin_color}`]);
            }
            if (data.measurements) {
                const mLabels = { height_cm: 'Körpergröße', shoulder_cm: 'Schulterbreite', hip_cm: 'Hüftbreite', torso_cm: 'Torsolänge', leg_cm: 'Beinlänge', arm_cm: 'Armlänge' };
                for (const [k, v] of Object.entries(data.measurements)) params.push([mLabels[k] || k, v + ' cm']);
            }
            if (data.meta_sliders) {
                const labels = { height: 'Größe (cm)', mass: 'Gewicht (kg)', tone: 'Muskeltonus', age: 'Alter' };
                for (const [k, v] of Object.entries(data.meta_sliders)) params.push([labels[k] || k, v]);
            }
            if (data.morphs && Object.keys(data.morphs).length > 0) {
                for (const [k, v] of Object.entries(data.morphs)) {
                    params.push([k.split('_').slice(1).join(' ') || k, (v >= 0 ? '+' : '') + (v * 100).toFixed(0) + '%']);
                }
            }
            params.forEach(([name, val]) => {
                const row = document.createElement('div');
                row.className = 'detection-param';
                row.innerHTML = `<span class="param-name">${name}</span><span class="param-val">${val}</span>`;
                paramsDiv.appendChild(row);
            });

            if (isMock) {
                const info = document.createElement('div');
                info.style.cssText = 'margin-top:8px;padding:8px;background:rgba(243,156,18,0.1);border:1px solid var(--warning);border-radius:6px;font-size:0.78rem;color:var(--text-muted);';
                info.innerHTML = '<i class="fas fa-info-circle" style="color:var(--warning);margin-right:4px;"></i> SMPL-X Modell oder MediaPipe Pose nicht verfügbar. Werte sind zufällige Testdaten.';
                paramsDiv.appendChild(info);
            }
            resultsDiv.style.display = 'block';

            // --- Apply betas to SMPL-X sliders ---
            if (data.betas) {
                for (let i = 0; i < Math.min(data.betas.length, 10); i++) {
                    smplxBetas[i] = data.betas[i];
                }
                smplxGender = data.gender || 'female';
                // Update SMPL-X slider UI
                const genderSel = document.getElementById('smplx-gender');
                if (genderSel) genderSel.value = smplxGender;
                const smplxPanel = document.getElementById('smplx-panel');
                if (smplxPanel) {
                    const sliders = smplxPanel.querySelectorAll('input[data-beta-idx]');
                    sliders.forEach(s => {
                        const idx = parseInt(s.dataset.betaIdx);
                        if (idx < smplxBetas.length) {
                            s.value = Math.round(smplxBetas[idx] * 100);
                            const vEl = s.parentElement.querySelector('.slider-val');
                            if (vEl) vEl.textContent = smplxBetas[idx].toFixed(1);
                        }
                    });
                }
                loadSmplxModel();
            }

            // --- Apply HumanBody sliders ---
            if (data.body_type) {
                const select = document.getElementById('body-type-select');
                if (select) { select.value = data.body_type; select.dispatchEvent(new Event('change')); }
            }
            if (data.meta_sliders) {
                for (const [name, val] of Object.entries(data.meta_sliders)) {
                    const slider = document.getElementById(`meta-${name}`);
                    const valSpan = document.getElementById(`meta-${name}-val`);
                    if (slider) { slider.value = val; if (valSpan) valSpan.textContent = val; slider.dispatchEvent(new Event('input')); }
                }
            }
            if (data.morphs) {
                for (const [morphName, val] of Object.entries(data.morphs)) {
                    morphValues[morphName] = val;
                    const slider = document.querySelector(`input[data-morph="${morphName}"]`);
                    if (slider) { slider.value = Math.round(val * 100); const vEl = slider.parentElement.querySelector('.slider-val'); if (vEl) vEl.textContent = Math.round(val * 100); }
                }
                requestMeshUpdate();
            }

            // Apply skin color from photo
            if (data.skin_color) {
                setTimeout(() => {
                    const mat = getSkinMat();
                    if (mat) { mat.color.set(data.skin_color); const picker = document.getElementById('skin-color-viewer'); if (picker) picker.value = data.skin_color; }
                    // Also tint SMPL-X mesh
                    if (smplxSkinnedMesh) smplxSkinnedMesh.material.color.set(data.skin_color);
                }, 200);
            }
        } else {
            paramsDiv.innerHTML = `<div style="color:var(--warning);padding:8px 0;">${data.error || 'Analyse fehlgeschlagen'}</div>`;
            resultsDiv.style.display = 'block';
        }
    } catch (e) {
        console.error('Analyze failed:', e);
        paramsDiv.innerHTML = `<div style="color:var(--danger);padding:8px 0;">Fehler: ${e.message}</div>`;
        resultsDiv.style.display = 'block';
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

// =========================================================================
// Status + Save
// =========================================================================
async function checkSmplxStatus() {
    const statusDiv = document.getElementById('smplx-status');
    try {
        const resp = await fetch(`${API}/analyze-photo/status/`);
        const data = await resp.json();
        const dot = statusDiv.querySelector('.status-dot');
        const span = statusDiv.querySelector('span');
        if (data.available) {
            dot.className = 'status-dot available';
            span.textContent = `SMPL-X: ${data.model_info || 'Bereit'}`;
        } else {
            dot.className = 'status-dot unavailable';
            span.textContent = 'SMPL-X: Nicht verfügbar — manuelle Anpassung möglich';
        }
    } catch (e) { /* ignore */ }
}

function initSaveButton() {
    const btn = document.getElementById('save-model-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
        const name = prompt('Preset-Name:', 'PhotoTo3D_' + currentBodyType);
        if (!name) return;
        const saveData = {
            name, data: {
                name, body_type: currentBodyType,
                morphs: { ...morphValues }, meta: { ...metaValues },
                skin_color: document.getElementById('skin-color-viewer')?.value || '#d4a574',
            },
        };
        try {
            const resp = await fetch(`${API}/model/save/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(saveData) });
            const result = await resp.json();
            if (result.ok) { btn.innerHTML = '<i class="fas fa-check"></i> Gespeichert'; setTimeout(() => { btn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 2000); }
        } catch (e) { console.error('Save failed:', e); }
    });
}

// =========================================================================
// Boot
// =========================================================================
init();
