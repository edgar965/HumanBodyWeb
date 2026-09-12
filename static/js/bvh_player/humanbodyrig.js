/**
 * Humanbodyrig — das umgezielte DEF-Rig (176 Knochen: Körper, Hände, Füße,
 * Gesicht) im Skelettfenster der Ergebnisseite.
 *
 * Edgar (12.09.2026): „sehe ich keine Knochen für Hände, Füsse und Gesicht,
 * kannst du das HumanBody Rig anzeigen auf allen views?" — das Fenster
 * zeichnete nur die Körperknochen des BVH-Formats (`Spielerskelett`). Hier
 * kommt dasselbe Rig dazu, das die 3D-Figur bewegt: `buildRigifySkeleton`
 * plus der Clip von `/api/retarget/?job=` — also Finger, Zehen und die
 * Gesichtsknochen aus der Ausdrucksdatei, so wie der Retarget sie liefert.
 *
 * MASSSTAB UND ORT: Das DEF-Rig lebt in Metern, Bild 0 im Ursprung, Boden bei
 * y = 0 (`Ruhelage`); das BVH-Skelett des Fensters in Zentimetern an der
 * Stelle, die das BVH nennt (bei Kameraraum-BVHs drei Meter vor der Kamera).
 * Das Rig sitzt deshalb in einer Gruppe mit Faktor 100, verschoben, bis sein
 * Becken in Bild 0 auf dem Becken des BVH liegt — beide Skelette decken sich
 * dann, und die Kamera des Fensters muss nicht umziehen.
 *
 * Gezeichnet werden Linien Eltern → Kind für JEDEN Knochen mit Eltern (wie
 * `SkeletonHelper`, aber mit zwei Farben: Rumpf und Glieder grün, Hände, Füße
 * und Gesicht orange — so sieht man, ob genau die Teile mitlaufen, um die es
 * Edgar ging).
 */
import * as THREE from 'three';
import { loadRigifySkeleton, loadSkinWeights, sharedState }
    from '../../viewer/character_core.js';
import { buildRigifySkeleton } from '../../viewer/rigify_skeleton_builder.js';
import { fetchRetargetedClipForJob } from '../../viewer/retarget_hybrid.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

/** Meter → Zentimeter des Skelettfensters. */
const CM_JE_M = 100;
/** Körperhöhe, wenn das Rig keine misst (dieselbe wie die 3D-Figur). */
const NOTHOEHE_M = 1.68;

/**
 * Knochen, die als Hand, Fuß oder Gesicht gelten — nach dem Namensanfang
 * (Familien aus `def_skeleton.json`: f_*, thumb, palm, toe, foot; brow, cheek,
 * chin, ear, forehead, jaw, lid, lip, nose, temple, tongue, MCH-eye/lid,
 * ORG-teeth). `buildRigifySkeleton` ersetzt nur Punkte durch Unterstriche,
 * der Bindestrich nach DEF bleibt.
 */
const FEINTEILE = /^(DEF-(f_|thumb|palm|toe|foot|brow|cheek|chin|ear|forehead|jaw|lid|lip|nose|temple|tongue)|MCH-|ORG-)/;

/** DEF-Knochen (Kopf des Knochens = Gelenk) → Namen des 2D-Gelenks je Wortschatz. */
export const GELENKPAARE = [
    ['DEF-spine', ['Pelvis', 'hip']],
    ['DEF-spine.004', ['Neck', 'neck']],
    ['DEF-spine.006', ['Head', 'head']],
    ['DEF-upper_arm.L', ['Left_shoulder', 'lshoulder']],
    ['DEF-forearm.L', ['Left_elbow', 'lelbow']],
    ['DEF-hand.L', ['Left_wrist', 'lhand']],
    ['DEF-upper_arm.R', ['Right_shoulder', 'rshoulder']],
    ['DEF-forearm.R', ['Right_elbow', 'relbow']],
    ['DEF-hand.R', ['Right_wrist', 'rhand']],
    ['DEF-thigh.L', ['Left_hip', 'lhip']],
    ['DEF-shin.L', ['Left_knee', 'lknee']],
    ['DEF-foot.L', ['Left_ankle', 'lfoot']],
    ['DEF-thigh.R', ['Right_hip', 'rhip']],
    ['DEF-shin.R', ['Right_knee', 'rknee']],
    ['DEF-foot.R', ['Right_ankle', 'rfoot']],
];

export class Humanbodyrig {
    static FARBE_KOERPER = 0x16c784;
    static FARBE_FEINTEILE = 0xf59e0b;

    constructor(szene) {
        this.szene = szene;
        this.gruppe = new THREE.Group();
        this.gruppe.scale.setScalar(CM_JE_M);
        this.gruppe.visible = false;
        this.skelett = null;
        this.mischer = null;
        this.aktion = null;
        this.klipdauer = 0;
        this.linien = [];
        this.paare = [];
    }

