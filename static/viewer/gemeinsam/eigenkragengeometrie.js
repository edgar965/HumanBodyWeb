import * as THREE from 'three';
import { Eigenkragenlinie } from './eigenkragenlinie.js';

/**
 * Eigenkragengeometrie — das Netz eines Kragens am Ausschnitt eines eigenen Oberteils (25.10.2026 nachts). Gerechnet im Speicher aus der Schale (`Eigenkleidgeometrie`),
 * ohne Server; gebraucht von `Eigenkragen`.
 *
 * AUFBAU: `SPALTEN` Spalten entlang des Ausschnittrands (`Eigenkragenlinie`, Stufe 0), gleichmäßig nach Bogenlänge, vorn eine Lücke (`luecke`: Knopfleiste oder
 * `LUECKE_M`), und `ZEILEN` + 1 Zeilen quer (Anteil r = 0 am Rand … 1 an der freien Kante). JEDE Zeile einer Spalte trägt dieselben Werte des Randpunkts: Lage,
 * Normale, Körperkoordinaten, Brücke und Hautgewichte (aus den zwei Ecken der geschnittenen Kante gemischt, die vier größten) — der Shader schiebt den Punkt erst
 * wie die Schale (Sitz, Brücke) und legt dann den Kragen darauf; das Hautgewicht des Rands lässt ihn der Haltung folgen wie die Schale.
 * Dazu je Spalte die Richtungen für die Form (`EigenkragenGLSL`): `kgOben` den Hals hinauf (Sehne zur Linie f = −3 cm, siehe `_netz`) und `kgF1…3` hinab auf der
 * Haut (Linien f = +1,5 / +3 / +5 cm, relativ zum Rand) — darauf liegt ein umgelegter Kragen. `kgLage` = (r, Gewicht der Spitze 0…1 nahe den vorderen Enden über
 * `SPITZE_M`, Bogenlänge m, –). Höhe, Spitzenlänge, Abstand und Form sind Uniforms: ein Zug an diesen Reglern baut nichts neu. Neu gebaut wird nur, wenn sich der
 * Ausschnitt ändert (Form, Tiefe, Breite) oder die Schale (Neubau des Körpers).
 */
export class Eigenkragengeometrie {

    static SPALTEN = 160;
    static ZEILEN = 28;
    /** f-Stufen (m): Hals hinauf, Rand, dreimal hinab */
    static STUFEN = [-0.03, 0, 0.015, 0.03, 0.05];
    static LUECKE_M = 0.012;
    static SPITZE_M = 0.05;
    static _bereich = new WeakMap();

