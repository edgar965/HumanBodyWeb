/**
 * Scene Editor -- Model Generator UI.
 * Extracted from scene_config.js lines 6994-7709.
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { _selectedInst, generateCharacterId, getCSRFToken, _bindSlider } from './utils.js';
import {
    classifyBones, getDefaultModelConfig, generateModelMesh,
    classifyRigBones, getDefaultRigConfig, generateRigBoneMesh,
} from './state.js';

async function initModelGenerator() {
    if (!state.rigifySkeletonData || !state.skinWeightData) {
        console.warn('Model Generator: skeleton data not loaded yet');
        return;
    }

    if (!state._mgConfig) {
        // Check if a loaded character already has a generated config (e.g. Rig3)
        const sel = _selectedInst();
        const genInst = (sel && sel.generatedConfig) ? sel
            : [...state.characters.values()].find(c => c.generatedConfig) || null;
        if (genInst && genInst.generatedConfig) {
            state._mgConfig = JSON.parse(JSON.stringify(genInst.generatedConfig));
            state._mgSkeletonType = genInst.generatedConfig.skeleton_type || 'rig';
            state._mgCharacterId = genInst.id;
            // Ensure rig bones data is loaded for rig-type models
            if (state._mgSkeletonType === 'rig' && !state._mgRigBonesData) {
                try {
                    const resp = await fetch('/api/character/rig/');
                    if (resp.ok) state._mgRigBonesData = await resp.json();
                } catch (e) { /* ignore */ }
            }
            console.log('[MG] Synced config from loaded character:', genInst.presetName);
        } else if (state._mgSkeletonType === 'rig') {
            // Load rig bones data for default rig mode
            if (!state._mgRigBonesData) {
                try {
                    const resp = await fetch('/api/character/rig/');
                    if (resp.ok) state._mgRigBonesData = await resp.json();
                } catch (e) {
                    console.warn('Failed to load rig bones:', e);
                }
            }
            if (state._mgRigBonesData && state._mgRigBonesData.bones && state._mgRigBonesData.bones.length > 0) {
                state._mgConfig = getDefaultRigConfig(state._mgRigBonesData);
            } else {
                // Fallback to DEF if rig data unavailable
                state._mgSkeletonType = 'def';
                state._mgConfig = getDefaultModelConfig(state.rigifySkeletonData, state.skinWeightData);
            }
        } else {
            state._mgConfig = getDefaultModelConfig(state.rigifySkeletonData, state.skinWeightData);
        }
    }

    if (!state._mgInitialized) {
        _bindModelGeneratorUI();
        state._mgInitialized = true;
    }

    // Sync skeleton type dropdown
    const skelSelect = document.getElementById('mg-skeleton-type');
    if (skelSelect) skelSelect.value = state._mgSkeletonType;

    _populateBoneTree();
    _syncMGGlobalUI();

    // Expand Modell tab panel sections
    document.querySelectorAll('#tab-modell .panel-section').forEach(p => {
        p.classList.remove('collapsed');
    });
}

