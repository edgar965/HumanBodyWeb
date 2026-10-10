/**
 * Stuecknaht — der Rand eines verschweißten Ersatzstücks (Scham aus einer .blend) folgt der Haut, die der Browser zeigt (09.10.2026).
 *
 * WARUM (Chrome, „cute girl", Haut und Stück verschweißt): Der Bau legt den Rand des Stücks auf die Ecken des Rings, den die Kanten
 * der Haut bilden (`Blendimportschamnaht`) — auf die Haut der FIGUR DES IMPORTS. Die Haut im Browser ist nicht dieselbe: gemessen
 * 09.10.2026 an 40 Stichproben im Schambereich von „cute girl", Browser gegen Import: Median 2,2 mm, größte 7,8 mm (Oberschenkel und
 * Leisten; über dem Schritt, y > 880 mm, 0,02 mm). Und die Punkte des Stücks, die der Server liefert, liegen am Rand bis 1 mm neben
 * der Lage im Bau (gemessen an 101 Randpunkten: 51 genau, 20 über 0,1 mm). Mit dem Rand 2–5 mm neben den Ringpunkten der Haut öffnet
 * sich ein Spalt, in Haltung (Beine gespreizt) wächst er.
 *
 * HIER: Das Stück bringt seine Ringecken mit (`hautLoch.ring`: Lage im Bau, Nummer des Hautpunkts, Verschiebung der Glättung). Der
 * Browser findet die Randpunkte des Stücks (Kanten mit einem Dreieck), ordnet jedem die nächste Ringecke zu und rückt ihn auf die
 * Lage des Hautpunkts, wie sie JETZT ist; die Verschiebung geht als glattes Feld (1/d²) ins ganze Stück weiter (`_feld`).
 * Geschrieben wird in das `einzug`-Feld des Stücks (xyz je Punkt, im Vertex-Shader vor dem Skinning addiert, `hauteinzug.js`). Rand
 * und Haut teilen Lage UND Gewichte (die Gewichte der Ecken sind die der Hautpunkte, `Blendimportschamgewichte.an_ring`): der Rand
 * bleibt in jeder Haltung dicht, auch wenn die Regler der Figur nach dem Bau verstellt wurden.
 *
 * Ohne Three.js und ohne DOM (Node-Test `test_js_stuecknaht.py`); das Schreiben ins Netz macht `hautverdeckung.js`.
 */
import { Hautwege } from './hautwege.js';

export class Stuecknaht {

    /** So weit (m) über das Netz reicht `weg` (für die Normalen, `stucknormalen.js`, und die Farbe, `stueckhautrechnung.js`: 14 mm). */
    static BAND_M = 0.014;
    /** Dämpfung der Gewichte 1/(d² + EPS²) des Verschiebungsfelds: ein Punkt auf dem Rand hat Abstand 0. */
    static EPS_M = 1e-4;
    /** Der Rest des Rands (Versatz minus Mittel) klingt über diesen Abstand (m) zum Rand nach innen ab — wie das Randband im Bau (`BAND_MM` 12). */
    static FELD_RADIUS_M = 0.012;
    /** Höchstens so weit (m) darf ein Randpunkt des Stücks von seiner Ringecke im Bau entfernt liegen, um ihr zugeordnet zu werden. */
    static ZUORDNUNG_M = 0.004;
    /** Punkte, die auf diese Stellen (m) gerundet gleich sind, gelten als ein Punkt (UV-Nähte des Stücks stehen mehrfach). */
    static LAGE_M = 1e-5;

