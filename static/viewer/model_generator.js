/**
 * Model Generator — Generate geometric models around skeleton bones.
 * Supports Rigify Skeleton (SkinnedMesh) and Rig Bones (static Mesh).
 */
import * as THREE from 'three';

// =========================================================================
// Helpers
// =========================================================================

/** Merge two indexed BufferGeometries into one, then dispose both inputs. */
function _mergeSimpleGeos(a, b) {
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
 * Build a spiral-tutu: multiple tutu discs spiraling downward.
 * Each disc is a flat ring with drooping outer edge, positioned along a helix.
 */
function _buildSpiralTutu(part, radius) {
    const winds     = part.spiralWinds ?? 3;
    const startR    = part.spiralStartR ?? radius * 0.5;
    const endR      = part.spiralEndR ?? radius;
    const posTop    = part.spiralPosTop ?? 0.05;
    const posBottom = part.spiralPosBottom ?? -0.15;
    const thickness = part.tutuThickness ?? 0.008;
    const droop     = part.tutuDroop ?? 0.02;
    const droopFrac = part.tutuDroopStart ?? 0.7;
    const radSegs   = 48; // segments around each disc
    const totalHeight = posTop - posBottom;
    // Steps: each wind gets its own disc
    const steps = Math.max(1, Math.round(winds));
    const geos = [];
    for (let i = 0; i < steps; i++) {
        const t = steps === 1 ? 0.5 : i / (steps - 1); // 0..1
        const y = posTop - t * totalHeight;
        const r = startR + t * (endR - startR);
        const angle = t * winds * Math.PI * 2; // spiral rotation
        const innerR = r * 0.08;
        const halfT = thickness * 0.5;
        const droopR = r * droopFrac;
        const pts = [
            new THREE.Vector2(innerR, halfT),
            new THREE.Vector2(droopR, halfT),
            new THREE.Vector2(r, -droop),
            new THREE.Vector2(r - 0.002, -droop - halfT),
            new THREE.Vector2(droopR, -halfT),
            new THREE.Vector2(innerR, -halfT),
        ];
        let disc = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
        // Rotate disc around Y by spiral angle, then translate to height
        const mat = new THREE.Matrix4().makeRotationY(angle);
        mat.setPosition(0, y, 0);
        disc.applyMatrix4(mat);
        geos.push(disc);
    }
    // Merge all discs
    let merged = geos[0];
    for (let i = 1; i < geos.length; i++) {
        merged = _mergeSimpleGeos(merged, geos[i]);
    }

    // Optional inner skirt (hollow cone connecting top to bottom)
    if (part.spiralSkirt) {
        const skirtThick = thickness;
        const topInnerR  = startR * 0.08;  // match tutu inner hole
        const botInnerR  = endR * 0.08;
        const radSegsSkirt = 48;
        const pts = [
            new THREE.Vector2(topInnerR + skirtThick, posTop),
            new THREE.Vector2(botInnerR + skirtThick, posBottom),
            new THREE.Vector2(botInnerR, posBottom),
            new THREE.Vector2(topInnerR, posTop),
        ];
        const skirtGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegsSkirt));
        merged = _mergeSimpleGeos(merged, skirtGeo);
    }

    return merged;
}

/**
 * Build a skirt (Rock): hollow cone/cylinder with configurable top/bottom radii and thickness.
 */
function _buildSkirt(part, radius) {
    const radiusTop    = part.skirtRadiusTop ?? radius * 0.3;
    const radiusBottom = part.skirtRadiusBottom ?? radius;
    const posTop       = part.skirtPosTop ?? 0.02;
    const posBottom    = part.skirtPosBottom ?? -0.15;
    const thickness    = part.skirtThickness ?? 0.005;
    const radSegs      = 48;
    const height = posTop - posBottom;
    if (height < 0.001) return new THREE.BufferGeometry();
    // Profile: outer top → outer bottom → inner bottom → inner top (closed loop)
    const pts = [
        new THREE.Vector2(radiusTop, posTop),                           // outer top
        new THREE.Vector2(radiusBottom, posBottom),                     // outer bottom
        new THREE.Vector2(radiusBottom - thickness, posBottom),         // inner bottom
        new THREE.Vector2(Math.max(0.001, radiusTop - thickness), posTop), // inner top
    ];
    const geo = new THREE.LatheGeometry(pts, radSegs);
    return _makeDoubleSided(geo);
}

/**
 * Build a helix ribbon: a continuous band spiraling downward like a corkscrew.
 * The ribbon has width (inner to outer edge) and the outer edge can droop.
 */
