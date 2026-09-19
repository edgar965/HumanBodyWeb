/**
 * Proportionenlinien — die Maßlinien als SVG-Markup, für Zeilenbilder und Popup.
 *
 * Eine Linie je Maß: `line`, Beschriftung am rechten Ende (damit sich Schulter,
 * Brust und Oberarm nicht überdecken), im Popup dazu ein Griff (`circle`) an
 * jedem Ende. Klassen: `prop-eingestellt` (Wert von Edgar), `prop-aktiv`
 * (hervorgehoben). Reine Markup-Erzeugung ohne DOM — deshalb in Node prüfbar.
 */
export class Proportionenlinien {

    /** Radius der Griffe als Anteil der Bildbreite. */
    static GRIFF = 0.012;

    /**
     * @param eintraege  `[{k, name, p, q, wert, eingestellt, aktiv}]` — p, q in Bildpixeln
     * @param bezug      Bildmaß (`bezug(breite, hoehe)`) für Griffradius und Schrift
     * @param griffe     true: Griffe an beiden Enden
     */
    /** Bildmaß, auf das Strich und Schrift des CSS ausgelegt sind — alles andere skaliert (`--s`). */
    static BEZUG = 600;

    /** Das Maß, nach dem Griffe und Schrift skalieren: die Breite, bei Hochkantbildern die Höhe × 0,6
     *  (das Seitenfoto ist 319 × 1600 — nach der Breite wären die Griffe 2 px groß). */
    static bezug(breite, hoehe) { return Math.max(Number(breite) || 0, (Number(hoehe) || 0) * 0.6); }

    static markup(eintraege, bezug, griffe = false) {
        const r = bezug * Proportionenlinien.GRIFF;
        const s = (bezug / Proportionenlinien.BEZUG).toFixed(3);
        return eintraege.map(e => {
            const klasse = 'prop-linie' + (e.eingestellt ? ' prop-eingestellt' : '') + (e.aktiv ? ' prop-aktiv' : '');
            const rechts = e.p[0] >= e.q[0] ? e.p : e.q;
            const wert = e.wert === null || e.wert === undefined ? '' : ` ${Proportionenlinien.zahl(e.wert)}`;
            const abstand = griffe ? r + 4 : 5 * s;
            return `<g class="${klasse}" data-mass="${e.k}" style="--s:${s}"><title>${e.name}: ${wert} cm</title>`
                + `<line x1="${e.p[0]}" y1="${e.p[1]}" x2="${e.q[0]}" y2="${e.q[1]}"/>`
                + `<text x="${rechts[0] + abstand}" y="${rechts[1] + 5 * s}">${e.name}${wert}</text>`
                + (griffe ? `<circle class="prop-griff" data-ende="0" cx="${e.p[0]}" cy="${e.p[1]}" r="${r}"/>`
                    + `<circle class="prop-griff" data-ende="1" cx="${e.q[0]}" cy="${e.q[1]}" r="${r}"/>` : '')
                + '</g>';
        }).join('');
    }

    /** Zahl mit einer Nachkommastelle, ganze ohne. */
    static zahl(v) {
        const n = Number(v);
        return Number.isInteger(n) ? String(n) : n.toFixed(1);
    }

    /** Länge einer Linie in cm — oder null ohne Maßstab. */
    static cm(linie, pxJeM) {
        if (!linie || !pxJeM) return null;
        const l = Math.hypot(linie[1][0] - linie[0][0], linie[1][1] - linie[0][1]);
        return Math.max(0.5, Math.round(l / pxJeM * 1000) / 10);
    }

    /** Strecke gleicher Richtung und Mitte mit neuer Länge (px). */
    static strecken(linie, laenge) {
        const [von, bis] = linie;
        const dx = bis[0] - von[0], dy = bis[1] - von[1];
        const alt = Math.hypot(dx, dy) || 1;
        const mx = (von[0] + bis[0]) / 2, my = (von[1] + bis[1]) / 2;
        const ex = dx / alt * laenge / 2, ey = dy / alt * laenge / 2;
        return [[mx - ex, my - ey], [mx + ex, my + ey]];
    }

    /** Linie um (dx, dy) verschoben. */
    static verschoben(linie, dx, dy) {
        return linie.map(([x, y]) => [x + dx, y + dy]);
    }

    /** Linie mit einem neu gesetzten Ende (0 oder 1). */
    static mitEnde(linie, ende, punkt) {
        const neu = [linie[0].slice(), linie[1].slice()];
        neu[ende] = [punkt[0], punkt[1]];
        return neu;
    }
}
