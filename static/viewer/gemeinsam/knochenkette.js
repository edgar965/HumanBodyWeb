/**
 * Knochenkette — aus der Knochenliste des Servers eine Three.js-Hierarchie.
 *
 * WARUM (Edgar, 07.09.2026): „jedes Hinzufügen eines Modells soll auch das
 * Skeleton dazu erzeugen — UMA mit UMA Skeleton, SMPL mit SMPL Skeleton."
 * HumanBody und UMA bringen ihres mit; SMPL und MakeHuman waren reine Netze.
 * Beide Server liefern jetzt `{name, knochen: [{name, eltern, kopf, schwanz,
 * pos, quat, ende}]}` — SMPL aus `J_regressor`, MakeHuman aus
 * `default.mhskel`.
 *
 * DIE RECHNUNG STEHT IN PYTHON, NICHT HIER
 * ========================================
 * `pos` (lokal, relativ zum Elternteil) und `quat` (die Ruhedrehung des
 * Knochens) kommen fertig vom Server: `humanbody_core/skeleton/
 * gelenkskelett.py`. Bis zum 07.09.2026 rechnete dieses Modul `kopf −
 * elternKopf` selbst und setzte die Drehung auf Einheit — für die ANZEIGE
 * genügt das, für das Abspielen nicht: Der Retarget-Motor liefert LOKALE
 * Drehungen relativ zu einer Ruhelage, die der Browser dann nicht hatte
 * (`retarget/motor.py`, `bone.rest_local_quat`). Die Figur zappelte, ohne
 * dass irgendwo etwas rot wurde.
 *
 * Deshalb: EINE Rechnung, in Python, mit Gegenprobe
 * (`test_gelenkskelett.py` rechnet die Kette vorwärts und muss die Gelenke
 * wieder treffen). Hier bleibt das Ordnen und das Einsetzen der Vorgaben —
 * geprüft in `core/tests/unit/test_js_knochenkette.py`.
 *
 * DIE VORGABEN SIND EIN NETZ, KEIN VERFAHREN: Fehlt `pos`, gilt
 * `kopf − elternKopf`, fehlt `quat`, die Einheitsdrehung. Damit bleibt eine
 * ältere oder fremde Knochenliste zeichenbar; animierbar ist sie nicht.
 */
export class Knochenkette {

    /** Endknochen tragen diesen Zusatz — im Helper unsichtbar, im Log lesbar. */
    static ENDE = '_ende';

    /** Keine Drehung. */
    static EINHEIT = [0, 0, 0, 1];

    /**
     * Die Bauliste: Eltern stehen immer vor ihren Kindern.
     *
     * @param knochen [{name, eltern, kopf, schwanz, pos, quat, ende}]
     * @returns [{name, eltern, pos:[x,y,z], quat:[x,y,z,w], welt:[x,y,z],
     *           ende:boolean}] — `pos`/`quat` lokal, `welt` absolut.
     */
    static bauplan(knochen) {
        const liste = (knochen || []).filter(k => k && k.name && Array.isArray(k.kopf));
        const welt = new Map(liste.map(k => [k.name, k.kopf]));
        const geordnet = Knochenkette.geordnet(liste, welt);

        const plan = [];
        for (const k of geordnet) {
            const eltern = welt.has(k.eltern) ? k.eltern : null;
            plan.push({
                name: k.name,
                eltern,
                pos: Knochenkette.lage(k, eltern ? welt.get(eltern) : null),
                quat: Array.isArray(k.quat) ? k.quat : Knochenkette.EINHEIT,
                welt: k.kopf,
                ende: !!k.ende,
            });
        }
        plan.push(...Knochenkette.endknochen(geordnet, welt));
        return plan;
    }

    /**
     * Die lokale Lage eines Knochens.
     *
     * Der Server rechnet sie mit der Ruhedrehung des Elternteils; ohne die
     * bliebe nur der Weltabstand, und der stimmt genau dann, wenn keine
     * Drehungen im Spiel sind.
     */
    static lage(k, elternWelt) {
        if (Array.isArray(k.pos)) return k.pos;
        const ursprung = elternWelt || [0, 0, 0];
        return [k.kopf[0] - ursprung[0], k.kopf[1] - ursprung[1],
                k.kopf[2] - ursprung[2]];
    }

    /**
     * Eltern vor Kindern.
     *
     * Der Server sortiert schon; verlassen wird sich darauf nicht. Eine
     * Datei mit vertauschten Zeilen oder ein künftiges Rig würde sonst eine
     * halb aufgebaute Hierarchie ergeben, in der einzelne Gliedmaßen im
     * Ursprung hängen. Wer auf einen unbekannten Elternteil zeigt, gilt als
     * Wurzel — verworfen wird nichts.
     */
    static geordnet(liste, welt) {
        const offen = new Map(liste.map(k => [k.name, k]));
        const fertig = new Set();
        const aus = [];
        let bewegung = true;
        while (offen.size && bewegung) {
            bewegung = false;
            for (const [name, k] of [...offen]) {
                const wartet = k.eltern && welt.has(k.eltern) && !fertig.has(k.eltern);
                if (wartet) continue;
                aus.push(k);
                fertig.add(name);
                offen.delete(name);
                bewegung = true;
            }
        }
        // Was übrig bleibt, hängt im Kreis — hinten anstellen statt verlieren.
        aus.push(...offen.values());
        return aus;
    }

    /**
     * Je Blatt ein Endknochen an dessen `schwanz`.
     *
     * Ein `SkeletonHelper` zieht Linien von jedem Knochen zu seinem
     * Elternteil; ein Knochen ohne Kinder zeichnet damit nichts — bei
     * MakeHuman blieben so die Fingerspitzen unsichtbar, bei SMPL Hände,
     * Füße und Kopf.
     *
     * Der Server liefert diese Knochen inzwischen selbst (er braucht sie
     * auch für den Retarget). Dann ist jedes Blatt schon Elternteil seines
     * Endknochens, und diese Schleife findet nichts mehr — sie bleibt als
     * Netz für Listen ohne `ende`-Knochen.
     */
    static endknochen(geordnet, welt) {
        const hatKind = new Set(geordnet.map(k => k.eltern).filter(Boolean));
        const aus = [];
        for (const k of geordnet) {
            if (hatKind.has(k.name) || !Array.isArray(k.schwanz)) continue;
            // Ein Endknochen genau auf dem Gelenk wäre eine Linie der Länge
            // null — der Helper zeichnet sie, sichtbar ist sie nicht.
            const weg = Knochenkette.abstand(k.kopf, k.schwanz);
            if (weg < 1e-6) continue;
            aus.push({
                name: k.name + Knochenkette.ENDE,
                eltern: k.name,
                pos: [k.schwanz[0] - k.kopf[0], k.schwanz[1] - k.kopf[1],
                      k.schwanz[2] - k.kopf[2]],
                quat: Knochenkette.EINHEIT,
                welt: k.schwanz,
                ende: true,
            });
        }
        return aus;
    }

    static abstand(a, b) {
        const dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }

    /** Die Wurzel des Bauplans — der erste Knochen ohne Elternteil. */
    static wurzelname(plan) {
        const ohne = (plan || []).filter(k => !k.eltern);
        return ohne.length ? ohne[0].name : null;
    }
}
