/**
 * Viewer — SMPL Body + SMPL Garment Library + Scene UI (Szene tab).
 *
 * UMBAU 18.08.2026: 393 Zeilen. Jetzt:
 *
 *     smpl_kleiderliste.js  Katalog, Auswahl, Knöpfe
 *     smpl_kleidernetz.js   Netz laden, an die Figur anpassen, entfernen
 *     smpl_koerperfrage.js  der Körperteil der Anpassfrage (zwei Seiten!)
 *     smpl_koerper.js       Formregler, Körpernetz, gespeicherte Einstellungen
 *     smpl_licht.js         Beleuchtung, Belichtung, Kamera des Reiters „Szene"
 *
 * Hier bleiben die drei Namen, die `index.js` und die Registrierung aufrufen.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { Smplkleiderliste } from './smpl_kleiderliste.js';
import { Smplkleidernetz } from './smpl_kleidernetz.js';
import { Smplkoerper } from './smpl_koerper.js';

export async function loadSmplGarmentUI() {
    return Smplkleiderliste.aufbauen();
}

export async function initSmplBodyUI() {
    return Smplkoerper.aufbauen();
}

export function removeSmplGarment(garmentId) {
    Smplkleidernetz.entfernen(garmentId);
}

fn.loadSmplGarmentUI = loadSmplGarmentUI;
fn.initSmplBodyUI = initSmplBodyUI;
fn.removeSmplGarment = removeSmplGarment;
