import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _populateTrackAddSubmenu } from './zeitleiste_spurmenue.js';
import { pushUndo } from './undo.js';
import { Modellhinzufuegen } from './zeitleiste_modellhinzufuegen.js';

/**
 * Das Rechtsklickmenü einer Spur in der Kopfspalte.
 *
 * Aus zeitleiste_kopfspalte.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`).
 */
export class Spurkontextmenue {
    /** Abstand des Menüs zum unteren Fensterrand in Pixeln. */
    static RANDABSTAND = 10;
    /** Angenommene Menühöhe, solange sie noch nicht gemessen werden kann. */
    static ERSATZHOEHE = 200;

    /**
     * @param {Object} spur die Spur, zu der das Menü gehört
     * @param {number} index ihre Stelle in `state.project.tracks`
     * @param {MouseEvent} e das auslösende Ereignis
     */
    static oeffnen(spur, index, e) {
        const menue = document.getElementById('track-context-menu');
        if (!menue) return;
        Spurkontextmenue._hinzufuegen(spur, index, menue);
        Spurkontextmenue._stummschrift(spur);
        Spurkontextmenue._verknuepfung(spur, menue);
        // `block`, nicht '' — die Klasse `.hb-kontextmenue` versteckt sonst
        // weiter (siehe `Zeitleistenmenue._zeigen`).
        menue.style.display = 'block';
        menue.style.left = e.clientX + 'px';
        const hoehe = menue.offsetHeight || Spurkontextmenue.ERSATZHOEHE;
        menue.style.top = Math.min(
            e.clientY,
            window.innerHeight - hoehe - Spurkontextmenue.RANDABSTAND) + 'px';
    }

    /**
     * „Hinzufügen" — bei einer Modellspur zweigeteilt (Edgar, 15.09.2026:
     * „Rechtsklick bei Modell — Hinzufügen ist nicht geändert!!!"): „Modell
     * hinzufügen" mit den Figurarten und „Animation hinzufügen" mit
     * Animation, Mimik, Script — am Abspielkopf, der Spurkopf hat keine Zeit.
     */
    static _hinzufuegen(spur, index, menue) {
        const modell = spur.type === 'model';
        const schrift = document.getElementById('track-ctx-add-label');
        if (schrift) schrift.textContent = modell ? 'Modell hinzufügen' : 'Hinzufügen';
        document.getElementById('track-ctx-anim')?.classList.toggle('hb-versteckt', !modell);
        if (!modell) {
            _populateTrackAddSubmenu(spur, index, menue);
            return;
        }
        const bild = state.playheadFrame;
        Modellhinzufuegen.fuellen(spur, index, menue, bild,
                                 { modell: 'track-ctx-add-submenu', bvh: 'track-ctx-bvh-submenu' });
        Modellhinzufuegen.binden(menue, index, bild);
    }

    /** „Ausschalten" oder „Einschalten" — je nachdem, wie die Spur steht. */
    static _stummschrift(spur) {
        const schrift = document.getElementById('track-ctx-mute-label');
        if (schrift) schrift.textContent = spur.muted ? 'Einschalten'
                                                      : 'Ausschalten';
    }

    /** Die Liste „mit Animation verknüpfen" gibt es nur bei Figurenspuren. */
    static _verknuepfung(spur, menue) {
        const abschnitt = document.getElementById('track-ctx-link-section');
        const liste = document.getElementById('track-ctx-link-list');
        if (spur.type !== 'model' || !abschnitt || !liste) {
            if (abschnitt) abschnitt.style.display = 'none';
            return;
        }
        // 'block'/'inline-block' statt '': die Vorlage versteckt per Klasse (11.09.2026)
        abschnitt.style.display = 'block';
        liste.innerHTML = '';
        state.project.animations.forEach(anim => {
            liste.appendChild(
                Spurkontextmenue._verknuepfungszeile(spur, anim, menue));
        });
    }

    static _verknuepfungszeile(spur, anim, menue) {
        const stelle = state.project.indexOf(anim);
        const verknuepft = spur._linkedAnimIdx === stelle;
        const zeile = document.createElement('div');
        zeile.className = 'ctx-item';
        zeile.innerHTML = `<i class="fas `
            + `${verknuepft ? 'fa-check' : 'fa-running'}" style="width:16px;`
            + `color:${verknuepft ? '#4caf50' : '#666'};"></i> ${anim.name}`;
        zeile.style.fontWeight = verknuepft ? 'bold' : '';
        zeile.addEventListener('click', () => {
            pushUndo('Verknüpfung ändern');
            spur._linkedAnimIdx = stelle;
            spur._currentPreset = null;
            fn.applyPlayhead();
            menue.style.display = 'none';
        });
        return zeile;
    }
}
