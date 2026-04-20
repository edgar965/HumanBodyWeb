/**
 * BVH Studio — Szenen-Erweiterungen:
 *  - Theatre-Licht-Presets
 *  - Boden-Track (floor) mit Textur/Farb-Properties
 *  - 3D-Objekt-Import (OBJ/GLB/GLTF)
 *  - TransformControls für Positionierung selektierter Szenen-Objekte
 */
import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
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

// Additive-Variante: lässt existierende Lichter unverändert und legt NUR die
// Preset-Lichter an, deren Name noch nicht als Track existiert. Aufgerufen über
// Kontextmenü "Hinzufügen > Presets" auf einem Licht-Track.
// atFrame: Frame, ab dem die neuen Lichter aktiv werden. Existierende Licht-Tracks
// erhalten an diesem Frame einen Pair-KF (upper = aktueller State mit visible=true,
// lower = visible=false) — d.h. ALTE Lichter werden ab atFrame ausgeschaltet,
// NEUE Lichter starten ab atFrame.
async function _applyTheatrePresetAdditive(presetName, atFrame) {
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

async function _applyTheatrePreset(presetName) {
    const resp = await fetch(`/api/studio/theatre-preset/${encodeURIComponent(presetName)}/`);
    if (!resp.ok) { alert(`Preset "${presetName}" nicht gefunden`); return; }
    const preset = await resp.json();
    const presetLights = preset.lights || [];
    pushUndo(`Theatre-Preset: ${preset.label || presetName}`);

    // 1) Alle vorhandenen Licht-Tracks entfernen (Szenen-Lichter + Preset-Lichter)
    //    damit das neue Preset eine saubere Licht-Setup erzeugt.
    const lightIndices = [];
    for (let i = 0; i < state.project.tracks.length; i++) {
        if (state.project.tracks[i].type === 'light') lightIndices.push(i);
    }
    // Von hinten entfernen (Indizes bleiben stabil)
    for (let j = lightIndices.length - 1; j >= 0; j--) {
        const idx = lightIndices[j];
        const t = state.project.tracks[idx];
        if (t.light) {
            if (t.light.target) state.scene.remove(t.light.target);
            state.scene.remove(t.light);
            t.light.dispose?.();
        }
        if (t.lightHelper) {
            state.scene.remove(t.lightHelper);
            t.lightHelper.traverse?.(obj => {
                if (obj.geometry) obj.geometry.dispose?.();
                if (obj.material) obj.material.dispose?.();
            });
        }
        state.project.tracks.splice(idx, 1);
    }

    // 2) Preset-Lichter als neue Tracks anlegen (mit nativen Typen)
    let newTracks = 0;
    for (const def of presetLights) {
        if (_createLightTrackFromDef(def, preset.label || presetName)) newTracks++;
    }

    if (state.selectedTrackIdx >= state.project.tracks.length) {
        state.selectedTrackIdx = state.project.tracks.length - 1;
    }
    fn.updateTrackHeaders?.();
    fn.renderTimeline?.();
    fn.updateProperties?.();
    fn.applyPlayhead?.();
    fn.serverLog?.('theatre_preset_applied',
        `${presetName}: alte Lichter entfernt, ${newTracks} Preset-Lichter`);
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
    track.lightVisible = false;  // Helfer-Linien: default AUS
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

// Liest OBJ-Datei-Inhalt und extrahiert die 'mtllib'-Referenz. Versucht die
// referenzierte MTL-Datei erst unter dem im OBJ angegebenen (Sub-)Pfad zu laden,
// fällt dann auf den reinen Dateinamen im OBJ-Verzeichnis zurück.
// Returns: URL zur gefundenen MTL, oder null.
async function _autoDiscoverMtl(objUrl) {
    try {
        const resp = await fetch(objUrl);
        if (!resp.ok) return null;
        const text = await resp.text();
        // Erster Treffer (OBJ kann mehrere mtllib haben, wir nehmen den ersten)
        const m = text.match(/^\s*mtllib\s+(.+?)\s*$/im);
        if (!m) return null;
        const ref = m[1].trim();
        const cleaned = ref.replace(/\\/g, '/').replace(/^\.\//, '');
        const basePath = objUrl.substring(0, objUrl.lastIndexOf('/') + 1);
        // 1. Versuch: im OBJ angegebener (möglicherweise Sub-)Pfad
        const candidates = [cleaned];
        // 2. Fallback: nur Dateiname (falls User flach ins Bundle geladen hat)
        const fileName = cleaned.split('/').pop();
        if (fileName !== cleaned) candidates.push(fileName);
        for (const c of candidates) {
            const testUrl = basePath + c;
            try {
                const head = await fetch(testUrl, { method: 'HEAD' });
                if (head.ok) {
                    console.log(`[OBJ] mtllib "${ref}" aufgelöst → ${testUrl}`);
                    return testUrl;
                }
            } catch {}
        }
        console.warn(`[OBJ] mtllib "${ref}" konnte nicht im Bundle aufgelöst werden`);
        return null;
    } catch (e) {
        console.warn('[OBJ] MTL-Autodiscover fehlgeschlagen:', e);
        return null;
    }
}

// Parst MTL-Text manuell und baut ein { name: MeshStandardMaterial } Dict.
// Robustet Textur-Pfade (entfernt \\-Separators, ./-Prefix, absolute Pfade → nur Dateiname)
// und lädt jede Textur als eigene Request mit Logging. Texturen werden sowohl unter
// dem im MTL angegebenen (Sub-)Pfad als auch unter dem reinen Dateinamen gesucht.
async function _parseMtlAndBuildMaterials(mtlUrl) {
    const mtlResp = await fetch(mtlUrl);
    if (!mtlResp.ok) throw new Error(`MTL-Fetch HTTP ${mtlResp.status}`);
    const mtlText = await mtlResp.text();
    const basePath = mtlUrl.substring(0, mtlUrl.lastIndexOf('/') + 1);

    // 1) Parse MTL
    const parsed = {};  // name → props
    let current = null;
    for (const raw of mtlText.split(/\r?\n/)) {
        const line = raw.trim();
        if (!line || line.startsWith('#')) continue;
        const parts = line.split(/\s+/);
        const cmd = parts[0];
        if (cmd === 'newmtl') {
            current = { name: parts.slice(1).join(' ') };
            parsed[current.name] = current;
            continue;
        }
        if (!current) continue;
        const val = parts.slice(1).join(' ');
        if (cmd === 'Kd') current.Kd = parts.slice(1, 4).map(parseFloat);
        else if (cmd === 'Ka') current.Ka = parts.slice(1, 4).map(parseFloat);
        else if (cmd === 'Ks') current.Ks = parts.slice(1, 4).map(parseFloat);
        else if (/^map_kd$/i.test(cmd)) current.map_Kd = val;
        else if (/^map_ks$/i.test(cmd)) current.map_Ks = val;
        else if (/^map_ka$/i.test(cmd)) current.map_Ka = val;
        else if (/^(map_bump|bump)$/i.test(cmd)) current.map_Bump = val;
        else if (/^map_ns$/i.test(cmd)) current.map_Ns = val;
        else if (/^(d|tr)$/i.test(cmd)) current.opacity = parseFloat(parts[1]);
        else if (cmd === 'Ns') current.shininess = parseFloat(parts[1]);
    }

    // 2) Textur-Pfad normalisieren und laden
    const texLoader = new THREE.TextureLoader();
    const loadTex = async (rawPath) => {
        // MTL-Optionen ignorieren (z.B. "-s 1 1 -o 0 0 0 filename.png")
        const tokens = rawPath.split(/\s+/).filter(t => t && !t.startsWith('-'));
        const candidate = tokens[tokens.length - 1] || rawPath;
        // Backslashes → Slashes, ./ entfernen
        const cleaned = candidate.replace(/\\/g, '/').replace(/^\.\//, '');
        const fileName = cleaned.split('/').pop();
        if (!fileName) return null;
        // Versuche beide Varianten: subpath (wie im MTL) UND basename (falls flach ins Bundle hochgeladen)
        const candidates = [cleaned];
        if (fileName !== cleaned) candidates.push(fileName);
        for (const c of candidates) {
            const fullUrl = basePath + c;
            try {
                const tex = await texLoader.loadAsync(fullUrl);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                tex.colorSpace = THREE.SRGBColorSpace;
                tex.needsUpdate = true;
                console.log(`[MTL] Textur geladen: ${c}`);
                return tex;
            } catch (e) {
                // stille Retry auf nächsten Kandidaten
            }
        }
        console.warn(`[MTL] Textur NICHT GEFUNDEN: "${rawPath}" — getestet: ${candidates.map(c => basePath + c).join(', ')}`);
        return null;
    };

    // 3) MeshStandardMaterial pro Eintrag bauen
    const materials = {};
    for (const [name, m] of Object.entries(parsed)) {
        const opts = { roughness: 0.85, metalness: 0.02, side: THREE.DoubleSide };
        if (m.Kd && m.Kd.length === 3) opts.color = new THREE.Color(m.Kd[0], m.Kd[1], m.Kd[2]);
        else opts.color = new THREE.Color(0xffffff);
        if (m.map_Kd) {
            const tex = await loadTex(m.map_Kd);
            if (tex) opts.map = tex;
        }
        if (m.map_Ks) {
            const tex = await loadTex(m.map_Ks);
            if (tex) opts.roughnessMap = tex;
        }
        if (m.map_Bump) {
            const tex = await loadTex(m.map_Bump);
            if (tex) opts.normalMap = tex;
        }
        if (m.opacity != null && m.opacity < 1) { opts.transparent = true; opts.opacity = m.opacity; }
        const mat = new THREE.MeshStandardMaterial(opts);
        mat.name = name;
        materials[name] = mat;
    }
    return materials;
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
            alert(`Format "${ext}" wird noch nicht unterstützt`);
            return;
        }
    } catch (e) {
        alert('Laden fehlgeschlagen: ' + e.message);
        return;
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
fn.setFloorGeometry = setFloorGeometry;
fn.setupTheatreMenu = setupTheatreMenu;
fn.setupSceneObjectImport = setupSceneObjectImport;
fn.setupTransformControls = setupTransformControls;
fn.attachTransformControls = attachTransformControls;
fn.detachTransformControls = detachTransformControls;
fn.setTransformMode = setTransformMode;
fn.setObjectTint = setObjectTint;
fn.getFloorTextures = getFloorTextures;
fn.addSceneObjectClip = addSceneObjectClip;
fn.applyTheatrePresetAdditive = _applyTheatrePresetAdditive;
fn.fetchTheatrePresets = _fetchTheatrePresets;
