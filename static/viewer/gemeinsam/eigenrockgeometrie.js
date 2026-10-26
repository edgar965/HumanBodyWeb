import * as THREE from 'three';
import { Eigenrockhuelle } from './eigenrockhuelle.js';

/**
 * Eigenrockgeometrie — das Netz eines eigenen Rocks (oder des Rockteils eines Kleids) aus der Haut der Figur (Stufe K3, 25.10.2026 nachts). Im Speicher, ohne Server.
 *
 * AUFBAU: `ZEILEN` + 1 Ringe vom Bund (Rumpf-Anteil `bund` der Körperkoordinaten) bis zum Saum (Bein-Anteil `laenge`), je `SPALTEN` Punkte um die Achse (Mitte des
 * Rumpfs am Bund) plus eine Nahtspalte (gleiche Lage, UV bis zum Umfang). Halbmesser = Hülle der Haut in dieser Höhe (`Eigenrockhuelle`, zwischen den Beinen
 * gespannt); ab der breitesten Zeile (Hüfte, Gesäß) abwärts nie enger als darüber — der Rock hängt von dort, er folgt den Beinen nicht nach innen. Dazu Sitz, ab der
 * Hüfte die A-Linie (`weite` vorn/hinten/seitlich am Saum, linear) und eingelegte Falten (`falten`: Anzahl, Tiefe am Saum) als Startform fürs Drapieren
 * (`Eigenrockdrapieren`). UV in Metern (Umfang, Länge) → `uvMeter` = 1 für den Stoff.
 * HAUTGEWICHTE je Punkt: Mittel der äußersten Hautpunkte der Hülle in dieser Höhe (`stuetze`) über ein Fenster von Richtungen, das zum Saum hin wächst — vorn und
 * hinten in der Mitte mischen sich so linkes und rechtes Bein, der Rock reißt beim Schritt nicht auf.
 */
export class Eigenrockgeometrie {

    /** 41 × 96 Punkte: mit 49 × 121 rechnete das Drapieren 2,7 s (240 Schritte, GPU und CPU durch einen Kettenlauf belegt, 25.10.2026). */
    static ZEILEN = 40;
    static SPALTEN = 96;
    /** Toleranz im Anteil der Körperkoordinaten, mit der Bund und Saum ihre Höhe suchen (verdoppelt, bis Punkte da sind). */
    static BAND = 0.01;
    /** Fenster der Hautgewichte in Richtungen (Fächer der Hülle): am Bund, dazu bis zum Saum. */
    static FENSTER = [2, 14];

    /** Mittlere Höhe (m) der Hautpunkte der Ketten `ketten` mit Komponente `k` von `kkKoord` ≈ `wert` (1 = Anteil entlang der Kette, 2 = Rumpfhöhe 0 = Halsansatz
     *  … 1 = Schritt — der Rumpf trägt im Anteil nur den Armanteil an der Schulter, sonst −0,5); null ohne Treffer. */
    static hoehe(pos, koord, ketten, wert, k = 1) {
        for (let band = Eigenrockgeometrie.BAND; band < 0.2; band *= 2) {
            let s = 0, n = 0;
            for (let i = 0; i < koord.length / 4; i++) {
                if (!ketten.includes(Math.round(koord[4 * i])) || Math.abs(koord[4 * i + k] - wert) > band) continue;
                s += pos[3 * i + 1]; n++;
            }
            if (n >= 8) return s / n;
        }
        return null;
    }

    /** [x, z] der Achse: Mitte der Rumpfpunkte in Bundhöhe (Rumpfhöhe ≈ `bund`). */
    static mitte(pos, koord, bund) {
        let x = 0, z = 0, n = 0;
        for (let i = 0; i < koord.length / 4; i++) {
            if (Math.round(koord[4 * i]) !== 1 || Math.abs(koord[4 * i + 2] - bund) > 4 * Eigenrockgeometrie.BAND) continue;
            x += pos[3 * i]; z += pos[3 * i + 2]; n++;
        }
        return n ? [x / n, z / n] : [0, 0];
    }

