/**
 * Blendermodellblenderfilm — der Film aus Blender (Schritt „blender": Figur mit Kostüm, BVH-Bewegung, gerendert) IN
 * der Hauptansicht (Edgar, 30.09.2026: „mach einen Button für Blender-Ausgabe"). Der Knopf `#buehne-blenderfilm`
 * legt das Video über die 3D-Bühne; noch ein Klick zeigt wieder die Bühne. Ohne Film (Schritt nicht gerechnet oder
 * ohne BVH übersprungen) ist der Knopf versteckt.
 *
 * Die Adresse trägt die Rechenzeit des Laufs als Kennung — ein neuer Film heißt wieder `blender_video.mp4`, der
 * Browser zeigte sonst den alten.
 */
export class Blendermodellblenderfilm {

    constructor(seite) {
        this.seite = seite;
        this.knopf = document.getElementById('buehne-blenderfilm');
        this.feld = document.getElementById('buehne');
        this.video = null;
        this.an = false;
        this._adresse = null;
        this.knopf.addEventListener('click', () => this.umschalten());
    }

    static adresse(z, seite) {
        const b = (z.ergebnis || {}).blender || {};
        if (!b.video) return null;
        const kennung = encodeURIComponent(JSON.stringify(b.sekunden || {}));
        return `${seite.dateiAdresse('ergebnis', b.video)}?t=${kennung}`;
    }

    umschalten() {
        this.an = !this.an;
        this.zeigen(this.seite.zustand);
    }

    /** Liegt der Film gerade über der Bühne? Dann steuern Knopf und Leertaste der Animationsleiste ihn. */
    sichtbar() {
        return this.an && !!this.video && !this.video.hidden;
    }

    /** Abspielen / Pause des Films (Knopf `#anim-play`, Leertaste). */
    abspielen() {
        if (!this.sichtbar()) return;
        if (!this.video.paused) {
            this.video.pause();
            return;
        }
        this.video.play().catch(fehler => this.seite.buehne._melden(`Film nicht abspielbar: ${fehler.message}`));
    }

    zeigen(z) {
        const adresse = Blendermodellblenderfilm.adresse(z || {}, this.seite);
        this.knopf.hidden = !adresse;
        const an = this.an && !!adresse;
        this.knopf.classList.toggle('active', an);
        if (!an) {
            if (this.video) { this.video.pause(); this.video.hidden = true; }
            this.seite.animation?.knopfNeu();
            return;
        }
        if (!this.video) {
            this.video = document.createElement('video');
            this.video.className = 'blendermodell-blenderfilm';
            this.video.controls = true;
            this.video.muted = true;
            this.video.loop = true;
            // Das Zeichen des Knopfs folgt dem Film, auch wenn er über die eigene Steuerung des Videos angehalten wird.
            this.video.addEventListener('play', () => this.seite.animation?.knopf(true));
            this.video.addEventListener('pause', () => { if (this.sichtbar()) this.seite.animation?.knopf(false); });
            this.feld.appendChild(this.video);
        }
        if (adresse !== this._adresse) {
            this._adresse = adresse;
            this.video.src = adresse;
        }
        this.video.hidden = false;
    }
}
