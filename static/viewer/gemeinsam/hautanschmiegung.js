/**
 * Hautanschmiegung — die Haut senkt sich auf ein ERSATZSTÜCK und läuft neben ihm sanft aus (die Scham aus einer .blend).
 *
 * BEFUND (Edgar, 09.10.2026, mit Bild: „die ist ja wie aus der Haut ausgeschnitten", „die soll mit der Nachbarhaut
 * verschmelzen, das funktioniert nicht"): Das Stück hat die Form des ORIGINALS, die Figur-Haut steht dort bis 22 mm davor
 * (gemessen am Rand des Stücks „cute girl Scham": Median 5,1 mm, p10 −9,3 mm hinter der Haut; zwei Kanten weiter innen 12 mm,
 * im Inneren 17–22 mm). Wo die Haut wegfiel, stand ein Rand von Haut, ein Sprung von Millimetern, eine Treppenkante der
 * Dreiecke und dazwischen Löcher bis zum Hintergrund.
 *
 * DER WEG: Die Haut ist im Original so tief wie das Stück — sie folgt ihm. Jeder Körperpunkt, den das Stück verdeckt
 * (`hautmaskeersatz.js`), sinkt entlang seiner Normale auf die Fläche des Stücks (`hoehe`) und noch `UNTER_M` darunter, damit
 * das Stück vorn liegt. Die Haut neben dem Stück sinkt mit, mit der Senkung der nächsten verdeckten Punkte und einem Auslauf
 * über `KRAGEN_M` (Hermite, 0 am Ende). Der Rand, den `Hautmaskeersatz.innen` stehen lässt, liegt damit auf der Fläche
 * des Stücks statt davor — keine Stufe, kein Loch; was vom Stück nicht gedeckt ist, zeigt Haut in derselben Höhe.
 *
 * Gerechnet wird in der Ruhelage; die Senkung wirkt als `einzug` im Shader vor dem Skinning (`hauteinzug.js`) und dreht mit
 * jedem Knochen mit. Ohne Three.js und ohne DOM (Node-Test `test_js_hautanschmiegung.py`).
 */
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';
import { Stueckrand } from './stueckrand.js';

export class Hautanschmiegung {

    /** So weit (m) neben dem Stück läuft die Senkung aus. */
    static KRAGEN_M = 0.025;
    /** So viel (m) tiefer als die Fläche des Stücks liegt die Haut am Rand des Stücks — es gewinnt die Tiefenprüfung. */
    static UNTER_M = 0.0005;
    /**
     * Dazu kommt nach innen, bis `Stueckrand.FEDER_M` vom Rand (Hermite): Zwischen den Hautpunkten (4–8 mm) weicht die Fläche
     * des Stücks um ±1–2 mm von der der Haut ab; bei 1,5 mm Abstand deckte die Haut 2–6 mm vom Rand das Stück stellenweise ab
     * (gemessen 09.10.2026: Haut im Median 0,3 mm HINTER dem Stück, p90 1,45 mm DAVOR) — harte Linien in der Farbe. Am Rand
     * selbst bleibt die Haut bündig, sonst stünde dort eine Stufe.
     */
    static UNTER_TIEF_M = 0.0035;
    /** Tiefste Senkung (m) — nicht tiefer, als die Haut dick ist. */
    static GRENZE_M = 0.03;
    /** Nur Punkte mit Normalen in diese Richtung (Kosinus) geben ihre Senkung weiter — nicht auf den anderen Schenkel. */
    static GLEICHRICHTUNG = 0.5;
    /** Die nächsten Quellen bis so weit (m) hinter der allernächsten werden gemittelt. */
    static MISCHEN_M = 0.008;
    /** Durchgänge, in denen die Senkung über die Hautnachbarn gemittelt wird. */
    static GLAETTEN = 4;

    /**
     * Die Senkung (m, ≥ 0) je Körperpunkt.
     * @param koerper  Punkte xyz (Ruhelage)
     * @param normalen Punktnormalen nach außen
     * @param ersatz   1 = ein Ersatzstück verdeckt den Punkt
     * @param hoehe    Höhe (m) des Stücks über dem Punkt (auch für Haut NEBEN dem Stück, `RADIUS_SENKUNG_M`), −Infinity ohne
     * @param maske    1 = verdeckt (von einem Stoff oder dem Ersatzstück)
     * @param dreiecke Index der Haut (Glättung über die Nachbarn); null ohne
     * @param rand     Abstand (m) des Stückpunkts vom Netzrand des Stücks (Infinity ohne) — je weiter innen, desto tiefer die Haut
     */
    static senkung(koerper, normalen, ersatz, hoehe, maske, dreiecke, rand) {
        const n = ersatz.length, s = new Float32Array(n);
        const quellen = [];
        for (let i = 0; i < n; i++) {
            if (hoehe[i] === -Infinity) continue;
            const x = rand && ersatz[i] ? Math.min(rand[i] / Stueckrand.FEDER_M, 1) : 0;
            const unter = Hautanschmiegung.UNTER_M + Hautanschmiegung.UNTER_TIEF_M * x * x * (3 - 2 * x);
            s[i] = Math.min(Math.max(-hoehe[i], 0), Hautanschmiegung.GRENZE_M) + unter;
            quellen.push(i);
        }
        if (!quellen.length) return s;
        const K = Hautanschmiegung.KRAGEN_M;
        const Q = new Float32Array(3 * quellen.length);
        quellen.forEach((i, k) => Q.set(koerper.subarray(3 * i, 3 * i + 3), 3 * k));
        const gitter = G.punktgitter(Q, K), huelle = G.huelle(Q, K);
        for (let i = 0; i < n; i++) {
            if (maske[i] || hoehe[i] !== -Infinity) continue;
            const px = koerper[3 * i], py = koerper[3 * i + 1], pz = koerper[3 * i + 2];
            if (px < huelle[0] || px > huelle[3] || py < huelle[1] || py > huelle[4]
                || pz < huelle[2] || pz > huelle[5]) continue;
            s[i] = Hautanschmiegung._auslauf(koerper, normalen, i, quellen, s, Q, gitter);
        }
        if (dreiecke) Hautanschmiegung._glaetten(s, dreiecke, quellen);
        return s;
    }

