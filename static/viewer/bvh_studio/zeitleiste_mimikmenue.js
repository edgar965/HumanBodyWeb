import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';
import { Mimikspur } from './mimikspur.js';
import { Mimikdialog } from './mimikdialog.js';

/**
 * Mimikmenue — das Kontextmenü der Mimikspur (`#mimik-context-menu`).
 *
 * Edgar, 13.09.2026: „eine Spur für die Gesichtsposen, mit Rechtsklick —
 * Kontextmenü zum Setzen der Pose, die Pose im Popup-Dialog." Einträge:
 * Pose setzen… (Dialog an der Klickzeit), Neutral setzen, Schlüsselbild
 * löschen (nur auf einem Schlüsselbild), Lebendigkeit… (Eigenschaften der
 * Spur), Mimik einrechnen (Nebendatei zur BVH, `Mimikeinrechnen`).
 */
export class Mimikmenue {

    /** Maus-X des Rechtsklicks, von Zeitleistenmenue gesetzt. */
    static mausX = 0;

    static get menue() {
        return document.getElementById('mimik-context-menu');
    }

    static zeigen(e, spur, spurNr, treffer, klickbild, anzeigen) {
        const menue = Mimikmenue.menue;
        if (!menue) return;
        state.selectedTrackIdx = spurNr;
        state.selectedClipIdx = treffer ? treffer.clipIdx : -1;
        fn.updateProperties();
        menue.querySelector('[data-action="ctx-mimik-loeschen"]')
            ?.classList.toggle('hb-versteckt', !treffer);
        Mimikmenue._binden(menue, spur, spurNr, treffer, klickbild);
        anzeigen(menue, e);
    }

    static _binden(menue, spur, spurNr, treffer, klickbild) {
        const clip = treffer ? spur.clips[treffer.clipIdx] : null;
        const frame = clip ? clip.startFrame : klickbild;
        const befehle = {
            'ctx-mimik-pose': () => Mimikdialog.oeffnen(spur, frame, clip),
            'ctx-mimik-neutral': () => Mimikspur.neutral(spur, frame),
            'ctx-mimik-loeschen': () => { if (clip) Mimikspur.loeschen(spur, clip); },
            'ctx-mimik-lebendigkeit': () => {
                state.selectedClipIdx = -1;
                fn.updateProperties();
                fn.switchPropsTab?.('props');
            },
            'ctx-mimik-einrechnen': () => fn.mimikEinrechnen?.(spur),
            'ctx-playhead': () => Zeitleistenziehen.abspielkopfSetzen(Mimikmenue.mausX),
        };
        menue.querySelectorAll('.ctx-item[data-action]').forEach(eintrag => {
            eintrag.onclick = () => {
                menue.style.display = 'none';
                befehle[eintrag.dataset.action]?.();
            };
        });
    }
}
