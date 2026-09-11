/**
 * Hautmaske — welche Körperpunkte unter einem Kleidungsstück liegen, und ein
 * Dreiecksindex ohne die verdeckten Flächen.
 *
 * BEFUND (Edgar, 11.09.2026, zweimal mit Bild: „bei einer animation kommt
 * der Körper durch die Kleidung hindurch", „natürlich ist es die Haut die
 * durch die Verformung durchkommt!!!"): Eine Leggings liegt 2 mm auf der
 * Haut, und in Dance1 stehen an Bund, Schritt und Knie weiße Splitter
 * heraus. Körperseitig gegen die Stoffdreiecke gemessen (Strahl entlang der
 * Körpernormale, Stoff hinten und keiner vorn): je Bild 3 bis 33 Körperpunkte
 * des Beckens vor dem Stoff, 2 bis 5 mm tief, am kreuzenden Knie 29 mm.
 * Gleiche Gewichte helfen nicht — mit den Hautgewichten der 70.851 Punkte
 * (nächster Punkt oder baryzentrisch über das nächste Dreieck) blieben es 16
 * und 31 statt 18 und 33. Zwei Flächen, die 2 mm auseinanderliegen und
 * getrennt gehäutet werden, kommen sich an jedem Gelenk um Millimeter nahe;
 * das ist keine Frage der Gewichte.
 *
 * DER WEG, DEN JEDE SPIELENGINE GEHT — und MakeHuman mit `delete_verts`
 * (08.09.2026, dort 23,5 % der Anzugpunkte in der Haut, ohne dass man es
 * sieht): Die Haut unter dem Stoff wird nicht gezeichnet. Was nicht gezeichnet
 * wird, kann nicht durchkommen — in keiner Pose, mit oder ohne Weichgewebe,
 * ohne Rechenzeit je Bild.
 *
 * VERDECKT ist ein Körperpunkt, wenn der Strahl entlang seiner Normale ein
 * Stoffdreieck trifft
 *   * höchstens `ABSTAND_M` über der Haut (25 mm — das Kontaktband der
 *     Durchstich-Messungen vom 07.09.2026, `KONTAKT_M`),
 *   * höchstens `TIEFE_M` IN der Haut (ein Stoff, der schon 5 mm drinsteckt,
 *     zählt noch als darüber — genau die Fälle, um die es geht),
 *   * und das Dreieck nicht in einem freien Randstreifen liegt — siehe unten.
 * Gesucht wird nur bei den Dreiecken um den nächsten Stoffpunkt (Gitter),
 * nicht über das ganze Stück.
 *
 * DER RANDSTREIFEN GILT NUR AN LOCKEREN KANTEN (Edgar, gleicher Abend, mit
 * Bild: „besser mit durchscheinen, aber noch immer nicht gefixt"). Die erste
 * Fassung ließ an JEDER offenen Stoffkante (Saum, Bund, Ausschnitt) zwei
 * Nachbarringe Haut stehen, damit ein Saum, der sich hebt, kein Loch
 * freigibt. Am Bund der 2-mm-Leggings war dieser Streifen (1,6 cm) genau
 * die Haut, die in Dance1 weiter herauskam — Bild 32, sechs Splitter entlang
 * der Bundkante, Beine und Knie sauber. Eine Kante, die auf der Haut liegt,
 * hebt sich nicht; eine, die `ENG_M` (4 mm) oder mehr Luft hat, kann es.
 * Deshalb wird je Randpunkt des Stoffs gemessen, wie weit er über der Haut
 * liegt (Abstand entlang der Körpernormale des nächsten Körperpunkts): Nur
 * von LOCKEREN Randpunkten aus bleiben `RANDRINGE` Ringe frei; an einer
 * anliegenden Kante reicht die Maske bis zum Rand. Der Preis dort ist ein
 * höchstens millimeterbreiter Spalt, wenn die Kante in Bewegung über die
 * Haut rutscht — an einem schwarzen Bund unsichtbar, gegen weiße Splitter
 * der bessere Tausch.
 *
 * Ein Dreieck des Körpers fällt aus dem Index, wenn ALLE drei Ecken verdeckt
 * sind; die Materialgruppen (Haut, Augen, Zähne, …) werden nachgezogen —
 * ohne das läge das Material des Innenmunds über dem Bauch (dieselbe Falle
 * wie bei UMA am 08.09.2026, `addGroup` zählt Indexeinträge).
 *
 * OHNE THREE.JS UND OHNE DOM — damit die Rechnung in Node prüfbar ist
 * (`core/tests/unit/test_js_hautmaske.py`). Die Geometrie-Bausteine stehen
 * in `hautmaskegeometrie.js`, die Three.js-Seite in `scene/hautverdeckung.js`,
 * Stoff über Stoff in `lagenmaske.js`.
 */
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';
import { Maskeninseln } from './maskeninseln.js';

