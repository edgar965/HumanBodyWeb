/**
 * Lippengruppe — die Lippen als eigene Materialgruppe des Körpernetzes.
 *
 * WARUM (Edgar, 12.09.2026: „es fehlen noch die Lippen (farbe usw.)"): Das
 * HumanBody-Netz kennt elf Materialgruppen (Haut, Wimpern, Augen, Zunge,
 * Zähne, Nägel …), aber keine Lippen — sie sind Haut. Der Server liefert
 * die Lippenpunkte (`lippen` in `/api/character/mesh/`, aus der MB-Lab-
 * Maske an den UVs, `core/dienste/lippenmaske.py`); hier werden die
 * Hautdreiecke, deren drei Ecken alle Lippenpunkte sind, ans Ende des
 * Hautbereichs sortiert und als Gruppe `LIPPEN` ausgewiesen. Der Index
 * bleibt vollständig (kein Dreieck geht verloren), die übrigen Gruppen
 * behalten ihre Bereiche.
 *
 * Ohne Three.js: Index und Gruppen als Felder herein, neue heraus — prüfbar
 * in Node (`test_js_lippengruppe.py`). Die Netzseite (Material, `setIndex`)
 * steht in `scene/lippenbau.js`.
 */
export class Lippengruppe {

    /** Materialgruppe der Haut, aus der abgespalten wird. */
    static HAUT = 0;
    /** Die neue Gruppe — direkt hinter den elf des Netzes (`koerpermaterialien.js`). */
    static LIPPEN = 11;

    /**
     * Den Hautbereich umsortieren: Lippendreiecke nach hinten, eigene Gruppe.
     * @param {ArrayLike<number>} index  voller Dreiecksindex
     * @param {Array<{start,count,materialIndex}>} gruppen
     * @param {ArrayLike<number>} lippen  Punktindizes der Lippen
     * @returns {{index: Uint32Array, gruppen: object[], dreiecke: number}}
     *          `dreiecke` = Zahl der abgespaltenen Dreiecke (0 = nichts getan)
     */
    static abspalten(index, gruppen, lippen) {
        const haut = (gruppen || []).find(g => g.materialIndex === Lippengruppe.HAUT);
        const menge = new Set(lippen || []);
        if (!haut || !menge.size || (gruppen || []).some(g => g.materialIndex === Lippengruppe.LIPPEN)) {
            return { index, gruppen, dreiecke: 0 };
        }
        const neu = Uint32Array.from(index);
        const rest = [], lippe = [];
        for (let k = haut.start; k + 2 < haut.start + haut.count; k += 3) {
            const ziel = menge.has(index[k]) && menge.has(index[k + 1]) && menge.has(index[k + 2])
                ? lippe : rest;
            ziel.push(index[k], index[k + 1], index[k + 2]);
        }
        if (!lippe.length) return { index, gruppen, dreiecke: 0 };
        neu.set(rest, haut.start);
        neu.set(lippe, haut.start + rest.length);
        const ohne = gruppen.map(g => (g === haut
            ? { start: g.start, count: rest.length, materialIndex: g.materialIndex }
            : { start: g.start, count: g.count, materialIndex: g.materialIndex }));
        ohne.push({ start: haut.start + rest.length, count: lippe.length,
                    materialIndex: Lippengruppe.LIPPEN });
        return { index: neu, gruppen: ohne, dreiecke: lippe.length / 3 };
    }
}
