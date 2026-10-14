/**
 * Mesh3dnetzinseln — die zusammenhängenden Teile („Inseln“) eines Netzes im Browser (13.10.2026, „Netz bearbeiten“).
 *
 * Dieselbe Rechnung wie `Mesh3dnetzkatalog.teile` auf dem Server (Konzept `Docu/konzepte/2026-10-13_mesh-3d-netz-ausschneiden-konzept.md`): Flächen, die sich eine KANTE teilen, gehören zusammen; Punkte gleicher Lage
 * (UV-Nahtkopien einer GLB) zählen als ein Punkt. Der Browser rechnet sie auf dem Netz, das er zeigt (bei großen Netzen die vereinfachte Kopie) — für die Färbung und die Liste. Maßgeblich für das, was geschnitten
 * wird, ist die Rechnung des Servers auf dem Original; die Zahlen beider stehen in der Leiste nebeneinander.
 *
 * Teil 0 ist der größte.
 */
export class Mesh3dnetzinseln {
    /** Punkte, die näher als dieser Anteil der Kastendiagonale liegen, sind derselbe Punkt (wie `Mesh3dnetzkatalog.RUNDEN`). */
    static RUNDEN = 5e-5;

    /**
     * @param {THREE.BufferGeometry} geometrie Dreiecke mit Position (mit oder ohne Index)
     * @returns {{flaechen: number, insel: Int32Array, groessen: Int32Array, erste: Int32Array}} `insel[f]` = Nummer des Teils; `erste[n]` = eine Fläche des Teils n
     */
    static zerlegen(geometrie) {
        const pos = geometrie.attributes.position;
        const index = geometrie.index ? geometrie.index.array : null;
        const flaechen = index ? index.length / 3 : pos.count / 3;
        const ecke = (f, k) => (index ? index[f * 3 + k] : f * 3 + k);
        geometrie.computeBoundingBox();
        const kasten = geometrie.boundingBox;
        const schritt = (kasten.min.distanceTo(kasten.max) || 1) * Mesh3dnetzinseln.RUNDEN;
        const punkt = new Int32Array(pos.count);
        const bekannt = new Map();
        for (let i = 0; i < pos.count; i++) {
            const schluessel = `${Math.round(pos.getX(i) / schritt)}/${Math.round(pos.getY(i) / schritt)}/${Math.round(pos.getZ(i) / schritt)}`;
            let nr = bekannt.get(schluessel);
            if (nr === undefined) { nr = bekannt.size; bekannt.set(schluessel, nr); }
            punkt[i] = nr;
        }
        const eltern = new Int32Array(flaechen);
        for (let f = 0; f < flaechen; f++) eltern[f] = f;
        const wurzel = f => { while (eltern[f] !== f) { eltern[f] = eltern[eltern[f]]; f = eltern[f]; } return f; };
        const kanten = new Map();
        const n = bekannt.size;
        for (let f = 0; f < flaechen; f++) {
            for (let k = 0; k < 3; k++) {
                const a = punkt[ecke(f, k)], b = punkt[ecke(f, (k + 1) % 3)];
                const schluessel = a < b ? a * n + b : b * n + a;
                const andere = kanten.get(schluessel);
                if (andere === undefined) kanten.set(schluessel, f);
                else {
                    const x = wurzel(f), y = wurzel(andere);
                    if (x !== y) eltern[x] = y;
                }
            }
        }
        const marke = new Int32Array(flaechen);
        const zaehler = new Map();
        for (let f = 0; f < flaechen; f++) { marke[f] = wurzel(f); zaehler.set(marke[f], (zaehler.get(marke[f]) || 0) + 1); }
        const reihenfolge = [...zaehler.entries()].sort((p, q) => q[1] - p[1] || p[0] - q[0]);
        const nummer = new Map(reihenfolge.map(([w], i) => [w, i]));
        const insel = new Int32Array(flaechen);
        const groessen = new Int32Array(reihenfolge.length);
        const erste = new Int32Array(reihenfolge.length).fill(-1);
        for (let f = 0; f < flaechen; f++) {
            const i = nummer.get(marke[f]);
            insel[f] = i;
            groessen[i]++;
            if (erste[i] < 0) erste[i] = f;
        }
        return { flaechen, insel, groessen, erste };
    }
}
