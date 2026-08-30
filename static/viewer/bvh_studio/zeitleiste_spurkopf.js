import { state, TRACK_ICONS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Spurkontextmenue } from './zeitleiste_kontextmenue.js';

/**
 * Die Zeile einer Spur in der Kopfspalte: Sinnbild, Name, Rechtsklickmenü und
 * Ablageziel für Bewegungen aus der Bibliothek.
 *
 * Aus zeitleiste_kopfspalte.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`).
 */
export class Spurkopf {
    /**
     * @param {{trackIdx: number, indent: boolean}} reihe
     * @returns {HTMLElement}
     */
    static element(reihe) {
        const index = reihe.trackIdx;
        const spur = state.project.tracks[index];
        const el = document.createElement('div');
        el.className = 'track-header'
            + (index === state.selectedTrackIdx ? ' selected' : '')
            + (reihe.indent ? ' spur-eingerueckt' : '');
        const bild = TRACK_ICONS[spur.type] || 'fa-running';
        el.innerHTML = `<i class="fas ${bild}" style="color:${spur.color};`
            + 'margin-right:6px;font-size:0.75rem;width:14px;'
            + `text-align:center;"></i>${spur.name}`;
        el.addEventListener('click', () => fn.selectTrack(index));
        el.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            fn.selectTrack(index);
            Spurkontextmenue.oeffnen(spur, index, e);
        });
        Spurkopf._ablageziel(el, index);
        return el;
    }

    /** Bewegungen aus der Bibliothek lassen sich auf die Spur ziehen. */
    static _ablageziel(el, index) {
        el.addEventListener('dragover', (e) => {
            e.preventDefault();
            el.classList.add('drop-target');
        });
        el.addEventListener('dragleave', () => el.classList.remove('drop-target'));
        el.addEventListener('drop', (e) => {
            e.preventDefault();
            el.classList.remove('drop-target');
            try {
                const daten = JSON.parse(
                    e.dataTransfer.getData('application/json'));
                fn.addClipToTrack(index, daten.category, daten.name,
                                  daten.frames);
            } catch (fehler) {
                Protokoll.debug('zeitleiste',
                                'Ablage ohne verwertbare JSON-Daten', fehler);
            }
        });
    }
}
