/**
 * Scene Editor -- Animation panel, BVH loading, ground fix, save anim dialog.
 * NOTE: Full implementation migrated from scene_config.js lines 2799-6992.
 * Contains loadAnimationUI, loadBVHAnimation, stopAnimation, applyGroundLevelFix, etc.
 */
import { THREE, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { escapeHtml, _selectedInst } from './utils.js';
import { convertToRigifySkinnedMesh, convertInstToSkinned } from './skeleton.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { Animationsstopp } from '../gemeinsam/animationsstopp.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';
import { Umaanimation } from './uma/umaanimation.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Abspielsteuerung } from './abspielsteuerung.js';
import { Figurmerker } from './figurmerker.js';

/** Play/Stop/Zeitleiste — und Play meint die ausgewählte Figur (Klassendoku dort). */
const abspielsteuerung = new Abspielsteuerung(state, fn);

export function stopAnimation(destroy = false) {
    Animationsstopp.aktion(state, destroy);
    Animationsstopp.mischer(state, destroy);
    // Das Skelett der animierten Figur — auf dieser Seite kann das eine von
    // mehreren Instanzen sein. Genau darin unterscheidet sich diese Fassung
    // von der des Einzel-Viewers; alles andere kommt aus `Animationsstopp`.
    const inst = state._animatedCharId
        ? state.characters.get(state._animatedCharId) : null;
    const uma = !!inst && inst.quelle === 'uma';
    const skelett = uma ? inst.skelett : (inst ? inst.rigifySkeleton : state.rigifySkeleton);
    if (uma) {
        Umaanimation.anhalten(inst);     // kein `pose()`: das wäre die Bindpose der GLB
    } else if (inst ? (inst.isSkinned && skelett) : (state.isSkinned && skelett)) {
        skelett.skeleton.pose();
    }
    Animationsstopp.hilfslinien(state);
    Animationsstopp.rigZeigen(state, skelett);
    state._animatedCharId = null;
    state.playing = false;
    state.currentAnimUrl = '';
    state.currentAnimBvhText = '';
    state.currentAnimGroundFixed = false;
    abspielsteuerung.knoepfeAngleichen();   // auch wenn ein Regler oder ein Umschalten angehalten hat
}

export async function loadBVHAnimation(url, name, fc, rawBvhText = null) {
    stopAnimation(true);
    state.currentAnimUrl = url;
    const groundChk = document.getElementById('scene-ground-fix');
    state.currentAnimGroundFixed = groundChk ? groundChk.checked : false;
    const inst = _selectedInst();
    abspielsteuerung.meldung(`Retarget läuft: ${name || url} …`);
    if (inst && inst.quelle === 'uma') {
        try {
            const clip = await Umaanimation.starten(inst, url, rawBvhText);
            abspielsteuerung.meldung(`${name || url} · ${clip.tracks.length} Spuren · ${clip.duration.toFixed(1)} s`);
        } catch (fehler) {
            abspielsteuerung.meldung(`Fehler: ${fehler.message || fehler}`);
            Protokoll.fehler('Umaanimation', 'Retarget auf UMA fehlgeschlagen', fehler);
        }
        abspielsteuerung.knoepfeAngleichen();
        return;
    }
    const targetMesh = inst ? inst.bodyMesh : state.bodyMesh;
    if (!targetMesh) {
        abspielsteuerung.meldung('Keine Figur ausgewählt — erst eine Figur anklicken.');
        return;
    }
    let skel = null;
    if (state.rigifySkeletonData && state.skinWeightData) {
        if (inst) { if (!inst.isSkinned) convertInstToSkinned(inst); }
        else { if (!state.isSkinned) convertToRigifySkinnedMesh(); }
        skel = inst ? inst.rigifySkeleton : state.rigifySkeleton;
    }
    if (skel) {
        const bMesh = inst ? inst.bodyMesh : state.bodyMesh;
        state._animatedCharId = inst ? inst.id : null;
        let bodyH = 1.68;
        const bb = new THREE.Box3().setFromObject(bMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
        try {
            let clip;
            const wahl = { bodyHeight: bodyH, deltaNorm: state._sceneDeltaNorm };
            if (rawBvhText) {
                clip = await fetchRetargetedClipFromText(rawBvhText, skel, wahl);
                state.currentAnimBvhText = rawBvhText;
            } else {
                clip = await fetchRetargetedClipFromUrl(url, skel, wahl);
                // Der Rohtext wird fuer "Boden richten" und den Export
                // gebraucht; ohne ihn bleiben beide Knoepfe wirkungslos.
                state.currentAnimBvhText = await Serverabruf.text(
                    url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now())
                    .catch(() => '');
            }
            if (!state.skeletonHelper) {
                state.skeletonHelper = Skelettanzeige.bauen(state.scene, skel.rootBone, state.rigVisible);
            }
            state.mixer = new THREE.AnimationMixer(bMesh);
            state.currentAction = state.mixer.clipAction(clip);
            state.currentAction.play(); state.playing = true;
            abspielsteuerung.meldung(`${name || url} · ${clip.tracks.length} Spuren · ${clip.duration.toFixed(1)} s`);
        } catch (e) {
            abspielsteuerung.meldung(`Fehler: ${e.message || e}`);
            console.error('[ANIM] Retarget failed:', e);
        }
    } else {
        // Fallback BVH preview
        const handleBvhFallback = (result, text) => {
            state.currentAnimBvhText = text;
            const bvhBones = result.skeleton.bones; if (bvhBones.length === 0) return;
            const rootBone = bvhBones[0]; rootBone.updateWorldMatrix(true, true);
            const skelBox = new THREE.Box3(); const tmpVec = new THREE.Vector3();
            bvhBones.forEach(b => { b.updateWorldMatrix(true, false); b.getWorldPosition(tmpVec);
                skelBox.expandByPoint(tmpVec); });
            let bodyHeight = 1.75; if (targetMesh) { const bb = new THREE.Box3().setFromObject(targetMesh);
                if (!bb.isEmpty()) bodyHeight = bb.max.y - bb.min.y; }
            const scale = bodyHeight / Math.max(skelBox.max.y - skelBox.min.y, 0.01);
            state.skelWrapper = new THREE.Group();
            state.skelWrapper.scale.set(scale, scale, scale);
            state.skelWrapper.add(rootBone);
            if (inst) state.skelWrapper.position.copy(inst.group.position);
            state.scene.add(state.skelWrapper);
            if (state.skeletonHelper) state.scene.remove(state.skeletonHelper);
            state.skeletonHelper = Skelettanzeige.bauen(state.scene, rootBone, state.rigVisible);
            state.mixer = new THREE.AnimationMixer(rootBone);
            state.currentAction = state.mixer.clipAction(result.clip);
            state.currentAction.play(); state.playing = true; state._animatedCharId = inst ? inst.id : null;
        };
        if (rawBvhText) { handleBvhFallback(state.bvhLoader.parse(rawBvhText), rawBvhText); }
        else {
            const fileLoader = new THREE.FileLoader(state.bvhLoader.manager);
            fileLoader.load(url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now(),
                (text) => { handleBvhFallback(state.bvhLoader.parse(text), text);
                    }, undefined, (err) => { console.error('BVH load failed:', err); });
        }
    }
    abspielsteuerung.knoepfeAngleichen();
}

/**
 * In der Bibliothek die Animation der ausgewählten Figur hervorheben — oder
 * keine, wenn die Figur noch keine gewählt hat. Die Markierung gehört zur
 * Figur, nicht zur Seite (Figurmerker).
 */
export function animationMarkieren(name) {
    const baum = document.getElementById('anim-tree');
    if (!baum) return false;
    let gefunden = false;
    for (const eintrag of baum.querySelectorAll('.anim-item')) {
        const passt = !!name && eintrag.dataset.name === name;
        eintrag.classList.toggle('active', passt);
        gefunden = gefunden || passt;
    }
    return gefunden;
}

export async function applyGroundLevelFix() {
    if (!state.currentAnimBvhText) { alert('Keine Animation geladen.'); return; }
    const chk = document.getElementById('scene-ground-fix'); if (chk) chk.checked = true;
    state.currentAnimGroundFixed = true;
    // Simplified ground fix -- modifies BVH Y root channel
    const lines = state.currentAnimBvhText.split('\n');
    let yPosChannel = -1, foundRoot = false;
    for (let i = 0; i < lines.length; i++) { const t = lines[i].trim(); if (t.startsWith('ROOT ')) { foundRoot = true;
        continue; } if (foundRoot && t.startsWith('CHANNELS')) { const parts = t.split(/\s+/); for (let c = 2;
            c < parts.length; c++) { if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; } } break; } }
    if (yPosChannel < 0) { alert('Yposition nicht gefunden.'); return; }
    let motionIdx = lines.findIndex(l => l.trim() === 'MOTION'); if (motionIdx < 0) return;
    let frameTime = 1/30, dataStart = motionIdx + 1;
    while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) { const t = lines[dataStart].trim();
        if (t.startsWith('Frame Time:')) frameTime = parseFloat(t.split(':')[1].trim()); dataStart++; }
    const frameLineIdx = []; for (let i = dataStart; i < lines.length;
        i++) { if (lines[i].trim().match(/^[\d\-\.]/)) frameLineIdx.push(i); }
    if (!frameLineIdx.length) return;
    const parsed = state.bvhLoader.parse(state.currentAnimBvhText);
    const bones = parsed.skeleton.bones, rootBone = bones[0];
    const tmpMixer = new THREE.AnimationMixer(rootBone), tmpAction = tmpMixer.clipAction(parsed.clip);
    tmpAction.play(); const tmpV = new THREE.Vector3(); let corrected = 0;
    for (let f = 0; f < frameLineIdx.length; f++) {
        tmpMixer.setTime(f * frameTime); rootBone.updateWorldMatrix(true, true);
        let minY = Infinity; for (const b of bones) { b.getWorldPosition(tmpV); if (tmpV.y < minY) minY = tmpV.y; }
        if (Math.abs(minY) > 0.001) { const vals = lines[frameLineIdx[f]].trim().split(/\s+/);
            vals[yPosChannel] = (parseFloat(vals[yPosChannel]) - minY).toFixed(6);
                lines[frameLineIdx[f]] = vals.join(' '); corrected++; }
    }
    tmpAction.stop(); tmpMixer.stopAllAction();
    if (corrected === 0) { alert('Bereits auf Bodenniveau.'); return; }
    state.currentAnimBvhText = lines.join('\n');
    if (state.currentAnimUrl) {
        const urlPath = state.currentAnimUrl.replace(/\?.*$/, '');
        const bvhMatch = urlPath.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)/);
        const saveBody = bvhMatch ? { category: bvhMatch[1], name: bvhMatch[2],
            bvh_text: state.currentAnimBvhText } : { path: urlPath, bvh_text: state.currentAnimBvhText };
        try { const resp = await fetch('/api/character/save-bvh-text/', { method: 'POST',
            headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(saveBody) });
            if (resp.ok) loadBVHAnimation(state.currentAnimUrl + (state.currentAnimUrl.includes('?') ? '&' : '?')
                + '_ground=' + Date.now(), state.currentAnimName, 0);
            else loadBVHAnimation(state.currentAnimUrl, state.currentAnimName, 0, state.currentAnimBvhText);
        } catch (e) { loadBVHAnimation(state.currentAnimUrl, state.currentAnimName, 0, state.currentAnimBvhText); }
    }
    alert(`Bodenniveau-Fix: ${corrected} Frames korrigiert.`);
}

