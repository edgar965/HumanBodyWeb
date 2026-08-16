import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Studioeinstellungen — die Vorgaben des BVH-Studios aus `/api/ui-prefs/`.
 *
 * Aus `index.js init()` herausgeloest (Umbau 16.08.2026). Zwei Dinge fielen auf:
 *
 *  * `/api/ui-prefs/` wurde in derselben `init()` ZWEIMAL geholt — einmal für
 *    die acht Studio-Vorgaben, und dreißig Zeilen später noch einmal für das
 *    Vorgabeprojekt. Jetzt eine Anfrage.
 *  * Die acht Werte wurden einzeln aus dem dict geklaubt, jeder mit eigener
 *    Umwandlung und eigenem Ersatzwert mitten im Ablauf. Der Auftrag verlangt
 *    für so einen Datensatz eine Klasse — hier ist sie, mit den Ersatzwerten
 *    als benannte Tabelle.
 */
export class Studioeinstellungen {

    /** Feldname → [Schlüssel in ui_prefs, Umwandlung, Ersatzwert]. */
    static FELDER = {
        modell: ['studio_default_model', String, 'Rig2'],
        koerperart: ['studio_body_type', String, 'Female_Caucasian'],
        bilderProSekunde: ['studio_fps', parseInt, 30],
        zeitleistenZoom: ['studio_zoom', parseInt, 100],
        videoziel: ['studio_video_output', String, ''],
        bvhziel: ['studio_bvh_output', String, ''],
        projektpfad: ['studio_project_path', String, ''],
        vorladeSekunden: ['studio_preload_seconds', parseFloat, 3],
        vorgabeprojekt: ['studio_default_project', String, ''],
    };

    constructor(werte = {}) {
        for (const [feld, [schluessel, wandeln, ersatz]]
                of Object.entries(Studioeinstellungen.FELDER)) {
            this[feld] = Studioeinstellungen._wert(werte[schluessel], wandeln, ersatz);
        }
    }

    /** Umwandeln, aber nie einen unbrauchbaren Wert übernehmen. */
    static _wert(roh, wandeln, ersatz) {
        if (roh === undefined || roh === null || roh === '') {
            return wandeln === String ? ersatz : ersatz;
        }
        const wert = wandeln(roh);
        if (wandeln !== String && !Number.isFinite(wert)) return ersatz;
        return wert;
    }

    static async holen() {
        try {
            return new Studioeinstellungen(
                await Serverabruf.json('/api/ui-prefs/'));
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'Vorgaben nicht ladbar, es gelten '
                              + 'die Ersatzwerte:', fehler);
            return new Studioeinstellungen();
        }
    }

    /** Werte in den Projektzustand übernehmen. */
    anwenden() {
        state.project.defaultModel = this.modell;
        state.project.defaultBodyType = this.koerperart;
        state.project.fps = this.bilderProSekunde;
        state.project.videoOutputPath = this.videoziel;
        state.project.bvhOutputPath = this.bvhziel;
        state.project.projectPath = this.projektpfad;
        state.project.preloadSeconds = this.vorladeSekunden;
        state.timelineZoom = this.zeitleistenZoom;
        return this;
    }
}
