import * as THREE from 'three';
import { loadBVHFromText } from '../asset-loader.js';
import { fetchBVH } from '../scene-manager.js';
import { fetchRetargetedClip } from '../retarget_hybrid.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Animationslauf — eine BVH-Animation auf die gewählte Figur legen.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): `stopAnimation` und
 * `handleAnimLoad`, zusammen 107 Zeilen, die den Mixer und die aktuelle Aktion
 * als Closure-Variablen fuehrten. Genau diese zwei Werte brauchten auch der
 * Abspieler, der Export und die Render-Schleife — jetzt fragen sie hier nach.
 *
 * Der Ablauf hat zwei Wege, beide bleiben erhalten:
 *
 *  1. Ist eine Figur gewaehlt, wird sie zum SkinnedMesh gemacht und der Clip
 *     serverseitig auf ihr Skelett umgezielt.
 *  2. Sonst der Rueckfallweg: die BVH-Datei als reines Knochengerippe laden.
 */
export class Animationslauf {

    /** Koerperhoehe, wenn sie sich nicht messen laesst. */
    static HOEHE_ERSATZ = 1.68;

    /**
     * @param {Object} buehne  { scene, sheet, studio }
     * @param {Skinner} skinner
     * @param {Auswahl} auswahl
     * @param {Abspieler} abspieler
     */
    constructor(buehne, skinner, auswahl, abspieler) {
        this.buehne = buehne;
        this.skinner = skinner;
        this.auswahl = auswahl;
        this.abspieler = abspieler;
        this.mixer = null;
        this.aktion = null;
        this.name = '';
    }

    /**
     * Laufende Animation anhalten. `entfernen` gibt Mixer und Aktion frei —
     * das ist noetig, bevor eine andere Animation geladen wird.
     */
    anhalten(entfernen = false) {
        if (this.aktion) {
            this.aktion.stop();
            this.aktion.reset();
            if (entfernen) this.aktion = null;
        }
        if (this.mixer && entfernen) {
            this.mixer.stopAllAction();
            this.mixer = null;
        }
        // Netz in die Bindehaltung zuruecksetzen, sonst bleibt die letzte
        // Pose der alten Animation stehen.
        const figur = this.auswahl.figur;
        if (figur?.userData?.isSkinnedMesh) {
            const netz = figur.userData.skinnedMesh;
            if (netz?.isSkinnedMesh) netz.skeleton.pose();
        }
        this.abspieler.laeuft = false;
        window.isPlaying = false;
        window.activeMixer = this.mixer;
    }

    /** Eine Animation laden und aufspielen. */
    async laden(kategorie, name) {
        try {
            const liefVorher = this.abspieler.laeuft;
            this.anhalten(true);

            let dauer = await this._aufFigur(kategorie, name);
            if (dauer === null) dauer = await this._alsGerippe(kategorie, name);

            this.name = `${kategorie}/${name}`;
            window.activeMixer = this.mixer;
            this.abspieler.dauerSetzen(dauer);
            this.abspieler.zeit = 0;
            this._sequenzlaengeSetzen(dauer);
            this._weiterlaufen(liefVorher);
            Protokoll.debug('animationslauf', 'Animation geladen:', kategorie, name, dauer);
            return dauer;
        } catch (fehler) {
            console.error('Animation nicht ladbar:', fehler);
            alert('Animation laden fehlgeschlagen: ' + fehler.message);
            return 0;
        }
    }

    // ------------------------------------------------------------------ intern

    /**
     * Weg 1: auf die gewaehlte Figur. Gibt die Dauer zurueck — oder null, wenn
     * es keine Figur gibt und der Rueckfallweg greifen muss.
     */
    async _aufFigur(kategorie, name) {
        const figur = this.auswahl.figur;
        if (!figur) return null;
        const netz = this.skinner.umwandeln(figur);
        if (!netz || !this.skinner.skelett) return null;

        const clip = await fetchRetargetedClip(kategorie, name, this.skinner.skelett,
                                               { bodyHeight: this._hoehe(netz) });
        this.mixer = new THREE.AnimationMixer(netz);
        this.aktion = this.mixer.clipAction(clip);
        this.aktion.setLoop(THREE.LoopRepeat);
        this.aktion.play();
        this.aktion.paused = true;

        // Bild 0 sofort anwenden, sonst steht die Figur bis zum ersten
        // Abspielen in der Bindehaltung.
        this.mixer.setTime(0);
        netz.updateWorldMatrix(true, true);
        this.skinner.skelett.rootBone.updateWorldMatrix(true, true);

        const dauer = clip.duration || 1;
        Protokoll.debug('animationslauf', `✓ BVH umgezielt: ${dauer.toFixed(1)}s, ${clip.tracks.length} Spuren`);
        return dauer;
    }

    /** Weg 2: BVH als reines Knochengerippe in die Szene. */
    async _alsGerippe(kategorie, name) {
        const text = await fetchBVH(kategorie, name);
        const { mixer, action, duration } = loadBVHFromText(
            text, this.buehne.scene, `${kategorie}/${name}`);
        this.mixer = mixer;
        this.aktion = action;
        return duration;
    }

    _hoehe(netz) {
        const kasten = new THREE.Box3().setFromObject(netz);
        return kasten.isEmpty() ? Animationslauf.HOEHE_ERSATZ
                                : kasten.max.y - kasten.min.y;
    }

    /** Die Theatre-Sequenz genauso lang machen wie die Animation. */
    _sequenzlaengeSetzen(dauer) {
        try {
            const laenge = Math.ceil(dauer);
            this.buehne.studio.transaction(({ set }) => {
                set(this.buehne.sheet.sequence.pointer.length, laenge);
            });
            Protokoll.debug('animationslauf', `✓ Theatre-Sequenz auf ${laenge}s gesetzt`);
        } catch (fehler) {
            Protokoll.warnung('animationslauf', 'Sequenzlänge nicht setzbar:', fehler);
        }
    }

    /** Lief vorher etwas, laeuft auch das Neue weiter. */
    _weiterlaufen(liefVorher) {
        const knopf = document.getElementById('btnPlayPause');
        if (liefVorher) {
            this.abspieler.umschalten();
            knopf?.classList.add('playing');
            Protokoll.debug('animationslauf', '✓ neue Animation läuft weiter');
        } else {
            this.abspieler.laeuft = false;
            window.isPlaying = false;
            knopf?.classList.remove('playing');
        }
        this.abspieler.zeit = 0;
        this.abspieler.anzeigen();
    }
}
