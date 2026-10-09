/**
 * Stueckdeckung — Hautdreiecke, die VOR dem Inneren eines Ersatzstücks liegen, fallen weg.
 *
 * BEFUND (Edgar, 09.10.2026: „noch nicht an der Haut dran", mit Bild): Nach dem Senken der Haut auf das Stück
 * (`hautanschmiegung.js`) standen im Inneren des Stücks noch große Platten Haut davor. Gemessen am Stück „cute girl Scham"
 * (Strahl von der Dreiecksmitte nach innen gegen alle Stückdreiecke, `ProjektTemp/_wegwerf/cutegirl/chrome_haut_vor_stueck.js`,
 * 336 Hautdreiecke nahe dem Stück): 0–2 mm vom Stückrand liegt die Haut im Median 2,2 mm HINTER dem Stück (gut), 6–9 mm
 * im Median 3,0 mm davor, 9–15 mm 6,7 mm davor, über 15 mm 13,3 mm davor — es sind die großen Dreiecke am Schritt und in den
 * Leisten (10–20 mm), deren Ecken die Punktprüfung nicht als „innen" fand, deren Fläche aber über der Furche spannt.
 *
 * Die Prüfung ist eine der FLÄCHE, nicht der Punkte: Ein Hautdreieck fällt weg, wenn seine Mitte (nach dem Einzug) und
 * mindestens zwei Ecken in Richtung der Hautnormale auf das Stück treffen und die Mitte mehr als `STARK_M` davor liegt — oder
 * Mitte/Ecke mehr als `MIN_DAVOR_M` davor liegen und der Treffer weiter als `grenze` vom Netzrand des Stücks entfernt ist. Im
 * Auslauf bleibt knapp davor liegende Haut — sie liegt dort fast bündig unter dem Stück, durch dessen weichen Rand sie
 * durchscheint (`stueckfeder.js`).
 *
 * SCHNELL: Die Stückdreiecke liegen in einem Gitter (`ZELLE_M`); ein Strahl wird alle `SCHRITT_M` abgetastet und prüft nur
 * die Dreiecke der Zellen darunter (4.000 Dreiecke, 1.500 Hautdreiecke: Millisekunden statt Sekunden).
 *
 * Ohne Three.js und ohne DOM (Node-Test `test_js_hautanschmiegung.py`).
 */
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';
import { Stueckrand } from './stueckrand.js';

export class Stueckdeckung {

    /** So viel (m) muss die Mitte oder eine Ecke des Hautdreiecks vor der Stückfläche liegen, damit das Dreieck wegfallen kann. */
    static MIN_DAVOR_M = 0.0003;
    /** Liegt die Mitte so weit (m) davor, fällt das Dreieck auch im Auslauf des Stückrands weg. */
    static STARK_M = 0.002;
    /** Die Strahlen beginnen so weit (m) über der Haut und reichen so weit (m) hinter sie. */
    static HOEHE_M = 0.04;
    static TIEFE_M = 0.03;
    /** Gitterzelle (m) für die Stückdreiecke und Abtastschritt (m) entlang des Strahls. */
    static ZELLE_M = 0.006;
    static SCHRITT_M = 0.002;

    /**
     * Je Dreieck des Index 1, wenn es wegfallen soll.
     * @param koerper  Punkte xyz der Haut (Ruhelage)
     * @param einzug   `einzug`-Feld (xyz je Punkt, nach innen) — die Punkte werden damit verschoben geprüft
     * @param normalen Punktnormalen der Haut nach außen
     * @param index    Index der Haut
     * @param stoff    `{punkte, dreiecke, randabstand}` des Ersatzstücks (ohne `randabstand` wird er gerechnet)
     * @param grenze   Abstand (m) vom Netzrand, ab dem davor liegende Haut wegfällt (`Stueckrand.FEDER_M`: der weiche Rand)
     * @param aus      optional: ein Feld je Dreieck, in das geschrieben wird (mehrere Stücke teilen es)
     */
    static dreiecke(koerper, einzug, normalen, index, stoff, grenze, aus) {
        const weg = aus || new Uint8Array(index.length / 3);
        const P = stoff.punkte, T = stoff.dreiecke;
        const rand = stoff.randabstand || Stueckrand.randabstand(P, T, grenze + 0.01);
        const huelle = G.huelle(P, Stueckdeckung.HOEHE_M);
        const suche = Stueckdeckung._gitter(P, T);
        for (let k = 0; k + 2 < index.length; k += 3) {
            const auf = Stueckdeckung._aufStueck(koerper, einzug, normalen, index, k, P, T, suche, huelle);
            if (!auf) continue;
            const treffer = auf.treffer, davor = auf.davor;
            // Das Dreieck muss zum größten Teil auf dem Stück liegen (Mitte und mindestens zwei Ecken treffen): ein Dreieck, das über den
            // Stückrand hinausragt, ließe beim Entfernen ein Loch bis zum Hintergrund (gesehen 09.10.2026: dunkle Keile in den Leisten,
            // bei „Fülle" +2 groß).
            // Weit davor (Platte über der Furche, gemessen 7–8 mm vor dem Stück): weg, auch im Auslauf des Stückrands — als braune Platte
            // stand sie vor der linken Lippe (gesehen 09.10.2026). Knapp davor — Mitte ODER eine Ecke —: nur im Inneren, nicht im
            // Auslauf: dort ist das Stück noch durchscheinend, und das Loch ließe den Hintergrund sehen. Die Zähne am Lochrand sind
            // Dreiecke, deren Ecke durch die Stückfläche stößt, obwohl die Mitte schon dahinter liegt (helle Zacken in den Leisten).
            if (treffer.davor >= Stueckdeckung.STARK_M) { weg[k / 3] = 1; continue; }
            if (davor < Stueckdeckung.MIN_DAVOR_M) continue;
            const d = Math.min(rand[T[treffer.dreieck]], rand[T[treffer.dreieck + 1]], rand[T[treffer.dreieck + 2]]);
            if (d > grenze) weg[k / 3] = 1;
        }
        return weg;
    }

