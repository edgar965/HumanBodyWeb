import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst } from './utils.js';
import { convertInstToSkinned } from './skeleton.js';
import { generateModelMesh } from './state.js';
import { generateRigBoneMesh } from '../modellbau/rignetz.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Kleiderhuelle — Stufe 1 der Kleideranpassung: Aus einem Knochenmodell wird
 * eine Hülle um den Körper gebaut, an die das Kleidungsstück später angepasst
 * wird.
 *
 * Aus scene/kleider_anpassen.js herausgeloest (Umbau 16.08.2026):
 * `_doKleiderStage1()` hatte 111 Zeilen.
 *
 * FEHLER dabei behoben: Der Rig-Zweig holte sein Netz per
 * `await import('../model_generator.js')` — diese Datei wurde beim Umbau am
 * 15.08.2026 in `modellbau/` aufgeteilt und existiert nicht mehr. Ein
 * dynamischer Import mitten in einer Funktion fällt erst auf, wenn genau
 * dieser Zweig läuft: beim Anpassen mit einem Rig-Modell (Rig1–4, die Vorgabe
 * der Einstellungen!). Jetzt ein fester Import auf `modellbau/rignetz.js`.
 * Gefunden mit Docu/umbau/verwaiste_module.py.
 */
export class Kleiderhuelle {

    /** Modell, wenn die Einstellungen keins nennen. */
    static VORGABEMODELL = 'Rig1';
    /** Schlüssel, unter dem die Hülle an der Figur hängt. */
    static SCHLUESSEL = 'kld_hull';
    /** Radius der Knochen, wenn das Modell keinen nennt. */
    static KNOCHENRADIUS = 0.03;
    static RADIUS_FAKTOR = 1.3;
    /** Die Hülle wird halbdurchsichtig blau gezeigt. */
    static FARBE = 0x44aaff;
    static DECKKRAFT = 0.5;

    static async bauen() {
        const figur = _selectedInst();
        if (!figur) return null;
        return new Kleiderhuelle(figur).bauen();
    }

    constructor(figur) {
        this.figur = figur;
    }

    async bauen() {
        if (!this.figur.isSkinned && state.rigifySkeletonData
            && state.skinWeightData) {
            convertInstToSkinned(this.figur);
        }
        const modellname = await this.modellname();
        const vorgabe = await this.vorgabe(modellname);
        if (!vorgabe) return null;
        this.radienSkalieren(vorgabe);
        const ergebnis = await this.netz(vorgabe);
        if (!ergebnis?.mesh) {
            console.warn('Stufe 1: Knochenmodell nicht baubar:', modellname);
            return null;
        }
        this.alteHuelleEntfernen();
        this.serverpunkteMerken(ergebnis.mesh);
        this.einsetzen(ergebnis.mesh);
        Protokoll.debug('Szene', `Stufe 1: Knochenmodell '${modellname}' geladen `
                    + `(${ergebnis.mesh.geometry.getAttribute('position').count} Punkte)`);
        fn.updateEquippedList(this.figur);
        fn.updateVertexCount();
        return ergebnis.mesh;
    }

    /** Welches Knochenmodell? Steht in Einstellungen → Szene → Kleider. */
    async modellname() {
        try {
            const daten = await Serverabruf.json('/api/settings/humanbody/');
            return daten.ui_prefs?.kleider_bone_model
                   || Kleiderhuelle.VORGABEMODELL;
        } catch (fehler) {
            console.warn('Einstellungen nicht ladbar:', fehler);
            return Kleiderhuelle.VORGABEMODELL;
        }
    }

    async vorgabe(name) {
        try {
            // `await` MUSS hier stehen: Ohne es verlaesst das Versprechen die
            // Funktion, bevor es scheitert — der catch griffe nie.
            return await Serverabruf.json('/api/character/model/'
                                          + encodeURIComponent(name) + '/');
        } catch (fehler) {
            console.error('Stufe 1: Knochenmodell nicht ladbar:', name, fehler);
            return null;
        }
    }

    /** Der Regler macht die Hülle dicker, damit Kleidung darüber passt. */
    radienSkalieren(vorgabe) {
        const faktor = parseFloat(
            document.getElementById('kleider-bone-radius')?.value)
            || Kleiderhuelle.RADIUS_FAKTOR;
        for (const teil of Object.values(vorgabe.bone_parts || {})) {
            if (!teil.visible) continue;
            teil.radius = (teil.radius || Kleiderhuelle.KNOCHENRADIUS) * faktor;
        }
    }

    async netz(vorgabe) {
        const alsRig = vorgabe.skeleton_type === 'rig'
                       || vorgabe.type === 'generated_model';
        if (!alsRig) {
            return generateModelMesh(state.rigifySkeletonData,
                                     state.skinWeightData, vorgabe);
        }
        let rigdaten = null;
        try {
            rigdaten = await Serverabruf.json('/api/character/rig/');
        } catch (fehler) {
            console.warn('Rig nicht ladbar:', fehler);
        }
        return generateRigBoneMesh(rigdaten, vorgabe, state.rigifySkeletonData,
                                   state.skinWeightData);
    }

    alteHuelleEntfernen() {
        const alt = this.figur.clothMeshes[Kleiderhuelle.SCHLUESSEL];
        if (!alt) return;
        this.figur.group.remove(alt);
        alt.geometry.dispose();
        alt.material.dispose();
        delete this.figur.clothMeshes[Kleiderhuelle.SCHLUESSEL];
    }

    /**
     * Der Server rechnet in Blender-Koordinaten. Die Punkte werden hier
     * umgerechnet und gemerkt, damit Stufe 2 sie senden kann.
     */
    serverpunkteMerken(netz) {
        const punkte = netz.geometry.getAttribute('position').array;
        const blender = new Float32Array(punkte.length);
        for (let i = 0; i < punkte.length; i += 3) {
            blender[i] = punkte[i];
            blender[i + 1] = -punkte[i + 2];
            blender[i + 2] = punkte[i + 1];
        }
        state._kleiderHullVertices = blender;
    }

    einsetzen(netz) {
        netz.material = new THREE.MeshStandardMaterial({
            color: Kleiderhuelle.FARBE, roughness: 0.5, metalness: 0.1,
            transparent: true, opacity: Kleiderhuelle.DECKKRAFT,
            side: THREE.DoubleSide,
        });
        this.poseUebernehmen(netz);
        this.figur.clothMeshes[Kleiderhuelle.SCHLUESSEL] = netz;
        this.figur.group.add(netz);
    }

    /**
     * Die Hülle hat ihr eigenes Skelett. Ohne Übernahme der Körperpose stünde
     * sie in T-Pose, während die Figur schon posiert ist.
     */
    poseUebernehmen(netz) {
        const koerperskelett = this.figur.bodyMesh?.isSkinnedMesh
            ? this.figur.bodyMesh.skeleton : null;
        if (!netz.isSkinnedMesh || !netz.skeleton || !koerperskelett) return;
        let uebernommen = 0;
        for (const knochen of netz.skeleton.bones) {
            const vorbild = koerperskelett.getBoneByName(knochen.name);
            if (!vorbild) continue;
            knochen.quaternion.copy(vorbild.quaternion);
            uebernommen++;
        }
        const wurzel = netz.skeleton.bones.find(k => !k.parent || k.parent === netz);
        wurzel?.updateWorldMatrix(true, true);
        Protokoll.debug('Hülle', `${uebernommen} Knochendrehungen aus der Körperpose`);
    }
}
