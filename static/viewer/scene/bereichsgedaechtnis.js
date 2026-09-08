/**
 * Welche Bereiche schon einmal da waren — damit neue offen anfangen.
 *
 * BEFUND (08.09.2026): Edgar suchte die Passform-Voreinstellungen und fand
 * sie nicht: „ich hatte dir aufgetragen für jedes Kleidungsstück
 * voreinstellungen zu machen «eng anliegend» usw. - das ist nicht gemacht
 * worden!" — dann, nach dem Aufklappen: „Korrektur - die sind im Bereich
 * Passform".
 *
 * Die Ursache liegt in `Starteinstellungen.bereicheOeffnen`: Gespeichert
 * werden nur die OFFENEN Bereiche (`expanded_panels_scene`), und alles, was
 * nicht in der Liste steht, wird zugeklappt. Ein Bereich, den es beim letzten
 * Speichern noch nicht gab, kann dort nicht stehen — jeder NEUE Bereich
 * startet also zugeklappt, für immer, bis jemand ihn zufällig findet.
 *
 * Aus der Liste allein ist „war zu" nicht von „ist neu" zu unterscheiden.
 * Deshalb merkt sich der Browser, welche Bereichsnamen er schon gesehen hat;
 * nur die werden zugeklappt. Ein Name, der zum ersten Mal auftaucht, bleibt
 * so, wie die Vorlage ihn setzt.
 *
 * WARUM `localStorage` UND NICHT DIE EINSTELLUNGEN: Das ist eine
 * Bequemlichkeit dieses Browsers, kein Projektzustand — und die
 * Einstellungen liegen serverseitig, ihr Format zu ändern hieße Migration.
 * Jeder Zugriff ist umschlossen: In einem privaten Fenster oder bei
 * gesperrten Seitendaten wirft schon das Lesen, und dann soll die Seite
 * trotzdem laufen (dann sind alle Bereiche „neu" und stehen offen — die
 * harmlose Richtung).
 */
export class Bereichsgedaechtnis {

    static SCHLUESSEL = 'hb_bereiche_gesehen';

    /** Die Namen, die dieser Browser schon einmal gesehen hat. */
    static gesehen() {
        try {
            const roh = localStorage.getItem(Bereichsgedaechtnis.SCHLUESSEL);
            const liste = roh ? JSON.parse(roh) : [];
            return new Set(Array.isArray(liste) ? liste : []);
        } catch (fehler) {
            return new Set();
        }
    }

    /** Namen dazuschreiben. */
    static merken(namen) {
        try {
            const alle = Bereichsgedaechtnis.gesehen();
            for (const name of namen) alle.add(name);
            localStorage.setItem(Bereichsgedaechtnis.SCHLUESSEL,
                                 JSON.stringify(Array.from(alle)));
            return alle.size;
        } catch (fehler) {
            return 0;
        }
    }

    /**
     * Soll dieser Bereich zugeklappt werden?
     *
     * @param name    Bereichsname (`data-panel-key`)
     * @param offene  die gespeicherten OFFENEN Namen
     * @param gesehen Ergebnis von `gesehen()` — einmal geholt, nicht je Bereich
     */
    static zuklappen(name, offene, gesehen) {
        if (offene.includes(name)) return false;
        // Neu: unberührt lassen. Bekannt und nicht offen: zuklappen.
        return gesehen.has(name);
    }
}
