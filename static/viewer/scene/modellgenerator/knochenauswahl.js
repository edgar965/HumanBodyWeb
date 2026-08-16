/**
 * Knochenauswahl — einen Knochen waehlen: Baum hervorheben, Regler nachziehen,
 * Markierung im 3D-Netz zeigen.
 *
 * Aus modellgenerator_ui.js herausgeloest (Umbau 16.08.2026): `_mgSelectBone`
 * war 144 Zeilen lang und bestand fast nur daraus, Element fuer Element den
 * gewaehlten Knochen in die Bedienelemente zu schreiben. Das erledigen jetzt die
 * Tabellen in Formregler und Knochenregler.
 */
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Modellbauzustand } from './zustand.js';
import { Formregler } from './formregler.js';
import { Knochenregler } from './knochenregler.js';
import { Knochenbaum } from './knochenbaum.js';

export class Knochenauswahl {
    static waehlen(name) {
        Modellbauzustand.gewaehlterKnochen = name;
        Knochenbaum.hervorheben(name);

        const abschnitt = document.getElementById('mg-bone-props-section');
        if (abschnitt) abschnitt.style.display = '';
        const anzeige = document.getElementById('mg-bone-name');
        if (anzeige) anzeige.textContent = name;

        const teil = Modellbauzustand.konfig?.bone_parts[name];
        if (!teil) return;

        Knochenregler.nachziehen(teil);
        Formregler.nachziehen(teil);
        Formregler.gruppeZeigen(teil.shape);
        Knochenauswahl._markierungZeigen(name);
    }

    /** Auswahl aufheben — Eigenschaften ausblenden, Hervorhebung loeschen. */
    static aufheben() {
        Modellbauzustand.gewaehlterKnochen = null;
        const abschnitt = document.getElementById('mg-bone-props-section');
        if (abschnitt) abschnitt.style.display = 'none';
        document.querySelectorAll('.mg-bone-item.selected')
            .forEach(el => el.classList.remove('selected'));
    }

    /** Den gewaehlten Knochen im Koerpernetz einfaerben. */
    static _markierungZeigen(name) {
        if (state._boneSelectOverlay) {
            fn._removeBoneOverlay(state._boneSelectOverlay);
            state._boneSelectOverlay = null;
        }
        state._selectedBoneName = name;
        if (!Modellbauzustand.charakterId) return;
        const inst = state.characters.get(Modellbauzustand.charakterId);
        if (!inst?.bodyMesh?.userData.boneVertexRanges) return;
        state._boneSelectOverlay = fn._createBoneOverlay(
            inst.bodyMesh, name, state._BONE_SELECT_MAT);
    }
}
