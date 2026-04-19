/**
 * BVH Studio — Timeline canvas drawing and mouse interaction.
 */
import { state, TRACK_HEIGHT, HEADER_WIDTH, RULER_HEIGHT, TRACK_ICONS } from './state.js';
import { fn } from './registry.js';
import { pushUndo } from './undo.js';
import { setLibSelectedItem } from './library.js';
import { Clip } from './models.js';

let tlCanvas, tlCtx;

// Cached API responses for track-context "Hinzufügen" submenu
let _cachedModelPresets = null;
let _cachedAnimations = null;

const DEFAULT_CLIP_SECONDS = 10;

async function _populateTrackAddSubmenu(track, trackIdx, ctx, targetFrame, submenuId = 'track-ctx-add-submenu') {
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
        if (!_cachedModelPresets) {
            try {
                const resp = await fetch('/api/character/models/');
                const data = await resp.json();
                _cachedModelPresets = data.presets || [];
            } catch (e) {
                sub.innerHTML = '<div class="ctx-submenu-empty">Fehler beim Laden</div>';
                return;
            }
        }
        sub.innerHTML = '';
        if (_cachedModelPresets.length === 0) {
            sub.innerHTML = '<div class="ctx-submenu-empty">Keine Modelle verfügbar</div>';
            return;
        }
        for (const p of _cachedModelPresets) {
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
        const item = document.createElement('div');
        item.className = 'ctx-item';
        item.innerHTML = `<i class="fas fa-lightbulb" style="width:16px;color:#ffc107;"></i> Licht`;
        item.addEventListener('click', () => {
            closeCtx();
            fn.addLightKeyframe(trackIdx, placeFrame);
        });
        sub.appendChild(item);
    } else {
        sub.innerHTML = '<div class="ctx-submenu-empty">Nicht verfügbar für diesen Spurtyp</div>';
    }
}

