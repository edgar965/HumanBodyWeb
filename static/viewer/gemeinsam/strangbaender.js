import * as THREE from 'three';

/**
 * Strangbaender — Wireframe-Strähnen für den Export in schmale Bänder
 * verwandeln.
 *
 * WARUM (26.09.2026): dForce-Stranghaar ist im Viewer ein `SkinnedMesh` mit
 * `wireframe`-Material, dessen Dreiecke alle die Form `[a, b, b]` haben. Im
 * Wireframe zeichnet WebGL die Kanten, und von `(a, b, b)` bleibt genau die
 * Linie a–b übrig — das Strähnensegment (`A:\3DTools\Genesis9\strang.py`).
 * Der Umweg über Dreiecke existiert nur, weil three.js `LineSegments` nicht
 * skinnen kann.
 *
 * OBJ, PLY, STL und GLB kennen kein Wireframe-Flag. Dort ist ein Dreieck mit
 * Fläche 0 unsichtbar, und MeshLab meldet beim Öffnen „Identical vertex
 * indices found in the same faces — faces ignored". Sie wegzufiltern wäre
 * falsch: dann fehlte das Haar ganz. Stattdessen bekommt jedes Segment hier
 * eine Breite — aus einer Linie werden vier Punkte und zwei Dreiecke.
 *
 * Läuft NACH dem Skinning (`Netzpose.gebacken`), damit die Punkte schon in
 * ihrer endgültigen Lage stehen und keine Hautgewichte mitgeführt werden
 * müssen.
 */
export class Strangbaender {

    //: Strähnenbreite in Szeneneinheiten (Meter). Daz zeichnet Stränge im
    //: Ansichtsfenster ein Pixel breit; 0,4 mm liegt in der Größenordnung
    //: eines echten Haares und bleibt in MeshLab/Blender sichtbar.
    static BREITE = 0.0004;

    /** Ob die Geometrie aus lauter entarteten Dreiecken besteht (Stranghaar). */
    static istStrang(geometrie) {
        const index = geometrie.getIndex();
        if (!index || !index.count) return false;
        const a = index.array;
        for (let i = 0; i < a.length; i += 3) {
            if (a[i] !== a[i + 1] && a[i + 1] !== a[i + 2] && a[i] !== a[i + 2]) return false;
        }
        return true;
    }

    /**
     * Neue Geometrie mit Bändern statt Linien; Materialgruppen wandern mit
     * (je Segment werden aus 3 Indizes deren 6).
     * @returns die neue `BufferGeometry`, oder `null` wenn nichts zu tun war
     */
    static bauen(geometrie, breite = Strangbaender.BREITE) {
        if (!Strangbaender.istStrang(geometrie)) return null;
        const index = geometrie.getIndex().array;
        const punkte = geometrie.getAttribute('position');
        const uv = geometrie.getAttribute('uv');
        const segmente = index.length / 3;

        const lage = new Float32Array(segmente * 4 * 3);
        const netzuv = uv ? new Float32Array(segmente * 4 * 2) : null;
        const neuIndex = new Uint32Array(segmente * 6);

        const anfang = new THREE.Vector3();
        const ende = new THREE.Vector3();
        const richtung = new THREE.Vector3();
        const quer = new THREE.Vector3();
        const bezug = new THREE.Vector3();

        for (let s = 0; s < segmente; s++) {
            const a = index[s * 3];
            const b = index[s * 3 + 1];
            anfang.fromBufferAttribute(punkte, a);
            ende.fromBufferAttribute(punkte, b);
            richtung.subVectors(ende, anfang);
            // Irgendeine Richtung quer zur Strähne — ohne Kamera gibt es keine
            // „richtige"; senkrecht zur Strähne reicht, damit Fläche entsteht.
            bezug.set(0, 0, 1);
            if (Math.abs(richtung.dot(bezug)) > 0.99 * richtung.length()) bezug.set(0, 1, 0);
            quer.crossVectors(richtung, bezug);
            const laenge = quer.length();
            if (laenge < 1e-12) quer.set(breite / 2, 0, 0);
            else quer.multiplyScalar(breite / 2 / laenge);

            const p = s * 4;
            Strangbaender._punkt(lage, p + 0, anfang, quer, -1);
            Strangbaender._punkt(lage, p + 1, anfang, quer, +1);
            Strangbaender._punkt(lage, p + 2, ende, quer, +1);
            Strangbaender._punkt(lage, p + 3, ende, quer, -1);
            if (netzuv) {
                for (const [ecke, quelle] of [[0, a], [1, a], [2, b], [3, b]]) {
                    netzuv[(p + ecke) * 2] = uv.getX(quelle);
                    netzuv[(p + ecke) * 2 + 1] = uv.getY(quelle);
                }
            }
            const i = s * 6;
            neuIndex[i] = p; neuIndex[i + 1] = p + 1; neuIndex[i + 2] = p + 2;
            neuIndex[i + 3] = p; neuIndex[i + 4] = p + 2; neuIndex[i + 5] = p + 3;
        }

        const neu = new THREE.BufferGeometry();
        neu.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        if (netzuv) neu.setAttribute('uv', new THREE.BufferAttribute(netzuv, 2));
        neu.setIndex(new THREE.BufferAttribute(neuIndex, 1));
        for (const g of geometrie.groups) {
            neu.addGroup(g.start * 2, g.count * 2, g.materialIndex);
        }
        return neu;
    }

    static _punkt(ziel, nummer, mitte, quer, seite) {
        ziel[nummer * 3] = mitte.x + quer.x * seite;
        ziel[nummer * 3 + 1] = mitte.y + quer.y * seite;
        ziel[nummer * 3 + 2] = mitte.z + quer.z * seite;
    }
}