function _buildHelixRibbon(part, radius) {
    const winds      = part.spiralWinds ?? 3;
    const startR     = part.spiralStartR ?? radius * 0.5;
    const endR       = part.spiralEndR ?? radius;
    const posTop     = part.spiralPosTop ?? 0.05;
    const posBottom  = part.spiralPosBottom ?? -0.15;
    const ribbonW    = part.ribbonWidth ?? 0.04;   // width of the ribbon band
    const thickness  = part.tutuThickness ?? 0.005;
    const droop      = part.tutuDroop ?? 0.015;    // outer edge hangs down
    const totalAngle = winds * Math.PI * 2;
    const totalH     = posTop - posBottom;
    const steps      = Math.max(48, Math.round(winds * 64)); // smooth helix

    // 4 verts per step: outer-top, inner-top, inner-bottom, outer-bottom
    const vertCount  = (steps + 1) * 4;
    const faceCount  = steps * 4 * 2; // 4 quads per step, 2 tris each
    const pos = new Float32Array(vertCount * 3);
    const idx = new Uint32Array(faceCount * 3);

    for (let i = 0; i <= steps; i++) {
        const t = i / steps; // 0..1
        const angle = t * totalAngle;
        const y = posTop - t * totalH;
        const r = startR + t * (endR - startR);
        const cosA = Math.cos(angle), sinA = Math.sin(angle);

        const rInner = Math.max(0.002, r - ribbonW * 0.5);
        const rOuter = r + ribbonW * 0.5;
        const halfT = thickness * 0.5;

        const base = i * 4 * 3;
        // 0: outer top
        pos[base]     = rOuter * cosA;
        pos[base + 1] = y - droop + halfT;
        pos[base + 2] = rOuter * sinA;
        // 1: inner top
        pos[base + 3] = rInner * cosA;
        pos[base + 4] = y + halfT;
        pos[base + 5] = rInner * sinA;
        // 2: inner bottom
        pos[base + 6] = rInner * cosA;
        pos[base + 7] = y - halfT;
        pos[base + 8] = rInner * sinA;
        // 3: outer bottom
        pos[base + 9]  = rOuter * cosA;
        pos[base + 10] = y - droop - halfT;
        pos[base + 11] = rOuter * sinA;
    }

    // Build faces: connect step i to step i+1
    let fi = 0;
    for (let i = 0; i < steps; i++) {
        const a = i * 4, b = (i + 1) * 4;
        // Top face (outer-top → inner-top)
        idx[fi++] = a;     idx[fi++] = b;     idx[fi++] = b + 1;
        idx[fi++] = a;     idx[fi++] = b + 1; idx[fi++] = a + 1;
        // Bottom face (inner-bottom → outer-bottom)
        idx[fi++] = a + 2; idx[fi++] = b + 2; idx[fi++] = b + 3;
        idx[fi++] = a + 2; idx[fi++] = b + 3; idx[fi++] = a + 3;
        // Outer edge (outer-top → outer-bottom)
        idx[fi++] = a;     idx[fi++] = a + 3; idx[fi++] = b + 3;
        idx[fi++] = a;     idx[fi++] = b + 3; idx[fi++] = b;
        // Inner edge (inner-top → inner-bottom)
        idx[fi++] = a + 1; idx[fi++] = b + 1; idx[fi++] = b + 2;
        idx[fi++] = a + 1; idx[fi++] = b + 2; idx[fi++] = a + 2;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.computeVertexNormals();
    let result = _makeDoubleSided(geo);

    // Optional inner skirt
    if (part.spiralSkirt) {
        const skirtThick = thickness;
        const topInnerR  = Math.max(0.003, startR - ribbonW * 0.5);
        const botInnerR  = Math.max(0.003, endR - ribbonW * 0.5);
        const pts = [
            new THREE.Vector2(topInnerR + skirtThick, posTop),
            new THREE.Vector2(botInnerR + skirtThick, posBottom),
            new THREE.Vector2(botInnerR, posBottom),
            new THREE.Vector2(topInnerR, posTop),
        ];
        const skirtGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, 48));
        result = _mergeSimpleGeos(result, skirtGeo);
    }

    return result;
}

/** Make a geometry double-sided by duplicating verts with flipped normals and reversed faces. */
function _makeDoubleSided(geo) {
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
    g.setIndex(new THREE.BufferAttribute(newIdx, 1));
    geo.dispose();
    return g;
}

// =========================================================================
// Bone Classification
// =========================================================================

/** Main body bones — visible by default (~25 bones) */
export const BODY_BONES = [
    'DEF-spine',    'DEF-spine.001', 'DEF-spine.002', 'DEF-spine.003',
    'DEF-spine.004', 'DEF-spine.005', 'DEF-spine.006',
    'DEF-thigh.L',   'DEF-thigh.L.001',
    'DEF-thigh.R',   'DEF-thigh.R.001',
    'DEF-shin.L',    'DEF-shin.L.001',
    'DEF-shin.R',    'DEF-shin.R.001',
    'DEF-foot.L',    'DEF-foot.R',
    'DEF-shoulder.L', 'DEF-shoulder.R',
    'DEF-upper_arm.L', 'DEF-upper_arm.L.001',
    'DEF-upper_arm.R', 'DEF-upper_arm.R.001',
    'DEF-forearm.L',  'DEF-forearm.L.001',
    'DEF-forearm.R',  'DEF-forearm.R.001',
    'DEF-hand.L',     'DEF-hand.R',
];

/** Finger bones — hidden by default */
export const FINGER_BONES = [];
const FINGER_NAMES = ['thumb', 'f_index', 'f_middle', 'f_ring', 'f_pinky'];
const FINGER_SEGS  = ['.01', '.02', '.03'];
for (const fn of FINGER_NAMES) {
    for (const seg of FINGER_SEGS) {
        FINGER_BONES.push(`DEF-${fn}${seg}.L`);
        FINGER_BONES.push(`DEF-${fn}${seg}.R`);
    }
}

/** Face bones — hidden by default */
export const FACE_BONES = [];
// Will be populated dynamically from skeleton data (any DEF- bone not in BODY or FINGER)

/** Bones that should never be shown (mechanism bones) */
const NEVER_SHOW_PREFIXES = ['MCH-', 'ORG-'];

/** Leaf bones with fixed display length (meters) */
const LEAF_LENGTHS = {
    'DEF-hand.L': 0.05, 'DEF-hand.R': 0.05,
    'DEF-toe.L': 0.03, 'DEF-toe.R': 0.03,
    'DEF-foot.L': 0.06, 'DEF-foot.R': 0.06,
};

// =========================================================================
// Bone Classification Helper
// =========================================================================

const _bodySet = new Set(BODY_BONES);
const _fingerSet = new Set(FINGER_BONES);

