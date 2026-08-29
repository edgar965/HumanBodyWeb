/**
 * BVH Studio — BVH Library management (sidebar tree, context menus, file ops).
 *
 * UMBAU 17.08.2026: Diese Datei hatte 329 Zeilen und vier Aufgaben. Jetzt ist sie
 * der Einstieg, und jede Aufgabe hat ihre Klasse:
 *
 *     bibliotheksbaum.js    der Ordnerbaum samt Zustand (offen, ausgewählt)
 *     bibliothekablage.js   die Dateioperationen am Endpunkt
 *     bibliothekmenues.js   Kontextmenüs und Werkzeugleiste
 *     panelbreiten.js       die ziehbaren Seitenleisten — gehörte nie hierher
 *
 * Die Namen nach außen bleiben gleich (`loadLibrary`, `setupLibraryManagement`,
 * `setupSidebarResize`, `getLibSelectedItem`, `setLibSelectedItem`): `studiostart.js`
 * und `zeitleiste_ziehen.js` importieren sie.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { Bibliothekmenues } from './bibliothekmenues.js';
import { Bibliotheksbaum } from './bibliotheksbaum.js';
import { Panelbreiten } from './panelbreiten.js';

/**
 * EINE Bibliothek je Seite. Der Zustand (offene Ordner, Auswahl) muss zwischen
 * Baum und Menüs geteilt werden — deshalb hier eine Instanz und nicht je
 * Aufrufer eine neue.
 */
const baum = new Bibliotheksbaum();

export function getLibSelectedItem() { return baum.auswahl; }
export function setLibSelectedItem(wert) { baum.auswahl = wert; }

export async function loadLibrary(nachher) { return baum.laden(nachher); }

export function setupLibraryManagement() {
    new Bibliothekmenues(baum).binden();
}

export function setupSidebarResize() {
    Panelbreiten.binden();
}

// Register functions in registry
fn.deleteSelectedLibItem = () => new Bibliothekmenues(baum).auswahlLoeschen();
fn.renameSelectedLibItem = () => new Bibliothekmenues(baum).auswahlUmbenennen();
