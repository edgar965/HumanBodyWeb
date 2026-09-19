/**
 * Proportionenmasstab — der zweite Reiter des Popups: die Maße als Zahlen.
 *
 * Eine Zeile je Maß (`katalog.proportionen`, 19): Name und Ansicht, Eingabe in
 * cm (leer = keine Vorgabe; × leert sie), Ziel wie gemessen, Modell, Differenz
 * und ein Hinweis (nicht formbar / geformt von → nach). Den Zustand hält der
 * `Proportionendialog` (`eingaben`); jede Eingabe geht als `beiWert(k, cm|null)`
 * dorthin. Ausgelagert am 20.09.2026, als der Dialog über 300 Zeilen wuchs.
 */
export class Proportionenmasstab {

    static ANSICHT = { vorn: 'vorn', seite: 'seite', kopf: 'Kopf' };

    /**
     * @param tabelle  das `tbody` der Maßtabelle
     * @param katalog  `katalog.proportionen`, `katalog.proportion_cm`
     * @param beiWert  `(schluessel, cm|null)` — getippt oder geleert
     */
    constructor(tabelle, katalog, beiWert) {
        this.tabelle = tabelle;
        this.katalog = katalog || {};
        this.beiWert = beiWert;
    }

    /** @param daten `{ziel, modell, formung}` des Ergebnisses, @param eingaben `{k: cm}` */
    fuellen(daten, eingaben) {
        if (!this.tabelle) return;
        this.tabelle.innerHTML = '';
        const [lo, hi] = this.katalog.proportion_cm || [0.5, 120];
        for (const m of this.katalog.proportionen || []) {
            const k = m.schluessel;
            const ziel = daten.ziel[k], modell = daten.modell[k];
            const tr = document.createElement('tr');
            tr.dataset.mass = k;
            const wert = eingaben[k] ?? '';
            const diff = (ziel !== undefined && modell !== undefined) ? (modell - ziel).toFixed(1) : '–';
            const formung = (daten.formung || {})[k];
            const hinweis = !m.formbar ? '<span class="hb-hinweis">nur Ansicht — Augäpfel folgen nicht</span>'
                : formung ? `<span class="hb-hinweis">geformt ${formung.vorher} → ${formung.nachher} cm</span>` : '';
            tr.innerHTML = `<th>${m.name}<br><span class="hb-hinweis">${Proportionenmasstab.ANSICHT[m.ansicht] || m.ansicht}</span></th>`
                + `<td><input type="number" step="0.1" min="${lo}" max="${hi}" value="${wert}" placeholder="${ziel ?? ''}" ${m.formbar ? '' : 'disabled'}>`
                + `<button type="button" class="btn btn-sm btn-secondary" data-tat="leeren" title="Vorgabe löschen — Linien zurück auf ihre Startlage">×</button></td>`
                + `<td>${ziel !== undefined ? ziel.toFixed(1) : '–'}</td><td>${modell !== undefined ? modell.toFixed(1) : '–'}</td>`
                + `<td>${diff}</td><td>${hinweis}</td>`;
            const input = tr.querySelector('input');
            input.addEventListener('input', () => this.beiWert(k, input.value === '' ? null : Number(input.value)));
            tr.querySelector('[data-tat="leeren"]').addEventListener('click', () => { input.value = ''; this.beiWert(k, null); });
            this.tabelle.appendChild(tr);
        }
    }

    /** Das Feld eines Maßes auf einen Wert setzen (nach einem Zug im Bild). */
    setzen(k, cm) {
        const feld = this.tabelle?.querySelector(`tr[data-mass="${k}"] input`);
        if (feld) feld.value = cm === null || cm === undefined ? '' : cm;
    }
}
