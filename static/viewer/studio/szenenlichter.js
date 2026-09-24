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
 *
 * DRITTER FALL SEIT DER AMBIENT-SPUR (24.09.2026)
 * ================================================
 * Ein VOR diesem Tag gespeichertes Projekt hat gar kein `"Ambient"`-Feld —
 * die Spur gab es beim Speichern noch nicht. Ohne Sonderfall sähe das genau
 * wie „Nutzer hat Ambient gelöscht" aus, und das Licht verschwände beim
 * ersten Laden jedes alten Projekts wieder ersatzlos.
 *
 * VIERTER FALL: EIN ZWISCHENSTAND ÜBERLEBT DIE NÄCHSTE ÄNDERUNG
 * ===============================================================
 * Derselbe Tag, zwei Änderungen kurz hintereinander: Die Ambient-Spur kam
 * zuerst mit `coneVisible: true` (Vorgabe wie bei den anderen drei), erst
 * danach auf `false` (die Lichtform lag sonst sichtbar bei (0,0,0) — Three.js
 * setzt ein AmbientLight immer dorthin — mitten in der Figur, Edgar-Bild:
 * Platte unter den Füßen). Dazwischen lief eine Sitzung, die den ersten Stand
 * (`coneVisible: true`) in `sessionStorage` einfror — jeder Reload holte ihn
 * zurück und überschrieb den neuen Code-Default. „Speichern schlägt Code"
 * gilt nur, wenn der Nutzer den Wert WIRKLICH gewählt hat, nicht wenn er nur
 * der zufällige Stand zwischen zwei Fixes war.
 *
 * `__ambientFassung` (`projekt_daten.js`) macht beide Fälle unterscheidbar:
 * fehlt sie, kennt der Speicherstand „Ambient" noch gar nicht (→ Fall drei);
 * steht sie unter `CONE_FASSUNG`, kennt er die Spur, aber noch nicht deren
 * `coneVisible`-Vorgabe (→ dieser vierte Fall: den gespeicherten Wert für
 * GENAU dieses eine Feld verwerfen, alles andere normal übernehmen).
 */
export class Szenenlichter {

    /** Die vier Lichter der Grundszene und ihre Felder im Zustand. */
    static LICHTER = [
        { name: 'Key Light', ref: 'sceneKeyLight' },
        { name: 'Fill Light', ref: 'sceneFillLight' },
        { name: 'Back Light', ref: 'sceneBackLight' },
        { name: 'Ambient', ref: 'sceneAmbient' },
    ];

    /** Fassung von `sceneLights` — bei jeder Migration hier hochzählen. */
    static AMBIENT_FASSUNG = 1;      // ab hier: die Spur selbst existiert
    static CONE_FASSUNG = 2;         // ab hier: coneVisible-Vorgabe = aus

    /** Spuren anlegen und gespeicherte Werte übernehmen. */
    static spurenAnlegen() {
        const gespeichert = state.project._pendingSceneOverrides?.sceneLights;
        const ausSave = gespeichert !== undefined && gespeichert !== null;
        const fassung = ausSave ? (gespeichert.__ambientFassung || 0) : Infinity;
        // Migration: ein Speicherstand von VOR der Ambient-Spur kennt sie
        // nicht — das darf nicht als „gelöscht" gelten (siehe Klassenkommentar).
        const altOhneAmbient = ausSave && fassung < Szenenlichter.AMBIENT_FASSUNG;
        for (const { name, ref } of Szenenlichter.LICHTER) {
            const licht = state[ref];
            if (!licht) continue;
            const fehltImSave = ausSave && !(name in gespeichert);
            if (fehltImSave && !(name === 'Ambient' && altOhneAmbient)) {
                Szenenlichter._entfernen(licht, ref);
                continue;
            }
            Szenenlichter._spur(name, licht);
        }
        Szenenlichter.uebernehmen(gespeichert, fassung);
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
        // Lichtform: Vorgabe an — außer bei Ambient. Three.js erzeugt ein
        // AmbientLight immer auf (0,0,0), also mitten in der Szene: die Form
        // (`lichtanzeiger.js`, flaches Rechteck) läge sonst sichtbar in der
        // Figur (24.09.2026, Edgar-Bild: Platte unter den Füßen). Per Kästchen
        // in der Licht-Leiste bleibt sie trotzdem zuschaltbar.
        spur.coneVisible = !licht.isAmbientLight;
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
     * schon stehen) — dann ohne `fassung` (Vorgabe: aktuell, nichts verwerfen).
     */
    static uebernehmen(werte, fassung = Infinity) {
        if (!werte) return;
        for (const spur of state.project.tracks) {
            if (!spur._sceneLight || !spur.light) continue;
            const gespeichert = werte[spur.name];
            if (!gespeichert) continue;
            Szenenlichter._lichtwerte(spur.light, gespeichert);
            Szenenlichter._spurwerte(spur, gespeichert, fassung);
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

    static _spurwerte(spur, werte, fassung = Infinity) {
        spur.lightVisible = werte.visible ?? false;
        // Lichtkegel: gespeichert seit je (`Projektdaten._lichter`), gelesen
        // erst seit dem 11.09.2026 (Edgar: „Lichtkegel (aus) gesetzt und
        // projekt gespeichert, beim neu laden war der alte Status"). Beim
        // Szenen-Ambient NUR ab `CONE_FASSUNG` übernehmen (siehe Klassenkommentar,
        // „vierter Fall") — davor bleibt es beim `_spur()`-Default (aus).
        const ignorieren = spur.light?.isAmbientLight
                          && fassung < Szenenlichter.CONE_FASSUNG;
        spur.coneVisible = ignorieren ? false : (werte.coneVisible ?? true);
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
