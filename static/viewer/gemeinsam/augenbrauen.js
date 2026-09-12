/**
 * Augenbrauen — Härchen für ein HumanBody-Gesicht, gerechnet aus dem Netz.
 *
 * WARUM (Edgar, 12.09.2026: „bei Augen - Wimpern - Nägel fehlen die
 * Augenbrauen"): Das HumanBody-Netz HAT keine Brauen. Die Wimpern sind
 * eigene Streifen (Materialgruppe 2), die Augen eigene Gruppen — für die
 * Brauen gibt es weder Gruppe noch Textur (die MB-Lab-Albedo an den UVs des
 * Netzes ist an der Brauenstelle so hell wie die Wange, gemessen
 * `ProjektTemp/brauen_probe.py`: 0 von 248 Punkten dunkler als 120). Nur
 * die Formmorphs `Eyebrows_*` bewegen die Haut dort.
 *
 * DER WEG: Der Bogen wird vom AUGE aus gesetzt (Mitte der Sklera, Gruppe 4,
 * je Seite) und auf die Hautfläche gelegt — je Bogenpunkt der vorderste
 * Hautpunkt in seiner Umgebung. So folgt er jedem Morph und jedem
 * Körpertyp, ohne dass jemand Punktnummern kennt. Darauf stehen kurze,
 * schmale Streifen (wie die Wimpern gebaut sind), nach außen und leicht nach
 * oben gekämmt, innen länger als außen. Jeder Streifen kennt seinen
 * WURZELPUNKT auf der Haut: von dort kommen Hautgewichte und Bewegung.
 *
 * DER ANKER (12.09.2026, Edgar: „die einstellung der Augenbrauen (Höhe usw)
 * funktionieren nicht"): Der Bogen wird EINMAL vom Auge aus bestimmt und als
 * Anker gemerkt — je Bogenpunkt der Hautpunkt darunter und der Versatz zu
 * ihm. Danach folgen die Brauen diesen Hautpunkten. Vorher wurde der Bogen
 * bei jedem Neubau wieder relativ zum Auge gelegt; die Morphs `Eyebrows_*`
 * heben aber die HAUT (gemessen `ProjektTemp/brauen_morph_probe.py`:
 * `Eyebrows_PosZ` bis 6,6 mm, `Ridge` 8,4 mm), nicht das Auge — die Braue
 * blieb also stehen, nur die Höhe über der Haut änderte sich um Zehntel.
 *
 * Alles in Metern, im Raum des Körpernetzes (Three.js: y hoch, z nach vorn).
 * Ohne Three.js und ohne DOM — prüfbar in Node (`test_js_augenbrauen.py`);
 * die Netzseite steht in `scene/augenbrauenbau.js`.
 */
export class Augenbrauen {

    /** Materialgruppen des Körpers (siehe `koerperdetails.js`). */
    static GRUPPE = { haut: 0, sklera: 4 };

    /** Bogen je Seite: von innen (nahe der Nase) nach außen, relativ zum Auge. */
    static BOGEN = {
        innenX: -0.014,     // Braueninnenseite: 14 mm NASENWÄRTS der Augenmitte (m)
        aussenX: 0.026,     // Außenseite: 26 mm schläfenwärts
        hoehe: 0.022,       // Bogenhöhe über der Augenmitte, innen
        woelbung: 0.006,    // zusätzliche Höhe am Scheitel (bei 55 % der Länge)
        abfall: 0.004,      // so viel tiefer liegt das äußere Ende
        haare: 30,          // Streifen je Braue — dicht genug für einen Strich, nicht eine Punktreihe
        suchweite: 0.008,   // Umkreis, in dem der vorderste Hautpunkt gesucht wird (m)
    };

    /** Ein Streifen: Länge innen/außen, Breite, Neigung nach oben, Abstand über der Haut. */
    static HAAR = { laengeInnen: 0.0085, laengeAussen: 0.0055, breite: 0.0017,
                    neigung: 0.55, abstand: 0.0008 };

