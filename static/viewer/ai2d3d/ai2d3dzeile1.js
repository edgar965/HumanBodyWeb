/**
 * Ai2d3dzeile1 — der Körper in Feld 3 der Zeile 2 auf der Genesis-Figur der Zeile 1 (31.10.2026, Edgar: „Zeile 2, die Vorlage von der ersten Zeile nehmen beim Körper und
 * Genesis-Modell … die zweite Zeile rechts unten ist immer noch völlig kaputt mit den Armen“).
 *
 * Gemessen (`ProjektTemp/_wegwerf/ergaenzung/zeilen_vergleich.py`): die Figur der Zeile 2 — Regler und Haltung je Foto der Mesh-Methode, auf die Regler-Figur umgezogen — lag je Foto
 * im Median 14 mm, an den Fingern bis 55 mm neben der Genesis-Figur der Zeile 1; Zeile 1 trägt dazu Gliedmaße und Versatz längs der Normale, die Regler allein nicht abbilden. Hier
 * nimmt jeder Punkt des Anzeigenetzes, der einem Käfigpunkt gehört (`ursprung`), den Punkt der Zeile 1 im gewählten Foto; Haut und Material bleiben die der Zeile 2. Punkte ohne
 * Käfigpunkt (Anhänge), Augen und Stücke verschieben sich wie der nächste Körperpunkt — die Stücke sind auf dem Körper der Zeile 2 gerechnet und bleiben so auf der Haut.
 * Normalen des Körpers aus den Dreiecken des Käfigs (über die UV-Nähte hinweg gleich).
 */
import { Ai2d3dnachbarn } from './ai2d3dnachbarn.js';
import { Ai2d3dtrainingfigur } from './ai2d3dtrainingfigur.js';

export class Ai2d3dzeile1 {

    /**
     * @param figur THREE.Group der Testfigur @param koerper [Mesh, …] die Körpernetze (gleiche Punkte) @param ursprung Int32Array (Anzeigenetz auf dem Käfig → Käfigpunkt)
     * @param netz `Mesh3daiflaechennetz` des Körpers: auf Netzstufe 1 (09.11.2026) mit Unterteilungsmatrix — dann gehen die Käfigpunkte der Zeile 1 durch sie (`ausKaefig`), nicht über `ursprung`
     */
    constructor(figur, koerper, ursprung, netz = null) {
        this.figur = figur;
        this.koerper = koerper;
        this.ursprung = ursprung;
        this.netz = netz?.matrix ? netz : null;
        this.nr = null;
        figur.traverse(o => { if (o.isMesh) o.geometry.userData.lage0 ??= o.geometry.attributes.position.array.slice(); });
        this.lage0 = koerper[0].geometry.userData.lage0;
        this.n0 = Math.min(this.netz ? this.netz.matrix.zeilen : ursprung.length, this.lage0.length / 3);
        this.nachbarn = new Ai2d3dnachbarn(this.lage0, this.n0);      // Körperpunkte mit Käfigpunkt (`Ai2d3dnachbarn.gewichte`)
    }

    /** Die Figur auf das Foto `nr` legen (`genesis` = Block der Zeile 1 aus `training_figur.json`). → false, wenn Zeile 1 für dieses Foto keine Punkte hat. */
    setzen(nr, genesis) {
        if (this.nr === nr) return true;
        const text = genesis?.fotos?.[String(nr + 1)];
        if (!text) return false;
        const p = Ai2d3dtrainingfigur._feld(text, Float32Array);
        const versatz = new Float32Array(this.n0 * 3);
        const u = this.ursprung;
        const kaefigNormalen = Ai2d3dzeile1._normalen(p, Ai2d3dtrainingfigur._feld(genesis.dreiecke, Uint32Array));
        // Stufe 1: Punkte und Normalen der Zeile 1 durch die Unterteilungsmatrix, danach je Körperpunkt der eigene (Index i statt u[i])
        const ziel = this.netz ? this.netz.ausKaefig(p) : p;
        const normalen = this.netz ? Ai2d3dzeile1._einheit(this.netz.ausKaefig(kaefigNormalen)) : kaefigNormalen;
        const nr0 = this.netz ? (i => i) : (i => u[i]);
        for (let i = 0; i < this.n0; i++) for (let c = 0; c < 3; c++) versatz[i * 3 + c] = ziel[nr0(i) * 3 + c] - this.lage0[i * 3 + c];
        this.figur.traverse(o => {
            if (!o.isMesh) return;
            const geo = o.geometry, a = geo.userData.lage0, pos = geo.attributes.position.array;
            const koerper = this.koerper.includes(o);
            geo.userData.nachbarn ??= Array.from({ length: a.length / 3 }, (_v, i) => (koerper && i < this.n0 ? [[i, 1]] : this.nachbarn.gewichte(a, i)));
            const nb = geo.userData.nachbarn, nrm = geo.attributes.normal?.array;
            for (let i = 0; i < a.length / 3; i++) {
                let vx = 0, vy = 0, vz = 0;
                for (const [j, w] of nb[i]) { vx += w * versatz[j * 3]; vy += w * versatz[j * 3 + 1]; vz += w * versatz[j * 3 + 2]; }
                pos[i * 3] = a[i * 3] + vx; pos[i * 3 + 1] = a[i * 3 + 1] + vy; pos[i * 3 + 2] = a[i * 3 + 2] + vz;
                if (koerper && i < this.n0 && nrm) for (let c = 0; c < 3; c++) nrm[i * 3 + c] = normalen[nr0(i) * 3 + c];
            }
            geo.attributes.position.needsUpdate = true;
            if (nrm) geo.attributes.normal.needsUpdate = true;
            geo.computeBoundingBox();
            geo.computeBoundingSphere();
        });
        this.nr = nr;
        return true;
    }

    /** Vektoren (V·3) auf Länge 1 — die unterteilten Normalen. */
    static _einheit(n) {
        for (let i = 0; i < n.length; i += 3) {
            const l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1;
            n[i] /= l; n[i + 1] /= l; n[i + 2] /= l;
        }
        return n;
    }

    /** Flächengewichtete Normalen je Käfigpunkt. */
    static _normalen(p, d) {
        const n = new Float32Array(p.length);
        for (let t = 0; t < d.length; t += 3) {
            const a = d[t] * 3, b = d[t + 1] * 3, c = d[t + 2] * 3;
            const ux = p[b] - p[a], uy = p[b + 1] - p[a + 1], uz = p[b + 2] - p[a + 2];
            const vx = p[c] - p[a], vy = p[c + 1] - p[a + 1], vz = p[c + 2] - p[a + 2];
            const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            for (const k of [a, b, c]) { n[k] += nx; n[k + 1] += ny; n[k + 2] += nz; }
        }
        for (let i = 0; i < n.length; i += 3) {
            const l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1;
            n[i] /= l; n[i + 1] /= l; n[i + 2] /= l;
        }
        return n;
    }
}
