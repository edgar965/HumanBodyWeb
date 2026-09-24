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
    // `fromFrame`/`toFrame` stehen auf der PROJEKT-Zeitleiste (Projekt-FPS,
    // meist 30) — `fps` ist die gewählte AUSGABE-Framerate und kann davon
    // abweichen (Edgar, 24.09.2026, mit `2.mp4`: „das sind doch keine 4K,
    // die Geschwindigkeit ist kaputt"). Vorher lief `f` 1:1 von `fromFrame`
    // bis `toFrame` und wurde direkt als Ausgabebild UND als Playhead
    // benutzt — bei FPS 60 auf einem 30-fps-Projekt kamen so nur halb so
    // viele Bilder heraus, wie ein 60-fps-Video für dieselbe Dauer braucht:
    // das Video lief exakt doppelt so schnell (gemessen: 1850 Bilder bei
    // 60 fps ergaben 30,8 s statt der beabsichtigten 61,7 s — dieselbe
    // Bildzahl wie ein 30-fps-Export derselben Spanne). Jetzt wird auf die
    // AUSGABE-Bildzahl umgerechnet und die Projekt-Zeit entsprechend
    // abgetastet — wie `_sampleFrames` in `export_nutzlast.js` es für den
    // Stoff-Export schon vormacht.
    const projFps = state.project.fps || fps;
    const verhaeltnis = projFps / fps;               // Projekt-Bilder je Ausgabebild
    const totalFrames = Math.max(1, Math.round((toFrame - fromFrame) / verhaeltnis));
    let sessionId = '';
    let stapel = [];
    let stapelStart = 0;
    const zuschneiden = _zuschneider(ausschnitt);

    // Phase 1: Bilder aufnehmen, in Paketen hochladen (nicht alle im
    // Speicher halten UND nicht alle in einer Anfrage, siehe oben).
    for (let bildnummer = 0; bildnummer < totalFrames; bildnummer++) {
        if (exportCancelled) { statusText.textContent = 'Abgebrochen.'; return; }

        state.playheadFrame = Math.round(fromFrame + bildnummer * verhaeltnis);
        fn.applyPlayhead();
        offRenderer.render(state.scene, state.camera);

        const quelle = zuschneiden ? zuschneiden(offCanvas) : offCanvas;
        const blob = await new Promise(r => quelle.toBlob(r, 'image/png'));
        stapel.push(blob);

        const pct = Math.round(bildnummer / totalFrames * 100);
        statusText.textContent = `Aufnahme: Frame ${bildnummer + 1}/${totalFrames} (${pct}%)`;
        progressBar.style.width = `${pct * 0.8}%`;  // 80% for capture, 20% for encoding

        if (stapel.length >= STAPEL_GROESSE || bildnummer === totalFrames - 1) {
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
    // Dieselbe Umrechnung wie in `exportServerFfmpeg` (24.09.2026, siehe
    // dort): `fromFrame`/`toFrame` sind Projekt-Frames, `fps` die gewählte
    // Ausgabe-Framerate. Der MediaRecorder zeichnet in ECHTZEIT auf (die
    // Wartezeit zwischen zwei Bildern ist `frameInterval`) — lief die
    // Schleife weiterhin `toFrame - fromFrame` mal (Projekt-Bilder statt
    // Ausgabebilder), war die AUFNAHMEDAUER selbst falsch: bei FPS 60 auf
    // einem 30-fps-Projekt nur halb so lang wie beabsichtigt.
    const projFps = state.project.fps || fps;
    const verhaeltnis = projFps / fps;               // Projekt-Bilder je Ausgabebild
    const totalFrames = Math.max(1, Math.round((toFrame - fromFrame) / verhaeltnis));
    const stream = offCanvas.captureStream(0);  // 0 = manual frame push
    const chunks = [];

    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
    const recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 8_000_000 });
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };

    const done = new Promise(resolve => { recorder.onstop = resolve; });
    recorder.start();

    const frameInterval = 1000 / fps;
    for (let bildnummer = 0; bildnummer < totalFrames; bildnummer++) {
        if (exportCancelled) { recorder.stop(); statusText.textContent = 'Abgebrochen.'; return; }

        state.playheadFrame = Math.round(fromFrame + bildnummer * verhaeltnis);
        fn.applyPlayhead();
        offRenderer.render(state.scene, state.camera);

        // Push frame to stream
        const track = stream.getVideoTracks()[0];
        if (track && track.requestFrame) track.requestFrame();

        const pct = (bildnummer / totalFrames * 100).toFixed(0);
        statusText.textContent = `Aufnahme: Frame ${bildnummer + 1}/${totalFrames} (${pct}%)`;
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
