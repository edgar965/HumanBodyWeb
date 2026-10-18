/**
 * Kleiderknochen — Stücke ohne Hautbindung (Haar, Requisiten, freie Stoffteile) folgen einem neuen Körper über ihre KNOCHEN,
 * noch bevor der Server ihre genaue Lage liefert.
 *
 * WARUM (Edgar, 17.10.2026: „posen dauern irrsinnig lange, das sollte doch in 1 s gehen" — dann „mach erst … Sofortschau"): Nach einer
 * Daz-Pose steht der neue Körper nach 1,4 s, Shirt und Shorts folgen ihm über ihre Bindung an die Körperdreiecke (`Kleidervorschau`).
 * Das Haar hat keine solche Bindung: Bei „03 Laying Back" schwebte es 1,8 s nach dem Klick noch an der alten Kopfstelle, bis seine
 * eigene Antwort nach rund 10 s kam (im Chrome gesehen, fünf Stücke an Ursula).
 *
 * Die Knochen tragen ihre volle Lage (Gelenk UND Drehung, aus der Antwort des Servers). Je Knochen ist `neu · alt⁻¹` die Bewegung von der
 * alten zur neuen Stellung; jeder Punkt eines Stücks wandert um die mit seinen Hautgewichten gemischte Bewegung — lineares Skinning, wie die
 * Figur selbst animiert wird. Gelesen wird die Lage beim BINDEN (`boneInverses`, im Raum der Figurgruppe, `Knochenbau.ruhelagen`): Die
 * Punkte eines Stücks stehen in dieser Lage — nicht in der, in die eine Vorschau oder Animation die Knochen gerade gedreht hat.
 * Ihre Achsen leitet der Bauplan aus den Gelenken her (`Gelenkskelett.bauplan`), die Verdrehung eines Knochens fehlt ihnen; genauer sind
 * die Daz-Wege des Servers (`ausServer`, von `Genesis9posenvorschau` geholt), wenn sie für genau diesen Zug gelten.
 *
 * Matrizen wie in Three.js: 16 Zahlen, spaltenweise. Ohne Importe — `test_js_kleiderknochen` rechnet in Node.
 */
export class Kleiderknochen {

    /**
     * Lage jedes Knochens beim Binden, im Raum der Figurgruppe — `Map(Name → 16 Zahlen)`, oder null ohne Skelett.
     * VOR dem Neuaufbau aufrufen: danach gibt es die alten Knochen nicht mehr.
     */
    static lagen(inst) {
        const knochen = inst?.skelett?.bones, umkehr = inst?.skelett?.skeleton?.boneInverses;
        if (!knochen?.length || umkehr?.length !== knochen.length) return null;
        const lagen = new Map();
        knochen.forEach((k, i) => lagen.set(k.name, Kleiderknochen.umkehren(umkehr[i].elements)));
        return lagen;
    }

    /**
     * Die Daz-Wege des Servers (`{Name: 16 Zahlen}`) für jeden Knochen des NEUEN Skeletts — ein Knochen ohne eigenen Weg (Zunge,
     * Zöpfe eines Stücks, Endknochen) nimmt den seines nächsten Vorfahren. `Map` wie `wege`, oder null.
     */
    static ausServer(wege, inst) {
        const knochen = inst?.skelett?.bones;
        if (!wege || !knochen?.length) return null;
        const aus = new Map();
        for (const k of knochen) {
            let weg = null;
            for (let b = k; b?.isBone && !weg; b = b.parent) weg = wege[b.name] || null;
            if (weg) aus.set(k.name, weg);
        }
        return aus.size ? aus : null;
    }

    /** Je Knochen die Bewegung `neu · alt⁻¹` — `Map(Name → 16 Zahlen)`; null, wenn nichts gemerkt ist. */
    static wege(alt, inst) {
        if (!alt?.size) return null;
        const neu = Kleiderknochen.lagen(inst);
        if (!neu) return null;
        const wege = new Map();
        for (const [name, lage] of neu) {
            const vorher = alt.get(name);
            if (vorher) wege.set(name, Kleiderknochen.mal(lage, Kleiderknochen.umkehren(vorher)));
        }
        return wege.size ? wege : null;
    }

