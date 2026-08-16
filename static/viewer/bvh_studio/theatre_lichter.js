/**
 * Theatre-Lichtvorgaben auf die Szene anwenden.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import './models.js';
import './spur_lichter.js';
import { pushUndo } from './undo.js';
import { _createLightTrackFromDef } from './theatre_lichtspuren.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

let _cachedTheatrePresets = null;


export async function _fetchTheatrePresets() {
    if (_cachedTheatrePresets) return _cachedTheatrePresets;
    const data = await Serverabruf.json('/api/studio/theatre-presets/');
    _cachedTheatrePresets = data.presets || [];
    return _cachedTheatrePresets;
}


async function _applyTheatrePreset(presetName) {
    let preset;
    try {
        preset = await Serverabruf.json(
            `/api/studio/theatre-preset/${encodeURIComponent(presetName)}/`);
    } catch (fehler) {
        alert(`Preset "${presetName}" nicht ladbar: ${fehler.message}`);
        return;
    }
    const presetLights = preset.lights || [];
    pushUndo(`Theatre-Preset: ${preset.label || presetName}`);

    // 1) Alle vorhandenen Licht-Tracks entfernen (Szenen-Lichter + Preset-Lichter)
    //    damit das neue Preset eine saubere Licht-Setup erzeugt.
    const lightIndices = [];
    for (let i = 0; i < state.project.tracks.length; i++) {
        if (state.project.tracks[i].type === 'light') lightIndices.push(i);
    }
    // Von hinten entfernen (Indizes bleiben stabil)
    for (let j = lightIndices.length - 1; j >= 0; j--) {
        const idx = lightIndices[j];
        const t = state.project.tracks[idx];
        if (t.light) {
            if (t.light.target) state.scene.remove(t.light.target);
            state.scene.remove(t.light);
            t.light.dispose?.();
        }
        if (t.lightHelper) {
            state.scene.remove(t.lightHelper);
            t.lightHelper.traverse?.(obj => {
                if (obj.geometry) obj.geometry.dispose?.();
                if (obj.material) obj.material.dispose?.();
            });
        }
        state.project.tracks.splice(idx, 1);
    }

    // 2) Preset-Lichter als neue Tracks anlegen (mit nativen Typen)
    let newTracks = 0;
    for (const def of presetLights) {
        if (_createLightTrackFromDef(def, preset.label || presetName)) newTracks++;
    }

    if (state.selectedTrackIdx >= state.project.tracks.length) {
        state.selectedTrackIdx = state.project.tracks.length - 1;
    }
    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
    fn.updateProperties?.();
    fn.applyPlayhead?.();
    fn.serverLog?.('theatre_preset_applied',
        `${presetName}: alte Lichter entfernt, ${newTracks} Preset-Lichter`);
}


export async function populateTheatrePresetsMenu() {
    const submenu = document.getElementById('theatre-lights-submenu');
    if (!submenu) return;
    submenu.innerHTML = '<div class="ctx-submenu-empty">Lade...</div>';
    try {
        const presets = await _fetchTheatrePresets();
        submenu.innerHTML = '';
        if (presets.length === 0) {
            submenu.innerHTML = '<div class="ctx-submenu-empty">Keine Presets verfügbar</div>';
            return;
        }
        for (const p of presets) {
            const item = document.createElement('div');
            item.className = 'ctx-item';
            item.innerHTML = `
                <i class="fas fa-lightbulb" style="width:16px;color:#ffc107;"></i>
                <span>${p.label}</span>
                <span style="margin-left:auto;font-size:0.7rem;color:var(--text-muted);">${p.lightCount}x</span>
            `;
            item.title = p.description || '';
            item.addEventListener('click', async () => {
                document.getElementById('theatre-dropdown')?.classList.remove('open');
                await _applyTheatrePreset(p.name);
            });
            submenu.appendChild(item);
        }
    } catch (e) {
        submenu.innerHTML = '<div class="ctx-submenu-empty">Fehler beim Laden</div>';
    }
}

export function setupTheatreMenu() {
    const dd = document.getElementById('theatre-dropdown');
    const btn = document.getElementById('btn-theatre');
    if (!dd || !btn) return;
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        dd.classList.toggle('open');
        if (dd.classList.contains('open')) populateTheatrePresetsMenu();
    });
    document.addEventListener('click', () => dd.classList.remove('open'));
}

fn.setupTheatreMenu = setupTheatreMenu;
fn.fetchTheatrePresets = _fetchTheatrePresets;