export class Hautmaske {

    /** Näher als das gilt als „unter dem Stoff" (Meter). */
    static ABSTAND_M = 0.025;
    /** So weit darf der Stoff schon IN der Haut stecken und zählt noch. */
    static TIEFE_M = 0.005;
    /** Nachbarringe um LOCKERE offene Stoffkanten, die frei bleiben. */
    static RANDRINGE = 2;
    /** Bis zu diesem Abstand über der Haut liegt eine Stoffkante AN. */
    static ENG_M = 0.004;
    /** Freie Inseln im Verdeckten bis zu dieser Punktzahl gelten als verdeckt. */
    static INSEL_MAX = 200;

    /**
     * Je Körperpunkt 1, wenn ihn eines der Stücke verdeckt.
     *
     * @param koerper      Float32Array/Float64Array, Punkte in Ruhelage (xyz)
     * @param dreiecke     Index des Körpers (drei Einträge je Dreieck)
     * @param stoffe       [{punkte, dreiecke}] — jedes Stück in derselben Lage
     * @param optionen     {abstand, tiefe, randringe, eng, normalen, suchweite, inseln}
     *                     `normalen`: fertige Punktnormalen des Körpers
     *                     (die Lagenmaske gibt einem Stoff die der Haut mit);
     *                     `suchweite`: Umkreis für den nächsten Stoffpunkt
     *                     (sonst das Größere von `abstand` und `tiefe`) —
     *                     Messungen fragen damit auch nach Stoff HINTER der
     *                     Haut (`abstand` negativ); `inseln`: Höchstgröße
     *                     freier Inseln, die noch geschlossen werden (0 = aus;
     *                     Messungen lassen die Maske roh).
     */
    static verdeckt(koerper, dreiecke, stoffe, optionen = {}) {
        const abstand = optionen.abstand ?? Hautmaske.ABSTAND_M;
        const tiefe = optionen.tiefe ?? Hautmaske.TIEFE_M;
        const ringe = optionen.randringe ?? Hautmaske.RANDRINGE;
        const eng = optionen.eng ?? Hautmaske.ENG_M;
        const suchweite = optionen.suchweite ?? Math.max(abstand, tiefe);
        const inseln = optionen.inseln ?? Hautmaske.INSEL_MAX;
        const n = koerper.length / 3;
        const maske = new Uint8Array(n);
        const normalen = optionen.normalen || G.normalen(koerper, dreiecke);
        const koerpergitter = G.punktgitter(koerper, G.ZELLE_M);
        const basis = { koerper, normalen, koerpergitter };
        for (const stoff of stoffe || []) {
            if (!stoff?.punkte?.length || !stoff?.dreiecke?.length) continue;
            Hautmaske._einStueck(basis, maske, stoff, abstand, tiefe, ringe, eng, suchweite);
        }
        if (inseln > 0 && dreiecke) Maskeninseln.schliessen(maske, dreiecke, inseln);
        return maske;
    }

