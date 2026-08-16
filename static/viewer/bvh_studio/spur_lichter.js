/**
 * Lichtspuren: Anzeiger, Helfer, Schluesselbilder, Szenenlichter.
 *
 * Aus tracks.js herausgeloest (Umbau 15.08.2026): rund 300 der 1115 Zeilen
 * drehten sich um Licht — vom Kegelanzeiger bis zum Uebernehmen gespeicherter
 * Lichtwerte. Wer eine Clipfunktion sucht, muss das nicht durchblaettern.
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track, Clip } from './models.js';
import { pushUndo } from './undo.js';
import { TRACK_COLORS } from './state.js';


// Erzeugt Helper-Group für beliebigen Licht-Typ. Enthält:
//   - .spotHelper: Three.js-Wireframe-Helfer (Toggle "Helfer-Linien")
//   - .originCone: solide Form, die den Licht-Typ visuell symbolisiert (Toggle "Lichtkegel")
//
// Formen pro Typ (immer: Spitze/Ursprung am Licht, Form zeigt IN die Szene):
//   - Spot:        Kegel, Radius aus light.angle (breiter Angle = breiter Kegel)
//   - Directional: Zylinder (parallele Strahlen)
//   - Point:       Kugel (omnidirektional)
//   - Ambient:     flaches Rechteck (ungerichtet)
export const _LIGHT_SHAPE_HEIGHT = 0.6;

export function _buildLightIndicator(light) {
    const color = light.color.clone();
    const mat = new THREE.MeshBasicMaterial({
        color, transparent: true, opacity: 0.45, side: THREE.DoubleSide, depthWrite: false,
    });
    const h = _LIGHT_SHAPE_HEIGHT;
    let geo;
    if (light.isSpotLight) {
        const angle = light.angle ?? Math.PI / 6;
        const radius = Math.min(Math.max(h * Math.tan(angle), 0.05), 1.0);
        geo = new THREE.ConeGeometry(radius, h, 24, 1, true);  // offene Unterseite
        geo.translate(0, -h / 2, 0);  // Spitze → Ursprung, Basis bei (0,-h,0)
    } else if (light.isDirectionalLight) {
        const r = 0.08;
        geo = new THREE.CylinderGeometry(r, r, h, 16, 1, true);
        geo.translate(0, -h / 2, 0);
    } else if (light.isPointLight) {
        geo = new THREE.SphereGeometry(0.12, 20, 14);
    } else if (light.isAmbientLight) {
        geo = new THREE.PlaneGeometry(0.5, 0.3);
        geo.rotateX(-Math.PI / 2);  // horizontal
    } else {
        return null;
    }
    const mesh = new THREE.Mesh(geo, mat);
    mesh._lightShapeKind = light.isSpotLight ? 'spot'
        : light.isDirectionalLight ? 'directional'
        : light.isPointLight ? 'point'
        : light.isAmbientLight ? 'ambient' : 'unknown';
    mesh._lastAngle = light.angle ?? null;
    return mesh;
}

export function createLightHelper(light) {
    if (!light) return null;
    const group = new THREE.Group();
    let typeHelper = null;
    if (light.isSpotLight) typeHelper = new THREE.SpotLightHelper(light, 0xffc107);
    else if (light.isDirectionalLight) typeHelper = new THREE.DirectionalLightHelper(light, 0.6, 0xffc107);
    else if (light.isPointLight) typeHelper = new THREE.PointLightHelper(light, 0.12, 0xffc107);
    // Ambient: kein Wireframe-Helfer vorhanden (→ null)
    if (typeHelper) {
        typeHelper.visible = false;  // Default: Helfer-Linien aus
        group.add(typeHelper);
    }

    const indicator = _buildLightIndicator(light);
    if (indicator) {
        indicator.visible = true;  // Default: an
        group.add(indicator);
    }

    group.spotHelper = typeHelper;
    group.originCone = indicator;  // Name bleibt für Abwärtskompatibilität

    group.update = function() {
        typeHelper?.update?.();
        if (!indicator) return;
        indicator.position.copy(light.position);
        // Ausrichtung: lokale -Y-Achse zeigt in Richtung Target (für Spot/Directional).
        // Point ist omnidirektional, Ambient ungerichtet → keine Rotation.
        if (light.target && (light.isSpotLight || light.isDirectionalLight)) {
            const dir = new THREE.Vector3().subVectors(light.target.position, light.position);
            if (dir.lengthSq() > 1e-6) {
                dir.normalize();
                indicator.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir);
            }
        } else if (light.isAmbientLight) {
            // Ambient: etwas erhöht platzieren damit vom Boden abhebt
            indicator.position.set(light.position.x, (light.position.y || 0) + 0.05, light.position.z);
            indicator.quaternion.identity();
        } else {
            indicator.quaternion.identity();
        }
        // Spot-Winkel geändert → Geometrie neu bauen
        if (light.isSpotLight && indicator._lastAngle !== light.angle) {
            indicator._lastAngle = light.angle;
            const h = _LIGHT_SHAPE_HEIGHT;
            const angle = light.angle ?? Math.PI / 6;
            const radius = Math.min(Math.max(h * Math.tan(angle), 0.05), 1.0);
            indicator.geometry.dispose();
            const geo = new THREE.ConeGeometry(radius, h, 24, 1, true);
            geo.translate(0, -h / 2, 0);
            indicator.geometry = geo;
        }
        indicator.material.color.copy(light.color);
    };
    group.update();
    return group;
}

// Bestimmt lightType-String aus einem THREE.Light-Objekt
export function detectLightType(light) {
    if (!light) return 'spot';
    if (light.isSpotLight) return 'spot';
    if (light.isDirectionalLight) return 'directional';
    if (light.isPointLight) return 'point';
    if (light.isAmbientLight) return 'ambient';
    return 'spot';
}

// Legt Standard-Keyframes an Frame 0 UND am Ende der Timeline an, die die
// aktuellen Licht-Properties einfrieren. Ohne Keyframe ist das Licht aus —
// die Start+End-Paare halten das Licht per Default im gewünschten Zustand.
export function addStandardLightKeyframes(track) {
    _addStandardKeyframe(track);
}

export function _addStandardKeyframe(track) {
    if (!track.light) return;
    const light = track.light;
    const tgt = light.target?.position || { x: 0, y: 0, z: 0 };
    const fps = state.project.fps;
    // Ende der Timeline: project.duration * fps, Fallback 10s wenn leer
    const endFrame = Math.max(Math.round((state.project.duration || 10) * fps), 10);

    const makeKF = (name, startFrame) => {
        const kf = new Clip(null, name, 0, fps);
        kf.type = 'light_kf';
        kf.startFrame = startFrame;
        kf.data = {
            position: { x: light.position.x, y: light.position.y, z: light.position.z },
            target:   { x: tgt.x, y: tgt.y, z: tgt.z },
            color: '#' + light.color.getHexString(),
            intensity: light.intensity,
            angle: light.angle ?? null,
            penumbra: light.penumbra ?? null,
            distance: light.distance ?? null,
            fade: true,
            visible: !track.muted,
        };
        return kf;
    };
    // Nur durchnummerierte Namen — keine "Standard Start/Ende" mehr
    track.clips.push(makeKF('1', 0));
    if (endFrame > 0) track.clips.push(makeKF('2', endFrame));
}

// Wendet eine Szenen-Licht-Override-Map auf existierende _sceneLight-Tracks an
// (inkl. Clips). Nutzbar direkt nach createSceneLightTracks() oder bei mid-session
// Project-Load wo die Tracks bereits existieren.
export function applySceneLightOverrides(overrides) {
    if (!overrides) return;
    for (const track of state.project.tracks) {
        if (!track._sceneLight || !track.light) continue;
        const o = overrides[track.name];
        if (!o) continue;
        const light = track.light;
        if (o.color) light.color.set(o.color);
        if (o.intensity != null) light.intensity = o.intensity;
        if (o.position) light.position.set(o.position.x, o.position.y, o.position.z);
        if (o.target && light.target) {
            light.target.position.set(o.target.x, o.target.y, o.target.z);
            light.target.updateMatrixWorld();
        }
        if (o.angle != null && 'angle' in light) light.angle = o.angle;
        if (o.penumbra != null && 'penumbra' in light) light.penumbra = o.penumbra;
        if (o.distance != null && 'distance' in light) light.distance = o.distance;
        track.lightVisible = o.visible ?? false;  // Helfer-Linien: default aus
        track.muted = o.muted ?? false;
        light.visible = !track.muted;
        if (track.lightHelper) {
            track.lightHelper.visible = track.lightVisible && !track.muted;
            track.lightHelper.update?.();
        }
        // Clips nur ersetzen wenn Overrides welche haben, sonst Standard-KFs behalten
        // (Pre-0.40 Saves haben keine clips-Array → Standard Start+Ende bleibt intakt)
        if (Array.isArray(o.clips) && o.clips.length > 0) {
            track.clips = o.clips.map(cd => {
                const kf = new Clip(null, cd.name || 'Licht', 0, state.project.fps);
                kf.type = 'light_kf';
                kf.startFrame = cd.startFrame || 0;
                kf.data = cd.data || {};
                return kf;
            }).sort((a, b) => a.startFrame - b.startFrame);
        }
    }
}

// Erzeugt Light-Tracks für die von createSceneSetup() angelegten Szenen-Lichter.
// Wird NACH restoreProjectData() aufgerufen; wendet dann etwaige gestashte
// Szenen-Licht-Overrides aus dem Save an.
export function createSceneLightTracks() {
    const overrides = state.project._pendingSceneOverrides?.sceneLights;
    // Wenn ein Save geladen wurde (overrides ist definiert, auch wenn {}): nur
    // Lichter anlegen, die im Save vorkommen. Wenn overrides === undefined (neues
    // Projekt, kein Save): alle Default-Szenen-Lichter anlegen.
    const hasSavedState = overrides !== undefined && overrides !== null;
    const sceneLights = [
        { name: 'Key Light',  light: state.sceneKeyLight,  ref: 'sceneKeyLight' },
        { name: 'Fill Light', light: state.sceneFillLight, ref: 'sceneFillLight' },
        { name: 'Back Light', light: state.sceneBackLight, ref: 'sceneBackLight' },
        { name: 'Ambient',    light: state.sceneAmbient,   ref: 'sceneAmbient' },
    ];
    for (const { name, light, ref } of sceneLights) {
        if (!light) continue;
        // Saved project kennt dieses Licht nicht → User hat es gelöscht → aus Szene entfernen
        if (hasSavedState && !(name in overrides)) {
            if (light.target) state.scene.remove(light.target);
            state.scene.remove(light);
            light.dispose?.();
            state[ref] = null;
            continue;
        }
        if (light.isDirectionalLight && light.target && !light.target.parent) {
            state.scene.add(light.target);
        }
        const track = new Track(name);
        track.type = 'light';
        track.color = TRACK_COLORS.light || track.color;
        track.light = light;
        track.lightType = detectLightType(light);
        track.lightVisible = false;  // Helfer-Linien: default aus
        track.coneVisible = true;    // Lichtkegel: default an
        track._sceneLight = true;
        track.lightHelper = createLightHelper(light);
        if (track.lightHelper) {
            state.scene.add(track.lightHelper);
        }
        state.project.addTrack(track);
    }
    applySceneLightOverrides(overrides);
    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
}

// Pair-Variante: legt ZWEI Keyframes am gleichen Frame an — 'upper' (vor dem Cut)
// und 'lower' (nach dem Cut). Erlaubt harten Zustandswechsel an einer Stelle.
// Visuell werden sie in der Timeline oben/unten versetzt gerendert.
export function addLightKeyframePair(trackIdx, frame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'light' || !track.light) return;
    pushUndo('Lichteigenschaft-Pair');
    const targetFrame = (frame != null) ? frame : state.playheadFrame;
    const makeKF = (position, nameSuffix) => {
        const kf = new Clip(null, `Licht ${track.clips.length + 1} (${nameSuffix})`, 0, state.project.fps);
        kf.type = 'light_kf';
        kf.startFrame = targetFrame;
        const tgt = track.light.target?.position || { x: 0, y: 0, z: 0 };
        kf.data = {
            position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
            target:   { x: tgt.x, y: tgt.y, z: tgt.z },
            color: '#' + track.light.color.getHexString(),
            intensity: track.light.intensity,
            angle: track.light.angle ?? (Math.PI / 6),
            penumbra: track.light.penumbra ?? 0.3,
            distance: track.light.distance ?? 50,
            fade: position === 'upper' ? false : true,  // vor-KF = harter Cut per default
            visible: !track.muted,
            trackPosition: position,  // 'upper' | 'lower' für Render-Offset
        };
        return kf;
    };
    track.clips.push(makeKF('upper', 'vor'));
    track.clips.push(makeKF('lower', 'nach'));
    track.clips.sort((a, b) => {
        if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
        return (a.data?.trackPosition === 'upper' ? 0 : 1) - (b.data?.trackPosition === 'upper' ? 0 : 1);
    });
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    fn.serverLog?.('light_kf_pair_added', `track=${track.name} frame=${targetFrame}`);
}

// Light keyframe helpers
export function addLightKeyframe(trackIdx, frame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'light' || !track.light) return;
    pushUndo('Licht Keyframe');
    const targetFrame = (frame != null) ? frame : state.playheadFrame;
    const kf = new Clip(null, `Licht ${track.clips.length + 1}`, 0, state.project.fps);
    kf.type = 'light_kf';
    kf.startFrame = targetFrame;
    const tgt = track.light.target?.position || { x: 0, y: 0, z: 0 };
    kf.data = {
        position: { x: track.light.position.x, y: track.light.position.y, z: track.light.position.z },
        target:   { x: tgt.x, y: tgt.y, z: tgt.z },
        color: '#' + track.light.color.getHexString(),
        intensity: track.light.intensity,
        angle: track.light.angle ?? (Math.PI / 6),
        penumbra: track.light.penumbra ?? 0.3,
        distance: track.light.distance ?? 50,
        fade: true,  // Fade-Effekt: true = interpolieren zum nächsten KF, false = Sprung
        visible: !track.muted,  // Licht An/Aus-State an diesem Keyframe
    };
    track.clips.push(kf);
    track.clips.sort((a, b) => a.startFrame - b.startFrame);
    fn.updateDuration();
    fn.renderTimeline();
    fn.updateProperties();
    console.log(`[BVH Studio] Licht-Keyframe gespeichert bei Frame ${targetFrame}`);
}
