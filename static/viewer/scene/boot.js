/**
 * Scene Editor — Einstiegspunkt.
 *
 * Hier stehen nur noch die Modul-Importe (jedes Modul meldet beim Laden seine
 * Funktionen in der Registrierung an) und der Aufruf des Aufbaus. Bühne,
 * Renderschleife, Einstellungen und Startsequenz stecken in `Szenenbuehne`,
 * `Szenenschleife`, `Starteinstellungen` und `Szenenaufbau`. Vorher standen
 * hier 169 Zeilen `init()` und 43 Zeilen `animate()`.
 */
import { buildRigifySkeleton } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

// Alle Module laden, damit sie sich in der Registrierung anmelden.
import './undo.js';
import './session.js';
import './utils.js';
import './skeleton.js';
import './character.js';
import './interaction.js';
import './lighting.js';
import './menubar.js';
import './save_load.js';
import './properties.js';
import './garments.js';
import './prop_garments.js';
import './pose_apply.js';
import './hair.js';
import './cloth.js';
import './animation.js';
import './kleider.js';
import './modellgenerator_ui.js';
import './mh_proxy.js';
import './rigging.js';
import './charmorph.js';
import './cloth_export.js';
import { Szenenaufbau } from './szenenaufbau.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

// Die Menüleiste schaltet das Rig darüber ein und aus.
fn.buildRigifySkeleton = buildRigifySkeleton;

Protokoll.debug('Scene Editor', 'v2.1 geladen (ES-Module, Klassen)');

/** Rückgängig: Strg+Shift+U, vor allen anderen Tastenkürzeln. */
window.addEventListener('keydown', ereignis => {
    if (!ereignis.ctrlKey || !ereignis.shiftKey || ereignis.code !== 'KeyU') return;
    ereignis.preventDefault();
    ereignis.stopImmediatePropagation();
    fn.sceneUndo?.();
}, true);

fn.initDialogCloseHandlers();

export async function init() {
    return new Szenenaufbau().starten();
}
