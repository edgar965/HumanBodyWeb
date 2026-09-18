import * as THREE from 'three';

/**
 * Dazachsen — Daz' Knochenwinkel aus dem Browser-Skelett lesen und setzen.
 *
 * DAZ DREHT UM DIE KNOCHENACHSEN: `orientation` (Euler XYZ, Grad) legt
 * sie fest, `rotation_order` (`YZX` …) die Reihenfolge, erste Achse zuerst
 * (`Genesis9/knochenmatrizen.py`, 18.09.2026): `R = O · E · O⁻¹` im Raum
 * der Figur. Three.js' `Euler` mit Ordnung `XYZ` ist `Rx·Ry·Rz` — Daz'
 * `XYZ` (X zuerst angewandt) ist `Rz·Ry·Rx`, also Threes `ZYX`: die
 * Ordnung wird UMGEKEHRT gelesen.
 *
 * DAS BROWSER-SKELETT hat eine geometrische Ruhelage (`Gelenkskelett`,
 * +Y entlang des Knochens, kein Roll) — Daz' Ruhe ist die Einheit. Mit
 * `Qp` (Ruhelage des Elternteils im Figurraum, aus `boneInverses`), `r`
 * (lokale Ruhedrehung) und `q` (lokale Drehung des Bildes, vom Mischer):
 *
 *     E = O⁻¹ · Qp · q · r⁻¹ · Qp⁻¹ · O  =  A · q · B
 *     q = A⁻¹ · E · B⁻¹
 *
 * `A` und `B` sind je Knochen konstant (`vorbereiten`); je Bild bleibt
 * eine Multiplikation und eine Euler-Zerlegung (`winkel`). Damit lesen
 * die Gelenkkorrekturen (`genesis9gelenke.js`) `l_thigh?rotation/x` aus
 * der BVH-Bewegung, und die Visemes setzen `lowerjaw` (`quaternion`).
 * Verschiebungen (`translation`, cm im Elternraum) gehen als
 * `Qp⁻¹ · t` auf `position` (`versatz`).
 */
export class Dazachsen {

    static _q = new THREE.Quaternion();
    static _e = new THREE.Euler();
    static _v = new THREE.Vector3();
    static _m = new THREE.Matrix4();

    /** Threes Euler-Ordnung zu Daz' `rotation_order` (umgekehrt gelesen). */
    static ordnung(daz) {
        return String(daz || 'XYZ').toUpperCase().split('').reverse().join('');
    }

    /** `O` aus Daz' `orientation` (Grad, Ordnung XYZ = Threes ZYX). */
    static orientierung(grad) {
        const r = Math.PI / 180;
        return new THREE.Quaternion().setFromEuler(
            new THREE.Euler(grad[0] * r, grad[1] * r, grad[2] * r, 'ZYX'));
    }

    /**
     * Konstanten je Knochen: `{A, Ainv, B, Binv, Qp, order, ruhePos, ruheQuat}`.
     * @param skelett  `{skeleton, bones, boneByName}` (Knochenbau)
     * @param achsen   `{name: {o: [x, y, z], r: 'XYZ'}}` vom Server
     */
    static vorbereiten(skelett, achsen) {
        const aus = {};
        const bones = skelett.skeleton.bones;
        const ruhe = bones.map((_, i) => {
            const m = skelett.skeleton.boneInverses[i].clone().invert();
            const p = new THREE.Vector3(), q = new THREE.Quaternion(), s = new THREE.Vector3();
            m.decompose(p, q, s);
            return { p, q };
        });
        const nummer = new Map(bones.map((b, i) => [b, i]));
        bones.forEach((bone, i) => {
            const a = achsen[bone.name];
            if (!a) return;
            const elternNr = nummer.get(bone.parent);
            const Qp = elternNr === undefined ? new THREE.Quaternion() : ruhe[elternNr].q.clone();
            const Qw = ruhe[i].q;
            const r = Qp.clone().invert().multiply(Qw);             // lokale Ruhedrehung
            const O = Dazachsen.orientierung(a.o);
            const A = O.clone().invert().multiply(Qp);
            const B = r.clone().invert().multiply(Qp.clone().invert()).multiply(O);
            const ruhePos = elternNr === undefined ? ruhe[i].p.clone()
                : ruhe[i].p.clone().sub(ruhe[elternNr].p).applyQuaternion(Qp.clone().invert());
            aus[bone.name] = {
                bone, A, B, Ainv: A.clone().invert(), Binv: B.clone().invert(),
                Qp, order: Dazachsen.ordnung(a.r), ruhePos, ruheQuat: r,
            };
        });
        return aus;
    }

    /** Daz-Winkel (Grad, [x, y, z]) des Knochens im aktuellen Bild. */
    static winkel(k, aus = [0, 0, 0]) {
        const q = Dazachsen._q.copy(k.A).multiply(k.bone.quaternion).multiply(k.B);
        Dazachsen._e.setFromQuaternion(q, k.order);
        const g = 180 / Math.PI;
        aus[0] = Dazachsen._e.x * g; aus[1] = Dazachsen._e.y * g; aus[2] = Dazachsen._e.z * g;
        return aus;
    }

    /** Die lokale Drehung, die den Daz-Winkeln (Grad, [x, y, z]) entspricht. */
    static quaternion(k, grad, aus = new THREE.Quaternion()) {
        const r = Math.PI / 180;
        Dazachsen._e.set(grad[0] * r, grad[1] * r, grad[2] * r, k.order);
        Dazachsen._q.setFromEuler(Dazachsen._e);
        return aus.copy(k.Ainv).multiply(Dazachsen._q).multiply(k.Binv);
    }

    /** Daz-Verschiebung (cm, Elternraum der Figur) als lokaler Versatz (m). */
    static versatz(k, cm, aus = new THREE.Vector3()) {
        return aus.set(cm[0] / 100, cm[1] / 100, cm[2] / 100)
            .applyQuaternion(Dazachsen._q.copy(k.Qp).invert());
    }
}
