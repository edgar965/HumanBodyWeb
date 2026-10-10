/**
 * Genesis9ersatz — Teile der Figur ausblenden, die ein getragenes Stück ersetzt (08.10.2026).
 *
 * Edgar zum Import von „cute girl": „die augen hast du nicht importiert (als extra objekt)". Die Originalaugen kommen als
 * eigenes Stück (`Blendimportstuecke`); zwei Augäpfel in einer Höhle zeichnen sich gegenseitig durch. Das Stück nennt, was es
 * ersetzt (`ersetzt` in der Netzantwort, `Genesis9/stueckersatz.py`, am Netz `userData.ersetzt`), und diese Klasse blendet die
 * Netze der Figur aus, solange es getragen wird — und wieder ein, wenn es geht.
 *
 * AUSDRÜCKLICHE AUGENWAHL (09.10.2026, Edgar: „alle Modelle sollen alle Augen kriegen können"): Wählt der Nutzer in der
 * Toolbar ein Augen-Preset (`inst._augenGewaehlt`), gilt es auch bei einem Modell mit Ersatz-Augen — dann bleiben die Augen der
 * Figur sichtbar und das Ersatz-Stück weicht (`userData.ersatzGewichen`). „Original Augen vom Modell" bringt es zurück.
 *
 * Nur, was DIESE Klasse ausgeblendet hat (`userData.ersatzVerdeckt`, `ersatzGewichen`), bringt sie wieder: ein Netz, das jemand
 * anders versteckt hat, bleibt versteckt. Aufgerufen wird sie nach jedem An- und Ausziehen (`Genesis9kleidung.melden`) und nach
 * jedem Körperneubau; sie ist idempotent und deshalb auch richtig, wenn die Netze der Figur neu gebaut wurden.
 */
export class Genesis9ersatz {

    /** Name des Ersatzes → Teile des Netznamens `genesis9_<teil>_…` der Figur. */
    static NETZE = { augen: ['augen', 'traene'] };

    /** Alle Stücknetze der Figur: `clothMeshes` UND die Gruppe — `_kleiderBinden` ruft `nachziehen` auf, bevor das neu gebundene
     *  Stück in `clothMeshes` eingetragen ist (gemessen 09.10.2026: das Ersatz-Stück blieb sichtbar), die Gruppe hat es schon. */
    static _stuecke(inst) {
        return new Set([...Object.values(inst?.clothMeshes || {}), ...(inst?.group?.children || [])]);
    }

    /** Die Netze, die die Augen der Figur ersetzen. */
    static augenstuecke(inst) {
        return [...Genesis9ersatz._stuecke(inst)].filter(netz => (netz?.userData?.ersetzt || []).includes('augen'));
    }

    /** Trägt die Figur ein Stück, das ihre Augen ersetzt (auch wenn es gerade weicht)? */
    static hatAugen(inst) {
        return Genesis9ersatz.augenstuecke(inst).length > 0;
    }

    /** Die Teile, die gerade ersetzt sind: `Set` der Netz-Teilnamen. */
    static weg(inst) {
        const weg = new Set();
        const gewaehlt = !!inst?._augenGewaehlt;       // eigene Augenwahl: die Augen der Figur bleiben
        for (const netz of Genesis9ersatz._stuecke(inst)) {
            for (const name of netz?.userData?.ersetzt || []) {
                if (gewaehlt && name === 'augen') continue;
                for (const teil of Genesis9ersatz.NETZE[name] || []) weg.add(teil);
            }
        }
        return weg;
    }

    /** Netze der Figur je nach getragenen Stücken aus- oder einblenden. */
    static nachziehen(inst) {
        const weg = Genesis9ersatz.weg(inst);
        const bekannt = new Set(Object.values(Genesis9ersatz.NETZE).flat());
        for (const netz of inst?.group?.children || []) {
            const teil = /^genesis9_([a-z]+)_/.exec(netz.name || '')?.[1];
            if (!teil || !bekannt.has(teil)) continue;
            if (weg.has(teil)) {
                if (netz.visible) netz.userData.ersatzVerdeckt = true;
                netz.visible = false;
            } else if (netz.userData.ersatzVerdeckt) {
                netz.visible = true;
                netz.userData.ersatzVerdeckt = false;
            }
        }
        Genesis9ersatz._stueckWeichen(inst);
    }

    /** Die Ersatz-Augen selbst: weg, solange die Augen der Figur gewählt sind, sonst wieder da. */
    static _stueckWeichen(inst) {
        const weichen = !!inst?._augenGewaehlt;
        for (const netz of Genesis9ersatz.augenstuecke(inst)) {
            if (weichen) {
                if (netz.visible) netz.userData.ersatzGewichen = true;
                netz.visible = false;
            } else if (netz.userData.ersatzGewichen) {
                netz.visible = true;
                netz.userData.ersatzGewichen = false;
            }
        }
    }
}
