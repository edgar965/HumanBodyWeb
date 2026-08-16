import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';
import { Auftragszeile } from './auftragszeile.js';
import { Pipelinefelder } from './pipelinefelder.js';
import { Htmltext } from '/static/djangobase/js/htmltext.js';

/**
 * Auftragslauf — einen Auftrag starten, stoppen und seinen Fortschritt
 * verfolgen.
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026):
 * `startProcessing` (36 Zeilen), `stopProcessing`, `startJobPolling` und
 * `addNewJobRow` (35 Zeilen HTML-Bau).
 *
 * Dabei behoben: Die Nachfrage lief ueber `fetch(...).then(r => r.json())` ohne
 * `.ok`-Pruefung und mit einem `catch`, der nach 5 s einfach weiterfragte —
 * bei einem Serverfehler drehte die Seite endlos, ohne dass etwas zu sehen war.
 * Jetzt wird nach einer Grenze aufgegeben und der Grund gemeldet.
 */
export class Auftragslauf {

    /** Abstand der Nachfragen in Millisekunden. */
    static TAKT_MS = 2000;
    /** Erste Nachfrage etwas spaeter — der Lauf braucht einen Moment. */
    static ERSTE_MS = 1500;
    /**
     * So oft darf die Nachfrage scheitern, bevor aufgegeben wird.
     *
     * Befund von Nemotron im Sparring am 16.08.2026: Erst waren es 5, und die
     * Anzeige sprang danach auf „fehlgeschlagen". Ein Server-Neustart oder ein
     * kurzer WLAN-Aussetzer erzeugt aber leicht fünf Fehler in Folge, WÄHREND
     * der Auftrag weiterläuft — der Nutzer sieht „fehlgeschlagen", startet neu
     * und hat den Auftrag doppelt. Jetzt: viele Versuche mit wachsendem
     * Abstand, und am Ende steht „Verbindung verloren", nicht „fehlgeschlagen".
     */
    static FEHLVERSUCHE = 40;
    /** Wartezeit nach einem Fehlversuch: 3 s, 6 s, 9 s … bis HOECHSTWARTE. */
    static WARTE_MS = 3000;
    static HOECHSTWARTE_MS = 30000;
    /** Auswahlfelder der Pipeline je Zeile. */
    static WAHL_VORSILBE = 'pl-';

    constructor(auftragId) {
        this.id = auftragId;
        this.anzeige = new Auftragszeile(auftragId);
        this.fehlversuche = 0;
    }

    /** Lauf starten. `knopf` wird waehrend des Starts gesperrt. */
    async starten(knopf) {
        const wahl = document.getElementById(
            Auftragslauf.WAHL_VORSILBE + this.id);
        const pipeline = wahl ? wahl.value : 'v4';
        this._knopf(knopf, true);
        try {
            const daten = await this._anfordern(pipeline);
            if (!daten.ok) throw new Error(daten.error || 'Unbekannter Fehler');
            // Ein Pipelinewechsel legt einen NEUEN Auftrag an; der alte bleibt.
            const laufend = daten.new_job_id
                ? this._neueZeile(daten, wahl, knopf) : this.id;
            const lauf = new Auftragslauf(laufend);
            lauf.anzeige.detailzeile();
            lauf.anzeige.aktualisieren({ status: daten.status, progress: 0,
                                         progress_detail: 'Startet …' });
            lauf.verfolgen();
        } catch (fehler) {
            this._knopf(knopf, false);
            alert('Start fehlgeschlagen: ' + fehler.message);
        }
    }

