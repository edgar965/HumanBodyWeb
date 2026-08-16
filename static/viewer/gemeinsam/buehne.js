import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Buehne — Renderer, Szene, Kamera, Licht und Gitter, wie alle Figurenseiten
 * sie brauchen.
 *
 * Umbau 16.08.2026: Dieser Aufbau stand DREIMAL im Projekt, Zeile für Zeile
 * gleich — in `character_core.createSceneSetup()`, in `scene/boot.js init()` und
 * in `animations.js init()`. Alle drei mit denselben Zahlen: Belichtung 1.6,
 * Blickwinkel 35°, Kamera auf (0, 1, 3.5), Ziel (0, 0.9, 0), dieselben drei
 * gerichteten Lichter, dasselbe Gitter. Wer die Beleuchtung ändern wollte,
 * musste es an drei Stellen tun — oder merkte nicht, dass es drei gibt.
 *
 * Zwei echte Unterschiede sind Wahlmöglichkeiten geworden:
 *  * woher die Maße kommen (Leinwand selbst oder ihr Rahmen),
 *  * ob `setSize` auch die CSS-Größe der Leinwand setzt.
 */
export class Buehne {

    static HINTERGRUND = 0x1a1a2e;
    static BELICHTUNG = 1.6;
    /** Bildpunkte je Anzeigepunkt — über 2 bringt kaum noch etwas. */
    static MAX_PIXELVERHAELTNIS = 2;

    /** Kamera. */
    static SICHTFELD = 35;
    static NAH = 0.01;
    static FERN = 100;
    static KAMERAPLATZ = [0, 1.0, 3.5];
    static KAMERAZIEL = [0, 0.9, 0];
    static ABSTAND_MIN = 0.5;
    static ABSTAND_MAX = 15;
    static DAEMPFUNG = 0.08;

    /** Licht: Name im Ergebnis, Farbe, Stärke, Platz. */
    static LICHTER = [
        ['keyLight', 0xffffff, 3.0, [2, 4, -5]],
        ['fillLight', 0xeeeeff, 2.0, [-3, 3, -4]],
        ['backLight', 0xffeedd, 2.5, [0, 4, 5]],
    ];
    static UMGEBUNGSLICHT = [0xffffff, 0.8];

    /** Gitter: Größe, Teilungen, Hauptfarbe, Nebenfarbe. */
    static GITTER = [4, 20, 0x333355, 0x222244];

    /**
     * @param leinwand   die <canvas>
     * @param wahl.masse 'leinwand' (Vorgabe) oder 'rahmen' — woher Breite und
     *                   Höhe kommen
     * @param wahl.stil  true: `setSize` setzt auch die CSS-Größe
     * @returns { renderer, scene, camera, controls, keyLight, fillLight,
     *            backLight, ambient, grid }
     */
    static bauen(leinwand, wahl = {}) {
        const { masse = 'leinwand', stil = false } = wahl;
        const [breite, hoehe] = Buehne.masse(leinwand, masse);

        const renderer = new THREE.WebGLRenderer({ canvas: leinwand,
                                                   antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio,
                                        Buehne.MAX_PIXELVERHAELTNIS));
        renderer.setSize(breite, hoehe, stil);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = Buehne.BELICHTUNG;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(Buehne.HINTERGRUND);

        const camera = new THREE.PerspectiveCamera(Buehne.SICHTFELD,
                                                   breite / hoehe,
                                                   Buehne.NAH, Buehne.FERN);
        camera.position.set(...Buehne.KAMERAPLATZ);

        const teile = { renderer, scene, camera,
                        controls: Buehne._steuerung(camera, leinwand) };
        Object.assign(teile, Buehne._licht(scene));
        teile.grid = new THREE.GridHelper(...Buehne.GITTER);
        scene.add(teile.grid);
        return teile;
    }

    /** Maße der Bühne — 0 wäre eine kaputte Kamera, deshalb Ersatzwerte. */
    static masse(leinwand, quelle) {
        if (quelle === 'rahmen') {
            const rahmen = leinwand.parentElement;
            return [rahmen.clientWidth,
                    rahmen.clientHeight || window.innerHeight];
        }
        return [leinwand.clientWidth || leinwand.width,
                leinwand.clientHeight || leinwand.height];
    }

    static _steuerung(camera, leinwand) {
        const steuerung = new OrbitControls(camera, leinwand);
        steuerung.target.set(...Buehne.KAMERAZIEL);
        steuerung.enableDamping = true;
        steuerung.dampingFactor = Buehne.DAEMPFUNG;
        steuerung.minDistance = Buehne.ABSTAND_MIN;
        steuerung.maxDistance = Buehne.ABSTAND_MAX;
        steuerung.update();
        return steuerung;
    }

    static _licht(scene) {
        const lichter = {};
        for (const [name, farbe, staerke, platz] of Buehne.LICHTER) {
            const licht = new THREE.DirectionalLight(farbe, staerke);
            licht.position.set(...platz);
            scene.add(licht);
            lichter[name] = licht;
        }
        lichter.ambient = new THREE.AmbientLight(...Buehne.UMGEBUNGSLICHT);
        scene.add(lichter.ambient);
        return lichter;
    }
}
