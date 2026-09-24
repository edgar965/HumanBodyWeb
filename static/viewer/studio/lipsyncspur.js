import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Lipsyncspur — ein Lippensynchronisations-Clip auf der Mimikspur, aus einer Tonspur.
 *
 * Edgar, 18.09.2026: „mach Lipsync." Der Weg: Rechtsklick auf die Mimikspur
 * → „Lippensynchronisation aus Tonspur" → der Server lässt Rhubarb Lip Sync
 * über die Tondatei laufen (`POST /api/studio/lipsync/`, Mundformen A–H/X mit
 * Zeiten) → ein Clip `lipsync` liegt genau unter dem Audio-Clip (gleicher
 * Start, gleiche Länge, gleicher `offset`). Je Bild rechnet `Mimikanwendung`
 * daraus die Reglerstellung (`Lipsynckurve`, `Lipsyncformen`): Daz-Visemes
 * bei Genesis 9, MB-Lab-Einheiten bei DEF-Figur und SMPL-X.
 *
 * Welcher Ton: der Audio-Clip, in dem der Klick liegt; sonst der erste des
 * Projekts. Die Cues kommen mit dem Projekt (`clip.data.cues`) — ein Neuladen
 * rechnet nicht noch einmal; der Server hält sie ohnehin neben der Datei.
 */
export class Lipsyncspur {

    static ADRESSE = '/api/studio/lipsync/';

    /** Alle Audio-Clips des Projekts mit ihrer Spur, in Zeitfolge. */
    static tonclips() {
        const aus = [];
        for (const spur of state.project.tracks) {
            if (spur.type !== 'audio') continue;
            for (const clip of spur.clips) {
                if (clip.type === 'audio' && clip.data?.audioUrl) aus.push({ spur, clip });
            }
        }
        return aus.sort((a, b) => a.clip.startFrame - b.clip.startFrame);
    }

    /** Der Audio-Clip zum Bild `frame`: der, in dem es liegt, sonst der erste. */
    static tonclipBei(frame) {
        const alle = Lipsyncspur.tonclips();
        const fps = state.project.fps;
        return alle.find(({ clip }) => frame >= clip.startFrame
            && frame < clip.startFrame + Math.round((clip.data.audioDuration || 0) * fps))
            || alle[0] || null;
    }

    /** Den Clip anlegen (oder den zu diesem Ton ersetzen); meldet über `meldung`. */
    static async anlegen(spur, frame, meldung = null) {
        const ton = Lipsyncspur.tonclipBei(frame);
        if (!ton) {
            meldung?.('Keine Tonspur mit hochgeladener Datei im Projekt');
            return null;
        }
        const d = ton.clip.data;
        meldung?.(`Lippensynchronisation: ${d.fileName || 'Ton'} wird gelesen …`);
        let antwort;
        try {
            antwort = await Serverabruf.senden(Lipsyncspur.ADRESSE, { audioUrl: d.audioUrl });
        } catch (fehler) {
            Protokoll.fehler('BVH Studio', 'Lippensynchronisation fehlgeschlagen', fehler);
            meldung?.(`Lippensynchronisation fehlgeschlagen: ${fehler.message || fehler}`);
            return null;
        }
        if (!antwort?.ok) {
            meldung?.(`Lippensynchronisation: ${antwort?.fehler || 'keine Antwort'}`);
            return null;
        }
        pushUndo('Lippensynchronisation');
        const alt = spur.clips.find(c => c.type === 'lipsync' && c.data?.audioUrl === d.audioUrl);
        if (alt) spur.clips.splice(spur.clips.indexOf(alt), 1);
        const clip = Lipsyncspur.clip(ton.clip, antwort);
        spur.clips.push(clip);
        spur.clips.sort((a, b) => a.startFrame - b.startFrame);
        state.selectedTrackIdx = state.project.tracks.indexOf(spur);
        state.selectedClipIdx = spur.clips.indexOf(clip);
        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updateProperties();
        meldung?.(`Lippensynchronisation: ${antwort.cues.length} Mundformen `
                  + `über ${antwort.dauer.toFixed(1)} s (${d.fileName || 'Ton'})`);
        return clip;
    }

    /** Der Clip unter dem Audio-Clip: gleicher Start, Länge = Ton, `offset` mit. */
    static clip(tonclip, antwort) {
        const fps = state.project.fps;
        const d = tonclip.data;
        const dauer = d.audioDuration || antwort.dauer || 0;
        const clip = new Clip(null, `Lipsync · ${d.fileName || 'Ton'}`,
                              Math.max(1, Math.round(dauer * fps)), fps);
        clip.type = 'lipsync';
        clip.startFrame = tonclip.startFrame;
        clip.data = {
            audioUrl: d.audioUrl, fileName: d.fileName || '',
            offset: d.offset || 0, dauer: antwort.dauer, cues: antwort.cues,
            erkenner: antwort.erkenner || '',
        };
        return clip;
    }

    /** Sekunden im Ton zum Bild `frame` — oder null außerhalb des Clips. */
    static tonzeit(clip, frame, fps) {
        const bilder = Math.max(0, (clip.totalFrames || 0) - (clip.trimIn || 0) - (clip.trimOut || 0));
        if (frame < clip.startFrame || frame >= clip.startFrame + bilder) return null;
        return (frame - clip.startFrame + (clip.trimIn || 0)) / fps + (clip.data?.offset || 0);
    }
}
