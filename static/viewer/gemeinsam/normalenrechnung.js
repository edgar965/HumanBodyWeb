/**
 * Normalenrechnung — die Zahlenrechnung hinter `Genesis9normalen`, OHNE Three.js und DOM (09.10.2026).
 *
 * WARUM: Die Gelenkkorrekturen (JCMs, `Genesis9gelenke`) verschieben an einer tanzenden Genesis-9-Figur über die Hälfte der
 * Körperpunkte JEDES Bild, und die Normalen dieser Punkte sind mit rund 78 % der größte Posten dieser Rechnung (gemessen im
 * Chrome-Tab, Damira, `genesis9normalen.js`). Der Hauptfaden stand dafür 25–70 ms je Bild — Animation und Zoomen ruckelten.
 * Dieselbe Rechnung läuft jetzt auch in einem Worker (`normalenarbeiter.js`); sie liegt hier, damit der Worker nichts
 * außer dieser Datei braucht (`Hautrechnung` ist nach demselben Muster gebaut).
 *
 * Die Normale eines Punktes ist die Summe der Flächennormalen ALLER Dreiecke ALLER Kopien seiner Gruppe (Punkte mit derselben
 * Ruhelage, UV-Nähte), als DIFFERENZ zur Ruhe angewandt, damit die Grenze zwischen berührt und unberührt keinen Sprung zeigt:
 *
 *     n[p] = normiert( nRuhe[p] + nDreiecke(verformt)[g] − nDreiecke(Ruhe)[g] )     (g = Gruppe von p, jeweils normiert)
 *
 * Das Netz wird dem Worker einmal übergeben (`index`, `gruppe`, die Ruhelage); je Bild kommen nur Punkte und Ruhenormalen mit.
 */
export class Normalenrechnung {

    /**
     * Die nicht normierte Flächennormalen-Summe JEDER Gruppe (`summen[3 g …]`): jedes Dreieck einmal rechnen und auf die
     * Gruppen seiner drei Ecken addieren. Ein Dreieck mit zwei Ecken in einer Gruppe zählt dort zweimal.
     * @param summen Float64Array(3 · Gruppen) — wird zuerst auf 0 gesetzt
     */
    static summen(index, gruppe, pos, summen) {
        summen.fill(0);
        for (let t = 0; t < index.length; t += 3) {
            const i0 = index[t], i1 = index[t + 1], i2 = index[t + 2];
            const a = 3 * i0, b = 3 * i1, c = 3 * i2;
            const abx = pos[b] - pos[a], aby = pos[b + 1] - pos[a + 1], abz = pos[b + 2] - pos[a + 2];
            const acx = pos[c] - pos[a], acy = pos[c + 1] - pos[a + 1], acz = pos[c + 2] - pos[a + 2];
            const nx = aby * acz - abz * acy, ny = abz * acx - abx * acz, nz = abx * acy - aby * acx;
            let h = 3 * gruppe[i0];
            summen[h] += nx; summen[h + 1] += ny; summen[h + 2] += nz;
            h = 3 * gruppe[i1];
            summen[h] += nx; summen[h + 1] += ny; summen[h + 2] += nz;
            h = 3 * gruppe[i2];
            summen[h] += nx; summen[h + 1] += ny; summen[h + 2] += nz;
        }
        return summen;
    }

    /** Die normierte Dreiecksnormale der Ruhelage für JEDEN Punkt (die seiner Gruppe) — `Float32Array(3 · Punkte)`. */
    static ruheDreiecke(index, gruppe, ruhePos, anzahlGruppen) {
        const summen = Normalenrechnung.summen(index, gruppe, ruhePos, new Float64Array(anzahlGruppen * 3));
        const aus = new Float32Array(gruppe.length * 3);
        for (let p = 0; p < gruppe.length; p++) {
            const g = 3 * gruppe[p];
            const l = Math.sqrt(summen[g] * summen[g] + summen[g + 1] * summen[g + 1] + summen[g + 2] * summen[g + 2]) || 1;
            aus[3 * p] = summen[g] / l; aus[3 * p + 1] = summen[g + 1] / l; aus[3 * p + 2] = summen[g + 2] / l;
        }
        return aus;
    }

    /**
     * Die Normalen der Punkte `punkte[0..anzahl)` aus der verformten Lage `pos` — kompakt, 3 Zahlen je Eintrag in der
     * Reihenfolge von `punkte`.
     * @param netz    `{index, gruppe, ruheDreiecke, summen}` (`summen`: Arbeitsfeld Float64Array(3 · Gruppen))
     * @param auftrag `{pos, ruheNormalen, punkte, anzahl}`
     */
    static rechnen(netz, auftrag) {
        const { gruppe, ruheDreiecke, summen } = netz;
        const { pos, ruheNormalen, punkte, anzahl } = auftrag;
        Normalenrechnung.summen(netz.index, gruppe, pos, summen);
        const aus = new Float32Array(anzahl * 3);
        for (let j = 0; j < anzahl; j++) {
            const q = punkte[j], g = 3 * gruppe[q], p = 3 * q;
            const ls = Math.sqrt(summen[g] * summen[g] + summen[g + 1] * summen[g + 1] + summen[g + 2] * summen[g + 2]) || 1;
            const x = ruheNormalen[p] + summen[g] / ls - ruheDreiecke[p];
            const y = ruheNormalen[p + 1] + summen[g + 1] / ls - ruheDreiecke[p + 1];
            const z = ruheNormalen[p + 2] + summen[g + 2] / ls - ruheDreiecke[p + 2];
            const l = Math.sqrt(x * x + y * y + z * z) || 1;
            aus[3 * j] = x / l; aus[3 * j + 1] = y / l; aus[3 * j + 2] = z / l;
        }
        return aus;
    }
}
