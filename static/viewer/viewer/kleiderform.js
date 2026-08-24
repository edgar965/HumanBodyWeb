import { state, REGION_DEFS } from './state.js';

/**
 * Kleiderform — den gespeicherten Zustand auf das Netz rechnen.
 *
 * Herausgelöst aus `garment_liste.js` (229 Zeilen). Drei Eigenheiten:
 *
 * 1. **Es wird immer von den Ausgangspunkten gerechnet** (`garmentOrigPositions`),
 *    nie vom aktuellen Stand. Sonst summiert sich jede Reglerbewegung auf und
 *    das Kleidungsstück wächst bei jedem Zug weiter.
 * 2. **Der Maßstab greift um den Schwerpunkt**, nicht um den Nullpunkt. Um den
 *    Nullpunkt skaliert, wandert das Kleidungsstück beim Vergrößern zugleich vom
 *    Körper weg.
 * 3. **Die Bereichsregler verschieben nur in der Höhe**, gewichtet je Punkt
 *    (`garmentRegionWeights`). Ein Bereich ohne Auslenkung wird übersprungen —
 *    das spart bei 30.000 Punkten fünf Durchläufe je Reglerbewegung.
 */
export class Kleiderform {

    /** Unterhalb dieser Auslenkung lohnt der Durchlauf nicht. */
    static SCHWELLE = 1e-6;

    constructor(gid) {
        this.netz = state.garmentMeshes[gid];
        this.zustand = state.garmentState[gid];
        this.ausgang = state.garmentOrigPositions[gid];
        this.gewichte = state.garmentRegionWeights[gid];
    }

    static anwenden(gid) {
        return new Kleiderform(gid).rechnen();
    }

    rechnen() {
        if (!this.netz || !this.zustand || !this.ausgang) return false;
        this.werkstoff();
        const punkte = this.netz.geometry.attributes.position.array;
        this.verschieben(punkte);
        this.bereiche(punkte);
        this.netz.geometry.attributes.position.needsUpdate = true;
        this.netz.geometry.computeBoundingSphere();
        return true;
    }

    werkstoff() {
        this.netz.material.color.set(this.zustand.color);
        this.netz.material.roughness = this.zustand.roughness;
        this.netz.material.metalness = this.zustand.metalness;
    }

    /** Schwerpunkt der Ausgangspunkte — Bezug für den Maßstab. */
    schwerpunkt() {
        const summe = [0, 0, 0];
        for (let i = 0; i < this.ausgang.length; i += 3) {
            summe[0] += this.ausgang[i];
            summe[1] += this.ausgang[i + 1];
            summe[2] += this.ausgang[i + 2];
        }
        const anzahl = this.ausgang.length / 3;
        return summe.map(wert => wert / anzahl);
    }

    verschieben(punkte) {
        const [mx, my, mz] = this.schwerpunkt();
        const z = this.zustand;
        for (let i = 0; i < this.ausgang.length; i += 3) {
            punkte[i] = (this.ausgang[i] - mx) * z.scaleX + mx + z.posX;
            punkte[i + 1] = (this.ausgang[i + 1] - my) * z.scaleY + my + z.posY;
            punkte[i + 2] = (this.ausgang[i + 2] - mz) * z.scaleZ + mz + z.posZ;
        }
    }

    bereiche(punkte) {
        if (!this.gewichte) return;
        const anzahl = this.ausgang.length / 3;
        for (const bereich of REGION_DEFS) {
            const feld = 'region' + bereich.id[0].toUpperCase() + bereich.id.slice(1);
            const weite = this.zustand[feld] || 0;
            if (Math.abs(weite) < Kleiderform.SCHWELLE) continue;
            const gewicht = this.gewichte[bereich.id];
            for (let i = 0; i < anzahl; i++) {
                punkte[i * 3 + 1] += weite * gewicht[i];
            }
        }
    }
}
