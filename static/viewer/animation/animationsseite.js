import { Seitenzustand } from './seitenzustand.js';
import { loadSkinColors, applySceneSettings } from './material.js';
import { loadAnimationTree, setupAnimManagement } from './baum.js';
import { loadMesh, loadRigifySkeleton, loadSkinWeights } from './netz.js';
import { loadBVHAnimation, bindPlaybackControls, animate } from './wiedergabe.js';
import { initSaveButtons } from './speichern.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { Buehne } from '../gemeinsam/buehne.js';
import { Klappbereiche } from '../gemeinsam/klappbereiche.js';

/**
 * Animationsseite — der Start der Animationsseite: Bühne, Bedienung, Daten.
 *
 * Aus animations.js herausgeloest (Umbau 16.08.2026): `init()` hatte 134 Zeilen,
 * davon 50 für einen Bühnenaufbau, der Zeile für Zeile dem von
 * `character_core.createSceneSetup()` und `scene/boot.js` entsprach — jetzt
 * `Buehne`. Der Demo-Knopf und die zwei Umschalter waren drei ähnliche Blöcke,
 * die jeweils Sichtbarkeit kippten und ihre Knopfbeschriftung nachzogen.
 */
export class Animationsseite {

    /** Die Animation des Demo-Knopfs. */
    static DEMO_URL = '/api/character/bvh/Mixamo/Catwalk_Idle_02/';
    static DEMO_NAME = 'Catwalk Idle 02';

    static SYMBOL_SPIELT = '<i class="fas fa-pause"></i>';
    static SYMBOL_HAELT = '<i class="fas fa-play"></i>';

    async starten() {
        this.buehne();
        this._bereicheKlappbar();
        bindPlaybackControls();
        this.demoknopf();
        this.umschalter();
        initSaveButtons();
        animate();
        this.datenLaden();
        return this;
    }

    buehne() {
        const leinwand = document.getElementById('viewer-canvas');
        const teile = Buehne.bauen(leinwand, { masse: 'rahmen', stil: true });
        Seitenzustand.renderer = teile.renderer;
        Seitenzustand.scene = teile.scene;
        Seitenzustand.camera = teile.camera;
        Seitenzustand.controls = teile.controls;
        // Die Seite merkt sich Lichteinstellungen im Browser.
        applySceneSettings(teile.keyLight, teile.fillLight, teile.backLight,
                           teile.ambient);
        window.addEventListener('resize', Seitenzustand.groesseAnpassen);
    }

    /** Abschnitte auf- und zuklappbar machen — siehe `Klappbereiche`. */
    _bereicheKlappbar() {
        Klappbereiche.verdrahten();
    }

    datenLaden() {
        loadMesh();
        loadRigifySkeleton();
        loadSkinWeights();
        loadSkinColors();
        loadAnimationTree();
        setupAnimManagement();
    }

    // ------------------------------------------------------------ Demo-Knopf

    /** Spielt eine Beispielanimation und hält sie wieder an. */
    demoknopf() {
        const knopf = document.getElementById('play-demo-anim');
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            if (!Seitenzustand.currentAction) {
                loadBVHAnimation(Animationsseite.DEMO_URL,
                                 Animationsseite.DEMO_NAME, 0);
                this.spielzustandZeigen(knopf, true);
                return;
            }
            const laeuft = Seitenzustand.playing;
            if (!laeuft && !Seitenzustand.currentAction.isRunning()) {
                Seitenzustand.currentAction.play();
            }
            Seitenzustand.currentAction.paused = laeuft;
            Seitenzustand.playing = !laeuft;
            this.spielzustandZeigen(knopf, !laeuft);
        });
    }

    /** Demo-Knopf und der Abspielknopf der Leiste zeigen dasselbe. */
    spielzustandZeigen(knopf, spielt) {
        const symbol = spielt ? Animationsseite.SYMBOL_SPIELT
                              : Animationsseite.SYMBOL_HAELT;
        knopf.innerHTML = symbol;
        knopf.classList.toggle('active', spielt);
        const leiste = document.getElementById('anim-play');
        if (leiste) leiste.innerHTML = symbol;
    }

    // ------------------------------------------------------------ Umschalter

    umschalter() {
        this._umschalter('rig-toggle', () => this._rigKippen(),
                         () => Seitenzustand.rigVisible);
        this._umschalter('model-toggle', () => {
            const netz = Seitenzustand.bodyMesh;
            if (netz) netz.visible = !netz.visible;
        }, () => !!Seitenzustand.bodyMesh?.visible);
    }

    _umschalter(id, kippen, steht) {
        const knopf = document.getElementById(id);
        knopf?.addEventListener('click', () => {
            kippen();
            knopf.classList.toggle('active', steht());
        });
    }

    /**
     * Das Rig wird erst beim ersten Einschalten gebaut — vorher gibt es kein
     * Skelett, auf das es zeigen könnte.
     */
    _rigKippen() {
        Seitenzustand.rigVisible = !Seitenzustand.rigVisible;
        if (Seitenzustand.rigVisible && !Seitenzustand.skeletonHelper
            && Seitenzustand.rigifySkeleton) {
            Seitenzustand.skeletonHelper = Skelettanzeige.bauen(
                Seitenzustand.scene, Seitenzustand.rigifySkeleton.rootBone);
        }
        if (Seitenzustand.skeletonHelper) {
            Seitenzustand.skeletonHelper.visible = Seitenzustand.rigVisible;
        }
    }
}
