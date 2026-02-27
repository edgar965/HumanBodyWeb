/**
 * HumanBody Scene Configuration — Three.js renderer with live UI controls
 * for lighting, renderer, camera, and material settings.
 * Auto-saves to localStorage; all other pages read these settings.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { detectBVHFormat, retargetBVHToDefClip } from './retarget_hybrid.js?v=17';

// =========================================================================
// Light Presets
// =========================================================================
const LIGHT_PRESETS = {
    studio: {
        key:     { intensity: 3.0, color: 0xffffff, pos: [2, 4, -5] },
        fill:    { intensity: 2.0, color: 0xeeeeff, pos: [-3, 3, -4] },
        back:    { intensity: 2.5, color: 0xffeedd, pos: [0, 4, 5] },
        ambient: { intensity: 0.8, color: 0xffffff },
        exposure: 1.6
    },
    outdoor: {
        key:     { intensity: 4.0, color: 0xfff5e0, pos: [5, 8, -2] },
        fill:    { intensity: 1.5, color: 0x8899cc, pos: [-4, 2, -3] },
        back:    { intensity: 1.0, color: 0xffeedd, pos: [-2, 3, 4] },
        ambient: { intensity: 1.2, color: 0xddeeff },
        exposure: 1.8
    },
    dramatic: {
        key:     { intensity: 4.5, color: 0xffddaa, pos: [4, 3, -3] },
        fill:    { intensity: 0.5, color: 0x4444aa, pos: [-3, 1, -2] },
        back:    { intensity: 3.0, color: 0xff8844, pos: [0, 3, 5] },
        ambient: { intensity: 0.3, color: 0x222244 },
        exposure: 1.4
    },
    neutral: {
        key:     { intensity: 2.5, color: 0xffffff, pos: [3, 5, -4] },
        fill:    { intensity: 2.5, color: 0xffffff, pos: [-3, 5, -4] },
        back:    { intensity: 2.0, color: 0xffffff, pos: [0, 4, 5] },
        ambient: { intensity: 1.0, color: 0xffffff },
        exposure: 1.6
    }
};

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

// Lights — global so UI can modify them
let keyLight, fillLight, backLight, ambientLight;

// Animation
let mixer = null;
let currentAction = null;
let skeletonHelper = null;
let playing = false;
const bvhLoader = new BVHLoader();
let defSkeletonData = null;
let skinWeightData = null;
let defSkeleton = null;
let isSkinned = false;
let skelWrapper = null;

// Rig
let rigVisible = false;

// Auto-save debounce
let saveTimer = null;

// =========================================================================
// Initialization
// =========================================================================
function init() {
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
    keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    scene.add(keyLight);

    fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    scene.add(fillLight);

    backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    scene.add(backLight);

    ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

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
    fetch('/api/settings/humanbody/')
        .then(r => r.json())
        .then(s => {
            const expanded = s.expanded_panels_scene;
            if (!Array.isArray(expanded)) return;
            document.querySelectorAll('.panel-section[data-panel-key]').forEach(panel => {
                if (expanded.includes(panel.dataset.panelKey)) {
                    panel.classList.remove('collapsed');
                } else {
                    panel.classList.add('collapsed');
                }
            });
        })
        .catch(() => {});

    // Bind all UI controls
    bindLightingUI();
    bindRendererUI();
    bindCameraUI();
    bindActions();
    initSaveButtons();

    // Rig toggle — single SkeletonHelper from defSkeleton
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigVisible) {
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
            } else {
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
                playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            }
        });
    }

    // Load saved settings from localStorage
    loadSettings();

    // Start render loop
    animate();

    // Load mesh + rig + skeleton data for animation
    loadMesh();
    loadDefSkeleton();
    loadSkinWeights();
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

    // Update camera info display
    updateCameraInfo();

    // FPS counter
    frameCount++;
    fpsAccum += dt;
    if (fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = frameCount;
        frameCount = 0;
        fpsAccum = 0;
    }
}

function updateCameraInfo() {
    const p = camera.position;
    const t = controls.target;
    document.getElementById('cam-pos').textContent =
        `${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(2)}`;
    document.getElementById('cam-target').textContent =
        `${t.x.toFixed(2)}, ${t.y.toFixed(2)}, ${t.z.toFixed(2)}`;
}

// =========================================================================
// Auto-save — debounced save to localStorage on every change
// =========================================================================
function autoSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
        const settings = gatherSettings();
        localStorage.setItem('humanbody_scene_settings', JSON.stringify(settings));
    }, 300);
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

        onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

// (Rig visualization now uses SkeletonHelper from defSkeleton — no separate rigGroup)

// =========================================================================
// UI Bindings: Lighting
// =========================================================================
function bindLightingUI() {
    function bindSlider(id, displayId, toDisplay, onChange) {
        const slider = document.getElementById(id);
        const display = document.getElementById(displayId);
        slider.addEventListener('input', () => {
            const v = parseFloat(slider.value);
            display.textContent = toDisplay(v);
            onChange(v);
            autoSave();
        });
    }

    // Key Light
    bindSlider('key-intensity', 'key-intensity-val', v => (v / 100).toFixed(1), v => {
        keyLight.intensity = v / 100;
    });
    document.getElementById('key-color').addEventListener('input', e => {
        keyLight.color.set(e.target.value); autoSave();
    });
    bindSlider('key-pos-x', 'key-pos-x-val', v => (v / 10).toFixed(1), v => {
        keyLight.position.x = v / 10;
    });
    bindSlider('key-pos-y', 'key-pos-y-val', v => (v / 10).toFixed(1), v => {
        keyLight.position.y = v / 10;
    });
    bindSlider('key-pos-z', 'key-pos-z-val', v => (v / 10).toFixed(1), v => {
        keyLight.position.z = v / 10;
    });

    // Fill Light
    bindSlider('fill-intensity', 'fill-intensity-val', v => (v / 100).toFixed(1), v => {
        fillLight.intensity = v / 100;
    });
    document.getElementById('fill-color').addEventListener('input', e => {
        fillLight.color.set(e.target.value); autoSave();
    });
    bindSlider('fill-pos-x', 'fill-pos-x-val', v => (v / 10).toFixed(1), v => {
        fillLight.position.x = v / 10;
    });
    bindSlider('fill-pos-y', 'fill-pos-y-val', v => (v / 10).toFixed(1), v => {
        fillLight.position.y = v / 10;
    });
    bindSlider('fill-pos-z', 'fill-pos-z-val', v => (v / 10).toFixed(1), v => {
        fillLight.position.z = v / 10;
    });

    // Back Light
    bindSlider('back-intensity', 'back-intensity-val', v => (v / 100).toFixed(1), v => {
        backLight.intensity = v / 100;
    });
    document.getElementById('back-color').addEventListener('input', e => {
        backLight.color.set(e.target.value); autoSave();
    });
    bindSlider('back-pos-x', 'back-pos-x-val', v => (v / 10).toFixed(1), v => {
        backLight.position.x = v / 10;
    });
    bindSlider('back-pos-y', 'back-pos-y-val', v => (v / 10).toFixed(1), v => {
        backLight.position.y = v / 10;
    });
    bindSlider('back-pos-z', 'back-pos-z-val', v => (v / 10).toFixed(1), v => {
        backLight.position.z = v / 10;
    });

    // Ambient
    bindSlider('ambient-intensity', 'ambient-intensity-val', v => (v / 100).toFixed(1), v => {
        ambientLight.intensity = v / 100;
    });
    document.getElementById('ambient-color').addEventListener('input', e => {
        ambientLight.color.set(e.target.value); autoSave();
    });

    // Preset dropdown
    document.getElementById('light-preset').addEventListener('change', e => {
        const preset = LIGHT_PRESETS[e.target.value];
        if (!preset) return;
        applyPreset(preset);
        autoSave();
    });
}

function applyPreset(preset) {
    keyLight.intensity = preset.key.intensity;
    keyLight.color.setHex(preset.key.color);
    keyLight.position.set(...preset.key.pos);

    fillLight.intensity = preset.fill.intensity;
    fillLight.color.setHex(preset.fill.color);
    fillLight.position.set(...preset.fill.pos);

    backLight.intensity = preset.back.intensity;
    backLight.color.setHex(preset.back.color);
    backLight.position.set(...preset.back.pos);

    ambientLight.intensity = preset.ambient.intensity;
    ambientLight.color.setHex(preset.ambient.color);

    renderer.toneMappingExposure = preset.exposure;

    syncUIFromState();
}

function syncUIFromState() {
    setSlider('key-intensity', keyLight.intensity * 100, 'key-intensity-val', v => (v / 100).toFixed(1));
    setColor('key-color', keyLight.color);
    setSlider('key-pos-x', keyLight.position.x * 10, 'key-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('key-pos-y', keyLight.position.y * 10, 'key-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('key-pos-z', keyLight.position.z * 10, 'key-pos-z-val', v => (v / 10).toFixed(1));

    setSlider('fill-intensity', fillLight.intensity * 100, 'fill-intensity-val', v => (v / 100).toFixed(1));
    setColor('fill-color', fillLight.color);
    setSlider('fill-pos-x', fillLight.position.x * 10, 'fill-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('fill-pos-y', fillLight.position.y * 10, 'fill-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('fill-pos-z', fillLight.position.z * 10, 'fill-pos-z-val', v => (v / 10).toFixed(1));

    setSlider('back-intensity', backLight.intensity * 100, 'back-intensity-val', v => (v / 100).toFixed(1));
    setColor('back-color', backLight.color);
    setSlider('back-pos-x', backLight.position.x * 10, 'back-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('back-pos-y', backLight.position.y * 10, 'back-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('back-pos-z', backLight.position.z * 10, 'back-pos-z-val', v => (v / 10).toFixed(1));

    setSlider('ambient-intensity', ambientLight.intensity * 100, 'ambient-intensity-val', v => (v / 100).toFixed(1));
    setColor('ambient-color', ambientLight.color);

    setSlider('exposure', renderer.toneMappingExposure * 100, 'exposure-val', v => (v / 100).toFixed(1));

    const tmSelect = document.getElementById('tone-mapping');
    for (const [name, val] of Object.entries(TONE_MAPPINGS)) {
        if (val === renderer.toneMapping) { tmSelect.value = name; break; }
    }

    setColor('bg-color', scene.background);
    setSlider('camera-fov', camera.fov, 'camera-fov-val', v => Math.round(v).toString());
}

function setSlider(id, value, displayId, toDisplay) {
    const slider = document.getElementById(id);
    slider.value = Math.round(value);
    document.getElementById(displayId).textContent = toDisplay(parseFloat(slider.value));
}

function setColor(id, threeColor) {
    document.getElementById(id).value = '#' + threeColor.getHexString();
}

// =========================================================================
// UI Bindings: Renderer
// =========================================================================
function bindRendererUI() {
    document.getElementById('tone-mapping').addEventListener('change', e => {
        renderer.toneMapping = TONE_MAPPINGS[e.target.value] || THREE.ACESFilmicToneMapping;
        autoSave();
    });

    const expSlider = document.getElementById('exposure');
    const expVal = document.getElementById('exposure-val');
    expSlider.addEventListener('input', () => {
        const v = parseFloat(expSlider.value) / 100;
        expVal.textContent = v.toFixed(1);
        renderer.toneMappingExposure = v;
        autoSave();
    });

    document.getElementById('bg-color').addEventListener('input', e => {
        scene.background.set(e.target.value);
        autoSave();
    });
}

// =========================================================================
// UI Bindings: Camera
// =========================================================================
function bindCameraUI() {
    const fovSlider = document.getElementById('camera-fov');
    const fovVal = document.getElementById('camera-fov-val');
    fovSlider.addEventListener('input', () => {
        const v = parseInt(fovSlider.value);
        fovVal.textContent = v;
        camera.fov = v;
        camera.updateProjectionMatrix();
        autoSave();
    });
}

// (Material/Skin UI removed — now lives in Konfiguration/Body Type panel)

// =========================================================================
// Actions
// =========================================================================
function bindActions() {
    // Manual save (redundant with auto-save but gives visual confirmation)
    document.getElementById('btn-apply').addEventListener('click', () => {
        const settings = gatherSettings();
        localStorage.setItem('humanbody_scene_settings', JSON.stringify(settings));
        const btn = document.getElementById('btn-apply');
        const orig = btn.textContent;
        btn.textContent = 'Gespeichert!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
    });

    // Reset
    document.getElementById('btn-reset').addEventListener('click', () => {
        applyPreset(LIGHT_PRESETS.studio);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        scene.background.set(0x1a1a2e);
        camera.fov = 35;
        camera.updateProjectionMatrix();
        document.getElementById('light-preset').value = 'studio';
        syncUIFromState();
        autoSave();
    });

    // Export
    document.getElementById('btn-export').addEventListener('click', () => {
        const settings = gatherSettings();
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'humanbody_scene_settings.json';
        a.click();
        URL.revokeObjectURL(url);
    });
}

function gatherSettings() {
    return {
        lighting: {
            key: {
                intensity: keyLight.intensity,
                color: '#' + keyLight.color.getHexString(),
                pos: [keyLight.position.x, keyLight.position.y, keyLight.position.z]
            },
            fill: {
                intensity: fillLight.intensity,
                color: '#' + fillLight.color.getHexString(),
                pos: [fillLight.position.x, fillLight.position.y, fillLight.position.z]
            },
            back: {
                intensity: backLight.intensity,
                color: '#' + backLight.color.getHexString(),
                pos: [backLight.position.x, backLight.position.y, backLight.position.z]
            },
            ambient: {
                intensity: ambientLight.intensity,
                color: '#' + ambientLight.color.getHexString()
            }
        },
        renderer: {
            toneMapping: document.getElementById('tone-mapping').value,
            exposure: renderer.toneMappingExposure,
            background: '#' + scene.background.getHexString()
        },
        camera: {
            fov: camera.fov
        },
    };
}

// =========================================================================
// Load settings from localStorage
// =========================================================================
function loadSettings() {
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
                ambientLight.intensity = s.lighting.ambient.intensity;
                ambientLight.color.set(s.lighting.ambient.color);
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

        document.getElementById('light-preset').value = '';
        syncUIFromState();

    } catch (e) {
        console.warn('Failed to load scene settings:', e);
    }
}

// =========================================================================
// DEF Skeleton + Skin Weights + BVH Animation
// =========================================================================
async function loadDefSkeleton() {
    try {
        const resp = await fetch('/api/character/def-skeleton/');
        if (resp.ok) defSkeletonData = await resp.json();
    } catch (e) { /* optional */ }
}

