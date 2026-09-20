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
 * DIE KAPSEL VON VORHIN ENTSCHEIDET DIE SEITE (20.09.2026, Edgar: „bei der
 * Jump animation verliert die Person das Kleid!!"): Zieht ein Bein in einem
 * Bild 10 cm an, fegt seine Kapsel durch den Rock. Radial hinausgedrückt
 * landet ein Punkt, der VOR dem Schenkel lag, auf dessen Rückseite — die
 * Kante zum Nachbarn spannt dann quer durchs Bein. Deshalb bekommt jeder
 * Durchgang auch die Kapseln des vorigen Schritts (`alt`) und die alte Lage
 * des Punkts (`xAlt`): Ist die Achse in ihrer Bewegungsrichtung über den
 * Punkt hinweg, kommt er in der Richtung heraus, die er vorhin zur Kapsel
 * hatte — in deren Achsenraum (pu, pw, pd), auf die Fläche der NEUEN Kapsel
 * gesetzt. Sonst radial, damit er an der Fläche entlanggleiten kann.
 *
 * RASTER STATT „JEDE KAPSEL GEGEN JEDEN PUNKT" (20.09.2026, Browser, Ursula im
 * Kleid: 22 Kapseln × 19k Käfigpunkte × 2 Durchgänge je Teilschritt = 6 ms je
 * Durchgang, fast alles Hüllentests, die nichts treffen): Je Durchgang werden
 * die Hüllen der Kapseln in Zellen von `RASTER` eingetragen, und jeder Punkt
 * prüft nur die Kapseln seiner Zelle - in derselben Reihenfolge wie vorher,
 * das Ergebnis ist dasselbe. Ein Punkt fern aller Kapseln kostet einen Blick.
 *
 * FLACH FÜR DEN WORKER (13 Zahlen je Kapsel): a(3) b(3) u(3) rua rwa rub rwb.
 * `{a, b, r}` oder `{a, b, ra, rb}` ohne `u` gilt weiter als runde Kapsel
 * (die Tests, und wer die alte Form schickt).
 *
 * Ohne Three.js, damit `test_js_kapselmass` es in Node prüft.
 */
export class Stoffkoerper {

    static JE_KAPSEL = 13;
    /** Zellweite (m) des Rasters über die Kapselhüllen. */
    static RASTER = 0.1;

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
     * `alt`: die Kapseln des vorigen Schritts (gleiche Reihenfolge) und
     * `xAlt` die Lage der Punkte davor — dann entscheidet die Seite von vorhin.
     */
    static hinaus(x, frei, n, kapseln, abstand, alt = null, xAlt = null) {
        if (!kapseln.length) return x;
        const mitAlt = alt && xAlt && alt.length === kapseln.length;
        const R = kapseln.map(k => Stoffkoerper._rahmen(k, abstand));
        const A = mitAlt ? alt.map(k => Stoffkoerper._rahmen(k, abstand)) : null;
        const zellen = Stoffkoerper._zellen(R), w = Stoffkoerper.RASTER;
        for (let i = 0; i < n; i++) {
            if (frei[i] <= 0) continue;
            const o = 3 * i;
            const liste = zellen.get(Stoffkoerper._schluessel(Math.floor(x[o] / w), Math.floor(x[o + 1] / w),
                                                             Math.floor(x[o + 2] / w)));
            if (!liste) continue;
            for (let j = 0; j < liste.length; j++) {
                const k = liste[j];
                Stoffkoerper._eine(x, o, R[k], A ? A[k] : null, xAlt);
            }
        }
        return x;
    }

    /** Je Rasterzelle die Kapseln (Indizes, aufsteigend), deren Hülle sie schneidet. */
    static _zellen(R) {
        const zellen = new Map(), w = Stoffkoerper.RASTER;
        for (let k = 0; k < R.length; k++) {
            const r = R[k];
            const x0 = Math.floor(r.minX / w), x1 = Math.floor(r.maxX / w), y0 = Math.floor(r.minY / w);
            const y1 = Math.floor(r.maxY / w), z0 = Math.floor(r.minZ / w), z1 = Math.floor(r.maxZ / w);
            for (let ix = x0; ix <= x1; ix++) for (let iy = y0; iy <= y1; iy++) for (let iz = z0; iz <= z1; iz++) {
                const s = Stoffkoerper._schluessel(ix, iy, iz), liste = zellen.get(s);
                if (liste) liste.push(k); else zellen.set(s, [k]);
            }
        }
        return zellen;
    }

    static _schluessel(ix, iy, iz) {
        return (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791);
    }