export function setupTimeline() {
    tlCanvas = document.getElementById('timeline-canvas');
    if (!tlCanvas) return;
    tlCtx = tlCanvas.getContext('2d');

    const wrap = tlCanvas.parentElement;
    const resize = () => {
        tlCanvas.width = wrap.clientWidth;
        tlCanvas.height = wrap.clientHeight;
        renderTimeline();
    };
    resize();
    new ResizeObserver(resize).observe(wrap);

    // Zoom slider
    const zoomSlider = document.getElementById('tl-zoom');
    if (zoomSlider) {
        zoomSlider.addEventListener('input', () => {
            state.timelineZoom = parseInt(zoomSlider.value);
            document.getElementById('tl-zoom-label').textContent = `Zoom: ${state.timelineZoom}%`;
            renderTimeline();
        });
    }

    // --- Clip hit-testing ---
    function hitTestClip(mx, my) {
        const pps = state.timelineZoom;
        for (let ti = 0; ti < state.project.tracks.length; ti++) {
            const track = state.project.tracks[ti];
            const y = RULER_HEIGHT + ti * TRACK_HEIGHT;
            for (let ci = 0; ci < track.clips.length; ci++) {
                const clip = track.clips[ci];
                const cx = HEADER_WIDTH + (clip.startFrame / state.project.fps) * pps - state.timelineScrollX;

                if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
                    // Keyframe marker: hit area 16x16 around point
                    const my2 = y + TRACK_HEIGHT / 2;
                    if (mx >= cx - 8 && mx <= cx + 8 && my >= my2 - 8 && my <= my2 + 8) {
                        return { trackIdx: ti, clipIdx: ci, clipX: cx, clipW: 0 };
                    }
                } else {
                    const cw = Math.max(clip.duration * pps, 4);
                    const cy = y + 4;
                    const ch = TRACK_HEIGHT - 8;
                    if (mx >= cx && mx <= cx + cw && my >= cy && my <= cy + ch) {
                        // Detect edge: 6px grab zone at left/right edge
                        let edge = null;
                        if (mx - cx < 6 && cw > 16) edge = 'left';
                        else if (cx + cw - mx < 6 && cw > 16) edge = 'right';
                        return { trackIdx: ti, clipIdx: ci, clipX: cx, clipW: cw, edge };
                    }
                }
            }
        }
        return null;
    }

    // --- Mouse interactions ---
    // Modes: 'none' | 'clip-drag' | 'trim-left' | 'trim-right' | 'scrub' | 'pan'
    let dragMode = 'none';
    let draggingClip = null;
    let dragStartX = 0;
    let dragOrigFrame = 0;
    let dragOrigTrimIn = 0;
    let dragOrigTrimOut = 0;
    let panStartScrollX = 0;

    function setPlayheadFromMouse(mx) {
        const x = mx - HEADER_WIDTH + state.timelineScrollX;
        state.playheadFrame = Math.max(0, Math.round((x / state.timelineZoom) * state.project.fps));
        renderTimeline();
        fn.updatePlaybackUI();
        fn.applyPlayhead();
    }

    tlCanvas.addEventListener('mousedown', (e) => {
        const rect = tlCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Middle mouse button or Alt+click -> pan
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            dragMode = 'pan';
            dragStartX = e.clientX;
            panStartScrollX = state.timelineScrollX;
            e.preventDefault();
            return;
        }

        // Hit test clips (left button only)
        if (e.button === 0) {
            const hit = hitTestClip(mx, my);
            // Clear library selection when clicking in timeline
            document.querySelectorAll('.lib-item.selected').forEach(el => el.classList.remove('selected'));
            setLibSelectedItem(null);
            if (hit) {
                state.selectedTrackIdx = hit.trackIdx;
                state.selectedClipIdx = hit.clipIdx;
                fn.updateProperties();
                renderTimeline();
                const clip = state.project.tracks[hit.trackIdx].clips[hit.clipIdx];
                draggingClip = hit;
                dragStartX = mx;
                dragOrigFrame = clip.startFrame;
                dragOrigTrimIn = clip.trimIn;
                dragOrigTrimOut = clip.trimOut;
                // Edge drag = trim, center drag = move
                if (hit.edge === 'left') { pushUndo('Trim links'); dragMode = 'trim-left'; }
                else if (hit.edge === 'right') { pushUndo('Trim rechts'); dragMode = 'trim-right'; }
                else { pushUndo('Clip verschieben'); dragMode = 'clip-drag'; }
                e.preventDefault();
                return;
            }

            // No clip hit
            if (mx > HEADER_WIDTH) {
                if (my <= RULER_HEIGHT) {
                    // Klick auf Ruler (über den Spuren) → Playhead scrubben
                    dragMode = 'scrub';
                    dragStartX = mx;
                    setPlayheadFromMouse(mx);
                } else {
                    // Klick in Spur-Bereich → nur Spur auswählen, Playhead bleibt stehen
                    const ti = Math.floor((my - RULER_HEIGHT) / TRACK_HEIGHT);
                    if (ti >= 0 && ti < state.project.tracks.length) {
                        state.selectedTrackIdx = ti;
                        state.selectedClipIdx = -1;
                        fn.updateProperties();
                        renderTimeline();
                    }
                }
                e.preventDefault();
            }
        }
    });

    tlCanvas.addEventListener('mousemove', (e) => {
        // Update cursor on hover
        if (dragMode === 'none') {
            const rect = tlCanvas.getBoundingClientRect();
            const hit = hitTestClip(e.clientX - rect.left, e.clientY - rect.top);
            if (hit?.edge) tlCanvas.style.cursor = 'ew-resize';
            else if (hit) tlCanvas.style.cursor = 'grab';
            else tlCanvas.style.cursor = 'default';
        }
        if (dragMode === 'none') return;
        const rect = tlCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;

        if (dragMode === 'clip-drag' && draggingClip) {
            const dx = mx - dragStartX;
            const frameDelta = Math.round((dx / state.timelineZoom) * state.project.fps);
            const clip = state.project.tracks[draggingClip.trackIdx].clips[draggingClip.clipIdx];
            clip.startFrame = Math.max(0, dragOrigFrame + frameDelta);
            fn.updateDuration();
            renderTimeline();
        } else if (dragMode === 'trim-left' && draggingClip) {
            const dx = mx - dragStartX;
            const frameDelta = Math.round((dx / state.timelineZoom) * state.project.fps);
            const clip = state.project.tracks[draggingClip.trackIdx].clips[draggingClip.clipIdx];
            const newTrimIn = Math.max(0, Math.min(clip.totalFrames - clip.trimOut - 1, dragOrigTrimIn + frameDelta));
            clip.trimIn = newTrimIn;
            // Shift start so the visible clip stays aligned
            clip.startFrame = Math.max(0, dragOrigFrame + (newTrimIn - dragOrigTrimIn));
            fn.updateDuration();
            renderTimeline();
        } else if (dragMode === 'trim-right' && draggingClip) {
            const dx = mx - dragStartX;
            const frameDelta = Math.round((dx / state.timelineZoom) * state.project.fps);
            const clip = state.project.tracks[draggingClip.trackIdx].clips[draggingClip.clipIdx];
            clip.trimOut = Math.max(0, Math.min(clip.totalFrames - clip.trimIn - 1, dragOrigTrimOut - frameDelta));
            fn.updateDuration();
            renderTimeline();
        } else if (dragMode === 'scrub') {
            if (mx > HEADER_WIDTH) setPlayheadFromMouse(mx);
        } else if (dragMode === 'pan') {
            const dx = e.clientX - dragStartX;
            state.timelineScrollX = Math.max(0, panStartScrollX - dx);
            renderTimeline();
        }
    });

    tlCanvas.addEventListener('mouseup', () => {
        if (dragMode === 'clip-drag' || dragMode === 'trim-left' || dragMode === 'trim-right') {
            draggingClip = null;
            fn.updateProperties();
        }
        dragMode = 'none';
        tlCanvas.style.cursor = 'default';
    });

    tlCanvas.addEventListener('mouseleave', () => {
        if (dragMode === 'clip-drag') draggingClip = null;
        dragMode = 'none';
    });

    // Prevent default middle-click paste/autoscroll
    tlCanvas.addEventListener('auxclick', (e) => { if (e.button === 1) e.preventDefault(); });

    // Context menu (right-click on clip)
    const ctxMenu = document.getElementById('clip-context-menu');
    // Store mouse X for "move playhead here" context menu action
    let _ctxMouseX = 0;

    const modelCtxMenu = document.getElementById('model-context-menu');

    function _setModelPreset(trackIdx, preset) {
        const track = state.project.tracks[trackIdx];
        if (!track || track.type !== 'model') return;
        pushUndo('Preset ändern');
        // Find the clip at the current playhead or the selected clip
        const t = state.playheadFrame / state.project.fps;
        let clip = null;
        if (state.selectedClipIdx >= 0 && state.selectedTrackIdx === trackIdx) {
            clip = track.clips[state.selectedClipIdx];
        } else {
            for (const c of track.clips) {
                const cs = c.startFrame / state.project.fps;
                const ce = cs + c.duration;
                if (t >= cs && t < ce) { clip = c; break; }
            }
        }
        if (!clip) {
            // No clip at playhead — create one
            const Clip = track.clips[0]?.constructor;
            if (!Clip) return;
            clip = new Clip(null, preset, Math.max(300, state.project.duration * state.project.fps), state.project.fps);
            clip.type = 'model';
            clip.startFrame = 0;
            clip.data = { preset, bodyType: 'Female_Caucasian' };
            track.clips.push(clip);
        } else {
            clip.data = clip.data || {};
            clip.data.preset = preset;
            clip.name = preset;
        }
        // Force model reload on next playhead
        track._currentPreset = null;
        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updateProperties();
        console.log(`[BVH Studio] Model preset changed to: ${preset}`);
    }
    let _modelPresetsFetched = false;

    tlCanvas.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        const rect = tlCanvas.getBoundingClientRect();
        _ctxMouseX = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const hit = hitTestClip(_ctxMouseX, my);

        // Determine which track the mouse is on
        const trackIdx = Math.floor((my - RULER_HEIGHT) / TRACK_HEIGHT);
        const track = state.project.tracks[trackIdx];

        if (hit) {
            state.selectedTrackIdx = hit.trackIdx;
            state.selectedClipIdx = hit.clipIdx;
            fn.updateProperties();
            renderTimeline();
        }

        // Klick in Spur-Bereich ohne Clip-Hit → Track-Kontextmenü mit "Hinzufügen"
        // (neue Clips werden an der Klick-Position platziert)
        if (!hit && track && my > RULER_HEIGHT && _ctxMouseX > HEADER_WIDTH) {
            state.selectedTrackIdx = trackIdx;
            state.selectedClipIdx = -1;
            fn.updateProperties();
            renderTimeline();

            const trackCtx = document.getElementById('track-context-menu');
            if (trackCtx) {
                ctxMenu.style.display = 'none';
                modelCtxMenu.style.display = 'none';
                const clickFrame = Math.max(0, Math.round(
                    ((_ctxMouseX - HEADER_WIDTH + state.timelineScrollX) / state.timelineZoom) * state.project.fps
                ));
                _populateTrackAddSubmenu(track, trackIdx, trackCtx, clickFrame);
                // Hide link section (only relevant on header right-click)
                const linkSection = document.getElementById('track-ctx-link-section');
                if (linkSection) linkSection.style.display = 'none';
                trackCtx.style.display = '';
                trackCtx.style.left = e.clientX + 'px';
                const menuH = trackCtx.offsetHeight || 200;
                trackCtx.style.top = Math.min(e.clientY, window.innerHeight - menuH - 10) + 'px';
                return;
            }
        }

        // Track-context-menu verstecken falls vorhin geöffnet
        const _trackCtxEl = document.getElementById('track-context-menu');
        if (_trackCtxEl) _trackCtxEl.style.display = 'none';

        // Berechne Klick-Position als Frame für "Hinzufügen"-Submenu
        const clickFrame = Math.max(0, Math.round(
            ((_ctxMouseX - HEADER_WIDTH + state.timelineScrollX) / state.timelineZoom) * state.project.fps
        ));

        // Use model context menu for model tracks
        if (track && track.type === 'model') {
            ctxMenu.style.display = 'none';
            // Populate "Hinzufügen" submenu — new items placed at click position
            _populateTrackAddSubmenu(track, trackIdx, modelCtxMenu, clickFrame, 'model-ctx-add-submenu');
            // Populate preset list if not done
            if (!_modelPresetsFetched) {
                _modelPresetsFetched = true;
                fetch('/api/character/models/').then(r => r.json()).then(data => {
                    const list = document.getElementById('model-preset-list');
                    list.innerHTML = '';
                    for (const p of (data.presets || [])) {
                        const item = document.createElement('div');
                        item.className = 'ctx-item';
                        item.dataset.action = 'ctx-model-preset';
                        item.dataset.preset = p.name;
                        item.innerHTML = `<i class="fas fa-user" style="width:16px;color:#e91e63;"></i> ${p.label || p.name}`;
                        list.appendChild(item);
                    }
                    // Bind click handlers
                    list.querySelectorAll('.ctx-item').forEach(item => {
                        item.addEventListener('click', () => {
                            modelCtxMenu.style.display = 'none';
                            _setModelPreset(trackIdx, item.dataset.preset);
                        });
                    });
                });
            }
            // Highlight current preset
            const currentPreset = hit ? track.clips[hit.clipIdx]?.data?.preset : null;
            modelCtxMenu.querySelectorAll('#model-preset-list .ctx-item').forEach(item => {
                item.style.fontWeight = item.dataset.preset === currentPreset ? 'bold' : '';
                item.style.color = item.dataset.preset === currentPreset ? '#e91e63' : '';
            });
            // Bind playhead/split/delete for model menu
            modelCtxMenu.querySelectorAll('.ctx-item[data-action]').forEach(item => {
                item.onclick = () => {
                    modelCtxMenu.style.display = 'none';
                    if (item.dataset.action === 'ctx-playhead') setPlayheadFromMouse(_ctxMouseX);
                    else if (item.dataset.action === 'ctx-split') fn.splitClipAtPlayhead();
                    else if (item.dataset.action === 'ctx-delete') fn.deleteSelectedClip();
                };
            });
            modelCtxMenu.style.display = '';
            modelCtxMenu.style.left = e.clientX + 'px';
            const menuH = modelCtxMenu.offsetHeight || 300;
            modelCtxMenu.style.top = Math.min(e.clientY, window.innerHeight - menuH - 10) + 'px';
            return;
        }

        // Normal context menu for other tracks
        modelCtxMenu.style.display = 'none';
        // Populate "Hinzufügen" submenu (nur wenn Track-Typ bekannt)
        if (track) _populateTrackAddSubmenu(track, trackIdx, ctxMenu, clickFrame, 'clip-ctx-add-submenu');
        const clipCtxAddItem = document.getElementById('clip-ctx-add');
        if (clipCtxAddItem) clipCtxAddItem.style.display = track ? '' : 'none';
        ctxMenu.style.display = '';
        ctxMenu.style.left = e.clientX + 'px';
        const menuH = ctxMenu.offsetHeight || 200;
        const maxY = window.innerHeight - menuH - 10;
        ctxMenu.style.top = Math.min(e.clientY, maxY) + 'px';
        ctxMenu.querySelectorAll('.ctx-item[data-action^="ctx-"]').forEach(item => {
            if (item.dataset.action === 'ctx-playhead') item.style.display = '';
            else item.style.display = hit ? '' : 'none';
        });
    });
    document.addEventListener('click', () => {
        if (ctxMenu) ctxMenu.style.display = 'none';
        if (modelCtxMenu) modelCtxMenu.style.display = 'none';
    });

    ctxMenu?.querySelectorAll('.ctx-item').forEach(item => {
        item.addEventListener('click', () => {
            ctxMenu.style.display = 'none';
            const action = item.dataset.action;
            if (action === 'ctx-split') fn.splitClipAtPlayhead();
            else if (action === 'ctx-delete') fn.deleteSelectedClip();
            else if (action === 'ctx-duplicate') fn.duplicateSelectedClip();
            else if (action === 'ctx-save-bvh') fn.saveBvhAs();
            else if (action === 'ctx-smooth') fn.smoothSelectedClip();
            else if (action === 'ctx-ground') fn.groundFixSelectedClip();
            else if (action === 'ctx-trim-start') fn.trimSelectedClip('start', 10);
            else if (action === 'ctx-trim-end') fn.trimSelectedClip('end', 10);
            else if (action === 'ctx-trim-reset') fn.trimSelectedClip('reset');
            else if (action === 'ctx-playhead') setPlayheadFromMouse(_ctxMouseX);
        });
    });

    // Drop clips on timeline
    tlCanvas.addEventListener('dragover', (e) => { e.preventDefault(); });
    tlCanvas.addEventListener('drop', (e) => {
        e.preventDefault();
        try {
            const data = JSON.parse(e.dataTransfer.getData('application/json'));
            const rect = tlCanvas.getBoundingClientRect();
            const y = e.clientY - rect.top - RULER_HEIGHT;
            const trackIdx = Math.floor(y / TRACK_HEIGHT);
            if (trackIdx >= 0 && trackIdx < state.project.tracks.length) {
                fn.addClipToTrack(trackIdx, data.category, data.name, data.frames);
            } else {
                // New track
                const track = fn.addTrack();
                fn.addClipToTrack(state.project.tracks.length - 1, data.category, data.name, data.frames);
            }
        } catch (err) { console.warn('Drop failed:', err); }
    });

    // Scroll
    tlCanvas.addEventListener('wheel', (e) => {
        if (e.ctrlKey) {
            state.timelineZoom = Math.max(10, Math.min(500, state.timelineZoom + (e.deltaY > 0 ? -10 : 10)));
            const zoomSlider = document.getElementById('tl-zoom');
            if (zoomSlider) zoomSlider.value = state.timelineZoom;
            document.getElementById('tl-zoom-label').textContent = `Zoom: ${state.timelineZoom}%`;
        } else {
            state.timelineScrollX = Math.max(0, state.timelineScrollX + e.deltaX + e.deltaY);
        }
        renderTimeline();
        e.preventDefault();
    });
}

