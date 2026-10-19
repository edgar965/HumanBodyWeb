import { Protokoll } from './protokoll.js';

/**
 * Genesis9kennungumzug — alte Kennungen getragener Stücke auf die neuen umstellen, bevor sie angefragt werden.
 *
 * WARUM (18.10.2026, Edgar: „warum sind bei Matt1 alle Kleider (ausser SChwert) weg?"): Die MakeHuman-Stücke heißen seit
 * demselben Tag `mh_…` statt `mb_…` (`Genesis9/mbstuecke.py`, `HERSTELLER`). Die Modelldateien sind umgestellt, aber ein
 * offener Tab trägt seinen Stand im sessionStorage (`session.js`) und stellte Matt1 mit `mb_rehmanpolanski_viking_tunic`
 * und `…_boots` wieder her — Serverlog 17:51:32 zweimal 404, die Stücke fehlten still; Haar, Anatomie und das Schwert
 * heißen anders und kamen. Dieselbe Fehlerklasse wie `mb_t_shirt` an Ursula1 am 26.09.2026 (`Genesis9aufbau.alles`).
 *
 * Umgestellt wird NUR, wenn der Katalog die alte Kennung nicht mehr kennt und die neue schon: Die Stücke des Daz-Herstellers
 * MagicBrush heißen ebenfalls `mb_…` (`mb_olesia_hd`, `mb_allyne`) und bleiben, wie sie sind. Eine Figur ohne `mb_`-Stück
 * wartet auf nichts; eine mit wartet nur mit diesen Stücken auf den Katalog, den die Garderobe ohnehin holt.
 */
export class Genesis9kennungumzug {

    /** Alter Präfix → neuer. */
    static UMZUG = [['mb_', 'mh_']];

    /**
     * Die Kennung, unter der `kennung` heute im Katalog steht — und `inst.kleidung` gleich mit umgestellt (Reihenfolge bleibt).
     * `null`: das Stück trägt die Figur schon unter dem neuen Namen, die alte Zeile ist gestrichen (nicht doppelt anziehen).
     */
    static async kennung(inst, kennung) {
        const paar = Genesis9kennungumzug.UMZUG.find(([alt]) => kennung.startsWith(alt));
        if (!paar) return kennung;
        const neu = paar[1] + kennung.slice(paar[0].length);
        // Erst hier geladen (19.10.2026): statisch zog `genesis9kleidung.js` Three.js in den Baum von `genesis9aufbau.js`, dessen Node-Test damit seit dem 18.10. scheiterte.
        const { Genesis9kleidung } = await import('./genesis9kleidung.js');
        const ids = new Set((await Genesis9kleidung.stuecke()).map((s) => s.id));
        if (!ids.size || ids.has(kennung) || !ids.has(neu) || !inst.kleidung?.[kennung]) return kennung;
        Protokoll.info('Genesis 9', `${kennung} heißt jetzt ${neu} — umgestellt`);
        if (inst.kleidung[neu]) {
            delete inst.kleidung[kennung];
            return null;
        }
        inst.kleidung = Object.fromEntries(Object.entries(inst.kleidung).map(([k, v]) => [k === kennung ? neu : k, v]));
        return neu;
    }
}
