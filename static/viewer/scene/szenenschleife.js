import { THREE } from './state.js';
import { state } from './state.js';
import { Zeichenschleife } from '../gemeinsam/zeichenschleife.js';
import { Rigsichtbarkeit } from './rigsichtbarkeit.js';
import { Weichgewebe } from './weichgewebe.js';
import { Posenabsatz } from './posenabsatz.js';
import { Bodenstand } from './bodenstand.js';
import { Genesis9zopfschwung } from './genesis9/genesis9zopfschwung.js';
import { Genesis9stoffschwung } from './genesis9/genesis9stoffschwung.js';
import { Genesis9gelenke } from '../gemeinsam/genesis9gelenke.js';

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
        /** Zeit der Animation beim letzten Bodenfix — für den Zeitregler bei Pause. */
        this._bodenZeit = null;
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
            // Der Absatzschuh bleibt Teil der Pose, auch wenn eine
            // Animation die Füsse stellt (`posenabsatz.js`, wie
            // MakeHumans Fusspose) — NACH dem Mixer, der die Knochen
            // dieses Bildes gesetzt hat.
            Posenabsatz.takt();
            this.zeitanzeige();
        }
        // Zopfschwung (18.09.2026): die eigenen Knochen der Daz-Haare — NACH
        // dem Mixer, VOR dem Weichgewebe, das ihr Tempo liest.
        Genesis9zopfschwung.takt(dt);
        Genesis9stoffschwung.takt(dt);
        // Gelenkkorrekturen (18.09.2026 abends): Daz' JCMs aus den Knochen-
        // winkeln dieses Bildes — nach dem Mischer, vor dem Weichgewebe.
        Genesis9gelenke.alle(state.characters.values());
        this.aufDenBoden();
        // Weichgewebe (11.09.2026): der Zuschlag auf das Skinning — NACH dem
        // Mixer, damit die Knochen dieses Bildes gelesen werden.
        Weichgewebe.takt(dt);
        // Neu dazugekommene Figuren bekommen ihre Knochenlinien von selbst;
        // gedrosselt, siehe `Rigsichtbarkeit.ABGLEICH_MS`.
        Rigsichtbarkeit.abgleichen();
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
     * Bei bodenfixierten Animationen die animierte Figur mit ihrem tiefsten
     * Punkt auf y=0 ziehen — sonst schwebt oder versinkt sie (`bodenstand.js`,
     * `koerpertiefe.js`; Edgar 12./13.09.2026). Läuft bei Wiedergabe in jedem
     * Bild, bei Pause nur, wenn der Zeitregler die Animation verstellt hat —
     * der Mixer setzt die Wurzel dann roh, ohne diesen Takt.
     */
    aufDenBoden() {
        if (!state.currentAnimGroundFixed || !state.mixer) return;
        const zeit = state.currentAction?.time ?? null;
        if (!state.playing && zeit === this._bodenZeit) return;
        this._bodenZeit = zeit;
        Bodenstand.richten(state, this._arbeitsvektor);
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
