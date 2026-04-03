/**
 * Scene Editor -- Animation panel, BVH loading, ground fix, save anim dialog.
 * NOTE: Full implementation migrated from scene_config.js lines 2799-6992.
 * Contains loadAnimationUI, loadBVHAnimation, stopAnimation, applyGroundLevelFix, etc.
 */
import { THREE, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText, buildRigifySkeleton } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { escapeHtml, _selectedInst, getCSRFToken } from './utils.js';
import { convertToRigifySkinnedMesh, convertInstToSkinned } from './skeleton.js';

export function stopAnimation(destroy = false) {
    if (state.currentAction) { state.currentAction.stop(); state.currentAction.reset(); if (destroy) state.currentAction = null; }
    if (state.mixer && destroy) { state.mixer.stopAllAction(); state.mixer = null; }
    if (state._animatedCharId) {
        const inst = state.characters.get(state._animatedCharId);
        if (inst && inst.isSkinned && inst.rigifySkeleton) inst.rigifySkeleton.skeleton.pose();
    } else {
        if (state.isSkinned && state.rigifySkeleton) state.rigifySkeleton.skeleton.pose();
    }
    if (state.skelWrapper) { state.scene.remove(state.skelWrapper); state.skelWrapper = null; }
    if (state.skeletonHelper) { state.scene.remove(state.skeletonHelper); state.skeletonHelper = null; }
    const activeSkel = state._animatedCharId ? state.characters.get(state._animatedCharId)?.rigifySkeleton : state.rigifySkeleton;
    if (state.rigVisible && activeSkel) {
        state.skeletonHelper = new THREE.SkeletonHelper(activeSkel.rootBone);
        state.skeletonHelper.material.depthTest = false; state.skeletonHelper.material.depthWrite = false;
        state.skeletonHelper.material.color.set(0x00ffaa); state.skeletonHelper.renderOrder = 999;
        state.scene.add(state.skeletonHelper);
    }
    state._animatedCharId = null; state.playing = false; state.currentAnimUrl = ''; state.currentAnimBvhText = ''; state.currentAnimGroundFixed = false;
}