    /**
     * Welche der `pruefen`-Dreiecke (Feld je Dreieck, 1 = prüfen) liegen zum größten Teil auf dem Stück (Mitte und mindestens zwei
     * Ecken treffen), gleich wie weit davor? Setzt `aus[k / 3] = 1` für die gedeckten und gibt `aus` zurück.
     *
     * BEFUND (Fallout ranger, 09.10.2026, Chrome, Haut mit und ohne Scham-Stück verglichen): Von 284 entfernten Hautdreiecken
     * deckte das Stück 200 ganz, 26 zur Hälfte und 58 GAR NICHT (Mitten bei x ±20…40 mm, y 847…876 mm: die Leisten) — dort
     * stand die Haut weg, und nichts dahinter; +61.000 Pixel Hintergrund von unten, +50.000 von hinten unten.
     */
    static gedeckt(koerper, einzug, normalen, index, stoff, pruefen, aus, grenze, anteil) {
        const P = stoff.punkte, T = stoff.dreiecke;
        const huelle = G.huelle(P, Stueckdeckung.HOEHE_M);
        const suche = Stueckdeckung._gitter(P, T);
        // Mit `grenze` (m): nur, wenn das getroffene Stückdreieck weiter als `grenze` vom Netzrand liegt (nicht im weichen Rand).
        const rand = grenze ? (stoff.randabstand || Stueckrand.randabstand(P, T, grenze + 0.01)) : null;
        const innen = (t) => !rand || Math.min(rand[T[t]], rand[T[t + 1]], rand[T[t + 2]]) > grenze;
        for (let k = 0; k + 2 < index.length; k += 3) {
            if (!pruefen[k / 3] || aus[k / 3]) continue;
            if (anteil) {
                if (Stueckdeckung._anteil(koerper, einzug, normalen, index, k, P, T, suche, innen) >= anteil) aus[k / 3] = 1;
                continue;
            }
            const auf = Stueckdeckung._aufStueck(koerper, einzug, normalen, index, k, P, T, suche, huelle);
            if (auf && innen(auf.treffer.dreieck)) aus[k / 3] = 1;
        }
        return aus;
    }

    /**
     * Anteil (0 … 1) von sieben Stellen des Dreiecks — Mitte, drei Ecken, drei Kantenmitten (nach dem Einzug, Strahl gegen die Hautnormale)
     * —, die auf dem Stück liegen und `innen(Stückdreieck)` erfüllen. Für schräge Splitter, deren Ecken teils neben dem Stück liegen.
     */
    static _anteil(koerper, einzug, normalen, index, k, P, T, suche, innen) {
        const e = [index[k], index[k + 1], index[k + 2]];
        const lage = e.map((i) => [koerper[3 * i] + einzug[3 * i], koerper[3 * i + 1] + einzug[3 * i + 1], koerper[3 * i + 2] + einzug[3 * i + 2]]);
        const nor = e.map((i) => [normalen[3 * i], normalen[3 * i + 1], normalen[3 * i + 2]]);
        const mix = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
        const einheit = (v) => { const l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };
        const mittel = einheit([nor[0][0] + nor[1][0] + nor[2][0], nor[0][1] + nor[1][1] + nor[2][1], nor[0][2] + nor[1][2] + nor[2][2]]);
        const stellen = [[[(lage[0][0] + lage[1][0] + lage[2][0]) / 3, (lage[0][1] + lage[1][1] + lage[2][1]) / 3,
                           (lage[0][2] + lage[1][2] + lage[2][2]) / 3], mittel]];
        for (let a = 0; a < 3; a++) {
            stellen.push([lage[a], nor[a]]);
            stellen.push([mix(lage[a], lage[(a + 1) % 3]), einheit(mix(nor[a], nor[(a + 1) % 3]))]);
        }
        let treffer = 0;
        for (const [p, n] of stellen) {
            const t = Stueckdeckung._trifft(P, T, suche, p, n);
            if (t && innen(t.dreieck)) treffer++;
        }
        return treffer / stellen.length;
    }

