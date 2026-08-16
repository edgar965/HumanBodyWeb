/**
 * Gauss-Glaettung der Bewegungsdaten (sitzungsweiter Schalter).
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026). Geglaettet werden
 * QUATERNIONEN, nicht Eulerwinkel — die springen bei jedem Umlauf.
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { applyFixedPositionAll } from './werkzeug_position.js';
import { _fixedPos } from './werkzeug_position.js';


// Gaussian Smooth (session-wide toggle)
export const _gaussSmooth = { active: false, sigma: 2.0, origClips: new Map() };

// =========================================================================
// Gaussian Smooth
// =========================================================================
export function _updateGaussUI() {
    const sigmaInput = document.getElementById('dd-gauss-sigma-input');
    if (sigmaInput) sigmaInput.value = _gaussSmooth.sigma;
    const onEl = document.getElementById('dd-gauss-on');
    const offEl = document.getElementById('dd-gauss-off');
    if (onEl) onEl.style.color = _gaussSmooth.active ? '#888' : '#4caf50';
    if (offEl) offEl.style.color = _gaussSmooth.active ? '#ef4444' : '#888';
    const toolsBtn = document.getElementById('btn-tools');
    if (toolsBtn) toolsBtn.innerHTML = _gaussSmooth.active
        ? `<i class="fas fa-wrench"></i> Tools <span style="font-size:0.65rem;color:#4caf50;">●σ=${_gaussSmooth.sigma}</span> <i class="fas fa-caret-down" style="font-size:0.65rem;"></i>`
        : `<i class="fas fa-wrench"></i> Tools <i class="fas fa-caret-down" style="font-size:0.65rem;"></i>`;
}

export function _gaussFilter(values, stride, sigma) {
    const nKeys = values.length / stride;
    const radius = Math.ceil(sigma * 3);
    const kernel = [];
    let ksum = 0;
    for (let i = -radius; i <= radius; i++) {
        const v = Math.exp(-0.5 * (i / sigma) ** 2);
        kernel.push(v); ksum += v;
    }
    for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;

    const orig = new Float32Array(values);
    for (let c = 0; c < stride; c++) {
        for (let k = 0; k < nKeys; k++) {
            let sum = 0;
            for (let j = 0; j < kernel.length; j++) {
                const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                sum += kernel[j] * orig[idx * stride + c];
            }
            values[k * stride + c] = sum;
        }
    }
    // Re-normalize quaternions
    if (stride === 4) {
        for (let k = 0; k < nKeys; k++) {
            const i = k * 4;
            const len = Math.sqrt(values[i]**2 + values[i+1]**2 + values[i+2]**2 + values[i+3]**2);
            if (len > 1e-8) { values[i]/=len; values[i+1]/=len; values[i+2]/=len; values[i+3]/=len; }
        }
    }
}

export function applyGaussToAllClips() {
    const sigma = _gaussSmooth.sigma;
    let smoothedCount = 0;
    let totalTracks = 0;
    for (const track of state.project.tracks) {
        totalTracks++;
        if (track.type !== 'bvh') { console.log(`[Gauss] skip track type=${track.type}`); continue; }
        for (const clip of track.clips) {
            if (!clip.animClip) continue;
            const key = `${clip.category}/${clip.name}`;
            // Save original values if not saved yet
            if (!_gaussSmooth.origClips.has(key)) {
                const backup = {};
                for (const t of clip.animClip.tracks) {
                    backup[t.name] = new Float32Array(t.values);
                }
                _gaussSmooth.origClips.set(key, backup);
            }
            // Restore original then apply smooth
            const backup = _gaussSmooth.origClips.get(key);
            let trackCount = 0;
            for (const t of clip.animClip.tracks) {
                if (backup[t.name]) t.values.set(backup[t.name]);
                _gaussFilter(t.values, t.getValueSize(), sigma);
                trackCount++;
            }
            // Log before/after for first track of first clip
            if (smoothedCount === 0 && clip.animClip.tracks.length > 0) {
                const t0 = clip.animClip.tracks[0];
                console.log(`[Gauss] Track "${t0.name}" first 4 values AFTER smooth: [${t0.values[0].toFixed(4)}, ${t0.values[1].toFixed(4)}, ${t0.values[2].toFixed(4)}, ${t0.values[3].toFixed(4)}]`);
                const bk = backup[t0.name];
                if (bk) console.log(`[Gauss] Track "${t0.name}" first 4 values ORIGINAL: [${bk[0].toFixed(4)}, ${bk[1].toFixed(4)}, ${bk[2].toFixed(4)}, ${bk[3].toFixed(4)}]`);
            }
            // CRITICAL: uncache the clip so Three.js creates a fresh Action with new data
            if (track.mixer) track.mixer.uncacheClip(clip.animClip);
            smoothedCount++;
        }
        // Reset active clip reference
        if (track.mixer) track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
    }
    // Re-apply fixed position if active (gauss changed track values)
    if (_fixedPos.active) { _fixedPos.origData.clear(); applyFixedPositionAll(); }
    fn.applyPlayhead();
    fn.serverLog('gauss_smooth_on', `sigma=${sigma} clips=${smoothedCount}/${totalTracks}`);
    if (smoothedCount === 0) console.warn('[BVH Studio] WARNING: No clips were smoothed! Check track.type and clip.animClip.');
}

export function reloadAllClipAnimations() {
    // Restore originals
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (const clip of track.clips) {
            if (!clip.animClip) continue;
            const key = `${clip.category}/${clip.name}`;
            const backup = _gaussSmooth.origClips.get(key);
            if (backup) {
                for (const t of clip.animClip.tracks) {
                    if (backup[t.name]) t.values.set(backup[t.name]);
                }
            }
            // Uncache so mixer uses restored data
            if (track.mixer) track.mixer.uncacheClip(clip.animClip);
        }
        if (track.mixer) track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
    }
    _gaussSmooth.origClips.clear();
    // Re-apply fixed position if active (originals were overwritten by gauss restore)
    if (_fixedPos.active) { _fixedPos.origData.clear(); applyFixedPositionAll(); }
    fn.applyPlayhead();
    fn.serverLog('gauss_smooth_off');
}

export async function saveSmoothedBVH() {
    if (!_gaussSmooth.active) { alert('Gaussian Smooth ist nicht aktiv.\nBitte erst EINSCHALTEN.'); return; }

    // Collect all clips from tracks
    const clips = [];
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (const clip of track.clips) {
            if (clip.category && clip.name) clips.push(clip);
        }
    }

    // If no track clips, try current preview animation
    if (clips.length === 0) {
        const previewInfo = fn.getPreviewInfo ? fn.getPreviewInfo() : null;
        if (previewInfo && previewInfo.category && previewInfo.name) {
            clips.push({ category: previewInfo.category, name: previewInfo.name });
        }
    }

    if (clips.length === 0) {
        alert('Keine Animation geladen.\nBitte erst eine Animation per Doppelklick zum Track hinzufügen\noder per A-Taste in der Vorschau öffnen.');
        return;
    }

    const sigma = _gaussSmooth.sigma;
    let saved = 0;
    for (const clip of clips) {
        try {
            const resp = await fetch(`/api/retarget/smooth-bvh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: clip.category, name: clip.name, sigma }),
            });
            const result = await resp.json();
            if (result.ok) {
                saved++;
                fn.serverLog('gauss_saved', `${clip.category}/${clip.name} sigma=${sigma}`);
            } else {
                console.error(`Save failed for ${clip.name}:`, result.error);
            }
        } catch(e) { console.error(`Save failed for ${clip.name}:`, e); }
    }
    _gaussSmooth.origClips.clear();
    alert(`Smooth (σ=${sigma}) permanent gespeichert auf ${saved} von ${clips.length} Clip(s).`);
    console.log(`[BVH Studio] Smoothed clips saved: ${saved}`);
}

export function smoothSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) { alert('Clip auswählen.'); return; }
    pushUndo('Smooth');
    const clip = state.project.tracks[state.selectedTrackIdx].clips[state.selectedClipIdx];
    if (!clip.animClip) { alert('Clip hat keine Animation.'); return; }

    // Read sigma from tools panel, fallback to clip property
    const sigmaInput = document.getElementById('tool-smooth-sigma');
    const sigma = sigmaInput ? parseFloat(sigmaInput.value) || 2 : (clip.smoothSigma || 2);
    if (sigma <= 0) { alert('Sigma muss > 0 sein.'); return; }

    const mode = document.getElementById('tool-smooth-mode')?.value || 'all';

    const radius = Math.ceil(sigma * 3);
    const kernel = [];
    let ksum = 0;
    for (let i = -radius; i <= radius; i++) {
        const v = Math.exp(-0.5 * (i / sigma) ** 2);
        kernel.push(v); ksum += v;
    }
    for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;

    // Filter bone names by mode
    const HAND_BONES = ['hand', 'finger', 'thumb', 'palm'];
    const BODY_ONLY_SKIP = [...HAND_BONES];

    let smoothedCount = 0;
    for (const track of clip.animClip.tracks) {
        const tn = track.name.toLowerCase();
        if (mode === 'body' && HAND_BONES.some(h => tn.includes(h))) continue;
        if (mode === 'hands' && !HAND_BONES.some(h => tn.includes(h))) continue;

        const stride = track.getValueSize();
        const nKeys = track.values.length / stride;
        const orig = new Float32Array(track.values);
        for (let c = 0; c < stride; c++) {
            for (let k = 0; k < nKeys; k++) {
                let sum = 0;
                for (let j = 0; j < kernel.length; j++) {
                    const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                    sum += kernel[j] * orig[idx * stride + c];
                }
                track.values[k * stride + c] = sum;
            }
        }
        // Re-normalize quaternions
        if (stride === 4) {
            for (let k = 0; k < nKeys; k++) {
                const i = k * 4;
                const len = Math.sqrt(track.values[i]**2 + track.values[i+1]**2 + track.values[i+2]**2 + track.values[i+3]**2);
                if (len > 1e-8) { track.values[i]/=len; track.values[i+1]/=len; track.values[i+2]/=len; track.values[i+3]/=len; }
            }
        }
        smoothedCount++;
    }
    // Update clip property
    clip.smoothSigma = sigma;
    fn.updateProperties();
    console.log(`[BVH Studio] Smoothed ${clip.name}: sigma=${sigma}, mode=${mode}, ${smoothedCount} tracks`);
}
