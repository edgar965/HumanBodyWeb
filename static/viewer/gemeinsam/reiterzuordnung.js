/**
 * Welcher Reiter gehört zu einem angeklickten Teilnetz?
 *
 * AUFTRAG (Edgar, 09.09.2026): „Klick auf die Hose ändert den Tab zu
 * Eigenschaften des Modells. Es soll zu GarmenCode wechseln!"
 *
 * Er hat recht, und es war nicht einmal eine Entscheidung: `_doSubMeshClick`
 * rief seit jeher fest `switchTab('eigenschaften')` — für jedes Teilnetz, ganz
 * gleich woher es kam. Bei einem GarmentCode-Stück ist das die falsche Seite:
 * Dort stehen die Kleiderregler der Bibliothek, während die 71 Regler DIESES
 * Stücks im GarmentCode-Reiter liegen.
 *
 * DIE ZUORDNUNG HÄNGT AM PRÄFIX DES SCHLÜSSELS, nicht am `type`. `type` ist
 * bei allen Kleidungsstücken `cloth` — egal ob sie aus der Bibliothek
 * (`gar_`), dem Kleiderbauer (`bld_`, `prim_`, `tpl_`) oder aus GarmentCode
 * (`gc_`) kommen. Die Präfixe sind ohnehin die Unterscheidung, an der auch
 * `_removeSubMesh` seine Aufräumzweige trennt.
 *
 * OHNE DOM, damit die Entscheidung prüfbar ist (`test_js_reiterzuordnung.py`).
 */
export class Reiterzuordnung {

    /** Präfix des Schlüssels → Reiter. Der erste Treffer gewinnt. */
    static NACH_PRAEFIX = [
        ['gc_', 'garmentcode'],
    ];

    /** Wohin ohne Treffer: der Reiter mit den Objekteigenschaften. */
    static VORGABE = 'eigenschaften';

    /**
     * Der Reiter für dieses Teilnetz.
     *
     * @param schluessel der Schlüssel aus `inst.clothMeshes` (z. B. `gc_hose`)
     * @returns die Reiterkennung (`data-tab`)
     */
    static fuer(schluessel) {
        const name = String(schluessel || '');
        for (const [praefix, reiter] of Reiterzuordnung.NACH_PRAEFIX) {
            if (name.startsWith(praefix)) return reiter;
        }
        return Reiterzuordnung.VORGABE;
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
