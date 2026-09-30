import * as THREE from 'three';

/**
 * Haarengineposenkopie — die Haltung der Genesis-Figur der Bühne auf das Iterationsmodell übertragen, Bild für Bild.
 *
 * Die Spuren der Bewegung (`Clipanimation`) sind LOKALE Drehungen in den Knochenachsen von `Genesis9Modell`. Eine GLB mit anderen
 * Knochenachsen (Befund aus BlenderModel: der Blender-Export, Y entlang des Knochens) stand damit verdreht in der Luft — im Browser
 * gemessen am 29.09.2026. Übertragen wird deshalb in WELTKOORDINATEN über die Ruhelage beider Skelette (aus den Bind-Matrizen, beide
 * A-Haltung):
 *
 *     Drehung_welt(GLB) = Drehung_welt(Genesis) · Ruhe_welt(Genesis)⁻¹ · Ruhe_welt(GLB)
 *
 * und für die Hüfte zusätzlich die Verschiebung gegenüber der Ruhelage. Die Genesis-Figur bewegt der Mixer wie bisher
 * (`Haarengineanimation`), auch wenn sie ausgeblendet ist — `updateMatrixWorld` läuft unabhängig von `visible`. Ohne Bewegung
 * behält das Modell die Haltung der Runde (gemerkt beim Laden).
 */
export class Haarengineposenkopie {

    static HUEFTE = 'hip';

    /** @param ziel `{skeleton, boneByName}` der GLB, @param quelle dasselbe der Genesis-Figur */
    constructor(ziel, quelle) {
        this.paare = [];
        this.ursprung = ziel.skeleton.bones.map(b => [b, b.quaternion.clone(), b.position.clone()]);
        const ruheZiel = Haarengineposenkopie._ruhe(ziel.skeleton);
        const ruheQuelle = Haarengineposenkopie._ruhe(quelle.skeleton);
        ziel.skeleton.bones.forEach((knochen, i) => {
            const j = quelle.skeleton.bones.findIndex(b => b.name === knochen.name);
            if (j < 0) return;
            this.paare.push({
                ziel: knochen, quelle: quelle.skeleton.bones[j],
                // Ruhe_welt(Genesis)⁻¹ · Ruhe_welt(GLB) — je Knochen fest
                versatz: ruheQuelle[j].q.clone().invert().multiply(ruheZiel[i].q),
                ruheZielOrt: ruheZiel[i].p, ruheQuelleOrt: ruheQuelle[j].p,
            });
        });
        // Eltern vor Kindern: Beim Setzen braucht jeder Knochen die schon gesetzte Weltdrehung seines Elternknochens.
        const tiefe = b => { let n = 0; for (let p = b.parent; p?.isBone; p = p.parent) n++; return n; };
        this.paare.sort((a, b) => tiefe(a.ziel) - tiefe(b.ziel));
        this._aktiv = false;
    }

    /** Ruhelage je Knochen in Welt (bzw. Netz-)Koordinaten: {q, p} aus der Umkehrung der Bind-Matrix. */
    static _ruhe(skeleton) {
        return skeleton.boneInverses.map(inv => {
            const m = inv.clone().invert(), p = new THREE.Vector3(), q = new THREE.Quaternion();
            m.decompose(p, q, new THREE.Vector3());
            return { q, p };
        });
    }

    /** Jedes Bild: `aktiv` = eine Bewegung liegt auf der Genesis-Figur. */
    folgen(aktiv) {
        if (!aktiv) {
            if (this._aktiv) this._zuruecksetzen();
            return;
        }
        this._aktiv = true;
        const welt = new THREE.Quaternion(), eltern = new THREE.Quaternion();
        for (const paar of this.paare) {
            paar.quelle.getWorldQuaternion(welt);
            welt.multiply(paar.versatz);
            paar.ziel.parent.getWorldQuaternion(eltern);
            paar.ziel.quaternion.copy(eltern.invert().multiply(welt));
            if (paar.ziel.name === Haarengineposenkopie.HUEFTE) this._ort(paar);
            paar.ziel.updateMatrixWorld(true);
        }
    }

    /** Hüfte: dieselbe Verschiebung gegenüber der Ruhelage wie bei der Genesis-Figur. */
    _ort(paar) {
        const jetzt = new THREE.Vector3();
        paar.quelle.getWorldPosition(jetzt);
        const ziel = paar.ruheZielOrt.clone().add(jetzt.sub(paar.ruheQuelleOrt));
        paar.ziel.parent.updateWorldMatrix(true, false);
        paar.ziel.position.copy(paar.ziel.parent.worldToLocal(ziel));
    }

    _zuruecksetzen() {
        for (const [b, q, p] of this.ursprung) { b.quaternion.copy(q); b.position.copy(p); }
        this._aktiv = false;
    }
}