    /**
     * Die Ecken einer Gruppe im vollen Index.
     * @returns {Uint32Array}
     */
    static ecken(index, gruppen, nummer) {
        const menge = new Set();
        for (const g of gruppen) {
            if (g.materialIndex !== nummer) continue;
            for (let k = g.start; k < g.start + g.count; k++) menge.add(index[k]);
        }
        return Uint32Array.from(menge);
    }

    /** Augenmitten aus der Sklera: links (x < 0) und rechts (x ≥ 0), oder null. */
    static augen(punkte, sklera) {
        const s = { links: [0, 0, 0, 0], rechts: [0, 0, 0, 0] };
        for (const e of sklera) {
            const z = punkte[3 * e] < 0 ? s.links : s.rechts;
            z[0] += punkte[3 * e]; z[1] += punkte[3 * e + 1]; z[2] += punkte[3 * e + 2]; z[3] += 1;
        }
        const mittel = (z) => (z[3] ? [z[0] / z[3], z[1] / z[3], z[2] / z[3]] : null);
        return { links: mittel(s.links), rechts: mittel(s.rechts) };
    }

    /**
     * Der Brauenbogen einer Seite auf der Haut: `haare` Punkte von innen nach
     * außen, jeder mit dem Hautpunkt darunter (`wurzel`) und dessen
     * Richtung nach vorn (Normale, grob: von der Augenmitte weg).
     * @param {number} seite  −1 links, +1 rechts
     * @returns {Array<{p: number[], wurzel: number, t: number}>}
     */
    static bogen(punkte, haut, auge, seite, wahl = Augenbrauen.BOGEN) {
        if (!auge) return [];
        const aus = [];
        for (let k = 0; k < wahl.haare; k++) {
            const t = wahl.haare > 1 ? k / (wahl.haare - 1) : 0;
            const x = auge[0] + seite * (wahl.innenX + t * (wahl.aussenX - wahl.innenX));
            // Scheitel bei etwa 55 % der Länge — der Bogen einer Braue.
            const u = t < 0.55 ? t / 0.55 * 0.5 : 0.5 + (t - 0.55) / 0.45 * 0.5;
            const y = auge[1] + wahl.hoehe + wahl.woelbung * Math.sin(Math.PI * u) - wahl.abfall * t;
            const vorn = Augenbrauen.vorderster(punkte, haut, x, y, wahl.suchweite);
            if (vorn < 0) continue;
            aus.push({ p: [x, y, punkte[3 * vorn + 2]], wurzel: vorn, t });
        }
        return aus;
    }

    /** Der vorderste Hautpunkt (größtes z) im Umkreis um (x, y) — oder −1. */
    static vorderster(punkte, haut, x, y, umkreis) {
        let best = -1, bestZ = -Infinity;
        const r2 = umkreis * umkreis;
        for (let i = 0; i < haut.length; i++) {
            const e = haut[i];
            const dx = punkte[3 * e] - x, dy = punkte[3 * e + 1] - y;
            if (dx * dx + dy * dy > r2) continue;
            const z = punkte[3 * e + 2];
            if (z > bestZ) { bestZ = z; best = e; }
        }
        return best;
    }

    /**
     * Der Anker beider Brauen: je Bogenpunkt Seite, Hautpunkt darunter und
     * der Versatz (x, y) zu ihm — bestimmt vom Auge aus, siehe `bogen`.
     * @returns {Array<{seite: number, wurzel: number, dx: number, dy: number, t: number}>}
     */
    static anker(punkte, index, gruppen) {
        const haut = Augenbrauen.ecken(index, gruppen, Augenbrauen.GRUPPE.haut);
        const sklera = Augenbrauen.ecken(index, gruppen, Augenbrauen.GRUPPE.sklera);
        const auge = Augenbrauen.augen(punkte, sklera);
        const aus = [];
        for (const [seite, mitte] of [[-1, auge.links], [1, auge.rechts]]) {
            for (const b of Augenbrauen.bogen(punkte, haut, mitte, seite)) {
                aus.push({ seite, wurzel: b.wurzel, t: b.t,
                           dx: b.p[0] - punkte[3 * b.wurzel], dy: b.p[1] - punkte[3 * b.wurzel + 1] });
            }
        }
        return aus;
    }

