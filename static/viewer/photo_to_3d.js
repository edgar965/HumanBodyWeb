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

/**
 * Align HB face/head profile to match SMPL-X proportions.
 *
 * Coordinate system after blenderToThreeCoords:
 *   Three.Z = -Blender.Y  →  face direction = POSITIVE Z (+Z = forward)
 *   back of head / back = NEGATIVE Z
 *
 * Problem: HB head protrudes 3-5cm more (relative to body axis) than SX.
 * Fix: push face-forward vertices backward (-Z) in head region,
 *      proportional to how far they are from the body axis.
 */
function alignBodyToSMPLX(buf) {
    const n = buf.length / 3;

    // --- Pass 1: height bounds + center X ---
    let minY = Infinity, maxY = -Infinity;
    for (let i = 0; i < n; i++) {
        const y = buf[i * 3 + 1];
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
    }
    const totalH = maxY - minY;
    if (totalH < 0.5) return;
    const headTop = maxY;

    // Center X from head verts (top 30cm)
    let sumCX = 0, cntCX = 0;
    for (let i = 0; i < n; i++) {
        if (buf[i * 3 + 1] > headTop - 0.30) { sumCX += buf[i * 3]; cntCX++; }
    }
    const cx = cntCX > 0 ? sumCX / cntCX : 0;

    // --- Pass 2: body axis Z = average Z of torso center verts (40-70% height) ---
    const torsoLow  = minY + totalH * 0.40;
    const torsoHigh = minY + totalH * 0.70;
    let sumAZ = 0, cntAZ = 0;
    for (let i = 0; i < n; i++) {
        const y = buf[i * 3 + 1];
        if (y >= torsoLow && y <= torsoHigh && Math.abs(buf[i * 3] - cx) < 0.15) {
            sumAZ += buf[i * 3 + 2]; cntAZ++;
        }
    }
    const axisZ = cntAZ > 0 ? sumAZ / cntAZ : 0;

    // --- Pass 3: compute max face Z per cm slice (head region) ---
    // For each 1cm height slice from top, find the most forward (+Z) vertex
    // Include ALL vertices (not just center) — jaw/ear are part of the silhouette
    const HEAD_START = 1, HEAD_END = 50;
    const maxFaceZ = new Float64Array(HEAD_END + 1).fill(-1e9);
    for (let i = 0; i < n; i++) {
        const y = buf[i * 3 + 1];
        const cm = Math.round((headTop - y) * 100);
        if (cm < HEAD_START || cm > HEAD_END) continue;
        const z = buf[i * 3 + 2];
        if (z > maxFaceZ[cm]) maxFaceZ[cm] = z;
    }

    // Per-cm correction LUT (meters): how much to push face back at each height
    // Calibrated from pixel-scan measurements (HB silhouette vs SX silhouette)
    // Remaining diffs after previous iteration added to base values
    //                     cm:  1     3     5     7     9    11    13    15    17    19    21    23    25    27    29    31    33    35    37    39    41    43    45    47    49
    const CORR_CM =            [1,    3,    5,    7,    9,   11,   13,   15,   17,   19,   21,   23,   25,   27,   29,   31,   33,   35,   37,   39,   41,   43,   45,   47,   49];
    const CORR_VAL =           [.051, .046, .044, .041, .038, .037, .025, .024, .035, .052, .067, .057, .062, .023, .016, .017, .020, .023, .030, .033, .037, .039, .040, .036, .056];

    function getCorrAtCm(cm) {
        if (cm <= CORR_CM[0]) return CORR_VAL[0];
        if (cm >= CORR_CM[CORR_CM.length - 1]) return CORR_VAL[CORR_VAL.length - 1];
        for (let j = 0; j < CORR_CM.length - 1; j++) {
            if (cm >= CORR_CM[j] && cm <= CORR_CM[j + 1]) {
                const t = (cm - CORR_CM[j]) / (CORR_CM[j + 1] - CORR_CM[j]);
                return CORR_VAL[j] + (CORR_VAL[j + 1] - CORR_VAL[j]) * t;
            }
        }
        return 0;
    }

    // --- Pass 4: apply face protrusion correction ---
    for (let i = 0; i < n; i++) {
        const y = buf[i * 3 + 1];
        const z = buf[i * 3 + 2];
        const cmFromTop = (headTop - y) * 100;

        // Only correct head region (cm 0-50 from top)
        if (cmFromTop < 0 || cmFromTop > 50) continue;

        // Only correct vertices that are in front of the body axis (+Z)
        if (z <= axisZ) continue;

        // How far forward from axis (0 = at axis, 1 = at face surface)
        const cm = Math.min(HEAD_END, Math.max(HEAD_START, Math.round(cmFromTop)));
        const faceMax = maxFaceZ[cm];
        if (faceMax <= axisZ) continue;

        const protrusion = z - axisZ;
        const maxProt = faceMax - axisZ;
        const faceFrac = Math.min(1, protrusion / maxProt);

        // Correction: push backward (-Z), scaled by how far forward the vertex is
        const corr = getCorrAtCm(cmFromTop);
        buf[i * 3 + 2] -= corr * faceFrac;
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

// --- Backend selection ---
let selectedBackend = 'smplest_x';
let backendStatus = {};

// --- Morph state (HumanBody) ---
let currentBodyType = 'Female_Caucasian';
let morphValues = {};
let metaValues = {};
let skinColors = {};
let morphsData = null;
let meshUpdateTimer = null;
let meshUpdatePending = false;
let detectedSkinColor = null;  // Custom skin color from photo analysis

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

    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
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
    // Expose for debugging (Playwright access)
    window._debugCamera = camera;
    window._debugControls = controls;
    window._debugScene = scene;
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

    // Load data — skeleton first, then mesh (so SkinnedMesh can be created)
    loadMorphs();
    loadDefSkeleton().then(() => {
        loadMesh().then(() => {
            animate();
            loadSmplxModel();
        });
    });

    // UI bindings
    initModelToggle();
    initRigToggle();
    initSmplxToggle();
    initSmplxRigToggle();
    initPhotoUpload();
    initSaveButton();
    loadBackendStatus();
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
    const mat = getSkinMat();
    if (!mat) return;
    // Prefer detected skin color from photo analysis
    if (detectedSkinColor) {
        mat.color.set(detectedSkinColor);
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = detectedSkinColor;
        return;
    }
    const parts = bodyType.split('_');
    const ethnicity = parts[1] || parts[0];
    const colors = skinColors[ethnicity];
    if (colors) {
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
    for (const [k, v] of Object.entries(metaValues)) {
        if (Math.abs(v) > 0.001) url += `&meta_${k}=${v}`;
    }

    try {
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        if (bodyMesh) {
            // Detach skeleton root from old SkinnedMesh before disposal
            if (bodyMesh.isSkinnedMesh && defSkeleton && defSkeleton.rootBone) {
                bodyMesh.remove(defSkeleton.rootBone);
            }
            scene.remove(bodyMesh);
            bodyMesh.geometry?.dispose();
            bodyMesh = null;
            bodyGeometry = null;
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        let normalBuf = null;
        if (data.normals) {
            normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
        }

        alignBodyToSMPLX(vertBuf);

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

        if (normalBuf) {
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];
        if (index && groups.length > 0) {
            for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
        }
        const mat = (index && groups.length > 0) ? materials : materials[0];

        // Create SkinnedMesh if skeleton + weights available, else regular Mesh
        if (defSkeleton && skinWeightData && skinWeightData.weights) {
            const vertCount = geo.attributes.position.count;
            const boneCount = defSkeleton.bones.length;
            const skinIndices = new Uint16Array(vertCount * 4);
            const skinWeights = new Float32Array(vertCount * 4);

            // Build bone name → index map (in defSkeleton.bones order)
            const skelBoneNames = skinWeightData.bone_names;
            // Map from skinWeightData bone index → defSkeleton bone index
            const swToBoneIdx = {};
            for (let si = 0; si < skelBoneNames.length; si++) {
                const idx = defSkeleton.bones.indexOf(defSkeleton.boneByName[skelBoneNames[si]]);
                if (idx >= 0) swToBoneIdx[si] = idx;
            }

            for (let vi = 0; vi < Math.min(vertCount, skinWeightData.weights.length); vi++) {
                const pairs = skinWeightData.weights[vi];
                for (let j = 0; j < Math.min(pairs.length, 4); j++) {
                    const boneIdx = swToBoneIdx[pairs[j][0]];
                    skinIndices[vi * 4 + j] = boneIdx !== undefined ? boneIdx : 0;
                    skinWeights[vi * 4 + j] = boneIdx !== undefined ? pairs[j][1] : 0;
                }
            }
            geo.setAttribute('skinIndex', new THREE.BufferAttribute(skinIndices, 4));
            geo.setAttribute('skinWeight', new THREE.BufferAttribute(skinWeights, 4));

            bodyMesh = new THREE.SkinnedMesh(geo, mat);
            const skeleton = new THREE.Skeleton(defSkeleton.bones);
            bodyMesh.add(defSkeleton.rootBone);
            bodyMesh.bind(skeleton);
        } else {
            bodyMesh = new THREE.Mesh(geo, mat);
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
async function loadDefSkeleton(bodyType) {
    bodyType = bodyType || currentBodyType;
    try {
        const resp = await fetch(`${API}/def-skeleton/?body_type=${encodeURIComponent(bodyType)}`);
        if (resp.ok) defSkeletonData = await resp.json();
    } catch (e) { console.warn('DEF skeleton not available:', e); }
    try {
        const resp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);
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

    // Store rest quaternions for facial expression deltas
    const restQuats = {};
    for (const [name, bone] of Object.entries(boneByName)) {
        restQuats[name] = bone.quaternion.clone();
    }

    if (rootBone) {
        rootBone.updateWorldMatrix(true, true);
        defSkeleton = { rootBone, bones, boneByName, restQuats };
    }
}

// =========================================================================
// Facial expression → HumanBody bone rotation mapping
// =========================================================================
// smplxExpr: [jawOpen, smile, browUp, browDown, lipUp, lipCorner, cheekPuff, squint, noseWrinkle, eyeWide]
function applyFacialExpression(expr) {
    if (!defSkeleton || !defSkeleton.restQuats) return;
    const { boneByName, restQuats } = defSkeleton;

    // Clamp SMPL-X expression values to reasonable range (-1.5..+1.5)
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
    const jawOpen     = clamp(expr[0] || 0, 0, 1.5);
    const smile       = clamp(expr[1] || 0, -1.5, 1.5);
    const browUp      = clamp(expr[2] || 0, -1.5, 1.5);
    const browDown    = clamp(expr[3] || 0, -1.5, 1.5);
    const lipUp       = clamp(expr[4] || 0, -1.5, 1.5);
    const lipCorner   = clamp(expr[5] || 0, -1.5, 1.5);
    const cheekPuff   = clamp(expr[6] || 0, -1.5, 1.5);
    const squint      = clamp(expr[7] || 0, -1.5, 1.5);
    const noseWrinkle = clamp(expr[8] || 0, -1.5, 1.5);
    const eyeWide     = clamp(expr[9] || 0, -1.5, 1.5);

    // Scale: SMPL-X expression → bone rotation (radians).
    // Keep small: DEF-jaw has a long lever arm, even 5-8° is very visible.
    // jawOpen=1.5 should produce ~6° (0.10 rad) — reduced to avoid beak.
    const S = 0.06;
    const browNet = (browUp - browDown) * S;

    // Accumulate [rx, ry, rz] per bone (Blender local space)
    const acc = {};
    function add(name, rx, ry, rz) {
        if (!acc[name]) acc[name] = [0, 0, 0];
        acc[name][0] += rx;
        acc[name][1] += ry;
        acc[name][2] += rz;
    }

    // === JAW: rx rotates jaw open in Blender local space ===
    // Max ~5° at full clamp (jawOpen=1.5 → 0.09 rad)
    add('DEF-jaw', jawOpen * S, 0, 0);

    // === LIPS (smile + lipUp + lipCorner combined) ===
    const sm = smile * S;
    const lu = lipUp * S;
    const lc = lipCorner * S;
    add('DEF-lip.T.L',     -lu, 0, 0);
    add('DEF-lip.T.R',     -lu, 0, 0);
    add('DEF-lip.T.L.001', -sm * 0.5, 0, -sm * 0.3 - lc * 0.5);
    add('DEF-lip.T.R.001', -sm * 0.5, 0,  sm * 0.3 + lc * 0.5);
    add('DEF-lip.B.L.001',  sm * 0.3, 0, -sm * 0.3 - lc * 0.5);
    add('DEF-lip.B.R.001',  sm * 0.3, 0,  sm * 0.3 + lc * 0.5);

    // === BROWS ===
    add('DEF-brow.B.L',       browNet,       0, 0);
    add('DEF-brow.B.L.001',   browNet * 0.8, 0, 0);
    add('DEF-brow.B.L.002',   browNet * 0.6, 0, 0);
    add('DEF-brow.B.R',       browNet,       0, 0);
    add('DEF-brow.B.R.001',   browNet * 0.8, 0, 0);
    add('DEF-brow.B.R.002',   browNet * 0.6, 0, 0);
    add('DEF-brow.T.L',       browNet * 0.5, 0, 0);
    add('DEF-brow.T.L.001',   browNet * 0.5, 0, 0);
    add('DEF-brow.T.R',       browNet * 0.5, 0, 0);
    add('DEF-brow.T.R.001',   browNet * 0.5, 0, 0);

    // === CHEEKS ===
    const ck = cheekPuff * S;
    add('DEF-cheek.B.L', 0, 0, -ck);
    add('DEF-cheek.B.R', 0, 0,  ck);
    add('DEF-cheek.T.L', 0, 0, -ck * 0.5);
    add('DEF-cheek.T.R', 0, 0,  ck * 0.5);

    // === EYELIDS ===
    const topLid = (squint - eyeWide) * S;
    const botLid = (-squint + eyeWide) * S;
    add('DEF-lid.T.L.001', topLid, 0, 0);
    add('DEF-lid.T.L.002', topLid, 0, 0);
    add('DEF-lid.T.R.001', topLid, 0, 0);
    add('DEF-lid.T.R.002', topLid, 0, 0);
    add('DEF-lid.B.L.001', botLid, 0, 0);
    add('DEF-lid.B.L.002', botLid, 0, 0);
    add('DEF-lid.B.R.001', botLid, 0, 0);
    add('DEF-lid.B.R.002', botLid, 0, 0);

    // === NOSE ===
    const nr = noseWrinkle * S * 0.5;
    add('DEF-nose.L',   0, 0, -nr);
    add('DEF-nose.R',   0, 0,  nr);
    add('DEF-nose.001', nr, 0,  0);

    // === CHIN (follows jaw subtly) ===
    add('DEF-chin',     jawOpen * S * 0.3, 0, 0);
    add('DEF-chin.001', jawOpen * S * 0.15, 0, 0);

    // Apply accumulated rotations to bones
    const tmpE = new THREE.Euler();
    const tmpQ = new THREE.Quaternion();
    for (const [name, [rx, ry, rz]] of Object.entries(acc)) {
        const bone = boneByName[name];
        const rest = restQuats[name];
        if (!bone || !rest) continue;
        // Blender local → Three.js: swap Y↔Z, negate new Z
        tmpE.set(rx, rz, -ry, 'XYZ');
        tmpQ.setFromEuler(tmpE);
        bone.quaternion.copy(rest).multiply(tmpQ);
    }

    // Force skeleton update
    if (defSkeleton.rootBone) defSkeleton.rootBone.updateWorldMatrix(true, true);
    if (bodyMesh && bodyMesh.skeleton) bodyMesh.skeleton.update();

    console.log('[FaceExpr] Applied:', {jawOpen, smile, browUp, browDown, lipUp, lipCorner, cheekPuff, squint, noseWrinkle, eyeWide});
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
        // IMPORTANT: Always use neutral model for SMPL-X mesh generation!
        // All analysis backends (SMPLest-X, PyMAF-X, HMR2) output betas trained
        // on the neutral model. Gender-specific models have DIFFERENT PCA
        // shapedirs, so same betas would produce completely wrong body shapes.
        const resp = await fetch(`${API}/smplx-mesh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ betas: allBetas, gender: 'neutral' }),
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

        // Auto-scale SMPL-X to match HumanBody height
        matchModelHeights();

        // Update rig helper visibility
        if (smplxRigVisible) showSmplxRig();

        const vcEl = document.getElementById('smplx-vertex-count');
        if (vcEl) vcEl.textContent = data.n_verts.toLocaleString();

        console.log(`SMPL-X model: ${data.n_verts} verts, ${data.n_faces} faces, ${data.n_joints} joints`);
    } catch (e) {
        console.error('Failed to load SMPL-X model:', e);
    }
}

function matchModelHeights() {
    if (!bodyMesh || !smplxSkinnedMesh) return;
    // Compute bounding box heights for both models
    bodyMesh.geometry.computeBoundingBox();
    smplxSkinnedMesh.geometry.computeBoundingBox();
    const hbBox = bodyMesh.geometry.boundingBox;
    const smplxBox = smplxSkinnedMesh.geometry.boundingBox;
    const hbHeight = hbBox.max.y - hbBox.min.y;
    const smplxHeight = smplxBox.max.y - smplxBox.min.y;
    if (smplxHeight > 0.01 && hbHeight > 0.01) {
        const scale = hbHeight / smplxHeight;
        smplxGroup.scale.setScalar(scale);
    }
}

function requestSmplxUpdate() {
    if (smplxUpdateTimer) clearTimeout(smplxUpdateTimer);
    smplxUpdateTimer = setTimeout(() => {
        smplxUpdateTimer = null;
        loadSmplxModel();
        applyFacialExpression(smplxExpr);
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
        slider.dataset.exprIdx = i;

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
        detectedSkinColor = null;  // Reset detected skin color
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
        form.append('backend', selectedBackend);
        const resp = await fetch(`${API}/analyze-photo/`, { method: 'POST', body: form });
        const data = await resp.json();

        if (data.ok) {
            paramsDiv.innerHTML = '';
            const isMock = data.mock === true;
            const usedBackend = data.backend || selectedBackend;
            const backendLabel = backendStatus[usedBackend]?.label || usedBackend;
            const modelLabel = isMock ? 'Mock-Daten' : backendLabel;
            const badgeClass = isMock ? 'mock' : 'real';
            const headerEl = resultsDiv.querySelector('h4');
            if (headerEl) headerEl.innerHTML = `Erkannte Parameter <span class="detection-model-badge ${badgeClass}">${modelLabel}</span>`;

            const EXPR_DE = ['Kiefer offen', 'Lächeln', 'Brauen hoch', 'Brauen runter', 'Lippe hoch', 'Mundwinkel', 'Wangen', 'Zusammenkneifen', 'Nase', 'Augen weit'];

            const genderLabel = data.gender === 'male' ? 'Männlich' : 'Weiblich';
            const genderNote = data.estimated_gender ? ' (auto)' : '';
            const params = [
                ['Geschlecht', genderLabel + genderNote],
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
            if (data.betas) {
                params.push(['Shape-Parameter', `${Math.min(data.betas.length, 10)} erkannt`]);
            }
            if (data.expression && data.expression.length > 0) {
                params.push(['Expression-Parameter', `${Math.min(data.expression.length, 10)} erkannt`]);
                // Show top expressions with magnitude > 0.3
                const topExpr = data.expression
                    .map((v, i) => ({ label: EXPR_DE[i] || `Expr ${i}`, val: v, i }))
                    .filter(e => Math.abs(e.val) > 0.3)
                    .sort((a, b) => Math.abs(b.val) - Math.abs(a.val))
                    .slice(0, 3);
                if (topExpr.length > 0) {
                    const exprStr = topExpr.map(e => `${e.label} ${e.val >= 0 ? '+' : ''}${e.val.toFixed(1)}`).join(', ');
                    params.push(['Ausdruck', exprStr]);
                }
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

            // --- Gender Override Dropdown ---
            const genderOverrideRow = document.createElement('div');
            genderOverrideRow.style.cssText = 'margin-top:8px;display:flex;align-items:center;gap:8px;';
            const genderOverrideLabel = document.createElement('span');
            genderOverrideLabel.style.cssText = 'font-size:0.82rem;color:var(--text);';
            genderOverrideLabel.textContent = 'Geschlecht:';
            const genderOverrideSel = document.createElement('select');
            genderOverrideSel.className = 'viewer-select';
            genderOverrideSel.style.cssText = 'margin-bottom:0;flex:1;';
            const autoLabel = `Automatisch (${genderLabel})`;
            [{ val: 'auto', label: autoLabel }, { val: 'male', label: 'Männlich' }, { val: 'female', label: 'Weiblich' }].forEach(opt => {
                const o = document.createElement('option');
                o.value = opt.val; o.textContent = opt.label;
                genderOverrideSel.appendChild(o);
            });
            genderOverrideSel.value = 'auto';
            genderOverrideSel.addEventListener('change', () => {
                const chosen = genderOverrideSel.value === 'auto' ? data.gender : genderOverrideSel.value;
                const prefix = chosen === 'male' ? 'Male' : 'Female';
                const ethnicity = currentBodyType.split('_')[1] || 'Caucasian';
                currentBodyType = `${prefix}_${ethnicity}`;
                smplxGender = chosen;
                const btSelect = document.getElementById('body-type-select');
                if (btSelect) { btSelect.value = currentBodyType; btSelect.dispatchEvent(new Event('change')); }
                const gSel = document.getElementById('smplx-gender');
                if (gSel) gSel.value = smplxGender;
                loadSmplxModel();
            });
            genderOverrideRow.appendChild(genderOverrideLabel);
            genderOverrideRow.appendChild(genderOverrideSel);
            paramsDiv.appendChild(genderOverrideRow);

            if (isMock) {
                const info = document.createElement('div');
                info.style.cssText = 'margin-top:8px;padding:8px;background:rgba(243,156,18,0.1);border:1px solid var(--warning);border-radius:6px;font-size:0.78rem;color:var(--text-muted);';
                info.innerHTML = '<i class="fas fa-info-circle" style="color:var(--warning);margin-right:4px;"></i> SMPL-X Modell oder MediaPipe Pose nicht verfügbar. Werte sind zufällige Testdaten.';
                paramsDiv.appendChild(info);
            }
            resultsDiv.style.display = 'block';

            // =============================================================
            // Step 1: Set ALL state values BEFORE triggering any loads
            // =============================================================

            // 1a. Skin color (global, used by applySkinColor on every mesh load)
            if (data.skin_color) {
                detectedSkinColor = data.skin_color;
                const picker = document.getElementById('skin-color-viewer');
                if (picker) picker.value = data.skin_color;
            }

            // 1b. SMPL-X betas + gender + expression (set state only, no load yet)
            if (data.betas) {
                for (let i = 0; i < Math.min(data.betas.length, 10); i++) {
                    smplxBetas[i] = data.betas[i];
                }
            }
            smplxGender = data.gender || 'female';

            if (data.expression && data.expression.length > 0) {
                for (let i = 0; i < Math.min(data.expression.length, 10); i++) {
                    smplxExpr[i] = data.expression[i];
                }
            }

            // 1c. HumanBody morphs + meta values (set state only, no load yet)
            if (data.morphs) {
                for (const [morphName, val] of Object.entries(data.morphs)) {
                    morphValues[morphName] = val;
                }
            }
            if (data.meta_sliders) {
                // Compute metaValues in -1..1 scale from raw slider values
                // Use known ranges (consistent across all body types) with
                // morphsData fallback for robustness
                const defaultRanges = {
                    height: { min: 150, max: 200 },
                    mass:   { min: 45,  max: 200 },
                    tone:   { min: 0,   max: 100 },
                    age:    { min: 18,  max: 100 },
                };
                const metaDefs = morphsData?.meta_sliders || {};
                for (const [name, val] of Object.entries(data.meta_sliders)) {
                    const def = metaDefs[name] || defaultRanges[name];
                    if (def) {
                        const min = def.min, max = def.max;
                        const neutral = (min + max) / 2, half = (max - min) / 2;
                        metaValues[name] = half ? (val - neutral) / half : 0;
                    }
                }
            }
            if (data.body_type) {
                currentBodyType = data.body_type;
            }

            // =============================================================
            // Step 2: Update ALL slider UIs
            // =============================================================

            // Body type dropdown
            const btSelect = document.getElementById('body-type-select');
            if (btSelect) btSelect.value = currentBodyType;

            // SMPL-X gender dropdown
            const genderSel = document.getElementById('smplx-gender');
            if (genderSel) genderSel.value = smplxGender;

            // SMPL-X beta sliders
            const smplxPanel = document.getElementById('smplx-panel');
            if (smplxPanel) {
                smplxPanel.querySelectorAll('input[data-beta-idx]').forEach(s => {
                    const idx = parseInt(s.dataset.betaIdx);
                    if (idx < smplxBetas.length) {
                        s.value = Math.round(smplxBetas[idx] * 100);
                        const vEl = s.parentElement.querySelector('.slider-val');
                        if (vEl) vEl.textContent = smplxBetas[idx].toFixed(1);
                    }
                });
                smplxPanel.querySelectorAll('input[data-expr-idx]').forEach(s => {
                    const idx = parseInt(s.dataset.exprIdx);
                    if (idx < smplxExpr.length) {
                        s.value = Math.round(smplxExpr[idx] * 100);
                        const vEl = s.parentElement.querySelector('.slider-val');
                        if (vEl) vEl.textContent = smplxExpr[idx].toFixed(1);
                    }
                });
            }

            // Meta sliders
            if (data.meta_sliders) {
                for (const [name, val] of Object.entries(data.meta_sliders)) {
                    const slider = document.getElementById(`meta-${name}`);
                    const valSpan = document.getElementById(`meta-${name}-val`);
                    if (slider) { slider.value = val; if (valSpan) valSpan.textContent = val; }
                }
            }

            // Morph sliders
            if (data.morphs) {
                for (const [morphName, val] of Object.entries(data.morphs)) {
                    const slider = document.querySelector(`input[data-morph="${morphName}"]`);
                    if (slider) {
                        slider.value = Math.round(val * 100);
                        const vEl = slider.parentElement.querySelector('.slider-val');
                        if (vEl) vEl.textContent = Math.round(val * 100);
                    }
                }
            }

            // =============================================================
            // Step 3: Trigger model loads (all state is set, one load each)
            // =============================================================
            console.log('[Photo→3D] Loading models:', {
                bodyType: currentBodyType, smplxGender,
                betas: smplxBetas.slice(0, 5), meta: {...metaValues},
                skinColor: detectedSkinColor,
            });

            // Refresh morphsData for the new body type (may have changed gender)
            try {
                const mResp = await fetch(`${API}/morphs/?body_type=${encodeURIComponent(currentBodyType)}`);
                morphsData = await mResp.json();
                skinColors = morphsData.skin_colors || {};
                buildMorphPanel(morphsData);
            } catch (e) { console.warn('Failed to refresh morphs:', e); }

            // Reload skin weights + DEF skeleton when body type changes
            // (Male/Female have different vertex counts & skeleton)
            try {
                const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(currentBodyType)}`);
                skinWeightData = await swResp.json();
                const dsResp = await fetch(`${API}/def-skeleton/?body_type=${encodeURIComponent(currentBodyType)}`);
                defSkeletonData = await dsResp.json();
                defSkeleton = null;
                buildDefSkeleton();
                console.log('[Photo→3D] Reloaded skin weights + skeleton for', currentBodyType);
            } catch (e) { console.warn('Failed to reload skin weights:', e); }

            // Load HumanBody mesh (with morphs + meta values included in URL)
            console.log('[Photo→3D] loadMesh meta:', {...metaValues}, 'morphs:', {...morphValues});
            await loadMesh(currentBodyType);

            // Apply facial expression to HumanBody bones
            applyFacialExpression(smplxExpr);

            // Load SMPL-X model (with betas + expression)
            await loadSmplxModel();

            // Apply skin color to SMPL-X mesh too
            if (detectedSkinColor && smplxSkinnedMesh) {
                smplxSkinnedMesh.material.color.set(detectedSkinColor);
            }

            // Capture screenshot for job thumbnail (with small delay for rendering)
            if (data.job_id) {
                setTimeout(() => captureAndSaveScreenshot(data.job_id), 800);
            }
            showJobJson(data);
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
async function loadBackendStatus() {
    const list = document.getElementById('backend-list');
    if (!list) return;

    try {
        const resp = await fetch(`${API}/analyze-photo/status/`);
        const data = await resp.json();
        backendStatus = data.backends || {};
    } catch (e) {
        console.warn('Failed to load backend status:', e);
        return;
    }

    list.innerHTML = '';
    const order = ['smplest_x', 'pymafx', 'hmr2', 'mediapipe'];

    for (const key of order) {
        const info = backendStatus[key];
        if (!info) continue;

        const item = document.createElement('div');
        item.className = 'backend-item';
        if (key === selectedBackend && info.available) item.classList.add('selected');
        if (!info.available) item.classList.add('disabled');
        item.dataset.backend = key;

        const radio = document.createElement('div');
        radio.className = 'backend-radio';

        const dot = document.createElement('div');
        dot.className = 'backend-status-dot ' + (info.available ? 'ok' : 'no');

        const infoDiv = document.createElement('div');
        infoDiv.className = 'backend-info';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'backend-label';
        labelDiv.textContent = info.label;

        // Quality badge
        if (info.quality === 'best') {
            const badge = document.createElement('span');
            badge.className = 'backend-badge best';
            badge.textContent = 'Best';
            labelDiv.appendChild(badge);
        }

        // GPU/CPU badge
        const hwBadge = document.createElement('span');
        hwBadge.className = 'backend-badge ' + (info.gpu ? 'gpu' : 'cpu');
        hwBadge.textContent = info.gpu ? 'GPU' : 'CPU';
        labelDiv.appendChild(hwBadge);

        const descDiv = document.createElement('div');
        descDiv.className = 'backend-desc';
        descDiv.textContent = info.available ? info.desc : info.info;

        infoDiv.appendChild(labelDiv);
        infoDiv.appendChild(descDiv);

        item.appendChild(radio);
        item.appendChild(dot);
        item.appendChild(infoDiv);

        item.addEventListener('click', () => {
            if (!info.available) return;
            selectedBackend = key;
            list.querySelectorAll('.backend-item').forEach(el => el.classList.remove('selected'));
            item.classList.add('selected');
        });

        list.appendChild(item);
    }

    // If selected backend is not available, auto-select first available
    if (!backendStatus[selectedBackend]?.available) {
        for (const key of order) {
            if (backendStatus[key]?.available) {
                selectedBackend = key;
                const el = list.querySelector(`[data-backend="${key}"]`);
                if (el) el.classList.add('selected');
                break;
            }
        }
    }
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
// Screenshot capture — save rendered 3D view to server for job thumbnail
// =========================================================================
async function captureAndSaveScreenshot(jobId) {
    if (!jobId || !renderer) return;
    try {
        // Force a render to ensure buffer is current
        renderer.render(scene, camera);
        const dataUrl = renderer.domElement.toDataURL('image/jpeg', 0.85);
        await fetch(`${API}/photo-job/${jobId}/screenshot/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl }),
        });
        console.log('[Photo→3D] Screenshot saved for job', jobId);
    } catch (e) {
        console.warn('Screenshot capture failed:', e);
    }
}

// =========================================================================
// Show full JSON data in detection panel
// =========================================================================
function showJobJson(data) {
    const el = document.getElementById('detection-json');
    if (!el) return;
    // Build a clean display object (skip photo_url, ok, mock)
    const display = {};
    if (data.gender) display.gender = data.gender;
    if (data.backend) display.backend = data.backend;
    if (data.body_type) display.body_type = data.body_type;
    if (data.confidence) display.confidence = data.confidence;
    if (data.duration) display.duration = data.duration + 's';
    if (data.skin_color) display.skin_color = data.skin_color;
    if (data.measurements) display.measurements = data.measurements;
    if (data.meta_sliders) display.meta_sliders = data.meta_sliders;
    if (data.betas) display.betas = data.betas.map(b => +b.toFixed(3));
    if (data.expression) display.expression = data.expression.map(e => +e.toFixed(3));
    if (data.morphs) {
        // Group morphs by category
        const cats = {};
        for (const [k, v] of Object.entries(data.morphs)) {
            const cat = k.split('_')[0];
            if (!cats[cat]) cats[cat] = {};
            cats[cat][k] = v;
        }
        display.morphs = cats;
    }
    el.textContent = JSON.stringify(display, null, 2);
    el.style.display = 'block';
}

// =========================================================================
// Job preload (for loading saved analysis results)
// =========================================================================
async function loadJobResult(jobId) {
    try {
        const resp = await fetch(`${API}/photo-job/${jobId}/`);
        const data = await resp.json();
        if (!data.ok) { console.error('Job load failed:', data.error); return; }

        // Display photo
        if (data.photo_url) {
            const img = document.getElementById('photo-img');
            const placeholder = document.getElementById('upload-zone');
            if (img) { img.src = data.photo_url; img.style.display = 'block'; }
            if (placeholder) placeholder.style.display = 'none';
            const preview = document.getElementById('photo-preview');
            if (preview) preview.style.display = 'block';
            const actions = document.getElementById('photo-actions');
            if (actions) actions.style.display = 'block';
        }

        // === Step 1: Set ALL state ===
        if (data.skin_color) {
            detectedSkinColor = data.skin_color;
            const picker = document.getElementById('skin-color-viewer');
            if (picker) picker.value = data.skin_color;
        }
        if (data.betas) {
            for (let i = 0; i < Math.min(data.betas.length, 10); i++) {
                smplxBetas[i] = data.betas[i];
            }
        }
        smplxGender = data.gender || 'female';
        if (data.expression && data.expression.length > 0) {
            for (let i = 0; i < Math.min(data.expression.length, 10); i++) {
                smplxExpr[i] = data.expression[i];
            }
        }
        if (data.morphs) {
            for (const [morphName, val] of Object.entries(data.morphs)) {
                morphValues[morphName] = val;
            }
        }
        if (data.meta_sliders) {
            const defaultRanges = {
                height: { min: 150, max: 200 }, mass: { min: 45, max: 200 },
                tone: { min: 0, max: 100 }, age: { min: 18, max: 100 },
            };
            const metaDefs = morphsData?.meta_sliders || {};
            for (const [name, val] of Object.entries(data.meta_sliders)) {
                const def = metaDefs[name] || defaultRanges[name];
                if (def) {
                    const min = def.min, max = def.max;
                    const neutral = (min + max) / 2, half = (max - min) / 2;
                    metaValues[name] = half ? (val - neutral) / half : 0;
                }
            }
        }
        if (data.body_type) currentBodyType = data.body_type;

        // === Step 2: Update UI sliders ===
        const btSelect = document.getElementById('body-type-select');
        if (btSelect) btSelect.value = currentBodyType;
        const genderSel = document.getElementById('smplx-gender');
        if (genderSel) genderSel.value = smplxGender;
        if (data.meta_sliders) {
            for (const [name, val] of Object.entries(data.meta_sliders)) {
                const slider = document.getElementById(`meta-${name}`);
                const valSpan = document.getElementById(`meta-${name}-val`);
                if (slider) { slider.value = val; if (valSpan) valSpan.textContent = val; }
            }
        }
        // Sync SMPL-X beta sliders
        document.querySelectorAll('[data-beta-idx]').forEach(sl => {
            const i = parseInt(sl.dataset.betaIdx);
            sl.value = Math.round(smplxBetas[i] * 100);
            const vs = sl.parentElement?.querySelector('.slider-val');
            if (vs) vs.textContent = smplxBetas[i].toFixed(1);
        });
        // Sync SMPL-X expression sliders
        document.querySelectorAll('[data-expr-idx]').forEach(sl => {
            const i = parseInt(sl.dataset.exprIdx);
            sl.value = Math.round(smplxExpr[i] * 100);
            const vs = sl.parentElement?.querySelector('.slider-val');
            if (vs) vs.textContent = smplxExpr[i].toFixed(1);
        });

        // === Step 3: Load models ===
        console.log('[Photo→3D] Loading job result:', {
            bodyType: currentBodyType, smplxGender,
            morphCount: Object.keys(morphValues).length,
        });
        try {
            const mResp = await fetch(`${API}/morphs/?body_type=${encodeURIComponent(currentBodyType)}`);
            morphsData = await mResp.json();
            skinColors = morphsData.skin_colors || {};
            buildMorphPanel(morphsData);
        } catch (e) { console.warn('Failed to refresh morphs:', e); }

        // Reload skin weights + DEF skeleton for correct body type
        try {
            const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(currentBodyType)}`);
            skinWeightData = await swResp.json();
            const dsResp = await fetch(`${API}/def-skeleton/?body_type=${encodeURIComponent(currentBodyType)}`);
            defSkeletonData = await dsResp.json();
            defSkeleton = null;
            buildDefSkeleton();
        } catch (e) { console.warn('Failed to reload skin weights:', e); }

        await loadMesh(currentBodyType);
        applyFacialExpression(smplxExpr);
        await loadSmplxModel();
        if (detectedSkinColor && smplxSkinnedMesh) {
            smplxSkinnedMesh.material.color.set(detectedSkinColor);
        }

        // Show results panel
        const resultsDiv = document.getElementById('detection-results');
        const paramsDiv = document.getElementById('detection-params');
        if (resultsDiv) resultsDiv.style.display = 'block';
        if (paramsDiv) {
            paramsDiv.innerHTML = `<div style="padding:4px 0;font-size:0.85rem;">
                <b>Geschlecht:</b> ${data.gender === 'male' ? 'Männlich' : 'Weiblich'} &nbsp;|&nbsp;
                <b>Body Type:</b> ${currentBodyType} &nbsp;|&nbsp;
                <b>Backend:</b> ${data.backend || '?'}
            </div>`;
        }
        showJobJson(data);
    } catch (e) {
        console.error('Failed to load job:', e);
    }
}

// =========================================================================
// Boot
// =========================================================================
init();

// Auto-load job if ?job=<uuid> is in URL
{
    const params = new URLSearchParams(window.location.search);
    const jobId = params.get('job');
    if (jobId) {
        // Wait for initial mesh load, then overlay with job data
        setTimeout(() => loadJobResult(jobId), 1500);
    }
}
