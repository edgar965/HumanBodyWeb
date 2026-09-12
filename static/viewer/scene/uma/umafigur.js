import * as THREE from 'three';
import { gltfLoader } from '../state.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Umaregler } from './umaregler.js';
import { Figurbasis } from '../figurbasis.js';

/**
 * UmaFigur — eine UMA-Figur aus dem Figurkatalog als Figur der Szene.
 *
 * WARUM (05.09.2026): Die Szene soll ein Modell beider Quellen laden — HumanBody
 * (`CharacterInstance`) oder UMA. Die UMA-Figur ist die GLB, die Unity für
 * Roomguest ablegt (`Figuren/uma/`), mit Haut, Haar, Augen und dem Skelett.
 * Kleidung bringt UMA in Unity mit; hier wird nur geladen, geformt und bewegt.
 *
 * SKELETT UNTER DER GRUPPE: In der GLB hängt die Hüfte unter vier Hilfsknoten
 * (`Avatar` 180° gedreht, `Root`, `Global`, `Position`). Die Wurzel kommt
 * mit ihrer Weltlage direkt unter die Figurgruppe und wird nach +Z gedreht —
 * genau so rechnet der Server das Skelett für den Retarget (`Umaskelett`),
 * und so passen seine Clips ohne Umweg auf diese Knochen. Das Skinning folgt
 * den Knochen in Weltlage; die Netze selbst brauchen keine eigene Lage.
 *
 * Dieselben Felder wie `CharacterInstance` (clothMeshes, hairMesh, garments,
 * morphs …), damit Liste, Auswahl, Zählung und Speichern nicht je Quelle
 * unterscheiden müssen — sie sind hier nur leer.
 */
export class UmaFigur extends Figurbasis {

    static QUELLE = 'uma';
    static ADRESSE = '/api/character/uma-figur/';
    static OBEN = new THREE.Vector3(0, 1, 0);
    /**
     * Sichtbare Höhe, auf die jede UMA-Figur beim Laden gebracht wird — dieselbe
     * wie `Einpassung.ZIELHOEHE` der Test-Animation-Seite und die HumanBody-Vorgabe
     * (Height 175 → 1,678 m Netz). Edgar, 05.09.2026: „mach die doch gleich groß".
     */
    static ZIELHOEHE = 1.68;

    constructor(id, daten) {
        super(id, UmaFigur.QUELLE);
        this.datei = daten.datei;
        this.presetName = daten.presetName || `UMA · ${(daten.datei || '').replace(/\.glb$/i, '')}`;
        this.bodyType = 'UMA';
        this.dna = { ...(daten.dna || {}) };
        this.farben = { haut: null, haar: null, ...(daten.farben || {}) };
        this.netze = [];
        this.ruhelage = null;
        this.regler = null;
        this.geschlecht = null;
        this.isSkinned = true;
    }

    async load() {
        const gltf = await gltfLoader.loadAsync(UmaFigur.ADRESSE + encodeURIComponent(this.datei) + '/');
        gltf.scene.updateMatrixWorld(true);
        const netze = [];
        gltf.scene.traverse(objekt => { if (objekt.isSkinnedMesh) netze.push(objekt); });
        if (netze.length === 0) throw new Error(`Keine Haut in ${this.datei}`);
        const bones = netze[0].skeleton.bones;
        const boneByName = {};
        for (const bone of bones) boneByName[bone.name] = bone;
        const wurzel = bones.find(bone => !bone.parent || !bone.parent.isBone);

        const lage = new THREE.Matrix4()
            .makeRotationFromQuaternion(UmaFigur.ausrichtung(boneByName))
            .multiply(wurzel.matrixWorld);
        wurzel.removeFromParent();
        this.group.add(wurzel);
        lage.decompose(wurzel.position, wurzel.quaternion, wurzel.scale);
        for (const netz of netze) {
            netz.removeFromParent();
            netz.frustumCulled = false;      // die Knochen tragen die Figur, nicht das Netz
            this.group.add(netz);
        }
        this.group.updateMatrixWorld(true);

        // GLEICH GROSS: UMAs Mensch ist 2,0 m hoch, die HumanBody-Figur 1,68 m.
        // Die Hülle trägt den Maßstab, die Gruppe bleibt bei 1 — die Transform-
        // Felder zeigen weiter 1, und der Regler `height` wirkt wie in Unity,
        // relativ dazu. Die Knochen hängen mit in der Hülle, das Skinning folgt
        // ihren Weltmatrizen (einmal skaliert, nicht doppelt).
        this.hoehe = UmaFigur.hoehe(netze);
        this.huelle = new THREE.Group();
        this.huelle.name = 'uma-huelle';
        this.huelle.scale.setScalar(this.hoehe > 0 ? UmaFigur.ZIELHOEHE / this.hoehe : 1);
        this.huelle.add(wurzel, ...netze);
        this.group.add(this.huelle);
        this.group.updateMatrixWorld(true);

        this.netze = netze;
        this.bodyMesh = UmaFigur.haut(netze);
        this.skelett = { skeleton: netze[0].skeleton, rootBone: wurzel, bones, boneByName };
        this.ruhelage = new Map(bones.map(bone => [bone.name, {
            position: bone.position.clone(), quaternion: bone.quaternion.clone(), scale: bone.scale.clone(),
        }]));

        this.regler = await Umaregler.laden(this.datei);
        this.geschlecht = this.regler.geschlecht;
        this.bodyType = `UMA · ${this.geschlecht}`;
        for (const [name, vorgabe] of Object.entries(this.regler.vorgaben())) {
            if (!(name in this.dna)) this.dna[name] = vorgabe;
        }
        this.anwenden();
        this.farbenAnwenden();
        Protokoll.debug('UmaFigur',
            `${this.datei}: ${netze.length} Netze, ${bones.length} Knochen, ${this.regler.anzahl} Regler`);
        return this;
    }

