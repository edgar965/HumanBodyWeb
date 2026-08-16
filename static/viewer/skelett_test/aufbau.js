import * as THREE from 'three';
import { Testzustand } from './testzustand.js';
import { loadRetargetConfig } from '../retarget_hybrid.js?v=32';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { loadRigifySkeleton } from '../skeleton_test.js';
import { loadAnimationTree, bindPlaybackControls } from './animationsliste.js';
/**
 * Aufbau der Vergleichsseite: Szene, Umschalter, Zeichenschleife.
 *
 * Aus skeleton_test.js herausgeloest (Umbau 16.08.2026).
 */


// =========================================================================
// Initialization
// =========================================================================
export async function init() {
    await loadRetargetConfig();
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    // WebGL Renderer
    Testzustand.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    Testzustand.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    Testzustand.renderer.setSize(w, h);
    Testzustand.renderer.outputColorSpace = THREE.SRGBColorSpace;

    // CSS2D Renderer for bone labels
    Testzustand.labelRenderer = new CSS2DRenderer();
    Testzustand.labelRenderer.setSize(w, h);
    Testzustand.labelRenderer.domElement.style.position = 'absolute';
    Testzustand.labelRenderer.domElement.style.top = '0';
    Testzustand.labelRenderer.domElement.style.left = '0';
    Testzustand.labelRenderer.domElement.style.pointerEvents = 'none';
    document.getElementById('label-renderer').appendChild(Testzustand.labelRenderer.domElement);

    // Scene
    Testzustand.scene = new THREE.Scene();
    Testzustand.scene.background = new THREE.Color(0x1a1a2e);

    // Camera — farther back to see all 3 Testzustand.skeletons
    Testzustand.camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    Testzustand.camera.position.set(0, 1.2, 7.5);

    // Controls
    Testzustand.controls = new OrbitControls(Testzustand.camera, canvas);
    Testzustand.controls.target.set(0, 0.9, 0);
    Testzustand.controls.enableDamping = true;
    Testzustand.controls.dampingFactor = 0.08;
    Testzustand.controls.minDistance = 0.5;
    Testzustand.controls.maxDistance = 20;
    Testzustand.controls.update();

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 2.0);
    Testzustand.scene.add(ambient);
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
    dirLight.position.set(2, 4, 3);
    Testzustand.scene.add(dirLight);

    // Ground grid (wider)
    const grid = new THREE.GridHelper(10, 50, 0x333355, 0x222244);
    Testzustand.scene.add(grid);

    // Create skeleton groups
    for (const [key, skel] of Object.entries(Testzustand.skeletons)) {
        skel.group = new THREE.Group();
        skel.group.position.x = skel.xOffset;
        if (skel.zOffset) skel.group.position.z = skel.zOffset;
        Testzustand.scene.add(skel.group);
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

    // Playback Testzustand.controls
    bindPlaybackControls();

    // Start render loop
    animate();

    // Debug exports for Playwright / console
    window.camera = Testzustand.camera;
    window.controls = Testzustand.controls;
    window.scene = Testzustand.scene;
    window.skeletons = Testzustand.skeletons;

    // Load data
    loadRigifySkeleton();
    loadAnimationTree();
}

export function onResize() {
    const container = Testzustand.renderer.domElement.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;
    Testzustand.renderer.setSize(w, h);
    Testzustand.labelRenderer.setSize(w, h);
    Testzustand.camera.aspect = w / h;
    Testzustand.camera.updateProjectionMatrix();
}

export function animate() {
    requestAnimationFrame(animate);
    const dt = Testzustand.clock.getDelta();
    Testzustand.controls.update();

    if (Testzustand.mixer && Testzustand.playing) Testzustand.mixer.update(dt);

    // Update label positions
    Testzustand.labelRenderer.render(Testzustand.scene, Testzustand.camera);
    Testzustand.renderer.render(Testzustand.scene, Testzustand.camera);

    // FPS counter
    Testzustand.frameCount++;
    Testzustand.fpsAccum += dt;
    if (Testzustand.fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = Testzustand.frameCount;
        Testzustand.frameCount = 0;
        Testzustand.fpsAccum = 0;
    }
}

// =========================================================================
// Visibility toggles
// =========================================================================
export function bindToggles() {
    document.getElementById('toggle-labels').addEventListener('change', (e) => {
        const show = e.target.checked;
        for (const skel of Object.values(Testzustand.skeletons)) {
            skel.labels.forEach(lbl => { lbl.visible = show; });
        }
    });

    document.getElementById('toggle-def').addEventListener('change', (e) => {
        Testzustand.skeletons.def.group.visible = e.target.checked;
    });
    document.getElementById('toggle-cmu').addEventListener('change', (e) => {
        Testzustand.skeletons.cmu.group.visible = e.target.checked;
    });
    document.getElementById('toggle-mixamo').addEventListener('change', (e) => {
        Testzustand.skeletons.mixamo.group.visible = e.target.checked;
    });
    document.getElementById('toggle-mocapnet').addEventListener('change', (e) => {
        Testzustand.skeletons.mocapnet.group.visible = e.target.checked;
    });
    document.getElementById('toggle-bandai').addEventListener('change', (e) => {
        Testzustand.skeletons.bandai.group.visible = e.target.checked;
    });
    document.getElementById('toggle-smpl').addEventListener('change', (e) => {
        Testzustand.skeletons.smpl.group.visible = e.target.checked;
    });
    document.getElementById('toggle-openpose').addEventListener('change', (e) => {
        Testzustand.skeletons.openpose.group.visible = e.target.checked;
    });
}