/**
 * Classify all DEF- bones from skeleton data into categories.
 * Returns { body: string[], finger: string[], face: string[] }
 */
export function classifyBones(skelData) {
    const body = [];
    const finger = [];
    const face = [];

    for (const b of skelData.bones) {
        const name = b.name;
        // Skip non-DEF bones
        if (NEVER_SHOW_PREFIXES.some(p => name.startsWith(p))) continue;
        if (!name.startsWith('DEF-')) continue;

        if (_bodySet.has(name)) {
            body.push(name);
        } else if (_fingerSet.has(name)) {
            finger.push(name);
        } else {
            face.push(name);
        }
    }
    return { body, finger, face };
}

// =========================================================================
// Default Config
// =========================================================================

/**
 * Build default model configuration from skeleton data.
 * Auto-computes radius as bone_length × 0.2, clamped [0.01, 0.05].
 */
export function getDefaultModelConfig(skelData, swData) {
    const classified = classifyBones(skelData);
    const worldTransforms = computeBoneWorldTransforms(skelData, swData);

    const boneParts = {};
    const defaultColor = '#4488cc';
    const defaultRadius = 0.03;

    const allVisible = [...classified.body];
    const allHidden  = [...classified.finger, ...classified.face];

    for (const name of allVisible) {
        const wt = worldTransforms.get(name);
        const len = wt ? wt.length : 0.1;
        const autoRadius = Math.min(0.05, Math.max(0.01, len * 0.2));
        boneParts[name] = {
            shape: 'cylinder',
            radius: parseFloat(autoRadius.toFixed(4)),
            color: defaultColor,
            visible: true,
        };
    }
    for (const name of allHidden) {
        const wt = worldTransforms.get(name);
        const len = wt ? wt.length : 0.05;
        const autoRadius = Math.min(0.05, Math.max(0.01, len * 0.2));
        boneParts[name] = {
            shape: 'cylinder',
            radius: parseFloat(autoRadius.toFixed(4)),
            color: defaultColor,
            visible: false,
        };
    }

    return {
        type: 'generated_model',
        version: 1,
        name: 'Neues Modell',
        bone_parts: boneParts,
        default_color: defaultColor,
        default_radius: defaultRadius,
        segments: 8,
    };
}

// =========================================================================
// World Transforms from Skeleton Data
// =========================================================================

/**
 * Compute world position, quaternion, and bone length for each bone.
 * Uses the parent chain from skelData (Blender coords) and converts to Three.js.
 * Returns Map<boneName, {worldPos: Vector3, worldQuat: Quaternion, length: number}>
 */
export function computeBoneWorldTransforms(skelData, swData) {
    const skelByName = {};
    for (const b of skelData.bones) skelByName[b.name] = b;

    // Build ordered bone list from swData if available, otherwise from skelData
    const boneNames = swData ? swData.bone_names : skelData.bones.map(b => b.name);

    const result = new Map();
    const _worldPos = {};
    const _worldQuat = {};

    // Recursive compute
    function computeWorld(name) {
        if (_worldPos[name]) return;
        const data = skelByName[name];
        if (!data) return;

        // Blender local -> Three.js local
        const lp = data.local_position;
        const localPos = new THREE.Vector3(lp[0], lp[2], -lp[1]);
        const lq = data.local_quaternion;
        const localQuat = new THREE.Quaternion(lq[1], lq[3], -lq[2], lq[0]);

        if (data.parent && skelByName[data.parent]) {
            computeWorld(data.parent);
            const parentPos = _worldPos[data.parent];
            const parentQuat = _worldQuat[data.parent];
            // worldPos = parentPos + parentQuat * localPos
            const rotatedLocal = localPos.clone().applyQuaternion(parentQuat);
            _worldPos[name] = parentPos.clone().add(rotatedLocal);
            _worldQuat[name] = parentQuat.clone().multiply(localQuat);
        } else {
            _worldPos[name] = localPos.clone();
            _worldQuat[name] = localQuat.clone();
        }
    }

    for (const name of boneNames) {
        computeWorld(name);
        const data = skelByName[name];
        if (!data) continue;

        // Bone length = distance from parent to this bone (length of local_position)
        const lp = data.local_position;
        let len = Math.sqrt(lp[0]*lp[0] + lp[1]*lp[1] + lp[2]*lp[2]);

        // For leaf bones or zero-length, use fixed length
        if (len < 0.001) {
            len = LEAF_LENGTHS[name] || 0.03;
        }

        if (_worldPos[name]) {
            result.set(name, {
                worldPos: _worldPos[name],
                worldQuat: _worldQuat[name],
                length: len,
            });
        }
    }

    return result;
}

// =========================================================================
// Mesh Generation
// =========================================================================

/**
 * Generate a merged SkinnedMesh from the model config.
 * Each visible bone gets a geometric shape (cylinder/box/sphere) positioned
 * between parent and bone world positions. All merged into one BufferGeometry.
 *
 * @param {Object} skelData - Raw skeleton data {bones: [{name, local_position, local_quaternion, parent}]}
 * @param {Object} swData   - Skin weight data {bone_names: [...], weights: [...]}
 * @param {Object} config   - Model config {bone_parts, segments, default_color, default_radius}
 * @returns {{ mesh: THREE.SkinnedMesh, skeleton: {skeleton, rootBone, bones, boneByName} }}
 */
