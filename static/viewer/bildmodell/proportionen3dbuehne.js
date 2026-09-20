import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { base64ToFloat32, base64ToUint32 } from '../gemeinsam/kodierung.js';

/**
 * Proportionen3dbuehne — das Zielnetz als Genesis-9-Käfig im 3D-Popup.
 *
 * Eine kleine Bühne wie `Ansicht3d` (Kamera auf Figurhöhe, Orbit, Lichter an
 * der Kamera), aber OHNE `Genesis9Modell`: das Netz kommt fertig vom Server
 * (`zielnetz3d/` — Dreiecke einmal, danach nur noch die Punkte je Zug) und
 * wird an Ort und Stelle ausgetauscht (`punkteSetzen`: Positionsattribut
 * überschreiben, Normalen neu — 25.182 Punkte in Millisekunden). Matte Haut
 * mit Licht von der Kamera, dazu ein Gitter zum Zuschalten: Donauwellen
 * sieht man an den Kanten schneller als an der Schattierung. Ungepaarte
 * Punkte (Gewicht 0) bekommen Grau — was dort steht, ist Modell, nicht Ziel.
 * Gezeichnet wird nur, solange das Popup offen ist (`starten`/`anhalten`).
 */
export class Proportionen3dbuehne {

    static HAUT = 0xd9b39c;
    static UNGEPAART = 0x8a8f99;

    constructor(canvas) {
        this.canvas = canvas;
        this.netz = null;
        this.gitter = null;
        this._laeuft = false;
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
        if (typeof ResizeObserver !== 'undefined') new ResizeObserver(() => this.groesse()).observe(canvas);
    }

    groesse() {
        const b = this.canvas.clientWidth || 400, h = this.canvas.clientHeight || 500;
        if (this.renderer.domElement.width === Math.round(b * this.renderer.getPixelRatio())
            && this.renderer.domElement.height === Math.round(h * this.renderer.getPixelRatio())) return;
        this.renderer.setSize(b, h, false);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
    }

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

    /** Erste Antwort mit Dreiecken: Netz bauen; Kamera auf die Figurhöhe. */
    netzSetzen(antwort) {
        const punkte = base64ToFloat32(antwort.punkte);
        const dreiecke = base64ToUint32(antwort.dreiecke);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        geo.setIndex(new THREE.BufferAttribute(dreiecke, 1));
        geo.setAttribute('color', new THREE.BufferAttribute(this._farben(antwort.gewicht, punkte.length / 3), 3));
        geo.computeVertexNormals();
        if (this.netz) { this.szene.remove(this.netz); this.netz.geometry.dispose(); }
        if (this.gitter) { this.szene.remove(this.gitter); }
        this.netz = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            vertexColors: true, roughness: 0.85, metalness: 0.0, side: THREE.DoubleSide,
        }));
        this.szene.add(this.netz);
        this.gitter = new THREE.LineSegments(new THREE.WireframeGeometry(geo),
            new THREE.LineBasicMaterial({ color: 0x223344, transparent: true, opacity: 0.35 }));
        this.gitter.visible = this._gitterAn || false;
        this.szene.add(this.gitter);
        const hoehe = (antwort.hoehe_cm || 170) / 100;
        this.steuerung.target.set(0, hoehe * 0.52, 0);
        this.kamera.position.set(0, hoehe * 0.55, hoehe * 2.4);
    }

    /** Jede weitere Antwort: nur die Punkte tauschen, Normalen und Gitter neu. */
    punkteSetzen(antwort) {
        if (!this.netz) return;
        const punkte = base64ToFloat32(antwort.punkte);
        const lage = this.netz.geometry.attributes.position;
        if (punkte.length !== lage.array.length) return;
        lage.array.set(punkte);
        lage.needsUpdate = true;
        this.netz.geometry.computeVertexNormals();
        this.netz.geometry.computeBoundingSphere();
        this._gitterAlt = true;
        if (this.gitter && this.gitter.visible) this._gitterNeu();
    }

    /** Das Gitter folgt den Punkten — neu gebaut nur, wenn es sichtbar ist (50.000 Dreiecke). */
    _gitterNeu() {
        if (!this.gitter || !this.netz) return;
        this.gitter.geometry.dispose();
        this.gitter.geometry = new THREE.WireframeGeometry(this.netz.geometry);
        this._gitterAlt = false;
    }

    gitterZeigen(an) {
        this._gitterAn = !!an;
        if (!this.gitter) return;
        this.gitter.visible = this._gitterAn;
        if (this._gitterAn && this._gitterAlt) this._gitterNeu();
    }

    _farben(gewichtB64, anzahl) {
        const farben = new Float32Array(anzahl * 3);
        const haut = new THREE.Color(Proportionen3dbuehne.HAUT), grau = new THREE.Color(Proportionen3dbuehne.UNGEPAART);
        const gewicht = gewichtB64 ? base64ToFloat32(gewichtB64) : null;
        for (let i = 0; i < anzahl; i++) {
            const f = gewicht && !(gewicht[i] > 0) ? grau : haut;
            farben[i * 3] = f.r; farben[i * 3 + 1] = f.g; farben[i * 3 + 2] = f.b;
        }
        return farben;
    }

    dispose() {
        this.anhalten();
        if (this.netz) { this.szene.remove(this.netz); this.netz.geometry.dispose(); this.netz = null; }
        if (this.gitter) { this.szene.remove(this.gitter); this.gitter.geometry.dispose(); this.gitter = null; }
    }
}
