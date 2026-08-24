import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { sharedState } from '../character_core.js?v=1';
import { loadTrackCharacter } from './spur_charakter.js';

/**
 * Clipanimation — die retargetete Bewegung eines Clips holen und einhängen.
 *
 * Herausgelöst aus `spur_clips.js` (298 Zeilen).
 *
 * DIE PUNKTE IN DEN KNOCHENNAMEN SIND DER KERN
 * ============================================
 * Three.js' `PropertyBinding` liest einen Punkt als Trenner:
 *
 *     "DEF-spine.001.quaternion"  ->  Objekt "DEF-spine", Eigenschaft "001"
 *
 * Das ist falsch und die Animation greift ins Leere — ohne Fehlermeldung, die
 * Figur steht einfach still. Deshalb werden Punkte in Knochennamen zu
 * Unterstrichen, und zwar an BEIDEN Stellen: im Skelett (`_namenEntschaerfen`)
 * und beim Bauen der Spuren.
 *
 * DIE NACHBEARBEITUNG BEIM LADEN
 * ==============================
 * Ist die Gauß-Glättung aktiv, wird sie sofort angewandt — und die Rohwerte
 * VORHER gesichert (`origClips`), sonst lässt sich die Glättung nie mehr
 * abschalten. Dasselbe für die feste Position.
 */
export class Clipanimation {

    static ENDPUNKT = '/api/retarget/';

    /** Bewegung laden, glätten, einhängen. */
    static async laden(spur, clip) {
        const daten = await Clipanimation._holen(clip);
        if (!daten) return;
        if (!daten.tracks || !daten.frame_count) {
            Protokoll.warnung('BVH Studio', `No animation data for ${clip.name}`);
            return;
        }
        clip.totalFrames = daten.frame_count;
        clip.fps = daten.frame_count / daten.duration;
        await Clipanimation._figurSichern(spur);
        if (spur.skeleton) {
            clip.animClip = Clipanimation.bauen(daten, spur.skeleton);
            fn.serverLog('clip_loaded',
                         `${clip.name} (${clip.totalFrames}f, `
                         + `${clip.duration.toFixed(1)}s)`);
            Clipanimation._nachbearbeiten(clip);
        }
        fn.updateDuration();
        fn.renderTimeline();
    }

    static async _holen(clip) {
        const adresse = `${Clipanimation.ENDPUNKT}?category=`
            + `${encodeURIComponent(clip.category)}&name=`
            + `${encodeURIComponent(clip.name)}`;
        try {
            return await Serverabruf.json(adresse);
        } catch (fehler) {
            // Der Clip bleibt in der Zeitleiste, aber als fehlerhaft markiert —
            // so sieht der Nutzer, WELCHER Clip nicht geladen hat.
            Protokoll.fehler('BVH Studio',
                             `Retarget failed for ${clip.category}/${clip.name}`,
                             fehler);
            clip._loadError = true;
            fn.renderTimeline();
            return null;
        }
    }

    /** Figur nachladen, wenn die Spur noch keine hat. */
    static async _figurSichern(spur) {
        if (spur.mesh) return;
        if (!sharedState.rigifySkeletonData || !sharedState.skinWeightData) return;
        await loadTrackCharacter(spur);
        if (spur.group) spur.group.visible = true;
    }

    // ------------------------------------------------------------------ Bauen

    /** Aus der Serverantwort einen `THREE.AnimationClip`. */
    static bauen(daten, skelett) {
        const spuren = [];
        const zeiten = daten.times.map(zeit => zeit);
        for (const [knochenname, werte] of Object.entries(daten.tracks)) {
            const knochen = skelett.boneByName[Clipanimation.jsName(knochenname)];
            if (!knochen) continue;
            spuren.push(new THREE.QuaternionKeyframeTrack(
                knochen.name + '.quaternion', zeiten, werte));
        }
        Clipanimation._ortsspur(daten, skelett, zeiten, spuren);
        return new THREE.AnimationClip('clip', daten.duration, spuren);
    }

    static _ortsspur(daten, skelett, zeiten, spuren) {
        if (!daten.position_track) return;
        const knochen = skelett.boneByName[
            Clipanimation.jsName(daten.position_track.bone)];
        if (!knochen) return;
        spuren.push(new THREE.VectorKeyframeTrack(
            knochen.name + '.position', zeiten, daten.position_track.values));
    }

    /** `DEF-spine.001` -> `DEF-spine_001` (siehe Klassendoku). */
    static jsName(name) {
        return name.replace(/\./g, '_');
    }

    /** Punkte in allen Knochennamen eines Skeletts entschärfen. */
    static namenEntschaerfen(skelett) {
        if (skelett.skeleton) {
            for (const knochen of skelett.skeleton.bones) {
                knochen.name = Clipanimation.jsName(knochen.name);
            }
        }
        if (skelett.boneByName) {
            const neu = {};
            for (const [name, knochen] of Object.entries(skelett.boneByName)) {
                neu[Clipanimation.jsName(name)] = knochen;
            }
            skelett.boneByName = neu;
        }
    }

    // ---------------------------------------------------------- Nachbearbeiten

    static _nachbearbeiten(clip) {
        Clipanimation._glaetten(clip);
        const festeLage = fn.getFixedPos ? fn.getFixedPos() : null;
        if (festeLage?.active && clip.animClip) fn.applyFixedPositionAll();
    }

    /**
     * Gauß-Glättung anwenden — mit Sicherung der Rohwerte.
     *
     * Ohne die Sicherung (`origClips`) ließe sich die Glättung nie zurücknehmen:
     * Sie arbeitet in den Werten des Clips, und die kämen erst beim nächsten
     * Laden wieder vom Server.
     */
    static _glaetten(clip) {
        const glaettung = fn.getGaussSmooth();
        if (!glaettung?.active || !clip.animClip) return;
        const sicherung = {};
        for (const spur of clip.animClip.tracks) {
            sicherung[spur.name] = new Float32Array(spur.values);
        }
        glaettung.origClips.set(`${clip.category}/${clip.name}`, sicherung);
        for (const spur of clip.animClip.tracks) {
            fn.gaussFilter(spur.values, spur.getValueSize(), glaettung.sigma);
        }
        fn.serverLog('gauss_auto_applied',
                     `${clip.name} sigma=${glaettung.sigma}`);
    }
}
