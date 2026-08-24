import { getSheet, createMeshSheet } from '../theatre-bridge.js';

/**
 * Theatreanmeldung — ein geladenes Objekt als animierbares Theatre-Objekt melden.
 *
 * Herausgelöst aus `asset-loader.js` (318 Zeilen). Dort stand der Dreisatz
 * „Zähler hoch, Blatt holen, `createMeshSheet`" VIERMAL — für GLB, Figur,
 * Vorgabefigur und BVH-Wurzel.
 *
 * Der Zähler läuft über ALLE Arten hinweg: Zwei Objekte mit demselben Namen
 * überschreiben sich in Theatre.js gegenseitig.
 */
export class Theatreanmeldung {

    static _zaehler = 0;

    /** @returns das angemeldete Objekt (oder `null`, wenn es kein Blatt gibt). */
    static anmelden(gruppe, name, art = 'Asset') {
        Theatreanmeldung._zaehler++;
        const blatt = getSheet();
        if (!blatt) return null;
        return createMeshSheet(blatt,
                               name || `${art} ${Theatreanmeldung._zaehler}`,
                               gruppe);
    }
}
