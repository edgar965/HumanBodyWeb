/**
 * Mesh3daiansichtart — eine Ansichtsart (`Mesh3daimaterial.MODI`) auf ein fertiges Objekt legen (24.10.2026, Testseite: Netz des Tests, gehäutete Figur, Stücke der Karte).
 * Die Jobseite baut ihre Flächen bei jedem Zeichnen neu (`Mesh3daiechtmaterial.netz`); die Testseite hält sie fertig. Hier: eine Kopie mit DENSELBEN Geometrien und den Materialien der Art
 * (`Mesh3daiechtmaterial`, geteilt) — „Textur“ gibt das Objekt selbst zurück, mit seinen Bildern bzw. Farben je Punkt.
 */
import { Mesh3daiechtmaterial } from './mesh3daiechtmaterial.js';

export class Mesh3daiansichtart {
    /** @param {THREE.Object3D} objekt Netz, Gruppe oder Szene @param {string} modus @returns {THREE.Object3D} */
    static anwenden(objekt, modus) {
        if (modus === 'textur') return objekt;
        const kopie = objekt.clone();
        const netze = [];
        kopie.traverse(o => { if (o.isMesh) netze.push(o); });
        for (const o of netze) {
            const ersatz = Mesh3daiechtmaterial.netz(o.geometry, modus);
            ersatz.position.copy(o.position);
            ersatz.quaternion.copy(o.quaternion);
            ersatz.scale.copy(o.scale);
            if (o === kopie) return ersatz;
            o.parent.add(ersatz);
            o.parent.remove(o);
        }
        return kopie;
    }
}
