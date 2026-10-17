/**
 * Bildnachlader — die Fassung aus djangoBase (`djangobase/js/bildnachlader.js`) plus Wiederholung.
 *
 * Wie `serverabruf.js` und `protokoll.js` steht die Logik an EINER Stelle in djangoBase; die Module hier behalten
 * ihren kurzen relativen Import. Eine Sache kommt dazu, die djangoBase nicht kennt:
 *
 * WARUM DIE WIEDERHOLUNG (Edgar, 16.10.2026: „bei einigen Eigen Assets fehlen die Icons", Bild: die Vorschauen der
 * Genesis-Garderobe bis „Eigen Foto 04111144 hose f24" kaputt, ab f25 heil): Der Nachlader setzt `src` genau einmal.
 * Startet der Entwicklungsserver gerade neu (Autoreload nach einer Codeänderung), scheitern die Bilder, die in diesem
 * Moment geladen werden — und bleiben kaputt, bis die Seite neu geladen wird. Gemessen danach im selben Tab:
 * alle 700 Vorschau-Adressen der Garderobe lieferten 200 und ein Bild (6,7 s für alle), die Adressen waren also in Ordnung.
 * Jetzt holt ein gescheitertes Bild sich selbst bis zu `WIEDERHOLUNGEN`-mal nach, mit wachsender Pause.
 */
import { Bildnachlader as Basis } from '/static/djangobase/js/bildnachlader.js';

export class Bildnachlader extends Basis {
    /** So oft wird ein gescheitertes Bild noch einmal geholt. */
    static WIEDERHOLUNGEN = 3;
    /** Pause vor dem n-ten neuen Versuch: n × PAUSE_MS. */
    static PAUSE_MS = 2000;

    /** Wie in djangoBase vormerken; scheitert das Laden später, kommt die Wiederholung. */
    static vormerken(bild, quelle) {
        super.vormerken(bild, quelle);
        if (!quelle || bild.dataset.versuche !== undefined) return;
        bild.dataset.versuche = '0';
        bild.addEventListener('error', () => Bildnachlader._nochmal(bild, quelle));
    }

    static _nochmal(bild, quelle) {
        const versuch = Number(bild.dataset.versuche) + 1;
        if (versuch > Bildnachlader.WIEDERHOLUNGEN) return;
        bild.dataset.versuche = String(versuch);
        // Die Marke umgeht einen zwischengespeicherten Fehlschlag; der Server ignoriert sie.
        const trenner = quelle.includes('?') ? '&' : '?';
        setTimeout(() => { bild.src = `${quelle}${trenner}versuch=${versuch}`; }, Bildnachlader.PAUSE_MS * versuch);
    }
}
