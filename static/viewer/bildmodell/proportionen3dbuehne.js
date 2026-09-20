import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Zielkaefig } from './zielkaefig.js';

/**
 * Proportionen3dbuehne — das Zielnetz als Genesis-9-Käfig im 3D-Popup.
 *
 * Eine kleine Bühne wie `Ansicht3d` (Kamera auf Figurhöhe, Orbit, Lichter an
 * der Kamera), aber OHNE `Genesis9Modell`: das Netz kommt fertig vom Server
 * (`zielnetz3d/` über `Zielnetzlive`) und liegt als `Zielkaefig` in der
 * Szene — Dreiecke einmal, danach nur noch die Punkte je Zug. Gezeichnet
 * wird nur, solange das Popup offen ist (`starten`/`anhalten`).
 */
export class Proportionen3dbuehne {

    constructor(canvas) {
        this.canvas = canvas;
        this._laeuft = false;
        this.foto = null;     // Kamera des Fotos (`fotokamera`) oder null = freie Kamera
        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(30, 1, 0.05, 50);
        this.kamera.position.set(0, 1.0, 4.2);
        this.steuerung = new OrbitControls(this.kamera, canvas);
        this.steuerung.target.set(0, 0.9, 0);
        this.steuerung.enableDamping = true;
        this.szene.add(new THREE.HemisphereLight(0xffffff, 0xc8c2ba, 1.1));
        const haupt = new THREE.DirectionalLight(0xffffff, 1.1);
        haupt.position.set(1, 1.5, 2);
        const fuell = new THREE.DirectionalLight(0xffffff, 0.3);
        fuell.position.set(-2, -0.5, 1.5);
        this.kamera.add(haupt, fuell);
        this.szene.add(this.kamera);
        this.szene.add(new THREE.GridHelper(2, 10, 0x445566, 0x2a3340));
        this.kaefig = new Zielkaefig(this.szene);
        if (typeof ResizeObserver !== 'undefined') new ResizeObserver(() => this.groesse()).observe(canvas);
    }

    get netz() { return this.kaefig.netz; }

    groesse() {
        const b = this.canvas.clientWidth || 400, h = this.canvas.clientHeight || 500;
        if (this.renderer.domElement.width === Math.round(b * this.renderer.getPixelRatio())
            && this.renderer.domElement.height === Math.round(h * this.renderer.getPixelRatio())) return;
        this.renderer.setSize(b, h, false);
        // Mit Fotokamera bleibt das Seitenverhältnis das des Fotos (die Leinwand ist danach geschnitten).
        this.kamera.aspect = this.foto ? this.foto.breite / this.foto.hoehe : b / h;
        this.kamera.updateProjectionMatrix();
    }

    /** Die Kamera des Fotos (GVHMR `K_fullimg`: fx, fy, cx, cy in Fotopixeln, breite, hoehe) —
     *  Kamera im Ursprung, Blick nach −z, Öffnungswinkel aus fy, Hauptpunkt über `setViewOffset`;
     *  das Netz in Kamerasicht (`kamera.punkte` von `gvhmr3d/`) erscheint dann genau im Ausschnitt
     *  des Fotos (Edgar, 20.09.2026: „Immer das 3D Modell in genau der gleichen pose und ausschnitt
     *  wie das 2D Bild!!!"). Orbit dreht um den Punkt der Blickachse in der Tiefe des Netzes;
     *  `fotoansicht()` stellt die Sicht wieder her. `null` = zurück zur freien Kamera. */
    fotokamera(k, tiefe = 2.0) {
        this.foto = k || null;
        if (!k) {
            this.kamera.clearViewOffset();
            this.kamera.fov = 30;
            this.groesse();
            return;
        }
        this.kamera.fov = 2 * Math.atan(k.hoehe / (2 * k.fy)) * 180 / Math.PI;
        this.kamera.aspect = k.breite / k.hoehe;
        this.kamera.setViewOffset(k.breite, k.hoehe, k.breite / 2 - k.cx, k.hoehe / 2 - k.cy, k.breite, k.hoehe);
        this.kamera.updateProjectionMatrix();
        this.kamera.position.set(0, 0, 0);
        this.steuerung.target.set(0, 0, -Math.max(0.2, tiefe));
        this.steuerung.update();
        this.steuerung.saveState();
    }

    /** Zurück zur Sicht des Fotos (nach dem Drehen). */
    fotoansicht() { if (this.foto) this.steuerung.reset(); }

    starten() {
        if (this._laeuft) return;
        this._laeuft = true;
        const lauf = () => {
            if (!this._laeuft) return;
            this.steuerung.update();
            this.renderer.render(this.szene, this.kamera);
            requestAnimationFrame(lauf);
        };
        this.groesse();
        requestAnimationFrame(lauf);
    }

    anhalten() { this._laeuft = false; }

    /** Eine Antwort von `Zielnetzlive`: erste mit Netz bauen (Kamera auf die Figurhöhe), sonst Punkte tauschen. */
    setzen(antwort, netz) {
        const neu = !this.kaefig.da;
        this.kaefig.setzen(antwort, netz);
        if (neu && this.kaefig.da) {
            const hoehe = this.kaefig.hoehe || 1.7;
            this.steuerung.target.set(0, hoehe * 0.52, 0);
            this.kamera.position.set(0, hoehe * 0.55, hoehe * 2.4);
        }
    }

    netzSetzen(antwort) { this.setzen(antwort, null); }

    punkteSetzen(antwort) { this.kaefig.punkteSetzen(antwort); }

    gitterZeigen(an) { this.kaefig.gitterZeigen(an); }

    dispose() {
        this.anhalten();
        this.kaefig.dispose();
    }
}
