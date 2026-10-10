/**
 * Stueckhautrechnung — wie weit ein verschweißtes Ersatzstück (Scham aus einer .blend) an der Naht in die Haut übergeht (09.10.2026).
 *
 * WARUM (Edgar, 09.10.2026, mit Bild: „die Texturanpassung an die Umgebung, warum machst du keine Interpolation der Textur?"; Chrome,
 * „cute girl"): Der Rand des Stücks liegt auf dem Ring der Haut, die Normalen gehen dort in die der Haut über (`stucknormalen.js`) —
 * aber das Stück bleibt ein eigenes Material: Farbe aus der Karte des Originals, kein Durchlicht (die Haut hat es,
 * `genesis9haut.js`: Gewicht 0,85, `dicke` je Punkt). Gemessen 09.10.2026 an „cute girl", Stück gegen Haut am selben Ort, Texturfarbe
 * ohne Licht (439 Punkte): Median 205/144/129 zu 200/152/133 (Verhältnis 1,01/0,99/0,99), im untersten Band (270 Punkte) 0,93 im
 * Grün — klein, aber an der Naht ein Sprung.
 *
 * HIER (ohne Three.js, Node-Test `test_js_stueckhaut.py`): je Punkt des Stücks (1) die Farbe der Haut an dieser Stelle — der Mittelwert
 * der nächsten Hautpunkte (höchstens `K`, `SUCH_M` weit), jeder mit der Farbe seiner eigenen Karte (`haut.farbe(j)`), (2) das Maß, in dem
 * das Stück sie annimmt, (3) die Dünnheit (`dicke`) des nächsten Hautpunkts für das Durchlicht. Die FARBE wird gemittelt, nicht die UV:
 * die UV der Haut springt an einer Naht der Karte (am Damm läuft eine), und eine UV zwischen zwei Inseln zeigt auf eine fremde Stelle
 * (erster Versuch mit UV je Punkt: an der Naht null Überblendung, gesehen im Chrome 09.10.2026). Das Maß ist 1 am Rand und klingt über
 * `BAND_M` (Weg über das Netz) aus; es zählt nur, wo das Stück AUF der Haut liegt: steht es klar davor (Schamlippen, mehr als
 * `FLUSH_AUS_M` über der Tangentialebene der Haut), bleibt seine eigene Farbe.
 */
export class Stueckhautrechnung {

    /** So weit (m) vom Rand (Weg über das Netz des Stücks) reicht die Überblendung in die Hautfarbe — gleich `Stuecknaht.BAND_M`. */
    static BAND_M = 0.014;
    /** Bis zu diesem Abstand (m) des Stücks von der Tangentialebene der Haut ist die Überblendung voll, ab `FLUSH_AUS_M` null. */
    static FLUSH_VOLL_M = 0.002;
    static FLUSH_AUS_M = 0.006;
    /** So weit (m) darf ein Hautpunkt höchstens entfernt sein, um mitzuzählen; die nächsten `K` zählen. */
    static SUCH_M = 0.012;
    static K = 4;
    /** Dämpfung der Gewichte 1/(d² + EPS²). */
    static EPS_M = 0.001;

