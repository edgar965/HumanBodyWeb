import { Zeiten } from './zeiten.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Knopfmeldung — ein Knopf zeigt kurz eine Rückmeldung und wird dann wieder
 * normal.
 *
 * Umbau 16.08.2026: Dieses Muster stand SECHSMAL im Projekt, jedes Mal neu
 * geschrieben:
 *
 *     const orig = btn.innerHTML;
 *     btn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
 *     setTimeout(() => { btn.innerHTML = orig; }, 1500);
 *
 * — in viewer/presets.js (dreimal), viewer/smpl.js, animation/speichern.js
 * (zweimal), scene/lighting.js und scene/save_load.js. Zwei davon vergaßen,
 * eine zwischenzeitlich gesetzte Farbe zurückzunehmen.
 */
export class Knopfmeldung {

    static SYMBOL_FERTIG = 'fa-check';
    static SYMBOL_FEHLER = 'fa-exclamation-triangle';

    /**
     * Kurz eine Meldung zeigen, dann den alten Zustand herstellen.
     *
     * @param knopf   das Element
     * @param text    was gemeldet wird, etwa 'Gespeichert!'
     * @param wahl    { symbol, dauer, farbe }
     */
    static zeigen(knopf, text, wahl = {}) {
        if (!knopf) { Protokoll.warnung('knopfmeldung', text); return; }
        const { symbol = Knopfmeldung.SYMBOL_FERTIG,
                dauer = Zeiten.BESTAETIGUNG_MS, farbe = null } = wahl;
        // Vorherigen Zustand vollständig merken — auch die Farbe, sonst bleibt
        // ein Rot oder Grün stehen.
        const vorher = { inhalt: knopf.innerHTML,
                         farbe: knopf.style.borderColor,
                         schrift: knopf.style.color };
        // `symbol: null` für Elemente, die kein Symbol tragen (etwa ein Titel).
        knopf.innerHTML = symbol ? `<i class="fas ${symbol}"></i> ${text}` : text;
        if (farbe) {
            knopf.style.borderColor = farbe;
            knopf.style.color = farbe;
        }
        setTimeout(() => {
            knopf.innerHTML = vorher.inhalt;
            knopf.style.borderColor = vorher.farbe;
            knopf.style.color = vorher.schrift;
        }, dauer);
    }

    static fertig(knopf, text = 'Gespeichert!') {
        Knopfmeldung.zeigen(knopf, text);
    }

    static fehler(knopf, text = 'Fehler') {
        Knopfmeldung.zeigen(knopf, text,
                            { symbol: Knopfmeldung.SYMBOL_FEHLER });
    }
}
