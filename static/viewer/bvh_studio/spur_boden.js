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
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Bodenuntergrund } from './bodenuntergrund.js';
import { pushUndo } from './undo.js';
import { Spurauswahl } from './spurauswahl.js';

let _cachedFloorTextures = null;
const _textureLoader = new THREE.TextureLoader();

/**
 * Boden-Track samt Netz bauen — der gemeinsame Kern von `createFloorTrack`
 * (der geschützte Start-Boden) und `addFloorTrack` (weitere, frei
 * platzierbare Böden, Edgar 22.09.2026: „Boden kann auch mehrfach
 * hinzugefügt werden, auch z-Position (Höhe) ist einstellbar").
 */
function _bodenBauen(name, werte) {
    const { width, length, cx, cy, cz, color, roughness, metalness } = werte;
    const geo = new THREE.PlaneGeometry(width, length, 1, 1);
    geo.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color), roughness, metalness, side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(cx, cy, cz);
    mesh.receiveShadow = true;
    mesh.userData.isFloor = true;
    state.scene.add(mesh);

    const track = new Track(name);
    track.type = 'scene_object';
    track.subtype = 'floor';
    track.color = '#795548';
    track.mesh = mesh;
    track.floorWidth = width;
    track.floorLength = length;
    track.floorSize = Math.max(width, length);  // Legacy-Feld für Abwärtskompatibilität
    track.floorColor = color;
    track.floorRoughness = roughness;
    track.floorMetalness = metalness;
    // Durchsichtiger Boden mit Platte darunter (13.09.2026, `Bodenuntergrund`).
    track.floorTransparenz = werte.transparenz ?? Bodenuntergrund.TRANSPARENZ;
    track.floorTiefe = werte.tiefe ?? Bodenuntergrund.TIEFE_CM;
    Bodenuntergrund.nachziehen(track);
    return track;
}

