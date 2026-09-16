import { state, TRACK_COLORS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track, Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Spurauswahl } from './spurauswahl.js';
import { Lebendigkeit } from './lebendigkeit.js';
import { Mimikbasis } from './mimikbasis.js';

/**
 * Scriptspur — die Script-Spur einer Modellspur: anlegen, Clips setzen.
 *
 * Edgar, 15.09.2026: „Hinzufügen … Animation mit normaler Animation, Mimik
 * und Script." Die Spur hängt wie die Mimikspur an einer Modellspur
 * (`_modellIdx`) und steht eingerückt darunter. Ein Clip `script` trägt in
 * `data` die Lebendigkeits-Einstellungen (Blinzeln, Blick, … Saat) und wirkt,
 * solange der Abspielkopf in ihm steht (`Scriptzuschlag`). Bis 14.09.2026
 * hing die Lebendigkeit als Einstellung an der Mimikspur — ohne Anfang und
 * Ende und ohne Möglichkeit, sie streckenweise anders zu setzen.
 */
export class Scriptspur {

    static CLIPNAME = 'Lebendigkeit';

    /** Eine Script-Spur zur Modellspur `modellIdx` anlegen (oder die vorhandene liefern). */
    static anlegen(modellIdx, name = null) {
        const vorhanden = Scriptspur.zuModell(modellIdx);
        if (vorhanden) return vorhanden;
        pushUndo('Script-Spur hinzufügen');
        const modell = state.project.tracks[modellIdx];
        const spur = new Track(name || `Script ${modell?.name || ''}`.trim());
        spur.type = 'script';
        spur.color = TRACK_COLORS.script;
        spur._modellIdx = modellIdx;
        state.project.addTrack(spur);
        Mimikbasis.laden().then(() => fn.applyPlayhead());
        fn.updateTrackHeaders();
        fn.renderTimeline();
        Spurauswahl.waehlen(state.project.tracks.length - 1);
        return spur;
    }

    static zuModell(modellIdx) {
        return state.project.tracks.find(s => s.type === 'script' && s._modellIdx === modellIdx) || null;
    }

    /**
     * Einen Script-Clip ab `bild` setzen — bis zum Projektende, mindestens eine
     * Sekunde (keine Längenvorgabe, die Länge setzt das Kontextmenü).
     * @param einstellung  Lebendigkeit; ohne Angabe die Vorgabe (Blinzeln, Blick an)
     */
    static clipSetzen(spur, bild, einstellung = null) {
        pushUndo('Script setzen');
        const fps = state.project.fps;
        const ende = Math.ceil(state.project.duration * fps);
        const clip = new Clip(null, Scriptspur.CLIPNAME, Math.max(fps, ende - bild), fps);
        clip.type = 'script';
        clip.startFrame = bild;
        clip.data = einstellung ? JSON.parse(JSON.stringify(einstellung)) : Lebendigkeit.vorgabe();
        spur.clips.push(clip);
        spur.clips.sort((a, b) => a.startFrame - b.startFrame);
        state.selectedTrackIdx = state.project.tracks.indexOf(spur);
        state.selectedClipIdx = spur.clips.indexOf(clip);
        fn.applyPlayhead();
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        return clip;
    }

    /** Spur (falls nötig) und Clip in einem Zug — der Weg aus dem Modellmenü. */
    static hinzufuegen(modellIdx, bild) {
        const spur = Scriptspur.anlegen(modellIdx);
        return Scriptspur.clipSetzen(spur, bild);
    }
}

fn.addScriptTrack = (modellIdx) => Scriptspur.anlegen(modellIdx);
fn.addScriptClip = (modellIdx, bild) => Scriptspur.hinzufuegen(modellIdx, bild);
