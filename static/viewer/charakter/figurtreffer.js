import { state } from './state.js';
import { Raycastbeschleunigung } from '../gemeinsam/raycastbeschleunigung.js';

/**
 * Figurtreffer — was unter dem Zeiger liegt: die Treffer auf allen sichtbaren Netzen aller Figuren, nächster zuerst,
 * jedes Netz mit `userData._parentCharId`.
 *
 * Aus `bindCanvasClick` herausgelöst (18.10.2026), als der Rechtsklick auf die Figur (`Figurkontextmenue`) dieselbe
 * Frage stellte — zwei Fassungen derselben Netzliste wären die Fehlerklasse „DIESELBEN LISTEN, ZWEIMAL".
 */
export class Figurtreffer {

    static unter(ereignis) {
        const canvas = state.canvas;
        const rect = canvas.getBoundingClientRect();
        state.mouse.x = ((ereignis.clientX - rect.left) / rect.width) * 2 - 1;
        state.mouse.y = -((ereignis.clientY - rect.top) / rect.height) * 2 + 1;
        state.raycaster.setFromCamera(state.mouse, state.camera);

        const meshes = [];
        state.characters.forEach((inst, id) => {
            inst.group.traverse(child => {
                // Unsichtbares (die ruhende Simulationskopie eines dForce-Stücks)
                // fängt keinen Klick — der Raycaster fragt `visible` nicht selbst.
                if (child.isMesh && child.visible && !child.userData._boneOverlay) {
                    child.userData._parentCharId = id;
                    meshes.push(child);
                }
            });
        });

        Raycastbeschleunigung.sicherstellen(meshes);
        return state.raycaster.intersectObjects(meshes, false);
    }

    /** Die Kennung der Figur unter dem Zeiger, sonst `null`. */
    static figur(ereignis) {
        const hits = Figurtreffer.unter(ereignis);
        return hits.length ? hits[0].object.userData._parentCharId || null : null;
    }
}
