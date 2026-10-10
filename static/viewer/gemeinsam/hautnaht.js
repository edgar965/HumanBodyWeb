/**
 * Hautnaht — wie weit die Haut an der Naht zu einem verschweißten Ersatzstück reicht, als Faktor je Hautpunkt (09.10.2026).
 *
 * WARUM (Chrome, „cute girl", Scham verschweißt, Normalen des Stücks an die der Haut angeglichen — `stucknormalen.js`): An der Naht blieb
 * eine feine Linie. Die gebackene Haut trägt Poren und Wellen in ihrer Normalenkarte, der Rand des Stücks nicht (seine Karte ist am
 * Inselrand neutral: gesehen am Atlas `EIGEN_cute_girl_Scham_atlas_normalen.png`). Am Rand springt das Relief von „Wellen" auf „glatt";
 * mit abgeschalteten Karten verschwand die Linie fast (Chrome, 09.10.2026).
 *
 * HIER: Faktor 1 an den Ringpunkten der Haut, nach `BAND_M` Weg über das Netz 0 (Hermite). Der Shader (`hautnahtpatch.js`) nimmt der
 * Haut dort das Relief zurück — am Ring fast ganz, nach `BAND_M` ist es wieder voll. Der Weg läuft über die Kanten der Haut
 * (`Hautwege`), nicht durch den Raum: die Gegenseite einer Falte bleibt unberührt.
 *
 * Ohne Three.js und ohne DOM (Node-Test `test_js_hautnaht.py`).
 */
import { Hautwege } from './hautwege.js';

export class Hautnaht {

    /** So weit (m) über die Haut klingt der Faktor aus — etwas mehr als das Band, in dem das Stück zur Haut hin angeglichen wird. */
    static BAND_M = 0.012;

    /**
     * @param pos          Punkte der Haut (Ruhelage), xyz
     * @param index        Dreiecksindex der Haut (voll)
     * @param ringPunkte   Punktnummern der Haut auf dem Ring (alle verschweißten Stücke)
     * @returns Float32Array, ein Wert 0…1 je Hautpunkt
     */
    static faktor(pos, index, ringPunkte) {
        const aus = new Float32Array(pos.length / 3);
        if (!ringPunkte.length) return aus;
        const weg = Hautwege.wege(pos, index, Array.from(ringPunkte), Hautnaht.BAND_M);
        for (let i = 0; i < aus.length; i++) {
            if (!(weg[i] < Hautnaht.BAND_M)) continue;
            const t = weg[i] / Hautnaht.BAND_M;
            aus[i] = 1 - t * t * (3 - 2 * t);
        }
        return aus;
    }
}
