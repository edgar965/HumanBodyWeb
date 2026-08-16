import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Buehne — Renderer, Szene, Kamera, Licht und Gitter der Viewer-Seite.
 *
 * Aus viewer/index.js herausgeloest (Umbau 16.08.2026). Die Datei hatte 358
 * Zeilen, davon 230 in einer einzigen `init()`-Funktion: Buehne aufbauen,
 * Knoepfe verdrahten, Seitenbefehle abarbeiten und ein Dutzend Module starten —
 * alles hintereinander in einem Rutsch.
 *
 * Die Werte hier sind aufeinander abgestimmt und stehen deshalb als benannte
 * Konstanten: Belichtung 1.6 mit ACES-Tonwertbildung, drei gerichtete Lichter
 * plus Umgebungslicht. Wer eines aendert, sieht am Namen, was es tut.
 */
export class Buehne {

    static HINTERGRUND = 0x1a1a2e;
    static BILDWINKEL = 35;
    static NAH = 0.01;
    static FERN = 100;
    static BELICHTUNG = 1.6;
    static KAMERA_START = [0, 1.0, 3.5];
    static BLICKZIEL = [0, 0.9, 0];
    static ABSTAND_MIN = 0.5;
    static ABSTAND_MAX = 15;

    /** Die drei gerichteten Lichter: Name, Farbe, Stärke, Position. */
    static LICHTER = [
        ['keyLight', 0xffffff, 3.0, [2, 4, -5]],
        ['fillLight', 0xeeeeff, 2.0, [-3, 3, -4]],
        ['backLight', 0xffeedd, 2.5, [0, 4, 5]],
    ];
    static UMGEBUNG = [0xffffff, 0.8];
    static GITTER = [4, 20, 0x333355, 0x222244];

    /**
     * @param {Object} state  der gemeinsame Zustand der Viewer-Seite; die
     *        Bühne schreibt ihre Bestandteile dort hinein, weil alle anderen
     *        Module sie von dort lesen.
     */
    constructor(state) {
        this.state = state;
    }

    /** Alles aufbauen. Gibt den Zustand zurück. */
    aufbauen(leinwandId = 'viewer-canvas') {
        const leinwand = document.getElementById(leinwandId);
        const [breite, hoehe] = this._masse(leinwand);
        this._renderer(leinwand, breite, hoehe);
        this._szene();
        this._kamera(breite, hoehe);
        this._steuerung(leinwand);
        this._licht();
        this.state.scene.add(new THREE.GridHelper(...Buehne.GITTER));
        window.addEventListener('resize', () => this.groesseAnpassen());
        return this.state;
    }

    _masse(leinwand) {
        const behaelter = leinwand.parentElement;
        return [behaelter.clientWidth,
                behaelter.clientHeight || window.innerHeight];
    }

    _renderer(leinwand, breite, hoehe) {
        const renderer = new THREE.WebGLRenderer({ canvas: leinwand, antialias: true });
        // Auf Bildschirmen mit hoher Punktdichte deckelt der Faktor 2 die
        // Pixelzahl — sonst rendert die Seite auf einem 3-fach-Schirm neunmal
        // so viele Punkte.
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(breite, hoehe);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = Buehne.BELICHTUNG;
        this.state.renderer = renderer;
    }

    _szene() {
        this.state.scene = new THREE.Scene();
        this.state.scene.background = new THREE.Color(Buehne.HINTERGRUND);
    }

    _kamera(breite, hoehe) {
        const kamera = new THREE.PerspectiveCamera(
            Buehne.BILDWINKEL, breite / hoehe, Buehne.NAH, Buehne.FERN);
        kamera.position.set(...Buehne.KAMERA_START);
        this.state.camera = kamera;
    }

    _steuerung(leinwand) {
        const steuerung = new OrbitControls(this.state.camera, leinwand);
        steuerung.target.set(...Buehne.BLICKZIEL);
        steuerung.enableDamping = true;
        steuerung.dampingFactor = 0.08;
        steuerung.minDistance = Buehne.ABSTAND_MIN;
        steuerung.maxDistance = Buehne.ABSTAND_MAX;
        steuerung.update();
        this.state.controls = steuerung;
    }

    _licht() {
        for (const [name, farbe, staerke, ort] of Buehne.LICHTER) {
            const licht = new THREE.DirectionalLight(farbe, staerke);
            licht.position.set(...ort);
            this.state.scene.add(licht);
            this.state[name] = licht;
        }
        this.state.ambient = new THREE.AmbientLight(...Buehne.UMGEBUNG);
        this.state.scene.add(this.state.ambient);
    }

    /** Nach Fenstergrößenänderung: Renderer und Kamera nachziehen. */
    groesseAnpassen() {
        const behaelter = this.state.renderer.domElement.parentElement;
        const breite = Math.max(behaelter.clientWidth, 100);
        const hoehe = behaelter.clientHeight || window.innerHeight;
        this.state.renderer.setSize(breite, hoehe);
        this.state.camera.aspect = breite / hoehe;
        this.state.camera.updateProjectionMatrix();
    }

    /** Licht und Kamera auf die Ausgangswerte — für „Beleuchtung zurücksetzen". */
    lichtZuruecksetzen() {
        for (const [name, farbe, staerke, ort] of Buehne.LICHTER) {
            const licht = this.state[name];
            if (!licht) continue;
            licht.color.setHex(farbe);
            licht.intensity = staerke;
            licht.position.set(...ort);
        }
        if (this.state.ambient) {
            const [farbe, staerke] = Buehne.UMGEBUNG;
            this.state.ambient.color.setHex(farbe);
            this.state.ambient.intensity = staerke;
        }
    }

    kameraZuruecksetzen() {
        this.state.camera.fov = Buehne.BILDWINKEL;
        this.state.camera.updateProjectionMatrix();
        this.state.camera.position.set(...Buehne.KAMERA_START);
        this.state.controls.target.set(...Buehne.BLICKZIEL);
        this.state.controls.update();
    }
}
