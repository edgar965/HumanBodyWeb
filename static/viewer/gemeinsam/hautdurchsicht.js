import { Hautmaske } from './hautmaske.js';
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';

/**
 * Hautdurchsicht — die Haut unter einem DURCHSICHTIGEN Stück (18.11.2026).
 *
 * Edgar mit Bild, 18.11.2026: „brüste werden deformiert bei kleidern, z.B: "GC FemSuit double breasted", auch die Haut, liegt das an Feauture
 * "Haut gibt nach"?“ — Ja. Gemessen im Chrome (seratin, daz_anatomie_frau, gc_fem_suit_double_breasted, Stoff auf 0,35 Deckung): unter dem Anzug
 * galten 22.177 von 104.480 Hautpunkten als verdeckt, und zwar fleckig, weil der Strahl nur bis 25 mm über der Haut Stoff sucht (`Hautmaske.ABSTAND_M`)
 * und der Anzug unter der Brust weiter absteht; im Brustband 526 von 1.690 Punkten. `Hauteinzug` zieht jede verdeckte Insel nach ihrem Abstand von
 * der freien Haut bis zur Tiefe der Bauart ein (anliegend 30 mm, „Haut gibt nach“, `Bauart`, seit 12.11.2026; davor 10 mm). Unter deckendem Stoff
 * sieht man das nicht, unter durchsichtigem sieht man die Dellen (`Stoffwerte.transparenz`, seit 18.11.2026).
 *
 * Unter einem durchsichtigen Stück gilt darum: Die Haut zählt nicht als verdeckt (kein Ausblenden, kein Saumband) und gibt nur dort nach, wo sie
 * durch den Stoff stößt — so tief, dass sie `LUFT_M` hinter dem Stoff liegt, höchstens bis zur Tiefe der Bauart (`stoff.nachgeben`). Gesucht wird
 * entlang der Körpernormale von `tiefe` in der Haut bis `LUFT_M` darüber, über ALLE Dreiecke um den nächsten Stoffpunkt (eine lockere Kante, die
 * die Haut durchstößt, zählt hier mit — man sieht sie ja). Durchsichtig ist ein Stück nach `Bauart.durchsichtig` (`stoff.durchsicht`).
 */
export class Hautdurchsicht {

    /** So weit (m) liegt durchstoßende Haut nach dem Einzug hinter dem Stoff. */
    static LUFT_M = 0.001;

    /**
     * Je Körperpunkt die nötige Tiefe (m) unter allen `stoffe` — null ohne solche Stücke. Höchstens bis `nachgeben` des Stücks, hinter die tiefste
     * Lage. `deckend` (`anheben`): bis zu seiner `tiefe` — so tief zählt die Haut unter ihm als verdeckt (`Bauart.deckTiefeM`) —, hinter die NÄCHSTE
     * Lage: Durch die Wange im Cyborg-Helm traf der Strahl in 10 cm auch den Visierrahmen (an Luna bis 97 mm statt weniger Millimeter).
     */
    static alle(koerper, normalen, stoffe, deckend = false) {
        const liste = (stoffe || []).filter((s) => s?.punkte?.length && s?.dreiecke?.length);
        if (!liste.length) return null;
        const durch = new Float32Array(koerper.length / 3);
        for (const s of liste) {
            const tiefe = Math.max(Hautmaske.TIEFE_M, s.tiefe || 0);
            Hautdurchsicht.stueck({ koerper, normalen }, durch, s, tiefe, deckend ? tiefe : Math.max(0, s.nachgeben || 0), deckend);
        }
        return durch;
    }

    /**
     * Je Körperpunkt die Tiefe (m), um die er unter diesem Stück nachgeben muss, in `durch` (das tiefste Stück gewinnt).
     * @param basis  `{koerper, normalen}` wie in `Hautmaske.verdeckt`
     * @param tiefe   so weit darf der Stoff schon in der Haut stecken (`Hautmaske.TIEFE_M` oder `stoff.tiefe`)
     * @param grenze  höchstens so tief gibt die Haut nach (m)
     * @param naechste  hinter die nächste getroffene Lage statt hinter die tiefste
     */
    static stueck(basis, durch, stoff, tiefe, grenze, naechste = false) {
        const { koerper, normalen } = basis;
        const P = stoff.punkte, T = stoff.dreiecke, nP = P.length / 3;
        if (!(grenze > 0)) return;
        const { nachbarn } = Hautmaske.randpunkte(T, nP);
        const umkreis = Hautmaske.dreieckeImUmkreis(T, nP, new Uint8Array(T.length / 3).fill(1), nachbarn);
        const h = G.ZELLE_M, gitter = G.punktgitter(P, h);
        const weite = Math.max(tiefe, Hautmaske.ABSTAND_M);
        const huelle = G.huelle(P, weite), grenze2 = weite * weite, luft = Hautdurchsicht.LUFT_M;
        for (let i = 0; i < durch.length; i++) {
            const px = koerper[3 * i], py = koerper[3 * i + 1], pz = koerper[3 * i + 2];
            if (px < huelle[0] || px > huelle[3] || py < huelle[1] || py > huelle[4] || pz < huelle[2] || pz > huelle[5]) continue;
            const nah = G.naechsterPunkt(P, gitter, h, px, py, pz);
            if (!nah || nah.d2 > grenze2) continue;
            const nx = normalen[3 * i], ny = normalen[3 * i + 1], nz = normalen[3 * i + 2];
            const liste = umkreis(nah.j);
            let noetig = 0, vorne = false;
            for (let l = 0; l < liste.length; l++) {
                const k = liste[l];
                const t = G.strahlDreieck(P, T[k], T[k + 1], T[k + 2], px, py, pz, nx, ny, nz);
                // t < luft: der Stoff liegt hinter oder knapp vor der Haut — sie muss bis `luft` hinter ihn.
                if (t !== null && t >= -tiefe && t < luft) noetig = naechste && noetig ? Math.min(noetig, luft - t) : Math.max(noetig, luft - t);
                // `naechste` (deckend): liegt bis `tiefe` auch Stoff VOR der Haut, deckt er sie von außen — kein Durchstich (die Wange im Cyborg-Helm traf
                // nach innen den Visierrahmen und zog sichtbar ein, 18.11.2026)
                else if (naechste && t !== null && t >= luft && t <= tiefe) vorne = true;
            }
            if (vorne) noetig = 0;
            if (noetig > 0) durch[i] = Math.max(durch[i], Math.min(noetig, grenze));
        }
    }

