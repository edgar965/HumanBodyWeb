import { getProject, types } from '@theatre/core';
import studio from '@theatre/studio';
import { state } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Theatre.js-Studio-Editor für die Kamera — die Drittanbieter-Drag-Oberfläche
 * aus Theatre, hier an Studios eigene Kamera gebunden statt Theatres eigener
 * (Vorbild: `TheatreJS/src/theatre-bridge.js` `createCameraSheet()` und
 * `TheatreJS/src/studio/studiostart.js`).
 *
 * NUR DIE KAMERA, NICHT DIE LICHTER: Theatre bindet dort DREI FESTE
 * Bühnenlichter fest an das Sheet. Studios Lichter sind dagegen dynamische,
 * projektabhängige Spuren (`state.project.lightTracks`) — beim Laden der
 * Seite existieren noch keine, und sie können sich jederzeit ändern
 * (Projekt laden, Spur hinzufügen/löschen). Theatre.js verlangt aber, dass
 * `studio.initialize()` auf MODULEBENE läuft und Objekte fest angemeldet
 * werden ("nach DOMContentLoaded ist es zu spät" — `studiostart.js`); eine
 * Anmeldung, die bei jedem Spurwechsel neu binden müsste, wäre brüchig und
 * zeigte nach einem Projektwechsel auf tote Objekte. Die Kamera dagegen ist
 * über die ganze Sitzung dieselbe Instanz (`state.camera`, einmal gebaut in
 * `Studiobuehne.bauen()`) — dafür passt Theatres Modell tatsächlich.
 *
 * WARUM `cameraActive` beim Öffnen ausgeschaltet wird: `applyPlayhead()`
 * (playback.js) setzt die Kamera aus der aktiven Zeitleisten-Spur bei jeder
 * Zustandsänderung neu — ohne das würde die nächste Änderung die von Hand
 * gesetzte Position sofort wieder überschreiben (dieselbe Konfliktklasse wie
 * in `globale_sichtbarkeit.js`, hier über den vorhandenen Schalter gelöst
 * statt über einen neuen Haken in `applyPlayhead()`).
 *
 * WARUM ABGEFRAGT STATT `obj.onValuesChange()`: In dieser Einbettung (zwei
 * getrennt gebaute Vendor-Dateien, `static/vendor/theatre/`, siehe
 * `TheatreJS/vite.vendor-theatre.config.js`) liefert `obj.value` nach einem
 * `studio.transaction(...)` sofort den neuen Wert — der Push-Callback
 * `onValuesChange` feuert dagegen nur EINMAL beim Registrieren und nie
 * wieder (geprüft in der Konsole: `obj.value` ändert sich, der Callback
 * bleibt stumm). Vermutlich fehlt der Theatre.js-Ticker, der in Theatres
 * eigenem App-Bau `TheatreJS/src/main.js` als Teil EINES Bündels mitläuft.
 * Statt die Bündel-Trennung aufzugeben, wird der Wert abgefragt — robust
 * unabhängig von der Ursache, nur währenddessen die Leiste offen ist.
 */
export class TheatrejsEditor {

    static WURZEL = 'theatrejs-studio-root';
    static AUFBAU_MS = 100;

    static _sheet = null;
    static _cameraObj = null;
    static _sichtbar = false;
    static _cameraActiveVorher = null;
    static _abfrageId = null;

    /** `studio.initialize()` — MUSS auf Modulebene laufen, siehe oben. */
    static hochfahren() {
        studio.initialize().then(() => {
            studio.ui.hide();
            setTimeout(() => TheatrejsEditor._zurechtruecken(), TheatrejsEditor.AUFBAU_MS);
        }).catch(fehler =>
            Protokoll.fehler('Theatre.js Editor', 'initialize() fehlgeschlagen', fehler));
    }