export function generateModelMesh(skelData, swData, config) {
    const segments = config.segments || 8;
    const worldTransforms = computeBoneWorldTransforms(skelData, swData);

    // Build bone index map from swData (same order as animation skeleton)
    const boneIndexMap = {};
    for (let i = 0; i < swData.bone_names.length; i++) {
        boneIndexMap[swData.bone_names[i]] = i;
    }

    // Build children map to find each bone's TAIL position
    const childrenMap = {};  // boneName -> [childNames]
    for (const b of skelData.bones) {
        if (b.parent) {
            if (!childrenMap[b.parent]) childrenMap[b.parent] = [];
            childrenMap[b.parent].push(b.name);
        }
    }

    // Collect all geometry pieces
    const geoChunks = [];   // { geometry, boneIndex, color }
    const skelByName = {};
    for (const b of skelData.bones) skelByName[b.name] = b;

    for (const [boneName, part] of Object.entries(config.bone_parts)) {
        if (!part.visible) continue;
        const boneIdx = boneIndexMap[boneName];
        if (boneIdx === undefined) continue;

        const wt = worldTransforms.get(boneName);
        if (!wt) continue;

        const data = skelByName[boneName];
        if (!data) continue;

        const radius = part.radius || config.default_radius || 0.03;
        const color = part.color || config.default_color || '#4488cc';

        // Compute bone HEAD→TAIL using the bone's own direction (local Y axis)
        // and determining length from the continuation child projected onto that direction.
        const headPos = wt.worldPos;
        const boneDir = new THREE.Vector3(0, 1, 0).applyQuaternion(wt.worldQuat);

        let boneLen = 0;
        const children = childrenMap[boneName];
        if (children && children.length > 0) {
            // Find length by projecting children onto bone direction — pick the best match
            for (const childName of children) {
                const childWt = worldTransforms.get(childName);
                if (!childWt) continue;
                const offset = new THREE.Vector3().subVectors(childWt.worldPos, headPos);
                const proj = offset.dot(boneDir);
                if (proj > boneLen) boneLen = proj;
            }
        }
        if (boneLen < 0.001) boneLen = LEAF_LENGTHS[boneName] || 0.03;

        const tailPos = headPos.clone().add(boneDir.clone().multiplyScalar(boneLen));

        // Apply head/tail position offsets in WORLD space
        let effectiveHead = headPos.clone();
        let effectiveTail = tailPos.clone();
        if (part.headOffset) {
            effectiveHead.add(new THREE.Vector3(
                part.headOffset.x || 0, part.headOffset.y || 0, part.headOffset.z || 0
            ));
        }
        if (part.tailOffset) {
            effectiveTail.add(new THREE.Vector3(
                part.tailOffset.x || 0, part.tailOffset.y || 0, part.tailOffset.z || 0
            ));
        }
        // Apply axial scale (stretch/shrink along bone direction)
        if (part.axialScale && part.axialScale !== 1) {
            const mid = effectiveHead.clone().add(effectiveTail).multiplyScalar(0.5);
            const halfDir = effectiveTail.clone().sub(effectiveHead).multiplyScalar(0.5 * part.axialScale);
            effectiveHead = mid.clone().sub(halfDir);
            effectiveTail = mid.clone().add(halfDir);
        }
        const effectiveLen = effectiveHead.distanceTo(effectiveTail);
        if (effectiveLen > 0.001) boneLen = effectiveLen;

        // Create shape geometry (centered at origin, along Y axis)
        let shapeGeo;
        switch (part.shape) {
            case 'box':
                shapeGeo = new THREE.BoxGeometry(radius * 2, boneLen, radius * 2, 1, 1, 1);
                break;
            case 'sphere_low':
                shapeGeo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                break;
            case 'sphere':
                shapeGeo = new THREE.SphereGeometry(radius, 24, 16);
                break;
            case 'cone':
                shapeGeo = new THREE.ConeGeometry(radius, boneLen, segments);
                break;
            case 'capsule':
                shapeGeo = new THREE.CapsuleGeometry(radius, Math.max(0.001, boneLen - radius * 2), segments, Math.max(4, segments >> 1));
                break;
            case 'oval':
                shapeGeo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                shapeGeo.scale(1, boneLen / (radius * 2), 1);
                break;
            case 'double_oval': {
                const ov = part.overlap ?? 0.5;
                const halfLen = boneLen * 0.5;
                const ovalLen = halfLen + halfLen * ov;
                const scY = ovalLen / (radius * 2);
                const sep = halfLen * (1 - ov);
                const hSegs = Math.max(4, segments >> 1);
                const g1 = new THREE.SphereGeometry(radius, segments, hSegs);
                g1.scale(1, scY, 1); g1.translate(0, -sep, 0);
                const g2 = new THREE.SphereGeometry(radius, segments, hSegs);
                g2.scale(1, scY, 1); g2.translate(0, sep, 0);
                shapeGeo = _mergeSimpleGeos(g1, g2);
                break;
            }
            case 'diamond':
                shapeGeo = new THREE.OctahedronGeometry(radius);
                shapeGeo.scale(1, boneLen / (radius * 2), 1);
                break;
            case 'tutu': {
                // Tutu: flat disc with drooping outer rim, built as LatheGeometry
                const thickness = part.tutuThickness ?? 0.01;
                const droop = part.tutuDroop ?? 0.03;
                const droopStart = part.tutuDroopStart ?? 0.7;
                const innerR = radius * 0.08; // small hole in center around bone
                const outerR = radius;
                const halfT = thickness * 0.5;
                const droopR = outerR * droopStart;
                const radSegs = Math.max(16, segments * 4);
                // Profile points (in XY plane, X=radius, Y=height), rotated around Y
                const pts = [
                    new THREE.Vector2(innerR, halfT),    // inner top
                    new THREE.Vector2(droopR, halfT),     // flat top to droop start
                    new THREE.Vector2(outerR, -droop),    // outer edge droops down
                    new THREE.Vector2(outerR - 0.002, -droop - halfT), // outer bottom edge
                    new THREE.Vector2(droopR, -halfT),    // flat bottom from droop start
                    new THREE.Vector2(innerR, -halfT),    // inner bottom
                ];
                shapeGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
                // Apply tutuOffset (shift along bone axis)
                const tOff = part.tutuOffset ?? 0;
                if (Math.abs(tOff) > 0.0001) shapeGeo.translate(0, tOff, 0);
                break;
            }
            case 'spiral_tutu':
                shapeGeo = _buildSpiralTutu(part, radius);
                break;
            case 'helix_ribbon':
                shapeGeo = _buildHelixRibbon(part, radius);
                break;
            case 'skirt':
                shapeGeo = _buildSkirt(part, radius);
                break;
            default: // cylinder
                shapeGeo = new THREE.CylinderGeometry(radius, radius, boneLen, segments, 1);
                break;
        }

        // Position shape from effective head to effective tail
        const midpoint = new THREE.Vector3().lerpVectors(effectiveHead, effectiveTail, 0.5);
        const direction = new THREE.Vector3().subVectors(effectiveTail, effectiveHead);
        if (direction.length() > 0.0001) direction.normalize();
        else direction.copy(boneDir);

        const yAxis = new THREE.Vector3(0, 1, 0);
        const shapeQuat = new THREE.Quaternion();
        if (Math.abs(direction.dot(yAxis)) < 0.9999) {
            shapeQuat.setFromUnitVectors(yAxis, direction);
        } else if (direction.y < 0) {
            shapeQuat.setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI);
        }

        // World-space rotation around shape center (premultiply = applied after bone alignment)
        if (part.shapeRotation) {
            const sr = part.shapeRotation;
            const rx = sr.x || 0, ry = sr.y || 0, rz = sr.z || 0;
            if (rx || ry || rz) {
                const deg = Math.PI / 180;
                const userRot = new THREE.Quaternion().setFromEuler(
                    new THREE.Euler(rx * deg, ry * deg, rz * deg));
                shapeQuat.premultiply(userRot);
            }
        }

        const mat4 = new THREE.Matrix4();
        mat4.compose(midpoint, shapeQuat, new THREE.Vector3(1, 1, 1));
        shapeGeo.applyMatrix4(mat4);

        geoChunks.push({ geometry: shapeGeo, boneIndex: boneIdx, color, boneName });
    }

    if (geoChunks.length === 0) return null;

    // Group by color for material groups
    const colorGroups = new Map(); // color -> [chunkIndices]
    geoChunks.forEach((chunk, i) => {
        if (!colorGroups.has(chunk.color)) colorGroups.set(chunk.color, []);
        colorGroups.get(chunk.color).push(i);
    });

    // Merge all geometries, tracking material group ranges
    let totalVerts = 0;
    let totalIndices = 0;
    for (const chunk of geoChunks) {
        totalVerts += chunk.geometry.attributes.position.count;
        totalIndices += chunk.geometry.index ? chunk.geometry.index.count : chunk.geometry.attributes.position.count;
    }

    const mergedPositions = new Float32Array(totalVerts * 3);
    const mergedNormals   = new Float32Array(totalVerts * 3);
    const mergedSkinIndices = new Float32Array(totalVerts * 4);
    const mergedSkinWeights = new Float32Array(totalVerts * 4);
    const mergedIndices = [];

    const materials = [];
    const groups = [];

    let vertOffset = 0;
    let indexOffset = 0;
    const boneVertexRanges = {};  // boneName -> { start, count }

    // Process chunks grouped by color
    for (const [color, chunkIndices] of colorGroups) {
        const groupStart = indexOffset;

        for (const ci of chunkIndices) {
            const chunk = geoChunks[ci];
            const geo = chunk.geometry;
            const posArr = geo.attributes.position.array;
            const normArr = geo.attributes.normal.array;
            const vCount = geo.attributes.position.count;

            // Track bone vertex range for 3D selection
            if (chunk.boneName) boneVertexRanges[chunk.boneName] = { start: vertOffset, count: vCount };

            // Copy positions and normals
            mergedPositions.set(posArr, vertOffset * 3);
            mergedNormals.set(normArr, vertOffset * 3);

            // Set skin weights: 100% on this bone
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

            // Copy indices with offset
            if (geo.index) {
                const idxArr = geo.index.array;
                for (let i = 0; i < idxArr.length; i++) {
                    mergedIndices.push(idxArr[i] + vertOffset);
                }
                indexOffset += idxArr.length;
            } else {
                for (let i = 0; i < vCount; i++) {
                    mergedIndices.push(vertOffset + i);
                }
                indexOffset += vCount;
            }

            vertOffset += vCount;
            geo.dispose();
        }

        const groupCount = indexOffset - groupStart;
        groups.push({ start: groupStart, count: groupCount, materialIndex: materials.length });

        materials.push(new THREE.MeshStandardMaterial({
            color: new THREE.Color(color),
            roughness: 0.6,
            metalness: 0.2,
            flatShading: false,
        }));
    }

    // Build merged BufferGeometry
    const mergedGeo = new THREE.BufferGeometry();
    mergedGeo.setAttribute('position', new THREE.Float32BufferAttribute(mergedPositions, 3));
    mergedGeo.setAttribute('normal', new THREE.Float32BufferAttribute(mergedNormals, 3));
    mergedGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(mergedSkinIndices, 4));
    mergedGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(mergedSkinWeights, 4));
    mergedGeo.setIndex(mergedIndices);

    for (const g of groups) {
        mergedGeo.addGroup(g.start, g.count, g.materialIndex);
    }

    // Build skeleton (same as buildRigifySkeleton in scene_config.js)
    const skelByNameMap = {};
    for (const b of skelData.bones) skelByNameMap[b.name] = b;

    const bones = [];
    const boneByName = {};
    let rootBone = null;

    for (const name of swData.bone_names) {
        const bone = new THREE.Bone();
        bone.name = name.replace(/\./g, '_');
        bones.push(bone);
        boneByName[name] = bone;
    }

    for (let i = 0; i < swData.bone_names.length; i++) {
        const name = swData.bone_names[i];
        const bone = bones[i];
        const bdata = skelByNameMap[name];
        if (!bdata) continue;
        const p = bdata.local_position;
        bone.position.set(p[0], p[2], -p[1]);
        const q = bdata.local_quaternion;
        bone.quaternion.set(q[1], q[3], -q[2], q[0]);
        if (bdata.parent && boneByName[bdata.parent]) {
            boneByName[bdata.parent].add(bone);
        } else if (!rootBone) {
            rootBone = bone;
        }
    }
    for (let i = 0; i < bones.length; i++) {
        const name = swData.bone_names[i];
        const bdata = skelByNameMap[name];
        if (!bdata) continue;
        if (!bdata.parent && bones[i] !== rootBone && rootBone) rootBone.add(bones[i]);
    }
    if (!rootBone && bones.length > 0) rootBone = bones[0];
    rootBone.updateWorldMatrix(true, true);

    const skeleton = new THREE.Skeleton(bones);

    // Create SkinnedMesh
    const skinnedMesh = new THREE.SkinnedMesh(mergedGeo, materials);
    skinnedMesh.add(rootBone);
    skinnedMesh.bind(skeleton);

    skinnedMesh.userData.boneVertexRanges = boneVertexRanges;
    skinnedMesh.userData.isGeneratedModel = true;

    return {
        mesh: skinnedMesh,
        skeleton: { skeleton, rootBone, bones, boneByName },
    };
}

