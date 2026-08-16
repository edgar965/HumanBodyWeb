/**
 * Bodenfix und Speichern der angewandten Effekte.
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _fixedPos } from './werkzeug_position.js';
import { _gaussSmooth } from './werkzeug_glaettung.js';
import { Bodenrichter } from './bodenrichter.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


export async function saveBvhWithEffects() {
    // Collect all clips
    const clips = [];
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (const clip of track.clips) {
            if (clip.category && clip.name) clips.push(clip);
        }
    }
    if (clips.length === 0) {
        const pi = fn.getPreviewInfo ? fn.getPreviewInfo() : null;
        if (pi && pi.category && pi.name) clips.push({ category: pi.category, name: pi.name });
    }
    if (clips.length === 0) { alert('Keine Animation geladen.'); return; }

    // Build effects list
    const effects = {};
    if (_gaussSmooth.active) effects.sigma = _gaussSmooth.sigma;
    if (_fixedPos.active) effects.fixed_radius = _fixedPos.radius;

    if (Object.keys(effects).length === 0) {
        alert('Keine Effekte aktiv (Smooth oder Feste Position einschalten).');
        return;
    }

    const desc = [];
    if (effects.sigma) desc.push(`Smooth σ=${effects.sigma}`);
    if (effects.fixed_radius) desc.push(`Feste Position r=${(effects.fixed_radius * 100).toFixed(0)}cm`);

    if (!confirm(`BVH speichern mit: ${desc.join(', ')}\n\n${clips.length} Clip(s) werden überschrieben!`)) return;

    let saved = 0;
    for (const clip of clips) {
        try {
            const result = await Serverabruf.json('/api/retarget/save-bvh-effects/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: clip.category, name: clip.name, ...effects }),
            });
            if (result.ok) saved++;
            else console.error(`Save failed for ${clip.name}:`, result.error);
        } catch (e) { console.error(`Save failed for ${clip.name}:`, e); }
    }

    // Clear caches so next load picks up saved version
    _gaussSmooth.origClips.clear();
    _fixedPos.origData.clear();
    alert(`Gespeichert: ${saved}/${clips.length} Clip(s) mit ${desc.join(', ')}`);
    Protokoll.info('BVH Studio', `Saved with effects: ${saved} clips, ${desc.join(', ')}`);
}

export async function groundFixSelectedClip() {
    // Die Arbeit steckt in `Bodenrichter` (bodenrichter.js) — vorher standen
    // hier 146 Zeilen, davon 60 fuer das Nachziehen der BVH-Datei als Text.
    return Bodenrichter.gewaehlten();
}
