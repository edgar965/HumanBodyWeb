/**
 * Projektdaten — den Studiozustand in die Struktur der .studio.json uebersetzen.
 *
 * Aus project.js herausgeloest (Umbau 16.08.2026).
 *
 * WARUM hier Dictionaries bleiben (Anforderung 11 des Umbaus): Diese Woerterbuecher
 * verlassen das Programm sofort — sie gehen als JSON in die Projektdatei bzw. in
 * sessionStorage und werden nur von Projektwiederherstellung wieder eingelesen.
 * Eine Klasse dazwischen waere eine zweite Beschreibung desselben Dateiformats,
 * die bei jeder Feldaenderung mitgepflegt werden muesste. Zu Klassen gehoeren die
 * Daten, die durch mehrere Funktionen gereicht und per ["schluessel"] gelesen
 * werden — das ist hier gerade nicht der Fall.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

export class Projektdaten {
    /** Vollstaendiger Projektstand als speicherbare Struktur. */
    static sammeln() {
        return {
            name: state.project.name,
            fps: state.project.fps,
            // Szenen-Lichter + Boden werden SEPARAT (nicht in tracks[]) gespeichert,
            // damit User-Tracks keine Index-Drift erleiden (_linkedAnimIdx bleibt stabil).
            sceneLights: Projektdaten._lichter(),
            sceneFloor: Projektdaten._boden(),
            tracks: state.project.tracks
                .filter(t => !t._sceneLight && !t._sceneItem)
                .map(Projektdaten._spur),
        };
    }

    /**
     * Licht-Eigenschaften der Szenenlichter (Key/Fill/Back/Ambient + Theatre)
     * als {name: {eigenschaften, clips}} fuer den Speicher-Rundlauf.
     */
    static _lichter() {
        const out = {};
        for (const t of state.project.tracks) {
            if (t.type !== 'light' || !t._sceneLight || !t.light) continue;
            out[t.name] = {
                color: '#' + t.light.color.getHexString(),
                intensity: t.light.intensity,
                position: { x: t.light.position.x, y: t.light.position.y, z: t.light.position.z },
                target: t.light.target
                    ? { x: t.light.target.position.x, y: t.light.target.position.y, z: t.light.target.position.z }
                    : null,
                angle: t.light.angle ?? null,
                penumbra: t.light.penumbra ?? null,
                distance: t.light.distance ?? null,
                visible: t.lightVisible,
                coneVisible: t.coneVisible !== false,
                muted: t.muted,
                clips: t.clips.filter(c => c.type === 'light_kf').map(c => ({
                    type: 'light_kf', name: c.name,
                    startFrame: c.startFrame, data: c.data,
                })),
            };
        }
        return out;
    }

    static _boden() {
        for (const t of state.project.tracks) {
            if (t.type !== 'scene_object' || t.subtype !== 'floor') continue;
            const w = t.floorWidth ?? t.floorSize ?? 6;
            const l = t.floorLength ?? t.floorSize ?? 6;
            return {
                color: t.floorColor || '#3a3a4a',
                texture: t.floorTexture || 'none',
                roughness: t.floorRoughness ?? 0.9,
                metalness: t.floorMetalness ?? 0.05,
                width: w,
                length: l,
                centerX: t.mesh?.position?.x ?? 0,
                centerZ: t.mesh?.position?.z ?? 0,
                size: Math.max(w, l),  // Legacy-Feld fuer Abwaertskompatibilitaet
                muted: t.muted,
                gridVisible: state.gridVisible !== false,
            };
        }
        return null;
    }

    static _spur(t) {
        const td = {
            name: t.name, type: t.type, preset: t.preset, bodyType: t.bodyType,
            color: t.color, muted: t.muted, position: t.position,
        };
        if (t.type === 'model') {
            td._linkedAnimIdx = t._linkedAnimIdx;
            td._currentPreset = t._currentPreset;
        }
        if (t.type === 'camera') td.cameraActive = t.cameraActive;
        if (t.type === 'light' && t.light) Projektdaten._licht(td, t);
        if (t.type === 'scene_object' && t.subtype === 'custom' && t.mesh) {
            td.objectTint = t.objectTint || '#ffffff';
            td.objectPosition = { x: t.mesh.position.x, y: t.mesh.position.y, z: t.mesh.position.z };
            td.objectRotation = { x: t.mesh.rotation.x, y: t.mesh.rotation.y, z: t.mesh.rotation.z };
            td.objectScale = t.mesh.scale.x;  // einheitlicher Faktor
        }
        td.clips = t.clips.map(Projektdaten._klip);
        return td;
    }

    static _licht(td, t) {
        td.lightColor = '#' + t.light.color.getHexString();
        td.lightIntensity = t.light.intensity;
        td.lightPosition = { x: t.light.position.x, y: t.light.position.y, z: t.light.position.z };
        if (t.light.target) {
            td.lightTarget = { x: t.light.target.position.x, y: t.light.target.position.y,
                z: t.light.target.position.z };
        }
        if (t.light.angle != null) td.lightAngle = t.light.angle;
        if (t.light.penumbra != null) td.lightPenumbra = t.light.penumbra;
        if (t.light.distance != null) td.lightDistance = t.light.distance;
        td.lightVisible = t.lightVisible;
        td.coneVisible = t.coneVisible !== false;  // Vorgabe: an
        td.lightType = t.lightType;
        td._sceneLight = !!t._sceneLight;
    }

    static _klip(c) {
        const cd = {
            type: c.type, category: c.category, name: c.name,
            totalFrames: c.totalFrames, fps: c.fps, startFrame: c.startFrame,
            trimIn: c.trimIn, trimOut: c.trimOut, speed: c.speed,
            smoothSigma: c.smoothSigma, groundFix: c.groundFix,
            blendIn: c.blendIn, blendOut: c.blendOut,
        };
        if (c.type === 'camera_kf' || c.type === 'light_kf') {
            cd.data = c.data;
        } else if (c.type === 'model') {
            cd.data = { preset: c.data.preset, bodyType: c.data.bodyType };
        } else if (c.type === 'audio') {
            cd.data = {
                fileName: c.data.fileName, audioUrl: c.data.audioUrl,
                audioDuration: c.data.audioDuration, volume: c.data.volume,
                fadeIn: c.data.fadeIn, fadeOut: c.data.fadeOut, offset: c.data.offset,
            };
        } else if (c.type === 'object_clip') {
            cd.data = {
                url: c.data?.url, ext: c.data?.ext,
                fileName: c.data?.fileName, mtlUrl: c.data?.mtlUrl || null,
            };
        }
        return cd;
    }
}

fn.buildProjectData = Projektdaten.sammeln;
