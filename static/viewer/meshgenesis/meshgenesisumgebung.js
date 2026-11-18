/**
 * Meshgenesisumgebung — eine erzeugte Studio-Umgebung (Equirect, HDR) für Materialien, die spiegeln sollen (18.11.2026, Goldprinzessin: Edgar „kleider sind schon gut, es fehlt die
 * Textur an den Kleidern“ — Lack und Gold standen ohne Umgebungskarte flach da, Metall 1 wurde schwarz). Nur Materialien mit `umgebung` in `materialien.json` bekommen sie
 * (`Meshgenesisflaechennetz.materialien`); alle anderen Stücke und die Haut bleiben, wie sie sind.
 *
 * Aufbau (Setzungen, im Tab gewählt): Himmel von 0,22 (Horizont) bis 0,47 (Zenit), Boden 0,07, Hauptfläche vorn oben links (wie das Hauptlicht von `Studioszene`), zwei
 * Streiflichter hinten links/rechts, eine schwache Aufhellung von vorn. three.js wandelt die Equirect-Karte selbst in eine PMREM um (`WebGLCubeUVMaps`), RoomEnvironment fehlt im
 * Vendor-Ordner (Regel `mesh.md`) — darum hier von Hand.
 */
import * as THREE from 'three';

export class Meshgenesisumgebung {
    static _karte = null;

    /** Die gemeinsame Karte (einmal je Seite gebaut). */
    static karte() {
        if (Meshgenesisumgebung._karte) return Meshgenesisumgebung._karte;
        const B = 256, H = 128, daten = new Float32Array(B * H * 4);
        const flaechen = [
            // [Richtung (x, y, z), Halbwinkel in Grad, Stärke]
            [[0.35, 0.65, 0.65], 24, 5.0],
            [[-0.85, 0.25, -0.45], 9, 2.2],
            [[0.85, 0.25, -0.45], 9, 2.2],
            [[0.0, 0.15, 1.0], 35, 0.6],
        ].map(([r, w, s]) => { const l = Math.hypot(...r); return [r.map(x => x / l), Math.cos(w * Math.PI / 180), s]; });
        for (let j = 0; j < H; j++) {
            const breite = ((j + 0.5) / H - 0.5) * Math.PI;
            for (let i = 0; i < B; i++) {
                const laenge = ((i + 0.5) / B - 0.5) * 2 * Math.PI;
                const d = [Math.cos(breite) * Math.cos(laenge), Math.sin(breite), Math.cos(breite) * Math.sin(laenge)];
                let w = d[1] >= 0 ? 0.22 + 0.25 * d[1] : 0.07 + 0.15 * Math.max(0, 1 + d[1] * 4);
                for (const [r, c, s] of flaechen) {
                    const k = d[0] * r[0] + d[1] * r[1] + d[2] * r[2];
                    if (k > c) w += s * Math.min(1, (k - c) / ((1 - c) * 0.35));
                }
                const o = (j * B + i) * 4;
                daten[o] = daten[o + 1] = daten[o + 2] = w;
                daten[o + 3] = 1;
            }
        }
        const t = new THREE.DataTexture(daten, B, H, THREE.RGBAFormat, THREE.FloatType);
        t.mapping = THREE.EquirectangularReflectionMapping;
        t.colorSpace = THREE.LinearSRGBColorSpace;
        t.magFilter = THREE.LinearFilter;
        t.minFilter = THREE.LinearFilter;
        t.needsUpdate = true;
        Meshgenesisumgebung._karte = t;
        return t;
    }
}
