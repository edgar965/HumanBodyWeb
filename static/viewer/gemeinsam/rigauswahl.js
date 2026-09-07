/**
 * Rigauswahl — welche Figur bekommt ein Rig, und woran hängt es?
 *
 * WARUM (Edgar, 07.09.2026): „es gibt einen Button zum Rig ein und ausblenden.
 * das blendet das aber nur für HumanBody ein/aus. das soll für alle Modelle
 * sein die sichtbar sind." Der Umschalter nahm `_selectedInst()` und baute
 * EINEN `state.skeletonHelper` — bei vier Figurarten in einer Szene sah man
 * das Rig genau einer Figur.
 *
 * Diese Klasse enthält die Entscheidung, nicht die Anzeige: Sie hängt an
 * keinem Three.js und an keinem DOM und ist deshalb prüfbar
 * (`core/tests/unit/test_js_rigauswahl.py`). Das Bauen der Linien steht in
 * `scene/rigsichtbarkeit.js`.
 *
 * DIE WURZEL WIRD NICHT GERATEN
 * =============================
 * Die vier Figurarten halten ihr Skelett verschieden, und eine feste Liste von
 * Feldnamen wäre bei der fünften Art wieder falsch:
 *
 *     HumanBody (CharacterInstance)   inst.rigifySkeleton.rootBone
 *     UMA (GLB aus Unity)             inst.skelett.rootBone
 *     SMPL, MakeHuman                 kein Skelett — reine Netze
 *
 * Deshalb wird zuerst nach den bekannten Feldern gesucht und danach im
 * Szenenbaum: Ein `SkinnedMesh` trägt sein Skelett, und dessen erster Knochen
 * ohne Knochen-Elternteil ist die Wurzel. Damit bekommt auch ein importiertes
 * GLB mit Rig seine Linien, ohne dass hier etwas nachgetragen wird.
 */
export class Rigauswahl {

    /**
     * Die Skelettwurzel einer Figur — oder `null`.
     *
     * `suchen` ist der Ausweg für Figuren, die ihr Skelett in keinem der
     * bekannten Felder führen: eine Funktion, die den Szenenbaum der Figur
     * durchgeht und den ersten Knochen ohne Knochen-Elternteil liefert. Sie
     * wird hereingereicht, damit dieses Modul ohne Three.js auskommt.
     */
    static wurzel(inst, suchen = null) {
        if (!inst) return null;
        const bekannt = inst.rigifySkeleton?.rootBone || inst.skelett?.rootBone;
        if (bekannt) return bekannt;
        return (suchen ? suchen(inst) : null) || null;
    }

    /**
     * Ist die Figur in der Szene sichtbar?
     *
     * Eine ausgeblendete Figur bekommt keine Knochenlinien — sonst schwebt ein
     * Skelett ohne Körper im Bild, und der Nutzer sucht die Figur dazu.
     * `undefined` gilt als sichtbar: Three.js setzt `visible` erst, wenn es
     * jemand ändert.
     */
    static sichtbar(inst) {
        return !!inst && inst.group?.visible !== false;
    }

    /**
     * Welche Figuren sollen Linien zeigen?
     *
     * @param figuren  iterierbar über die Figuren (etwa `state.characters.values()`)
     * @param suchen   optionale Suche im Szenenbaum (siehe `wurzel`)
     * @returns [{inst, wurzel}]
     */
    static traeger(figuren, suchen = null) {
        const aus = [];
        for (const inst of (figuren || [])) {
            if (!Rigauswahl.sichtbar(inst)) continue;
            const wurzel = Rigauswahl.wurzel(inst, suchen);
            if (wurzel) aus.push({ inst, wurzel });
        }
        return aus;
    }

    /**
     * Was sich seit dem letzten Stand geändert hat.
     *
     * `bestand` ist eine Map `id -> wurzel` der Figuren, für die schon Linien
     * gebaut sind. Zurück kommen die drei Mengen, die die Anzeige braucht:
     *
     *     neu       Figur ist dazugekommen oder wieder sichtbar
     *     ersetzt   Figur ist dieselbe, aber ihre Wurzel eine andere
     *     weg       Figur ist verschwunden oder ausgeblendet
     *
     * `ersetzt` ist der Fall, den man vergisst: Die SMPL-Formregler und der
     * UMA-Typwechsel tauschen die Instanz unter DERSELBEN id aus
     * (`state.characters.set(inst.id, neu)`). Wer nur die ids vergleicht,
     * behält Linien, die an einem Skelett hängen, das nicht mehr in der Szene
     * steht — sie bleiben starr im Raum stehen.
     */
    static abgleich(traeger, bestand) {
        const jetzt = new Map((traeger || []).map(t => [t.inst.id, t]));
        const neu = [];
        const ersetzt = [];
        for (const [id, t] of jetzt) {
            if (!bestand.has(id)) neu.push(t);
            else if (bestand.get(id) !== t.wurzel) ersetzt.push(t);
        }
        const weg = [];
        for (const id of bestand.keys()) {
            if (!jetzt.has(id)) weg.push(id);
        }
        return { neu, ersetzt, weg };
    }
}
