import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { el, Abschnitt } from './bauteile.js';
import { Morphliste } from '../gemeinsam/morphliste.js';

/**
 * Morphregler — der Abschnitt "Morphs" des Bedienfelds der Ergebnisseite.
 *
 * Aus ui_panel.js herausgeloest (Umbau 16.08.2026). Die Kategorienliste selbst
 * kommt aus `Morphliste`; hier steht nur, was diese Seite eigen hat: das
 * `rc-`-Präfix ihrer CSS-Klassen, die Werte aus `state.currentMorphs` und der
 * Reset-Knopf in der Kopfzeile.
 */
export class Morphregler {

    constructor(daten) {
        this.daten = daten;
        this.abschnitt = new Abschnitt('Morphs', false);
        this.liste = new Morphliste({
            praefix: 'rc-',
            startwert: name => state.currentMorphs[name],
            geaendert: (name, wert) => {
                state.currentMorphs[name] = wert;
                fn.sendMorphThrottled(name, wert);
            },
        });
    }

    bauen() {
        this.abschnitt.kopf.appendChild(this._zuruecksetzen());
        this.liste.bauen(this.abschnitt.inhalt, this.daten.morphs,
                         this.daten.categories);
        return this.abschnitt.el;
    }

    _zuruecksetzen() {
        const knopf = el('button', 'rc-btn-sm');
        knopf.textContent = 'Reset';
        knopf.addEventListener('click', () => {
            Morphliste.zuruecksetzen(this.abschnitt.inhalt,
                                     name => { state.currentMorphs[name] = 0; });
            fn.wsSend({ type: 'reset', body_type: state.currentBodyType });
        });
        return knopf;
    }
}
