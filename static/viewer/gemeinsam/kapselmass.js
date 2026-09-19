/**
 * Kapselmass — die Maße einer Körperkapsel aus den Hautpunkten des Knochens:
 * zwei Halbachsen quer zum Knochen, je Ende.
 *
 * WARUM JE ENDE UND ELLIPTISCH (19.09.2026, Edgar: „Hose (genesis) animiert
 * nicht"): Eine Kapsel mit EINEM Radius über die ganze Knochenlänge (85.
 * Perzentil aller Abstände) trug am Oberschenkel 12 cm bis zum Knie, wo der
 * Schenkel halb so dick ist — die Jeans blähte in Daz' Idle 12–19 cm auf.
 * Und ein Schenkel ist kein Kreis: vorn/hinten dicker als seitlich. Mit dem
 * Median statt des 85. Perzentils folgte die Jeans (8 statt 31 mm), aber
 * 2,4 % ihrer Punkte lagen bis 19 mm in der Haut (`stoffkoerper.js`).
 *
 * Deshalb `ellipse`: die Hauptachsen der Querabstände (2-D-Kovarianz in der
 * Ebene senkrecht zum Knochen), und je Hälfte der Achse (Anteil t < ½ am
 * Kopf, sonst am Kind) je Hauptachse ein Radius — das `PERZENTIL` der
 * Beträge entlang dieser Achse. 0,9: Auf einer Ellipse ist |o·u| = ru·|cos φ|,
 * das 90. Perzentil von |cos φ| liegt bei 0,988 — der Radius trifft die
 * Hülle, ein Median träfe nur 71 % davon.
 *
 * Fehlen einer Hälfte die Punkte (`MINDEST`), nimmt sie die Radien der
 * anderen — ein Knochen, dessen Haut nur am Kopf sitzt, wird ein Zylinder.
 *
 * Ohne Three.js, damit `test_js_kapselmass` es in Node prüft.
 */
export class Kapselmass {

    /** Perzentil der Beträge je Hauptachse und Hälfte. */
    static PERZENTIL = 0.9;
    /** Weniger Punkte in einer Hälfte: sie nimmt die Radien der anderen. */
    static MINDEST = 20;

    /**
     * Hauptachsen und Radien je Ende.
     * @param x1, x2    Querabstände je Hautpunkt in einer festen Basis (e1, e2)
     *                  senkrecht zum Knochen (Meter)
     * @param anteile   Anteil je Hautpunkt auf der Achse, 0 (Kopf) … 1 (Kind)
     * @returns {{theta, rua, rwa, rub, rwb}} — `theta`: Winkel der ersten
     *          Hauptachse u in der Basis (u = cos θ·e1 + sin θ·e2, w = −sin θ·e1 + cos θ·e2)
     */
    static ellipse(x1, x2, anteile, perzentil = Kapselmass.PERZENTIL) {
        const n = x1.length;
        let sxx = 0, sxy = 0, syy = 0;
        for (let i = 0; i < n; i++) { sxx += x1[i] * x1[i]; sxy += x1[i] * x2[i]; syy += x2[i] * x2[i]; }
        const theta = 0.5 * Math.atan2(2 * sxy, sxx - syy);
        const c = Math.cos(theta), s = Math.sin(theta);
        const ua = [], wa = [], ub = [], wb = [];
        for (let i = 0; i < n; i++) {
            const pu = Math.abs(x1[i] * c + x2[i] * s), pw = Math.abs(-x1[i] * s + x2[i] * c);
            if (anteile[i] < 0.5) { ua.push(pu); wa.push(pw); } else { ub.push(pu); wb.push(pw); }
        }
        const genugA = ua.length >= Kapselmass.MINDEST, genugB = ub.length >= Kapselmass.MINDEST;
        const P = (l) => Kapselmass.perzentil(l, perzentil);
        let rua = P(ua), rwa = P(wa), rub = P(ub), rwb = P(wb);
        if (!genugA && !genugB) { rua = rub = P(ua.concat(ub)); rwa = rwb = P(wa.concat(wb)); }
        else if (!genugA) { rua = rub; rwa = rwb; }
        else if (!genugB) { rub = rua; rwb = rwa; }
        return { theta, rua, rwa, rub, rwb };
    }

    /** `[ra, rb]` — EIN Radius je Ende (rund), das Perzentil der Abstände je Hälfte. */
    static endradien(abstaende, anteile, perzentil = Kapselmass.PERZENTIL) {
        const kopf = [], kind = [];
        for (let i = 0; i < abstaende.length; i++) (anteile[i] < 0.5 ? kopf : kind).push(abstaende[i]);
        const ra = Kapselmass.perzentil(kopf, perzentil), rb = Kapselmass.perzentil(kind, perzentil);
        const genugA = kopf.length >= Kapselmass.MINDEST, genugB = kind.length >= Kapselmass.MINDEST;
        if (genugA && genugB) return [ra, rb];
        if (genugA) return [ra, ra];
        if (genugB) return [rb, rb];
        const alle = Kapselmass.perzentil(abstaende, perzentil);
        return [alle, alle];
    }

    /** Das Perzentil (0..1) einer Liste — 0 für eine leere. */
    static perzentil(werte, p) {
        if (!werte.length) return 0;
        const sortiert = Array.from(werte).sort((x, y) => x - y);
        return sortiert[Math.min(sortiert.length - 1, Math.floor(sortiert.length * p))];
    }
}