    static _einStueck(basis, maske, stoff, abstand, tiefe, ringe, eng, suchweite) {
        const { koerper, normalen } = basis;
        const P = stoff.punkte, T = stoff.dreiecke, nP = P.length / 3;
        const { rand, nachbarn } = Hautmaske.randpunkte(T, nP);
        const locker = Hautmaske.lockereRandpunkte(P, rand, basis, eng);
        const ok = Hautmaske.dreieckeOhne(T, Hautmaske.ringeUm(locker, nachbarn, ringe));
        const umkreis = Hautmaske.dreieckeImUmkreis(T, nP, ok, nachbarn);
        const h = G.ZELLE_M;
        const gitter = G.punktgitter(P, h);
        // Nur Körperpunkte in der (erweiterten) Hülle des Stücks kommen in Frage.
        const huelle = G.huelle(P, suchweite);
        const grenze2 = suchweite * suchweite;
        for (let i = 0; i < maske.length; i++) {
            if (maske[i]) continue;
            const px = koerper[3 * i], py = koerper[3 * i + 1], pz = koerper[3 * i + 2];
            if (px < huelle[0] || px > huelle[3] || py < huelle[1] || py > huelle[4]
                || pz < huelle[2] || pz > huelle[5]) continue;
            const nah = G.naechsterPunkt(P, gitter, h, px, py, pz);
            if (!nah || nah.d2 > grenze2) continue;
            // Der Strahl entlang der Körpernormale, von `tiefe` in der Haut
            // bis `abstand` darüber, muss ein zulässiges Dreieck treffen.
            const nx = normalen[3 * i], ny = normalen[3 * i + 1], nz = normalen[3 * i + 2];
            const liste = umkreis(nah.j);
            for (let l = 0; l < liste.length; l++) {
                const k = liste[l];
                const t = G.strahlDreieck(P, T[k], T[k + 1], T[k + 2], px, py, pz, nx, ny, nz);
                if (t !== null && t >= -tiefe && t <= abstand) { maske[i] = 1; break; }
            }
        }
    }

    /**
     * Je Stoffpunkt die zulässigen Dreiecke bis zwei Nachbarringe weit —
     * gerechnet beim ersten Zugriff, dann gemerkt.
     *
     * WARUM DER STRAHL UND NICHT DER NÄCHSTE FLÄCHENPUNKT: Am Rand eines
     * anliegenden Stücks ist der nächste Flächenpunkt eines Körperpunkts
     * knapp jenseits der Kante die Kante selbst — 2 mm über der Haut, also
     * „darüber", und die Haut verschwände bis 25 mm über den Bund hinaus.
     * Der Strahl entlang der Normale trifft jenseits der Kante nichts.
     * Zwei Ringe reichen: Bei 8 mm Stoffnetz und 25 mm Abstand liegt der
     * Treffer höchstens 13 mm neben dem nächsten Stoffpunkt.
     */
    static dreieckeImUmkreis(T, n, ok, nachbarn) {
        const jePunkt = Hautmaske.dreieckeJePunkt(T, n, ok);
        const merker = new Array(n);
        return (j) => {
            if (merker[j]) return merker[j];
            const menge = new Set(jePunkt[j]);
            for (const w of nachbarn[j]) {
                for (const k of jePunkt[w]) menge.add(k);
                for (const x of nachbarn[w]) for (const k of jePunkt[x]) menge.add(k);
            }
            merker[j] = Array.from(menge);
            return merker[j];
        };
    }

    // ------------------------------------------------------------ Index

