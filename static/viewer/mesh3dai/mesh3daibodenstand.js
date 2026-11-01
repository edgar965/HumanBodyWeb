/**
 * Mesh3daibodenstand — die bewegte Ergebnisfigur mit ihrem tiefsten Punkt auf den Boden (31.10.2026, Edgar zu koenigin1: „nach unten gehen die Füsse und das Kleid durch den boden“).
 *
 * Gemessen im Tanz A_Results/DanceKurz ohne Bodenstand (Testseite, `computeBoundingBox` des gehäuteten Körpers): edgar bis 157 mm unter y = 0 (Bild 188), koenigin1 bis 141 mm, Zehenknochen
 * −115 mm bei einem Knöchel 28 mm über dem Boden — der Retarget auf Genesis 9 hält den Fuß nicht am Boden, bei jeder Figur. Dasselbe Werkzeug wie die Charakter-Seite (`Bodenstand`,
 * `Koerpertiefe`: jeder gehäutete Punkt des Körpers), dazu die Schuhe aus dem Kostüm — ihr Absatz liegt unter der Sohle der Figur.
 */
import { Koerpertiefe } from '../charakter/koerpertiefe.js';

export class Mesh3daibodenstand {
    /**
     * Die Wurzel heben oder senken, bis der tiefste Punkt von Körper und sichtbaren Schuhen auf y = 0 liegt; → Verschiebung (m), 0 ohne Wurzel oder Netz.
     * @param modell `Genesis9Modell` der Bewegung
     * @param kleider `[{mesh, art}]` (`Mesh3daifigurbewegung.kleider`)
     */
    static richten(modell, kleider) {
        const wurzel = modell?.skelett?.rootBone;
        if (!wurzel) return 0;
        wurzel.updateWorldMatrix(true, true);
        let tiefste = Infinity;
        const schuhe = (kleider || []).filter(k => k.art === 'schuh' && k.mesh.visible).map(k => k.mesh);
        for (const netz of [modell.bodyMesh, ...schuhe]) if (Koerpertiefe.messbar(netz)) tiefste = Math.min(tiefste, Koerpertiefe.netzY(netz));
        if (!isFinite(tiefste) || tiefste === 0) return 0;
        wurzel.position.y -= tiefste;
        wurzel.updateWorldMatrix(false, true);
        return tiefste;
    }
}
