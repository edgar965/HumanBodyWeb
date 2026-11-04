/**
 * Ai2d3dpshumanumriss — der Umriss eines Körpers als Vorlage für einen Bildplatz der PSHuman-Eingabe (03.11.2026, Edgar: „mach vorschlag, wie die sein sollten,
 * z.B. Umriss vom Körper“). Gezeigt wird, wie das Foto aussehen soll: ganzer Körper im Rahmen, stehend, Arme etwas vom Körper weg, Blickrichtung je Winkel
 * (Winkel der Fotojobs: 90 = linke Körperseite, die Person blickt im Bild nach links wie EdgarTrip 4.jpg; 270 = rechte Seite, Blick nach rechts).
 *
 * Gezeichnet in zwei Durchgängen aus einfachen Teilen (Kopf, Rumpf, Glieder): erst alles etwas dicker in der Randfarbe, darüber dieselben Teile in der
 * Flächenfarbe — so bleibt nur die Außenlinie der Vereinigung stehen. Farben über CSS (`.ai2d3d-umriss-*` in ai2d3d.css).
 */
const NS = 'http://www.w3.org/2000/svg';

export class Ai2d3dpshumanumriss {
    /** Randbreite (Einheiten der viewBox 100 × 200) */
    static RAND = 2.4;

    /** Teile je Winkel: ['ellipse', cx, cy, rx, ry] | ['kreis', cx, cy, r] | ['glied', x1, y1, x2, y2, dicke] | ['rumpf', [[x, y], …]] */
    static teile(winkel) {
        const w = ((Number(winkel) % 360) + 360) % 360;
        if (w === 90 || w === 270) return Ai2d3dpshumanumriss._seite(w === 90 ? -1 : 1);
        const schraeg = w === 45 || w === 315;
        return Ai2d3dpshumanumriss._vorn(schraeg ? 0.78 : 1, w === 45 ? -1 : w === 315 ? 1 : 0);
    }

    /** von vorn oder hinten (k = 1) bzw. schräg (k < 1, s = Blickrichtung im Bild: −1 links, +1 rechts) */
    static _vorn(k, s) {
        const x = v => 50 + (v - 50) * k;
        const t = [['ellipse', 50 + s * 2, 20, 9, 11], ['glied', 50, 29, 50, 38, 8],
                   ['rumpf', [[x(33), 40], [x(67), 40], [x(64), 62], [x(62), 82], [x(66), 100], [x(34), 100], [x(38), 82], [x(36), 62]]]];
        if (s) t.push(['kreis', 50 + s * 11.5, 21, 2.4]);
        for (const seite of [-1, 1]) {
            const m = v => 50 + seite * v * k;
            // schräg: der Arm auf der Seite, zu der die Person blickt, ist der hintere — halb hinter dem Rumpf
            const a = v => 50 + seite * v * k * (s && seite === s ? 0.62 : 1);
            t.push(['glied', a(16), 43, a(25), 72, 8], ['glied', a(25), 72, a(32), 98, 7], ['kreis', a(33), 103, 4],
                   ['glied', m(8), 99, m(10), 145, 13], ['glied', m(10), 145, m(11), 184, 9],
                   s ? ['glied', m(11), 188, m(11) + s * 7, 190, 7] : ['glied', m(11) - 3, 189, m(11) + 3, 189, 7]);
        }
        return t;
    }

    /** im Profil, s = Blickrichtung im Bild (−1 links, +1 rechts) */
    static _seite(s) {
        const x = v => 50 + s * v;
        return [['ellipse', 50, 20, 8.5, 11], ['kreis', x(9), 21, 2.2], ['glied', x(-1), 29, x(-1), 38, 8],
                ['rumpf', [[x(7), 40], [x(-8), 40], [x(-10), 62], [x(-8), 82], [x(-9), 100], [x(8), 100], [x(10), 82], [x(9), 58]]],
                ['glied', x(0), 43, x(1), 72, 8], ['glied', x(1), 72, x(3), 98, 7], ['kreis', x(3.5), 103, 4],
                ['glied', x(0), 99, x(0), 145, 14], ['glied', x(0), 145, x(-1), 184, 10], ['glied', x(-2), 188, x(9), 190, 7]];
    }

    static svg(winkel) {
        const svg = document.createElementNS(NS, 'svg');
        svg.setAttribute('viewBox', '0 0 100 200');
        svg.setAttribute('class', 'ai2d3d-umriss');
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', `Umriss als Vorlage, ${winkel}°`);
        svg.append(Ai2d3dpshumanumriss._element('rect', { x: 2, y: 2, width: 96, height: 196, rx: 3, class: 'ai2d3d-umriss-rahmen' }),
                   Ai2d3dpshumanumriss._element('line', { x1: 12, y1: 192, x2: 88, y2: 192, class: 'ai2d3d-umriss-boden' }));
        const teile = Ai2d3dpshumanumriss.teile(winkel);
        for (const [klasse, rand] of [['ai2d3d-umriss-rand', Ai2d3dpshumanumriss.RAND], ['ai2d3d-umriss-flaeche', 0]]) {
            const g = Ai2d3dpshumanumriss._element('g', { class: klasse });
            for (const t of teile) g.append(Ai2d3dpshumanumriss._teil(t, rand));
            svg.append(g);
        }
        return svg;
    }

    static _teil(t, rand) {
        const [art, ...w] = t;
        if (art === 'ellipse') return Ai2d3dpshumanumriss._element('ellipse', { cx: w[0], cy: w[1], rx: w[2] + rand / 2, ry: w[3] + rand / 2 });
        if (art === 'kreis') return Ai2d3dpshumanumriss._element('circle', { cx: w[0], cy: w[1], r: w[2] + rand / 2 });
        if (art === 'glied') return Ai2d3dpshumanumriss._element('line', { x1: w[0], y1: w[1], x2: w[2], y2: w[3], 'stroke-width': w[4] + rand, 'stroke-linecap': 'round' });
        if (art === 'rumpf') return Ai2d3dpshumanumriss._element('polygon', { points: w[0].map(p => p.join(',')).join(' '), 'stroke-width': rand, 'stroke-linejoin': 'round' });
        throw new Error(`Ai2d3dpshumanumriss: unbekanntes Teil ${art}`);
    }

    static _element(name, attribute) {
        const e = document.createElementNS(NS, name);
        for (const [k, v] of Object.entries(attribute)) e.setAttribute(k, String(v));
        return e;
    }
}
