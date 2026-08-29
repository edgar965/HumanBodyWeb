/**
 * Viewer — Cloth UI (template/builder/primitive cloth generation).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, bindSlider, sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { Stoffvorlagen } from './cloth/stoffvorlagen.js';
import { Stoffbauer } from './cloth/stoffbauer.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';

/**
 * Kleidungs-Bedienfeld aufbauen.
 *
 * Der Inhalt steckt in cloth/stoffvorlagen.js und cloth/stoffbauer.js — vorher
 * 245 Zeilen in dieser einen Funktion, mit vier Bereichen und verschachtelten
 * Hilfsfunktionen dazwischen.
 */
export async function loadClothUI() {
    try {
        const daten = await Serverabruf.json('/api/character/cloth/regions/');
        const dienste = {
            reglerBinden: bindSlider,
            reglerWert: sliderVal,
            stoffLaden: (key, params, farbe) => loadCloth(key, params, farbe),
            bereichEntfernen: removeClothRegion,
            stoffNetze: () => state.clothMeshes,
        };
        new Stoffvorlagen(daten, dienste).verdrahten();
        new Stoffbauer(daten, dienste).verdrahten();
        document.getElementById('cloth-remove-all')
            ?.addEventListener('click', () => removeAllCloth());
    } catch (fehler) {
        Protokoll.warnung('cloth', 'Kleidungs-Bedienfeld nicht verfuegbar:', fehler);
    }
}

export async function loadCloth(key, params, color) {
    const createBtns = document.querySelectorAll('#cloth-tpl-create, #cloth-bld-create, #cloth-prim-create');
    createBtns.forEach(b => b.disabled = true);

    ensureSkinned();

    try {
        const qs = Object.entries(params)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        const data = await Serverabruf.json(`/api/character/cloth/?${qs}`);
        if (data.error) { console.error('Cloth error:', data.error); return; }

        removeClothRegion(key);

        const geo = Netzgeometrie.bauen(data, THREE);

        let matColor;
        if (color) {
            matColor = new THREE.Color(color);
        } else {
            const colorPicker = document.getElementById('cloth-color');
            matColor = colorPicker
                ? new THREE.Color(colorPicker.value)
                : new THREE.Color(data.color[0], data.color[1], data.color[2]);
        }

        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide });

        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        state.clothMeshes[key] = mesh;
        state.clothParams[key] = { params, color: '#' + mesh.material.color.getHexString() };
        state.scene.add(mesh);

        Protokoll.debug('Viewer', `Cloth ${key}: ${data.vertex_count} verts, ${data.face_count} tris, skinned=${mesh.isSkinnedMesh || false}`);
        fn.updateEquippedList();
    } catch (e) {
        console.error('Failed to load cloth:', e);
    }
    createBtns.forEach(b => b.disabled = false);
}

export function removeClothRegion(key) {
    if (!Netzentsorgung.ausAblage(state.scene, state.clothMeshes, key)) return;
    delete state.clothParams[key];
    fn.updateEquippedList();
}

export function removeAllCloth() {
    for (const key of Object.keys(state.clothMeshes)) {
        removeClothRegion(key);
    }
}

// Register
fn.loadClothUI = loadClothUI;
fn.loadCloth = loadCloth;
fn.removeClothRegion = removeClothRegion;
fn.removeAllCloth = removeAllCloth;
