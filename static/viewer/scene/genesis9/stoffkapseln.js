import { THREE } from '../state.js';
import { Kapselmass } from '../../gemeinsam/kapselmass.js';
import { Stoffkoerper } from '../../gemeinsam/stoffkoerper.js';

/**
 * Stoffkapseln — der Körper für den Stoffschwung, als Kapseln um die Knochen,
 * und die Häutung auf der CPU (`Stoffhaut`), die dieselbe Rechnung macht wie
 * Threes Vertex-Shader (`bindMatrix`, `boneMatrices`, `bindMatrixInverse`).
 *
 * WARUM KAPSELN: Der Stoff muss je Bild gegen den Körper prüfen — 75.977
 * Punkte des Dancing-Queen-Kleids gegen 104.480 Hautpunkte wäre je Bild ein
 * Nächste-Nachbar-Lauf. Eine Kapsel je Knochen (Achse Kopf→Mittel seiner
 * Knochenkinder, Radius aus der Haut der Hautpunkte, die dieser Knochen am
 * stärksten hält) ist 20–30 Prüfungen je Punkt, mit Hülle davor.
 * Knochen mit weniger als `MINDESTPUNKTE` Hautpunkten (Finger, Gesicht) oder
 * Radius unter `MINDESTRADIUS` bleiben weg; höchstens `HOECHSTENS` Kapseln.
 *
 * KONISCH, MEDIAN, KINDERMITTEL (19.09.2026, Edgar: „Hose (genesis) animiert
 * nicht"): In Daz' Idle blähte die Angie-Jeans an Ursula 12–19 cm auf. Ohne
 * Kapseln folgte sie der gehäuteten Lage auf 5,6 mm (max 33 mm), mit den
 * alten Kapseln (EIN Radius, 85. Perzentil, Achse zum ERSTEN Kind) lag sie
 * 36 mm daneben (max 120): `l_thightwist1` bekam 12 cm über die ganze Länge —
 * am Knie ist der Schenkel halb so dick —, und `pelvis → l_thigh` läuft
 * schief nach links, sodass der rechte Hüftpunkt 15 cm „Radius" ergab.
 * Jetzt: Achse zum Mittel der Knochenkinder, je Ende zwei Halbachsen quer
 * zum Knochen (Hauptachsen der Hautpunkte, `Kapselmass.ellipse`), dazwischen
 * linear; die erste Hauptachse `u` liegt im Knochenraum und dreht mit
 * (`bild`). Rund mit Median gemessen: 8,7 mm / max 65 mm, aber 2,4 % der
 * Jeanspunkte bis 19 mm in der Haut — die Ellipse trifft beide Seiten.
 */
export class Stoffkapseln {

    static MINDESTPUNKTE = 200;
    static MINDESTRADIUS = 0.02;
    static HOECHSTENS = 32;
    /** Die Achse spannt die Hautpunkte auf — ohne die äußersten 2 % je Ende. */
    static RAND = 0.02;