async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) skinWeightData = await resp.json();
    } catch (e) { /* optional */ }
}

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
        } else if (!rootBone) {
            rootBone = bone;
        }
    }
    for (let i = 0; i < bones.length; i++) {
        const name = swData.bone_names[i];
        const data = skelByName[name];
        if (!data) continue;
        if (!data.parent && bones[i] !== rootBone && rootBone) rootBone.add(bones[i]);
    }
    if (!rootBone && bones.length > 0) rootBone = bones[0];
    rootBone.updateWorldMatrix(true, true);
    return { skeleton: new THREE.Skeleton(bones), rootBone, bones, boneByName };
}

function convertToDefSkinnedMesh() {
    if (isSkinned || !bodyMesh || !bodyGeometry || !skinWeightData) return;
    bodyGeometry = bodyGeometry.clone();
    const vCount = bodyGeometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);
    for (let v = 0; v < vCount; v++) {
        const infs = skinWeightData.weights[v] || [];
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
    defSkeleton = buildDefSkeleton(defSkeletonData, skinWeightData);
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
}

function loadBVHAnimation(url, name, fc) {
    stopAnimation(true);
    bvhLoader.load(url, (result) => {
        const bvhBones = result.skeleton.bones;
        if (bvhBones.length === 0) return;
        if (defSkeletonData && skinWeightData && bodyMesh) {
            if (!isSkinned) convertToDefSkinnedMesh();
            const format = detectBVHFormat(bvhBones);
            const clip = retargetBVHToDefClip(result, defSkeleton, format, { bodyMesh });
            // Ensure SkeletonHelper exists for DEF skeleton
            if (!skeletonHelper) {
                skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
                skeletonHelper.material.depthTest = false;
                skeletonHelper.material.depthWrite = false;
                skeletonHelper.material.color.set(0x00ffaa);
                skeletonHelper.renderOrder = 999;
                skeletonHelper.visible = rigVisible;
                scene.add(skeletonHelper);
            }
            mixer = new THREE.AnimationMixer(bodyMesh);
            currentAction = mixer.clipAction(clip);
            currentAction.play();
            playing = true;
        } else {
            // Fallback: BVH skeleton only
            const rootBone = bvhBones[0];
            rootBone.updateWorldMatrix(true, true);
            const skelBox = new THREE.Box3();
            const tmpVec = new THREE.Vector3();
            bvhBones.forEach(b => { b.updateWorldMatrix(true, false); b.getWorldPosition(tmpVec); skelBox.expandByPoint(tmpVec); });
            let bodyHeight = 1.75;
            if (bodyMesh) { const bb = new THREE.Box3().setFromObject(bodyMesh); if (!bb.isEmpty()) bodyHeight = bb.max.y - bb.min.y; }
            const scale = bodyHeight / Math.max(skelBox.max.y - skelBox.min.y, 0.01);
            skelWrapper = new THREE.Group();
            skelWrapper.scale.set(scale, scale, scale);
            skelWrapper.add(rootBone);
            scene.add(skelWrapper);
            if (skeletonHelper) scene.remove(skeletonHelper);
            skeletonHelper = new THREE.SkeletonHelper(rootBone);
            skeletonHelper.material.depthTest = false;
            skeletonHelper.material.depthWrite = false;
            skeletonHelper.material.color.set(0x00ffaa);
            skeletonHelper.renderOrder = 999;
            skeletonHelper.visible = rigVisible;
            scene.add(skeletonHelper);
            mixer = new THREE.AnimationMixer(rootBone);
            currentAction = mixer.clipAction(result.clip);
            currentAction.play();
            playing = true;
        }
    }, undefined, (err) => { console.error('Failed to load BVH:', err); });
}

