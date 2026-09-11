import * as THREE from 'three';
import { Groessenangleich }
    from '../../../static/viewer/gemeinsam/groessenangleich.js';

/**
 * Figurlage — wo eine neu geladene Figur steht und wie groß sie ist.
 *
 * Das Gegenstück zu `scene/figurplatzierung.js` für die Theatre-Bühne
 * (11.09.2026, mit dem Figurwahl-Dialog). Der Dialog liefert `{x, angleichen,
 * vorbildHoehe}`; hier wird es angewandt — VOR der Theatre-Anmeldung, damit
 * Theatre.js die Lage als Startwert kennt und nicht beim ersten Setzen der
 * Werte auf den Ursprung zurückstellt.
 *
 * Gemessen wird über die Bounding-Box. Das genügt für HumanBody-Figuren (die
 * Morphs sind im Netz eingerechnet) und für eine frisch geladene GLB in
 * Ruhelage; die Entscheidung, ob der Unterschied überhaupt zählt, trifft
 * `Groessenangleich`.
 */
export class Figurlage {

    /** Sichtbare Höhe einer Gruppe in Metern; 0, wenn nichts zu messen ist. */
    static hoehe(gruppe) {
        if (!gruppe) return 0;
        gruppe.updateMatrixWorld(true);
        const kasten = new THREE.Box3().setFromObject(gruppe);
        if (kasten.isEmpty() || !isFinite(kasten.min.y) || !isFinite(kasten.max.y)) return 0;
        const hoch = kasten.max.y - kasten.min.y;
        return hoch > 0 ? hoch : 0;
    }

    /**
     * Lage anwenden. Liefert den Skalierungsfaktor (1 = unverändert).
     * @param {THREE.Group} gruppe
     * @param {Object} lage  {x, angleichen, vorbildHoehe}
     */
    static anwenden(gruppe, lage) {
        if (!gruppe || !lage) return 1;
        if (Number.isFinite(Number(lage.x))) gruppe.position.x = Number(lage.x);
        let faktor = 1;
        if (lage.angleichen && lage.vorbildHoehe > 0) {
            faktor = Groessenangleich.faktor(Figurlage.hoehe(gruppe), lage.vorbildHoehe);
            if (faktor !== 1) gruppe.scale.multiplyScalar(faktor);
        }
        return faktor;
    }
}
