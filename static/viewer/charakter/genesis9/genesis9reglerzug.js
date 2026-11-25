import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9groessehalten } from './genesis9groessehalten.js';
import { Genesis9nachformen } from '../../gemeinsam/genesis9nachformen.js';
import { Genesis9reglerfeld } from '../../gemeinsam/genesis9reglerfeld.js';
import { Genesis9sofortzug } from '../../gemeinsam/genesis9sofortzug.js';

/**
 * Genesis9reglerzug — ein Reglerzug in zwei Schritten (25.11.2026, Edgar: „alle regler unter 0,2 s“):
 *
 *   1. SOFORT  die stehende Figur verschiebt sich im Browser mit dem Schieber (`Genesis9sofortzug`; beim ersten Zug holt `Genesis9reglerfeld` das Feld, 0,03–0,2 s)
 *   2. GENAU   nach dem Loslassen (oder `PAUSE_MS` ohne Bewegung — der genaue Zug baut nichts neu, `Genesis9nachformen`) rechnet der Server nach, was die Sofortschau nicht genau kennt (`Genesis9lauf`): steht der Körper schon genau da
 *              (`Genesis9sofortzug.plan`), nur die berührten Stücke, sonst Körper und Kleidung wie bisher
 *
 * Solange Schritt 2 aussteht, läuft die Sanduhr (`Genesis9lauf`). Loslassen, Verweilen und Fokus werden EINMAL am Dokument gehört — die Liste hat dreitausend Schieber.
 */
export class Genesis9reglerzug {

    /** So lange darf der Schieber beim Ziehen stehen, bevor der genaue Zug beginnt. */
    static PAUSE_MS = 150;
    /** Nach dem Loslassen. */
    static LOS_MS = 0;
    /** So lange steht der Zeiger auf dem Schieber, bis sein Feld vorab kommt. */
    static VERWEIL_MS = 90;
    /** Schieber → {inst, regler} */
    static _zeilen = new WeakMap();
    static _verdrahtet = false;
    static _warten = null;

    /**
     * @param kanaele  die Kanäle, die dieser Regler stellt (Haupt-, Gegenstück-, Aliaskanäle), `grenzen` je Kanal (`Genesis9reglerzeile.stellen`)
     * @param genau    () => Promise — der genaue Zug
     */
    static ziehen(inst, name, { kanaele, grenzen }, genau, nachher) {
        Genesis9sofortzug.zeigen(inst);
        Genesis9reglerfeld.nachziehen(inst, kanaele, grenzen);
        Genesis9lauf.planen(inst, () => Genesis9reglerzug._genau(inst, genau), nachher, `regler:${name}`, Genesis9reglerzug.PAUSE_MS);
    }

    /** So lange wartet der genaue Zug auf ein Feld, das noch unterwegs ist. */
    static FELD_MS = 600;

    static async _genau(inst, voll) {
        await Genesis9reglerfeld.abwarten(inst, Genesis9reglerzug.FELD_MS);
        const plan = Genesis9groessehalten.an(inst) ? null : Genesis9sofortzug.plan(inst);
        if (!plan) return voll();
        Genesis9sofortzug.zeigen(inst);
        Genesis9sofortzug.werte(inst, plan.eintraege);
        if (Genesis9nachformen.geht(inst)) await Genesis9nachformen.stuecke(inst, plan.stuecke);
        else await Promise.all(plan.stuecke.map(kennung => inst.anziehen(kennung, inst.kleidung[kennung], null, false)));
        return inst;
    }

    /** Einen Schieber der Reglerliste kennenlernen (`Genesis9reglerzeile.bauen`). */
    static kennen(schieber, inst, regler) {
        Genesis9reglerzug._zeilen.set(schieber, { inst, regler });
        if (Genesis9reglerzug._verdrahtet) return;
        Genesis9reglerzug._verdrahtet = true;
        const mit = (ereignis, tun) => document.addEventListener(ereignis, e => {
            const zeile = Genesis9reglerzug._zeilen.get(e.target);
            if (zeile) tun(zeile);
        });
        mit('change', ({ inst: figur }) => Genesis9lauf.vorziehen(figur, Genesis9reglerzug.LOS_MS));
        mit('focusin', Genesis9reglerzug._vorab);
        mit('pointerover', zeile => {
            clearTimeout(Genesis9reglerzug._warten);
            Genesis9reglerzug._warten = setTimeout(() => Genesis9reglerzug._vorab(zeile), Genesis9reglerzug.VERWEIL_MS);
        });
        mit('pointerout', () => clearTimeout(Genesis9reglerzug._warten));
    }

    /** Das Feld des Reglers schon holen — beim Ziehen ist es dann da. */
    static _vorab({ inst, regler }) {
        if (Genesis9lauf.inSzene(inst)) Genesis9reglerfeld.vorab(inst, regler.name, { min: regler.paar ? 0 : regler.min, max: regler.max });
    }
}
