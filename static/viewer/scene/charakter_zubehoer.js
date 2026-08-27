/**
 * Charakterzubehoer — Stoff, Kleidung, Haare und MakeHuman-Proxys eines
 * Charakters nachladen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026): Die Klasse
 * CharacterInstance hatte 537 Zeilen, davon 220 nur fuer das Nachladen von
 * Zubehoer. Als statische Methoden mit dem Charakter als erstem Parameter
 * bleibt der Ablauf lesbar, ohne die Klasse weiter aufzublaehen.
 */

import * as THREE from 'three';
import { state, gltfLoader } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _computeGarmentRegionWeights } from './kleidung_anpassen.js';
import { Kleidungszustand } from './kleidungszustand.js';
import { _skinifyHairGroup, _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Stoffgeometrie } from '../gemeinsam/stoffgeometrie.js';

export class Charakterzubehoer {

    static async proxys(inst) {
        const list = inst._pendingMHProxies || [];
        inst._pendingMHProxies = [];
        for (const entry of list) {
            if (!entry || !entry.id) continue;
            try { await fn._fitMHProxyOnInst(inst, entry.id, entry); }
            catch (e) { Protokoll.warnung('charakter_zubehoer', 'MH proxy load failed:', entry.id, e); }
        }
    }

    static async stoff(inst) {
        for (const [key, mesh] of Object.entries(inst.clothMeshes)) {
            inst.group.remove(mesh);
            mesh.geometry.dispose();
            mesh.material.dispose();
        }
        inst.clothMeshes = {};

        if (!inst.cloth || inst.cloth.length === 0) return;
        const isMale = inst.bodyType.startsWith('Male_');
        if (isMale) return;

        if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(inst);
        }

