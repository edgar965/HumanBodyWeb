import { DazkleidungAblage } from '../charakter/genesis9/dazkleidungablage.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Spurdazkleidung — die Daz-Stücke (Kleidung und Haar) eines gespeicherten
 * HumanBody-Modells im BVH Studio anziehen.
 *
 * ANLASS (Edgar, 30.09.2026: „bvh-studio fixe das auch"): Seit dem Abend trägt
 * das Modell die Daz-Stücke im Feld `kleidung` (`DazkleidungAblage`), und die
 * Szene zieht sie beim Laden an. Das Studio baut HumanBody über
 * `HumanbodyModell` + `Modellzubehoer` — dort kamen GarmentCode, Haare und
 * Kleidung an, die Daz-Stücke nicht. Genesis 9 kennt sein Feld selbst
 * (`Genesis9Modell`); das hier ist nur der HumanBody-Weg.
 *
 * Gebunden wird wie in der Szene über `Dazkleidung.binden` an
 * `modell.rigifySkeleton` — im Studio steht das Skelett schon beim Bau
 * (`HumanbodyModell._gehaeutet`), die Stücke folgen also sofort dem Mischer.
 * Nicht abgewartet: die Figur steht, die Stücke kommen dazu.
 */
export class Spurdazkleidung {

    /**
     * @param modell  das gebaute `HumanbodyModell`
     * @param vorgabe die Modelldatei (`/api/character/model/<name>/`)
     * @returns Versprechen der Zahl angezogener Stücke
     */
    static humanbody(modell, vorgabe) {
        const stuecke = vorgabe?.[DazkleidungAblage.FELD];
        if (!stuecke || !Object.keys(stuecke).length) return Promise.resolve(0);
        modell.dazBereit = DazkleidungAblage.laden(modell, stuecke).then((anzahl) => {
            Protokoll.debug('Spurdazkleidung',
                `${modell.presetName}: ${anzahl}/${Object.keys(stuecke).length} Daz-Stück(e)`);
            return anzahl;
        });
        return modell.dazBereit;
    }
}
