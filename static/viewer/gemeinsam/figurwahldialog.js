import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Figurkataloge } from './figurkataloge.js';
import { Figurwahlzeile } from './figurwahlzeile.js';
import { Figurlagefelder } from './figurlagefelder.js';

/**
 * Figurwahldialog — „Charakter hinzufügen", ein Reiter je Figurart, mit Lage.
 *
 * ANLASS (Edgar, 11.09.2026, Theatre): „Datei - Modell laden funktioniert
 * nicht, das soll so funktionieren wie bei /humanbody/scene/, mit dem
 * gleichen Popup. Mach das Popup wiederverwendbar, eigene Klasse, html bzw.
 * ES Modul, wo auch die Position festgelegt ist (default so wie in anderer
 * View)."
 *
 * Der Dialog der Szene-Seite (`_charakter_dialog.html` + `scene/charakterdialog.js`)
 * war an sie gebunden: Vorlage im Template, Listen über `state`, Laden über
 * die Registrierung. Dieser hier baut sein HTML selbst, holt die Listen über
 * `Figurkataloge` und kennt die Bühne nicht — wer ihn öffnet, gibt je Reiter
 * einen `lader(name, lage)` mit. Stil: `static/css/figurwahldialog.css`.
 *
 * DIE LAGE DER NEUEN FIGUR ist Teil des Dialogs, wie in der Szene: Position X
 * und „Größe der vorhandenen Figur angleichen" (`figurlagefelder.js`). Die
 * Vorgabe liefert der Aufrufer über `vorgaben()`; ohne Angabe gilt die der
 * Szene-Seite — `ABSTAND_M` rechts neben der vorhandenen Figur, angeglichen.
 *
 * Was je Reiter anders ist, steht in `Figurkataloge.QUELLEN` (Liste,
 * Leertext, Pflege) und im `lader` des Aufrufers. Der Rest kennt die
 * Figurarten nicht.
 *
 * ZWEITE AUFGABE (11.09.2026, „Modell austauschen"): derselbe Dialog ohne
 * Lage-Felder (`lage: false`), mit eigener `kennung` — zwei Dialoge auf einer
 * Seite dürfen keine gleichen IDs tragen — und eigenem Knopftext.
 */
export class Figurwahldialog {

    /** Vorgabe der Szene-Seite: 1,5 m rechts neben der vorhandenen Figur. */
    static ABSTAND_M = Figurlagefelder.ABSTAND_M;

    static ID = 'figurwahl-dialog';

    /**
     * @param {Object} einstellungen
     *   lader     {quelle: async (name, lage) => …}  — Pflicht je Reiter
     *   quellen   Reiter in dieser Reihenfolge; Vorgabe: alle mit Lader
     *   vorgaben  () => ({x, angleichen, vorbildHoehe}); Vorgabe siehe oben
     *   pflege    {umbenennen(quelle, name), loeschen(quelle, name)} oder null
     *   titel     Überschrift
     *   knopf     Text des Bestätigen-Knopfs
     *   symbol    Font-Awesome-Klasse im Kopf
     *   lage      false = ohne Lage-Felder; `lage()` liefert dann `vorgaben()`
     *   angleichen false = Position X ohne das Kästchen „Größe angleichen"
     *   kennung   Präfix aller IDs (zwei Dialoge je Seite brauchen zwei)
     */
    constructor({ lader, quellen = null, vorgaben = null, pflege = null,
                  titel = 'Charakter hinzufügen', knopf = 'Hinzufügen',
                  symbol = 'fa-user-plus', lage = true, angleichen = true,
                  kennung = Figurwahldialog.ID } = {}) {
        this.lader = lader || {};
        this.quellen = (quellen || Figurkataloge.REIHENFOLGE)
            .filter(q => Figurkataloge.QUELLEN[q] && this.lader[q]);
        this.vorgaben = vorgaben || Figurwahldialog.vorgabeLage;
        this.pflege = pflege;
        this.titel = titel;
        this.knopf = knopf;
        this.symbol = symbol;
        this.kennung = kennung;
        this.lagefelder = lage
            ? new Figurlagefelder(kennung, this.vorgaben, { angleichen }) : null;
        this.quelle = this.quellen[0] || null;
        this.gewaehlt = null;
        this.element = null;
    }

