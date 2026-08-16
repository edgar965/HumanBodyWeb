import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';
import { Pipelinefelder } from './pipelinefelder.js';
import { Videoablage } from './videoablage.js';

/**
 * Videowahl — die Liste der hochgeladenen Videos, das Ablegen neuer Dateien und
 * der Knopf "Pipeline starten".
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026):
 * `startSelectedVideo` (26 Zeilen) und die Radio-Zuhoerer mit dem Merken der
 * Auswahl. Das Ablegen von Dateien steht in `Videoablage` — es ist auf der
 * alten Upload-Seite dasselbe.
 *
 * Dabei behoben: Beide `fetch('/api/ui-prefs/')`-Aufrufe liefen ohne jede
 * Fehlerbehandlung — schlug das Merken fehl, blieb es unbemerkt, und beim
 * naechsten Aufruf der Seite war die Auswahl weg, ohne dass jemand wusste,
 * warum.
 */
export class Videowahl {

    static VORGABEN = '/api/ui-prefs/';
    static ANLEGEN = '/api/job/create-from-file/';
    /** Nach dem Start geht es auf die Statusseite. */
    static WEITER = '/process/VideoToBVH/';

    static aufbauen(pipelinewahl) {
        return new Videowahl(pipelinewahl).aufbauen();
    }

    constructor(pipelinewahl) {
        this.pipelinewahl = pipelinewahl;
        this.knopf = document.getElementById('startSelectedBtn');
    }

    aufbauen() {
        document.querySelectorAll('input[name="selected_video"]')
            .forEach(feld => {
                feld.addEventListener('change', () => this.gewaehlt(feld));
            });
        this.knopf?.addEventListener('click', () => this.starten());
        Videoablage.aufbauen();
        return this;
    }

    /** Auswahl hervorheben und auf dem Server merken. */
    gewaehlt(feld) {
        document.querySelectorAll('.video-file-item').forEach(eintrag => {
            eintrag.classList.toggle('selected',
                                     eintrag.querySelector('input').checked);
        });
        this._merken({ selected_video_path: feld.value });
    }

    async _merken(werte) {
        try {
            await Serverabruf.senden(Videowahl.VORGABEN, werte);
        } catch (fehler) {
            Protokoll.warnung('Auftraege', 'Auswahl nicht gemerkt:',
                              fehler.message);
        }
    }

    async starten() {
        const gewaehlt = document.querySelector(
            'input[name="selected_video"]:checked');
        if (!gewaehlt) { alert('Bitte zuerst ein Video auswählen.'); return; }
        const pipeline = this.pipelinewahl.gewaehlt();
        if (!pipeline) { alert('Bitte eine Pipeline auswählen.'); return; }

        const parameter = Pipelinefelder.sammeln(pipeline);
        this._merken({ last_pipeline: pipeline,
                       selected_video_path: gewaehlt.value });
        this._laufend(true);
        try {
            const daten = await Serverabruf.senden(Videowahl.ANLEGEN, {
                video_path: gewaehlt.value, pipeline,
                pipeline_params: parameter,
            });
            if (!daten.ok) throw new Error(daten.error || 'Unbekannter Fehler');
            window.location.href = Videowahl.WEITER;
        } catch (fehler) {
            alert('Start fehlgeschlagen: ' + fehler.message);
            this._laufend(false);
        }
    }

    _laufend(an) {
        if (!this.knopf) return;
        this.knopf.disabled = an;
        this.knopf.innerHTML = an
            ? '<i class="fas fa-spinner fa-spin"></i> Starte...'
            : '<i class="fas fa-play"></i> Pipeline starten';
    }
}
