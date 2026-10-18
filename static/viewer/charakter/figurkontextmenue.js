import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Kontextmenue } from '../gemeinsam/kontextmenue.js';
import { Figurtreffer } from './figurtreffer.js';
import { Modellexportdialog } from './modellexport_dialog.js';

/**
 * Figurkontextmenue — Rechtsklick auf eine Figur in der 3D-Ansicht (Edgar, 18.10.2026: „Rechte Maustaste beim
 * Modell, neues Kontextmenü: 1. ‚Modell Exportieren'").
 *
 * Die rechte Taste verschiebt in der Ansicht auch die Kamera (OrbitControls). Ein Menü kommt deshalb nur bei einem
 * KLICK — Taste ohne Bewegung über `CLICK_THRESHOLD` hinaus; nach einem Verschieben feuert Windows `contextmenu`
 * ebenfalls, beim Loslassen. Daneben ins Leere: kein Menü, die Kamera bleibt, wie sie war.
 */
export class Figurkontextmenue {

    static _druck = null;

    static binden() {
        const canvas = state.canvas;
        if (!canvas) return;
        canvas.addEventListener('pointerdown', (e) => {
            Figurkontextmenue._druck = e.button === 2 ? { x: e.clientX, y: e.clientY } : null;
        });
        canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const druck = Figurkontextmenue._druck;
            Figurkontextmenue._druck = null;
            if (!druck || state.greiftGerade || state.transformDragging) return;
            if (Math.hypot(e.clientX - druck.x, e.clientY - druck.y) > state.CLICK_THRESHOLD) return;
            const charId = Figurtreffer.figur(e);
            if (!charId) return;
            // Der Klick wählt die Figur mit an (`bindCanvasClick` auf `pointerup`) — das Menü gilt ihr.
            if (state.selectedCharacterId !== charId) fn.selectCharacter(charId);
            Kontextmenue.zeigen(e.clientX, e.clientY, Figurkontextmenue.eintraege(charId));
        });
    }

    static eintraege(charId) {
        return [
            { symbol: 'fa-file-export', text: 'Modell exportieren …', tun: () => Modellexportdialog.oeffnen(charId) },
        ];
    }
}

fn.bindFigurKontextmenue = () => Figurkontextmenue.binden();
