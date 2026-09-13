/**
 * Viewer — Mesh loading, body materials, vertex updates.
 *
 * Seit 13.09.2026 baut `HumanbodyModell` (`gemeinsam/humanbodymodell.js`)
 * den Körper — wie auf jeder Seite; `state.modell` ist die Figur, die
 * Häutung läuft über `modell.haeuten` (`skinning.js`).
 */
import { Netzpunkte } from '../gemeinsam/netzpunkte.js';
import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';
import { applySceneSkinSettings, applySkinColor } from './scene_settings.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

function _getBodyTop() {
    if (!state.bodyGeometry) return null;
    const pos = state.bodyGeometry.attributes.position.array;
    let maxY = -Infinity;
    for (let i = 1; i < pos.length; i += 3) {
        if (pos[i] > maxY) maxY = pos[i];
    }
    return maxY;
}

export function updateMeshVertices(float32Buffer) {
    if (!Netzpunkte.ausPuffer(state.bodyGeometry, float32Buffer)) return;
    // Die Ausgangshoehe wird beim ERSTEN Netz gemerkt: An ihr haengt die
    // Nachskalierung der Haare (`refitHairToBody`).
    if (state.initialBodyTop === null) {
        state.initialBodyTop = _getBodyTop();
    }
}

/**
 * Den Körper über `HumanbodyModell` bauen und in die Szene stellen.
 *
 * WARUM ALS EIGENER SCHRITT (28.08.2026, Befund `doppelcode`): Dieser
 * Ablauf stand zweimal in DIESER Datei — in `loadMesh` und in
 * `reloadMeshForBodyType`.
 */
async function _netzAufbauen(bodyType) {
    const modell = new HumanbodyModell('modellseite', bodyType ? { body_type: bodyType } : {});
    await modell.koerper();
    state.modell = modell;
    state.bodyMesh = modell.bodyMesh;
    state.bodyGeometry = state.bodyMesh.geometry;
    state.vertexCount = state.bodyGeometry.attributes.position.count;
    state.scene.add(modell.group);
    _punktzahlZeigen(state.vertexCount);

    applySceneSkinSettings();
    applySkinColor();
}

/** Die Punktzahl in der Statuszeile — fehlt das Feld, passiert nichts. */
function _punktzahlZeigen(anzahl) {
    const feld = document.getElementById('vertex-count');
    if (feld) feld.textContent = anzahl.toLocaleString();
}

export async function loadMesh() {
    try {
        await _netzAufbauen(null);
        if (state.initialBodyTop === null) state.initialBodyTop = _getBodyTop();
        fn.onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

export async function reloadMeshForBodyType(bodyType, gender) {
    Protokoll.debug('Viewer', 'Reloading mesh for', bodyType, '(gender:', gender, ')');
    if (state.modell) {
        state.scene.remove(state.modell.group);
        state.modell.dispose();
        state.modell = null;
        state.bodyMesh = null;
        state.bodyGeometry = null;
    }
    state.isSkinned = false;
    state.rigifySkeleton = null;
    state.skinWeightData = null;
    state.initialBodyTop = null;

    try {
        await _netzAufbauen(bodyType);
        state.initialBodyTop = _getBodyTop();

        state.skinWeightData = await Serverabruf.json(
            `${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);

        if (typeof fn.removeAllCloth === 'function') fn.removeAllCloth();
    } catch (e) {
        console.error('Failed to reload mesh:', e);
    }
}

// Register
fn.loadMesh = loadMesh;
fn._getBodyTop = _getBodyTop;