export function renderTimeline() {
    if (!tlCtx || !tlCanvas) return;
    const w = tlCanvas.width, h = tlCanvas.height;
    const pps = state.timelineZoom;  // pixels per second at current zoom

    tlCtx.clearRect(0, 0, w, h);

    // Ruler
    tlCtx.fillStyle = '#1a1a2e';
    tlCtx.fillRect(0, 0, w, RULER_HEIGHT);
    tlCtx.strokeStyle = '#334155';
    tlCtx.lineWidth = 1;
    tlCtx.beginPath();
    tlCtx.moveTo(0, RULER_HEIGHT);
    tlCtx.lineTo(w, RULER_HEIGHT);
    tlCtx.stroke();

    // Time markers
    tlCtx.fillStyle = '#64748b';
    tlCtx.font = '10px monospace';
    const secStep = Math.max(1, Math.floor(50 / pps));
    for (let s = 0; s < state.project.duration + 10; s += secStep) {
        const x = HEADER_WIDTH + s * pps - state.timelineScrollX;
        if (x < HEADER_WIDTH || x > w) continue;
        tlCtx.fillText(`${s}s`, x + 2, 12);
        tlCtx.beginPath();
        tlCtx.moveTo(x, 14);
        tlCtx.lineTo(x, RULER_HEIGHT);
        tlCtx.stroke();
    }

    // Tracks + Clips
    for (let ti = 0; ti < state.project.tracks.length; ti++) {
        const track = state.project.tracks[ti];
        const y = RULER_HEIGHT + ti * TRACK_HEIGHT;

        // Track background
        tlCtx.fillStyle = ti === state.selectedTrackIdx ? 'rgba(124,92,191,0.1)' : 'rgba(0,0,0,0.2)';
        tlCtx.fillRect(HEADER_WIDTH, y, w - HEADER_WIDTH, TRACK_HEIGHT);
        tlCtx.strokeStyle = '#1e293b';
        tlCtx.beginPath();
        tlCtx.moveTo(HEADER_WIDTH, y + TRACK_HEIGHT);
        tlCtx.lineTo(w, y + TRACK_HEIGHT);
        tlCtx.stroke();

        // Clips
        // Draw interpolation lines for camera/light keyframe tracks first
        if ((track.type === 'camera' || track.type === 'light') && track.clips.length > 1) {
            tlCtx.strokeStyle = track.color;
            tlCtx.lineWidth = 1.5;
            tlCtx.globalAlpha = 0.4;
            tlCtx.beginPath();
            for (let ci = 0; ci < track.clips.length; ci++) {
                const cx = HEADER_WIDTH + (track.clips[ci].startFrame / state.project.fps) * pps - state.timelineScrollX;
                if (ci === 0) tlCtx.moveTo(cx, y + TRACK_HEIGHT / 2);
                else tlCtx.lineTo(cx, y + TRACK_HEIGHT / 2);
            }
            tlCtx.stroke();
            tlCtx.globalAlpha = 1.0;
        }

        for (let ci = 0; ci < track.clips.length; ci++) {
            const clip = track.clips[ci];
            const cx = HEADER_WIDTH + (clip.startFrame / state.project.fps) * pps - state.timelineScrollX;
            const isSelected = (ti === state.selectedTrackIdx && ci === state.selectedClipIdx);

            if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
                // Keyframe marker: diamond (camera) or circle (light)
                const my = y + TRACK_HEIGHT / 2;
                const sz = isSelected ? 8 : 6;
                tlCtx.fillStyle = track.color;
                tlCtx.globalAlpha = isSelected ? 1.0 : 0.8;
                if (clip.type === 'camera_kf') {
                    // Diamond
                    tlCtx.beginPath();
                    tlCtx.moveTo(cx, my - sz);
                    tlCtx.lineTo(cx + sz, my);
                    tlCtx.lineTo(cx, my + sz);
                    tlCtx.lineTo(cx - sz, my);
                    tlCtx.closePath();
                    tlCtx.fill();
                } else {
                    // Circle
                    tlCtx.beginPath();
                    tlCtx.arc(cx, my, sz, 0, Math.PI * 2);
                    tlCtx.fill();
                }
                if (isSelected) {
                    tlCtx.strokeStyle = '#fff';
                    tlCtx.lineWidth = 2;
                    tlCtx.stroke();
                }
                tlCtx.globalAlpha = 1.0;
                // Label rechts neben dem Marker (Name z.B. "Kameraposition 1")
                if (clip.name) {
                    tlCtx.fillStyle = isSelected ? '#fff' : 'rgba(255,255,255,0.75)';
                    tlCtx.font = '10px sans-serif';
                    tlCtx.textBaseline = 'middle';
                    tlCtx.fillText(clip.name, cx + sz + 4, my);
                }
            } else {
                // Rectangle clips (BVH, Audio)
                const cw = Math.max(clip.duration * pps, 4);
                const cy = y + 4;
                const ch = TRACK_HEIGHT - 8;

                tlCtx.fillStyle = track.color;
                tlCtx.globalAlpha = isSelected ? 1.0 : 0.7;
                tlCtx.fillRect(cx, cy, cw, ch);
                tlCtx.globalAlpha = 1.0;

                // Audio waveform indicator
                if (clip.type === 'audio') {
                    tlCtx.strokeStyle = 'rgba(255,255,255,0.3)';
                    tlCtx.lineWidth = 1;
                    for (let wx = cx + 4; wx < cx + cw - 2; wx += 6) {
                        const wh = 3 + Math.random() * (ch - 8);
                        tlCtx.beginPath();
                        tlCtx.moveTo(wx, cy + ch / 2 - wh / 2);
                        tlCtx.lineTo(wx, cy + ch / 2 + wh / 2);
                        tlCtx.stroke();
                    }
                }

                // Clip border
                tlCtx.strokeStyle = '#fff';
                tlCtx.lineWidth = isSelected ? 2 : 0.5;
                tlCtx.strokeRect(cx, cy, cw, ch);

                // Clip label
                tlCtx.fillStyle = '#fff';
                tlCtx.font = '10px sans-serif';
                if (clip.type === 'model' && clip.data?.preset) {
                    // Model clip: show person icon + preset name
                    const presetName = clip.data.preset;
                    const maxLen = Math.max(3, Math.floor((cw - 24) / 6));
                    const label = presetName.length > maxLen ? presetName.substring(0, maxLen) + '…' : presetName;
                    // Person icon (Unicode)
                    tlCtx.font = '12px sans-serif';
                    tlCtx.fillText('👤', cx + 3, cy + ch / 2 + 4);
                    // Preset name
                    tlCtx.font = 'bold 10px sans-serif';
                    tlCtx.fillText(label, cx + 18, cy + ch / 2 + 3, cw - 22);
                } else {
                    tlCtx.fillText(clip.name, cx + 4, cy + ch / 2 + 3, cw - 8);
                }
            }
        }
    }

    // Playhead
    const phX = HEADER_WIDTH + (state.playheadFrame / state.project.fps) * pps - state.timelineScrollX;
    if (phX >= HEADER_WIDTH) {
        tlCtx.strokeStyle = '#ef4444';
        tlCtx.lineWidth = 2;
        tlCtx.beginPath();
        tlCtx.moveTo(phX, 0);
        tlCtx.lineTo(phX, h);
        tlCtx.stroke();
        // Playhead handle
        tlCtx.fillStyle = '#ef4444';
        tlCtx.beginPath();
        tlCtx.moveTo(phX - 6, 0);
        tlCtx.lineTo(phX + 6, 0);
        tlCtx.lineTo(phX, 10);
        tlCtx.fill();
    }

    // Update frame info
    const info = document.getElementById('tl-frame-info');
    if (info) info.textContent = `Frame ${state.playheadFrame} / ${Math.round(state.project.duration * state.project.fps)}`;
}

