/**
 * Aehnlichkeit — Maßstab und Verschiebung, die Punktmenge p auf q legen.
 *
 * Kleinste Quadrate ohne Drehung, geschlossen: s = Σ(p-p̄)·(q-q̄) / Σ|p-p̄|²,
 * t = q̄ - s·p̄. Herausgelöst aus `rigueberlagerung.js` (12.09.2026), damit die
 * Rechnung in Node prüfbar ist — das Zeichnen hängt an `three` und der
 * Leinwand, die Rechnung an nichts.
 */
export class Aehnlichkeit {
    /** Mit weniger Paaren wird nicht gerechnet. */
    static MINDESTPAARE = 3;

    /**
     * @param {number[][]} p Quellpunkte [[x, y], …]
     * @param {number[][]} q Zielpunkte, gleich lang
     * @returns {{s: number, tx: number, ty: number, paare: number}|null}
     */
    static anpassen(p, q) {
        if (p.length < Aehnlichkeit.MINDESTPAARE || p.length !== q.length) return null;
        const mp = Aehnlichkeit.mittel(p), mq = Aehnlichkeit.mittel(q);
        let zaehler = 0, nenner = 0;
        for (let i = 0; i < p.length; i++) {
            const dx = p[i][0] - mp[0], dy = p[i][1] - mp[1];
            zaehler += dx * (q[i][0] - mq[0]) + dy * (q[i][1] - mq[1]);
            nenner += dx * dx + dy * dy;
        }
        if (nenner <= 0 || zaehler <= 0) return null;
        const s = zaehler / nenner;
        return { s, tx: mq[0] - s * mp[0], ty: mq[1] - s * mp[1], paare: p.length };
    }

    static mittel(liste) {
        const m = [0, 0];
        for (const [x, y] of liste) { m[0] += x; m[1] += y; }
        return [m[0] / liste.length, m[1] / liste.length];
    }

    /** Einen Punkt mit der Anpassung abbilden. */
    static abbilden(fit, x, y) {
        return [fit.s * x + fit.tx, fit.s * y + fit.ty];
    }
}
