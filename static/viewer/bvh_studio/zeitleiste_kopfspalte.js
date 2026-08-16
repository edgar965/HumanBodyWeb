/**
 * Kopfspalte der Zeitleiste — die Spurnamen links.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026). Die Hoehe folgt der
 * Leinwand, damit die Spalte beim Scrollen mitgeht.
 */

import { state, TRACK_HEIGHT, RULER_HEIGHT, TRACK_ICONS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Reihen } from './zeitleiste_reihen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { _populateTrackAddSubmenu } from './zeitleiste_spurmenue.js';
import { pushUndo } from './undo.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';


export function updateTrackHeaders() {
    const container = document.getElementById('track-headers');
    if (!container) return;
    container.innerHTML = '';
    // Genauso hoch wie die Leinwand, damit die Kopfspalte beim Scrollen
    // mitgeht (das CSS hat kein `bottom: 0` mehr — siehe bvh_studio.html).
    if (Zeitleistenflaeche.canvas) container.style.height = Zeitleistenflaeche.canvas.height + 'px';
    const ruler = document.createElement('div');
    ruler.style.cssText = `height:${RULER_HEIGHT}px;border-bottom:1px solid var(--border);`;
    container.appendChild(ruler);

    const rows = Reihen.liste();
    for (const row of rows) {
        if (row.header) {
            const isLight = row.header === 'light';
            const bgColor = isLight ? 'rgba(255,193,7,0.12)' : 'rgba(124,92,191,0.12)';
            const borderColor = isLight ? 'rgba(255,193,7,0.4)' : 'rgba(124,92,191,0.4)';
            const textColor = isLight ? '#ffc107' : '#b388ff';
            const icon = isLight ? 'fa-lightbulb' : 'fa-cube';
            const headerEl = document.createElement('div');
            headerEl.className = 'track-group-header';
            headerEl.style.cssText = `height:${TRACK_HEIGHT}px;padding:0 12px;background:${bgColor};border-top:1px solid ${borderColor};border-bottom:1px solid ${borderColor};color:${textColor};font-weight:bold;font-size:0.78rem;display:flex;align-items:center;box-sizing:border-box;cursor:pointer;user-select:none;`;
            const caretClass = row.collapsed ? 'fa-caret-right' : 'fa-caret-down';
            headerEl.innerHTML = `<i class="fas ${caretClass}" style="margin-right:6px;width:10px;"></i><i class="fas ${icon}" style="margin-right:6px;"></i>${row.label}`;
            headerEl.title = 'Klick zum Ein-/Ausklappen';
            headerEl.addEventListener('click', () => {
                if (isLight) state.lightGroupCollapsed = !state.lightGroupCollapsed;
                else state.sceneGroupCollapsed = !state.sceneGroupCollapsed;
                updateTrackHeaders();
                renderTimeline();
            });
            container.appendChild(headerEl);
            continue;
        }
        const i = row.trackIdx;
        const track = state.project.tracks[i];
        const el = document.createElement('div');
        el.className = 'track-header' + (i === state.selectedTrackIdx ? ' selected' : '');
        if (row.indent) el.style.paddingLeft = '20px';
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
            // Update Ausschalten/Einschalten label based on mute state
            const muteLabel = document.getElementById('track-ctx-mute-label');
            if (muteLabel) muteLabel.textContent = track.muted ? 'Einschalten' : 'Ausschalten';
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

fn.updateTrackHeaders = updateTrackHeaders;