function _bindModelGeneratorUI() {
    // Skeleton type selector
    const skelSelect = document.getElementById('mg-skeleton-type');
    if (skelSelect) skelSelect.addEventListener('change', async () => {
        const newType = skelSelect.value;
        if (newType === state._mgSkeletonType) return;
        state._mgSkeletonType = newType;

        if (newType === 'rig') {
            // Fetch rig bones data if not cached
            if (!state._mgRigBonesData) {
                try {
                    const resp = await fetch('/api/character/rig/');
                    if (resp.ok) state._mgRigBonesData = await resp.json();
                } catch (e) {
                    console.warn('Failed to load rig bones:', e);
                }
            }
            if (state._mgRigBonesData && state._mgRigBonesData.bones && state._mgRigBonesData.bones.length > 0) {
                state._mgConfig = getDefaultRigConfig(state._mgRigBonesData);
            } else {
                console.warn('Rig bones data not available');
                state._mgSkeletonType = 'def';
                skelSelect.value = 'def';
                return;
            }
        } else {
            state._mgConfig = getDefaultModelConfig(state.rigifySkeletonData, state.skinWeightData);
        }

        state._mgSelectedBone = null;
        fn._clearBoneHighlightCache();
        const propsSection = document.getElementById('mg-bone-props-section');
        if (propsSection) propsSection.style.display = 'none';

        _populateBoneTree();
        _syncMGGlobalUI();
    });

    // Global controls
    const nameInput = document.getElementById('mg-model-name');
    if (nameInput) nameInput.addEventListener('input', () => { state._mgConfig.name = nameInput.value; });

    const colorInput = document.getElementById('mg-default-color');
    if (colorInput) colorInput.addEventListener('input', () => {
        state._mgConfig.default_color = colorInput.value;
    });

    const radiusSlider = document.getElementById('mg-default-radius');
    const radiusVal = document.getElementById('mg-default-radius-val');
    if (radiusSlider) radiusSlider.addEventListener('input', () => {
        const v = parseFloat(radiusSlider.value);
        state._mgConfig.default_radius = v;
        if (radiusVal) radiusVal.textContent = v.toFixed(3);
    });

    const segSlider = document.getElementById('mg-segments');
    const segVal = document.getElementById('mg-segments-val');
    if (segSlider) segSlider.addEventListener('input', () => {
        const v = parseInt(segSlider.value);
        state._mgConfig.segments = v;
        if (segVal) segVal.textContent = v;
    });

    // Bone properties
    const boneShape = document.getElementById('mg-bone-shape');
    if (boneShape) boneShape.addEventListener('change', () => {
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].shape = boneShape.value;
        const overlapRow = document.getElementById('mg-overlap-row');
        if (overlapRow) overlapRow.style.display = boneShape.value === 'double_oval' ? '' : 'none';
        const tutuParams = document.getElementById('mg-tutu-params');
        if (tutuParams) tutuParams.style.display = boneShape.value === 'tutu' ? '' : 'none';
        const spiralParams = document.getElementById('mg-spiral-tutu-params');
        if (spiralParams) spiralParams.style.display = boneShape.value === 'spiral_tutu' ? '' : 'none';
        const helixParams = document.getElementById('mg-helix-ribbon-params');
        if (helixParams) helixParams.style.display = boneShape.value === 'helix_ribbon' ? '' : 'none';
        const skirtParams = document.getElementById('mg-skirt-params');
        if (skirtParams) skirtParams.style.display = boneShape.value === 'skirt' ? '' : 'none';
        _mgAutoRegenerate();
    });

    // Tutu parameter sliders
    function _tutuSlider(id, valId, prop, fmt) {
        const el = document.getElementById(id);
        const valEl = document.getElementById(valId);
        if (!el) return;
        el.addEventListener('input', () => {
            const v = parseFloat(el.value);
            if (valEl) valEl.textContent = v.toFixed(fmt || 3);
            if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
            state._mgConfig.bone_parts[state._mgSelectedBone][prop] = v;
            _mgAutoRegenerate();
        });
    }
    _tutuSlider('mg-tutu-thickness', 'mg-tutu-thickness-val', 'tutuThickness', 3);
    _tutuSlider('mg-tutu-droop', 'mg-tutu-droop-val', 'tutuDroop', 3);
    _tutuSlider('mg-tutu-droop-start', 'mg-tutu-droop-start-val', 'tutuDroopStart', 2);
    _tutuSlider('mg-tutu-offset', 'mg-tutu-offset-val', 'tutuOffset', 3);

    // Spiral-Tutu sliders
    _tutuSlider('mg-spiral-winds', 'mg-spiral-winds-val', 'spiralWinds', 0);
    _tutuSlider('mg-spiral-start-r', 'mg-spiral-start-r-val', 'spiralStartR', 3);
    _tutuSlider('mg-spiral-end-r', 'mg-spiral-end-r-val', 'spiralEndR', 3);
    _tutuSlider('mg-spiral-pos-top', 'mg-spiral-pos-top-val', 'spiralPosTop', 3);
    _tutuSlider('mg-spiral-pos-bottom', 'mg-spiral-pos-bottom-val', 'spiralPosBottom', 3);
    _tutuSlider('mg-spiral-thickness', 'mg-spiral-thickness-val', 'tutuThickness', 3);
    _tutuSlider('mg-spiral-droop', 'mg-spiral-droop-val', 'tutuDroop', 3);
    const spiralSkirtCb = document.getElementById('mg-spiral-skirt');
    if (spiralSkirtCb) spiralSkirtCb.addEventListener('change', () => {
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].spiralSkirt = spiralSkirtCb.checked;
        _mgAutoRegenerate();
    });

    // Helix ribbon sliders
    _tutuSlider('mg-helix-winds', 'mg-helix-winds-val', 'spiralWinds', 1);
    _tutuSlider('mg-helix-start-r', 'mg-helix-start-r-val', 'spiralStartR', 3);
    _tutuSlider('mg-helix-end-r', 'mg-helix-end-r-val', 'spiralEndR', 3);
    _tutuSlider('mg-helix-ribbon-w', 'mg-helix-ribbon-w-val', 'ribbonWidth', 3);
    _tutuSlider('mg-helix-pos-top', 'mg-helix-pos-top-val', 'spiralPosTop', 3);
    _tutuSlider('mg-helix-pos-bottom', 'mg-helix-pos-bottom-val', 'spiralPosBottom', 3);
    _tutuSlider('mg-helix-thickness', 'mg-helix-thickness-val', 'tutuThickness', 3);
    _tutuSlider('mg-helix-droop', 'mg-helix-droop-val', 'tutuDroop', 3);
    const helixSkirtCb = document.getElementById('mg-helix-skirt');
    if (helixSkirtCb) helixSkirtCb.addEventListener('change', () => {
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].spiralSkirt = helixSkirtCb.checked;
        _mgAutoRegenerate();
    });

    // Skirt sliders
    _tutuSlider('mg-skirt-radius-top', 'mg-skirt-radius-top-val', 'skirtRadiusTop', 3);
    _tutuSlider('mg-skirt-radius-bottom', 'mg-skirt-radius-bottom-val', 'skirtRadiusBottom', 3);
    _tutuSlider('mg-skirt-pos-top', 'mg-skirt-pos-top-val', 'skirtPosTop', 3);
    _tutuSlider('mg-skirt-pos-bottom', 'mg-skirt-pos-bottom-val', 'skirtPosBottom', 3);
    _tutuSlider('mg-skirt-thickness', 'mg-skirt-thickness-val', 'skirtThickness', 3);

    const boneRadius = document.getElementById('mg-bone-radius');
    const boneRadiusVal = document.getElementById('mg-bone-radius-val');
    if (boneRadius) boneRadius.addEventListener('input', () => {
        const v = parseFloat(boneRadius.value);
        if (boneRadiusVal) boneRadiusVal.textContent = v.toFixed(3);
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].radius = v;
        _updateBoneTreeItem(state._mgSelectedBone);
        _mgAutoRegenerate();
    });

    const boneColor = document.getElementById('mg-bone-color');
    if (boneColor) boneColor.addEventListener('input', () => {
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].color = boneColor.value;
        _updateBoneTreeItem(state._mgSelectedBone);
        _mgAutoRegenerate();
    });

    // Overlap slider (double_oval)
    const boneOverlap = document.getElementById('mg-bone-overlap');
    const boneOverlapVal = document.getElementById('mg-bone-overlap-val');
    if (boneOverlap) boneOverlap.addEventListener('input', () => {
        const v = parseFloat(boneOverlap.value);
        if (boneOverlapVal) boneOverlapVal.textContent = v.toFixed(2);
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].overlap = v;
        _mgAutoRegenerate();
    });

    // Head/Tail offset sliders
    for (const end of ['head', 'tail']) {
        for (const axis of ['x', 'y', 'z']) {
            const slider = document.getElementById(`mg-${end}-off-${axis}`);
            const valSpan = document.getElementById(`mg-${end}-off-${axis}-val`);
            if (!slider) continue;
            slider.addEventListener('input', () => {
                const v = parseFloat(slider.value);
                if (valSpan) valSpan.textContent = v.toFixed(3);
                if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
                const part = state._mgConfig.bone_parts[state._mgSelectedBone];
                const key = end + 'Offset'; // headOffset or tailOffset
                if (!part[key]) part[key] = { x: 0, y: 0, z: 0 };
                part[key][axis] = v;
                _mgAutoRegenerate();
            });
        }
    }

    // Axial scale slider
    const axialSlider = document.getElementById('mg-axial-scale');
    const axialVal = document.getElementById('mg-axial-scale-val');
    if (axialSlider) axialSlider.addEventListener('input', () => {
        const v = parseFloat(axialSlider.value);
        if (axialVal) axialVal.textContent = v.toFixed(2);
        if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
        state._mgConfig.bone_parts[state._mgSelectedBone].axialScale = v;
        _mgAutoRegenerate();
    });

    // Shape rotation sliders (degrees)
    for (const axis of ['x', 'y', 'z']) {
        const slider = document.getElementById(`mg-shape-rot-${axis}`);
        const valSpan = document.getElementById(`mg-shape-rot-${axis}-val`);
        if (!slider) continue;
        slider.addEventListener('input', () => {
            const v = parseFloat(slider.value);
            if (valSpan) valSpan.textContent = v;
            if (!state._mgSelectedBone || !state._mgConfig.bone_parts[state._mgSelectedBone]) return;
            const part = state._mgConfig.bone_parts[state._mgSelectedBone];
            if (!part.shapeRotation) part.shapeRotation = { x: 0, y: 0, z: 0 };
            part.shapeRotation[axis] = v;
            _mgAutoRegenerate();
        });
    }

    // Action buttons
    const genBtn = document.getElementById('mg-generate');
    if (genBtn) genBtn.addEventListener('click', () => {
        _mgGenerateCharacter();
    });

    const saveServerBtn = document.getElementById('mg-save-server');
    if (saveServerBtn) saveServerBtn.addEventListener('click', () => {
        _mgSaveModelToServer();
    });
}

