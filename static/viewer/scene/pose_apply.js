/**
 * Scene Editor -- Pose browser + apply + rename/delete.
 */
import { THREE, SESSION_KEY } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { _selectedInst, getCSRFToken } from './utils.js';
import { convertInstToSkinned } from './skeleton.js';

/* ── Selection state ── */
let _selectedPoseRow = null;
let _selectedPoseData = null;  // {id, name, category}

function _selectPoseRow(row, pose) {
    if (_selectedPoseRow) _selectedPoseRow.style.background = '';
    _selectedPoseRow = row;
    _selectedPoseData = pose;
    row.style.background = 'rgba(124,92,191,0.35)';
}

/* ── Context menu ── */
const _ctxMenu = () => document.getElementById('pose-ctx-menu');

function _showCtx(x, y) {
    const m = _ctxMenu(); if (!m) return;
    m.style.display = 'block'; m.style.left = x + 'px'; m.style.top = y + 'px';
    // Clamp to viewport
    const r = m.getBoundingClientRect();
    if (r.right > window.innerWidth) m.style.left = (window.innerWidth - r.width - 4) + 'px';
    if (r.bottom > window.innerHeight) m.style.top = (window.innerHeight - r.height - 4) + 'px';
}

function _hideCtx() { const m = _ctxMenu(); if (m) m.style.display = 'none'; }

/* ── API helper ── */
async function poseManage(action, data) {
    const resp = await fetch('/api/character/pose-manage/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        body: JSON.stringify({ action, ...data }),
    });
    return resp.json();
}

/* ── Rename / Delete ── */
function renameSelectedPose() {
    if (!_selectedPoseData) return;
    const newName = prompt('Neuer Name:', _selectedPoseData.name);
    if (!newName || newName === _selectedPoseData.name) return;
    poseManage('rename', { category: _selectedPoseData.category, name: _selectedPoseData.name, new_name: newName }).then(res => {
        if (res.ok) { _selectedPoseRow = null; _selectedPoseData = null; loadPoseUI(); }
        else alert(res.error || 'Rename fehlgeschlagen');
    });
}

function deleteSelectedPose() {
    if (!_selectedPoseData) return;
    if (!confirm(`Pose "${_selectedPoseData.name}" wirklich loeschen?`)) return;
    poseManage('delete', { category: _selectedPoseData.category, name: _selectedPoseData.name }).then(res => {
        if (res.ok) { _selectedPoseRow = null; _selectedPoseData = null; loadPoseUI(); }
        else alert(res.error || 'Delete fehlgeschlagen');
    });
}

/* ── Init context menu actions (once) ── */
let _ctxBound = false;
function _bindCtxMenu() {
    if (_ctxBound) return; _ctxBound = true;
    document.addEventListener('click', _hideCtx);
    const m = _ctxMenu(); if (!m) return;
    m.querySelectorAll('.pose-ctx-item').forEach(el => {
        el.addEventListener('click', e => {
            e.stopPropagation(); _hideCtx();
            const action = el.dataset.action;
            if (action === 'apply' && _selectedPoseData) applyPoseFromServer(_selectedPoseData.id);
            else if (action === 'rename') renameSelectedPose();
            else if (action === 'delete') deleteSelectedPose();
        });
    });
}

/* ── Keyboard shortcuts (on pose-list focus area) ── */
let _kbBound = false;
function _bindKeyboard() {
    if (_kbBound) return; _kbBound = true;
    const list = document.getElementById('pose-list');
    if (!list) return;
    list.setAttribute('tabindex', '0');
    list.addEventListener('keydown', e => {
        if (e.key === 'F2') { e.preventDefault(); renameSelectedPose(); }
        else if (e.key === 'Delete') { e.preventDefault(); deleteSelectedPose(); }
    });
}

export async function loadPoseUI() {
    const list = document.getElementById('pose-list');
    const resetBtn = document.getElementById('pose-reset');
    if (!list) return;
    _bindCtxMenu();
    _bindKeyboard();
    try {
        const resp = await fetch('/api/character/poses/');
        const data = await resp.json();
        list.innerHTML = '';
        for (const [cat, poses] of Object.entries(data.categories || {})) {
            const folder = document.createElement('div'); folder.className = 'anim-folder';
            const header = document.createElement('div'); header.className = 'anim-folder-header';
            header.innerHTML = `<span class="chevron">&#9660;</span> ${cat} (${poses.length})`;
            folder.appendChild(header);
            const body = document.createElement('div'); body.className = 'anim-folder-body';
            for (const pose of poses) {
                const poseInfo = { id: pose.id, name: pose.name, category: cat };
                const row = document.createElement('div'); row.className = 'anim-item'; row.style.cssText = 'padding:4px 8px;cursor:pointer;font-size:0.8rem;';
                row.textContent = pose.name;
                row.addEventListener('click', () => _selectPoseRow(row, poseInfo));
                row.addEventListener('dblclick', () => applyPoseFromServer(pose.id));
                row.addEventListener('contextmenu', e => { e.preventDefault(); _selectPoseRow(row, poseInfo); _showCtx(e.clientX, e.clientY); });
                body.appendChild(row);
            }
            folder.appendChild(body);
            header.addEventListener('click', () => { body.style.display = body.style.display === 'none' ? '' : 'none'; header.querySelector('.chevron').textContent = body.style.display === 'none' ? '\u25B6' : '\u25BC'; });
            if (cat !== 'rest_poses') { body.style.display = 'none'; header.querySelector('.chevron').textContent = '\u25B6'; }
            list.appendChild(folder);
        }
    } catch(e) { list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Poses nicht verf\u00fcgbar</div>'; }
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            const inst = _selectedInst();
            if (!inst?.isSkinned) return;
            let skel = null;
            inst.group.traverse(child => { if (!skel && child.isSkinnedMesh && child.skeleton) skel = child.skeleton; });
            if (!skel || !inst._aPoseBones) return;
            for (const bone of skel.bones) { const saved = inst._aPoseBones[bone.name]; if (saved) bone.quaternion.copy(saved); }
        });
    }
}