export async function loadBVHAnimation(url, name, fc, rawBvhText = null) {
    stopAnimation(true);
    state.currentAnimUrl = url;
    const groundChk = document.getElementById('scene-ground-fix');
    state.currentAnimGroundFixed = groundChk ? groundChk.checked : false;
    const inst = _selectedInst();
    const targetMesh = inst ? inst.bodyMesh : state.bodyMesh;
    if (!targetMesh) return;
    let skel = null;
    if (state.rigifySkeletonData && state.skinWeightData) {
        if (inst) { if (!inst.isSkinned) convertInstToSkinned(inst); }
        else { if (!state.isSkinned) convertToRigifySkinnedMesh(); }
        skel = inst ? inst.rigifySkeleton : state.rigifySkeleton;
    }
    if (skel) {
        const bMesh = inst ? inst.bodyMesh : state.bodyMesh;
        state._animatedCharId = inst ? inst.id : null;
        let bodyH = 1.68; const bb = new THREE.Box3().setFromObject(bMesh); if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
        try {
            let clip;
            if (rawBvhText) { clip = await fetchRetargetedClipFromText(rawBvhText, skel, { bodyHeight: bodyH, deltaNorm: state._sceneDeltaNorm }); state.currentAnimBvhText = rawBvhText; }
            else { clip = await fetchRetargetedClipFromUrl(url, skel, { bodyHeight: bodyH, deltaNorm: state._sceneDeltaNorm }); try { const tr = await fetch(url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now()); state.currentAnimBvhText = await tr.text(); } catch { state.currentAnimBvhText = ''; } }
            if (!state.skeletonHelper) {
                state.skeletonHelper = new THREE.SkeletonHelper(skel.rootBone);
                state.skeletonHelper.material.depthTest = false; state.skeletonHelper.material.depthWrite = false;
                state.skeletonHelper.material.color.set(0x00ffaa); state.skeletonHelper.renderOrder = 999;
                state.skeletonHelper.visible = state.rigVisible;
                state.scene.add(state.skeletonHelper);
            }
            state.mixer = new THREE.AnimationMixer(bMesh);
            state.currentAction = state.mixer.clipAction(clip);
            state.currentAction.play(); state.playing = true;
        } catch (e) { console.error('[ANIM] Retarget failed:', e); }
    } else {
        // Fallback BVH preview
        const handleBvhFallback = (result, text) => {
            state.currentAnimBvhText = text;
            const bvhBones = result.skeleton.bones; if (bvhBones.length === 0) return;
            const rootBone = bvhBones[0]; rootBone.updateWorldMatrix(true, true);
            const skelBox = new THREE.Box3(); const tmpVec = new THREE.Vector3();
            bvhBones.forEach(b => { b.updateWorldMatrix(true, false); b.getWorldPosition(tmpVec); skelBox.expandByPoint(tmpVec); });
            let bodyHeight = 1.75; if (targetMesh) { const bb = new THREE.Box3().setFromObject(targetMesh); if (!bb.isEmpty()) bodyHeight = bb.max.y - bb.min.y; }
            const scale = bodyHeight / Math.max(skelBox.max.y - skelBox.min.y, 0.01);
            state.skelWrapper = new THREE.Group(); state.skelWrapper.scale.set(scale, scale, scale); state.skelWrapper.add(rootBone);
            if (inst) state.skelWrapper.position.copy(inst.group.position);
            state.scene.add(state.skelWrapper);
            if (state.skeletonHelper) state.scene.remove(state.skeletonHelper);
            state.skeletonHelper = new THREE.SkeletonHelper(rootBone);
            state.skeletonHelper.material.depthTest = false; state.skeletonHelper.material.depthWrite = false;
            state.skeletonHelper.material.color.set(0x00ffaa); state.skeletonHelper.renderOrder = 999;
            state.skeletonHelper.visible = state.rigVisible;
            state.scene.add(state.skeletonHelper);
            state.mixer = new THREE.AnimationMixer(rootBone);
            state.currentAction = state.mixer.clipAction(result.clip);
            state.currentAction.play(); state.playing = true; state._animatedCharId = inst ? inst.id : null;
        };
        if (rawBvhText) { handleBvhFallback(state.bvhLoader.parse(rawBvhText), rawBvhText); }
        else {
            const fileLoader = new THREE.FileLoader(state.bvhLoader.manager);
            fileLoader.load(url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now(), (text) => { handleBvhFallback(state.bvhLoader.parse(text), text); }, undefined, (err) => { console.error('BVH load failed:', err); });
        }
    }
    const _pb = document.getElementById('anim-play');
    if (_pb) _pb.innerHTML = state.playing ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
}

