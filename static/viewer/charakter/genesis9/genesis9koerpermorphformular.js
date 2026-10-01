import { escapeHtml } from '../utils.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9morphformular } from './genesis9morphformular.js';

/**
 * Genesis9koerpermorphformular — das freie Morph-Formular im Bereich „Nachformung (Ort)" des Körper-Reiters
 * (01.10.2026). Dieselben Felder wie am Stück (`Genesis9morphformular.rumpf`), dazu „spiegeln" (links = rechts);
 * `POST genesis9-figur/morph/` baut den Eigenmorph `eigen:ort_<name>` (`G9koerpermorph.bauen`), die Antwort nennt den
 * Regler — er wird als Zeile in den Bereich gehängt und auf 1 gestellt (`inst.reglerSetzen`, ein Lauf wie jeder
 * Reglerzug). Der Reglerplan des Servers kennt ihn beim nächsten Laden über `G9eigenmorphe.liste()`.
 */
export class Genesis9koerpermorphformular {

    static ADRESSE = '/api/character/genesis9-figur/morph/';
    static BEREICH = 'ort';

    static anhaengen(kasten, bereich, inst, zeileBauen) {
        if (bereich.schluessel !== Genesis9koerpermorphformular.BEREICH) return;
        const formular = document.createElement('details');
        formular.className = 'g9-kategorie genesis9-morphformular';
        formular.open = false;
        formular.innerHTML = `<summary class="aufklappkopf">Neuer Körpermorph … <span class="gedaempft">(Ort, Richtung, Weg)</span></summary>`;
        const felder = document.createElement('div');
        felder.className = 'genesis9-morphfelder';
        felder.innerHTML = Genesis9morphformular._html({}) + `
            <div class="slider-row"><label>Spiegeln (links = rechts)</label>
                <input type="checkbox" data-feld="spiegeln" checked></div>`;
        formular.appendChild(felder);
        Genesis9morphformular._landmarkenFuellen(felder);
        felder.querySelector('[data-tat="bauen"]').addEventListener('click', async () => {
            await Genesis9koerpermorphformular._bauen(inst, felder, kasten, bereich, zeileBauen);
        });
        kasten.appendChild(formular);
    }

    static async _bauen(inst, felder, kasten, bereich, zeileBauen) {
        const meldung = felder.querySelector('.genesis9-morphmeldung');
        const knopf = felder.querySelector('[data-tat="bauen"]');
        const rumpf = Genesis9morphformular.rumpf(felder);
        rumpf.spiegeln = felder.querySelector('[data-feld="spiegeln"]').checked;
        if (!rumpf.name) { meldung.textContent = 'Name fehlt'; return; }
        if (!Object.keys(rumpf.ort).length) { meldung.textContent = 'Einen Ort wählen (Landmarke, Band, Sektor)'; return; }
        knopf.disabled = true;
        meldung.textContent = 'Baut …';
        try {
            const antwort = await Serverabruf.senden(Genesis9koerpermorphformular.ADRESSE, rumpf);
            if (antwort.fehler) throw new Error(antwort.fehler);
            const regler = antwort.regler;
            meldung.textContent = `${antwort.brief?.bewegt ?? antwort.brief?.punkte ?? '?'} Punkte, bis ${antwort.brief?.weg_max_mm ?? antwort.brief?.max_mm ?? '?'} mm`;
            if (!bereich.regler.some(r => r.name === regler.name)) bereich.regler.push(regler);
            const zeile = zeileBauen(regler);
            kasten.insertBefore(zeile, kasten.querySelector('details.genesis9-morphformular'));
            const zaehler = kasten.querySelector(':scope > summary .gedaempft');
            if (zaehler) zaehler.textContent = `(${bereich.regler.length})`;
            const schieber = zeile.querySelector('input[type="range"]');
            if (schieber) { schieber.value = '1'; zeile.querySelector('.slider-value').textContent = '100 %'; }
            Genesis9lauf.planen(inst, () => inst.reglerSetzen(regler.name, 1), () => {}, `regler:${regler.name}`);
        } catch (fehler) {
            meldung.textContent = `Fehler: ${escapeHtml(fehler.daten?.fehler || fehler.message)}`;
        } finally {
            knopf.disabled = false;
        }
    }
}