function _syncMGGlobalUI() {
    if (!state._mgConfig) return;
    const nameInput = document.getElementById('mg-model-name');
    if (nameInput) nameInput.value = state._mgConfig.name || 'Neues Modell';
    const colorInput = document.getElementById('mg-default-color');
    if (colorInput) colorInput.value = state._mgConfig.default_color || '#4488cc';
    const radiusSlider = document.getElementById('mg-default-radius');
    const radiusVal = document.getElementById('mg-default-radius-val');
    if (radiusSlider) radiusSlider.value = state._mgConfig.default_radius || 0.03;
    if (radiusVal) radiusVal.textContent = (state._mgConfig.default_radius || 0.03).toFixed(3);
    const segSlider = document.getElementById('mg-segments');
    const segVal = document.getElementById('mg-segments-val');
    if (segSlider) segSlider.value = state._mgConfig.segments || 8;
    if (segVal) segVal.textContent = state._mgConfig.segments || 8;
}

function _populateBoneTree() {
    const container = document.getElementById('mg-bone-tree');
    if (!container || !state._mgConfig) return;

    let categories;
    if (state._mgSkeletonType === 'rig' && state._mgRigBonesData) {
        const classified = classifyRigBones(state._mgRigBonesData);
        categories = [
            { label: `DEF (${classified.def.length})`, bones: classified.def, collapsed: false },
            { label: `MCH (${classified.mch.length})`, bones: classified.mch, collapsed: true },
            { label: `ORG (${classified.org.length})`, bones: classified.org, collapsed: true },
            { label: `Control (${classified.control.length})`, bones: classified.control, collapsed: true },
        ];
    } else {
        const classified = classifyBones(state.rigifySkeletonData);
        categories = [
            { label: 'K\u00f6rper', bones: classified.body, collapsed: false },
            { label: 'Finger', bones: classified.finger, collapsed: true },
            { label: 'Gesicht', bones: classified.face, collapsed: true },
        ];
    }

    container.innerHTML = '';

    for (const cat of categories) {
        if (cat.bones.length === 0) continue;
        const catDiv = document.createElement('div');
        catDiv.className = 'mg-category';

        const header = document.createElement('div');
        header.className = 'mg-category-header' + (cat.collapsed ? ' collapsed' : '');
        header.innerHTML = `<span class="mg-chevron">&#9660;</span> ${cat.label} (${cat.bones.length})`;
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'mg-category-body' + (cat.collapsed ? ' hidden' : '');

        for (const boneName of cat.bones) {
            const part = state._mgConfig.bone_parts[boneName];
            if (!part) continue;

            const item = document.createElement('div');
            item.className = 'mg-bone-item';
            item.dataset.bone = boneName;

            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.checked = part.visible;
            cb.addEventListener('change', (e) => {
                e.stopPropagation();
                part.visible = cb.checked;
                _mgAutoRegenerate();
            });

            const label = document.createElement('span');
            label.className = 'mg-bone-label';
            label.textContent = boneName.replace(/^(DEF|MCH|ORG)-/, '');
            label.title = boneName;

            const swatch = document.createElement('span');
            swatch.className = 'mg-bone-swatch';
            swatch.style.backgroundColor = part.color || state._mgConfig.default_color;

            item.appendChild(cb);
            item.appendChild(label);
            item.appendChild(swatch);

            item.addEventListener('click', (e) => {
                if (e.target === cb) return; // checkbox handles itself
                _mgSelectBone(boneName);
            });

            body.appendChild(item);
        }

        catDiv.appendChild(body);
        container.appendChild(catDiv);

        // Toggle collapse
        header.addEventListener('click', () => {
            header.classList.toggle('collapsed');
            body.classList.toggle('hidden');
        });
    }
}

