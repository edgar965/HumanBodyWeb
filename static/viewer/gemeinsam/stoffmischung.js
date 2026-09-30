import { base64ToFloat32, base64ToUint32 } from './kodierung.js';

/**
 * Stoffmischung — der Stoffschwung (dForce) eines GEMISCHTEN Stücks aus „Kleidung – Generisch".
 *
 * Edgar, 30.09.2026: „Stoffschwung (dForce) … mischen nicht — beheb das". Der Stoffschwung rechnet auf dem KÄFIG des
 * ursprünglichen Stücks (`Genesis9/stoff.py`, `stoffarbeiter.js`): Verlet-Teilchen, Unterteilungsmatrix Käfig →
 * Browserpunkte. Ein gemischtes Stück hat andere Punkte — die Fläche ist an der Haut verschoben und dort
 * zugeschnitten, wo ein anderes Stück sie überlässt (`G9kleidmischflaeche`). Käfig und Matrix passen dazu nicht mehr.
 *
 * Deshalb schwingt der Worker weiter das URSPRÜNGLICHE Netz, und hier wird sein Ergebnis übertragen:
 *
 *     Punkt i des gemischten Netzes = Punkt quelle[i] des schwingenden Netzes + Häutung(versatz[i])
 *
 * `quelle` ist der Punkt des ungeschnittenen Netzes, aus dem der bleibende Punkt stammt; `versatz` die Verschiebung
 * durch die Mischung, in der Ruhelage (`teil.stoff.misch`, vom Server: `G9kleidmischflaeche.stoff_misch`). Die
 * Häutung legt den Versatz in die Lage dieses Bildes — nur der lineare Anteil der Knochenmatrizen, ein Versatz ist
 * eine Richtung —, damit er mit dem Körper mitdreht: Die Mischzone am Rumpf bleibt an der Haut, auch wenn sich
 * das Stück bewegt. Wo nichts verschoben wurde (Versatz 0), ist das Ergebnis genau der schwingende Punkt.
 *
 * Ohne Three — läuft im Worker. Die Normalen stammen vom schwingenden Netz: Der Versatz beträgt Millimeter.
 */
export class Stoffmischung {

    /**
     * `teil.stoff.misch` aus der Antwort (base64 oder fertige Puffer des Binärpakets) → `{quelle, versatz}`.
     * @returns {{quelle: Uint32Array, versatz: Float32Array}|null}  null ohne Mischung
     */
    static lesen(misch) {
        if (!misch?.quelle || !misch?.versatz) return null;
        return { quelle: base64ToUint32(misch.quelle), versatz: base64ToFloat32(misch.versatz) };
    }

    /**
     * Die Nachricht `bauen` für den Worker: `misch` samt den Hautgewichten der bleibenden Punkte (aus der Geometrie
     * des Stücks — `skinIndex`/`skinWeight`, je vier).
     * @param {{quelle: Uint32Array, versatz: Float32Array}} misch  `lesen(…)`
     * @param {object} geometrie  `THREE.BufferGeometry` des gemischten, gehäuteten Stücks
     */
    static nachricht(misch, geometrie) {
        const a = geometrie.attributes;
        return { quelle: misch.quelle, versatz: misch.versatz,
                 skinIndex: Uint16Array.from(a.skinIndex.array), skinGewicht: Float32Array.from(a.skinWeight.array) };
    }

    /** Im Worker: aus der Nachricht `nachricht(…)`. */
    constructor(d) {
        this.quelle = d.quelle;
        this.versatz = d.versatz;
        this.index = d.skinIndex;
        this.gewicht = d.skinGewicht;
        this.anzahl = d.quelle.length;
    }

    /** Die Dreiecke des geschnittenen Netzes mit den Nummern des ursprünglichen (für dessen Normalen). */
    dreiecke(geschnitten) {
        return Uint32Array.from(geschnitten, i => this.quelle[i]);
    }

    /**
     * Punkte und Normalen des ursprünglichen Netzes (`pos`, `nrm`, je 3 · Zeilen) → die der bleibenden Punkte.
     * @param {Float32Array} M  Knochenmatrizen dieses Bildes (16 je Knochen, `Stoffhaut.matrizen`)
     */
    anwenden(pos, nrm, M) {
        const { quelle, versatz, index, gewicht, anzahl } = this;
        const p = new Float32Array(3 * anzahl), n = new Float32Array(3 * anzahl);
        for (let i = 0; i < anzahl; i++) {
            const r = 3 * quelle[i], o3 = 3 * i;
            const dx = versatz[o3], dy = versatz[o3 + 1], dz = versatz[o3 + 2];
            let sx = 0, sy = 0, sz = 0;
            if (dx !== 0 || dy !== 0 || dz !== 0) {
                for (let k = 0; k < 4; k++) {
                    const w = gewicht[4 * i + k];
                    if (w === 0) continue;
                    const o = 16 * index[4 * i + k];
                    sx += w * (M[o] * dx + M[o + 4] * dy + M[o + 8] * dz);
                    sy += w * (M[o + 1] * dx + M[o + 5] * dy + M[o + 9] * dz);
                    sz += w * (M[o + 2] * dx + M[o + 6] * dy + M[o + 10] * dz);
                }
            }
            p[o3] = pos[r] + sx; p[o3 + 1] = pos[r + 1] + sy; p[o3 + 2] = pos[r + 2] + sz;
            n[o3] = nrm[r]; n[o3 + 1] = nrm[r + 1]; n[o3 + 2] = nrm[r + 2];
        }
        return { pos: p, nrm: n };
    }
}
