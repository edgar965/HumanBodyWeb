/**
 * BVH Studio — BVH Export and Video Export (server ffmpeg + browser MediaRecorder).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

let exportCancelled = false;

export async function exportBVH() {
    if (state.selectedTrackIdx < 0) { alert('Track auswaehlen.'); return; }
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
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) { alert('Clip auswaehlen.'); return; }
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

    // Use same camera with adjusted aspect
    const origAspect = state.camera.aspect;
    state.camera.aspect = expW / expH;
    state.camera.updateProjectionMatrix();

    const wasPlaying = state.playing;
    state.playing = false;

    if (engine === 'server') {
        await exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, crf, filename, statusText, progressBar);
    } else {
        await exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText, progressBar);
    }

    // Cleanup
    offRenderer.dispose();
    state.camera.aspect = origAspect;
    state.camera.updateProjectionMatrix();
    if (wasPlaying) state.playing = true;

    // Reset UI
    progressDiv.style.display = 'none';
    cancelBtn.style.display = 'none';
    startBtn.disabled = false;
    startBtn.style.opacity = '1';
}

/** Save blob with native "Save As" dialog, fallback to download */
export async function saveBlobAs(blob, suggestedName, mimeType) {
    if (window.showSaveFilePicker) {
        try {
            const ext = '.' + suggestedName.split('.').pop();
            const handle = await window.showSaveFilePicker({
                suggestedName,
                types: [{ description: 'Video', accept: { [mimeType]: [ext] } }],
            });
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            console.log(`[BVH Studio] Saved via picker: ${handle.name}`);
            return;
        } catch (e) {
            if (e.name === 'AbortError') return;
            console.warn('[BVH Studio] Picker failed, fallback:', e);
        }
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = suggestedName;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, crf, filename, statusText, progressBar) {
    const totalFrames = toFrame - fromFrame;
    const frames = [];

    // Phase 1: Capture frames
    for (let f = fromFrame; f < toFrame; f++) {
        if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }

        state.playheadFrame = f;
        fn.applyPlayhead();
        offRenderer.render(state.scene, state.camera);

        const blob = await new Promise(r => offCanvas.toBlob(r, 'image/png'));
        frames.push(blob);

        const pct = ((f - fromFrame) / totalFrames * 100).toFixed(0);
        statusText.textContent = `Aufnahme: Frame ${f - fromFrame + 1}/${totalFrames} (${pct}%)`;
        progressBar.style.width = `${pct * 0.8}%`;  // 80% for capture, 20% for encoding

        // Yield to keep UI responsive
        if ((f - fromFrame) % 5 === 0) await new Promise(r => setTimeout(r, 0));
    }

    if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }

    // Phase 2: Send to server
    statusText.textContent = 'Encoding auf Server...';
    progressBar.style.width = '85%';

    const formData = new FormData();
    frames.forEach((blob, i) => formData.append('frames', blob, `${String(i).padStart(6, '0')}.png`));
    formData.append('fps', fps);
    formData.append('format', 'mp4');
    formData.append('crf', crf);

    // Build save path -- always save to server disk
    const outputDir = (document.getElementById('export-target-dir')?.value || '').trim()
        || 'A:/3DTools/HumanBodyWeb/media/output';
    const sep = outputDir.includes('\\') ? '\\' : '/';
    const savePath = outputDir.replace(/[/\\]$/, '') + sep + filename;
    formData.append('save_path', savePath);

    try {
        const resp = await fetch('/api/theatre/encode-frames/', { method: 'POST', body: formData });
        if (resp.ok) {
            progressBar.style.width = '100%';
            const ct = resp.headers.get('content-type') || '';
            if (ct.includes('application/json')) {
                // Server saved to disk
                const data = await resp.json();
                statusText.textContent = `Gespeichert: ${data.saved}`;
            } else {
                // Server returned file blob (no save_path configured)
                statusText.textContent = 'Fertig! Speichern...';
                const blob = await resp.blob();
                await saveBlobAs(blob, filename, 'video/mp4');
            }
        } else {
            statusText.textContent = 'Encoding fehlgeschlagen: ' + await resp.text();
        }
    } catch (e) {
        statusText.textContent = 'Fehler: ' + e.message;
    }

    console.log(`[BVH Studio] Server export done: ${totalFrames} frames, crf=${crf}, save_path=${formData.get('save_path')}`);
}

async function exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText, progressBar) {
    const totalFrames = toFrame - fromFrame;
    const stream = offCanvas.captureStream(0);  // 0 = manual frame push
    const chunks = [];

    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
    const recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 8_000_000 });
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };

    const done = new Promise(resolve => { recorder.onstop = resolve; });
    recorder.start();

    const frameInterval = 1000 / fps;
    for (let f = fromFrame; f < toFrame; f++) {
        if (exportCancelled) { recorder.stop(); statusText.textContent = 'Abgebrochen.'; return; }

        state.playheadFrame = f;
        fn.applyPlayhead();
        offRenderer.render(state.scene, state.camera);

        // Push frame to stream
        const track = stream.getVideoTracks()[0];
        if (track && track.requestFrame) track.requestFrame();

        const pct = ((f - fromFrame) / totalFrames * 100).toFixed(0);
        statusText.textContent = `Aufnahme: Frame ${f - fromFrame + 1}/${totalFrames} (${pct}%)`;
        progressBar.style.width = `${pct}%`;

        await new Promise(r => setTimeout(r, frameInterval));
    }

    recorder.stop();
    await done;

    const blob = new Blob(chunks, { type: mimeType });
    statusText.textContent = 'Fertig! Speichern...';
    await saveBlobAs(blob, filename.replace('.mp4', '.webm'), mimeType);
    statusText.textContent = 'Fertig!';
    progressBar.style.width = '100%';
    console.log(`[BVH Studio] Browser export: ${totalFrames} frames`);
}

// Register functions in registry
fn.exportBVH = exportBVH;
fn.saveBvhAs = saveBvhAs;
fn.setupExportPanel = setupExportPanel;
fn.saveBlobAs = saveBlobAs;
