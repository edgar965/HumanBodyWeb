/**
 * Koerperzuordnung — welcher Knochen einen Körperpunkt am stärksten hält,
 * und zu welcher Gliedmaßen-Gruppe dieser Knochen gehört.
 *
 * HERAUSGELÖST aus `stoffkapseln.js` (22.09.2026, Fund Edgar: „bei Animation
 * Spagat geht der Arm in den Körper" / „die Hose ist zerrissen in dem
 * Frame"): Die stärkste-Knochen-Zuordnung je Punkt stand dort schon, nur für
 * den Stoffschwung. `Oberflaechenbindung` braucht dieselbe Zuordnung jetzt
 * auch für ANLIEGENDE Kleidung — nicht um den Körper zu häuten, sondern um
 * zu wissen, zu welcher GRUPPE ein gebundener Punkt gehört: Die Kapseln
 * (Schicht 3) sollen ihn nur aus FREMDEN Gliedmaßen drücken, nie aus seiner
 * eigenen (das verzerrt die Passform, siehe `oberflaecheglsl.js`).
 *
 * WARUM GRUPPEN STATT EINZELNER KNOCHEN: Ein Jeans-Punkt am Oberschenkel ist
 * an `l_thigh` gebunden, eine Kapsel kann aber auf `l_thightwist1` sitzen —
 * derselbe Körperteil, anderer Knochen. Ohne Gruppierung würde die
 * Twist-Kapsel den Punkt trotzdem aus dem eigenen Bein drücken.
 */
export class Koerperzuordnung {

    /** Gruppen-IDs für den Shader (0 = keine, andere = Gliedmaße). */
    static GRUPPEN = { l_arm: 1, r_arm: 2, l_bein: 3, r_bein: 4 };

    /** Seite eines Knochennamens: 'l', 'r' oder '' (Daz `l_`/`r_`, Rigify `.L`/`.R`). */
    static seite(name) {
        if (/^l_/i.test(name) || /\.L$/i.test(name)) return 'l';
        if (/^r_/i.test(name) || /\.R$/i.test(name)) return 'r';
        return '';
    }

    /** Arm, Bein oder '' — dieselben Muster wie `Stoffkapseln.GLIEDER`, aber getrennt. */
    static ARM = /upperarm|upper_arm|forearm|hand|shldr|shoulder|f_|thumb|index|mid(?!dle)|ring|pinky|carpal/i;
    static BEIN = /thigh|shin|foot|toe/i;

    /** Gruppen-ID (0 = keine) eines Knochennamens — `GRUPPEN` oder 0. */
    static gruppenindex(name) {
        const seite = Koerperzuordnung.seite(name);
        if (!seite) return 0;
        if (Koerperzuordnung.ARM.test(name)) return Koerperzuordnung.GRUPPEN[seite + '_arm'];
        if (Koerperzuordnung.BEIN.test(name)) return Koerperzuordnung.GRUPPEN[seite + '_bein'];
        return 0;
    }

    /**
     * Der stärkste Knochen je Punkt eines SkinnedMesh — `Int32Array(n)`,
     * Knochenindex in `netz.skeleton.bones`. `null` ohne Skinning-Attribute.
     */
    static staerksterKnochen(netz) {
        const geo = netz?.geometry;
        const index = geo?.attributes?.skinIndex?.array;
        const gewicht = geo?.attributes?.skinWeight?.array;
        const n = geo?.attributes?.position?.count || 0;
        if (!index || !gewicht || !n) return null;
        const aus = new Int32Array(n);
        for (let i = 0; i < n; i++) {
            let beste = 0, w = -1;
            for (let k = 0; k < 4; k++) {
                if (gewicht[4 * i + k] > w) { w = gewicht[4 * i + k]; beste = index[4 * i + k]; }
            }
            aus[i] = beste;
        }
        return aus;
    }

    /**
     * Gruppen-ID je Punkt eines SkinnedMesh (0 = keine) — `staerksterKnochen`
     * plus `gruppenindex` des zugehörigen Knochennamens. Gecacht an der
     * Geometrie (`userData.gruppeJePunkt`): Körper und Skelett ändern sich
     * nur bei einem Neubau, nicht jedes Bild.
     */
    static gruppeJePunkt(netz) {
        const geo = netz?.geometry;
        if (!geo) return null;
        if (geo.userData.gruppeJePunkt) return geo.userData.gruppeJePunkt;
        const knochen = Koerperzuordnung.staerksterKnochen(netz);
        const bones = netz.skeleton?.bones;
        if (!knochen || !bones) return null;
        const gruppeJeKnochen = bones.map((b) => Koerperzuordnung.gruppenindex(b.name));
        const aus = new Float32Array(knochen.length);
        for (let i = 0; i < knochen.length; i++) aus[i] = gruppeJeKnochen[knochen[i]] || 0;
        geo.userData.gruppeJePunkt = aus;
        return aus;
    }
}
