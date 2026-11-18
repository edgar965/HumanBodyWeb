/**
 * Stueckschweissung — ein grobes Stück für die Hautmaske verschweißen und verfeinern (18.11.2026).
 *
 * MH Joachip Cyborg Suit (Edgar, 18.11.2026: „passt sich nicht an Fran an, Brüste sichtbar"), gemessen an Luna:
 *   1. 5.791 Punkte auf 2.380 Dreiecke — jede Platte hat eigene Punkte (harte Kanten). Für die Hautmaske war jede Kante eine Randkante, jeder Punkt ein
 *      lockerer Randpunkt (die Platten haben Luft zur Haut): `RANDRINGE` Ringe um alle gesperrt, kein Dreieck erlaubt, die Maske leer (0 von 104.480
 *      Körperpunkten). Verschweißt (Lage auf 1e-5 m): 944 Punkte, 18 Randkanten.
 *   2. Kanten im Median 100 mm, p90 209 mm. Die Maske prüft nur die Dreiecke um den NÄCHSTEN Stoffpunkt im Umkreis `max(ABSTAND_M, tiefe, NAHE_M)` —
 *      bei so großen Platten liegt dort meist keiner: verschweißt deckte die Maske 2.946 Punkte, an der Brust 74 von 3.431, Brust und Bauch stachen weiter
 *      durch die flachen Platten.
 * Jetzt bekommt die Maske (Browser und Server bekommen dasselbe, `Hautmaskenvorrat`) solche Stücke verschweißt und verfeinert. Ein gewöhnliches Netz
 * (etwa halb so viele Punkte wie Dreiecke, Kanten um 5–15 mm) bleibt, wie es ist. Ersatzstücke verschweißt `Stueckrand` selbst.
 *
 * VERFEINERT WERDEN DIE LANGEN KANTEN (`teilen`), nicht alle: Bis zum Abend des 18.11.2026 wurde jedes Dreieck dreimal geviertelt (152.320 Dreiecke).
 * Splitter blieben Splitter — an Luna stachen danach 141 Hautpunkte oben an der Brust durch die Platte, ohne Maske: Der Strahl traf die Platte 4–9 mm
 * hinter der Haut, aber in Dreiecken mit Kanten von 35–41 mm bei 2–4 mm Breite, deren Ecken 11–29 mm entfernt lagen, mehr als zwei Ringe vom nächsten
 * Stoffpunkt (10,5 mm). Jetzt wird jede Kante über `ZIEL_M` halbiert, je Dreieck nach der Zahl seiner geteilten Kanten in zwei, drei oder vier
 * (die Mitte gehört der Kante, beide Nachbarn teilen sie — keine T-Stellen), bis keine länger ist, höchstens `STUFEN_MAX` mal.
 */
export class Stueckschweissung {

    /** Ab so vielen Punkten je Dreieck teilen die Flächen keine Punkte (Cyborg Suit 2,43; ein gewöhnliches Netz um 0,5). */
    static VERHAELTNIS = 1.2;

    /** Raster der Lage: 1e-5 m. */
    static RASTER = 1e5;

    /** Mittlere Kante, ab der verfeinert wird (Meter), und die längste Kante danach. */
    static GROB_M = 0.025;
    static ZIEL_M = 0.015;
    /** Höchstens so viele Durchgänge (jeder halbiert die langen Kanten: 400 mm → 12,5 mm in fünf) und so viele Dreiecke. */
    static STUFEN_MAX = 6;
    static DREIECKE_MAX = 400000;

    /** `{punkte, dreiecke}` für die Maske — dieselben Felder, wenn nichts zu tun ist. */
    static netz(punkte, dreiecke, ersatz = false) {
        if (ersatz || !dreiecke?.length) return { punkte, dreiecke };
        let netz = { punkte, dreiecke };
        if (punkte.length / 3 > Stueckschweissung.VERHAELTNIS * dreiecke.length / 3) netz = Stueckschweissung.schweissen(punkte, dreiecke);
        if (Stueckschweissung.mittlereKante(netz.punkte, netz.dreiecke) <= Stueckschweissung.GROB_M) return netz;
        for (let s = 0; s < Stueckschweissung.STUFEN_MAX && netz.dreiecke.length / 3 < Stueckschweissung.DREIECKE_MAX; s++) {
            const neu = Stueckschweissung.teilen(netz.punkte, netz.dreiecke, Stueckschweissung.ZIEL_M);
            if (neu.dreiecke.length === netz.dreiecke.length) break;
            netz = neu;
        }
        return netz;
    }

