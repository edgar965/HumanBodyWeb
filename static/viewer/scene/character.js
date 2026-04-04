/**
 * Scene Editor -- CharacterInstance class + character management.
 */
import { THREE, gltfLoader, BODY_MATERIALS, buildRigifySkeleton, generateModelMesh, generateRigBoneMesh } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, escapeHtml, generateCharacterId, _getBodyTop } from './utils.js';
import { _skinifyMesh, _skinifyHairGroup, convertInstToSkinned } from './skeleton.js';
import { markDirty } from './undo.js';
import { _computeGarmentRegionWeights } from './garments.js';

// =========================================================================
// CharacterInstance
// =========================================================================
export class CharacterInstance {
    constructor(id, presetData) {
        this.id = id;
        this.presetName = presetData.name || presetData.label || 'Unnamed';
        this.bodyType = presetData.body_type || 'Female_Caucasian';
        this.morphs = presetData.morphs || {};
        this.meta = presetData.meta || {};
        this.cloth = presetData.cloth || [];
        this.hairStyle = presetData.hair_style || null;
        this.garments = presetData.garments || [];
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        this.clothMeshes = {};
        this.garmentState = {};
        this.garmentOrigPositions = {};
        this.garmentRegionWeights = {};
        this.hairMesh = null;
        this.initialBodyTop = 0;
        this.selected = false;
        this.isSkinned = false;
        this.rigifySkeleton = null;
        this.generatedConfig = presetData.type === 'generated_model' ? presetData : null;
    }

    async load() {
        if (this.generatedConfig) {
            return this._loadGeneratedModel();
        }

        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const resp = await fetch(`/api/character/mesh/?${params}`);
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            index = new THREE.BufferAttribute(base64ToUint32(data.faces), 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            uvAttr = new THREE.BufferAttribute(base64ToFloat32(data.uvs), 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];
        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            this.bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            this.bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        this._applySkinColor(materials);
        this.group.add(this.bodyMesh);
        this.initialBodyTop = _getBodyTop(this);

        await this._loadCloth();
        await this._loadHair();
        await this._loadGarments();

        return this;
    }

    async reloadBody() {
        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const resp = await fetch(`/api/character/mesh/?${params}`);
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        if (this.bodyMesh && this.bodyMesh.geometry.attributes.position.count === vertBuf.length / 3) {
            this.bodyMesh.geometry.attributes.position.array.set(vertBuf);
            this.bodyMesh.geometry.attributes.position.needsUpdate = true;

            if (data.normals) {
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);
                if (this.bodyMesh.geometry.attributes.normal) {
                    this.bodyMesh.geometry.attributes.normal.array.set(normalBuf);
                    this.bodyMesh.geometry.attributes.normal.needsUpdate = true;
                }
            } else {
                this.bodyMesh.geometry.computeVertexNormals();
            }

            this.bodyMesh.geometry.computeBoundingSphere();
            this.bodyMesh.geometry.computeBoundingBox();
        } else {
            if (this.bodyMesh) {
                this.group.remove(this.bodyMesh);
                this.bodyMesh.geometry.dispose();
                const mats = Array.isArray(this.bodyMesh.material)
                    ? this.bodyMesh.material : [this.bodyMesh.material];
                mats.forEach(m => m.dispose());
                this.bodyMesh = null;
            }
            await this.load();
        }
    }

