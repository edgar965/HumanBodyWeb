/**
 * BVH Studio — Szenen-Erweiterungen:
 *  - Theatre-Licht-Presets
 *  - Boden-Track (floor) mit Textur/Farb-Properties
 *  - 3D-Objekt-Import (OBJ/GLB/GLTF)
 *  - TransformControls für Positionierung selektierter Szenen-Objekte
 */
import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { state, TRACK_COLORS } from './state.js';
import { fn } from './registry.js';
import { Track, Clip } from './models.js';
import { pushUndo } from './undo.js';
import { createLightHelper, addStandardLightKeyframes } from './tracks.js';

let _cachedTheatrePresets = null;
let _cachedFloorTextures = null;
let _transformControls = null;
let _textureLoader = new THREE.TextureLoader();

// =========================================================================
// Boden-Track
// =========================================================================

export function createFloorTrack() {
    if (state.project.tracks.some(t => t._sceneItem === 'floor')) return;
    const override = state.project._pendingSceneOverrides?.sceneFloor;
    const size = override?.size ?? 6;
    const color = override?.color ?? '#3a3a4a';
    const roughness = override?.roughness ?? 0.9;
    const metalness = override?.metalness ?? 0.05;

    const geo = new THREE.PlaneGeometry(size, size, 1, 1);
    geo.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color), roughness, metalness, side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.y = -0.001;
    mesh.receiveShadow = true;
    mesh.userData.isFloor = true;
    state.scene.add(mesh);

    const track = new Track('Boden');
    track.type = 'scene_object';
    track.subtype = 'floor';
    track.color = '#795548';
    track._sceneItem = 'floor';
    track.mesh = mesh;
    track.floorSize = size;
    track.floorTexture = override?.texture || 'none';
    track.floorColor = color;
    track.floorRoughness = roughness;
    track.floorMetalness = metalness;
    track.muted = override?.muted || false;
    state.project.addTrack(track);
    return track;
}

export function updateFloorMaterial(track) {
    if (!track?.mesh || !track.mesh.material) return;
    const m = track.mesh.material;
    m.color.set(track.floorColor || '#3a3a4a');
    m.roughness = track.floorRoughness ?? 0.9;
    m.metalness = track.floorMetalness ?? 0.05;
    m.needsUpdate = true;
}

export async function applyFloorTexture(track, textureUrl) {
    if (!track?.mesh) return;
    const m = track.mesh.material;
    track.floorTexture = textureUrl ? textureUrl.split('/').pop().split('.')[0] : 'none';
    if (!textureUrl) {
        if (m.map) { m.map.dispose(); m.map = null; }
        m.needsUpdate = true;
        return;
    }
    try {
        const tex = await _textureLoader.loadAsync(textureUrl);
        tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
        tex.repeat.set(4, 4);
        tex.colorSpace = THREE.SRGBColorSpace;
        if (m.map) m.map.dispose();
        m.map = tex;
        m.needsUpdate = true;
    } catch (e) {
        console.warn('[scene_extras] Textur-Load fehlgeschlagen:', textureUrl, e);
    }
}

export function setFloorSize(track, size) {
    if (!track?.mesh) return;
    const s = Math.max(0.5, Math.min(50, size || 6));
    track.mesh.geometry.dispose();
    const geo = new THREE.PlaneGeometry(s, s, 1, 1);
    geo.rotateX(-Math.PI / 2);
    track.mesh.geometry = geo;
    track.floorSize = s;
}

// =========================================================================
// Theatre-Licht-Presets
// =========================================================================

async function _fetchTheatrePresets() {
    if (_cachedTheatrePresets) return _cachedTheatrePresets;
    const resp = await fetch('/api/studio/theatre-presets/');
    const data = await resp.json();
    _cachedTheatrePresets = data.presets || [];
    return _cachedTheatrePresets;
}

async function _applyTheatrePreset(presetName) {
    const resp = await fetch(`/api/studio/theatre-preset/${encodeURIComponent(presetName)}/`);
    if (!resp.ok) { alert(`Preset "${presetName}" nicht gefunden`); return; }
    const preset = await resp.json();
    pushUndo(`Theatre-Preset: ${preset.label || presetName}`);
    for (const lightDef of (preset.lights || [])) {
        _createLightTrackFromDef(lightDef, preset.label || presetName);
    }
    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
    fn.serverLog?.('theatre_preset_applied', `${presetName} — ${preset.lights?.length || 0} lights`);
}

