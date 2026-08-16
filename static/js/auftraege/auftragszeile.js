import { Htmltext } from '/static/djangobase/js/htmltext.js';

/**
 * Auftragszeile — die Anzeige eines Auftrags in der Tabelle: Statuszelle,
 * aufklappbare Detailzeile mit Fortschritt, Fehler und Aktionen.
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026):
 * `getOrCreateDetailRow` (29 Zeilen HTML-Bau) und `updateJobUI` (77 Zeilen mit
 * sieben `getElementById` und drei Inline-Stilen je Aufruf).
 */
export class Auftragszeile {

    /** Beschriftung der Phasen, die der Server als `status` liefert. */
    static PHASEN = {
        pending: 'Wartet', detecting_2d: '2D-Posenerkennung',
        openpose: '2D-Erkennung (GPU)', openpose_csv: 'CSV-Umwandlung',
        mediapipe: '2D-Erkennung (CPU)', lifting_3d: '3D-Posenschätzung',
        mocapnet: '3D-Posenschätzung', v4_processing: 'MocapNET v4',
        processing: 'Läuft', complete: 'Fertig', failed: 'Fehlgeschlagen',
        hybrid_processing: 'Hybrid (Körper + Gesicht)',
    };
    /** Zustaende, nach denen nicht weiter gefragt wird. */
    static ENDE = ['complete', 'failed'];

    constructor(auftragId) {
        this.id = auftragId;
    }

    /** Zeile des Auftrags in der Tabelle. */
    zeile() {
        return document.getElementById('row-' + this.id);
    }

    /** Detailzeile, bei Bedarf angelegt. */
    detailzeile() {
        const vorhanden = document.getElementById('detail-' + this.id);
        if (vorhanden) return vorhanden;
        const zeile = this.zeile();
        if (!zeile) return null;
        const neu = document.createElement('tr');
        neu.id = 'detail-' + this.id;
        neu.className = 'detail-row';
        neu.innerHTML = `<td colspan="${zeile.children.length}">`
            + '<div class="detail-panel">'
            + '<div class="detail-header">'
            + `<span class="badge" id="detail-badge-${this.id}">Startet</span>`
            + `<span class="detail-phase" id="detail-phase-${this.id}"></span>`
            + '</div>'
            + '<div class="progress-bar">'
            + `<div class="progress-fill hb-breite-0" id="detail-fill-${this.id}">`
            + `<span id="detail-pct-${this.id}">0%</span></div></div>`
            + `<div class="detail-progress-text" id="detail-text-${this.id}">`
            + 'Startet …</div>'
            + `<div class="detail-thumb" id="detail-thumb-${this.id}">`
            + `<img src="/api/thumbnail/${this.id}/" alt="Video"></div>`
            + `<div class="detail-error hb-versteckt" id="detail-error-${this.id}">`
            + '</div>'
            + `<div class="detail-actions" id="detail-actions-${this.id}">`
            + '<button class="btn btn-sm btn-danger" data-aktion="stop" '
            + `data-auftrag="${this.id}">`
            + '<i class="fas fa-stop"></i> Stopp</button>'
            + '</div></div></td>';
        zeile.after(neu);
        return neu;
    }

    /** Stand des Auftrags in Tabelle und Detailzeile eintragen. */
    aktualisieren(daten) {
        this._statuszelle(daten);
        if (!document.getElementById('detail-' + this.id)) return;
        this._fortschritt(daten);
        if (Auftragszeile.ENDE.includes(daten.status)) this._startknopfFrei();
        if (daten.status === 'complete') this._fertig(daten);
        else if (daten.status === 'failed') this._gescheitert(daten);
    }

    /**
     * Die Verbindung ist weg — der Auftrag laeuft aber vielleicht weiter.
     *
     * Bewusst NICHT „fehlgeschlagen": Wer das liest, startet den Auftrag neu
     * und hat ihn doppelt (Befund von Nemotron, Sparring 16.08.2026).
     */
    verbindungWeg(meldung) {
        const zelle = document.getElementById('status-' + this.id);
        if (zelle) {
            zelle.innerHTML = '<span class="hb-laeuft" title="'
                + Htmltext.maskieren(meldung)
                + '"><i class="fas fa-question-circle"></i> '
                + 'Verbindung verloren — Seite neu laden</span>';
        }
        this._setzen('detail-text-',
                     'Verbindung verloren. Der Auftrag läuft möglicherweise '
                     + 'weiter — bitte die Seite neu laden.');
    }

