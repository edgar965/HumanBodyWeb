import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Studioanzeige } from './studioanzeige.js';
import { Cliplaenge } from './cliplaenge.js';

/**
 * Clipbearbeitung — Clips duplizieren, löschen, kürzen, teilen.
 *
 * Herausgelöst aus `spur_clips.js` (298 Zeilen).
 *
 * DIE KÜRZEN-RECHNUNG HAT EINEN NACHGERECHNETEN GRUND (Review 13.08.2026)
 * ======================================================================
 * `Math.max(…)` UM die Begrenzung herum, nicht nur `Math.min`:
 *
 *     trimIn=5, trimOut=maxTrim−2  ->  maxTrim−trimOut = 2  ->  min(2, 15) = 2
 *
 * Ein Klick auf „Anfang kürzen" hat den Clip damit VERLÄNGERT. Jetzt bleibt der
 * Wert stehen, wenn die Grenze erreicht ist.
 *
 * WAS BEIM LÖSCHEN AUFGERÄUMT WIRD
 * ================================
 * Der Mixer hält gespielte Animationen (`uncacheClip`), ein Modellclip steuert
 * die Figur einer anderen Spur (die muss verschwinden), und ein 3D-Objekt-Clip
 * ist das letzte, was ein Objekt in der Szene hält — dort wird das Netz wirklich
 * entfernt und sein Speicher freigegeben, nicht nur unsichtbar gemacht.
 */
export class Clipbearbeitung {

