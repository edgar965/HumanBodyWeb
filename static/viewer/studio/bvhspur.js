import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Retargetziel } from './retargetziel.js';
import { Spurfigurarten } from './spurfigurarten.js';
import { Zeitkurve } from './zeitkurve.js';
import { Effektebindung } from './effektebindung.js';

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

    /**
     * `zeit` ist Wanduhrzeit (Abspielkopf). Eine verknuepfte Effekte-Spur
     * (`effektebindung.js`) kann sie auf eine andere Stelle im Quellmaterial
     * abbilden — Standbild und Zeitlupe/-raffer ohne den Clip zu schneiden
     * (Edgar, 21.09.2026, „andersrum"). Ohne verknuepfte Effekte-Spur ist die
     * Abbildung die Identitaet, bitgleich mit vorher.
     */
    static anwenden(spur, zeit) {
        if (!spur.mixer) {
            Bvhspur._melden(spur, 'no-mixer', 'bvh_no_mixer',
                            `track=${spur.name} mesh=${!!spur.mesh} preset=${spur.preset}`);
            return;
        }
        const bvhIdx = state.project.indexOf(spur);
        const inhaltBild = Effektebindung.inhaltBild(bvhIdx, Math.round(zeit * state.project.fps));
        const inhaltZeit = inhaltBild / state.project.fps;
        const gefunden = Bvhspur._laufen(spur, inhaltZeit);
        if (!gefunden) Bvhspur._anhalten(spur, inhaltZeit);
        if (!spur._modelControlled && spur.group) spur.group.visible = gefunden;
    }

    /** Den Clip finden, der `zeit` enthält, und ihn spielen. */
    static _laufen(spur, zeit) {
        const ziel = Retargetziel.wahl(spur.modell, spur.figurHoehe).schluessel;
        for (const clip of spur.clips) {
            if (clip.animClip && clip._animZiel !== ziel) Bvhspur._neuHolen(spur, clip);
            if (!clip.animClip) {
                Bvhspur._ohneAnimation(spur, clip);
                continue;
            }
            const beginn = clip.startFrame / state.project.fps;
            if (zeit < beginn || zeit >= beginn + clip.duration) continue;
            const ort = Bvhspur._quellzeit(clip, zeit, beginn);
            if (spur._activeClip !== clip) Bvhspur._starten(spur, clip, zeit, ort);
            else if (!spur._activeAction.isRunning()) Bvhspur._weiter(spur, clip);
            spur._activeAction.time = ort;
            spur.mixer.setTime(ort);
            spur._lastLogState = 'playing';
            return true;
        }
        return false;
    }

    /**
     * Stelle im Quellmaterial (Sekunden ab dessen Bild 0), die bei `zeit`
     * gezeigt wird.
     *
     * Standbild (`type: 'freeze'`): immer derselbe, beim Einfügen
     * festgehaltene Zeitpunkt — die Pose bewegt sich nicht (`clipbearbeitung.js`).
     *
     * Normaler BVH-Clip MIT Kurve (`data.remap`, `zeitkurve.js`): `u` ist der
     * Zeitanteil seit Clipbeginn, `Zeitkurve.quellanteil` biegt ihn zu einem
     * Quellanteil `v` — ohne Punkte ist das exakt `v=u`, also bitgleich mit
     * der Formel darunter (siehe `Zeitkurve`-Klassendoku).
     *
     * Ohne Kurve: die bisherige Formel unverändert — konstantes `speed`.
     */
    static _quellzeit(clip, zeit, beginn) {
        if (clip.type === 'freeze') return clip.data.sourceTime;
        if (!clip.data?.remap?.length) {
            return (zeit - beginn) * clip.speed + clip.trimIn / clip.fps;
        }
        const u = clip.duration > 0 ? (zeit - beginn) / clip.duration : 0;
        const quellbereich = clip.totalFrames - clip.trimIn - clip.trimOut;
        const v = Zeitkurve.quellanteil(clip.data.remap, u);
        return (clip.trimIn + v * quellbereich) / clip.fps;
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

    /**
     * Der Clip ist auf ein anderes Skelett gebaut (die Figur hat die Art
     * gewechselt, 15.09.2026): Spuren nennen Knochen beim Namen, also neu
     * holen — einmal, nicht je Bild.
     */
    static _neuHolen(spur, clip) {
        if (spur._activeClip === clip) {
            spur.mixer.stopAllAction();
            spur._activeClip = null;
            spur._activeAction = null;
        }
        clip.animClip = null;
        clip._noAnimClipLogged = false;
        fn.serverLog('bvh_clip_retarget_again', `track=${spur.name} clip=${clip.name}`);
        fn.loadClipAnimation(spur, clip);
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
            Spurfigurarten.ruhelage(spur);
            fn.serverLog('bvh_action_stop',
                         `track=${spur.name} clip=${alter.name} `
                         + `t=${zeit.toFixed(2)}s (out of range)`);
            spur._lastLogState = 'stopped';
            return;
        }
        // Liegt HIER ein Clip, der nur keine Animation hat (Datei fehlt,
        // Retarget gescheitert — `_loadError`/`clipfehlt.js`), ist „keine
        // Bewegung hier" die falsche Meldung: Sie klingt nach einer Lücke,
        // dabei liegt hier ein Clip, dessen Schicksal längst geklärt ist
        // (der Nutzer hat ihn über den Dialog bewusst stehen lassen oder er
        // verschwindet gleich). Edgar, 24.09.2026: „mach die weg" — kein
        // eigener Text dafür, `_lastLogState` bleibt unbekannt und
        // `zeitleiste_spuren.js` zeigt dann gar nichts (Fallthrough).
        if (Bvhspur._kaputterClipHier(spur, zeit)) {
            spur._lastLogState = 'clip-broken';
            return;
        }
        Bvhspur._melden(spur, 'no-clip-in-range', 'bvh_no_clip_in_range',
                        `track=${spur.name} t=${zeit.toFixed(2)}s `
                        + `clips=[${Bvhspur._bereiche(spur) || 'none'}]`);
    }

    /** Deckt ein Clip OHNE Animation gerade `zeit` ab? */
    static _kaputterClipHier(spur, zeit) {
        return spur.clips.some((clip) => {
            if (clip.animClip) return false;
            const beginn = clip.startFrame / state.project.fps;
            return zeit >= beginn && zeit < beginn + clip.duration;
        });
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
