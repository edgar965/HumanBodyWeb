import { fn } from '../gemeinsam/registrierung.js';
import { Reiterfreigabe } from './reiterfreigabe.js';
import { Reiterinhalt } from './reiterinhalt.js';

/**
 * Reiterstand — der offene Reiter und seine Rollstellung, über Undo und F5.
 *
 * Edgar (18.09.2026): „bei Undo ist der ganze Tab geschlossen … bei F5 wird
 * auch der ganze Tab geschlossen, es soll genau an der Stelle weitergemacht
 * werden wo ich gerade war". Beides hatte denselben Grund: Undo baut die
 * Szene aus dem Schnappschuss neu, F5 aus der Sitzung — dabei sind kurz
 * KEINE Figuren da, und `Reiterfreigabe` schaltet die Figur-Reiter auf
 * „Szene" zurück (`AUSWEICH`). Danach stand die Figur wieder, der Reiter
 * nicht.
 *
 * `merken()` liefert `{reiter, rollen}` (der aktive Reiter, `scrollTop` des
 * Reiterinhalts); `herstellen(stand)` schaltet zurück, sobald der Reiter frei
 * ist, und rollt, sobald sein Inhalt gebaut ist (`Reiterinhalt.bauen` gibt
 * das Versprechen des laufenden Baus). Über `fn.switchTab`, nicht per Klick:
 * `Figurmerker` und `Reitergedaechtnis` haben den Reiter schon.
 */
export class Reiterstand {

    /** Ob die Sitzung ihren Stand schon hergestellt hat (dann kein zweiter Wechsel). */
    static hergestellt = false;

    static merken() {
        const reiter = document.querySelector('.panel-tab.active')?.dataset.tab || null;
        const inhalt = document.querySelector('.panel-tab-content');
        return { reiter, rollen: inhalt ? inhalt.scrollTop : 0 };
    }

    static async herstellen(stand) {
        if (!stand?.reiter || !Reiterfreigabe.frei(stand.reiter)) return false;
        fn.switchTab?.(stand.reiter);
        Reiterstand.hergestellt = true;
        await Reiterinhalt.bauen(stand.reiter);
        // Kein `requestAnimationFrame`: in einem verdeckten Tab feuert es nie,
        // und ein Undo, das hier hinge, liesse `_undoInProgress` stehen —
        // danach nähme kein Reglerzug mehr einen Schnappschuss.
        // Der Inhalt waechst noch (die Regler kommen nach dem Reglerplan vom
        // Server): rollen, sobald er hoch genug ist — bis zu zwei Sekunden.
        for (let versuch = 0; stand.rollen && versuch < 8; versuch++) {
            await new Promise(resolve => setTimeout(resolve, versuch ? 250 : 0));
            const inhalt = document.querySelector('.panel-tab-content');
            if (!inhalt) break;
            if (inhalt.scrollHeight - inhalt.clientHeight >= stand.rollen) {
                inhalt.scrollTop = stand.rollen;
                break;
            }
        }
        return true;
    }
}
