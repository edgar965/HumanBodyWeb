/**
 * Fotogenesisanpassungsaugen — die Augäpfel der eingepassten Genesis-Figur in Zeile 1 der Jobseite (19.11.2026, Edgar: „bau Augen in Zeile 1 ein“).
 *
 * Netz und Lage rechnet der Server (`Meshgenesisanpassungsaugen`: je Augapfel starr an die Körperpunkte um das Auge gesetzt), hier nur Geometrie und
 * Material: Blöcke `augen_punkte`, `augen_uv`, `augen_dreiecke`, im Kopf `augen` = je Gruppe Indexbereich und Albedo (Pfad der Daz-Bibliothek, geladen wie die
 * Haut der Figur über `Genesis9texturen`). Ohne die Blöcke (ältere Server, keine Daz-Bibliothek) null.
 */
import * as THREE from 'three';
import { Genesis9texturen } from '../gemeinsam/genesis9texturen.js';

export class Fotogenesisanpassungsaugen {
    /** → {geometrie, materialien} oder null; `neu()` ruft, sobald ein Bild da ist. */
    static bauen(daten, gruppen, neu) {
        if (!daten.augen_punkte || !daten.augen_uv || !daten.augen_dreiecke || !gruppen?.length) return null;
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(daten.augen_punkte, 3));
        g.setAttribute('uv', new THREE.BufferAttribute(daten.augen_uv, 2));
        g.setIndex(new THREE.BufferAttribute(daten.augen_dreiecke, 1));
        g.computeVertexNormals();
        g.userData.gemeinsam = true;            // gehört der Figur, nicht dem Feld (`Meshgenesisansicht._leeren`)
        const materialien = gruppen.map((gruppe, i) => {
            g.addGroup(gruppe.index_ab, gruppe.index_anzahl, i);
            const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.25 });
            m.userData.gemeinsam = true;
            if (gruppe.albedo) {
                Genesis9texturen.holen(gruppe.albedo, true, m, t => {
                    m.map = t;
                    neu?.();
                });
            }
            return m;
        });
        return { geometrie: g, materialien };
    }
}
