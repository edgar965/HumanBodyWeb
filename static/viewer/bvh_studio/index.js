/**
 * BVH Studio — Einstiegspunkt: Mehrspur-Editor für BVH mit Zeitleiste, Trimmen,
 * Überblenden und Export. Spuren für BVH, Kamera, Licht, Ton und Modelle.
 *
 * Hier stehen nur noch die Modul-Importe, die Tastenkürzel, die Sicherung beim
 * Verlassen und der Start. Bühne, Renderschleife, Vorgaben und Startsequenz
 * stecken in `Studiobuehne`, `Studioschleife`, `Studioeinstellungen` und
 * `Studiostart`. Vorher standen hier 146 Zeilen `init()` und 27 `animate()`.
 */
import { fn } from '../gemeinsam/registrierung.js';

// Alle Module laden, damit sie sich in der Registrierung anmelden.
import { undo, redo, undoStack } from './undo.js';
import './tracks.js';
import './zeitleiste_zeichnen.js';
import './properties.js';
import './vorschau.js';
import { Projektdatei } from './project.js';
import { Sitzung } from './sitzung.js';
import { Studiostart } from './studiostart.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

Protokoll.debug('BVH Studio', 'v2.1 geladen (ES-Module, Klassen)');

/** Wie oft der Stand gesichert wird, falls die Seite abstürzt. */
const SICHERN_MS = 30000;

/**
 * Wichtige Vorgänge auch auf dem Server protokollieren — die Konsole ist nach
 * einem Absturz weg, das Serverprotokoll nicht.
 */
function serverLog(aktion, detail, stufe) {
    Protokoll.debug('BVH Studio', `${detail ? `${aktion} — ${detail}` : aktion}`);
    fetch('/api/log/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page: 'bvh_studio', action: aktion,
                               detail: detail || '', level: stufe || 'info' }),
    // stumm gewollt: Diese Zeile IST der Protokollweg — ein Fehler dabei darf
    // die Aktion nicht aufhalten und sich nicht selbst melden wollen.
    }).catch(() => {});   // Protokoll darf nichts aufhalten
}

fn.serverLog = serverLog;

/**
 * Tastenkürzel, in der Erfassungsphase angemeldet.
 * Chrome auf QWERTZ schluckt Strg+Z/Y/M — deshalb gibt es Strg+Shift+U als
 * zweiten Weg zum Rückgängigmachen.
 */
window.addEventListener('keydown', ereignis => {
    if (!ereignis.ctrlKey) return;
    const ziel = ereignis.target;
    const inEingabe = ziel.tagName === 'INPUT' || ziel.tagName === 'TEXTAREA'
                      || ziel.isContentEditable;
    const halt = () => {
        ereignis.preventDefault();
        ereignis.stopImmediatePropagation();
    };
    if (ereignis.shiftKey && ereignis.code === 'KeyU') { halt(); undo(); return; }
    // In Eingabefeldern gehören Z und Y dem Feld.
    if (!inEingabe && ereignis.code === 'KeyZ') {
        halt();
        if (ereignis.shiftKey) redo();
        else undo();
        return;
    }
    if (!inEingabe && ereignis.code === 'KeyY') { halt(); redo(); return; }
    if (ereignis.code === 'KeyS') { ereignis.preventDefault(); Projektdatei.speichern(); return; }
    if (ereignis.code === 'KeyO') { ereignis.preventDefault(); Projektdatei.laden(); }
}, true);

// Zugänge für die Fehlersuche in der Konsole.
window.__studioUndo = undo;
window.__studioRedo = redo;
window.__undoStack = undoStack;

window.addEventListener('beforeunload', Sitzung.sichern);
// dauerhaft gewollt: Absturzsicherung. Beim regulären Verlassen greift der
// `beforeunload`-Zuhörer darüber; dieses Intervall fängt den Fall ab, dass der
// Browser abstürzt oder der Tab hart geschlossen wird.
setInterval(Sitzung.sichern, SICHERN_MS);

// Doppelten Start verhindern — das Modul wird von mehreren Seiten geladen.
if (!window.__bvhStudioInitialized) {
    window.__bvhStudioInitialized = true;
    new Studiostart().starten();
}
