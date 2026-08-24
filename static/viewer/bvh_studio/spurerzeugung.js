import * as THREE from 'three';
import { state, TRACK_COLORS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track } from './models.js';
import { pushUndo } from './undo.js';
import { createLightHelper } from './spur_lichter.js';
import { Spurauswahl } from './spurauswahl.js';

/**
 * Spurerzeugung — neue Spuren im Studio anlegen.
 *
 * Herausgelöst aus `tracks.js` (324 Zeilen). Es gibt drei Sorten, und sie
 * unterscheiden sich mehr, als der gemeinsame Name vermuten lässt:
 *
 * * **Animation** — bekommt Modell und Körpertyp aus den Projektvorgaben. Das
 *   Netz wird NICHT hier geladen, sondern erst, wenn der erste BVH-Clip kommt.
 * * **Modell** — steuert eine Animationsspur an (`_linkedAnimIdx`), hat selbst
 *   kein Netz.
 * * **Besonders** (Kamera, Licht, Audio, Szenenobjekt) — jede mit eigenem
 *   Zubehör: Lichtquelle plus Helfer, Tonkanal, leeres Objekt.
 */
export class Spurerzeugung {

    static ERSATZMODELL = 'Rig2';
    static ERSATZKOERPER = 'Female_Caucasian';
    static NAMEN = { camera: 'Kamera', light: 'Licht', audio: 'Audio' };
    static OBJEKTFARBE = '#7c5cbf';

    /** Eine Animationsspur (BVH-Clips). */
    static animation(name) {
        pushUndo('Spur hinzufügen');
        const nummer = state.project.animations.length + 1;
        const spur = new Track(
            name || `Animation ${nummer}`,
            state.project.defaultModel || Spurerzeugung.ERSATZMODELL,
            state.project.defaultBodyType || Spurerzeugung.ERSATZKOERPER);
        return Spurerzeugung._einhaengen(spur, true);
    }

    /** Eine Modellspur — sie stellt die Figur einer Animationsspur. */
    static modell(name) {
        pushUndo('Modell-Spur hinzufügen');
        const nummer = state.project.modelTracks.length + 1;
        const spur = new Track(name || `Modell ${nummer}`);
        spur.type = 'model';
        spur.color = TRACK_COLORS.model;
        spur.muted = false;
        spur._currentPreset = null;
        spur._linkedAnimIdx = -1;
        return Spurerzeugung._einhaengen(spur, false);
    }

    /** Kamera, Licht, Ton oder Szenenobjekt. */
    static besonders(art, name) {
        pushUndo('Spur hinzufügen');
        const spur = new Track(name || Spurerzeugung.NAMEN[art] || art);
        spur.type = art;
        spur.color = TRACK_COLORS[art] || spur.color;
        Spurerzeugung._zubehoer[art]?.(spur);
        state.project.addTrack(spur);
        fn.updateTrackHeaders();
        Spurauswahl.waehlen(state.project.tracks.length - 1);
        return spur;
    }

    /** Was eine besondere Spur über den Namen hinaus braucht. */
    static _zubehoer = {
        camera(spur) {
            spur.cameraActive = true;
        },
        light(spur) {
            // Vom Nutzer erzeugte Lichtspur = Spotlicht.
            spur.light = new THREE.SpotLight(0xffffff, 2.0, 50, Math.PI / 6,
                                             0.3, 1);
            spur.light.position.set(2, 3, 2);
            spur.light.target.position.set(0, 0, 0);
            state.scene.add(spur.light);
            state.scene.add(spur.light.target);
            spur.lightType = 'spot';
            spur.lightHelper = createLightHelper(spur.light);
            if (spur.lightHelper) state.scene.add(spur.lightHelper);
            spur.lightVisible = false;   // Helferlinien: aus
            spur.coneVisible = true;     // Lichtkegel: an
        },
        audio(spur) {
            // EIN Tonkontext für das ganze Projekt: Browser erlauben nur
            // wenige, und jeder weitere bliebe stumm.
            spur.audioCtx = state.project._audioCtx
                || (state.project._audioCtx = new (window.AudioContext
                    || window.webkitAudioContext)());
            spur.gainNode = spur.audioCtx.createGain();
            spur.gainNode.connect(spur.audioCtx.destination);
        },
        scene_object(spur) {
            spur.subtype = 'custom';
            spur.color = Spurerzeugung.OBJEKTFARBE;
            spur.mesh = null;   // kommt über „Hinzufügen" im Kontextmenü
            spur.objectTint = '#ffffff';
            // Szene-Gruppe aufklappen, damit die neue Spur zu sehen ist.
            state.sceneGroupCollapsed = false;
        },
    };

    static _einhaengen(spur, inSzene) {
        state.project.addTrack(spur);
        if (inSzene) state.scene.add(spur.group);
        fn.updateTrackHeaders();
        fn.renderTimeline();
        Spurauswahl.waehlen(state.project.tracks.length - 1);
        return spur;
    }
}