    /** Kamera als Theatre-Objekt anmelden — erst aufrufen, wenn `state.camera` existiert. */
    static kameraRegistrieren() {
        const project = getProject('BVH Studio Kamera');
        TheatrejsEditor._sheet = project.sheet('Kamera');
        const kamera = state.camera;
        const obj = TheatrejsEditor._sheet.object('Kamera', {
            position: types.compound({
                x: types.number(kamera.position.x, { range: [-50, 50] }),
                y: types.number(kamera.position.y, { range: [-10, 20] }),
                z: types.number(kamera.position.z, { range: [-50, 50] }),
            }),
            fov: types.number(kamera.fov, { range: [10, 120] }),
        });
        TheatrejsEditor._cameraObj = obj;
        // Maus-Orbit soll sich im Panel widerspiegeln — sonst zeigt es beim
        // Öffnen veraltete Werte, solange nicht am Regler selbst gezogen wurde.
        state.controls?.addEventListener('change', () => {
            if (!TheatrejsEditor._sichtbar) return;
            studio.transaction(({ set }) => {
                set(obj.props.position.x, state.camera.position.x);
                set(obj.props.position.y, state.camera.position.y);
                set(obj.props.position.z, state.camera.position.z);
            });
        });
    }

    /** Knopf „Theatre.js Studio ein/ausblenden" — liefert den neuen Zustand. */
    static sichtbarkeitUmschalten() {
        TheatrejsEditor._sichtbar = !TheatrejsEditor._sichtbar;
        if (TheatrejsEditor._sichtbar) {
            studio.ui.restore();
            if (TheatrejsEditor._sheet) studio.setSelection([TheatrejsEditor._sheet]);
            const spuren = state.project.cameraTracks;
            TheatrejsEditor._cameraActiveVorher = spuren.map(spur => spur.cameraActive);
            for (const spur of spuren) spur.cameraActive = false;
            TheatrejsEditor._abfrageStarten();
        } else {
            studio.ui.hide();
            const spuren = state.project.cameraTracks;
            spuren.forEach((spur, i) => {
                spur.cameraActive = TheatrejsEditor._cameraActiveVorher?.[i] ?? spur.cameraActive;
            });
            TheatrejsEditor._cameraActiveVorher = null;
            TheatrejsEditor._abfrageStoppen();
        }
        return TheatrejsEditor._sichtbar;
    }

    /** Pro Bild den Theatre-Wert auf die Kamera anwenden (siehe WARUM oben). */
    static _abfrageStarten() {
        TheatrejsEditor._abfrageStoppen();
        const schritt = () => {
            const obj = TheatrejsEditor._cameraObj;
            if (obj) {
                const werte = obj.value;
                state.camera.position.set(werte.position.x, werte.position.y, werte.position.z);
                state.camera.fov = werte.fov;
                state.camera.updateProjectionMatrix();
            }
            TheatrejsEditor._abfrageId = requestAnimationFrame(schritt);
        };
        schritt();
    }

    static _abfrageStoppen() {
        if (TheatrejsEditor._abfrageId != null) cancelAnimationFrame(TheatrejsEditor._abfrageId);
        TheatrejsEditor._abfrageId = null;
    }

    /**
     * Das Wurzelelement in Studios eigenes Layout einpassen — rechtes
     * Eigenschaften-Feld statt über der ganzen Seite (Vorbild:
     * `Studiostart._zurechtruecken()`, Werte an Studio statt Theatre angepasst).
     */
    static _zurechtruecken() {
        const wurzel = document.getElementById(TheatrejsEditor.WURZEL);
        if (!wurzel) return;
        wurzel.style.setProperty('z-index', '850', 'important');
        wurzel.style.setProperty('position', 'fixed', 'important');
        wurzel.style.setProperty('pointer-events', 'none', 'important');
        wurzel.style.top = '40px';
        wurzel.style.left = '300px';
        wurzel.style.right = '0';
        wurzel.style.bottom = '0';
        if (wurzel.shadowRoot) {
            const stil = document.createElement('style');
            stil.textContent = `
                [data-testid="SequenceEditor"],
                [data-testid="GlobalToolbar"] { pointer-events: auto !important; }
                div[class] > div[class]:nth-child(3),
                div[class] > div[class]:nth-child(4) { pointer-events: auto !important; }
                [data-radix-popper-content-wrapper], [data-radix-menu-content],
                [role="menu"], [role="dialog"] {
                    pointer-events: auto !important; z-index: 99999 !important;
                }
            `;
            wurzel.shadowRoot.prepend(stil);
        }
    }
}

TheatrejsEditor.hochfahren();
// Zugang für die Fehlersuche in der Konsole (Vorbild: `debugzugaenge()` in
// `studiostart.js`).
window.__theatrejsEditor = TheatrejsEditor;
window.__theatrejsStudio = studio;
