/**
 * Netzverschmelzung — Geometriestuecke nach Material gruppieren und zu einem
 * einzigen BufferGeometry zusammenfuegen.
 *
 * Aus modellnetz.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `zusammenfuegen()` hatte 113
 * Zeilen. Die Gruppierung nach Material steht jetzt in `Materialgruppen`, die
 * Zielfelder in `Netzpuffer` — hier bleibt nur die Reihenfolge.
 */

import './knochenmatrizen.js';
import './knochengruppen.js';
import { Materialgruppen } from './materialgruppen.js';
import { Netzpuffer } from './netzpuffer.js';

export class Netzverschmelzung {
    /**
     * @param {Array} geoChunks Stücke mit `geometry`, `color`/`texture`,
     *     `boneName`, `boneIndex`
     * @returns {{geometry, materials, boneVertexRanges, mergedSkinIndices,
     *            mergedSkinWeights}}
     */
    static zusammenfuegen(geoChunks) {
        const gruppen = Materialgruppen.von(geoChunks);
        const puffer = Netzpuffer.vorbereiten(geoChunks);
        const materials = [];
        const zeichengruppen = [];

        for (const gruppe of gruppen) {
            const beginn = puffer.indexstelle;
            for (const i of gruppe.indices) puffer.anfuegen(geoChunks[i]);
            zeichengruppen.push({ start: beginn,
                                  count: puffer.indexstelle - beginn,
                                  materialIndex: materials.length });
            materials.push(Materialgruppen.material(gruppe));
        }

        return { geometry: puffer.geometrie(zeichengruppen),
                 materials,
                 boneVertexRanges: puffer.knochenbereiche,
                 mergedSkinIndices: puffer.knochenIndex,
                 mergedSkinWeights: puffer.knochenGewicht };
    }
}
