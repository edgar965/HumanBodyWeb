/**
 * Videoschleife — die Renderschleife der Ergebnisseite.
 *
 * Aus `initResultCharacter()` herausgeloest (Umbau 16.08.2026). Besonderheit
 * dieser Seite: Das Video gibt den Takt vor, nicht eine eigene Uhr. Die
 * Animation wird auf den Bruchteil gesetzt, an dem das Video steht — so laufen
 * Video und Figur zusammen, auch wenn der Benutzer im Video springt.
 */
import { Zeichenschleife } from '../gemeinsam/zeichenschleife.js';


export class Videoschleife extends Zeichenschleife {

    /** Fällt die Höhe des Rahmens aus, gilt diese. */
    static HOEHE_ERSATZ = 500;

    constructor(state) {
        super();
        this.state = state;
        this.rahmen = state.canvas.parentElement;
    }

    /** Vorbereitung dieser Seite — vor dem ersten Takt. */
    vorbereiten() {
        this._groesseVerfolgen();
    }

    schritt() {
        this.state.controls.update();
        if (this.state.mixer && this.state.bvhClipDuration > 0) {
            this._animationSetzen();
        }
        this.state.renderer.render(this.state.scene, this.state.camera);
    }

    _animationSetzen() {
        const aktion = this.state.currentAction;
        // Eine angehaltene Aktion bewegt sich auch mit setTime() nicht.
        if (aktion?.paused) {
            aktion.reset();
            aktion.play();
        }
        this.state.mixer.setTime(this.anteil() * this.state.bvhClipDuration);
    }

    /**
     * Wo im Video stehen wir, 0..1? Läuft kein Video (etwa wenn nur eine BVH
     * ohne Film gezeigt wird), nimmt der BVH-Abspieler seinen Stand hierher.
     */
    anteil() {
        const video = this.state.video;
        const dauer = video.duration;
        if (dauer > 0 && isFinite(dauer)) return video.currentTime / dauer;
        if (typeof window.bvhPlayerProgress === 'number') {
            return window.bvhPlayerProgress;
        }
        return 0;
    }

    _groesseVerfolgen() {
        const nachziehen = () => this.groesseAnpassen();
        window.addEventListener('resize', nachziehen);
        if (typeof ResizeObserver !== 'undefined') {
            new ResizeObserver(nachziehen).observe(this.rahmen);
        }
    }

    groesseAnpassen() {
        const breite = this.rahmen.clientWidth;
        const hoehe = this.rahmen.clientHeight || Videoschleife.HOEHE_ERSATZ;
        this.state.renderer.setSize(breite, hoehe, false);
        this.state.camera.aspect = breite / hoehe;
        this.state.camera.updateProjectionMatrix();
    }
}
