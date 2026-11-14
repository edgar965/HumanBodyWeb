import { Hautmaskegeometrie } from './hautmaskegeometrie.js';

/**
 * Hautdicke — wie dick der Körper unter einem Punkt ist, entlang seiner
 * Normale nach innen gemessen (bis zur gegenüberliegenden Haut).
 *
 * BEFUND (24.09.2026, Edgar mit Bild: an Ursulas Angie Sneakers stehen an der
 * Kappe zwei hautfarbene Flecken, „heute morgen war das nicht da"): Es waren
 * die ZEHENNÄGEL. Unter dem Schuh gelten sie als verdeckt und liegen im
 * Saumband, also versenkt `Hauteinzug` sie um `Saumband.TIEFE_M` = 10 mm nach
 * innen. Ein kleiner Zeh ist aber nur gut 10 mm dick: Der Rand des Nagels
 * (Normale zur Seite) wanderte quer durch den Zeh und kam an der anderen Seite
 * vor der Schuhwand heraus. Im Browser gemessen: mit Nagel-Einzug 0 waren die
 * Flecken weg, Oberflächenbindung und Gelenkkorrekturen änderten nichts.
 *
 * Deshalb wird der Einzug auf `ANTEIL` der Dicke begrenzt — ein versenkter
 * Punkt bleibt immer auf seiner Seite des Körpers. Am Rumpf (Dicke 20 cm und
 * mehr) ändert das nichts, an Zehen, Fingern und Ohren begrenzt es.
 *
 * GEMESSEN wird an Punkten, nicht an Dreiecken (Tempo): Gegenüber ist jeder
 * Punkt HINTER dem Punkt (entlang −N), mit abgewandter Normale und höchstens
 * `QUER` seitlich (oder der halben Tiefe) neben dem Strahl. Ohne solchen Punkt
 * bis `REICHWEITE_M` gilt die Dicke als unbegrenzt.
 *
 * Ohne Three.js, damit `test_js_hautdicke` es in Node prüft.
 */
export class Hautdicke {

    /** So viel der Dicke darf der Einzug höchstens nehmen. */
    static ANTEIL = 0.4;
    /** Weiter wird ohne Angabe nicht gesucht (Meter): Bei `Saumband.TIEFE_M` 10 mm und
     *  `ANTEIL` 0,4 begrenzt eine Dicke über 25 mm nichts mehr. Mit „Haut gibt nach“
     *  (`Bauart`, bis 50 mm) bekommt jeder Punkt seine Reichweite `bis / ANTEIL`
     *  (`dicken(…, reichweiten)`) — sonst gälte ein 60 mm dicker Knöchel unter einem
     *  Einzug von 30 mm als unbegrenzt, und beide Seiten träfen sich (12.11.2026). */
    static REICHWEITE_M = 0.025;
    /** Seitlicher Spielraum um den Strahl (Meter), mindestens. */
    static QUER_M = 0.002;
    /** … und höchstens: die Hälfte der Tiefe, aber nicht mehr als die Hälfte der alten
     *  Reichweite — bis 25 mm Tiefe misst das wie vorher, tiefer bleibt der Strahl schmal. */
    static QUER_MAX_M = 0.0125;
    /** Zellgröße des Suchgitters = Reichweite: 27 Zellen je Punkt statt 343
     *  bei 1 cm (dort war die Hautverdeckung 7,6 s statt 6,0 s). */
    static ZELLE_M = 0.025;

