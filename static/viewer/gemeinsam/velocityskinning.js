/**
 * Velocity Skinning — die vier Verformungsformeln, in JavaScript.
 *
 * Zweite Fassung derselben Rechnung wie `VelocitySkinning_Python/verformung.py`
 * (Rohmer et al., EG 2021, `skinning.cpp` Zeile 26–105). Zwei Fassungen
 * laufen irgendwann auseinander; deshalb prüft `test_js_velocityskinning.py`
 * beide gegen DIESELBEN Zahlen (`fixture.json`, aus Python erzeugt) auf 1e-9.
 *
 * Ohne DOM, ohne Three.js: reine Zahlenarbeit auf Float64Array, damit sie in
 * Node läuft. Die Einbindung in die Szene steht in `scene/weichgewebe.js`.
 *
 * Alle vier sind GESCHLOSSENE Ausdrücke — kein Löser, kein Zeitschritt.
 * Die Verschiebung folgt allein aus der Geschwindigkeit; nichts kann
 * divergieren.
 */
export class Velocityskinning {
    /** `skinning.hpp` Zeile 89 — der Deckel des Drehwinkels. */
    static HOECHSTWINKEL = Math.PI / 6;

    // ------------------------------------------------------- Vektorhelfer

    static norm(v) { return Math.hypot(v[0], v[1], v[2]); }

