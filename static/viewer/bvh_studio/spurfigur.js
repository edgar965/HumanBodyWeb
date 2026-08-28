import * as THREE from 'three';
import { sharedState, applySkinColorToMaterials }
    from '../character_core.js';
import { generateRigBoneMesh } from '../modellbau/rignetz.js';
import { Spurzubehoer } from './spurzubehoer.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Spurfigur — die Figur einer Spur im BVH-Studio aufbauen: Netz der
 * Modellvorgabe, Skelett, Materialien, dann Kleidung und Haare.
 *
 * Aus bvh_studio/spur_charakter.js herausgeloest (Umbau 16.08.2026):
 * `loadTrackCharacter()` hatte 113 Zeilen mit zwei Wegen (erzeugtes Knochennetz
 * oder Netz vom Server) und dem Einsetzen in die Spur dazwischen.
 */
export class Spurfigur {

    static VORGABE_KOERPERART = 'Female_Caucasian';

    /**
     * @param spur         die Spur
     * @param skelettBauen (skelettDaten, gewichte) => Skelett
     * @param gewichteBauen (geo, gewichte) => { skinIndices, skinWeights }
     * @param namenSaeubern (skelett) => void
     */
    constructor(spur, { skelettBauen, gewichteBauen, namenSaeubern }) {
        this.spur = spur;
        this.skelettBauen = skelettBauen;
        this.gewichteBauen = gewichteBauen;
        this.namenSaeubern = namenSaeubern;
    }

    async laden() {
        try {
            const vorgabe = await this._vorgabe();
            // Export1 liest `bone_parts` später von hier.
            this.spur.modelData = vorgabe;
            const netz = await this._netz(vorgabe);
            if (!netz) return null;
            this._einsetzen(netz);
            if (vorgabe.garments || vorgabe.hair_style) {
                await new Spurzubehoer(this.spur, vorgabe).laden();
            }
            Protokoll.debug('BVH Studio', `Figur geladen: ${this.spur.preset} `
                        + `für ${this.spur.name}`);
            return netz;
        } catch (fehler) {
            console.error('[BVH Studio] Figur nicht ladbar:', fehler);
            return null;
        }
    }

    async _vorgabe() {
        return Serverabruf.json('/api/character/model/'
            + encodeURIComponent(this.spur.preset) + '/');
    }

    async _netz(vorgabe) {
        if (vorgabe.type === 'generated_model') {
            const erzeugt = await this._knochennetz(vorgabe);
            if (erzeugt) return erzeugt;
        }
        return this._servernetz(vorgabe);
    }

    // --------------------------------------------------------- Erzeugtes Netz

    /** Rig1–4: Das Netz wird aus den Knochen gebaut, nicht vom Server geholt. */
    async _knochennetz(vorgabe) {
        let knochen = null;
        try {
            const antwort = await fetch('/api/character/rig/');
            if (antwort.ok) knochen = await antwort.json();
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'Rig nicht ladbar:', fehler);
        }
        if (!knochen || !sharedState.rigifySkeletonData
            || !sharedState.skinWeightData) return null;
        const ergebnis = generateRigBoneMesh(knochen, vorgabe,
                                            sharedState.rigifySkeletonData,
                                            sharedState.skinWeightData);
        if (!ergebnis?.mesh) return null;
        if (ergebnis.skeleton) {
            this.spur.skeleton = ergebnis.skeleton;
            this.namenSaeubern(this.spur.skeleton);
        }
        return ergebnis.mesh;
    }

    // ----------------------------------------------------------- Netz vom Server

    /**
     * Netz zur Modellvorgabe holen. Die Morph- und Metawerte der Vorgabe MÜSSEN
     * mit in die Frage — sonst kommt immer der Grundkörper zurück (so sah
     * "FrauHaarDünn" aus wie das Vorgabemodell).
     */
    async _servernetz(vorgabe) {
        // Eine Vorgabe darf eine andere Körperart nennen als die Spur.
        this.spur.bodyType = vorgabe.body_type || this.spur.bodyType
                             || Spurfigur.VORGABE_KOERPERART;
        const frage = new URLSearchParams({ body_type: this.spur.bodyType });
        for (const [name, wert] of Object.entries(vorgabe.morphs || {})) {
            if (wert !== 0) frage.set(`morph_${name}`, wert);
        }
        for (const [name, wert] of Object.entries(vorgabe.meta || {})) {
            if (wert !== 0) frage.set(`meta_${name}`, wert);
        }
        const daten = await Serverabruf.json(`/api/character/mesh/?${frage}`);
        if (daten.error) {
            Protokoll.warnung('BVH Studio', 'Netz nicht ladbar:', daten.error);
            return null;
        }
        const geo = Spurzubehoer.geometrie(daten);
        const material = this._materialien(daten, geo);
        return this._geskinnt(geo, material);
    }

    /**
     * Materialien dieser Spur — mit ihrer Hautfarbe.
     *
     * Die Rechnung steht in `Koerpernetz.materialsatz` (28.08.2026, Befund
     * `doppelcode`). Hier stand sie ein zweites Mal, in
     * `photo_to_3d/fotokoerpernetz.js` ein drittes — und die Fassung hier
     * hat die Verzweigung „Liste oder Hautmaterial allein" nur an der
     * Gruppenzahl festgemacht, nicht am Index.
     */
    _materialien(daten, geo) {
        return Koerpernetz.materialsatz(
            geo, daten, THREE,
            (materialien) => applySkinColorToMaterials(
                materialien, this.spur.bodyType, sharedState.skinColors));
    }

    _geskinnt(geo, material) {
        const { skinIndices, skinWeights } =
            this.gewichteBauen(geo, sharedState.skinWeightData);
        geo.setAttribute('skinIndex',
                         new THREE.Float32BufferAttribute(skinIndices, 4));
        geo.setAttribute('skinWeight',
                         new THREE.Float32BufferAttribute(skinWeights, 4));
        this.spur.skeleton = this.skelettBauen(sharedState.rigifySkeletonData,
                                               sharedState.skinWeightData);
        this.namenSaeubern(this.spur.skeleton);
        const netz = new THREE.SkinnedMesh(geo, material);
        netz.add(this.spur.skeleton.rootBone);
        netz.bind(this.spur.skeleton.skeleton);
        return netz;
    }

    // --------------------------------------------------------------- Einsetzen

    _einsetzen(netz) {
        // Alte Netze nur aus der Gruppe nehmen, NICHT entsorgen — sie können
        // in einem Zwischenspeicher noch gebraucht werden.
        while (this.spur.group.children.length > 0) {
            this.spur.group.remove(this.spur.group.children[0]);
        }
        this.spur.mesh = netz;
        // Das Netz selbst bleibt sichtbar; über die Sichtbarkeit der Gruppe
        // entscheiden `applyModelTrack`/`applyBvhTrack` — sie deckt Netz,
        // Kleidung und Haare zusammen ab.
        netz.visible = true;
        this.spur.group.add(netz);
        this.spur.mixer = new THREE.AnimationMixer(netz);
        this.spur._activeClip = null;
        this.spur._activeAction = null;
    }
}
