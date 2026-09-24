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
 * wären importierte Objekte und Modelle völlig schwarz — es bekommt aber
 * (24.09.2026) selbst eine Spur (`Szenenlichter`), damit es über die
 * Licht-Leiste aus-/einschaltbar ist. Vorher lief jedes Mute/„Alle Lichter
 * aus" an ihm vorbei: `state.sceneAmbient` stand fest auf `null`.
 */
export class Studiobuehne {

    /** Größter Zeitschritt der Schleife — nach einem Tabwechsel sonst ein Sprung. */
    static MAX_SCHRITT_S = 0.1;

    bauen() {
        const teile = createSceneSetup(
            /** @type {HTMLCanvasElement} */ (document.getElementById('studio-canvas')));
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
        // Keine Spuren für diese drei. Das Umgebungslicht bleibt in der Szene
        // UND bekommt seine State-Referenz behalten — `Szenenlichter.spurenAnlegen()`
        // legt daraus die vierte Spur „Ambient" an (siehe Klassenkommentar).
        state.sceneKeyLight = null;
        state.sceneFillLight = null;
        state.sceneBackLight = null;
        state.sceneAmbient = teile.ambient || null;
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
