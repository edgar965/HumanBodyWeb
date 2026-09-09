/**
 * Welche Schritte ein Bau hat — und wie lange sie dauern.
 *
 * HERAUSGELOEST AM 09.09.2026: `garmentcode_ablauf.js` stand bei 304 Zeilen,
 * und die Regel ist, dass eine Datei beim Anfassen nicht ueber ihre Grenze
 * waechst (`~/.claude/rules/struktur.md`). Der Schrittplan ist der
 * geschlossenste Block darin: reine Daten, kein DOM, keine Anfrage — und
 * damit fuer sich pruefbar.
 *
 * DIE ERWARTETEN DAUERN SIND GEMESSEN, nicht geschaetzt: Schnitt 4 s und
 * Panels unter 1 s (07.09.2026), Drapierung 22 s und Anziehen 3 s
 * (06.09.2026). Sie gewichten den Fortschrittsbalken; eine falsche Zahl
 * laesst ihn am Anschlag stehen, und das liest sich als „haengt".
 */
export class GarmentcodeSchritte {

    /** Diese Wege bauen keinen Schnitt, sie brauchen einen. */
    static NUR3D = ['3d', 'vorschau3d'];

    /**
     * Der Plan fuer einen Lauf.
     *
     * @param reiter  fuer `drapierbereit` — ohne Simulationsumgebung gibt es
     *                keine Drapier- und keinen Anziehschritt
     * @param modus   'vorschau2d' | 'vorschau3d' | '2d' | '3d' | 'komplett'
     */
    static fuer(reiter, modus) {
        const schritte = [];
        if (modus === 'vorschau3d') {
            return [{ schluessel: 'vorschau3d', erwartet: 1,
                      titel: 'Am Körper anlegen' }];
        }
        if (!GarmentcodeSchritte.NUR3D.includes(modus)) {
            schritte.push({ schluessel: 'schnitt', erwartet: 4,
                            titel: 'Schnitt konstruieren' });
        }
        if (modus === '2d' || modus === 'vorschau2d') {
            schritte.push({ schluessel: 'panels', erwartet: 1,
                            titel: 'Panels an die Figur' });
        }
        if (reiter.drapierbereit && modus !== '2d'
                && modus !== 'vorschau2d') {
            schritte.push({ schluessel: 'drape', erwartet: 22,
                            titel: 'Stoff drapieren' });
            schritte.push({ schluessel: 'rig', erwartet: 3,
                            titel: 'Anziehen' });
        }
        return schritte;
    }
}
