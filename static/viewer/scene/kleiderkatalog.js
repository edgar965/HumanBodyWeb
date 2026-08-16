import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Kleiderkatalog — die Kleiderbibliothek einmal holen und die Kategorien in ein
 * Auswahlfeld setzen.
 *
 * Umbau 16.08.2026: Das stand ZWEIMAL fast gleich da — in `loadKleiderUI()` und
 * in `loadMHProxyUI()`, beide als `setInterval(…, 200)`, das den Katalog immer
 * wieder anfragte, bis er gefüllt war, OHNE Abbruch. Bei leerer Bibliothek oder
 * Serverfehler fragte die Seite endlos alle 200 ms nach — zwei Dauerläufer
 * gleichzeitig, denn beide Reiter der Szene bauen sich beim Laden auf.
 *
 * Ein Unterschied blieb: Der Kleider-Reiter hängte gefundene Stücke ungeprüft
 * an, der MakeHuman-Reiter prüfte auf Dubletten. Geprüft wird jetzt immer —
 * sonst steht dasselbe Stück zweimal in der Liste, wenn beide Reiter laden.
 */
export class Kleiderkatalog {

    /** So oft wird höchstens angefragt, dann steht eine Warnung. */
    static VERSUCHE = 10;
    static PAUSE_MS = 400;

    /**
     * @param feldId   id des Kategorie-Auswahlfelds
     */
    constructor(feldId) {
        this.feldId = feldId;
    }

    /** true, wenn der Katalog steht. */
    async laden() {
        for (let versuch = 0; versuch < Kleiderkatalog.VERSUCHE; versuch++) {
            if (state._garmentCatalog.length > 0) break;
            await this._holen();
            if (state._garmentCatalog.length > 0) break;
            await new Promise(weiter => setTimeout(weiter, Kleiderkatalog.PAUSE_MS));
        }
        if (!state._garmentCatalog.length) {
            console.warn('Kleider-Katalog bleibt leer — Kategorien fehlen');
            return false;
        }
        this.kategorienFuellen();
        return true;
    }

    async _holen() {
        try {
            const daten = await Serverabruf.json('/api/character/garment/library/');
            for (const [kategorie, kleider] of Object.entries(daten.garments || {})) {
                for (const kleid of kleider) {
                    kleid._category = kategorie;
                    if (!state._garmentCatalog.find(k => k.id === kleid.id)) {
                        state._garmentCatalog.push(kleid);
                    }
                }
            }
        } catch (fehler) {
            console.warn('Kleider-Katalog nicht ladbar:', fehler);
        }
    }

    kategorienFuellen() {
        const feld = document.getElementById(this.feldId);
        if (!feld) return;
        const vorhanden = new Set([...feld.options].map(eintrag => eintrag.value));
        for (const kategorie of new Set(
                state._garmentCatalog.map(kleid => kleid._category))) {
            if (vorhanden.has(kategorie)) continue;
            feld.appendChild(new Option(
                kategorie.charAt(0).toUpperCase() + kategorie.slice(1), kategorie));
        }
    }
}
