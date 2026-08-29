/**
 * Scene Editor -- Properties panel: transform, body type, presets, morphs, equipped list.
 */
import { THREE, serverLog } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { escapeHtml } from './utils.js';
import { markDirty } from './undo.js';
import { _sameSubMesh, getSelectableSubMeshes } from './teilnetz_auswahl.js';
import { Charakterkoerper } from './charakter_koerper.js';
import { Morphliste } from '../gemeinsam/morphliste.js';
import { Metaregler } from '../gemeinsam/metaregler.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/** Unter diesem Betrag gilt ein Morph als aus und wird aus der Figur entfernt. */
const MORPH_SCHWELLE = 0.005;

export function initTabs() {
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
            if (tab.dataset.tab === 'modell') fn.initModelGenerator();
        });
    });
    const resetBtn = document.getElementById('prop-reset-morphs');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (!state.currentPropsCharId) return;
            const inst = state.characters.get(state.currentPropsCharId);
            if (!inst) return;
            inst.morphs = {};
            populateMorphSliders(inst);
            reloadCharacterMesh(inst);
        });
    }
    const refitBtn = document.getElementById('prop-refit-btn');
    if (refitBtn) refitBtn.addEventListener('click', () => fn._refitAllForCurrentChar());
}

export function switchTab(tabName) {
    document.querySelectorAll('.panel-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.toggle('active', p.id === `tab-${tabName}`));
}

export async function fetchMorphDefs() {
    if (state.morphDefs && state.morphDefs.morphs && state.morphDefs.morphs.length > 0) return state.morphDefs;
    state.morphDefs = await Serverabruf.json('/api/character/morphs/');
    return state.morphDefs;
}

export async function populateProperties(charId) {
    const inst = state.characters.get(charId);
    if (!inst) return;
    state.currentPropsCharId = charId;
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-content').style.display = '';
    document.getElementById('assets-empty').style.display = 'none';
    document.getElementById('assets-content').style.display = '';
    try { await fetchMorphDefs(); } catch (e) { console.error('Failed to fetch morph defs:', e); return; }
    populateTransform(inst);
    updateEquippedList(inst);
    populateBodyType(inst);
    populatePresets(inst);
    populateMetaSliders(inst);
    populateMorphSliders(inst);
    fn.syncHairSelect(inst);
    _updatePropContext();
    const activeTab = document.querySelector('.panel-tab.active');
    if (!activeTab || activeTab.dataset.tab !== 'modell') switchTab('eigenschaften');
}

export function clearProperties() {
    fn.clearSubMeshSelection();
    state.currentPropsCharId = null;
    document.getElementById('prop-empty').style.display = '';
    document.getElementById('prop-content').style.display = 'none';
    document.getElementById('assets-empty').style.display = '';
    document.getElementById('assets-content').style.display = 'none';
}

function populateTransform(inst) {
    const grid = document.getElementById('prop-transform');
    grid.innerHTML = '';
    const rows = [
        { label: 'Pos', prop: 'position', step: 0.01 },
        { label: 'Rot', prop: 'rotation', step: 1, isDeg: true },
        { label: 'Scale', prop: 'scale', step: 0.01 },
    ];
    const axes = ['x', 'y', 'z'];
    for (const row of rows) {
        const lbl = document.createElement('label'); lbl.textContent = row.label; grid.appendChild(lbl);
        for (const axis of axes) {
            const input = document.createElement('input');
            input.type = 'number';
            input.step = row.step;
            input.dataset.prop = row.prop;
            input.dataset.axis = axis;
            input.className = 'prop-transform-input';
            let val = row.isDeg ? THREE.MathUtils.radToDeg(inst.group.rotation[axis]) : inst.group[row.prop][axis];
            input.value = parseFloat(val.toFixed(3));
            input.addEventListener('input', () => {
                const num = parseFloat(input.value); if (isNaN(num)) return;
                if (row.isDeg) inst.group.rotation[axis] = THREE.MathUtils.degToRad(num);
                else inst.group[row.prop][axis] = num;
                fn.updateCharacterListUI();
            });
            grid.appendChild(input);
        }
    }
}

export function syncTransformInputs() {
    const inst = state.characters.get(state.currentPropsCharId);
    if (!inst) return;
    document.querySelectorAll('.prop-transform-input').forEach(input => {
        const prop = input.dataset.prop, axis = input.dataset.axis;
        if (!prop || !axis || document.activeElement === input) return;
        let val = prop === 'rotation' ? THREE.MathUtils.radToDeg(inst.group.rotation[axis]) : inst.group[prop][axis];
        input.value = parseFloat(val.toFixed(3));
    });
}

function populateBodyType(inst) {
    const select = document.getElementById('prop-body-type');
    select.innerHTML = '';
    if (state.morphDefs && state.morphDefs.body_types) {
        for (const bt of state.morphDefs.body_types) {
            const opt = document.createElement('option'); opt.value = bt; opt.textContent = bt.replace(/_/g, ' '); select.appendChild(opt);
        }
    }
    select.value = inst.bodyType;
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);
    newSelect.addEventListener('change', () => { inst.bodyType = newSelect.value; reloadCharacterMesh(inst); });
}