export function openSaveAnimDialog() {
    if (!state.currentAnimBvhText) { alert('Keine Animation geladen.'); return; }
    let category = '', baseName = '';
    const m = state.currentAnimUrl.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)\/?/);
    if (m) { category = decodeURIComponent(m[1]); baseName = decodeURIComponent(m[2]); } else { category = 'Custom';
        baseName = state.currentAnimName || 'animation'; }
    let suggestedName = baseName;
    if (state.currentAnimGroundFixed && !baseName.endsWith('_ground')) suggestedName = baseName + '_ground';
    document.getElementById('save-anim-category').value = category;
    document.getElementById('save-anim-name').value = suggestedName;
    const dlg = document.getElementById('save-anim-dialog'); dlg.classList.add('visible');
}

export function _initSaveAnimDialog() {
    const dlg = document.getElementById('save-anim-dialog'); if (!dlg) return;
    dlg.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click',
        () => dlg.classList.remove('visible')));
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.classList.remove('visible'); });
    document.getElementById('save-anim-confirm')?.addEventListener('click', async () => {
        const category = document.getElementById('save-anim-category').value.trim();
        const name = document.getElementById('save-anim-name').value.trim();
        if (!name) { alert('Bitte Dateiname eingeben.'); return; }
        try {
            const data = await Serverabruf.senden('/api/character/animation/save/',
                { category, name, bvh_content: state.currentAnimBvhText });
            if (!data.ok) {
                alert('Fehler: ' + (data.error || 'Unbekannt'));
                return;
            }
            dlg.classList.remove('visible');
            state.currentAnimUrl = `/api/character/bvh/`
                + `${encodeURIComponent(category)}/${encodeURIComponent(name)}/`;
            state.currentAnimName = name;
            loadAnimationUI();
        } catch (e) { alert('Speichern fehlgeschlagen: ' + e.message); }
    });
}

