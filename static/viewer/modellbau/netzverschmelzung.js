/**
 * Netzverschmelzung — Geometriestuecke nach Material gruppieren und zu einem
 * einzigen BufferGeometry zusammenfuegen.
 *
 * Aus modellnetz.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { _getOrLoadTexture } from './formenbauer.js';
import './knochenmatrizen.js';
import './knochengruppen.js';

export class Netzverschmelzung {
    /** @returns {{geometry, materials, boneVertexRanges}} */
    static zusammenfuegen(geoChunks) {
        // Group by (color + texture) so each unique material is one group.
        const matGroups = new Map(); // groupKey -> { color, texture, indices: [chunkIndices] }
        geoChunks.forEach((chunk, i) => {
            const key = chunk.texture ? `tex:${chunk.texture}` : `col:${chunk.color}`;
            let g = matGroups.get(key);
            if (!g) { g = { color: chunk.color, texture: chunk.texture, indices: [] }; matGroups.set(key, g); }
            g.indices.push(i);
        });
        
        // Merge all geometries, tracking material group ranges
        let totalVerts = 0;
        let totalIndices = 0;
        let needsUV = false;
        for (const chunk of geoChunks) {
            totalVerts += chunk.geometry.attributes.position.count;
            totalIndices += chunk.geometry.index ? chunk.geometry.index.count : chunk.geometry.attributes.position.count;
            if (chunk.geometry.attributes.uv || chunk.texture) needsUV = true;
        }
        
        const mergedPositions = new Float32Array(totalVerts * 3);
        const mergedNormals   = new Float32Array(totalVerts * 3);
        const mergedSkinIndices = new Float32Array(totalVerts * 4);
        const mergedSkinWeights = new Float32Array(totalVerts * 4);
        const mergedUVs = needsUV ? new Float32Array(totalVerts * 2) : null;
        const mergedIndices = [];
        
        const materials = [];
        const groups = [];
        
        let vertOffset = 0;
        let indexOffset = 0;
        const boneVertexRanges = {};  // boneName -> { start, count }
        
        // Process chunks grouped by material (color + optional texture)
        for (const [, grp] of matGroups) {
            const groupStart = indexOffset;
        
            for (const ci of grp.indices) {
                const chunk = geoChunks[ci];
                const geo = chunk.geometry;
                const posArr = geo.attributes.position.array;
                const normArr = geo.attributes.normal.array;
                const uvArr   = geo.attributes.uv ? geo.attributes.uv.array : null;
                const vCount = geo.attributes.position.count;
        
                if (chunk.boneName) boneVertexRanges[chunk.boneName] = { start: vertOffset, count: vCount };
        
                mergedPositions.set(posArr, vertOffset * 3);
                mergedNormals.set(normArr, vertOffset * 3);
                if (mergedUVs) {
                    if (uvArr) mergedUVs.set(uvArr, vertOffset * 2);
                    // chunks without UVs get the default zero-fill (0, 0)
                }
        
                for (let v = 0; v < vCount; v++) {
                    const base = (vertOffset + v) * 4;
                    mergedSkinIndices[base]     = chunk.boneIndex;
                    mergedSkinIndices[base + 1] = 0;
                    mergedSkinIndices[base + 2] = 0;
                    mergedSkinIndices[base + 3] = 0;
                    mergedSkinWeights[base]     = 1;
                    mergedSkinWeights[base + 1] = 0;
                    mergedSkinWeights[base + 2] = 0;
                    mergedSkinWeights[base + 3] = 0;
                }
        
                if (geo.index) {
                    const idxArr = geo.index.array;
                    for (let i = 0; i < idxArr.length; i++) mergedIndices.push(idxArr[i] + vertOffset);
                    indexOffset += idxArr.length;
                } else {
                    for (let i = 0; i < vCount; i++) mergedIndices.push(vertOffset + i);
                    indexOffset += vCount;
                }
        
                vertOffset += vCount;
                geo.dispose();
            }
        
            const groupCount = indexOffset - groupStart;
            groups.push({ start: groupStart, count: groupCount, materialIndex: materials.length });
        
            const matOpts = {
                color: new THREE.Color(grp.color),
                roughness: 0.6,
                metalness: 0.2,
                flatShading: false,
            };
            if (grp.texture) {
                matOpts.map = _getOrLoadTexture(grp.texture);
                // Tint stays neutral so the texture's true colors show through.
                matOpts.color = new THREE.Color(0xffffff);
            }
            materials.push(new THREE.MeshStandardMaterial(matOpts));
        }
        
        // Build merged BufferGeometry
        const mergedGeo = new THREE.BufferGeometry();
        mergedGeo.setAttribute('position', new THREE.Float32BufferAttribute(mergedPositions, 3));
        mergedGeo.setAttribute('normal', new THREE.Float32BufferAttribute(mergedNormals, 3));
        if (mergedUVs) mergedGeo.setAttribute('uv', new THREE.Float32BufferAttribute(mergedUVs, 2));
        mergedGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(mergedSkinIndices, 4));
        mergedGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(mergedSkinWeights, 4));
        mergedGeo.setIndex(mergedIndices);
        
        for (const g of groups) {
            mergedGeo.addGroup(g.start, g.count, g.materialIndex);
        }
        
        return { geometry: mergedGeo, materials, boneVertexRanges,
                 mergedSkinIndices, mergedSkinWeights };
    }
}
