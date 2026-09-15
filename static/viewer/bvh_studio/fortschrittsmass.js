/**
 * Fortschrittsmass — die Rechnung hinter dem Fortschrittsbalken unter der
 * Zeitleiste: Bild ↔ Anteil ↔ Pixel. Ohne Importe, damit der Test sie in
 * Node prüft (`test_js_fortschritt`); das Zeichnen und die Maus liegen in
 * `zeitleiste_fortschritt.js`.
 */
export class Fortschrittsmass {
    /** Anteil 0…1 des Bildes am Ende (0 bei leerem Projekt). */
    static anteil(bild, ende) {
        if (!(ende > 0)) return 0;
        return Math.min(1, Math.max(0, bild / ende));
    }

    /**
     * Das Bild an einer Pixelstelle des Balkens.
     * @param {number} x      Pixel vom linken Balkenrand
     * @param {number} breite Balkenbreite in Pixeln
     * @param {number} ende   letztes Bild
     */
    static bild(x, breite, ende) {
        if (!(breite > 0) || !(ende > 0)) return 0;
        return Math.round(Fortschrittsmass.anteil(x, breite) * ende);
    }
}
