import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Lebendigkeit } from './lebendigkeit.js';
import { Modellkindspur } from './modellkindspur.js';
import { Spurauswahl } from './spurauswahl.js';

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
        return Scriptspur.zuModell(modellIdx)
            || Modellkindspur.anlegen(modellIdx, 'script', 'Script', 'Script-Spur hinzufügen', name);
    }

    static zuModell(modellIdx) {
        return Modellkindspur.zuModell(modellIdx, 'script');
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
        const spurNr = state.project.tracks.indexOf(spur);
        state.selectedTrackIdx = spurNr;
        state.selectedClipIdx = spur.clips.indexOf(clip);
        fn.applyPlayhead();
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        // Steckt die Script-Spur unter einer zugeklappten Modellspur, wäre der
        // neue Clip sonst unsichtbar (Edgar, 22.09.2026: „erscheint nicht im Track").
        Spurauswahl.einblenden(spurNr, spur);
        return clip;
    }

    /** Spur (falls nötig) und Clip in einem Zug — der Weg aus dem Modellmenü. */
    static hinzufuegen(modellIdx, bild) {
        const spur = Scriptspur.anlegen(modellIdx);
        return Scriptspur.clipSetzen(spur, bild);
    }
}
