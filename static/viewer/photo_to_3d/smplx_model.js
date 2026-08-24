/**
 * Photo To 3D — SMPL-X model loading, texture, rig, slider panel.
 */
import * as THREE from 'three';
import { state, API, SMPLX_OFFSET_X } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, base64ToUint32, base64ToUint16 } from './helpers.js';
import { buildSmplxPanel, requestSmplxUpdate, showSmplxRig } from './smplx_panel.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Smplxnetz } from './smplxnetz.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

// =========================================================================
// SMPL-X model loading — full SkinnedMesh + Rig (shifted right)
// =========================================================================
/**
 * SMPL-X-Vergleichsmodell holen und in die Szene setzen.
 *
 * Umbau 17.08.2026: 103 Zeilen. Der Bau des Netzes steht jetzt in
 * `Smplxnetz` (smplxnetz.js) — hier bleiben Anfrage, Aufräumen und Anzeige.
 */
export async function loadSmplxModel() {
    let daten;
    try {
        daten = await Serverabruf.senden(`${API}/smplx-mesh/`, {
            betas: Smplxnetz.formwerte(state.smplxBetas, state.smplxExpr),
            gender: 'neutral',
        });
    } catch (fehler) {
        Protokoll.fehler('SMPL-X', 'Modell nicht ladbar:', fehler);
        return;
    }
    if (!daten.ok) {
        Protokoll.warnung('SMPL-X', daten.error || 'Antwort ohne ok');
        return;
    }

    _altesEntsorgen();
    state.smplxGroup = new THREE.Group();
    state.smplxGroup.position.x = SMPLX_OFFSET_X;
    state.smplxSkinnedMesh = new Smplxnetz(daten).bauen();
    state.smplxGroup.add(state.smplxSkinnedMesh);
    state.scene.add(state.smplxGroup);

    matchModelHeights();
    if (state.smplxRigVisible) showSmplxRig();
    const zaehler = document.getElementById('smplx-vertex-count');
    if (zaehler) zaehler.textContent = daten.n_verts.toLocaleString();
    Protokoll.debug('SMPL-X', `${daten.n_verts} Punkte, ${daten.n_faces} `
                    + `Flächen, ${daten.n_joints} Gelenke`);
}

/** Vorheriges Modell samt Geometrie und Material freigeben. */
function _altesEntsorgen() {
    if (!state.smplxGroup) return;
    state.scene.remove(state.smplxGroup);
    state.smplxSkinnedMesh?.geometry?.dispose();
    state.smplxSkinnedMesh?.material?.dispose();
    state.smplxSkelHelper = null;
}

/**
 * Load baked photo texture for SMPL-X mesh from the backend.
 */
export async function loadSmplxTexture(jobId, backend = 'orthographic', region = 'all') {
    if (!jobId || !state.smplxSkinnedMesh) {
        Protokoll.warnung('SMPL-X Tex', 'No jobId or mesh');
        return;
    }
    if (!state.smplxSkinnedMesh.geometry.getAttribute('uv')) {
        Protokoll.warnung('SMPL-X Tex', 'No UV attribute on SMPL-X mesh');
        return;
    }

    Protokoll.debug('SMPL-X Tex', 'Loading texture for job', jobId, 'backend', backend, 'region', region);
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
            Protokoll.warnung('SMPL-X Tex', 'Server error:', errMsg);
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

        Protokoll.debug('SMPL-X Tex', 'Texture applied successfully');
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




fn.loadSmplxModel = loadSmplxModel;
fn.loadSmplxTexture = loadSmplxTexture;
fn.requestSmplxUpdate = requestSmplxUpdate;
fn.showSmplxRig = showSmplxRig;
fn.buildSmplxPanel = buildSmplxPanel;