    /**
     * @param schale  BufferGeometry mit `position`, `kkKoord`, `skinIndex`, `skinWeight` (`Eigenkleidgeometrie`)
     * @param w       `{bund, laenge, sitz (m), weite: [vorn, hinten, seitlich] (m), falten: [Anzahl, Tiefe m]}`
     * @returns `{geo, huelle, zeilen, spalten, breit, ySaum, ms}` oder null (Bund oder Saum nicht gefunden, Saum über dem Bund)
     */
    static bauen(schale, w) {
        const t0 = performance.now(), Z = Eigenrockgeometrie.ZEILEN, S = Eigenrockgeometrie.SPALTEN;
        const a = schale.attributes, pos = a.position.array, koord = a.kkKoord.array;
        const yBund = Eigenrockgeometrie.hoehe(pos, koord, [1], w.bund, 2), ySaum = Eigenrockgeometrie.hoehe(pos, koord, [4, 5], w.laenge, 1);
        if (yBund === null || ySaum === null || ySaum > yBund - 0.05) return null;
        let boden = Infinity;
        for (let i = 1; i < pos.length; i += 3) boden = Math.min(boden, pos[i]);
        const mitte = Eigenrockgeometrie.mitte(pos, koord, w.bund);
        const huelle = new Eigenrockhuelle(pos, koord, yBund + 0.01, Math.max(boden, ySaum - 0.3), mitte);
        huelle.zugabe = w.sitz;
        const r = new Float32Array((Z + 1) * S), y = new Float32Array(Z + 1);
        let breit = 0, best = -1;
        for (let z = 0; z <= Z; z++) {
            y[z] = yBund - (yBund - ySaum) * z / Z;
            let summe = 0;
            for (let s = 0; s < S; s++) summe += (r[z * S + s] = huelle.halbmesser(y[z], s / S));
            if (summe > best) { best = summe; breit = z; }
        }
        for (let z = breit + 1; z <= Z; z++) for (let s = 0; s < S; s++) r[z * S + s] = Math.max(r[z * S + s], r[(z - 1) * S + s]);
        const p = new Float32Array((Z + 1) * (S + 1) * 3), uv = new Float32Array((Z + 1) * (S + 1) * 2);
        const umfang = 2 * Math.PI * best / S;
        for (let z = 0; z <= Z; z++) {
            const t = z <= breit ? 0 : (z - breit) / (Z - breit);
            for (let s = 0; s <= S; s++) {
                const th = 2 * Math.PI * s / S, c = Math.cos(th), sn = Math.sin(th), k = z * (S + 1) + s;
                const weite = w.weite[0] * Math.max(c, 0) ** 2 + w.weite[1] * Math.max(-c, 0) ** 2 + w.weite[2] * sn * sn;
                const h = r[z * S + s % S];
                const R = Math.max(h + 0.5 * w.sitz, h + w.sitz + t * weite + w.falten[1] * t * Math.sin(Math.round(w.falten[0]) * th));
                p.set([mitte[0] + R * sn, y[z], mitte[1] + R * c], 3 * k);
                uv.set([umfang * s / S, (yBund - y[z])], 2 * k);
            }
        }
        const index = [];
        for (let z = 0; z < Z; z++) {
            for (let s = 0; s < S; s++) {
                const i = z * (S + 1) + s, j = i + S + 1;
                index.push(i, j, i + 1, i + 1, j, j + 1);
            }
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(p, 3));
        geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
        Eigenrockgeometrie._haut(geo, schale, huelle, y, breit);
        geo.setIndex(index);
        Eigenrockgeometrie.normalen(geo, Z, S);
        return { geo, huelle, zeilen: Z, spalten: S, breit, ySaum, ms: performance.now() - t0 };
    }

    /** Hautgewichte je Punkt aus den Stützpunkten der Hülle (Kopf der Datei); die Nahtspalte wie Spalte 0. */
    static _haut(geo, schale, huelle, y, breit) {
        const Z = y.length - 1, S = Eigenrockgeometrie.SPALTEN, W = Eigenrockhuelle.WINKEL, [f0, f1] = Eigenrockgeometrie.FENSTER;
        const ki = schale.attributes.skinIndex.array, kw = schale.attributes.skinWeight.array;
        const idx = new Uint16Array((Z + 1) * (S + 1) * 4), gew = new Float32Array((Z + 1) * (S + 1) * 4);
        for (let z = 0; z <= Z; z++) {
            const t = z <= breit ? 0 : (z - breit) / (Z - breit), fenster = Math.round(f0 + (f1 - f0) * t), sch = huelle.scheibe(y[z]);
            for (let s = 0; s <= S; s++) {
                const summe = new Map(), mitte = Eigenrockhuelle.fach(s / S);
                // ohne Stützpunkt im Fenster (Hüllkante zwischen den Beinen) weiter: erst breiter, dann die Scheiben darüber (gemessen DamiraAlt: 544 Punkte ohne Gewicht)
                for (let f = fenster, sc = sch; !summe.size && sc >= 0; f < W / 2 ? f *= 2 : (f = fenster, sc--)) {
                    for (let d = -f; d <= f; d++) {
                        const h = huelle.stuetze[sc * W + (mitte + d + 2 * W) % W];
                        if (h < 0) continue;
                        for (let k = 0; k < 4; k++) summe.set(ki[4 * h + k], (summe.get(ki[4 * h + k]) || 0) + kw[4 * h + k]);
                    }
                }
                const beste = [...summe].filter(([, v]) => v > 0).sort((u, v) => v[1] - u[1]).slice(0, 4);
                const gesamt = beste.reduce((q, [, v]) => q + v, 0) || 1, o = 4 * (z * (S + 1) + s);
                beste.forEach(([knochen, v], k) => { idx[o + k] = knochen; gew[o + k] = v / gesamt; });
            }
        }
        geo.setAttribute('skinIndex', new THREE.BufferAttribute(idx, 4));
        geo.setAttribute('skinWeight', new THREE.BufferAttribute(gew, 4));
    }

    /** Normalen ohne Naht: Spalte 0 und die Nahtspalte bekommen ihre gemeinsame. */
    static normalen(geo, Z, S) {
        geo.computeVertexNormals();
        const n = geo.attributes.normal.array, v = new THREE.Vector3();
        for (let z = 0; z <= Z; z++) {
            const a = 3 * z * (S + 1), b = 3 * (z * (S + 1) + S);
            v.set(n[a] + n[b], n[a + 1] + n[b + 1], n[a + 2] + n[b + 2]).normalize();
            n.set([v.x, v.y, v.z], a);
            n.set([v.x, v.y, v.z], b);
        }
        geo.attributes.normal.needsUpdate = true;
    }
}
