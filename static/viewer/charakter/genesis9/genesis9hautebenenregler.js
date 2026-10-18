import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9hautebenen } from '../../gemeinsam/genesis9hautebenen.js';
import { Genesis9hautebenenwerte } from '../../gemeinsam/genesis9hautebenenwerte.js';

/**
 * Genesis9hautebenenregler — der Bereich „Hautebenen" in den Eigenschaften einer Genesis-9-Figur (17.10.2026) und dieselben Schieber im Popup hinter dem Zahnrad der Haut
 * (`Genesis9hautdialogblock`, 18.10.2026).
 *
 * Edgar, 17.10.2026: „wo sind die Regler Haut?" — je ein Schieber in Prozent (`inst.hautebenen`, Felder und Hilfen in `Genesis9hautebenenwerte.FELDER`, seit 18.10.2026 nach Gruppen
 * aufklappbar). Kein Serverlauf beim Ziehen: die Werte sind Uniforms; erst der erste Gebrauch von Punkten und Zeichnung holt die Karten (60–80 s Bau je Geschlecht beim allerersten Mal,
 * danach aus der Ablage). Steht derselbe Schieber zweimal auf der Seite (Bedienfeld und Popup), zieht der eine den anderen nach (`data-hautebene`).
 */
export class Genesis9hautebenenregler {

    static BEREICH = 'prop-genesis9-hautebenen';

    static fuellen(inst) {
        const behaelter = document.getElementById(Genesis9hautebenenregler.BEREICH);
        if (!behaelter) return;
        behaelter.innerHTML = '<div class="hb-font-size-0-72rem">Farbe, Flecken, Relief der Haut und graue Haare — dieselben Schieber (ohne graue Haare) stehen auch im Zahnrad neben „Haut". '
            + 'Altersflecken, Altersfalten und graue Haare folgen dem Alter; der Regler hebt sie an.</div>';
        behaelter.appendChild(Genesis9hautebenenregler.gruppen(inst, { praefix: 'g9-hautebene-' }));
        const zurueck = document.createElement('button');
        zurueck.type = 'button';
        zurueck.className = 'btn btn-sm';
        zurueck.textContent = 'Alle Hautebenen zurücksetzen';
        zurueck.addEventListener('click', async () => {
            await Genesis9hautebenen.alleSetzen(inst, Object.fromEntries(Genesis9hautebenen.FELDER.map(f => [f.name, null])));
            markDirty();
            Genesis9hautebenenregler.nachziehen(inst);
        });
        behaelter.appendChild(zurueck);
    }

    /**
     * Die Schieber nach Gruppen, je Gruppe ein aufklappbarer Block (offen). `nurHaut`: ohne die Gruppe „Haar" (Popup der Haut); `praefix` macht die Kennungen eindeutig.
     */
    static gruppen(inst, { nurHaut = false, praefix = 'g9-hautebene-' } = {}) {
        const aussen = document.createDocumentFragment();
        for (const gruppe of Genesis9hautebenenwerte.GRUPPEN) {
            if (nurHaut && !gruppe.haut) continue;
            const felder = Genesis9hautebenen.FELDER.filter(f => f.gruppe === gruppe.name);
            if (!felder.length) continue;
            const block = document.createElement('details');
            block.className = 'uma-gruppe hb-hautebenengruppe';
            block.open = true;
            block.innerHTML = `<summary>${escapeHtml(gruppe.name)}</summary>`;
            for (const feld of felder) block.appendChild(Genesis9hautebenenregler.zeile(inst, feld, praefix));
            aussen.appendChild(block);
        }
        return aussen;
    }

    static zeile(inst, feld, praefix = 'g9-hautebene-') {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `${praefix}${feld.name}`;
        const wert = Genesis9hautebenen.wert(inst, feld.name);
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(feld.hilfe)}">${escapeHtml(feld.titel)}</label>
            <input type="range" id="${kennung}" data-hautebene="${feld.name}" min="${feld.min}" max="${feld.max}" step="1" value="${wert}"
                   title="${escapeHtml(feld.hilfe)} · Doppelklick: Standard">
            <span class="slider-value">${wert} %</span>`;
        const schieber = zeile.querySelector('input');
        schieber.addEventListener('input', () => {
            const neu = parseInt(schieber.value, 10) || 0;
            Genesis9hautebenenregler._zeigen(feld.name, neu);
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

    /** Alle Schieber dieses Felds auf der Seite (Bedienfeld und Popup) auf den Wert stellen. */
    static _zeigen(name, wert) {
        for (const schieber of document.querySelectorAll(`input[data-hautebene="${name}"]`)) {
            if (String(schieber.value) !== String(wert)) schieber.value = wert;
            const anzeige = schieber.parentElement?.querySelector('.slider-value');
            if (anzeige) anzeige.textContent = `${wert} %`;
        }
    }

    /** Alle Schieber auf der Seite auf den Stand der Figur (nach Zurücksetzen oder dem Auflegen einer gespeicherten Haut). */
    static nachziehen(inst) {
        for (const feld of Genesis9hautebenen.FELDER) Genesis9hautebenenregler._zeigen(feld.name, Genesis9hautebenen.wert(inst, feld.name));
    }
}
