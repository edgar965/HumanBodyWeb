import { dbTabelle, esc } from '/static/djangobase/js/tabelle_bauen.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';

/**
 * Exportleistelaeufe — die Render-Läufe der Exportleiste als djangoBase-Tabelle, neueste zuerst (31.10.2026; Server `Engine2d3dKleiderrenderlaeufe`, dieselben Einträge wie bei
 * „2D3D Kleider"). Je Lauf: Nummer, Bilder und Länge, Größe und Proben, Dauer, Zeit, das Video, die Anmerkung. Neu gebaut wird nur, wenn sich die Läufe ändern.
 *
 * Seit 31.10.2026 abends ohne den Bogen aus vier Bildern (Edgar: „bei den Render jobs brauche ich keine Bilder. Mach diese jobs als djangoBase tabelle, mit Löschen button und
 * batch löschen"): Kästchen je Zeile mit Shift-Bereich und Kopfkästchen (`Zeilenwahl`, wie die Auftragstabelle), „Löschen" je Zeile und „Auswahl löschen (n)" über der Tabelle.
 *
 * „Neu rendern" je Zeile und „Alle neu rendern" (übernommen von 2D3D Kleider, Edgar 04.10.2026: „Buttons, um einen oder alle Render Jobs neu zu generieren"): der Lauf mit seinen
 * eigenen Einstellungen und dem Modell von heute, das Ergebnis ersetzt seine Zeile (`Exportleisterender.neu`). Ein Zuhörer für alle Knöpfe (`data-aktion`).
 */
export class Exportleistelaeufe {

    static SCHLUESSEL = 'exportleiste-laeufe';

    /**
     * @param neuRendern `async (nummern | 'alle') => …` — vom Render-Block (`Exportleisterender.neu`)
     * @param loeschen `async (nummern) => bool` — vom Render-Block (`Exportleisterender.loeschen`)
     */
    constructor(feld, adresse, neuRendern, loeschen) {
        this.feld = feld;
        this.adresse = adresse;
        this.neuRendern = neuRendern;
        this.loeschen = loeschen;
        this._stand = '';
        this._gesperrt = false;
        this.wahl = null;
        this.feld.addEventListener('click', ereignis => this._klick(ereignis));
    }

    _klick(ereignis) {
        const knopf = ereignis.target.closest('[data-aktion]');
        if (!knopf || knopf.disabled) return;
        const aktion = knopf.dataset.aktion;
        if (aktion === 'neu') this.neuRendern(knopf.dataset.nr === 'alle' ? 'alle' : [Number(knopf.dataset.nr)]);
        else if (aktion === 'loeschen') this._loeschen([Number(knopf.dataset.nr)], `Lauf #${knopf.dataset.nr} samt Video löschen?`);
        else if (aktion === 'auswahl') {
            const nummern = (this.wahl?.kennungen() || []).map(Number);
            if (nummern.length) this._loeschen(nummern, `${nummern.length} Lauf/Läufe samt Video löschen?`);
        }
    }

    async _loeschen(nummern, frage) {
        if (!confirm(frage)) return;
        this.sperren(true);
        try {
            await this.loeschen(nummern);
        } finally {
            this.sperren(false);
        }
    }

    /** Knöpfe sperren, solange ein Render läuft (oder gerade startet) oder gelöscht wird. */
    sperren(gesperrt) {
        this._gesperrt = !!gesperrt;
        for (const knopf of this.feld.querySelectorAll('[data-aktion="neu"], [data-aktion="loeschen"]')) knopf.disabled = this._gesperrt;
        this._knopfstand();
    }

