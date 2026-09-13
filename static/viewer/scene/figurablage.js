import { GarmentcodeAblage } from './garmentcode_ablage.js';

/**
 * Figurablage — Speichern und Laden einer Figur der Szene, mit ihren
 * GarmentCode-Stücken.
 *
 * WARUM HIER, NICHT IM MODELL (13.09.2026): Die Figurarten liegen seit heute
 * als `Modell`-Unterklassen in `gemeinsam/` (`UmaModell`, `MakehumanModell`,
 * `SmplModell`, `UmapythonModell`, `HumanbodyModell`) und kennen keinen
 * Szenenzustand. Die GarmentCode-Ablage braucht ihn (`GarmentcodeAblage`
 * hängt an `garmentcode_anziehen.js` und der Registrierung). Deshalb steht
 * der Weg EINMAL hier, und die dünnen Szene-Unterklassen (`UmaFigur`,
 * `MhFigur`, `SmplFigur`, `UmapythonFigur`) rufen ihn aus `toJSON`/`fromJSON`.
 *
 * Vorher (12.09.2026, Befund `doppelcode`) war das `Figurbasis` — die
 * gemeinsame Basis der vier Arten in der Szene; ihre Felder, `dispose` und
 * die Lage sind in `gemeinsam/modell.js` aufgegangen.
 */
export class Figurablage {

    /** Die Grunddaten des Modells plus die GarmentCode-Stücke. */
    static grunddaten(figur) {
        return {
            ...figur.grunddaten(),
            // GarmentCode-Stuecke ueberleben das Speichern (08.09.2026).
            [GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(figur),
        };
    }

    /**
     * `fromJSON` aller Arten: bauen, Lage setzen, anziehen.
     *
     * Die Reihenfolge zählt: `GarmentcodeAblage.laden` NACH `bauen()`, weil
     * die Stücke das Skelett der Figur brauchen und in der Lage der
     * Figurgruppe binden (07.09.2026, „Kleider von MakeHuman animieren
     * immer noch nicht").
     */
    static async ausJSON(Klasse, daten) {
        const figur = new Klasse(daten.id, daten);
        await figur.bauen();
        figur.lageSetzen(daten.transform);
        await GarmentcodeAblage.laden(figur, daten[GarmentcodeAblage.FELD]);
        return figur;
    }
}
