/**
 * Voreinstellungen im Voraus laden, damit der Modellwechsel nicht stockt.
 *
 * Aus playback.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import * as THREE from 'three';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Modellzustaendigkeit } from './modellzustaendigkeit.js';


/**
 * Warteschlange fürs Vorladen — höchstens EIN Preset gleichzeitig im Bau.
 *
 * WARUM (Edgar, 24.09.2026, „fixe teuere Sprünge"): `_schedulePreloads` stößt
 * bei jedem `applyPlayhead()` ALLE Modell-Presets des Projekts an — jedes davon
 * fächert selbst in viele Garderobe-Netz-Anfragen auf. Bei drei Figuren liefen
 * so an die zwanzig `/netz/`-Anfragen gleichzeitig los, blockierten sich
 * gegenseitig (Browser-Verbindungslimit, Server-Last) und liefen bis zu 39 s
 * (`client.log`, 24.09.2026: `.../Damira1/netz/ ok 28428ms`,
 * `.../kin_hair/netz/ ok 39492ms`) — ein Sprung in einen noch nicht geladenen
 * Bereich landete mitten in diesem Stau. Jetzt läuft ein Preset nach dem
 * anderen; das GERADE benötigte Preset (`Modellspur._laden`, direkter Aufruf
 * ohne diese Schlange) muss sich dann höchstens gegen EIN Hintergrund-Preset
 * durchsetzen, nicht gegen alle.
 */
const _vorladeSchlange = [];
let _vorladeLaeuft = false;

function _einreihen(aufgabe) {
    return new Promise((resolve, reject) => {
        _vorladeSchlange.push({ aufgabe, resolve, reject });
        _vorladeWeiter();
    });
}

async function _vorladeWeiter() {
    if (_vorladeLaeuft) return;
    const naechste = _vorladeSchlange.shift();
    if (!naechste) return;
    _vorladeLaeuft = true;
    try {
        naechste.resolve(await naechste.aufgabe());
    } catch (e) {
        naechste.reject(e);
    } finally {
        _vorladeLaeuft = false;
        _vorladeWeiter();
    }
}

// Preload-Cache: lädt Preset-Assets im Hintergrund via Shadow-Track.
// Resolved zu {group, mesh, skeleton, mixer}. Beim Switch wird die vorbereitete
// Gruppe atomic in den echten Track übernommen.
export async function _preloadPreset(animTrack, preset) {
    if (!animTrack._preloadCache) animTrack._preloadCache = {};
    if (animTrack._preloadCache[preset]) return animTrack._preloadCache[preset];
    const teile = Modellzustaendigkeit.zerlegen(preset);
    const shadow = {
        name: `${animTrack.name}_preload_${preset}`,
        type: animTrack.type,
        preset: teile.preset,
        quelle: teile.quelle,
        bodyType: animTrack.bodyType,
        group: new THREE.Group(),
    };
    shadow.group.visible = false;
    state.scene.add(shadow.group);
    // Das Registrieren (Cache-Eintrag) bleibt sofort/synchron, damit
    // `_schedulePreloads` denselben Preset nicht beim nächsten Bild erneut
    // anstösst — nur der teure Teil (`loadTrackCharacter`) wartet in der Schlange.
    const promise = _einreihen(() => fn.loadTrackCharacter(shadow)).then(() => ({
        group: shadow.group, mesh: shadow.mesh, skeleton: shadow.skeleton, mixer: shadow.mixer,
        modell: shadow.modell, figurHoehe: shadow.figurHoehe,
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
    // Die vorgeladene Gruppe entsteht frisch im Ursprung (0,0,0) — ohne das
    // hier zurückzusetzen, springt die Figur bei jedem Preset-Wechsel auf
    // Position 0 (Edgar, 23.09.2026: „Kin1 hat bei Frame 1045 die Position
    // 5 m, sie wird jedoch bei 0 angezeigt"). `animTrack.position` bleibt die
    // ganze Zeit unverändert, nur die THREE-Gruppe wird ausgetauscht.
    const p = animTrack.position || [0, 0, 0];
    animTrack.group.position.set(p[0] || 0, p[1] || 0, p[2] || 0);
    animTrack.group.visible = true;
    animTrack.mesh = assets.mesh;
    animTrack.modell = assets.modell;
    animTrack.figurHoehe = assets.figurHoehe;
    Object.assign(animTrack, Modellzustaendigkeit.zerlegen(activePreset));
    animTrack.skeleton = assets.skeleton;
    animTrack.mixer = assets.mixer;
    animTrack._activeClip = null;
    animTrack._activeAction = null;
    animTrack.meshActive = activePreset;
    animTrack._loadingPreset = null;
    if (animTrack._preloadCache) delete animTrack._preloadCache[activePreset];
    fn.serverLog('preset_swap_preloaded', `track=${animTrack.name} preset=${activePreset}`);
}

/**
 * Prüft Model-Tracks: startet Preload für jedes Preset, das noch nicht geladen
 * ist oder gerade lädt. Bis 23.09.2026 nur für Presets, deren Clip innerhalb
 * eines Zeit-Vorlaufs lag (`state.project.preloadSeconds`) — bei einer echten
 * Ladezeit von bis zu einer Minute (Netz + Retarget) reichten die Sekunden
 * Vorlauf oft nicht: Der Abspielkopf erreichte den Clip, bevor das Modell
 * fertig war, und die Figur "animierte gerade nicht" (Edgar, 23.09.2026).
 * Jetzt (Einstellungen → Studio → „Alle Modelle vorladen"): ALLE Modell-Clips
 * des Projekts werden angestoßen, unabhängig von ihrer Position — die
 * Wächter unten (`meshActive`/`_loadingPreset`/`_preloadCache`) sorgen dafür,
 * dass ein bereits geladenes oder ladendes Preset nicht doppelt angefasst
 * wird. Bewegungen (Retarget) laufen unverändert immer eager beim Laden des
 * Projekts (`projekt_wiederherstellung.js`, `_klipAnlegen`).
 */
export function _schedulePreloads(t) {
    if (state.project.preloadAll === false) return;
    for (const track of state.project.tracks) {
        if (track.type !== 'model') continue;
        const animTrack = state.project.getLinkedAnimation(track);
        if (!animTrack) continue;
        for (const clip of track.clips) {
            if (clip.type !== 'model' || !clip.data?.preset) continue;
            const preset = Modellzustaendigkeit.schluessel(clip.data);
            if (animTrack.meshActive === preset) continue;
            if (animTrack._loadingPreset === preset) continue;
            if (animTrack._preloadCache?.[preset]) continue;
            _preloadPreset(animTrack, preset).catch((e) => { Protokoll.debug('vorladen',
                `Vorladen von ${preset} fehlgeschlagen`, e); });
        }
    }
}
