import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { Buehnenboden } from './buehnenboden.js';
import { Buehnenlicht } from './buehnenlicht.js';

/**
 * Aufbau der Theaterbühne: Renderer, Szene, Kamera, Steuerung.
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `createScene()` hatte 130 Zeilen.
 * Boden und Beleuchtung stehen jetzt in `Buehnenboden` bzw. `Buehnenlicht` —
 * dort war der Aufbau dreimal fast wortgleich wiederholt.
 *
 * @param {HTMLCanvasElement} canvas
 * @returns {{scene, camera, renderer, controls, lights, lightIcons,
 *            transformControls}}
 */
export function createScene(canvas) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.shadowMap.enabled = false;              // keine Schatten
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;              // wie result_character.js
    renderer.outputColorSpace = THREE.SRGBColorSpace;  // Pflicht fuer PBR

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x151520);
    scene.fog = new THREE.FogExp2(0x151520, 0.03);

    const camera = new THREE.PerspectiveCamera(
        50, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(0, 1.6, 5);

    const controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.update();

    Buehnenboden.aufbauen(scene);
    const { lights, lightIcons } = Buehnenlicht.aufbauen(scene);

    const transformControls = new TransformControls(camera, canvas);
    transformControls.setMode('translate');
    transformControls.setSize(0.8);
    // getHelper() und nicht die Steuerung selbst (Fehlerbehebung 16.08.2026):
    // Seit three.js r169 erbt TransformControls von Controls und ist KEIN
    // Object3D mehr. `scene.add(transformControls)` meldete deshalb bei jedem
    // Seitenaufruf zweimal
    //     THREE.Object3D.add: object not an instance of THREE.Object3D
    // in der Browserkonsole — und der Anfasser zum Verschieben von Lichtern und
    // Figuren war unsichtbar, weil sein Hilfsobjekt nie in die Szene kam.
    scene.add(transformControls.getHelper());
    // Solange am Anfasser gezogen wird, darf die Umlaufsteuerung nicht mitdrehen.
    transformControls.addEventListener('dragging-changed', (event) => {
        controls.enabled = !event.value;
    });

    window.addEventListener('resize', () => {
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    });

    return { scene, camera, renderer, controls, lights, lightIcons,
             transformControls };
}