    /** Nach dem Einzug (`Hauteinzugrechnung`): Punkte, die kein deckendes Stück verdeckt, wandern um ihre Tiefe nach innen. Zählt die gesetzten. */
    static eintragen(werte, maske, durch, normalen) {
        let gesetzt = 0;
        for (let i = 0; i < durch.length; i++) {
            if (maske[i] || !(durch[i] > 0)) continue;
            werte[3 * i] = -durch[i] * normalen[3 * i];
            werte[3 * i + 1] = -durch[i] * normalen[3 * i + 1];
            werte[3 * i + 2] = -durch[i] * normalen[3 * i + 2];
            gesetzt += 1;
        }
        return gesetzt;
    }

    /**
     * Unter DECKENDEN Stücken (18.11.2026, Edgar: „cyborg suit besser, aber immer noch haut sichtbar“): Verdeckte Haut vor dem Stoff darf so tief
     * nachgeben, dass sie `LUFT_M` hinter ihm liegt — `nachgeben` (die Obergrenze des Einzugs, `Hauteinzugrechnung`) wird dafür angehoben. Der Einzug
     * selbst bleibt der nach dem Abstand von der gezeichneten Haut (`Saumband.tiefe`), sonst stünde neben freier Haut eine Klippe (am Cyborg-Visier
     * gesehen). Gemessen an Luna im MH Joachip Cyborg Suit (Chrome): Am Rumpf standen 2.223 Hautpunkte bis 29,6 mm vor den flachen Platten, 2.082
     * verdeckt; die Nachgebe-Tiefe von 30 mm reichte nicht. Zählt die angehobenen Punkte.
     */
    static anheben(nachgeben, maske, durch) {
        let zahl = 0;
        for (let i = 0; i < durch.length; i++) {
            if (!maske[i] || !(durch[i] > nachgeben[i])) continue;
            nachgeben[i] = durch[i];
            zahl += 1;
        }
        return zahl;
    }

    /** So oft wird `nachgeben` an Inselpunkte weitergereicht (je Runde ein Dreiecksring). */
    static RUNDEN = 40;

    /**
     * Punkte, die erst `Maskeninseln` verdeckt, gehören zu keinem Stück: `nachgeben` 0, also nur `Saumband.TIEFE_M` (10 mm) Einzug — am Rücken von Luna
     * im Cyborg Suit standen 87 solche Punkte bis 23,7 mm vor der Platte (Chrome, 18.11.2026). Sie erben den größten Wert ihrer Nachbarn über die Dreiecke,
     * Runde für Runde (jede Runde rechnet aus dem Stand davor), bis nichts mehr dazukommt. Zählt die Inselpunkte.
     */
    static inselnErben(nachgeben, maske, index) {
        const n = maske.length, offen = new Uint8Array(n);
        let zahl = 0;
        for (let i = 0; i < n; i++) if (maske[i] && !(nachgeben[i] > 0)) { offen[i] = 1; zahl += 1; }
        if (!zahl) return 0;
        const neu = new Float32Array(n);
        for (let r = 0; r < Hautdurchsicht.RUNDEN; r++) {
            neu.fill(0);
            for (let t = 0; t < index.length; t += 3) {
                const a = index[t], b = index[t + 1], c = index[t + 2], w = Math.max(nachgeben[a], nachgeben[b], nachgeben[c]);
                if (w > neu[a]) neu[a] = w;
                if (w > neu[b]) neu[b] = w;
                if (w > neu[c]) neu[c] = w;
            }
            let geaendert = 0;
            for (let i = 0; i < n; i++) if (offen[i] && neu[i] > nachgeben[i]) { nachgeben[i] = neu[i]; geaendert += 1; }
            if (!geaendert) break;
        }
        return zahl;
    }
}