    _statuszelle(daten) {
        const zelle = document.getElementById('status-' + this.id);
        if (!zelle) return;
        if (daten.status === 'complete') {
            zelle.innerHTML = '<span class="hb-gut">'
                + '<i class="fas fa-check-circle"></i> Fertig</span>';
            return;
        }
        if (daten.status === 'failed') {
            zelle.innerHTML = '<span class="hb-schlecht">'
                + '<i class="fas fa-times-circle"></i> Fehlgeschlagen</span>';
            return;
        }
        const prozent = daten.progress || 0;
        // Maskieren: `progress_detail` kommt vom Server und enthaelt teils
        // Dateinamen. Befund von Nemotron im Sparring am 16.08.2026.
        const text = Htmltext.maskieren(
            (daten.progress_detail || daten.status || '').slice(0, 30));
        zelle.innerHTML = '<div class="inline-progress">'
            + `<span class="status-text"><i class="fas fa-spinner fa-spin"></i> ${text}</span>`
            + '<div class="progress-bar-mini"><div class="progress-fill-mini"'
            + ` style="width:${prozent}%"></div></div>`
            + `<span class="progress-pct">${prozent}%</span></div>`;
    }

    _fortschritt(daten) {
        const prozent = daten.progress || 0;
        const beschriftung = Auftragszeile.PHASEN[daten.status] || daten.status;
        const abzeichen = document.getElementById('detail-badge-' + this.id);
        if (abzeichen) {
            abzeichen.textContent = beschriftung;
            abzeichen.className = 'badge badge-' + daten.status;
        }
        this._setzen('detail-phase-', beschriftung);
        this._setzen('detail-pct-', prozent + '%');
        this._setzen('detail-text-', daten.progress_detail || '');
        const balken = document.getElementById('detail-fill-' + this.id);
        if (balken) balken.style.width = prozent + '%';
    }

    _setzen(vorsilbe, text) {
        const element = document.getElementById(vorsilbe + this.id);
        if (element) element.textContent = text;
    }

    /** Nach Ende des Laufs den Startknopf der Zeile wieder freigeben. */
    _startknopfFrei() {
        const knopf = this.zeile()?.querySelector('[data-aktion="start"]');
        if (!knopf) return;
        knopf.disabled = false;
        knopf.innerHTML = '<i class="fas fa-play"></i>';
    }

    _fertig(daten) {
        document.getElementById('detail-error-' + this.id)
            ?.classList.add('hb-versteckt');
        const aktionen = document.getElementById('detail-actions-' + this.id);
        if (aktionen) {
            aktionen.innerHTML =
                `<a class="btn btn-sm btn-primary" href="/process/${this.id}/result/">`
                + '<i class="fas fa-eye"></i> Ergebnis</a>'
                + (daten.bvh_file
                    ? ` <a class="btn btn-sm btn-secondary" href="/api/bvh/${this.id}/"`
                      + ' download><i class="fas fa-download"></i> BVH</a>' : '');
        }
        this._ergebnislink();
    }

    /** In der Tabellenzeile einen "Ergebnis"-Link ergaenzen, falls er fehlt. */
    _ergebnislink() {
        const zelle = this.zeile()?.querySelector('td:last-child');
        if (!zelle || zelle.querySelector('a[href*="result"]')) return;
        const link = document.createElement('a');
        link.className = 'btn btn-sm btn-primary';
        link.href = `/process/${this.id}/result/`;
        link.innerHTML = '<i class="fas fa-eye"></i> Ergebnis';
        zelle.insertBefore(link, zelle.firstChild);
    }

    _gescheitert(daten) {
        const fehler = document.getElementById('detail-error-' + this.id);
        if (fehler && daten.error) {
            fehler.classList.remove('hb-versteckt');
            fehler.innerHTML = '<strong>Fehler:</strong> '
                               + Htmltext.maskieren(daten.error);
        }
        const aktionen = document.getElementById('detail-actions-' + this.id);
        if (aktionen) aktionen.innerHTML = '';
    }
}
