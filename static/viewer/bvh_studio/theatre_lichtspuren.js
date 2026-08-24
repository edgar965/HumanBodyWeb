/**
 * Lichtspuren aus einer Theatre-Vorgabe erzeugen.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { state, TRACK_COLORS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track } from './models.js';
import { createLightHelper, addStandardLightKeyframes } from './spur_lichter.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';


// Additive-Variante: lässt existierende Lichter unverändert und legt NUR die
// Preset-Lichter an, deren Name noch nicht als Track existiert. Aufgerufen über
// Kontextmenü "Hinzufügen > Presets" auf einem Licht-Track.
// atFrame: Frame, ab dem die neuen Lichter aktiv werden. Existierende Licht-Tracks
// erhalten an diesem Frame einen Pair-KF (upper = aktueller State mit visible=true,
// lower = visible=false) — d.h. ALTE Lichter werden ab atFrame ausgeschaltet,
// NEUE Lichter starten ab atFrame.
export async function _applyTheatrePresetAdditive(presetName, atFrame) {
    const resp = await fetch(`/api/studio/theatre-preset/${encodeURIComponent(presetName)}/`);
    if (!resp.ok) { alert(`Preset "${presetName}" nicht gefunden`); return; }
    const preset = await resp.json();
    const presetLights = preset.lights || [];
    const fps = state.project.fps;
    const frame = (atFrame != null) ? Math.max(0, Math.round(atFrame)) : state.playheadFrame;
    const endFrame = Math.max(Math.round((state.project.duration || 10) * fps), frame + 1);
    pushUndo(`Preset hinzufügen: ${preset.label || presetName}`);

    // 1) Bestehende Licht-Tracks: Pair-KF bei frame einfügen. upper = current visible=true,
    //    lower = visible=false → Licht ist davor an, danach aus.
    const existingLights = state.project.tracks.filter(t => t.type === 'light');
    const existingLightNames = new Set(existingLights.map(t => t.name));
    for (const t of existingLights) {
        if (!t.light) continue;
        const tgt = t.light.target?.position || { x: 0, y: 0, z: 0 };
        const baseData = () => ({
            position: { x: t.light.position.x, y: t.light.position.y, z: t.light.position.z },
            target:   { x: tgt.x, y: tgt.y, z: tgt.z },
            color: '#' + t.light.color.getHexString(),
            intensity: t.light.intensity,
            angle: t.light.angle ?? (Math.PI / 6),
            penumbra: t.light.penumbra ?? 0.3,
            distance: t.light.distance ?? 50,
        });
        // Nummerierte Namen: nächste freie Nummer je Track, upper/lower als Suffix
        const nextN = t.clips.length + 1;
        const upperKF = new Clip(null, `${nextN}a`, 0, fps);
        upperKF.type = 'light_kf';
        upperKF.startFrame = frame;
        upperKF.data = { ...baseData(), fade: false, visible: true, trackPosition: 'upper' };
        const lowerKF = new Clip(null, `${nextN}b`, 0, fps);
        lowerKF.type = 'light_kf';
        lowerKF.startFrame = frame;
        lowerKF.data = { ...baseData(), fade: true, visible: false, trackPosition: 'lower' };
        t.clips.push(upperKF, lowerKF);
        t.clips.sort((a, b) => {
            if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
            return (a.data?.trackPosition === 'upper' ? 0 : 1) - (b.data?.trackPosition === 'upper' ? 0 : 1);
        });
    }

    // 2) Neue Preset-Lichter anlegen. Start-KF bei frame, Ende-KF bei Projekt-Ende.
    let added = 0, skipped = 0;
    for (const def of presetLights) {
        const targetName = `${def.name || 'Licht'} (${preset.label || presetName})`;
        if (existingLightNames.has(targetName) || existingLightNames.has(def.name)) {
            skipped++;
            continue;
        }
        const track = _createLightTrackFromDef(def, preset.label || presetName);
        if (!track) continue;
        // Standard-KFs durch _createLightTrackFromDef (0..endFrame) ersetzen durch
        // Range (frame..endFrame) — Licht startet erst ab Preset-Apply-Zeitpunkt.
        track.clips = [];
        const tgt = track.light.target?.position || { x: 0, y: 0, z: 0 };
        const kfData = () => ({
            position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
            target:   { x: tgt.x, y: tgt.y, z: tgt.z },
            color: '#' + track.light.color.getHexString(),
            intensity: track.light.intensity,
            angle: track.light.angle ?? (Math.PI / 6),
            penumbra: track.light.penumbra ?? 0.3,
            distance: track.light.distance ?? 50,
            fade: true,
            visible: true,
        });
        const startKF = new Clip(null, '1', 0, fps);
        startKF.type = 'light_kf';
        startKF.startFrame = frame;
        startKF.data = kfData();
        const endKF = new Clip(null, '2', 0, fps);
        endKF.type = 'light_kf';
        endKF.startFrame = endFrame;
        endKF.data = kfData();
        track.clips.push(startKF, endKF);
        added++;
    }

    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
    fn.updateProperties?.();
    fn.applyPlayhead?.();
    fn.serverLog?.('theatre_preset_added',
        `${presetName} @f${frame}: +${added} Lichter, ${existingLights.length}× Alt-Licht ausgeschaltet (${skipped} übersprungen)`);
}

export function _createLightTrackFromDef(def, presetLabel) {
    // Erzeugt einen Licht-Track entsprechend einer Preset-Definition
    const name = def.name || 'Licht';
    const type = def.type || 'spot';
    let light;
    if (type === 'spot') {
        light = new THREE.SpotLight(
            new THREE.Color(def.color || '#ffffff'),
            def.intensity ?? 5,
            def.distance ?? 50,
            (def.angle ?? 30) * Math.PI / 180,
            def.penumbra ?? 0.3,
            1
        );
    } else if (type === 'directional') {
        light = new THREE.DirectionalLight(new THREE.Color(def.color || '#ffffff'), def.intensity ?? 3);
    } else if (type === 'point') {
        light = new THREE.PointLight(new THREE.Color(def.color || '#ffffff'), def.intensity ?? 3, def.distance ?? 30);
    } else if (type === 'ambient') {
        light = new THREE.AmbientLight(new THREE.Color(def.color || '#ffffff'), def.intensity ?? 0.8);
    } else {
        return;
    }
    if (def.position && Array.isArray(def.position)) {
        light.position.set(def.position[0], def.position[1], def.position[2]);
    }
    if (light.target && def.target && Array.isArray(def.target)) {
        light.target.position.set(def.target[0], def.target[1], def.target[2]);
        state.scene.add(light.target);
    }
    state.scene.add(light);

    const track = new Track(`${name} (${presetLabel})`);
    track.type = 'light';
    track.color = TRACK_COLORS.light || track.color;
    track.light = light;
    track.lightType = type;
    track.lightVisible = false;  // Helferlinien: default AUS
    track.coneVisible = true;    // Lichtkegel (Formkörper): default an
    track._theatrePreset = presetLabel;
    track.lightHelper = createLightHelper(light);
    if (track.lightHelper) state.scene.add(track.lightHelper);
    state.project.addTrack(track);
    // Theatre-Preset-Lichter bekommen Standard Start/Ende-Keyframes über die volle
    // Projektdauer — damit die Timeline sichtbar ist und das Licht dauerhaft aktiv bleibt.
    addStandardLightKeyframes(track);
    return track;
}

fn.applyTheatrePresetAdditive = _applyTheatrePresetAdditive;
