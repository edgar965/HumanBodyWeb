/**
 * Genesis9ersatz — Teile der Figur ausblenden, die ein getragenes Stück ersetzt (08.10.2026).
 *
 * Edgar zum Import von „cute girl": „die augen hast du nicht importiert (als extra objekt)". Die Originalaugen kommen als
 * eigenes Stück (`Blendimportstuecke`); zwei Augäpfel in einer Höhle zeichnen sich gegenseitig durch. Das Stück nennt, was es
 * ersetzt (`ersetzt` in der Netzantwort, `Genesis9/stueckersatz.py`, am Netz `userData.ersetzt`), und diese Klasse blendet die
 * Netze der Figur aus, solange es getragen wird — und wieder ein, wenn es geht.
 *
 * Nur, was DIESE Klasse ausgeblendet hat (`userData.ersatzVerdeckt`), bringt sie wieder: ein Netz, das jemand anders versteckt
 * hat, bleibt versteckt. Aufgerufen wird sie nach jedem An- und Ausziehen (`Genesis9kleidung.melden`); sie ist idempotent und
 * deshalb auch richtig, wenn die Netze der Figur neu gebaut wurden (neu gebaute Netze sind sichtbar).
 */
export class Genesis9ersatz {

    /** Name des Ersatzes → Teile des Netznamens `genesis9_<teil>_…` der Figur. */
    static NETZE = { augen: ['augen', 'traene'] };

    /** Die Teile, die gerade ersetzt sind: `Set` der Netz-Teilnamen. */
    static weg(inst) {
        const weg = new Set();
        for (const netz of Object.values(inst?.clothMeshes || {})) {
            for (const name of netz.userData?.ersetzt || []) {
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
    }
}
