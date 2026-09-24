import * as THREE from 'three';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';
import { Spurfigurarten } from './spurfigurarten.js';

/**
 * Spurfigur — die Figur einer Spur im BVH-Studio: ein Modell nach der
 * Quelle der Spur (`Spurfigurarten`: HumanBody, UMA, MakeHuman, SMPL, UMA
 * Python), in die Gruppe der Spur gesetzt.
 *
 * SEIT 13.09.2026 BAUT DAS STUDIO NICHTS MEHR SELBST (Edgar: „Alle HTML-
 * Seiten … sollen die Figur NICHT selber bauen, sondern eine globale Klasse
 * nutzen"). Vorher standen hier Netz, Materialien, Skinning und in
 * `Spurzubehoer` Kleidung, Haare und GarmentCode — und die Figur kam ohne
 * Lippen, Brauen und Nagelfarben (`details`) auf die Bühne. Jetzt gibt die
 * Spur dem Modell, was das Studio hat (Skelett, Gewichte, Farbtabellen aus
 * `sharedState`), und übernimmt Netz, Skelett und Mischer aus dem Modell.
 * Seit 15.09.2026 gilt das für alle fünf Figurarten.
 *
 * Die Knochennamen werden wie bisher entschärft (`namenSaeubern`, Punkte →
 * Unterstriche), weil die Clips des Studios sie so führen.
 */
export class Spurfigur {

    static VORGABE_KOERPERART = HumanbodyModell.VORGABE_KOERPERART;

    /**
     * @param spur          die Spur
     * @param namenSaeubern (skelett) => void
     */
    constructor(spur, { namenSaeubern }) {
        this.spur = spur;
        this.namenSaeubern = namenSaeubern;
    }

    async laden() {
        try {
            await Spurfigurarten.bauen(this.spur, (m) => this._einsetzen(m));
            Protokoll.debug('BVH Studio', `Figur geladen: ${this.spur.quelle || 'modell'}/`
                        + `${this.spur.preset} für ${this.spur.name}`);
            return this.spur.mesh;
        } catch (fehler) {
            console.error('[BVH Studio] Figur nicht ladbar:', fehler);
            return null;
        }
    }

    // --------------------------------------------------------------- Einsetzen

    /**
     * Netz, Skelett und Mischer aus dem Modell in die Spur — sobald der
     * Körper steht; Zubehör und Brauen hängen im selben `modell.group`, der
     * zur Gruppe der Spur wird.
     */
    _einsetzen(modell) {
        // Alte Netze nur aus der Gruppe nehmen, NICHT entsorgen — sie können
        // in einem Zwischenspeicher noch gebraucht werden.
        while (this.spur.group.children.length > 0) {
            this.spur.group.remove(this.spur.group.children[0]);
        }
        for (const kind of [...modell.group.children]) this.spur.group.add(kind);
        // Zubehör, das das Modell NACH dem Körper anhängt, soll in der Spur landen.
        modell.group = this.spur.group;
        this.spur.modell = modell;
        this.spur.mesh = modell.bodyMesh;
        if (modell.skelett) {
            this.spur.skeleton = modell.skelett;
            this.namenSaeubern(this.spur.skeleton);
            this.spur.group.updateMatrixWorld(true);
            this.spur.figurHoehe = Spurfigurarten.hoehe(this.spur.skeleton);
        }
        // Das Netz selbst bleibt sichtbar; über die Sichtbarkeit der Gruppe
        // entscheiden `applyModelTrack`/`applyBvhTrack` — sie deckt Netz,
        // Kleidung und Haare zusammen ab.
        if (this.spur.mesh) this.spur.mesh.visible = true;
        this.spur.mixer = new THREE.AnimationMixer(Spurfigurarten.mischerWurzel(this.spur));
        this.spur._activeClip = null;
        this.spur._activeAction = null;
    }
}
