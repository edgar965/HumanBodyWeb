/**
 * Mesh3dailinienflaeche — das Mesh eines Testjobs in der A-Pose unter den Messlinien (27.10.2026, Edgar: „Was sollen diese Punkte? Wo sind die Einstellungen, dass ich auch die Textur sehe
 * und so weiter, sowie bei der Anzeige oben?“). Server `Mesh3dailinienflaeche` (Netz der Kette im Raum der Linien, auf 3 mm zusammengefasst, Farbe je Punkt).
 * Die Ansichtsarten sind die der Zeilen oben (`Mesh3daimaterial.MODI`); „Textur“ zeigt hier die Farbe je Punkt des Meshs. Das Mesh ist halb durchsichtig (`DECKKRAFT`), damit die
 * Linien und Figurpunkte innerhalb des Meshs zu sehen bleiben.
 */
import * as THREE from 'three';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daimaterial } from './mesh3daimaterial.js';
import { Mesh3dailinienzeichner as LZ } from './mesh3dailinienzeichner.js';

export class Mesh3dailinienflaeche {
    static DECKKRAFT = 0.6;
    static FARBE = 0xc9c2b8;

    /** Paket → {kopf, geo} (Geometrie mit Farbe je Punkt, geteilt über alle Felder). */
    static async laden(adresse) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw new Error(antwort.status === 404 ? 'Kein Mesh in der A-Pose für diesen Test' : `HTTP ${antwort.status}`);
        const { kopf, daten } = LZ.paket(await antwort.arrayBuffer());
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(daten.punkte, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(daten.farbe, 3, true));
        geo.setIndex(new THREE.BufferAttribute(daten.dreiecke, 1));
        geo.computeVertexNormals();
        geo.userData.gemeinsam = true;
        return { kopf, geo };
    }

    /** Objekt in der gewählten Ansichtsart; Materialien geteilt (`Mesh3daigemeinsam`). */
    static objekt(geo, modus) {
        const z = Mesh3dailinienflaeche;
        if (modus === 'textur') {
            return new THREE.Mesh(geo, Mesh3daigemeinsam.material(`linienflaeche:textur:${z.DECKKRAFT}`,
                () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85, transparent: true, opacity: z.DECKKRAFT })));
        }
        if (modus === 'punkte') {
            return new THREE.Points(geo, Mesh3daigemeinsam.material('linienflaeche:punkte', () => new THREE.PointsMaterial({ vertexColors: true, size: 0.003, sizeAttenuation: true })));
        }
        return Mesh3daimaterial.netz(geo, { modus, sollfarbe: z.FARBE, deckkraft: modus === 'drahtnetz' || modus === 'roentgen' ? 1 : z.DECKKRAFT });
    }
}