        for (const c of inst.cloth) {
            try {
                const method = c.method || 'template';
                const params = new URLSearchParams();
                params.set('method', method);
                params.set('body_type', inst.bodyType);

                let key;
                if (method === 'builder') {
                    params.set('region', c.region || 'TOP');
                    params.set('looseness', c.looseness !== undefined ? c.looseness : 0.5);
                    key = `bld_${c.region || 'TOP'}`;
                } else if (method === 'primitive') {
                    params.set('prim_type', c.prim_type || 'PRIM_SKIRT');
                    params.set('segments', c.segments || 32);
                    params.set('length', c.length !== undefined ? c.length : 0.5);
                    params.set('flare', c.flare !== undefined ? c.flare : 0.5);
                    key = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                } else {
                    const tpl = c.template || 'TPL_TSHIRT';
                    params.set('template', tpl);
                    params.set('tightness', c.tightness !== undefined ? c.tightness : 0.5);
                    params.set('segments', c.segments || 32);
                    if (c.top_extend) params.set('top_extend', c.top_extend);
                    if (c.bottom_extend) params.set('bottom_extend', c.bottom_extend);
                    key = `tpl_${tpl}`;
                }

                for (const [k, v] of Object.entries(inst.morphs)) {
                    if (v !== 0) params.set(`morph_${k}`, v);
                }
                for (const [k, v] of Object.entries(inst.meta)) {
                    if (v !== 0) params.set(`meta_${k}`, v);
                }

                const data = await Serverabruf.json(`/api/character/cloth/?${params}`);
                if (data.error) { Protokoll.warnung('charakter_zubehoer', 'Cloth error:', data.error); continue; }

                const geo = Stoffgeometrie.bauen(data, THREE);

                const matColor = c.color ? new THREE.Color(c.color) : new THREE.Color(0.5, 0.5, 0.6);
                const mat = new THREE.MeshStandardMaterial({
                    color: matColor, roughness: 0.8, metalness: 0.0,
                    side: THREE.DoubleSide,
                });

                const mesh = _skinifyMesh(geo, mat, inst, data);
                inst.clothMeshes[key] = mesh;
                inst.group.add(mesh);
            } catch (e) {
                console.error('Failed to load cloth piece:', e);
            }
        }
    }

    static async kleidung(inst) {
        if (!inst.garments || inst.garments.length === 0) return;

        if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(inst);
        }

        const params = new URLSearchParams();
        params.set('body_type', inst.bodyType);
        for (const [k, v] of Object.entries(inst.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(inst.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        for (const g of inst.garments) {
            try {
                const p = new URLSearchParams(params);
                p.set('garment_id', g.id);
                p.set('offset', (g.offset || 0).toFixed(4));
                p.set('stiffness', (g.stiffness || 0.5).toFixed(2));
                p.set('min_dist', g.minDist !== undefined ? g.minDist : 3);
                p.set('crotch_floor', g.crotchFloor !== undefined ? g.crotchFloor : 0);
                p.set('lift', g.lift !== undefined ? g.lift : 0);
                p.set('crotch_depth', g.crotchDepth !== undefined ? g.crotchDepth : 0);
                if (g.color) {
                    let cr, cg, cb;
                    if (Array.isArray(g.color)) {
                        [cr, cg, cb] = g.color;
                    } else {
                        const tc = new THREE.Color(g.color);
                        cr = tc.r; cg = tc.g; cb = tc.b;
                    }
                    p.set('color_r', cr.toFixed(3));
                    p.set('color_g', cg.toFixed(3));
                    p.set('color_b', cb.toFixed(3));
                }

                const data = await Serverabruf.json(`/api/character/garment/fit/?${p}`);
                if (data.error) {
                    Protokoll.warnung('charakter_zubehoer', 'Garment load error:', data.error);
                    continue;
                }

                const vertBuf = Stoffgeometrie.punkte(data.vertices);
                const geo = Stoffgeometrie.bauen(
                    { vertices: data.vertices, faces: data.faces }, THREE);

                const color = g.color ? new THREE.Color(g.color[0], g.color[1], g.color[2])
                                      : new THREE.Color(0.3, 0.35, 0.5);
                const mat = new THREE.MeshStandardMaterial({
                    color, roughness: g.roughness ?? 0.8, metalness: g.metalness ?? 0.0,
                    side: THREE.DoubleSide,
                    polygonOffset: true,
                    polygonOffsetFactor: -1,
                    polygonOffsetUnit: -1,
                });

                const mesh = _skinifyMesh(geo, mat, inst, data);
                const key = `gar_${g.id}`;
                inst.clothMeshes[key] = mesh;
                inst.group.add(mesh);

                inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
                _computeGarmentRegionWeights(inst, key);

                // Die Vorgabewerte stehen in `Kleidungszustand.VORGABEN` —
                // vorher stand die Feldliste hier ein viertes Mal.
                inst.garmentState[key] = Kleidungszustand.ausJson({
                    ...g, color: g.color || [color.r, color.g, color.b],
                });
            } catch (e) {
                console.error('Failed to load garment:', g.id, e);
            }
        }
    }

    static async haare(inst) {
        if (inst.hairMesh) {
            inst.group.remove(inst.hairMesh);
            inst.hairMesh.traverse(child => {
                if (child.isMesh) {
                    child.geometry.dispose();
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => m.dispose());
                }
            });
            inst.hairMesh = null;
        }

        if (!inst.hairStyle || !inst.hairStyle.url) return;

        return new Promise((resolve) => {
            gltfLoader.load(inst.hairStyle.url, (gltf) => {
                let hairGroup = gltf.scene;

                if (inst.isSkinned && inst.rigifySkeleton) {
                    hairGroup = _skinifyHairGroup(hairGroup, inst);
                }

                inst.hairMesh = hairGroup;

                if (inst.hairStyle.color && state.hairColorData[inst.hairStyle.color]) {
                    const rgb = state.hairColorData[inst.hairStyle.color];
                    const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
                    inst.hairMesh.traverse(child => {
                        if (child.isMesh && child.material) {
                            const mats = Array.isArray(child.material) ? child.material : [child.material];
                            mats.forEach(m => { m.color.copy(color); });
                        }
                    });
                }

                inst.group.add(inst.hairMesh);
                resolve();
            }, undefined, (err) => {
                Protokoll.warnung('charakter_zubehoer', 'Failed to load hair:', err);
                resolve();
            });
        });
    }
}

// In der Registrierung angemeldet, damit skeleton.js die Haare nachladen kann,
// ohne diese Datei zu importieren: charakter_zubehoer.js holt sich seinerseits
// `convertInstToSkinned` von dort — ein direkter Import waere ein Ring.
fn.charakterHaare = (inst) => Charakterzubehoer.haare(inst);