export async function applyPoseFromServer(poseId) {
    const inst = _selectedInst();
    if (!inst) return;
    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) convertInstToSkinned(inst);
    if (!inst.isSkinned) return;
    const resp = await fetch(`/api/character/pose/${poseId}/`);
    const data = await resp.json();
    if (!data.bones) return;
    let skel = null;
    inst.group.traverse(child => { if (!skel && child.isSkinnedMesh && child.skeleton) skel = child.skeleton; });
    if (!skel) return;
    if (!inst._aPoseBones) {
        inst._aPoseBones = {};
        for (const bone of skel.bones) inst._aPoseBones[bone.name] = bone.quaternion.clone();
    }
    for (const bone of skel.bones) { const saved = inst._aPoseBones[bone.name]; if (saved) bone.quaternion.copy(saved); }
    const limbRoots = new Set(['DEF-upper_arm.L', 'DEF-upper_arm.R', 'DEF-thigh.L', 'DEF-thigh.R']);
    skel.bones[0].updateWorldMatrix(true, true);
    const restParentWorldQ = {};
    const Quat = skel.bones[0].quaternion.constructor;
    for (const defName of limbRoots) {
        const threeName = defName.replace(/\./g, '_');
        const bone = skel.getBoneByName(threeName);
        if (bone?.parent) { const wq = new Quat(); bone.parent.getWorldQuaternion(wq); restParentWorldQ[defName] = wq; }
    }
    let applied = 0;
    const threeData = data.threejs || {};
    for (const [defName, q] of Object.entries(threeData)) {
        const threeName = defName.replace(/\./g, '_');
        const bone = skel.getBoneByName(threeName);
        if (bone) { bone.quaternion.multiply(new Quat(q[0], q[1], q[2], q[3])); applied++; }
    }
    skel.bones[0].updateWorldMatrix(true, true);
    for (const defName of limbRoots) {
        const restPWQ = restParentWorldQ[defName]; if (!restPWQ) continue;
        const threeName = defName.replace(/\./g, '_');
        const bone = skel.getBoneByName(threeName); if (!bone?.parent) continue;
        const posedPWQ = new Quat(); bone.parent.getWorldQuaternion(posedPWQ);
        bone.quaternion.premultiply(posedPWQ.clone().invert().multiply(restPWQ));
    }
    skel.bones[0].updateWorldMatrix(true, true);
    const _correctedLegs = _correctThighsToTPose(skel, poseId);
    console.log(`[Pose] Applied ${poseId}: ${applied} bones (${_correctedLegs} leg corrections)`);
}

function _correctThighsToTPose(skel, poseId) {
    if (!poseId.includes('t-pose') && !poseId.includes('tpose')) return 0;
    const thighPairs = [['DEF-thigh_L', 'DEF-thigh_L_001'], ['DEF-thigh_R', 'DEF-thigh_R_001']];
    let corrected = 0;
    for (const [thighName, childName] of thighPairs) {
        const thigh = skel.getBoneByName(thighName); const child = skel.getBoneByName(childName);
        if (!thigh || !child) continue;
        const Vec3 = thigh.position.constructor; const Quat = thigh.quaternion.constructor;
        const posHead = new Vec3(); const posTail = new Vec3();
        thigh.getWorldPosition(posHead); child.getWorldPosition(posTail);
        const currentDir = posTail.clone().sub(posHead).normalize(); const desiredDir = new Vec3(0, -1, 0);
        if (currentDir.dot(desiredDir) > 0.9999) continue;
        const corrWorld = new Quat().setFromUnitVectors(currentDir, desiredDir);
        const parentWQ = new Quat(); if (thigh.parent) thigh.parent.getWorldQuaternion(parentWQ);
        const parentWQ_inv = parentWQ.clone().invert();
        thigh.quaternion.premultiply(parentWQ_inv.clone().multiply(corrWorld).multiply(parentWQ));
        corrected++;
    }
    return corrected;
}

export function _applyPose(pose) {
    if (pose === state._currentPose) return;
    fetch('/api/ui-pref/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key: 'default_pose', value: pose }) });
    sessionStorage.removeItem(SESSION_KEY);
    window.location.reload();
}

// Register
fn.loadPoseUI = loadPoseUI;
fn.applyPoseFromServer = applyPoseFromServer;
fn._applyPose = _applyPose;
window.__applyPose = _applyPose;
window.__applyPoseRuntime = applyPoseFromServer;
window.__characters = state.characters;
