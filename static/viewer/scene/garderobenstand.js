import { Kleidungszustand } from './kleidungszustand.js';

/**
 * Garderobenstand — die Kleiderliste einer Figur, wie sie gespeichert wird.
 *
 * DER BEFUND (Edgar, 09.09.2026: „farbe der Schuhe wird nicht gespeichert")
 * ========================================================================
 * Eine Figur führt ihre Garment-Fit-Stücke DOPPELT:
 *
 *     inst.garments          die Liste — Stand vom letzten Anpassen
 *     inst.garmentState[key] der lebende Zustand — Farbe, Material, Regionen
 *
 * Alles, was danach am Stück verändert wird, geht in den ZUSTAND: der
 * Farbwähler, die Materialregler, die Regionsverschiebungen. Die Liste bleibt
 * stehen, wie sie beim Anziehen war.
 *
 * `character.js toJSON` (Szene speichern) rechnete den Zustand ein.
 * `Szenenausgabe._zusammengestellt` (Modell speichern) nahm `figur.garments`
 * ROH. Damit hing es am Menüpunkt, ob eine geänderte Farbe überlebt — im
 * Browser gemessen: Zustand [1, 0, 0], gespeicherte Datei [0.0742, 0.0999,
 * 0.2159], also die Vorgabe `#4d5980`. Kein Fehler, keine Meldung.
 *
 * Beide Wege nehmen jetzt diese eine Stelle. Und die Feldliste steht nicht
 * noch einmal hier, sondern kommt aus `Kleidungszustand.zuJson()` — dessen
 * Modulkopf nennt genau den Grund: „Ein Feld dazu hieß: sechs Stellen ändern
 * — oder eine übersehen."
 */
export class Garderobenstand {

    /** Schlüsselvorsilbe der Garment-Fit-Stücke in `clothMeshes`. */
    static VORSILBE = 'gar_';

    /**
     * Die Liste mit eingerechnetem Zustand.
     *
     * Ein Stück ohne Zustand bleibt unverändert stehen: Es kann aus einer
     * älteren Datei stammen und wurde in dieser Sitzung nie angefasst — seine
     * Werte zu ersetzen hiesse, sie durch Vorgaben zu überschreiben.
     */
    static liste(figur) {
        const zustaende = figur.garmentState || {};
        return (figur.garments || []).map((stueck) => {
            const zustand = zustaende[Garderobenstand.VORSILBE + stueck.id];
            if (!zustand) return stueck;
            return { id: stueck.id,
                     ...Kleidungszustand.ausJson(zustand).zuJson() };
        });
    }
}
