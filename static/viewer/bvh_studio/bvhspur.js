import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Bvhspur — den passenden Bewegungsclip am Abspielkopf laufen lassen.
 *
 * Herausgelöst aus `spur_anwenden.js` (288 Zeilen).
 *
 * WARUM SO VIEL PROTOKOLL
 * =======================
 * „Die Figur bewegt sich nicht" hat sechs Ursachen, und man sieht keine davon:
 * kein Mixer (Netz nicht geladen), kein `animClip` (Retarget gescheitert), kein
 * Clip an dieser Stelle, Clip mit falscher Länge, Skelett ohne Netzbindung. Jede
 * dieser Lagen schreibt eine Zeile — aber nur bei ZUSTANDSWECHSEL
 * (`_lastLogState`), sonst wären es 30 Zeilen je Sekunde.
 *
 * `uncacheClip` beim Wechsel: Ohne das hält der Mixer jede je gespielte
 * Animation im Speicher — bei einem langen Studio-Nachmittag sind das Hunderte.
 */
export class Bvhspur {

    static anwenden(spur, zeit) {
        if (!spur.mixer) {
            Bvhspur._melden(spur, 'no-mixer', 'bvh_no_mixer',
                            `track=${spur.name} mesh=${!!spur.mesh} preset=${spur.preset}`);
            return;
        }
        const gefunden = Bvhspur._laufen(spur, zeit);
        if (!gefunden) Bvhspur._anhalten(spur, zeit);
        if (!spur._modelControlled && spur.group) spur.group.visible = gefunden;
    }

    /** Den Clip finden, der `zeit` enthält, und ihn spielen. */
    static _laufen(spur, zeit) {
        for (const clip of spur.clips) {
            if (!clip.animClip) {
                Bvhspur._ohneAnimation(spur, clip);
                continue;
            }
            const beginn = clip.startFrame / state.project.fps;
            if (zeit < beginn || zeit >= beginn + clip.duration) continue;
            const ort = (zeit - beginn) * clip.speed + clip.trimIn / clip.fps;
            if (spur._activeClip !== clip) Bvhspur._starten(spur, clip, zeit, ort);
            else if (!spur._activeAction.isRunning()) Bvhspur._weiter(spur, clip);
            spur._activeAction.time = ort;
            spur.mixer.setTime(ort);
            spur._lastLogState = 'playing';
            return true;
        }
        return false;
    }

    static _starten(spur, clip, zeit, ort) {
        spur.mixer.stopAllAction();
        // Ohne `uncacheClip` bleibt jede gespielte Animation im Mixer liegen.
        if (spur._activeClip?.animClip) {
            spur.mixer.uncacheClip(spur._activeClip.animClip);
        }
        spur._activeAction = spur.mixer.clipAction(clip.animClip);
        spur._activeAction.setLoop(THREE.LoopRepeat, Infinity);
        spur._activeAction.clampWhenFinished = false;
        spur._activeAction.play();
        spur._activeClip = clip;
        fn.serverLog('bvh_action_start',
            `track=${spur.name} clip=${clip.name} t=${zeit.toFixed(2)}s `
            + `localT=${ort.toFixed(2)}s trackCount=${clip.animClip.tracks.length} `
            + `mixerRoot=${spur.mixer.getRoot()?.name || '?'} `
            + `meshSkel=${!!spur.mesh?.skeleton}`);
    }

    static _weiter(spur, clip) {
        spur._activeAction.reset();
        spur._activeAction.play();
        fn.serverLog('bvh_action_resume', `track=${spur.name} clip=${clip.name}`);
    }

    static _ohneAnimation(spur, clip) {
        if (clip._noAnimClipLogged) return;
        clip._noAnimClipLogged = true;
        fn.serverLog('bvh_clip_no_animclip',
                     `track=${spur.name} clip=${clip.name} cat=${clip.category}`);
    }

    /** Kein Clip an dieser Stelle: anhalten und in die Ruhelage. */
    static _anhalten(spur, zeit) {
        if (spur._activeClip) {
            spur.mixer.stopAllAction();
            const alter = spur._activeClip;
            spur._activeClip = null;
            spur._activeAction = null;
            if (spur.skeleton) spur.skeleton.skeleton.pose();
            fn.serverLog('bvh_action_stop',
                         `track=${spur.name} clip=${alter.name} `
                         + `t=${zeit.toFixed(2)}s (out of range)`);
            spur._lastLogState = 'stopped';
            return;
        }
        Bvhspur._melden(spur, 'no-clip-in-range', 'bvh_no_clip_in_range',
                        `track=${spur.name} t=${zeit.toFixed(2)}s `
                        + `clips=[${Bvhspur._bereiche(spur) || 'none'}]`);
    }

    static _bereiche(spur) {
        return spur.clips.map(clip => {
            const beginn = clip.startFrame / state.project.fps;
            return `${clip.name}@${beginn.toFixed(1)}-${(beginn + clip.duration).toFixed(1)}s`;
        }).join(',');
    }

    /** Eine Zeile schreiben, aber nur bei Zustandswechsel. */
    static _melden(spur, zustand, marke, text) {
        if (spur._lastLogState === zustand) return;
        spur._lastLogState = zustand;
        fn.serverLog(marke, text);
    }
}
