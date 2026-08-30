/**
 * Voreinstellungen im Voraus laden, damit der Modellwechsel nicht stockt.
 *
 * Aus playback.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import * as THREE from 'three';
import { Protokoll } from '../gemeinsam/protokoll.js';


// Preload-Cache: lädt Preset-Assets im Hintergrund via Shadow-Track.
// Resolved zu {group, mesh, skeleton, mixer}. Beim Switch wird die vorbereitete
// Gruppe atomic in den echten Track übernommen.
export async function _preloadPreset(animTrack, preset) {
    if (!animTrack._preloadCache) animTrack._preloadCache = {};
    if (animTrack._preloadCache[preset]) return animTrack._preloadCache[preset];
    const shadow = {
        name: `${animTrack.name}_preload_${preset}`,
        type: animTrack.type,
        preset: preset,
        bodyType: animTrack.bodyType,
        group: new THREE.Group(),
    };
    shadow.group.visible = false;
    state.scene.add(shadow.group);
    const promise = fn.loadTrackCharacter(shadow).then(() => ({
        group: shadow.group, mesh: shadow.mesh, skeleton: shadow.skeleton, mixer: shadow.mixer,
    })).catch(e => {
        state.scene.remove(shadow.group);
        delete animTrack._preloadCache[preset];
        throw e;
    });
    animTrack._preloadCache[preset] = promise;
    return promise;
}

export function _swapToPreloaded(animTrack, assets, activePreset) {
    // Alte Group aus Szene entfernen (Meshes werden weiter unten disposed bei Bedarf)
    if (animTrack.group) {
        state.scene.remove(animTrack.group);
        // Dispose alte Kinder (altes Preset wird nicht mehr gebraucht)
        animTrack.group.traverse?.(obj => {
            if (obj.geometry) obj.geometry.dispose?.();
            if (obj.material) {
                if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose?.());
                else obj.material.dispose?.();
            }
        });
    }
    animTrack.group = assets.group;
    animTrack.group.visible = true;
    animTrack.mesh = assets.mesh;
    animTrack.skeleton = assets.skeleton;
    animTrack.mixer = assets.mixer;
    animTrack._activeClip = null;
    animTrack._activeAction = null;
    animTrack.meshActive = activePreset;
    animTrack._loadingPreset = null;
    if (animTrack._preloadCache) delete animTrack._preloadCache[activePreset];
    fn.serverLog('preset_swap_preloaded', `track=${animTrack.name} preset=${activePreset}`);
}

// Prüft Model-Tracks: startet Preload für Presets die demnächst aktiv werden.
export function _schedulePreloads(t) {
    const lookahead = state.project.preloadSeconds;
    if (!lookahead || lookahead <= 0) return;
    for (const track of state.project.tracks) {
        if (track.type !== 'model') continue;
        const animTrack = state.project.getLinkedAnimation(track);
        if (!animTrack) continue;
        for (const clip of track.clips) {
            if (clip.type !== 'model' || !clip.data?.preset) continue;
            const cs = clip.startFrame / state.project.fps;
            // Clip beginnt innerhalb lookahead-Fensters — bereits geladen oder am Laden? Skip.
            if (cs > t && cs - t <= lookahead) {
                const preset = clip.data.preset;
                if (animTrack.meshActive === preset) continue;
                if (animTrack._loadingPreset === preset) continue;
                if (animTrack._preloadCache?.[preset]) continue;
                _preloadPreset(animTrack, preset).catch((e) => { Protokoll.debug('vorladen',
                    `Vorladen von ${preset} fehlgeschlagen`, e); });
            }
        }
    }
}
