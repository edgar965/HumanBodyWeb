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

    /**
     * Die GarmentCode-Stücke einer Genesis-9-Figur für die Lagenrechnung
     * (24.09.2026, Edgar: „GarmentCode Pants Harem zieht die Kleider bei Genesis
     * nicht über existierende Genesis-Kleider"): `[{stueck, ordner, rig_datei,
     * stand}]` — nur Stücke, deren Netz noch hängt (`gc_<stück>`; die Ablage
     * vergisst gelöschte nicht). `stand` macht einen Neubau unter demselben
     * Dateinamen für den Antwortvorrat des Servers unterscheidbar.
     */
    static gcGetragen(inst) {
        if (inst?.quelle !== 'genesis9') return [];
        return Object.values(inst.gcStuecke || {}).map((e) => {
            const teile = String(e?.rig_url || '').split('/').filter(Boolean);
            const schluessel = `gc_${String(e?.stueck || 'kleidung').replace(/[^a-z0-9_-]/gi, '_')}`;
            // Einem Reglerzug nachgeformt (`Gcreglerfolge`): die Punkte, wie sie hängen.
            const rig = inst.clothMeshes?.[schluessel]?.userData?.gcRig;
            return {
                stueck: e?.stueck, ordner: teile[teile.length - 2], rig_datei: teile[teile.length - 1],
                stand: rig?.nachgeformt ? `${e?.stand || ''}:${rig.nachgeformt}` : (e?.stand || ''),
                ...(rig?.punkte64 ? { punkte: rig.punkte64 } : {}),
                haengt: !!inst.clothMeshes?.[schluessel],
            };
        }).filter(e => e.haengt && e.ordner && e.rig_datei)
            .map(({ haengt, ...e }) => e);
    }

    /** Nach der Antwort: Lagen merken und die äußeren Stücke neu holen. */
    static async nachziehen(inst, kennung, daten, stufen, kaskade) {
        inst.lagen[kennung] = { innen: daten.innen || [], aussen: daten.aussen || [] };
        if (!kaskade) return;
        // `gc:`-Stücke stehen nicht in `inst.kleidung` — die baut nur GarmentCode neu.
        await Promise.all((daten.aussen || [])
            .filter(andere => inst.kleidung[andere])
            .map(andere => inst.anziehen(andere, inst.kleidung[andere], stufen, false)));
    }

    /**
     * Nach einem GarmentCode-Bau (24.09.2026): jedes Daz-Stück neu holen, das
     * NICHT als innere Lage in den Bau einging (`unter` = `ueber_getragene` der
     * Antwort) — der Server legt es dann über das neue Stück (`gc:` in den Lagen).
     * Erst holte das nur die als außen gemeldeten Kleidungsstücke (`daz_aussen`);
     * Damiras Haar ist keine Kleidung und blieb unter dem Kleid (Edgar: „die
     * Haare müssten nach GarmentCode nach außen angepasst werden"). Ohne Haken
     * „über getragene" ist `unter` leer: alles kommt neu. `stuecke`: ein Name oder
     * mehrere (gemeinsamer Bau). Gibt die neu geholten Kennungen zurück.
     */
    static async nachGcBau(inst, stuecke, unter = []) {
        if (inst?.quelle !== 'genesis9' || ![].concat(stuecke || []).length) return [];
        const neu = Object.keys(inst.kleidung || {}).filter(k => !(unter || []).includes(k));
        await Promise.all(neu.map(k => inst.anziehen(k, inst.kleidung[k], null, true)));
        return neu;
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