    zeigen(laeufe) {
        const stand = (laeufe || []).map(l => `${l.nr}:${l.zeit}`).join('|');
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.replaceChildren();
        this.wahl = null;
        if (!laeufe?.length) return;
        const leiste = document.createElement('div');
        leiste.className = 'exportleiste-laeufe-leiste';
        leiste.innerHTML = this._knopf('neu', 'alle', 'fa-redo', 'Alle neu rendern', 'Alle Läufe mit ihren Einstellungen und dem Modell von heute noch einmal, nacheinander')
            + '<button type="button" class="btn btn-danger btn-sm" data-aktion="auswahl" disabled title="Die angekreuzten Läufe samt Video löschen">'
            + '<i class="fas fa-trash"></i> <span>Auswahl löschen (<span data-zahl>0</span>)</span></button>'
            + '<small class="hb-gedaempft">Kästchen wählt eine Zeile, Shift-Klick alle bis zur zuletzt gewählten, das Kopfkästchen alle.</small>';
        const tabelle = document.createElement('div');
        tabelle.innerHTML = dbTabelle({ key: Exportleistelaeufe.SCHLUESSEL, spalten: this._spalten(), zeilen: laeufe.map(l => this._zeile(l)) });
        this.feld.append(leiste, tabelle);
        this.wahl = new Zeilenwahl(tabelle.querySelector('table'), () => this._knopfstand()).binden();
    }

    _spalten() {
        return [
            { label: '<input type="checkbox" id="select-all" title="alle auswählen / Auswahl aufheben">', key: 'wahl', sortAus: true },
            { label: 'Lauf', key: 'nr', num: true }, { label: 'Aktion', key: 'aktion', sortAus: true }, { label: 'Bilder', key: 'bilder', num: true },
            { label: 'Größe · Proben', key: 'groesse' }, { label: 'Dauer', key: 'dauer', num: true }, { label: 'Gelaufen am', key: 'zeit' },
            { label: 'Video', key: 'video' }, { label: 'Anmerkung', key: 'anmerkung' },
        ];
    }

    _knopf(aktion, nr, symbol, text, titel, art = 'btn-secondary') {
        return `<button type="button" class="btn ${art} btn-sm" data-aktion="${aktion}" data-nr="${esc(nr)}" title="${esc(titel)}"${this._gesperrt ? ' disabled' : ''}>`
            + `<i class="fas ${symbol}"></i> ${esc(text)}</button>`;
    }

    _zeile(l) {
        const sekunden = Number(l.sekunden).toFixed(2).replace('.', ',');
        const video = `<a href="${esc(this.adresse(`datei/${encodeURIComponent(l.video)}`))}" target="_blank" title="${esc(`${l.verzeichnis}\\${l.video}`)}">${esc(l.video)}</a>`;
        return {
            id: l.nr,
            zellen: [
                { html: `<input type="checkbox" class="job-check" value="${esc(l.nr)}">`, klasse: 'kaestchen' },
                { text: `#${l.nr}`, sort: l.nr, num: true },
                { html: this._knopf('neu', l.nr, 'fa-redo', 'Neu rendern', `Lauf #${l.nr} mit seinen Einstellungen und dem Modell von heute noch einmal; ersetzt diese Zeile`)
                    + ' ' + this._knopf('loeschen', l.nr, 'fa-trash', 'Löschen', `Lauf #${l.nr} samt Video und Bogen löschen (der Export im Exportordner bleibt)`, 'btn-danger') },
                { text: `${l.bilder} (${sekunden} s)`, sort: l.bilder, num: true },
                { text: `${l.groesse} · ${l.spp}${l.ton ? ' · mit Ton' : ''}${l.physik === false ? ' · ohne Physik' : ''}` },
                { text: `${Math.round(l.dauer_s)} s`, sort: l.dauer_s, num: true },
                { text: l.zeit || '' },
                { html: video, sort: l.video },
                { text: l.anmerkung || '' },
            ],
        };
    }

    /** „Auswahl löschen (n)": Zahl der Häkchen, gesperrt ohne Häkchen oder während eines Renders. */
    _knopfstand() {
        const knopf = this.feld.querySelector('[data-aktion="auswahl"]');
        if (!knopf) return;
        const anzahl = this.wahl?.anzahl() || 0;
        knopf.disabled = this._gesperrt || anzahl === 0;
        knopf.querySelector('[data-zahl]').textContent = String(anzahl);
    }
}
