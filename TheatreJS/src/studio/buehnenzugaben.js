import * as THREE from 'three';
import { loadGLBFromFile } from '../asset-loader.js';
import { createLightSheet } from '../theatre-bridge.js';
import { PRESETS, applyPreset } from '../presets.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Buehnenzugaben — was der Nutzer der Bühne hinzufügen kann.
 *
 * Herausgelöst aus `main.js` (788 Zeilen): GLB-Datei einfügen, eine
 * Beleuchtungsvorgabe anwenden, ein zusätzliches Licht setzen.
 *
 * Das neue Licht bekommt eine ZUFÄLLIGE Position im Bühnenraum — zwei Lichter
 * exakt übereinander sähen aus wie eines, und der Nutzer zieht es ohnehin
 * dorthin, wo er es braucht. Die gelbe Kugel daran ist der Griff: Ein
 * `PointLight` allein ist unsichtbar und damit nicht anklickbar.
 *
 * Jedes neue Licht bekommt ein eigenes Theatre-Blatt, sonst ist es nicht
 * animierbar.
 */
export class Buehnenzugaben {

    static LICHTSTAERKE = 1.0;
    static LICHTWEITE = 15;
    static GRIFFGROESSE = 0.08;
    static RAUM = { breite: 6, hoeheMin: 2, hoeheSpanne: 3 };

    /**
     * @param {Object} buehne { scene, camera, lights, controls, sheet }
     */
    constructor(buehne) {
        Object.assign(this, buehne);
        this.lichtzaehler = 0;
    }

    verdrahten() {
        this._glbImport();
        this._vorgabenknoepfe();
        this._lichtknopf();
        return this;
    }

    // ------------------------------------------------------------ GLB-Import

    _glbImport() {
        const menue = document.getElementById('menu-add-glb');
        const feld = document.getElementById('glb-file-input');
        if (!menue || !feld) return;
        menue.addEventListener('click', () => feld.click());
        feld.addEventListener('change', async () => {
            const datei = feld.files[0];
            if (datei) await this._glbLaden(datei);
            feld.value = '';   // damit dieselbe Datei erneut waehlbar ist
        });
    }

    async _glbLaden(datei) {
        try {
            await loadGLBFromFile(datei, this.scene);
        } catch (fehler) {
            Protokoll.fehler('main', 'GLB nicht ladbar', fehler);
            alert('Fehler beim Laden der GLB-Datei: ' + fehler.message);
        }
    }

    // ------------------------------------------------------- Lichtvorgaben

    _vorgabenknoepfe() {
        document.querySelectorAll('[data-preset]').forEach(knopf => {
            knopf.addEventListener('click', () => {
                const name = knopf.getAttribute('data-preset');
                const vorgabe = PRESETS[name];
                if (!vorgabe) {
                    Protokoll.warnung('main', 'Preset not found:', name);
                    return;
                }
                applyPreset(vorgabe, this.camera, this.lights, this.controls);
                Protokoll.debug('main', '✓ Applied preset:', vorgabe.name);
            });
        });
    }

    // --------------------------------------------------------- Zusatzlicht

    _lichtknopf() {
        document.getElementById('menu-add-light')
            ?.addEventListener('click', () => this.lichtHinzufuegen());
    }

    lichtHinzufuegen() {
        this.lichtzaehler++;
        const licht = new THREE.PointLight(0xffffff, Buehnenzugaben.LICHTSTAERKE,
                                           Buehnenzugaben.LICHTWEITE);
        licht.position.set(...Buehnenzugaben._platz());
        this.scene.add(licht);
        licht.add(Buehnenzugaben._griff());
        createLightSheet(this.sheet, `Light ${this.lichtzaehler}`, licht);
        return licht;
    }

    static _platz() {
        const raum = Buehnenzugaben.RAUM;
        return [(Math.random() - 0.5) * raum.breite,
                raum.hoeheMin + Math.random() * raum.hoeheSpanne,
                (Math.random() - 0.5) * raum.breite];
    }

    /** Die sichtbare Kugel am Licht — ohne sie ist es nicht anklickbar. */
    static _griff() {
        return new THREE.Mesh(
            new THREE.SphereGeometry(Buehnenzugaben.GRIFFGROESSE, 8, 8),
            new THREE.MeshBasicMaterial({ color: 0xffff00 }));
    }
}