export function updateTrackHeaders() {
    const container = document.getElementById('track-headers');
    if (!container) return;
    container.innerHTML = '';
    // Ruler space
    const ruler = document.createElement('div');
    ruler.style.cssText = `height:${RULER_HEIGHT}px;border-bottom:1px solid var(--border);`;
    container.appendChild(ruler);

    for (let i = 0; i < state.project.tracks.length; i++) {
        const track = state.project.tracks[i];
        const el = document.createElement('div');
        el.className = 'track-header' + (i === state.selectedTrackIdx ? ' selected' : '');
        const icon = TRACK_ICONS[track.type] || 'fa-running';
        el.innerHTML = `<i class="fas ${icon}" style="color:${track.color};margin-right:6px;font-size:0.75rem;width:14px;text-align:center;"></i>${track.name}`;
        el.addEventListener('click', () => fn.selectTrack(i));
        // Right-click: track context menu
        el.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            fn.selectTrack(i);
            const ctx = document.getElementById('track-context-menu');
            if (!ctx) return;
            // Populate "Hinzufügen" submenu based on track type
            _populateTrackAddSubmenu(track, i, ctx);
            // Show/hide link section for model tracks
            const linkSection = document.getElementById('track-ctx-link-section');
            const linkList = document.getElementById('track-ctx-link-list');
            if (track.type === 'model' && linkSection && linkList) {
                linkSection.style.display = '';
                linkList.innerHTML = '';
                state.project.animations.forEach(t => {
                    const ti = state.project.indexOf(t);
                    const item = document.createElement('div');
                    item.className = 'ctx-item';
                    const isLinked = track._linkedAnimIdx === ti;
                    item.innerHTML = `<i class="fas ${isLinked ? 'fa-check' : 'fa-running'}" style="width:16px;color:${isLinked ? '#4caf50' : '#666'};"></i> ${t.name}`;
                    item.style.fontWeight = isLinked ? 'bold' : '';
                    item.addEventListener('click', () => {
                        pushUndo('Verknüpfung ändern');
                        track._linkedAnimIdx = ti;
                        track._currentPreset = null;
                        fn.applyPlayhead();
                        ctx.style.display = 'none';
                    });
                    linkList.appendChild(item);
                });
            } else if (linkSection) {
                linkSection.style.display = 'none';
            }
            ctx.style.display = '';
            ctx.style.left = e.clientX + 'px';
            const menuH = ctx.offsetHeight || 200;
            ctx.style.top = Math.min(e.clientY, window.innerHeight - menuH - 10) + 'px';
        });
        // Drop target
        el.addEventListener('dragover', (e) => { e.preventDefault(); el.classList.add('drop-target'); });
        el.addEventListener('dragleave', () => el.classList.remove('drop-target'));
        el.addEventListener('drop', (e) => {
            e.preventDefault();
            el.classList.remove('drop-target');
            try {
                const data = JSON.parse(e.dataTransfer.getData('application/json'));
                fn.addClipToTrack(i, data.category, data.name, data.frames);
            } catch (err) {}
        });
        container.appendChild(el);
    }
}

export function updateDuration() {
    // Duration is now auto-computed by Timeline.duration getter.
    // This function is kept for backward compatibility (called from many places).
}

// Register functions in registry
fn.renderTimeline = renderTimeline;
fn.updateTrackHeaders = updateTrackHeaders;
fn.updateDuration = updateDuration;
fn.setupTimeline = setupTimeline;
