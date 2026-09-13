import { Augenbrauen } from './augenbrauen.js';

/**
 * Augenbrauenform — Dichte, Dicke, Länge und Lage der Brauenhärchen.
 *
 * WARUM (Edgar, 13.09.2026: „augenbrauen regler auch sehr schlecht, die Höhe
 * sollte weiter nach unten verstellbar sein, es fehlen Regler für dicke,
 * dichte der Augenbrauen, im Moment sind es wie ein paar vereinzelte
 * Steckrüben"): `Augenbrauen` setzt 30 Streifen je Braue auf einen Bogen
 * 22 mm über der Augenmitte — auf dieser Figur eine gezackte Linie weit
 * über dem Brauenwulst (gemessen: Braue bei 1,60 m, Augenmitte 1,566 m).
 * Der Morph `Eyebrows_PosZ` hebt nur die Haut um 6,6 mm, tiefer ging es
 * nicht.
 *
 * Hier kommen vier Regler dazu (`Koerperdetails`: `brauen_staerke` = Länge,
 * `brauen_dicke`, `brauen_dichte`, `brauen_lage`):
 *   - DICHTE: `HAARE · dichte` Härchen je Braue, entlang des gemerkten Ankers
 *     (`Augenbrauen.anker`, 30 Stützpunkte) INTERPOLIERT — der Anker bleibt,
 *     wie er ist, damit die Braue weiter der Haut folgt (Morphs).
 *   - LAGE: der Bogen wandert um `lage` Meter nach oben (+) oder unten (−);
 *     die Wurzel wird dort NEU gesucht (vorderster Hautpunkt), sonst schwebte
 *     die Braue 15 mm unter ihrer Wurzel vor der Augenhöhle.
 *   - DICKE: Breite der Streifen; STÄRKE: ihre Länge (wie bisher).
 *   - Ein kleines, DETERMINISTISCHES Zittern je Härchen (Lage quer, Länge,
 *     Neigung) — sonst stehen sie wie Zaunlatten in einer Reihe.
 *   - Die Spitze folgt der HAUT nach hinten: Zur Schläfe hin weicht das
 *     Gesicht um 0,85 mm je mm zurück (Anker gemessen: z 133 → 116 mm auf
 *     20 mm); ein flacher Streifen auf der Wurzelhöhe stand dort 5 mm vor
 *     der Haut und wirkte als zweiter Strang. Die Steigung kommt aus den
 *     Nachbarstützen.
 *
 * Ohne Three.js und ohne DOM — prüfbar in Node (`test_js_augenbrauenform.py`).
 * Die Netzseite (`augenbrauenbau.js`) ruft `bauen` statt `Augenbrauen.bauen`.
 */
export class Augenbrauenform {

    /** Härchen je Braue bei Dichte 1 — doppelt so viele wie der alte Bogen hatte. */
    static HAARE = 60;
    /** Zittern: quer zur Braue (m), Länge (Anteil), Neigung (Anteil der Neigung). */
    static ZITTERN = { quer: 0.0004, laenge: 0.10, neigung: 0.08 };
    /** Umkreis für die neue Wurzelsuche bei verschobener Lage (m) — eng, sonst
     *  springt die Wurzel auf einen weit entfernten Vorderpunkt und die Braue
     *  bekommt eine Stufe; findet er nichts, dann der weite des Bogens. */
    static SUCHWEITE = 0.003;

    /** Die Regler aus den Details, mit Vorgaben. */
    static form(details) {
        return { staerke: details?.brauen_staerke ?? 1, dicke: details?.brauen_dicke ?? 1,
                 dichte: details?.brauen_dichte ?? 1, lage: details?.brauen_lage ?? 0 };
    }

    /**
     * Wie `Augenbrauen.bauen`, mit Form: gleiche Rückgabe, gleicher Anker.
     * @param details  `Koerperdetails` der Figur (oder null = Vorgaben)
     */
    static bauen(punkte, index, gruppen, details, anker = null) {
        const a = anker || Augenbrauen.anker(punkte, index, gruppen);
        const form = Augenbrauenform.form(details);
        const haut = Augenbrauen.ecken(index, gruppen, Augenbrauen.GRUPPE.haut);
        const streifen = [];
        for (const seite of [-1, 1]) {
            const stuetzen = a.filter(s => s.seite === seite);
            for (const stelle of Augenbrauenform.stellen(stuetzen, punkte, form, haut)) {
                streifen.push(Augenbrauenform.streifen(stelle, seite, form, streifen.length));
            }
        }
        return { ...Augenbrauen.geometrie(streifen), anker: a };
    }

