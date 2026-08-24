import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track, Clip } from './models.js';
import { TRACK_COLORS } from './state.js';
import { Lichtanzeiger } from './lichtanzeiger.js';
import { Lichtschluessel } from './lichtschluessel.js';

/**
 * Szenenlichter — die vier Lichter der Grundszene als Spuren.
 *
 * Herausgelöst aus `spur_lichter.js` (321 Zeilen). Aufgerufen NACH dem
 * Wiederherstellen eines Projekts, weil die gespeicherten Werte dann vorliegen.
 *
 * DER UNTERSCHIED ZWISCHEN „KEIN SAVE" UND „SAVE OHNE DIESES LICHT"
 * =================================================================
 * `_pendingSceneOverrides.sceneLights` ist
 *
 *     undefined  -> neues Projekt: alle vier Lichter anlegen
 *     {}         -> geladenes Projekt, in dem KEIN Licht mehr vorkommt:
 *                   der Nutzer hat sie gelöscht, also aus der Szene entfernen
 *
 * Das zu verwechseln heißt: Gelöschte Lichter kommen beim nächsten Laden wieder.
 * Deshalb `!== undefined && !== null` und nicht bloß ein Wahrheitstest.
 */
export class Szenenlichter {

    /** Die vier Lichter der Grundszene und ihre Felder im Zustand. */
    static LICHTER = [
        { name: 'Key Light', ref: 'sceneKeyLight' },
        { name: 'Fill Light', ref: 'sceneFillLight' },
        { name: 'Back Light', ref: 'sceneBackLight' },
        { name: 'Ambient', ref: 'sceneAmbient' },
    ];

    /** Spuren anlegen und gespeicherte Werte übernehmen. */
    static spurenAnlegen() {
        const gespeichert = state.project._pendingSceneOverrides?.sceneLights;
        const ausSave = gespeichert !== undefined && gespeichert !== null;
        for (const { name, ref } of Szenenlichter.LICHTER) {
            const licht = state[ref];
            if (!licht) continue;
            if (ausSave && !(name in gespeichert)) {
                Szenenlichter._entfernen(licht, ref);
                continue;
            }
            Szenenlichter._spur(name, licht);
        }
        Szenenlichter.uebernehmen(gespeichert);
        fn.updateTrackHeaders?.();
        fn.renderTimeline?.();
    }

    static _entfernen(licht, ref) {
        if (licht.target) state.scene.remove(licht.target);
        state.scene.remove(licht);
        licht.dispose?.();
        state[ref] = null;
    }

    static _spur(name, licht) {
        // Ein Richtungslicht braucht sein Ziel IN der Szene, sonst zeigt es
        // immer zum Ursprung.
        if (licht.isDirectionalLight && licht.target && !licht.target.parent) {
            state.scene.add(licht.target);
        }
        const spur = new Track(name);
        spur.type = 'light';
        spur.color = TRACK_COLORS.light || spur.color;
        spur.light = licht;
        spur.lightType = Lichtanzeiger.art(licht);
        spur.lightVisible = false;      // Helferlinien: Vorgabe aus
        spur.coneVisible = true;        // Lichtform: Vorgabe an
        spur._sceneLight = true;
        spur.lightHelper = Lichtanzeiger.helfer(licht);
        if (spur.lightHelper) state.scene.add(spur.lightHelper);
        state.project.addTrack(spur);
        return spur;
    }

    // ------------------------------------------------------- Gespeicherte Werte

    /**
     * Gespeicherte Werte auf die vorhandenen Szenenlicht-Spuren übernehmen.
     *
     * Auch mitten in einer Sitzung aufrufbar (Projekt laden, während die Spuren
     * schon stehen).
     */
    static uebernehmen(werte) {
        if (!werte) return;
        for (const spur of state.project.tracks) {
            if (!spur._sceneLight || !spur.light) continue;
            const gespeichert = werte[spur.name];
            if (!gespeichert) continue;
            Szenenlichter._lichtwerte(spur.light, gespeichert);
            Szenenlichter._spurwerte(spur, gespeichert);
            Szenenlichter._clips(spur, gespeichert);
        }
    }

    static _lichtwerte(licht, werte) {
        if (werte.color) licht.color.set(werte.color);
        if (werte.intensity != null) licht.intensity = werte.intensity;
        if (werte.position) {
            licht.position.set(werte.position.x, werte.position.y,
                               werte.position.z);
        }
        if (werte.target && licht.target) {
            licht.target.position.set(werte.target.x, werte.target.y,
                                      werte.target.z);
            licht.target.updateMatrixWorld();
        }
        for (const feld of ['angle', 'penumbra', 'distance']) {
            if (werte[feld] != null && feld in licht) licht[feld] = werte[feld];
        }
    }

    static _spurwerte(spur, werte) {
        spur.lightVisible = werte.visible ?? false;
        spur.muted = werte.muted ?? false;
        spur.light.visible = !spur.muted;
        if (spur.lightHelper) {
            spur.lightHelper.visible = spur.lightVisible && !spur.muted;
            spur.lightHelper.update?.();
        }
    }

    /**
     * Clips nur ersetzen, wenn welche gespeichert sind.
     *
     * Speicherstände vor 0.40 haben kein `clips`-Feld — dort bleibt das
     * Standardpaar stehen, sonst wäre das Licht nach dem Laden aus.
     */
    static _clips(spur, werte) {
        if (!Array.isArray(werte.clips) || werte.clips.length === 0) return;
        spur.clips = werte.clips.map(gespeichert => {
            const schluessel = new Clip(null, gespeichert.name || 'Licht', 0,
                                        state.project.fps);
            schluessel.type = 'light_kf';
            schluessel.startFrame = gespeichert.startFrame || 0;
            schluessel.data = gespeichert.data || {};
            return schluessel;
        }).sort(Lichtschluessel._reihenfolge);
    }
}
