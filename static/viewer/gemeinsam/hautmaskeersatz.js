/**
 * Hautmaskeersatz — die Haut vor und auf einem ERSATZSTÜCK (die Scham aus einer .blend, 09.10.2026).
 *
 * BEFUND (Edgar: „die hat im moment zwei mal Geschlechtsorgane", dann in der Szene gemessen): Das Stück liegt zum großen
 * Teil 5–25 mm HINTER der Genesis-Fläche (die Figur überbrückt die Furche) und war deshalb komplett verdeckt — die
 * gezeigte Furche war die Körperhaut. Die Maske eines Stoffs trifft den Stoff mit einem Strahl entlang der Körpernormale,
 * und zwar nur die Dreiecke um den NÄCHSTEN Stoffpunkt (`hautmaske.js`); bei einer Haut, die ein Stück überbrückt, liegt der
 * nächste Stoffpunkt nicht dort, wo der Strahl landet. Gemessen am Stück „cute girl Scham": 111 verdeckte Körperpunkte mit
 * Strahl, auch bei Tiefen von 45, 60 und 90 mm unverändert — die Tiefe war nicht das Problem, die Trefferliste war es.
 *
 * Hier gilt die einfachere Frage: Liegt an der Normale des Körperpunkts — von `tiefe` hinein bis `abstand` darüber, in einem
 * Zylinder vom Radius `RADIUS_M` — ein PUNKT des Stücks? Dann fällt die Haut dort weg. Ohne Dreiecke, ohne Nachbarschaft,
 * und ein Ersatzstück ist dicht genug (2 mm), dass ein Zylinder von 4 mm keine Lücke lässt. Reichweite: eine Gitterzelle
 * (`Hautmaskegeometrie.ZELLE_M`, 30 mm) um den Körperpunkt.
 *
 * DER RAND (Edgar: „wie aus der Haut ausgeschnitten", „die soll mit der Nachbarhaut verschmelzen"): Ganz entfällt die Haut
 * nur im Inneren des Stücks (`innen`) — am Rand bleibt ein Streifen stehen, der sich unter das Stück senkt
 * (`hautanschmiegung.js`) und durch dessen weichen Rand (`stueckfeder.js`) hindurchscheint. Der Streifen misst sich am
 * Netzrand des STÜCKS (`RING_M`), nicht in Dreiecksschichten der Haut: Zwei Schichten Haut (8 mm) reichten nicht für den
 * weichen Rand, vier ließen in der schmalen Furche (30 mm breit) Haut über den inneren Lippen stehen.
 */
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';
import { Stueckrand } from './stueckrand.js';

export class Hautmaskeersatz {

    /** Radius (m) des Zylinders um die Körpernormale — etwa ein Punktabstand der Stufe 1 (4 mm). */
    static RADIUS_M = 0.004;
    /** Weiter Zylinder (m) für Haut NEBEN dem Stück: ihre Höhe über dem Stück bestimmt, wie tief sie sinkt. */
    static RADIUS_SENKUNG_M = 0.009;
    /** So weit (m) vom Netzrand des Stücks bleibt Haut unter ihm stehen — über den weichen Rand (`Stueckrand.FEDER_M`) hinaus. */
    static RING_M = 0.03;
    /** Ringe Haut (Dreiecksschichten), wenn kein Randabstand des Stücks vorliegt (`innen` ohne `rand`). */
    static RINGE = 2;

