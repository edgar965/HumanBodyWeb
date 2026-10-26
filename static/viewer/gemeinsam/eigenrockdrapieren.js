import { Stoffpendel } from './stoffpendel.js';

/**
 * Eigenrockdrapieren — der Knopf „Drapieren“ eines eigenen Rocks oder Kleids (Stufe K3, 25.10.2026 nachts; Konzept: „der Fall entsteht beim Drapieren auf Knopf
 * … mit Reglern für Faltenbildung, Steifigkeit, Gewicht und örtliche Weite“). Ohne Three.js, in Node prüfbar.
 *
 * Derselbe Löser wie der Stoffschwung der Daz-Stücke (`Stoffpendel`: Verlet-Teilchen, Kanten als Längenbedingungen, Anker, Biegung), hier einmal in der Ruhelage
 * und ohne Bewegung des Körpers: die oberen `HALTEZEILEN` Ringe halten den Bund (Freiheit 0), der Rest fällt `SCHRITTE` Schritte zu `DT` unter der Schwerkraft;
 * Körper ist die Hülle der Haut (`Eigenrockhuelle.hinaus` als `Stoffpendel.oberflaeche`, auf Sitz über ihr). Die Startform (A-Linie, eingelegte Falten) ist zugleich
 * das Formgedächtnis: `FEDER` und `BIEGUNG` wachsen mit der Steifigkeit — steifer Stoff behält die Startform, weicher fällt senkrecht und wirft die überzählige
 * Weite in Falten. Gewicht = Anteil der Schwerkraft. Gerechnet wird auf dem Hauptfaden in Stücken zu `JE_BILD` Schritten (zwischen ihnen zeichnet die Szene).
 * Das Ergebnis sind neue Ruhepunkte des Rocknetzes — die Haltung kommt danach wie immer über die Hautgewichte.
 */
export class Eigenrockdrapieren {

    static SCHRITTE = 180;
    static DT = 1 / 60;
    static JE_BILD = 30;
    static HALTEZEILEN = 2;

    /** Werte für `Stoffpendel.schritt`; `steif` und `gewicht` als Anteil (0 … 1, 0,2 … 2). Setzungen, nicht gemessen. */
    static werte(steif, gewicht) {
        const v = {};
        for (const k of ['DAEMPFUNG', 'FEDER', 'FEDER_HAFT', 'SCHWERKRAFT', 'SCHWERE', 'MITNAHME', 'DURCHGAENGE', 'BIEGUNG', 'ABSTAND', 'MAX_DT', 'G']) v[k] = Stoffpendel[k];
        return { ...v, DAEMPFUNG: 4, FEDER: 8 * steif, BIEGUNG: 0.02 + 0.5 * steif, SCHWERE: gewicht, MITNAHME: 0, DURCHGAENGE: 4, ABSTAND: 0.002 };
    }

    /**
     * @param bau      `Eigenrockgeometrie.bauen(…)` — `geo.position` wird überschrieben (Naht mit)
     * @param steif    0 … 1
     * @param gewicht  0,2 … 2
     * @param warten   () → Promise zwischen den Stücken (Vorgabe: nächstes Bild)
     * @returns `{ms, schritte, saum_mm: mittlere Senkung des Saums, weite_mm: mittlere Änderung des Saum-Halbmessers}`
     */
    static async rechnen(bau, steif, gewicht, warten = Eigenrockdrapieren.bild) {
        const t0 = performance.now(), { geo, huelle, zeilen: Z, spalten: S } = bau;
        const p = geo.attributes.position.array, n = (Z + 1) * S;
        const ruhe = new Float32Array(3 * n), frei = new Float32Array(n), dreiecke = [];
        for (let z = 0; z <= Z; z++) {
            for (let s = 0; s < S; s++) {
                const i = z * S + s, k = z * (S + 1) + s;
                ruhe.set(p.subarray(3 * k, 3 * k + 3), 3 * i);
                frei[i] = z < Eigenrockdrapieren.HALTEZEILEN ? 0 : 1;
                if (z < Z) {
                    const a = i, b = z * S + (s + 1) % S, c = a + S, d = b + S;
                    dreiecke.push(a, c, b, b, c, d);
                }
            }
        }
        const pendel = Stoffpendel.ausDreiecken(ruhe, dreiecke, frei);
        pendel.oberflaeche = huelle;
        const werte = Eigenrockdrapieren.werte(steif, gewicht);
        let rechnen = 0, t = performance.now();
        for (let k = 1; k <= Eigenrockdrapieren.SCHRITTE; k++) {
            pendel.schritt(ruhe, Eigenrockdrapieren.DT, [], werte, null, true);
            if (k % Eigenrockdrapieren.JE_BILD === 0) {
                rechnen += performance.now() - t;
                await warten();
                t = performance.now();
            }
        }
        rechnen += performance.now() - t;
        const x = pendel.x, [cx, cz] = huelle.mitte;
        let senkung = 0, weite = 0;
        for (let s = 0; s < S; s++) {
            const i = 3 * (Z * S + s);
            senkung += ruhe[i + 1] - x[i + 1];
            weite += Math.hypot(x[i] - cx, x[i + 2] - cz) - Math.hypot(ruhe[i] - cx, ruhe[i + 2] - cz);
        }
        for (let z = 0; z <= Z; z++) {
            for (let s = 0; s <= S; s++) p.set(x.subarray(3 * (z * S + s % S), 3 * (z * S + s % S) + 3), 3 * (z * (S + 1) + s));
        }
        geo.attributes.position.needsUpdate = true;
        return { ms: Math.round(performance.now() - t0), rechnen_ms: Math.round(rechnen), schritte: Eigenrockdrapieren.SCHRITTE,
                 saum_mm: Math.round(1000 * senkung / S), weite_mm: Math.round(1000 * weite / S) };
    }

    /** Zwischen den Stücken die Ereignisschleife freigeben — NICHT aufs nächste Bild warten: bei 2 Bildern je Sekunde (GPU belegt, 25.10.2026) kostete das
     *  Warten auf `requestAnimationFrame` den größten Teil der 5,2 s eines Laufs. */
    static bild() {
        return new Promise(fertig => setTimeout(fertig, 0));
    }
}