    /** Punkte mit derselben Lage (auf 1e-5 m) werden einer. */
    static schweissen(punkte, dreiecke) {
        const n = punkte.length / 3, neu = new Int32Array(n), lage = new Map(), aus = [], r = Stueckschweissung.RASTER;
        for (let i = 0; i < n; i++) {
            const k = `${Math.round(punkte[3 * i] * r)},${Math.round(punkte[3 * i + 1] * r)},${Math.round(punkte[3 * i + 2] * r)}`;
            let j = lage.get(k);
            if (j === undefined) {
                j = aus.length / 3;
                lage.set(k, j);
                aus.push(punkte[3 * i], punkte[3 * i + 1], punkte[3 * i + 2]);
            }
            neu[i] = j;
        }
        const d = new Uint32Array(dreiecke.length);
        for (let t = 0; t < dreiecke.length; t++) d[t] = neu[dreiecke[t]];
        return { punkte: Float32Array.from(aus), dreiecke: d };
    }

    /** Mittlere Kantenlänge, geschätzt an jedem siebten Dreieck. */
    static mittlereKante(p, d) {
        let summe = 0, zahl = 0;
        for (let t = 0; t < d.length; t += 21) {
            for (let k = 0; k < 3; k++) {
                const a = 3 * d[t + k], b = 3 * d[t + (k + 1) % 3];
                summe += Math.hypot(p[a] - p[b], p[a + 1] - p[b + 1], p[a + 2] - p[b + 2]);
                zahl++;
            }
        }
        return zahl ? summe / zahl : 0;
    }

    /**
     * Ein Durchgang: Jede Kante über `laenge` bekommt ihre Mitte; ein Dreieck mit einer geteilten Kante wird zu zwei, mit zweien zu drei, mit dreien zu
     * vier — immer in seiner Umlaufrichtung. Ob eine Kante geteilt wird, hängt nur an ihren Ecken, beide Nachbarn sehen also dieselbe Mitte.
     */
    static teilen(p, d, laenge) {
        const n = p.length / 3, l2 = laenge * laenge, mitten = new Map(), aus = Array.from(p), neu = [];
        const mitte = (a, b) => {
            if ((p[3 * a] - p[3 * b]) ** 2 + (p[3 * a + 1] - p[3 * b + 1]) ** 2 + (p[3 * a + 2] - p[3 * b + 2]) ** 2 <= l2) return -1;
            const k = a < b ? a * n + b : b * n + a;
            let j = mitten.get(k);
            if (j === undefined) {
                j = aus.length / 3;
                mitten.set(k, j);
                aus.push((p[3 * a] + p[3 * b]) / 2, (p[3 * a + 1] + p[3 * b + 1]) / 2, (p[3 * a + 2] + p[3 * b + 2]) / 2);
            }
            return j;
        };
        for (let t = 0; t < d.length; t += 3) {
            const v = [d[t], d[t + 1], d[t + 2]], m = [mitte(v[0], v[1]), mitte(v[1], v[2]), mitte(v[2], v[0])];   // m[k] auf der Kante v[k] → v[k+1]
            const zahl = (m[0] >= 0) + (m[1] >= 0) + (m[2] >= 0);
            if (!zahl) {
                neu.push(v[0], v[1], v[2]);
            } else if (zahl === 3) {
                neu.push(v[0], m[0], m[2], m[0], v[1], m[1], m[2], m[1], v[2], m[0], m[1], m[2]);
            } else if (zahl === 1) {
                const k = m.findIndex((x) => x >= 0), a = v[k], b = v[(k + 1) % 3], c = v[(k + 2) % 3];
                neu.push(a, m[k], c, m[k], b, c);
            } else {
                const k = m.findIndex((x) => x < 0), a = v[k], b = v[(k + 1) % 3], c = v[(k + 2) % 3];     // a → b bleibt ganz
                const bc = m[(k + 1) % 3], ca = m[(k + 2) % 3];
                neu.push(ca, bc, c, a, b, bc, a, bc, ca);
            }
        }
        return { punkte: Float32Array.from(aus), dreiecke: Uint32Array.from(neu) };
    }
}
