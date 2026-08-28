/**
 * Scene Editor -- CharacterInstance class + character management.
 */
import { THREE, BODY_MATERIALS } from './state.js';
import './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, _getBodyTop } from './utils.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import './skeleton.js';
import './undo.js';
import './garments.js';
import './modellgenerator/zustand.js';
import { Charakterzubehoer } from './charakter_zubehoer.js';
import { Charakterkoerper } from './charakter_koerper.js';
import { addCharacterFromPreset, clearAllCharacters, deleteCharacter, deselectCharacter, focusCharacter, loadDefaultCharacter, selectCharacter, setTransformMode, updateCharacterListUI, updateVertexCount } from './charakterliste.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';

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
        this.mhProxies = {};
        this._pendingMHProxies = Array.isArray(presetData.mh_proxy) ? presetData.mh_proxy : [];
    }

    async load() {
        if (this.generatedConfig) {
            return Charakterkoerper.ausKonfiguration(this);
        }

        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const data = await Serverabruf.json(`/api/character/mesh/?${params}`);
        if (data.error) throw new Error(data.error);

        // Puffer, Normalen, Materialgruppen: siehe `Koerpernetz`. Diese dreißig
        // Zeilen standen fünfmal im Projekt (Befund `doppelcode`, 17.08.2026).
        this.bodyMesh = Koerpernetz.netz(data, THREE);
        const materials = Array.isArray(this.bodyMesh.material)
            ? this.bodyMesh.material : [this.bodyMesh.material];

        Charakterkoerper.hautfarbe(this, materials);
        this.group.add(this.bodyMesh);
        this.initialBodyTop = _getBodyTop(this);

        await Charakterzubehoer.stoff(this);
        await Charakterzubehoer.haare(this);
        await Charakterzubehoer.kleidung(this);
        await Charakterzubehoer.proxys(this);

        return this;
    }








    dispose() {
        Netzentsorgung.netz(this.bodyMesh);
        // Ueber `Netzentsorgung`, nicht `mesh.material.dispose()`: Ein Netz
        // mit MEHREREN Materialien haette hier eine TypeError geworfen
        // (`material` ist dann ein Array). Bisher kam das nicht vor — der
        // naechste Stoff mit Materialgruppen haette es ausgeloest.
        for (const netz of Object.values(this.clothMeshes)) {
            Netzentsorgung.netz(netz);
        }
        Netzentsorgung.baum(this.hairMesh);
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
            presetKey: this.presetKey || null,
            bodyType: this.bodyType,
            morphs: this.morphs,
            meta: this.meta,
            cloth: this.cloth,
            hair_style: this.hairStyle,
            garments,
            mh_proxy: Object.values(this.mhProxies || {}),
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
                mh_proxy: data.mh_proxy || [],
            };
        }

        const inst = new CharacterInstance(data.id, presetPayload);
        if (data.presetKey) {
            inst.presetKey = data.presetKey;
            inst.presetName = data.presetKey;
        }
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
