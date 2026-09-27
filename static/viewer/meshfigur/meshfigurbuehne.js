import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Texturauflage } from '../bildmodell/texturauflage.js';

/**
 * Meshfigurbuehne — die angepasste Genesis-Figur und das hochgeladene Netz auf einer Bühne.
 *
 * Die Figur ist dieselbe Klasse wie in Szene und Studio (`Genesis9Modell`: Käfig sofort, feine
 * Stufe nach) mit den gestellten Reglern samt Eigenmorph; die gebackenen Kacheln legt
 * `Texturauflage` auf (wie im Reiter „3D"). Das Netz kommt aus dem Eingang des Auftrags und wird
 * mit der Matrix der Erkennung in dieselbe Lage gebracht (Y oben, Blick +Z, Füße auf 0, ggf. auf
 * die Körpergröße gestreckt) — „Nebeneinander" rückt es um `ABSTAND` nach rechts.
 */
export class Meshfigurbuehne {

    static ABSTAND = 0.75;

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('buehne');
        this.hinweis = document.getElementById('buehne-hinweis');
        this.was = 'figur';
        this.modell = null;
        this.netz = null;
        this.auflage = new Texturauflage(seite);
        this._stand = null;
        this._baut = false;
        try { this._buehne(); } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); return; }
        for (const r of document.querySelectorAll('input[name="meshfigur-was"]')) {
            r.addEventListener('change', () => { if (r.checked) { this.was = r.value; this._sichtbarkeit(); } });
        }
    }

    _melden(text) { if (this.hinweis) { this.hinweis.textContent = text; this.hinweis.hidden = !text; } }

    _buehne() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'meshfigur-leinwand';
        this.feld.appendChild(this.canvas);
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(30, 1, 0.05, 50);
        this.kamera.position.set(0, 1.0, 4.4);
        this.steuerung = new OrbitControls(this.kamera, this.canvas);
        this.steuerung.target.set(0, 0.9, 0);
        this.steuerung.enableDamping = true;
        this.szene.add(new THREE.HemisphereLight(0xffffff, 0xc8c2ba, 1.3));
        const haupt = new THREE.DirectionalLight(0xffffff, 1.0);
        haupt.position.set(1, 1.5, 2);
        this.kamera.add(haupt);
        this.szene.add(this.kamera, new THREE.GridHelper(3, 12, 0x445566, 0x2a3340));
        // Der Behälter, nicht das Fenster: Er schrumpft, sobald die rechte Spalte gefüllt ist, ohne dass
        // ein `resize` kommt — gemessen stand die Leinwand dann 1045 × 866 px in 760 × 794 px und zog das
        // Bodengitter über das Formular (27.09.2026).
        new ResizeObserver(() => this._groesse()).observe(this.feld);
        const lauf = () => { this.steuerung.update(); this.renderer.render(this.szene, this.kamera); requestAnimationFrame(lauf); };
        requestAnimationFrame(lauf);
    }

    _groesse() {
        const b = this.feld.clientWidth || 640, h = this.feld.clientHeight || 640;
        this.renderer.setSize(b, h);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
    }

    _sichtbarkeit() {
        if (this.modell) this.modell.group.visible = this.was !== 'netz';
        if (this.netz) {
            this.netz.visible = this.was !== 'figur';
            this.netz.position.x = this.was === 'beide' ? Meshfigurbuehne.ABSTAND : 0;
        }
        const mitte = this.was === 'beide' ? Meshfigurbuehne.ABSTAND / 2 : 0;
        this.steuerung.target.x = mitte;
    }

    // --------------------------------------------------------------- Stand

    async zeigen(z) {
        if (!this.renderer) return;
        const e = z.ergebnis || {};
        if (!this.netz && e.erkennung && e.erkennung.matrix) this._netzLaden(z);
        const stellung = z.stellung || {};
        if (!Object.keys(stellung).length) { this._melden('Noch keine Figur — erst nach der Körperkette.'); return; }
        const stand = JSON.stringify(stellung);
        if (this.modell) this.auflage.anwenden(this.modell, e.fototextur);
        if (stand === this._stand || this._baut) return;
        this._stand = stand;
        await this._bauen(stellung, z);
    }

    async _bauen(stellung, z) {
        this._baut = true;
        this._melden('Figur wird gebaut …');
        try {
            const neu = new Genesis9Modell('meshfigur', { figur: 'basis', regler: stellung, presetName: z.name });
            await neu.bauen();
            if (this.modell) { this.szene.remove(this.modell.group); this.modell.dispose?.(); }
            this.modell = neu;
            this.szene.add(neu.group);
            const h = neu.hoehe || 1.7;
            this.steuerung.target.set(0, h * 0.52, 0);
            this.kamera.position.set(0, h * 0.55, h * 2.6);
            this.auflage.anwenden(neu, (z.ergebnis || {}).fototextur);
            this._sichtbarkeit();
            this._melden('');
        } catch (fehler) {
            this._stand = null;
            this._melden(`Figur nicht gebaut: ${fehler.message}`);
        } finally {
            this._baut = false;
        }
    }

    // ---------------------------------------------------------------- Netz

    _lader(name) {
        const endung = name.toLowerCase().split('.').pop();
        if (endung === 'glb' || endung === 'gltf') return ['gltf', new GLTFLoader()];
        if (endung === 'obj') return ['obj', new OBJLoader()];
        if (endung === 'ply') return ['ply', new PLYLoader()];
        if (endung === 'stl') return ['stl', new STLLoader()];
        return [null, null];
    }

    _netzLaden(z) {
        const datei = (z.eingang || {}).datei;
        const [art, lader] = datei ? this._lader(datei) : [null, null];
        if (!lader) return;
        this.netz = new THREE.Group();
        this.netz.visible = false;
        this.szene.add(this.netz);
        const e = z.ergebnis || {};
        const m = e.erkennung.matrix;
        const faktor = ((e.erkennung || {}).skalierung || {}).faktor || 1;
        const matrix = new THREE.Matrix4().set(...m[0], ...m[1], ...m[2], ...m[3]);
        matrix.premultiply(new THREE.Matrix4().makeScale(faktor, faktor, faktor));
        lader.load(this.seite.dateiAdresse('eingang', datei), ergebnis => {
            let objekt = ergebnis.scene || ergebnis;
            if (ergebnis.isBufferGeometry) {
                ergebnis.computeVertexNormals();
                objekt = new THREE.Mesh(ergebnis, new THREE.MeshStandardMaterial({ color: 0xc9b4a4, roughness: 0.8 }));
            }
            objekt.updateMatrixWorld(true);
            const innen = new THREE.Group();
            innen.matrixAutoUpdate = false;
            innen.matrix.copy(matrix);
            innen.add(objekt);
            this.netz.add(innen);
            this._sichtbarkeit();
        }, undefined, fehler => this._melden(`Netz (${art}) nicht geladen: ${fehler.message || fehler}`));
    }
}