    /**
     * Die Stellen der Härchen einer Seite: entlang der Stützpunkte des Ankers
     * interpoliert, um `lage` versetzt, jede mit ihrer Wurzel auf der Haut.
     * @returns {Array<{p: number[], wurzel: number, t: number}>}
     */
    static stellen(stuetzen, punkte, form, haut) {
        if (stuetzen.length < 2) return [];
        const lage = (s) => [punkte[3 * s.wurzel] + s.dx, punkte[3 * s.wurzel + 1] + s.dy];
        const n = Math.max(2, Math.round(Augenbrauenform.HAARE * form.dichte));
        const aus = [];
        for (let k = 0; k < n; k++) {
            const t = k / (n - 1);
            const lauf = t * (stuetzen.length - 1);
            const i = Math.min(stuetzen.length - 2, Math.floor(lauf));
            const f = lauf - i;
            const [x0, y0] = lage(stuetzen[i]), [x1, y1] = lage(stuetzen[i + 1]);
            const x = x0 + f * (x1 - x0), y = y0 + f * (y1 - y0) + form.lage;
            const wurzel = form.lage === 0 ? stuetzen[f < 0.5 ? i : i + 1].wurzel
                : Augenbrauenform.wurzel(punkte, haut, x, y);
            if (wurzel < 0) continue;
            // Steigung über ein Fenster von Stützen — Nachbarn teilen sich oft
            // dieselbe Wurzel (gleiches z), von Stütze zu Stütze spränge sie.
            const a0 = stuetzen[Math.max(0, i - 3)], a1 = stuetzen[Math.min(stuetzen.length - 1, i + 4)];
            const dx = punkte[3 * a1.wurzel] - punkte[3 * a0.wurzel];
            const dz = Math.abs(dx) > 1e-6 ? (punkte[3 * a1.wurzel + 2] - punkte[3 * a0.wurzel + 2]) / dx : 0;
            aus.push({ p: [x, y, punkte[3 * wurzel + 2]], wurzel, t, dz });
        }
        return aus;
    }

    /** Der Hautpunkt unter (x, y): erst eng gesucht, dann so weit wie der Bogen. */
    static wurzel(punkte, haut, x, y) {
        const eng = Augenbrauen.vorderster(punkte, haut, x, y, Augenbrauenform.SUCHWEITE);
        return eng >= 0 ? eng : Augenbrauen.vorderster(punkte, haut, x, y, Augenbrauen.BOGEN.suchweite);
    }

    /** Ein Härchen mit Dicke, Stärke und seinem Zittern. */
    static streifen(stelle, seite, form, nummer) {
        const z = Augenbrauenform.zittern(nummer);
        const haar = { ...Augenbrauen.HAAR,
                       breite: Augenbrauen.HAAR.breite * form.dicke,
                       neigung: Augenbrauen.HAAR.neigung * (1 + z[2] * Augenbrauenform.ZITTERN.neigung) };
        const p = [stelle.p[0], stelle.p[1] + z[0] * Augenbrauenform.ZITTERN.quer, stelle.p[2]];
        const staerke = form.staerke * (1 + z[1] * Augenbrauenform.ZITTERN.laenge);
        const aus = Augenbrauen.streifen({ p, wurzel: stelle.wurzel, t: stelle.t }, seite, staerke, haar);
        // Die Spitze (Ecken 2 und 3) der Haut nach: so weit, wie sie in x wandert.
        for (const e of [2, 3]) aus.ecken[e][2] += (stelle.dz || 0) * (aus.ecken[e][0] - p[0]);
        return aus;
    }

    /** Drei Werte in −1..1 je Härchen — immer dieselben für dieselbe Nummer. */
    static zittern(nummer) {
        const aus = [];
        let x = (nummer + 1) * 2654435761 % 4294967296;
        for (let k = 0; k < 3; k++) {
            x = (x * 1664525 + 1013904223) % 4294967296;
            aus.push((x / 4294967296) * 2 - 1);
        }
        return aus;
    }
}
