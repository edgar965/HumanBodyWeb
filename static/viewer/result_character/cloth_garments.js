/**
 * Result Character — Cloth templates + MH garments.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    skinifyMesh,
} from '../character_core.js?v=1';

// =====================================================================
// Cloth (templates)
// =====================================================================

export async function loadCloth(key, params, presetColor, useApiColor = false) {
    if (!state.isSkinned || !state.rigifySkeleton) return;

    try {
        const qs = Object.entries(params)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        const resp = await fetch(`/api/character/cloth/?${qs}`);
        const data = await resp.json();
        if (data.error) { console.error('Cloth error:', data.error); return; }

        removeClothRegion(key);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

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
    const m = state.clothMeshes[key];
    if (m) {
        state.scene.remove(m);
        m.geometry.dispose();
        m.material.dispose();
        delete state.clothMeshes[key];
    }
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

        const resp = await fetch(`/api/character/garment/fit/?${qs}`);
        const data = await resp.json();
        if (data.error) {
            console.error('Garment fit error:', data.error);
            return;
        }

        removeGarment(garmentId);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.computeVertexNormals();

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
        console.log('[result_character] Garment loaded:', garmentId);
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
