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
    /** Weiter wird nicht gesucht (Meter): Bei `Saumband.TIEFE_M` 10 mm und
     *  `ANTEIL` 0,4 begrenzt eine Dicke über 25 mm nichts mehr. */
    static REICHWEITE_M = 0.025;
    /** Seitlicher Spielraum um den Strahl (Meter), mindestens. */
    static QUER_M = 0.002;
    /** Zellgröße des Suchgitters = Reichweite: 27 Zellen je Punkt statt 343
     *  bei 1 cm (dort war die Hautverdeckung 7,6 s statt 6,0 s). */
    static ZELLE_M = 0.025;

    /**
     * Je Punkt die Dicke (Meter) — `Infinity`, wo nichts gegenüber liegt oder
     * `auswahl[i]` 0 ist (nur ausgewählte Punkte werden gemessen).
     * @param P        Punkte xyz (Ruhelage)
     * @param N        normierte Außennormalen xyz (`Hautmaskegeometrie.normalen`)
     * @param auswahl  je Punkt 1 = messen (die verdeckten)
     */
    static dicken(P, N, auswahl) {
        const n = P.length / 3;
        const aus = new Float32Array(n).fill(Infinity);
        const h = Hautdicke.ZELLE_M;
        const r = Math.ceil(Hautdicke.REICHWEITE_M / h);
        const vorrat = Hautdicke._vorratFuer(P, h);
        for (let i = 0; i < n; i++) {
            if (!auswahl[i]) continue;
            if (Number.isNaN(vorrat.dicke[i])) vorrat.dicke[i] = Hautdicke._dicke(P, N, vorrat.gitter, h, r, i);
            aus[i] = vorrat.dicke[i];
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
            v = { gitter: Hautmaskegeometrie.punktgitter(P, h), dicke: new Float32Array(P.length / 3).fill(NaN) };
            Hautdicke._vorrat.set(P, v);
        }
        return v;
    }

    static _dicke(P, N, gitter, h, r, i) {
        const px = P[3 * i], py = P[3 * i + 1], pz = P[3 * i + 2];
        const nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
        const ci = Math.floor(px / h), cj = Math.floor(py / h), ck = Math.floor(pz / h);
        let best = Infinity;
        for (let a = -r; a <= r; a++) for (let b = -r; b <= r; b++) for (let c = -r; c <= r; c++) {
            const L = gitter.get(Hautmaskegeometrie.zelle(ci + a, cj + b, ck + c));
            if (!L) continue;
            for (let l = 0; l < L.length; l++) {
                const j = L[l];
                // Abgewandt: die Haut der Gegenseite schaut in die andere Richtung.
                if (N[3 * j] * nx + N[3 * j + 1] * ny + N[3 * j + 2] * nz >= 0) continue;
                const dx = px - P[3 * j], dy = py - P[3 * j + 1], dz = pz - P[3 * j + 2];
                const tiefe = dx * nx + dy * ny + dz * nz;          // > 0: j liegt dahinter
                if (tiefe <= 0 || tiefe >= best || tiefe > Hautdicke.REICHWEITE_M) continue;
                const qx = dx - tiefe * nx, qy = dy - tiefe * ny, qz = dz - tiefe * nz;
                const quer = Math.max(Hautdicke.QUER_M, 0.5 * tiefe);
                if (qx * qx + qy * qy + qz * qz <= quer * quer) best = tiefe;
            }
        }
        return best;
    }

    /** Der höchste Einzug (Meter) bei dieser Dicke. */
    static grenze(dicke) {
        return Hautdicke.ANTEIL * dicke;
    }
}
