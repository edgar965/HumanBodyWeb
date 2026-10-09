import { Hautmaskegeometrie } from './hautmaskegeometrie.js';
import { Saumschnitt } from './saumschnitt.js';
import { Saumband } from './saumband.js';
import { Hautdicke } from './hautdicke.js';

/**
 * Hauteinzugrechnung — die Rechnung hinter `Hauteinzug.setzen`: wohin jede verdeckte Hautecke wandert.
 *
 * AUS `hauteinzug.js` ABGETEILT (09.10.2026, Edgar: „warum dauert laden des Characters ewig … ich brauche schnelles Anzeigen"):
 * Die Haut-Maske war der letzte große Block auf dem Hauptfaden — am feinen Körper (104.480 Punkte, 7 Stücke) 2,8 s im Leerlauf,
 * 11–14 s bei belasteter CPU, auf der Filmstufe bis 19 s. Die Rechnung braucht weder Three.js noch das DOM; sie läuft deshalb
 * in einem Web Worker (`hautarbeiter.js`, `hautrechnung.js`). Hier steht nur die Zahlenseite, `Hauteinzug` schreibt das Ergebnis
 * ins Attribut und patcht die Materialien.
 *
 * Die Beschreibung des Einzugs (Saumschnitt, Saumband, Dicke) steht in `hauteinzug.js`.
 */
export class Hauteinzugrechnung {

    /**
     * Der Einzug je Punkt (xyz, Meter, vor dem Skinning addiert) und was der Index daraus braucht.
     *
     * @param pos       Punkte des Körpers (Ruhelage)
     * @param maske     1 = verdeckt; null oder leer: kein Einzug
     * @param dreiecke  der volle Index; null: kein Einzug
     * @param optionen  `kanten` (Strecken, `Saumschnitt.kanten`), `normalen` (ersetzen die Ruhenormalen — ein Stoff unter Stoff
     *                  nimmt die der Haut, dann ohne Dickenbegrenzung), `hautnormalen` (die eigenen Ruhenormalen des Körpers,
     *                  schon gerechnet — sie sparen eine zweite Rechnung, ändern aber nichts am Ergebnis)
     * @returns {{werte: Float32Array, gesetzt: number, geschnappt: number, band: number, weg: Uint8Array|null}}
     */
    static rechnen(pos, maske, dreiecke, optionen = {}) {
        const n = pos.length / 3;
        const werte = new Float32Array(n * 3);
        const stand = { werte, gesetzt: 0, geschnappt: 0, band: 0, weg: null };
        if (!maske || !dreiecke) return stand;
        // Ruhenormalen nach außen (signiertes Volumen) — das `normal`-Attribut des Körpers zeigt im Browser nach innen.
        const N = optionen.normalen || optionen.hautnormalen || Hautmaskegeometrie.normalen(pos, dreiecke);
        const kanten = optionen.kanten?.length ? optionen.kanten : null;
        const gitter = kanten
            ? Hautmaskegeometrie.punktgitter(Saumschnitt.mitten(kanten), Saumschnitt.ZELLE_M) : null;
        const ecken = kanten ? Saumschnitt.randecken(maske, dreiecke) : null;
        const abstaende = Saumband.abstaende(pos, maske, dreiecke);
        // Nie tiefer als ein Teil der Körperdicke — sonst tritt ein Punkt an einer dünnen Stelle drüben wieder aus
        // (`hautdicke.js`). Nur für die Haut; Stoff unter Stoff bringt die Hautnormalen mit.
        const dicken = optionen.normalen ? null : Hautdicke.dicken(pos, N, maske);
        for (let i = 0; i < n; i++) {
            if (!maske[i]) continue;
            const nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
            const schnapp = (ecken && ecken[i])
                ? Saumschnitt.verschiebung(pos[3 * i], pos[3 * i + 1], pos[3 * i + 2], nx, ny, nz, kanten, gitter)
                : null;
            if (schnapp) {
                werte[3 * i] = schnapp[0]; werte[3 * i + 1] = schnapp[1]; werte[3 * i + 2] = schnapp[2];
                stand.geschnappt += 1;
            } else {
                const tiefe = dicken
                    ? Math.min(Saumband.tiefe(abstaende[i]), Hautdicke.grenze(dicken[i]))
                    : Saumband.tiefe(abstaende[i]);
                werte[3 * i] = -tiefe * nx;
                werte[3 * i + 1] = -tiefe * ny;
                werte[3 * i + 2] = -tiefe * nz;
            }
            if (abstaende[i] <= Saumband.BAND_M) stand.band += 1;
            stand.gesetzt += 1;
        }
        stand.weg = Saumband.weg(maske, abstaende);
        return stand;
    }
}
