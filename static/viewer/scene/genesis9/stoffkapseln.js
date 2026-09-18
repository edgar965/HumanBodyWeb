import { THREE } from '../state.js';

/**
 * Stoffkapseln — der Körper für den Stoffschwung, als Kapseln um die Knochen,
 * und die Häutung auf der CPU (`Stoffhaut`), die dieselbe Rechnung macht wie
 * Threes Vertex-Shader (`bindMatrix`, `boneMatrices`, `bindMatrixInverse`).
 *
 * WARUM KAPSELN: Der Stoff muss je Bild gegen den Körper prüfen — 75.977
 * Punkte des Dancing-Queen-Kleids gegen 104.480 Hautpunkte wäre je Bild ein
 * Nächste-Nachbar-Lauf. Eine Kapsel je Knochen (Achse Kopf→Kind, Radius aus
 * der Haut in Ruhe: 85. Perzentil des Abstands der Hautpunkte, die dieser
 * Knochen am stärksten hält) ist 20–30 Prüfungen je Punkt, mit Hülle davor.
 * Knochen mit weniger als `MINDESTPUNKTE` Hautpunkten (Finger, Gesicht) oder
 * Radius unter `MINDESTRADIUS` bleiben weg; höchstens `HOECHSTENS` Kapseln.
 */
export class Stoffkapseln {

    static MINDESTPUNKTE = 200;
    static MINDESTRADIUS = 0.02;
    static HOECHSTENS = 32;
    static PERZENTIL = 0.85;

    /** Einmal je Skelett: Radien aus dem Körpernetz. `[{bone, kind, r}]`. */
    static anlegen(inst) {
        const netz = inst.bodyMesh;
        if (!netz?.isSkinnedMesh || !netz.skeleton) return [];
        const bones = netz.skeleton.bones;
        const welt = Stoffhaut.welt(netz);
        const index = netz.geometry.attributes.skinIndex.array;
        const gewicht = netz.geometry.attributes.skinWeight.array;
        const n = netz.geometry.attributes.position.count;
        // Der stärkste Knochen je Hautpunkt.
        const zuordnung = new Int32Array(n);
        for (let i = 0; i < n; i++) {
            let beste = 0, w = -1;
            for (let k = 0; k < 4; k++) {
                if (gewicht[4 * i + k] > w) { w = gewicht[4 * i + k]; beste = index[4 * i + k]; }
            }
            zuordnung[i] = beste;
        }
        const a = new THREE.Vector3(), b = new THREE.Vector3(), p = new THREE.Vector3(), q = new THREE.Vector3();
        const aus = [];
        bones.forEach((bone, nummer) => {
            const kind = bone.children.find(k => k.isBone);
            if (!kind) return;
            bone.getWorldPosition(a); kind.getWorldPosition(b);
            const abstaende = [];
            for (let i = 0; i < n; i++) {
                if (zuordnung[i] !== nummer) continue;
                p.set(welt[3 * i], welt[3 * i + 1], welt[3 * i + 2]);
                abstaende.push(Stoffkapseln.abstand(p, a, b, q));
            }
            if (abstaende.length < Stoffkapseln.MINDESTPUNKTE) return;
            abstaende.sort((x, y) => x - y);
            const r = abstaende[Math.floor(abstaende.length * Stoffkapseln.PERZENTIL)];
            if (r < Stoffkapseln.MINDESTRADIUS) return;
            aus.push({ bone, kind, r, punkte: abstaende.length });
        });
        aus.sort((x, y) => y.punkte - x.punkte);
        return aus.slice(0, Stoffkapseln.HOECHSTENS);
    }

    static abstand(p, a, b, q) {
        q.subVectors(b, a);
        const bb = q.lengthSq() || 1e-12;
        let t = p.clone().sub(a).dot(q) / bb;
        t = Math.max(0, Math.min(1, t));
        q.multiplyScalar(t).add(a);
        return p.distanceTo(q);
    }

    /** Die Kapseln dieses Bildes in Weltkoordinaten, flach `[ax,ay,az, bx,by,bz, r, …]` (für den Worker). */
    static bild(kapseln) {
        const v = new THREE.Vector3();
        const aus = new Float32Array(kapseln.length * 7);
        kapseln.forEach((k, i) => {
            k.bone.getWorldPosition(v); aus[7 * i] = v.x; aus[7 * i + 1] = v.y; aus[7 * i + 2] = v.z;
            k.kind.getWorldPosition(v); aus[7 * i + 3] = v.x; aus[7 * i + 4] = v.y; aus[7 * i + 5] = v.z;
            aus[7 * i + 6] = k.r;
        });
        return aus;
    }
}

/** Häutung auf der CPU, Ergebnis in WELTkoordinaten (Float32Array n·3). */
export class Stoffhaut {

    static _m = new THREE.Matrix4();
    static _bind = new THREE.Matrix4();

    /** Je Knochen die Matrix `bindMatrixInverse · matrixWorld · boneInverse · bindMatrix`, als 16er-Block. */
    static matrizen(netz) {
        const { bones, boneInverses } = netz.skeleton;
        const aus = new Float32Array(bones.length * 16);
        const m = Stoffhaut._m, bind = Stoffhaut._bind;
        for (let i = 0; i < bones.length; i++) {
            m.multiplyMatrices(bones[i].matrixWorld, boneInverses[i]);
            bind.multiplyMatrices(m, netz.bindMatrix);
            m.multiplyMatrices(netz.bindMatrixInverse, bind);
            aus.set(m.elements, 16 * i);
        }
        return aus;
    }

    /** Gehäutete Punkte in der Welt (`netz.matrixWorld` obendrauf). */
    static welt(netz, ziel = null) {
        const pos = netz.geometry.attributes.position.array;
        const index = netz.geometry.attributes.skinIndex.array;
        const gewicht = netz.geometry.attributes.skinWeight.array;
        const n = netz.geometry.attributes.position.count;
        const M = Stoffhaut.matrizen(netz);
        const W = netz.matrixWorld.elements;
        const aus = ziel || new Float32Array(n * 3);
        for (let i = 0; i < n; i++) {
            const x = pos[3 * i], y = pos[3 * i + 1], z = pos[3 * i + 2];
            let sx = 0, sy = 0, sz = 0;
            for (let k = 0; k < 4; k++) {
                const w = gewicht[4 * i + k];
                if (w === 0) continue;
                const o = 16 * index[4 * i + k];
                sx += w * (M[o] * x + M[o + 4] * y + M[o + 8] * z + M[o + 12]);
                sy += w * (M[o + 1] * x + M[o + 5] * y + M[o + 9] * z + M[o + 13]);
                sz += w * (M[o + 2] * x + M[o + 6] * y + M[o + 10] * z + M[o + 14]);
            }
            aus[3 * i] = W[0] * sx + W[4] * sy + W[8] * sz + W[12];
            aus[3 * i + 1] = W[1] * sx + W[5] * sy + W[9] * sz + W[13];
            aus[3 * i + 2] = W[2] * sx + W[6] * sy + W[10] * sz + W[14];
        }
        return aus;
    }
}