    /**
     * Setzt `maske[i] = 1` und `ersatz[i] = 1` für jeden Körperpunkt, an dessen Normale ein Punkt des Stücks liegt — auch
     * für die, die der Strahltest davor schon verdeckt hat (sie lägen sonst als Saumband versenkt VOR dem Stück,
     * gesehen 09.10.2026: eine beige Platte mit Treppenkante mitten im Stück). `ersatz` sind die Körperpunkte, deren Haut
     * ganz entfällt oder sich auf das Stück senkt (`hautanschmiegung.js`). `hoehe` (Float32Array, vorbelegt mit −Infinity):
     * je Punkt die größte Höhe (m) eines Stückpunkts über dem Körperpunkt, entlang der Normale. `rand` (Float32Array,
     * vorbelegt mit Infinity): der Abstand dieses Stückpunkts vom Netzrand des Stücks (m).
     */
    static maskieren(basis, maske, stoff, abstand, tiefe, ersatz, hoehe, rand) {
        const { koerper, normalen } = basis;
        const P = stoff.punkte, h = G.ZELLE_M;
        const gitter = G.punktgitter(P, h);
        const huelle = G.huelle(P, Math.max(abstand, tiefe));
        const r2 = Hautmaskeersatz.RADIUS_M ** 2, r2weit = Hautmaskeersatz.RADIUS_SENKUNG_M ** 2;
        const randabstand = rand ? Stueckrand.randabstand(P, stoff.dreiecke, Hautmaskeersatz.RING_M + 0.004) : null;
        if (randabstand) stoff.randabstand = randabstand;
        const treffer = new Int32Array(1);
        for (let i = 0; i < maske.length; i++) {
            const px = koerper[3 * i], py = koerper[3 * i + 1], pz = koerper[3 * i + 2];
            if (px < huelle[0] || px > huelle[3] || py < huelle[1] || py > huelle[4]
                || pz < huelle[2] || pz > huelle[5]) continue;
            const p = [px, py, pz], n = [normalen[3 * i], normalen[3 * i + 1], normalen[3 * i + 2]];
            const t = Hautmaskeersatz._hoechster(P, gitter, h, p, n, abstand, tiefe, r2, treffer);
            if (t !== -Infinity) {
                maske[i] = 1;
                if (ersatz) ersatz[i] = 1;
                if (hoehe && t > hoehe[i]) hoehe[i] = t;
                if (randabstand && randabstand[treffer[0]] < rand[i]) rand[i] = randabstand[treffer[0]];
            } else if (hoehe) {
                // Haut, die das Stück nicht verdeckt, aber in seiner Nähe liegt: sie darf nicht vor ihm stehen (`hautanschmiegung.js`).
                const w = Hautmaskeersatz._hoechster(P, gitter, h, p, n, abstand, tiefe, r2weit, treffer);
                if (w > hoehe[i]) hoehe[i] = w;
            }
        }
    }

    /**
     * Die Körperpunkte, deren Haut ganz entfällt. Mit `rand` (Abstand vom Netzrand des Stücks, siehe `maskieren`): die Ersatz-
     * Punkte, die weiter als `RING_M` vom Rand liegen. Ohne: Ersatz-Punkte ohne Dreieck mit einer gezeichneten Ecke, `RINGE`
     * Schichten tief — der Stückrand ist gezackt, und bis dorthin entfernt klafft ein Loch (gesehen 09.10.2026: dunkle Zacken
     * oben und an den Seiten der Scham).
     */
    static innen(ersatz, maske, dreiecke, rand) {
        if (rand) {
            const aus = new Uint8Array(ersatz.length);
            for (let i = 0; i < aus.length; i++) if (ersatz[i] && rand[i] > Hautmaskeersatz.RING_M) aus[i] = 1;
            return aus;
        }
        const innen = Uint8Array.from(ersatz);
        let gezeichnet = maske;
        for (let r = 0; r < Hautmaskeersatz.RINGE; r++) {
            const neu = Uint8Array.from(innen);
            for (let k = 0; k + 2 < dreiecke.length; k += 3) {
                const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
                if (r === 0 ? (gezeichnet[a] && gezeichnet[b] && gezeichnet[c]) : (innen[a] && innen[b] && innen[c])) continue;
                neu[a] = 0; neu[b] = 0; neu[c] = 0;
            }
            innen.set(neu);
        }
        return innen;
    }

    /**
     * Markiert in `weg` jede Ecke eines Dreiecks, das einen `innen`-Punkt berührt — `Hautmaske.indexOhne` lässt dann auch
     * die Randdreiecke des Lochs weg. Sie spannten sonst von einer tief gesenkten Ecke (im Inneren des Stücks bis 20 mm unter
     * der Haut) zu einer flachen und standen als große Platten vor den inneren Lippen (gesehen 09.10.2026). Der Lochrand liegt
     * danach auf den Ring-Punkten, die nur knapp unter der Fläche des Stücks sitzen.
     */
    static beruehrt(innen, dreiecke, weg) {
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            if (innen[a] || innen[b] || innen[c]) { weg[a] = 1; weg[b] = 1; weg[c] = 1; }
        }
    }

    /**
     * Die größte Höhe `t` (m) eines Stückpunkts im Zylinder um die Normale `n` in den 27 Zellen um `p`; sonst −Infinity.
     * `treffer[0]` bekommt die Nummer dieses Stückpunkts.
     */
    static _hoechster(P, gitter, h, p, n, abstand, tiefe, r2, treffer) {
        const ci = Math.floor(p[0] / h), cj = Math.floor(p[1] / h), ck = Math.floor(p[2] / h);
        let best = -Infinity;
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            const liste = gitter.get(G.zelle(ci + a, cj + b, ck + c));
            if (!liste) continue;
            for (let l = 0; l < liste.length; l++) {
                const j = liste[l];
                const vx = P[3 * j] - p[0], vy = P[3 * j + 1] - p[1], vz = P[3 * j + 2] - p[2];
                const t = vx * n[0] + vy * n[1] + vz * n[2];
                if (t < -tiefe || t > abstand) continue;
                if (vx * vx + vy * vy + vz * vz - t * t <= r2 && t > best) { best = t; treffer[0] = j; }
            }
        }
        return best;
    }
}
