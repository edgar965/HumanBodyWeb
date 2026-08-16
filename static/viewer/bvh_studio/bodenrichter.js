import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { Bvhtext } from './bvhtext.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bodenrichter — hebt oder senkt eine Animation so, dass der tiefste Fuß in
 * jedem Bild auf dem Boden steht.
 *
 * Aus werkzeug_boden.js herausgeloest (Umbau 16.08.2026):
 * `groundFixSelectedClip()` hatte 146 Zeilen und machte drei Dinge in einem —
 * prüfen und vorbereiten, Bild für Bild rechnen, und die BVH-Datei als TEXT
 * nachziehen. Der Textteil steckt jetzt in `Bvhtext`.
 */
export class Bodenrichter {

    /** Abstand über dem Boden, wenn der Fuß nicht darunter steckt (3 cm). */
    static VORGABE_ABSTAND = 0.03;
    /** Unter dieser Verschiebung lohnt keine Korrektur (1 mm). */
    static SCHWELLE = 0.001;
    /** Namensteile, an denen Fußknochen erkannt werden. */
    static FUSSNAMEN = ['foot', 'toe', 'heel'];

    /** Den gewählten Clip richten. */
    static async gewaehlten() {
        if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) {
            alert('Clip auswählen.');
            return null;
        }
        const spur = state.project.tracks[state.selectedTrackIdx];
        const clip = spur.clips[state.selectedClipIdx];
        if (!clip.animClip || !spur.skeleton) {
            alert('Clip oder Skeleton nicht geladen.');
            return null;
        }
        return new Bodenrichter(spur, clip).richten();
    }

    constructor(spur, clip) {
        this.spur = spur;
        this.clip = clip;
        this.abstand = parseFloat(
            document.getElementById('tool-ground-offset')?.value)
            || Bodenrichter.VORGABE_ABSTAND;
    }

    async richten() {
        const spur = this.positionsspur();
        if (!spur) {
            alert('Kein Position-Track gefunden.');
            return null;
        }
        const fuesse = this.fussknochen();
        if (!fuesse.length) {
            alert('Keine Fuß-Knochen gefunden.');
            return null;
        }
        pushUndo('Bodenniveau');
        Protokoll.debug('BVH Studio', `Boden: ${fuesse.length} Fußknochen — `
                    + fuesse.map(k => k.name).join(', '));
        const geaendert = this.hoehenKorrigieren(spur, fuesse);
        this.clip.groundFix = true;
        fn.updateProperties();
        fn.applyPlayhead();
        if (!geaendert) {
            Protokoll.debug('BVH Studio', `${this.clip.name}: schon auf Bodenniveau.`);
            return 0;
        }
        Protokoll.debug('BVH Studio', `Boden: ${geaendert}/${spur.times.length} `
                    + `Bilder korrigiert für ${this.clip.name}`);
        await this.dateiNachziehen(spur);
        return geaendert;
    }

    /** Die Positionsspur der Wurzel — nur sie verschiebt die ganze Figur. */
    positionsspur() {
        return this.clip.animClip.tracks.find(spur =>
            spur.name.includes('.position')) || null;
    }

    fussknochen() {
        return this.spur.skeleton.skeleton.bones.filter(knochen => {
            const name = knochen.name.toLowerCase();
            return Bodenrichter.FUSSNAMEN.some(teil => name.includes(teil));
        });
    }

    /**
     * Bild für Bild den tiefsten Fuß suchen und die Wurzel verschieben.
     * Ein eigener Mixer stellt dazu jeden Zeitpunkt her, ohne die Wiedergabe
     * der Seite zu stören.
     */
    hoehenKorrigieren(positionsspur, fuesse) {
        const mixer = new THREE.AnimationMixer(this.spur.mesh);
        const aktion = mixer.clipAction(this.clip.animClip);
        aktion.play();
        const punkt = new THREE.Vector3();
        const wurzel = this.spur.skeleton.rootBone;
        let geaendert = 0;

        for (let bild = 0; bild < positionsspur.times.length; bild++) {
            mixer.setTime(positionsspur.times[bild]);
            wurzel.updateWorldMatrix(true, true);
            let tiefste = Infinity;
            for (const knochen of fuesse) {
                knochen.getWorldPosition(punkt);
                if (punkt.y < tiefste) tiefste = punkt.y;
            }
            // Steckt der Fuß im Boden, kommt er genau auf 0; steht er darüber,
            // auf den eingestellten Abstand.
            const ziel = tiefste < 0 ? 0 : this.abstand;
            const verschiebung = tiefste - ziel;
            if (Math.abs(verschiebung) <= Bodenrichter.SCHWELLE) continue;
            // Werte liegen als x,y,z je Bild — y ist der zweite.
            positionsspur.values[bild * 3 + 1] -= verschiebung;
            geaendert++;
        }
        aktion.stop();
        mixer.stopAllAction();
        return geaendert;
    }

    /**
     * Die Korrektur auch in die BVH-Datei schreiben — sonst ist sie beim
     * nächsten Laden wieder weg.
     */
    async dateiNachziehen(positionsspur) {
        try {
            const datei = await Bvhtext.holen(this.clip.category, this.clip.name);
            const kanal = datei.kanal('Yposition');
            if (kanal < 0) {
                console.warn('[BVH Studio] Kein Yposition-Kanal, nicht gespeichert.');
                return false;
            }
            datei.kanalSetzen(kanal, positionsspur.times.length,
                              bild => positionsspur.values[bild * 3 + 1]);
            const gespeichert = await datei.speichern(this.clip.category,
                                                      this.clip.name);
            if (gespeichert) {
                Protokoll.info('BVH Studio', 'BVH gespeichert:',
                            `${this.clip.category}/${this.clip.name}`);
            }
            return gespeichert;
        } catch (fehler) {
            console.error('[BVH Studio] BVH nicht speicherbar:', fehler);
            return false;
        }
    }
}
