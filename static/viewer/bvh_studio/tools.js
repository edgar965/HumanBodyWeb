/**
 * BVH Studio — Toolbar, Help system, Gaussian Smooth, Ground Fix.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { undo, redo, pushUndo } from './undo.js';
import { HELP_CONTENT } from './hilfetexte.js';
import { _gaussSmooth, _gaussFilter, _updateGaussUI, applyGaussToAllClips, reloadAllClipAnimations, smoothSelectedClip, saveSmoothedBVH } from './werkzeug_glaettung.js';
import { _fixedPos, applyFixedPositionAll, restoreFixedPositionAll } from './werkzeug_position.js';
import { groundFixSelectedClip, saveBvhWithEffects } from './werkzeug_boden.js';


export function setupToolbar() {
    // Track dropdown
    const trackDD = document.getElementById('track-dropdown');
    document.getElementById('btn-add-track')?.addEventListener('click', (e) => { e.stopPropagation(); trackDD?.classList.toggle('open'); });
    document.getElementById('dd-add-bvh')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addTrack(); });
    document.getElementById('dd-add-camera')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addSpecialTrack('camera'); });
    document.getElementById('dd-add-light')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addSpecialTrack('light'); });
    document.getElementById('dd-add-audio')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addSpecialTrack('audio'); });
    document.getElementById('dd-add-model')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addModelTrack(); });

    document.getElementById('btn-undo')?.addEventListener('click', () => undo());
    document.getElementById('btn-redo')?.addEventListener('click', () => redo());
    document.getElementById('btn-delete-track')?.addEventListener('click', () => fn.removeTrack(state.selectedTrackIdx));
    document.getElementById('btn-delete-clip')?.addEventListener('click', () => fn.deleteSelectedClip());
    document.getElementById('btn-split')?.addEventListener('click', fn.splitClipAtPlayhead);
    document.getElementById('btn-export-bvh')?.addEventListener('click', fn.exportBVH);
    document.getElementById('btn-export-video')?.addEventListener('click', () => {
        // Switch to Export tab and update range
        fn.switchPropsTab('export');
        const toEl = document.getElementById('export-to');
        if (toEl && (toEl.value === '0' || !toEl.value)) toEl.value = Math.round(state.project.duration * state.project.fps);
    });
    // File dropdown
    const fileDD = document.getElementById('file-dropdown');
    document.getElementById('btn-file')?.addEventListener('click', (e) => { e.stopPropagation(); fileDD?.classList.toggle('open'); });
    document.getElementById('dd-file-save')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.saveProject(); });
    document.getElementById('dd-file-save-as')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.saveProjectAs(); });
    document.getElementById('dd-file-load')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.loadProject(); });
    document.getElementById('dd-file-load-last')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.loadLastProject(); });
    document.getElementById('dd-file-default')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.resetToDefault(); });

    // Tools dropdown
    const toolsDD = document.getElementById('tools-dropdown');
    const toolsBtn = document.getElementById('btn-tools');
    toolsBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        toolsDD.classList.toggle('open');
    });
    document.addEventListener('click', () => {
        fileDD?.classList.remove('open');
        toolsDD?.classList.remove('open');
        trackDD?.classList.remove('open');
        document.getElementById('help-dropdown')?.classList.remove('open');
    });
    // Gaussian Smooth
    document.getElementById('dd-gauss-on')?.addEventListener('click', () => {
        _gaussSmooth.active = true;
        _updateGaussUI();
        applyGaussToAllClips();
        toolsDD.classList.remove('open');
    });
    document.getElementById('dd-gauss-off')?.addEventListener('click', () => {
        _gaussSmooth.active = false;
        _updateGaussUI();
        reloadAllClipAnimations();
        toolsDD.classList.remove('open');
    });
    document.getElementById('dd-gauss-sigma-input')?.addEventListener('change', (e) => {
        _gaussSmooth.sigma = Math.max(0.5, Math.min(20, parseFloat(e.target.value) || 2));
        e.target.value = _gaussSmooth.sigma;
        _updateGaussUI();
        if (_gaussSmooth.active) applyGaussToAllClips();
    });
    document.getElementById('dd-gauss-save')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        saveSmoothedBVH();
    });
    document.getElementById('dd-ground')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        fn.switchPropsTab('tools');
        groundFixSelectedClip();
    });
    // Fixed Position toggle
    document.getElementById('dd-fixed-pos')?.addEventListener('click', () => {
        _fixedPos.active = !_fixedPos.active;
        document.getElementById('fixed-pos-status').textContent = _fixedPos.active ? 'An' : 'Aus';
        document.getElementById('fixed-pos-status').style.color = _fixedPos.active ? '#4caf50' : 'var(--text-muted)';
        if (_fixedPos.active) applyFixedPositionAll();
        else restoreFixedPositionAll();
        toolsDD.classList.remove('open');
    });
    document.getElementById('fixed-pos-radius')?.addEventListener('input', (e) => {
        e.stopPropagation();
        const v = parseInt(e.target.value);
        document.getElementById('fixed-pos-radius-val').textContent = v + 'cm';
        _fixedPos.radius = v / 100;  // cm -> meters
        if (_fixedPos.active) applyFixedPositionAll();
    });
    // Save BVH with all current effects
    document.getElementById('dd-save-bvh')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        saveBvhWithEffects();
    });

    // Properties panel tabs
    document.querySelectorAll('.props-tab').forEach(tab => {
        tab.addEventListener('click', () => fn.switchPropsTab(tab.dataset.tab));
    });

    // Tools panel buttons
    document.getElementById('tool-smooth-apply')?.addEventListener('click', smoothSelectedClip);
    document.getElementById('tool-ground-apply')?.addEventListener('click', groundFixSelectedClip);
    document.getElementById('tool-smooth-sigma')?.addEventListener('input', (e) => {
        const sigma = parseFloat(e.target.value) || 2;
        const radiusEl = document.getElementById('tool-smooth-radius');
        if (radiusEl) radiusEl.textContent = Math.ceil(sigma * 3);
    });

    // Track context menu
    const trackCtx = document.getElementById('track-context-menu');
    document.addEventListener('click', () => { if (trackCtx) trackCtx.style.display = 'none'; });
    document.getElementById('track-ctx-delete')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (state.selectedTrackIdx >= 0) fn.removeTrack(state.selectedTrackIdx);
    });
    document.getElementById('track-ctx-rename')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (state.selectedTrackIdx >= 0) {
            const track = state.project.tracks[state.selectedTrackIdx];
            const newName = prompt('Neuer Track-Name:', track.name);
            if (newName && newName !== track.name) {
                pushUndo('Spur umbenennen');
                track.name = newName;
                fn.updateTrackHeaders();
                fn.updateProperties();
            }
        }
    });
    document.getElementById('track-ctx-mute')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (state.selectedTrackIdx >= 0) {
            pushUndo('Mute/Unmute');
            const track = state.project.tracks[state.selectedTrackIdx];
            track.muted = !track.muted;
            if (track.type === 'light' && track.light) {
                track.light.visible = !track.muted;
                if (track.lightHelper) track.lightHelper.visible = !track.muted && track.lightVisible;
            }
            fn.updateProperties();
        }
    });

    // Help dropdown
    const helpDD = document.getElementById('help-dropdown');
    document.getElementById('btn-help')?.addEventListener('click', (e) => { e.stopPropagation(); helpDD?.classList.toggle('open'); });
    document.getElementById('dd-help-tracks')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('tracks'); });
    document.getElementById('dd-help-camera')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('camera'); });
    document.getElementById('dd-help-light')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('light'); });
    document.getElementById('dd-help-audio')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('audio'); });
    document.getElementById('dd-help-shortcuts')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('shortcuts'); });
    document.getElementById('dd-help-animations')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('animations'); });
    document.getElementById('dd-help-export')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('export'); });
    document.getElementById('help-modal-close')?.addEventListener('click', () => { document.getElementById('help-modal').style.display = 'none'; });
    document.getElementById('help-modal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) e.currentTarget.style.display = 'none'; });
}

// =========================================================================
// Help system
// =========================================================================

export function showHelp(topic) {
    const h = HELP_CONTENT[topic];
    if (!h) return;
    document.getElementById('help-modal-title').innerHTML = `<i class="fas fa-question-circle"></i> ${h.title}`;
    document.getElementById('help-modal-body').innerHTML = h.body;
    document.getElementById('help-modal').style.display = 'flex';
}












// Register functions in registry
fn.setupToolbar = setupToolbar;
fn.showHelp = showHelp;
fn.smoothSelectedClip = smoothSelectedClip;
fn.groundFixSelectedClip = groundFixSelectedClip;
fn.getGaussSmooth = () => _gaussSmooth;
fn.gaussFilter = _gaussFilter;
fn.applyGaussToAllClips = applyGaussToAllClips;
fn.reloadAllClipAnimations = reloadAllClipAnimations;
fn.getFixedPos = () => _fixedPos;
fn.applyFixedPositionAll = applyFixedPositionAll;
fn.restoreFixedPositionAll = restoreFixedPositionAll;
