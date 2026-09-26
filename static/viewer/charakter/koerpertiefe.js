/**
 * Körpertiefe — der tiefste Punkt der FIGUR in ihrer aktuellen Pose.
 *
 * WARUM (Edgar, 13.09.2026: „Animation immer auf Bodenniveau funktioniert
 * nicht, die Fußspitzen gehen noch in den Boden hinein … nimm den tiefsten
 * Punkt des Körpers bei jedem Animationsframe"): Vorher maß `Fusssohle`
 * nur ein 1-cm-Sohlenband der Ruhelage — was in der Ruhelage nicht Sohle
 * ist (Zehenrücken bei gestrecktem Fuß, Knie, Hände, Gesäß bei Bodenarbeit),
 * wurde nie gemessen. Davor war es der tiefste Knochenkopf (`DEF-toe`, am
 * Ballen, 2,4–7,1 cm über der Sohle). Jetzt zählt jeder Punkt des Netzes.
 *
 * DER WEG: Nicht `applyBoneTransform` je Punkt (Matrix- und Vektorobjekte:
 * 28 ms für 70.851 Punkte), sondern nur die y-ZEILE des Skinnings — je
 * Knochen einmal `Welt · Bindinverse · Knochenwelt · Knocheninverse · Bind`
 * (176 Matrizen), dann je Punkt vier Skalarprodukte auf Float-Feldern.
 * Gemessen an Female1 (70.851 Punkte, 176 Knochen): 5,4–6,7 ms je Bild,
 * bitgleich mit `applyBoneTransform` (fünf Bilder von 0001_Dance).
 *
 * Morphziele sind hier nicht drin — die Szene backt Morphs in die
 * Geometrie (`morphTargetDictionary` leer). Ohne gehäutetes Netz gilt der
 * tiefste Knochen. Schuhe sind ein eigenes Thema (`posenabsatz.js`).
 */
export class Koerpertiefe {

    /** Der tiefste Welt-y der Figur — ihr Netz, sonst ihr tiefster Knochen. */
    static tiefste(figur, wurzel, v) {
        const netz = figur?.bodyMesh;
        if (Koerpertiefe.messbar(netz)) {
            wurzel.updateWorldMatrix(true, true);
            const y = Koerpertiefe.netzY(netz);
            if (isFinite(y)) return y;
        }
        return Koerpertiefe._knochenY(wurzel, v);
    }

    /** Hat das Netz alles, was das Skinning braucht? */
    static messbar(netz) {
        const a = netz?.geometry?.attributes;
        return !!(netz?.isSkinnedMesh && netz.skeleton && a?.position?.array
                  && a.skinIndex?.array && a.skinWeight?.array);
    }

    static _knochenY(wurzel, v) {
        let tiefste = Infinity;
        wurzel.traverse(knochen => {
            if (!knochen.isBone) return;
            knochen.getWorldPosition(v);
            if (v.y < tiefste) tiefste = v.y;
        });
        return tiefste;
    }

    /**
     * Der tiefste gehäutete Punkt des Netzes in Weltkoordinaten. Rechnet
     * dieselbe Kette wie der Shader (`bindMatrixInverse · Σ w·boneMatrix ·
     * bindMatrix`, davor `matrixWorld`), aber nur ihre y-Zeile.
     */
    static netzY(netz) {
        const zeilen = Koerpertiefe.yZeilen(netz);
        const a = netz.geometry.attributes;
        const pos = a.position.array, si = a.skinIndex.array, sw = a.skinWeight.array;
        const anzahl = a.position.count;
        let tiefste = Infinity;
        for (let p = 0; p < anzahl; p++) {
            const x = pos[3 * p], y = pos[3 * p + 1], z = pos[3 * p + 2];
            let yy = 0;
            for (let k = 0; k < 4; k++) {
                const w = sw[4 * p + k];
                if (w === 0) continue;
                const b = si[4 * p + k] * 4;
                yy += w * (zeilen[b] * x + zeilen[b + 1] * y + zeilen[b + 2] * z + zeilen[b + 3]);
            }
            if (yy < tiefste) tiefste = yy;
        }
        return tiefste;
    }

    /** Je Knochen die y-Zeile (4 Zahlen) der ganzen Skinning-Kette. */
    static yZeilen(netz) {
        const knochen = netz.skeleton.bones, inverse = netz.skeleton.boneInverses;
        const vorn = Koerpertiefe._vorn(netz);
        const zeilen = new Float64Array(knochen.length * 4);
        const m = Koerpertiefe._matrix(netz);
        for (let i = 0; i < knochen.length; i++) {
            m.multiplyMatrices(knochen[i].matrixWorld, inverse[i])
             .multiply(netz.bindMatrix).premultiply(vorn);
            const e = m.elements;
            zeilen[4 * i] = e[1]; zeilen[4 * i + 1] = e[5];
            zeilen[4 * i + 2] = e[9]; zeilen[4 * i + 3] = e[13];
        }
        return zeilen;
    }

    /** `matrixWorld · bindMatrixInverse` — der Teil vor der Knochensumme. */
    static _vorn(netz) {
        return Koerpertiefe._matrix(netz).multiplyMatrices(netz.matrixWorld, netz.bindMatrixInverse);
    }

    /** Eine Arbeitsmatrix derselben Klasse wie die des Netzes (kein THREE-Import nötig). */
    static _matrix(netz) {
        return new netz.matrixWorld.constructor();
    }
}
