/**
 * Skelettformat — welche Knochen ein BVH hat und wie sie verbunden sind.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026): Die vier Tabellen und die
 * Formaterkennung standen mitten in der 907 Zeilen langen `initBVHPlayer`.
 */

/** MocapNET-Koerperknochen. */
const MOCAPNET_KNOCHEN = [
    'hip', 'abdomen', 'chest', 'neck', 'neck1', 'head',
    'rCollar', 'rShldr', 'rForeArm', 'rHand',
    'lCollar', 'lShldr', 'lForeArm', 'lHand',
    'rButtock', 'rThigh', 'rShin', 'rFoot',
    'lButtock', 'lThigh', 'lShin', 'lFoot',
];

const MOCAPNET_VERBINDUNGEN = [
    ['hip', 'abdomen'], ['abdomen', 'chest'], ['chest', 'neck'],
    ['neck', 'neck1'], ['neck1', 'head'],
    ['chest', 'rCollar'], ['rCollar', 'rShldr'], ['rShldr', 'rForeArm'],
    ['rForeArm', 'rHand'],
    ['chest', 'lCollar'], ['lCollar', 'lShldr'], ['lShldr', 'lForeArm'],
    ['lForeArm', 'lHand'],
    ['hip', 'rButtock'], ['rButtock', 'rThigh'], ['rThigh', 'rShin'],
    ['rShin', 'rFoot'],
    ['hip', 'lButtock'], ['lButtock', 'lThigh'], ['lThigh', 'lShin'],
    ['lShin', 'lFoot'],
];

/** SMPL-Koerperknochen. Reihenfolge = Beschriftungsnummern in der Anzeige. */
const SMPL_KNOCHEN = [
    'Pelvis', 'Spine1', 'Spine2', 'Spine3', 'Neck', 'Head',
    'Left_hip', 'Left_knee', 'Left_ankle', 'Left_foot',
    'Right_hip', 'Right_knee', 'Right_ankle', 'Right_foot',
    'Left_collar', 'Left_shoulder', 'Left_elbow', 'Left_wrist',
    'Right_collar', 'Right_shoulder', 'Right_elbow', 'Right_wrist',
];

const SMPL_VERBINDUNGEN = [
    ['Pelvis', 'Spine1'], ['Spine1', 'Spine2'], ['Spine2', 'Spine3'],
    ['Spine3', 'Neck'], ['Neck', 'Head'],
    ['Spine3', 'Left_collar'], ['Left_collar', 'Left_shoulder'],
    ['Left_shoulder', 'Left_elbow'], ['Left_elbow', 'Left_wrist'],
    ['Spine3', 'Right_collar'], ['Right_collar', 'Right_shoulder'],
    ['Right_shoulder', 'Right_elbow'], ['Right_elbow', 'Right_wrist'],
    ['Pelvis', 'Left_hip'], ['Left_hip', 'Left_knee'],
    ['Left_knee', 'Left_ankle'], ['Left_ankle', 'Left_foot'],
    ['Pelvis', 'Right_hip'], ['Right_hip', 'Right_knee'],
    ['Right_knee', 'Right_ankle'], ['Right_ankle', 'Right_foot'],
];

/**
 * Elternknochen je SMPL-Knochen — fuer die Winkel der Vergleichstafel.
 * Die Handflaechen stehen nur hier, nicht in SMPL_KNOCHEN: Sie kommen aus den
 * 2D-Daten, nicht aus dem BVH.
 */
export const SMPL_ELTERN = {
    'Pelvis': null,
    'Spine1': 'Pelvis', 'Spine2': 'Spine1', 'Spine3': 'Spine2',
    'Neck': 'Spine3', 'Head': 'Neck',
    'Left_collar': 'Spine3', 'Left_shoulder': 'Left_collar',
    'Left_elbow': 'Left_shoulder', 'Left_wrist': 'Left_elbow',
    'Left_palm': 'Left_wrist',
    'Right_collar': 'Spine3', 'Right_shoulder': 'Right_collar',
    'Right_elbow': 'Right_shoulder', 'Right_wrist': 'Right_elbow',
    'Right_palm': 'Right_wrist',
    'Left_hip': 'Pelvis', 'Left_knee': 'Left_hip',
    'Left_ankle': 'Left_knee', 'Left_foot': 'Left_ankle',
    'Right_hip': 'Pelvis', 'Right_knee': 'Right_hip',
    'Right_ankle': 'Right_knee', 'Right_foot': 'Right_ankle',
};

/** Zeilen der Vergleichstafel — SMPL plus die beiden Handflaechen. */
export const VERGLEICHSKNOCHEN = [...SMPL_KNOCHEN.slice(0, 22)]
    .concat(['Left_palm', 'Right_palm']);

export class Skelettformat {
    constructor(name, knochen, verbindungen) {
        this.name = name;
        this.namen = new Set(knochen);
        this.reihenfolge = knochen;
        this.verbindungen = verbindungen;
    }

    /**
     * Format an den vorhandenen Knochennamen erkennen.
     * SMPL, sobald Pelvis UND Left_hip da sind — sonst MocapNET.
     */
    static erkennen(vorhandeneNamen) {
        if (vorhandeneNamen.has('Pelvis') && vorhandeneNamen.has('Left_hip')) {
            return new Skelettformat('SMPL', SMPL_KNOCHEN, SMPL_VERBINDUNGEN);
        }
        return new Skelettformat('MocapNET', MOCAPNET_KNOCHEN,
                                 MOCAPNET_VERBINDUNGEN);
    }

    /** Vorgabe, solange kein BVH geladen ist. */
    static vorgabe() {
        return new Skelettformat('MocapNET', MOCAPNET_KNOCHEN,
                                 MOCAPNET_VERBINDUNGEN);
    }

    /** Welche der erwarteten Knochen das BVH liefert und welche fehlen. */
    abgleich(vorhandeneNamen) {
        const da = [], fehlt = [];
        for (const n of this.reihenfolge) {
            (vorhandeneNamen.has(n) ? da : fehlt).push(n);
        }
        return { da, fehlt };
    }

    /** Nummer eines Knochens in der Beschriftung. */
    nummer(name) {
        return this.reihenfolge.indexOf(name);
    }
}
