/**
 * Zopfpendel — die Rechnung des Zopfschwungs ohne Three.js, prüfbar in Node.
 *
 * Ein Glied ist ein Knochen mit Länge `laenge` (m) und einer Pendelspitze
 * `tail`/`prev` (Welt, Verlet). Je Bild (VRMC_springBone-1.0, „Update"):
 *
 *     next = tail + (tail − prev)·(1 − drag) + ruhe·stiffness·dt + g·gravity·dt
 *     next = kopf + normalize(next − kopf)·laenge
 *
 * `ruhe` ist die Ruherichtung der Spitze in der Welt (Einheitsvektor), `kopf`
 * der Knochenkopf dieses Bildes. Zurück kommt die neue Richtung (Einheit);
 * die Drehung in Knochenquaternionen macht `genesis9zopfschwung.js`.
 *
 * Vorgabewerte der Spezifikation: stiffness 1,0, dragForce 0,5, gravityPower 0.
 */
export class Zopfpendel {

    static STIFFNESS = 1.0;
    static DRAG = 0.5;
    static GRAVITY_POWER = 0.0;
    static GRAVITY_DIR = [0, -1, 0];

    /** Ein Glied anlegen — die Spitze liegt in Ruhe. */
    static glied(laenge, kopf, ruhe) {
        const tail = [kopf[0] + ruhe[0] * laenge, kopf[1] + ruhe[1] * laenge,
                      kopf[2] + ruhe[2] * laenge];
        return { laenge, tail, prev: tail.slice() };
    }

    /**
     * Ein Bild rechnen; `g.tail`/`g.prev` werden fortgeschrieben.
     * @returns {number[]} die neue Richtung Kopf → Spitze (Einheitsvektor)
     */
    static schritt(g, kopf, ruhe, dt, werte = Zopfpendel) {
        const s = werte.STIFFNESS * dt;
        const gr = werte.GRAVITY_POWER * dt;
        const tr = 1 - werte.DRAG;
        const next = [0, 0, 0];
        for (let i = 0; i < 3; i++) {
            next[i] = g.tail[i] + (g.tail[i] - g.prev[i]) * tr + ruhe[i] * s
                      + werte.GRAVITY_DIR[i] * gr - kopf[i];
        }
        const n = Math.hypot(next[0], next[1], next[2]) || 1;
        const richtung = [next[0] / n, next[1] / n, next[2] / n];
        g.prev = g.tail;
        g.tail = [kopf[0] + richtung[0] * g.laenge, kopf[1] + richtung[1] * g.laenge,
                  kopf[2] + richtung[2] * g.laenge];
        return richtung;
    }

    /** Abstand der Spitze von ihrer Ruhelage (m) — die Auslenkung. */
    static auslenkung(g, kopf, ruhe) {
        return Math.hypot(kopf[0] + ruhe[0] * g.laenge - g.tail[0],
                          kopf[1] + ruhe[1] * g.laenge - g.tail[1],
                          kopf[2] + ruhe[2] * g.laenge - g.tail[2]);
    }
}
