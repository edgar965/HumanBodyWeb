/**
 * Formenbauer — die Geometrien, aus denen ein Modellteil entsteht.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026): Tutu, Rock,
 * Helixband, Ebene, Rhombus, das Verschmelzen zweier Geometrien und der
 * Texturspeicher. Rund 330 Zeilen reine Three.js-Geometrie, die zwischen den
 * Modellgeneratoren standen.
 */

import * as THREE from 'three';


/** Merge two indexed BufferGeometries into one, then dispose both inputs. */
export function _mergeSimpleGeos(a, b) {
    const pA = a.attributes.position.array, pB = b.attributes.position.array;
    const nA = a.attributes.normal.array,   nB = b.attributes.normal.array;
    const pos = new Float32Array(pA.length + pB.length);
    pos.set(pA); pos.set(pB, pA.length);
    const nor = new Float32Array(nA.length + nB.length);
    nor.set(nA); nor.set(nB, nA.length);

    const iA = a.index ? a.index.array : null;
    const iB = b.index ? b.index.array : null;
    const vertCountA = a.attributes.position.count;
    const lenA = iA ? iA.length : vertCountA;
    const lenB = iB ? iB.length : b.attributes.position.count;
    const idx = new Uint32Array(lenA + lenB);
    for (let i = 0; i < lenA; i++) idx[i] = iA ? iA[i] : i;
    for (let i = 0; i < lenB; i++) idx[lenA + i] = (iB ? iB[i] : i) + vertCountA;

    a.dispose(); b.dispose();

    const merged = new THREE.BufferGeometry();
    merged.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    merged.setAttribute('normal',   new THREE.BufferAttribute(nor, 3));
    merged.setIndex(new THREE.BufferAttribute(idx, 1));
    return merged;
}




/**
 * Build a flat plane (card-like quad). Lies in local XY (height along Y = bone axis),
 * faces +Z. Built-in UVs (0,0..1,1) map the texture across the full plane.
 * Optionally double-sided so the back face is visible too.
 */
export function _buildPlane(part) {
    const w = part.planeWidth ?? 0.15;
    const h = part.planeHeight ?? 0.22;
    const geo = new THREE.PlaneGeometry(w, h);
    if (part.planeDoubleSided !== false) return _makeDoubleSided(geo);
    return geo;
}

/**
 * Build a frustum / rhombus: a 3D shape with top (Y=+H/2) and bottom (Y=-H/2)
 * rectangles whose width × depth can differ. Different sizes give angled side
 * walls. Each of the 6 faces gets full UV (0..1) mapping for textures.
 *
 * Local coords: bone direction = +Y, so height stretches along the bone.
 */
export function _buildRhombus(part) {
    const tw = (part.rhombusTopWidth ?? 0.10) * 0.5;
    const td = (part.rhombusTopDepth ?? 0.10) * 0.5;
    const bw = (part.rhombusBotWidth ?? 0.20) * 0.5;
    const bd = (part.rhombusBotDepth ?? 0.20) * 0.5;
    const h  = (part.rhombusHeight   ?? 0.20) * 0.5;

    // 8 corners (top T0..T3, bottom B0..B3)
    const T0 = [-tw, +h, -td], T1 = [+tw, +h, -td], T2 = [+tw, +h, +td], T3 = [-tw, +h, +td];
    const B0 = [-bw, -h, -bd], B1 = [+bw, -h, -bd], B2 = [+bw, -h, +bd], B3 = [-bw, -h, +bd];

    // Build 6 quads with their own vertices, so each face gets its own UVs.
    // Each face: 4 verts + 4 UVs + 6 indices (two triangles).
    const faces = [
        // [v0, v1, v2, v3] CCW outwards
        [T0, T1, T2, T3], // top    (+Y up)
        [B3, B2, B1, B0], // bottom (-Y down, wound opposite to face outwards)
        [B0, B1, T1, T0], // front  (-Z)
        [B2, B3, T3, T2], // back   (+Z)
        [B3, B0, T0, T3], // left   (-X)
        [B1, B2, T2, T1], // right  (+X)
    ];
    const uvs2D = [[0, 0], [1, 0], [1, 1], [0, 1]];

    const pos = new Float32Array(faces.length * 4 * 3);
    const uv  = new Float32Array(faces.length * 4 * 2);
    const idx = new Uint32Array(faces.length * 6);
    let pi = 0, ui = 0, ii = 0, vBase = 0;
    for (const f of faces) {
        for (let k = 0; k < 4; k++) {
            pos[pi++] = f[k][0]; pos[pi++] = f[k][1]; pos[pi++] = f[k][2];
            uv[ui++]  = uvs2D[k][0]; uv[ui++] = uvs2D[k][1];
        }
        idx[ii++] = vBase; idx[ii++] = vBase + 1; idx[ii++] = vBase + 2;
        idx[ii++] = vBase; idx[ii++] = vBase + 2; idx[ii++] = vBase + 3;
        vBase += 4;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.computeVertexNormals();
    return geo;
}

/**
 * Cache of THREE.Texture instances keyed by data-URL / source string,
 * so the same texture isn't re-uploaded to the GPU per frame regen.
 */
export const _bonePartTextureCache = new Map();

export function _getOrLoadTexture(src) {
    if (!src) return null;
    let tex = _bonePartTextureCache.get(src);
    if (tex) return tex;
    tex = new THREE.TextureLoader().load(src);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.wrapS = THREE.ClampToEdgeWrapping;
    tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.minFilter = THREE.LinearMipmapLinearFilter;
    tex.magFilter = THREE.LinearFilter;
    _bonePartTextureCache.set(src, tex);
    return tex;
}

/** Make a geometry double-sided by duplicating verts with flipped normals and reversed faces. */
export function _makeDoubleSided(geo) {
    const pos = geo.attributes.position.array;
    const nrm = geo.attributes.normal.array;
    const idx = geo.index ? geo.index.array : null;
    if (!idx) return geo; // non-indexed not supported
    const vCount = pos.length / 3;
    const fCount = idx.length;
    // Double verts: original + copy with flipped normals
    const newPos = new Float32Array(pos.length * 2);
    const newNrm = new Float32Array(nrm.length * 2);
    newPos.set(pos); newPos.set(pos, pos.length);
    newNrm.set(nrm);
    for (let i = 0; i < nrm.length; i++) newNrm[nrm.length + i] = -nrm[i];
    // Double indices: original + reversed winding for back faces
    const newIdx = new Uint32Array(fCount * 2);
    newIdx.set(idx);
    for (let i = 0; i < fCount; i += 3) {
        newIdx[fCount + i]     = idx[i + 2] + vCount;
        newIdx[fCount + i + 1] = idx[i + 1] + vCount;
        newIdx[fCount + i + 2] = idx[i]     + vCount;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(newPos, 3));
    g.setAttribute('normal', new THREE.BufferAttribute(newNrm, 3));
    // Preserve UVs (required for textured shapes like the plane "card").
    if (geo.attributes.uv) {
        const uv = geo.attributes.uv.array;
        const newUv = new Float32Array(uv.length * 2);
        newUv.set(uv); newUv.set(uv, uv.length);
        g.setAttribute('uv', new THREE.BufferAttribute(newUv, 2));
    }
    g.setIndex(new THREE.BufferAttribute(newIdx, 1));
    geo.dispose();
    return g;
}
