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

/**
 * Audio-Clips im Exportbereich einsammeln — für die Mischung auf dem Server.
 *
 * Zeiten stehen in PROJEKT-Sekunden (`state.project.fps`), nicht in
 * Export-Bildern: `fromFrame`/`toFrame` sind Projekt-Frames, die Ausgabe-FPS
 * des Videos (`angaben.bilder`) zählt nur die Bilder, ändert aber nicht die
 * Position der Projekt-Zeitleiste. Ein Clip, der über den Rand des
 * Exportbereichs hinausragt, wird beschnitten (Versatz wandert in
 * `source_offset_sec`, damit die Tondatei an der richtigen Stelle weiterläuft).
 */
function _sammleAudioClips(fromFrame, toFrame) {
    const fps = state.project.fps;
    const exportStart = fromFrame / fps;
    const exportEnde = toFrame / fps;
    const ergebnis = [];
    for (const spur of state.project.tracks) {
        if (spur.type !== 'audio' || spur.muted) continue;
        for (const clip of spur.clips || []) {
            if (clip.type !== 'audio') continue;
            if (!clip.data.audioUrl) {
                Protokoll.warnung('BVH Studio',
                    `Ton "${clip.data.fileName || clip.name}" nicht hochgeladen — fehlt im Export.`);
                continue;
            }
            const clipStart = clip.startFrame / fps;
            const clipEnde = clipStart + clip.duration;
            const start = Math.max(clipStart, exportStart);
            const ende = Math.min(clipEnde, exportEnde);
            if (ende <= start) continue;
            ergebnis.push({
                url: clip.data.audioUrl,
                delay_sec: start - exportStart,
                source_offset_sec: (clip.data.offset || 0) + (start - clipStart),
                duration_sec: ende - start,
                volume: clip.data.volume != null ? clip.data.volume : 1,
                fade_in_sec: clip.data.fadeIn || 0,
                fade_out_sec: clip.data.fadeOut || 0,
            });
        }
    }
    return ergebnis;
}

/**
 * Bilder je Anfrage beim Server-Export. Vorher gingen ALLE Bilder eines
 * Exports in EINER Anfrage — Django prüft sein 500-MB-Limit am GESAMTEN
 * Anfrage-Körper, nicht je Bild; überschritt ein langer Export das, öffnete
 * Django beim Auspacken für JEDES Bild eine eigene Temp-Datei GLEICHZEITIG
 * und stürzte mit „Too many open files" ab (Fund 24.09.2026, nach 123,5 s).
 * Jetzt ist jedes Paket eine eigene, kleine Anfrage — die Temp-Dateien der
 * vorigen sind längst wieder zu, bevor die nächste beginnt (Server-Gegenstück
 * `core/api/studio_video_stapel.py`, `TheatrevideoStapel`).
 */
const STAPEL_GROESSE = 150;

async function _stapelHochladen(sessionId, startIndex, stapel) {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('start_index', startIndex);
    stapel.forEach((blob, i) => formData.append('frames', blob, `${String(startIndex + i).padStart(6, '0')}.png`));
    const resp = await fetch('/api/theatre/encode-frames/', { method: 'POST', body: formData });
    if (!resp.ok) throw new Error(await resp.text());
    const daten = await resp.json();
    return daten.session_id;
}

/**
 * Bildausschnitt (Crop) VOR dem Hochladen: ein zweites, kleineres Canvas
 * bekommt nur den gewählten Ausschnitt aus dem vollen Bild — der Server sieht
 * dann bereits die Zielgröße und braucht keinen eigenen Crop-Schalter.
 */
function _zuschneider(ausschnitt) {
    if (!ausschnitt || !ausschnitt.breite || !ausschnitt.hoehe) return null;
    const zielcanvas = document.createElement('canvas');
    zielcanvas.width = ausschnitt.breite;
    zielcanvas.height = ausschnitt.hoehe;
    const kontext = zielcanvas.getContext('2d');
    return (quellcanvas) => {
        kontext.drawImage(quellcanvas, ausschnitt.x, ausschnitt.y, ausschnitt.breite, ausschnitt.hoehe,
            0, 0, ausschnitt.breite, ausschnitt.hoehe);
        return zielcanvas;
    };
}

