import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Auftragslauf } from './auftragslauf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

/**
 * Auftragsliste — die Tabelle der Auftraege: auswaehlen, loeschen, sortieren
 * und die Knoepfe je Zeile.
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026): `deleteJob`,
 * `bulkDelete`, `toggleSelectAll`, `updateBulkBtn` und `sortTable` — dazu 28
 * `onclick`/`onchange`-Attribute in der Vorlage.
 *
 * Die Knoepfe der Zeilen haengen jetzt an EINEM Zuhoerer auf der Tabelle
 * (`data-aktion` + `data-auftrag`). Das ist noetig, weil ein `onclick`-Attribut
 * einen globalen Namen braucht und ES-Module keinen anlegen — und es gilt
 * automatisch fuer Zeilen, die erst zur Laufzeit entstehen.
 */
export class Auftragsliste {

    static LOESCHEN = '/api/job/';
    static MASSENLOESCHEN = '/api/jobs/bulk-delete/';

    static aufbauen() {
        return new Auftragsliste().aufbauen();
    }

    constructor() {
        this.koerper = document.getElementById('jobTableBody');
        this.richtung = {};
    }

    aufbauen() {
        if (!this.koerper) return this;
        this.koerper.addEventListener('click', ereignis => this._klick(ereignis));
        this.koerper.addEventListener('change', ereignis => {
            if (ereignis.target.classList.contains('job-check')) this.knopfstand();
        });
        document.getElementById('selectAll')
            ?.addEventListener('change', feld => this.alleWaehlen(feld.target));
        document.getElementById('bulkDeleteBtn')
            ?.addEventListener('click', () => this.massenloeschen());
        document.querySelectorAll('[data-sort]').forEach(kopf => {
            kopf.addEventListener('click', () => this.sortieren(kopf.dataset.sort));
        });
        Auftragslauf.laufendeVerfolgen();
        return this;
    }

    /** Ein Klick in der Tabelle: Start, Stopp oder Loeschen einer Zeile. */
    _klick(ereignis) {
        const knopf = ereignis.target.closest('[data-aktion]');
        if (!knopf) return;
        const id = knopf.dataset.auftrag;
        // Ohne Kennung passiert sonst NICHTS — kein Fehler, keine Meldung.
        // Genau die stille Klasse, die dieser Umbau beseitigen soll (Befund
        // von Nemotron im Sparring am 16.08.2026).
        if (!id) {
            Protokoll.fehler('Auftraege', 'Knopf ohne data-auftrag:',
                             knopf.dataset.aktion, knopf);
            return;
        }
        const aktionen = {
            start: () => new Auftragslauf(id).starten(knopf),
            stop: () => new Auftragslauf(id).stoppen(knopf),
            delete: () => this.loeschen(id, knopf),
        };
        aktionen[knopf.dataset.aktion]?.();
    }

    async loeschen(auftragId, knopf) {
        if (!confirm('Diesen Auftrag löschen?')) return;
        if (knopf) knopf.disabled = true;
        try {
            const daten = await Serverabruf.senden(
                `${Auftragsliste.LOESCHEN}${auftragId}/delete/`, {});
            if (!daten.ok) throw new Error(daten.error || 'Unbekannter Fehler');
            this._zeileEntfernen(auftragId);
            this.knopfstand();
            this._leerPruefen();
        } catch (fehler) {
            if (knopf) knopf.disabled = false;
            alert('Löschen fehlgeschlagen: ' + fehler.message);
        }
    }

    async massenloeschen() {
        const kennungen = [...document.querySelectorAll('.job-check:checked')]
            .map(feld => feld.value);
        if (!kennungen.length) return;
        if (!confirm(`${kennungen.length} Auftrag/Aufträge löschen?`)) return;
        const knopf = document.getElementById('bulkDeleteBtn');
        if (knopf) {
            knopf.disabled = true;
            knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Löscht …';
        }
        try {
            const daten = await Serverabruf.senden(
                Auftragsliste.MASSENLOESCHEN, { ids: kennungen });
            if (!daten.ok) throw new Error(daten.error || 'Unbekannter Fehler');
            (daten.deleted || []).forEach(id => this._zeileEntfernen(id));
            const alle = document.getElementById('selectAll');
            if (alle) alle.checked = false;
            this._leerPruefen();
        } catch (fehler) {
            alert('Löschen fehlgeschlagen: ' + fehler.message);
        } finally {
            this._knopfBeschriften();
            this.knopfstand();
        }
    }

    _knopfBeschriften() {
        const knopf = document.getElementById('bulkDeleteBtn');
        if (!knopf) return;
        knopf.innerHTML = '<i class="fas fa-trash"></i> Auswahl löschen '
            + '(<span id="bulkCount">0</span>)';
    }

    _zeileEntfernen(auftragId) {
        document.getElementById('detail-' + auftragId)?.remove();
        document.getElementById('row-' + auftragId)?.remove();
    }

    /** Ist die Tabelle leer, verschwindet der ganze Abschnitt. */
    _leerPruefen() {
        if (!this.koerper) return;
        const zeilen = this.koerper.querySelectorAll('tr:not(.detail-row)');
        if (zeilen.length) return;
        this.koerper.closest('.job-list-section')
            ?.classList.add('hb-versteckt');
    }

    alleWaehlen(feld) {
        document.querySelectorAll('.job-check').forEach(kaestchen => {
            kaestchen.checked = feld.checked;
        });
        this.knopfstand();
    }

    /** Der Massenlösch-Knopf zeigt die Zahl der Häkchen. */
    knopfstand() {
        const anzahl = document.querySelectorAll('.job-check:checked').length;
        const knopf = document.getElementById('bulkDeleteBtn');
        const zaehler = document.getElementById('bulkCount');
        if (knopf) knopf.disabled = anzahl === 0;
        if (zaehler) zaehler.textContent = anzahl;
    }

    /**
     * Nach einer Spalte sortieren. Die Detailzeile folgt ihrer Hauptzeile —
     * sonst stehen aufgeklappte Details nach dem Sortieren beim falschen
     * Auftrag.
     */
    sortieren(schluessel) {
        if (!this.koerper) return;
        const zeilen = [...this.koerper.querySelectorAll('tr:not(.detail-row)')];
        this.richtung[schluessel] = !this.richtung[schluessel];
        const aufwaerts = this.richtung[schluessel];
        zeilen.sort((a, b) => {
            const links = a.dataset[schluessel] || '';
            const rechts = b.dataset[schluessel] || '';
            if (schluessel === 'size') {
                return aufwaerts ? Number(links) - Number(rechts)
                                 : Number(rechts) - Number(links);
            }
            return aufwaerts ? links.localeCompare(rechts)
                             : rechts.localeCompare(links);
        });
        for (const zeile of zeilen) {
            this.koerper.appendChild(zeile);
            const detail = document.getElementById(
                'detail-' + zeile.id.replace('row-', ''));
            if (detail) this.koerper.appendChild(detail);
        }
    }
}