    /**
     * Je Punkt die Dicke (Meter) — `Infinity`, wo nichts gegenüber liegt oder
     * `auswahl[i]` 0 ist (nur ausgewählte Punkte werden gemessen).
     * @param P        Punkte xyz (Ruhelage)
     * @param N        normierte Außennormalen xyz (`Hautmaskegeometrie.normalen`)
     * @param auswahl  je Punkt 1 = messen (die verdeckten)
     * @param reichweiten  je Punkt die Suchweite (Meter), 0 oder ohne = `REICHWEITE_M`
     */
    static dicken(P, N, auswahl, reichweiten = null) {
        const n = P.length / 3;
        const aus = new Float32Array(n).fill(Infinity);
        const h = Hautdicke.ZELLE_M;
        const vorrat = Hautdicke._vorratFuer(P, h);
        for (let i = 0; i < n; i++) {
            if (!auswahl[i]) continue;
            const weit = Math.max(Hautdicke.REICHWEITE_M, (reichweiten && reichweiten[i]) || 0);
            // Gemerkt wird mit der Weite, bis zu der gesucht wurde: „unbegrenzt bis 25 mm“ heißt nichts für 75 mm.
            if (Number.isNaN(vorrat.dicke[i]) || (vorrat.dicke[i] === Infinity && vorrat.weite[i] < weit)) {
                vorrat.dicke[i] = Hautdicke._dicke(P, N, vorrat.gitter, h, i, weit);
                vorrat.weite[i] = weit;
            }
            aus[i] = vorrat.dicke[i] <= weit ? vorrat.dicke[i] : Infinity;
        }
        return aus;
    }

    /** Punkte-Feld → {gitter, dicke (NaN = noch nicht gemessen)}. Die Dicke
     *  hängt nur am Körper, nicht an der Kleidung: Ein Kleiderwechsel misst
     *  nur neu verdeckte Punkte (gemessen 24.09.2026: sonst 1,1–1,5 s je Lauf
     *  bei 104.480 Punkten). Ein neuer Körper hat ein neues Feld. */
    static _vorrat = new WeakMap();

    static _vorratFuer(P, h) {
        let v = Hautdicke._vorrat.get(P);
        if (!v) {
            const anzahl = P.length / 3;
            v = { gitter: Hautmaskegeometrie.punktgitter(P, h), dicke: new Float32Array(anzahl).fill(NaN), weite: new Float32Array(anzahl) };
            Hautdicke._vorrat.set(P, v);
        }
        return v;
    }

    /**
     * Die Dicke an Punkt `i` bis `weit` (Meter). Bis zur Zellweite die 27 Zellen um den Punkt (wie bisher), weiter
     * entlang −N je Zellweite noch einmal die 27 Zellen um den Strahl, vorn zuerst; hat ein Schritt getroffen, liegt
     * nichts Näheres weiter hinten.
     */
    static _dicke(P, N, gitter, h, i, weit = Hautdicke.REICHWEITE_M) {
        const px = P[3 * i], py = P[3 * i + 1], pz = P[3 * i + 2];
        const nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
        const schritte = Math.max(0, Math.ceil(weit / h) - 1);
        const gesehen = schritte ? new Set() : null;
        let best = Infinity;
        for (let s = 0; s <= schritte; s++) {
            if (best < (s - 1) * h) break;
            const ci = Math.floor((px - s * h * nx) / h), cj = Math.floor((py - s * h * ny) / h), ck = Math.floor((pz - s * h * nz) / h);
            for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
                const zelle = Hautmaskegeometrie.zelle(ci + a, cj + b, ck + c);
                if (gesehen) { if (gesehen.has(zelle)) continue; gesehen.add(zelle); }
                const L = gitter.get(zelle);
                if (!L) continue;
                for (let l = 0; l < L.length; l++) {
                    const j = L[l];
                    // Abgewandt: die Haut der Gegenseite schaut in die andere Richtung.
                    if (N[3 * j] * nx + N[3 * j + 1] * ny + N[3 * j + 2] * nz >= 0) continue;
                    const dx = px - P[3 * j], dy = py - P[3 * j + 1], dz = pz - P[3 * j + 2];
                    const tiefe = dx * nx + dy * ny + dz * nz;          // > 0: j liegt dahinter
                    if (tiefe <= 0 || tiefe >= best || tiefe > weit) continue;
                    const qx = dx - tiefe * nx, qy = dy - tiefe * ny, qz = dz - tiefe * nz;
                    const quer = Math.max(Hautdicke.QUER_M, Math.min(0.5 * tiefe, Hautdicke.QUER_MAX_M));
                    if (qx * qx + qy * qy + qz * qz <= quer * quer) best = tiefe;
                }
            }
        }
        return best;
    }

    /** Der höchste Einzug (Meter) bei dieser Dicke. */
    static grenze(dicke) {
        return Hautdicke.ANTEIL * dicke;
    }
}