    /**
     * @param schale  BufferGeometry der Schale (`position`, `normal`, `kkKoord`, `kkNormal`, `kkBruecke`, `kkBrueckeB`, `skinIndex`, `skinWeight`, Index, Gruppen)
     * @param haut    (gruppe) → true, wenn die Gruppe Stoff trägt
     * @param w       Ausschnitt `{form, tiefe, hinten, breite, laenge, steh}` (`Eigenkragenlinie.hals`)
     * @returns `{geo, ms, laenge, besetzt}` oder null, wenn keine geschlossene Linie gefunden wurde
     */
    static bauen(schale, haut, w, luecke, uvMeter) {
        const t0 = performance.now();
        const a = schale.attributes, pos = a.position.array, koord = a.kkKoord.array;
        let b = Eigenkragengeometrie._bereich.get(schale);
        if (!b) {
            b = { dreiecke: Eigenkragenlinie.bereich(schale.index.array, schale.groups, koord, haut), achse: Eigenkragenlinie.achse(pos, koord) };
            Eigenkragengeometrie._bereich.set(schale, b);
        }
        const f = Eigenkragenlinie.feld(pos, koord, a.kkAnsatz?.array, b.dreiecke, w);
        const linien = Eigenkragengeometrie.STUFEN.map(c => Eigenkragenlinie.stufe(pos, b.dreiecke, f, c, b.achse));
        if (linien.some(l => !l)) return null;
        const rand = linien[1].punkte, n = rand.length;
        const am = (linie, feld, breite, x) => {
            const k0 = ((Math.floor(x) % n) + n) % n, k1 = (k0 + 1) % n, t = x - Math.floor(x);
            const p = Eigenkragenlinie.wert(feld, breite, linie[k0]), q = Eigenkragenlinie.wert(feld, breite, linie[k1]);
            return p.map((v, i) => v * (1 - t) + q[i] * t);
        };
        // Knoten: −0,5 (vorn Mitte) … n − 0,5 (wieder vorn Mitte), Bogenlänge dazwischen
        const knoten = [-0.5, ...Array.from({ length: n }, (_, k) => k), n - 0.5], bogen = [0];
        for (let j = 1; j < knoten.length; j++) {
            const p = am(rand, pos, 3, knoten[j - 1]), q = am(rand, pos, 3, knoten[j]);
            bogen.push(bogen[j - 1] + Math.hypot(q[0] - p[0], q[1] - p[1], q[2] - p[2]));
        }
        const laenge = bogen[bogen.length - 1], spalten = Eigenkragengeometrie._spalten(knoten, bogen, laenge, luecke);
        return { geo: Eigenkragengeometrie._netz(a, linien, spalten, am, uvMeter), ms: Math.round(performance.now() - t0), laenge, besetzt: linien[1].besetzt };
    }

    /** Je Spalte (Bruchindex der Fächer x, Bogenlänge σ, Gewicht der Spitze). */
    static _spalten(knoten, bogen, laenge, luecke) {
        const m = Eigenkragengeometrie.SPALTEN, aus = [];
        let j = 0;
        for (let i = 0; i < m; i++) {
            const sigma = luecke / 2 + (laenge - luecke) * i / (m - 1);
            while (j < bogen.length - 2 && bogen[j + 1] < sigma) j++;
            const t = (sigma - bogen[j]) / Math.max(bogen[j + 1] - bogen[j], 1e-9);
            const ende = Math.min(sigma - luecke / 2, laenge - luecke / 2 - sigma) / Eigenkragengeometrie.SPITZE_M;
            const g = Math.min(1, Math.max(0, ende));
            aus.push({ x: knoten[j] + t * (knoten[j + 1] - knoten[j]), sigma, spitze: 1 - g * g * (3 - 2 * g) });
        }
        return aus;
    }

    /**
     * `kgOben` ist die SEHNE vom Rand zur Linie 3 cm den Hals hinauf, nicht die Richtung senkrecht zur Normale: In der Mulde zwischen Trapezmuskel und Hals steht
     * die Normale schräg, die Senkrechte darauf zeigt in den Hals — der Steg verschwand dort in der Haut (im Chrome gesehen an DamiraAlt, seitlich). Eine Sehne
     * über eine Innenecke liegt außerhalb des Körpers. Die Richtungen werden über `GLATT` Spalten gemittelt (die Linien sind je Fach abgetastet und zittern).
     */
    static GLATT = 3;