    /** Die Vorgabe, wenn der Aufrufer keine liefert. */
    static vorgabeLage() {
        return Figurlagefelder.vorgabe();
    }

    // -- Öffnen und Schließen -------------------------------------------------

    async oeffnen() {
        const dialog = this._element();
        dialog.classList.add('visible');
        this._waehlen(null);
        this.lagefelder?.vorbelegen();
        this._umschalten(this.quelle);
        await Promise.all(this.quellen.map(q => this._fuellen(q)));
    }

    schliessen() {
        this.element?.classList.remove('visible');
    }

    /** Die Lage, wie sie jetzt im Dialog steht — ohne Felder die Vorgabe. */
    lage() {
        return this.lagefelder ? this.lagefelder.lage() : this.vorgaben();
    }

    // -- Aufbau ---------------------------------------------------------------

    _element() {
        if (this.element) return this.element;
        const overlay = document.createElement('div');
        overlay.className = 'scene-modal-overlay figurwahl-dialog';
        overlay.id = this.kennung;
        overlay.innerHTML = this._html();
        document.body.appendChild(overlay);
        this.element = overlay;
        this.lagefelder?.anbinden(overlay);
        this._verdrahten();
        return overlay;
    }

    _html() {
        const reiter = this.quellen.map((q, i) =>
            `<button class="dialogreiter-knopf${i === 0 ? ' active' : ''}" `
            + `data-quelle="${q}">${Htmltext.t(Figurkataloge.QUELLEN[q].titel)}</button>`).join('');
        const listen = this.quellen.map((q, i) =>
            `<ul class="preset-list${i === 0 ? '' : ' hb-versteckt'}" `
            + `id="${this.kennung}-liste-${q}" data-quelle="${q}"></ul>`).join('');
        const k = this.kennung;
        return `
    <div class="scene-modal">
        <div class="scene-modal-header">
            <h4><i class="fas ${this.symbol}"></i> ${Htmltext.t(this.titel)}</h4>
            <button class="scene-modal-close" data-close>&times;</button>
        </div>
        <div class="scene-modal-body">
            <div class="dialogreiter" id="${k}-reiter">${reiter}</div>
            ${listen}
            ${this.lagefelder ? this.lagefelder.html() : ''}
        </div>
        <div class="scene-modal-footer">
            <span class="dialoghinweis" id="${k}-hinweis">Erst einen Eintrag wählen</span>
            <button data-close>Abbrechen</button>
            <button class="primary" id="${k}-bestaetigen" disabled
                    title="Erst einen Eintrag in der Liste wählen">${Htmltext.t(this.knopf)}</button>
        </div>
    </div>`;
    }