    /**
     * @param punkte      Punkte des Stücks (Ruhelage, schon um den Randversatz gerückt), xyz
     * @param naht        Ergebnis von `Stuecknaht.verschiebung`: `weg` (Weg zum Rand, `Infinity` jenseits des Bands)
     * @param haut        `{pos, normal, dicke|null, farbe: (j) => [r, g, b] (linear)}` — Punkte, Normalen, Dünnheit der Haut, Farbe der Karte
     * @returns {{farbe: Float32Array, misch: Float32Array, dicke: Float32Array|null, mitFarbe: number}}
     */
    static rechnen(punkte, naht, haut) {
        const R = Stueckhautrechnung, n = punkte.length / 3;
        const gitter = R._gitter(punkte, haut.pos);
        const farbe = new Float32Array(3 * n), misch = new Float32Array(n);
        const dicke = haut.dicke ? new Float32Array(n) : null;
        const eps2 = R.EPS_M * R.EPS_M;
        let mitFarbe = 0;
        for (let i = 0; i < n; i++) {
            const nah = R._naechste(gitter, haut.pos, punkte, i);
            if (!nah.length) continue;
            const j = nah[0].j;
            if (dicke) dicke[i] = haut.dicke[j];
            let sw = 0;
            for (const { j: k, d2 } of nah) {
                const w = 1 / (d2 + eps2), c = haut.farbe(k);
                farbe[3 * i] += w * c[0]; farbe[3 * i + 1] += w * c[1]; farbe[3 * i + 2] += w * c[2]; sw += w;
            }
            farbe[3 * i] /= sw; farbe[3 * i + 1] /= sw; farbe[3 * i + 2] /= sw;
            if (!(naht.weg && naht.weg[i] < R.BAND_M)) continue;
            const t = Math.abs((punkte[3 * i] - haut.pos[3 * j]) * haut.normal[3 * j] + (punkte[3 * i + 1] - haut.pos[3 * j + 1]) * haut.normal[3 * j + 1]
                               + (punkte[3 * i + 2] - haut.pos[3 * j + 2]) * haut.normal[3 * j + 2]);
            misch[i] = R._glatt(1 - (t - R.FLUSH_VOLL_M) / (R.FLUSH_AUS_M - R.FLUSH_VOLL_M)) * R._glatt(1 - naht.weg[i] / R.BAND_M);
            if (misch[i] > 0) mitFarbe++;
        }
        return { farbe, misch, dicke, mitFarbe };
    }

    /** Hermite 0…1 mit Klemmung: 1 für `t ≥ 1`, 0 für `t ≤ 0`. */
    static _glatt(t) {
        const x = Math.min(1, Math.max(0, t));
        return x * x * (3 - 2 * x);
    }

    /** Raster der Hautpunkte um das Stück (Zelle `SUCH_M`). */
    static _gitter(punkte, pos) {
        const z = Stueckhautrechnung.SUCH_M, lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < punkte.length; i += 3) for (let c = 0; c < 3; c++) { lo[c] = Math.min(lo[c], punkte[i + c]); hi[c] = Math.max(hi[c], punkte[i + c]); }
        const zellen = new Map();
        for (let j = 0; j < pos.length / 3; j++) {
            const x = pos[3 * j], y = pos[3 * j + 1], zz = pos[3 * j + 2];
            if (x < lo[0] - z || x > hi[0] + z || y < lo[1] - z || y > hi[1] + z || zz < lo[2] - z || zz > hi[2] + z) continue;
            const k = `${Math.floor(x / z)},${Math.floor(y / z)},${Math.floor(zz / z)}`;
            if (!zellen.has(k)) zellen.set(k, []);
            zellen.get(k).push(j);
        }
        return zellen;
    }

    /** Die `K` nächsten Hautpunkte zum Punkt `i` des Stücks (höchstens `SUCH_M` weit), nächster zuerst: `[{j, d2}]`. */
    static _naechste(gitter, pos, punkte, i) {
        const R = Stueckhautrechnung, z = R.SUCH_M, x = punkte[3 * i], y = punkte[3 * i + 1], zz = punkte[3 * i + 2];
        const cx = Math.floor(x / z), cy = Math.floor(y / z), cz = Math.floor(zz / z);
        const liste = [];
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            const zelle = gitter.get(`${cx + a},${cy + b},${cz + c}`);
            if (!zelle) continue;
            for (const j of zelle) {
                const d2 = (pos[3 * j] - x) ** 2 + (pos[3 * j + 1] - y) ** 2 + (pos[3 * j + 2] - zz) ** 2;
                if (d2 < z * z) liste.push({ j, d2 });
            }
        }
        liste.sort((p, q) => p.d2 - q.d2);
        return liste.slice(0, R.K);
    }
}