function _createLightTrackFromDef(def, presetLabel) {
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
    track.lightVisible = true;
    track._theatrePreset = presetLabel;
    track.lightHelper = createLightHelper(light);
    if (track.lightHelper) state.scene.add(track.lightHelper);
    state.project.addTrack(track);
    // Start + Ende Keyframes damit das Licht auf der Timeline sichtbar läuft
    addStandardLightKeyframes(track);
    return track;
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

// =========================================================================
// 3D-Objekt-Import (OBJ / GLB / GLTF)
// =========================================================================

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

// Aufgerufen vom Context-Menu: lädt eine 3D-Datei in den Track an Click-Position
export async function addSceneObjectClip(trackIdx, startFrame) {
    const track = state.project.tracks[trackIdx];
    if (!track || track.type !== 'scene_object') return;
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.obj,.glb,.gltf,.fbx';
    input.addEventListener('change', async () => {
        const file = input.files[0];
        if (!file) return;
        try {
            const formData = new FormData();
            formData.append('object', file);
            const upResp = await fetch('/api/studio/scene-object-upload/', { method: 'POST', body: formData });
            const upData = await upResp.json();
            if (!upData.ok) throw new Error(upData.error || 'Upload fehlgeschlagen');
            await _loadSceneObjectIntoTrack(track, upData.url, upData.name, upData.ext, startFrame);
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

async function _loadSceneObjectIntoTrack(track, url, displayName, ext, startFrame) {
    pushUndo('3D-Objekt Clip hinzufügen');
    let object3d = null;
    try {
        if (ext === 'obj') {
            object3d = await new OBJLoader().loadAsync(url);
        } else if (ext === 'glb' || ext === 'gltf') {
            const gltf = await new GLTFLoader().loadAsync(url);
            object3d = gltf.scene;
        } else {
            alert(`Format "${ext}" wird noch nicht unterstützt`);
            return;
        }
    } catch (e) {
        alert('Laden fehlgeschlagen: ' + e.message);
        return;
    }

    if (ext === 'obj') {
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
    if (track.objectTint) setObjectTint(track, track.objectTint);
    state.scene.add(object3d);
    object3d.visible = false;  // Sichtbarkeit per Clip-Timing (applyPlayhead)

    // Clip auf der Timeline anlegen: 10s default
    const fps = state.project.fps;
    const durationFrames = 10 * fps;
    const clip = new Clip(null, displayName.replace(/\.(obj|glb|gltf|fbx)$/i, ''), durationFrames, fps);
    clip.type = 'object_clip';
    clip.startFrame = Math.max(0, startFrame || 0);
    clip.data = { url, ext, fileName: displayName };
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

// =========================================================================
// TransformControls: Ziehen selektierter Szenen-Objekte
// =========================================================================

export function setupTransformControls() {
    if (!state.camera || !state.renderer || !state.scene) return;
    _transformControls = new TransformControls(state.camera, state.renderer.domElement);
    _transformControls.setSize(0.8);
    _transformControls.addEventListener('dragging-changed', (e) => {
        // OrbitControls deaktivieren während Gizmo-Drag
        if (state.controls) state.controls.enabled = !e.value;
    });
    // Three.js r170+: TransformControls ist Controls-Klasse, braucht getHelper()
    // Ältere Versionen: TransformControls ist Object3D direkt
    const helper = typeof _transformControls.getHelper === 'function'
        ? _transformControls.getHelper()
        : _transformControls;
    state.scene.add(helper);
}

export function attachTransformControls(trackOrMesh) {
    if (!_transformControls) return;
    const mesh = trackOrMesh?.mesh || trackOrMesh;
    if (!mesh) return;
    _transformControls.attach(mesh);
}

export function detachTransformControls() {
    if (_transformControls) _transformControls.detach();
}

export function setTransformMode(mode) {
    // 'translate' | 'rotate' | 'scale'
    if (_transformControls) _transformControls.setMode(mode);
}

// =========================================================================
// Floor-Texturen abrufen (für Properties-Dropdown)
// =========================================================================

export async function getFloorTextures() {
    if (_cachedFloorTextures) return _cachedFloorTextures;
    try {
        const resp = await fetch('/api/studio/floor-textures/');
        const data = await resp.json();
        _cachedFloorTextures = data.textures || [];
    } catch (e) {
        _cachedFloorTextures = [{ name: 'none', label: 'Keine', url: '' }];
    }
    return _cachedFloorTextures;
}

// Registry
fn.createFloorTrack = createFloorTrack;
fn.updateFloorMaterial = updateFloorMaterial;
fn.applyFloorTexture = applyFloorTexture;
fn.setFloorSize = setFloorSize;
fn.setupTheatreMenu = setupTheatreMenu;
fn.setupSceneObjectImport = setupSceneObjectImport;
fn.setupTransformControls = setupTransformControls;
fn.attachTransformControls = attachTransformControls;
fn.detachTransformControls = detachTransformControls;
fn.setTransformMode = setTransformMode;
fn.setObjectTint = setObjectTint;
fn.getFloorTextures = getFloorTextures;
fn.addSceneObjectClip = addSceneObjectClip;
