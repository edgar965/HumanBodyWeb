import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Spurauswahl } from './spurauswahl.js';
import { Scriptspur } from './scriptspur.js';
import { Modellkindspur } from './modellkindspur.js';

/**
 * Mimikspur — die Gesichtsspur einer Modellspur: anlegen, Schlüsselbilder setzen.
 *
 * Edgar, 13.09.2026: „eine Spur für die Gesichtsposen, mit Rechtsklick —
 * Kontextmenü zum Setzen der Pose." Die Spur hängt an einer Modellspur
 * (`_modellIdx`) und steht in der Zeitleiste eingerückt darunter, wie die
 * Animation. Ein Schlüsselbild ist ein Clip `mimik_kf` mit
 * `data = {pose, gewichte, staerke, uebergang, halten}`; „Neutral" ist ein
 * Schlüsselbild ohne Gewichte. Lebendigkeit ist bei einer neuen Spur an
 * (Edgar, 13.09.2026) — seit 15.09.2026 als Script-Clip auf der Script-Spur
 * des Modells, die mit der ersten Mimikspur entsteht (`Scriptspur`).
 */
export class Mimikspur {

    static VORGABE_STAERKE = 1;
    static VORGABE_UEBERGANG = 'weich';
    static VORGABE_HALTEN = 0;

    /** Eine Mimikspur zur Modellspur `modellIdx` anlegen (oder die vorhandene liefern). */
    static anlegen(modellIdx, name = null) {
        const vorhanden = Mimikspur.zuModell(modellIdx);
        if (vorhanden) return vorhanden;
        const spur = Modellkindspur.anlegen(modellIdx, 'mimik', 'Mimik', 'Mimikspur hinzufügen', name);
        // Lebendigkeit an bei neuer Spur: ein Script von 0 bis zum Projektende.
        if (!Scriptspur.zuModell(modellIdx)) {
            Scriptspur.clipSetzen(Scriptspur.anlegen(modellIdx), 0);
            Spurauswahl.waehlen(state.project.tracks.indexOf(spur));
        }
        return spur;
    }

    static zuModell(modellIdx) {
        return Modellkindspur.zuModell(modellIdx, 'mimik');
    }

    /** Das Schlüsselbild genau an diesem Bild — oder null. */
    static schluesselBei(spur, frame) {
        return spur.clips.find(c => c.type === 'mimik_kf' && c.startFrame === frame) || null;
    }

    /**
     * Pose an `frame` setzen; ein Schlüsselbild an derselben Stelle wird
     * ersetzt. `pose` ist `{id, name, gewichte}`; `optionen` Stärke/Übergang/Halten.
     */
    static setzen(spur, frame, pose, optionen = {}) {
        pushUndo('Mimik setzen');
        let clip = Mimikspur.schluesselBei(spur, frame);
        if (!clip) {
            clip = new Clip(null, pose.name, 1, state.project.fps);
            clip.type = 'mimik_kf';
            clip.startFrame = frame;
            spur.clips.push(clip);
        }
        clip.name = pose.name;
        clip.data = {
            pose: pose.id,
            gewichte: { ...(pose.gewichte || {}) },
            staerke: optionen.staerke ?? Mimikspur.VORGABE_STAERKE,
            uebergang: optionen.uebergang || Mimikspur.VORGABE_UEBERGANG,
            halten: optionen.halten ?? Mimikspur.VORGABE_HALTEN,
        };
        spur.clips.sort((a, b) => a.startFrame - b.startFrame);
        Mimikspur._nachtragen(spur, clip);
        return clip;
    }

    static neutral(spur, frame) {
        return Mimikspur.setzen(spur, frame, { id: 'neutral', name: 'Neutral', gewichte: {} });
    }

    static loeschen(spur, clip) {
        const stelle = spur.clips.indexOf(clip);
        if (stelle < 0) return;
        pushUndo('Mimik löschen');
        spur.clips.splice(stelle, 1);
        state.selectedClipIdx = -1;
        Mimikspur._nachtragen(spur, null);
    }

    static _nachtragen(spur, clip) {
        state.selectedTrackIdx = state.project.tracks.indexOf(spur);
        state.selectedClipIdx = clip ? spur.clips.indexOf(clip) : -1;
        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updateProperties();
    }
}
