/**
 * Genesis9lagen — Anziehreihenfolge und Lagen der getragenen Daz-Stücke.
 *
 * WARUM (Edgar, 19.09.2026: „das genesis T-Shirt ist an einigen Stellen
 * kaputt"): Der Bund der Jeans stach durch den Saum des Hemds — der Server
 * hob jedes Stück nur aus der Haut. Jetzt schickt jede Stückanfrage die
 * ANDEREN getragenen Stücke mit (`getragen`, in Anziehreihenfolge, und den
 * eigenen Platz `rang`); der Server ordnet ein (`Genesis9/lagen.py`: außen
 * liegt, was in der Überlappung weiter von der Haut steht) und hebt das Stück
 * über die inneren. Seine Antwort sagt `innen` (worüber es liegt) und
 * `aussen` (was über ihm liegt): DIE werden neu geholt, denn ihre
 * Kollisionsfläche hat sich mit diesem Stück geändert — eine Stufe tief, kein
 * Kreis (`kaskade`). Beim Ausziehen kommen die Stücke neu, die über dem
 * ausgezogenen lagen, sonst blieben sie über einer Jeans gewölbt, die
 * niemand mehr trägt.
 *
 * Die Anziehreihenfolge ist die Einfügereihenfolge von `inst.kleidung`; sie
 * entscheidet nur bei Gleichstand (spätere liegen außen). Ohne Importe, damit
 * `test_js_genesis9lagen` das Modul in Node prüft.
 */
export class Genesis9lagen {

    /** `[stil, pose, laenge]` eines Stücks ohne Leere. */
    static stilliste(werte) {
        return [werte?.stil || '', ...Object.values(werte?.stile || {})].filter(Boolean);
    }

    /** `{getragen, rang}` für die Anfrage eines Stücks: die anderen in Anziehreihenfolge. */
    static anfrage(kleidung, kennung) {
        const namen = Object.keys(kleidung || {});
        const platz = namen.indexOf(kennung);
        return {
            rang: platz < 0 ? namen.length : platz,
            getragen: namen.filter(k => k !== kennung).map(k => ({
                kennung: k, stil: Genesis9lagen.stilliste(kleidung[k]),
                regler_stueck: kleidung[k]?.regler || {},
            })),
        };
    }

    /** Nach der Antwort: Lagen merken und die äußeren Stücke neu holen. */
    static async nachziehen(inst, kennung, daten, stufen, kaskade) {
        inst.lagen[kennung] = { innen: daten.innen || [], aussen: daten.aussen || [] };
        if (!kaskade) return;
        await Promise.all((daten.aussen || [])
            .filter(andere => inst.kleidung[andere])
            .map(andere => inst.anziehen(andere, inst.kleidung[andere], stufen, false)));
    }

    /** Nach dem Ausziehen: die Stücke neu holen, die über dem ausgezogenen lagen. */
    static async nachAusziehen(inst, kennung, stufen = null) {
        delete inst.lagen[kennung];
        const oben = Object.entries(inst.lagen)
            .filter(([andere, lage]) => lage.innen.includes(kennung) && inst.kleidung[andere])
            .map(([andere]) => andere);
        await Promise.all(oben.map(
            andere => inst.anziehen(andere, inst.kleidung[andere], stufen, false)));
    }
}