async function populatePresets(inst) {
    const sel = document.getElementById('prop-preset');
    if (!sel || sel._loaded) return;
    try {
        const data = await Serverabruf.json('/api/character/charmorph-presets/');
        sel.innerHTML = '<option value="">-- Kein Preset --</option>';
        for (const p of (data.presets || [])) { const opt = document.createElement('option'); opt.value = JSON.stringify(p); opt.textContent = p.label; sel.appendChild(opt); }
        sel._loaded = true;
        sel.addEventListener('change', () => {
            if (!sel.value || !inst) return;
            const p = JSON.parse(sel.value);
            if (p.meta) { for (const [key, val] of Object.entries(p.meta)) { const slider = document.querySelector(`[data-meta="${key}"]`); if (slider) { slider.value = val; slider.dispatchEvent(new Event('input')); } } }
            if (p.structural) { for (const [name, val] of Object.entries(p.structural)) { const slider = document.querySelector(`[data-morph="${name}"]`); if (slider) { slider.value = val; slider.dispatchEvent(new Event('input')); } } }
            serverLog('preset_applied', p.label);
        });
    } catch(e) { console.error('Failed to load presets:', e); }
}

/**
 * Metaregler der Figur. Die Werte stehen in der Figur als -1..1 und im Regler
 * in ihrer Einheit — die Umrechnung kommt aus `Metaregler`, wo sie einmal
 * steht (war vorher an fünf Stellen ausgeschrieben).
 */
function populateMetaSliders(inst) {
    const container = document.getElementById('prop-meta-sliders');
    container.innerHTML = '';
    for (const [name, meta] of Object.entries(state.morphDefs?.meta_sliders || {})) {
        const angezeigt = Math.round(
            Metaregler.aussen(inst.meta[name] || 0, meta.min, meta.max));
        const row = document.createElement('div');
        row.className = 'slider-row';
        const label = document.createElement('label');
        label.textContent = meta.label || name;
        const slider = document.createElement('input');
        Object.assign(slider, { type: 'range', min: meta.min, max: meta.max,
                                step: 1, value: angezeigt });
        slider.dataset.meta = name;
        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = angezeigt;
        slider.addEventListener('input', () => { valSpan.textContent = slider.value; });
        // Erst beim Loslassen, weil danach das Netz neu geholt wird.
        slider.addEventListener('change', () => {
            inst.meta[name] = Metaregler.innen(parseFloat(slider.value),
                                               meta.min, meta.max);
            reloadCharacterMesh(inst);
        });
        row.append(label, slider, valSpan);
        container.appendChild(row);
    }
}

/**
 * Morphregler der Figur — dieselbe Liste wie auf den anderen Seiten, deshalb
 * aus `Morphliste`. Eigen ist hier nur: Meldung erst beim Loslassen, Pfeil vor
 * dem Kategorienamen, und Werte unter der Schwelle werden ganz entfernt, damit
 * die Figur keine Nullwerte mitschleppt.
 */
function populateMorphSliders(inst) {
    const container = document.getElementById('prop-morphs-panel');
    if (!state.morphDefs?.morphs || !state.morphDefs?.categories) {
        container.innerHTML = '';
        return;
    }
    new Morphliste({
        ereignis: 'change',
        chevron: true,
        startwert: name => inst.morphs[name],
        geaendert: (name, wert) => {
            if (Math.abs(wert) < MORPH_SCHWELLE) delete inst.morphs[name];
            else inst.morphs[name] = wert;
            reloadCharacterMesh(inst);
        },
    }).bauen(container, state.morphDefs.morphs, state.morphDefs.categories);
}