    /** Rig bauen, Clip holen, in die Szene setzen. Gibt das Rig zurück.
     *  `klipVersprechen`: der Clip der 3D-Figur (`Klipquelle`, 12.09.2026) —
     *  derselbe Abruf, dieselbe Höhe wie unten; ohne ihn holt das Rig selbst. */
    static async laden(szene, jobId, klipVersprechen = null) {
        const rig = new Humanbodyrig(szene);
        await Promise.all([loadRigifySkeleton(), loadSkinWeights()]);
        rig.skelett = buildRigifySkeleton(
            sharedState.rigifySkeletonData, sharedState.skinWeightData);
        rig.gruppe.add(rig.skelett.rootBone);
        szene.scene.add(rig.gruppe);
        const klip = await (klipVersprechen || fetchRetargetedClipForJob(
            jobId, rig.skelett, { bodyHeight: rig.koerperhoehe() }));
        rig._bewegungBauen(klip);
        rig._linienBauen();
        Protokoll.debug('bvh_player', 'HumanBody-Rig:', rig.paare.length,
                        'Knochen,', klip.tracks.length, 'Spuren');
        return rig;
    }

    /** Höhe des Rigs in der Ruhelage (Meter) — der Maßstab des Retargets. */
    koerperhoehe() {
        const wurzel = this.skelett.rootBone;
        wurzel.updateWorldMatrix(true, true);
        const kasten = new THREE.Box3();
        const punkt = new THREE.Vector3();
        wurzel.traverse((k) => { if (k.isBone) kasten.expandByPoint(k.getWorldPosition(punkt)); });
        const hoehe = kasten.isEmpty() ? 0 : (kasten.max.y - kasten.min.y) / CM_JE_M;
        return hoehe > 0.5 ? hoehe : NOTHOEHE_M;
    }

    /** Ein neuer Clip der Figur (Modellwechsel, Fußkorrektur): Mischer neu, Ort bleibt. */
    klipUebernehmen(klip) {
        this.mischer?.stopAllAction();
        this._bewegungBauen(klip);
        this.linienNachziehen();
    }

    _bewegungBauen(klip) {
        this.mischer = new THREE.AnimationMixer(this.skelett.rootBone);
        this.aktion = this.mischer.clipAction(klip);
        this.aktion.setLoop(THREE.LoopOnce, 1);
        this.aktion.clampWhenFinished = true;
        this.aktion.play();
        this.klipdauer = klip.duration;
        this.mischer.setTime(0);
        this.gruppe.updateWorldMatrix(true, true);
    }

    _linienBauen() {
        this.skelett.rootBone.traverse((kind) => {
            if (!kind.isBone || !kind.parent?.isBone) return;
            this.paare.push([kind.parent, kind]);
        });
        for (const fein of [false, true]) {
            const anzahl = this.paare.filter(([, k]) => this._fein(k) === fein).length;
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position',
                new THREE.BufferAttribute(new Float32Array(anzahl * 6), 3));
            const material = new THREE.LineBasicMaterial({
                color: fein ? Humanbodyrig.FARBE_FEINTEILE : Humanbodyrig.FARBE_KOERPER,
                depthTest: false, depthWrite: false });
            const linien = new THREE.LineSegments(geo, material);
            linien.renderOrder = 998;
            linien.visible = false;
            this.szene.scene.add(linien);
            this.linien.push(linien);
        }
        this.linienNachziehen();
    }

    _fein(knochen) {
        return FEINTEILE.test(knochen.name);
    }

    /** Das Rig so verschieben, dass sein Becken in Bild 0 auf `beckenWelt` liegt. */
    anlegen(beckenWelt) {
        const becken = this.skelett.boneByName['DEF-spine'];
        if (!becken || !beckenWelt) return;
        this.mischer.setTime(0);
        this.gruppe.updateWorldMatrix(true, true);
        const eigen = becken.getWorldPosition(new THREE.Vector3());
        this.gruppe.position.add(beckenWelt.clone().sub(eigen));
        this.gruppe.updateWorldMatrix(true, true);
        this.linienNachziehen();
    }

    /** Linienenden auf die Weltlagen der Knochen setzen. */
    linienNachziehen() {
        const a = new THREE.Vector3(), b = new THREE.Vector3();
        const zeiger = [0, 0];
        for (const [vater, kind] of this.paare) {
            const fein = this._fein(kind) ? 1 : 0;
            const punkte = this.linien[fein].geometry.attributes.position;
            vater.getWorldPosition(a);
            kind.getWorldPosition(b);
            punkte.setXYZ(zeiger[fein], a.x, a.y, a.z);
            punkte.setXYZ(zeiger[fein] + 1, b.x, b.y, b.z);
            zeiger[fein] += 2;
        }
        for (const linien of this.linien) linien.geometry.attributes.position.needsUpdate = true;
    }

    /** Auf einen Zeitpunkt stellen. Gibt false zurück, wenn dahinter. */
    zeitSetzen(sekunden) {
        if (!this.mischer || this.klipdauer <= 0) return false;
        if (sekunden >= this.klipdauer) return false;
        if (this.aktion?.paused) { this.aktion.reset(); this.aktion.play(); }
        this.mischer.setTime(sekunden);
        this.gruppe.updateWorldMatrix(true, true);
        return true;
    }

    sichtbarkeit(an) {
        this.gruppe.visible = an;
        for (const linien of this.linien) linien.visible = an;
        if (an) this.linienNachziehen();
    }

    /** Weltlage eines DEF-Knochens (Originalname mit Punkten) oder null. */
    position(name, ziel) {
        const knochen = this.skelett?.boneByName[name];
        if (!knochen) return null;
        return knochen.getWorldPosition(ziel);
    }

    /** Alle Linienpaare als Weltlagen — für die Videoüberlagerung. */
    weltlinien() {
        return this.paare.map(([v, k]) => [
            v.getWorldPosition(new THREE.Vector3()),
            k.getWorldPosition(new THREE.Vector3()), this._fein(k)]);
    }
}