    static _netz(a, linien, spalten, am, uvMeter) {
        const z = Eigenkragengeometrie.ZEILEN + 1, m = spalten.length, anzahl = m * z;
        const felder = { position: 3, normal: 3, kkKoord: 4, kkNormal: 3, kkBruecke: 4, kkBrueckeB: 4, kgLage: 4, kgOben: 3, kgF1: 3, kgF2: 3, kgF3: 3, uv: 2 };
        const aus = Object.fromEntries(Object.entries(felder).map(([k, b]) => [k, new Float32Array(anzahl * b)]));
        const skinI = new a.skinIndex.array.constructor(anzahl * 4), skinW = new Float32Array(anzahl * 4);
        const [oben, rand, ...hinab] = linien.map(l => l.punkte), um = uvMeter > 0 ? uvMeter : 1;
        const spalte = spalten.map((s) => {
            const b = am(rand, a.position.array, 3, s.x), relativ = l => am(l, a.position.array, 3, s.x).map((v, k) => v - b[k]);
            return { b, richtung: [relativ(oben), ...hinab.map(relativ)] };
        });
        const glatt = (i, j) => [0, 1, 2].map(k => {
            let summe = 0, n = 0;
            for (let d = -Eigenkragengeometrie.GLATT; d <= Eigenkragengeometrie.GLATT; d++) {
                const q = spalte[i + d];
                if (q) { summe += q.richtung[j][k]; n++; }
            }
            return summe / n;
        });
        for (let i = 0; i < m; i++) {
            const s = spalten[i], b = spalte[i].b;
            const nb = Eigenkragengeometrie._einheit(am(rand, a.kkNormal.array, 3, s.x));
            const werte = {
                position: b, normal: am(rand, a.normal.array, 3, s.x), kkKoord: am(rand, a.kkKoord.array, 4, s.x), kkNormal: nb,
                kkBruecke: am(rand, a.kkBruecke.array, 4, s.x), kkBrueckeB: am(rand, a.kkBrueckeB.array, 4, s.x),
                kgOben: glatt(i, 0), kgF1: glatt(i, 1), kgF2: glatt(i, 2), kgF3: glatt(i, 3),
            };
            const naechst = rand[((Math.round(s.x) % rand.length) + rand.length) % rand.length];
            werte.kkKoord[0] = Math.round(a.kkKoord.array[4 * (naechst.s < 0.5 ? naechst.a : naechst.b)]);   // die Kette nie mitteln (1 und 6 ergäbe „Bein“)
            const haut = Eigenkragengeometrie._gewichte(a, naechst);
            for (let r = 0; r < z; r++) {
                const p = i * z + r;
                for (const [k, wert] of Object.entries(werte)) aus[k].set(wert, p * felder[k]);
                aus.kgLage.set([r / (z - 1), s.spitze, s.sigma, 0], p * 4);
                aus.uv.set([s.sigma / um, 0.09 * r / (z - 1) / um], p * 2);
                skinI.set(haut.index, p * 4);
                skinW.set(haut.gewicht, p * 4);
            }
        }
        const geo = new THREE.BufferGeometry();
        for (const [k, b] of Object.entries(felder)) geo.setAttribute(k, new THREE.BufferAttribute(aus[k], b));
        geo.setAttribute('skinIndex', new THREE.BufferAttribute(skinI, 4));
        geo.setAttribute('skinWeight', new THREE.BufferAttribute(skinW, 4));
        const index = [];
        for (let i = 0; i + 1 < m; i++) {
            for (let r = 0; r + 1 < z; r++) {
                const p = i * z + r, q = (i + 1) * z + r;
                index.push(p, q, p + 1, p + 1, q, q + 1);
            }
        }
        geo.setIndex(index);
        return geo;
    }

    /** Hautgewichte am Schnittpunkt: beide Ecken nach ihrem Anteil gemischt, die vier größten, auf 1 gebracht. */
    static _gewichte(a, e) {
        const summe = new Map(), si = a.skinIndex.array, sw = a.skinWeight.array;
        for (const [p, anteil] of [[e.a, 1 - e.s], [e.b, e.s]]) {
            for (let k = 0; k < 4; k++) {
                const knochen = si[4 * p + k], g = sw[4 * p + k] * anteil;
                if (g > 0) summe.set(knochen, (summe.get(knochen) || 0) + g);
            }
        }
        const beste = [...summe.entries()].sort((x, y) => y[1] - x[1]).slice(0, 4), gesamt = beste.reduce((s, [, g]) => s + g, 0) || 1;
        while (beste.length < 4) beste.push([0, 0]);
        return { index: beste.map(([k]) => k), gewicht: beste.map(([, g]) => g / gesamt) };
    }

    static _einheit(v) {
        const l = Math.hypot(v[0], v[1], v[2]) || 1;
        return [v[0] / l, v[1] / l, v[2] / l];
    }
}
