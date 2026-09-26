/**
 * Materialziel — auf WELCHE Stücke ein Reglerstand aus „Farbe / Material"
 * gelegt wird.
 *
 * Edgar, 12.09.2026: „bei GarmentCode - bereich Farbe/Material - ändere ich
 * das Gewebe, oder andere Einstellungen, tut sich nichts." Seit dem
 * 09.09.2026 wirkten die Regler NUR auf ein angeklicktes Stück; ohne Auswahl
 * wurde der Stand bloß gemerkt. Die Überschrift des Bereichs versprach
 * dagegen „ohne Auswahl für alle GarmentCode-Stücke dieser Figur" — und
 * Edgar tat, was sie sagte: Regler bewegt, nichts passiert.
 *
 * WARUM ES AM 09.09. ABGESCHALTET WURDE, UND WARUM DAS HIER NICHT WIEDERKOMMT
 * ==========================================================================
 * Das Reitergedächtnis stellt beim Seitenstart `gc-color` her und feuert
 * dabei `input` — ohne dass jemand etwas angeklickt hat. Ein Vorbild aus
 * dem Kleider-Reiter schreibt ebenso Farbe und Glanz in die Felder. Beides
 * ging „auf alle" und überschrieb Farben, die Stücke aus der gespeicherten
 * Szene mitgebracht hatten (gemessen: #dcd8d0 → #ff0000 durch EIN `input`).
 *
 * Die Unterscheidung ist deshalb NICHT „Auswahl oder nicht", sondern
 * „Nutzer oder Code": Ein Ereignis, das der Nutzer am Feld auslöst, trägt
 * `isTrusted`; ein synthetisches (`dispatchEvent`) nicht. Nur der Nutzer
 * darf breit wirken. Was Code in die Felder schreibt, wird gemerkt und
 * gilt für das nächste gebaute Stück — wie seit dem 09.09.
 *
 * „BREIT" HEISST SEIT DEM 20.09.2026 NICHT MEHR „ALLE", SONDERN „DAS STÜCK
 * DER GEWÄHLTEN VORLAGE" (Edgar: „ich habe Kin1 aktiviert und möchte ein
 * T-Shirt erzeugen, sobald ich die Farbe eingeben will, wird die Farbe der
 * Leggings geändert!!"): Wer im Reiter „Oberteil" stehen hat und die Farbe
 * für das T-Shirt einstellt, das er gleich baut, meint nicht die Leggings,
 * die schon hängen. Ohne Auswahl bekommt den Stand also nur das Stück, das
 * zur gewählten Vorlage gehört (`gc_<vorlage>`), falls es hängt; sonst
 * niemand — der Stand wird gemerkt und liegt auf dem nächsten Bau.
 *
 * Ohne DOM und ohne Three.js, damit die Entscheidung in Node prüfbar ist.
 */
export class Materialziel {

    /** Der Schlüssel eines GarmentCode-Stücks in `clothMeshes`. */
    static VORSILBE = 'gc_';

    /**
     * Die Netze, die den Stand bekommen.
     *
     * @param {Object} [wahl]
     * @param {Object|null} [wahl.gewaehlt]  das angeklickte GarmentCode-Stück
     * @param {Object|null} [wahl.stuecke]  `inst.clothMeshes` der Figur
     * @param {boolean} [wahl.nutzer]  hat der Nutzer das Feld bedient?
     * @param {string|null} [wahl.aktuell]  Schlüssel des Stücks der
     *        gewählten Vorlage (`gc_oberteil`)
     * @returns {Array<Object>} gewählt → nur dieses; sonst bei einer
     *          Nutzeraktion das Stück der gewählten Vorlage, falls es
     *          hängt; sonst keines
     */
    static netze({ gewaehlt = null, stuecke = null, nutzer = false,
                   aktuell = null } = {}) {
        if (gewaehlt) return [gewaehlt];
        if (!nutzer || !aktuell) return [];
        const netz = (stuecke || {})[aktuell];
        return netz && String(aktuell).startsWith(Materialziel.VORSILBE) ? [netz] : [];
    }
}
