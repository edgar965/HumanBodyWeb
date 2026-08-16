/**
 * Bodenspur der Szene: anlegen, Material, Textur, Abmessungen.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026) — die Datei hatte 784
 * Zeilen und vier voellig getrennte Themen: Boden, Theatre-Lichtvorgaben,
 * Objektimport und die Anfasser zum Verschieben.
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track } from './models.js';

let _cachedFloorTextures = null;
const _textureLoader = new THREE.TextureLoader();


export function createFloorTrack() {
    if (state.project.tracks.some(t => t._sceneItem === 'floor')) return;
    const override = state.project._pendingSceneOverrides?.sceneFloor;
    // Legacy: quadratische "size" → in width+length konvertieren
    const legacySize = override?.size;
    const width = override?.width ?? legacySize ?? 6;
    const length = override?.length ?? legacySize ?? 6;
    const cx = override?.centerX ?? 0;
    const cz = override?.centerZ ?? 0;
    const color = override?.color ?? '#3a3a4a';
    const roughness = override?.roughness ?? 0.9;
    const metalness = override?.metalness ?? 0.05;

    const geo = new THREE.PlaneGeometry(width, length, 1, 1);
    geo.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color), roughness, metalness, side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(cx, -0.001, cz);
    mesh.receiveShadow = true;
    mesh.userData.isFloor = true;
    state.scene.add(mesh);

    const track = new Track('Boden');
    track.type = 'scene_object';
    track.subtype = 'floor';
    track.color = '#795548';
    track._sceneItem = 'floor';
    track.mesh = mesh;
    track.floorWidth = width;
    track.floorLength = length;
    track.floorSize = Math.max(width, length);  // Legacy-Feld für Abwärtskompatibilität
    track.floorTexture = override?.texture || 'none';
    track.floorColor = color;
    track.floorRoughness = roughness;
    track.floorMetalness = metalness;
    track.muted = override?.muted || false;
    state.project.addTrack(track);
    // Grid-Sichtbarkeit aus Save wiederherstellen
    if (override?.gridVisible !== undefined) {
        state.gridVisible = !!override.gridVisible;
        state.scene?.traverse(o => {
            if (o.type === 'GridHelper' || o.isGridHelper) o.visible = state.gridVisible;
        });
    }
    // Textur aus Save anwenden
    if (override?.texture && override.texture !== 'none') {
        // Im Property-Panel wird ein Textur-Dropdown mit URLs geladen — hier haben wir nur den Namen,
        // daher triggern wir eine Wiederanwendung wenn Texturen-Liste verfügbar ist.
        setTimeout(() => {
            fn.getFloorTextures?.().then(list => {
                const found = list?.find(x => x.name === override.texture);
                if (found?.url) applyFloorTexture(track, found.url);
            });
        }, 0);
    }
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

// Boden-Geometrie neu erzeugen. centerX/centerZ sind optional — wenn nicht
// angegeben, bleibt der bestehende Mittelpunkt erhalten (zentriertes Wachstum).
export function setFloorGeometry(track, width, length, centerX, centerZ) {
    if (!track?.mesh) return;
    const w = Math.max(0.2, Math.min(200, width  || 6));
    const l = Math.max(0.2, Math.min(200, length || 6));
    track.mesh.geometry.dispose();
    const geo = new THREE.PlaneGeometry(w, l, 1, 1);
    geo.rotateX(-Math.PI / 2);
    track.mesh.geometry = geo;
    if (centerX != null) track.mesh.position.x = centerX;
    if (centerZ != null) track.mesh.position.z = centerZ;
    track.floorWidth = w;
    track.floorLength = l;
    track.floorSize = Math.max(w, l);
}

// Legacy-Wrapper (setFloorSize) — quadratisch, Mittelpunkt unverändert
export function setFloorSize(track, size) {
    setFloorGeometry(track, size, size);
}

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

fn.createFloorTrack = createFloorTrack;
fn.updateFloorMaterial = updateFloorMaterial;
fn.applyFloorTexture = applyFloorTexture;
fn.setFloorSize = setFloorSize;
fn.setFloorGeometry = setFloorGeometry;
fn.getFloorTextures = getFloorTextures;
