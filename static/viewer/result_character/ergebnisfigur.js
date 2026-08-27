import { state } from './state.js';
import { sharedState, loadRigifySkeleton, loadSkinWeights,
         createSceneSetup } from '../character_core.js';
import { applySceneSettings } from './scene_setup.js';
import { connectWebSocket } from './websocket.js';
import { loadMesh, convertToRigifySkinnedMesh, applySkinColor } from './mesh_loading.js';
import { loadCloth } from './cloth_garments.js';
import { loadHair } from './hair.js';
import { loadBVH } from './bvh_animation.js';
import { loadPresetClothAndHair } from './presets.js';
import { buildControlPanel } from './ui_panel.js';
import { Videoschleife } from './videoschleife.js';
import { Kopfbedienung } from './kopfbedienung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Ergebnisfigur — die 3D-Figur auf der Ergebnisseite eines Auftrags.
 *
 * Aus `result_character/index.js` herausgeloest (Umbau 16.08.2026):
 * `initResultCharacter()` hatte 216 Zeilen und machte sieben Dinge
 * hintereinander — Szene bauen, Bildschleife starten, Einstellungen holen,
 * Vorgabe holen, Daten laden, Kopfzeile verdrahten, Kleidung anziehen. Jetzt
 * je eine Methode, und `starten()` liest wie eine Inhaltsangabe.
 *
 * Zwei Wiederholungen dabei aufgelöst: die drei gleich gebauten
 * "Element ändern → BVH neu laden"-Blöcke (jetzt in `Kopfbedienung`) und die
 * zwei gleichlautenden Aufrufe für Hemd und Hose (jetzt `ERSATZKLEIDUNG`).
 */
export class Ergebnisfigur {

    /**
     * Kleidung, wenn die Vorgabe keine mitbringt. Vorher standen dafür zwei
     * Aufrufe mit denselben sechs Werten, nur mit anderem Schnitt.
     */
    static ERSATZKLEIDUNG = ['TPL_TSHIRT', 'TPL_PANTS'];
    static ERSATZWERTE = { method: 'template', segments: 32, tightness: 0.5,
                           top_extend: 0, bottom_extend: 0 };
    /** Frisur, wenn die Vorgabe keine nennt. */
    static ERSATZFRISUR = 'ballerina';

    constructor(werte) {
        this.canvas = document.getElementById(werte.canvasId);
        this.video = document.getElementById(werte.videoId);
        this.ladeanzeige = document.getElementById('characterLoading');
        this.feld = werte.panelId ? document.getElementById(werte.panelId) : null;
        this.modellwahlId = werte.modelSelectId;
        this.werte = werte;
    }

    /** true, wenn Leinwand und Video da sind. */
    vollstaendig() {
        if (this.canvas && this.video) return true;
        console.error('[result_character] Elemente fehlen:',
                      { canvas: !!this.canvas, video: !!this.video });
        return false;
    }

    async starten() {
        if (!this.vollstaendig()) return null;
        this._zustandSetzen();
        this._buehne();
        new Videoschleife(state).starten();
        await this.vorgabeHolen();
        if (!await this.datenLaden()) return null;
        await this.hautUndSkelett();
        if (state.isSkinned) await this._mitMessung('BVH', () => loadBVH());
        connectWebSocket();
        if (this.ladeanzeige) this.ladeanzeige.style.display = 'none';
        await new Kopfbedienung().verdrahten(this.modellwahlId);
        if (this.feld && state.morphData) buildControlPanel(this.feld, state.morphData);
        this.kleidungAnziehen();
        return this;
    }

    _zustandSetzen() {
        state.canvas = this.canvas;
        state.video = this.video;
        state.loadingEl = this.ladeanzeige;
        state.panel = this.feld;
        state.modelSelectId = this.modellwahlId;
        state.jobId = this.werte.jobId;
        state.bvhUrl = this.werte.bvhUrl;
        state.bvhFaceUrl = this.werte.bvhFaceUrl;
    }