function _mgSelectBone(boneName) {
    state._mgSelectedBone = boneName;
    // Highlight in tree
    document.querySelectorAll('.mg-bone-item').forEach(el => {
        el.classList.toggle('selected', el.dataset.bone === boneName);
    });
    // Show bone properties
    const propsSection = document.getElementById('mg-bone-props-section');
    if (propsSection) propsSection.style.display = '';
    const nameEl = document.getElementById('mg-bone-name');
    if (nameEl) nameEl.textContent = boneName;

    const part = state._mgConfig.bone_parts[boneName];
    if (!part) return;

    const shapeSelect = document.getElementById('mg-bone-shape');
    if (shapeSelect) shapeSelect.value = part.shape || 'cylinder';
    const radiusSlider = document.getElementById('mg-bone-radius');
    const radiusVal = document.getElementById('mg-bone-radius-val');
    if (radiusSlider) radiusSlider.value = part.radius || 0.03;
    if (radiusVal) radiusVal.textContent = (part.radius || 0.03).toFixed(3);
    const colorInput = document.getElementById('mg-bone-color');
    if (colorInput) colorInput.value = part.color || state._mgConfig.default_color;

    // Overlap slider -- show only for double_oval
    const overlapRow = document.getElementById('mg-overlap-row');
    if (overlapRow) overlapRow.style.display = (part.shape === 'double_oval') ? '' : 'none';
    const overlapSlider = document.getElementById('mg-bone-overlap');
    const overlapVal = document.getElementById('mg-bone-overlap-val');
    if (overlapSlider) overlapSlider.value = part.overlap ?? 0.5;
    if (overlapVal) overlapVal.textContent = (part.overlap ?? 0.5).toFixed(2);

    // Shape-specific params -- show/hide based on shape
    const tutuParams = document.getElementById('mg-tutu-params');
    if (tutuParams) tutuParams.style.display = (part.shape === 'tutu') ? '' : 'none';
    const spiralParams = document.getElementById('mg-spiral-tutu-params');
    if (spiralParams) spiralParams.style.display = (part.shape === 'spiral_tutu') ? '' : 'none';
    const spiralSkirtCb = document.getElementById('mg-spiral-skirt');
    if (spiralSkirtCb) spiralSkirtCb.checked = !!part.spiralSkirt;
    const helixParams = document.getElementById('mg-helix-ribbon-params');
    if (helixParams) helixParams.style.display = (part.shape === 'helix_ribbon') ? '' : 'none';
    const helixSkirtCb = document.getElementById('mg-helix-skirt');
    if (helixSkirtCb) helixSkirtCb.checked = !!part.spiralSkirt;
    const skirtParams = document.getElementById('mg-skirt-params');
    if (skirtParams) skirtParams.style.display = (part.shape === 'skirt') ? '' : 'none';

    const shapeSliders = [
        // Tutu
        ['mg-tutu-thickness', 'mg-tutu-thickness-val', 'tutuThickness', 0.01, 3],
        ['mg-tutu-droop', 'mg-tutu-droop-val', 'tutuDroop', 0.03, 3],
        ['mg-tutu-droop-start', 'mg-tutu-droop-start-val', 'tutuDroopStart', 0.7, 2],
        ['mg-tutu-offset', 'mg-tutu-offset-val', 'tutuOffset', 0, 3],
        // Spiral-Tutu
        ['mg-spiral-winds', 'mg-spiral-winds-val', 'spiralWinds', 3, 0],
        ['mg-spiral-start-r', 'mg-spiral-start-r-val', 'spiralStartR', 0.15, 3],
        ['mg-spiral-end-r', 'mg-spiral-end-r-val', 'spiralEndR', 0.35, 3],
        ['mg-spiral-pos-top', 'mg-spiral-pos-top-val', 'spiralPosTop', 0.05, 3],
        ['mg-spiral-pos-bottom', 'mg-spiral-pos-bottom-val', 'spiralPosBottom', -0.15, 3],
        ['mg-spiral-thickness', 'mg-spiral-thickness-val', 'tutuThickness', 0.008, 3],
        ['mg-spiral-droop', 'mg-spiral-droop-val', 'tutuDroop', 0.02, 3],
        // Helix ribbon
        ['mg-helix-winds', 'mg-helix-winds-val', 'spiralWinds', 3, 1],
        ['mg-helix-start-r', 'mg-helix-start-r-val', 'spiralStartR', 0.15, 3],
        ['mg-helix-end-r', 'mg-helix-end-r-val', 'spiralEndR', 0.35, 3],
        ['mg-helix-ribbon-w', 'mg-helix-ribbon-w-val', 'ribbonWidth', 0.04, 3],
        ['mg-helix-pos-top', 'mg-helix-pos-top-val', 'spiralPosTop', 0.05, 3],
        ['mg-helix-pos-bottom', 'mg-helix-pos-bottom-val', 'spiralPosBottom', -0.15, 3],
        ['mg-helix-thickness', 'mg-helix-thickness-val', 'tutuThickness', 0.005, 3],
        ['mg-helix-droop', 'mg-helix-droop-val', 'tutuDroop', 0.015, 3],
        // Skirt
        ['mg-skirt-radius-top', 'mg-skirt-radius-top-val', 'skirtRadiusTop', 0.08, 3],
        ['mg-skirt-radius-bottom', 'mg-skirt-radius-bottom-val', 'skirtRadiusBottom', 0.25, 3],
        ['mg-skirt-pos-top', 'mg-skirt-pos-top-val', 'skirtPosTop', 0.02, 3],
        ['mg-skirt-pos-bottom', 'mg-skirt-pos-bottom-val', 'skirtPosBottom', -0.15, 3],
        ['mg-skirt-thickness', 'mg-skirt-thickness-val', 'skirtThickness', 0.005, 3],
    ];
    for (const [slId, valId, prop, def, dec] of shapeSliders) {
        const sl = document.getElementById(slId);
        const sp = document.getElementById(valId);
        const v = part[prop] ?? def;
        if (sl) sl.value = v;
        if (sp) sp.textContent = dec === 0 ? String(Math.round(v)) : v.toFixed(dec);
    }

    // Head/Tail offset sliders
    for (const end of ['head', 'tail']) {
        const off = part[end + 'Offset'] || { x: 0, y: 0, z: 0 };
        for (const axis of ['x', 'y', 'z']) {
            const sl = document.getElementById(`mg-${end}-off-${axis}`);
            const sp = document.getElementById(`mg-${end}-off-${axis}-val`);
            if (sl) sl.value = off[axis] || 0;
            if (sp) sp.textContent = (off[axis] || 0).toFixed(3);
        }
    }

    // Axial scale slider
    const axSl = document.getElementById('mg-axial-scale');
    const axVal = document.getElementById('mg-axial-scale-val');
    if (axSl) axSl.value = part.axialScale ?? 1.0;
    if (axVal) axVal.textContent = (part.axialScale ?? 1.0).toFixed(2);

    // Shape rotation sliders
    const rot = part.shapeRotation || { x: 0, y: 0, z: 0 };
    for (const axis of ['x', 'y', 'z']) {
        const sl = document.getElementById(`mg-shape-rot-${axis}`);
        const sp = document.getElementById(`mg-shape-rot-${axis}-val`);
        if (sl) sl.value = rot[axis] || 0;
        if (sp) sp.textContent = rot[axis] || 0;
    }

    // Bidirectional sync: show 3D selection overlay
    if (state._boneSelectOverlay) {
        fn._removeBoneOverlay(state._boneSelectOverlay);
        state._boneSelectOverlay = null;
    }
    state._selectedBoneName = boneName;
    if (state._mgCharacterId) {
        const inst = state.characters.get(state._mgCharacterId);
        if (inst && inst.bodyMesh && inst.bodyMesh.userData.boneVertexRanges) {
            state._boneSelectOverlay = fn._createBoneOverlay(inst.bodyMesh, boneName, state._BONE_SELECT_MAT);
        }
    }
}

