import { state } from './state.js';
import { Figurhaut } from '../gemeinsam/figurhaut.js';
import { Oberflaechenbindung } from '../gemeinsam/oberflaechenbindung.js';

/**
 * Bindungsprobe — stimmt die Oberflächenbindung der getragenen Stücke zum Körper, den die Seite zeichnet?
 *
 * WARUM (Edgar, 12.11.2026, an Olesia1 in der Ruhelage: „das T-Shirt sitzt oben nicht (kein Saum), und die Schuhe haben
 * Texturprobleme, oder haut geht durch“): Der Stoff-Shader (`oberflaecheglsl.js`) schiebt einen gebundenen Punkt aus der
 * Haut, wenn er tiefer liegt als in Ruhe — gemessen an drei Körperpunkten, deren NUMMERN der Server mitgibt. In Ruhe darf
 * er nichts schieben. Die Nummern kamen aber gerundet an (`core/daten/netzkurz.py`: 16 Bit über die Spanne 0 … 104.479,
 * Raster 1,59), trafen andere Körperpunkte, und der Shader schob schon in der Ruhelage: Stacheln an Kragen, Seitennaht
 * und Schuhspitze. Keine Prüfung sah es: Die `Kleidungsprobe` misst die gehäuteten Punkte OHNE den Schub des Shaders und
 * vergleicht mit der Ruhelage, der Modell-Check zählte nur Hautpunkte außerhalb des Schuhs.
 *
 * Gemessen am 12.11.2026 im Chrome, feine Stufe (vor dem Fix Olesia1 von Hand im Tab, der Fallout Ranger mit dieser Klasse):
 *   Angie Sneakers        176.246 von 176.484 Nummern gebrochen; 39.186 von 58.828 Punkten ohne Körperdreieck, 8.395 mit Ecken
 *                         über 5 cm auseinander; in Ruhe 2.221 Punkte über 1 mm geschoben, höchstens 39,8 mm
 *   G9 Base Shirt         20.223 von 28.546 ohne Körperdreieck, 6.261 fern; in Ruhe 2.875 Punkte über 1 mm geschoben
 *   Fallout Ranger        Stiefel 1.799 Punkte bis 39,8 mm, Helm 783 bis 38,4, Brustpanzer 405 bis 39,8, Jeans 307 bis 22,1,
 *                         Leggings 98 bis 12,6, Seil 12 bis 1,4 — alle Nummern gebrochen
 *   nach dem Fix          an allen neun Stücken 0 gebrochen, 0 fern, 0 ohne Körperdreieck, 0 geschoben
 *   Stücke unter 4.096 Werten (die Nieten der Angie Jeans, 193 Punkte) wurden nie gekürzt und waren vorher schon grün.
 * Gegenprobe (Sneakers, im Tab): Nummern auf das alte Raster gerundet → 58.828 gebrochen, 12.923 fern, 3.234 geschoben bis
 * 40 mm, rot; EINE Nummer um einen Punkt daneben → rot; zurückgestellt → grün. Dazu am Bild: Umriss des Stücks allein mit und
 * ohne Bindung in der Ruhelage (sieben Ansichten, Renderer der Seite) — vorher Shirt 59,4 / Sneakers 92,9 / Jeans 25,6 cm²
 * hinausgeschoben, nachher 0,4 / 0,1 / 0,3.
 *
 * Aufruf in der Konsole, Figur in der Ruhelage — vor dem Laden einer Animation, oder nach `skeleton.pose()` erst ein paar
 * Bilder warten: die Gelenkfelder der letzten Pose stehen sonst noch in den Punkten (gemessen: Shirt 28 statt 0,4 cm²):
 *     __bindungsprobe.laufen({ inst: __characters.get('…') })        // `nur`: RegExp auf den Stücknamen
 * Je Stück: `gebunden`, `nummern_gebrochen`, `ausserhalb` (Nummer jenseits des Körpers), `ecken_fern` (die drei Körperpunkte
 * liegen weiter auseinander als zwei längste Körperkanten), `kein_koerperdreieck` (das Tripel steht nicht im vollen Index des
 * Körpers) und `ruheschub` — die Rechnung des Shaders auf der CPU, mit den Grenzen aus `Oberflaechenbindung`.
 * `ok`: keine gebrochene Nummer, keine außerhalb, keine fernen Ecken, jedes Tripel ein Körperdreieck, in Ruhe kein Punkt über
 * `SCHUB_M` geschoben. Steht die Figur nicht in der Ruhelage, bleibt `ruheschub` leer (die Rechnung gilt nur dort) und zählt nicht.
 */
