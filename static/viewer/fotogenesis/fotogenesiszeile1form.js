import * as THREE from 'three';
import { Fotogenesisnachbarn } from './fotogenesisnachbarn.js';
import { Fotogenesistrainingfigur } from './fotogenesistrainingfigur.js';

/**
 * Fotogenesiszeile1form — die Form der Zeile 1 auf der bewegten Genesis-Figur (31.10.2026 nachts, Edgar: „Die bewegte Figur in Zeile 1 übernimmt die Gliedmaßen-Anpassung von Zeile 1
 * noch nicht“ — „mach das alles“).
 *
 * Der Server legt die Form der Zeile 1 als Versatz der Ruhelage ab (`KoerperKI_Fotos.Zeile1versatz`: Käfigpunkte der Figur der Zeile 2 in Ruhe und je Punkt der Versatz, mit der
 * Häutung der Fotos zurückgedreht; `zeile1_form` in `/api/fotogenesis/<job>/figur/`). Die bewegte Figur hat andere Punkte (Stufe des Browsers) — jeder Punkt nimmt den Versatz seiner
 * Käfignachbarn (`Fotogenesisnachbarn`), in den Rahmen der gebauten Figur gedreht (`abbildung` der Bewegung, wie die Stücke). Dasselbe für Anhänge und Stücke, damit sie auf der Haut
 * bleiben. Die Lage wird ERSETZT (neues Attribut), nie im Feld geändert: dieselben Felder kann der Speicher der Figur auch der Zeile 2 geben.
 */
export class Fotogenesiszeile1form {

    /** @param daten `{ruhe, versatz}` (base64 float32) @param abbildung `{quaternion, verschiebung}` Rahmen des Servers → Rahmen der Figur, oder null */
    constructor(daten, abbildung) {
        this.ruhe = Fotogenesistrainingfigur._feld(daten.ruhe, Float32Array).slice();
        this.versatz = Fotogenesistrainingfigur._feld(daten.versatz, Float32Array).slice();
        if (abbildung) {
            const v = new THREE.Vector3();
            for (let i = 0; i < this.ruhe.length; i += 3) {
                v.fromArray(this.ruhe, i).applyQuaternion(abbildung.quaternion).add(abbildung.verschiebung).toArray(this.ruhe, i);
                v.fromArray(this.versatz, i).applyQuaternion(abbildung.quaternion).toArray(this.versatz, i);
            }
        }
        this.nachbarn = new Fotogenesisnachbarn(this.ruhe);
    }

    /** Die Ruhelage eines Netzes um den Versatz der Zeile 1 verschieben — einmal je Geometrie. */
    anwenden(geometrie) {
        if (!geometrie?.attributes?.position || geometrie.userData.zeile1Form) return false;
        const a = geometrie.attributes.position.array, neu = new Float32Array(a.length), v = this.versatz;
        for (let i = 0; i < a.length / 3; i++) {
            let vx = 0, vy = 0, vz = 0;
            for (const [j, w] of this.nachbarn.gewichte(a, i)) { vx += w * v[j * 3]; vy += w * v[j * 3 + 1]; vz += w * v[j * 3 + 2]; }
            neu[i * 3] = a[i * 3] + vx; neu[i * 3 + 1] = a[i * 3 + 1] + vy; neu[i * 3 + 2] = a[i * 3 + 2] + vz;
        }
        geometrie.setAttribute('position', new THREE.BufferAttribute(neu, 3));
        geometrie.computeBoundingBox();
        geometrie.computeBoundingSphere();
        geometrie.userData.zeile1Form = true;
        return true;
    }
}
