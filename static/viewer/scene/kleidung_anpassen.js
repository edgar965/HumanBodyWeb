import * as THREE from 'three';
import { _charQueryParams, _selectedInst, _sliderVal } from './utils.js';
import { _selectedGarmentMesh } from './garments.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { state, REGION_DEFS } from './state.js';
import { Bereichsgewichte } from '../gemeinsam/bereichsgewichte.js';
import { Kleidungszustand } from './kleidungszustand.js';
import { Kleideranpassung } from './kleideranpassung.js';
/**
 * Kleidungsstueck an den Koerper anpassen und die Regler dazu.
 *
 * Aus garments.js herausgeloest (Umbau 16.08.2026).
 */


/** Die Kosinus-Gewichte der fuenf Baender — Rechnung siehe `Bereichsgewichte`. */
export function _computeGarmentRegionWeights(inst, key) {
    const gewichte = Bereichsgewichte.rechnen(inst.garmentOrigPositions[key]);
    if (!gewichte) return;
    inst.garmentRegionWeights[key] = gewichte;
}

/** Apply per-region Y-offsets to a garment mesh using cosine-blended weights. */
export function _applyGarmentRegionOffsets(inst, key) {
    const mesh = inst.clothMeshes[key];
    const orig = inst.garmentOrigPositions[key];
    const rw = inst.garmentRegionWeights[key];
    const st = inst.garmentState[key];
    if (!mesh || !orig || !rw || !st) return;
    const positions = mesh.geometry.attributes.position.array;
    const n = orig.length / 3;
    positions.set(orig);
    for (const def of REGION_DEFS) {
        const stKey = 'region' + def.id[0].toUpperCase() + def.id.slice(1);
        const offset = st[stKey] || 0;
        if (Math.abs(offset) < 1e-6) continue;
        const w = rw[def.id];
        for (let i = 0; i < n; i++) {
            positions[i * 3 + 1] += offset * w[i];
        }
    }
    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.computeBoundingSphere();
}

/**
 * Reglerstaende in den Zustand des gewaehlten Stuecks zuruecklegen. Die
 * Feldliste steht in `Kleidungszustand` — vorher war sie hier zum dritten Mal
 * ausgeschrieben, inklusive der Umrechnung der fuenf Regionsregler.
 */
export function _saveSelectedGarmentState() {
    const sel = _selectedGarmentMesh();
    const zustand = sel && sel.inst.garmentState[sel.key];
    if (!zustand) return;
    const farbfeld = document.getElementById('garment-color');
    const neu = Kleidungszustand.ausJson(zustand).ausReglernUebernehmen(
        'garment', _sliderVal,
        farbfeld ? new THREE.Color(farbfeld.value) : null);
    // Die Werte in das vorhandene Objekt schreiben, nicht die Instanz
    // austauschen: Andere Stellen halten eine Referenz darauf.
    Object.assign(zustand, neu.zuJson());
}

/**
 * Regler auf den Zustand des gewaehlten Stuecks stellen. Die elf Zuweisungen
 * stehen in `Kleidungszustand.inRegler()` — hier bleibt nur, was diese Seite
 * eigen hat: die gewaehlte Kennung und die Farbe.
 */
export function _syncGarmentSliders() {
    if (state._selectedSubMesh?.type !== 'cloth') return;
    const inst = state.characters.get(state._selectedSubMesh.charId);
    const key = state._selectedSubMesh.key;
    const st = inst?.garmentState[key];
    if (!st) return;
    if (key.startsWith('gar_')) state._selectedGarmentId = key.slice(4);

    // Die Regler loesen beim Setzen ihr `input` aus; ohne diese Sperre wuerde
    // das als Benutzereingabe gelten und eine Neuanpassung anstossen.
    state._syncingSliders = true;
    try {
        Kleidungszustand.ausJson(st).inRegler('garment');
        const farbfeld = document.getElementById('garment-color');
        if (farbfeld && st.color) {
            farbfeld.value = '#' + new THREE.Color(...st.color).getHexString();
        }
    } finally {
        state._syncingSliders = false;
    }
}

/**
 * Kleidungsstueck des Assets-Reiters anpassen. Der Ablauf steckt in
 * `Kleideranpassung` — er stand bis zum Umbau am 16.08.2026 hier mit 101 Zeilen
 * und fast gleich noch einmal in `_doKleiderFit` (Kleider-Reiter).
 *
 * Eigen ist nur, was danach passiert: Der Assets-Reiter fuehrt eine Liste
 * `inst.garments` (fuer das Speichern der Szene) und stellt die Auswahl des
 * Teilnetzes wieder her, wenn genau dieses Stueck gewaehlt war.
 */
export async function _doGarmentFit() {
    const kennung = state._selectedGarmentId;
    if (!kennung) return null;
    const vorherGewaehlt = state._selectedSubMesh?.key;
    return new Kleideranpassung({
        vorsilbe: 'garment',
        schluessel: 'gar_',
        kennung,
        danach: (figur, schluessel, zustand, netz) => {
            figur.garments = figur.garments.filter(g => g.id !== kennung);
            figur.garments.push({ id: kennung, ...zustand.zuJson() });
            if (vorherGewaehlt !== schluessel) return;
            state._selectedSubMesh = { type: 'cloth', key: schluessel,
                                       label: kennung, meshObj: netz,
                                       charId: figur.id };
            fn._setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
            fn._syncPropGarmentControls();
        },
    }).ausfuehren();
}
