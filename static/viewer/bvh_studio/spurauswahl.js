import { state, TRACK_HEIGHT, RULER_HEIGHT } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Reihen } from './zeitleiste_reihen.js';
import { Modellgruppen } from './modellgruppen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';

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
        Spurauswahl.einblenden(index, spur);
        fn.updateTrackHeaders();
        fn.updateProperties();
        fn.switchPropsTab?.('props');
    }

    /**
     * Die Reihe der gewählten Spur in den sichtbaren Teil der Zeitleiste rollen;
     * steckt sie in einer zugeklappten Gruppe, die Gruppe aufklappen.
     *
     * WARUM (11.09.2026, Edgar: „ich finde nicht den Schwan in der Timeline"):
     * Der Rahmen zeigt vier Reihen, der Schwan lag als 3D-Objekt in der Gruppe
     * „Szene" auf Reihe 14 von 15. Der Klick auf ihn im Bild wählte die Spur —
     * zu sehen war davon nichts, sie stand 400 px unter dem Rand.
     */
    static einblenden(index, spur) {
        if (spur?.type === 'light' && state.lightGroupCollapsed) {
            state.lightGroupCollapsed = false;
        }
        if (spur?.type === 'scene_object' && state.sceneGroupCollapsed) {
            state.sceneGroupCollapsed = false;
        }
        // Eine Animation unter einer zugeklappten Modellspur: aufklappen.
        const traeger = state.project.tracks[
            Modellgruppen.traeger(state.project.tracks, index)];
        if (traeger?.zugeklappt) traeger.zugeklappt = false;
        const rahmen = Zeitleistenflaeche.rahmen;
        const oben = Reihen.yFuerSpur(index);
        if (!rahmen || oben < 0) return;
        const unten = oben + TRACK_HEIGHT;
        if (oben - RULER_HEIGHT < rahmen.scrollTop) {
            rahmen.scrollTop = oben - RULER_HEIGHT;
        } else if (unten > rahmen.scrollTop + rahmen.clientHeight) {
            rahmen.scrollTop = unten - rahmen.clientHeight;
        }
        fn.renderTimeline?.();
    }
}
