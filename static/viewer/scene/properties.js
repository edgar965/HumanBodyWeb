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
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Auswahlfeld } from '../gemeinsam/auswahlfeld.js';
import { Umaeigenschaften } from './uma/umaeigenschaften.js';
import { Smpleigenschaften } from './smpl/smpleigenschaften.js';
import { Umapythoneigenschaften } from './umapython/umapythoneigenschaften.js';
import { Mheigenschaften } from './makehuman/mheigenschaften.js';
import { Eigenschaftenbereiche } from './eigenschaftenbereiche.js';
import { Transformfelder } from './transformfelder.js';
import { Figurmerker } from './figurmerker.js';
import { Reitergedaechtnis } from './reitergedaechtnis.js';
import { Formbedienung } from './formbedienung.js';
import { Reiterfreigabe } from './reiterfreigabe.js';

export function initTabs() {
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Ein ausgegrauter Reiter muss auch wirklich gesperrt sein
            // (08.09.2026) — sonst ist das Grau eine Behauptung.
            if (!Reiterfreigabe.frei(tab.dataset.tab)) return;
            switchTab(tab.dataset.tab);
            // Der Reiter gehört zur Figur: beim nächsten Anklicken derselben
            // Figur öffnet er sich wieder (Edgar, 06.09.2026).
            Figurmerker.tabMerken(state.selectedCharacterId, tab.dataset.tab);
            // Zusaetzlich ohne Figurbezug: `Figurmerker` liegt im
            // sessionStorage und gilt fuer die Figuren DIESER Sitzung.
            // „Beim naechsten Aufruf" heisst neues Fenster (09.09.2026).
            Reitergedaechtnis.reiterMerken(tab.dataset.tab);
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
            Formbedienung.humanbody(inst, state.morphDefs, reloadCharacterMesh);
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
    Eigenschaftenbereiche.zeigen(true);
    populateTransform(inst);
    // Eine UMA-Figur (05.09.2026) hat Regler und Farben statt Body Type,
    // Morphs und Ausstattung; der Assets-Reiter zeigt ihre Unity-Garderobe.
    const uma = inst.quelle === 'uma';
    const smpl = inst.quelle === 'smpl';
    const makehuman = inst.quelle === 'makehuman';
    const umapython = inst.quelle === 'umapython';
    Eigenschaftenbereiche.humanbodyTeile(!uma && !smpl && !makehuman && !umapython);
    Eigenschaftenbereiche.umaGarderobe(uma ? inst : null);
    // Eine MakeHuman-Figur (06.09.2026) bringt ihre eigene Garderobe mit —
    // die 181 .mhclo-Stücke sitzen auf ihr ohne Fit-Regler. Body Type,
    // Morphs und Ausstattung des HumanBody-Körpers hat sie nicht.
    if (makehuman) {
        Umaeigenschaften.leeren();
        Smpleigenschaften.leeren();
        Formbedienung.leeren();
        await Mheigenschaften.fuellen(inst);
        _updatePropContext();
        _gemerktesHerstellen(charId);
        return;
    }
    Mheigenschaften.leeren();
    // Eine UMA-Python-Figur (08.09.2026) ist Koerper plus angepasstes
    // Kleidungsstueck; geformt wird ueber zwei geometrische Regler, den
    // Stoff zieht der portierte Konformer nach.
    if (umapython) {
        Umaeigenschaften.leeren();
        Smpleigenschaften.leeren();
        Formbedienung.leeren();
        Umapythoneigenschaften.fuellen(inst);
        _updatePropContext();
        _gemerktesHerstellen(charId);
        return;
    }
    Umapythoneigenschaften.leeren();
    // Ein SMPL-Referenzkörper (06.09.2026) hat nur Geschlecht und die
    // vorgegebenen Maße — keine Morphs, keine Regler, kein Skelett.
    if (smpl) {
        Umaeigenschaften.leeren();
        Formbedienung.leeren();
        Smpleigenschaften.fuellen(inst);
        _updatePropContext();
        _gemerktesHerstellen(charId);
        return;
    }
    Smpleigenschaften.leeren();
    if (uma) {
        Umaeigenschaften.fuellen(inst);
        // Ein Name, zwei Übersetzungen: derselbe Block wie bei HumanBody,
        // hier auf Knochen (Edgar, 06.09.2026).
        await Formbedienung.uma(
            inst, () => Umaeigenschaften.einzelreglerAngleichen(inst));
        _updatePropContext();
        _gemerktesHerstellen(charId);
        return;
    }
    Umaeigenschaften.leeren();
    try { await fetchMorphDefs(); } catch (e) { console.error('Failed to fetch morph defs:', e); return; }
    updateEquippedList(inst);
    populateBodyType(inst);
    populatePresets(inst);
    // Metaregler, gemeinsamer Block und Einzelmorphs — sie ziehen sich
    // gegenseitig nach (`Formbedienung`). Nach `fetchMorphDefs`, weil der
    // gemeinsame Block die Morphnamen dieses Körpertyps braucht.
    await Formbedienung.humanbody(inst, state.morphDefs, reloadCharacterMesh);
    fn.syncHairSelect(inst);
    _updatePropContext();
    _gemerktesHerstellen(charId);
}

