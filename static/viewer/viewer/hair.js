/**
 * Viewer — Hair UI (loading, refit, coloring).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { ensureSkinned } from './skinning.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Werkstofffreigabe } from '../gemeinsam/werkstofffreigabe.js';
import { applyHairColor, findHeadBoneIndex, skinifyHairGroup }
    from '../character_core.js';

export async function loadHairUI() {
    try {
        const data = await Serverabruf.json('/api/character/hairstyles/');
        const select = document.getElementById('hair-style-select');
        const colorSelect = document.getElementById('hair-color-select');
        if (!select) return;

        state.hairColorData = data.colors || {};

        (data.hairstyles || []).forEach(h => {
            const opt = document.createElement('option');
            opt.value = h.url;
            opt.textContent = h.label;
            opt.dataset.name = h.name;
            select.appendChild(opt);
        });

        if (colorSelect) {
            Object.keys(state.hairColorData).forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                colorSelect.appendChild(opt);
            });
        }

        select.addEventListener('change', () => {
            if (!select.value) { removeHair(); return; }
            loadHair(select.value);
        });

        if (colorSelect) {
            colorSelect.addEventListener('change', () => {
                haarfarbeSetzen(colorSelect.value);
            });
        }
    } catch (e) {
        Protokoll.warnung('hair', 'Hair UI not available:', e);
    }
}

export function loadHair(url) {
    removeHair();
    ensureSkinned();

    state.gltfLoader.load(url, (gltf) => {
        let hairGroup = gltf.scene;

        if (state.isSkinned && state.rigifySkeleton && state.skinWeightData) {
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
        }

        state.hairMesh = hairGroup;
        const colorSelect = document.getElementById('hair-color-select');
        if (colorSelect && colorSelect.value) {
            applyHairColorToObject(state.hairMesh, colorSelect.value);
        }
        state.scene.add(state.hairMesh);
        Protokoll.debug('Viewer', 'Hair loaded:', url, 'skinned=' + (state.isSkinned && state.rigifySkeleton ? 'yes' : 'no'));
        fn.updateEquippedList();
    }, undefined, (err) => {
        console.error('Failed to load hair:', err);
    });
}

/** Kopfknochen dieser Seite — die Suche steht in `character_core`
 *  (Umbau 28.08.2026, Befund `doppelcode`). */
function _findHeadBoneIndex() {
    return findHeadBoneIndex(state.skinWeightData);
}

/** Haare an den Kopfknochen des SEITENZUSTANDS binden.
 *
 *  Die Rechnung steht in `character_core.skinifyHairGroup` (Umbau
 *  28.08.2026, Befund `doppelcode`) — hier stand sie ein drittes Mal. */
function _skinifyHairGroup(gltfScene, headBoneIdx) {
    return skinifyHairGroup(gltfScene, headBoneIdx,
                            state.rigifySkeleton.skeleton,
                            state.bodyMesh.bindMatrix);
}

export function removeHair() {
    if (state.hairMesh) {
        state.scene.remove(state.hairMesh);
        Werkstofffreigabe.baum(state.hairMesh);   // samt Texturen
        state.hairMesh = null;
        fn.updateEquippedList();
    }
}

export function refitHairToBody() {
    if (!state.bodyGeometry || state.initialBodyTop === null) return;
    const hairSelect = document.getElementById('hair-style-select');
    if (!hairSelect || !hairSelect.value) return;
    if (!state.hairMesh) return;

    const currentTop = fn._getBodyTop();
    if (currentTop === null || Math.abs(currentTop - state.initialBodyTop) < 0.001) return;
    const scale = currentTop / state.initialBodyTop;

    const hairUrl = hairSelect.value;
    const colorSelect = document.getElementById('hair-color-select');
    const colorName = colorSelect ? colorSelect.value : '';
    removeHair();

    state.gltfLoader.load(hairUrl, (gltf) => {
        let hairGroup = gltf.scene;

        hairGroup.traverse(child => {
            if (child.isMesh) {
                child.geometry.scale(scale, scale, scale);
            }
        });

        if (state.isSkinned && state.rigifySkeleton && state.skinWeightData) {
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
        }

        state.hairMesh = hairGroup;
        if (colorName) applyHairColorToObject(state.hairMesh, colorName);
        state.scene.add(state.hairMesh);
        fn.updateEquippedList();
        Protokoll.debug('Hair refit', `scale=${scale.toFixed(4)} (initial=${state.initialBodyTop.toFixed(4)}, current=${currentTop.toFixed(4)})`);
    }, undefined, (err) => {
        console.error('[Hair refit] failed to reload:', err);
    });
}

/**
 * Die Farbe auf das Haar DIESER SEITE legen.
 *
 * Hiess bis zum 28.08.2026 ebenfalls `applyHairColor` — wie die Rechnung in
 * `character_core`, aber mit anderer Bedeutung und anderer Signatur. Ein Name
 * fuer zwei Dinge ist genauso teuer wie zwei Namen fuer eins (Kriterium 7);
 * aufgefallen ist es, als diese Datei die gemeinsame Fassung importieren
 * sollte und der Modullader abbrach.
 */
export function haarfarbeSetzen(colorName) {
    if (state.hairMesh) applyHairColorToObject(state.hairMesh, colorName);
}

/** Haarfarbe auf einen Objektbaum legen — die Rechnung steht in
 *  `character_core.applyHairColor` (Umbau 28.08.2026, Befund `doppelcode`;
 *  sie stand dreimal im Projekt). */
export function applyHairColorToObject(obj, colorName) {
    applyHairColor(obj, colorName, state.hairColorData);
}

// Register
fn.loadHairUI = loadHairUI;
fn.loadHair = loadHair;
fn.removeHair = removeHair;
fn.refitHairToBody = refitHairToBody;
fn.applyHairColor = haarfarbeSetzen;