    /**
     * Die Verschiebung (xyz je Punkt des Stücks, `Float32Array`) und ihr Bericht.
     * @param punkte   Punkte des Stücks (Ruhelage), xyz
     * @param index    Dreiecksindex des Stücks (voll)
     * @param ring     `{lage: Float32Array (k·3), punkte: Uint32Array (k), d: Float32Array (k·3)}`
     * @param haut     Punkte der Haut (Ruhelage), xyz — so, wie der Browser sie hat
     * @returns {{werte, ecken, gefunden, medianMm, maxMm, weg, randpunkte}} — `weg`: Weg über das Netz zum Rand je Punkt (`Infinity`
     *   jenseits von `BAND_M`; null ohne Randpunkt), `randpunkte`: `{ids, ecke}` die Randpunkte (alle Kopien) und ihre Ringecke
     *   (für `stucknormalen.js`)
     */
    static verschiebung(punkte, index, ring, haut) {
        const n = punkte.length / 3, k = ring.punkte.length;
        const gruppen = Stuecknaht._rand(punkte, index);
        const zuordnung = Stuecknaht._zuordnen(gruppen, ring);
        const werte = new Float32Array(3 * n);
        const randIds = [], versatz = [], randEcke = [];     // je Randpunkt (alle Kopien): Nummer, Versatz und Ringecke
        const betrag = [];
        zuordnung.forEach((j, g) => {
            const i = ring.punkte[j], ziel = [0, 0, 0], v = [0, 0, 0];
            for (let c = 0; c < 3; c++) { ziel[c] = haut[3 * i + c] + ring.d[3 * j + c]; v[c] = ziel[c] - gruppen[g].p[c]; }
            betrag.push(Math.hypot(v[0], v[1], v[2]));
            for (const id of gruppen[g].ids) { randIds.push(id); versatz.push(v); randEcke.push(j); }
        });
        let weg = null;
        if (randIds.length) {
            weg = Hautwege.wege(punkte, index, randIds, Stuecknaht.BAND_M);
            Stuecknaht._feld(punkte, randIds, versatz, werte);
        }
        betrag.sort((a, b) => a - b);
        return { werte, ecken: k, gefunden: zuordnung.size, rand: gruppen.length, weg,
                 randpunkte: { ids: Uint32Array.from(randIds), ecke: Uint32Array.from(randEcke) },
                 medianMm: betrag.length ? Math.round(1e5 * betrag[betrag.length >> 1]) / 100 : 0,
                 maxMm: betrag.length ? Math.round(1e5 * betrag[betrag.length - 1]) / 100 : 0 };
    }

    /**
     * Die Randpunkte des Stücks: Kanten mit nur einem Dreieck, Punkte gleicher Lage (UV-Nähte) als eine Gruppe.
     * @returns {Array<{ids: number[], p: number[]}>} je Gruppe die Punktnummern und die Lage
     */
    static _rand(punkte, index) {
        const n = punkte.length / 3, s = 1 / Stuecknaht.LAGE_M;
        const lage = new Map(), gruppe = new Int32Array(n);
        const gruppen = [];
        for (let v = 0; v < n; v++) {
            const schluessel = `${Math.round(punkte[3 * v] * s)},${Math.round(punkte[3 * v + 1] * s)},${Math.round(punkte[3 * v + 2] * s)}`;
            if (!lage.has(schluessel)) { lage.set(schluessel, gruppen.length); gruppen.push({ ids: [], p: [punkte[3 * v], punkte[3 * v + 1], punkte[3 * v + 2]] }); }
            gruppe[v] = lage.get(schluessel);
            gruppen[gruppe[v]].ids.push(v);
        }
        const kanten = new Map();
        for (let t = 0; t + 2 < index.length; t += 3) {
            for (let e = 0; e < 3; e++) {
                const a = gruppe[index[t + e]], b = gruppe[index[t + (e + 1) % 3]];
                if (a === b) continue;
                const k = a < b ? a * gruppen.length + b : b * gruppen.length + a;
                kanten.set(k, (kanten.get(k) || 0) + 1);
            }
        }
        const rand = new Set();
        for (const [k, zahl] of kanten) if (zahl === 1) { rand.add(Math.floor(k / gruppen.length)); rand.add(k % gruppen.length); }
        return Array.from(rand).sort((x, y) => x - y).map((g) => gruppen[g]);
    }