// =========================================================================
// Rig Bones Support
// =========================================================================

/**
 * Classify rig bones into 4 categories: DEF, MCH, ORG, Control.
 * @param {Object} rigData - {bones: [{name, parent, head, tail, connected, deform}]}
 * @returns {{ def: string[], mch: string[], org: string[], control: string[] }}
 */
export function classifyRigBones(rigData) {
    const def = [], mch = [], org = [], control = [];
    for (const b of rigData.bones) {
        const name = b.name;
        if (name.startsWith('DEF-'))      def.push(name);
        else if (name.startsWith('MCH-')) mch.push(name);
        else if (name.startsWith('ORG-')) org.push(name);
        else                               control.push(name);
    }
    return { def, mch, org, control };
}

/**
 * Compute world transforms for rig bones (head/tail format, Blender Z-up coords).
 * Rig bones have absolute head/tail in Blender world coordinates.
 * Returns Map<boneName, {worldPos: Vector3 (head in Three.js), tailPos: Vector3, length: number}>
 */
export function computeRigBoneWorldTransforms(rigData) {
    const result = new Map();
    for (const b of rigData.bones) {
        const h = b.head; // [x, y, z] Blender coords (Z-up, Y-forward)
        const t = b.tail;
        // Convert Blender→Three.js: (x, z, -y)
        const headPos = new THREE.Vector3(h[0], h[2], -h[1]);
        const tailPos = new THREE.Vector3(t[0], t[2], -t[1]);
        const len = headPos.distanceTo(tailPos);
        result.set(b.name, { worldPos: headPos, tailPos, length: len || 0.02 });
    }
    return result;
}