    _buehne() {
        const teile = createSceneSetup(this.canvas);
        state.renderer = teile.renderer;
        state.scene = teile.scene;
        state.camera = teile.camera;
        state.controls = teile.controls;
        window._debugScene = teile.scene;
        applySceneSettings(teile.renderer, teile.scene, teile.camera,
                           teile.keyLight, teile.fillLight, teile.backLight,
                           teile.ambient);
    }

    // ------------------------------------------------------------ Vorgabe

    /** Welches Modell zeigt die Seite? Erst die Einstellung, dann das Modell. */
    async vorgabeHolen() {
        state.defaultPresetName = await this._einstellung()
                                  || state.defaultPresetName;
        await this._modellHolen(state.defaultPresetName);
    }

    async _einstellung() {
        try {
            const daten = await Serverabruf.json('/api/settings/humanbody/');
            return daten.result;
        } catch (fehler) {
            Protokoll.warnung('result_character', 'Einstellungen nicht ladbar,'
                         + ' Vorgabe bleibt', state.defaultPresetName);
            return null;
        }
    }

    async _modellHolen(name) {
        try {
            const antwort = await fetch(
                `/api/character/model/${encodeURIComponent(name)}/`);
            if (!antwort.ok) { Protokoll.warnung('ergebnisfigur', `Modell "${name}" nicht abrufbar (HTTP ${antwort.status})`); return; }
            const daten = await antwort.json();
            state.presetData = daten;
            if (daten.body_type) state.currentBodyType = daten.body_type;
            state.currentPresetName = name;
            state.currentMorphs = daten.morphs || {};
            state.currentMeta = daten.meta || {};
        } catch (fehler) {
            Protokoll.warnung('result_character', 'Modell nicht ladbar:', name);
        }
    }

    // -------------------------------------------------------------- Daten

    /** Netz, Skelett, Gewichte, Morphs und Frisuren — alles gleichzeitig. */
    async datenLaden() {
        const start = performance.now();
        try {
            const [, , , morphs, frisuren] = await Promise.all([
                loadMesh(state.currentBodyType),
                loadRigifySkeleton(),
                loadSkinWeights(state.currentBodyType),
                fetch('/api/character/morphs/').then(a => a.json()),
                fetch('/api/character/hairstyles/').then(a => a.json())
                    .catch(() => null),
            ]);
            state.morphData = morphs;
            state.hairData = frisuren;
            if (morphs.skin_colors) sharedState.skinColors = morphs.skin_colors;
            if (frisuren?.colors) sharedState.hairColorData = frisuren.colors;
        } catch (fehler) {
            console.error('[result_character] Daten laden fehlgeschlagen:', fehler);
            if (this.ladeanzeige) this.ladeanzeige.textContent = 'Fehler beim Laden';
            return false;
        }
        Protokoll.debug('PERF', `Daten in ${(performance.now() - start).toFixed(0)}ms`);
        return true;
    }

    async hautUndSkelett() {
        if (state.bodyMesh && sharedState.rigifySkeletonData
            && sharedState.skinWeightData) {
            await this._mitMessung('Skinning', () => convertToRigifySkinnedMesh());
        }
        applySkinColor(state.currentBodyType);
    }

    /** Dauer eines Schritts messen und melden — vorher dreimal ausgeschrieben. */
    async _mitMessung(name, tun) {
        const start = performance.now();
        const ergebnis = await tun();
        Protokoll.debug('PERF', `${name} in ${(performance.now() - start).toFixed(0)}ms`);
        return ergebnis;
    }

    // ----------------------------------------------------------- Kleidung

    kleidungAnziehen() {
        if (!state.isSkinned) return;
        if (state.presetData) {
            loadPresetClothAndHair(state.presetData);
            return;
        }
        for (const schnitt of Ergebnisfigur.ERSATZKLEIDUNG) {
            loadCloth(`tpl_${schnitt}`,
                      { ...Ergebnisfigur.ERSATZWERTE, template: schnitt });
        }
        this._ersatzfrisur();
    }

    _ersatzfrisur() {
        const frisuren = state.hairData?.hairstyles;
        if (!frisuren?.length) return;
        const gewaehlt = frisuren.find(f => f.name === Ergebnisfigur.ERSATZFRISUR)
                         || frisuren[0];
        if (gewaehlt) loadHair(gewaehlt.url);
    }
}
