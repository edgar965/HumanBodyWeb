/**
 * Untermenue „Clip hinzufuegen" der Spuren.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026): 244 Zeilen, die je Spurtyp
 * ein dreistufiges Menue aufbauen (Kategorie -> Animation, Modelle, Audio,
 * Szenenobjekte). Mit dem Zeichnen der Zeitleiste hat das nichts zu tun.
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { Clip } from './models.js';


// Cached animations list — Modelle werden immer frisch vom Server geholt
// damit neue Dateien in data/models/ sofort erscheinen.
export let _cachedAnimations = null;

export const DEFAULT_CLIP_SECONDS = 10;

export async function _populateTrackAddSubmenu(track, trackIdx, ctx, targetFrame, submenuId = 'track-ctx-add-submenu') {
    const sub = document.getElementById(submenuId);
    if (!sub) return;
    sub.innerHTML = '<div class="ctx-submenu-empty">Lade...</div>';

    const closeCtx = () => { ctx.style.display = 'none'; };
    const fps = state.project.fps;
    const defaultFrames = DEFAULT_CLIP_SECONDS * fps;
    // Platziere Clip an übergebener Position, oder Playhead als Fallback
    const placeFrame = (targetFrame != null) ? targetFrame : state.playheadFrame;

    if (track.type === 'bvh') {
        if (!_cachedAnimations) {
            try {
                const resp = await fetch('/api/character/animations/');
                _cachedAnimations = await resp.json();
            } catch (e) {
                sub.innerHTML = '<div class="ctx-submenu-empty">Fehler beim Laden</div>';
                return;
            }
        }
        sub.innerHTML = '';
        const cats = _cachedAnimations.categories || {};
        const keys = Object.keys(cats).sort();
        if (keys.length === 0) {
            sub.innerHTML = '<div class="ctx-submenu-empty">Keine Animationen verfügbar</div>';
            return;
        }
        // Zwei-stufiges Menü: Kategorie → Animation
        for (const cat of keys) {
            const anims = cats[cat] || [];
            const catItem = document.createElement('div');
            catItem.className = 'ctx-item has-submenu';
            catItem.innerHTML = `
                <i class="fas fa-folder" style="width:16px;color:var(--text-muted);"></i>
                ${cat}
                <span style="margin-left:auto;display:flex;align-items:center;gap:6px;">
                    <span style="font-size:0.7rem;color:var(--text-muted);">${anims.length}</span>
                    <i class="fas fa-caret-right" style="font-size:0.7rem;color:var(--text-muted);"></i>
                </span>
            `;
            const nested = document.createElement('div');
            nested.className = 'ctx-submenu';
            if (anims.length === 0) {
                nested.innerHTML = '<div class="ctx-submenu-empty">Leer</div>';
            } else {
                for (const anim of anims) {
                    const animItem = document.createElement('div');
                    animItem.className = 'ctx-item';
                    animItem.innerHTML = `<i class="fas fa-running" style="width:16px;"></i> ${anim.name} <span style="margin-left:auto;font-size:0.7rem;color:var(--text-muted);">${anim.frames || '?'}f</span>`;
                    animItem.addEventListener('click', async () => {
                        closeCtx();
                        await fn.addClipToTrack(trackIdx, cat, anim.name, anim.frames || 0);
                        const t2 = state.project.tracks[trackIdx];
                        const c = t2.clips[t2.clips.length - 1];
                        if (c) {
                            // Default 10s — trim only if animation is longer than 10s in clip-fps.
                            const targetClipFrames = Math.round(DEFAULT_CLIP_SECONDS * c.fps);
                            if (c.totalFrames > targetClipFrames) c.trimOut = c.totalFrames - targetClipFrames;
                            c.startFrame = placeFrame;
                            fn.updateDuration();
                            fn.renderTimeline();
                        }
                    });
                    nested.appendChild(animItem);
                }
            }
            // Position level-3 submenu with position:fixed on hover to break out
            // of the level-1 submenu's overflow:auto clipping.
            nested.classList.add('ctx-submenu-fixed');
            catItem.addEventListener('mouseenter', () => {
                const rect = catItem.getBoundingClientRect();
                nested.style.left = rect.right + 'px';
                nested.style.top = (rect.top - 5) + 'px';
            });
            catItem.appendChild(nested);
            sub.appendChild(catItem);
        }
    } else if (track.type === 'model') {
        // Immer frisch vom Server holen (kein Cache) — so werden neu hinzugefügte
        // Modelle im data/models/-Verzeichnis sofort angezeigt.
        let presets = [];
        try {
            const resp = await fetch('/api/character/models/');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            presets = data.presets || [];
        } catch (e) {
            sub.innerHTML = `<div class="ctx-submenu-empty">Fehler beim Laden: ${e.message}</div>`;
            return;
        }
        sub.innerHTML = '';
        if (presets.length === 0) {
            sub.innerHTML = '<div class="ctx-submenu-empty">Keine Modelle in data/models/</div>';
            return;
        }
        for (const p of presets) {
            const item = document.createElement('div');
            item.className = 'ctx-item';
            item.innerHTML = `<i class="fas fa-user" style="width:16px;color:#e91e63;"></i> ${p.label || p.name}`;
            item.addEventListener('click', () => {
                closeCtx();
                pushUndo('Modell-Clip hinzufügen');
                const clip = new Clip(null, p.label || p.name, defaultFrames, fps);
                clip.type = 'model';
                clip.startFrame = placeFrame;
                clip.data = { preset: p.name, bodyType: 'Female_Caucasian' };
                track.clips.push(clip);
                track._currentPreset = null;
                fn.applyPlayhead();
                fn.updateDuration();
                fn.renderTimeline();
                fn.updateProperties();
            });
            sub.appendChild(item);
        }
    } else if (track.type === 'audio') {
        sub.innerHTML = '';
        const item = document.createElement('div');
        item.className = 'ctx-item';
        item.innerHTML = `<i class="fas fa-music" style="width:16px;color:#4caf50;"></i> Audio-Datei wählen...`;
        item.addEventListener('click', () => {
            closeCtx();
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'audio/*';
            input.addEventListener('change', async () => {
                const file = input.files[0];
                if (!file) return;
                try {
                    const arrayBuf = await file.arrayBuffer();
                    const audioBuffer = await track.audioCtx.decodeAudioData(arrayBuf);
                    pushUndo('Audio-Clip hinzufügen');
                    // Default 10s Clip — audioDuration bestimmt clip.duration für Audio-Tracks
                    const clip = new Clip(null, file.name, defaultFrames, fps);
                    clip.type = 'audio';
                    clip.startFrame = placeFrame;
                    clip.data = {
                        fileName: file.name,
                        audioBuffer: audioBuffer,
                        audioDuration: Math.min(DEFAULT_CLIP_SECONDS, audioBuffer.duration),
                        volume: 1.0, fadeIn: 0, fadeOut: 0, offset: 0,
                    };
                    try {
                        const formData = new FormData();
                        formData.append('audio', file);
                        const upResp = await fetch('/api/studio/audio-upload/', { method: 'POST', body: formData });
                        const upData = await upResp.json();
                        if (upData.ok) clip.data.audioUrl = upData.url;
                    } catch {}
                    track.clips.push(clip);
                    fn.updateDuration();
                    fn.renderTimeline();
                    fn.updateProperties();
                } catch (err) {
                    console.error('[BVH Studio] Audio decode failed:', err);
                    alert('Audio laden fehlgeschlagen: ' + err.message);
                }
            });
            input.click();
        });
        sub.appendChild(item);
    } else if (track.type === 'scene_object') {
        sub.innerHTML = '';
        const item = document.createElement('div');
        item.className = 'ctx-item';
        item.innerHTML = `<i class="fas fa-cube" style="width:16px;color:#7c5cbf;"></i> 3D-Datei wählen...`;
        item.addEventListener('click', () => {
            closeCtx();
            fn.addSceneObjectClip?.(trackIdx, placeFrame);
        });
        sub.appendChild(item);
    } else if (track.type === 'camera') {
        sub.innerHTML = '';
        const item = document.createElement('div');
        item.className = 'ctx-item';
        item.innerHTML = `<i class="fas fa-video" style="width:16px;color:#00bcd4;"></i> Kameraposition`;
        item.addEventListener('click', () => {
            closeCtx();
            fn.addCameraKeyframe(trackIdx, placeFrame);
        });
        sub.appendChild(item);
    } else if (track.type === 'light') {
        sub.innerHTML = '';
        const pairItem = document.createElement('div');
        pairItem.className = 'ctx-item';
        pairItem.innerHTML = `<i class="fas fa-lightbulb" style="width:16px;color:#ffc107;"></i> Lichteigenschaft (Pair: vor/nach)`;
        pairItem.title = 'Legt zwei Keyframes am gleichen Frame an — einer für das Segment davor, einer für danach';
        pairItem.addEventListener('click', () => {
            closeCtx();
            fn.addLightKeyframePair(trackIdx, placeFrame);
        });
        sub.appendChild(pairItem);
        const singleItem = document.createElement('div');
        singleItem.className = 'ctx-item';
        singleItem.innerHTML = `<i class="fas fa-lightbulb" style="width:16px;color:#ffc107;"></i> Lichteigenschaft (einzel)`;
        singleItem.addEventListener('click', () => {
            closeCtx();
            fn.addLightKeyframe(trackIdx, placeFrame);
        });
        sub.appendChild(singleItem);
        // Presets-Submenu: fügt Preset-Lichter HINZU (keine Löschung existierender)
        const presetsItem = document.createElement('div');
        presetsItem.className = 'ctx-item has-submenu';
        presetsItem.innerHTML = `<i class="fas fa-star" style="width:16px;color:#ffc107;"></i> Presets <i class="fas fa-caret-right" style="margin-left:auto;"></i>`;
        const nested = document.createElement('div');
        nested.className = 'ctx-submenu ctx-submenu-fixed';
        nested.innerHTML = '<div class="ctx-submenu-empty">Lade...</div>';
        presetsItem.appendChild(nested);
        sub.appendChild(presetsItem);
        // Nested-Submenü positionieren (wie bei Animationen)
        presetsItem.addEventListener('mouseenter', () => {
            const rect = presetsItem.getBoundingClientRect();
            nested.style.left = rect.right + 'px';
            nested.style.top = rect.top + 'px';
        });
        // Presets async laden
        (async () => {
            try {
                const presets = await (fn.fetchTheatrePresets?.() ?? fetch('/api/studio/theatre-presets/').then(r => r.json()).then(d => d.presets || []));
                nested.innerHTML = '';
                if (!presets || presets.length === 0) {
                    nested.innerHTML = '<div class="ctx-submenu-empty">Keine Presets</div>';
                    return;
                }
                for (const p of presets) {
                    const item = document.createElement('div');
                    item.className = 'ctx-item';
                    item.innerHTML = `<i class="fas fa-lightbulb" style="width:16px;color:#ffc107;"></i> <span>${p.label}</span> <span style="margin-left:auto;font-size:0.7rem;color:var(--text-muted);">${p.lightCount}x</span>`;
                    item.title = (p.description || '') + '\n\nFügt Preset-Lichter HINZU (existierende bleiben erhalten).';
                    item.addEventListener('click', () => {
                        closeCtx();
                        fn.applyTheatrePresetAdditive?.(p.name, placeFrame);
                    });
                    nested.appendChild(item);
                }
            } catch (e) {
                nested.innerHTML = '<div class="ctx-submenu-empty">Fehler beim Laden</div>';
            }
        })();
    } else {
        sub.innerHTML = '<div class="ctx-submenu-empty">Nicht verfügbar für diesen Spurtyp</div>';
    }
}
