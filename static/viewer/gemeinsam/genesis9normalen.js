/**
 * Genesis9normalen — die Normalen der von Feldern berührten Punkte nachziehen.
 *
 * WARUM (18.09.2026 abends, Offen-Punkt „Normalen der Felder"): Die
 * Reglerfelder (JCMs, Visemes) verschieben Punkte je Bild, die Normalen
 * blieben die der Ruhelage — ein voller `computeVertexNormals` kostete auf
 * 104.480 Punkten 40 ms je Bild, und nur die berührten Punkte über die
 * Browserdreiecke zu rechnen ließ an den NAHTKOPIEN (ein Daz-Punkt, mehrere
 * Browserpunkte mit eigener UV) sichtbare Nähte entstehen: jede Kopie sah
 * nur ihre Hälfte der Dreiecke.
 *
 * Hier zählen die Kopien zusammen: Punkte mit derselben Ruhelage bilden eine
 * Gruppe (einmal je Netz über die Bits der Ruhekoordinaten), und die Normale
 * eines Punkts ist die Summe der Flächennormalen ALLER Dreiecke ALLER Kopien
 * (flächengewichtet wie `computeVertexNormals`). Damit die Grenze zwischen
 * berührt und unberührt keinen Sprung zeigt (die Ruhenormalen kommen vom
 * Server aus den Vierecken, nicht aus den Dreiecken), wird die DIFFERENZ
 * angewandt:
 *
 *     n[p] = normiert( nRuhe[p] + nDreiecke(verformt)[p] − nDreiecke(Ruhe)[p] )
 *
 * Bei Verschiebung null ist das exakt die Ruhenormale. Kosten je Bild: nur
 * die berührten Punkte und ihre Dreiecke (JCM Oberschenkel: einige tausend).
 */
export class Genesis9normalen {

    /** Vorbereitung je Geometrie: Nachbardreiecke (CSR) und Kopiengruppen. */
    static vorbereiten(geo, ruhePos) {
        const daten = geo.userData;
        if (daten.normalen) return daten.normalen;
        const lage = geo.getAttribute('position');
        const normal = geo.getAttribute('normal');
        if (!lage || !normal || !geo.index || !ruhePos) return null;
        const n = lage.count, index = geo.index.array;
        // Kopien: gleiche Ruhelage (Bits) → gleiche Gruppe.
        const bits = new Uint32Array(ruhePos.buffer, ruhePos.byteOffset, n * 3);
        const gruppe = new Uint32Array(n), gruppen = new Map();
        for (let p = 0; p < n; p++) {
            const key = `${bits[3 * p]},${bits[3 * p + 1]},${bits[3 * p + 2]}`;
            let g = gruppen.get(key);
            if (g === undefined) { g = gruppen.size; gruppen.set(key, g); }
            gruppe[p] = g;
        }
        // Mitglieder je Gruppe (CSR) und Dreiecke je Gruppe (CSR).
        const anzahl = gruppen.size;
        const mitgliedZahl = new Uint32Array(anzahl + 1), dreieckZahl = new Uint32Array(anzahl + 1);
        for (let p = 0; p < n; p++) mitgliedZahl[gruppe[p] + 1]++;
        for (let i = 0; i < index.length; i++) dreieckZahl[gruppe[index[i]] + 1]++;
        for (let g = 0; g < anzahl; g++) { mitgliedZahl[g + 1] += mitgliedZahl[g]; dreieckZahl[g + 1] += dreieckZahl[g]; }
        const mitglied = new Uint32Array(n), dreieck = new Uint32Array(index.length);
        const fm = Uint32Array.from(mitgliedZahl), fd = Uint32Array.from(dreieckZahl);
        for (let p = 0; p < n; p++) mitglied[fm[gruppe[p]]++] = p;
        for (let i = 0; i < index.length; i++) dreieck[fd[gruppe[index[i]]]++] = (i - i % 3);
        daten.normalen = {
            gruppe, mitgliedZahl, mitglied, dreieckZahl, dreieck,
            ruhe: Float32Array.from(normal.array),
            ruheDreiecke: new Float32Array(n * 3),      // je Gruppe einmal gerechnet …
            gerechnet: new Uint8Array(anzahl),           // … sobald sie berührt wird
            arbeit: [0, 0, 0],
        };
        return daten.normalen;
    }

    /** Flächennormalen aller Dreiecke der Gruppe `g` summieren (in `aus`). */
    static _summe(v, pos, index, g, aus) {
        aus[0] = aus[1] = aus[2] = 0;
        for (let k = v.dreieckZahl[g]; k < v.dreieckZahl[g + 1]; k++) {
            const t = v.dreieck[k];
            const a = 3 * index[t], b = 3 * index[t + 1], c = 3 * index[t + 2];
            const abx = pos[b] - pos[a], aby = pos[b + 1] - pos[a + 1], abz = pos[b + 2] - pos[a + 2];
            const acx = pos[c] - pos[a], acy = pos[c + 1] - pos[a + 1], acz = pos[c + 2] - pos[a + 2];
            aus[0] += aby * acz - abz * acy; aus[1] += abz * acx - abx * acz; aus[2] += abx * acy - aby * acx;
        }
        const l = Math.hypot(aus[0], aus[1], aus[2]) || 1;
        aus[0] /= l; aus[1] /= l; aus[2] /= l;
        return aus;
    }

    /**
     * Die Normalen der Punkte `punkte[0..anzahl)` nachziehen (nach dem
     * Schreiben der Positionen) und die der Punkte `vorher[0..vorherAnzahl)`
     * auf die Ruhe zurücksetzen. `ruhePos`: die Ruhelage (für die Ruhe-
     * Dreiecksnormale, einmal je Gruppe).
     */
    static nachziehen(geo, punkte, anzahl, vorher, vorherAnzahl, ruhePos) {
        const v = Genesis9normalen.vorbereiten(geo, ruhePos);
        if (!v) return false;
        const normal = geo.getAttribute('normal');
        const out = normal.array, pos = geo.getAttribute('position').array, index = geo.index.array;
        for (let j = 0; j < vorherAnzahl; j++) {
            const p = 3 * vorher[j];
            out[p] = v.ruhe[p]; out[p + 1] = v.ruhe[p + 1]; out[p + 2] = v.ruhe[p + 2];
        }
        const s = v.arbeit;
        for (let j = 0; j < anzahl; j++) {
            const q = punkte[j], g = v.gruppe[q];
            if (!v.gerechnet[g]) {
                Genesis9normalen._summe(v, ruhePos, index, g, s);
                for (let k = v.mitgliedZahl[g]; k < v.mitgliedZahl[g + 1]; k++) {
                    const m = 3 * v.mitglied[k];
                    v.ruheDreiecke[m] = s[0]; v.ruheDreiecke[m + 1] = s[1]; v.ruheDreiecke[m + 2] = s[2];
                }
                v.gerechnet[g] = 1;
            }
            Genesis9normalen._summe(v, pos, index, g, s);
            const p = 3 * q;
            let x = v.ruhe[p] + s[0] - v.ruheDreiecke[p];
            let y = v.ruhe[p + 1] + s[1] - v.ruheDreiecke[p + 1];
            let z = v.ruhe[p + 2] + s[2] - v.ruheDreiecke[p + 2];
            const l = Math.hypot(x, y, z) || 1;
            out[p] = x / l; out[p + 1] = y / l; out[p + 2] = z / l;
        }
        normal.needsUpdate = true;
        return true;
    }
}
