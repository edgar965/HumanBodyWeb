import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Auftragslauf } from './auftragslauf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';
import { Detailzeilen } from './detailzeilen.js';
import { Zeilenwahl } from './zeilenwahl.js';
import { Auftragszeile } from './auftragszeile.js';

/**
 * Auftragsliste — die Tabelle der Auftraege: auswaehlen, loeschen und die
 * Knoepfe je Zeile.
 *
 * DIE TABELLE RENDERT SEIT DEM 12.09.2026 `djangobase/_tabelle.html`
 * (`core.dienste.auftragstabelle`). Sie hat deshalb keine `id` mehr — der
 * Anker ist der Abschnitt `#auftragsliste`, die Zeilen tragen `data-id`
 * (so sieht es die Vorlage vor), nicht mehr `id="row-<auftrag>"`. Die
 * Auswahl (Kaestchen, Shift-Bereich, Kopfkaestchen) macht `Zeilenwahl`.
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
        this.abschnitt = document.getElementById('auftragsliste');
        /** @type {HTMLTableElement|null} */
        this.tabelle = this.abschnitt?.querySelector('table') || null;
        this.koerper = this.tabelle?.tBodies[0] || null;
        this.wahl = new Zeilenwahl(this.tabelle, () => this.knopfstand());
    }

    aufbauen() {
        if (!this.koerper) return this;
        this.koerper.addEventListener('click', ereignis => this._klick(ereignis));
        this.wahl.binden();
        document.getElementById('bulk-delete-btn')
            ?.addEventListener('click', () => this.massenloeschen());
        // Sortiert wird von djangoBase (`tabellen_auto.js` bindet jede
        // `table.sortable` von selbst an). Hier bleibt nur, was djangoBase
        // nicht wissen kann: dass eine Detailzeile ihrer Hauptzeile folgt.
        Detailzeilen.binden(this.tabelle);
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
            this.wahl.nachziehen();
            this._leerPruefen();
        } catch (fehler) {
            if (knopf) knopf.disabled = false;
            alert('Löschen fehlgeschlagen: ' + fehler.message);
        }
    }

    async massenloeschen() {
        const kennungen = this.wahl.kennungen();
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
            this._leerPruefen();
        } catch (fehler) {
            alert('Löschen fehlgeschlagen: ' + fehler.message);
        } finally {
            this._knopfBeschriften();
            this.wahl.nachziehen();
        }
    }

    _knopfBeschriften() {
        const knopf = document.getElementById('bulk-delete-btn');
        if (!knopf) return;
        // Dieselbe Form wie in `_auftragstabelle.html`: Text in EINER Hülle,
        // sonst setzt der Flex-Abstand des Knopfs Lücken um die Zahl.
        knopf.innerHTML = '<i class="fas fa-trash"></i><span>Auswahl löschen '
            + '(<span id="bulk-count">0</span>)</span>';
    }

    _zeileEntfernen(auftragId) {
        document.getElementById('detail-' + auftragId)?.remove();
        new Auftragszeile(auftragId).zeile()?.remove();
    }

    /** Ist die Tabelle leer, verschwindet der ganze Abschnitt. */
    _leerPruefen() {
        if (!this.koerper) return;
        const zeilen = this.koerper.querySelectorAll('tr:not(.detail-row)');
        if (zeilen.length) return;
        this.koerper.closest('.job-list-section')
            ?.classList.add('hb-versteckt');
    }

    /** Der Massenlösch-Knopf zeigt die Zahl der Häkchen. */
    knopfstand() {
        const anzahl = this.wahl.anzahl();
        const knopf = document.getElementById('bulk-delete-btn');
        const zaehler = document.getElementById('bulk-count');
        if (knopf) knopf.disabled = anzahl === 0;
        if (zaehler) zaehler.textContent = String(anzahl);
    }
}
