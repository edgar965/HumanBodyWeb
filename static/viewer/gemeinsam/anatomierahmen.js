/**
 * Anatomierahmen — die Tangentenrahmen zweier Flächen ineinander umrechnen (11.10.2026, für die Normalenkarte von `Anatomiebild`).
 *
 * Eine Normalenkarte ist auf ihre UV bezogen: three.js bildet im Fragment-Shader aus Lage und UV den Rahmen `[∇u, ∇v, N]` (`getTangentFrame`,
 * „Cotangent frame": die Gradienten von u und v in der Fläche, beide durch die längere der beiden geteilt) und rechnet den Karteneintrag mit ihm in
 * den Raum. Die Karte der Haut gehört zur UV der Haut, die neue Karte des Stücks zu seiner Atlas-UV — beide Rahmen stehen an derselben Stelle
 * verschieden. Ein Karteneintrag wird deshalb vom Rahmen der Haut in den des Stücks umgerechnet: `n' = M_stück⁻¹ · M_haut · n`. Ohne das sind
 * die Poren im falschen Winkel beleuchtet (Rotation um die Normale, bei gespiegelter UV auch eine Spiegelung).
 *
 * Matrizen sind `Float64Array` zeilenweise (`m[3 · zeile + spalte]`), die Spalten sind `∇u`, `∇v`, `N`.
 */
export class Anatomierahmen {

    /**
     * Der Rahmen des Dreiecks `a b c` (Punktnummern in `pos`, `uv`, `normal`) nach `aus` ab `o`. `normal` darf fehlen (dann die Flächennormale).
     * @returns false bei einem entarteten Dreieck (Fläche 0 oder UV ohne Ausdehnung); `aus` bleibt dann unberührt
     */
    static rahmen(pos, uv, normal, a, b, c, aus, o = 0) {
        const e1 = [0, 1, 2].map(k => pos[3 * b + k] - pos[3 * a + k]), e2 = [0, 1, 2].map(k => pos[3 * c + k] - pos[3 * a + k]);
        const punkt = (u, w) => u[0] * w[0] + u[1] * w[1] + u[2] * w[2];
        const g11 = punkt(e1, e1), g12 = punkt(e1, e2), g22 = punkt(e2, e2), det = g11 * g22 - g12 * g12;
        if (!(det > 1e-30)) return false;
        const d1 = [0, 1, 2].map(k => (g22 * e1[k] - g12 * e2[k]) / det), d2 = [0, 1, 2].map(k => (g11 * e2[k] - g12 * e1[k]) / det);   // duale Basis
        const gu = [0, 1, 2].map(k => (uv[2 * b] - uv[2 * a]) * d1[k] + (uv[2 * c] - uv[2 * a]) * d2[k]);
        const gv = [0, 1, 2].map(k => (uv[2 * b + 1] - uv[2 * a + 1]) * d1[k] + (uv[2 * c + 1] - uv[2 * a + 1]) * d2[k]);
        let n = normal ? [0, 1, 2].map(k => normal[3 * a + k] + normal[3 * b + k] + normal[3 * c + k])
            : [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]];
        const nl = Math.sqrt(punkt(n, n));
        if (!(nl > 1e-12)) return false;
        n = n.map(w => w / nl);
        const t = gu.map((w, k) => w - punkt(gu, n) * n[k]), bb = gv.map((w, k) => w - punkt(gv, n) * n[k]);
        const lang = Math.max(punkt(t, t), punkt(bb, bb));
        if (!(lang > 1e-30)) return false;
        const s = 1 / Math.sqrt(lang);
        for (let k = 0; k < 3; k++) { aus[o + 3 * k] = t[k] * s; aus[o + 3 * k + 1] = bb[k] * s; aus[o + 3 * k + 2] = n[k]; }
        return true;
    }

    /** Die Einheitsmatrix nach `aus` ab `o` (für entartete Dreiecke: der Karteneintrag bleibt, wie er ist). */
    static eins(aus, o = 0) {
        aus.fill(0, o, o + 9);
        aus[o] = aus[o + 4] = aus[o + 8] = 1;
    }

    /** Die Umkehrmatrix von `m` (ab `o`) nach `aus` (ab `p`); false, wenn sie nicht umkehrbar ist. */
    static invers(m, o, aus, p = 0) {
        const [a, b, c, d, e, f, g, h, i] = Array.from(m.subarray(o, o + 9));
        const k0 = e * i - f * h, k1 = f * g - d * i, k2 = d * h - e * g, det = a * k0 + b * k1 + c * k2;
        if (!(Math.abs(det) > 1e-18)) return false;
        const r = 1 / det;
        aus[p] = k0 * r; aus[p + 1] = (c * h - b * i) * r; aus[p + 2] = (b * f - c * e) * r;
        aus[p + 3] = k1 * r; aus[p + 4] = (a * i - c * g) * r; aus[p + 5] = (c * d - a * f) * r;
        aus[p + 6] = k2 * r; aus[p + 7] = (b * g - a * h) * r; aus[p + 8] = (a * e - b * d) * r;
        return true;
    }

    /** `a · b` für zwei 3×3-Matrizen (ab `p` und `q`) nach `aus` (ab 0). */
    static mal(a, p, b, q, aus) {
        for (let z = 0; z < 3; z++) for (let s = 0; s < 3; s++) {
            aus[3 * z + s] = a[p + 3 * z] * b[q + s] + a[p + 3 * z + 1] * b[q + 3 + s] + a[p + 3 * z + 2] * b[q + 6 + s];
        }
        return aus;
    }
}