function stopAnimation(destroy = false) {
    if (currentAction) { currentAction.stop(); currentAction.reset(); if (destroy) currentAction = null; }
    if (mixer && destroy) { mixer.stopAllAction(); mixer = null; }
    if (isSkinned && defSkeleton) defSkeleton.skeleton.pose();
    // Clean up animation skeleton; recreate from DEF skeleton if rig visible
    if (skelWrapper) { scene.remove(skelWrapper); skelWrapper = null; }
    if (skeletonHelper) { scene.remove(skeletonHelper); skeletonHelper = null; }
    if (rigVisible && defSkeleton) {
        skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
        skeletonHelper.material.depthTest = false;
        skeletonHelper.material.depthWrite = false;
        skeletonHelper.material.color.set(0x00ffaa);
        skeletonHelper.renderOrder = 999;
        scene.add(skeletonHelper);
    }
    playing = false;
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
    // Override scene with current scene settings
    model.scene = gatherSettings();
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
            if (s.scene) currentPresetName = s.scene;
            // Apply rig visibility from settings
            if (s.show_rig_scene) {
                rigVisible = true;
                const rigToggle = document.getElementById('rig-toggle');
                if (rigToggle) rigToggle.classList.add('active');
            }
            // Auto-play default animation
            if (s.default_anim_scene) {
                // Wait for mesh + skeleton to be ready
                const waitForMesh = async () => {
                    const maxWait = 15000;
                    const start = Date.now();
                    while (!bodyMesh && Date.now() - start < maxWait) {
                        await new Promise(r => setTimeout(r, 200));
                    }
                    if (bodyMesh) {
                        await new Promise(r => setTimeout(r, 1000));
                        loadBVHAnimation(s.default_anim_scene, 'Default', 0);
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
