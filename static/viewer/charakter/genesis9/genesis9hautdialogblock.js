import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9hautebenen } from '../../gemeinsam/genesis9hautebenen.js';
import { Genesis9hautebenenwerte } from '../../gemeinsam/genesis9hautebenenwerte.js';
import { Genesis9eigenehaut } from '../../gemeinsam/genesis9eigenehaut.js';
import { Genesis9hautebenenregler } from './genesis9hautebenenregler.js';

/**
 * Genesis9hautdialogblock — im Popup hinter dem Zahnrad der Haut (`Genesis9materialdialog`) unter Glanz, Rauheit und Relief: alle Schieber der Hautebenen (Farbe und Teint,
 * Flecken, Relief — ohne graue Haare) und „Als eigene Haut speichern" (18.10.2026).
 *
 * Edgar, 18.10.2026: „neue Regler, damit ich sowas wie Sommersprossen, Falten, Farbfehler, Farbton usw. erstellen kann? Möglichst viele Regler … Auch Button zum speichern der Neuen
 * Haut, mit hautnamen, die soll dann auch in die Haut Combo box erscheinen" — dann: „bei den einstellungen der Haut sollen diese Regler kommen, darin auch Button zum speichern der neuen
 * Haut". Die Schieber sind dieselben wie im Bereich „Hautebenen" des Bedienfelds (`Genesis9hautebenenregler`), gespeichert wird über `Genesis9eigenehaut`.
 */
export class Genesis9hautdialogblock {

    /** Der Block; `nachSpeichern` baut die Hautauswahl neu (die neue Haut steht dann darin und ist gewählt). */
    static block(inst, plan, nachSpeichern) {
        const block = document.createElement('div');
        block.className = 'hb-hautdialogblock';
        block.innerHTML = '<div class="hb-formkopf">Haut gestalten</div>'
            + '<div class="hb-font-size-0-72rem">Wirkt sofort im Shader, ohne Neubau. Doppelklick auf einen Schieber: Standard. Der Hilfetext steht am Namen.</div>';
        block.appendChild(Genesis9hautebenenregler.gruppen(inst, { nurHaut: true, praefix: 'g9d-hautebene-' }));
        block.appendChild(Genesis9hautdialogblock._speichern(inst, plan, nachSpeichern));
        return block;
    }

    /** Steht irgendeine Hautebene der Haut nicht auf Standard? */
    static hatEigene(inst) {
        return Genesis9hautebenenwerte.hautfelder().some(f => f.name in (inst.hautebenen || {}));
    }

    /** Alle Hautebenen der Haut auf Standard (graue Haare bleiben). */
    static async zuruecksetzen(inst) {
        await Genesis9hautebenen.alleSetzen(inst, Object.fromEntries(Genesis9hautebenenwerte.hautfelder().map(f => [f.name, null])));
        Genesis9hautebenenregler.nachziehen(inst);
    }

    static _speichern(inst, plan, nachSpeichern) {
        const teil = document.createElement('div');
        teil.className = 'hb-hautspeichern';
        teil.innerHTML = `
            <div class="hb-formkopf">Als eigene Haut speichern</div>
            <div class="hb-font-size-0-72rem">Gespeichert werden die gewählte Haut als Grundlage, alle Schieber dieses Fensters und die Texturmischung. Die Haut erscheint danach
                in der Auswahl „Haut" als „Eigene Haut · Name".</div>
            <div class="hb-hautspeichern-zeile">
                <input type="text" maxlength="60" placeholder="Name der Haut" aria-label="Name der Haut" value="${escapeHtml(Genesis9eigenehaut.name(inst, plan))}">
                <button type="button" class="primary">Haut speichern</button>
            </div>
            <div class="hb-hautspeichern-stand" role="status"></div>`;
        const feld = teil.querySelector('input');
        const knopf = teil.querySelector('button');
        const stand = teil.querySelector('.hb-hautspeichern-stand');
        const melden = (text, fehler = false) => {
            stand.textContent = text;
            stand.classList.toggle('fehler', fehler);
        };
        const los = async () => {
            const name = feld.value.trim();
            if (!name) {
                melden('Bitte einen Namen für die Haut eingeben.', true);
                feld.focus();
                return;
            }
            if (Genesis9eigenehaut.vorhanden(plan, name) && !window.confirm(`Eine eigene Haut „${name}" gibt es schon. Überschreiben?`)) return;
            knopf.disabled = true;
            melden('Speichere …');
            try {
                const { eintrag, ueberschrieben } = await Genesis9eigenehaut.speichern(inst, plan, name);
                markDirty();
                nachSpeichern?.();
                melden(`${ueberschrieben ? 'Überschrieben' : 'Gespeichert'}: „${eintrag.rezept?.name || name}" — steht jetzt in der Auswahl „Haut" und ist gewählt.`);
            } catch (fehler) {
                melden(fehler.message, true);
            } finally {
                knopf.disabled = false;
            }
        };
        knopf.addEventListener('click', los);
        feld.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                los();
            }
        });
        return teil;
    }
}
