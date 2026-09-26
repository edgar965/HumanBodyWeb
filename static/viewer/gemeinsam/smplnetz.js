import * as THREE from 'three';

/**
 * Smplnetz — das Browsernetz eines SMPL-Körpers aus Punkten und Dreiecken.
 * Herausgelöst aus `smplmodell.js` (25.09.2026, die Datei stand bei 290
 * Zeilen und bekam die Details dazu).
 */
export class Smplnetz {

    /** Hautfarbe des Referenzkörpers (wie `SmplModell.FARBE`). */
    static FARBE = 0x9a9a9a;

    /**
     * `uv`/`uvDreiecke`/`uvUrsprung` kommen nur bei SMPL-X-Körpern mit
     * gefundener UV-Datei (`Smplxuv` im Server) — sonst wird wie bisher das
     * UNGETEILTE Netz ohne UV gebaut (GarmentCodes eigene Referenzkörper).
     */
    static bauen(punkte, dreiecke, uv, uvDreiecke, uvUrsprung) {
        let lage, index, uvFeld = null;
        if (uv && uvDreiecke && uvUrsprung) {
            const n = uvUrsprung.length;
            lage = new Float32Array(n * 3);
            uvFeld = new Float32Array(n * 2);
            for (let j = 0; j < n; j++) {
                const quelle = uvUrsprung[j];
                lage[j * 3] = punkte[quelle][0];
                lage[j * 3 + 1] = punkte[quelle][1];
                lage[j * 3 + 2] = punkte[quelle][2];
                uvFeld[j * 2] = uv[j][0];
                uvFeld[j * 2 + 1] = uv[j][1];
            }
            index = new Uint32Array(uvDreiecke.length * 3);
            for (let i = 0; i < uvDreiecke.length; i++) {
                index[i * 3] = uvDreiecke[i][0];
                index[i * 3 + 1] = uvDreiecke[i][1];
                index[i * 3 + 2] = uvDreiecke[i][2];
            }
        } else {
            lage = new Float32Array(punkte.length * 3);
            for (let i = 0; i < punkte.length; i++) {
                lage[i * 3] = punkte[i][0];
                lage[i * 3 + 1] = punkte[i][1];
                lage[i * 3 + 2] = punkte[i][2];
            }
            index = new Uint32Array(dreiecke.length * 3);
            for (let i = 0; i < dreiecke.length; i++) {
                index[i * 3] = dreiecke[i][0];
                index[i * 3 + 1] = dreiecke[i][1];
                index[i * 3 + 2] = dreiecke[i][2];
            }
        }
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geometrie.setIndex(new THREE.BufferAttribute(index, 1));
        if (uvFeld) geometrie.setAttribute('uv', new THREE.BufferAttribute(uvFeld, 2));
        geometrie.computeVertexNormals();
        // MeshPhysicalMaterial statt Standard — trägt den Klarlack-Anteil für
        // „Glanz" (`hautAnwenden`), wie bei den Genesis-Stücken (`Stueckstoff`).
        return new THREE.Mesh(geometrie, new THREE.MeshPhysicalMaterial({
            color: Smplnetz.FARBE, roughness: 0.7, metalness: 0.0, clearcoat: 0.0,
        }));
    }
}
