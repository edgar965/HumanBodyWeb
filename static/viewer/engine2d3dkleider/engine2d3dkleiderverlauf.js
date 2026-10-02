/**
 * Engine2d3dKleiderverlauf — die Kurve der Iterationen über alle Runden.
 *
 * `ergebnis.kreislauf.verlauf` = [[runde, beste Abweichung bis dahin, beste Abweichung DIESER Runde]]. Die dunkle Linie ist die beste
 * bisherige (fällt nur oder bleibt), die hellen Punkte zeigen, was jede Runde gefunden hat — so sieht man, ob der Optimierer noch in
 * der Nähe sucht oder schon weit daneben liegt. Einfaches SVG, keine Bibliothek.
 */
export class Engine2d3dKleiderverlauf {

    static BREITE = 900;
    static HOEHE = 160;
    static RAND = 34;

    static zeichnen(behaelter, verlauf) {
        behaelter.replaceChildren();
        if (!verlauf || verlauf.length < 2) return;
        const { BREITE: B, HOEHE: H, RAND: R } = Engine2d3dKleiderverlauf;
        const werte = verlauf.flatMap(([, a, b]) => [a, b]).filter(Number.isFinite);
        const lo = Math.min(...werte);
        const hi = Math.max(...werte);
        const spanne = hi - lo || 1;
        const r0 = verlauf[0][0];
        const r1 = verlauf[verlauf.length - 1][0];
        const x = r => R + (B - 2 * R) * (r - r0) / ((r1 - r0) || 1);
        const y = v => H - R / 2 - (H - R) * (v - lo) / spanne;
        const ns = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', `0 0 ${B} ${H}`);
        svg.setAttribute('class', 'engine2d3dkleider-verlauf');
        const linie = document.createElementNS(ns, 'polyline');
        linie.setAttribute('points', verlauf.map(([r, a]) => `${x(r)},${y(a)}`).join(' '));
        linie.setAttribute('class', 'engine2d3dkleider-verlauf-bester');
        svg.appendChild(linie);
        for (const [r, , b] of verlauf) {
            const punkt = document.createElementNS(ns, 'circle');
            punkt.setAttribute('cx', x(r));
            punkt.setAttribute('cy', y(b));
            punkt.setAttribute('r', 2.5);
            punkt.setAttribute('class', 'engine2d3dkleider-verlauf-runde');
            svg.appendChild(punkt);
        }
        for (const [text, wert] of [[hi.toFixed(3), hi], [lo.toFixed(3), lo]]) {
            const t = document.createElementNS(ns, 'text');
            t.setAttribute('x', 2);
            t.setAttribute('y', y(wert) + 4);
            t.textContent = text;
            svg.appendChild(t);
        }
        const unten = document.createElementNS(ns, 'text');
        unten.setAttribute('x', B / 2);
        unten.setAttribute('y', H - 2);
        unten.textContent = `Runde ${r0} … ${r1} · Abweichung (kleiner ist besser)`;
        svg.appendChild(unten);
        behaelter.appendChild(svg);
    }
}
