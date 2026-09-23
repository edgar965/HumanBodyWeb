import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';

/**
 * Effektemenue — das Kontextmenü der Effekte-Spur (`#effekte-context-menu`).
 *
 * Edgar, 22.09.2026: „Mach auch ein Kontextmenü in der Effekte-Leiste zum
 * Hinzufügen eines Effekt-Ereignisses" — bisher ging ein Speed-Ereignis nur
 * über die Taste G auf der VERKNÜPFTEN Animationsspur, nicht auf der
 * Effekte-Spur selbst. Dazu (selber Tag, „Kontext menü eintrag fehlt für
 * 'Ereignis' hinzufügen für Standbild usw."): „Standbild einfügen" — zwei
 * Tempo-0-Punkte im Abstand einer Sekunde, dazwischen zeichnet
 * `effektbalken()` schon den roten Balken (`effektschluessel.js
 * standbildEinfuegen`). Einträge: Speed-Ereignis hinzufügen, Standbild
 * einfügen (beide an der Klickstelle), Playhead hierher, Löschen (nur mit
 * einem Ereignis unter der Maus).
 */
export class Effektemenue {

    /** Maus-X des Rechtsklicks, von Zeitleistenmenue gesetzt. */
    static mausX = 0;

    static get menue() {
        return document.getElementById('effekte-context-menu');
    }

    static zeigen(e, spur, spurNr, treffer, klickbild, anzeigen) {
        const menue = Effektemenue.menue;
        if (!menue) return;
        state.selectedTrackIdx = spurNr;
        state.selectedClipIdx = treffer ? treffer.clipIdx : -1;
        fn.updateProperties();
        menue.querySelector('[data-action="ctx-delete"]')
            ?.classList.toggle('hb-versteckt', !treffer);
        for (const aktion of ['ctx-effekte-speed', 'ctx-effekte-standbild']) {
            menue.querySelector(`[data-action="${aktion}"]`)
                ?.classList.toggle('hb-versteckt', !!treffer);
        }
        Effektemenue._binden(menue, spurNr, klickbild);
        anzeigen(menue, e);
    }

    static _binden(menue, spurNr, klickbild) {
        const befehle = {
            'ctx-effekte-speed': () => fn.addSpeedKeyframe(spurNr, klickbild),
            'ctx-effekte-standbild': () => fn.standbildEinfuegenEffekte(spurNr, klickbild),
            'ctx-playhead': () => Zeitleistenziehen.abspielkopfSetzen(Effektemenue.mausX),
            'ctx-delete': () => fn.deleteSelectedClip(),
        };
        menue.querySelectorAll('.ctx-item[data-action]').forEach(eintrag => {
            eintrag.onclick = () => {
                menue.style.display = 'none';
                befehle[eintrag.dataset.action]?.(eintrag);
            };
        });
    }
}