    /** Achse, Querachsen, Radien (mit Abstand) und Hülle einer Kapsel — einmal je Durchgang. */
    static _rahmen(k, abstand) {
        const ax = k.a[0], ay = k.a[1], az = k.a[2];
        let dx = k.b[0] - ax, dy = k.b[1] - ay, dz = k.b[2] - az;
        const laenge = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
        dx /= laenge; dy /= laenge; dz /= laenge;
        // Querachsen: u aus der Kapsel (rund: irgendeine Senkrechte), w = d × u.
        let ux, uy, uz;
        if (k.u) { [ux, uy, uz] = k.u; }
        else if (Math.abs(dx) < 0.9) { ux = 0; uy = -dz; uz = dy; }
        else { ux = dz; uy = 0; uz = -dx; }
        const ul = Math.sqrt(ux * ux + uy * uy + uz * uz) || 1; ux /= ul; uy /= ul; uz /= ul;
        const r = (k.r ?? k.ra), rua = (k.rua ?? k.ra ?? r) + abstand, rwa = (k.rwa ?? k.ra ?? r) + abstand;
        const rub = (k.rub ?? k.rb ?? r) + abstand, rwb = (k.rwb ?? k.rb ?? r) + abstand;
        const r0 = Math.max(rua, rwa, rub, rwb);
        return { ax, ay, az, dx, dy, dz, laenge, ux, uy, uz,
                 wx: dy * uz - dz * uy, wy: dz * ux - dx * uz, wz: dx * uy - dy * ux,
                 rua, rwa, rub, rwb,
                 minX: Math.min(ax, k.b[0]) - r0, maxX: Math.max(ax, k.b[0]) + r0,
                 minY: Math.min(ay, k.b[1]) - r0, maxY: Math.max(ay, k.b[1]) + r0,
                 minZ: Math.min(az, k.b[2]) - r0, maxZ: Math.max(az, k.b[2]) + r0 };
    }

    /** Zwei Arbeitsobjekte — je Punkt eines anzulegen kostete den Müllsammler. */
    static _L = {};
    static _V = {};

    /** Lage eines Punkts im Achsenraum der Kapsel, in `aus`:
     *  `{t, qx, qy, qz, ox, oy, oz, pu, pw, pd, e}` (e < 1: drin). */
    static _lage(R, px, py, pz, aus) {
        const s = (px - R.ax) * R.dx + (py - R.ay) * R.dy + (pz - R.az) * R.dz;
        const t = s < 0 ? 0 : (s > R.laenge ? 1 : s / R.laenge);
        const qx = R.ax + R.dx * R.laenge * t, qy = R.ay + R.dy * R.laenge * t, qz = R.az + R.dz * R.laenge * t;
        const ox = px - qx, oy = py - qy, oz = pz - qz;
        const pu = ox * R.ux + oy * R.uy + oz * R.uz, pw = ox * R.wx + oy * R.wy + oz * R.wz;
        const pd = ox * R.dx + oy * R.dy + oz * R.dz;
        const ru = R.rua + (R.rub - R.rua) * t, rw = R.rwa + (R.rwb - R.rwa) * t, rm = 0.5 * (ru + rw);
        aus.t = t; aus.qx = qx; aus.qy = qy; aus.qz = qz; aus.ox = ox; aus.oy = oy; aus.oz = oz;
        aus.pu = pu; aus.pw = pw; aus.pd = pd;
        aus.e = Math.sqrt((pu / ru) ** 2 + (pw / rw) ** 2 + (pd / rm) ** 2);
        return aus;
    }

    /** Den Punkt bei `o` aus der Kapsel `R` (Rahmen) hinaus; `A`: ihr Rahmen von vorhin. */
    static _eine(x, o, R, A, xAlt) {
        const px = x[o], py = x[o + 1], pz = x[o + 2];
        if (px < R.minX || px > R.maxX || py < R.minY || py > R.maxY || pz < R.minZ || pz > R.maxZ) return;
        const L = Stoffkoerper._lage(R, px, py, pz, Stoffkoerper._L);
        if (L.e >= 1 || L.e < 1e-6) return;
        if (A) {
            // Ist die Achse in ihrer Bewegungsrichtung m über den Punkt hinweg (vorhin lag er
            // vor ihr, jetzt dahinter), kommt er in der Richtung von vorhin heraus, auf die
            // Fläche der neuen Kapsel. Sonst radial - nur so kann er an der Fläche entlang
            // gleiten (immer die alte Richtung: ein drapierter Streifen hing fest, 1,44-fach
            // gedehnt; das Vorzeichen des ganzen Richtungsprodukts statt nur entlang m schob
            // die Nachbarreihen über die Kapsel statt vor sie).
            const V = Stoffkoerper._lage(A, xAlt[o], xAlt[o + 1], xAlt[o + 2], Stoffkoerper._V);
            const mx = L.qx - V.qx, my = L.qy - V.qy, mz = L.qz - V.qz;
            if (V.e > 1e-3 && V.ox * mx + V.oy * my + V.oz * mz > 0 && L.ox * mx + L.oy * my + L.oz * mz < 0) {
                const f = 1 / V.e, qx = R.ax + R.dx * R.laenge * V.t, qy = R.ay + R.dy * R.laenge * V.t;
                const qz = R.az + R.dz * R.laenge * V.t;
                x[o] = qx + (V.pu * R.ux + V.pw * R.wx + V.pd * R.dx) * f;
                x[o + 1] = qy + (V.pu * R.uy + V.pw * R.wy + V.pd * R.dy) * f;
                x[o + 2] = qz + (V.pu * R.uz + V.pw * R.wz + V.pd * R.dz) * f;
                return;
            }
        }
        const f = 1 / L.e;
        x[o] = L.qx + L.ox * f; x[o + 1] = L.qy + L.oy * f; x[o + 2] = L.qz + L.oz * f;
    }
}
