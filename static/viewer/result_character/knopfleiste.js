import { state } from './state.js';
import '../gemeinsam/registrierung.js';
import { el, Ziehgriff } from './bauteile.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { Videofenster } from './videofenster.js';

/**
 * Knopfleiste der Ergebnisseite — Umschalter für Modell, Rig, Kleidung, Haar,
 * das Originalvideo und die Größe der 3D-Ansicht.
 *
 * Erster Umbau (16.08.2026) hatte die 185 Zeilen nur aus ui_panel.js
 * herübergeschoben, in EINE statische Methode. Zweiter Durchgang: die vier
 * Umschalter waren viermal derselbe Block (Knopf bauen, Sichtbarkeit kippen,
 * Klasse `active` nachziehen) — jetzt die Tabelle UMSCHALTER. Das Videofenster
 * (Verschieben, Größe, Schließen) ist eine eigene Klasse, weil es nichts mit
 * der Leiste zu tun hat außer dem Knopf, der es zeigt.
 */
export class Knopfleiste {

    /** Kleinste Höhe der 3D-Ansicht beim Ziehen. */
    static MIN_HOEHE = 250;
    /** Höhe, wenn das Vollbild verlassen wird und keine gemerkt ist. */
    static HOEHE_ERSATZ = 500;

    /**
     * Die vier Sichtbarkeits-Umschalter: Beschriftung, Symbol, ob sie
     * anfangs leuchten, und was sie kippen.
     */
    static UMSCHALTER = [
        { text: 'Model', symbol: 'fa-user', an: true,
          kippen: () => Knopfleiste._netzKippen(state.bodyMesh),
          steht: () => state.bodyMesh?.visible },
        { text: 'Rig', symbol: 'fa-bone', an: false,
          kippen: () => Knopfleiste._rigKippen(),
          steht: () => state.rigVisible },
        { text: 'Kleider', symbol: 'fa-tshirt', an: true,
          kippen: () => Knopfleiste._kleidungKippen(),
          steht: () => state.clothesVisible },
        { text: 'Haar', symbol: 'fa-hat-wizard', an: true,
          kippen: () => Knopfleiste._netzKippen(state.hairMesh),
          steht: () => state.hairMesh?.visible },
    ];

    /** Baut die Leiste in den Behälter. */
    static bauen(behaelter) {
        const leiste = el('div', 'rc-toggle-bar');
        for (const eintrag of Knopfleiste.UMSCHALTER) {
            leiste.appendChild(Knopfleiste._umschalter(eintrag));
        }
        const fenster = Videofenster.bauen(leiste);
        Knopfleiste._ansichtsgroesse();
        behaelter.appendChild(leiste);
        return fenster;
    }

    static _umschalter({ text, symbol, an, kippen, steht }) {
        const knopf = el('button', 'rc-toggle-btn' + (an ? ' active' : ''));
        knopf.innerHTML = `<i class="fas ${symbol}"></i> ${text}`;
        knopf.addEventListener('click', () => {
            kippen();
            knopf.classList.toggle('active', !!steht());
        });
        return knopf;
    }

    static _netzKippen(netz) {
        if (netz) netz.visible = !netz.visible;
    }

    /**
     * Das Rig wird erst beim ersten Einschalten gebaut — vorher gibt es noch
     * kein Skelett, auf das es zeigen könnte.
     */
    static _rigKippen() {
        state.rigVisible = !state.rigVisible;
        if (state.rigVisible && !state.skeletonHelper && state.rigifySkeleton) {
            state.skeletonHelper = Skelettanzeige.bauen(
                state.scene, state.rigifySkeleton.rootBone);
        }
        if (state.skeletonHelper) state.skeletonHelper.visible = state.rigVisible;
        if (typeof window.setBvhOverlayVisible === 'function') {
            window.setBvhOverlayVisible(state.rigVisible);
        }
    }

    static _kleidungKippen() {
        state.clothesVisible = !state.clothesVisible;
        for (const netz of [...Object.values(state.clothMeshes),
                            ...Object.values(state.garmentMeshes)]) {
            if (netz) netz.visible = state.clothesVisible;
        }
    }

    // ------------------------------------------------------- Größe der Ansicht

    /**
     * Vollbild-Knopf und Ziehgriff der 3D-Ansicht. Wird an der Höhe gezogen,
     * verlässt die Ansicht das Vollbild — sonst hätte das Ziehen keine Wirkung,
     * weil das Vollbild die Höhe vorgibt.
     */
    static _ansichtsgroesse() {
        const rahmen = document.getElementById('resultCharacter');
        const ansicht = document.getElementById('characterViewport');
        const knopf = document.getElementById('btnViewportFullscreen');
        if (!knopf || !rahmen || !ansicht) return;

        const stand = { vollbild: true, hoehe: null };
        const vollbildSetzen = ein => {
            stand.vollbild = ein;
            rahmen.classList.toggle('result-character-fullscreen', ein);
            knopf.innerHTML = ein ? '<i class="fas fa-expand"></i>'
                                  : '<i class="fas fa-compress"></i>';
        };
        knopf.addEventListener('click', () => {
            vollbildSetzen(!stand.vollbild);
            if (stand.vollbild) {
                ansicht.style.height = '';
                stand.hoehe = null;
            } else {
                ansicht.style.height =
                    (stand.hoehe || Knopfleiste.HOEHE_ERSATZ) + 'px';
            }
            window.dispatchEvent(new Event('resize'));
        });

        let starthoehe = 0;
        Ziehgriff.an(document.getElementById('viewportResizeHandle'),
            (dx, dy) => {
                stand.hoehe = Math.max(Knopfleiste.MIN_HOEHE, starthoehe + dy);
                ansicht.style.height = stand.hoehe + 'px';
                window.dispatchEvent(new Event('resize'));
            },
            { beginn: () => {
                starthoehe = ansicht.offsetHeight;
                if (stand.vollbild) vollbildSetzen(false);
            } });
    }
}