export async function exportServerFfmpeg(offRenderer, offCanvas, fromFrame, toFrame, fps, format, crf, ausschnitt,
    filename, statusText, progressBar) {
    const totalFrames = toFrame - fromFrame;
    let sessionId = '';
    let stapel = [];
    let stapelStart = 0;
    const zuschneiden = _zuschneider(ausschnitt);

    // Phase 1: Bilder aufnehmen, in Paketen hochladen (nicht alle im
    // Speicher halten UND nicht alle in einer Anfrage, siehe oben).
    for (let f = fromFrame; f < toFrame; f++) {
        if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }

        state.playheadFrame = f;
        fn.applyPlayhead();
        offRenderer.render(state.scene, state.camera);

        const quelle = zuschneiden ? zuschneiden(offCanvas) : offCanvas;
        const blob = await new Promise(r => quelle.toBlob(r, 'image/png'));
        stapel.push(blob);

        const bildnummer = f - fromFrame;
        const pct = Math.round(bildnummer / totalFrames * 100);
        statusText.textContent = `Aufnahme: Frame ${bildnummer + 1}/${totalFrames} (${pct}%)`;
        progressBar.style.width = `${pct * 0.8}%`;  // 80% for capture, 20% for encoding

        if (stapel.length >= STAPEL_GROESSE || f === toFrame - 1) {
            try {
                sessionId = await _stapelHochladen(sessionId, stapelStart, stapel);
            } catch (e) {
                statusText.textContent = 'Fehler beim Hochladen: ' + e.message;
                return;
            }
            stapelStart += stapel.length;
            stapel = [];
        }

        // Yield EVERY frame so Cancel-Button-Click zeitnah gegriffen wird.
        // Vorher nur alle 5 Frames → bis zu 500ms Verzögerung bis der Click
        // registriert wurde.
        await new Promise(r => setTimeout(r, 0));
        if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }
    }

    if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }
    if (!sessionId) { statusText.textContent = 'Fehler: keine Bilder aufgenommen.'; return; }

    // Phase 2: Encoding abschließen
    statusText.textContent = 'Encoding auf Server...';
    progressBar.style.width = '85%';

    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('finish', '1');
    formData.append('frame_count', stapelStart);
    formData.append('fps', fps);
    formData.append('format', format);
    formData.append('crf', crf);

    const audioClips = _sammleAudioClips(fromFrame, toFrame);
    if (audioClips.length) formData.append('audio_clips', JSON.stringify(audioClips));

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
                const mime = { mp4: 'video/mp4', webm: 'video/webm', png: 'application/zip' }[format]
                    || 'application/octet-stream';
                await saveBlobAs(blob, filename, mime);
            }
        } else {
            statusText.textContent = 'Encoding fehlgeschlagen: ' + await resp.text();
        }
    } catch (e) {
        statusText.textContent = 'Fehler: ' + e.message;
    }

    Protokoll.info('BVH Studio',
        `Server export done: ${stapelStart} frames, crf=${crf}, audio=${audioClips.length}, `
        + `save_path=${savePath}`);
}

export async function exportBrowserMediaRecorder(offRenderer, offCanvas, fromFrame, toFrame, fps, filename, statusText,
    progressBar) {
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
    // MediaRecorder liefert IMMER WebM — unabhängig vom Format-Feld (das nur
    // für den Server-Weg gilt, siehe „Engine" in `templates/bvh_studio.html`).
    const dateiname = filename.replace(/\.[^.]+$/, '') + '.webm';
    await saveBlobAs(blob, dateiname, mimeType);
    statusText.textContent = 'Fertig!';
    progressBar.style.width = '100%';
    Protokoll.info('BVH Studio', `Browser export: ${totalFrames} frames`);
}
