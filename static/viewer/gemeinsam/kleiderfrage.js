/**
 * Kleiderfrage — die Anpassparameter eines Kleidungsstücks als Frage an
 * `/api/character/garment/fit/`.
 *
 * EIGENES MODUL (09.09.2026): Beim Laden einer Figur werden die Stücke seither
 * NEBENEINANDER angepasst (`Charakterzubehoer.kleidung`); dafür muss die Frage
 * gebaut werden können, ohne dass gleich das Netz entsteht. In der Schleife war
 * beides verwoben.
 *
 * DIE FARBE GEHT NUR MIT, WENN ES EINE GIBT — und das ist kein Detail:
 * `Anpassungsregler._farbe` nimmt die Kanäle nur an, wenn alle drei da sind,
 * und ohne sie gilt „die Materialfarbe" aus der `.mhmat` des Stücks. Wer hier
 * ersatzweise eine Vorgabefarbe mitschickt, färbt jedes Stück ohne eigene
 * Farbe einheitlich blaugrau ein.
 */
export class Kleiderfrage {

    /**
     * @param grund  die Figurparameter (`body_type`, Morphs) — wird kopiert
     * @param g      ein Eintrag aus `inst.garments`
     * @param Farbe  THREE.Color, um eine Textfarbe (`#rrggbb`) umzurechnen
     */
    static fuer(grund, g, Farbe) {
        const frage = new URLSearchParams(grund);
        frage.set('garment_id', g.id);
        frage.set('offset', (g.offset || 0).toFixed(4));
        frage.set('stiffness', (g.stiffness || 0.5).toFixed(2));
        frage.set('min_dist', g.minDist !== undefined ? g.minDist : 3);
        frage.set('crotch_floor', g.crotchFloor !== undefined ? g.crotchFloor : 0);
        frage.set('lift', g.lift !== undefined ? g.lift : 0);
        frage.set('crotch_depth', g.crotchDepth !== undefined ? g.crotchDepth : 0);
        const kanaele = Kleiderfrage.kanaele(g.color, Farbe);
        if (kanaele) {
            frage.set('color_r', kanaele[0].toFixed(3));
            frage.set('color_g', kanaele[1].toFixed(3));
            frage.set('color_b', kanaele[2].toFixed(3));
        }
        return frage;
    }

    /** Eine Farbe als [r, g, b] in 0..1 — aus Array oder Text; sonst `null`. */
    static kanaele(farbe, Farbe) {
        if (!farbe) return null;
        if (Array.isArray(farbe)) return farbe;
        const c = new Farbe(farbe);
        return [c.r, c.g, c.b];
    }
}
