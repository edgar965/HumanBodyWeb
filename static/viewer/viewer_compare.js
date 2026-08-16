/**
 * Vergleichsansicht — zwei Charaktere nebeneinander, jeder mit eigener Szene,
 * eigener Verbindung und eigenen Reglern.
 *
 * WARUM eine Klasse (Umbau 16.08.2026): Die Datei war eine Fabrikfunktion
 * `createViewer` mit 653 Zeilen. Neunundzwanzig Variablen und sechzehn
 * Funktionen lagen in ihrer Closure — aufteilen liess sich davon nichts, weil
 * jede Funktion an Variablen hing, die nur dort sichtbar waren. Als Klasse mit
 * Feldern verteilt sich das auf fuenf Module:
 *
 *   vergleich/vergleichsfelder.js  die elf Bedienelemente als Datensatz
 *   vergleich/vergleichspanel.js   Bedienspalte aufbauen
 *   vergleich/vergleichsregler.js  Morph- und Grundregler fuellen
 *   vergleich/vergleichsnetz.js    Koerpernetz laden und einfaerben
 *   vergleich/vergleichsfunk.js    WebSocket
 *
 * Nebenbei fielen 55 doppelte Zeilen weg: `loadMesh` und `reloadMesh` waren
 * bis auf drei Stellen buchstabengleich.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Vergleichsfelder } from './vergleich/vergleichsfelder.js';
import { Vergleichspanel } from './vergleich/vergleichspanel.js';
import { Vergleichsregler } from './vergleich/vergleichsregler.js';
import { Vergleichsnetz } from './vergleich/vergleichsnetz.js';
import { Vergleichsfunk } from './vergleich/vergleichsfunk.js';

export class Vergleichsansicht {
    /**
     * @param {Object} config
     * @param {string} config.canvasId         Kennung der Leinwand
     * @param {string} config.panelId          Kennung der Bedienspalte
     * @param {string} config.apiPrefix        z.B. '/api/character-test'
     * @param {string} config.wsPath           z.B. '/ws/character-test/'
     * @param {string} config.defaultBodyType  z.B. 'Male_Caucasian'
     * @param {string} config.label            Anzeigename
     */
    constructor(config) {
        Object.assign(this, config);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.bodyMesh = null;
        this.bodyGeometry = null;
        this.vertexCount = 0;
        this.clock = new THREE.Clock();
        this.frameCount = 0;
        this.fpsAccum = 0;
        this.morphData = null;
        this.skinColorMap = {};
        this.felder = new Vergleichsfelder();
        this.funk = new Vergleichsfunk(this);
    }

    init() {
        Vergleichspanel.bauen(this);
        this._szeneBauen();
        window.addEventListener('resize', () => this.groesseAnpassen());
        Vergleichsregler.laden(this);
        Vergleichsnetz.laden(this).then(() => this._schleife());
        this.funk.verbinden();
    }

    _szeneBauen() {
        const leinwand = document.getElementById(this.canvasId);
        const behaelter = leinwand.parentElement;
        const w = behaelter.clientWidth;
        const h = behaelter.clientHeight || window.innerHeight;

        this.renderer = new THREE.WebGLRenderer({ canvas: leinwand, antialias: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.setSize(w, h);
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.6;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);
        this.camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
        this.camera.position.set(0, 1.0, 3.5);

        this.controls = new OrbitControls(this.camera, leinwand);
        this.controls.target.set(0, 0.9, 0);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08;
        this.controls.minDistance = 0.5;
        this.controls.maxDistance = 15;
        this.controls.update();

        this._licht();
        this.scene.add(new THREE.GridHelper(4, 20, 0x333355, 0x222244));
    }

    /** Dreipunktlicht plus Grundhelligkeit. */
    _licht() {
        const setzen = (farbe, staerke, x, y, z) => {
            const l = new THREE.DirectionalLight(farbe, staerke);
            l.position.set(x, y, z);
            this.scene.add(l);
        };
        setzen(0xffffff, 3.0, 2, 4, -5);      // Fuehrungslicht
        setzen(0xeeeeff, 2.0, -3, 3, -4);     // Aufhellung
        setzen(0xffeedd, 2.5, 0, 4, 5);       // Gegenlicht
        this.scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    }

    _schleife() {
        const bild = () => {
            requestAnimationFrame(bild);
            const dt = this.clock.getDelta();
            this.controls.update();
            this.renderer.render(this.scene, this.camera);
            this.frameCount++;
            this.fpsAccum += dt;
            if (this.fpsAccum >= 1.0) {
                this.felder.zahl('bildrate', this.frameCount);
                this.frameCount = 0;
                this.fpsAccum = 0;
            }
        };
        bild();
    }

    groesseAnpassen() {
        const behaelter = this.renderer.domElement.parentElement;
        const w = Math.max(behaelter.clientWidth, 100);
        const h = behaelter.clientHeight || window.innerHeight;
        this.renderer.setSize(w, h);
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
    }
}

/** Beibehaltener Einstieg fuer die Vergleichsseite. */
export function createViewer(config) {
    return new Vergleichsansicht(config);
}
