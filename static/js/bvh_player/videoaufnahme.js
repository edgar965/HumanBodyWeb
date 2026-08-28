import { Aufnahmebalken } from './aufnahmebalken.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

/**
 * Videoaufnahme — die 3D-Ansicht als WebM aufzeichnen, während das Video läuft.
 *
 * WARUM ALS MODUL (Befund `doppelcode`, 28.08.2026): Dieser Ablauf stand als
 * 130-Zeilen-Block INLINE in `job_result.html` UND `standalone_result.html` —
 * bis auf zehn Kommentarzeilen wortgleich. Zwei Kopien einer Aufnahme, die
 * Video, Zeichenfläche, MediaRecorder und einen Serverupload koordiniert:
 * Wer an einer davon etwas richtet, hat es in der anderen nicht.
 *
 * DIE REIHENFOLGE IST NICHT BELIEBIG
 * ==================================
 * Erst anhalten und auf Bild 0 springen, dann ZWEI Bilder warten, dann
 * aufnehmen. Ohne die zwei Bilder steht am Anfang der Aufnahme noch der alte
 * Stand der 3D-Szene — sie zieht der Videoposition immer ein Bild hinterher.
 */
export class Videoaufnahme {
    /** Bitrate der Aufnahme — 8 Mbit/s reichen für 1080p-Figuren. */
    static BITRATE = 8_000_000;

    /** So lange bleibt der fertige Balken stehen, damit „100 %" lesbar ist. */
    static NACHLEUCHTEN_MS = 1500;

    /** Bevorzugtes Format; der Rückfall gilt für Browser ohne VP9. */
    static VP9 = 'video/webm;codecs=vp9';
    static WEBM = 'video/webm';

    /**
     * @param {Object} teile {canvas, video, knopf, fps, dateiname, ablageUrl}
     */
    constructor(teile) {
        Object.assign(this, teile);
    }

    static format() {
        return MediaRecorder.isTypeSupported(Videoaufnahme.VP9)
            ? Videoaufnahme.VP9 : Videoaufnahme.WEBM;
    }

    async laufen() {
        const balken = new Aufnahmebalken(this.canvas.parentElement);
        const knopftext = this.knopf.innerHTML;
        this.knopf.disabled = true;
        this.knopf.innerHTML =
            '<i class="fas fa-circle fehlertext"></i> Aufnahme...';
        try {
            const blob = await this._aufzeichnen(balken);
            balken.fertig();
            await this._ablegen(blob, balken);
            this._herunterladen(blob);
            await new Promise(r => setTimeout(r,
                                              Videoaufnahme.NACHLEUCHTEN_MS));
        } finally {
            // `finally`: Bleibt der Knopf nach einem Fehler gesperrt, sieht
            // die Seite kaputt aus, obwohl nur die Aufnahme misslang.
            balken.weg();
            this.knopf.disabled = false;
            this.knopf.innerHTML = knopftext;
            this.video.pause();
        }
    }

    async _aufzeichnen(balken) {
        this.video.pause();
        this.video.currentTime = 0;
        await new Promise(r => { this.video.onseeked = r; });
        // Zwei Bilder warten — siehe Klassenkopf.
        await new Promise(r => requestAnimationFrame(r));
        await new Promise(r => requestAnimationFrame(r));

        const format = Videoaufnahme.format();
        const stuecke = [];
        const aufnehmer = new MediaRecorder(
            this.canvas.captureStream(this.fps),
            { mimeType: format, videoBitsPerSecond: Videoaufnahme.BITRATE });
        aufnehmer.ondataavailable = (e) => {
            if (e.data.size > 0) stuecke.push(e.data);
        };
        const beendet = new Promise(r => { aufnehmer.onstop = r; });

        aufnehmer.start();
        this.video.play();
        balken.verfolgen(this.video);
        await this._bisZumEnde(aufnehmer);
        if (aufnehmer.state === 'recording') aufnehmer.stop();
        await beendet;
        return new Blob(stuecke, { type: format });
    }

    /** Bis das Video zu Ende ist — oder der Nutzer es anhält. */
    _bisZumEnde(aufnehmer) {
        return new Promise(loslassen => {
            this.video.onended = loslassen;
            this.video.onpause = () => {
                // Eine halbe Sekunde Spielraum: Der Browser meldet `pause`
                // auch am regulaeren Ende, und dann greift `onended`.
                if (this.video.currentTime < this.video.duration - 0.5) {
                    aufnehmer.stop();
                    loslassen();
                }
            };
        });
    }

    async _ablegen(blob, balken) {
        const formular = new FormData();
        formular.append('video', blob, this.dateiname);
        try {
            const antwort = await fetch(this.ablageUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': Videoaufnahme._csrf() },
                body: formular,
            });
            const daten = await antwort.json();
            if (daten.ok) balken.melden('Saved!');
        } catch (fehler) {
            // Kein Abbruch: Das Herunterladen unten geht trotzdem, und der
            // Nutzer hat sein Video.
            Protokoll.warnung('Videoaufnahme',
                              'Ablage auf dem Server misslungen:', fehler);
        }
    }

    static _csrf() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value
            || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    }

    _herunterladen(blob) {
        const adresse = URL.createObjectURL(blob);
        const verweis = document.createElement('a');
        verweis.href = adresse;
        verweis.download = this.dateiname;
        document.body.appendChild(verweis);
        verweis.click();
        document.body.removeChild(verweis);
        URL.revokeObjectURL(adresse);
    }
}
