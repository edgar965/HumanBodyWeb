/**
 * Stoffkoerper — der Körper für den Stoffschwung: elliptische Kegelkapseln
 * um die Knochen, und das Hinausdrücken der Stoffpunkte.
 *
 * WARUM ELLIPTISCH (19.09.2026, Edgar: „Hose (genesis) animiert nicht"):
 * Ein Schenkel ist kein Kreis — vorn/hinten dicker als seitlich. Eine RUNDE
 * Kapsel steht mit dem 85. Perzentil an der schmalen Seite 3 cm aus der
 * Haut (die Jeans blähte in Daz' Idle 12–19 cm auf), mit dem Median liegt
 * sie an der breiten Seite 2 cm IN der Haut (2,4 % der Jeanspunkte bis
 * 19 mm in der Haut, Stichprobe Ursula). Gemessen mit `__kapselprobe2`:
 *
 *     rund, 85. Perzentil   Abweichung 31 mm   in der Haut 1,8 %, 7 mm
 *     rund, Median           8 mm               2,4 %, 8 mm (max 19)
 *
 * Deshalb je Kapsel zwei Halbachsen quer zum Knochen (`u`, `w = d × u`,
 * Hauptachsen der Hautpunkte, `Kapselmass.ellipse`), je Ende eigene
 * (`rua, rwa` am Kopf, `rub, rwb` am Kind), dazwischen linear. Ein Punkt
 * liegt drin, wenn `(pu/ru)² + (pw/rw)² + (pd/r̄)² < 1` (pd: Anteil über die
 * Enden hinaus, Kugelkappe mit dem Mittelradius); hinaus geht er radial.
 *
 * FLACH FÜR DEN WORKER (13 Zahlen je Kapsel): a(3) b(3) u(3) rua rwa rub rwb.
 * `{a, b, r}` oder `{a, b, ra, rb}` ohne `u` gilt weiter als runde Kapsel
 * (die Tests, und wer die alte Form schickt).
 *
 * Ohne Three.js, damit `test_js_kapselmass` es in Node prüft.
 */
export class Stoffkoerper {

    static JE_KAPSEL = 13;

    /** Die flache Liste des Hauptfadens → `[{a, b, u, rua, rwa, rub, rwb}]`. */
    static lesen(flach) {
        const aus = [], je = Stoffkoerper.JE_KAPSEL;
        for (let k = 0; k + je - 1 < (flach?.length || 0); k += je) {
            aus.push({ a: [flach[k], flach[k + 1], flach[k + 2]], b: [flach[k + 3], flach[k + 4], flach[k + 5]],
                       u: [flach[k + 6], flach[k + 7], flach[k + 8]],
                       rua: flach[k + 9], rwa: flach[k + 10], rub: flach[k + 11], rwb: flach[k + 12] });
        }
        return aus;
    }

    /**
     * Freie Punkte (`frei > 0`) aus allen Kapseln hinausdrücken, auf
     * `abstand` über die Fläche. `x`: Float32Array (n·3), in place.
     */
    static hinaus(x, frei, n, kapseln, abstand) {
        for (const k of kapseln) Stoffkoerper._eine(x, frei, n, k, abstand);
        return x;
    }

    static _eine(x, frei, n, k, abstand) {
        const ax = k.a[0], ay = k.a[1], az = k.a[2];
        let dx = k.b[0] - ax, dy = k.b[1] - ay, dz = k.b[2] - az;
        const laenge = Math.hypot(dx, dy, dz) || 1e-6;
        dx /= laenge; dy /= laenge; dz /= laenge;
        // Querachsen: u aus der Kapsel (rund: irgendeine Senkrechte), w = d × u.
        let ux, uy, uz;
        if (k.u) { [ux, uy, uz] = k.u; }
        else if (Math.abs(dx) < 0.9) { ux = 0; uy = -dz; uz = dy; }
        else { ux = dz; uy = 0; uz = -dx; }
        const ul = Math.hypot(ux, uy, uz) || 1; ux /= ul; uy /= ul; uz /= ul;
        const wx = dy * uz - dz * uy, wy = dz * ux - dx * uz, wz = dx * uy - dy * ux;
        const r = (k.r ?? k.ra), rua = (k.rua ?? k.ra ?? r) + abstand, rwa = (k.rwa ?? k.ra ?? r) + abstand;
        const rub = (k.rub ?? k.rb ?? r) + abstand, rwb = (k.rwb ?? k.rb ?? r) + abstand;
        const r0 = Math.max(rua, rwa, rub, rwb);
        // Grobe Hülle: Achse ± größter Radius.
        const minX = Math.min(ax, k.b[0]) - r0, maxX = Math.max(ax, k.b[0]) + r0;
        const minY = Math.min(ay, k.b[1]) - r0, maxY = Math.max(ay, k.b[1]) + r0;
        const minZ = Math.min(az, k.b[2]) - r0, maxZ = Math.max(az, k.b[2]) + r0;
        for (let i = 0; i < n; i++) {
            if (frei[i] <= 0) continue;
            const o = 3 * i, px = x[o], py = x[o + 1], pz = x[o + 2];
            if (px < minX || px > maxX || py < minY || py > maxY || pz < minZ || pz > maxZ) continue;
            let s = (px - ax) * dx + (py - ay) * dy + (pz - az) * dz;
            const t = s < 0 ? 0 : (s > laenge ? 1 : s / laenge);
            const qx = ax + dx * laenge * t, qy = ay + dy * laenge * t, qz = az + dz * laenge * t;
            const ox = px - qx, oy = py - qy, oz = pz - qz;
            const pu = ox * ux + oy * uy + oz * uz, pw = ox * wx + oy * wy + oz * wz, pd = ox * dx + oy * dy + oz * dz;
            const ru = rua + (rub - rua) * t, rw = rwa + (rwb - rwa) * t, rm = 0.5 * (ru + rw);
            const e = Math.sqrt((pu / ru) ** 2 + (pw / rw) ** 2 + (pd / rm) ** 2);
            if (e >= 1 || e < 1e-6) continue;
            const f = 1 / e;
            x[o] = qx + ox * f; x[o + 1] = qy + oy * f; x[o + 2] = qz + oz * f;
        }
    }
}
