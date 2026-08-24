/**
 * BVH Studio — Export1 tab: cloth-simulation MP4 export via the 3 engines.
 *
 * Gathers the currently visible Modell track's mesh + skeleton + cached
 * modelData, samples the active animation per-frame, and POSTs everything
 * to /api/cloth/export/. No popup, no Scene page.
 */
import './state.js';
import '../gemeinsam/registrierung.js';
import { _buildPayload } from './export_nutzlast.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


function _setStatus(text, color) {
    const box = document.getElementById('cloth-export-status');
    const el = document.getElementById('cloth-export-status-text');
    if (!box || !el) return;
    box.style.display = text ? 'block' : 'none';
    el.textContent = text || '';
    el.style.color = color || 'var(--text-muted)';
}

function _setButtonsEnabled(enabled) {
    document.querySelectorAll('.cloth-export-btn').forEach(b => {
        b.disabled = !enabled;
        b.style.opacity = enabled ? '1' : '0.5';
        b.style.cursor = enabled ? 'pointer' : 'wait';
    });
}

function _progress(engine, pct, text, color) {
    const bar = document.querySelector(`.cloth-progress[data-engine="${engine}"]`);
    if (!bar) return;
    if (pct === null) { bar.style.display = 'none'; return; }
    bar.style.display = 'block';
    const fill = bar.querySelector('.cloth-progress-fill');
    const label = bar.querySelector('.cloth-progress-text');
    if (fill) fill.style.width = Math.max(0, Math.min(100, pct)) + '%';
    if (label) {
        label.textContent = text || '';
        if (color) label.style.color = color;
    }
}

// Monotonic ramp, 25% → 95%, labelled with elapsed seconds.
// Per-engine singleton: starting a new one stops the previous.
const _progressTimers = {};
function _startProgress(engine, expectedSeconds = 30, label = 'Sim + Render läuft') {
    if (_progressTimers[engine]) {
        clearInterval(_progressTimers[engine].t);
        _progressTimers[engine] = null;
    }
    const t0 = performance.now();
    let lastPct = 25;
    const tick = () => {
        const elapsed = (performance.now() - t0) / 1000;
        let target;
        if (elapsed < expectedSeconds) target = 25 + (elapsed / expectedSeconds) * 60;
        else target = 85 + Math.min(10, ((elapsed - expectedSeconds) / expectedSeconds) * 10);
        // Strict monotonic: never decrease
        lastPct = Math.max(lastPct, target);
        _progress(engine, lastPct, `${label} — ${elapsed.toFixed(0)}s`);
    };
    tick();
    const t = setInterval(tick, Zeiten.FORTSCHRITT_MS);
    _progressTimers[engine] = { t };
    return () => {
        if (_progressTimers[engine]) { clearInterval(_progressTimers[engine].t); _progressTimers[engine] = null; }
    };
}










// Module-level AbortController, damit _runClothExport einen cancel-Button
// bedienen kann. Nur eines aktiv gleichzeitig.
let _clothAbort = null;

