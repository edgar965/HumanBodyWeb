import { fn } from '../gemeinsam/registrierung.js';
import { UmaFigur } from './uma/umafigur.js';
import { SmplFigur } from './smpl/smplfigur.js';
import { MhFigur } from './makehuman/mhfigur.js';

/**
 * Figurarten — welche Klasse zu einer gespeicherten Figur gehört.
 *
 * WARUM (06.09.2026): Dieselbe Fallunterscheidung stand in `session.js` und in
 * `szenenzustand.js`, und sie wuchs mit jeder neuen Figurart als verschachtelter
 * Bedingungsausdruck:
 *
 *     daten.quelle === UmaFigur.QUELLE ? await UmaFigur.fromJSON(daten)
 *         : (daten.quelle === SmplFigur.QUELLE ? await SmplFigur.fromJSON(daten)
 *             : await fn.CharacterInstance.fromJSON(daten))
 *
 * Bei der vierten Art (MakeHuman) wären das zwei Stellen mit je drei Ebenen —
 * und wer nur eine davon erweitert, bekommt eine Szene, die sich SPEICHERN,
 * aber nicht wiederherstellen lässt: Die Figur landet stumm bei
 * `CharacterInstance`, die den Körpertyp „MakeHuman" beim Server anfragt und
 * eine 500 bekommt. Genau dieser Fehler ist bei UMA schon einmal passiert
 * (Kommentar in `session.js`, 05.09.2026).
 *
 * `CharacterInstance` kommt über die Registrierung und nicht als Import: Sie
 * lädt `character.js`, und das hängt am halben Seitengerüst.
 */
export class Figurarten {

    /** Quelle -> Klasse. Ohne Eintrag gilt die HumanBody-Figur. */
    static KLASSEN = {
        [UmaFigur.QUELLE]: UmaFigur,
        [SmplFigur.QUELLE]: SmplFigur,
        [MhFigur.QUELLE]: MhFigur,
    };

    /** Eine gespeicherte Figur wieder aufbauen. */
    static async ausJSON(daten) {
        const klasse = Figurarten.KLASSEN[daten?.quelle];
        return klasse ? klasse.fromJSON(daten)
                      : fn.CharacterInstance.fromJSON(daten);
    }

    /** Das Symbol der Figur in der Charakterliste. */
    static symbol(inst) {
        return Figurarten.SYMBOLE[inst.quelle]
            || (inst.generatedConfig ? 'fa-robot' : 'fa-user');
    }

    static SYMBOLE = {
        [UmaFigur.QUELLE]: 'fa-user-astronaut',
        [SmplFigur.QUELLE]: 'fa-cube',
        [MhFigur.QUELLE]: 'fa-child',
    };
}
