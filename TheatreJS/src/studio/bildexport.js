/**
 * Bildexport — Video aus der Bühne, Bild für Bild oder am Server.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 230 Zeilen in vier Funktionen,
 * die sich über sechs Oberflächen-Elemente und vier Zustandsvariablen im
 * Closure verstanden.
 *
 * DABEI EIN FEHLER GEFUNDEN. Am Ende von `exportBrowser` standen 27 Zeilen,
 * die aus einer frueheren Fassung stammten — der mit MediaRecorder, die einen
 * WebM-Blob erzeugte:
 *
 *     exportBtn.style.display = '';
 *     setTimeout(() => { progressDiv.style.display = 'none'; }, 3000);
 *
 *     if (s.format === 'webm') {
 *         const url = URL.createObjectURL(blob);      // <-- blob
 *         …
 *     } else {
 *         formData.append('video', blob, 'export.webm');   // <-- blob
 *         … zweiter Server-Aufruf nach /api/theatre/convert-video/ …
 *     }
 *
 * `blob` war die Variable aus dem `if (resp.ok)`-Block weiter oben und
 * ausserhalb davon nicht mehr sichtbar. Der Block lief also nach jedem
 * Browser-Export in einen `ReferenceError: blob is not defined` — unbemerkt,
 * weil er in einer async-Funktion ohne Auffangzweig steht und die Datei zu
 * diesem Zeitpunkt schon heruntergeladen war. Bei Format 'mp4' waere sogar ein
 * zweiter, sinnloser Server-Aufruf versucht worden. Die 27 Zeilen sind
 * entfallen; das WebM-Verfahren gibt es weiter in video-export.js.
 */
export class Bildexport {

    /** Nach so vielen Millisekunden verschwindet der Fortschrittsbalken. */
    static NACHLEUCHTEN_MS = 3000;

    /** Feste Auflösungen der Auswahlliste. */
    static AUFLOESUNGEN = {
        '720': [1280, 720], '1080': [1920, 1080],
        '1440': [2560, 1440], '2160': [3840, 2160],
    };

    /**
     * @param {Object} buehne  { renderer, scene, camera, canvas }
     * @param {Object} abspieler  Zugriff auf die laufende Animation:
     *        { dauer(), zeitSetzen(t), pausieren(), fortsetzen(), laeuft() }
     */
    constructor(buehne, abspieler) {
        this.buehne = buehne;
        this.abspieler = abspieler;
        this.abgebrochen = false;
        this.elemente = {
            start: document.getElementById('export-start-btn'),
            abbruch: document.getElementById('export-cancel-btn'),
            balkenfeld: document.getElementById('export-progress'),
            balken: document.getElementById('export-progress-bar'),
            text: document.getElementById('export-progress-text'),
        };
    }

    /** Knöpfe verdrahten. Gibt sich selbst zurück, damit man verketten kann. */
    verdrahten() {
        const { start, abbruch } = this.elemente;
        if (start) {
            start.addEventListener('click', async () => {
                const art = document.getElementById('export-method')?.value;
                if (art === 'browser') await this.imBrowser();
                else await this.amServer();
            });
        }
        if (abbruch) {
            abbruch.addEventListener('click', () => { this.abgebrochen = true; });
        }
        return this;
    }

    // ------------------------------------------------------------ Einstellungen

    einstellungen() {
        const wahl = document.getElementById('export-resolution')?.value;
        const [breite, hoehe] = this._masse(wahl);
        return {
            width: breite, height: hoehe,
            fps: this._zahl('export-fps', 30),
            format: document.getElementById('export-format')?.value || 'mp4',
            crf: this._zahl('export-crf', 18),
            startTime: this._kommazahl('export-start', 0),
            endTime: this._kommazahl('export-end', 0),
            bg: document.getElementById('export-bg')?.value || 'scene',
            cropX: this._zahl('export-crop-x', 0),
            cropY: this._zahl('export-crop-y', 0),
            cropW: this._zahl('export-crop-w', 0),
            cropH: this._zahl('export-crop-h', 0),
        };
    }

    _masse(wahl) {
        if (wahl === 'viewport') {
            const leinwand = this.buehne.canvas;
            return [leinwand.clientWidth, leinwand.clientHeight];
        }
        if (wahl === 'custom') {
            return [this._zahl('export-width', 1920), this._zahl('export-height', 1080)];
        }
        return Bildexport.AUFLOESUNGEN[wahl] || [1920, 1080];
    }

    _zahl(id, ersatz) {
        return parseInt(document.getElementById(id)?.value, 10) || ersatz;
    }

    _kommazahl(id, ersatz) {
        return parseFloat(document.getElementById(id)?.value) || ersatz;
    }

    /** Zeitspanne aus den Einstellungen und der tatsaechlichen Dauer. */
    zeitspanne(s) {
        const dauer = this.abspieler.dauer() || 10;
        const von = s.startTime || 0;
        const bis = (s.endTime > von) ? s.endTime : dauer;
        return { von, bis, bilder: Math.ceil((bis - von) * s.fps) };
    }

    // ------------------------------------------------------------- Oberfläche

    fortschritt(prozent, text) {
        const { balkenfeld, balken, text: anzeige } = this.elemente;
        if (balkenfeld) balkenfeld.style.display = '';
        if (balken) balken.style.width = prozent + '%';
        if (anzeige) anzeige.textContent = text || (prozent.toFixed(0) + '%');
    }