    _verdrahten() {
        const dialog = this.element;
        for (const knopf of dialog.querySelectorAll('[data-close]')) {
            knopf.addEventListener('click', () => this.schliessen());
        }
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) this.schliessen();
        });
        for (const knopf of this._reiterknoepfe()) {
            knopf.addEventListener('click', () => this._umschalten(knopf.dataset.quelle));
        }
        this._feld('bestaetigen')?.addEventListener('click', async () => {
            if (!this.gewaehlt) return;
            this.schliessen();
            await this._laden(this.gewaehlt);
        });
    }

    _feld(name) {
        return this.element?.querySelector(`#${this.kennung}-${name}`) || null;
    }

    _liste(quelle) {
        return this.element?.querySelector(`#${this.kennung}-liste-${quelle}`) || null;
    }

    _reiterknoepfe() {
        return this.element?.querySelectorAll(`#${this.kennung}-reiter .dialogreiter-knopf`) || [];
    }

    // -- Reiter und Wahl ------------------------------------------------------

    _umschalten(quelle) {
        this.quelle = quelle;
        for (const knopf of this._reiterknoepfe()) {
            knopf.classList.toggle('active', knopf.dataset.quelle === quelle);
        }
        for (const q of this.quellen) {
            this._liste(q)?.classList.toggle('hb-versteckt', q !== quelle);
        }
        // Die Wahl gehört zum Reiter: wer umschaltet, wählt neu.
        this._waehlen(null);
        this._einzelnenVorwaehlen(quelle);
    }

    /**
     * Hat der Reiter genau EINEN Eintrag, ist er gewählt (07.09.2026: Der
     * MakeHuman-Reiter zeigt eine einzige Zeile; sie sah aus wie eine
     * Überschrift, und „Hinzufügen" blieb gesperrt). Bei mehreren wird
     * NICHT vorgewählt — dort ist die Wahl eine Entscheidung.
     */
    _einzelnenVorwaehlen(quelle) {
        const zeilen = this._liste(quelle)?.querySelectorAll('li[data-name]') || [];
        if (zeilen.length !== 1) return;
        this._waehlen({ quelle, name: zeilen[0].dataset.name });
    }

    _waehlen(eintrag) {
        this.gewaehlt = eintrag;
        const knopf = this._feld('bestaetigen');
        if (knopf) knopf.disabled = !eintrag;
        this._feld('hinweis')?.classList.toggle('hb-versteckt', Boolean(eintrag));
        for (const liste of this.element.querySelectorAll('.preset-list')) {
            for (const li of liste.querySelectorAll('li')) {
                li.classList.toggle('selected',
                    Boolean(eintrag) && li.dataset.name === eintrag.name
                    && liste.dataset.quelle === eintrag.quelle);
            }
        }
    }

    // -- Listen ---------------------------------------------------------------

    async _fuellen(quelle) {
        const liste = this._liste(quelle);
        if (!liste) return;
        liste.innerHTML = '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade …</li>';
        let eintraege;
        try {
            eintraege = await Figurkataloge.liste(quelle);
        } catch (fehler) {
            liste.innerHTML = `<li class="fehlertext">Fehler: ${Htmltext.t(fehler.message)}</li>`;
            return;
        }
        liste.innerHTML = '';
        if (!eintraege.length) {
            liste.innerHTML = `<li class="gedaempft">${Htmltext.t(Figurkataloge.QUELLEN[quelle].leer)}</li>`;
            return;
        }
        for (const eintrag of eintraege) {
            liste.appendChild(this._zeile(eintrag, quelle));
        }
        // Die Listen kommen nebenläufig; vorwählen nur im offenen Reiter.
        if (quelle === this.quelle && !this.gewaehlt) this._einzelnenVorwaehlen(quelle);
    }

    _zeile(eintrag, quelle) {
        const pflege = Boolean(this.pflege) && Figurkataloge.QUELLEN[quelle].pflege;
        return Figurwahlzeile.bauen(eintrag, {
            waehlen: () => this._waehlen({ quelle, name: eintrag.name }),
            laden: async () => {
                this.schliessen();
                await this._laden({ quelle, name: eintrag.name });
            },
            pflegen: pflege ? (was) => this._pflegen(quelle, eintrag.name, was) : null,
        });
    }

    // -- Umbenennen, Löschen, Laden -------------------------------------------

    async _pflegen(quelle, name, was) {
        try {
            const geschehen = await this.pflege[was](quelle, name);
            if (!geschehen) return;
            this._waehlen(null);
            await this._fuellen(quelle);
        } catch (fehler) {
            window.alert(`Fehler: ${fehler.message}`);
        }
    }

    async _laden({ quelle, name }) {
        const lage = this.lage();
        try {
            return await this.lader[quelle](name, lage);
        } catch (fehler) {
            window.alert(`Fehler: ${fehler.message}`);
            return null;
        }
    }
}
