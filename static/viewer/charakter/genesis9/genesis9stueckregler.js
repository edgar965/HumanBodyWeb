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

    /** Bis zu so vielen Gruppen stehen sie beim Öffnen AUF — darüber alle zu.
     *  „Haar – Generisch" bringt eine Gruppe je Frisur mit (18 Gruppen, über 400 Regler);
     *  alle offen wäre eine Liste, durch die niemand scrollt. Ein gewöhnliches Stück hat
     *  ein bis drei Gruppen und soll sich nicht schlechter bedienen als vorher. */
    static OFFEN_BIS = 3;

    /** Welche Gruppen dieser Browser offen gelassen hat — Muster wie
     *  `Genesis9garderobekategorien.SCHLUESSEL`, aber ein EIGENER Schlüssel: Die Namen
     *  überschneiden sich (mehrere Stücke haben eine Gruppe „Adjustment"), deshalb steht
     *  je Eintrag `<stück>/<gruppe>`. */
    static SCHLUESSEL = 'hb_g9_stueckregler_offen';

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
            const ziel = gruppen.size > 1
                ? Genesis9stueckregler._gruppe(kasten, gruppe, regler.length, gruppen.size, stueck.id)
                : kasten;
            for (const r of regler) ziel.appendChild(Genesis9stueckregler._zeile(inst, stueck, r, werteLesen));
        }
        return kasten;
    }

    /** Eine Gruppe als eigener Klappkasten (Edgar, 30.09.2026: „in Kategorien der jeweiligen
     *  Hauptsorte … und aufklappbar"). Kopf wie die Kategorien der Garderobe. */
    static _gruppe(kasten, gruppe, anzahl, gruppenzahl, stueckId) {
        const eigen = document.createElement('details');
        const merkname = `${stueckId}/${gruppe}`;
        eigen.className = 'g9-kategorie genesis9-reglergruppe';
        eigen.open = Genesis9stueckregler._gemerkt().includes(merkname)
            || gruppenzahl <= Genesis9stueckregler.OFFEN_BIS;
        eigen.innerHTML = `<summary class="aufklappkopf">${escapeHtml(gruppe)} `
            + `<span class="gedaempft">(${anzahl})</span></summary>`;
        eigen.addEventListener('toggle', () => Genesis9stueckregler._merken(merkname, eigen.open));
        kasten.appendChild(eigen);
        return eigen;
    }

    /** Die gemerkten offenen Gruppen. Leer, wenn nie etwas gemerkt wurde oder der Browser
     *  keine Seitendaten zulässt (privates Fenster). */
    static _gemerkt() {
        try {
            const roh = JSON.parse(localStorage.getItem(Genesis9stueckregler.SCHLUESSEL));
            return Array.isArray(roh) ? roh : [];
        } catch (fehler) {
            return [];
        }
    }

    static _merken(name, offen) {
        const alle = new Set(Genesis9stueckregler._gemerkt());
        if (offen) alle.add(name); else alle.delete(name);
        try {
            localStorage.setItem(Genesis9stueckregler.SCHLUESSEL, JSON.stringify([...alle]));
        } catch (fehler) {
            // privates Fenster, gesperrte Seitendaten — dann eben nicht gemerkt
        }
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
