/**
 * Result Character — Cloth templates + MH garments.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import {
        skinifyMesh,
} from '../character_core.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';

// =====================================================================
// Cloth (templates)
// =====================================================================

export async function loadCloth(key, params, presetColor, useApiColor = false) {
    if (!state.isSkinned || !state.rigifySkeleton) return;

    try {
        const qs = Object.entries(params)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        const data = await Serverabruf.json(`/api/character/cloth/?${qs}`);
        if (data.error) { console.error('Cloth error:', data.error); return; }

        removeClothRegion(key);

        const geo = Netzgeometrie.bauen(data, THREE);

        let matColor;
        if (presetColor) {
            matColor = new THREE.Color(presetColor);
        } else if (useApiColor && data.color) {
            matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        } else {
            const colorPicker = document.getElementById('rc-cloth-color');
            matColor = colorPicker
                ? new THREE.Color(colorPicker.value)
                : new THREE.Color(data.color[0], data.color[1], data.color[2]);
        }

        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0,
            side: THREE.DoubleSide,
        });

        const skInfo = (state.isSkinned && state.rigifySkeleton) ? {
            skeleton: state.rigifySkeleton.skeleton, bindMatrix: state.bodyMesh.bindMatrix
        } : null;
        const mesh = skinifyMesh(geo, mat, skInfo, data);

        mesh.visible = state.clothesVisible;
        state.clothMeshes[key] = mesh;
        state.scene.add(mesh);
    } catch (e) {
        console.error('Failed to load cloth:', e);
    }
}

export function removeClothRegion(key) {
    Netzentsorgung.ausAblage(state.scene, state.clothMeshes, key);
}

export function removeAllCloth() {
    for (const key of Object.keys(state.clothMeshes)) {
        removeClothRegion(key);
    }
}

// =====================================================================
// MH Garments
// =====================================================================

export async function loadGarment(garmentId, opts = {}) {
    if (!state.isSkinned || !state.rigifySkeleton) return;

    try {
        const offset = opts.offset !== undefined ? opts.offset : 0.006;
        const stiffness = opts.stiffness !== undefined ? opts.stiffness : 0.8;

        let hasColor = false;
        let cr = 0, cg = 0, cb = 0;
        if (Array.isArray(opts.color)) {
            cr = opts.color[0]; cg = opts.color[1]; cb = opts.color[2];
            hasColor = true;
        } else if (typeof opts.color === 'string') {
            const c = new THREE.Color(opts.color);
            cr = c.r; cg = c.g; cb = c.b;
            hasColor = true;
        }

        let qs = `garment_id=${encodeURIComponent(garmentId)}&body_type=${encodeURIComponent(state.currentBodyType)}`;
        qs += `&offset=${offset}&stiffness=${stiffness}`;
        if (hasColor) {
            qs += `&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;
        }
        for (const [k, v] of Object.entries(state.currentMorphs)) {
            if (Math.abs(v) > 0.001) qs += `&morph_${k}=${v}`;
        }
        for (const [k, v] of Object.entries(state.currentMeta)) {
            if (Math.abs(v) > 0.001) qs += `&meta_${k}=${v}`;
        }

        const data = await Serverabruf.json(`/api/character/garment/fit/?${qs}`);
        if (data.error) {
            console.error('Garment fit error:', data.error);
            return;
        }

        removeGarment(garmentId);

        const vertBuf = Netzgeometrie.punkte(data.vertices);
        const geo = Netzgeometrie.bauen({ vertices: data.vertices,
                                           faces: data.faces }, THREE);

        const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        const roughness = opts.roughness !== undefined ? opts.roughness : 0.8;
        const metalness = opts.metalness !== undefined ? opts.metalness : 0.0;
        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness, metalness,
            side: THREE.DoubleSide,
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnit: -1,
        });

        const skInfo = (state.isSkinned && state.rigifySkeleton) ? {
            skeleton: state.rigifySkeleton.skeleton, bindMatrix: state.bodyMesh.bindMatrix
        } : null;
        const mesh = skinifyMesh(geo, mat, skInfo, data);

        mesh.visible = state.clothesVisible;
        state.garmentMeshes[garmentId] = mesh;
        state.scene.add(mesh);
        Protokoll.debug('result_character', 'Garment loaded:', garmentId);
    } catch (e) {
        console.error('Failed to load garment:', e);
    }
}

export function removeGarment(garmentId) {
    const m = state.garmentMeshes[garmentId];
    if (m) {
        state.scene.remove(m);
        m.geometry.dispose();
        m.material.dispose();
        delete state.garmentMeshes[garmentId];
    }
}

export function removeAllGarments() {
    for (const key of Object.keys(state.garmentMeshes)) {
        removeGarment(key);
    }
}

fn.loadCloth = loadCloth;
fn.removeClothRegion = removeClothRegion;
fn.removeAllCloth = removeAllCloth;
fn.loadGarment = loadGarment;
fn.removeGarment = removeGarment;
fn.removeAllGarments = removeAllGarments;
