/**
 * Bodenfix und Speichern der angewandten Effekte.
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import * as THREE from 'three';
import { _fixedPos } from './werkzeug_position.js';
import { _gaussSmooth } from './werkzeug_glaettung.js';


export async function saveBvhWithEffects() {
    // Collect all clips
    const clips = [];
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (const clip of track.clips) {
            if (clip.category && clip.name) clips.push(clip);
        }
    }
    if (clips.length === 0) {
        const pi = fn.getPreviewInfo ? fn.getPreviewInfo() : null;
        if (pi && pi.category && pi.name) clips.push({ category: pi.category, name: pi.name });
    }
    if (clips.length === 0) { alert('Keine Animation geladen.'); return; }

    // Build effects list
    const effects = {};
    if (_gaussSmooth.active) effects.sigma = _gaussSmooth.sigma;
    if (_fixedPos.active) effects.fixed_radius = _fixedPos.radius;

    if (Object.keys(effects).length === 0) {
        alert('Keine Effekte aktiv (Smooth oder Feste Position einschalten).');
        return;
    }

    const desc = [];
    if (effects.sigma) desc.push(`Smooth σ=${effects.sigma}`);
    if (effects.fixed_radius) desc.push(`Feste Position r=${(effects.fixed_radius * 100).toFixed(0)}cm`);

    if (!confirm(`BVH speichern mit: ${desc.join(', ')}\n\n${clips.length} Clip(s) werden überschrieben!`)) return;

    let saved = 0;
    for (const clip of clips) {
        try {
            const resp = await fetch('/api/retarget/save-bvh-effects/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: clip.category, name: clip.name, ...effects }),
            });
            const result = await resp.json();
            if (result.ok) saved++;
            else console.error(`Save failed for ${clip.name}:`, result.error);
        } catch (e) { console.error(`Save failed for ${clip.name}:`, e); }
    }

    // Clear caches so next load picks up saved version
    _gaussSmooth.origClips.clear();
    _fixedPos.origData.clear();
    alert(`Gespeichert: ${saved}/${clips.length} Clip(s) mit ${desc.join(', ')}`);
    console.log(`[BVH Studio] Saved with effects: ${saved} clips, ${desc.join(', ')}`);
}

export async function groundFixSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) { alert('Clip auswählen.'); return; }
    pushUndo('Bodenniveau');
    const track = state.project.tracks[state.selectedTrackIdx];
    const clip = track.clips[state.selectedClipIdx];
    if (!clip.animClip || !track.skeleton) { alert('Clip oder Skeleton nicht geladen.'); return; }

    // Read desired ground offset from Tools panel (default 0.03m = 3cm)
    const groundOffset = parseFloat(document.getElementById('tool-ground-offset')?.value) || 0.03;

    const skel = track.skeleton;
    const bones = skel.skeleton.bones;
    const rootBone = skel.rootBone;

    // Create temporary mixer to evaluate each frame
    const tmpMixer = new THREE.AnimationMixer(track.mesh);
    const tmpAction = tmpMixer.clipAction(clip.animClip);
    tmpAction.play();

    const tmpV = new THREE.Vector3();

    // Find position track for root bone
    let posTrack = null;
    for (const t of clip.animClip.tracks) {
        if (t.name.includes('.position')) { posTrack = t; break; }
    }
    if (!posTrack) {
        alert('Kein Position-Track gefunden.');
        tmpAction.stop(); tmpMixer.stopAllAction();
        return;
    }

    // Identify foot bones (left + right)
    const footBones = bones.filter(b => {
        const n = b.name.toLowerCase();
        return n.includes('foot') || n.includes('toe') || n.includes('heel');
    });
    if (footBones.length === 0) {
        alert('Keine Fuß-Knochen gefunden.');
        tmpAction.stop(); tmpMixer.stopAllAction();
        return;
    }
    console.log(`[BVH Studio] Ground fix: ${footBones.length} foot bones: ${footBones.map(b => b.name).join(', ')}`);

    const nKeys = posTrack.times.length;
    let corrected = 0;

    for (let f = 0; f < nKeys; f++) {
        const t = posTrack.times[f];
        tmpMixer.setTime(t);
        rootBone.updateWorldMatrix(true, true);

        // Find lowest foot bone Y (considering both left and right)
        let minY = Infinity;
        for (const b of footBones) {
            b.getWorldPosition(tmpV);
            if (tmpV.y < minY) minY = tmpV.y;
        }

        // If foot is below ground (minY < 0): correct to exactly 0
        // If foot is above ground (minY >= 0): correct to groundOffset
        const target = minY < 0 ? 0 : groundOffset;
        const correction = minY - target;
        if (Math.abs(correction) > 0.001) {
            const idx = f * 3 + 1;  // Y component (position is vec3: x,y,z)
            posTrack.values[idx] -= correction;
            corrected++;
        }
    }

    tmpAction.stop();
    tmpMixer.stopAllAction();

    clip.groundFix = true;
    fn.updateProperties();

    if (corrected === 0) {
        console.log(`[BVH Studio] ${clip.name}: bereits auf Bodenniveau.`);
        fn.applyPlayhead();
        return;
    }

    console.log(`[BVH Studio] Ground fix: ${corrected}/${nKeys} Frames korrigiert für ${clip.name}`);
    fn.applyPlayhead();

    // Save corrected BVH to disk
    try {
        // Fetch original BVH text
        const bvhUrl = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
        const bvhResp = await fetch(bvhUrl);
        const bvhText = await bvhResp.text();
        const lines = bvhText.split('\n');

        // Find Yposition channel index
        let yPosChannel = -1, foundRoot = false;
        for (let i = 0; i < lines.length; i++) {
            const trimmed = lines[i].trim();
            if (trimmed.startsWith('ROOT ')) { foundRoot = true; continue; }
            if (foundRoot && trimmed.startsWith('CHANNELS')) {
                const parts = trimmed.split(/\s+/);
                for (let c = 2; c < parts.length; c++) {
                    if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; }
                }
                break;
            }
        }

        if (yPosChannel < 0) {
            console.warn('[BVH Studio] Yposition channel not found in BVH, skip save.');
            return;
        }

        // Find motion data lines
        const motionIdx = lines.findIndex(l => l.trim() === 'MOTION');
        if (motionIdx < 0) return;
        let dataStart = motionIdx + 1;
        while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) dataStart++;

        const frameLines = [];
        for (let i = dataStart; i < lines.length; i++) {
            if (lines[i].trim().match(/^[\d\-\.]/)) frameLines.push(i);
        }

        // Apply corrections from posTrack to BVH text
        for (let f = 0; f < Math.min(nKeys, frameLines.length); f++) {
            const li = frameLines[f];
            const vals = lines[li].trim().split(/\s+/);
            vals[yPosChannel] = posTrack.values[f * 3 + 1].toFixed(6);
            lines[li] = vals.join(' ');
        }

        // Save via API
        const saveResp = await fetch('/api/character/save-bvh-text/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: clip.category, name: clip.name, bvh_text: lines.join('\n') }),
        });
        if (saveResp.ok) {
            console.log(`[BVH Studio] BVH saved: ${clip.category}/${clip.name}`);
        } else {
            console.warn(`[BVH Studio] BVH save failed: ${await saveResp.text()}`);
        }
    } catch (e) {
        console.error('[BVH Studio] BVH save error:', e);
    }
}
