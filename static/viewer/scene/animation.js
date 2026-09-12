/**
 * Scene Editor -- Animation panel, BVH loading, ground fix, save anim dialog.
 * NOTE: Full implementation migrated from scene_config.js lines 2799-6992.
 * Contains loadAnimationUI, loadBVHAnimation, stopAnimation, applyGroundLevelFix, etc.
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { escapeHtml, _selectedInst } from './utils.js';
import { convertToRigifySkinnedMesh, convertInstToSkinned } from './skeleton.js';
import { Animationsstopp } from '../gemeinsam/animationsstopp.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';
import { Animationsmenue } from './animationsmenue.js';
import { Umaanimation } from './uma/umaanimation.js';
import { Eigenanimation } from './eigenanimation.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Abspielsteuerung } from './abspielsteuerung.js';
import { Figurmerker } from './figurmerker.js';
import { Animationsentfernung } from './animationsentfernung.js';
import { Bvhladen } from './bvhladen.js';

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
    const eigen = Eigenanimation.passt(inst);
    const skelett = (uma || eigen) ? inst.skelett
        : (inst ? inst.rigifySkeleton : state.rigifySkeleton);
    if (uma) {
        Umaanimation.anhalten(inst);     // kein `pose()`: das wäre die Bindpose der GLB
    } else if (eigen) {
        // SMPL und MakeHuman: `pose()` ist hier richtig — ihre Bindpose IST
        // die Ruhelage, die der Server gerechnet hat (`gelenkskelett.py`).
        Eigenanimation.anhalten(inst);
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
    // Der Knopf quittiert den Klick sofort — das Laden dauert Sekunden.
    abspielsteuerung.ladeanzeige();
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
    // SMPL und MakeHuman haben ihr eigenes Skelett und ihre eigenen
    // Hautgewichte. Ohne diesen Zweig liefen sie in den DEF-Weg darunter,
    // und der hängt ihnen das Rigify-Skelett an — 176 fremde Knochen und
    // Hautgewichte für eine andere Topologie (07.09.2026).
    if (Eigenanimation.passt(inst)) {
        try {
            const clip = await Eigenanimation.starten(inst, url, rawBvhText);
            abspielsteuerung.meldung(`${name || url} · ${clip.tracks.length} Spuren · ${clip.duration.toFixed(1)} s`);
        } catch (fehler) {
            abspielsteuerung.meldung(`Fehler: ${fehler.message || fehler}`);
            Protokoll.fehler('Eigenanimation',
                             `Retarget auf ${inst.quelle} fehlgeschlagen`, fehler);
        }
        abspielsteuerung.knoepfeAngleichen();
        return;
    }
    // Eine Figur mit eigener Quelle, aber OHNE Skelett (GarmentCodes eigene
    // Körper ohne SMPL-Topologie, MakeHuman ohne Upstream) bekommt keine
    // Ersatzknochen: Das sagt die Meldung, statt dass ein fremdes Rig
    // stillschweigend einspringt.
    if (inst && Eigenanimation.ZIELE[inst.quelle]) {
        abspielsteuerung.meldung(
            `${inst.quelle}-Figur ohne Skelett — nicht animierbar.`);
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
    // Die beiden HumanBody-Wege stehen in `bvhladen.js`: Retarget auf das
    // Rigify-Skelett, sonst die nackte Skelettvorschau.
    const quelle = { url, name, rawBvhText };
    if (skel) {
        await Bvhladen.retarget(inst, skel, quelle,
                                (text) => abspielsteuerung.meldung(text));
    } else {
        Bvhladen.vorschau(inst, targetMesh, quelle);
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
        // Offene Ordner bleiben offen — der Neubau (nach Umbenennen, Löschen,
        // Speichern) klappte sonst alles zu (Edgar, 12.09.2026).
        const offen = Animationsentfernung.offeneOrdner(tree);
        tree.innerHTML = '';
        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();
        if (catNames.length === 0) { tree.innerHTML = '<div class="leer-hinweis">Keine Animationen</div>'; return; }
        for (const cat of catNames) {
            const anims = categories[cat];
            const {kasten: catDiv, koerper: body} =
                Kategoriekasten.bauen(cat, anims.length, { offen: offen.has(cat) });
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
                // Rechtsklick: umbenennen, verschieben, loeschen (08.09.2026).
                // Nach der Aktion wird der Baum neu geholt — die Datei
                // heisst dann anders oder ist weg. Das Loeschen stoppt
                // dazu die laufende Animation und waehlt den Nachfolger
                // (`Animationsentfernung`, 12.09.2026).
                Animationsmenue.binden(item, cat, anim.name, (aktion) => (
                    aktion === 'delete'
                        ? Animationsentfernung.nach(anim, cat, {
                            eintraege: Animationsentfernung.eintraege(tree),
                            state, fn, merker: Figurmerker,
                            baumNeu: loadAnimationUI,
                            meldung: (text) => abspielsteuerung.meldung(text) })
                        : loadAnimationUI()));
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