async function _runClothExport(engine) {
    const duration = parseFloat(document.getElementById('cloth-duration')?.value || '3.0');
    const fps = parseInt(document.getElementById('cloth-fps')?.value || '30');
    const qualityIdMap = {
        'blender_eevee':    'cloth-quality-blender-eevee',
        'warp_blender':     'cloth-quality-warp-blender',
        'warp_only':        'cloth-quality-warp-only',
        'skinning_blender': null,  // Skinning hat keine Quality-Stufe
    };
    const quality = document.getElementById(qualityIdMap[engine])?.value || 'medium';
    const resolutionHeight = parseInt(document.getElementById('cloth-resolution')?.value || '1080');
    const resolutionMap = {720: [1280, 720], 1080: [1920, 1080], 1440: [2560, 1440], 2160: [3840, 2160]};
    const [width, height] = resolutionMap[resolutionHeight] || [1920, 1080];
    const outputDir = (document.getElementById('cloth-target-dir')?.value || '').trim();
    let filename = (document.getElementById('cloth-filename')?.value || '').trim() || 'cloth_export.mp4';
    if (!filename.toLowerCase().endsWith('.mp4')) filename += '.mp4';

    _setButtonsEnabled(false);
    _progress(engine, 5, 'Daten aus BVH Studio sammeln…');
    _setStatus(`Daten sammeln für ${engine}…`, 'var(--accent)');

    let payload;
    try {
        payload = await _buildPayload({ duration, fps });
    } catch (e) {
        _progress(engine, 100, `Fehler: ${e.message}`, '#e74c3c');
        _setStatus(`Fehler: ${e.message}`, '#e74c3c');
        _setButtonsEnabled(true);
        setTimeout(() => _progress(engine, null), 6000);
        return;
    }
    payload.engine = engine;
    payload.quality = quality;
    payload.width = width;
    payload.height = height;
    if (outputDir) payload.output_dir = outputDir;
    if (filename) payload.filename = filename;

    _progress(engine, 25, `POST ${payload.anim_frames} Frames → Server`);
    _setStatus(`Läuft: ${engine}, ${payload.anim_frames} Frames…`, 'var(--accent)');

    const expectedSec = { blender_eevee: 60, warp_blender: 30, warp_only: 20, skinning_blender: 25 }[engine] || 30;
    const stopPulse = _startProgress(engine, expectedSec, `${engine}: Sim + Render`);
    const t0 = performance.now();
    // Cancel-Button sichtbar machen + AbortController verbinden
    _clothAbort = new AbortController();
    const cancelBtn = document.getElementById('cloth-export-cancel');
    if (cancelBtn) cancelBtn.style.display = '';
    try {
        // Kein `Serverabruf.senden`: Der Abbruch-Knopf braucht das `signal`.
        const data = await Serverabruf.json('/api/cloth/export/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json',
                       'X-CSRFToken': Serverabruf.csrfToken() },
            body: JSON.stringify(payload),
            signal: _clothAbort.signal,
        });
        stopPulse();
        const elapsed = ((performance.now() - t0) / 1000).toFixed(1);
        if (data.ok) {
            const t = Math.round(data.elapsed_sec || elapsed);
            const href = data.url || data.output || '';
            _progress(engine, 100, `✓ ${t}s → ${href.split(/[/\\]/).pop()}`, '#4caf50');
            _setStatus(`✓ Fertig in ${t}s → ${href}`, '#4caf50');
            if (href) window.open(href, '_blank');
        } else {
            console.error('[Cloth Export] failed:', data);
            _progress(engine, 100, `Fehler — siehe Console`, '#e74c3c');
            _setStatus(`Fehler: ${data.error || 'siehe Console'} (log: ${(data.log || '').slice(-200)})`, '#e74c3c');
        }
    } catch (e) {
        stopPulse();
        if (e.name === 'AbortError') {
            _progress(engine, 100, 'Abgebrochen', '#ff9800');
            _setStatus('Export abgebrochen. Der Server-Prozess läuft ggf. noch im Hintergrund weiter.', '#ff9800');
        } else {
            _progress(engine, 100, `Netzwerkfehler: ${e.message}`, '#e74c3c');
            _setStatus(`Netzwerkfehler: ${e.message}`, '#e74c3c');
        }
    } finally {
        _setButtonsEnabled(true);
        if (cancelBtn) cancelBtn.style.display = 'none';
        _clothAbort = null;
        setTimeout(() => _progress(engine, null), 15000);
    }
}

async function _autofillTargetDir() {
    const el = document.getElementById('cloth-target-dir');
    if (!el || el.value) return;
    try {
        const prefs = await Serverabruf.json('/api/ui-prefs/');
        el.value = prefs.studio_video_output || '';
    } catch (e) { Protokoll.debug('export', 'Ausgabeordner nicht abrufbar', e); }
}

export function bindClothExportButtons() {
    _autofillTargetDir();
    document.querySelectorAll('.props-tab').forEach(tab => {
        if (tab.dataset.tab === 'export1') tab.addEventListener('click', _autofillTargetDir);
    });
    document.getElementById('cloth-export-cancel')?.addEventListener('click', () => {
        if (_clothAbort) _clothAbort.abort();
    });
    document.querySelectorAll('.cloth-export-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const engine = btn.dataset.engine;
            if (!engine) return;
            Protokoll.debug('Cloth Export', `Klick auf ${engine}`);
            _runClothExport(engine);
        });
    });
    Protokoll.debug('Cloth Export', 'bound ' + document.querySelectorAll('.cloth-export-btn').length + ' buttons');
}
