import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Dazkleidung } from './dazkleidung.js';

/**
 * Genesis9stueckregler — die Anpassungsregler EINES Daz-Kleidungsstücks.
 *
 * Edgar, 18.09.2026: „es fehlen die Einstellungen für die Kleider". Jedes
 * Stück bringt eigene Morphkanäle mit (`Genesis9/anhangmorphe.py`: Viking-
 * Shirt *Adj Inflate Collar*, Worker-Overall *Loosen Back Upper*, Eirgrid
 * *Adjust Hairline*, Mavick *Wind*); der Server nennt sie in der Garderoben-
 * liste (`regler`, gruppiert nach Daz' Gruppe). Sie stehen aufklappbar unter
 * der Zeile des Stücks und wirken nur, wenn es angezogen ist — die Werte
 * liegen in `inst.kleidung[kennung].regler` und werden mitgespeichert.
 */
export class Genesis9stueckregler {

    static bauen(inst, stueck, werteLesen) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe genesis9-stueckregler';
        kasten.innerHTML = `<summary class="gedaempft">Einstellungen `
            + `<span class="gedaempft">(${stueck.regler.length})</span></summary>`;
        const gruppen = new Map();
        for (const r of stueck.regler) {
            if (!gruppen.has(r.gruppe)) gruppen.set(r.gruppe, []);
            gruppen.get(r.gruppe).push(r);
        }
        for (const [gruppe, regler] of gruppen) {
            if (gruppen.size > 1) {
                const kopf = document.createElement('div');
                kopf.className = 'gedaempft hb-font-size-0-72rem';
                kopf.textContent = gruppe;
                kasten.appendChild(kopf);
            }
            for (const r of regler) kasten.appendChild(Genesis9stueckregler._zeile(inst, stueck, r, werteLesen));
        }
        return kasten;
    }

    static _zeile(inst, stueck, regler, werteLesen) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const wert = Dazkleidung.kleidung(inst)[stueck.id]?.regler?.[regler.name] ?? regler.vorgabe ?? 0;
        zeile.innerHTML = `
            <label title="${escapeHtml(regler.name)}">${escapeHtml(regler.anzeige)}</label>
            <input type="range" min="${regler.min}" max="${regler.max}" step="${regler.schritt || 0.01}" value="${wert}">
            <span class="slider-value">${Genesis9stueckregler.text(wert, regler)}</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseFloat(schieber.value); anzeige.textContent = Genesis9stueckregler.text(neu, regler);
            const getragen = Dazkleidung.kleidung(inst)[stueck.id];
            if (!getragen) return;                       // nicht angezogen: nur merken
            const werte = werteLesen(); werte.regler = { ...(getragen.regler || {}) };
            if (Math.abs(neu) < 1e-6) delete werte.regler[regler.name];
            else werte.regler[regler.name] = neu;
            Genesis9lauf.planen(inst, () => Dazkleidung.anziehenAuf(inst, stueck.id, werte), () => {});
            markDirty();
        });
        return zeile;
    }

    /** Daz-Regler in Prozent; Passform-Regler (`einheit: cm`, `Genesis9/passform.py`) in Zentimetern. */
    static text(wert, regler = null) {
        if (regler?.einheit === 'cm') return `${(Math.round(wert * 10) / 10).toFixed(1)} cm`;
        return `${Math.round(wert * 100)} %`;
    }
}