    /**
     * Die Punkte eines gebundenen Netzes um die gemischte Knochenbewegung verschieben.
     * @param anteil  `(i) => 0…1`, wie viel der Bewegung Punkt i bekommt (null = alles) — der Rest gehört der Oberflächenbindung
     * @returns Zahl der bewegten Punkte
     */
    static haeuten(netz, wege, anteil = null) {
        const geo = netz?.geometry;
        const index = geo?.attributes?.skinIndex?.array, gewicht = geo?.attributes?.skinWeight?.array;
        const knochen = netz?.skeleton?.bones;
        const position = geo?.attributes?.position;
        if (!wege || !index || !gewicht || !knochen || !position) return 0;
        const zu = knochen.map(k => wege.get(k.name) || null);
        const p = position.array;
        const m = new Float64Array(12);
        let bewegt = 0;
        for (let i = 0; i < position.count; i++) {
            const r = anteil ? anteil(i) : 1;
            if (!(r > 0)) continue;
            m.fill(0);
            let summe = 0;
            for (let j = 0; j < 4; j++) {
                const w = gewicht[4 * i + j];
                if (!(w > 0)) continue;
                summe += w;
                const x = zu[index[4 * i + j]];
                if (!x) { m[0] += w; m[5] += w; m[10] += w; continue; }      // Knochen ohne Bewegung: bleibt
                for (const [k, e] of Kleiderknochen.FELDER) m[k] += w * x[e];
            }
            if (summe < 1e-6) continue;
            const x = p[3 * i], y = p[3 * i + 1], z = p[3 * i + 2];
            const nx = (m[0] * x + m[4] * y + m[8] * z + m[1]) / summe;
            const ny = (m[2] * x + m[5] * y + m[9] * z + m[3]) / summe;
            const nz = (m[6] * x + m[7] * y + m[10] * z + m[11]) / summe;
            p[3 * i] = x + r * (nx - x);
            p[3 * i + 1] = y + r * (ny - y);
            p[3 * i + 2] = z + r * (nz - z);
            bewegt++;
        }
        if (bewegt) {
            position.needsUpdate = true;
            geo.boundingSphere = null;
            geo.boundingBox = null;
        }
        return bewegt;
    }

    /**
     * Welche der 12 Mischfelder aus welchem Matrixeintrag (spaltenweise) kommt: Drehteil und Verschiebung.
     * Belegung des Mischfelds: 0 m00, 4 m01, 8 m02, 1 t_x · 2 m10, 5 m11, 9 m12, 3 t_y · 6 m20, 7 m21, 10 m22, 11 t_z.
     */
    static FELDER = [[0, 0], [4, 4], [8, 8], [1, 12], [2, 1], [5, 5], [9, 9], [3, 13], [6, 2], [7, 6], [10, 10], [11, 14]];

    /** `a · b` zweier 4×4 (spaltenweise). */
    static mal(a, b) {
        const aus = new Float64Array(16);
        for (let spalte = 0; spalte < 4; spalte++) {
            for (let zeile = 0; zeile < 4; zeile++) {
                let s = 0;
                for (let k = 0; k < 4; k++) s += a[k * 4 + zeile] * b[spalte * 4 + k];
                aus[spalte * 4 + zeile] = s;
            }
        }
        return aus;
    }

    /** Die Umkehrung einer affinen 4×4 (spaltenweise): Drehteil invertiert, Verschiebung zurück. */
    static umkehren(m) {
        const [a, b, c, d, e, f, g, h, i] = [m[0], m[4], m[8], m[1], m[5], m[9], m[2], m[6], m[10]];
        const A = e * i - f * h, B = -(d * i - f * g), C = d * h - e * g;
        const det = a * A + b * B + c * C;
        const aus = new Float64Array(16);
        if (Math.abs(det) < 1e-12) { aus[0] = aus[5] = aus[10] = aus[15] = 1; return aus; }
        const inv = [A, -(b * i - c * h), b * f - c * e,
                     B, a * i - c * g, -(a * f - c * d),
                     C, -(a * h - b * g), a * e - b * d].map(v => v / det);
        // inv zeilenweise: [r0c0, r0c1, r0c2, r1c0, …]
        aus[0] = inv[0]; aus[4] = inv[1]; aus[8] = inv[2];
        aus[1] = inv[3]; aus[5] = inv[4]; aus[9] = inv[5];
        aus[2] = inv[6]; aus[6] = inv[7]; aus[10] = inv[8];
        const tx = m[12], ty = m[13], tz = m[14];
        aus[12] = -(aus[0] * tx + aus[4] * ty + aus[8] * tz);
        aus[13] = -(aus[1] * tx + aus[5] * ty + aus[9] * tz);
        aus[14] = -(aus[2] * tx + aus[6] * ty + aus[10] * tz);
        aus[15] = 1;
        return aus;
    }
}
