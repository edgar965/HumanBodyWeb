/**
 * Scene Editor -- Pose browser + apply.
 * Exact pose logic from commit 95172c8 (HumanBodyTest).
 */
import { THREE, SESSION_KEY } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { _selectedInst } from './utils.js';
import { convertInstToSkinned } from './skeleton.js';

export async function loadPoseUI() {
    const list = document.getElementById('pose-list');
    const resetBtn = document.getElementById('pose-reset');
    if (!list) return;
    try {
        const resp = await fetch('/api/character/poses/');
        const data = await resp.json();
        list.innerHTML = '';
        for (const [cat, poses] of Object.entries(data.categories || {})) {
            const folder = document.createElement('div');
            folder.className = 'anim-folder';
            const header = document.createElement('div');
            header.className = 'anim-folder-header';
            header.innerHTML = `<span class="chevron">&#9660;</span> ${cat} (${poses.length})`;
            folder.appendChild(header);
            const body = document.createElement('div');
            body.className = 'anim-folder-body';
            for (const pose of poses) {
                const row = document.createElement('div');
                row.className = 'anim-item';
                row.style.cssText = 'padding:4px 8px;cursor:pointer;font-size:0.8rem;';
                row.textContent = pose.name;
                row.addEventListener('click', () => applyPoseFromServer(pose.id));
                body.appendChild(row);
            }
            folder.appendChild(body);
            header.addEventListener('click', () => {
                body.style.display = body.style.display === 'none' ? '' : 'none';
                header.querySelector('.chevron').textContent = body.style.display === 'none' ? '\u25B6' : '\u25BC';
            });
            if (cat !== 'rest_poses') {
                body.style.display = 'none';
                header.querySelector('.chevron').textContent = '\u25B6';
            }
            list.appendChild(folder);
        }
    } catch(e) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Poses nicht verf\u00fcgbar</div>';
    }
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            const inst = _selectedInst();
            if (!inst?.isSkinned) return;
            let skel = null;
            inst.group.traverse(child => {
                if (!skel && child.isSkinnedMesh && child.skeleton) skel = child.skeleton;
            });
            if (!skel || !inst._aPoseBones) return;
            for (const bone of skel.bones) {
                const saved = inst._aPoseBones[bone.name];
                if (saved) bone.quaternion.copy(saved);
            }
        });
    }
}

export async function applyPoseFromServer(poseId) {
    const inst = _selectedInst();
    if (!inst) return;

    // Auto-skin if needed
    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }
    if (!inst.isSkinned) return;

    // Fetch pose data
    const resp = await fetch(`/api/character/pose/${poseId}/`);
    const data = await resp.json();
    if (!data.bones) return;

    // Find skeleton
    let skel = null;
    inst.group.traverse(child => {
        if (!skel && child.isSkinnedMesh && child.skeleton) skel = child.skeleton;
    });
    if (!skel) return;

    // Save A-pose quaternions for reset (first time)
    if (!inst._aPoseBones) {
        inst._aPoseBones = {};
        for (const bone of skel.bones) {
            inst._aPoseBones[bone.name] = bone.quaternion.clone();
        }
    }

    // Reset to A-pose first
    for (const bone of skel.bones) {
        const saved = inst._aPoseBones[bone.name];
        if (saved) bone.quaternion.copy(saved);
    }

    // CharMorph sets fk_limb_follow=0 for arms and thighs: the pose quaternion
    // is in world-space (no parent inheritance). Our DEF bones ARE hierarchical,
    // so we must compensate by undoing the parent's pose contribution.
    const limbRoots = new Set([
        'DEF-upper_arm.L', 'DEF-upper_arm.R',
        'DEF-thigh.L', 'DEF-thigh.R',
    ]);

    // Save REST world quaternions of limb root parents BEFORE any pose
    skel.bones[0].updateWorldMatrix(true, true);
    const restParentWorldQ = {};
    const Quat = skel.bones[0].quaternion.constructor;
    for (const defName of limbRoots) {
        const threeName = defName.replace(/\./g, '_');
        const bone = skel.getBoneByName(threeName);
        if (bone?.parent) {
            const wq = new Quat();
            bone.parent.getWorldQuaternion(wq);
            restParentWorldQ[defName] = wq;
        }
    }

    // Apply pose quaternions to ALL bones
    let applied = 0;
    const threeData = data.threejs || {};
    for (const [defName, q] of Object.entries(threeData)) {
        const threeName = defName.replace(/\./g, '_');
        const bone = skel.getBoneByName(threeName);
        if (bone) {
            const poseQ = new Quat(q[0], q[1], q[2], q[3]);
            bone.quaternion.multiply(poseQ);
            applied++;
        }
    }

    // Compensate limb roots: undo parent pose contribution
    skel.bones[0].updateWorldMatrix(true, true);
    for (const defName of limbRoots) {
        const restPWQ = restParentWorldQ[defName];
        if (!restPWQ) continue;
        const threeName = defName.replace(/\./g, '_');
        const bone = skel.getBoneByName(threeName);
        if (!bone?.parent) continue;

        const posedPWQ = new Quat();
        bone.parent.getWorldQuaternion(posedPWQ);

        // correction = posedPWQ⁻¹ × restPWQ
        const correction = posedPWQ.clone().invert().multiply(restPWQ);
        bone.quaternion.premultiply(correction);
    }

    // T-pose only: additional thigh geometry correction (straight down)
    skel.bones[0].updateWorldMatrix(true, true);
    const _correctedLegs = _correctThighsToTPose(skel, poseId);

    console.log(`[Pose] Applied ${poseId}: ${applied} bones (${_correctedLegs} leg corrections)`);
}

/**
 * Correct thigh bone rotations for T-pose using skeleton geometry.
 * MB-Lab pose quaternions use different bone local axes than Rigify,
 * so we compute the correction from actual world bone directions.
 */
function _correctThighsToTPose(skel, poseId) {
    // Only correct for T-pose (legs straight down)
    if (!poseId.includes('t-pose') && !poseId.includes('tpose')) return 0;

    const thighPairs = [
        ['DEF-thigh_L', 'DEF-thigh_L_001'],
        ['DEF-thigh_R', 'DEF-thigh_R_001'],
    ];

    let corrected = 0;
    for (const [thighName, childName] of thighPairs) {
        const thigh = skel.getBoneByName(thighName);
        const child = skel.getBoneByName(childName);
        if (!thigh || !child) continue;

        const Vec3 = thigh.position.constructor;
        const Quat = thigh.quaternion.constructor;

        // Get current world positions
        const posHead = new Vec3();
        const posTail = new Vec3();
        thigh.getWorldPosition(posHead);
        child.getWorldPosition(posTail);

        const currentDir = posTail.clone().sub(posHead).normalize();
        const desiredDir = new Vec3(0, -1, 0);

        // Skip if already close enough
        if (currentDir.dot(desiredDir) > 0.9999) continue;

        // World-space correction rotation
        const corrWorld = new Quat().setFromUnitVectors(currentDir, desiredDir);

        // Convert to parent space: parentSpaceCorr = parentWQ⁻¹ × corrWorld × parentWQ
        const parentWQ = new Quat();
        if (thigh.parent) thigh.parent.getWorldQuaternion(parentWQ);
        const parentWQ_inv = parentWQ.clone().invert();
        const parentSpaceCorr = parentWQ_inv.clone().multiply(corrWorld).multiply(parentWQ);

        thigh.quaternion.premultiply(parentSpaceCorr);
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
