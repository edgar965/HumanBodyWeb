import * as THREE from 'three';

/**
 * Skelettanzeige — der SkeletonHelper mit den Einstellungen des Projekts.
 *
 * WARUM (Umbau 16.08.2026): Dieselben fuenf Zeilen standen DREIMAL im Projekt —
 *
 *   * TheatreJS/src/main.js beim Umwandeln zu SkinnedMesh,
 *   * ebenda beim Einschalten der Rig-Anzeige,
 *   * static/viewer/viewer/index.js im Rig-Umschalter der Viewer-Seite.
 *
 * Immer mit denselben Werten: kein Tiefentest, kein Tiefenschreiben, Farbe
 * 0x00ffaa, Linienbreite 2, renderOrder 999. Die Werte sind kein Zufall —
 * ohne abgeschalteten Tiefentest verschwindet das Rig im Koerper, und ohne die
 * hohe renderOrder zeichnet Three.js es hinter das Netz.
 */
export class Skelettanzeige {

    static FARBE = 0x00ffaa;
    static LINIENBREITE = 2;
    /** Muss ueber allem liegen, sonst steckt das Rig im Netz. */
    static REIHENFOLGE = 999;

    /**
     * Anzeige zu einem Wurzelknochen bauen und in die Szene setzen.
     * @param {THREE.Scene} scene
     * @param {THREE.Bone} wurzelknochen
     * @param {boolean} sichtbar
     * @returns {THREE.SkeletonHelper}
     */
    static bauen(scene, wurzelknochen, sichtbar = true) {
        const anzeige = new THREE.SkeletonHelper(wurzelknochen);
        anzeige.material.depthTest = false;
        anzeige.material.depthWrite = false;
        anzeige.material.color.set(Skelettanzeige.FARBE);
        anzeige.material.linewidth = Skelettanzeige.LINIENBREITE;
        anzeige.renderOrder = Skelettanzeige.REIHENFOLGE;
        anzeige.visible = sichtbar;
        scene.add(anzeige);
        return anzeige;
    }

    /**
     * Alte Anzeige entfernen und freigeben. Notwendig, wenn der Wurzelknochen
     * ausgetauscht wurde — die Anzeige haengt daran fest.
     */
    static entfernen(scene, anzeige) {
        if (!anzeige) return null;
        scene.remove(anzeige);
        anzeige.dispose();
        return null;
    }

    /** Neu bauen und die Sichtbarkeit der alten uebernehmen. */
    static erneuern(scene, anzeige, wurzelknochen) {
        const sichtbar = anzeige ? anzeige.visible : true;
        Skelettanzeige.entfernen(scene, anzeige);
        return Skelettanzeige.bauen(scene, wurzelknochen, sichtbar);
    }
}
