import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';
import { Scriptspur } from './scriptspur.js';

/**
 * Scriptmenue — das Kontextmenü der Script-Spur (`#script-context-menu`).
 *
 * Edgar, 15.09.2026: „Animation mit normaler Animation, Mimik und Script."
 * Einträge: Script hinzufügen (Clip ab der Klickstelle, nur ohne Treffer),
 * Einstellungen… (der Clip rechts unter Eigenschaften), Playhead hierher,
 * Split, Länge (wie beim Modellclip), Löschen, Mimik einrechnen — die
 * Nebendatei zur BVH nimmt die Scripts mit.
 */
export class Scriptmenue {

    /** Maus-X des Rechtsklicks, von Zeitleistenmenue gesetzt. */
    static mausX = 0;

    static get menue() {
        return document.getElementById('script-context-menu');
    }

    static zeigen(e, spur, spurNr, treffer, klickbild, anzeigen) {
        const menue = Scriptmenue.menue;
        if (!menue) return;
        state.selectedTrackIdx = spurNr;
        state.selectedClipIdx = treffer ? treffer.clipIdx : -1;
        fn.updateProperties();
        // Ohne Clip unter der Maus: nur Hinzufügen und Playhead.
        for (const aktion of ['ctx-script-einstellungen', 'ctx-split', 'ctx-laenge', 'ctx-delete']) {
            menue.querySelector(`[data-action="${aktion}"]`)?.classList.toggle('hb-versteckt', !treffer);
        }
        menue.querySelector('[data-action="ctx-script-clip"]')?.classList.toggle('hb-versteckt', !!treffer);
        Scriptmenue._binden(menue, spur, klickbild);
        anzeigen(menue, e);
    }

    static _binden(menue, spur, klickbild) {
        const befehle = {
            'ctx-script-clip': () => Scriptspur.clipSetzen(spur, klickbild),
            'ctx-script-einstellungen': () => fn.switchPropsTab?.('props'),
            'ctx-playhead': () => Zeitleistenziehen.abspielkopfSetzen(Scriptmenue.mausX),
            'ctx-split': () => fn.splitClipAtPlayhead(),
            'ctx-delete': () => fn.deleteSelectedClip(),
            'ctx-laenge-prozent': (eintrag) => fn.clipLaenge('prozent', Number(eintrag.dataset.wert) || null),
            'ctx-laenge-sekunden': () => fn.clipLaenge('sekunden'),
            'ctx-mimik-einrechnen': () => fn.mimikEinrechnen?.(spur),
        };
        menue.querySelectorAll('.ctx-item[data-action]').forEach(eintrag => {
            eintrag.onclick = () => {
                if (eintrag.dataset.action === 'ctx-laenge') return;   // öffnet nur das Untermenü
                menue.style.display = 'none';
                befehle[eintrag.dataset.action]?.(eintrag);
            };
        });
    }
}
