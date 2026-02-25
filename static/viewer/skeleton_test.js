/**
 * Skeleton Test — 4 skeletons side-by-side for bone-mapping debugging.
 *
 * Left (red):    AutoRig DEF skeleton (176 bones)
 * Center-L (green): CMU BVH skeleton (~31 bones)
 * Center-R (orange): Mixamo BVH skeleton (~52 bones, with fingers)
 * Right (blue):  MocapNET v4 BVH skeleton (~150+ bones)
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { detectBVHFormat, retargetBVHToDefClip, BVH_TO_DEF_CMU, BVH_TO_DEF_MIXAMO, BVH_TO_DEF_MOCAPNET } from './retarget_hybrid.js?v=7';

// =========================================================================
// Global state
// =========================================================================
let scene, camera, renderer, controls, labelRenderer;
let clock = new THREE.Clock();
let frameCount = 0;
let fpsAccum = 0;

const bvhLoader = new BVHLoader();

// Animation
let mixer = null;
let currentAction = null;
let playing = false;
let currentBvhResult = null;
let currentFormat = null;

// DEF skeleton data from API
let defSkeletonData = null;
let skinWeightData = null;

// All animations list (for auto-loading first of each type)
let allAnimations = {};

// Three skeleton groups
const skeletons = {
    def:      { group: null, bones: null, labels: [], vizMeshes: [], color: 0xff4444, xOffset: -2.0, rootBone: null, boneByName: null, skeleton: null },
    cmu:      { group: null, bones: null, labels: [], vizMeshes: [], color: 0x44ff44, xOffset: -0.7, rootBone: null, bvhResult: null, wrapper: null },
    mixamo:   { group: null, bones: null, labels: [], vizMeshes: [], color: 0xffaa44, xOffset:  0.7, rootBone: null, bvhResult: null, wrapper: null },
    mocapnet: { group: null, bones: null, labels: [], vizMeshes: [], color: 0x4488ff, xOffset:  2.0, rootBone: null, bvhResult: null, wrapper: null },
};

// Shared materials for bone visualization
const JOINT_MAT = new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false });
const BONE_MAT  = new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false });

// Base sizes (at scale=1)
const JOINT_RADIUS = 0.008;
const CYL_RADIUS_TOP = 0.003;
const CYL_RADIUS_BOT = 0.004;

// Retarget imports from shared module (retarget.js)

// =========================================================================
// Build DEF Skeleton (from def_skeleton.json + skin_weights bone_names)
// =========================================================================
function buildDefSkeleton(skelData, swData) {
    const skelByName = {};
    for (const b of skelData.bones) skelByName[b.name] = b;

    const bones = [];
    const boneByName = {};
    let rootBone = null;

    for (const name of swData.bone_names) {
        const bone = new THREE.Bone();
        bone.name = name.replace(/\./g, '_');
        bones.push(bone);
        boneByName[name] = bone;
    }

    for (let i = 0; i < swData.bone_names.length; i++) {
        const name = swData.bone_names[i];
        const bone = bones[i];
        const data = skelByName[name];
        if (!data) continue;

        const p = data.local_position;
        bone.position.set(p[0], p[2], -p[1]);
        const q = data.local_quaternion;
        bone.quaternion.set(q[1], q[3], -q[2], q[0]);

        if (data.parent && boneByName[data.parent]) {
            boneByName[data.parent].add(bone);
        } else {
            if (!rootBone) rootBone = bone;
        }
    }

    for (let i = 0; i < bones.length; i++) {
        const name = swData.bone_names[i];
        const data = skelByName[name];
        if (!data) continue;
        if (!data.parent && bones[i] !== rootBone) {
            if (rootBone) rootBone.add(bones[i]);
        }
    }

    if (!rootBone && bones.length > 0) rootBone = bones[0];
    rootBone.updateWorldMatrix(true, true);
    const skeleton = new THREE.Skeleton(bones);
    return { skeleton, rootBone, bones, boneByName };
}

// =========================================================================
// Initialization
// =========================================================================
function init() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    // WebGL Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    // CSS2D Renderer for bone labels
    labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(w, h);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0';
    labelRenderer.domElement.style.left = '0';
    labelRenderer.domElement.style.pointerEvents = 'none';
    document.getElementById('label-renderer').appendChild(labelRenderer.domElement);

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Camera — farther back to see all 3 skeletons
    camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    camera.position.set(0, 1.2, 7.5);

    // Controls
    controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 0.5;
    controls.maxDistance = 20;
    controls.update();

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 2.0);
    scene.add(ambient);
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
    dirLight.position.set(2, 4, 3);
    scene.add(dirLight);

    // Ground grid (wider)
    const grid = new THREE.GridHelper(10, 50, 0x333355, 0x222244);
    scene.add(grid);

    // Create skeleton groups
    for (const [key, skel] of Object.entries(skeletons)) {
        skel.group = new THREE.Group();
        skel.group.position.x = skel.xOffset;
        scene.add(skel.group);
    }

    // Resize
    window.addEventListener('resize', onResize);

    // Panel toggle
    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => {
            h3.closest('.panel-section').classList.toggle('collapsed');
        });
    });

    // Visibility toggles
    bindToggles();

    // Playback controls
    bindPlaybackControls();

    // Start render loop
    animate();

    // Load data
    loadDefSkeleton();
    loadAnimationTree();
}

function onResize() {
    const container = renderer.domElement.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;
    renderer.setSize(w, h);
    labelRenderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
}

function animate() {
    requestAnimationFrame(animate);
    const dt = clock.getDelta();
    controls.update();

    if (mixer && playing) mixer.update(dt);

    // Update label positions
    labelRenderer.render(scene, camera);
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
// Visibility toggles
// =========================================================================
function bindToggles() {
    document.getElementById('toggle-labels').addEventListener('change', (e) => {
        const show = e.target.checked;
        for (const skel of Object.values(skeletons)) {
            skel.labels.forEach(lbl => { lbl.visible = show; });
        }
    });

    document.getElementById('toggle-def').addEventListener('change', (e) => {
        skeletons.def.group.visible = e.target.checked;
    });
    document.getElementById('toggle-cmu').addEventListener('change', (e) => {
        skeletons.cmu.group.visible = e.target.checked;
    });
    document.getElementById('toggle-mixamo').addEventListener('change', (e) => {
        skeletons.mixamo.group.visible = e.target.checked;
    });
    document.getElementById('toggle-mocapnet').addEventListener('change', (e) => {
        skeletons.mocapnet.group.visible = e.target.checked;
    });
}

// =========================================================================
// Bone Visualization — white cylinders + joint spheres
// =========================================================================
function createBoneViz(bones, skelKey, invScale) {
    const skel = skeletons[skelKey];
    removeBoneViz(skelKey);

    // invScale compensates for wrapper scaling so all skeletons look identical
    const s = invScale || 1;
    const jointGeo = new THREE.SphereGeometry(JOINT_RADIUS * s, 6, 4);
    const _up = new THREE.Vector3(0, 1, 0);

    for (const bone of bones) {
        // Joint sphere at each bone origin
        const joint = new THREE.Mesh(jointGeo, JOINT_MAT);
        joint.renderOrder = 998;
        bone.add(joint);
        skel.vizMeshes.push(joint);

        // Cylinder from parent to this bone
        if (!bone.parent || !bone.parent.isBone) continue;
        const len = bone.position.length();
        if (len < 0.0001) continue;

        const cylGeo = new THREE.CylinderGeometry(CYL_RADIUS_TOP * s, CYL_RADIUS_BOT * s, len, 4, 1);
        const cyl = new THREE.Mesh(cylGeo, BONE_MAT);
        cyl.renderOrder = 998;

        cyl.position.copy(bone.position).multiplyScalar(0.5);
        const dir = bone.position.clone().normalize();
        cyl.quaternion.setFromUnitVectors(_up, dir);

        bone.parent.add(cyl);
        skel.vizMeshes.push(cyl);
    }

    skel._jointGeo = jointGeo;
}

function removeBoneViz(skelKey) {
    const skel = skeletons[skelKey];
    for (const mesh of skel.vizMeshes) {
        if (mesh.parent) mesh.parent.remove(mesh);
        if (mesh.geometry) mesh.geometry.dispose();
    }
    skel.vizMeshes = [];
    skel._jointGeo = null;
}

// =========================================================================
// Bone Labels (CSS2DObjects) — sequential numbers only
// =========================================================================
function createBoneLabels(bones, skelKey) {
    const skel = skeletons[skelKey];
    // Remove old labels
    skel.labels.forEach(lbl => lbl.parent && lbl.parent.remove(lbl));
    skel.labels = [];

    const colorMap = { def: '#ff6666', cmu: '#66ff66', mixamo: '#ffaa66', mocapnet: '#6699ff' };
    const color = colorMap[skelKey] || '#ffffff';
    const showLabels = document.getElementById('toggle-labels').checked;

    // Store name mapping for tooltip/console lookup
    skel.boneIndex = [];

    for (let i = 0; i < bones.length; i++) {
        const bone = bones[i];
        skel.boneIndex.push(bone.name);

        const div = document.createElement('div');
        div.textContent = i;
        div.title = bone.name;
        div.style.cssText = `
            font-size: 8px;
            font-family: monospace;
            color: ${color};
            background: rgba(0,0,0,0.55);
            padding: 0px 2px;
            border-radius: 2px;
            line-height: 1.1;
            pointer-events: none;
        `;

        const label = new CSS2DObject(div);
        label.visible = showLabels;
        bone.add(label);
        skel.labels.push(label);
    }

    // Log mapping to console for reference
    console.log(`${skelKey.toUpperCase()} bone index:`, skel.boneIndex.map((n, i) => `${i}: ${n}`));
}

// =========================================================================
// DEF Skeleton (left, red)
// =========================================================================
async function loadDefSkeleton() {
    try {
        const [skelResp, swResp] = await Promise.all([
            fetch('/api/character/def-skeleton/'),
            fetch('/api/character/skin-weights/')
        ]);

        if (!skelResp.ok || !swResp.ok) {
            console.warn('DEF skeleton or skin weights not available');
            return;
        }

        defSkeletonData = await skelResp.json();
        skinWeightData = await swResp.json();

        const defSkel = buildDefSkeleton(defSkeletonData, skinWeightData);
        skeletons.def.rootBone = defSkel.rootBone;
        skeletons.def.boneByName = defSkel.boneByName;
        skeletons.def.skeleton = defSkel;
        skeletons.def.bones = defSkel.bones;
        skeletons.def.group.add(defSkel.rootBone);

        // Bone cylinders + joints (white)
        createBoneViz(defSkel.bones, 'def');

        // Bone number labels
        createBoneLabels(defSkel.bones, 'def');

        console.log(`DEF skeleton loaded: ${defSkel.bones.length} bones`);
    } catch (e) {
        console.error('Failed to load DEF skeleton:', e);
    }
}

// =========================================================================
// BVH Skeleton helper — load and place a BVH as a rest-pose skeleton
// =========================================================================
function placeBvhSkeleton(result, skelKey) {
    const skel = skeletons[skelKey];
    const bones = result.skeleton.bones;
    if (bones.length === 0) return;

    const rootBone = bones[0];
    rootBone.updateWorldMatrix(true, true);

    // Measure height and scale to ~1.68m
    const box = new THREE.Box3();
    const tmpVec = new THREE.Vector3();
    bones.forEach(b => { b.getWorldPosition(tmpVec); box.expandByPoint(tmpVec); });
    const bvhHeight = Math.max(box.max.y - box.min.y, 0.01);
    const targetH = 1.68;
    const scale = targetH / bvhHeight;

    // Wrapper group for scaling
    const wrapper = new THREE.Group();
    wrapper.scale.set(scale, scale, scale);
    wrapper.add(rootBone);
    skel.group.add(wrapper);
    skel.wrapper = wrapper;
    skel.rootBone = rootBone;
    skel.bones = bones;

    // Bone cylinders + joints — invScale compensates wrapper so sizes match DEF
    createBoneViz(bones, skelKey, 1 / scale);

    // Bone number labels
    createBoneLabels(bones, skelKey);

    console.log(`${skelKey.toUpperCase()} skeleton placed: ${bones.length} bones, scale=${scale.toFixed(3)}`);
}

// =========================================================================
// Animation Tree
// =========================================================================
async function loadAnimationTree() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        allAnimations = data.categories || {};

        const tree = document.getElementById('anim-tree');
        tree.innerHTML = '';

        const catNames = Object.keys(allAnimations).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:16px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = allAnimations[cat];
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
                item.dataset.category = cat;
                item.innerHTML = `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    loadAndPlayAnimation(anim.url, anim.name, anim.frames, cat);
                });
                body.appendChild(item);
            });

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        });

        // Auto-load first CMU and MocapNET animations for rest-pose display
        autoLoadRestPoseSkeletons();
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

// =========================================================================
// Auto-load first BVH of each type for rest-pose display
// =========================================================================
function autoLoadRestPoseSkeletons() {
    let cmuAnim = null;
    let mixamoAnim = null;
    let mocapnetAnim = null;

    for (const cat of Object.keys(allAnimations)) {
        for (const anim of allAnimations[cat]) {
            if (cat === 'MocapNET') {
                if (!mocapnetAnim) mocapnetAnim = anim;
            } else if (cat === 'Mixamo') {
                if (!mixamoAnim) mixamoAnim = anim;
            } else {
                if (!cmuAnim) cmuAnim = anim;
            }
        }
    }

    // Load CMU rest-pose skeleton (green)
    if (cmuAnim) {
        bvhLoader.load(cmuAnim.url, (result) => {
            const format = detectBVHFormat(result.skeleton.bones);
            if (format === 'CMU') {
                placeBvhSkeleton(result, 'cmu');
                skeletons.cmu.bvhResult = result;
            }
        });
    }

    // Load Mixamo rest-pose skeleton (orange)
    if (mixamoAnim) {
        bvhLoader.load(mixamoAnim.url, (result) => {
            const format = detectBVHFormat(result.skeleton.bones);
            if (format === 'MIXAMO') {
                placeBvhSkeleton(result, 'mixamo');
                skeletons.mixamo.bvhResult = result;
            }
        });
    }

    // Load MocapNET rest-pose skeleton (blue)
    if (mocapnetAnim) {
        bvhLoader.load(mocapnetAnim.url, (result) => {
            const format = detectBVHFormat(result.skeleton.bones);
            if (format === 'MOCAPNET') {
                placeBvhSkeleton(result, 'mocapnet');
                skeletons.mocapnet.bvhResult = result;
            }
        });
    }
}

// =========================================================================
// Load & Play Animation on all 3 skeletons
// =========================================================================
function loadAndPlayAnimation(url, name, fc, category) {
    stopAnimation();
    document.getElementById('anim-info').textContent = `Lade ${name}...`;

    bvhLoader.load(url, (result) => {
        const bones = result.skeleton.bones;
        if (bones.length === 0) return;

        const format = detectBVHFormat(bones);
        currentBvhResult = result;
        currentFormat = format;

        // Create a multi-target mixer using a common root
        // We use separate mixers for each skeleton

        const mixers = [];

        // --- BVH skeleton (position depends on format) ---
        const bvhKey = format === 'CMU' ? 'cmu'
                     : format === 'MIXAMO' ? 'mixamo'
                     : 'mocapnet';
        const bvhSkel = skeletons[bvhKey];

        // Remove old BVH skeleton
        if (bvhSkel.wrapper) {
            bvhSkel.group.remove(bvhSkel.wrapper);
            bvhSkel.wrapper = null;
        }
        removeBoneViz(bvhKey);
        bvhSkel.labels.forEach(lbl => lbl.parent && lbl.parent.remove(lbl));
        bvhSkel.labels = [];

        // Place the new BVH skeleton
        placeBvhSkeleton(result, bvhKey);

        // Play animation on BVH skeleton
        const bvhMixer = new THREE.AnimationMixer(bvhSkel.rootBone);
        const bvhAction = bvhMixer.clipAction(result.clip);
        bvhAction.play();
        mixers.push(bvhMixer);
        window._cmuMixer = bvhMixer;
        window._cmuRootBone = bvhSkel.rootBone;

        // --- DEF skeleton (left, red) — retargeted ---
        if (skeletons.def.skeleton && defSkeletonData && skinWeightData) {
            try {
                skeletons.def.skeleton.skeleton.pose();
                const clip = retargetBVHToDefClip(result, skeletons.def.skeleton, format);
                const defMixer = new THREE.AnimationMixer(skeletons.def.rootBone);
                const defAction = defMixer.clipAction(clip);
                defAction.play();
                mixers.push(defMixer);
                // Debug exports for Playwright testing
                window._defMixer = defMixer;
                window._defRootBone = skeletons.def.rootBone;
                window._defClip = clip;
            } catch (e) {
                console.error('DEF retarget failed:', e.message);
            }
        }

        // Store combined mixer
        mixer = {
            _mixers: mixers,
            update(dt) { for (const m of this._mixers) m.update(dt); },
            stopAllAction() { for (const m of this._mixers) m.stopAllAction(); },
            setTime(t) { for (const m of this._mixers) m.setTime(t); },
        };
        currentAction = { clip: result.clip, paused: false };
        playing = true;

        document.getElementById('anim-play').innerHTML = '<i class="fas fa-pause"></i>';
        document.getElementById('anim-info').textContent =
            `${name} — ${fc}f — ${result.clip.duration.toFixed(1)}s — ${format}`;
    }, undefined, (err) => {
        console.error('Failed to load BVH:', err);
        document.getElementById('anim-info').textContent = `Fehler: ${name}`;
    });
}

function stopAnimation() {
    if (mixer) {
        mixer.stopAllAction();
        mixer = null;
    }
    currentAction = null;
    currentBvhResult = null;

    // Reset DEF skeleton to rest pose
    if (skeletons.def.skeleton) {
        skeletons.def.skeleton.skeleton.pose();
    }

    playing = false;
}

// =========================================================================
// Playback controls
// =========================================================================
function bindPlaybackControls() {
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');

    playBtn.addEventListener('click', () => {
        if (!currentAction) return;
        playing = !playing;
        currentAction.paused = !playing;
        playBtn.innerHTML = playing
            ? '<i class="fas fa-pause"></i>'
            : '<i class="fas fa-play"></i>';
    });

    stopBtn.addEventListener('click', () => {
        stopAnimation();
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
        timeline.value = 0;
        document.getElementById('anim-info').textContent = '—';
        document.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
    });

    timeline.addEventListener('input', () => {
        if (currentAction && mixer) {
            const clip = currentAction.clip;
            const time = (parseInt(timeline.value) / 100) * clip.duration;
            mixer.setTime(time);
        }
    });
}

// =========================================================================
// Boot
// =========================================================================
init();
