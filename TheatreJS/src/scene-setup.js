import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';

/**
 * Create a small light icon (cone pointing in direction)
 * @param {THREE.Color} color Light color
 * @returns {THREE.Group}
 */
function createLightIcon(color) {
    const group = new THREE.Group();

    // VIEL GRÖßERER Kegel als Licht-Symbol (zeigt Richtung)
    const coneGeo = new THREE.ConeGeometry(0.4, 1.0, 16);
    const coneMat = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 1.0,
        side: THREE.DoubleSide,
        depthTest: false, // Immer sichtbar, auch hinter anderen Objekten!
        depthWrite: false
    });
    const cone = new THREE.Mesh(coneGeo, coneMat);
    cone.rotation.x = Math.PI; // Spitze zeigt nach unten
    cone.renderOrder = 999; // Render nach allem anderen

    // GRÖßERE leuchtende Kugel als Basis (sehr hell!)
    const sphereGeo = new THREE.SphereGeometry(0.35, 32, 32);
    const sphereMat = new THREE.MeshBasicMaterial({
        color: new THREE.Color(1, 1, 1), // WEISS statt Lichtfarbe!
        emissive: color,
        emissiveIntensity: 2.0, // SEHR HELL
        transparent: true,
        opacity: 1.0,
        depthTest: false, // Immer sichtbar!
        depthWrite: false
    });
    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
    sphere.position.y = 0.5;
    sphere.renderOrder = 999;

    group.add(cone);
    group.add(sphere);
    return group;
}

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
    renderer.toneMappingExposure = 1.6; // Match result_character.js exposure
    renderer.outputColorSpace = THREE.SRGBColorSpace; // CRITICAL for PBR materials!

    // Scene — lighter theatre backdrop for better visibility
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x151520); // Lighter background
    scene.fog = new THREE.FogExp2(0x151520, 0.03); // Less dense fog

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

    // ── Stage floor — lighter wood for visibility ──
    const stageGeo = new THREE.PlaneGeometry(14, 10);
    const stageMat = new THREE.MeshStandardMaterial({
        color: 0x4a3a2e, // Lighter brown
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
        color: 0x3a2a1a, // Lighter edge
        roughness: 0.6,
    });
    const stageEdge = new THREE.Mesh(edgeGeo, edgeMat);
    stageEdge.position.y = -0.04;
    stageEdge.receiveShadow = true;
    scene.add(stageEdge);

    // ── Lighting — theatrical 3-point + spotlights ──

    // BRIGHTER ambient for better base visibility
    const ambient = new THREE.AmbientLight(0x2a2a3e, 0.5); // Much brighter!
    scene.add(ambient);

    // Spot 1 — warm key from front-left above
    const spotLeft = new THREE.SpotLight(0xffeedd, 60); // VERY BRIGHT for PBR!
    spotLeft.position.set(-3, 3, 3); // Niedriger positioniert für bessere Sichtbarkeit
    spotLeft.target.position.set(0, 0, 0);
    spotLeft.angle = Math.PI / 6;
    spotLeft.penumbra = 0.5;
    spotLeft.decay = 1.5;
    spotLeft.castShadow = true;
    spotLeft.shadow.mapSize.set(4096, 4096); // Higher resolution to reduce shadow acne
    spotLeft.shadow.camera.near = 1;
    spotLeft.shadow.camera.far = 15;
    spotLeft.shadow.bias = -0.0001; // Reduce shadow acne
    scene.add(spotLeft);
    scene.add(spotLeft.target);

    // Kleines Licht-Icon (anklickbar, zeigt Richtung)
    const spotLeftIcon = createLightIcon(new THREE.Color(0xffeedd));
    spotLeftIcon.position.copy(spotLeft.position);
    spotLeftIcon.lookAt(spotLeft.target.position);
    spotLeftIcon.userData.light = spotLeft; // Referenz zum Licht
    scene.add(spotLeftIcon);

    // Spot 2 — warm key from front-right above
    const spotRight = new THREE.SpotLight(0xffeedd, 60); // VERY BRIGHT for PBR!
    spotRight.position.set(3, 3, 3); // Niedriger positioniert
    spotRight.target.position.set(0, 0, 0);
    spotRight.angle = Math.PI / 6;
    spotRight.penumbra = 0.5;
    spotRight.decay = 1.5;
    spotRight.castShadow = true;
    spotRight.shadow.mapSize.set(4096, 4096); // Higher resolution to reduce shadow acne
    spotRight.shadow.camera.near = 1;
    spotRight.shadow.camera.far = 15;
    spotRight.shadow.bias = -0.0001; // Reduce shadow acne
    scene.add(spotRight);
    scene.add(spotRight.target);

    // Kleines Licht-Icon für rechtes Licht
    const spotRightIcon = createLightIcon(new THREE.Color(0xffeedd));
    spotRightIcon.position.copy(spotRight.position);
    spotRightIcon.lookAt(spotRight.target.position);
    spotRightIcon.userData.light = spotRight;
    scene.add(spotRightIcon);

    // Spot 3 — blue-violet backlight (rim light from behind)
    const backLight = new THREE.SpotLight(0x6644aa, 25); // BRIGHTER for rim light visibility
    backLight.position.set(0, 2.5, -4); // Niedriger positioniert
    backLight.target.position.set(0, 0.5, 0);
    backLight.angle = Math.PI / 5;
    backLight.penumbra = 0.7;
    backLight.decay = 1.5;
    backLight.castShadow = false;
    scene.add(backLight);
    scene.add(backLight.target);

    // Kleines Licht-Icon für Backlicht
    const backLightIcon = createLightIcon(new THREE.Color(0x6644aa));
    backLightIcon.position.copy(backLight.position);
    backLightIcon.lookAt(backLight.target.position);
    backLightIcon.userData.light = backLight;
    scene.add(backLightIcon);

    const lights = { ambient, spotLeft, spotRight, backLight };
    const lightIcons = { spotLeftIcon, spotRightIcon, backLightIcon };

    // TransformControls für Licht-Icons (zum Bewegen/Drehen)
    const transformControls = new TransformControls(camera, canvas);
    transformControls.setMode('translate'); // Start mit Position-Modus
    transformControls.setSize(0.8); // Kleiner für bessere Sicht
    scene.add(transformControls);

    // Wenn TransformControls aktiv, OrbitControls deaktivieren
    transformControls.addEventListener('dragging-changed', (event) => {
        controls.enabled = !event.value;
    });

    // Resize handler
    function onResize() {
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', onResize);

    return { scene, camera, renderer, controls, lights, lightIcons, transformControls };
}
