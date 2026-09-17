/**
 * Detailplan — je Wimpernstreifen und je Fußnagel die beteiligten Ecken.
 *
 * Aus `koerperdetails.js` abgeteilt (Code Review 17.09.2026: die Datei stand
 * bei 302 Zeilen). Der Plan hängt nur an der Topologie (Index + Gruppen) und
 * wird einmal je Geometrie gemerkt (`geometrie.userData.detailplan`);
 * `Koerperdetails.strecken` rechnet damit die Längen. Ohne Three.js — Index
 * als Uint32Array, Punkte als Float32Array, so läuft es auch in Node.
 */
export class Detailplan {

    /** Materialgruppen, die der Plan braucht (Index = `face_materials`). */
    static GRUPPE = { haut: 0, wimpern: 2, sklera: 4, naegelFuss: 10 };

    /**
     * Der Plan einer Geometrie: je Wimpernstreifen und je Fußnagel die
     * beteiligten Ecken. Einmal je Topologie (Index + Gruppen), gemerkt unter
     * `geometrie.userData.detailplan`.
     */
    static plan(index, gruppen, punkte) {
        const ecken = (nummer) => {
            const menge = new Set();
            for (const g of gruppen) {
                if (g.materialIndex !== nummer) continue;
                for (let k = g.start; k < g.start + g.count; k++) menge.add(index[k]);
            }
            return menge;
        };
        const haut = ecken(Detailplan.GRUPPE.haut);
        const sklera = Detailplan._schwerpunkteJeSeite([...ecken(Detailplan.GRUPPE.sklera)], punkte);
        return {
            wimpern: Detailplan._teile(index, gruppen, Detailplan.GRUPPE.wimpern)
                .map(teil => ({ ecken: teil, sklera })),
            naegelFuss: Detailplan._teile(index, gruppen, Detailplan.GRUPPE.naegelFuss)
                .map(teil => ({ wurzel: teil.filter(e => haut.has(e)), frei: teil.filter(e => !haut.has(e)) })),
        };
    }

    /** Zusammenhängende Teile einer Gruppe (Ecken, die über Dreiecke verbunden sind). */
    static _teile(index, gruppen, nummer) {
        const eltern = new Map();
        const finden = (a) => {
            while (eltern.get(a) !== a) { eltern.set(a, eltern.get(eltern.get(a))); a = eltern.get(a); }
            return a;
        };
        const vereinen = (a, b) => { eltern.set(finden(a), finden(b)); };
        for (const g of gruppen) {
            if (g.materialIndex !== nummer) continue;
            for (let k = g.start; k + 2 < g.start + g.count; k += 3) {
                for (const e of [index[k], index[k + 1], index[k + 2]]) if (!eltern.has(e)) eltern.set(e, e);
                vereinen(index[k], index[k + 1]);
                vereinen(index[k], index[k + 2]);
            }
        }
        const teile = new Map();
        for (const e of eltern.keys()) {
            const w = finden(e);
            if (!teile.has(w)) teile.set(w, []);
            teile.get(w).push(e);
        }
        return [...teile.values()];
    }

    /** Schwerpunkt der Ecken links (x < 0) und rechts (x ≥ 0). */
    static _schwerpunkteJeSeite(ecken, p) {
        const summe = { links: [0, 0, 0, 0], rechts: [0, 0, 0, 0] };
        for (const e of ecken) {
            const s = p[3 * e] < 0 ? summe.links : summe.rechts;
            s[0] += p[3 * e]; s[1] += p[3 * e + 1]; s[2] += p[3 * e + 2]; s[3] += 1;
        }
        const mittel = (s) => (s[3] ? [s[0] / s[3], s[1] / s[3], s[2] / s[3]] : null);
        return { links: mittel(summe.links), rechts: mittel(summe.rechts) };
    }
}