    /** Einmal je Skelett: Maße aus dem Körpernetz. `[{bone, kinder, u (Knochenraum), ta, tb, rua, rwa, rub, rwb}]`. */
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
        const a = new THREE.Vector3(), b = new THREE.Vector3(), q = new THREE.Vector3();
        const d = new THREE.Vector3(), e1 = new THREE.Vector3(), e2 = new THREE.Vector3(), o = new THREE.Vector3();
        const aus = [];
        bones.forEach((bone, nummer) => {
            const kinder = bone.children.filter(k => k.isBone);
            if (!kinder.length) return;
            bone.getWorldPosition(a); Stoffkapseln.mittel(kinder, b, q);
            Stoffkapseln.basis(a, b, d, e1, e2);
            // Projektion auf die Achse (Meter ab a) — die Kapsel reicht zum Kopf
            // hin so weit wie die Haut des Knochens (`spine1` hält den Bauch
            // nicht, `pelvis` schon), zum Kind hin höchstens bis zum Kind: Über
            // die Schenkelköpfe hinaus verlängert stand die Pelvis-Kapsel im
            // Schritt und drückte die Jeans dort 19 cm heraus (19.09.2026).
            const lauf = [], x1 = [], x2 = [];
            for (let i = 0; i < n; i++) {
                if (zuordnung[i] !== nummer) continue;
                o.set(welt[3 * i], welt[3 * i + 1], welt[3 * i + 2]).sub(a);
                lauf.push(o.dot(d)); x1.push(o.dot(e1)); x2.push(o.dot(e2));
            }
            if (lauf.length < Stoffkapseln.MINDESTPUNKTE) return;
            const ta = Math.min(0, Kapselmass.perzentil(lauf, Stoffkapseln.RAND));
            const tb = Math.min(a.distanceTo(b), Kapselmass.perzentil(lauf, 1 - Stoffkapseln.RAND));
            if (tb - ta < 1e-3) return;
            const anteile = lauf.map((l) => (l - ta) / (tb - ta));
            const m = Kapselmass.ellipse(x1, x2, anteile);
            if (Math.max(m.rua, m.rwa, m.rub, m.rwb) < Stoffkapseln.MINDESTRADIUS) return;
            // u in den Knochenraum — dreht dann mit dem Knochen (`bild`).
            const u = e1.clone().multiplyScalar(Math.cos(m.theta)).addScaledVector(e2, Math.sin(m.theta));
            u.applyQuaternion(bone.getWorldQuaternion(new THREE.Quaternion()).invert());
            aus.push({ bone, kinder, u, ta, tb, rua: m.rua, rwa: m.rwa, rub: m.rub, rwb: m.rwb, punkte: lauf.length });
        });
        aus.sort((x, y) => y.punkte - x.punkte);
        return aus.slice(0, Stoffkapseln.HOECHSTENS);
    }

    /** Achse `d` = b − a (Einheit) und eine Basis `e1`, `e2` senkrecht dazu. */
    static basis(a, b, d, e1, e2) {
        d.subVectors(b, a).normalize();
        e1.set(0, 1, 0);
        if (Math.abs(d.dot(e1)) > 0.9) e1.set(1, 0, 0);
        e1.crossVectors(d, e1).normalize();
        e2.crossVectors(d, e1);
    }

    /** Das Mittel der Weltlagen der Knochenkinder in `ziel`. */
    static mittel(kinder, ziel, q) {
        ziel.set(0, 0, 0);
        for (const k of kinder) ziel.add(k.getWorldPosition(q));
        return ziel.divideScalar(kinder.length);
    }

    /** Die Kapseln dieses Bildes in Weltkoordinaten, flach (13 je Kapsel, `Stoffkoerper.lesen`). */
    static bild(kapseln) {
        const v = new THREE.Vector3(), q = new THREE.Vector3(), dreh = new THREE.Quaternion();
        const je = Stoffkoerper.JE_KAPSEL, aus = new Float32Array(kapseln.length * je);
        const a = new THREE.Vector3(), d = new THREE.Vector3();
        kapseln.forEach((k, i) => {
            const o = je * i;
            k.bone.getWorldPosition(a); Stoffkapseln.mittel(k.kinder, v, q); d.subVectors(v, a).normalize();
            v.copy(a).addScaledVector(d, k.ta); aus[o] = v.x; aus[o + 1] = v.y; aus[o + 2] = v.z;
            v.copy(a).addScaledVector(d, k.tb); aus[o + 3] = v.x; aus[o + 4] = v.y; aus[o + 5] = v.z;
            v.copy(k.u).applyQuaternion(k.bone.getWorldQuaternion(dreh)); aus[o + 6] = v.x; aus[o + 7] = v.y; aus[o + 8] = v.z;
            aus[o + 9] = k.rua; aus[o + 10] = k.rwa; aus[o + 11] = k.rub; aus[o + 12] = k.rwb;
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
