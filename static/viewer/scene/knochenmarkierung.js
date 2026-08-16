/**
 * Knochen im Koerpernetz hervorheben.
 *
 * Aus interaction.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { state } from './state.js';


// =========================================================================
// Bone selection helpers
// =========================================================================
export function _getBoneFromIntersection(intersection, bodyMesh) {
    if (!bodyMesh || !bodyMesh.userData.boneVertexRanges) return null;
    const vertIdx = intersection.face.a;
    const ranges = bodyMesh.userData.boneVertexRanges;
    for (const [boneName, range] of Object.entries(ranges)) {
        if (vertIdx >= range.start && vertIdx < range.start + range.count) return boneName;
    }
    return null;
}

export function _getOrCreateBoneHighlightGeo(bodyMesh, boneName) {
    if (state._boneHighlightCache.has(boneName)) return state._boneHighlightCache.get(boneName);
    const geo = bodyMesh.geometry;
    const ranges = bodyMesh.userData.boneVertexRanges;
    if (!ranges || !ranges[boneName]) return null;
    const { start, count } = ranges[boneName];
    const end = start + count;
    const indexArr = geo.index.array;
    const newIndices = [];
    for (let i = 0; i < indexArr.length; i += 3) {
        const a = indexArr[i], b = indexArr[i + 1], c = indexArr[i + 2];
        if (a >= start && a < end && b >= start && b < end && c >= start && c < end) {
            newIndices.push(a - start, b - start, c - start);
        }
    }
    if (newIndices.length === 0) return null;
    const posArr = geo.attributes.position.array;
    const subGeo = new THREE.BufferGeometry();
    subGeo.setAttribute('position', new THREE.Float32BufferAttribute(posArr.slice(start * 3, end * 3), 3));
    subGeo.setIndex(newIndices);
    subGeo.computeVertexNormals();
    if (geo.attributes.skinIndex && geo.attributes.skinWeight) {
        subGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(geo.attributes.skinIndex.array.slice(start * 4, end * 4), 4));
        subGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(geo.attributes.skinWeight.array.slice(start * 4, end * 4), 4));
    }
    state._boneHighlightCache.set(boneName, subGeo);
    return subGeo;
}

export function _createBoneOverlay(bodyMesh, boneName, material) {
    const subGeo = _getOrCreateBoneHighlightGeo(bodyMesh, boneName);
    if (!subGeo) return null;
    let overlay;
    if (bodyMesh.isSkinnedMesh && subGeo.attributes.skinIndex) {
        overlay = new THREE.SkinnedMesh(subGeo, material);
        overlay.bind(bodyMesh.skeleton, bodyMesh.bindMatrix);
    } else {
        overlay = new THREE.Mesh(subGeo, material);
    }
    overlay.renderOrder = 1;
    overlay.raycast = function() {};
    overlay.userData._boneOverlay = true;
    if (bodyMesh.parent) bodyMesh.parent.add(overlay);
    return overlay;
}

export function _removeBoneOverlay(overlay) {
    if (overlay && overlay.parent) overlay.parent.remove(overlay);
}

export function _clearBoneHover() {
    if (state._boneHoverOverlay) { _removeBoneOverlay(state._boneHoverOverlay); state._boneHoverOverlay = null; }
    state._hoveredBoneName = null;
}

export function _clearBoneSelection() {
    if (state._boneSelectOverlay) { _removeBoneOverlay(state._boneSelectOverlay); state._boneSelectOverlay = null; }
    state._selectedBoneName = null;
}

export function _clearBoneHighlightCache() {
    for (const geo of state._boneHighlightCache.values()) geo.dispose();
    state._boneHighlightCache.clear();
    _clearBoneHover();
    _clearBoneSelection();
}
