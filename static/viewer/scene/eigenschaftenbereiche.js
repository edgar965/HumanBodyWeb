/**
 * Eigenschaftenbereiche — was in den Reitern „Eigenschaften" und „Assets"
 * sichtbar ist: Platzhalter oder Inhalt, HumanBody-Teile oder UMA-Garderobe.
 *
 * Herausgelöst aus `properties.js` (05.09.2026, die Datei stand bei 345 Zeilen).
 *
 * WARUM KLASSEN STATT INLINE-STILEN: Die Inhalte tragen seit dem Umbau vom
 * 30.08.2026 die Klasse `hb-versteckt`; ein geleertes `style.display` ließ
 * sie versteckt, und der Reiter „Eigenschaften" blieb leer, obwohl der
 * Charakter ausgewählt war (gefunden und behoben 05.09.2026).
 */
import { Umagarderobe } from './uma/umagarderobe.js';
import { Reiterfreigabe } from './reiterfreigabe.js';

export class Eigenschaftenbereiche {

    static PAARE = [['prop-empty', 'prop-content'], ['assets-empty', 'assets-content']];
    static HUMANBODY = ['prop-equipped-section', 'prop-bodytype-section', 'prop-morphs-section'];

    /** Inhalt zeigen (`true`) oder den Platzhalter „Charakter auswählen". */
    static zeigen(zeigen) {
        for (const [leer, inhalt] of Eigenschaftenbereiche.PAARE) {
            document.getElementById(leer).style.display = zeigen ? 'none' : '';
            document.getElementById(inhalt).classList.toggle('hb-versteckt', !zeigen);
        }
        // HIER und nicht in `selectCharacter`/`deselectCharacter`: Diese
        // Methode wird auf BEIDEN Wegen gerufen (`populateProperties` mit
        // `true`, `clearProperties` mit `false`) — es gibt nur eine Stelle,
        // die den Zustand kennt.
        Reiterfreigabe.anwenden(!!zeigen);
    }

    /** Die HumanBody-Abschnitte (Ausstattung, Body Type, Morphs) zeigen oder verbergen. */
    static humanbodyTeile(sichtbar) {
        for (const id of Eigenschaftenbereiche.HUMANBODY) {
            document.getElementById(id)?.classList.toggle('hb-versteckt', !sichtbar);
        }
    }

    /**
     * Der Assets-Reiter für eine UMA-Figur: statt Garment-, MakeHuman- und
     * Haar-Werkzeugen die Garderobe, die Unity gebaut hat. `null` = keine UMA-Figur.
     */
    static umaGarderobe(figur) {
        const leer = document.getElementById('assets-empty');
        const inhalt = document.getElementById('assets-content');
        if (!leer || !inhalt) return;
        if (!leer.dataset.original) leer.dataset.original = leer.innerHTML;
        if (!figur) {
            leer.innerHTML = leer.dataset.original;
            return;
        }
        leer.style.display = '';
        inhalt.classList.add('hb-versteckt');
        Umagarderobe.fuellen(leer, figur);
    }
}