    async _loadGeneratedModel() {
        const skelType = this.generatedConfig.skeleton_type || 'def';
        let result;

        if (skelType === 'rig') {
            if (!state._mgRigBonesData) {
                const r = await fetch('/api/character/rig/');
                if (r.ok) state._mgRigBonesData = await r.json();
            }
            if (!state._mgRigBonesData) {
                throw new Error('Rig bones data not loaded');
            }
            result = generateRigBoneMesh(state._mgRigBonesData, this.generatedConfig, state.rigifySkeletonData, state.skinWeightData);
            if (result.skeleton) {
                this.rigifySkeleton = result.skeleton;
                this.isSkinned = true;
            }
        } else {
            if (!state.rigifySkeletonData || !state.skinWeightData) {
                throw new Error('Skeleton data not loaded');
            }
            result = generateModelMesh(state.rigifySkeletonData, state.skinWeightData, this.generatedConfig);
            if (result.skeleton) {
                this.rigifySkeleton = result.skeleton;
                this.isSkinned = true;
            }
        }

        if (!result) throw new Error('No visible bones in generated model config');

        this.bodyMesh = result.mesh;
        this.group.add(this.bodyMesh);
        return this;
    }

    _applySkinColor(materials) {
        if (!Object.keys(state.skinColors).length) return;
        const parts = this.bodyType.split('_');
        const ethnicity = parts.length > 1 ? parts.slice(1).join('_') : 'Caucasian';
        const colors = state.skinColors[ethnicity] || state.skinColors['Caucasian'];
        if (colors && materials[0]) {
            materials[0].color.setRGB(
                Math.pow(colors[0], 1/2.2),
                Math.pow(colors[1], 1/2.2),
                Math.pow(colors[2], 1/2.2)
            );
            if (materials[1]) {
                materials[1].color.copy(materials[0].color);
            }
        }
    }