/** Ruhezeit, bevor das Netz neu geholt wird — beim Ziehen sammeln sich Werte. */
const NEULADEN_RUHE_MS = 300;

export async function reloadCharacterMesh(inst) {
    clearTimeout(state.reloadTimer);
    state.reloadTimer = setTimeout(async () => {
        try {
            await Charakterkoerper.neuLaden(inst);
            fn.updateVertexCount();
            fn.updateCharacterListUI();
            if (state.currentPropsCharId === inst.id) updateEquippedList(inst);
            markDirty();
        } catch (fehler) {
            console.error('Netz nicht neu ladbar:', fehler);
        }
    }, NEULADEN_RUHE_MS);
}

export function updateEquippedList(inst) {
    const list = document.getElementById('prop-equipped-list');
    if (!list) return;
    list.innerHTML = '';
    if (!inst) { list.innerHTML = '<li class="equipped-empty">Keine Objekte</li>'; return; }
    const targets = getSelectableSubMeshes(inst.id);
    if (targets.length === 0) { list.innerHTML = '<li class="equipped-empty">Keine Objekte</li>'; return; }
    for (const t of targets) {
        const li = document.createElement('li'); li.className = 'equipped-item';
        const nameSpan = document.createElement('span'); nameSpan.className = 'equipped-item-name';
        if (_sameSubMesh(state._selectedSubMesh, t)) nameSpan.classList.add('selected');
        nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => {
            if (state._selectedSubMesh) fn._setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
            const fresh = getSelectableSubMeshes(inst.id).find(x => x.type === t.type && x.key === t.key);
            if (!fresh) return;
            state._selectedSubMesh = fresh;
            fn._setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
            fn._setBodyEmissive(inst, state._ZERO_EMISSIVE);
            fn._syncGarmentSliders();
            _updatePropContext();
            if (fresh.type === 'cloth') fn._syncPropGarmentControls();
            else if (fresh.type === 'hair') fn._syncPropHairControls();
            updateEquippedList(inst);
        });
        const rmBtn = document.createElement('button');
        rmBtn.className = 'equipped-item-remove';
        rmBtn.innerHTML = '&#10005;';
        rmBtn.title = 'Entfernen';
        rmBtn.addEventListener('click', (e) => { e.stopPropagation(); fn._removeSubMesh(t); });
        li.appendChild(nameSpan); li.appendChild(rmBtn); list.appendChild(li);
    }
}

export function _updatePropContext() {
    const bodySections = ['prop-transform-section', 'prop-equipped-section', 'prop-bodytype-section', 'prop-morphs-section'];
    const isGarment = state._selectedSubMesh && state._selectedSubMesh.type === 'cloth' && state._selectedSubMesh.key.startsWith('gar_');
    const isMH = state._selectedSubMesh && state._selectedSubMesh.type === 'cloth' && state._selectedSubMesh.key.startsWith('mh_');
    const isHair = state._selectedSubMesh && state._selectedSubMesh.type === 'hair';
    const isAsset = isGarment || isMH || isHair;
    for (const id of bodySections) { const el = document.getElementById(id); if (el) el.style.display = isAsset ? 'none' : ''; }
    const gEl = document.getElementById('prop-garment-section'); if (gEl) gEl.style.display = isGarment ? '' : 'none';
    const mhEl = document.getElementById('prop-mh-section'); if (mhEl) mhEl.style.display = isMH ? '' : 'none';
    const hEl = document.getElementById('prop-hair-section'); if (hEl) hEl.style.display = isHair ? '' : 'none';
    if (isMH) fn._syncPropMHControls();
}

// Register
fn.initTabs = initTabs;
fn.switchTab = switchTab;
fn.fetchMorphDefs = fetchMorphDefs;
fn.populateProperties = populateProperties;
fn.clearProperties = clearProperties;
fn.syncTransformInputs = syncTransformInputs;
fn.updateEquippedList = updateEquippedList;
fn._updatePropContext = _updatePropContext;
