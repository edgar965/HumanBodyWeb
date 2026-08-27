import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';

/**
 * Linksklick in der 3D-Ansicht: wählt den Lichthelfer oder das Szenenobjekt
 * unter dem Zeiger aus.
 *
 * Gesammelt werden ALLE Kandidaten, ausgewählt wird der NÄCHSTE — sonst
 * gewinnt ein Lichtkegel weit hinten gegen den Boden direkt vor der Kamera.
 *
 * Aus szenenmenue.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`).
 */
export class Szenenauswahl {
    /** Näher als das ist ein Treffer die Kameraebene selbst. */
    static MINDESTABSTAND = 0.01;

    /** @param {HTMLCanvasElement} canvas */
    constructor(canvas) {
        this.canvas = canvas;
        this.strahl = new THREE.Raycaster();
        this.zeiger = new THREE.Vector2();
        canvas.addEventListener('mousedown', (e) => this._maustaste(e));
    }

    _maustaste(e) {
        if (e.button !== 0 || e.altKey || e.shiftKey || e.ctrlKey) return;
        const rahmen = this.canvas.getBoundingClientRect();
        this.zeiger.x = ((e.clientX - rahmen.left) / rahmen.width) * 2 - 1;
        this.zeiger.y = -((e.clientY - rahmen.top) / rahmen.height) * 2 + 1;
        this.strahl.setFromCamera(this.zeiger, state.camera);

        const naechste = this._naechsteSpur();
        if (naechste !== null) fn.selectTrack?.(naechste);
    }

    /** @returns {number|null} Stelle der nächstgelegenen getroffenen Spur */
    _naechsteSpur() {
        let beste = null;
        let bester = Infinity;
        for (let i = 0; i < state.project.tracks.length; i++) {
            const abstand = this._abstand(state.project.tracks[i]);
            if (abstand !== null && abstand < bester) {
                bester = abstand;
                beste = i;
            }
        }
        return beste;
    }

    /** @returns {number|null} Abstand des nächsten Treffers auf dieser Spur */
    _abstand(spur) {
        if (spur.type === 'light' && spur.lightHelper) {
            return this._lichtabstand(spur);
        }
        if (spur.type === 'scene_object' && spur.mesh) {
            const treffer = this._treffer(spur.mesh);
            return treffer.length > 0 ? treffer[0].distance : null;
        }
        return null;
    }

    /**
     * Die Helferlinien zählen nur, wenn der Nutzer sie eingeschaltet hat; der
     * Kegel, solange er nicht ausgeschaltet ist.
     */
    _lichtabstand(spur) {
        const ziele = [];
        if (spur.lightVisible && spur.lightHelper.spotHelper) {
            ziele.push(spur.lightHelper.spotHelper);
        }
        if (spur.coneVisible !== false && spur.lightHelper.originCone) {
            ziele.push(spur.lightHelper.originCone);
        }
        let naechster = null;
        for (const ziel of ziele) {
            const treffer = this._treffer(ziel);
            if (treffer.length > 0
                && (naechster === null || treffer[0].distance < naechster)) {
                naechster = treffer[0].distance;
            }
        }
        return naechster;
    }

    _treffer(ziel) {
        return this.strahl.intersectObject(ziel, true).filter(
            t => Szenenauswahl._sichtbar(t.object)
                 && t.distance > Szenenauswahl.MINDESTABSTAND);
    }

    /**
     * Objekt UND alle Vorfahren müssen sichtbar sein — three.js trifft auch
     * `visible: false` (so gewollt).
     */
    static _sichtbar(objekt) {
        for (let o = objekt; o; o = o.parent) {
            if (o.visible === false) return false;
        }
        return true;
    }
}
