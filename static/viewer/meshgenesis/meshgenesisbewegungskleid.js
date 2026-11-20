/**
 * Meshgenesisbewegungskleid — ein Stück der Ergebnisfigur (Anzeigenetz `Meshgenesisflaechennetz`: Ruhelage, Knochen und Gewichte je Punkt) an das Skelett der Genesis-Figur binden, damit es der
 * Standardanimation folgt (22.10.2026, `Meshgenesisfigurbewegung`).
 *
 * Still gezeigt wird ein Stück auf der CPU mit den Matrizen der KI-Haltung gehäutet (`Meshgenesistestnetzbau`). Für die Bewegung braucht es ein `SkinnedMesh` an den Knochen der Figur, die three.js
 * je Bild stellt: dieselben Gewichte, die Knochen über ihre NAMEN aufgelöst (die Gewichte zählen in der Reihenfolge der `kinematik.json` der Figur, das Skelett in der des Bauplans — wie `Eigenhaut`),
 * höchstens vier je Punkt (die stärksten, neu auf Summe 1).
 *
 * Die Ruhelage des Stücks und die des Skeletts liegen im selben Rahmen, wenn beide aus denselben Reglern gebaut sind; `abbildung` (`{quaternion, verschiebung}`, `Meshgenesisausrichtung.starr` von den
 * Ruhegelenken der Kinematik auf die Knochen der gebauten Figur) nimmt einen Unterschied der Rahmen heraus — gemessen wird er von `Meshgenesisfigurbewegung` und steht in deren Text.
 */
import * as THREE from 'three';
import { Eigenhaut } from '../gemeinsam/eigenhaut.js';
import { Meshgenesishaarschwung } from './meshgenesishaarschwung.js';
import { Meshgenesiskollision } from './meshgenesiskollision.js';
import { Meshgenesisstoffkleid } from './meshgenesisstoffkleid.js';
import { Meshgenesishaarfilm } from './meshgenesishaarfilm.js';
import { Meshgenesistestnetzbau } from './meshgenesistestnetzbau.js';

export class Meshgenesisbewegungskleid {
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
        const still = Meshgenesistestnetzbau.mesh(netz, einheit);
        const geo = still.geometry;
        geo.setAttribute('position', new THREE.BufferAttribute(Meshgenesisbewegungskleid.ruhe(netz, abbildung), 3));
        const normalen = geo.getAttribute('normal');
        if (normalen && abbildung) {
            const n = new THREE.Vector3();
            for (let i = 0; i < normalen.count; i++) normalen.setXYZ(i, ...n.fromBufferAttribute(normalen, i).applyQuaternion(abbildung.quaternion).toArray());
        }
        const { index, gewicht } = Meshgenesisbewegungskleid._vier(netz, spalte);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(index, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewicht, 4));
        geo.userData.gemeinsam = false;         // gehört der Bewegung, nicht dem Feld: `Meshgenesisfigurbewegung.verwerfen` gibt sie frei
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

    /**
     * Alle Stücke der Quelle an das Skelett der bewegten Figur binden (`bewegung`: `Meshgenesisfigurbewegung`; bis 19.11.2026 dort `_kleiderBinden`): je Stück das `SkinnedMesh`, der Kapselschub
     * aus fremden Gliedern (31.10.2026 nachts), die Bewegung je Locke (16.11.2026) und der Stoff der gewählten Bewegung, wo einer gerechnet ist (`Meshgenesisstoffkleid`, 19.11.2026).
     */
    static alleBinden(bewegung) {
        for (const k of bewegung.kleider) {
            k.mesh.parent?.remove(k.mesh);
            k.mesh.geometry.dispose();
        }
        bewegung.kleider = [];
        const q = bewegung._q;
        for (const st of q?.stuecke || []) {
            const mesh = Meshgenesisbewegungskleid.binden(st.netz, bewegung.modell.skelett, q.knochen, bewegung._abbildung);
            if (!mesh) continue;
            mesh.userData.art = st.art; mesh.name = `ki_${st.id}`;      // Name = Schlüssel in `hautStuecke` (Exportleiste: `Exportleistefigur.hautDeckt`, Knotenname in GLB und .blend)
            mesh.visible = bewegung._kleiderAn;
            Eigenhaut.einhaengen(bewegung.modell.group, mesh, bewegung.modell.skelett);
            Meshgenesiskollision.anbringen(mesh, q.kapseln, bewegung.modell.skelett, bewegung._abbildung, q.knochen);
            Meshgenesishaarschwung.anbringen(mesh, st.netz, bewegung._abbildung);
            bewegung.kleider.push({ mesh, art: st.art, adresse: st.adresse });
        }
        bewegung._kleiderWurzel = bewegung.modell.skelett?.rootBone || null;
        Meshgenesisstoffkleid.anbringenAlle(bewegung);
        Meshgenesishaarfilm.anbringenAlle(bewegung);              // Haar und Bart aus der Kette (Schritt „haar“, 20.11.2026)
    }
}
