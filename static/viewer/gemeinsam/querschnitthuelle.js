/**
 * Querschnitthuelle — konvexe Hülle eines waagrechten Querschnitts und ihr Halbmesser je Richtung (Stufe K2a, 25.10.2026; für `Eigenkleidbruecke`).
 *
 * `scheibe` nimmt die Punkte einer Scheibe (x, z relativ zur Mitte), bildet die Hülle (Andrews monotone Kette) und schreibt je Strahl (0 = vorn, +z) zwei Werte:
 * wie weit der Strahl bis zur Hülle reicht (`halbmesser`) und wie weit der Treffpunkt vom nächsten Eckpunkt der Hülle entfernt ist (`stuetze`) — Eckpunkte sind
 * Hautpunkte, auf denen der Stoff aufliegt; über einer Kante spannt er. Ohne Three.js, in Node prüfbar.
 */
export class Querschnitthuelle {

    /** `pkt` [[x, z]] → Ecken gegen den Uhrzeigersinn. */
    static huelle(pkt) {
        const p = [...pkt].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
        const kreuz = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
        const unten = [], oben = [];
        for (const q of p) { while (unten.length >= 2 && kreuz(unten[unten.length - 2], unten[unten.length - 1], q) <= 0) unten.pop(); unten.push(q); }
        for (let i = p.length - 1; i >= 0; i--) {
            const q = p[i];
            while (oben.length >= 2 && kreuz(oben[oben.length - 2], oben[oben.length - 1], q) <= 0) oben.pop();
            oben.push(q);
        }
        return unten.slice(0, -1).concat(oben.slice(0, -1));
    }

    /** Strahl t·(dx, dz) vom Ursprung → `[t, Abstand des Treffpunkts zum nächsten Eckpunkt]` (größtes t über alle Kanten). */
    static strahl(h, dx, dz) {
        let best = 0, stuetze = 0;
        for (let i = 0; i < h.length; i++) {
            const a = h[i], b = h[(i + 1) % h.length], ex = b[0] - a[0], ez = b[1] - a[1];
            const nenner = dx * ez - dz * ex;
            if (Math.abs(nenner) < 1e-12) continue;
            const t = (a[0] * ez - a[1] * ex) / nenner, u = (a[0] * dz - a[1] * dx) / nenner;
            if (u >= -1e-6 && u <= 1 + 1e-6 && t > best) {
                best = t;
                stuetze = Math.min(Math.max(u, 0), Math.max(1 - u, 0)) * Math.hypot(ex, ez);
            }
        }
        return [best, stuetze];
    }

    /** Eine Scheibe: `halbmesser[k]`, `stuetze[k]` für `halbmesser.length` Strahlen; weniger als drei Punkte: nichts (0). */
    static scheibe(pkt, halbmesser, stuetze) {
        if (pkt.length < 3) return;
        const h = Querschnitthuelle.huelle(pkt);
        for (let k = 0; k < halbmesser.length; k++) {
            const phi = 2 * Math.PI * k / halbmesser.length;
            [halbmesser[k], stuetze[k]] = Querschnitthuelle.strahl(h, Math.sin(phi), Math.cos(phi));
        }
    }
}
