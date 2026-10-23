/**
 * Mesh3daibewegungskleid — ein Stück der Ergebnisfigur (Anzeigenetz `Mesh3daiflaechennetz`: Ruhelage, Knochen und Gewichte je Punkt) an das Skelett der Genesis-Figur binden, damit es der
 * Standardanimation folgt (22.10.2026, `Mesh3daifigurbewegung`).
 *
 * Still gezeigt wird ein Stück auf der CPU mit den Matrizen der KI-Haltung gehäutet (`Mesh3daitestnetzbau`). Für die Bewegung braucht es ein `SkinnedMesh` an den Knochen der Figur, die three.js
 * je Bild stellt: dieselben Gewichte, die Knochen über ihre NAMEN aufgelöst (die Gewichte zählen in der Reihenfolge der `kinematik.json` der Figur, das Skelett in der des Bauplans — wie `Eigenhaut`),
 * höchstens vier je Punkt (die stärksten, neu auf Summe 1).
 *
 * Die Ruhelage des Stücks und die des Skeletts liegen im selben Rahmen, wenn beide aus denselben Reglern gebaut sind; `abbildung` (`{quaternion, verschiebung}`, `Mesh3daiausrichtung.starr` von den
 * Ruhegelenken der Kinematik auf die Knochen der gebauten Figur) nimmt einen Unterschied der Rahmen heraus — gemessen wird er von `Mesh3daifigurbewegung` und steht in deren Text.
 */
import * as THREE from 'three';
import { Eigenhaut } from '../gemeinsam/eigenhaut.js';
import { Mesh3daitestnetzbau } from './mesh3daitestnetzbau.js';

export class Mesh3daibewegungskleid {
    /** Die Ruhelage eines Netzes im Rahmen der Figur (Float32Array, V·3). */
    static ruhe(netz, abbildung) {
        const aus = new Float32Array(netz.ruhe);
        if (!abbildung) return aus;
        const v = new THREE.Vector3();
        for (let i = 0; i < aus.length; i += 3) {
            v.set(aus[i], aus[i + 1], aus[i + 2]).applyQuaternion(abbildung.quaternion).add(abbildung.verschiebung);
            aus[i] = v.x; aus[i + 1] = v.y; aus[i + 2] = v.z;
        }
        return aus;
    }

    /**
     * @param netz Anzeigenetz mit `ruhe`, `knochen`, `gewicht`, `kopf.haut` @param skelett `{skeleton, bones}` der Genesis-Figur @param namen Knochennamen in der Reihenfolge der Gewichte
     * @param abbildung Rahmen der Kinematik → Rahmen der Figur (oder null) @returns {THREE.SkinnedMesh|null} null, wenn ein Knochen fehlt (dann bleibt das Stück weg — nie halb gebunden)
     */
    static binden(netz, skelett, namen, abbildung) {
        if (!netz?.ruhe || !netz.knochen || !netz.gewicht || !skelett?.skeleton) return null;
        const spalte = Eigenhaut.spaltenNummern(namen, skelett);
        if (!spalte) return null;
        // Geometrie, Gruppen, Materialien und UV wie das stille Stück: mit Einheitsmatrizen gehäutet ist die Lage die Ruhelage.
        const einheit = new Float32Array(namen.length * 12);
        for (let j = 0; j < namen.length; j++) einheit.set([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0], j * 12);
        const still = Mesh3daitestnetzbau.mesh(netz, einheit);
        const geo = still.geometry;
        geo.setAttribute('position', new THREE.BufferAttribute(Mesh3daibewegungskleid.ruhe(netz, abbildung), 3));
        const normalen = geo.getAttribute('normal');
        if (normalen && abbildung) {
            const n = new THREE.Vector3();
            for (let i = 0; i < normalen.count; i++) normalen.setXYZ(i, ...n.fromBufferAttribute(normalen, i).applyQuaternion(abbildung.quaternion).toArray());
        }
        const { index, gewicht } = Mesh3daibewegungskleid._vier(netz, spalte);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(index, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewicht, 4));
        geo.userData.gemeinsam = false;         // gehört der Bewegung, nicht dem Feld: `Mesh3daifigurbewegung.verwerfen` gibt sie frei
        const mesh = new THREE.SkinnedMesh(geo, still.material);
        mesh.frustumCulled = false;
        return mesh;
    }

    /** Die vier stärksten Knochen je Punkt (Gewichte ×255 im Netz), auf Summe 1. */
    static _vier(netz, spalte) {
        const k = netz.kopf.haut;
        const v = netz.ruhe.length / 3;
        const index = new Float32Array(v * 4);
        const gewicht = new Float32Array(v * 4);
        const paare = [];
        for (let i = 0; i < v; i++) {
            paare.length = 0;
            for (let h = 0; h < k; h++) {
                const w = netz.gewicht[i * k + h];
                if (w) paare.push([w, spalte[netz.knochen[i * k + h]] ?? 0]);
            }
            paare.sort((a, b) => b[0] - a[0]);
            const summe = paare.slice(0, 4).reduce((s, p) => s + p[0], 0) || 1;
            for (let h = 0; h < Math.min(4, paare.length); h++) {
                index[i * 4 + h] = paare[h][1];
                gewicht[i * 4 + h] = paare[h][0] / summe;
            }
            if (!paare.length) gewicht[i * 4] = 1;          // ohne Gewicht am ersten Knochen (der Wurzel): bleibt in Ruhe am Körper, statt zum Ursprung zu fallen
        }
        return { index, gewicht };
    }
}