function _updateBoneTreeItem(boneName) {
    const item = document.querySelector(`.mg-bone-item[data-bone="${boneName}"]`);
    if (!item) return;
    const part = state._mgConfig.bone_parts[boneName];
    if (!part) return;
    const swatch = item.querySelector('.mg-bone-swatch');
    if (swatch) swatch.style.backgroundColor = part.color;
}

let _mgRegenTimer = null;
let _mgRegenBusy = false;
function _mgAutoRegenerate() {
    if (!state._mgCharacterId) return; // Only auto-regen if character exists
    if (_mgRegenBusy) {
        // Already generating -- schedule one more after current finishes
        _mgRegenTimer = true;
        return;
    }
    _mgRegenBusy = true;
    requestAnimationFrame(() => {
        _mgGenerateCharacter();
        _mgRegenBusy = false;
        if (_mgRegenTimer) {
            _mgRegenTimer = false;
            _mgAutoRegenerate();
        }
    });
}

function _mgGeneratePreview() {
    if (!state._mgConfig) {
        console.warn('Model Generator: missing config');
        return;
    }

    let result;
    if (state._mgSkeletonType === 'rig' && state._mgRigBonesData) {
        result = generateRigBoneMesh(state._mgRigBonesData, state._mgConfig, state.rigifySkeletonData, state.skinWeightData);
    } else {
        if (!state.rigifySkeletonData || !state.skinWeightData) {
            console.warn('Model Generator: missing skeleton data');
            return;
        }
        result = generateModelMesh(state.rigifySkeletonData, state.skinWeightData, state._mgConfig);
    }

    if (!result) {
        console.warn('Model Generator: no visible bones');
        return;
    }

    return result;
}