export class Bindungsprobe {

    /** So weit (m) darf der Shader einen Punkt in der Ruhelage schieben, ohne dass es zählt. Setzung: die float32-Felder
     *  (Abstand, Baryzentrik) kommen auf 16 Bit gerundet, das sind Bruchteile eines Millimeters; die Stacheln lagen bei 1 bis 40 mm. */
    static SCHUB_M = 0.001;
    /** Knochen gelten als in Ruhe, wenn sich ihre Bildmatrizen höchstens so weit unterscheiden. */
    static RUHE_TOLERANZ = 1e-4;

    static laufen({ inst = null, nur = null } = {}) {
        inst = inst || [...state.characters.values()].find(c => Object.keys(c.clothMeshes || {}).length);
        const koerper = inst?.bodyMesh, kg = koerper?.geometry;
        if (!kg?.attributes?.position || !kg.attributes.normal) return { fehler: 'keine Figur mit Körper' };
        inst.group?.updateMatrixWorld(true);
        const index = Figurhaut.vollerIndex(kg);
        const koerperdaten = { KP: kg.attributes.position.array, KN: kg.attributes.normal.array, kn: kg.attributes.position.count,
                               dreiecke: Bindungsprobe._dreiecke(index), fern: 2 * Bindungsprobe._laengsteKante(kg.attributes.position.array, index) };
        const ruhe = Bindungsprobe.inRuhe(koerper);
        const aus = { koerperpunkte: koerperdaten.kn, ruhe, stuecke: {} };
        for (const [name, netz] of Object.entries(inst.clothMeshes || {})) {
            if (nur && !nur.test(name)) continue;
            const g = netz?.geometry?.attributes;
            if (!g?.bindung || !g.bary || !g.bindabstand || !g.mischung) continue;
            aus.stuecke[name] = Bindungsprobe._stueck(g, koerperdaten, ruhe);
        }
        aus.ok = Object.values(aus.stuecke).every(s => s.ok);
        return aus;
    }

    /** Stehen alle Knochen in der Bindpose? Dann ist `Knochen · Kehrmatrix` für alle dieselbe Matrix (die Lage der Gruppe). */
    static inRuhe(koerper) {
        const { bones, boneInverses } = koerper.skeleton || {};
        if (!bones?.length) return false;
        const erste = bones[0].matrixWorld.clone().multiply(boneInverses[0]).elements, m = bones[0].matrixWorld.clone();
        for (let i = 1; i < bones.length; i++) {
            const e = m.copy(bones[i].matrixWorld).multiply(boneInverses[i]).elements;
            for (let k = 0; k < 16; k++) if (Math.abs(e[k] - erste[k]) > Bindungsprobe.RUHE_TOLERANZ) return false;
        }
        return true;
    }

