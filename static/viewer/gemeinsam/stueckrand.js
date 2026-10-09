/**
 * Stueckrand — wie weit ein Punkt eines Ersatzstücks vom Rand seines Netzes liegt, und daraus die Deckkraft für den
 * weichen Auslauf (`stueckfeder.js`).
 *
 * WARUM (Edgar, 09.10.2026: „die soll mit der Nachbarhaut verschmelzen"): Das Scham-Stück wird aus dem Original
 * geschnitten, wo es mehr als 5 mm von der Figurfläche abweicht — sein Rand ist ausgefranst (Flügel in den Leisten, Treppen
 * der Dreiecke; gesehen im Chrome, Stück allein gezeichnet). Mit hartem Rand ist jede Stufe als Farbsprung zur Nachbarhaut
 * sichtbar. Läuft die Deckkraft über `FEDER_M` am Rand von 0 auf 1, scheint die Haut darunter (`Hautanschmiegung`: die Ringe
 * Haut am Stückrand liegen knapp unter der Fläche des Stücks) durch, und die Stufen verschwimmen.
 *
 * Der Rand: Kanten, die nur ein Dreieck hat. UV-Nähte teilen sich Kanten mit doppelten Punkten — die Punkte werden
 * deshalb nach der Lage verschweißt, sonst wäre jede Naht ein Rand. Der Weg läuft über das Netz (`Hautwege`, mit Kanten der
 * Länge 0 über die Nähte). Ohne Three.js und ohne DOM (Node-Test `test_js_stueckrand.py`).
 */
import { Hautwege } from './hautwege.js';

export class Stueckrand {

    /**
     * So weit (m) vom Netzrand läuft die Deckkraft von 0 auf 1 — kleiner als die Ringe Haut am Rand (2 × ~4 mm).
     *
     * 6 mm bis 09.10.2026. Seit der Rand eine glatte Kontur ist (`Blendimportschamschnitt`, nicht mehr die Zähne ganzer Dreiecke),
     * versteckt die Feder keine Zacken mehr — sie macht nur noch die schmalen Ausläufer in den Leisten durchsichtig, und durch die
     * schienen Hautsplitter hindurch (Edgar: „keine helle, gesägte Zipfel an den Rändern"). Ein Ausläufer unter 2 × `FEDER_M` Breite
     * erreicht nie die volle Deckkraft.
     */
    static FEDER_M = 0.003;
    /** Durchgänge, in denen `fahnen` Spitzen am Rand abträgt. */
    static FAHNEN = 3;

    /**
     * Die Deckkraft (0 … 1) je Punkt.
     * @param P  Punkte xyz
     * @param T  Index des Netzes
     */
    static deckkraft(P, T, feder = Stueckrand.FEDER_M) {
        const weg = Stueckrand.randabstand(P, T, feder);
        const a = new Float32Array(weg.length);
        for (let i = 0; i < a.length; i++) {
            const x = Math.min(weg[i] / feder, 1);
            a[i] = x * x * (3 - 2 * x);
        }
        return a;
    }

    /** Je Punkt der Weg über das Netz zum nächsten Randpunkt, höchstens `reichweite` (darüber Infinity). */
    static randabstand(P, T, reichweite) {
        const rand = Stueckrand.randpunkte(P, T);
        return Hautwege.wege(P, T, rand, reichweite);
    }

    /** Je Punkt die Nummer des ersten Punkts gleicher Lage (UV-Nähte teilen Punkte). */
    static _schweiss(P) {
        const n = P.length / 3, schweiss = new Int32Array(n), erste = new Map();
        for (let i = 0; i < n; i++) {
            const s = `${Math.round(P[3 * i] * 1e5)},${Math.round(P[3 * i + 1] * 1e5)},${Math.round(P[3 * i + 2] * 1e5)}`;
            if (!erste.has(s)) erste.set(s, i);
            schweiss[i] = erste.get(s);
        }
        return schweiss;
    }

    /**
     * Die Fahnen am Netzrand: Dreiecke mit höchstens EINEM Nachbarn über eine Kante, `durchgaenge` Mal wiederholt (ein Dreieck, das
     * erst durch das Entfernen einer Fahne zur Spitze wird, gehört dazu). Der Rand des Scham-Stücks ist aus dem Original nach
     * einem Abstandsmaß geschnitten und läuft in Spitzen aus; sie standen als helle Splitter in den Leisten (gesehen 09.10.2026).
     * Je Dreieck 1 = weg.
     */
    static fahnen(P, T, durchgaenge = Stueckrand.FAHNEN) {
        const schweiss = Stueckrand._schweiss(P), anzahl = T.length / 3, weg = new Uint8Array(anzahl), kanten = new Map();
        const schluessel = (t, e) => {
            const a = schweiss[T[3 * t + e]], b = schweiss[T[3 * t + (e + 1) % 3]];
            return a < b ? `${a},${b}` : `${b},${a}`;
        };
        for (let t = 0; t < anzahl; t++) for (let e = 0; e < 3; e++) {
            const s = schluessel(t, e), liste = kanten.get(s);
            if (liste) liste.push(t); else kanten.set(s, [t]);
        }
        for (let durchgang = 0; durchgang < durchgaenge; durchgang++) {
            const neu = [];
            for (let t = 0; t < anzahl; t++) {
                if (weg[t]) continue;
                let nachbarn = 0;
                for (let e = 0; e < 3; e++) for (const u of kanten.get(schluessel(t, e))) if (u !== t && !weg[u]) nachbarn++;
                if (nachbarn <= 1) neu.push(t);
            }
            if (!neu.length) break;
            for (const t of neu) weg[t] = 1;
        }
        return weg;
    }

    /** Die Punkte (Nummern) an Kanten mit nur einem Dreieck — Punkte gleicher Lage gelten als einer. */
    static randpunkte(P, T) {
        const schweiss = Stueckrand._schweiss(P);
        const kanten = new Map();
        for (let k = 0; k + 2 < T.length; k += 3) {
            for (let e = 0; e < 3; e++) {
                const a = schweiss[T[k + e]], b = schweiss[T[k + (e + 1) % 3]];
                if (a === b) continue;
                const s = a < b ? `${a},${b}` : `${b},${a}`;
                kanten.set(s, (kanten.get(s) || 0) + 1);
            }
        }
        const rand = new Set();
        for (const [s, zahl] of kanten) {
            if (zahl !== 1) continue;
            const [a, b] = s.split(',').map(Number);
            rand.add(a); rand.add(b);
        }
        return Array.from(rand);
    }
}