function _mgGenerateCharacter() {
    const result = _mgGeneratePreview();
    if (!result) return;

    // Clear bone highlight cache and overlays (references become invalid)
    fn._clearBoneHighlightCache();

    // Remember position + presetKey of old character before removing
    let oldPos = null;
    let oldPresetKey = null;
    if (state._mgCharacterId && state.characters.has(state._mgCharacterId)) {
        const old = state.characters.get(state._mgCharacterId);
        oldPos = old.group.position.clone();
        oldPresetKey = old.presetKey || null;
        fn.deleteCharacter(state._mgCharacterId);
        state._mgCharacterId = null;
    }

    // Create CharacterInstance
    const id = generateCharacterId();
    const configCopy = JSON.parse(JSON.stringify(state._mgConfig));
    configCopy.type = 'generated_model';
    configCopy.skeleton_type = state._mgSkeletonType;
    const inst = new fn.CharacterInstance(id, configCopy);
    inst.presetName = state._mgConfig.name || 'Generiertes Modell';
    inst.presetKey = oldPresetKey;
    inst.bodyType = state._mgSkeletonType === 'rig' ? 'Rig Bones' : 'DEF Skeleton';

    // Set the mesh directly
    inst.bodyMesh = result.mesh;
    if (result.skeleton) {
        inst.rigifySkeleton = result.skeleton;
        inst.isSkinned = true;
    }
    inst.group.add(result.mesh);

    // Restore position or offset
    if (oldPos) {
        inst.group.position.copy(oldPos);
    }

    state.characters.set(id, inst);
    state.scene.add(inst.group);
    state._mgCharacterId = id;

    fn.updateCharacterListUI();
    fn.updateVertexCount();
    fn.selectCharacter(id);

    const vc = result.mesh.geometry.attributes.position.count;
    console.log(`Model Generator: created ${state._mgSkeletonType === 'rig' ? 'Mesh' : 'SkinnedMesh'} with ${vc} vertices as character "${inst.presetName}"`);
}

