import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';

/**
 * Werkzeugknoepfe — die Umschalter über der Bühne der Viewer-Seite.
 *
 * Aus viewer/index.js herausgeloest (Umbau 16.08.2026): 90 Zeilen fuer fuenf
 * Knoepfe. Der Rig-Umschalter enthielt dabei die DRITTE Kopie des
 * SkeletonHelper-Aufbaus im Projekt (die anderen zwei lagen in der
 * Theatre-Seite) — sie kommt jetzt aus gemeinsam/skelettanzeige.js.
 */
export class Werkzeugknoepfe {

    /** Die Standard-Animation des Demo-Knopfes. */
    static DEMO_URL = '/api/character/bvh/Mixamo/Catwalk_Idle_02/';
    static DEMO_NAME = 'Catwalk Idle 02';

    static SYMBOL_ABSPIELEN = '<i class="fas fa-play"></i>';
    static SYMBOL_PAUSE = '<i class="fas fa-pause"></i>';

    /**
     * @param {Object} state  gemeinsamer Zustand der Viewer-Seite
     * @param {Object} dienste  { animationLaden, garnitureRefit, haareRefit,
     *                            garmentZustandSichern }
     */
    constructor(state, dienste) {
        this.state = state;
        this.dienste = dienste;
        this.kleidungSichtbar = true;
    }

    verdrahten() {
        this._demo();
        this._rig();
        this._modell();
        this._kleidung();
        this._refit();
        return this;
    }

    // -------------------------------------------------------------- Demo-Knopf

    _demo() {
        const knopf = document.getElementById('play-demo-anim');
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            if (!this.state.currentAction) this._demoStarten(knopf);
            else if (this.state.playing) this._demoPausieren(knopf);
            else this._demoFortsetzen(knopf);
        });
    }

    _demoStarten(knopf) {
        // Ist der Animationsbereich zugeklappt, sieht man nicht, was passiert.
        const bereich = document.getElementById('animation-panel')
            ?.closest('.panel-section');
        bereich?.classList.remove('collapsed');
        this.dienste.animationLaden(Werkzeugknoepfe.DEMO_URL,
                                    Werkzeugknoepfe.DEMO_NAME, 0);
        this._demoSymbol(knopf, true);
    }

    _demoPausieren(knopf) {
        this.state.currentAction.paused = true;
        this.state.playing = false;
        this._demoSymbol(knopf, false);
    }

    _demoFortsetzen(knopf) {
        if (!this.state.currentAction.isRunning()) this.state.currentAction.play();
        this.state.currentAction.paused = false;
        this.state.playing = true;
        this._demoSymbol(knopf, true);
    }

    /** Beide Abspielknöpfe zeigen denselben Zustand. */
    _demoSymbol(knopf, laeuft) {
        const symbol = laeuft ? Werkzeugknoepfe.SYMBOL_PAUSE
                              : Werkzeugknoepfe.SYMBOL_ABSPIELEN;
        knopf.innerHTML = symbol;
        knopf.classList.toggle('active', laeuft);
        const zweiter = document.getElementById('anim-play');
        if (zweiter) zweiter.innerHTML = symbol;
    }

    // ------------------------------------------------------------- Umschalter

    _rig() {
        const knopf = document.getElementById('rig-toggle');
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            this.state.rigVisible = !this.state.rigVisible;
            if (this.state.rigVisible && !this.state.skeletonHelper
                    && this.state.rigifySkeleton) {
                this.state.skeletonHelper = Skelettanzeige.bauen(
                    this.state.scene, this.state.rigifySkeleton.rootBone, true);
            } else if (this.state.skeletonHelper) {
                this.state.skeletonHelper.visible = this.state.rigVisible;
            }
            knopf.classList.toggle('active', this.state.rigVisible);
        });
    }

    _modell() {
        const knopf = document.getElementById('model-toggle');
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            if (this.state.bodyMesh) {
                this.state.bodyMesh.visible = !this.state.bodyMesh.visible;
            }
            knopf.classList.toggle('active',
                Boolean(this.state.bodyMesh && this.state.bodyMesh.visible));
        });
    }

    /** Kleidung, Zubehör, Garnituren und Haare zusammen umschalten. */
    _kleidung() {
        const knopf = document.getElementById('clothes-toggle');
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            this.kleidungSichtbar = !this.kleidungSichtbar;
            for (const sammlung of [this.state.clothMeshes, this.state.loadedAssets,
                                    this.state.garmentMeshes]) {
                for (const netz of Object.values(sammlung || {})) {
                    if (netz) netz.visible = this.kleidungSichtbar;
                }
            }
            if (this.state.hairMesh) {
                this.state.hairMesh.visible = this.kleidungSichtbar;
            }
            knopf.classList.toggle('active', this.kleidungSichtbar);
        });
    }

    /** Alle Garnituren neu an den Körper anpassen. */
    _refit() {
        const knopf = document.getElementById('refit-all-btn');
        if (!knopf) return;
        knopf.addEventListener('click', async () => {
            knopf.disabled = true;
            knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
            const kennungen = Object.keys(this.state.garmentMeshes);
            for (const kennung of kennungen) {
                this.dienste.garmentZustandSichern(kennung);
            }
            for (const kennung of kennungen) {
                await this.dienste.garmentLaden(kennung);
            }
            this.dienste.haareRefit();
            knopf.disabled = false;
            knopf.innerHTML = '<i class="fas fa-sync"></i> Refit';
        });
    }
}
