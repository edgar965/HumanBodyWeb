import { Serverabruf } from './serverabruf.js';
import { Genesis9netz } from './genesis9netz.js';
import { Genesis9aufbau } from './genesis9aufbau.js';
import { Genesis9lagen } from './genesis9lagen.js';

/**
 * Genesis9kleidung — Daz-Stücke einer Genesis-9-Figur anziehen und ausziehen,
 * über den getragenen Stücken darunter (`Genesis9lagen`).
 *
 * Herausgelöst aus `genesis9modell.js` (19.09.2026, 327 Zeilen), als die
 * Lagen dazukamen — Edgar: „das genesis T-Shirt ist an einigen Stellen
 * kaputt". Was die Lagen sind und warum, steht in `genesis9lagen.js`; hier
 * nur der Weg zum Server und die Netze.
 */
export class Genesis9kleidung {

    static stilliste(werte) { return Genesis9lagen.stilliste(werte); }

    /**
     * Ein Stück anziehen — alle seine Teile, über den getragenen Stücken darunter.
     * `werte`: `{variante, stil, stile: {pose, laenge}, regler, griff}`.
     */
    static async anziehen(inst, kennung, werte, stufen, kaskade) {
        inst.kleidung[kennung] = { ...(werte || {}) };
        const lauf = inst._lauf;
        const daten = await Serverabruf.senden(Genesis9aufbau.adresse(
            `${inst.constructor.ADRESSE}garderobe/${encodeURIComponent(kennung)}/netz/`, stufen), {
                regler: inst.regler || {}, variante: werte?.variante || '',
                stil: Genesis9kleidung.stilliste(werte), regler_stueck: werte?.regler || {},
                pose: inst.pose, ausdruck: inst.ausdruck, griffe: inst.griffe(),
                ...Genesis9lagen.anfrage(inst.kleidung, kennung),
            });
        if (daten.fehler) throw new Error(daten.fehler);
        if (lauf !== inst._lauf || !inst.kleidung[kennung]) return 0;   // überholt oder ausgezogen
        inst._stueckWeg(kennung);
        (daten.teile || []).forEach((teil, nummer) => {
            const netz = Genesis9netz.bauen(teil, `genesis9_kleid_${kennung}_${nummer}`);
            inst.clothMeshes[`${kennung}/${nummer}`] = inst._einhaengen(netz, teil.hautgewichte);
        });
        await Genesis9lagen.nachziehen(inst, kennung, daten, stufen, kaskade);
        return daten.teile?.length || 0;
    }

    /** Ausziehen; `neu`: die Figur wird ohnehin neu gebaut (Griffpose, eigene Knochen). */
    static async ausziehen(inst, kennung, neu) {
        inst._stueckWeg(kennung);
        delete inst.kleidung[kennung];
        if (neu) await inst.neuFormen();
        else await Genesis9lagen.nachAusziehen(inst, kennung);
    }
}