async function _mgSaveModelToServer() {
    // Sync config if needed
    if (!state._mgConfig) {
        let inst = _selectedInst();
        if (!inst || !inst.generatedConfig) {
            for (const [, c] of state.characters) {
                if (c.generatedConfig) { inst = c; break; }
            }
        }
        if (inst && inst.generatedConfig) {
            state._mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
            state._mgSkeletonType = inst.generatedConfig.skeleton_type || 'rig';
            state._mgCharacterId = inst.id;
        }
    }
    if (!state._mgConfig) {
        alert('Kein Modell vorhanden.');
        return;
    }

    const data = {
        ...state._mgConfig,
        type: 'generated_model',
        name: state._mgConfig.name || 'Generiertes Modell',
        body_type: state._mgSkeletonType === 'rig' ? 'Rig Bones' : 'DEF Skeleton',
        skeleton_type: state._mgSkeletonType
    };
    const inst = state._mgCharacterId ? state.characters.get(state._mgCharacterId) : null;
    const defaultName = ((inst && inst.presetKey) ? inst.presetKey : state.defaultPresetName || state._mgConfig.name || 'Neues Modell') + '.json';
    const chosenName = await fn._saveJsonWithPicker(data, defaultName);
    if (!chosenName) return;                // user cancelled file dialog

    // Also save to server models directory so Theatre and other pages see it
    const saveName = chosenName.replace(/\.json$/i, '');
    try {
        await fetch('/api/character/model/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ name: saveName, data })
        });
        if (state._mgCharacterId) {
            const ci = state.characters.get(state._mgCharacterId);
            if (ci) {
                ci.generatedConfig = JSON.parse(JSON.stringify(data));
                ci.presetKey = saveName;
            }
        }
        console.log(`[MG] Model saved as "${saveName}" (file + server)`);
    } catch (e) { console.warn('[MG] Server save failed:', e); }
}

