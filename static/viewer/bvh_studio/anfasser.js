/**
 * Anfasser — die Ziehgriffe (TransformControls) fuer Szenenobjekte.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026). Die Datei hiess
 * "Erweiterungen" und enthielt vier unverwandte Themen auf 784 Zeilen:
 * Bodenspur, Theatre-Lichtvorgaben, Objektimport und diese Griffe. Jedes hat
 * jetzt sein Modul, und jedes meldet seine eigenen Eintraege in der Registry
 * an — vorher stand am Dateiende ein Block mit fuenfzehn `fn.x = y`.
 */
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

export class Anfasser {
    static griffe = null;

    static aufbauen() {
        if (!state.camera || !state.renderer || !state.scene) return;
        const griffe = new TransformControls(state.camera, state.renderer.domElement);
        griffe.setSize(0.8);
        griffe.addEventListener('dragging-changed', (e) => {
            // Waehrend des Ziehens darf die Kamerasteuerung nicht mitlaufen.
            if (state.controls) state.controls.enabled = !e.value;
        });
        // Ab Three.js r170 ist TransformControls eine Controls-Klasse und
        // liefert ihr Anzeigeobjekt ueber getHelper(); vorher war sie selbst
        // ein Object3D.
        state.scene.add(typeof griffe.getHelper === 'function'
            ? griffe.getHelper() : griffe);
        Anfasser.griffe = griffe;
    }

    static anhaengen(spurOderNetz) {
        const netz = spurOderNetz?.mesh || spurOderNetz;
        if (Anfasser.griffe && netz) Anfasser.griffe.attach(netz);
    }

    static loesen() {
        Anfasser.griffe?.detach();
    }

    /** 'translate' | 'rotate' | 'scale' */
    static modus(art) {
        Anfasser.griffe?.setMode(art);
    }
}

fn.attachTransformControls = Anfasser.anhaengen;
fn.detachTransformControls = Anfasser.loesen;
fn.setTransformMode = Anfasser.modus;