export async function applyGroundLevelFix() {
    if (!state.currentAnimBvhText) { alert('Keine Animation geladen.'); return; }
    const chk = document.getElementById('scene-ground-fix'); if (chk) chk.checked = true;
    state.currentAnimGroundFixed = true;
    // Simplified ground fix -- modifies BVH Y root channel
    const lines = state.currentAnimBvhText.split('\n');
    let yPosChannel = -1, foundRoot = false;
    for (let i = 0; i < lines.length; i++) { const t = lines[i].trim(); if (t.startsWith('ROOT ')) { foundRoot = true; continue; } if (foundRoot && t.startsWith('CHANNELS')) { const parts = t.split(/\s+/); for (let c = 2; c < parts.length; c++) { if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; } } break; } }
    if (yPosChannel < 0) { alert('Yposition nicht gefunden.'); return; }
    let motionIdx = lines.findIndex(l => l.trim() === 'MOTION'); if (motionIdx < 0) return;
    let frameTime = 1/30, dataStart = motionIdx + 1;
    while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) { const t = lines[dataStart].trim(); if (t.startsWith('Frame Time:')) frameTime = parseFloat(t.split(':')[1].trim()); dataStart++; }
    const frameLineIdx = []; for (let i = dataStart; i < lines.length; i++) { if (lines[i].trim().match(/^[\d\-\.]/)) frameLineIdx.push(i); }
    if (!frameLineIdx.length) return;
    const parsed = state.bvhLoader.parse(state.currentAnimBvhText);
    const bones = parsed.skeleton.bones, rootBone = bones[0];
    const tmpMixer = new THREE.AnimationMixer(rootBone), tmpAction = tmpMixer.clipAction(parsed.clip);
    tmpAction.play(); const tmpV = new THREE.Vector3(); let corrected = 0;
    for (let f = 0; f < frameLineIdx.length; f++) {
        tmpMixer.setTime(f * frameTime); rootBone.updateWorldMatrix(true, true);
        let minY = Infinity; for (const b of bones) { b.getWorldPosition(tmpV); if (tmpV.y < minY) minY = tmpV.y; }
        if (Math.abs(minY) > 0.001) { const vals = lines[frameLineIdx[f]].trim().split(/\s+/); vals[yPosChannel] = (parseFloat(vals[yPosChannel]) - minY).toFixed(6); lines[frameLineIdx[f]] = vals.join(' '); corrected++; }
    }
    tmpAction.stop(); tmpMixer.stopAllAction();
    if (corrected === 0) { alert('Bereits auf Bodenniveau.'); return; }
    state.currentAnimBvhText = lines.join('\n');
    if (state.currentAnimUrl) {
        const urlPath = state.currentAnimUrl.replace(/\?.*$/, '');
        const bvhMatch = urlPath.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)/);
        const saveBody = bvhMatch ? { category: bvhMatch[1], name: bvhMatch[2], bvh_text: state.currentAnimBvhText } : { path: urlPath, bvh_text: state.currentAnimBvhText };
        try { const resp = await fetch('/api/character/save-bvh-text/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(saveBody) });
            if (resp.ok) loadBVHAnimation(state.currentAnimUrl + (state.currentAnimUrl.includes('?') ? '&' : '?') + '_ground=' + Date.now(), state.currentAnimName, 0);
            else loadBVHAnimation(state.currentAnimUrl, state.currentAnimName, 0, state.currentAnimBvhText);
        } catch (e) { loadBVHAnimation(state.currentAnimUrl, state.currentAnimName, 0, state.currentAnimBvhText); }
    }
    alert(`Bodenniveau-Fix: ${corrected} Frames korrigiert.`);
}

export function openSaveAnimDialog() {
    if (!state.currentAnimBvhText) { alert('Keine Animation geladen.'); return; }
    let category = '', baseName = '';
    const m = state.currentAnimUrl.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)\/?/);
    if (m) { category = decodeURIComponent(m[1]); baseName = decodeURIComponent(m[2]); } else { category = 'Custom'; baseName = state.currentAnimName || 'animation'; }
    let suggestedName = baseName;
    if (state.currentAnimGroundFixed && !baseName.endsWith('_ground')) suggestedName = baseName + '_ground';
    document.getElementById('save-anim-category').value = category;
    document.getElementById('save-anim-name').value = suggestedName;
    const dlg = document.getElementById('save-anim-dialog'); dlg.classList.add('visible');
}

export function _initSaveAnimDialog() {
    const dlg = document.getElementById('save-anim-dialog'); if (!dlg) return;
    dlg.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click', () => dlg.classList.remove('visible')));
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.classList.remove('visible'); });
    document.getElementById('save-anim-confirm')?.addEventListener('click', async () => {
        const category = document.getElementById('save-anim-category').value.trim();
        const name = document.getElementById('save-anim-name').value.trim();
        if (!name) { alert('Bitte Dateiname eingeben.'); return; }
        try {
            const resp = await fetch('/api/character/animation/save/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }, body: JSON.stringify({ category, name, bvh_content: state.currentAnimBvhText }) });
            const data = await resp.json();
            if (data.ok) { dlg.classList.remove('visible'); state.currentAnimUrl = `/api/character/bvh/${encodeURIComponent(category)}/${encodeURIComponent(name)}/`; state.currentAnimName = name; loadAnimationUI(); }
            else alert('Fehler: ' + (data.error || 'Unbekannt'));
        } catch (e) { alert('Speichern fehlgeschlagen: ' + e.message); }
    });
}

