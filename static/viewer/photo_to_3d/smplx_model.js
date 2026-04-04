/**
 * Photo To 3D — SMPL-X model loading, texture, rig, slider panel.
 */
import * as THREE from 'three';
import { state, API, SMPLX_OFFSET_X, SMPLX_BETA_LABELS, SMPLX_EXPR_LABELS } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, base64ToUint16 } from './helpers.js';

// =========================================================================
// SMPL-X model loading — full SkinnedMesh + Rig (shifted right)
// =========================================================================
export async function loadSmplxModel() {
    const betas = [...state.smplxBetas];
    const allBetas = new Array(310).fill(0);
    for (let i = 0; i < 10; i++) allBetas[i] = betas[i];
    for (let i = 0; i < 10; i++) allBetas[300 + i] = state.smplxExpr[i];

    try {
        const resp = await fetch(`${API}/smplx-mesh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ betas: allBetas, gender: 'neutral' }),
        });
        const data = await resp.json();
        if (!data.ok) { console.warn('SMPL-X mesh:', data.error); return; }

        // Clean up old
        if (state.smplxGroup) {
            state.scene.remove(state.smplxGroup);
            if (state.smplxSkinnedMesh) {
                state.smplxSkinnedMesh.geometry?.dispose();
                state.smplxSkinnedMesh.material?.dispose();
            }
            if (state.smplxSkelHelper) state.smplxSkelHelper = null;
        }

        state.smplxGroup = new THREE.Group();
        state.smplxGroup.position.x = SMPLX_OFFSET_X;

        // --- Build skeleton from joints + parents ---
        const jointPos = base64ToFloat32(data.joints);
        const parents = data.parents;
        const nJoints = data.n_joints;

        const bones = [];
        for (let i = 0; i < nJoints; i++) {
            const bone = new THREE.Bone();
            bone.name = `smplx_j${i}`;
            bones.push(bone);
        }

        for (let i = 0; i < nJoints; i++) {
            const wx = jointPos[i * 3];
            const wy = jointPos[i * 3 + 1];
            const wz = jointPos[i * 3 + 2];
            const parentIdx = parents[i];
            if (parentIdx < 0) {
                bones[i].position.set(wx, wy, wz);
            } else {
                const px = jointPos[parentIdx * 3];
                const py = jointPos[parentIdx * 3 + 1];
                const pz = jointPos[parentIdx * 3 + 2];
                bones[i].position.set(wx - px, wy - py, wz - pz);
                bones[parentIdx].add(bones[i]);
            }
        }

        const skeleton = new THREE.Skeleton(bones);

        // --- Build geometry ---
        const hasUV = !!data.uv_coords;
        const verts   = hasUV ? base64ToFloat32(data.uv_vertices) : base64ToFloat32(data.vertices);
        const faces   = hasUV ? base64ToUint32(data.uv_faces)     : base64ToUint32(data.faces);
        const skinIdx = hasUV ? base64ToUint16(data.uv_skin_indices) : base64ToUint16(data.skin_indices);
        const skinWgt = hasUV ? base64ToFloat32(data.uv_skin_weights) : base64ToFloat32(data.skin_weights);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(verts, 3));
        geo.setIndex(new THREE.BufferAttribute(faces, 1));

        if (hasUV) {
            const uvCoords = base64ToFloat32(data.uv_coords);
            geo.setAttribute('uv', new THREE.BufferAttribute(uvCoords, 2));
            console.log(`[SMPL-X] UV data: ${data.n_uv_verts} uv verts`);
        }

        geo.computeVertexNormals();

        geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIdx, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWgt, 4));

        const mat = new THREE.MeshStandardMaterial({
            color: 0xccaa88,
            roughness: 0.55,
            metalness: 0.0,
            side: THREE.DoubleSide,
        });

        state.smplxSkinnedMesh = new THREE.SkinnedMesh(geo, mat);
        state.smplxSkinnedMesh.add(bones[0]);
        state.smplxSkinnedMesh.bind(skeleton);

        state.smplxGroup.add(state.smplxSkinnedMesh);
        state.scene.add(state.smplxGroup);

        matchModelHeights();

        if (state.smplxRigVisible) showSmplxRig();

        const vcEl = document.getElementById('smplx-vertex-count');
        if (vcEl) vcEl.textContent = data.n_verts.toLocaleString();

        console.log(`SMPL-X model: ${data.n_verts} verts, ${data.n_faces} faces, ${data.n_joints} joints`);
    } catch (e) {
        console.error('Failed to load SMPL-X model:', e);
    }
}

/**
 * Load baked photo texture for SMPL-X mesh from the backend.
 */
export async function loadSmplxTexture(jobId, backend = 'orthographic', region = 'all') {
    if (!jobId || !state.smplxSkinnedMesh) {
        console.warn('[SMPL-X Tex] No jobId or mesh');
        return;
    }
    if (!state.smplxSkinnedMesh.geometry.getAttribute('uv')) {
        console.warn('[SMPL-X Tex] No UV attribute on SMPL-X mesh');
        return;
    }

    console.log('[SMPL-X Tex] Loading texture for job', jobId, 'backend', backend, 'region', region);
    try {
        let url = `${API}/smplx-texture/${jobId}/?backend=${encodeURIComponent(backend)}`;
        if (region && region !== 'all') url += `&region=${encodeURIComponent(region)}`;
        const resp = await fetch(url);
        if (!resp.ok) {
            let errMsg = `Server ${resp.status}`;
            try {
                const errData = await resp.json();
                errMsg = errData.error || errMsg;
            } catch (_) {
                errMsg = await resp.text() || errMsg;
            }
            console.warn('[SMPL-X Tex] Server error:', errMsg);
            throw new Error(errMsg);
        }

        const blob = await resp.blob();
        const imgUrl = URL.createObjectURL(blob);

        const loader = new THREE.TextureLoader();
        const texture = await new Promise((resolve, reject) => {
            loader.load(imgUrl, resolve, undefined, reject);
        });

        texture.flipY = true;
        texture.colorSpace = THREE.SRGBColorSpace;

        state.smplxSkinnedMesh.material.map = texture;
        state.smplxSkinnedMesh.material.color.set(0xffffff);
        state.smplxSkinnedMesh.material.needsUpdate = true;

        console.log('[SMPL-X Tex] Texture applied successfully');
    } catch (e) {
        console.error('[SMPL-X Tex] Failed:', e);
        throw e;
    }
}

function matchModelHeights() {
    if (!state.bodyMesh || !state.smplxSkinnedMesh) return;
    state.bodyMesh.geometry.computeBoundingBox();
    state.smplxSkinnedMesh.geometry.computeBoundingBox();
    const hbBox = state.bodyMesh.geometry.boundingBox;
    const smplxBox = state.smplxSkinnedMesh.geometry.boundingBox;
    const hbHeight = hbBox.max.y - hbBox.min.y;
    const smplxHeight = smplxBox.max.y - smplxBox.min.y;
    if (smplxHeight > 0.01 && hbHeight > 0.01) {
        const scale = hbHeight / smplxHeight;
        state.smplxGroup.scale.setScalar(scale);
    }
}

export function requestSmplxUpdate() {
    if (state.smplxUpdateTimer) clearTimeout(state.smplxUpdateTimer);
    state.smplxUpdateTimer = setTimeout(() => {
        state.smplxUpdateTimer = null;
        loadSmplxModel();
        fn.applyFacialExpression(state.smplxExpr);
    }, 120);
}

export function showSmplxRig() {
    if (!state.smplxSkinnedMesh) return;
    if (state.smplxSkelHelper) {
        state.smplxGroup.remove(state.smplxSkelHelper);
        state.smplxSkelHelper.dispose();
    }
    state.smplxSkelHelper = new THREE.SkeletonHelper(state.smplxSkinnedMesh);
    state.smplxSkelHelper.material.depthTest = false;
    state.smplxSkelHelper.material.depthWrite = false;
    state.smplxSkelHelper.material.color.set(0xff8844);
    state.smplxSkelHelper.renderOrder = 999;
    state.smplxGroup.add(state.smplxSkelHelper);
}

// =========================================================================
// SMPL-X slider panel
// =========================================================================
export function buildSmplxPanel() {
    const panel = document.getElementById('smplx-panel');
    if (!panel) return;

    // Gender dropdown
    const genderRow = document.createElement('div');
    genderRow.style.cssText = 'margin-bottom:8px;';
    const genderSel = document.createElement('select');
    genderSel.className = 'viewer-select';
    genderSel.id = 'smplx-gender';
    ['female', 'male', 'neutral'].forEach(g => {
        const opt = document.createElement('option');
        opt.value = g;
        opt.textContent = g.charAt(0).toUpperCase() + g.slice(1);
        genderSel.appendChild(opt);
    });
    genderSel.value = state.smplxGender;
    genderSel.addEventListener('change', () => {
        state.smplxGender = genderSel.value;
        requestSmplxUpdate();
    });
    genderRow.appendChild(genderSel);
    panel.appendChild(genderRow);

    // Shape betas
    const shapeHeader = document.createElement('div');
    shapeHeader.className = 'morph-category-header';
    shapeHeader.textContent = 'Shape (Body)';
    shapeHeader.style.cssText = 'cursor:pointer;margin-top:4px;';
    const shapeBody = document.createElement('div');
    shapeBody.style.display = 'block';
    shapeHeader.addEventListener('click', () => {
        shapeBody.style.display = shapeBody.style.display === 'none' ? 'block' : 'none';
    });
    panel.appendChild(shapeHeader);

    for (let i = 0; i < 10; i++) {
        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = SMPLX_BETA_LABELS[i];
        label.title = `Beta ${i}`;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -300; slider.max = 300;
        slider.value = 0; slider.step = 1;
        slider.dataset.betaIdx = i;

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = '0.0';

        slider.addEventListener('input', () => {
            const v = parseInt(slider.value) / 100.0;
            valSpan.textContent = v.toFixed(1);
            state.smplxBetas[i] = v;
            requestSmplxUpdate();
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        shapeBody.appendChild(row);
    }
    panel.appendChild(shapeBody);

    // Expression params
    const exprHeader = document.createElement('div');
    exprHeader.className = 'morph-category-header';
    exprHeader.textContent = 'Expression (Face)';
    exprHeader.style.cssText = 'cursor:pointer;margin-top:8px;';
    const exprBody = document.createElement('div');
    exprBody.style.display = 'none';
    exprHeader.addEventListener('click', () => {
        exprBody.style.display = exprBody.style.display === 'none' ? 'block' : 'none';
    });
    panel.appendChild(exprHeader);

    for (let i = 0; i < 10; i++) {
        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = SMPLX_EXPR_LABELS[i];

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -300; slider.max = 300;
        slider.value = 0; slider.step = 1;
        slider.dataset.exprIdx = i;

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = '0.0';

        slider.addEventListener('input', () => {
            const v = parseInt(slider.value) / 100.0;
            valSpan.textContent = v.toFixed(1);
            state.smplxExpr[i] = v;
            requestSmplxUpdate();
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        exprBody.appendChild(row);
    }
    panel.appendChild(exprBody);

    // Reset button
    const resetBtn = document.getElementById('reset-smplx');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            state.smplxBetas.fill(0);
            state.smplxExpr.fill(0);
            panel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                const vEl = s.parentElement.querySelector('.slider-val');
                if (vEl) vEl.textContent = '0.0';
            });
            requestSmplxUpdate();
        });
    }
}

fn.loadSmplxModel = loadSmplxModel;
fn.loadSmplxTexture = loadSmplxTexture;
fn.requestSmplxUpdate = requestSmplxUpdate;
fn.showSmplxRig = showSmplxRig;
fn.buildSmplxPanel = buildSmplxPanel;