    _laufendAnzeigen(laeuft) {
        const { start, abbruch } = this.elemente;
        if (start) start.style.display = laeuft ? 'none' : '';
        if (abbruch) abbruch.style.display = laeuft ? '' : 'none';
    }

    _aufraeumen() {
        this._laufendAnzeigen(false);
        setTimeout(() => {
            if (this.elemente.balkenfeld) this.elemente.balkenfeld.style.display = 'none';
        }, Bildexport.NACHLEUCHTEN_MS);
    }

    // ------------------------------------------------------------ Bild fuer Bild

    /**
     * Jedes Bild einzeln rendern, als PNG einsammeln und vom Server mit ffmpeg
     * zusammensetzen lassen. Genauer als die Echtzeitaufnahme, aber langsamer.
     */
    async imBrowser() {
        const s = this.einstellungen();
        const { von, bis, bilder } = this.zeitspanne(s);
        this._laufendAnzeigen(true);
        this.abgebrochen = false;
        this.fortschritt(0, `0 / ${bilder} Bilder …`);

        const liefWeiter = this.abspieler.laeuft();
        this.abspieler.pausieren();

        const aufnahmen = await this._bilderSammeln(s, von, bilder);

        if (liefWeiter) this.abspieler.fortsetzen();
        if (this.abgebrochen || !aufnahmen.length) {
            this._laufendAnzeigen(false);
            if (this.elemente.balkenfeld) this.elemente.balkenfeld.style.display = 'none';
            return;
        }

        this.fortschritt(100, 'Sende an Server für ffmpeg …');
        await this._kodierenLassen(s, aufnahmen);
        this._aufraeumen();
    }

    async _bilderSammeln(s, von, bilder) {
        const { renderer, scene, camera, canvas } = this.buehne;
        const aufnahmen = [];
        for (let nummer = 0; nummer < bilder; nummer++) {
            if (this.abgebrochen) break;
            const zeit = von + nummer / s.fps;
            this.abspieler.zeitSetzen(zeit);
            renderer.render(scene, camera);
            aufnahmen.push(await new Promise(fertig => canvas.toBlob(fertig, 'image/png')));
            if (nummer % 10 === 0 || nummer === bilder - 1) {
                this.fortschritt(((nummer + 1) / bilder) * 100,
                    `${nummer + 1} / ${bilder} Bilder (${zeit.toFixed(1)}s)`);
            }
            // Der Oberfläche Luft lassen, sonst friert die Seite ein.
            await new Promise(weiter => setTimeout(weiter, 0));
        }
        return aufnahmen;
    }

    async _kodierenLassen(s, aufnahmen) {
        const daten = new FormData();
        aufnahmen.forEach((bild, i) => {
            daten.append('frames', bild, `${String(i).padStart(6, '0')}.png`);
        });
        for (const [feld, wert] of [['fps', s.fps], ['format', s.format],
                                    ['crf', s.crf], ['width', s.width],
                                    ['height', s.height]]) {
            daten.append(feld, wert);
        }
        await this._holenUndSpeichern('/api/theatre/encode-frames/',
                                     { method: 'POST', body: daten }, s.format,
                                     'Encoding fehlgeschlagen');
    }

    // ----------------------------------------------------------- Server-Export

    /** Der Server rendert selbst (Playwright + ffmpeg). */
    async amServer() {
        const s = this.einstellungen();
        const { von, bis, bilder } = this.zeitspanne(s);
        this._laufendAnzeigen(true);
        this.abgebrochen = false;
        this.fortschritt(0, `Server-Rendering: ${bilder} Bilder `
            + `(${(bis - von).toFixed(1)}s @ ${s.fps} fps) …`);

        if (this.elemente.abbruch) {
            this.elemente.abbruch.onclick = () => {
                this.abgebrochen = true;
                this._laufendAnzeigen(false);
                if (this.elemente.balkenfeld) {
                    this.elemente.balkenfeld.style.display = 'none';
                }
            };
        }

        await this._holenUndSpeichern('/api/theatre/render-video/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                width: s.width, height: s.height, fps: s.fps,
                format: s.format, crf: s.crf,
                start_time: von, end_time: bis,
                background: s.bg,
                crop_x: s.cropX, crop_y: s.cropY,
                crop_w: s.cropW, crop_h: s.cropH,
                scene_url: window.location.href,
            }),
        }, s.format, 'Server-Export fehlgeschlagen');
        this._aufraeumen();
    }

    /**
     * Anfrage stellen und die Antwort als Datei speichern.
     * Beide Exportwege endeten mit demselben Block — Blob holen, Link bauen,
     * klicken, Objekt-URL freigeben, Fehler melden.
     */
    async _holenUndSpeichern(adresse, anfrage, format, fehlertext) {
        try {
            const antwort = await fetch(adresse, anfrage);
            if (!antwort.ok) {
                alert(fehlertext + ': ' + await antwort.text());
                return;
            }
            this._speichern(await antwort.blob(), format);
            this.fortschritt(100, 'Export fertig!');
        } catch (fehler) {
            alert('Export-Fehler: ' + fehler.message);
        }
    }

    _speichern(blob, format) {
        const endung = format === 'png' ? 'zip' : format;
        const adresse = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = adresse;
        link.download = `theatre_export.${endung}`;
        link.click();
        URL.revokeObjectURL(adresse);
    }
}
