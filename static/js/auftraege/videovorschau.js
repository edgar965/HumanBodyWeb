/**
 * Videovorschau — der Vorschau-Bereich der Liste verarbeiteter Videos.
 *
 * Herausgeloest aus templates/processed.html (Umbau 16.08.2026): 16 Zeilen
 * inline mit fünf `var` und drei onclick-Attributen.
 *
 * Die Quelle wird beim Schliessen geleert. Das ist Absicht und kein
 * Aufräumtick: Ein Video, dessen `src` gesetzt bleibt, laedt im Hintergrund
 * weiter, auch wenn der Bereich unsichtbar ist.
 */
export class Videovorschau {

    static aufbauen() {
        return new Videovorschau().aufbauen();
    }

    constructor() {
        this.bereich = document.getElementById('videoPreview');
        this.video = document.getElementById('previewVideo');
        this.titel = document.getElementById('previewTitle');
    }

    aufbauen() {
        document.querySelectorAll('[data-video]').forEach(element => {
            element.addEventListener('click', () => {
                this.zeigen(element.dataset.video, element.dataset.videoname);
            });
        });
        document.getElementById('previewClose')
            ?.addEventListener('click', () => this.schliessen());
        return this;
    }

    zeigen(adresse, name) {
        if (!this.bereich || !this.video) return;
        this.video.src = adresse;
        if (this.titel) this.titel.textContent = name || '';
        this.bereich.classList.add('visible');
        // `play()` liefert ein Versprechen, das mit AbortError bricht, wenn
        // vorher `pause()` kommt (Schliessen kurz nach dem Oeffnen). Ohne
        // diesen Fänger steht die Ausnahme in der Konsole, obwohl nichts
        // kaputt ist — im Browser gemessen am 16.08.2026.
        this.video.play()?.catch(() => {});
    }

    schliessen() {
        if (!this.bereich || !this.video) return;
        this.video.pause();
        this.video.src = '';
        this.bereich.classList.remove('visible');
    }
}
