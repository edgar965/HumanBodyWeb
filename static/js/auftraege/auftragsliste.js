import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Auftragslauf } from './auftragslauf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';
import { Detailzeilen } from './detailzeilen.js';

/**
 * Auftragsliste — die Tabelle der Auftraege: auswaehlen, loeschen und die
 * Knoepfe je Zeile.
 *
 * SORTIERT WIRD SEIT DEM 28.08.2026 VON djangoBase. Hier stand eine eigene
 * Fassung (Klick auf `th[data-sort]`, Zeilen umhaengen) — dieselbe Aufgabe
 * wie `TabellenSortierung`, nur ohne sichtbare Pfeile und ohne gemerkte
 * Spaltenbreiten. Was djangoBase nicht wissen kann, steht in `Detailzeilen`.
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
    }

    aufbauen() {
        if (!this.koerper) return this;
        this.koerper.addEventListener('click', ereignis => this._klick(ereignis));
        this.koerper.addEventListener('change', ereignis => {
            if (ereignis.target.classList.contains('job-check')) this.knopfstand();
        });
        document.getElementById('select-all')
            ?.addEventListener('change', feld => this.alleWaehlen(feld.target));
        document.getElementById('bulk-delete-btn')
            ?.addEventListener('click', () => this.massenloeschen());
        // Sortiert wird von djangoBase (`tabellen_auto.js` bindet jede
        // `table.sortable` von selbst an). Hier bleibt nur, was djangoBase
        // nicht wissen kann: dass eine Detailzeile ihrer Hauptzeile folgt.
        Detailzeilen.binden(document.getElementById('jobTable'));
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
        const knopf = document.getElementById('bulk-delete-btn');
        if (knopf) {
            knopf.disabled = true;
            knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Löscht …';
        }
        try {
            const daten = await Serverabruf.senden(
                Auftragsliste.MASSENLOESCHEN, { ids: kennungen });
            if (!daten.ok) throw new Error(daten.error || 'Unbekannter Fehler');
            (daten.deleted || []).forEach(id => this._zeileEntfernen(id));
            const alle = document.getElementById('select-all');
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
        const knopf = document.getElementById('bulk-delete-btn');
        if (!knopf) return;
        knopf.innerHTML = '<i class="fas fa-trash"></i> Auswahl löschen '
            + '(<span id="bulk-count">0</span>)';
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
        const knopf = document.getElementById('bulk-delete-btn');
        const zaehler = document.getElementById('bulk-count');
        if (knopf) knopf.disabled = anzahl === 0;
        if (zaehler) zaehler.textContent = anzahl;
    }
}
