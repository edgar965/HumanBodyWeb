/**
 * Abspieler — Wiedergabe, Zeitleiste und Tempo der Bühne.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 137 Zeilen, acht
 * Oberflaechen-Elemente und vier Zustandsvariablen (`isPlaying`, `currentTime`,
 * `animDuration`, `playbackSpeed`), die zusammen an 60 Stellen der Datei
 * gelesen und gesetzt wurden.
 *
 * Der Abspieler haelt ZWEI Dinge im Gleichschritt, und darin lag die
 * Verflechtung: die Three.js-Animation (Mixer und Aktion) und die
 * Theatre.js-Sequenz (Kamera- und Lichtspuren). Beide muessen zusammen
 * starten, pausieren, springen und ihr Tempo aendern — steht das verteilt in
 * einer 2.600-Zeilen-Datei, geraet es unweigerlich auseinander.
 *
 * `window.isPlaying` wird weiter gepflegt: Die Render-Schleife und der
 * Server-Export (Playwright) lesen es.
 */
export class Abspieler {

    /** Bildrate für Einzelbild-Sprünge. */
    static FPS = 30;
    /** Ersatzlänge der Theatre-Sequenz, wenn keine Animation geladen ist. */
    static ERSATZLAENGE = 10;

    /**
     * @param {Object} sequenz  sheet.sequence von Theatre.js
     * @param {Object} animation  { mixer(), aktion(), stoppen() } — Zugriff auf
     *        die AKTUELLE Animation; sie wird bei jedem Laden ersetzt, deshalb
     *        Funktionen statt Werte.
     */
    constructor(sequenz, animation) {
        this.sequenz = sequenz;
        this.animation = animation;
        this.laeuft = false;
        this.zeit = 0;
        this.dauer = 1;
        this.tempo = 1.0;
        this.elemente = {
            abspielen: document.getElementById('btnPlayPause'),
            anhalten: document.getElementById('btnStop'),
            zurueck: document.getElementById('btnFrameBack'),
            vor: document.getElementById('btnFrameFwd'),
            leiste: document.getElementById('timelineSlider'),
            jetzt: document.getElementById('timeCurrent'),
            gesamt: document.getElementById('timeDuration'),
            symbol: document.getElementById('playIcon'),
        };
    }

    /** mm:ss aus Sekunden. */
    static zeitText(sekunden) {
        const min = Math.floor(sekunden / 60);
        const sek = Math.floor(sekunden % 60);
        return `${String(min).padStart(2, '0')}:${String(sek).padStart(2, '0')}`;
    }

    verdrahten() {
        const e = this.elemente;
        e.abspielen?.addEventListener('click', () => this.umschalten());
        e.anhalten?.addEventListener('click', () => this.anhalten());
        e.zurueck?.addEventListener('click',
            () => this.zeitSetzen(this.zeit - 1 / Abspieler.FPS));
        e.vor?.addEventListener('click',
            () => this.zeitSetzen(this.zeit + 1 / Abspieler.FPS));
        e.leiste?.addEventListener('input', () => {
            const zeit = parseFloat(e.leiste.value);
            this.zeitSetzen(zeit);
            // Die Theatre-Sequenz mitziehen, sonst laufen Kamera- und
            // Lichtspuren gegen die Figur.
            this.sequenz.position = zeit;
        });
        document.querySelectorAll('.speed-btn').forEach(knopf => {
            knopf.addEventListener('click', () => {
                this.tempoSetzen(parseFloat(knopf.getAttribute('data-speed')));
                document.querySelectorAll('.speed-btn')
                    .forEach(k => k.classList.remove('active'));
                knopf.classList.add('active');
            });
        });
        this._tasten();
        return this;
    }

    /** Leertaste und Pfeiltasten — nicht, wenn in einem Feld getippt wird. */
    _tasten() {
        document.addEventListener('keydown', (ereignis) => {
            if (ereignis.target.tagName === 'INPUT') return;
            const knopf = { Space: this.elemente.abspielen,
                            ArrowLeft: this.elemente.zurueck,
                            ArrowRight: this.elemente.vor }[ereignis.code];
            if (!knopf) return;
            ereignis.preventDefault();
            knopf.click();
        });
    }

    // ------------------------------------------------------------------ Steuern

    umschalten() {
        this.laeuft ? this._pausieren() : this._starten();
        this.anzeigen();
        return this.laeuft;
    }

    _starten() {
        this.laeuft = true;
        window.isPlaying = true;
        const aktion = this.animation.aktion();
        if (this.animation.mixer() && aktion) {
            aktion.paused = false;
            aktion.play();
        }
        this.sequenz.play({ iterationCount: Infinity, rate: this.tempo,
                            range: [0, this._sequenzlaenge()] });
    }

    _pausieren() {
        this.laeuft = false;
        window.isPlaying = false;
        const aktion = this.animation.aktion();
        if (aktion) aktion.paused = true;
        this.sequenz.pause();
    }

    /** Anhalten und an den Anfang — die Dauer bleibt erhalten. */
    anhalten() {
        this.animation.stoppen();
        this.zeit = 0;
        this.laeuft = false;
        window.isPlaying = false;
        this.sequenz.pause();
        this.sequenz.position = 0;
        this.anzeigen();
    }

    /** Auf eine Zeit springen (innerhalb der Dauer). */
    zeitSetzen(zeit) {
        const mixer = this.animation.mixer();
        const aktion = this.animation.aktion();
        if (!mixer || !aktion) return;
        this.zeit = Math.max(0, Math.min(zeit, this.dauer));
        aktion.time = this.zeit;
        mixer.update(0);     // anwenden, ohne die Zeit weiterzudrehen
        this.anzeigen();
    }

    tempoSetzen(faktor) {
        this.tempo = faktor;
        const mixer = this.animation.mixer();
        if (mixer) mixer.timeScale = faktor;
        // Läuft es gerade, muss die Sequenz mit dem neuen Tempo neu anlaufen.
        if (this.laeuft) {
            this.sequenz.play({ iterationCount: Infinity, rate: faktor,
                                range: [0, this._sequenzlaenge()] });
        }
    }

    /** Neue Animationslänge übernehmen (nach dem Laden einer BVH-Datei). */
    dauerSetzen(dauer) {
        this.dauer = dauer || 1;
        if (this.elemente.gesamt) {
            this.elemente.gesamt.textContent = Abspieler.zeitText(this.dauer);
        }
        if (this.elemente.leiste) this.elemente.leiste.max = this.dauer;
        window.animDuration = this.dauer;
    }

    /** Zeitanzeige, Zeitleiste und Abspielsymbol nachziehen. */
    anzeigen() {
        const e = this.elemente;
        if (e.jetzt) e.jetzt.textContent = Abspieler.zeitText(this.zeit);
        if (e.leiste) e.leiste.value = this.zeit;
        if (e.symbol) e.symbol.className = this.laeuft ? 'fas fa-pause' : 'fas fa-play';
        window.currentTime = this.zeit;
    }

    /**
     * In der Render-Schleife: Zeit von der laufenden Aktion uebernehmen.
     * Gibt true zurueck, wenn sich die Anzeige geaendert hat.
     */
    zeitVerfolgen() {
        if (!this.laeuft) return false;
        const aktion = this.animation.aktion();
        if (!aktion) return false;
        this.zeit = aktion.time % (this.dauer || 1);
        this.anzeigen();
        return true;
    }

    _sequenzlaenge() {
        return (this.dauer > 1) ? this.dauer : Abspieler.ERSATZLAENGE;
    }
}
