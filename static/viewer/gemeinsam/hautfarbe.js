/**
 * Hautfarbe — Ethnie aus der Körperart lesen und die Farbe ins Material setzen.
 *
 * Umbau 16.08.2026: Die Gamma-Umrechnung
 * `Math.pow(farbe, 1/2.2)` stand an ACHT Stellen ausgeschrieben —
 * animation/material.js, character_core.js, photo_to_3d/humanbody_mesh.js,
 * scene/charakter_koerper.js, vergleich/vergleichsnetz.js,
 * vergleich/vergleichsregler.js und zweimal in viewer/morphs.js.
 *
 * Die Ethnie wurde dabei auf zwei Weisen bestimmt: `teile[1] || teile[0]` und
 * `teile.slice(1).join('_')` mit Ersatz 'Caucasian'. Bei allen 13 Körperarten
 * (Female_Caucasian … Male_Latin) hat jede genau EINEN Unterstrich, also
 * liefern beide dasselbe. Hier gilt die zweite, weil sie auch bei einem Namen
 * wie 'Female_African_American' die ganze Ethnie behält.
 */
export class Hautfarbe {

    /** Die Farben in der Datenbank sind linear, die Anzeige erwartet sRGB. */
    static GAMMA = 1 / 2.2;
    /** Ethnie, wenn die Körperart keine nennt oder die genannte fehlt. */
    static ERSATZ_ETHNIE = 'Caucasian';
    /** Hautfarbe, wenn die Tabelle nichts hergibt. */
    static ERSATZ_FARBE = 0xd4a574;

    static ethnie(koerperart) {
        const teile = String(koerperart || '').split('_');
        return teile.length > 1 ? teile.slice(1).join('_')
                                : Hautfarbe.ERSATZ_ETHNIE;
    }

    /** Farbwerte zur Körperart, oder null. */
    static farben(koerperart, tabelle, mitErsatz = false) {
        if (!tabelle) return null;
        const gefunden = tabelle[Hautfarbe.ethnie(koerperart)];
        if (gefunden) return gefunden;
        return mitErsatz ? tabelle[Hautfarbe.ERSATZ_ETHNIE] || null : null;
    }

    /** Lineare Farbwerte gamma-korrigiert ins Material setzen. */
    static setzen(material, rgb, zweites = null) {
        if (!material || !rgb) return false;
        material.color.setRGB(Math.pow(rgb[0], Hautfarbe.GAMMA),
                              Math.pow(rgb[1], Hautfarbe.GAMMA),
                              Math.pow(rgb[2], Hautfarbe.GAMMA));
        // Der Körper hat ein zweites Material für dieselbe Haut (Kopf/Rumpf).
        if (zweites) zweites.color.copy(material.color);
        return true;
    }

    /**
     * Farbe der Körperart ins Material — der übliche Fall.
     * @returns true, wenn eine Farbe gefunden und gesetzt wurde
     */
    static ausKoerperart(material, koerperart, tabelle, wahl = {}) {
        const { zweites = null, mitErsatz = false } = wahl;
        return Hautfarbe.setzen(
            material, Hautfarbe.farben(koerperart, tabelle, mitErsatz), zweites);
    }
}
