/**
 * Viewer — Hair UI (loading, refit, coloring).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { ensureSkinned } from './skinning.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Auswahlfeld } from '../gemeinsam/auswahlfeld.js';
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

        Auswahlfeld.fuellen(select, (data.hairstyles || []).map(
            (h) => ({ wert: h.url, text: h.label, daten: { name: h.name } })));
        Auswahlfeld.ausNamen(colorSelect, Object.keys(state.hairColorData));

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
        const colorSelect = document.getElementById('hair-color-select');
        _einsetzen(gltf.scene, {farbe: colorSelect && colorSelect.value});
        Protokoll.debug('Viewer', 'Hair loaded:', url, 'skinned=' + (state.isSkinned && state.rigifySkeleton ? 'yes'
            : 'no'));
    }, undefined, (err) => {
        console.error('Failed to load hair:', err);
    });
}

/**
 * Ein geladenes Haar-Modell an die Figur haengen.
 *
 * BEFUND `doppelcode` (30.08.2026): Diese sieben Zeilen standen in `loadHair`
 * und in `refitHairToBody` — beide laden dieselbe Datei, nur einmal frisch und
 * einmal umskaliert nach einer Koerpergroessen-Aenderung.
 *
 * DIE REIHENFOLGE ZAEHLT: Erst skalieren, DANN binden. Andersherum bekaeme das
 * `SkinnedMesh` seine Bindematrix auf der alten Groesse, und das Haar sitzt bei
 * jeder Kopfdrehung daneben — sichtbar erst in Bewegung, nicht in der Ruhelage.
 *
 * OHNE HAUTDATEN bleibt es eine gewoehnliche Gruppe. Sie haengt dann an der
 * Szene statt am Kopf und bleibt stehen, wenn die Figur laeuft. Das ist kein
 * Fehler dieser Stelle: Die Figur ist dann noch nicht gebunden.
 */
function _einsetzen(gruppe, {farbe, skalierung} = {}) {
    if (skalierung) {
        gruppe.traverse(kind => {
            if (kind.isMesh) kind.geometry.scale(skalierung, skalierung, skalierung);
        });
    }
    if (state.isSkinned && state.rigifySkeleton && state.skinWeightData) {
        const kopf = _findHeadBoneIndex();
        if (kopf >= 0) gruppe = _skinifyHairGroup(gruppe, kopf);
    }
    state.hairMesh = gruppe;
    if (farbe) applyHairColorToObject(state.hairMesh, farbe);
    state.scene.add(state.hairMesh);
    fn.updateEquippedList();
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
        _einsetzen(gltf.scene, {farbe: colorName, skalierung: scale});
        Protokoll.debug('Hair refit',
            `scale=${scale.toFixed(4)} (initial=${state.initialBodyTop.toFixed(4)}, current=${currentTop.toFixed(4)})`);
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
