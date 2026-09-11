/**
 * Hauteinzug — die verdeckten Ecken der Randdreiecke wandern im Shader
 * unter den Stoff.
 *
 * BEFUND (11.09.2026, Female1 in Dance1, Bild 32, nach der Hautmaske mit
 * anliegenden Kanten): Kein gezeichneter Körperpunkt lag mehr vor dem
 * Stoff — und am Bund standen trotzdem zwei feine weiße Splitter. Das sind
 * die Dreiecke, die die Maskengrenze ÜBERSPANNEN: eine Ecke verdeckt (unter
 * dem Stoff, bis 5 mm hinter der Bundkante), zwei davor. Sie bleiben
 * gezeichnet, weil nur Dreiecke mit drei verdeckten Ecken aus dem Index
 * fallen; ihr innerer Teil liegt unter dem Stoff und kommt in Bewegung
 * genauso heraus wie vorher die ganze Fläche.
 *
 * Alle drei Ecken zu verlangen ist richtig — sonst entstünde jenseits der
 * Stoffkante ein Loch von einer Dreieckslänge, sichtbar als dunkler Saum um
 * jeden Bund. Stattdessen bekommen die VERDECKTEN Ecken einen Einzug:
 * `EINZUG_M` entlang der Ruhenormale nach innen, als Attribut `einzug` und
 * im Vertex-Shader VOR dem Skinning addiert (`begin_vertex`), damit er
 * mit dem Knochen mitdreht. Ein Randdreieck kippt damit unter den Stoff —
 * am Bund sieht das aus wie ein Bund, der die Haut leicht eindrückt. Die
 * Geometrie bleibt unverändert: Messungen, Stoffgrenze, Export und
 * Speichern sehen davon nichts.
 *
 * Das Weichgewebe klont dasselbe Material später (`Shaderpatch.klonen`
 * nimmt den Einzug mit); ohne den gemeinsamen `Shaderpatch` löschte der
 * zweite Eingriff den ersten.
 */
import { THREE } from './state.js';
import { Shaderpatch } from '../gemeinsam/shaderpatch.js';
import { Hautmaskegeometrie } from '../gemeinsam/hautmaskegeometrie.js';

export class Hauteinzug {

    /** Einzug der verdeckten Ecken nach innen (Meter). */
    static EINZUG_M = 0.010;

    /**
     * Das `einzug`-Attribut aus der Maske setzen (alle Punkte, verdeckte
     * mit −EINZUG_M · Normale) und die Materialien des Netzes patchen.
     * `maske` null oder leer: kein Einzug, Attribut auf null.
     */
    static setzen(netz, maske, dreiecke) {
        const geo = netz.geometry;
        const pos = geo.attributes.position.array;
        const n = pos.length / 3;
        const werte = new Float32Array(n * 3);
        let gesetzt = 0;
        if (maske && dreiecke) {
            // Ruhenormalen nach außen (signiertes Volumen) — das
            // `normal`-Attribut des Körpers zeigt im Browser nach innen.
            const N = Hautmaskegeometrie.normalen(pos, dreiecke);
            for (let i = 0; i < n; i++) {
                if (!maske[i]) continue;
                werte[3 * i] = -Hauteinzug.EINZUG_M * N[3 * i];
                werte[3 * i + 1] = -Hauteinzug.EINZUG_M * N[3 * i + 1];
                werte[3 * i + 2] = -Hauteinzug.EINZUG_M * N[3 * i + 2];
                gesetzt += 1;
            }
        }
        const bisher = geo.getAttribute('einzug');
        if (bisher && bisher.array.length === werte.length) {
            bisher.array.set(werte);
            bisher.needsUpdate = true;
        } else {
            geo.setAttribute('einzug', new THREE.BufferAttribute(werte, 3));
        }
        Hauteinzug.patchen(netz);
        return gesetzt;
    }

    /** Die Materialien des Netzes (eines oder ein Feld) um den Einzug ergänzen. */
    static patchen(netz) {
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) {
            if (!mat || Shaderpatch.hat(mat, 'hauteinzug')) continue;
            Shaderpatch.anhaengen(mat, 'hauteinzug', (shader) => {
                Shaderpatch.hinterInclude(shader, 'common', 'attribute vec3 einzug;');
                Shaderpatch.hinterInclude(shader, 'begin_vertex', 'transformed += einzug;');
            });
        }
    }
}