/**
 * Reiter, Animation und Kleidungsstück, die diese Figur zuletzt hatte
 * (`Figurmerker`). Früher sprang jede Auswahl auf „Eigenschaften"; wer im
 * Animation-Reiter die Figur wechselte, musste zurückklicken. Eine Figur ohne
 * Merkzettel lässt den Reiter, wo er ist.
 */
function _gemerktesHerstellen(charId) {
    const tab = Figurmerker.tab(charId);
    if (tab && document.querySelector(`.panel-tab[data-tab="${tab}"]`)) switchTab(tab);
    fn.animationMarkieren?.(Figurmerker.animation(charId)?.name || null);
    const kleid = Figurmerker.kleider(charId);
    if (kleid) fn.kleiderSelectById?.(kleid);
}

export function clearProperties() {
    fn.clearSubMeshSelection();
    state.currentPropsCharId = null;
    Eigenschaftenbereiche.zeigen(false);
    Umaeigenschaften.leeren();
    Smpleigenschaften.leeren();
    Mheigenschaften.leeren();
    Formbedienung.leeren();
    Eigenschaftenbereiche.umaGarderobe(null);
}

function populateTransform(inst) {
    Transformfelder.fuellen(inst);
}

export function syncTransformInputs() {
    Transformfelder.angleichen();
}

function populateBodyType(inst) {
    const select = document.getElementById('prop-body-type');
    select.innerHTML = '';
    if (state.morphDefs && state.morphDefs.body_types) {
        Auswahlfeld.ausNamen(select, state.morphDefs.body_types,
            (bt) => bt.replace(/_/g, ' '));
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
        Auswahlfeld.fuellen(sel, (data.presets || []).map(
            (p) => ({ wert: JSON.stringify(p), text: p.label })));
        sel._loaded = true;
        sel.addEventListener('change', () => {
            if (!sel.value || !inst) return;
            const p = JSON.parse(sel.value);
            if (p.meta) { for (const [key,
                val] of Object.entries(p.meta)) { const slider = document.querySelector(`[data-meta="${key}"]`);
                    if (slider) { slider.value = val; slider.dispatchEvent(new Event('input')); } } }
            if (p.structural) { for (const [name,
                val] of Object.entries(p.structural)) { const slider = document.querySelector(`[data-morph="${name}"]`);
                    if (slider) { slider.value = val; slider.dispatchEvent(new Event('input')); } } }
            serverLog('preset_applied', p.label);
        });
    } catch(e) { console.error('Failed to load presets:', e); }
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
    const bodySections = ['prop-transform-section', 'prop-equipped-section', 'prop-bodytype-section',
        'prop-morphs-section'];
    // Beide Pruefungen fragen dasselbe dreimal ab; nur die Vorsilbe des
    // Schluessels unterscheidet sie.
    const teilnetz = state._selectedSubMesh;
    const istStoff = Boolean(teilnetz) && teilnetz.type === 'cloth';
    const isGarment = istStoff && teilnetz.key.startsWith('gar_');
    const isMH = istStoff && teilnetz.key.startsWith('mh_');
    const isHair = state._selectedSubMesh && state._selectedSubMesh.type === 'hair';
    const isAsset = isGarment || isMH || isHair;
    for (const id of bodySections) { const el = document.getElementById(id); if (el) el.style.display = isAsset
        ? 'none' : ''; }
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
