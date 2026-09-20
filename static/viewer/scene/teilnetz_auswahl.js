import { fn } from '../gemeinsam/registrierung.js';
import { markDirty } from './undo.js';
import { state } from './state.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { GarmentcodeAblage } from './garmentcode_ablage.js';
import { Stueckereignis } from '../gemeinsam/stueckereignis.js';
import { Stueckmarkierung } from './stueckmarkierung.js';
/**
 * Teilnetze eines Charakters auswaehlen und entfernen.
 *
 * Aus interaction.js herausgeloest (Umbau 16.08.2026).
 */


// =========================================================================
// Sub-mesh target helpers
// =========================================================================
export function getSelectableSubMeshes(charId) {
    const inst = state.characters.get(charId);
    if (!inst) return [];
    const targets = [];
    for (const [key, mesh] of Object.entries(inst.clothMeshes)) {
        if (mesh) {
            // `beschriftung` schlaegt den Schluessel: Ein GarmentCode-Stueck
            // hiesse sonst `gc_kleid` statt „kleid (GarmentCode)".
            targets.push({ type: 'cloth', key,
                           label: mesh.userData?.beschriftung || key,
                           meshObj: mesh, charId });
        }
    }
    if (inst.hairMesh) {
        const hName = inst.hairStyle?.name || inst.hairStyle?.url?.split('/').pop() || 'Hair';
        targets.push({ type: 'hair', key: 'hair', label: `Hair (${hName})`, meshObj: inst.hairMesh, charId });
    }
    return targets;
}

export function getAllSubMeshTargets() {
    const targets = [];
    state.characters.forEach((inst, id) => { targets.push(...getSelectableSubMeshes(id)); });
    return targets;
}

export function _findSubMeshForObject(obj, targets) {
    // Das Simulationsnetz des Stoffschwungs steht fuer sein Stueck (`userData.stueckVon`).
    const ziel = obj?.userData?.stueckVon || obj;
    for (const t of targets) {
        let cur = ziel;
        while (cur) {
            if (cur === t.meshObj) return t;
            cur = cur.parent;
        }
    }
    return null;
}

export function _sameSubMesh(a, b) {
    if (!a || !b) return false;
    return a.type === b.type && a.key === b.key && a.charId === b.charId;
}

export function _getMeshesOf(root) {
    const meshes = [];
    if (root.isMesh) { meshes.push(root); } else { root.traverse(child => { if (child.isMesh) meshes.push(child); }); }
    return meshes;
}

export function _setSubMeshEmissive(target, color) {
    if (!target || !target.meshObj) return;
    for (const m of _getMeshesOf(target.meshObj)) {
        if (m.material) {
            const mats = Array.isArray(m.material) ? m.material : [m.material];
            for (const mat of mats) {
                if (mat.emissive) { mat.emissive.copy(color); continue; }
                // Stranghaar (`Genesis9strang`): MeshBasicMaterial ohne `emissive`. Die
                // Grundfarbe multipliziert die Strähnenfarben — 1 + 20·Leuchtfarbe hebt
                // sie bläulich an (Auswahl: Blau ×1,9), Null → weiß = unverändert.
                // Sonst sähe man einer gewählten Viola nichts an (20.09.2026).
                if (mat.wireframe && mat.vertexColors) {
                    mat.color.setRGB(1 + 20 * color.r, 1 + 20 * color.g, 1 + 20 * color.b);
                }
            }
        }
    }
}

export function _setBodyEmissive(inst, color) {
    if (!inst || !inst.bodyMesh) return;
    // Eine UMA-Figur besteht aus mehreren Netzen (Haut je Kachel, Haar, Augen);
    // hervorgehoben wird die ganze Figur, nicht nur eine Kachel.
    const netze = inst.netze && inst.netze.length ? inst.netze : [inst.bodyMesh];
    for (const netz of netze) {
        const mats = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of mats) { if (mat && mat.emissive) mat.emissive.copy(color); }
    }
}

export function clearSubMeshSelection() {
    if (state._selectedSubMesh) {
        _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = null;
    }
    if (state._hoveredSubMesh) {
        _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE);
        state._hoveredSubMesh = null;
    }
    fn._updatePropContext();
    const tooltip = document.getElementById('mesh-tooltip');
    if (tooltip) tooltip.style.display = 'none';
}

