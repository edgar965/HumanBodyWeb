import { state, TRACK_HEIGHT } from './state.js';

/**
 * Die Gruppenzeile in der Kopfspalte — „Lichter" bzw. „Szene", zum Ein- und
 * Ausklappen.
 *
 * Aus zeitleiste_kopfspalte.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`: `updateTrackHeaders()` hatte 97 Zeilen).
 */
export class Gruppenkopf {
    /** Farben und Sinnbild je Gruppenart. */
    static ARTEN = {
        light: { grund: 'rgba(255,193,7,0.12)', rand: 'rgba(255,193,7,0.4)',
                 schrift: '#ffc107', bild: 'fa-lightbulb' },
        scene: { grund: 'rgba(124,92,191,0.12)', rand: 'rgba(124,92,191,0.4)',
                 schrift: '#b388ff', bild: 'fa-cube' },
    };

    /** @param {string} art `'light'` oder sonst */
    static farben(art) {
        return Gruppenkopf.ARTEN[art] || Gruppenkopf.ARTEN.scene;
    }

    /**
     * @param {{header: string, label: string, collapsed: boolean}} reihe
     * @param {Function} neuzeichnen wird nach dem Umklappen gerufen
     * @returns {HTMLElement}
     */
    static element(reihe, neuzeichnen) {
        const farben = Gruppenkopf.farben(reihe.header);
        const el = document.createElement('div');
        el.className = 'track-group-header';
        el.style.cssText = `height:${TRACK_HEIGHT}px;padding:0 12px;`
            + `background:${farben.grund};border-top:1px solid ${farben.rand};`
            + `border-bottom:1px solid ${farben.rand};color:${farben.schrift};`
            + 'font-weight:bold;font-size:0.78rem;display:flex;'
            + 'align-items:center;box-sizing:border-box;cursor:pointer;'
            + 'user-select:none;';
        const pfeil = reihe.collapsed ? 'fa-caret-right' : 'fa-caret-down';
        el.innerHTML = `<i class="fas ${pfeil}" style="margin-right:6px;`
            + `width:10px;"></i><i class="fas ${farben.bild}" `
            + `style="margin-right:6px;"></i>${reihe.label}`;
        el.title = 'Klick zum Ein-/Ausklappen';
        el.addEventListener('click', () => {
            if (reihe.header === 'light') {
                state.lightGroupCollapsed = !state.lightGroupCollapsed;
            } else {
                state.sceneGroupCollapsed = !state.sceneGroupCollapsed;
            }
            neuzeichnen();
        });
        return el;
    }
}