    /**
     * Der Index ohne Dreiecke, deren drei Ecken verdeckt sind. Die Gruppen
     * (`{start, count, materialIndex}`, in Indexeinträgen) folgen mit.
     * Ohne Gruppen gilt der ganze Index als eine.
     */
    static indexOhne(index, gruppen, maske) {
        const quellen = (gruppen && gruppen.length)
            ? gruppen
            : [{ start: 0, count: index.length, materialIndex: 0 }];
        const behalten = new Uint32Array(index.length);
        const neueGruppen = [];
        let lauf = 0, entfernt = 0;
        for (const g of quellen) {
            const start = lauf;
            const ende = Math.min(g.start + g.count, index.length);
            for (let k = g.start; k + 2 < ende; k += 3) {
                const a = index[k], b = index[k + 1], c = index[k + 2];
                if (maske[a] && maske[b] && maske[c]) { entfernt += 1; continue; }
                behalten[lauf] = a; behalten[lauf + 1] = b; behalten[lauf + 2] = c;
                lauf += 3;
            }
            neueGruppen.push({ start, count: lauf - start, materialIndex: g.materialIndex ?? 0 });
        }
        return { index: behalten.slice(0, lauf),
                 gruppen: (gruppen && gruppen.length) ? neueGruppen : [],
                 entfernt };
    }

    // ------------------------------------------------------------- Rand

    /** Die Punkte an offenen Kanten (Kante in genau einem Dreieck) und
     *  die Nachbarn je Punkt. */
    static randpunkte(T, n) {
        const zaehler = new Map(), nachbarn = Array.from({ length: n }, () => []);
        for (let k = 0; k + 2 < T.length; k += 3) {
            for (const [a, b] of [[T[k], T[k + 1]], [T[k + 1], T[k + 2]], [T[k + 2], T[k]]]) {
                const s = a < b ? a * n + b : b * n + a;
                const bisher = zaehler.get(s) || 0;
                zaehler.set(s, bisher + 1);
                if (!bisher) { nachbarn[a].push(b); nachbarn[b].push(a); }
            }
        }
        const rand = new Set();
        for (const [s, c] of zaehler) if (c === 1) { rand.add(Math.floor(s / n)); rand.add(s % n); }
        return { rand, nachbarn };
    }

    /**
     * Die Randpunkte, die LOCKER über der Haut liegen: mehr als `eng` entlang
     * der Normale des nächsten Körperpunkts — oder ohne Körper in Reichweite
     * (drei Zellen, 9 cm). Nur von ihnen aus bleibt ein Streifen frei.
     */
    static lockereRandpunkte(P, rand, basis, eng) {
        const { koerper, normalen, koerpergitter } = basis;
        const locker = new Set();
        for (const v of rand) {
            const qx = P[3 * v], qy = P[3 * v + 1], qz = P[3 * v + 2];
            const nah = G.naechsterPunkt(koerper, koerpergitter, G.ZELLE_M, qx, qy, qz);
            if (!nah) { locker.add(v); continue; }
            const i = nah.j;
            const d = (qx - koerper[3 * i]) * normalen[3 * i] + (qy - koerper[3 * i + 1]) * normalen[3 * i + 1]
                    + (qz - koerper[3 * i + 2]) * normalen[3 * i + 2];
            if (Math.abs(d) > eng) locker.add(v);
        }
        return locker;
    }

    /** `start` um `ringe` Nachbarringe erweitert. */
    static ringeUm(start, nachbarn, ringe) {
        let menge = new Set(start);
        for (let r = 0; r < ringe; r++) {
            const neu = new Set(menge);
            for (const v of menge) for (const w of nachbarn[v]) neu.add(w);
            menge = neu;
        }
        return menge;
    }

    /** Je Dreieck 1, wenn keine Ecke in `gesperrt` liegt. */
    static dreieckeOhne(T, gesperrt) {
        const ok = new Uint8Array(T.length / 3);
        for (let k = 0; k + 2 < T.length; k += 3) {
            ok[k / 3] = (gesperrt.has(T[k]) || gesperrt.has(T[k + 1]) || gesperrt.has(T[k + 2])) ? 0 : 1;
        }
        return ok;
    }

    /** Je Stoffpunkt die Anfänge der zulässigen Dreiecke, die ihn berühren. */
    static dreieckeJePunkt(T, n, ok) {
        const je = Array.from({ length: n }, () => []);
        for (let k = 0; k + 2 < T.length; k += 3) {
            if (!ok[k / 3]) continue;
            je[T[k]].push(k); je[T[k + 1]].push(k); je[T[k + 2]].push(k);
        }
        return je;
    }
}
