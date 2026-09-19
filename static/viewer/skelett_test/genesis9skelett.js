import * as THREE from 'three';
import { Zielskelett } from './zielskelett.js';
import { Knochenbau } from '../gemeinsam/knochenbau.js';

/**
 * Genesis9skelett — das Daz-Rig (Genesis 9) als Skelettspalte.
 *
 * WARUM (Edgar, 19.09.2026): „füge in test-animation den Genesis Rig als
 * neuen Rig hinzu, so wie andere". Genesis 9 ist seit dem 17.09.2026 die
 * sechste Figurart und ein Ziel des Retargets (`target=genesis9`); ob eine
 * Bewegung dort ankommt wie auf DEF, sieht man erst nebeneinander — die
 * hängenden Schultern vom 19.09. wären hier aufgefallen.
 *
 * Der Server liefert die Kette der Grundstellung
 * (`/api/character/genesis9-skeleton/`, `G9formung({}).skelett().bauen()`)
 * in Metern, Y oben, Füße am Boden — genau die Kette, gegen die der Retarget
 * rechnet. Gebaut wird sie wie in der Szene über `Knochenbau` (gemeinsam);
 * die Wegwerfgruppe nimmt die Wurzel nur auf, bis `Einpassung` sie in die
 * Hülle der Spalte hängt.
 */
export class Genesis9skelett extends Zielskelett {

    static ADRESSE = '/api/character/genesis9-skeleton/';
    static PLATZ = 'genesis9';
    static NAME = 'Genesis 9';
    static FEHLT = 'Daz-Bibliothek fehlt';

    static bauen(daten) {
        const gebaut = Knochenbau.bauen(daten, new THREE.Group());
        if (!gebaut) throw new Error('Genesis-9-Skelett ohne Knochen');
        return gebaut;
    }

    static herkunft(daten) {
        return daten.figur || '';
    }
}
