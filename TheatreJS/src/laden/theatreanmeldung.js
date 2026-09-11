import { getSheet, createMeshSheet } from '../theatre-bridge.js';
import { Sequenzspuren } from './sequenzspuren.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Theatreanmeldung — ein geladenes Objekt als animierbares Theatre-Objekt melden.
 *
 * Herausgelöst aus `asset-loader.js` (318 Zeilen). Dort stand der Dreisatz
 * „Zähler hoch, Blatt holen, `createMeshSheet`" VIERMAL — für GLB, Figur,
 * Vorgabefigur und BVH-Wurzel.
 *
 * Der Zähler läuft über ALLE Arten hinweg: Zwei Objekte mit demselben Namen
 * überschreiben sich in Theatre.js gegenseitig.
 *
 * SCHLÜSSEL SIND EINDEUTIG (11.09.2026): Dieselbe Vorgabe zweimal geladen
 * — etwa zwei „Female1" nebeneinander über den Figurwahl-Dialog — hieße
 * zweimal `sheet.object('Female1')`, und Theatre.js verweigert den zweiten.
 * Ein vergebener Name bekommt deshalb eine Nummer (`Female1 2`). `abmelden`
 * gibt ihn frei, damit Rückgängig dieselbe Figur unter ihrem alten Schlüssel
 * zurückbringen kann; `schluessel()` sagt vorher, welcher es wird.
 *
 * IN DER ZEITLEISTE (11.09.2026): Ein frisch angemeldetes Objekt hat nur
 * statische Werte und fehlt darum im Sequenz-Editor. `Sequenzspuren.anlegen`
 * gibt jedem Wert eine Spur mit einem Schlüsselbild bei 0 s — damit steht
 * die Figur dort, wo Kamera und Lichter stehen.
 */
export class Theatreanmeldung {

    static _zaehler = 0;
    static _vergeben = new Set();

    /** Der Schlüssel, unter dem `name` angemeldet würde. */
    static schluessel(name) {
        if (!Theatreanmeldung._vergeben.has(name)) return name;
        let nummer = 2;
        while (Theatreanmeldung._vergeben.has(`${name} ${nummer}`)) nummer += 1;
        return `${name} ${nummer}`;
    }

    /**
     * @returns das angemeldete Objekt (oder `null`, wenn es kein Blatt gibt).
     *          Der verwendete Schlüssel steht danach in
     *          `gruppe.userData.theatreSchluessel`.
     */
    static anmelden(gruppe, name, art = 'Asset') {
        Theatreanmeldung._zaehler++;
        const blatt = getSheet();
        if (!blatt) return null;
        const schluessel = Theatreanmeldung.schluessel(
            name || `${art} ${Theatreanmeldung._zaehler}`);
        Theatreanmeldung._vergeben.add(schluessel);
        if (gruppe?.userData) gruppe.userData.theatreSchluessel = schluessel;
        const objekt = createMeshSheet(blatt, schluessel, gruppe);
        try {
            Sequenzspuren.anlegen(objekt);
        } catch (fehler) {
            Protokoll.warnung('theatreanmeldung', `${schluessel}: ohne Spuren —`, fehler.message);
        }
        return objekt;
    }

    /** Das Objekt aus dem Blatt nehmen und den Schlüssel freigeben. */
    static abmelden(schluessel) {
        if (!schluessel) return false;
        Theatreanmeldung._vergeben.delete(schluessel);
        const blatt = getSheet();
        if (!blatt?.detachObject) return false;
        blatt.detachObject(schluessel);
        return true;
    }
}