/**
 * Build default config for rig bones. Only DEF bones visible by default.
 */
export function getDefaultRigConfig(rigData) {
    const classified = classifyRigBones(rigData);
    const worldTransforms = computeRigBoneWorldTransforms(rigData);

    const boneParts = {};
    const defaultColor = '#4488cc';
    const defaultRadius = 0.03;
    const colors = {
        def: '#4488cc',
        mch: '#cc8844',
        org: '#44cc88',
        control: '#cc4488',
    };

    for (const [cat, boneList] of Object.entries(classified)) {
        const visible = cat === 'def';
        for (const name of boneList) {
            const wt = worldTransforms.get(name);
            const len = wt ? wt.length : 0.05;
            const autoRadius = Math.min(0.05, Math.max(0.005, len * 0.15));
            boneParts[name] = {
                shape: 'cylinder',
                radius: parseFloat(autoRadius.toFixed(4)),
                color: colors[cat],
                visible,
            };
        }
    }

    return {
        type: 'generated_model',
        skeleton_type: 'rig',
        version: 1,
        name: 'Rig Model',
        bone_parts: boneParts,
        default_color: defaultColor,
        default_radius: defaultRadius,
        segments: 8,
    };
}

/**
 * Generate a non-skinned Mesh from rig bone config.
 * Rig bones have head/tail world positions — no skeleton needed for animation.
 * @param {Object} rigData - Rig bone data {bones: [{name, head, tail, parent, ...}]}
 * @param {Object} config  - Model config {bone_parts, segments, ...}
 * @returns {{ mesh: THREE.Mesh }} | null
 */
