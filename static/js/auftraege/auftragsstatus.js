import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';
import { Auftragszeile } from './auftragszeile.js';

/**
 * Auftragsstatus — die Statusseite EINES Auftrags: Fortschrittsbalken,
 * Phasenanzeige und der Stopp-Knopf.
 *
 * Herausgeloest aus templates/job_status.html (Umbau 16.08.2026): 86 Zeilen
 * inline. Darin steckten die Phasenbeschriftungen ein DRITTES Mal (nach
 * upload.html und upload_v4.html, jetzt `Auftragszeile.PHASEN`) — in zwei
 * Fassungen sogar innerhalb derselben Funktion, einmal kurz fuer das Abzeichen
 * und einmal lang fuer die Phasenzeile.
 *
 * Die Nachfrage laeuft weiter mit wachsendem Abstand, wenn der Server nicht
 * antwortet, und gibt nach einer Grenze auf — dieses Verhalten war schon da und
 * ist hier erhalten (`GRENZE`, `WARTE_MS`).
 */
export class Auftragsstatus {

    static TAKT_MS = 2000;
    /** Wartezeit nach einem Fehlversuch: 5 s, 10 s, 15 s … bis HOECHSTWARTE. */
    static WARTE_MS = 5000;
    static HOECHSTWARTE_MS = 30000;
    /** Nach so vielen Fehlversuchen in Folge wird aufgegeben (~5 Minuten). */
    static GRENZE = 60;

    static aufbauen(auftragId) {
        return new Auftragsstatus(auftragId).aufbauen();
    }

    constructor(auftragId) {
        this.id = auftragId;
        this.fehlversuche = 0;
    }

    aufbauen() {
        setTimeout(() => this.nachfragen(), Auftragsstatus.TAKT_MS);
        this._stoppknopf();
        return this;
    }

    async nachfragen() {
        try {
            const daten = await Serverabruf.json(`/api/job/${this.id}/status/`);
            this.fehlversuche = 0;
            this.anzeigen(daten);
            if (Auftragszeile.ENDE.includes(daten.status)) {
                location.reload();
                return;
            }
            setTimeout(() => this.nachfragen(), Auftragsstatus.TAKT_MS);
        } catch (fehler) {
            this._fehlversuch(fehler);
        }
    }

    anzeigen(daten) {
        const prozent = daten.progress || 0;
        const balken = document.getElementById('progressFill');
        if (balken) balken.style.width = prozent + '%';
        this._text('progressText', prozent + '%');
        this._text('progressDetail', daten.progress_detail || '');
        const beschriftung = Auftragszeile.PHASEN[daten.status] || daten.status;
        const abzeichen = document.getElementById('jobBadge');
        if (abzeichen) {
            abzeichen.textContent = beschriftung;
            abzeichen.className = 'badge badge-' + daten.status;
        }
        this._text('jobPhase', beschriftung);
    }

    _text(kennung, wert) {
        const element = document.getElementById(kennung);
        if (element) element.textContent = wert;
    }

    _fehlversuch(fehler) {
        this.fehlversuche++;
        if (this.fehlversuche >= Auftragsstatus.GRENZE) {
            Protokoll.warnung('Auftrag', 'Status nicht abfragbar:',
                              fehler.message);
            this._text('jobPhase',
                       'Verbindung verloren — bitte die Seite neu laden');
            return;
        }
        const warten = Math.min(Auftragsstatus.WARTE_MS * this.fehlversuche,
                                Auftragsstatus.HOECHSTWARTE_MS);
        setTimeout(() => this.nachfragen(), warten);
    }

    _stoppknopf() {
        const knopf = document.getElementById('stopBtn');
        if (!knopf) return;
        knopf.addEventListener('click', async () => {
            if (!confirm('Verarbeitung stoppen?')) return;
            knopf.disabled = true;
            knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stoppt …';
            try {
                await Serverabruf.senden(`/api/job/${this.id}/stop/`, {});
                knopf.innerHTML = '<i class="fas fa-check"></i> Gestoppt';
                knopf.className = 'btn btn-secondary';
                // Die Nachfrage sieht danach 'failed' und laedt die Seite neu.
            } catch (fehler) {
                Protokoll.fehler('Auftrag', 'Stopp fehlgeschlagen:', fehler);
                knopf.innerHTML =
                    '<i class="fas fa-exclamation-triangle"></i> Fehler';
            }
        });
    }
}
