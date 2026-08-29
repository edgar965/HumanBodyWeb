/**
 * 3D-Objekte in die Szene laden: OBJ/GLB/FBX samt MTL und Texturen.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { _autoDiscoverMtl } from './mtl_laden.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Objektlader } from './objektlader.js';

const _textureLoader = new THREE.TextureLoader();

export function setupSceneObjectImport() {
    const addBtn = document.getElementById('dd-add-3d-object');
    if (!addBtn) return;
    addBtn.addEventListener('click', () => {
        document.getElementById('track-dropdown')?.classList.remove('open');
        // Legt leere 3D-Objekt-Spur an; Datei wird via Context-Menu → Hinzufügen geladen
        const track = fn.addSpecialTrack('scene_object', '3D-Objekt');
        if (track) {
            track.subtype = 'custom';
            track.color = '#7c5cbf';
        }
        fn.updateTrackHeaders?.();
        fn.renderTimeline?.();
    });
}

// Aufgerufen vom Context-Menu: lädt eine oder mehrere 3D-Dateien (OBJ+MTL+Texturen)
// in den Track an Click-Position. User kann mehrere Dateien auswählen.
export async function addSceneObjectClip(trackIdx, startFrame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'scene_object') return;
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;  // OBJ + MTL + Texturen
    input.accept = '.obj,.mtl,.glb,.gltf,.fbx,.jpg,.jpeg,.png,.webp';
    input.addEventListener('change', async () => {
        const files = Array.from(input.files || []);
        if (files.length === 0) return;
        try {
            // Alle Dateien in denselben Bundle-Ordner → MTL→Textur-Referenzen funktionieren
            const bundleId = 'obj_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
            const uploaded = {};  // { filename: { url, ext } }
            await Promise.all(files.map(async (file) => {
                const fd = new FormData();
                fd.append('object', file);
                fd.append('bundleId', bundleId);
                const data = await Serverabruf.formular(
                    '/api/studio/scene-object-upload/', fd);
                if (data.ok) uploaded[file.name.toLowerCase()] = { url: data.url, name: file.name, ext: data.ext };
                else Protokoll.warnung('scene_extras', 'Upload fehlgeschlagen:', file.name, data.error);
            }));
            // Haupt-Datei: erste OBJ/GLB/GLTF/FBX
            const mainKey = Object.keys(uploaded).find(k => /\.(obj|glb|gltf|fbx)$/i.test(k));
            if (!mainKey) { alert('Keine OBJ/GLB/GLTF/FBX Datei gefunden.'); return; }
            const main = uploaded[mainKey];
            // MTL-Datei finden (falls OBJ)
            let mtlUrl = null;
            if (main.ext === 'obj') {
                const mtlKey = Object.keys(uploaded).find(k => /\.mtl$/i.test(k));
                if (mtlKey) mtlUrl = uploaded[mtlKey].url;
            }
            await _loadSceneObjectIntoTrack(track, main.url, main.name, main.ext, startFrame, mtlUrl);
            fn.updateTrackHeaders?.();
            fn.renderTimeline?.();
            fn.updateProperties?.();
        } catch (e) {
            console.error('[scene_extras] 3D-Import fehlgeschlagen:', e);
            alert('3D-Objekt Import fehlgeschlagen: ' + e.message);
        }
    });
    input.click();
}

/**
 * Ein 3D-Objekt laden und als Clip in eine Spur setzen.
 *
 * Umbau 17.08.2026: Diese Funktion hatte 116 Zeilen. Das Laden, die
 * Materialreparatur und das Normieren stehen jetzt in `Objektlader`
 * (objektlader.js); hier bleibt, was mit der Spur und der Zeitleiste zu tun
 * hat — und genau das steht jetzt auch auf einer Bildschirmseite.
 */
export async function _loadSceneObjectIntoTrack(track, url, displayName, ext,
                                                startFrame, mtlUrl = null) {
    pushUndo('3D-Objekt Clip hinzufügen');
    let objekt;
    try {
        // Ohne ausdrueckliche MTL-Angabe: die `mtllib`-Zeile im OBJ lesen. So
        // funktioniert auch die Auswahl einer einzelnen Datei, sofern MTL und
        // Texturen im selben Buendelordner liegen.
        if (ext === 'obj' && !mtlUrl) mtlUrl = await _autoDiscoverMtl(url);
        objekt = await new Objektlader(url, ext, mtlUrl).laden();
    } catch (fehler) {
        Protokoll.warnung('3D-Objekt', 'nicht ladbar:', url, fehler);
        // Der Aufrufer entscheidet ueber die Meldung: Beim Wiederherstellen
        // einer Sitzung wird geschluckt, beim Hochladen nicht.
        throw fehler;
    }

    if (track.mesh) {
        state.scene.remove(track.mesh);
        Objektlader.entsorgen(track.mesh);
    }
    track.mesh = objekt;
    track.objectUrl = url;
    track.objectExt = ext;
    track.objectMtlUrl = mtlUrl || null;        // fuer das Wiederherstellen
    if (track.objectTint) setObjectTint(track, track.objectTint);
    state.scene.add(objekt);
    objekt.visible = true;      // applyPlayhead korrigiert das gleich

    const clip = _objektclip(displayName, startFrame, url, ext, mtlUrl);
    track.clips.push(clip);
    fn.applyPlayhead?.();
    fn.serverLog?.('scene_object_loaded',
                   `track=${track.name} clip=${displayName} @${clip.startFrame}f`);
}

/** Vorgabelaenge eines Objekt-Clips in Sekunden. */
const OBJEKT_SEKUNDEN = 10;

function _objektclip(displayName, startFrame, url, ext, mtlUrl) {
    const fps = state.project.fps;
    const clip = new Clip(null, displayName.replace(/\.(obj|glb|gltf|fbx)$/i, ''),
                          OBJEKT_SEKUNDEN * fps, fps);
    clip.type = 'object_clip';
    clip.startFrame = Math.max(0, startFrame || 0);
    clip.data = { url, ext, fileName: displayName, mtlUrl: mtlUrl || null };
    return clip;
}

export function setObjectTint(track, colorHex) {
    if (!track?.mesh) return;
    track.objectTint = colorHex;
    track.mesh.traverse(obj => {
        if (obj.isMesh && obj.material) {
            if (Array.isArray(obj.material)) obj.material.forEach(m => m.color && m.color.set(colorHex));
            else if (obj.material.color) obj.material.color.set(colorHex);
        }
    });
}

fn.setObjectTint = setObjectTint;
fn.addSceneObjectClip = addSceneObjectClip;
