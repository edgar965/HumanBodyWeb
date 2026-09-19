/**
 * Proportionenlinien — die Maßlinien als SVG-Markup, für Zeilenbilder und Popup.
 *
 * Eine Linie je Maß: `line` mit einer Pfeilspitze an jedem Ende (`prop-pfeil`,
 * Edgar 20.09.2026: „Die Maße sollen Pfeile am Ende haben"), Beschriftung am
 * rechten Ende (damit sich Schulter, Brust und Oberarm nicht überdecken). Im
 * Popup sind die Pfeilspitzen selbst die Griffe (`prop-griff`, `data-ende`) —
 * größer, KEINE Kugeln („ich sagte Pfeile im Popup, keine Kugeln am Ende!!!",
 * Edgar, 20.09.2026) — und am linken Ende steht ein × (`prop-loeschen`: den
 * Marker aus diesem Bild löschen). Klassen: `prop-eingestellt` (Wert von
 * Edgar), `prop-aktiv` (hervorgehoben). Reine Markup-Erzeugung ohne DOM —
 * deshalb in Node prüfbar.
 */
export class Proportionenlinien {

    /** Länge der Pfeilspitzen in Bezugspixeln (skaliert mit `--s`). */
    static PFEIL = 9;
    /** Länge der Pfeilspitzen im Popup — sie sind dort die Griffe. */
    static PFEIL_GRIFF = 16;

    /** Bildmaß, auf das Strich und Schrift des CSS ausgelegt sind — alles andere skaliert (`--s`). */
    static BEZUG = 600;

    /** Das Maß, nach dem Pfeile und Schrift skalieren: die Breite, bei Hochkantbildern die Höhe × 0,6
     *  (das Seitenfoto ist 319 × 1600 — nach der Breite wären die Pfeile 2 px groß). */
    static bezug(breite, hoehe) { return Math.max(Number(breite) || 0, (Number(hoehe) || 0) * 0.6); }

    /**
     * @param eintraege  `[{k, name, p, q, wert, eingestellt, aktiv}]` — p, q in Bildpixeln
     * @param bezug      Bildmaß (`bezug(breite, hoehe)`) für Pfeile und Schrift
     * @param griffe     true (Popup): die Pfeilspitzen sind anfassbare Griffe, dazu das ×
     */
    static markup(eintraege, bezug, griffe = false) {
        const s = (bezug / Proportionenlinien.BEZUG).toFixed(3);
        const pfeil = (griffe ? Proportionenlinien.PFEIL_GRIFF : Proportionenlinien.PFEIL) * Number(s);
        return eintraege.map(e => {
            const klasse = 'prop-linie' + (e.eingestellt ? ' prop-eingestellt' : '') + (e.aktiv ? ' prop-aktiv' : '');
            const rechts = e.p[0] >= e.q[0] ? e.p : e.q;
            const links = rechts === e.p ? e.q : e.p;
            const wert = e.wert === null || e.wert === undefined ? '' : ` ${Proportionenlinien.zahl(e.wert)}`;
            const abstand = griffe ? pfeil + 4 * s : 5 * s;
            return `<g class="${klasse}" data-mass="${e.k}" style="--s:${s}"><title>${e.name}: ${wert} cm</title>`
                + `<line x1="${e.p[0]}" y1="${e.p[1]}" x2="${e.q[0]}" y2="${e.q[1]}"/>`
                + Proportionenlinien.pfeile(e.p, e.q, pfeil, griffe)
                + `<text x="${rechts[0] + abstand}" y="${rechts[1] + 5 * s}">${e.name}${wert}</text>`
                + (griffe ? `<text class="prop-loeschen" x="${links[0] - abstand - 6 * s}" y="${links[1] + 6 * s}" text-anchor="end">`
                    + `<title>${e.name} aus diesem Bild löschen</title>×</text>` : '')
                + '</g>';
        }).join('');
    }

    /** Zwei Pfeilspitzen (Dreiecke) an den Enden der Strecke p–q, Länge `l` Bildpixel;
     *  mit `griffe` tragen sie `prop-griff` und `data-ende` (0 = p, 1 = q) zum Anfassen. */
    static pfeile(p, q, l, griffe = false) {
        const dx = q[0] - p[0], dy = q[1] - p[1];
        const laenge = Math.hypot(dx, dy);
        if (!(laenge > 0)) return '';
        const ux = dx / laenge, uy = dy / laenge;
        const spitze = (t, richtung, ende) => {
            const bx = t[0] - richtung * ux * l, by = t[1] - richtung * uy * l;
            const nx = -uy * l * 0.4, ny = ux * l * 0.4;
            const f = v => Math.round(v * 10) / 10;
            const griff = griffe ? ` prop-griff" data-ende="${ende}` : '';
            return `<polygon class="prop-pfeil${griff}" points="${f(t[0])},${f(t[1])} ${f(bx + nx)},${f(by + ny)} ${f(bx - nx)},${f(by - ny)}"/>`;
        };
        return spitze(p, -1, 0) + spitze(q, 1, 1);
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
