/**
 * Strahldreieck — wo ein Strahl (in beide Richtungen) ein Dreieck trifft (11.10.2026, für `Anatomiezuordnung`).
 *
 * Möller–Trumbore. Gebraucht, weil der NÄCHSTE Punkt der Haut auf einer Fläche aus ebenen Facetten an den Kanten und Ecken hängenbleibt: Texel
 * des Stücks, die über einer Kante liegen, bekamen alle dieselbe Stelle und damit dieselbe Farbe und Normale — Blöcke aus ein paar Texeln in der
 * Karte (im Chrome gesehen, 11.10.2026). Der Strahl entlang der Normale des Stücks trifft das Dreieck, durch das er geht, und wandert stetig
 * von einem zum nächsten.
 */
export class Strahldreieck {

    /** Wie weit (Anteil des Dreiecks) ein Treffer außerhalb der Kanten noch gilt. */
    static RAND = 1e-4;
    /** Ab diesem |cos| zwischen Strahl und Dreiecksnormale gilt ein Treffer (flacher: der nächste Punkt ist verlässlicher). */
    static MIN_COS = 0.5;

    /**
     * Schnitt des Strahls `p + t · n` (n Einheitsvektor, t in beide Richtungen) mit dem Dreieck `a b c`.
     * `aus[0]` = |t|, `aus[1]` = Gewicht von b, `aus[2]` = Gewicht von c (das von a ist 1 − aus[1] − aus[2]).
     * @returns true, wenn der Strahl das Dreieck trifft und nicht zu flach darauf steht
     */
    static trifft(px, py, pz, nx, ny, nz, ax, ay, az, bx, by, bz, cx, cy, cz, aus) {
        const e1x = bx - ax, e1y = by - ay, e1z = bz - az, e2x = cx - ax, e2y = cy - ay, e2z = cz - az;
        const hx = ny * e2z - nz * e2y, hy = nz * e2x - nx * e2z, hz = nx * e2y - ny * e2x;
        const det = e1x * hx + e1y * hy + e1z * hz;
        const fx = e1y * e2z - e1z * e2y, fy = e1z * e2x - e1x * e2z, fz = e1x * e2y - e1y * e2x;
        const flaeche = Math.sqrt(fx * fx + fy * fy + fz * fz);
        if (!(flaeche > 1e-18) || Math.abs(det) / flaeche < Strahldreieck.MIN_COS) return false;      // |det| = |n · (e1 × e2)|, geteilt durch die Fläche (|e1 × e2|) ist der |cos| zwischen Strahl und Dreiecksnormale
        const inv = 1 / det, sx = px - ax, sy = py - ay, sz = pz - az;
        const u = (sx * hx + sy * hy + sz * hz) * inv;
        const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x;
        const v = (nx * qx + ny * qy + nz * qz) * inv;
        const r = Strahldreieck.RAND;
        if (u < -r || v < -r || u + v > 1 + r) return false;
        aus[0] = Math.abs((e2x * qx + e2y * qy + e2z * qz) * inv);
        aus[1] = Math.min(1, Math.max(0, u));
        aus[2] = Math.min(1, Math.max(0, v));
        return true;
    }
}
