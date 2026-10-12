/**
 * Dreiecksabstand — der nächste Punkt eines Dreiecks zu einem Punkt (11.10.2026, für `Anatomiezuordnung`).
 *
 * Ericson, Real-Time Collision Detection, 5.1.5 (ClosestPtPointTriangle). Ohne Zwischenobjekte: die Zuordnung ruft es für jedes Texel
 * der Karte des Stücks etwa zwanzigmal auf.
 */
export class Dreiecksabstand {

    /**
     * Abstand² von `p` zum Dreieck `a b c` und die Schwerpunktkoordinaten des nächsten Punkts.
     * `aus[0]` = Abstand², `aus[1]` = Gewicht von b, `aus[2]` = Gewicht von c (das von a ist 1 − aus[1] − aus[2]).
     */
    static naechster(px, py, pz, ax, ay, az, bx, by, bz, cx, cy, cz, aus) {
        const abx = bx - ax, aby = by - ay, abz = bz - az, acx = cx - ax, acy = cy - ay, acz = cz - az;
        const apx = px - ax, apy = py - ay, apz = pz - az;
        const bpx = px - bx, bpy = py - by, bpz = pz - bz, cpx = px - cx, cpy = py - cy, cpz = pz - cz;
        const d1 = abx * apx + aby * apy + abz * apz, d2 = acx * apx + acy * apy + acz * apz;
        const d3 = abx * bpx + aby * bpy + abz * bpz, d4 = acx * bpx + acy * bpy + acz * bpz;
        const d5 = abx * cpx + aby * cpy + abz * cpz, d6 = acx * cpx + acy * cpy + acz * cpz;
        const vc = d1 * d4 - d3 * d2, vb = d5 * d2 - d1 * d6, va = d3 * d6 - d5 * d4;
        let v = 0, w = 0;
        if (d1 <= 0 && d2 <= 0) { v = 0; w = 0; }
        else if (d3 >= 0 && d4 <= d3) { v = 1; w = 0; }
        else if (vc <= 0 && d1 >= 0 && d3 <= 0) { v = d1 / (d1 - d3); w = 0; }
        else if (d6 >= 0 && d5 <= d6) { v = 0; w = 1; }
        else if (vb <= 0 && d2 >= 0 && d6 <= 0) { v = 0; w = d2 / (d2 - d6); }
        else if (va <= 0 && (d4 - d3) >= 0 && (d5 - d6) >= 0) { w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); v = 1 - w; }
        else {
            const summe = va + vb + vc;
            if (summe === 0) { v = 0; w = 0; }                     // zu einer Linie entartetes Dreieck: Ecke a
            else { v = vb / summe; w = vc / summe; }
        }
        const dx = apx - v * abx - w * acx, dy = apy - v * aby - w * acy, dz = apz - v * abz - w * acz;
        aus[0] = dx * dx + dy * dy + dz * dz;
        aus[1] = v;
        aus[2] = w;
        return aus;
    }
}