export async function loadAnimationUI() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('anim-tree'); if (!tree) return;
        tree.innerHTML = '';
        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();
        if (catNames.length === 0) { tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen</div>'; return; }
        for (const cat of catNames) {
            const anims = categories[cat];
            const catDiv = document.createElement('div'); catDiv.className = 'anim-category';
            const header = document.createElement('div'); header.className = 'anim-category-header';
            header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span><span>${escapeHtml(cat)}</span><span class="cat-count">${anims.length}</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            catDiv.appendChild(header);
            const body = document.createElement('div'); body.className = 'anim-category-body';
            for (const anim of anims) {
                const item = document.createElement('div'); item.className = 'anim-item';
                item.innerHTML = `<span>${escapeHtml(anim.name)}</span><span class="frames">${anim.frames || ''}f</span>`;
                item.addEventListener('click', () => { tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active')); item.classList.add('active'); state.currentAnimName = anim.name; loadBVHAnimation(anim.url, anim.name, anim.frames || 0); });
                body.appendChild(item);
            }
            catDiv.appendChild(body); tree.appendChild(catDiv);
        }
    } catch (e) { const tree = document.getElementById('anim-tree'); if (tree) tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);">Animationen nicht verf\u00fcgbar</div>'; }
    // Playback controls binding
    const playBtn = document.getElementById('anim-play');
    if (playBtn) playBtn.addEventListener('click', () => { if (!state.currentAction) return; state.playing = !state.playing; if (state.playing) { if (!state.currentAction.isRunning()) state.currentAction.play(); state.currentAction.paused = false; } else state.currentAction.paused = true; playBtn.innerHTML = state.playing ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>'; });
    const stopBtn = document.getElementById('anim-stop');
    if (stopBtn) stopBtn.addEventListener('click', () => { stopAnimation(false); if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>'; state.currentAnimName = ''; });
    const timeline = document.getElementById('anim-timeline');
    if (timeline) timeline.addEventListener('input', () => { if (state.currentAction?.getClip()) { const dur = state.currentAction.getClip().duration; state.currentAction.time = (parseInt(timeline.value) / 100) * dur; if (state.mixer) state.mixer.update(0); } });
    const speedSlider = document.getElementById('anim-speed');
    const speedLabel = document.getElementById('speed-label');
    if (speedSlider && speedLabel) speedSlider.addEventListener('input', () => { const speed = parseInt(speedSlider.value) / 100; speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`; if (state.mixer) state.mixer.timeScale = speed; });
    const deltaSel = document.getElementById('scene-delta-norm');
    if (deltaSel) deltaSel.addEventListener('change', () => { const v = deltaSel.value; state._sceneDeltaNorm = v === 'auto' ? undefined : v === '1'; if (state.currentAnimUrl) loadBVHAnimation(state.currentAnimUrl, state.currentAnimName, 0, state.currentAnimBvhText || null); });
    const groundChk = document.getElementById('scene-ground-fix');
    if (groundChk) groundChk.addEventListener('change', () => { state.currentAnimGroundFixed = groundChk.checked; });
    document.getElementById('anim-save-btn')?.addEventListener('click', () => { if (!state.currentAnimBvhText && !state.currentAnimUrl) { alert('Keine Animation geladen.'); return; } openSaveAnimDialog(); });
}

fn.loadAnimationUI = loadAnimationUI;
fn.loadBVHAnimation = loadBVHAnimation;
fn.stopAnimation = stopAnimation;
fn.applyGroundLevelFix = applyGroundLevelFix;
fn.openSaveAnimDialog = openSaveAnimDialog;
fn._initSaveAnimDialog = _initSaveAnimDialog;