    /**
     * Die Senkung über die Hautnachbarn mitteln (`GLAETTEN` Durchgänge): sie springt von Punkt zu Punkt, wo das Stück in den
     * Leisten steil steht, und die Dreiecke dazwischen standen als Splitter (gesehen 09.10.2026, von vorn unten). Punkte unter
     * dem Stück werden dabei nur tiefer, nie flacher — die Haut bleibt unter ihm.
     */
    static _glaetten(s, dreiecke, quellen) {
        const n = s.length, aktiv = new Uint8Array(n);
        for (let i = 0; i < n; i++) if (s[i] > 0) aktiv[i] = 1;
        const nachbarn = new Map();
        const verbinden = (a, b) => { if (!nachbarn.has(a)) nachbarn.set(a, []); nachbarn.get(a).push(b); };
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            if (!(aktiv[a] || aktiv[b] || aktiv[c])) continue;
            for (const [x, y] of [[a, b], [b, c], [c, a]]) { verbinden(x, y); verbinden(y, x); }
        }
        const unter = new Uint8Array(n);
        for (const i of quellen) unter[i] = 1;
        for (let durchgang = 0; durchgang < Hautanschmiegung.GLAETTEN; durchgang++) {
            const neu = Float32Array.from(s);
            for (const [i, liste] of nachbarn) {
                if (!aktiv[i] && !liste.some((j) => aktiv[j])) continue;
                let summe = 0;
                for (const j of liste) summe += s[j];
                const mittel = 0.5 * s[i] + 0.5 * summe / liste.length;
                neu[i] = unter[i] ? Math.max(mittel, s[i]) : mittel;
            }
            s.set(neu);
        }
    }

    /** Die Senkung eines Punkts neben dem Stück: gemittelt aus den nächsten Quellen, mal Hermite-Auslauf. */
    static _auslauf(koerper, normalen, i, quellen, s, Q, gitter) {
        const K = Hautanschmiegung.KRAGEN_M, h = K;
        const px = koerper[3 * i], py = koerper[3 * i + 1], pz = koerper[3 * i + 2];
        const nx = normalen[3 * i], ny = normalen[3 * i + 1], nz = normalen[3 * i + 2];
        const ci = Math.floor(px / h), cj = Math.floor(py / h), ck = Math.floor(pz / h);
        const treffer = [];
        let dmin = Infinity;
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            const liste = gitter.get(G.zelle(ci + a, cj + b, ck + c));
            if (!liste) continue;
            for (const k of liste) {
                const j = quellen[k];
                if (nx * normalen[3 * j] + ny * normalen[3 * j + 1] + nz * normalen[3 * j + 2]
                    < Hautanschmiegung.GLEICHRICHTUNG) continue;
                const d = Math.hypot(Q[3 * k] - px, Q[3 * k + 1] - py, Q[3 * k + 2] - pz);
                if (d >= K) continue;
                treffer.push(d, s[j]);
                if (d < dmin) dmin = d;
            }
        }
        if (dmin === Infinity) return 0;
        let summe = 0, gewicht = 0;
        for (let t = 0; t < treffer.length; t += 2) {
            if (treffer[t] > dmin + Hautanschmiegung.MISCHEN_M) continue;
            const g = 1 / (treffer[t] * treffer[t] + 4e-6);
            summe += g * treffer[t + 1]; gewicht += g;
        }
        const x = dmin / K;
        const auslauf = 1 - x * x * (3 - 2 * x);
        const wert = auslauf * summe / gewicht;
        return wert < 5e-5 ? 0 : wert;
    }

    /**
     * Die Senkung in das `einzug`-Feld schreiben (xyz je Punkt, nach innen). Punkte, die ein anderer Stoff verdeckt,
     * behalten ihren Einzug (Saumband) — nur Ersatzpunkte und die freie Haut neben dem Stück werden überschrieben.
     * @returns Anzahl der gesenkten Punkte
     */
    static eintragen(einzug, senkung, normalen, ersatz, maske) {
        let n = 0;
        for (let i = 0; i < senkung.length; i++) {
            if (maske[i] && !ersatz[i]) continue;
            if (!ersatz[i] && senkung[i] === 0) continue;
            einzug[3 * i] = -senkung[i] * normalen[3 * i];
            einzug[3 * i + 1] = -senkung[i] * normalen[3 * i + 1];
            einzug[3 * i + 2] = -senkung[i] * normalen[3 * i + 2];
            if (senkung[i] > 0) n++;
        }
        return n;
    }
}
