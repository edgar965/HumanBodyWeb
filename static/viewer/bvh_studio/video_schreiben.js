import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
import { exportCancelled } from './export_video.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
/**
 * Bildfolge in ein Video schreiben — auf dem Server oder im Browser.
 *
 * Aus export_video.js herausgeloest (Umbau 16.08.2026).
 */


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
            Protokoll.info('BVH Studio', `Saved via picker: ${handle.name}`);
            return;
        } catch (e) {
            if (e.name === 'AbortError') return;
            Protokoll.warnung('BVH Studio', 'Picker failed, fallback:', e);
        }
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = suggestedName;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

export async function exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, crf, filename, statusText, progressBar) {
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

        // Yield EVERY frame so Cancel-Button-Click zeitnah gegriffen wird.
        // Vorher nur alle 5 Frames → bis zu 500ms Verzögerung bis der Click
        // registriert wurde.
        await new Promise(r => setTimeout(r, 0));
        if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }
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

    Protokoll.info('BVH Studio', `Server export done: ${totalFrames} frames, crf=${crf}, save_path=${formData.get('save_path')}`);
}

export async function exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText, progressBar) {
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
    Protokoll.info('BVH Studio', `Browser export: ${totalFrames} frames`);
}
