/**
 * HumanBody Character Viewer — Einstieg der Seite.
 *
 * Umbau 16.08.2026: Die Datei hatte 358 Zeilen, davon 230 in einer einzigen
 * `init()`-Funktion — Bühne aufbauen, fünf Knöpfe verdrahten, acht
 * Seitenbefehle abarbeiten, ein Dutzend Module starten und die Renderschleife.
 * Jetzt vier Klassen und hier nur noch die Reihenfolge:
 *
 *   buehne.js          Renderer, Szene, Kamera, Licht, Gitter
 *   werkzeugknoepfe.js die Umschalter über der Bühne
 *   seitenbefehle.js   die Befehle aus Menüleiste und Tastatur
 *   bildschleife.js    Renderschleife, Zeitanzeige, Bildrate
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

// Module laden, damit sie ihre Funktionen registrieren (Reihenfolge:
// Grundlagen zuerst, dann die darauf aufbauenden).
import './utils.js';
import './scene_settings.js';
import './mesh.js';
import './skinning.js';
import './websocket.js';
import './morphs.js';
import './wardrobe.js';
import './animation.js';
import './cloth.js';
import './hair.js';
import './garment.js';
import './vertex_editor.js';
import './pattern_editor.js';
import './interaction.js';
import './presets.js';
import './smpl.js';

import { applySceneSettings, applyExpandedPanels } from './scene_settings.js';
import { loadMesh } from './mesh.js';
import { loadSkinWeights, loadRigifySkeleton } from './skinning.js';
import { connectWebSocket } from './websocket.js';
import { loadMorphs } from './morphs.js';
import { loadWardrobe } from './wardrobe.js';
import { loadAnimations, loadBVHAnimation } from './animation.js';
import { loadClothUI, removeAllCloth } from './cloth.js';
import { loadHairUI, removeHair, refitHairToBody } from './hair.js';
import { loadGarmentUI, removeAllGarments } from './garment.js';
import { initPatternEditor } from './pattern_editor.js';
import { initInteraction, updateEquippedList, _setEmissiveOnItem } from './interaction.js';
import { initLoadPreset, initSaveButtons, gatherModelState } from './presets.js';
import { loadSmplGarmentUI, initSmplBodyUI } from './smpl.js';
import { isVeActive } from './vertex_editor.js';

import { Buehne } from './buehne.js';
import { Werkzeugknoepfe } from './werkzeugknoepfe.js';
import { Seitenbefehle } from './seitenbefehle.js';
import { Bildschleife } from './bildschleife.js';

console.log('[Viewer] v2.1 geladen (ES-Module, Klassen)');

/** Alle Panel-Bereiche auf- und zuklappbar machen. */
function bereicheKlappbar() {
    document.querySelectorAll('.panel-section h3').forEach(kopf => {
        kopf.addEventListener('click', () => {
            kopf.closest('.panel-section').classList.toggle('collapsed');
        });
    });
}

/** Die Module, die beim Start ihre Daten holen. */
function inhalteLaden(schleife) {
    loadMorphs();
    loadMesh().then(() => schleife.starten());
    loadSkinWeights();
    loadRigifySkeleton();
    loadWardrobe();
    loadAnimations();
    loadClothUI();
    loadHairUI();
    initPatternEditor();
    loadGarmentUI();
    loadSmplGarmentUI();
    initSmplBodyUI();
    initLoadPreset();
    initSaveButtons();
    connectWebSocket();
}

// EINE Bühne, vor init() angelegt: Sie wird zweimal gebraucht — beim Aufbauen
// und für die Zurücksetzen-Befehle — und `fn.onResize` muss sie ebenfalls
// erreichen. `init()` läuft am Dateiende, die Deklaration gilt dann längst.
const buehne = new Buehne(state);
fn.onResize = () => buehne.groesseAnpassen();

function init() {
    buehne.aufbauen();
    applySceneSettings();
    bereicheKlappbar();
    applyExpandedPanels();

    const schleife = new Bildschleife(state);
    inhalteLaden(schleife);

    new Werkzeugknoepfe(state, {
        animationLaden: loadBVHAnimation,
        garmentLaden: (kennung) => fn.loadGarment(kennung),
        garmentZustandSichern: (kennung) => fn._saveGarmentState(kennung),
        haareRefit: refitHairToBody,
    }).verdrahten();

    new Seitenbefehle(state, buehne, {
        auswahlFarbeSetzen: _setEmissiveOnItem,
        ausstattungAktualisieren: updateEquippedList,
        alleGarnituren: removeAllGarments,
        alleKleider: removeAllCloth,
        haareEntfernen: removeHair,
        modellzustand: gatherModelState,
        gewaehltesEntfernen: () => fn._removeSelectedItem?.(),
    }).verdrahten();

    initInteraction();
}

// Zugriff für die Playwright-Tests.
window.__viewer = {
    get scene() { return state.scene; },
    get bodyMesh() { return state.bodyMesh; },
    get garmentMeshes() { return state.garmentMeshes; },
    get garmentState() { return state.garmentState; },
    get selectedGarmentId() { return state.selectedGarmentId; },
    get clothMeshes() { return state.clothMeshes; },
    get smplGarmentMeshes() { return state.smplGarmentMeshes; },
    get smplBodyMesh() { return state.smplBodyMesh; },
    get camera() { return state.camera; },
    get controls() { return state.controls; },
    get rigifySkeleton() { return state.rigifySkeleton; },
    get isSkinned() { return state.isSkinned; },
    get selectedItem() { return state._selectedItem; },
    getSelectableTargets: fn.getSelectableTargets,
    updateEquippedList,
    _buildBodyQueryString: fn.buildBodyQueryString,
    peRegionGenerate: fn.peRegionGenerate,
    peGenerate3D: fn.peGenerate3D,
    get peMode() { return fn.getPeMode(); },
    set peMode(v) { fn.setPeMode(v); },
    get veActive() { return isVeActive(); },
    get veSelectedIndices() { return fn.getVeSelectedIndices(); },
    get veTargetMesh() { return fn.getVeTargetMesh(); },
    veEnterEditMode: fn.veEnterEditMode,
    veExitEditMode: fn.veExitEditMode,
};

init();
