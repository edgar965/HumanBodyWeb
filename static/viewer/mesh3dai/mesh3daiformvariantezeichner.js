/**
 * Mesh3daiformvariantezeichner — die Figuren der Seite „Formvariante“ (18.10.2026): der Körper kommt EINMAL (Dreiecke, UV, Material mit der Haut der Grundlage, `…/koerper/`), je Figur nur die Lage
 * der 27.087 Punkte (`…/figur/<was>/`, Server `Mesh3daiformvariantefigur`) — alle Figuren tragen denselben Genesis-Körper. Dazu die Wolke des Starts.
 * Alles Gebaute trägt `userData.gemeinsam`: die Felder (`Mesh3daiansicht`) geben ihren Inhalt bei jedem Zeichnen frei, Geometrie und Material bleiben.
 */
import * as THREE from 'three';
import { Mesh3daiechtmaterial } from './mesh3daiechtmaterial.js';

/** Abweichung je Punkt in mm → Farbe (dieselben Stufen wie die Legende in `mesh3daiformvariante.css`). */
const STUFEN = [[0, 0x2ea043], [10, 0xe3b341], [30, 0xf0883e], [60, 0xe5534b]];

export class Mesh3daiformvariantezeichner {
    static STUFEN = STUFEN;
    /** Wird gerufen, sobald ein Hautbild geladen ist (die Felder zeichnen nur auf Anforderung). */
    static nachLaden = null;
    static PUNKTGROESSE = 0.011;

