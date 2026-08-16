/**
 * Projektnachladen — die beiden Clip-Arten, die beim Laden Daten vom Server holen:
 * 3D-Objekte und Tonspuren.
 *
 * Aus project.js herausgeloest (Umbau 16.08.2026): Beides stand als je ein
 * `loadPromises.push((async () => { … })())` mitten in der 191 Zeilen langen
 * Wiederherstellungsschleife.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

export class Projektnachladen {
    /**
     * 3D-Objekt eines gespeicherten object_clip wieder in die Spur laden.
     *
     * `_loadSceneObjectIntoTrack` legt selbst einen Clip an — wir haben aber schon
     * einen (aus der Projektdatei). Darum wird der neu angelegte danach entfernt,
     * sonst steht das Objekt doppelt in der Zeitleiste.
     */
    static async objekt(track, td, clip) {
        try {
            const se = await import('./objektimport.js');
            const vorher = track.clips.length;
            await se._loadSceneObjectIntoTrack(
                track, clip.data.url, clip.data.fileName || 'object',
                clip.data.ext || 'obj', clip.startFrame, clip.data.mtlUrl || null);
            if (track.clips.length > vorher) track.clips.pop();  // Duplikat weg
            // Gespeicherte Lage anwenden — ueberschreibt die Auto-Normalisierung.
            if (track.mesh) Projektnachladen._lageSetzen(track, td);
        } catch (e) {
            console.warn('[Restore] 3D-Objekt reload failed:', clip.data?.fileName, e);
        }
    }

    static _lageSetzen(track, td) {
        const { objectPosition: p, objectRotation: r } = td;
        if (p) track.mesh.position.set(p.x, p.y, p.z);
        if (r) track.mesh.rotation.set(r.x, r.y, r.z);
        if (td.objectScale != null) track.mesh.scale.setScalar(td.objectScale);
        if (td.objectTint) fn.setObjectTint?.(track, td.objectTint);
    }

    /** Tondatei erneut holen und dekodieren. */
    static async ton(track, clip) {
        try {
            if (!track.audioCtx) {
                track.audioCtx = state.project._audioCtx
                    || (state.project._audioCtx =
                        new (window.AudioContext || window.webkitAudioContext)());
                track.gainNode = track.audioCtx.createGain();
                track.gainNode.connect(track.audioCtx.destination);
            }
            const resp = await fetch(clip.data.audioUrl);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            clip.data.audioBuffer =
                await track.audioCtx.decodeAudioData(await resp.arrayBuffer());
            clip._needsReload = false;
            console.log('[Restore] Audio reloaded:', clip.data.fileName);
        } catch (e) {
            console.warn('[Restore] Audio reload failed:', clip.data?.fileName, e);
            clip._needsReload = true;
        }
    }
}
