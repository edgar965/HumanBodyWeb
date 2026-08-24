import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Spurauswahl — welche Spur im Studio gerade bearbeitet wird.
 *
 * Herausgelöst aus `tracks.js` (324 Zeilen), damit die Spur-Klassen sie rufen
 * können, ohne dass ein Ringimport entsteht.
 *
 * Beim Wechsel wandern die Verschiebe-Griffe mit: Sie hängen nur an einem
 * eigenen 3D-Objekt. Bleiben sie an der alten Spur, verschiebt der nächste Zug
 * ein Objekt, das gar nicht mehr ausgewählt ist.
 */
export class Spurauswahl {

    static waehlen(index) {
        state.selectedTrackIdx = index;
        state.selectedClipIdx = -1;
        const spur = state.project.tracks[index];
        if (spur?.type === 'scene_object' && spur.subtype === 'custom'
                && spur.mesh) {
            fn.attachTransformControls?.(spur);
        } else {
            fn.detachTransformControls?.();
        }
        fn.updateTrackHeaders();
        fn.updateProperties();
        fn.switchPropsTab?.('props');
    }
}
