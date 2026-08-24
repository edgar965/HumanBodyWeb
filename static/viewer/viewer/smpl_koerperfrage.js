import { buildBodyFitQueryString } from './garment.js';
import { Metawerte } from './metawerte.js';

/**
 * Smplkoerperfrage — der Körperteil der Anpassfrage an den Server.
 *
 * Herausgelöst aus `smpl.js` (393 Zeilen). Es gibt ZWEI Seiten mit SMPL-
 * Kleidung, und sie haben verschiedene Bedienfelder:
 *
 * * Die Modellseite hat die Kleiderregler (`#garment-offset`). Dort liefert
 *   `buildBodyFitQueryString()` alles — Körpertyp, Abstand, Steifigkeit, Farbe,
 *   Morphs, Metawerte.
 * * Die SMPL-Testseite hat sie NICHT. Dort dürfen die Kleiderwerte auch nicht
 *   mitgeschickt werden: `sliderVal` liefert für fehlende Regler 0, und ein
 *   Abstand von 0 mm ist etwas anderes als „nicht angegeben" — das Stück klebt
 *   dann auf der Haut.
 *
 * Ihre Morphregler tragen ausserdem nicht immer `data-morph`; deshalb die drei
 * Fallbacks auf `data-morphName` und die Kennung.
 */
export class Smplkoerperfrage {

    static LEITREGLER = 'garment-offset';
    static ERSATZKOERPER = 'Female_Caucasian';

    /** Der Körperteil der Frage — je nach Seite vollständig oder schlank. */
    static text() {
        if (document.getElementById(Smplkoerperfrage.LEITREGLER)) {
            return buildBodyFitQueryString();
        }
        return Smplkoerperfrage._ohneKleiderregler();
    }

    static _ohneKleiderregler() {
        const wahl = document.getElementById('body-type-select');
        const koerper = wahl ? wahl.value : Smplkoerperfrage.ERSATZKOERPER;
        let frage = `body_type=${encodeURIComponent(koerper)}`;
        frage += Smplkoerperfrage._morphs();
        frage += Smplkoerperfrage._meta();
        return frage;
    }

    static _morphs() {
        let frage = '';
        document.querySelectorAll('#morphs-panel input[type="range"]')
            .forEach(regler => {
                const name = regler.dataset.morph || regler.dataset.morphName
                    || regler.id.replace('morph-', '');
                if (name && regler.value !== undefined) {
                    frage += `&morph_${name}=${regler.value / 100}`;
                }
            });
        return frage;
    }

    /** Die vier Metawerte auf −1…+1 umgerechnet (siehe `metawerte.js`). */
    static _meta() {
        return Metawerte.frage();
    }
}
