/**
 * Videoaufnahme — der Dialog „Als MP4 exportieren".
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Der Knopf hat ZWEI Bedeutungen,
 * und das ist Absicht: Beim ersten Klick startet die Aufnahme und **der Dialog
 * schließt sich** — der Nutzer muss die Animation ja abspielen und die Bühne
 * bedienen können. Der zweite Klick (Dialog wieder geöffnet) stoppt und
 * verarbeitet.
 *
 * `mp4` geht über den Server (ffmpeg wandelt das WebM des Browsers um), `webm`
 * lädt direkt herunter. Browser können MP4 nicht selbst aufnehmen.
 */
export class Videoaufnahme {

    static BITRATEN = { low: 2_000_000, medium: 5_000_000,
                        high: 8_000_000, ultra: 15_000_000 };
    static AUFLOESUNGEN = { '720p': [1280, 720], '1080p': [1920, 1080],
                            '1440p': [2560, 1440], '4k': [3840, 2160] };
    static WANDLER = '/api/theatre/convert-video/';

    static KNOPF_START = '<i class="fas fa-circle fehlertext"></i> Aufnahme starten';
    static KNOPF_STOPP = '<i class="fas fa-stop fehlertext"></i> '
        + 'Aufnahme stoppen &amp; exportieren';

    constructor(aufnehmer, bild) {
        this.aufnehmer = aufnehmer;      // VideoExporter
        this.bild = bild;                // { renderer, camera }
        this.menue = document.getElementById('menu-export-mp4');
        this.dialog = document.getElementById('modal-export-mp4');
        this.knopf = document.getElementById('export-mp4-start');
        this.status = document.getElementById('export-mp4-status');
    }

    verdrahten() {
        if (!this.menue || !this.dialog) return this;
        this.menue.addEventListener('click', () => this.oeffnen());
        this.knopf.addEventListener('click', () => this.umschalten());
        return this;
    }

    // ------------------------------------------------------------------ Dialog

    oeffnen() {
        this._vorbelegen();
        this.dialog.classList.add('open');
        this.status.style.display = 'none';
        this.knopf.innerHTML = this.aufnehmer.isRecording
            ? Videoaufnahme.KNOPF_STOPP : Videoaufnahme.KNOPF_START;
    }

    /** Die Werte aus den Projekteinstellungen vorbelegen. */
    _vorbelegen() {
        const werte = window._theatreVideoSettings || {};
        for (const [kennung, wert] of [
                ['export-mp4-resolution', werte.resolution],
                ['export-mp4-fps', werte.fps && String(werte.fps)],
                ['export-mp4-quality', werte.quality],
                ['export-mp4-format', werte.format]]) {
            const feld = document.getElementById(kennung);
            if (feld && wert) feld.value = wert;
        }
    }

    _melden(text, art) {
        this.status.style.display = 'block';
        this.status.className = 'export-status ' + art;
        this.status.textContent = text;
    }

    _wert(kennung, ersatz) {
        return document.getElementById(kennung)?.value || ersatz;
    }

    // ----------------------------------------------------------------- Aufnahme

    umschalten() {
        return this.aufnehmer.isRecording ? this.beenden() : this.starten();
    }

    starten() {
        const bilder = parseInt(this._wert('export-mp4-fps', '30')) || 30;
        const guete = this._wert('export-mp4-quality', 'high');
        const aufloesung = this._wert('export-mp4-resolution', '1080p');
        const [breite, hoehe] = Videoaufnahme.AUFLOESUNGEN[aufloesung]
            || Videoaufnahme.AUFLOESUNGEN['1080p'];
        this.aufnehmer.start({
            fps: bilder,
            bitrate: Videoaufnahme.BITRATEN[guete] || Videoaufnahme.BITRATEN.high,
            width: breite, height: hoehe,
            renderer: this.bild.renderer, camera: this.bild.camera,
        });
        this._melden(`Aufnahme läuft (${aufloesung}, ${bilder}fps)... `
                     + 'Spiele die Animation ab und klicke dann "Stoppen".',
                     'export-status-laeuft');
        this.knopf.innerHTML = Videoaufnahme.KNOPF_STOPP;
        // Dialog schliessen, damit die Buehne bedienbar ist.
        this.dialog.classList.remove('open');
    }

    async beenden() {
        this.knopf.disabled = true;
        this._melden('Aufnahme gestoppt. Verarbeite...', 'export-status-laeuft');
        const format = this._wert('export-mp4-format', 'mp4');
        const name = Videoaufnahme._dateiname(
            this._wert('export-mp4-filename', 'theatre-export'), format);
        try {
            if (format === 'mp4') {
                this._melden('Konvertiere zu MP4 (ffmpeg)...', 'export-status-laeuft');
                await this.aufnehmer.stopAndUpload(Videoaufnahme.WANDLER, name);
            } else {
                await this.aufnehmer.stopAndDownload(name);
            }
            this._melden('Export erfolgreich: ' + name, 'export-status-fertig');
        } catch (fehler) {
            this._melden('Fehler: ' + fehler.message, 'export-status-fehler');
        }
        this.knopf.disabled = false;
        this.knopf.innerHTML = Videoaufnahme.KNOPF_START;
    }

    /** Endung an das gewählte Format angleichen. */
    static _dateiname(name, format) {
        const endung = format === 'webm' ? '.webm' : '.mp4';
        return name.endsWith(endung) ? name : name.replace(/\.\w+$/, '') + endung;
    }
}
