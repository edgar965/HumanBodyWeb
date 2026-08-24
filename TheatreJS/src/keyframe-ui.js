/**
 * Simple Keyframe UI for Camera/Light Animation
 * Uses Theatre.js Core API without Studio UI
 *
 * UMBAU 18.08.2026: 319 Zeilen, davon rund 60 Markup mit Inline-Stilen. Jetzt:
 *
 *     studio/keyframefeld.js    das Bedienfeld (Stile als .kf-* in theatre.html)
 *     studio/keyframeliste.js   die Liste der Schlüsselbilder
 *     studio/keyframeablage.js  Aus- und Einlesen als JSON
 *
 * Hier bleiben Zustand und Ablauf: setzen, auf die Sequenz schreiben, abspielen.
 */
import { Keyframefeld } from './studio/keyframefeld.js';
import { Keyframeliste } from './studio/keyframeliste.js';
import { Keyframeablage } from './studio/keyframeablage.js';
import { Protokoll } from '../../static/viewer/gemeinsam/protokoll.js';

export class KeyframeUI {

    static VORGABE_DAUER = 10;

    constructor(project, sheet, objects, studio) {
        this.project = project;
        this.sheet = sheet;
        this.studio = studio;
        this.sequence = sheet.sequence;
        this.objects = objects;   // { Camera: theatreObj, 'Spot Left': …, … }
        this.keyframes = [];      // { id, time, objectName, values }
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = KeyframeUI.VORGABE_DAUER;
        this.liste = new Keyframeliste(kennung => this.deleteKeyframe(kennung));
        if (new Keyframefeld(Object.keys(objects)).aufbauen()) {
            this.attachEventListeners();
        } else {
            Protokoll.warnung('keyframe-ui', 'Reiter „Keyframes" nicht gefunden');
        }
    }

    // ------------------------------------------------------------- Verdrahten

    attachEventListeners() {
        this._klick('kf-play', () => this.play());
        this._klick('kf-stop', () => this.stop());
        this._klick('kf-add', () => this.addKeyframe());
        this._klick('kf-clear', () => this.clearKeyframes());
        this._klick('kf-export',
                    () => Keyframeablage.ausgeben(this.duration, this.keyframes));
        this._klick('kf-import',
                    () => Keyframeablage.einlesen(daten => this._uebernehmen(daten)));
        document.getElementById('kf-duration')?.addEventListener('change',
            ereignis => this.dauerSetzen(parseFloat(ereignis.target.value)));
        document.getElementById('kf-timeline')?.addEventListener('input',
            ereignis => this.zeitSetzen(parseFloat(ereignis.target.value)));
    }

    _klick(kennung, tun) {
        document.getElementById(kennung)?.addEventListener('click', tun);
    }

    dauerSetzen(dauer) {
        this.duration = dauer;
        const leiste = document.getElementById('kf-timeline');
        if (leiste) leiste.max = dauer;
    }

    zeitSetzen(zeit) {
        this.currentTime = zeit;
        this.sequence.position = zeit;
        this.updateTimeDisplay();
    }

    // -------------------------------------------------------- Schlüsselbilder

    addKeyframe() {
        const name = document.getElementById('kf-object-select')?.value;
        const objekt = this.objects[name];
        if (!objekt) return;
        this.keyframes.push({
            id: Date.now(),
            time: this.currentTime,
            objectName: name,
            values: JSON.parse(JSON.stringify(objekt.value)),   // tiefe Kopie
        });
        this.keyframes.sort((a, b) => a.time - b.time);
        this.applyKeyframesToSequence();
        this.liste.zeichnen(this.keyframes);
        Protokoll.debug('keyframe-ui',
                        `✓ Keyframe added for ${name} `
                        + `at ${this.currentTime.toFixed(2)}s`);
    }

