import { Saumschnitt } from './saumschnitt.js';
import { Hautwege } from './hautwege.js';

/**
 * Saumband — verdeckte Haut neben der gezeichneten bleibt gezeichnet,
 * versenkt.
 *
 * BEFUND (Edgar, 13.09.2026, Bild vom Ärmel des anliegenden T-Shirts in
 * einer Tanzpose des BVH Studios: „bei den Ärmeln gibt es noch fehler.
 * Offenbar wird kein Skin erzeugt unter dem T-Shirt, dann kommt der Ärmel
 * von der anderen Körperseite durch"): Die Maske entfernt die Haut unter
 * dem Stoff. In der Pose (`0001_Dance`, Bild 344, Arm gebeugt) liegt der
 * Ärmel an der Unterseite des Oberarms nicht mehr vor der Haut — von unten
 * sieht man durch das Loch in der Haut auf die Innenseite der oberen
 * Ärmelwand, im Studio hell (zweiseitiges Material). Die Treppen im Bild
 * sind die Grenze des entfernten Bereichs auf dem groben Armnetz (Vierecke
 * um 1 cm). Ein erstes Band von 40 mm hinter der gezeichneten Haut (vom
 * Nachmittag) reichte nicht: Das Loch begann dahinter, 5–8 cm vom Saum.
 *
 * DER WEG: Verdeckte Haut bis `BAND_M` (auf der Haut entlang) neben der
 * gezeichneten Haut wird weiter gezeichnet, aber nach innen versenkt —
 * `Saumschnitt.UNTERKANTE_M` gleich an der Grenze, dann `STEIGUNG` je
 * Meter, höchstens `TIEFE_M` (der Einzug, den die Randecken schon immer
 * bekamen). Versenkte Haut kann nicht durch den Stoff kommen, solange er
 * nicht tiefer eindringt als sie liegt: Der Bund der 2-mm-Leggings kam in
 * Dance1 2–5 mm tief heraus (`hautmaske.js`); mit Steigung 1 liegt die
 * Haut ab 4 mm hinter der Grenze tiefer als das. Entfernt wird nur, was
 * weiter als `BAND_M` von jeder gezeichneten Haut liegt — Knie und Becken
 * unter der Leggings (dort kam der Stoff bis 29 mm tief), nicht mehr der
 * Oberarm im Ärmel.
 *
 * Der Abstand läuft auf der Haut entlang (`Hautwege`, Dijkstra von allen
 * gezeichneten Punkten, Nähte mit doppelten Punkten verbunden): Über einen
 * Spalt hinweg (Achsel, Schritt) misst ein Raumabstand zu kurz, und hinter
 * dem freien Streifen einer lockeren Kante beginnt die Versenkung so sanft
 * am Streifen statt mit einem Zahn von einem Zentimeter.
 *
 * Ohne Three.js, damit `test_js_saumband` es in Node prüft.
 */
export class Saumband {

    /** So weit (auf der Haut) neben der gezeichneten Haut bleibt verdeckte
     *  Haut gezeichnet. 15 cm: Der Ärmelsaum liegt 12 cm von der Achsel. */
    static BAND_M = 0.15;
    /** Versenkung je Meter Abstand zur gezeichneten Haut (1 mm je mm). */
    static STEIGUNG = 1.0;
    /** Tiefste Versenkung — der Einzug der Randecken. */
    static TIEFE_M = 0.010;

    /**
     * Je Punkt der Weg auf der Haut zum nächsten gezeichneten Punkt (Meter):
     * 0 für gezeichnete, `Infinity` jenseits von `BAND_M`.
     * @param pos       Punkte xyz (Ruhelage)
     * @param maske     1 = verdeckt
     * @param dreiecke  der volle Index
     */
    static abstaende(pos, maske, dreiecke) {
        const quellen = [];
        for (let i = 0; i < maske.length; i++) if (!maske[i]) quellen.push(i);
        return Hautwege.wege(pos, dreiecke, quellen, Saumband.BAND_M);
    }

    /** Je Punkt 1, wenn verdeckt UND jenseits des Bands — nur Dreiecke mit
     *  drei solchen Ecken fallen aus dem Index. */
    static weg(maske, abstaende) {
        const aus = new Uint8Array(maske.length);
        for (let i = 0; i < maske.length; i++) {
            if (maske[i] && !(abstaende[i] <= Saumband.BAND_M)) aus[i] = 1;
        }
        return aus;
    }

    /** Die Versenkung (Meter) eines verdeckten Punkts im Abstand `d`. */
    static tiefe(d) {
        return Math.min(Saumband.TIEFE_M, Saumschnitt.UNTERKANTE_M + Saumband.STEIGUNG * d);
    }
}