    /**
     * Jeder Randgruppe die nächste Ringecke (höchstens `ZUORDNUNG_M`), jede Ecke und jede Gruppe höchstens einmal; die kürzesten
     * Abstände zuerst. @returns Map Gruppe → Ecke
     */
    static _zuordnen(gruppen, ring) {
        const k = ring.punkte.length, paare = [];
        gruppen.forEach((g, i) => {
            for (let j = 0; j < k; j++) {
                const d = Math.hypot(g.p[0] - ring.lage[3 * j], g.p[1] - ring.lage[3 * j + 1], g.p[2] - ring.lage[3 * j + 2]);
                if (d <= Stuecknaht.ZUORDNUNG_M) paare.push([d, i, j]);
            }
        });
        paare.sort((a, b) => a[0] - b[0]);
        const zuordnung = new Map(), benutzt = new Set();
        for (const [, i, j] of paare) {
            if (zuordnung.has(i) || benutzt.has(j)) continue;
            zuordnung.set(i, j); benutzt.add(j);
        }
        return zuordnung;
    }

    /**
     * Die Verschiebung jedes Punkts des Stücks: der MITTLERE Versatz aller Randpunkte (`versatz`, xyz je Randpunkt) für das ganze Stück, dazu
     * der Rest des eigenen Rands (1/d²-gewichtet über alle Randpunkte), der mit dem Abstand zum Rand über `FELD_RADIUS_M` abklingt. Am Rand
     * ist es der eigene Versatz, im Innern eine einheitliche Verschiebung — die Lippen behalten ihre Form.
     * Gemessen 09.10.2026 an einer Figur, deren Haut im Browser 105 mm höher steht als die des Imports („Größe" gesetzt; am ganzen Ring
     * 101–109 mm): mit einem Versatz, der nur über `BAND_M` ausläuft, wurde der Rand 105 mm hochgezogen und das Innere blieb stehen — die
     * Textur lief als Streifen über 10 mm, das Stück stand als gestrecktes Rechteck im Loch. Ein gewichtetes Mittel allein (die Fassung davor)
     * verformte das Innere dort, wo die Ränder links und rechts verschieden weit von der Haut standen (Edgar: „warum so unregelmäßig???";
     * Python-Seite gemessen: Spiegelabstand 90. Perzentil 4,6 mm gegen 0,5 mm im Original, `blendimportschamregister.py`).
     */
    static _feld(punkte, randIds, versatz, werte) {
        const n = punkte.length / 3, k = randIds.length, eps2 = Stuecknaht.EPS_M * Stuecknaht.EPS_M;
        const mittel = [0, 0, 0];
        for (const v of versatz) { mittel[0] += v[0] / k; mittel[1] += v[1] / k; mittel[2] += v[2] / k; }
        for (let p = 0; p < n; p++) {
            let sx = 0, sy = 0, sz = 0, sw = 0, nah2 = Infinity;
            for (let r = 0; r < k; r++) {
                const q = randIds[r];
                const d2 = (punkte[3 * q] - punkte[3 * p]) ** 2 + (punkte[3 * q + 1] - punkte[3 * p + 1]) ** 2 + (punkte[3 * q + 2] - punkte[3 * p + 2]) ** 2;
                const w = 1 / (d2 + eps2);
                sx += w * (versatz[r][0] - mittel[0]); sy += w * (versatz[r][1] - mittel[1]); sz += w * (versatz[r][2] - mittel[2]); sw += w;
                if (d2 < nah2) nah2 = d2;
            }
            const t = Math.min(1, Math.sqrt(nah2) / Stuecknaht.FELD_RADIUS_M), f = 1 - t * t * (3 - 2 * t);
            werte[3 * p] = mittel[0] + f * sx / sw; werte[3 * p + 1] = mittel[1] + f * sy / sw; werte[3 * p + 2] = mittel[2] + f * sz / sw;
        }
        randIds.forEach((q, r) => { werte[3 * q] = versatz[r][0]; werte[3 * q + 1] = versatz[r][1]; werte[3 * q + 2] = versatz[r][2]; });   // der Rand exakt
    }
}