    /**
     * Alle Schlüsselbilder in die Theatre-Sequenz schreiben.
     *
     * Theatre.js setzt einen Schlüssel dort, wo die Sequenz gerade steht —
     * deshalb wird die Position je Bild verschoben und am Ende zurückgestellt.
     *
     * GESCHRIEBEN WIRD ÜBER `studio.transaction` (Befund 18.08.2026). Vorher
     * stand hier `objekt.props[feld][unterfeld].setValue(wert)` — ein Zeiger
     * von Theatre.js hat aber gar kein `setValue`. Jeder Klick auf „Add
     * Keyframe" endete deshalb in
     *
     *     TypeError: e.props[n][a].setValue is not a function
     *
     * und weil der Fehler mitten im Ablauf flog, wurde auch die Liste darunter
     * nie neu gezeichnet: Der Reiter sah aus, als nähme er keine Keyframes an.
     * `Zeitleistenwerkzeuge.neuAufbauen` macht es seit jeher richtig.
     */
    applyKeyframesToSequence() {
        for (const bild of this.keyframes) {
            const objekt = this.objects[bild.objectName];
            if (!objekt) continue;
            this.sequence.position = bild.time;
            this.studio.transaction(({ set }) => {
                for (const [feld, wert] of Object.entries(bild.values)) {
                    KeyframeUI._setzen(set, objekt, feld, wert);
                }
            });
        }
        this.sequence.position = this.currentTime;
    }

    /** Zusammengesetzte Werte (Position, Drehung) gehen nur einzeln. */
    static _setzen(set, objekt, feld, wert) {
        if (typeof wert === 'object' && wert !== null && !Array.isArray(wert)) {
            for (const [unterfeld, unterwert] of Object.entries(wert)) {
                set(objekt.props[feld][unterfeld], unterwert);
            }
            return;
        }
        set(objekt.props[feld], wert);
    }

    deleteKeyframe(kennung) {
        this.keyframes = this.keyframes.filter(bild => bild.id !== kennung);
        this.applyKeyframesToSequence();
        this.liste.zeichnen(this.keyframes);
    }

    clearKeyframes() {
        this.keyframes = [];
        this.liste.zeichnen(this.keyframes);
        // „Timeline löschen" im Werkzeugmenü raeumt auch den gespeicherten
        // Theatre-Zustand ab — sonst kaeme er beim naechsten Laden zurueck.
        document.getElementById('menu-tracks-clear')?.click();
    }

    _uebernehmen({ dauer, schluesselbilder }) {
        this.keyframes = schluesselbilder;
        this.dauerSetzen(dauer);
        const feld = document.getElementById('kf-duration');
        if (feld) feld.value = dauer;
        this.applyKeyframesToSequence();
        this.liste.zeichnen(this.keyframes);
    }

    // ------------------------------------------------------------- Abspielen

    play() {
        if (this.isPlaying) return;
        this.isPlaying = true;
        this._spielknopf(true);
        this.sequence.play({ range: [0, this.duration], rate: 1 });
        this.playLoop();
    }

    pause() {
        this.isPlaying = false;
        this._spielknopf(false);
    }

    stop() {
        this.isPlaying = false;
        this.zeitSetzen(0);
        const leiste = document.getElementById('kf-timeline');
        if (leiste) leiste.value = 0;
        this._spielknopf(false);
    }

    /** Der Knopf trägt beide Bedeutungen — deshalb wechselt auch sein Zuhörer. */
    _spielknopf(laeuft) {
        const knopf = document.getElementById('kf-play');
        if (!knopf) return;
        knopf.innerHTML = laeuft
            ? '<i class="fas fa-pause"></i> Pause'
            : '<i class="fas fa-play"></i> Play';
        knopf.onclick = laeuft ? () => this.pause() : () => this.play();
    }

    playLoop() {
        if (!this.isPlaying) return;
        this.currentTime = this.sequence.position;
        if (this.currentTime >= this.duration) {
            this.stop();
            return;
        }
        const leiste = document.getElementById('kf-timeline');
        if (leiste) leiste.value = this.currentTime;
        this.updateTimeDisplay();
        requestAnimationFrame(() => this.playLoop());
    }

    updateTimeDisplay() {
        const anzeige = document.getElementById('kf-time-display');
        if (anzeige) anzeige.textContent = this.currentTime.toFixed(2) + 's';
    }
}
