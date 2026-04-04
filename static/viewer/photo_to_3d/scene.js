/**
 * Photo To 3D — Scene setup: init renderer, camera, controls, lighting, resize, animate.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { state, MODEL_OFFSET_X, SMPLX_OFFSET_X } from './state.js';
import { fn } from './registry.js';

export function initScene() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    state.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    state.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    state.renderer.setSize(w, h);
    state.renderer.outputColorSpace = THREE.SRGBColorSpace;
    state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    state.renderer.toneMappingExposure = 1.6;

    state.scene = new THREE.Scene();
    state.scene.background = new THREE.Color(0x1a1a2e);

    state.camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    state.camera.position.set(0, 1.0, 4.5);

    state.controls = new OrbitControls(state.camera, canvas);
    state.controls.target.set(0, 0.9, 0);
    // Expose for debugging (Playwright access)
    window._debugCamera = state.camera;
    window._debugControls = state.controls;
    window._debugScene = state.scene;
    state.controls.enableDamping = true;
    state.controls.dampingFactor = 0.08;
    state.controls.minDistance = 0.5;
    state.controls.maxDistance = 15;
    state.controls.update();

    // Lighting
    state.scene.add(new THREE.DirectionalLight(0xffffff, 3.0).translateX(2).translateY(4).translateZ(-5));
    state.scene.add(new THREE.DirectionalLight(0xeeeeff, 2.0).translateX(-3).translateY(3).translateZ(-4));
    state.scene.add(new THREE.DirectionalLight(0xffeedd, 2.5).translateX(0).translateY(4).translateZ(5));
    state.scene.add(new THREE.AmbientLight(0xffffff, 0.8));

    // Ground grid
    state.scene.add(new THREE.GridHelper(6, 30, 0x333355, 0x222244));

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
    state.scene.add(sprite);
}

function onResize() {
    const container = state.renderer.domElement.parentElement;
    const w = Math.max(container.clientWidth, 100);
    const h = container.clientHeight || window.innerHeight;
    state.renderer.setSize(w, h);
    state.camera.aspect = w / h;
    state.camera.updateProjectionMatrix();
}

export function animate() {
    requestAnimationFrame(animate);
    state.controls.update();
    state.renderer.render(state.scene, state.camera);

    state.frameCount++;
    state.fpsAccum += state.clock.getDelta();
    if (state.fpsAccum >= 1.0) {
        const el = document.getElementById('fps-display');
        if (el) el.textContent = state.frameCount;
        state.frameCount = 0;
        state.fpsAccum = 0;
    }
}

fn.initScene = initScene;
fn.animate = animate;
