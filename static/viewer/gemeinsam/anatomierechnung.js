import { Anatomiebild } from './anatomiebild.js';
import { Anatomiedreiecke } from './anatomiedreiecke.js';
import { Anatomiefuellung } from './anatomiefuellung.js';

/**
 * Anatomierechnung — die Karten des Scham-Stücks aus reinen Zahlen rechnen und auffüllen (12.10.2026, für `Anatomiebacken`).
 *
 * Edgar: „das Backen der neuen Haut soll nur ein paar Sekunden dauern." Nach dem Zwischenspeicher der Zuordnung (`Anatomiehash`) blieben 1,5–2 s
 * Rechnung auf dem Hauptfaden: Bild (`Anatomiebild`, 1,8 s) und Füllen (`Anatomiefuellung`, 0,6 s). Beides steht hier zusammen, ohne DOM und ohne Three.js
 * — derselbe Code läuft im Worker (`anatomiearbeiter.js`) und, wenn der nicht zu haben ist, auf dem Hauptfaden (`Anatomiebacken.bild`): dasselbe
 * Ergebnis, Bit für Bit.
 */
export class Anatomierechnung {

    /** Was die Füllung der Normalenkarte außerhalb der Inseln einsetzt: die flache Normale. */
    static NORMALE_LEER = [128, 128, 255, 255];

    /**
     * @param a  `{zu, st: {pos, uv, normal, index}, ha: {pos, uv, normal, ecken}, gruppe, fenster, breite, hoehe, uvKarte}` — `Anatomiebild.rechnen`
     *           bekommt daraus die Dreiecke des Stücks und der Haut; `fenster` kommt von `Anatomiefenster.lesen`
     * @param atmen  `async () => void` oder null — Gelegenheit für den Hauptfaden (im Worker null)
     * @returns `{farbe, normal, rauheit}` je `Uint8ClampedArray` (RGBA, `breite · hoehe`), gefüllt; `normal` und `rauheit` null, wenn keine Karte der Haut sie hat
     */
    static async rechnen(a, atmen = null) {
        const st = new Anatomiedreiecke(a.st.pos, a.st.uv, a.st.normal, a.st.index);
        const ha = new Anatomiedreiecke(a.ha.pos, a.ha.uv, a.ha.normal, a.ha.ecken);
        const bild = await Anatomiebild.rechnen(a.zu, st, ha, a.gruppe, a.fenster, a.breite, a.hoehe, a.uvKarte, atmen);
        Anatomiefuellung.fuellen(a.zu.belegt, a.breite, a.hoehe, [
            { rgba: bild.farbe, vorgabe: null },
            bild.normal && { rgba: bild.normal, vorgabe: Anatomierechnung.NORMALE_LEER },
            bild.rauheit && { rgba: bild.rauheit, vorgabe: null },
        ].filter(Boolean));
        return bild;
    }
}
