/**
 * Stueckluecke — Haut, die nur wegen des Ersatzstücks wegfiele, aber keine Stückfläche dahinter hat, bleibt stehen.
 *
 * BEFUND (Edgar: „Damm-Loch"; gemessen am Modell „Fallout ranger", 09.10.2026, Chrome, Haut mit und ohne Scham-Stück, Pixel in
 * Hintergrundfarbe): Mit dem Stück zeigten Ansichten von unten und hinten unten 61.000 und 50.000 Pixel Hintergrund MEHR als ohne.
 * `Hautmaskeersatz.beruehrt` nimmt jedes Dreieck weg, das einen Innenpunkt berührt, und `indexOhne` jedes, dessen DREI Ecken so
 * markiert sind — auch ein Dreieck, dessen Ecken je an einem anderen Nachbarn hängen. Von 284 entfernten Dreiecken deckte das Stück 200
 * ganz, 26 zur Hälfte und 58 gar nicht (Mitten bei x ±20…40 mm, y 847…876 mm, z −14…44 mm — die Leisten): dort blieb ein Loch bis
 * zum Hintergrund.
 *
 * Hier: Unter den Dreiecken, die erst durch die Nachbarschaft zum Stück wegfielen (nicht durch Stoff oder Saumband, nicht durch
 * `Stueckdeckung.dreiecke`), bleiben die stehen, die das Stück nicht zum größten Teil trägt (`Stueckdeckung.gedeckt`). Sie sind
 * ohnehin auf das Stück gesenkt (`hautanschmiegung.js`); ein sichtbarer Rest Haut ist besser als ein Loch.
 */
import { Stueckdeckung } from './stueckdeckung.js';
import { Stueckrand } from './stueckrand.js';

export class Stueckluecke {

    /** Ab so viel (m) Unterschied im Einzug zwischen den Ecken ist ein Hautdreieck der Ringe am Stück ein steiler Splitter. */
    static SPLITTER_M = 0.004;
    /** Anteil der sieben Stellen eines Splitters (Mitte, Ecken, Kantenmitten), die auf dem Stück liegen müssen, damit er wegfällt. */
    static SPLITTER_ANTEIL = 0.5;
    /** Splitter fallen nur weg, wenn das Stück dahinter mehr als so weit (m) vom Netzrand liegt (dort scheint die Haut noch durch). */
    static SPLITTER_RAND_M = Stueckrand.FEDER_M + 0.004;

    /**
     * Steile Hautdreiecke auf dem Stück: alle Ecken verdeckt, der Einzug der Ecken um mindestens `SPLITTER_M` verschieden — die Senkung
     * springt dort von Punkt zu Punkt (4 mm bis 19 mm bei Nachbarn, gemessen „cute girl", 09.10.2026), das Dreieck dazwischen steht
     * schräg VOR der Fläche des Stücks als brauner Splitter in den Leisten (Edgar: „keine helle, gesägte Zipfel"). Fällt weg, wenn das
     * Stück darunter es ganz trägt (Mitte und zwei Ecken, `Stueckdeckung.gedeckt`) — dann zeigt es dort das Stück.
     * Gibt `vorStueck` samt dieser Dreiecke zurück (ein neues Feld; `vorStueck` selbst bleibt), ohne Splitter dasselbe `vorStueck`.
     */
    static splitter(index, maske, einzug, vorStueck, koerper, normalen, stoffe) {
        const n = index.length / 3, pruefen = new Uint8Array(n);
        let geprueft = 0;
        const laenge = (i) => Math.hypot(einzug[3 * i], einzug[3 * i + 1], einzug[3 * i + 2]);
        for (let k = 0; k < n; k++) {
            const a = index[3 * k], b = index[3 * k + 1], c = index[3 * k + 2];
            if (!(maske[a] || maske[b] || maske[c])) continue;
            if (vorStueck && vorStueck[k]) continue;
            const la = laenge(a), lb = laenge(b), lc = laenge(c);
            if (Math.max(la, lb, lc) - Math.min(la, lb, lc) < Stueckluecke.SPLITTER_M) continue;
            pruefen[k] = 1;
            geprueft++;
        }
        if (!geprueft) return { weg: vorStueck, splitter: 0 };
        const gedeckt = new Uint8Array(n);
        for (const stoff of stoffe) {
            if (stoff.ersatz) {
                Stueckdeckung.gedeckt(koerper, einzug, normalen, index, stoff, pruefen, gedeckt, Stueckluecke.SPLITTER_RAND_M,
                                      Stueckluecke.SPLITTER_ANTEIL);
            }
        }
        const weg = vorStueck ? Uint8Array.from(vorStueck) : new Uint8Array(n);
        let anzahl = 0;
        for (let k = 0; k < n; k++) if (gedeckt[k]) { weg[k] = 1; anzahl++; }
        return { weg, splitter: anzahl };
    }

    /**
     * `{bleibt, offen, geprueft}` — `bleibt` ein Feld je Dreieck des Index (1 = Dreieck nicht entfernen) — oder null ohne Kandidaten.
     * @param index     voller Index der Haut
     * @param weg       Ecken, deren Dreiecke wegfallen (nach `Hautmaskeersatz.beruehrt`)
     * @param vorher    dasselbe Feld VOR `beruehrt` (Stoff, Saumband)
     * @param vorStueck Feld je Dreieck von `Stueckdeckung.dreiecke` (oder null)
     * @param koerper   Punkte der Haut; `einzug` der Einzug je Punkt; `normalen` die Punktnormalen
     * @param stoffe    die Stücke der Figur (`Hautverdeckung.stoffe`) — nur die mit `ersatz` zählen
     */
    static bleibt(index, weg, vorher, vorStueck, koerper, einzug, normalen, stoffe) {
        const n = index.length / 3;
        const pruefen = new Uint8Array(n);
        let geprueft = 0;
        for (let k = 0; k < n; k++) {
            const a = index[3 * k], b = index[3 * k + 1], c = index[3 * k + 2];
            if (!(weg[a] && weg[b] && weg[c])) continue;
            if (vorher[a] && vorher[b] && vorher[c]) continue;
            if (vorStueck && vorStueck[k]) continue;
            pruefen[k] = 1;
            geprueft++;
        }
        if (!geprueft) return null;
        const gedeckt = new Uint8Array(n);
        for (const stoff of stoffe) {
            if (stoff.ersatz) Stueckdeckung.gedeckt(koerper, einzug, normalen, index, stoff, pruefen, gedeckt);
        }
        const bleibt = new Uint8Array(n);
        let offen = 0;
        for (let k = 0; k < n; k++) if (pruefen[k] && !gedeckt[k]) { bleibt[k] = 1; offen++; }
        return { bleibt, offen, geprueft };
    }
}
