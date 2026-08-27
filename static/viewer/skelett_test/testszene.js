import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { Testzustand } from './testzustand.js';

/**
 * Die Szene der Vergleichsseite: zwei Zeichner, Kamera, Licht, Gitter und je
 * eine Gruppe pro Skelett.
 *
 * `Testszene` und nicht `Szenenaufbau` — der Name ist in
 * `static/viewer/scene/szenenaufbau.js` schon für die Modellseite vergeben, und
 * zwei Klassen desselben Namens meldet `namens-dubletten`.
 *
 * Aus aufbau.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `init()` hatte 103 Zeilen).
 */
export class Testszene {
    /**
     * Baut alles auf und legt es in `Testzustand` ab.
     * @param {HTMLCanvasElement} canvas
     */
    static aufbauen(canvas) {
        const behaelter = canvas.parentElement;
        const breite = behaelter.clientWidth;
        const hoehe = behaelter.clientHeight || window.innerHeight;

        Testszene._zeichner(canvas, breite, hoehe);
        Testszene._szene();
        Testszene._kamera(canvas, breite, hoehe);
        Testszene._licht();
        Testszene._skelettgruppen();
    }

    static _zeichner(canvas, breite, hoehe) {
        Testzustand.renderer = new THREE.WebGLRenderer({ canvas,
                                                         antialias: true });
        Testzustand.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        Testzustand.renderer.setSize(breite, hoehe);
        Testzustand.renderer.outputColorSpace = THREE.SRGBColorSpace;

        // Zweiter Zeichner nur für die Knochenbeschriftungen (CSS2D).
        Testzustand.labelRenderer = new CSS2DRenderer();
        Testzustand.labelRenderer.setSize(breite, hoehe);
        const stil = Testzustand.labelRenderer.domElement.style;
        stil.position = 'absolute';
        stil.top = '0';
        stil.left = '0';
        stil.pointerEvents = 'none';
        document.getElementById('label-renderer')
                .appendChild(Testzustand.labelRenderer.domElement);
    }

    static _szene() {
        Testzustand.scene = new THREE.Scene();
        Testzustand.scene.background = new THREE.Color(0x1a1a2e);
    }

    static _kamera(canvas, breite, hoehe) {
        // Weiter hinten als sonst — es stehen bis zu sieben Skelette
        // nebeneinander.
        Testzustand.camera = new THREE.PerspectiveCamera(35, breite / hoehe,
                                                         0.01, 100);
        Testzustand.camera.position.set(0, 1.2, 7.5);

        Testzustand.controls = new OrbitControls(Testzustand.camera, canvas);
        Testzustand.controls.target.set(0, 0.9, 0);
        Testzustand.controls.enableDamping = true;
        Testzustand.controls.dampingFactor = 0.08;
        Testzustand.controls.minDistance = 0.5;
        Testzustand.controls.maxDistance = 20;
        Testzustand.controls.update();
    }

    static _licht() {
        Testzustand.scene.add(new THREE.AmbientLight(0xffffff, 2.0));
        const richtlicht = new THREE.DirectionalLight(0xffffff, 1.5);
        richtlicht.position.set(2, 4, 3);
        Testzustand.scene.add(richtlicht);
        Testzustand.scene.add(new THREE.GridHelper(10, 50, 0x333355, 0x222244));
    }

    static _skelettgruppen() {
        for (const skelett of Object.values(Testzustand.skeletons)) {
            skelett.group = new THREE.Group();
            skelett.group.position.x = skelett.xOffset;
            if (skelett.zOffset) skelett.group.position.z = skelett.zOffset;
            Testzustand.scene.add(skelett.group);
        }
    }
}
