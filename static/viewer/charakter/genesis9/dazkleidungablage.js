import { Dazkleidung } from './dazkleidung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * DazkleidungAblage — die Daz-Stücke einer HumanBody-Figur, Kleidung UND Haar, im
 * gespeicherten Modell.
 *
 * BEFUND (Edgar, 30.09.2026): „habe gerade ein HumanBody mit Genesis Haar und Kleidern
 * erstellt, gespeichert. beim neu laden von /Charakter/ sind die wieder weg" — und dazu:
 * „mache ein Feld im Modell für die Kleidung und das Haar". Seit dem 19.09.2026 trägt eine
 * HumanBody-Figur Daz-Stücke (`Dazkleidung`), ihr Stand lag aber nur zur Laufzeit in
 * `inst.dazKleidung`. Weder `toJSON` (die Sitzung, die das Neuladen überbrückt, und die
 * Szenendatei) noch „Modell speichern" (`Szenenausgabe.modelldaten`) schrieben ihn — dieselbe
 * Lücke wie bei GarmentCode am 08.09.2026 (`GarmentcodeAblage`).
 *
 * DAS FELD HEISST `kleidung` wie bei einer Genesis-9-Figur (`Genesis9Figur.toJSON`) und hat
 * dieselbe Form: Kennung → Werte (`variante`, `stil`, `regler`, Farbe, Stoff) in
 * Anziehreihenfolge, das Haar eingeschlossen. Das Netz steht nicht in der Datei — beim Laden
 * holt `Dazkleidung.anziehen` es vom Server wie beim ersten Anziehen; der Antwortvorrat
 * kennt es dann meist schon.
 */
export class DazkleidungAblage {

    /** Der Name des Felds in Modell-, Szenen- und Sitzungsdaten. */
    static FELD = 'kleidung';

    /**
     * Kennung → Werte als TIEFE Kopie: Farbe und Stoff werden an den Werten der Figur
     * geändert (`Stueckfarbe`), eine flache Kopie schriebe in einen schon abgelegten Stand.
     */
    static toJSON(inst) {
        return structuredClone(inst?.dazKleidung || {});
    }

    /**
     * Die gespeicherten Stücke wieder anziehen — alle Anfragen zugleich; auf HumanBody baut
     * der Server jedes Stück für sich, ohne Lagenrechnung.
     *
     * Die Häkchen stehen sofort: `Dazkleidung.anziehen` trägt die Kennung ein, BEVOR es auf
     * den Server wartet — die Garderobe zeigt die Stücke angehakt, während die Netze noch
     * kommen. Ein Stück, das nicht kommt, wird gemeldet und bleibt eingetragen: sonst ginge
     * es beim nächsten Speichern verloren, nur weil der Server gerade neu lud.
     *
     * @param stuecke Kennung → Werte (das Feld `kleidung`), leer oder fehlend = nichts
     * @returns Versprechen der Zahl angezogener Stücke — es scheitert nie
     */
    static laden(inst, stuecke) {
        if (!inst || !stuecke || typeof stuecke !== 'object' || Array.isArray(stuecke)) {
            return Promise.resolve(0);
        }
        const laeufe = Object.entries(stuecke).map(([kennung, werte]) =>
            Dazkleidung.anziehen(inst, kennung, werte).then(() => 1, (fehler) => {
                Protokoll.warnung('Dazkleidung',
                    `„${kennung}" nicht wiederherstellbar: ${fehler?.message || fehler}`);
                return 0;
            }));
        return Promise.all(laeufe).then(zahlen => zahlen.reduce((summe, n) => summe + n, 0));
    }
}
