/**
 * Spielerbedienung — Knoepfe, Tastatur, Zeitleiste, Videoereignisse.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026).
 */

/** Sekunden je Sprungknopf. */
const SPRUENGE = [
    ['btnSkipBack10', -10], ['btnSkipBack1', -1],
    ['btnSkipFwd1', 1], ['btnSkipFwd10', 10],
];

export class Spielerbedienung {
    constructor(spieler) {
        this.spieler = spieler;
        this.zustand = spieler.zustand;
        this.video = spieler.video;
        this.abspielsymbol = document.getElementById('playIcon');
        this.zeitleiste = document.getElementById('timelineSlider');
        this.zeitAnzeige = document.getElementById('timeCurrent');
        this.dauerAnzeige = document.getElementById('timeDuration');
        this.tempoknoepfe = document.querySelectorAll('.speed-btn');
    }

    anbinden() {
        this._knoepfe();
        this._zeitleiste();
        this._tempo();
        this._tastatur();
        this._videoereignisse();
        this._nummernknopf();
    }

    _an(id, tun) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('click', tun);
        else console.warn('[bvh_player] Missing button:', id);
    }

    _knoepfe() {
        const start = document.getElementById('btnPlayPause');
        if (start) start.addEventListener('click', () => this.umschalten());
        this._an('btnStop', () => this.anhalten());
        for (const [id, sekunden] of SPRUENGE) {
            this._an(id, () => this.zustand.springen(this.zustand.zeit + sekunden));
        }
        this._an('btnFrameBack', () => this.bildweise(-1));
        this._an('btnFrameFwd', () => this.bildweise(1));
    }

    _zeitleiste() {
        if (!this.zeitleiste) return;
        this.zeitleiste.addEventListener('input', () => {
            this.zustand.springen(parseFloat(this.zeitleiste.value));
        });
    }

    _tempo() {
        this.tempoknoepfe.forEach(knopf => {
            knopf.addEventListener('click',
                () => this.tempoSetzen(parseFloat(knopf.dataset.speed)));
        });
    }

    _tastatur() {
        document.addEventListener('keydown', (e) => {
            const feld = e.target.tagName;
            if (feld === 'TEXTAREA' || feld === 'INPUT') return;
            if (e.key === ' ') {
                e.preventDefault();
                this.umschalten();
            } else if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.bildweise(e.ctrlKey ? -10 : -1);
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.bildweise(e.ctrlKey ? 10 : 1);
            } else if (e.key === 'n' || e.key === 'N') {
                this.spieler.nummernUmschalten();
            }
        });
    }

    _nummernknopf() {
        const knopf = document.getElementById('btnToggleIdx');
        if (!knopf) return;
        knopf.classList.add('active');          // Nummern sind zunaechst an
        knopf.addEventListener('click', () => {
            knopf.classList.toggle('active', this.spieler.nummernUmschalten());
        });
    }

    _videoereignisse() {
        this.video.addEventListener('play', () => {
            this.zustand.laeuft = true;
            this.zustand.zeigen = true;
            this._symbol(true);
        });
        this.video.addEventListener('pause', () => {
            this.zustand.laeuft = false;
            this._symbol(false);
        });
        this.video.addEventListener('ended', () => {
            this.zustand.laeuft = false;
            this._symbol(false);
        });
        this.video.addEventListener('seeked', () => { this.zustand.zeigen = true; });
        this.video.addEventListener('loadedmetadata', () => this.dauerUebernehmen());
        this.video.addEventListener('error', () => {
            console.warn('[bvh_player] Video error — using BVH clock fallback');
        });
        // Schon geladen (aus dem Zwischenspeicher)? Dann sofort uebernehmen.
        if (this.video.duration && !isNaN(this.video.duration)) {
            this.dauerUebernehmen();
        }
    }

    _symbol(laeuft) {
        if (this.abspielsymbol) {
            this.abspielsymbol.className = laeuft ? 'fas fa-pause' : 'fas fa-play';
        }
    }

    umschalten() {
        if (this.zustand.videoBrauchbar) {
            // Der Zustand kommt ueber die play/pause-Ereignisse zurueck.
            if (this.video.paused) {
                this.video.play().catch(
                    e => console.warn('[bvh_player] play() rejected:', e.message));
            } else {
                this.video.pause();
            }
            return;
        }
        this.zustand.laeuft = !this.zustand.laeuft;
        this.zustand.zeigen = true;
        this.zustand.letzterStempel = 0;        // Zeitdifferenz neu beginnen
        this._symbol(this.zustand.laeuft);
    }

    bildweise(richtung) {
        const schritt = richtung / this.spieler.fps;
        if (this.zustand.videoBrauchbar) {
            this.video.pause();
        } else {
            this.zustand.laeuft = false;
            this._symbol(false);
        }
        this.zustand.springen(this.zustand.zeit + schritt);
    }

    tempoSetzen(wert) {
        this.zustand.tempo = wert;
        if (this.zustand.videoBrauchbar) this.video.playbackRate = wert;
        this.spieler.skelett.tempo(wert);
        this.tempoknoepfe.forEach(knopf => {
            knopf.classList.toggle('active',
                                   parseFloat(knopf.dataset.speed) === wert);
        });
    }

    anhalten() {
        if (this.zustand.videoBrauchbar) {
            this.video.pause();
            this.video.currentTime = 0;
        }
        this.zustand.zuruecksetzen();
        this._symbol(false);
    }

    /** Gesamtdauer in die Zeitleiste schreiben. */
    dauerUebernehmen() {
        const dauer = this.zustand.dauer;
        if (!(dauer > 0)) return;
        if (this.zeitleiste) this.zeitleiste.max = dauer;
        if (this.dauerAnzeige) {
            this.dauerAnzeige.textContent = Spielerbedienung.zeittext(dauer);
        }
    }

    /** Laufende Anzeige: Zeit plus Bildnummern beider Quellen. */
    standAnzeigen(skelett, daten, fps) {
        if (!(this.zustand.dauer > 0)) return;
        if (this.zeitleiste) this.zeitleiste.value = this.zustand.zeit;
        if (!this.zeitAnzeige) return;
        const bilddauer = skelett.bilddauer(fps);
        const bild3d = skelett.klipdauer > 0
            ? Math.floor(this.zustand.fortschritt * skelett.klipdauer / bilddauer) : 0;
        const gesamt3d = skelett.klipdauer > 0
            ? Math.round(skelett.klipdauer / bilddauer) : 0;
        const bild2d = Math.max(0, daten.bildnummer(this.zustand.fortschritt));
        this.zeitAnzeige.textContent = Spielerbedienung.zeittext(this.zustand.zeit)
            + `  2D:${bild2d}/${daten.bildzahl} 3D:${bild3d}/${gesamt3d}`;
    }

    static zeittext(sekunden) {
        if (!sekunden || isNaN(sekunden)) return '00:00';
        const m = Math.floor(sekunden / 60);
        const s = Math.floor(sekunden % 60);
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
}