    static _stueck(g, { KP, KN, kn, dreiecke, fern }, ruhe) {
        const P = g.position.array, B = g.bindung.array, U = g.bary.array, D = g.bindabstand.array, M = g.mischung.array, n = g.position.count;
        const LUFT = Oberflaechenbindung.LUFT, TIEF = Oberflaechenbindung.TIEF_GRENZE, SEIT = Oberflaechenbindung.SEIT_GRENZE;
        const z = { gebunden: 0, nummern_gebrochen: 0, ausserhalb: 0, ecken_fern: 0, kein_koerperdreieck: 0 };
        let geschoben = 0, schubMax = 0;
        for (let i = 0; i < n; i++) {
            const fa = B[3 * i], fb = B[3 * i + 1], fc = B[3 * i + 2];
            if (!(M[i] > 0) || fa < 0) continue;                         // wie der Shader: `mischung > 0.0 && bindung.x >= 0.0`
            z.gebunden++;
            const a = Math.floor(fa + 0.5), b = Math.floor(fb + 0.5), c = Math.floor(fc + 0.5);     // der Shader liest `int(nummer + 0.5)`
            if (a !== fa || b !== fb || c !== fc) z.nummern_gebrochen++;
            if (a >= kn || b >= kn || c >= kn || b < 0 || c < 0) { z.ausserhalb++; continue; }
            if (!Bindungsprobe._hat(dreiecke, a, b, c)) z.kein_koerperdreieck++;
            if (Math.max(Bindungsprobe._weg(KP, a, b), Bindungsprobe._weg(KP, a, c), Bindungsprobe._weg(KP, b, c)) > fern) z.ecken_fern++;
            if (!ruhe) continue;
            // Die Rechnung des Shaders (`OberflaecheGLSL.VERTEX`) mit Körper und Stück in der Bindpose
            const u = U[3 * i], v = U[3 * i + 1], w = U[3 * i + 2];
            let nx = u * KN[3 * a] + v * KN[3 * b] + w * KN[3 * c], ny = u * KN[3 * a + 1] + v * KN[3 * b + 1] + w * KN[3 * c + 1],
                nz = u * KN[3 * a + 2] + v * KN[3 * b + 2] + w * KN[3 * c + 2];
            const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
            const ox = P[3 * i] - (u * KP[3 * a] + v * KP[3 * b] + w * KP[3 * c]), oy = P[3 * i + 1] - (u * KP[3 * a + 1] + v * KP[3 * b + 1] + w * KP[3 * c + 1]),
                  oz = P[3 * i + 2] - (u * KP[3 * a + 2] + v * KP[3 * b + 2] + w * KP[3 * c + 2]);
            const hoehe = ox * nx + oy * ny + oz * nz, tief = Math.min(D[i], LUFT) - hoehe;
            if (tief > Bindungsprobe.SCHUB_M && tief < TIEF && Math.hypot(ox - hoehe * nx, oy - hoehe * ny, oz - hoehe * nz) < SEIT) {
                geschoben++; schubMax = Math.max(schubMax, tief);
            }
        }
        const ruheschub = ruhe ? { punkte: geschoben, hoechstens_mm: +(schubMax * 1000).toFixed(1) } : null;
        return { ...z, ruheschub,
                 ok: z.nummern_gebrochen === 0 && z.ausserhalb === 0 && z.ecken_fern === 0 && z.kein_koerperdreieck === 0
                     && (!ruheschub || ruheschub.punkte === 0) };
    }

    static _weg(KP, a, b) {
        return Math.hypot(KP[3 * a] - KP[3 * b], KP[3 * a + 1] - KP[3 * b + 1], KP[3 * a + 2] - KP[3 * b + 2]);
    }

    /** Die Dreiecke des Körpers zum Nachschlagen: kleinste und mittlere Nummer als Schlüssel, dazu die größten. */
    static _dreiecke(index) {
        const aus = new Map();
        for (let t = 0; index && t + 2 < index.length; t += 3) {
            const [a, b, c] = Bindungsprobe._sortiert(index[t], index[t + 1], index[t + 2]), k = a * 2097152 + b;
            const liste = aus.get(k);
            if (liste) liste.push(c); else aus.set(k, [c]);
        }
        return aus;
    }

    static _hat(dreiecke, x, y, z) {
        const [a, b, c] = Bindungsprobe._sortiert(x, y, z);
        return dreiecke.get(a * 2097152 + b)?.includes(c) || false;
    }

    static _sortiert(a, b, c) {
        if (a > b) [a, b] = [b, a];
        if (b > c) [b, c] = [c, b];
        if (a > b) [a, b] = [b, a];
        return [a, b, c];
    }

    static _laengsteKante(KP, index) {
        let max = 0;
        for (let t = 0; index && t + 2 < index.length; t += 3) {
            max = Math.max(max, Bindungsprobe._weg(KP, index[t], index[t + 1]), Bindungsprobe._weg(KP, index[t], index[t + 2]),
                           Bindungsprobe._weg(KP, index[t + 1], index[t + 2]));
        }
        return max;
    }
}

window.__bindungsprobe = Bindungsprobe;
