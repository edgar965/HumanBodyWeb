/**
 * Studioknoepfe — die vier kleinen Umschalter der Werkzeugleiste.
 *
 * Herausgelöst aus `main.js` (788 Zeilen): Rig anzeigen, Abspielen (leitet an
 * den Hauptknopf weiter), Theatre-Studio ein-/ausblenden, „Modelle"-Reiter
 * öffnen.
 *
 * Der Abspiel-Knopf DRÜCKT den Hauptknopf, statt selbst umzuschalten — sonst
 * gäbe es zwei Stellen, die den Abspielzustand kennen, und sie liefen
 * auseinander.
 */
export class Studioknoepfe {

    constructor(skinner, studio) {
        this.skinner = skinner;
        this.studio = studio;
        this.studioSichtbar = true;
    }

    verdrahten() {
        this._rig();
        this._abspielen();
        this._studio();
        this._modellreiter();
        return this;
    }

    _rig() {
        const knopf = document.getElementById('btn-toggle-rig');
        knopf?.addEventListener('click', () => {
            knopf.classList.toggle('active', this.skinner.rigUmschalten());
        });
    }

    _abspielen() {
        document.getElementById('btn-play-animation')?.addEventListener(
            'click', () => document.getElementById('btnPlayPause')?.click());
    }

    _studio() {
        const knopf = document.getElementById('btn-toggle-studio');
        knopf?.addEventListener('click', () => {
            this.studioSichtbar = !this.studioSichtbar;
            if (this.studioSichtbar) this.studio.ui.restore();
            else this.studio.ui.hide();
            knopf.classList.toggle('active', this.studioSichtbar);
        });
    }

    /** Der Knopf links schaltet nur auf den Modelle-Reiter. */
    _modellreiter() {
        document.getElementById('menu-model-load')?.addEventListener('click', () => {
            document.querySelectorAll('.panel-tab')
                .forEach(reiter => reiter.classList.remove('active'));
            document.querySelectorAll('.tab-pane')
                .forEach(feld => feld.classList.remove('active'));
            document.querySelector('[data-tab="tab-models"]')
                ?.classList.add('active');
            document.getElementById('tab-models')?.classList.add('active');
        });
    }
}
