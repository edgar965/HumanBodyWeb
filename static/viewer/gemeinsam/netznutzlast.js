import { float32ToBase64, uint32ToBase64 } from './kodierung.js';

/**
 * Netznutzlast — die dreizehn Felder, die jeder Export an den Server schickt.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Dieselbe Aufzählung stand in
 * `bvh_studio/export_nutzlast.js` und `scene/cloth_export.js` — Zeichen für
 * Zeichen gleich, nur die Quelle der Werte unterschied sich. Das BVH-Studio
 * legt Kamera, Lichter und Ton obendrauf, der Kleiderexport die Knochenteile.
 *
 * Das hier ist kein Aufräumen um der Ordnung willen: Die Schlüssel sind der
 * VERTRAG mit dem Server (`core/api/*` liest `positions`, `skin_indices`,
 * `inv_bind`, `anim_matrices`, …). Wer einen Namen ändert und nur eine der
 * beiden Stellen findet, bekommt einen Export, der weiter läuft und dessen
 * Ergebnis falsch ist — der Server sieht das fehlende Feld als „nicht
 * mitgeschickt", nicht als Fehler.
 *
 * Die Zählwerte werden hier GERECHNET, nicht übergeben (`vertex_count`,
 * `face_count`): Sie hängen an den Puffern daneben, und eine Zahl, die nicht
 * zu ihrem Puffer passt, ist die unangenehmste Sorte Fehler — der Server
 * liest dann über das Ende hinaus oder zu kurz.
 */
export class Netznutzlast {
    /**
     * @param {Object} teile
     * @param {string} teile.name Name der Szene
     * @param {Float32Array} teile.punkte Vertexpositionen
     * @param {Uint32Array} teile.dreiecke Indexpuffer
     * @param {Uint32Array} teile.hautindizes skinIndex, vier je Punkt
     * @param {Float32Array} teile.hautgewichte skinWeight, vier je Punkt
     * @param {Array} teile.knochennamen Reihenfolge = Index im Skelett
     * @param {Float32Array} teile.bindeinverse 16 Werte je Knochen
     * @param {Float32Array} teile.matrizen Animationsmatrizen
     * @param {number} teile.fps Bilder je Sekunde
     * @param {number} teile.bilder Anzahl der Bilder
     * @param {Object} teile.bereiche `bone_vertex_ranges`
     * @param {Object} teile.knochenteile `bone_parts`
     * @returns {Object} die Nutzlast, bereit zum Senden
     */
    static bauen({name, punkte, dreiecke, hautindizes, hautgewichte,
                  knochennamen, bindeinverse, matrizen, fps, bilder,
                  bereiche, knochenteile}) {
        return {
            scene_name: name,
            positions: float32ToBase64(punkte),
            vertex_count: punkte.length / 3,
            faces: uint32ToBase64(dreiecke),
            face_count: dreiecke.length / 3,
            skin_indices: uint32ToBase64(hautindizes),
            skin_weights: float32ToBase64(hautgewichte),
            bone_names: knochennamen,
            inv_bind: float32ToBase64(bindeinverse),
            anim_matrices: float32ToBase64(matrizen),
            anim_fps: fps,
            anim_frames: bilder,
            bone_vertex_ranges: bereiche,
            bone_parts: knochenteile || {},
        };
    }
}