    static _kopf(puffer) {
        const laenge = new DataView(puffer).getUint32(0, true);
        return { kopf: JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge))), ab: 4 + laenge };
    }

    /** Paket `…/koerper/` → Körper (Sichten auf den Puffer, jeder Block beginnt auf einem Vielfachen von 4). */
    static koerper(puffer, basis) {
        const { kopf, ab } = Mesh3daiformvariantezeichner._kopf(puffer);
        const { punkte: v, dreiecke: f } = kopf;
        const dreiecke = new Uint32Array(puffer, ab, f * 3);
        const uv = new Float32Array(puffer, ab + f * 12, v * 2);
        const material = new Int16Array(puffer, ab + f * 12 + v * 8, f);
        return { kopf, dreiecke, uv: new THREE.BufferAttribute(uv, 2), material, basis, index: null, materialien: null };
    }

    /** Paket `…/figur/<was>/` → Figur ({kopf, lage}); Geometrie und Farben entstehen beim ersten Zeichnen. */
    static figur(puffer) {
        const { kopf, ab } = Mesh3daiformvariantezeichner._kopf(puffer);
        return { kopf, lage: new Float32Array(puffer, ab, kopf.punkte * 3), geometrie: null, farbe: null };
    }

    /** Index nach Material sortiert (eine Gruppe je Material, −1 = einfarbig = das letzte), einmal je Körper. */
    static _index(k) {
        if (k.index) return k.index;
        const zahl = k.kopf.materialien.length + 1;
        const je = Array.from({ length: zahl }, () => []);
        for (let t = 0; t < k.material.length; t++) {
            const m = k.material[t] < 0 ? zahl - 1 : k.material[t];
            je[m].push(k.dreiecke[3 * t], k.dreiecke[3 * t + 1], k.dreiecke[3 * t + 2]);
        }
        const index = new Uint32Array(je.reduce((s, l) => s + l.length, 0));
        const gruppen = [];
        let ab = 0;
        je.forEach((l, m) => {
            if (!l.length) return;
            index.set(l, ab);
            gruppen.push([ab, l.length, m]);
            ab += l.length;
        });
        k.index = { attribut: new THREE.BufferAttribute(index, 1), gruppen };
        return k.index;
    }

    /** Haut je Material (Bilder der Grundlage), dazu einfarbig (wie „Oberfläche“ auf der Jobseite) und nach Farbe je Punkt. */
    static _materialien(k) {
        if (k.materialien) return k.materialien;
        const lader = new THREE.TextureLoader();
        const einfarbig = new THREE.MeshStandardMaterial({ color: Mesh3daiechtmaterial.EINHEIT, roughness: 0.7, side: THREE.DoubleSide });
        const haut = k.kopf.materialien.map(m => {
            const material = new THREE.MeshStandardMaterial({ color: new THREE.Color(...(m.farbe ?? [1, 1, 1])), roughness: 0.75, side: THREE.DoubleSide });
            if (m.bild && m.genutzt) {
                material.map = lader.load(`${k.basis}/bild/${m.bild}`, () => Mesh3daiformvariantezeichner.nachLaden?.());
                material.map.colorSpace = THREE.SRGBColorSpace;
                material.map.anisotropy = 4;
            }
            return material;
        });
        const abweichung = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7, side: THREE.DoubleSide });
        k.materialien = { haut: [...haut, einfarbig], einfarbig, abweichung };
        for (const m of [...k.materialien.haut, abweichung]) m.userData.gemeinsam = true;
        return k.materialien;
    }

    /**
     * @param ansicht 'textur' | 'oberflaeche' | 'abweichung' @param ziel die Figur des Ziels (für die Abweichung)
     * @returns {THREE.Mesh} neues Objekt auf der geteilten Geometrie der Figur
     */
    static mesh(k, figur, ansicht, ziel = null) {
        if (!figur.geometrie) {
            const g = new THREE.BufferGeometry();
            g.setAttribute('position', new THREE.BufferAttribute(figur.lage, 3));
            g.setAttribute('uv', k.uv);
            const index = Mesh3daiformvariantezeichner._index(k);
            g.setIndex(index.attribut);
            for (const [ab, n, m] of index.gruppen) g.addGroup(ab, n, m);
            g.computeVertexNormals();
            g.userData.gemeinsam = true;
            figur.geometrie = g;
        }
        const m = Mesh3daiformvariantezeichner._materialien(k);
        if (ansicht === 'abweichung' && ziel && ziel !== figur) {
            figur.farbe ??= Mesh3daiformvariantezeichner.farben(figur.lage, ziel.lage);
            figur.geometrie.setAttribute('color', figur.farbe);
            return new THREE.Mesh(figur.geometrie, m.abweichung);
        }
        return new THREE.Mesh(figur.geometrie, ansicht === 'textur' ? m.haut : m.einfarbig);
    }

    /** Abstand je Punkt zum Ziel (mm) → Farbe, zwischen den Stufen linear. */
    static farben(lage, ziel) {
        const stufen = STUFEN.map(([mm, hex]) => [mm, new THREE.Color(hex)]);
        const aus = new Float32Array(lage.length);
        const c = new THREE.Color();
        for (let i = 0; i < lage.length; i += 3) {
            const d = 1000 * Math.hypot(lage[i] - ziel[i], lage[i + 1] - ziel[i + 1], lage[i + 2] - ziel[i + 2]);
            let s = 1;
            while (s < stufen.length - 1 && d > stufen[s][0]) s++;
            const [a, fa] = stufen[s - 1];
            const [b, fb] = stufen[s];
            c.copy(fa).lerp(fb, Math.min(1, Math.max(0, (d - a) / (b - a))));
            aus[i] = c.r;
            aus[i + 1] = c.g;
            aus[i + 2] = c.b;
        }
        return new THREE.BufferAttribute(aus, 3);
    }

    /** Die Wolke des Starts (Antwort von `…/wolke/<nr>/<k>/`: Punkte in m, Farbe 0–255 sRGB). */
    static wolke(w) {
        const n = w.punkte.length;
        const lage = new Float32Array(n * 3);
        const farbe = new Float32Array(n * 3);
        const c = new THREE.Color();
        for (let i = 0; i < n; i++) {
            lage.set(w.punkte[i], 3 * i);
            c.setRGB(w.farbe[i][0] / 255, w.farbe[i][1] / 255, w.farbe[i][2] / 255, THREE.SRGBColorSpace);
            farbe[3 * i] = c.r;
            farbe[3 * i + 1] = c.g;
            farbe[3 * i + 2] = c.b;
        }
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        g.setAttribute('color', new THREE.BufferAttribute(farbe, 3));
        g.userData.gemeinsam = true;
        const material = new THREE.PointsMaterial({ size: Mesh3daiformvariantezeichner.PUNKTGROESSE, vertexColors: true, sizeAttenuation: true });
        material.userData.gemeinsam = true;
        return new THREE.Points(g, material);
    }
}
