import * as THREE from 'three';

/**
 * Die Geometrie eines GarmentCode-Stücks aus seiner Rig-Datei.
 *
 * Herausgelöst aus `garmentcode_anziehen.js` (11.09.2026), als die
 * Körpernormalen dazukamen und die Datei über 300 Zeilen ging.
 */
export class GarmentcodeGeometrie {

    /** Punkte und Dreiecke zu einer Geometrie. */
    static aus(daten) {
        const punkte = daten?.punkte || [];
        const dreiecke = daten?.dreiecke || [];
        if (!punkte.length || !dreiecke.length) {
            throw new Error('Rig-Datei ohne Netz');
        }
        // Z OBEN → Y OBEN. Die Rig-Datei steht in Projektkoordinaten
        // (`Anziehen.aus_garmentcode`: „cm, Y oben" → „m, Z oben", also
        // Blender-Konvention), die Szene rechnet wie Three.js mit Y oben.
        // Ohne diese Drehung lag das Kleidungsstück flach am Boden neben der
        // Figur: gemessen y −0,14…0,14 bei einem Körper von 0…1,68
        // (06.09.2026). Dieselbe Umstellung wie `to_threejs()` bei den Posen.
        const lage = new Float32Array(punkte.length * 3);
        for (let i = 0; i < punkte.length; i++) {
            lage[i * 3] = punkte[i][0];
            lage[i * 3 + 1] = punkte[i][2];
            lage[i * 3 + 2] = -punkte[i][1];
        }
        const felder = new Uint32Array(dreiecke.length * 3);
        for (let i = 0; i < dreiecke.length; i++) {
            felder[i * 3] = dreiecke[i][0];
            felder[i * 3 + 1] = dreiecke[i][1];
            felder[i * 3 + 2] = dreiecke[i][2];
        }
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geometrie.setIndex(new THREE.BufferAttribute(felder, 1));
        // UV je Punkt, wenn die Rig-Datei sie führt (seit 10.09.2026). Sie
        // stehen NICHT in Three-Achsen: Eine UV ist eine Lage im flach
        // ausgebreiteten Schnittmuster und von der Achswandlung oben
        // unberührt.
        const uv = daten?.uv;
        if (Array.isArray(uv) && uv.length === punkte.length) {
            const flaeche = new Float32Array(uv.length * 2);
            for (let i = 0; i < uv.length; i++) {
                flaeche[i * 2] = uv[i][0];
                flaeche[i * 2 + 1] = uv[i][1];
            }
            geometrie.setAttribute('uv', new THREE.BufferAttribute(flaeche, 2));
        }
        // Körpernormalen (seit 11.09.2026, `stoffanlegen.py`): Ein an die
        // Haut gelegtes Stück schattiert wie die Haut. Aus dem 8-mm-Netz
        // gerechnet wichen die Normalen median 2, p90 5 Grad ab — Dellen
        // am Gesäß, die die Geometrie nicht hat. Dieselbe Achswandlung.
        const normalen = daten?.normalen;
        if (Array.isArray(normalen) && normalen.length === punkte.length) {
            const n = new Float32Array(normalen.length * 3);
            for (let i = 0; i < normalen.length; i++) {
                n[i * 3] = normalen[i][0];
                n[i * 3 + 1] = normalen[i][2];
                n[i * 3 + 2] = -normalen[i][1];
            }
            geometrie.setAttribute('normal', new THREE.BufferAttribute(n, 3));
            geometrie.userData.festeNormalen = true;
        } else {
            geometrie.computeVertexNormals();
        }
        return geometrie;
    }
}