    /** Der ausgewählte Clip und seine Spur — oder `null`. */
    static auswahl() {
        if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) return null;
        const spur = state.project.tracks[state.selectedTrackIdx];
        if (!spur || state.selectedClipIdx >= spur.clips.length) return null;
        return { spur, clip: spur.clips[state.selectedClipIdx] };
    }

    // ------------------------------------------------------------ Duplizieren

    /** Kopie hinter dem Original — mit derselben Bewegung (geteilt). */
    static duplizieren() {
        const wahl = Clipbearbeitung.auswahl();
        if (!wahl) return;
        pushUndo('Duplizieren');
        const { spur, clip } = wahl;
        const kopie = new Clip(clip.category, clip.name, clip.totalFrames,
                               clip.fps);
        kopie.startFrame = clip.endFrame;
        Clipbearbeitung._eigenschaften(clip, kopie);
        spur.clips.push(kopie);
        Clipbearbeitung._nachtragen();
        fn.serverLog('clip_duplicated');
    }

    /** Die Bearbeitungswerte eines Clips auf einen anderen übertragen. */
    static _eigenschaften(quelle, ziel) {
        ziel.trimIn = quelle.trimIn;
        ziel.trimOut = quelle.trimOut;
        ziel.speed = quelle.speed;
        ziel.smoothSigma = quelle.smoothSigma;
        ziel.groundFix = quelle.groundFix;
        // Dieselbe Animation, nicht kopiert: Sie kann mehrere Megabyte haben.
        ziel.animClip = quelle.animClip;
    }

    // ----------------------------------------------------------------- Löschen

    static loeschen() {
        const wahl = Clipbearbeitung.auswahl();
        if (!wahl) return;
        pushUndo('Clip löschen');
        const { spur, clip } = wahl;
        Clipbearbeitung._mixerLoesen(spur, clip);
        spur.clips.splice(state.selectedClipIdx, 1);
        state.selectedClipIdx = -1;
        Clipbearbeitung._figurVerstecken(spur, clip);
        Clipbearbeitung._objektEntfernen(spur, clip);
        Clipbearbeitung._nachtragen();
        fn.applyPlayhead?.();
        Clipbearbeitung._leereSpur(spur);
        Clipbearbeitung._wiedergabeAnhalten();
        fn.serverLog('clip_deleted');
    }

    static _mixerLoesen(spur, clip) {
        if (spur.mixer) {
            spur.mixer.stopAllAction();
            if (clip.animClip) spur.mixer.uncacheClip(clip.animClip);
        }
        spur._activeClip = null;
        spur._activeAction = null;
    }

    /** Modellclip weg -> die Figur der verknüpften Bewegungsspur verstecken. */
    static _figurVerstecken(spur, clip) {
        if (clip.type !== 'model' || spur.type !== 'model') return;
        spur._currentPreset = null;
        const bewegung = state.project.getLinkedAnimation(spur);
        if (bewegung?.group) bewegung.group.visible = false;
    }

    /**
     * Letzter Objektclip weg -> Netz wirklich aus der Szene nehmen.
     *
     * `applyPlayhead` würde es nur unsichtbar machen; gemeint ist aber „weg",
     * samt Grafikspeicher (`dispose`).
     */
    static _objektEntfernen(spur, clip) {
        if (clip.type !== 'object_clip' || spur.type !== 'scene_object') return;
        if (spur.clips.some(rest => rest.type === 'object_clip')) return;
        if (!spur.mesh) return;
        state.scene.remove(spur.mesh);
        spur.mesh.traverse?.(teil => {
            teil.geometry?.dispose?.();
            const werkstoff = teil.material;
            if (Array.isArray(werkstoff)) werkstoff.forEach(m => m.dispose?.());
            else werkstoff?.dispose?.();
        });
        spur.mesh = null;
        spur.objectUrl = null;
        spur.objectMtlUrl = null;
        fn.detachTransformControls?.();
    }

    static _leereSpur(spur) {
        if (spur.type === 'bvh' && spur.clips.length === 0 && spur.group) {
            spur.group.visible = false;
        }
        // Zurück in die Ruhelage, sonst bleibt die letzte Haltung stehen.
        spur.skeleton?.skeleton.pose();
    }

    static _wiedergabeAnhalten() {
        const nochClips = state.project.tracks.some(spur => spur.clips.length > 0);
        if (nochClips || !state.playing) return;
        state.playing = false;
        const zeichen = document.getElementById('pb-play-icon');
        if (zeichen) zeichen.className = 'fas fa-play';
    }

    // ------------------------------------------------------------------ Kürzen

    /** `start`, `end` oder `reset` — siehe Klassendoku zur Rechnung. */
    static kuerzen(art, bilder = 10) {
        const wahl = Clipbearbeitung.auswahl();
        if (!wahl) return;
        pushUndo('Trim');
        const clip = wahl.clip;
        if (clip.type !== 'bvh') return;
        const grenze = clip.totalFrames - 1;
        if (art === 'start') {
            clip.trimIn = Math.max(clip.trimIn,
                Math.min(grenze - clip.trimOut, clip.trimIn + bilder));
        } else if (art === 'end') {
            clip.trimOut = Math.max(clip.trimOut,
                Math.min(grenze - clip.trimIn, clip.trimOut + bilder));
        } else if (art === 'reset') {
            clip.trimIn = 0;
            clip.trimOut = 0;
        }
        Clipbearbeitung._nachtragen();
        Protokoll.debug('BVH Studio',
                        `Trim ${art}: in=${clip.trimIn}, out=${clip.trimOut}`);
    }

    // ------------------------------------------------------------------ Teilen

    /**
     * Den Clip unter dem Abspielkopf in zwei teilen.
     *
     * Beide Hälften teilen dieselbe Bewegung; getrennt wird über `trimIn` und
     * `trimOut`. Ein Kopieren der Animation wäre unnötig und teuer.
     */
    static teilen() {
        if (state.selectedTrackIdx < 0) return;
        pushUndo('Split');
        const spur = state.project.tracks[state.selectedTrackIdx];
        const zeit = state.playheadFrame / state.project.fps;
        for (let i = 0; i < spur.clips.length; i++) {
            const clip = spur.clips[i];
            const beginn = clip.startFrame / state.project.fps;
            if (zeit <= beginn || zeit >= beginn + clip.duration) continue;
            const stelle = Math.round((zeit - beginn) * clip.fps * clip.speed)
                + clip.trimIn;
            spur.clips.splice(i + 1, 0, Clipbearbeitung._zweiteHaelfte(clip, stelle));
            clip.trimOut = clip.totalFrames - stelle;
            fn.updateDuration();
            fn.renderTimeline();
            Protokoll.debug('BVH Studio', `Split clip at frame ${stelle}`);
            return;
        }
    }

    static _zweiteHaelfte(clip, stelle) {
        const zweite = new Clip(clip.category, clip.name, clip.totalFrames,
                                clip.fps);
        zweite.type = clip.type;
        zweite.startFrame = state.playheadFrame;
        Clipbearbeitung._eigenschaften(clip, zweite);
        zweite.trimIn = stelle;
        if (clip.data) zweite.data = { ...clip.data };
        return zweite;
    }

    // ------------------------------------------------------------------ Länge

    /**
     * Länge des gewählten Clips setzen — `art` 'prozent' oder 'sekunden';
     * ohne `wert` fragt ein Dialog, vorbelegt mit dem Stand (Edgar, 13.09.2026:
     * „keine Längenvorgaben! … Kontextmenüs, wo man die Länge setzen kann").
     */
    static laenge(art, wert = null) {
        const wahl = Clipbearbeitung.auswahl();
        if (!wahl || !['bvh', 'audio', 'model'].includes(wahl.clip.type)) return;
        const clip = wahl.clip;
        const bezug = clip.type === 'model' ? Clipbearbeitung._modellbezug(clip) : null;
        const vorher = Cliplaenge.stand(clip, bezug);
        if (wert == null) {
            const ganzes = clip.type === 'model' ? 'des Projektendes (ohne diesen Clip)' : 'der ganzen Animation';
            const frage = art === 'prozent'
                ? `Länge in Prozent ${ganzes} (jetzt ${vorher.prozent.toFixed(0)} %):`
                : `Länge in Sekunden (jetzt ${vorher.sekunden.toFixed(1)} s, ganz ${vorher.ganz.toFixed(1)} s):`;
            const vorgabe = art === 'prozent' ? vorher.prozent.toFixed(0) : vorher.sekunden.toFixed(1);
            wert = Cliplaenge.zahl(prompt(frage, vorgabe));
            if (wert == null) return;
        }
        pushUndo('Clip-Länge');
        const stand = art === 'prozent' ? Cliplaenge.prozent(clip, wert, bezug)
                                        : Cliplaenge.sekunden(clip, wert, bezug);
        Clipbearbeitung._nachtragen();
        Studioanzeige.melden(`${clip.name}: ${stand.sekunden.toFixed(1)} s (${stand.prozent.toFixed(0)} %)`);
        Protokoll.debug('BVH Studio', `Länge ${art} ${wert}: ${stand.sekunden.toFixed(2)} s, `
                        + `trimOut=${clip.trimOut}`);
    }

    /**
     * Woran sich die Prozent eines Modellclips messen: am Ende der ANDEREN
     * Clips. Die Projektdauer selbst taugt nicht — sie ist das Ende des
     * längsten Clips, oft dieses Modellclips: 50 % hätten die Dauer halbiert,
     * und 100 % danach wären die halbe geblieben (gemessen 13.09.2026: 5520 →
     * 2760 → 2760). Ohne andere Clips zählt seine bisherige Länge.
     */
    static _modellbezug(clip) {
        let ende = 0;
        for (const spur of state.project.tracks) {
            for (const anderer of spur.clips) {
                if (anderer !== clip && anderer.endFrame > ende) ende = anderer.endFrame;
            }
        }
        return ende > 0 ? ende : clip.totalFrames;
    }

    /** Dauer, Zeitleiste, Eigenschaften — siehe `Studioanzeige`. */
    static _nachtragen() {
        Studioanzeige.nachtragen();
    }
}

fn.clipLaenge = (art, wert) => Clipbearbeitung.laenge(art, wert);
