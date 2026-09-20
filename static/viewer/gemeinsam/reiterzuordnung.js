/**
 * Welcher Reiter gehört zu einem angeklickten Teilnetz — und welche Zeile darin?
 *
 * AUFTRAG (Edgar, 09.09.2026): „Klick auf die Hose ändert den Tab zu
 * Eigenschaften des Modells. Es soll zu GarmenCode wechseln!" — und wieder
 * am 20.09.2026: „wenn ich auf ein Asset oder Garment Code oder was auch
 * immer klicke, soll in der Toolbar genau das ausgewählt sein. das hatte ich
 * schon oft so als Auftrag vergeben!"
 *
 * Bis dahin kannte diese Zuordnung nur `gc_`; jedes andere Stück — die
 * Daz-Garderobe, MakeHuman, Garment Fit, die Kleider — landete weiter im
 * Modell-Reiter, und seine Zeile in der Liste blieb unmarkiert.
 *
 * DIE ZUORDNUNG HÄNGT AM PRÄFIX DES SCHLÜSSELS, nicht am `type`. `type` ist
 * bei allen Kleidungsstücken `cloth` — egal ob sie aus der Bibliothek
 * (`gar_`), MakeHuman (`mhk_`), dem Kleider-Reiter (`kld_`), Daz auf einer
 * HumanBody-Figur (`daz_<kennung>/<teil>`), der Daz-Garderobe einer
 * Genesis-9-Figur (`<kennung>/<teil>`, ohne Präfix) oder aus GarmentCode
 * (`gc_`) kommen. Die Präfixe sind ohnehin die Unterscheidung, an der auch
 * `_removeSubMesh` seine Aufräumzweige trennt.
 *
 * OHNE DOM, damit die Entscheidung prüfbar ist (`test_js_reiterzuordnung.py`);
 * das Markieren im DOM macht `scene/stueckmarkierung.js`.
 */
export class Reiterzuordnung {

    /** Präfix des Schlüssels → [Reiter, Liste]. Der erste Treffer gewinnt. */
    static NACH_PRAEFIX = [
        ['gc_', 'garmentcode', 'garmentcode'],
        ['kld_', 'kleider', 'kleider'],
        ['gar_', 'assets', 'garment'],
        ['mhk_', 'assets', 'makehuman'],
        ['daz_', 'assets', 'daz'],
    ];

    /** Wohin ohne Treffer: der Reiter mit den Objekteigenschaften. */
    static VORGABE = 'eigenschaften';

    /** Ein Daz-Stück auf Genesis 9: `<kennung>/<teil>` — die HumanBody-Frisur
     *  (`humanbody_frisur/0`) sitzt zwar auch so, gehört aber zum Modell-Reiter. */
    static DAZ_TEIL = /^([^/]+)\/\d+$/;

    /**
     * Der Reiter für dieses Teilnetz.
     *
     * @param schluessel der Schlüssel aus `inst.clothMeshes` (z. B. `gc_hose`)
     * @returns die Reiterkennung (`data-tab`)
     */
    static fuer(schluessel) {
        const stueck = Reiterzuordnung.stueckVon(schluessel);
        return stueck ? stueck.reiter : Reiterzuordnung.VORGABE;
    }

    /**
     * Reiter, Liste und Kennung des Stücks hinter einem Schlüssel — `null`
     * bei allem, was keine eigene Zeile in einem Reiter hat (Haar, Kleiderbauer).
     *
     * @returns `{reiter, liste, kennung}` oder `null`
     */
    static stueckVon(schluessel) {
        const name = String(schluessel || '');
        for (const [praefix, reiter, liste] of Reiterzuordnung.NACH_PRAEFIX) {
            if (!name.startsWith(praefix)) continue;
            const rest = name.slice(praefix.length);
            const kennung = liste === 'daz' ? Reiterzuordnung.dazKennung(rest) : rest;
            return kennung ? { reiter, liste, kennung } : null;
        }
        const kennung = Reiterzuordnung.dazKennung(name);
        return kennung ? { reiter: 'assets', liste: 'daz', kennung } : null;
    }

    /** `angie_jeans/2` → `angie_jeans`; `humanbody_frisur/0` und alles andere → `null`. */
    static dazKennung(name) {
        const treffer = Reiterzuordnung.DAZ_TEIL.exec(name);
        if (!treffer || treffer[1].startsWith('humanbody_')) return null;
        return treffer[1];
    }

    /**
     * Die GarmentCode-Vorlage hinter einem Schlüssel — `null` bei allem
     * anderen.
     *
     * Sie ist der zweite Teil der Antwort auf denselben Befund: Ein Reiter,
     * der aufgeht und dabei die Regler eines ANDEREN Stücks zeigt, ist keine
     * Hilfe. Genau daran hing am 09.09.2026 ein Bau, der „sommerkleid" statt
     * „hose" erzeugte, weil die Auswahl im Reiter etwas anderes führte als
     * die Figur trug.
     */
    static vorlageVon(schluessel) {
        const name = String(schluessel || '');
        return name.startsWith('gc_') ? name.slice(3) : null;
    }
}
