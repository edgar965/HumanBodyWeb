import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderreferenz — das Referenzvideo (Franks Ergebnis) im Rahmen rechts neben den Vorlagebildern (04.10.2026).
 *
 * Edgar: „füge franks ergebnis video rechts neben den Vorlagebildern als Frame ein, mit play soll ich das abspielen können" (Datei `Model_Jobs/Frank/Randy/vid2.mp4`).
 * Der Pfad der Videodatei steht im Feld; „Übernehmen" lässt den Server sie in den Auftrag kopieren (`POST …/referenz/`), danach spielt der Rahmen sie ab
 * (Datei-Endpunkt `…/datei/referenz/<name>`, mit Bereichsanfragen: Springen im Video geht). Die Klasse hängt nicht an `Engine2d3dKleiderseite`: Sie liest den Zustand einmal
 * beim Start und setzt ihn danach selbst fort (das Video ändert sich nur durch „Übernehmen").
 */
export class Engine2d3dKleiderreferenz {

    static async starten(jobId) {
        const rahmen = new Engine2d3dKleiderreferenz(jobId);
        await rahmen.laden();
        return rahmen;
    }

    constructor(jobId) {
        this.jobId = jobId;
        const $ = id => document.getElementById(id);
        this.video = $('referenz-video');
        this.pfad = $('referenz-pfad');
        this.knopf = $('referenz-uebernehmen');
        this.meldung = $('referenz-meldung');
        this.knopf.addEventListener('click', () => this.uebernehmen());
        this.pfad.addEventListener('keydown', e => { if (e.key === 'Enter') this.uebernehmen(); });
    }

    async laden() {
        try {
            const zustand = await Serverabruf.json(`/api/engine2d3dkleider/${this.jobId}/zustand/`);
            this.zeigen(zustand.referenz || {});
        } catch (fehler) {
            this._sagen(`Referenzvideo: Zustand nicht gelesen (${fehler.message})`, true);
        }
    }

    zeigen(referenz) {
        if (referenz.quelle && !this.pfad.value) this.pfad.value = referenz.quelle;
        if (!referenz.video) {
            this._sagen('Noch kein Referenzvideo — Pfad der Videodatei eintragen und „Übernehmen“.', false);
            return;
        }
        const adresse = `/api/engine2d3dkleider/${this.jobId}/datei/referenz/${encodeURIComponent(referenz.video)}?v=${referenz.bytes}`;
        if (!this.video.src.endsWith(adresse)) this.video.src = adresse;
        this._sagen(`${referenz.video} · ${(referenz.bytes / 1048576).toFixed(1)} MB`, false);
    }

    async uebernehmen() {
        this.knopf.disabled = true;
        this._sagen('Kopiere das Video in den Auftrag …', false);
        try {
            const antwort = await Serverabruf.senden(`/api/engine2d3dkleider/${this.jobId}/referenz/`, { pfad: this.pfad.value.trim() });
            if (antwort.error) throw new Error(antwort.error);
            this.zeigen(antwort.referenz);
        } catch (fehler) {
            this._sagen(`Nicht übernommen: ${fehler.daten?.error || fehler.message}`, true);
        } finally {
            this.knopf.disabled = false;
        }
    }

    _sagen(text, schlecht) {
        this.meldung.textContent = text;
        this.meldung.classList.toggle('hb-schlecht', !!schlecht);
    }
}