async function _mgSaveModel() {
    // Sync config from selected character if not yet linked
    if (!state._mgConfig) {
        // Try selected character first, then any character with generatedConfig
        let inst = _selectedInst();
        if (!inst || !inst.generatedConfig) {
            for (const [, c] of state.characters) {
                if (c.generatedConfig) { inst = c; break; }
            }
        }
        if (inst && inst.generatedConfig) {
            state._mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
            state._mgSkeletonType = inst.generatedConfig.skeleton_type || 'rig';
            state._mgCharacterId = inst.id;
            console.log('[MG] Synced config from character:', inst.presetName);
        }
    }
    if (!state._mgConfig) {
        alert('Kein Modell vorhanden. Bitte zuerst ein Modell erzeugen.');
        return;
    }

    // Format as importable character preset
    const data = {
        ...state._mgConfig,
        type: 'generated_model',
        name: state._mgConfig.name || 'Generiertes Modell',
        body_type: state._mgSkeletonType === 'rig' ? 'Rig Bones' : 'DEF Skeleton',
        skeleton_type: state._mgSkeletonType
    };
    const defaultName = (state._mgConfig.name || 'Neues Modell').trim().replace(/[^a-zA-Z0-9_\-\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df ]/g, '_') + '.json';
    await fn._saveJsonWithPicker(data, defaultName);
}

/** Handle Ctrl+Click on a generated model bone. */
function _doBoneClick(boneName, inst) {
    // Ensure model generator is initialized from this instance's config
    if (!state._mgConfig && inst.generatedConfig) {
        state._mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
        state._mgSkeletonType = inst.generatedConfig.skeleton_type || 'rig';
        state._mgCharacterId = inst.id;
        if (!state._mgInitialized) {
            _bindModelGeneratorUI();
            state._mgInitialized = true;
        }
        const skelSelect = document.getElementById('mg-skeleton-type');
        if (skelSelect) skelSelect.value = state._mgSkeletonType;
        _populateBoneTree();
        _syncMGGlobalUI();
    }
    // Link model generator to this character if not linked
    if (!state._mgCharacterId && inst.generatedConfig) {
        state._mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
        state._mgCharacterId = inst.id;
        _populateBoneTree();
    }

    if (state._selectedBoneName === boneName) {
        // Toggle off
        fn._clearBoneSelection();
        state._mgSelectedBone = null;
        const propsSection = document.getElementById('mg-bone-props-section');
        if (propsSection) propsSection.style.display = 'none';
        document.querySelectorAll('.mg-bone-item.selected').forEach(el => el.classList.remove('selected'));
        return;
    }

    // Select new bone
    fn._clearBoneSelection();
    state._selectedBoneName = boneName;
    if (inst.bodyMesh) {
        state._boneSelectOverlay = fn._createBoneOverlay(inst.bodyMesh, boneName, state._BONE_SELECT_MAT);
    }

    // Sync with Model Generator UI
    _mgSelectBone(boneName);
    fn.switchTab('modell');

    // Ensure bone properties section is expanded
    const propsSection = document.getElementById('mg-bone-props-section');
    if (propsSection) propsSection.classList.remove('collapsed');

    // Scroll bone into view in tree
    const treeItem = document.querySelector(`.mg-bone-item[data-bone="${boneName}"]`);
    if (treeItem) {
        // Expand parent category if collapsed
        const catBody = treeItem.closest('.mg-category-body');
        if (catBody && catBody.classList.contains('hidden')) {
            catBody.classList.remove('hidden');
            const header = catBody.previousElementSibling;
            if (header) header.classList.remove('collapsed');
        }
        treeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

export {
    initModelGenerator, _bindModelGeneratorUI, _syncMGGlobalUI,
    _populateBoneTree, _mgSelectBone, _updateBoneTreeItem,
    _mgAutoRegenerate, _mgGeneratePreview, _mgGenerateCharacter,
    _mgSaveModelToServer, _mgSaveModel, _doBoneClick,
};

fn.initModelGenerator = initModelGenerator;
fn._doBoneClick = _doBoneClick;
fn._mgSelectBone = _mgSelectBone;
fn._mgGenerateCharacter = _mgGenerateCharacter;
fn._mgSaveModelToServer = _mgSaveModelToServer;
fn._mgSaveModel = _mgSaveModel;
fn._mgAutoRegenerate = _mgAutoRegenerate;
fn._mgGeneratePreview = _mgGeneratePreview;