    /**
     * Das Dreieck ab `index[k]` auf dem Stück: `{treffer, davor}` — `treffer` der Strahl der Mitte, `davor` das größte Davor von Mitte
     * und Ecken (m) — oder null, wenn die Mitte außerhalb der Hülle liegt, ihr Strahl nichts trifft oder weniger als zwei Ecken treffen.
     */
    static _aufStueck(koerper, einzug, normalen, index, k, P, T, suche, huelle) {
        const ecken = [index[k], index[k + 1], index[k + 2]];
        const mitte = [0, 0, 0], nm = [0, 0, 0], lagen = [];
        for (const i of ecken) {
            const lage = [koerper[3 * i] + einzug[3 * i], koerper[3 * i + 1] + einzug[3 * i + 1],
                          koerper[3 * i + 2] + einzug[3 * i + 2]];
            lagen.push(lage);
            for (let d = 0; d < 3; d++) { mitte[d] += lage[d] / 3; nm[d] += normalen[3 * i + d]; }
        }
        if (mitte[0] < huelle[0] || mitte[0] > huelle[3] || mitte[1] < huelle[1] || mitte[1] > huelle[4]
            || mitte[2] < huelle[2] || mitte[2] > huelle[5]) return null;
        const ln = Math.hypot(nm[0], nm[1], nm[2]) || 1;
        nm[0] /= ln; nm[1] /= ln; nm[2] /= ln;
        const treffer = Stueckdeckung._trifft(P, T, suche, mitte, nm);
        if (!treffer) return null;
        let davor = treffer.davor, getroffen = 0;
        for (let e = 0; e < 3; e++) {
            const ne = [normalen[3 * ecken[e]], normalen[3 * ecken[e] + 1], normalen[3 * ecken[e] + 2]];
            const te = Stueckdeckung._trifft(P, T, suche, lagen[e], ne);
            if (te) { getroffen++; if (te.davor > davor) davor = te.davor; }
        }
        return getroffen < 2 ? null : { treffer, davor };
    }

    /** Zelle → Dreiecke (Nummer des ersten Index) des Stücks; jedes Dreieck steht in allen Zellen seiner um 1,1 mm erweiterten Hülle. */
    static _gitter(P, T) {
        const h = Stueckdeckung.ZELLE_M, m = 0.0011, gitter = new Map();
        for (let t = 0; t + 2 < T.length; t += 3) {
            const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
            for (let e = 0; e < 3; e++) for (let d = 0; d < 3; d++) {
                const x = P[3 * T[t + e] + d];
                if (x < lo[d]) lo[d] = x;
                if (x > hi[d]) hi[d] = x;
            }
            for (let i = Math.floor((lo[0] - m) / h); i <= Math.floor((hi[0] + m) / h); i++) {
                for (let j = Math.floor((lo[1] - m) / h); j <= Math.floor((hi[1] + m) / h); j++) {
                    for (let l = Math.floor((lo[2] - m) / h); l <= Math.floor((hi[2] + m) / h); l++) {
                        const s = G.zelle(i, j, l), liste = gitter.get(s);
                        if (liste) liste.push(t); else gitter.set(s, [t]);
                    }
                }
            }
        }
        return gitter;
    }

    /** Der äußerste Treffer des Strahls von `p` (+ HOEHE_M entlang `n`) nach innen: `{dreieck, davor}` (davor in m) oder null. */
    static _trifft(P, T, gitter, p, n) {
        const h = Stueckdeckung.HOEHE_M, z = Stueckdeckung.ZELLE_M, schritt = Stueckdeckung.SCHRITT_M;
        const ox = p[0] + h * n[0], oy = p[1] + h * n[1], oz = p[2] + h * n[2];
        const gesehen = new Set();
        let best = Infinity, bj = -1;
        for (let s = 0; s <= h + Stueckdeckung.TIEFE_M + 1e-9; s += schritt) {
            const liste = gitter.get(G.zelle(Math.floor((ox - s * n[0]) / z), Math.floor((oy - s * n[1]) / z),
                                              Math.floor((oz - s * n[2]) / z)));
            if (!liste) continue;
            for (const t of liste) {
                if (gesehen.has(t)) continue;
                gesehen.add(t);
                const r = G.strahlDreieck(P, T[t], T[t + 1], T[t + 2], ox, oy, oz, -n[0], -n[1], -n[2]);
                if (r !== null && r > 0 && r < best) { best = r; bj = t; }
            }
        }
        return bj < 0 ? null : { dreieck: bj, davor: best - h };
    }
}