    async _loadCloth() {
        for (const [key, mesh] of Object.entries(this.clothMeshes)) {
            this.group.remove(mesh);
            mesh.geometry.dispose();
            mesh.material.dispose();
        }
        this.clothMeshes = {};

        if (!this.cloth || this.cloth.length === 0) return;
        const isMale = this.bodyType.startsWith('Male_');
        if (isMale) return;

        if (!this.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(this);
        }

        for (const c of this.cloth) {
            try {
                const method = c.method || 'template';
                const params = new URLSearchParams();
                params.set('method', method);
                params.set('body_type', this.bodyType);

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

                for (const [k, v] of Object.entries(this.morphs)) {
                    if (v !== 0) params.set(`morph_${k}`, v);
                }
                for (const [k, v] of Object.entries(this.meta)) {
                    if (v !== 0) params.set(`meta_${k}`, v);
                }

                const resp = await fetch(`/api/character/cloth/?${params}`);
                const data = await resp.json();
                if (data.error) { console.warn('Cloth error:', data.error); continue; }

                const vertBuf = base64ToFloat32(data.vertices);
                blenderToThreeCoords(vertBuf);
                const faceBuf = base64ToUint32(data.faces);
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);

                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
                geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
                geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

                const matColor = c.color ? new THREE.Color(c.color) : new THREE.Color(0.5, 0.5, 0.6);
                const mat = new THREE.MeshStandardMaterial({
                    color: matColor, roughness: 0.8, metalness: 0.0,
                    side: THREE.DoubleSide,
                });

                const mesh = _skinifyMesh(geo, mat, this, data);
                this.clothMeshes[key] = mesh;
                this.group.add(mesh);
            } catch (e) {
                console.error('Failed to load cloth piece:', e);
            }
        }
    }

    async _loadGarments() {
        if (!this.garments || this.garments.length === 0) return;

        if (!this.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(this);
        }

        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        for (const g of this.garments) {
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

                const resp = await fetch(`/api/character/garment/fit/?${p}`);
                const data = await resp.json();
                if (data.error) { console.warn('Garment load error:', data.error); continue; }

                const vertBuf = base64ToFloat32(data.vertices);
                blenderToThreeCoords(vertBuf);
                const faceBuf = base64ToUint32(data.faces);

                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
                geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
                geo.computeVertexNormals();

                const color = g.color ? new THREE.Color(g.color[0], g.color[1], g.color[2])
                                      : new THREE.Color(0.3, 0.35, 0.5);
                const mat = new THREE.MeshStandardMaterial({
                    color, roughness: g.roughness ?? 0.8, metalness: g.metalness ?? 0.0,
                    side: THREE.DoubleSide,
                    polygonOffset: true,
                    polygonOffsetFactor: -1,
                    polygonOffsetUnit: -1,
                });

                const mesh = _skinifyMesh(geo, mat, this, data);
                const key = `gar_${g.id}`;
                this.clothMeshes[key] = mesh;
                this.group.add(mesh);

                this.garmentOrigPositions[key] = new Float32Array(vertBuf);
                _computeGarmentRegionWeights(this, key);

                this.garmentState[key] = {
                    offset: g.offset || 0,
                    stiffness: g.stiffness || 0.5,
                    minDist: g.minDist !== undefined ? g.minDist : 3,
                    crotchFloor: g.crotchFloor !== undefined ? g.crotchFloor : 0,
                    lift: g.lift !== undefined ? g.lift : 0,
                    crotchDepth: g.crotchDepth !== undefined ? g.crotchDepth : 0,
                    color: g.color || [color.r, color.g, color.b],
                    roughness: g.roughness ?? 0.8,
                    metalness: g.metalness ?? 0.0,
                    regionTop: 0, regionUpper: 0, regionMid: 0, regionLower: 0, regionBottom: 0,
                };
            } catch (e) {
                console.error('Failed to load garment:', g.id, e);
            }
        }
    }

    async _loadHair() {
        if (this.hairMesh) {
            this.group.remove(this.hairMesh);
            this.hairMesh.traverse(child => {
                if (child.isMesh) {
                    child.geometry.dispose();
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => m.dispose());
                }
            });
            this.hairMesh = null;
        }

        if (!this.hairStyle || !this.hairStyle.url) return;

        return new Promise((resolve) => {
            gltfLoader.load(this.hairStyle.url, (gltf) => {
                let hairGroup = gltf.scene;

                if (this.isSkinned && this.rigifySkeleton) {
                    hairGroup = _skinifyHairGroup(hairGroup, this);
                }

                this.hairMesh = hairGroup;

                if (this.hairStyle.color && state.hairColorData[this.hairStyle.color]) {
                    const rgb = state.hairColorData[this.hairStyle.color];
                    const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
                    this.hairMesh.traverse(child => {
                        if (child.isMesh && child.material) {
                            const mats = Array.isArray(child.material) ? child.material : [child.material];
                            mats.forEach(m => { m.color.copy(color); });
                        }
                    });
                }

                this.group.add(this.hairMesh);
                resolve();
            }, undefined, (err) => {
                console.warn('Failed to load hair:', err);
                resolve();
            });
        });
    }

    dispose() {
        if (this.bodyMesh) {
            this.bodyMesh.geometry.dispose();
            const mats = Array.isArray(this.bodyMesh.material) ? this.bodyMesh.material : [this.bodyMesh.material];
            mats.forEach(m => m.dispose());
        }
        for (const mesh of Object.values(this.clothMeshes)) {
            mesh.geometry.dispose();
            mesh.material.dispose();
        }
        if (this.hairMesh) {
            this.hairMesh.traverse(child => {
                if (child.isMesh) {
                    child.geometry.dispose();
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => m.dispose());
                }
            });
        }
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    toJSON() {
        if (this.generatedConfig) {
            return {
                id: this.id,
                presetName: this.presetName,
                presetKey: this.presetKey || null,
                bodyType: 'generated',
                generatedConfig: this.generatedConfig,
                transform: {
                    position: this.group.position.toArray(),
                    rotation: [this.group.rotation.x, this.group.rotation.y, this.group.rotation.z],
                    scale: this.group.scale.toArray()
                }
            };
        }

        const garments = (this.garments || []).map(g => {
            const key = `gar_${g.id}`;
            const st = this.garmentState[key];
            if (!st) return g;
            return {
                id: g.id,
                offset: st.offset,
                stiffness: st.stiffness,
                minDist: st.minDist,
                crotchFloor: st.crotchFloor,
                lift: st.lift,
                crotchDepth: st.crotchDepth,
                color: st.color,
                roughness: st.roughness,
                metalness: st.metalness,
            };
        });
        return {
            id: this.id,
            presetName: this.presetName,
            bodyType: this.bodyType,
            morphs: this.morphs,
            meta: this.meta,
            cloth: this.cloth,
            hair_style: this.hairStyle,
            garments,
            rigParams: this._rigParams || null,
            transform: {
                position: this.group.position.toArray(),
                rotation: [this.group.rotation.x, this.group.rotation.y, this.group.rotation.z],
                scale: this.group.scale.toArray()
            }
        };
    }

    static async fromJSON(data) {
        let presetPayload;
        if (data.bodyType === 'generated' && data.generatedConfig) {
            presetPayload = {
                ...data.generatedConfig,
                name: data.presetName,
                type: 'generated_model',
            };
        } else {
            presetPayload = {
                name: data.presetName,
                body_type: data.bodyType,
                morphs: data.morphs || {},
                meta: data.meta || {},
                cloth: data.cloth || [],
                hair_style: data.hair_style || null,
                garments: data.garments || [],
            };
        }

        const inst = new CharacterInstance(data.id, presetPayload);
        if (data.presetKey) inst.presetKey = data.presetKey;
        await inst.load();
        if (data.transform) {
            if (data.transform.position) inst.group.position.fromArray(data.transform.position);
            if (data.transform.rotation) {
                inst.group.rotation.set(data.transform.rotation[0], data.transform.rotation[1], data.transform.rotation[2]);
            }
            if (data.transform.scale) inst.group.scale.fromArray(data.transform.scale);
        }
        if (data.rigParams) inst._rigParams = data.rigParams;
        return inst;
    }
}

