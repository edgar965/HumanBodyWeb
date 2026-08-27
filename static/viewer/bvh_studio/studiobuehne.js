import { state } from './state.js';
import { createSceneSetup } from '../character_core.js';

/**
 * Studiobuehne — Renderer, Szene und Kamera des BVH-Studios.
 *
 * Aus `index.js init()` herausgeloest (Umbau 16.08.2026).
 *
 * Besonderheit: Das Studio übernimmt den gemeinsamen Szenenaufbau, entfernt
 * aber die drei gerichteten Lichter wieder. Grund (aus dem ursprünglichen
 * Kommentar): Im Studio soll das Licht über Licht-SPUREN kommen, die der
 * Benutzer selbst anlegt. Das Umgebungslicht bleibt als Szenenelement, sonst
 * wären importierte Objekte und Modelle völlig schwarz.
 */
export class Studiobuehne {

    /** Größter Zeitschritt der Schleife — nach einem Tabwechsel sonst ein Sprung. */
    static MAX_SCHRITT_S = 0.1;

    bauen() {
        const teile = createSceneSetup(document.getElementById('studio-canvas'));
        state.renderer = teile.renderer;
        state.scene = teile.scene;
        state.camera = teile.camera;
        state.controls = teile.controls;
        this._lichterEntfernen(teile);
        this._groesseVerfolgen();
        return this;
    }

    _lichterEntfernen(teile) {
        for (const licht of [teile.keyLight, teile.fillLight, teile.backLight]) {
            if (!licht) continue;
            teile.scene.remove(licht);
            licht.dispose?.();
        }
        // Keine Spuren für diese Lichter — auch nicht für das Umgebungslicht,
        // das in der Szene bleibt.
        state.sceneKeyLight = null;
        state.sceneFillLight = null;
        state.sceneBackLight = null;
        state.sceneAmbient = null;
    }

    _groesseVerfolgen() {
        const nachziehen = () => this.groesseAnpassen();
        window.addEventListener('resize', nachziehen);
        const ansicht = document.querySelector('.studio-viewport');
        if (ansicht && typeof ResizeObserver !== 'undefined') {
            new ResizeObserver(nachziehen).observe(ansicht);
        }
    }

    groesseAnpassen() {
        const ansicht = document.querySelector('.studio-viewport');
        if (!ansicht) return;
        const breite = ansicht.clientWidth;
        const hoehe = ansicht.clientHeight;
        if (!breite || !hoehe) return;
        state.renderer.setSize(breite, hoehe, false);
        state.camera.aspect = breite / hoehe;
        state.camera.updateProjectionMatrix();
    }
}
