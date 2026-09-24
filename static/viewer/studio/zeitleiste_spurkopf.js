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
 *
 * Eine Modellspur mit verknüpfter Animation (`reihe.unterreihe`, siehe
 * `Modellgruppen`) trägt vorn den Pfeil der Gruppenköpfe; der Klick darauf
 * klappt die Unterreihe zu oder auf, ohne die Spur zu wählen (11.09.2026).
 */
export class Spurkopf {
    /**
     * @param {{trackIdx: number, indent: boolean, unterreihe: number, collapsed: boolean}} reihe
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
        el.innerHTML = Spurkopf._pfeil(reihe)
            + `<i class="fas ${bild}" style="color:${spur.color};`
            + 'margin-right:6px;font-size:0.75rem;width:14px;'
            + `text-align:center;"></i>${spur.name}`;
        el.querySelector('.gruppenpfeil')?.addEventListener('click', (e) => {
            e.stopPropagation();
            spur.zugeklappt = !spur.zugeklappt;
            fn.updateTrackHeaders();
            fn.renderTimeline();
        });
        el.addEventListener('click', () => fn.selectTrack(index));
        el.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            fn.selectTrack(index);
            Spurkontextmenue.oeffnen(spur, index, e);
        });
        Spurkopf._ablageziel(el, index);
        return el;
    }

    /** Der Klapp-Pfeil — nur an einer Modellspur mit Unterreihe. */
    static _pfeil(reihe) {
        if (reihe.unterreihe === undefined) return '';
        const richtung = reihe.collapsed ? 'fa-caret-right' : 'fa-caret-down';
        const tipp = reihe.collapsed ? 'Verknüpfte Animation zeigen'
                                     : 'Verknüpfte Animation zuklappen';
        return `<i class="fas ${richtung} gruppenpfeil" title="${tipp}"></i>`;
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
