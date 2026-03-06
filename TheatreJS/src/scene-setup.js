import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Create a theatrical ballet-stage scene with spotlights, dark wood floor,
 * and dramatic lighting.
 * @param {HTMLCanvasElement} canvas
 * @returns {{ scene, camera, renderer, controls, lights }}
 */
export function createScene(canvas) {
    // Renderer
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2; // Increased from 0.9 for brighter scene
    renderer.outputColorSpace = THREE.SRGBColorSpace; // CRITICAL for PBR materials!

    // Scene — dark blue-black theatre backdrop
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x080812);
    scene.fog = new THREE.FogExp2(0x080812, 0.04);

    // Camera
    const camera = new THREE.PerspectiveCamera(
        50,
        canvas.clientWidth / canvas.clientHeight,
        0.1,
        1000
    );
    camera.position.set(0, 1.6, 5);

    // Controls
    const controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.update();

    // ── Stage floor — dark polished wood ──
    const stageGeo = new THREE.PlaneGeometry(14, 10);
    const stageMat = new THREE.MeshStandardMaterial({
        color: 0x2a1a0e,
        roughness: 0.35,
        metalness: 0.05,
    });
    const stageFloor = new THREE.Mesh(stageGeo, stageMat);
    stageFloor.rotation.x = -Math.PI / 2;
    stageFloor.position.y = -0.01;
    stageFloor.receiveShadow = true;
    scene.add(stageFloor);

    // Thin edge strip to define stage boundary
    const edgeGeo = new THREE.BoxGeometry(14.2, 0.06, 10.2);
    const edgeMat = new THREE.MeshStandardMaterial({
        color: 0x1a0f06,
        roughness: 0.6,
    });
    const stageEdge = new THREE.Mesh(edgeGeo, edgeMat);
    stageEdge.position.y = -0.04;
    stageEdge.receiveShadow = true;
    scene.add(stageEdge);

    // ── Lighting — theatrical 3-point + spotlights ──

    // Very dim ambient (theatre darkness)
    const ambient = new THREE.AmbientLight(0x1a1a2e, 0.15);
    scene.add(ambient);

    // Spot 1 — warm key from front-left above
    const spotLeft = new THREE.SpotLight(0xffeedd, 25); // Increased from 8
    spotLeft.position.set(-3, 6, 3);
    spotLeft.target.position.set(0, 0, 0);
    spotLeft.angle = Math.PI / 6;
    spotLeft.penumbra = 0.5;
    spotLeft.decay = 1.5;
    spotLeft.castShadow = true;
    spotLeft.shadow.mapSize.set(2048, 2048);
    spotLeft.shadow.camera.near = 1;
    spotLeft.shadow.camera.far = 15;
    scene.add(spotLeft);
    scene.add(spotLeft.target);

    // Spot 2 — warm key from front-right above
    const spotRight = new THREE.SpotLight(0xffeedd, 25); // Increased from 8
    spotRight.position.set(3, 6, 3);
    spotRight.target.position.set(0, 0, 0);
    spotRight.angle = Math.PI / 6;
    spotRight.penumbra = 0.5;
    spotRight.decay = 1.5;
    spotRight.castShadow = true;
    spotRight.shadow.mapSize.set(2048, 2048);
    spotRight.shadow.camera.near = 1;
    spotRight.shadow.camera.far = 15;
    scene.add(spotRight);
    scene.add(spotRight.target);

    // Spot 3 — blue-violet backlight (rim light from behind)
    const backLight = new THREE.SpotLight(0x6644aa, 15); // Increased from 6
    backLight.position.set(0, 5, -4);
    backLight.target.position.set(0, 0.5, 0);
    backLight.angle = Math.PI / 5;
    backLight.penumbra = 0.7;
    backLight.decay = 1.5;
    backLight.castShadow = false;
    scene.add(backLight);
    scene.add(backLight.target);

    const lights = { ambient, spotLeft, spotRight, backLight };

    // Resize handler
    function onResize() {
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', onResize);

    return { scene, camera, renderer, controls, lights };
}
