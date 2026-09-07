/**
 * Ruhematrix — die Ruhelage einer Knochenkette, in ihrer EIGENEN Gruppe.
 *
 * WARUM (Edgar, 07.09.2026: „bei SMPL verschwinden die Kleider beim
 * Abspielen einer Animation"): `THREE.Skeleton` rechnet seine
 * `boneInverses` aus `bone.matrixWorld` — also aus der Lage, in der die
 * Figur GERADE steht. Der Körper wird gebunden, während sie noch im
 * Ursprung ist; ein GarmentCode-Stück 16 Sekunden später, wenn sie längst
 * 90 cm weiter steht. Dann liegen `bindMatrix` und `boneInverses` in
 * verschiedenen Bezugssystemen, und der Gruppenversatz wird doppelt
 * verrechnet: Der Körper bewegte sich sauber, das Kleidungsstück zerriss in
 * meterlange Zacken (gemessen: Stoffpunkte wanderten bis 1,92 m). Kein
 * Fehler, keine Meldung.
 *
 * Deshalb wird die Ruhelage hier aus dem Bauplan gerechnet — Elternmatrix ×
 * eigene Matrix, von der Wurzel abwärts — und hängt an nichts, was sich
 * später bewegt.
 *
 * OHNE THREE.JS, damit die Rechnung prüfbar ist (wie `knochenkette.js` und
 * `greifrechnung.js`). Matrizen sind flache Felder mit 16 Zahlen in
 * SPALTENfolge — dieselbe Ordnung wie `THREE.Matrix4.elements`, damit
 * `fromArray` sie ohne Umsortieren nimmt. Wer hier zeilenweise rechnet,
 * bekommt eine transponierte Drehung: Die Figur steht dann verdreht da, und
 * es sieht aus wie ein Fehler im Retarget.
 */
export class Ruhematrix {

    /** Die Einheitsmatrix. */
    static einheit() {
        return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
    }

    /**
     * Lage und Drehung zu einer Matrix (Spaltenfolge).
     *
     * @param pos  [x, y, z]
     * @param quat [x, y, z, w] — fehlt sie, gilt keine Drehung
     */
    static aus(pos, quat) {
        const [x, y, z, w] = Array.isArray(quat) ? quat : [0, 0, 0, 1];
        const x2 = x + x, y2 = y + y, z2 = z + z;
        const xx = x * x2, xy = x * y2, xz = x * z2;
        const yy = y * y2, yz = y * z2, zz = z * z2;
        const wx = w * x2, wy = w * y2, wz = w * z2;
        const [px, py, pz] = Array.isArray(pos) ? pos : [0, 0, 0];
        return [
            1 - (yy + zz), xy + wz, xz - wy, 0,
            xy - wz, 1 - (xx + zz), yz + wx, 0,
            xz + wy, yz - wx, 1 - (xx + yy), 0,
            px, py, pz, 1,
        ];
    }

    /** `a × b` — erst `b`, dann `a` (wie `THREE.Matrix4.multiplyMatrices`). */
    static mal(a, b) {
        const aus = new Array(16);
        for (let s = 0; s < 4; s++) {
            for (let z = 0; z < 4; z++) {
                let summe = 0;
                for (let k = 0; k < 4; k++) summe += a[k * 4 + z] * b[s * 4 + k];
                aus[s * 4 + z] = summe;
            }
        }
        return aus;
    }

    /**
     * Je Knochen seine Ruhematrix in der Lage der FIGURGRUPPE.
     *
     * @param plan [{name, eltern, pos, quat}] — Eltern vor ihren Kindern
     *             (`Knochenkette.bauplan` sortiert so)
     * @returns Map name -> Matrix (16 Zahlen)
     */
    static kette(plan) {
        const aus = new Map();
        for (const eintrag of plan || []) {
            const eigen = Ruhematrix.aus(eintrag.pos, eintrag.quat);
            const eltern = eintrag.eltern ? aus.get(eintrag.eltern) : null;
            aus.set(eintrag.name, eltern ? Ruhematrix.mal(eltern, eigen) : eigen);
        }
        return aus;
    }

    /** Wo ein Knochen in dieser Ruhelage steht: die Verschiebung der Matrix. */
    static punkt(matrix) {
        return [matrix[12], matrix[13], matrix[14]];
    }
}