export function createFloorTrack() {
    if (state.project.tracks.some(t => t._sceneItem === 'floor')) return;
    const override = state.project._pendingSceneOverrides?.sceneFloor;
    // Legacy: quadratische "size" → in width+length konvertieren
    const legacySize = override?.size;
    const track = _bodenBauen('Boden', {
        width: override?.width ?? legacySize ?? 6,
        length: override?.length ?? legacySize ?? 6,
        cx: override?.centerX ?? 0,
        cy: override?.centerY ?? -0.001,
        cz: override?.centerZ ?? 0,
        color: override?.color ?? '#3a3a4a',
        roughness: override?.roughness ?? 0.9,
        metalness: override?.metalness ?? 0.05,
        transparenz: override?.transparenz,
        tiefe: override?.tiefe,
    });
    track._sceneItem = 'floor';
    track.floorTexture = override?.texture || 'none';
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

/**
 * Einen WEITEREN Boden hinzufügen — anders als der Start-Boden nicht
 * geschützt (kein `_sceneItem`), also normal löschbar; über die Höhe
 * (`prop-floor-y` im Eigenschaften-Panel) als eigene Ebene/Bühne platzierbar.
 */
export function addFloorTrack() {
    pushUndo('Boden hinzufügen');
    const anzahl = state.project.tracks.filter(t => t.subtype === 'floor').length;
    const track = _bodenBauen(`Boden ${anzahl + 1}`, {
        width: 6, length: 6, cx: 0, cy: -0.001, cz: 0,
        color: '#3a3a4a', roughness: 0.9, metalness: 0.05,
    });
    track.floorTexture = 'none';
    track.muted = false;
    state.project.addTrack(track);
    fn.updateTrackHeaders();
    fn.renderTimeline();
    Spurauswahl.waehlen(state.project.tracks.length - 1);
    return track;
}

/**
 * Gespeicherte Bodenwerte auf die BESTEHENDE Bodenspur legen.
 *
 * BEFUND (11.09.2026, Edgar: „auch boden größe wird nicht gespeichert"):
 * Gespeichert wurde sie (`Projektdaten._boden`), gelesen nur beim SEITENSTART
 * (`createFloorTrack` über `_pendingSceneOverrides`). Beim Laden zur Laufzeit
 * (Datei → Laden, Rückgängig) bleibt der Boden stehen — `Spurabbau` schützt
 * Szenen-Elemente —, und `createFloorTrack` kehrt beim vorhandenen Boden um,
 * ohne die Werte anzufassen. Im Browser gemessen: 9 × 4 m gespeichert, nach
 * dem Laden 6 × 6.
 */
export function applyFloorOverride(override) {
    const track = state.project.tracks.find(t => t._sceneItem === 'floor');
    if (!track?.mesh || !override) return false;
    const legacySize = override.size;
    setFloorGeometry(track, override.width ?? legacySize ?? 6,
                     override.length ?? legacySize ?? 6,
                     override.centerX ?? 0, override.centerZ ?? 0);
    track.floorColor = override.color ?? track.floorColor;
    track.floorRoughness = override.roughness ?? track.floorRoughness;
    track.floorMetalness = override.metalness ?? track.floorMetalness;
    track.floorTransparenz = override.transparenz ?? Bodenuntergrund.TRANSPARENZ;
    track.floorTiefe = override.tiefe ?? Bodenuntergrund.TIEFE_CM;
    updateFloorMaterial(track);
    track.muted = override.muted || false;
    if (override.gridVisible !== undefined) {
        state.gridVisible = !!override.gridVisible;
        state.scene?.traverse(o => {
            if (o.type === 'GridHelper' || o.isGridHelper) o.visible = state.gridVisible;
        });
    }
    const textur = override.texture || 'none';
    if (textur !== track.floorTexture) {
        if (textur === 'none') applyFloorTexture(track, '');
        else getFloorTextures().then(list => {
            const found = list?.find(x => x.name === textur);
            if (found?.url) applyFloorTexture(track, found.url);
        });
    }
    return true;
}

export function updateFloorMaterial(track) {
    if (!track?.mesh || !track.mesh.material) return;
    const m = track.mesh.material;
    m.color.set(track.floorColor || '#3a3a4a');
    m.roughness = track.floorRoughness ?? 0.9;
    m.metalness = track.floorMetalness ?? 0.05;
    m.needsUpdate = true;
    Bodenuntergrund.nachziehen(track);
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
        Protokoll.warnung('scene_extras', 'Textur-Load fehlgeschlagen:', textureUrl, e);
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
    Bodenuntergrund.nachziehen(track);        // die Platte teilt die Geometrie
}

// Legacy-Wrapper (setFloorSize) — quadratisch, Mittelpunkt unverändert
export function setFloorSize(track, size) {
    setFloorGeometry(track, size, size);
}

/**
 * Höhe (Y-Position) eines Bodens setzen — braucht mehrere Böden auf
 * verschiedenen Ebenen (Edgar, 22.09.2026: „auch z-Position (Höhe) ist
 * einstellbar", gemeint ist die vertikale Achse; die Breite/Länge-Achsen
 * heißen im Panel bereits X/Z).
 */
export function setFloorHeight(track, hoehe) {
    if (!track?.mesh) return;
    track.mesh.position.y = hoehe;
    Bodenuntergrund.nachziehen(track);        // die Platte hängt unter dem Boden
}

export async function getFloorTextures() {
    if (_cachedFloorTextures) return _cachedFloorTextures;
    try {
        const data = await Serverabruf.json('/api/studio/floor-textures/');
        _cachedFloorTextures = data.textures || [];
    } catch (e) {
        _cachedFloorTextures = [{ name: 'none', label: 'Keine', url: '' }];
    }
    return _cachedFloorTextures;
}

fn.addFloorTrack = addFloorTrack;
fn.setFloorHeight = setFloorHeight;
fn.updateFloorMaterial = updateFloorMaterial;
fn.applyFloorTexture = applyFloorTexture;
fn.setFloorGeometry = setFloorGeometry;
fn.applyFloorOverride = applyFloorOverride;
fn.getFloorTextures = getFloorTextures;