    /** Drehung um Y, die die Figur nach +Z blicken lässt — wie `Skelettausrichtung`. */
    static ausrichtung(boneByName) {
        const links = boneByName.LeftUpLeg, rechts = boneByName.RightUpLeg;
        const drehung = new THREE.Quaternion();
        if (!links || !rechts) return drehung;
        const quer = links.getWorldPosition(new THREE.Vector3())
            .sub(rechts.getWorldPosition(new THREE.Vector3()));
        quer.y = 0;
        const vorn = quer.cross(UmaFigur.OBEN).normalize();
        return drehung.setFromAxisAngle(UmaFigur.OBEN, -Math.atan2(vorn.x, vorn.z));
    }

    /**
     * Sichtbare Höhe in der Knotenpose: jeden Punkt durch seine Knochen rechnen
     * (`applyBoneTransform`). Nicht `Box3.setFromObject` — das nähme die Bindpose
     * der GLB, und die liegt entlang −Z (meldete 2,06 m statt der echten Höhe).
     */
    static hoehe(netze) {
        const punkt = new THREE.Vector3();
        let unten = Infinity, oben = -Infinity;
        for (const netz of netze) {
            const lage = netz.geometry.attributes.position;
            for (let i = 0; i < lage.count; i++) {
                punkt.fromBufferAttribute(lage, i);
                netz.applyBoneTransform(i, punkt).applyMatrix4(netz.matrixWorld);
                if (punkt.y < unten) unten = punkt.y;
                if (punkt.y > oben) oben = punkt.y;
            }
        }
        return oben > unten ? oben - unten : 0;
    }

    /** Das Hautnetz: das mit „Skin" im Materialnamen, sonst das größte. */
    static haut(netze) {
        return netze.find(n => /skin/i.test(n.material?.name || ''))
            || netze.reduce((a, b) => (b.geometry.attributes.position.count
                > a.geometry.attributes.position.count ? b : a));
    }

    /** Die Regler auf die Knochen rechnen (relativ zur Ruhelage der GLB). */
    anwenden() {
        if (this.regler && this.skelett) {
            this.regler.anwenden(this.dna, this.skelett.boneByName, this.ruhelage);
        }
    }

    /** Ruhelage samt Reglern wiederherstellen — nach einer Animation. */
    ruhelageHerstellen() {
        this.anwenden();
    }

    farbenAnwenden() {
        for (const netz of this.netze) {
            const name = netz.material?.name || '';
            const farbe = /skin/i.test(name) ? this.farben.haut : (/hair/i.test(name) ? this.farben.haar : null);
            if (!netz.material) continue;
            if (!netz.userData.grundfarbe) netz.userData.grundfarbe = netz.material.color.clone();
            if (farbe) netz.material.color.set(farbe);
            else netz.material.color.copy(netz.userData.grundfarbe);
        }
    }

    toJSON() {
        return {
            ...this.grunddaten(),
            datei: this.datei,
            dna: this.dna,
            farben: this.farben,
        };
    }

    static fromJSON(daten) {
        return Figurbasis.ausJSON(UmaFigur, daten);
    }
}