    /**
     * Die Streifen beider Brauen als Geometrie.
     * @param {Float32Array} punkte  Körperpunkte (aktuelle Lage, Netzraum)
     * @param {ArrayLike<number>} index  voller Dreiecksindex des Körpers
     * @param {Array<{start,count,materialIndex}>} gruppen
     * @param {number} staerke  1 = Vorgabe; skaliert Länge und Breite
     * @param anker  gemerkter Anker (`anker()`); ohne ihn wird er hier bestimmt
     * @returns {{positionen: Float32Array, index: Uint32Array, wurzeln: Uint32Array,
     *            haare: number, anker: object[]}}
     */
    static bauen(punkte, index, gruppen, staerke = 1, anker = null) {
        const a = anker || Augenbrauen.anker(punkte, index, gruppen);
        const streifen = a.map(({ seite, wurzel, dx, dy, t }) => Augenbrauen.streifen(
            { p: [punkte[3 * wurzel] + dx, punkte[3 * wurzel + 1] + dy, punkte[3 * wurzel + 2]],
              wurzel, t }, seite, staerke));
        return { ...Augenbrauen.geometrie(streifen), anker: a };
    }

    /**
     * Ein Streifen: Wurzel auf dem Bogen, Spitze nach außen (Seite) und nach
     * oben geneigt, leicht vor der Haut; innen lang, außen kurz.
     * @returns {{ecken: number[][], wurzel: number}}
     */
    static streifen({ p, wurzel, t }, seite, staerke, haar = Augenbrauen.HAAR) {
        const laenge = (haar.laengeInnen + t * (haar.laengeAussen - haar.laengeInnen)) * staerke;
        const breite = haar.breite * Math.sqrt(staerke);
        // Richtung: nach außen (x) mit Neigung nach oben (y), normiert.
        const n = Math.hypot(1, haar.neigung);
        const rx = seite / n, ry = haar.neigung / n;
        // Quer zur Richtung, in der Hautebene (x/y), für die Breite — mit
        // `seite` gespiegelt, damit links und rechts Ecke für Ecke
        // symmetrisch sind (das Material ist beidseitig, die Wicklung egal).
        const qx = -ry * seite, qy = rx * seite;
        const z = p[2] + haar.abstand;
        const w = [p[0], p[1], z];
        const s = [p[0] + rx * laenge, p[1] + ry * laenge, z + haar.abstand];
        const h = breite / 2;
        return { wurzel, ecken: [
            [w[0] + qx * h, w[1] + qy * h, w[2]], [w[0] - qx * h, w[1] - qy * h, w[2]],
            [s[0] - qx * h * 0.4, s[1] - qy * h * 0.4, s[2]], [s[0] + qx * h * 0.4, s[1] + qy * h * 0.4, s[2]],
        ] };
    }

    /** Alle Streifen in einen Puffer: 4 Ecken, 2 Dreiecke je Streifen. */
    static geometrie(streifen) {
        const positionen = new Float32Array(streifen.length * 12);
        const index = new Uint32Array(streifen.length * 6);
        const wurzeln = new Uint32Array(streifen.length * 4);
        streifen.forEach((s, k) => {
            for (let e = 0; e < 4; e++) {
                positionen.set(s.ecken[e], 12 * k + 3 * e);
                wurzeln[4 * k + e] = s.wurzel;
            }
            const a = 4 * k;
            index.set([a, a + 1, a + 2, a, a + 2, a + 3], 6 * k);
        });
        return { positionen, index, wurzeln, haare: streifen.length };
    }
}
