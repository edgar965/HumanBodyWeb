/**
 * 3D-Objekte in die Szene laden: OBJ/GLB/FBX samt MTL und Texturen.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { _autoDiscoverMtl } from './mtl_laden.js';

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
                const resp = await fetch('/api/studio/scene-object-upload/', { method: 'POST', body: fd });
                const data = await resp.json();
                if (data.ok) uploaded[file.name.toLowerCase()] = { url: data.url, name: file.name, ext: data.ext };
                else console.warn('[scene_extras] Upload fehlgeschlagen:', file.name, data.error);
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



export async function _loadSceneObjectIntoTrack(track, url, displayName, ext, startFrame, mtlUrl = null) {
    pushUndo('3D-Objekt Clip hinzufügen');
    let object3d = null;
    let customMaterials = null;
    try {
        if (ext === 'obj') {
            // Wenn kein MTL explizit übergeben wurde: versuche Auto-Discover aus 'mtllib'-Zeile
            // im OBJ. Damit funktioniert auch Single-File-Selection (nur OBJ), sofern MTL und
            // Texturen zuvor/gleichzeitig in denselben Bundle-Ordner hochgeladen wurden.
            if (!mtlUrl) {
                mtlUrl = await _autoDiscoverMtl(url);
            }
            const loader = new OBJLoader();
            // Three.js MTLLoader (bewährt) — setzt Materialien inkl. Texturen am OBJLoader.
            if (mtlUrl) {
                try {
                    const mtlLoader = new MTLLoader();
                    const basePath = mtlUrl.substring(0, mtlUrl.lastIndexOf('/') + 1);
                    mtlLoader.setResourcePath(basePath);
                    const mtlFileName = mtlUrl.substring(mtlUrl.lastIndexOf('/') + 1);
                    mtlLoader.setPath(basePath);
                    const materials = await mtlLoader.loadAsync(mtlFileName);
                    materials.preload();
                    loader.setMaterials(materials);
                    const matNames = Object.keys(materials.materials || {});
                    console.log(`[scene_extras] MTL via Three.js MTLLoader: ${matNames.length} Materialien (${matNames.join(', ')})`);
                } catch (mtlErr) {
                    console.warn('[scene_extras] MTLLoader fehlgeschlagen, OBJ ohne MTL:', mtlErr);
                }
            }
            object3d = await loader.loadAsync(url);
            // Vertex-Normals berechnen falls OBJ keine hatte — sonst ist Material schwarz.
            object3d.traverse(o => {
                if (o.isMesh && o.geometry && !o.geometry.attributes.normal) {
                    o.geometry.computeVertexNormals();
                }
                if (o.isMesh && o.material) {
                    const mats = Array.isArray(o.material) ? o.material : [o.material];
                    mats.forEach(m => {
                        if (!m) return;
                        // DoubleSide für alle Materialien (viele OBJs haben inkonsistente Normals).
                        m.side = THREE.DoubleSide;
                        // 3ds Max MTL-Export-Bug: Ke (emissive) oft auf 1,1,1 gesetzt — das überstrahlt
                        // komplett die Textur und lässt das Mesh einheitlich weiß aussehen. Bei vorhandener
                        // Textur (map_Kd) ist Emissive praktisch immer ein Fehler → auf 0 forcieren.
                        if (m.map && m.emissive && (m.emissive.r > 0 || m.emissive.g > 0 || m.emissive.b > 0)) {
                            m.emissive.setRGB(0, 0, 0);
                            m.needsUpdate = true;
                        }
                    });
                }
            });
        } else if (ext === 'glb' || ext === 'gltf') {
            const gltf = await new GLTFLoader().loadAsync(url);
            object3d = gltf.scene;
        } else {
            throw new Error(`Format "${ext}" wird noch nicht unterstützt`);
        }
    } catch (e) {
        console.warn('[scene_extras] 3D-Objekt Load fehlgeschlagen:', url, e);
        throw e;  // Caller entscheidet über alert (Session-Restore schluckt, User-Upload zeigt)
    }

    // Fallback-Material nur wenn gar keins vorhanden
    if (ext === 'obj' && !mtlUrl) {
        object3d.traverse(obj => {
            if (obj.isMesh && (!obj.material || !obj.material.color)) {
                obj.material = new THREE.MeshStandardMaterial({ color: 0x888899, roughness: 0.7 });
            }
        });
    }

    // Auto-center + scale auf 1m
    const box = new THREE.Box3().setFromObject(object3d);
    const size = new THREE.Vector3(); const center = new THREE.Vector3();
    box.getSize(size); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    if (maxDim > 0) {
        const scale = 1 / maxDim;
        object3d.scale.setScalar(scale);
        object3d.position.set(-center.x * scale, -box.min.y * scale, -center.z * scale);
    }

    // Falls Track schon ein Mesh hat (mehrere Clips → selbes Mesh wiederverwenden):
    // altes entsorgen, neues einsetzen. Einfachheit halber: erst mal immer neues Mesh.
    if (track.mesh) {
        state.scene.remove(track.mesh);
        track.mesh.traverse?.(obj => {
            if (obj.geometry) obj.geometry.dispose?.();
            if (obj.material) {
                if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose?.());
                else obj.material.dispose?.();
            }
        });
    }
    track.mesh = object3d;
    track.objectUrl = url;
    track.objectExt = ext;
    track.objectMtlUrl = mtlUrl || null;  // für Restore
    if (track.objectTint) setObjectTint(track, track.objectTint);
    state.scene.add(object3d);
    object3d.visible = true;  // applyPlayhead korrigiert ggf. (hasClips && !muted)

    // Clip auf der Timeline anlegen: 10s default
    const fps = state.project.fps;
    const durationFrames = 10 * fps;
    const clip = new Clip(null, displayName.replace(/\.(obj|glb|gltf|fbx)$/i, ''), durationFrames, fps);
    clip.type = 'object_clip';
    clip.startFrame = Math.max(0, startFrame || 0);
    clip.data = { url, ext, fileName: displayName, mtlUrl: mtlUrl || null };
    track.clips.push(clip);

    // Sichtbarkeit jetzt sofort anhand Playhead auswerten
    fn.applyPlayhead?.();
    fn.serverLog?.('scene_object_loaded', `track=${track.name} clip=${displayName} @${clip.startFrame}f`);
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

fn.setupSceneObjectImport = setupSceneObjectImport;
fn.setObjectTint = setObjectTint;
fn.addSceneObjectClip = addSceneObjectClip;
