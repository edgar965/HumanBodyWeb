import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { el, Abschnitt, Reglerzeile } from './bauteile.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Stoffabschnitt — der Bereich "Cloth - Template" des Bedienfelds: Schnitt
 * wählen, vier Regler, Farbe, und die Knöpfe Anlegen/Ändern/Löschen.
 *
 * Aus ui_panel.js herausgeloest (Umbau 16.08.2026). Die vier Knöpfe waren
 * viermal derselbe Block, die vier Regler viermal ein Aufruf mit anderen
 * Grenzen — beide jetzt als Tabelle. Die Umrechnung der Reglerwerte in
 * Serverwerte (Prozent → Bruch, Zentimeter → Meter) stand vorher in
 * `getTplParams()` als vier Zeilen mit Zahlen ohne Namen.
 */
export class Stoffabschnitt {

    /** Schnitt, wenn nichts gewählt ist. */
    static ERSATZ = 'TPL_TSHIRT';

    /** Regler: Name, Kennung, von, bis, Vorgabe, Schritt, Anzeigeform. */
    static REGLER = [
        ['Segments', 'rc-cloth-segments', 16, 64, 32, 2, wert => wert],
        ['Tightness', 'rc-cloth-tightness', 0, 100, 50, 1,
         wert => (wert / 100).toFixed(2)],
        ['Top', 'rc-cloth-top', -30, 30, 0, 1,
         wert => (wert / 100).toFixed(2) + ' m'],
        ['Bottom', 'rc-cloth-bot', -30, 50, 0, 1,
         wert => (wert / 100).toFixed(2) + ' m'],
    ];

    /** Reihenfolge der Regler in REGLER — als Namen für `werte()`. */
    static FELDER = ['segments', 'tightness', 'top_extend', 'bottom_extend'];

    constructor() {
        this.abschnitt = new Abschnitt('Cloth - Template', true);
        this.schnittwahl = null;
        this.regler = [];
    }

    bauen() {
        this.abschnitt.anhaengen(this._schnittzeile());
        for (const angabe of Stoffabschnitt.REGLER) {
            const zeile = new Reglerzeile(...angabe);
            this.regler.push(zeile);
            this.abschnitt.anhaengen(zeile.zeile);
        }
        this.abschnitt.anhaengen(this._farbzeile(), this._knopfzeile());
        this._schnitteLaden();
        return this.abschnitt.el;
    }

    _schnittzeile() {
        const zeile = el('div', 'rc-slider-row');
        const text = el('label', '');
        text.textContent = 'Template';
        this.schnittwahl = el('select', 'rc-select');
        this.schnittwahl.id = 'rc-cloth-tpl-type';
        zeile.append(text, this.schnittwahl);
        return zeile;
    }

    _farbzeile() {
        const zeile = el('div', 'rc-slider-row');
        const text = el('label', '');
        text.textContent = 'Color';
        const feld = document.createElement('input');
        Object.assign(feld, { type: 'color', value: '#404870',
                              id: 'rc-cloth-color' });
        feld.classList.add('rc-color-input');
        zeile.append(text, feld);
        return zeile;
    }

    /** Die vier Knöpfe — vorher vier gleich gebaute Blöcke. */
    _knopfzeile() {
        const zeile = el('div', 'rc-btn-row');
        const knoepfe = [
            ['rc-btn', 'fa-plus', ' Create', () => this.anlegen()],
            ['rc-btn', 'fa-sync-alt', ' Update', () => this.aendern()],
            ['rc-btn rc-btn-danger', 'fa-times', '', () => this.loeschen()],
            ['rc-btn rc-btn-danger', 'fa-trash', '', () => fn.removeAllCloth()],
        ];
        for (const [klasse, symbol, text, tun] of knoepfe) {
            const knopf = el('button', klasse);
            knopf.innerHTML = `<i class="fas ${symbol}"></i>${text}`;
            knopf.addEventListener('click', tun);
            zeile.appendChild(knopf);
        }
        return zeile;
    }

    // ------------------------------------------------------------------- Wirken

    schnitt() {
        return this.schnittwahl.value || Stoffabschnitt.ERSATZ;
    }

    /** Reglerstände als Serverwerte. */
    werte() {
        const werte = { method: 'template', template: this.schnitt() };
        this.regler.forEach((zeile, i) => {
            const feld = Stoffabschnitt.FELDER[i];
            // Segmente sind eine Anzahl, die anderen drei stehen in Prozent
            // bzw. Zentimetern und gehen als Bruch bzw. Meter zum Server.
            werte[feld] = feld === 'segments' ? zeile.zahl() : zeile.zahl() / 100;
        });
        return werte;
    }

    anlegen() {
        const werte = this.werte();
        fn.loadCloth(`tpl_${werte.template}`, werte);
    }

    /** Ändern wirkt nur auf ein Stück, das schon an der Figur ist. */
    aendern() {
        const werte = this.werte();
        const schluessel = `tpl_${werte.template}`;
        if (state.clothMeshes[schluessel]) fn.loadCloth(schluessel, werte);
    }

    loeschen() {
        fn.removeClothRegion(`tpl_${this.schnitt()}`);
    }

    async _schnitteLaden() {
        try {
            const daten = await Serverabruf.json('/api/character/cloth/regions/');
            for (const schnitt of daten.templates || []) {
                this.schnittwahl.appendChild(
                    new Option(schnitt.label, schnitt.key));
            }
        } catch (fehler) {
            Protokoll.warnung('result_character', 'Schnitte nicht ladbar:', fehler);
        }
    }
}
