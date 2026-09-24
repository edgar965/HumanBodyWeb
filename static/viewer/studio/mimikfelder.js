/**
 * Mimikfelder — Gewichte auf MB-Lab-Einheiten → Verschiebung je Netzpunkt.
 *
 * Das Gegenstück zu `Mimikbasis.bewegungen` für Figuren ohne DEF-Gesichts-
 * knochen (SMPL-X, 16.09.2026: „Mimik auch auf SMPL-X"). `smplx_basis.json`
 * (`manage.py mimik_vorbereiten`) führt je Einheit und Richtung ein dünnes
 * Feld `{i: [Punktindex, …], d: [dx, dy, dz, …]}` in Metern, Three.js-Achsen;
 * positive Gewichte nehmen `plus`, negative `minus` (MB-Labs _max/_min), der
 * Betrag skaliert. Die Felder addieren sich linear — wie die Knochendrehungen.
 *
 * Ohne Importe — `test_js_mimikfelder` rechnet in Node.
 */
export class Mimikfelder {

    /**
     * Summe der Felder: `Map<punktindex, [dx, dy, dz]>`; Punkte ohne Anteil
     * fehlen. `basis` ist der Inhalt von `smplx_basis.json`.
     */
    static summe(basis, gewichte) {
        const aus = new Map();
        for (const [einheit, g] of Object.entries(gewichte || {})) {
            const eintrag = basis?.[einheit];
            if (!eintrag || !g) continue;
            const feld = g > 0 ? eintrag.plus : eintrag.minus;
            if (!feld || !feld.i) continue;
            const betrag = Math.abs(g);
            const { i, d } = feld;
            for (let n = 0; n < i.length; n++) {
                let s = aus.get(i[n]);
                if (!s) { s = [0, 0, 0]; aus.set(i[n], s); }
                s[0] += d[n * 3] * betrag;
                s[1] += d[n * 3 + 1] * betrag;
                s[2] += d[n * 3 + 2] * betrag;
            }
        }
        return aus;
    }

    /**
     * `lage` (Float32Array, xyz je Punkt) aus `ruhe` + Summe neu schreiben —
     * nur die Punkte aus `vorher` (die beim letzten Mal bewegt waren) und die
     * der Summe werden angefasst. Gibt die Menge der jetzt bewegten Punkte zurück.
     */
    static anwenden(lage, ruhe, summe, vorher) {
        for (const p of vorher || []) {
            if (summe.has(p)) continue;
            lage[p * 3] = ruhe[p * 3];
            lage[p * 3 + 1] = ruhe[p * 3 + 1];
            lage[p * 3 + 2] = ruhe[p * 3 + 2];
        }
        for (const [p, d] of summe) {
            lage[p * 3] = ruhe[p * 3] + d[0];
            lage[p * 3 + 1] = ruhe[p * 3 + 1] + d[1];
            lage[p * 3 + 2] = ruhe[p * 3 + 2] + d[2];
        }
        return new Set(summe.keys());
    }

    /** Eine kurze Kennung der Gewichte — gleiche Gewichte, gleiche Kennung. */
    static kennung(gewichte) {
        return Object.entries(gewichte || {})
            .filter(([, g]) => g)
            .sort(([a], [b]) => (a < b ? -1 : 1))
            .map(([e, g]) => `${e}:${g.toFixed(4)}`)
            .join('|');
    }
}