// =========================================================================
// Character management functions
// =========================================================================
export async function addCharacterFromPreset(presetName) {
    const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
    if (!resp.ok) throw new Error(`Preset not found: ${presetName}`);
    const presetData = await resp.json();

    const id = generateCharacterId();
    const inst = new CharacterInstance(id, presetData);

    const xOffset = state.characters.size * 0.8;
    inst.group.position.set(xOffset, 0, 0);

    inst.presetKey = presetName;
    await inst.load();
    state.characters.set(id, inst);
    state.scene.add(inst.group);

    fn.updateCharacterListUI();
    fn.updateVertexCount();
    fn.selectCharacter(id);
    markDirty();

    return inst;
}

export async function loadDefaultCharacter() {
    try {
        await addCharacterFromPreset(state.defaultPresetName);
    } catch (e) {
        console.warn('Failed to load default character:', e);
    }
}

export function selectCharacter(id) {
    if (state.selectedCharacterId && state.characters.has(state.selectedCharacterId)) {
        const prev = state.characters.get(state.selectedCharacterId);
        prev.selected = false;
        fn._setBodyEmissive(prev, state._ZERO_EMISSIVE);
    }

    state.selectedCharacterId = id;
    const inst = state.characters.get(id);
    if (!inst) {
        deselectCharacter();
        return;
    }

    inst.selected = true;
    if (!state._selectedSubMesh) {
        fn._setBodyEmissive(inst, state._SELECT_EMISSIVE);
    }
    state.transformControls.attach(inst.group);
    state.transformHelper.visible = true;
    state.transformControls.enabled = true;

    fn.updateCharacterListUI();
    fn.populateProperties(id);
}

export function deselectCharacter() {
    if (state.selectedCharacterId && state.characters.has(state.selectedCharacterId)) {
        const prev = state.characters.get(state.selectedCharacterId);
        prev.selected = false;
        fn._setBodyEmissive(prev, state._ZERO_EMISSIVE);
    }
    fn.clearSubMeshSelection();
    state.selectedCharacterId = null;
    state.transformControls.detach();
    state.transformHelper.visible = false;
    state.transformControls.enabled = false;
    fn.updateCharacterListUI();
    fn.clearProperties();
}

