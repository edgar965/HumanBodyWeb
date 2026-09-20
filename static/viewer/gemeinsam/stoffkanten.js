/**
 * Stoffkanten — die Längenbedingungen des Stoffschwungs (Position-Based
 * Dynamics, Müller et al. 2007), aus `stoffpendel.js` herausgelöst:
 * Kanten auf ihre Ruhelänge, Biegebedingungen (2-Ring-Abstände, nur bei
 * Stauchung). Die Verschiebung teilt sich nach der Freiheit der beiden
 * Punkte (f = 0 bewegt sich nicht).
 *
 * OHNE `Math.hypot` (20.09.2026): Es läuft je Bild über 150.000 Kanten und
 * 112.000 Biegungen; `Math.hypot` kostet in V8 das Dreifache von
 * `Math.sqrt(x·x + y·y + z·z)` (gemessen: 400.000 Aufrufe 23 ms gegen 8 ms,
 * Schleife inklusive) und rechnet hier nichts, was `sqrt` nicht auch kann —
 * Überlauf gibt es bei Metern nicht.
 */
export class Stoffkanten {

    /** Jede Kante auf ihre Ruhelänge `l` — ein Gauss-Seidel-Durchgang. */
    static halten(x, frei, kanten) {
        const { a, b, l } = kanten;
        for (let e = 0; e < a.length; e++) {
            const wi = frei[a[e]], wj = frei[b[e]], summe = wi + wj;
            if (summe <= 0) continue;
            const i = 3 * a[e], j = 3 * b[e];
            const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2];
            const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (len < 1e-9) continue;
            const diff = (len - l[e]) / len;
            const ki = diff * wi / summe, kj = diff * wj / summe;
            x[i] += dx * ki; x[i + 1] += dy * ki; x[i + 2] += dz * ki;
            x[j] -= dx * kj; x[j + 1] -= dy * kj; x[j + 2] -= dz * kj;
        }
    }

    /** Gestauchte Biegebedingungen (`Stoffanker.biegung`) um `anteil` ausgleichen. */
    static biegen(x, frei, biegung, anteil) {
        if (!(anteil > 0) || !biegung) return;
        const { a, b, l } = biegung;
        for (let e = 0; e < a.length; e++) {
            const wi = frei[a[e]], wj = frei[b[e]], summe = wi + wj;
            if (summe <= 0) continue;
            const i = 3 * a[e], j = 3 * b[e];
            const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2];
            const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (len < 1e-9 || len >= l[e]) continue;
            const diff = anteil * (len - l[e]) / len;
            const ki = diff * wi / summe, kj = diff * wj / summe;
            x[i] += dx * ki; x[i + 1] += dy * ki; x[i + 2] += dz * ki;
            x[j] -= dx * kj; x[j + 1] -= dy * kj; x[j + 2] -= dz * kj;
        }
    }
}