export async function loadAnimationUI() {
    try {
        const data = await Serverabruf.json('/api/character/animations/');
        const tree = document.getElementById('anim-tree'); if (!tree) return;
        tree.innerHTML = '';
        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();
        if (catNames.length === 0) { tree.innerHTML = '<div class="leer-hinweis">Keine Animationen</div>'; return; }
        for (const cat of catNames) {
            const anims = categories[cat];
            const {kasten: catDiv, koerper: body} =
                Kategoriekasten.bauen(cat, anims.length);
            for (const anim of anims) {
                const item = document.createElement('div'); item.className = 'anim-item';
                item.innerHTML = `<span>${escapeHtml(anim.name)}</span><span
                    class="frames">${anim.frames || ''}f</span>`;
                // Name und Adresse am Eintrag: `Abspielsteuerung.wahlFuer` liest
                // sie, wenn Play auf einer Figur ohne gemerkte Animation gedrückt wird.
                item.dataset.name = anim.name;
                item.dataset.url = anim.url;
                item.dataset.category = cat;
                item.addEventListener('click', () => {
                    animationMarkieren(anim.name);
                    Figurmerker.animationMerken(state.selectedCharacterId,
                                                { name: anim.name, url: anim.url, category: cat });
                    state.currentAnimName = anim.name;
                    loadBVHAnimation(anim.url, anim.name, anim.frames || 0);
                });
                body.appendChild(item);
            }
            tree.appendChild(catDiv);
        }
        animationMarkieren(Figurmerker.animation(state.selectedCharacterId)?.name || null);
    } catch (e) { const tree = document.getElementById('anim-tree');
        if (tree) tree.innerHTML = '<div class="leer-hinweis">Animationen nicht verfügbar</div>'; }
    // Einmal — `loadAnimationUI` läuft auch nach „Animation speichern" noch
    // einmal; früher hingen danach zwei Zuhörer am Play-Knopf.
    abspielsteuerung.verdrahten();
}

fn.loadAnimationUI = loadAnimationUI;
fn.loadBVHAnimation = loadBVHAnimation;
fn.stopAnimation = stopAnimation;
fn.animationMarkieren = animationMarkieren;
fn.abspielen = (ersatz) => abspielsteuerung.abspielen(ersatz);
fn.applyGroundLevelFix = applyGroundLevelFix;
fn.openSaveAnimDialog = openSaveAnimDialog;
fn._initSaveAnimDialog = _initSaveAnimDialog;