export function deleteCharacter(id) {
    const inst = state.characters.get(id);
    if (!inst) return;

    if (state.selectedCharacterId === id) {
        deselectCharacter();
    }

    if (state._mgCharacterId === id) {
        fn._clearBoneHighlightCache();
        state._mgCharacterId = null;
    }

    inst.dispose();
    state.characters.delete(id);
    fn.updateCharacterListUI();
    fn.updateVertexCount();
    markDirty();
}

export function focusCharacter(id) {
    const inst = state.characters.get(id);
    if (!inst) return;
    const box = new THREE.Box3().setFromObject(inst.group);
    const center = box.getCenter(new THREE.Vector3());
    state.controls.target.copy(center);
    state.controls.update();
}

export function updateCharacterListUI() {
    const list = document.getElementById('character-list');
    const countEl = document.getElementById('char-count');
    if (countEl) countEl.textContent = state.characters.size;

    list.innerHTML = '';
    state.characters.forEach((inst, id) => {
        const li = document.createElement('li');
        li.className = 'character-item' + (id === state.selectedCharacterId ? ' selected' : '');
        li.dataset.charId = id;

        const pos = inst.group.position;
        const posStr = `${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)}`;

        const icon = inst.generatedConfig ? 'fa-robot' : 'fa-user';
        li.innerHTML = `
            <span class="character-item-icon"><i class="fas ${icon}"></i></span>
            <div class="character-item-info">
                <div class="character-item-name">${escapeHtml(inst.presetName)}</div>
                <div class="character-item-detail">${escapeHtml(inst.bodyType)} &bull; (${posStr})</div>
            </div>
            <div class="character-item-actions">
                <button class="btn-focus" title="Fokussieren"><i class="fas fa-crosshairs"></i></button>
                <button class="btn-delete" title="L\u00f6schen"><i class="fas fa-trash"></i></button>
            </div>
        `;

        li.addEventListener('click', (e) => {
            if (e.target.closest('.character-item-actions')) return;
            selectCharacter(id);
        });

        li.querySelector('.btn-focus').addEventListener('click', (e) => {
            e.stopPropagation();
            selectCharacter(id);
            focusCharacter(id);
        });

        li.querySelector('.btn-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteCharacter(id);
        });

        list.appendChild(li);
    });

    if (state.currentPropsCharId && state.currentPropsCharId === state.selectedCharacterId) {
        fn.syncTransformInputs();
    }
}

export function updateVertexCount() {
    let total = 0;
    state.characters.forEach(inst => {
        if (inst.bodyMesh) total += inst.bodyMesh.geometry.attributes.position.count;
        for (const m of Object.values(inst.clothMeshes)) {
            if (m && m.geometry) total += m.geometry.attributes.position.count;
        }
        if (inst.hairMesh) {
            inst.hairMesh.traverse(child => {
                if (child.isMesh && child.geometry) total += child.geometry.attributes.position.count;
            });
        }
    });
    document.getElementById('vertex-count').textContent = total.toLocaleString();
}

export function clearAllCharacters() {
    deselectCharacter();
    state.characters.forEach(inst => inst.dispose());
    state.characters.clear();
    updateCharacterListUI();
    updateVertexCount();
}

export function setTransformMode(mode) {
    state.currentTransformMode = mode;
    state.transformControls.setMode(mode);
    document.querySelectorAll('.transform-btn[data-mode]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
}

// Register
fn.CharacterInstance = CharacterInstance;
fn.addCharacterFromPreset = addCharacterFromPreset;
fn.loadDefaultCharacter = loadDefaultCharacter;
fn.selectCharacter = selectCharacter;
fn.deselectCharacter = deselectCharacter;
fn.deleteCharacter = deleteCharacter;
fn.focusCharacter = focusCharacter;
fn.updateCharacterListUI = updateCharacterListUI;
fn.updateVertexCount = updateVertexCount;
fn.clearAllCharacters = clearAllCharacters;
fn.setTransformMode = setTransformMode;
