/**
 * Stueckaufklappung — was für ein angeklicktes Stück aufgeklappt wurde, wieder zuklappen.
 *
 * Edgar, 30.09.2026: „Wenn man mal Schuhe ausgewählt hat, zeigt der Tab die ausgewählten
 * Schuhe links. Wenn man woanders klickt, bleibt der Tab ‚Schuhe‘ offen. der soll wieder
 * zu sein, wenn man was anderes klickt, sonst ist die Navigation unmöglich."
 *
 * `Stueckmarkierung.aufklappen` öffnet die Kategorie des angeklickten Stücks, damit seine
 * Zeile sichtbar ist. Zurückgenommen wurde das nie: `loeschen()` entfernte die Markierung
 * der Zeile, der Kasten blieb offen. Nach ein paar Klicks steht die halbe Garderobe offen —
 * und genau die Vorgabe „alles zu beim Laden", die hier mehrfach beauftragt war, ist wieder
 * hinfällig.
 *
 * DIE DAZ-GARDEROBE: GENAU DIE KATEGORIE DES GEWÄHLTEN STÜCKS OFFEN (`nurDie`). Der erste
 * Versuch merkte sich nur, was DIESE Klasse geöffnet hatte, und nahm genau das zurück — im
 * Chrome nachgeklickt blieb „Oberteile" trotzdem offen, als danach die Hose gewählt wurde.
 * Die Kategorie öffnet nämlich auch der Bau der Garderobe (`Genesis9garderobe.fuellen`:
 * offen, wenn sie das gewählte Stück enthält), und von DEM wusste die Klasse nichts. Jetzt
 * gilt nach jedem Auswahlwechsel dieselbe Regel wie beim Bau: die Kategorie des gewählten
 * Stücks offen, alle anderen zu — gleich, wer sie geöffnet hatte. Wer woanders hinklickt
 * (Haut, GarmentCode, leer), bekommt alle zu.
 *
 * DIE ANDEREN LISTEN (Garment Fit, MakeHuman): Dort wird nur zurückgenommen, was diese
 * Klasse selbst aufgeklappt hat (`oeffnen`/`zuklappen`) — ihr Aufbau kennt keine Regel „nur
 * das Gewählte offen", und was der Nutzer dort selbst aufklappt, soll bleiben.
 *
 * Der Bereich (`.panel-section.collapsed`) gehört NICHT dazu: Er hat sein eigenes
 * Gedächtnis (`expanded_panels_scene`) und ist nicht die Navigation, über die Edgar
 * spricht.
 */
export class Stueckaufklappung {

    /** Die Kategorien der Daz-Garderobe (`Genesis9garderobe.fuellen`). */
    static KATEGORIE = 'details.g9-kategorie';

    /**
     * Daz-Garderobe: nur die Kategorie um `zeile` offen, alle anderen zu.
     * @param zeile die markierte Zeile — oder null: dann alle zu
     * @param wurzel wo gesucht wird (Test: eine Attrappe; sonst das Dokument)
     */
    static nurDie(zeile, wurzel = globalThis.document) {
        if (!wurzel?.querySelectorAll) return;
        for (const kategorie of wurzel.querySelectorAll(Stueckaufklappung.KATEGORIE)) {
            kategorie.open = Boolean(zeile) && kategorie.contains(zeile);
        }
    }

    /** Was wir geöffnet haben: `[{ zu: () => void, element }]`. */
    static _offen = [];

    /**
     * Einen Kasten öffnen und merken, falls er zu war.
     * @param element das `<details>`, `.anim-category` oder `.anim-folder`
     * @param istOffen ob es jetzt schon offen ist
     * @param oeffnen Wie man es öffnet
     * @param schliessen Wie man es wieder schliesst
     */
    static oeffnen(element, istOffen, oeffnen, schliessen) {
        if (!element) return;
        if (istOffen) return;                      // der Nutzer hatte ihn offen
        oeffnen();
        Stueckaufklappung._offen.push({ element, zu: schliessen });
    }

    /**
     * Alles zuklappen, was wir geöffnet haben — ausser den Kästen um `behalten`.
     * @param behalten Element (die neu markierte Zeile), dessen Kästen offen bleiben
     */
    static zuklappen(behalten = null) {
        const bleibt = Stueckaufklappung._offen.filter(e => {
            if (behalten && e.element.contains(behalten)) return true;
            try { e.zu(); } catch (fehler) { /* Element ist weg — nichts zu tun */ }
            return false;
        });
        Stueckaufklappung._offen = bleibt;
    }

    /** Für den Neubau der Listen: das Gedächtnis fallen lassen, ohne zu schliessen. */
    static vergessen() {
        Stueckaufklappung._offen = [];
    }
}
