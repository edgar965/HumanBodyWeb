import { state } from './state.js';
import { Lichtsetzen } from './lichtsetzen.js';
import { Szenenauswahl } from './szenenauswahl.js';

/**
 * Kontextmenue und Klickauswahl in der 3D-Ansicht des Studios.
 *
 * Aus index.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): 96 Zeilen in einer Funktion. Das
 * Setzen per Alt+Klick steht jetzt in `Lichtsetzen`, die Klickauswahl in
 * `Szenenauswahl`.
 */
export function setupViewportContextMenu() {
    const menue = document.getElementById('viewport-context-menu');
    if (menue) menue.style.display = 'none';

    const canvas = state.renderer?.domElement
                   || document.getElementById('studio-canvas');
    if (!canvas) return;

    new Lichtsetzen(canvas);
    new Szenenauswahl(canvas);
}