export function generateRigBoneMesh(rigData, config, rigifySkeletonData = null, swData = null) {
    const segments = config.segments || 8;
    const worldTransforms = computeRigBoneWorldTransforms(rigData);

    // Build bone index map for skinning (Rigify bones only)
    const canSkin = !!(rigifySkeletonData && swData);
    const boneIndexMap = {};
    if (canSkin) {
        for (let i = 0; i < swData.bone_names.length; i++) {
            boneIndexMap[swData.bone_names[i]] = i;
        }
    }

    const geoChunks = [];  // { geometry, color, boneIndex }

    for (const [boneName, part] of Object.entries(config.bone_parts)) {
        if (!part.visible) continue;
        const wt = worldTransforms.get(boneName);
        if (!wt) continue;

        const radius = part.radius || config.default_radius || 0.03;
        const color = part.color || config.default_color || '#4488cc';
        let boneLen = wt.length;
        if (boneLen < 0.001) boneLen = 0.02;

        // Apply head/tail offsets in bone-local space
        let effectiveHead = wt.worldPos.clone();
        let effectiveTail = wt.tailPos.clone();
        if (part.headOffset || part.tailOffset) {
            // Derive bone orientation quaternion from head→tail direction
            const rawDir = new THREE.Vector3().subVectors(wt.tailPos, wt.worldPos);
            if (rawDir.length() > 0.0001) rawDir.normalize(); else rawDir.set(0, 1, 0);
            const boneQuat = new THREE.Quaternion();
            const yUp = new THREE.Vector3(0, 1, 0);
            if (Math.abs(rawDir.dot(yUp)) < 0.9999) boneQuat.setFromUnitVectors(yUp, rawDir);
            else if (rawDir.y < 0) boneQuat.setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI);
            if (part.headOffset) {
                effectiveHead.add(new THREE.Vector3(
                    part.headOffset.x || 0, part.headOffset.y || 0, part.headOffset.z || 0
                ).applyQuaternion(boneQuat));
            }
            if (part.tailOffset) {
                effectiveTail.add(new THREE.Vector3(
                    part.tailOffset.x || 0, part.tailOffset.y || 0, part.tailOffset.z || 0
                ).applyQuaternion(boneQuat));
            }
            const effLen = effectiveHead.distanceTo(effectiveTail);
            if (effLen > 0.001) boneLen = effLen;
        }

        // Create shape geometry
        let shapeGeo;
        switch (part.shape) {
            case 'box':
                shapeGeo = new THREE.BoxGeometry(radius * 2, boneLen, radius * 2, 1, 1, 1);
                break;
            case 'sphere_low':
                shapeGeo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                break;
            case 'sphere':
                shapeGeo = new THREE.SphereGeometry(radius, 24, 16);
                break;
            case 'cone':
                shapeGeo = new THREE.ConeGeometry(radius, boneLen, segments);
                break;
            case 'capsule':
                shapeGeo = new THREE.CapsuleGeometry(radius, Math.max(0.001, boneLen - radius * 2), segments, Math.max(4, segments >> 1));
                break;
            case 'oval':
                shapeGeo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                shapeGeo.scale(1, boneLen / (radius * 2), 1);
                break;
            case 'double_oval': {
                const ov = part.overlap ?? 0.5;
                const halfLen = boneLen * 0.5;
                const ovalLen = halfLen + halfLen * ov;
                const scY = ovalLen / (radius * 2);
                const sep = halfLen * (1 - ov);
                const hSegs = Math.max(4, segments >> 1);
                const g1 = new THREE.SphereGeometry(radius, segments, hSegs);
                g1.scale(1, scY, 1); g1.translate(0, -sep, 0);
                const g2 = new THREE.SphereGeometry(radius, segments, hSegs);
                g2.scale(1, scY, 1); g2.translate(0, sep, 0);
                shapeGeo = _mergeSimpleGeos(g1, g2);
                break;
            }
            case 'diamond':
                shapeGeo = new THREE.OctahedronGeometry(radius);
                shapeGeo.scale(1, boneLen / (radius * 2), 1);
                break;
            case 'tutu': {
                const thickness = part.tutuThickness ?? 0.01;
                const droop = part.tutuDroop ?? 0.03;
                const droopStart = part.tutuDroopStart ?? 0.7;
                const innerR = radius * 0.08;
                const outerR = radius;
                const halfT = thickness * 0.5;
                const droopR = outerR * droopStart;
                const radSegs = Math.max(16, segments * 4);
                const pts = [
                    new THREE.Vector2(innerR, halfT),
                    new THREE.Vector2(droopR, halfT),
                    new THREE.Vector2(outerR, -droop),
                    new THREE.Vector2(outerR - 0.002, -droop - halfT),
                    new THREE.Vector2(droopR, -halfT),
                    new THREE.Vector2(innerR, -halfT),
                ];
                shapeGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
                const tOff = part.tutuOffset ?? 0;
                if (Math.abs(tOff) > 0.0001) shapeGeo.translate(0, tOff, 0);
                break;
            }
            case 'spiral_tutu':
                shapeGeo = _buildSpiralTutu(part, radius);
                break;
            case 'helix_ribbon':
                shapeGeo = _buildHelixRibbon(part, radius);
                break;
            case 'skirt':
                shapeGeo = _buildSkirt(part, radius);
                break;
            default:
                shapeGeo = new THREE.CylinderGeometry(radius, radius, boneLen, segments, 1);
                break;
        }

        // Position between effective head and tail
        const midpoint = new THREE.Vector3().lerpVectors(effectiveHead, effectiveTail, 0.5);
        const direction = new THREE.Vector3().subVectors(effectiveTail, effectiveHead);
        if (direction.length() > 0.0001) direction.normalize();
        else direction.set(0, 1, 0);

        const yAxis = new THREE.Vector3(0, 1, 0);
        const shapeQuat = new THREE.Quaternion();
        if (Math.abs(direction.dot(yAxis)) < 0.9999) {
            shapeQuat.setFromUnitVectors(yAxis, direction);
        } else if (direction.y < 0) {
            shapeQuat.setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI);
        }

        // World-space rotation around shape center (premultiply = applied after bone alignment)
        if (part.shapeRotation) {
            const sr = part.shapeRotation;
            const rx = sr.x || 0, ry = sr.y || 0, rz = sr.z || 0;
            if (rx || ry || rz) {
                const deg = Math.PI / 180;
                const userRot = new THREE.Quaternion().setFromEuler(
                    new THREE.Euler(rx * deg, ry * deg, rz * deg));
                shapeQuat.premultiply(userRot);
            }
        }

        const mat4 = new THREE.Matrix4();
        mat4.compose(midpoint, shapeQuat, new THREE.Vector3(1, 1, 1));
        shapeGeo.applyMatrix4(mat4);

        // Determine skin bone index: DEF bones map to their skeleton index, others to root (0)
        const boneIdx = canSkin ? (boneIndexMap[boneName] !== undefined ? boneIndexMap[boneName] : 0) : 0;
        geoChunks.push({ geometry: shapeGeo, color, boneIndex: boneIdx, boneName });
    }

    if (geoChunks.length === 0) return null;

    // Group by color
    const colorGroups = new Map();
    geoChunks.forEach((chunk, i) => {
        if (!colorGroups.has(chunk.color)) colorGroups.set(chunk.color, []);
        colorGroups.get(chunk.color).push(i);
    });

    let totalVerts = 0, totalIndices = 0;
    for (const chunk of geoChunks) {
        totalVerts += chunk.geometry.attributes.position.count;
        totalIndices += chunk.geometry.index ? chunk.geometry.index.count : chunk.geometry.attributes.position.count;
    }

    const mergedPositions = new Float32Array(totalVerts * 3);
    const mergedNormals = new Float32Array(totalVerts * 3);
    const mergedSkinIndices = canSkin ? new Float32Array(totalVerts * 4) : null;
    const mergedSkinWeights = canSkin ? new Float32Array(totalVerts * 4) : null;
    const mergedIndices = [];
    const materials = [];
    const groups = [];

    let vertOffset = 0, indexOffset = 0;
    const boneVertexRanges = {};  // boneName -> { start, count }

    for (const [color, chunkIndices] of colorGroups) {
        const groupStart = indexOffset;
        for (const ci of chunkIndices) {
            const chunk = geoChunks[ci];
            const geo = chunk.geometry;
            const posArr = geo.attributes.position.array;
            const normArr = geo.attributes.normal.array;
            const vCount = geo.attributes.position.count;

            // Track bone vertex range for 3D selection
            if (chunk.boneName) boneVertexRanges[chunk.boneName] = { start: vertOffset, count: vCount };

            mergedPositions.set(posArr, vertOffset * 3);
            mergedNormals.set(normArr, vertOffset * 3);

            // Assign skin weights: 100% on the bone
            if (canSkin) {
                for (let v = 0; v < vCount; v++) {
                    const base = (vertOffset + v) * 4;
                    mergedSkinIndices[base] = chunk.boneIndex;
                    mergedSkinWeights[base] = 1;
                }
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
        groups.push({ start: groupStart, count: indexOffset - groupStart, materialIndex: materials.length });
        materials.push(new THREE.MeshStandardMaterial({
            color: new THREE.Color(color), roughness: 0.6, metalness: 0.2, flatShading: false,
        }));
    }

    const mergedGeo = new THREE.BufferGeometry();
    mergedGeo.setAttribute('position', new THREE.Float32BufferAttribute(mergedPositions, 3));
    mergedGeo.setAttribute('normal', new THREE.Float32BufferAttribute(mergedNormals, 3));
    mergedGeo.setIndex(mergedIndices);
    for (const g of groups) mergedGeo.addGroup(g.start, g.count, g.materialIndex);

    // Build SkinnedMesh with Rigify skeleton if skin data is available
    if (canSkin) {
        mergedGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(mergedSkinIndices, 4));
        mergedGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(mergedSkinWeights, 4));

        const skelByName = {};
        for (const b of rigifySkeletonData.bones) skelByName[b.name] = b;

        const bones = [];
        const boneByName = {};
        let rootBone = null;

        for (const name of swData.bone_names) {
            const bone = new THREE.Bone();
            bone.name = name.replace(/\./g, '_');
            bones.push(bone);
            boneByName[name] = bone;
        }
        for (let i = 0; i < swData.bone_names.length; i++) {
            const name = swData.bone_names[i];
            const bone = bones[i];
            const bdata = skelByName[name];
            if (!bdata) continue;
            const p = bdata.local_position;
            bone.position.set(p[0], p[2], -p[1]);
            const q = bdata.local_quaternion;
            bone.quaternion.set(q[1], q[3], -q[2], q[0]);
            if (bdata.parent && boneByName[bdata.parent]) {
                boneByName[bdata.parent].add(bone);
            } else if (!rootBone) {
                rootBone = bone;
            }
        }
        for (let i = 0; i < bones.length; i++) {
            const name = swData.bone_names[i];
            const bdata = skelByName[name];
            if (!bdata) continue;
            if (!bdata.parent && bones[i] !== rootBone && rootBone) rootBone.add(bones[i]);
        }
        if (!rootBone && bones.length > 0) rootBone = bones[0];
        rootBone.updateWorldMatrix(true, true);

        const skeleton = new THREE.Skeleton(bones);
        const skinnedMesh = new THREE.SkinnedMesh(mergedGeo, materials);
        skinnedMesh.add(rootBone);
        skinnedMesh.bind(skeleton);

        skinnedMesh.userData.boneVertexRanges = boneVertexRanges;
        skinnedMesh.userData.isGeneratedModel = true;

        return {
            mesh: skinnedMesh,
            skeleton: { skeleton, rootBone, bones, boneByName },
        };
    }

    const plainMesh = new THREE.Mesh(mergedGeo, materials);
    plainMesh.userData.boneVertexRanges = boneVertexRanges;
    plainMesh.userData.isGeneratedModel = true;
    return { mesh: plainMesh };
}
