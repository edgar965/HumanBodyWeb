import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9hautebenen } from '../../gemeinsam/genesis9hautebenen.js';

/**
 * Genesis9hautebenenregler — der Bereich „Hautebenen" in den Eigenschaften einer Genesis-9-Figur (17.10.2026).
 *
 * Edgar, 17.10.2026: „wo sind die Regler Haut?" — Hautton, Rötung, Sommersprossen (und ihre Größe), Altersflecken, Muskel- und Fettzeichnung und graue Haare, je ein
 * Schieber in Prozent (`inst.hautebenen`, Felder und Hilfen in `Genesis9hautebenen.FELDER`). Kein Serverlauf beim Ziehen: die Werte sind Uniforms; erst der erste Gebrauch von
 * Punkten und Zeichnung holt die Karten (60–80 s Bau je Geschlecht beim allerersten Mal, danach aus der Ablage). Wie `genesis9texturmischung.js`.
 */
export class Genesis9hautebenenregler {

    static BEREICH = 'prop-genesis9-hautebenen';

    static fuellen(inst) {
        const behaelter = document.getElementById(Genesis9hautebenenregler.BEREICH);
        if (!behaelter) return;
        behaelter.innerHTML = '<div class="hb-font-size-0-72rem">Hautton, Sommersprossen, Altersflecken, Muskel- und Fettzeichnung und graue Haare. '
            + 'Altersflecken und graue Haare folgen dem Alter; der Regler hebt sie an.</div>';
        let gruppe = '';
        for (const feld of Genesis9hautebenen.FELDER) {
            if (feld.gruppe !== gruppe) {
                gruppe = feld.gruppe;
                const titel = document.createElement('div');
                titel.className = 'hb-font-size-0-72rem';
                titel.innerHTML = `<b>${escapeHtml(gruppe)}</b>`;
                behaelter.appendChild(titel);
            }
            behaelter.appendChild(Genesis9hautebenenregler._zeile(inst, feld));
        }
        const zurueck = document.createElement('button');
        zurueck.type = 'button';
        zurueck.className = 'btn btn-sm';
        zurueck.textContent = 'Alle Hautebenen zurücksetzen';
        zurueck.addEventListener('click', async () => {
            for (const feld of Genesis9hautebenen.FELDER) await inst.hautebenenSetzen(feld.name, null);
            markDirty();
            Genesis9hautebenenregler.fuellen(inst);
        });
        behaelter.appendChild(zurueck);
    }

    static _zeile(inst, feld) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `g9-hautebene-${feld.name}`;
        const wert = Genesis9hautebenen.wert(inst, feld.name);
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(feld.hilfe)}">${escapeHtml(feld.titel)}</label>
            <input type="range" id="${kennung}" data-hautebene="${feld.name}" min="${feld.min}" max="${feld.max}" step="1" value="${wert}">
            <span class="slider-value">${wert} %</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseInt(schieber.value, 10) || 0;
            anzeige.textContent = `${neu} %`;
            inst.hautebenenSetzen(feld.name, neu);
        });
        schieber.addEventListener('change', () => markDirty());
        schieber.addEventListener('dblclick', () => {
            schieber.value = Genesis9hautebenen.standard(feld.name);
            schieber.dispatchEvent(new Event('input'));
            markDirty();
        });
        return zeile;
    }
}
