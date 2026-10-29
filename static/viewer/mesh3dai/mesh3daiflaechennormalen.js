/**
 * Mesh3daiflaechennormalen — Normalen einer Fläche der Seite „Mesh3D-AI“: mitgeliefert oder gerechnet (19.10.2026, Edgar an Damira0Tripo: „die textur der Scham ist falsch“).
 *
 * Gerechnet (`computeVertexNormals`) hat jedes Netz seine eigenen Normalen je Punkt — an der Naht zwischen Haut und Anatomie-Stück (zwei Netze, deren Randpunkte aufeinander liegen) knickte die
 * Schattierung: gemessen am Export von Damira0Tripo (`ProjektTemp/_wegwerf/paar_naht_normalen.py`) Winkel über die Naht median 36,7°, p90 123° — eine Stufe am oberen Rand der Scham. Der Genesis-Export
 * der Charakter-Seite trägt die Normalen, mit denen sie schattiert: dort median 0,0°, p90 0,8°. Die Trainingspaare liefern sie mit (`Mesh3daiflaechennetz`, Block `normalen`); hier werden sie gesetzt
 * und für das Ergebnis mit denselben Knochenmatrizen gedreht wie die Punkte (`Mesh3daihaeutung.verformen`, nur der Drehteil). Ohne mitgelieferte Normalen: wie bisher gerechnet.
 */
import * as THREE from 'three';

export class Mesh3daiflaechennormalen {
    /** Normalen an `geometrie`: `normalen` (Float32Array V·3) oder, ohne sie, aus den Dreiecken gerechnet und über gleich liegende Punkte gemittelt (`geschweisst`). */
    static setzen(geometrie, normalen) {
        if (normalen && normalen.length === geometrie.getAttribute('position').count * 3) geometrie.setAttribute('normal', new THREE.BufferAttribute(normalen, 3));
        else Mesh3daiflaechennormalen.geschweisst(geometrie);
    }

    /**
     * Normalen aus den Dreiecken, an den UV-Nähten nicht geknickt (28.10.2026 nachts, Edgar zur zweiten Zeile der Testseite edgar: „unter der Hose noch ein Fehler in der Textur und bei den
     * Beinen. In der ersten Zeile gibt es diese Fehler nicht.“). Das Anzeigenetz ist an den UV-Nähten geteilt (Genesis: Rumpf ↔ Beine am Oberschenkel, y ≈ 0,74 m); `computeVertexNormals` gab
     * jeder Seite der Naht ihre eigene Normale — im Bild eine Kante rund um den Oberschenkel (im Tab gesehen; mit gemittelten Normalen weg). Die erste Zeile nimmt die Normalen vom ungeteilten
     * Käfig (`Mesh3daimeshanpassung._haut`). Hier: Punkte gleicher Lage (auf 1e-5 m) bekommen die Summe ihrer Normalen.
     */
    static geschweisst(geometrie) {
        geometrie.computeVertexNormals();
        const p = geometrie.getAttribute('position').array, n = geometrie.getAttribute('normal').array;
        const gruppen = new Map();
        for (let i = 0; i < p.length / 3; i++) {
            const k = `${Math.round(p[3 * i] * 1e5)},${Math.round(p[3 * i + 1] * 1e5)},${Math.round(p[3 * i + 2] * 1e5)}`;
            const g = gruppen.get(k);
            if (g) g.push(i);
            else gruppen.set(k, [i]);
        }
        for (const g of gruppen.values()) {
            if (g.length < 2) continue;
            let x = 0, y = 0, z = 0;
            for (const i of g) {
                x += n[3 * i];
                y += n[3 * i + 1];
                z += n[3 * i + 2];
            }
            const l = Math.hypot(x, y, z) || 1;
            for (const i of g) {
                n[3 * i] = x / l;
                n[3 * i + 1] = y / l;
                n[3 * i + 2] = z / l;
            }
        }
        geometrie.getAttribute('normal').needsUpdate = true;
    }

    /** Normalen mit den Knochenmatrizen `m` (je Knochen 12 Zahlen, 3×4 zeilenweise, wie `Mesh3daihaeutung.verformen`) gedreht und wieder auf Länge 1 gebracht. */
    static gehaeutet(normalen, knochen, gewicht, k, m) {
        const aus = new Float32Array(normalen.length);
        for (let i = 0; i < normalen.length / 3; i++) {
            const nx = normalen[i * 3], ny = normalen[i * 3 + 1], nz = normalen[i * 3 + 2];
            let x = 0, y = 0, z = 0;
            for (let h = 0; h < k; h++) {
                const w = gewicht[i * k + h];
                if (!w) continue;
                const o = knochen[i * k + h] * 12;
                x += w * (m[o] * nx + m[o + 1] * ny + m[o + 2] * nz);
                y += w * (m[o + 4] * nx + m[o + 5] * ny + m[o + 6] * nz);
                z += w * (m[o + 8] * nx + m[o + 9] * ny + m[o + 10] * nz);
            }
            const l = Math.hypot(x, y, z);
            if (l > 1e-12) {
                aus[i * 3] = x / l;
                aus[i * 3 + 1] = y / l;
                aus[i * 3 + 2] = z / l;
            } else {
                aus[i * 3] = nx;
                aus[i * 3 + 1] = ny;
                aus[i * 3 + 2] = nz;
            }
        }
        return aus;
    }
}
