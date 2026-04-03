/**
 * BVH Studio — Timeline canvas drawing and mouse interaction.
 */
import { state, TRACK_HEIGHT, HEADER_WIDTH, RULER_HEIGHT, TRACK_ICONS } from './state.js';
import { fn } from './registry.js';
import { pushUndo } from './undo.js';
import { setLibSelectedItem } from './library.js';

let tlCanvas, tlCtx;

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

            // No clip hit -- start scrubbing (playhead follows mouse)
            if (mx > HEADER_WIDTH) {
                dragMode = 'scrub';
                dragStartX = mx;

                // Select track by Y position
                if (my > RULER_HEIGHT) {
                    const ti = Math.floor((my - RULER_HEIGHT) / TRACK_HEIGHT);
                    if (ti >= 0 && ti < state.project.tracks.length) {
                        state.selectedTrackIdx = ti;
                        state.selectedClipIdx = -1;
                        fn.updateProperties();
                    }
                }

                setPlayheadFromMouse(mx);
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
    tlCanvas.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        const rect = tlCanvas.getBoundingClientRect();
        const hit = hitTestClip(e.clientX - rect.left, e.clientY - rect.top);
        if (hit) {
            state.selectedTrackIdx = hit.trackIdx;
            state.selectedClipIdx = hit.clipIdx;
            fn.updateProperties();
            renderTimeline();
            ctxMenu.style.display = '';
            ctxMenu.style.left = e.clientX + 'px';
            ctxMenu.style.top = e.clientY + 'px';
        } else {
            ctxMenu.style.display = 'none';
        }
    });
    document.addEventListener('click', () => { if (ctxMenu) ctxMenu.style.display = 'none'; });

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
                tlCtx.fillText(clip.name, cx + 4, cy + ch / 2 + 3, cw - 8);
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
            if (ctx) { ctx.style.display = ''; ctx.style.left = e.clientX + 'px'; ctx.style.top = e.clientY + 'px'; }
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
    let maxEnd = 0;
    for (const track of state.project.tracks) {
        for (const clip of track.clips) {
            const end = clip.endFrame / state.project.fps;
            if (end > maxEnd) maxEnd = end;
        }
    }
    state.project.duration = maxEnd;
}

// Register functions in registry
fn.renderTimeline = renderTimeline;
fn.updateTrackHeaders = updateTrackHeaders;
fn.updateDuration = updateDuration;
fn.setupTimeline = setupTimeline;