    /**
     * Der Endpunkt erwartet ein Formular, nicht JSON — deshalb hier
     * `URLSearchParams` statt `Serverabruf.senden`.
     */
    async _anfordern(pipeline) {
        const rumpf = new URLSearchParams({ pipeline });
        // Die alte Upload-Seite hat keine Pipeline-Einstellungen; dort bleibt
        // `pipeline_params` weg, damit der Server seine Vorgaben nimmt.
        const parameter = Pipelinefelder.sammeln(pipeline);
        if (Object.keys(parameter).length) {
            rumpf.set('pipeline_params', JSON.stringify(parameter));
        }
        return Serverabruf.json(`/api/job/${this.id}/start/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded',
                       'X-CSRFToken': Serverabruf.csrfToken() },
            body: rumpf.toString(),
        });
    }

    _neueZeile(daten, wahl, knopf) {
        Auftragslauf.zeileEinfuegen(daten.new_job_id, daten.new_pipeline,
                                    daten.new_pipeline_display, this.id);
        if (wahl) wahl.value = wahl.dataset.current;
        this._knopf(knopf, false);
        return daten.new_job_id;
    }

    async stoppen(knopf) {
        if (!confirm('Verarbeitung stoppen?')) return;
        if (knopf) {
            knopf.disabled = true;
            knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stoppt …';
        }
        try {
            await Serverabruf.senden(`/api/job/${this.id}/stop/`, {});
            if (knopf) knopf.innerHTML = '<i class="fas fa-stop"></i> Gestoppt';
        } catch (fehler) {
            Protokoll.warnung('Auftraege', 'Stopp fehlgeschlagen:',
                              fehler.message);
            if (knopf) {
                knopf.disabled = false;
                knopf.innerHTML = '<i class="fas fa-stop"></i> Stopp';
            }
        }
    }

    /** Fortschritt verfolgen, bis der Auftrag fertig oder gescheitert ist. */
    verfolgen() {
        setTimeout(() => this._nachfragen(), Auftragslauf.ERSTE_MS);
    }

    async _nachfragen() {
        try {
            const daten = await Serverabruf.json(`/api/job/${this.id}/status/`);
            this.fehlversuche = 0;
            this.anzeige.aktualisieren(daten);
            if (Auftragszeile.ENDE.includes(daten.status)) return;
        } catch (fehler) {
            this.fehlversuche++;
            if (this.fehlversuche >= Auftragslauf.FEHLVERSUCHE) {
                Protokoll.warnung('Auftraege',
                                  `Status von ${this.id} nicht abfragbar:`,
                                  fehler.message);
                // KEIN 'failed': Der Auftrag laeuft auf dem Server womoeglich
                // weiter. Nur die Verbindung ist weg — und das steht auch da.
                this.anzeige.verbindungWeg(fehler.message);
                return;
            }
            // Wachsender Abstand: Nach einem Neustart des Servers ist wenige
            // Sekunden spaeter wieder alles da, ohne ihn zu bestuermen.
            setTimeout(() => this._nachfragen(),
                       Math.min(Auftragslauf.WARTE_MS * this.fehlversuche,
                                Auftragslauf.HOECHSTWARTE_MS));
            return;
        }
        setTimeout(() => this._nachfragen(), Auftragslauf.TAKT_MS);
    }

    _knopf(knopf, laeuft) {
        if (!knopf) return;
        knopf.disabled = laeuft;
        knopf.innerHTML = laeuft ? '<i class="fas fa-spinner fa-spin"></i>'
                                 : '<i class="fas fa-play"></i>';
    }

    /** Alle Auftraege, die beim Laden der Seite schon laufen, weiterverfolgen. */
    static laufendeVerfolgen() {
        document.querySelectorAll('tr[id^="row-"]').forEach(zeile => {
            const zelle = zeile.querySelector('td[id^="status-"]');
            if (!zelle?.querySelector('.inline-progress')) return;
            const lauf = new Auftragslauf(zelle.id.replace('status-', ''));
            lauf.anzeige.detailzeile();
            lauf.verfolgen();
        });
    }

    /** Pipelines im Auswahlfeld einer neuen Zeile. */
    static PIPELINES = [['v4', 'v4'], ['gvhmr', 'GVHMR'], ['wham', 'WHAM'],
                        ['prompthmr', 'PromptHMR'],
                        ['hybrid_gvhmr', 'Hybrid (GVHMR)'],
                        ['hybrid_prompthmr', 'Hybrid (PromptHMR)']];

    /** Zeile fuer einen neu angelegten Auftrag oben in die Tabelle setzen. */
    static zeileEinfuegen(neueId, pipeline, anzeigename, quelleId) {
        const quelle = document.getElementById('row-' + quelleId);
        const koerper = document.getElementById('jobTableBody');
        if (!quelle || !koerper) return;
        // Maskieren: Der Dateiname kommt aus dem Upload. Ein Video mit dem
        // Namen `<img src=x onerror=…>.mp4` fuehrte hier fremdes JavaScript
        // aus (Befund von Nemotron, Sparring 16.08.2026).
        const name = Htmltext.maskieren(
            quelle.querySelector('td:nth-child(2)').textContent);
        const groesse = Htmltext.maskieren(
            quelle.querySelector('td:nth-child(5)').textContent);
        const anzeige = Htmltext.maskieren(anzeigename);
        const zeile = document.createElement('tr');
        zeile.id = 'row-' + neueId;
        zeile.innerHTML = '<td></td>'
            + `<td>${name}</td>`
            + `<td><span class="badge badge-${pipeline}">${anzeige}</span></td>`
            + `<td id="status-${neueId}"><span class="hb-laeuft">`
            + '<i class="fas fa-spinner fa-spin"></i> Startet …</span></td>'
            + `<td>${groesse}</td>`
            + `<td>${new Date().toLocaleString('de-DE')}</td>`
            + '<td><div class="hb-zeilenaktionen">'
            + `<select class="pipeline-select" id="pl-${neueId}"`
            + ` data-current="${pipeline}">`
            + Auftragslauf.PIPELINES.map(([wert, text]) =>
                `<option value="${wert}"`
                + `${wert === pipeline ? ' selected' : ''}>${text}</option>`).join('')
            + '</select>'
            + '<button class="btn btn-sm btn-primary" data-aktion="start"'
            + ` data-auftrag="${neueId}"><i class="fas fa-play"></i></button>`
            + '</div></td>'
            + '<td class="hb-zeilenaktionen">'
            + '<button class="btn btn-sm btn-danger" data-aktion="delete"'
            + ` data-auftrag="${neueId}"><i class="fas fa-trash"></i></button>`
            + '</td>';
        koerper.insertBefore(zeile, koerper.firstChild);
    }
}