/**
 * Den Reiter aufschlagen, der zu dem angeklickten Teilnetz gehört, und
 * dort SEINE Zeile markieren (`Stueckmarkierung`, Edgar 20.09.2026: „soll in
 * der Toolbar genau das ausgewählt sein"). Wird ein Teilnetz ABgewählt
 * (`ziel === null`), bleibt es beim Vorgabereiter — so war es auch vorher.
 */
const markierung = new Stueckmarkierung(state);

function _reiterZeigen(ziel) {
    markierung.zeigen(ziel);
}

export function _doSubMeshClick(hitTarget) {
    const inst = state.characters.get(hitTarget.charId);
    if (_sameSubMesh(state._selectedSubMesh, hitTarget)) {
        _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = null;
        if (inst) _setBodyEmissive(inst, state._SELECT_EMISSIVE);
    } else {
        if (state._selectedSubMesh) _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = hitTarget;
        _setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
        if (inst) _setBodyEmissive(inst, state._ZERO_EMISSIVE);
    }
    fn._syncGarmentSliders();
    _reiterZeigen(state._selectedSubMesh);
    fn._updatePropContext();
    if (state._selectedSubMesh && state._selectedSubMesh.type === 'cloth') {
        fn._syncPropGarmentControls();
    } else if (state._selectedSubMesh && state._selectedSubMesh.type === 'hair') {
        fn._syncPropHairControls();
    }
    if (inst) fn.updateEquippedList(inst);
}

export function _removeSubMesh(target) {
    if (!target) return;
    const inst = state.characters.get(target.charId);
    if (!inst) return;

    switch (target.type) {
        case 'cloth': {
            if (String(target.key).startsWith('gc_')) {
                // GarmentCode ZUERST — auch an einer Genesis-9-Figur (Edgar, 20.09.2026,
                // mit Bild: „nach löschen ist das Modell kaputt", ein schwarzes Band
                // quer über der Brust). Der Daz-Weg darunter (`inst.ausziehen`) nahm
                // das Netz zwar weg, meldete aber kein `Stueckereignis` mehr — die
                // Hautverdeckung des gelöschten Stücks blieb stehen (ausgeblendete
                // Dreiecke, versenkte Randhaut), und die Ablage wusste nichts davon:
                // beim nächsten Laden wäre das Stück wieder da gewesen.
                if (Netzentsorgung.ausAblage(inst.group, inst.clothMeshes, target.key)) {
                    GarmentcodeAblage.vergessen(inst, target.key);
                    Stueckereignis.melden(inst, target.key.slice(3), false);
                }
            } else if (typeof inst.ausziehen === 'function' && inst.kleidung) {
                // Genesis 9: ein Stueck sind mehrere Teile (`kennung/n`), und die
                // Figur merkt sich das Getragene in `kleidung` — nur das Netz zu
                // entfernen brachte das Stueck beim naechsten Neubau zurueck
                // (Edgar, 18.09.2026: „wenn ich auf Ctrl-Alt-H klicke erscheint
                // das Modell wieder mit den Kleidern").
                inst.ausziehen(String(target.key).split('/')[0]);
            } else if (Netzentsorgung.ausAblage(inst.group, inst.clothMeshes,
                                                target.key)) {
                if (target.key.startsWith('gar_')) {
                    const garId = target.key.slice(4);
                    inst.garments = (inst.garments || []).filter(g => g.id !== garId);
                    delete inst.garmentState[target.key];
                    delete inst.garmentOrigPositions[target.key];
                    delete inst.garmentRegionWeights[target.key];
                } else {
                    inst.cloth = (inst.cloth || []).filter(c => {
                        const m = c.method || 'template';
                        let ck;
                        if (m === 'builder') ck = `bld_${c.region || 'TOP'}`;
                        else if (m === 'primitive') ck = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                        else ck = `tpl_${c.template || 'TPL_TSHIRT'}`;
                        return ck !== target.key;
                    });
                }
            }
            break;
        }
        case 'hair': {
            if (inst.hairMesh) {
                Netzentsorgung.entfernen(inst.group, inst.hairMesh);
                inst.hairMesh = null;
                inst.hairStyle = null;
            }
            break;
        }
    }

    if (_sameSubMesh(state._selectedSubMesh, target)) state._selectedSubMesh = null;
    if (_sameSubMesh(state._hoveredSubMesh, target)) state._hoveredSubMesh = null;
    fn.updateEquippedList(inst);
    fn.updateVertexCount();
    markDirty();
}
