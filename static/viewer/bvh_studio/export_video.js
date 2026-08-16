/**
 * BVH Studio — BVH Export and Video Export (server ffmpeg + browser MediaRecorder).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { exportBrowserMediaRecorder, exportServerFfmpeg, saveBlobAs } from './video_schreiben.js';

export let exportCancelled = false;

export async function exportBVH() {
    if (state.selectedTrackIdx < 0) { alert('Track auswählen.'); return; }
    const track = state.project.tracks[state.selectedTrackIdx];
    if (track.clips.length === 0) { alert('Track hat keine Clips.'); return; }

    // For each clip, fetch the original BVH text and concatenate
    const bvhTexts = [];
    for (const clip of track.clips) {
        try {
            const url = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
            const resp = await fetch(url);
            const text = await resp.text();
            bvhTexts.push({ clip, text });
        } catch (e) {
            console.error(`Failed to fetch BVH for ${clip.name}:`, e);
        }
    }

    if (bvhTexts.length === 0) { alert('Keine BVH Daten.'); return; }

    // For single clip: trim and download
    // For multiple clips: download each separately (BVH doesn't support multi-skeleton)
    if (bvhTexts.length === 1) {
        const blob = new Blob([bvhTexts[0].text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url;
        a.download = `${track.name}_${bvhTexts[0].clip.name}.bvh`;
        a.click(); URL.revokeObjectURL(url);
    } else {
        // Download all as individual files
        for (const { clip, text } of bvhTexts) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url;
            a.download = `${track.name}_${clip.name}.bvh`;
            a.click(); URL.revokeObjectURL(url);
            await new Promise(r => setTimeout(r, 500));
        }
    }
    console.log(`[BVH Studio] Exported ${bvhTexts.length} BVH file(s) for track "${track.name}"`);
}

export async function saveBvhAs() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) { alert('Clip auswählen.'); return; }
    const clip = state.project.tracks[state.selectedTrackIdx].clips[state.selectedClipIdx];
    try {
        const url = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
        const resp = await fetch(url);
        const text = await resp.text();
        const blob = new Blob([text], { type: 'text/plain' });
        const defaultName = `${clip.name}.bvh`;

        // Use File System Access API for native "Save As" dialog
        if (window.showSaveFilePicker) {
            try {
                const handle = await window.showSaveFilePicker({
                    suggestedName: defaultName,
                    types: [{
                        description: 'BVH Motion Capture',
                        accept: { 'text/plain': ['.bvh'] },
                    }],
                });
                const writable = await handle.createWritable();
                await writable.write(blob);
                await writable.close();
                console.log(`[BVH Studio] BVH saved via picker: ${handle.name}`);
                return;
            } catch (pickerErr) {
                if (pickerErr.name === 'AbortError') return;  // user cancelled
                console.warn('[BVH Studio] File picker failed, fallback to download:', pickerErr);
            }
        }

        // Fallback: classic download
        const dlUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = dlUrl;
        a.download = defaultName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(dlUrl);
        console.log(`[BVH Studio] BVH downloaded: ${defaultName}`);
    } catch (e) {
        alert('BVH speichern fehlgeschlagen: ' + e.message);
    }
}

export function setupExportPanel() {
    // Pre-fill target dir from prefs
    const dirEl = document.getElementById('export-target-dir');
    if (dirEl && state.project.videoOutputPath) dirEl.value = state.project.videoOutputPath;

    // Set default range from project duration
    const updateRange = () => {
        const toEl = document.getElementById('export-to');
        if (toEl && toEl.value === '0') toEl.value = Math.round(state.project.duration * state.project.fps);
        const fpsEl = document.getElementById('export-fps');
        if (fpsEl) fpsEl.value = String(state.project.fps);
    };

    document.getElementById('export-start')?.addEventListener('click', startExport);
    document.getElementById('export-cancel')?.addEventListener('click', () => { exportCancelled = true; });

    // Export engine info
    document.getElementById('export-engine')?.addEventListener('change', (e) => {
        console.log(`[BVH Studio] Export engine: ${e.target.value}`);
    });

    // Auto-update frame range + target dir when export tab opens
    document.querySelectorAll('.props-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            if (tab.dataset.tab === 'export') {
                updateRange();
                const dirEl = document.getElementById('export-target-dir');
                if (dirEl && !dirEl.value) dirEl.value = state.project.videoOutputPath || '';
            }
        });
    });
}

async function startExport() {
    const fromFrame = parseInt(document.getElementById('export-from')?.value) || 0;
    let toFrame = parseInt(document.getElementById('export-to')?.value) || 0;
    const fps = parseInt(document.getElementById('export-fps')?.value) || state.project.fps;
    const resolution = parseInt(document.getElementById('export-resolution')?.value) || 1080;
    const crf = document.getElementById('export-quality')?.value || '18';
    const engine = document.getElementById('export-engine')?.value || 'server';
    const filename = document.getElementById('export-filename')?.value || 'bvh_studio_export.mp4';

    if (toFrame <= fromFrame) toFrame = Math.round(state.project.duration * state.project.fps);
    if (toFrame <= fromFrame) { alert('Keine Frames zum Exportieren.'); return; }

    const totalFrames = toFrame - fromFrame;
    exportCancelled = false;

    // UI: show progress, cancel button
    const progressDiv = document.getElementById('export-progress');
    const statusText = document.getElementById('export-status-text');
    const progressBar = document.getElementById('export-progress-bar');
    const startBtn = document.getElementById('export-start');
    const cancelBtn = document.getElementById('export-cancel');
    progressDiv.style.display = '';
    cancelBtn.style.display = '';
    startBtn.disabled = true;
    startBtn.style.opacity = '0.5';

    // Create offscreen renderer (same size as export resolution)
    const aspect = 16 / 9;
    const expW = Math.round(resolution * aspect);
    const expH = resolution;
    const offCanvas = document.createElement('canvas');
    offCanvas.width = expW;
    offCanvas.height = expH;
    const offRenderer = new THREE.WebGLRenderer({ canvas: offCanvas, antialias: true, preserveDrawingBuffer: true });
    offRenderer.setSize(expW, expH, false);
    offRenderer.setPixelRatio(1);

    // Snapshot and override camera so the export uses the SCENE camera
    // (= first Kamera-Track with keyframes), not the user's OrbitControls
    // pose. If there is no such track, we bail with a clear message instead
    // of silently baking the current view.
    const camTrack = state.project.tracks.find(
        t => t.type === 'camera' && (t.clips?.length || 0) > 0
    );
    if (!camTrack) {
        statusText.textContent = 'Fehler: Kein Kamera-Track mit Keyframes. '
            + 'Lege im Timeline-Bereich einen Kamera-Track an und füge mind. einen Keyframe hinzu.';
        progressBar.style.width = '0%';
        startBtn.disabled = false;
        startBtn.style.opacity = '1';
        cancelBtn.style.display = 'none';
        return;
    }
    // Remember user's live orbit pose so we can restore after export.
    const camRestore = {
        pos: state.camera.position.clone(),
        quat: state.camera.quaternion.clone(),
        fov: state.camera.fov,
        aspect: state.camera.aspect,
        cameraActive: camTrack.cameraActive,
        controlsEnabled: state.controls ? state.controls.enabled : true,
    };
    // Disable OrbitControls so they cannot overwrite the timeline pose.
    if (state.controls) state.controls.enabled = false;
    // Force the chosen track to drive the camera, even if the user muted it.
    camTrack.cameraActive = true;
    state.camera.aspect = expW / expH;
    state.camera.updateProjectionMatrix();

    const wasPlaying = state.playing;
    state.playing = false;

    try {
        if (engine === 'server') {
            await exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, crf, filename, statusText, progressBar);
        } else {
            await exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText, progressBar);
        }
    } finally {
        // Cleanup: restore camera + controls exactly as the user left them.
        offRenderer.dispose();
        camTrack.cameraActive = camRestore.cameraActive;
        state.camera.position.copy(camRestore.pos);
        state.camera.quaternion.copy(camRestore.quat);
        state.camera.fov = camRestore.fov;
        state.camera.aspect = camRestore.aspect;
        state.camera.updateProjectionMatrix();
        if (state.controls) state.controls.enabled = camRestore.controlsEnabled;
        if (wasPlaying) state.playing = true;

        progressDiv.style.display = 'none';
        cancelBtn.style.display = 'none';
        startBtn.disabled = false;
        startBtn.style.opacity = '1';
    }
}




// Register functions in registry
fn.exportBVH = exportBVH;
fn.saveBvhAs = saveBvhAs;
fn.setupExportPanel = setupExportPanel;
fn.saveBlobAs = saveBlobAs;
