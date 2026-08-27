import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeichenschleife } from '../gemeinsam/zeichenschleife.js';

/**
 * Szenenschleife — die Renderschleife der Szene-Seite samt Anzeigen.
 *
 * Aus `boot.js animate()` herausgeloest (Umbau 16.08.2026).
 *
 * PERFORMANCE: Die Schleife rief in JEDEM Bild `document.getElementById` —
 * zweimal fest (`cam-pos`, `cam-target`), bei laufender Animation zusätzlich
 * `anim-time` und `anim-timeline`, und einmal je Sekunde `fps-display`. Bei
 * 60 Bildern/s sind das 120 bis 240 DOM-Suchen pro Sekunde für fünf Elemente,
 * die sich nie ändern. Sie werden jetzt einmal geholt.
 *
 * Auch neu: `new THREE.Vector3()` stand in der Bodenfixierung INNERHALB der
 * Schleife — ein Objekt pro Bild, das der Sammler wieder einsammeln muss.
 * Jetzt ein wiederverwendeter Vektor.
 */
export class Szenenschleife extends Zeichenschleife {

    /** Größter Zeitschritt — nach einem Tab-Wechsel sonst ein Sprung. */
    static MAX_SCHRITT_S = 0.1;
    /** Fenster, über das die Bildrate gemittelt wird. */
    static FPS_FENSTER_S = 1.0;
    /** Ersatz-Bildzeit, wenn die Spur keine zweite Stützstelle hat. */
    static ERSATZ_BILDZEIT_S = 1 / 30;

    /** Kennung der Anzeigefelder — einmal geholt, nicht in jedem Bild. */
    static FELDER = {
        kameraplatz: 'cam-pos',
        kameraziel: 'cam-target',
        bildrate: 'fps-display',
        zeit: 'anim-time',
        leiste: 'anim-timeline',
    };

    constructor() {
        super();
        this.anzeigen = null;
        this._arbeitsvektor = new THREE.Vector3();
    }

    /**
     * Die Anzeigefelder holen. Fehlt eines beim Start (etwa weil sein Reiter
     * noch nicht gebaut ist), wird es beim nächsten Zugriff nachgeholt — sonst
     * bliebe es für die Lebensdauer der Seite stumm.
     */
    feld(name) {
        if (!this.anzeigen[name]) {
            this.anzeigen[name] = document.getElementById(
                Szenenschleife.FELDER[name]);
        }
        return this.anzeigen[name];
    }

    _anzeigen() {
        const felder = {};
        for (const [name, id] of Object.entries(Szenenschleife.FELDER)) {
            felder[name] = document.getElementById(id);
        }
        return felder;
    }

    /** Vorbereitung dieser Seite — vor dem ersten Takt. */
    vorbereiten() {
        this.anzeigen = this._anzeigen();
    }

    schritt() {
        const dt = Math.min(state.clock.getDelta(), Szenenschleife.MAX_SCHRITT_S);
        state.controls.update();
        if (state.mixer && state.playing) {
            state.mixer.update(dt);
            this.zeitanzeige();
            if (state.currentAnimGroundFixed) this.aufDenBoden();
        }
        state.renderer.render(state.scene, state.camera);
        this.kameraanzeige();
        this.bildrate(dt);
    }

    zeitanzeige() {
        const aktion = state.currentAction;
        const clip = aktion?.getClip();
        if (!clip) return;
        const zeit = aktion.time;
        const dauer = clip.duration;
        const bildzeit = clip.tracks[0]?.times?.[1]
                         || Szenenschleife.ERSATZ_BILDZEIT_S;
        const zeitfeld = this.feld('zeit');
        if (zeitfeld) {
            zeitfeld.textContent =
                `Frame ${Math.floor(zeit / bildzeit)} / `
                + `${Math.round(dauer / bildzeit)} • `
                + `${zeit.toFixed(2)}s / ${dauer.toFixed(2)}s`;
        }
        const leiste = this.feld('leiste');
        if (leiste && dauer > 0) {
            leiste.value = Math.round((zeit / dauer) * 100);
        }
    }

    /**
     * Bei bodenfixierten Animationen den tiefsten Knochen auf y=0 ziehen —
     * sonst schwebt oder versinkt die Figur.
     */
    aufDenBoden() {
        const figur = fn._selectedInst ? fn._selectedInst() : null;
        const skelett = figur ? figur.rigifySkeleton : state.rigifySkeleton;
        const wurzel = skelett?.rootBone;
        if (!wurzel) return;
        let tiefste = Infinity;
        wurzel.traverse(knochen => {
            if (!knochen.isBone) return;
            knochen.getWorldPosition(this._arbeitsvektor);
            if (this._arbeitsvektor.y < tiefste) tiefste = this._arbeitsvektor.y;
        });
        if (isFinite(tiefste)) wurzel.position.y -= tiefste;
    }

    kameraanzeige() {
        const platz = state.camera.position;
        const ziel = state.controls.target;
        const platzfeld = this.feld('kameraplatz');
        if (platzfeld) platzfeld.textContent = Szenenschleife.dreizahl(platz);
        const zielfeld = this.feld('kameraziel');
        if (zielfeld) zielfeld.textContent = Szenenschleife.dreizahl(ziel);
    }

    static dreizahl(v) {
        return `${v.x.toFixed(2)}, ${v.y.toFixed(2)}, ${v.z.toFixed(2)}`;
    }

    bildrate(dt) {
        state.frameCount++;
        state.fpsAccum += dt;
        if (state.fpsAccum < Szenenschleife.FPS_FENSTER_S) return;
        const feld = this.feld('bildrate');
        if (feld) feld.textContent = state.frameCount;
        state.frameCount = 0;
        state.fpsAccum = 0;
    }
}