    static kreuz(a, b) {
        return [a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0]];
    }

    static skalar(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

    static einheit(v) {
        const n = Math.max(Velocityskinning.norm(v), 1e-12);
        return [v[0] / n, v[1] / n, v[2] / n];
    }

    /** `rotation_from_axis_angle_mat3` — 3x3 als flaches Feld, zeilenweise. */
    static drehung(achse, winkel) {
        const [x, y, z] = Velocityskinning.einheit(achse);
        const c = Math.cos(winkel), s = Math.sin(winkel), t = 1 - c;
        return [
            c + x * x * t, x * y * t - z * s, x * z * t + y * s,
            y * x * t + z * s, c + y * y * t, y * z * t - x * s,
            z * x * t - y * s, z * y * t + x * s, c + z * z * t,
        ];
    }

    /** `rotation_between_vector_mat3`. */
    static drehungZwischen(a, b) {
        const u0 = Velocityskinning.einheit(a);
        const u1 = Velocityskinning.einheit(b);
        const diff = Math.hypot(u0[0] - u1[0], u0[1] - u1[1], u0[2] - u1[2]);
        if (diff < 1e-4) return [1, 0, 0, 0, 1, 0, 0, 0, 1];
        const summe = Math.hypot(u0[0] + u1[0], u0[1] + u1[1], u0[2] + u1[2]);
        if (summe < 1e-4) return [-1, 0, 0, 0, -1, 0, 0, 0, -1];
        const d = Math.max(-1, Math.min(1, Velocityskinning.skalar(u0, u1)));
        return Velocityskinning.drehung(Velocityskinning.kreuz(u0, u1),
                                        Math.acos(d));
    }

    static matVek(m, v) {
        return [m[0] * v[0] + m[1] * v[1] + m[2] * v[2],
                m[3] * v[0] + m[4] * v[1] + m[5] * v[2],
                m[6] * v[0] + m[7] * v[1] + m[8] * v[2]];
    }

    // ------------------------------------------------------- linear, floppy

    /** `deformation_flappy_linear_speed`: der Punkt bleibt zurück. */
    static flappyLinear(w, tempo, aus, i) {
        aus[3 * i] = -w * tempo[0];
        aus[3 * i + 1] = -w * tempo[1];
        aus[3 * i + 2] = -w * tempo[2];
    }

    // ------------------------------------------------------ linear, squashy

    /**
     * `deformation_squashy_linear_speed`: strecken entlang der Bewegung,
     * stauchen quer dazu. Gibt die Matrix `T - I` zurück, die je Punkt auf
     * `(p - mitte)` anzuwenden ist — einmal je Knochen, nicht je Punkt.
     */
    static squashyLinearMatrix(wSquashy, tempo) {
        const betrag = Velocityskinning.norm(tempo);
        const faktor = wSquashy * betrag;
        const streckung = 1 + faktor;
        const stauchung = 1 / Math.sqrt(1 + faktor);
        const r = Velocityskinning.drehungZwischen([1, 0, 0], tempo);
        // T = R S R^T mit S = diag(streckung, stauchung, stauchung);
        // T - I = (streckung - stauchung) * r0 r0^T + (stauchung - 1) * I,
        // weil die zweite und dritte Achse gleich gestaucht werden — es
        // zählt nur die erste Spalte r0 = (r[0], r[3], r[6]).
        const r0 = [r[0], r[3], r[6]];
        const a = streckung - stauchung, b = stauchung - 1;
        return [
            a * r0[0] * r0[0] + b, a * r0[0] * r0[1], a * r0[0] * r0[2],
            a * r0[1] * r0[0], a * r0[1] * r0[1] + b, a * r0[1] * r0[2],
            a * r0[2] * r0[0], a * r0[2] * r0[1], a * r0[2] * r0[2] + b,
        ];
    }

    static squashyLinear(wSquashy, tempo, punkte, mitte, aus, i) {
        const m = Velocityskinning.squashyLinearMatrix(wSquashy, tempo);
        const d = Velocityskinning.matVek(m, [punkte[3 * i] - mitte[0],
                                              punkte[3 * i + 1] - mitte[1],
                                              punkte[3 * i + 2] - mitte[2]]);
        aus[3 * i] = d[0]; aus[3 * i + 1] = d[1]; aus[3 * i + 2] = d[2];
    }

    // ----------------------------------------------------- Drehung, floppy

    /**
     * `deformation_flappy_rotation_speed`: der Punkt hinkt der Drehung um
     * die Achse hinterher. Drehmittelpunkt ist die Projektion auf die
     * Achse — mathematisch gleichwertig zum Gelenk, weil `(R-I)` einen
     * achsparallelen Vektor nicht bewegt (nachgerechnet 11.09.2026).
     */
    static flappyRotation(w, punkte, gelenk, achse, punkttempo, aus, i) {
        const rel = [punkte[3 * i] - gelenk[0], punkte[3 * i + 1] - gelenk[1],
                     punkte[3 * i + 2] - gelenk[2]];
        let winkel = punkttempo * w;
        const max = Velocityskinning.HOECHSTWINKEL;
        if (winkel > max) {
            // Weich gedeckelt, nicht hart (`skinning.cpp` 58–60): der Rest
            // wird durch das Tempo geteilt. Schranke ist max + w.
            winkel = max + (winkel - max) / Math.max(punkttempo, 1e-9);
        }
        // Rodrigues für (R - I) * rel mit Winkel -winkel:
        //   (c-1) rel + s (u x rel) + (1-c) (u . rel) u
        const u = Velocityskinning.einheit(achse);
        const c = Math.cos(-winkel), s = Math.sin(-winkel);
        const k = Velocityskinning.kreuz(u, rel);
        const sk = Velocityskinning.skalar(rel, u);
        aus[3 * i] = (c - 1) * rel[0] + s * k[0] + (1 - c) * sk * u[0];
        aus[3 * i + 1] = (c - 1) * rel[1] + s * k[1] + (1 - c) * sk * u[1];
        aus[3 * i + 2] = (c - 1) * rel[2] + s * k[2] + (1 - c) * sk * u[2];
    }

    // ---------------------------------------------------- Drehung, squashy

    /**
     * Das Achsenkreuz für `deformation_squashy_rotation_speed` — einmal je
     * Knochen. `null`, wenn sich das Glied um seine eigene Längsachse
     * dreht (dann gibt es keine Querrichtung; Original: Zeile 84).
     */
    static squashyRotationAchsen(medial, achse) {
        const laengsRoh = Velocityskinning.kreuz(medial, achse);
        if (Velocityskinning.norm(laengsRoh) < 1e-2) return null;
        const laengs = Velocityskinning.einheit(laengsRoh);
        const quer = Velocityskinning.kreuz(medial, laengs);
        return { laengs, quer, medial };
    }

    static squashyRotation(wSquashy, punkte, gelenk, medial, achse, punkttempo,
                           aus, i) {
        const kreuz = Velocityskinning.squashyRotationAchsen(medial, achse);
        if (!kreuz) { aus[3 * i] = 0; aus[3 * i + 1] = 0; aus[3 * i + 2] = 0; return; }
        Velocityskinning.squashyRotationMit(kreuz, wSquashy, punkte, gelenk,
                                            punkttempo, aus, i);
    }

    static squashyRotationMit(kreuz, wSquashy, punkte, gelenk, punkttempo,
                              aus, i) {
        const { laengs, quer, medial } = kreuz;
        const rel = [punkte[3 * i] - gelenk[0], punkte[3 * i + 1] - gelenk[1],
                     punkte[3 * i + 2] - gelenk[2]];
        // Bezugspunkt: Projektion auf die Gliedachse — der Rest steht
        // senkrecht darauf, die dritte Spalte trägt nie bei.
        const entlang = Velocityskinning.skalar(rel, medial);
        const v = [rel[0] - entlang * medial[0], rel[1] - entlang * medial[1],
                   rel[2] - entlang * medial[2]];
        const faktor = wSquashy * punkttempo;
        const l = Velocityskinning.skalar(v, laengs) * faktor;
        const q = Velocityskinning.skalar(v, quer) * (-faktor / (1 + faktor));
        aus[3 * i] = l * laengs[0] + q * quer[0];
        aus[3 * i + 1] = l * laengs[1] + q * quer[1];
        aus[3 * i + 2] = l * laengs[2] + q * quer[2];
    }
}
