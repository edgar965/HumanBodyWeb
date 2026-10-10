/**
 * Hautnahtpatch — der Haut an der Naht zu einem verschweißten Ersatzstück das Relief teilweise zurücknehmen (09.10.2026).
 *
 * Der Faktor je Punkt kommt aus `hautnaht.js`; hier steht, was das Netz betrifft: das Attribut `nahtf` und der Eingriff in den
 * Shader (`Shaderpatch`, damit er neben Einzug, Weichgewebe und Genesis-Haut besteht). Im Fragment-Shader wird die Normale nach
 * allen Karten (Haut-Normalenkarte, Detail, Glitzer) wieder ein Stück zur unverformten Flächennormale (`nonPerturbedNormal`) gezogen:
 * `normal = mix(nonPerturbedNormal, normal, 1 − RELIEF_WEG · nahtf)`. Ohne das Attribut (andere Netzstufe, Stück abgelegt) steht
 * `nahtf` auf 0 (WebGL: unbelegtes Attribut = Konstante 0) — dann ändert sich nichts.
 */
import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';

export class Hautnahtpatch {

    /** Anteil des Reliefs, der am Ring selbst wegfällt (Faktor 1). Setzung, kein Messwert: 0,85 lässt noch einen Rest von 15 %. */
    static RELIEF_WEG = 0.85;
    static SCHLUESSEL = 'hautnaht';

    /** Das Attribut `nahtf` am Netz setzen (oder überschreiben) und die Materialien patchen. */
    static eintragen(netz, faktor) {
        const geo = netz.geometry;
        const bisher = geo.getAttribute('nahtf');
        if (bisher && bisher.array.length === faktor.length) {
            bisher.array.set(faktor);
            bisher.needsUpdate = true;
        } else {
            geo.setAttribute('nahtf', new THREE.BufferAttribute(Float32Array.from(faktor), 1));
        }
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) {
            if (!mat || Shaderpatch.hat(mat, Hautnahtpatch.SCHLUESSEL)) continue;
            Shaderpatch.anhaengen(mat, Hautnahtpatch.SCHLUESSEL, Hautnahtpatch.eingriff);
        }
    }

    /** Den Eingriff wieder abnehmen (kein verschweißtes Stück mehr): Attribut weg, Shader ohne. */
    static aufheben(netz) {
        netz.geometry.deleteAttribute('nahtf');
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) if (mat) Shaderpatch.entfernen(mat, Hautnahtpatch.SCHLUESSEL);
    }

    /** Der Eingriff in den Shader: Attribut und Varying, im Fragment die Rücknahme des Reliefs vor dem Klarlack. */
    static eingriff(shader) {
        Shaderpatch.hinterInclude(shader, 'common', 'attribute float nahtf;\nvarying float vNahtF;');
        Shaderpatch.hinterInclude(shader, 'begin_vertex', 'vNahtF = nahtf;');
        const marke = '#include <common>';
        if (shader.fragmentShader.includes(marke)) {
            shader.fragmentShader = shader.fragmentShader.replace(marke, `${marke}\nvarying float vNahtF;`);
        }
        const zeile = `normal = normalize( mix( nonPerturbedNormal, normal, 1.0 - ${Hautnahtpatch.RELIEF_WEG.toFixed(3)} * vNahtF ) );`;
        for (const anker of ['#include <clearcoat_normal_fragment_begin>', '#include <emissivemap_fragment>']) {
            if (shader.fragmentShader.includes(anker)) {
                shader.fragmentShader = shader.fragmentShader.replace(anker, `${zeile}\n${anker}`);
                break;
            }
        }
    }
}
