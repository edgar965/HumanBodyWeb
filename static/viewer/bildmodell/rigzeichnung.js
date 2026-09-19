/**
 * Rigzeichnung — die MediaPipe-Landmarken eines Bildes als SVG darüber.
 *
 * Edgar (19.09.2026): „mach bei der Jobseite auch die Bilder im ersten
 * Schritt mit dem Rig darauf." Die Sichtung liefert je Bild 33 Landmarken
 * `[x, y, sichtbar]` (normiert auf das Bild) und den Gesichtskasten; hier
 * werden daraus Knochenlinien (`VERBINDUNGEN`, MediaPipe-Pose-Topologie),
 * Punkte und der Kasten — ohne Bibliothek, als SVG mit `viewBox 0 0 1 1`,
 * das sich mit dem Bild skaliert. Unsichere Punkte (< 0,5) gestrichelt.
 */
export class Rigzeichnung {

    static SICHTBAR_AB = 0.5;
    /** MediaPipe Pose: Paare von Landmarkennummern. */
    static VERBINDUNGEN = [
        [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
        [11, 23], [12, 24], [23, 24], [23, 25], [25, 27], [24, 26], [26, 28],
        [27, 29], [29, 31], [27, 31], [28, 30], [30, 32], [28, 32],
        [15, 17], [17, 19], [15, 19], [15, 21], [16, 18], [18, 20], [16, 20], [16, 22],
        [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8], [9, 10],
    ];
    static LINKS = new Set([1, 2, 3, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]);
    /** COCO-17 (YOLO11-Pose, die ersten 17 von openpifpaf): Nase, Augen, Ohren, Schultern,
     *  Ellbogen, Handgelenke, Hüften, Knie, Knöchel — ungerade Nummern sind links. */
    static COCO_VERBINDUNGEN = [
        [0, 1], [0, 2], [1, 3], [2, 4], [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],
        [5, 11], [6, 12], [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
    ];
    static COCO_LINKS = new Set([1, 3, 5, 7, 9, 11, 13, 15]);
    /** openpifpaf Wholebody: 17 Körper + Füße 17..22 + Gesicht 23..90 + Hände 91..111 / 112..132. */
    static WHOLEBODY_KETTEN = [
        [15, 17], [15, 18], [15, 19], [16, 20], [16, 21], [16, 22],
    ];
    static FARBE = { links: '#4fc3f7', rechts: '#ffb74d', mitte: '#e0e0e0', gesicht: '#81c784', hand: '#f06292' };
    /** MediaPipe Hands: fünf Fingerketten ab dem Handgelenk (0) und der Handflächenbogen. */
    static HANDKETTEN = [
        [0, 1, 2, 3, 4], [0, 5, 6, 7, 8], [0, 9, 10, 11, 12], [0, 13, 14, 15, 16], [0, 17, 18, 19, 20],
        [5, 9, 13, 17],
    ];

    /**
     * @param {Array<[number, number, number]>|null} landmarken
     * @param {{x:number,y:number,breite:number,hoehe:number}|null} gesicht
     * @param {number} seitenverhaeltnis  Breite / Höhe des Bildes (Strichstärke)
     * @param {Array<{bild: Array<[number, number]>}>} [haende]  Handpunkte der Sichtung (seit 19.09.2026)
     */
    static svg(landmarken, gesicht, seitenverhaeltnis = 0.75, haende = []) {
        const ns = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', '0 0 1 1');
        svg.setAttribute('preserveAspectRatio', 'none');
        svg.classList.add('bildmodell-rig');
        // Strichstärke in BILDSCHIRMPIXELN (`vector-effect: non-scaling-stroke`):
        // in viewBox-Einheiten wäre sie bei `preserveAspectRatio="none"` je Achse
        // anders skaliert — und 0,006 px unsichtbar (Sichtprobe 19.09.2026).
        const dick = 2;
        // Kreise: der viewBox 0..1 wird auf Breite und Höhe verschieden gestreckt;
        // ry = rx × (Breite / Höhe) macht den Punkt wieder rund.
        const rx = 0.014, ry = 0.014 * seitenverhaeltnis;
        if (gesicht && gesicht.breite > 0) {
            const r = document.createElementNS(ns, 'rect');
            r.setAttribute('x', gesicht.x); r.setAttribute('y', gesicht.y);
            r.setAttribute('width', gesicht.breite); r.setAttribute('height', gesicht.hoehe);
            r.setAttribute('fill', 'none'); r.setAttribute('stroke', Rigzeichnung.FARBE.gesicht);
            r.setAttribute('stroke-width', dick); r.setAttribute('vector-effect', 'non-scaling-stroke');
            svg.appendChild(r);
        }
        for (const hand of haende || []) Rigzeichnung.hand(svg, ns, hand.bild, dick);
        if (!landmarken || landmarken.length < 33) return svg;
        for (const [a, b] of Rigzeichnung.VERBINDUNGEN) {
            const p = landmarken[a], q = landmarken[b];
            if (!p || !q) continue;
            const l = document.createElementNS(ns, 'line');
            l.setAttribute('x1', p[0]); l.setAttribute('y1', p[1]);
            l.setAttribute('x2', q[0]); l.setAttribute('y2', q[1]);
            l.setAttribute('stroke', Rigzeichnung.farbe(a, b));
            l.setAttribute('stroke-width', dick);
            l.setAttribute('vector-effect', 'non-scaling-stroke');
            if (Math.min(p[2], q[2]) < Rigzeichnung.SICHTBAR_AB) l.setAttribute('stroke-dasharray', '6 4');
            svg.appendChild(l);
        }
        landmarken.forEach((p, i) => {
            const k = document.createElementNS(ns, 'ellipse');
            k.setAttribute('cx', p[0]); k.setAttribute('cy', p[1]);
            k.setAttribute('rx', rx); k.setAttribute('ry', ry);
            k.setAttribute('fill', Rigzeichnung.farbe(i, i));
            k.setAttribute('opacity', p[2] < Rigzeichnung.SICHTBAR_AB ? 0.35 : 0.95);
            svg.appendChild(k);
        });
        return svg;
    }

    /** Die 21 Handpunkte als Fingerketten — eine Farbe, die Seite steht im Text der Kachel. */
    static hand(svg, ns, punkte, dick) {
        if (!punkte || punkte.length < 21) return;
        for (const kette of Rigzeichnung.HANDKETTEN) {
            const l = document.createElementNS(ns, 'polyline');
            l.setAttribute('points', kette.map(i => `${punkte[i][0]},${punkte[i][1]}`).join(' '));
            l.setAttribute('fill', 'none');
            l.setAttribute('stroke', Rigzeichnung.FARBE.hand);
            l.setAttribute('stroke-width', dick);
            l.setAttribute('vector-effect', 'non-scaling-stroke');
            svg.appendChild(l);
        }
    }

    /**
     * Ein COCO-Rig (17 Punkte) oder openpifpaf-Wholebody (133) als SVG.
     * @param {Array<[number, number, number]>} punkte  normiert, dritter Wert die Güte
     */
    static cocoSvg(punkte, seitenverhaeltnis = 0.75) {
        const ns = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', '0 0 1 1');
        svg.setAttribute('preserveAspectRatio', 'none');
        svg.classList.add('bildmodell-rig');
        if (!punkte || punkte.length < 17) return svg;
        const dick = 2, rx = 0.012, ry = 0.012 * seitenverhaeltnis;
        const sichtbar = i => punkte[i] && punkte[i][2] >= Rigzeichnung.SICHTBAR_AB;
        const linie = (a, b, farbe) => {
            if (!sichtbar(a) || !sichtbar(b)) return;
            const l = document.createElementNS(ns, 'line');
            l.setAttribute('x1', punkte[a][0]); l.setAttribute('y1', punkte[a][1]);
            l.setAttribute('x2', punkte[b][0]); l.setAttribute('y2', punkte[b][1]);
            l.setAttribute('stroke', farbe); l.setAttribute('stroke-width', dick);
            l.setAttribute('vector-effect', 'non-scaling-stroke');
            svg.appendChild(l);
        };
        const cocoFarbe = (a, b) => {
            const l = Rigzeichnung.COCO_LINKS.has(a) && Rigzeichnung.COCO_LINKS.has(b);
            const r = !Rigzeichnung.COCO_LINKS.has(a) && !Rigzeichnung.COCO_LINKS.has(b) && a > 4;
            return l ? Rigzeichnung.FARBE.links : r ? Rigzeichnung.FARBE.rechts : Rigzeichnung.FARBE.mitte;
        };
        for (const [a, b] of Rigzeichnung.COCO_VERBINDUNGEN) linie(a, b, cocoFarbe(a, b));
        if (punkte.length >= 133) {
            for (const [a, b] of Rigzeichnung.WHOLEBODY_KETTEN) linie(a, b, cocoFarbe(a, a));
            // Hände als Fingerketten, wenn die Mehrheit der 21 Punkte sicher ist.
            for (const start of [91, 112]) {
                const sicher = punkte.slice(start, start + 21).filter(p => p[2] >= Rigzeichnung.SICHTBAR_AB).length;
                if (sicher >= 11) Rigzeichnung.hand(svg, ns, punkte.slice(start, start + 21), dick);
            }
        }
        punkte.forEach((p, i) => {
            if (!sichtbar(i)) return;
            const k = document.createElementNS(ns, 'ellipse');
            const klein = i >= 23;
            k.setAttribute('cx', p[0]); k.setAttribute('cy', p[1]);
            k.setAttribute('rx', klein ? rx * 0.4 : rx); k.setAttribute('ry', klein ? ry * 0.4 : ry);
            const farbe = i >= 23 && i < 91 ? Rigzeichnung.FARBE.gesicht : i >= 91 ? Rigzeichnung.FARBE.hand : cocoFarbe(i, i);
            k.setAttribute('fill', farbe);
            k.setAttribute('opacity', 0.95);
            svg.appendChild(k);
        });
        return svg;
    }

    static farbe(a, b) {
        const links = Rigzeichnung.LINKS.has(a) && Rigzeichnung.LINKS.has(b);
        const rechts = !Rigzeichnung.LINKS.has(a) && !Rigzeichnung.LINKS.has(b) && a > 10;
        return links ? Rigzeichnung.FARBE.links : rechts ? Rigzeichnung.FARBE.rechts : Rigzeichnung.FARBE.mitte;
    }
}
