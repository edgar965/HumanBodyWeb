import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Figurwahldialog } from '../gemeinsam/figurwahldialog.js';
import { Katalogpflege } from '../scene/katalogpflege.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Spurerzeugung } from './spurerzeugung.js';
import { Modellmenue } from './zeitleiste_modellmenue.js';
import { Modellplatz } from './modellplatz.js';
import { pushUndo } from './undo.js';

/**
 * Modellwahl — „Hinzufügen → Spur → Modell" öffnet den Figurwahl-Dialog.
 *
 * ANLASS (Edgar, 11.09.2026): „beim Hinzufügen eines Modells bitte den
 * gleichen Popup dialog wie bei /humanbody/scene/, wo ich das Modell und die
 * Position auswähle, default die gleichen Meter." Bis dahin legte der
 * Menüpunkt eine LEERE Modellspur an — ohne Modell, ohne Verknüpfung; das
 * Modell kam erst über das Rechtsklickmenü der Spur, die Lage über die
 * Eigenschaften der Animationsspur.
 *
 * Jetzt derselbe Dialog wie in der Szene und im Theatre
 * (`gemeinsam/figurwahldialog.js`): Reiter HumanBody (nur den kann das
 * Studio häuten — `Spurfigur` holt Netz und Gewichte je Modellvorgabe),
 * Position X mit der Vorgabe der Szene (1,5 m rechts neben der zuletzt
 * angelegten Figur), OHNE „Größe angleichen": Im Studio bestimmt die
 * Bewegung die Größe der Figur, ein Kästchen ohne Wirkung wäre eine
 * Behauptung.
 *
 * Was beim Bestätigen entsteht (EIN Undo-Schritt; die drei Bausteine merken
 * sich sonst je einen): eine Animationsspur, die noch keine Figur trägt (die
 * gewählte oder die erste freie, sonst eine neue), mit der Lage und dem
 * Modell als Vorgabe; eine Modellspur, benannt nach dem Modell, auf sie
 * verknüpft; darauf ein Modellclip ab Bild 0 — `Modellspur.anwenden` lädt
 * damit die Figur sofort, ohne dass ein BVH-Clip liegen muss.
 */
export class Modellwahl {

    static ABSTAND_M = Modellplatz.ABSTAND_M;

    static _dialog = null;

    static dialog() {
        if (!Modellwahl._dialog) {
            Modellwahl._dialog = new Figurwahldialog({
                lader: { modell: (name, lage) => Modellwahl.hinzufuegen(name, lage) },
                vorgaben: () => Modellwahl.vorgaben(),
                pflege: Katalogpflege,
                titel: 'Modell hinzufügen',
                angleichen: false,
                kennung: 'studio-modellwahl',
            });
        }
        return Modellwahl._dialog;
    }

    static oeffnen() {
        return Modellwahl.dialog().oeffnen();
    }

    /** Rechts neben der zuletzt angelegten Figur — ohne Figur im Ursprung. */
    static vorgaben() {
        return {
            x: Modellplatz.vorgabeX(state.project.tracks, Modellwahl.ABSTAND_M),
            angleichen: false,
            vorbildHoehe: 0,
        };
    }

    /**
     * Das Modell in die Zeitleiste stellen.
     * @param {string} name  Modellvorgabe (Name unter `data/models/`)
     * @param {Object} lage  { x } aus dem Dialog
     */
    static hinzufuegen(name, lage) {
        const x = Number(lage?.x) || 0;
        pushUndo('Modell hinzufügen');
        state._undoSuppressed = true;
        let modell;
        try {
            const bewegung = Modellplatz.freieAnimation(state.project.tracks,
                                                         state.selectedTrackIdx)
                || Spurerzeugung.animation();
            bewegung.preset = name;
            bewegung.position = [x, 0, bewegung.position?.[2] || 0];
            bewegung.group.position.set(x, 0, bewegung.position[2]);
            modell = Spurerzeugung.modell(name);
            modell._linkedAnimIdx = state.project.indexOf(bewegung);
            Modellmenue.vorlageSetzen(state.project.indexOf(modell), name);
        } finally {
            state._undoSuppressed = false;
        }
        fn.updateTrackHeaders();
        fn.serverLog('model_added', `preset=${name} x=${x}`);
        Protokoll.debug('BVH Studio', `Modell ${name} bei x = ${x} m hinzugefügt`);
        return modell;
    }
}
