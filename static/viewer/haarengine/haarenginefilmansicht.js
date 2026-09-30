/**
 * Haarenginefilmansicht — der Film der Genesis Haar Engine (Schritt „film": Figur mit Haar, BVH-Bewegung, gerendert) IN der
 * Hauptansicht. Der Knopf `#buehne-film` legt das Video über die 3D-Bühne; noch ein Klick zeigt wieder die Bühne. Ohne Film (Schritt
 * nicht gerechnet oder ohne BVH übersprungen) ist der Knopf versteckt.
 *
 * Die Adresse trägt die Rechenzeit des Laufs als Kennung — ein neuer Film heißt wieder `film_video.mp4`, der Browser zeigte sonst den
 * alten.
 */
export class Haarenginefilmansicht {

    constructor(seite) {
        this.seite = seite;
        this.knopf = document.getElementById('buehne-film');
        this.feld = document.getElementById('buehne');
        this.video = null;
        this.an = false;
        this._adresse = null;
        this.knopf.addEventListener('click', () => this.umschalten());
    }

    static adresse(z, seite) {
        const b = (z.ergebnis || {}).film || {};
        if (!b.video) return null;
        const kennung = encodeURIComponent(JSON.stringify(b.sekunden || {}));
        return `${seite.dateiAdresse('ergebnis', b.video)}?t=${kennung}`;
    }

    umschalten() {
        this.an = !this.an;
        this.zeigen(this.seite.zustand);
    }

    zeigen(z) {
        const adresse = Haarenginefilmansicht.adresse(z || {}, this.seite);
        this.knopf.hidden = !adresse;
        const an = this.an && !!adresse;
        this.knopf.classList.toggle('active', an);
        if (!an) {
            if (this.video) { this.video.pause(); this.video.hidden = true; }
            return;
        }
        if (!this.video) {
            this.video = document.createElement('video');
            this.video.className = 'haarengine-film';
            this.video.controls = true;
            this.video.muted = true;
            this.video.loop = true;
            this.feld.appendChild(this.video);
        }
        if (adresse !== this._adresse) {
            this._adresse = adresse;
            this.video.src = adresse;
        }
        this.video.hidden = false;
    }
}
