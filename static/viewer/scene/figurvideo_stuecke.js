/**
 * Figurvideostuecke — die Kleidungsstücke der Szene für den Server-Weg.
 *
 * WARUM (11.09.2026): Bis dahin kamen NUR GarmentCode-Stücke ins Server-
 * Video, über ihre `_sim_rig.json`. Vorlagen-Cloth (`tpl_`), Garderobe
 * (`gar_`) und MakeHuman-Proxys (`mh_`) haben keine solche Datei — die
 * Figur kam ohne sie an. Was in der Szene an der Figur hängt und gehäutet
 * ist, geht jetzt SO mit, wie es hier steht: Punkte, Dreiecke, Hautgewichte
 * — dieselben Daten, die der Shader benutzt.
 *
 * BINÄR, NICHT JSON: Ein T-Shirt hat 10.814 Punkte; als Zahlenliste in JSON
 * wären das rund 3 MB je Stück, als Puffer 640 KB. Aufbau je Stück, ohne
 * Kopf — die Zahlen stehen im Auftrag:
 *
 *     Float32[n*3]  Punkte (Lage der Figur, Y oben — der Server dreht)
 *     Uint32 [m*3]  Dreiecke
 *     Uint16 [n*4]  Knochennummern     (Reihenfolge: `knochen` im Auftrag)
 *     Float32[n*4]  Gewichte
 *
 * DIE KNOCHENNAMEN kommen aus `skinWeightData.bone_names` (mit Punkten,
 * `DEF-spine.004`), nicht aus `bone.name`: Three.js ersetzt dort Punkte
 * durch Unterstriche, und `DEF-upper_arm_L` lässt sich nicht eindeutig
 * zurückübersetzen. Der Aufrufer reicht sie herein — so braucht dieses
 * Modul weder `state.js` noch Three.js und läuft in Node
 * (`test_js_figurvideo_stuecke.py`).
 */
export class Figurvideostuecke {

    /** Alle gehäuteten Stücke der Figur als Pakete — und die Namen derer,
     *  die starr hängen und deshalb nicht mitkommen. */
    static sammeln(inst) {
        const skelett = inst?.bodyMesh?.skeleton;
        const stuecke = [], starre = [];
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            const paket = (netz?.isSkinnedMesh && netz.skeleton === skelett)
                ? Figurvideostuecke.paket(netz, schluessel) : null;
            if (paket) stuecke.push(paket); else starre.push(schluessel);
        }
        return { stuecke, starre };
    }

    /** Ein Netz als Paket, oder null, wenn ihm Gewichte fehlen. */
    static paket(netz, schluessel) {
        const geo = netz.geometry;
        const pos = geo.getAttribute('position');
        const si = geo.getAttribute('skinIndex');
        const sw = geo.getAttribute('skinWeight');
        if (!pos || !si || !sw) return null;
        const n = pos.count;
        // Punkte in der Lage der FIGUR: die eigene Matrix des Netzes gehört
        // dazu (ein GarmentCode-Stück bindet mit `netz.matrix`).
        netz.updateMatrix();
        const m = netz.matrix.elements;
        const punkte = new Float32Array(n * 3);
        for (let i = 0; i < n; i++) {
            const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
            punkte[3 * i] = m[0] * x + m[4] * y + m[8] * z + m[12];
            punkte[3 * i + 1] = m[1] * x + m[5] * y + m[9] * z + m[13];
            punkte[3 * i + 2] = m[2] * x + m[6] * y + m[10] * z + m[14];
        }
        let dreiecke;
        if (geo.index) {
            dreiecke = Uint32Array.from(geo.index.array);
        } else {
            dreiecke = new Uint32Array(n);
            for (let i = 0; i < n; i++) dreiecke[i] = i;
        }
        const nummern = new Uint16Array(n * 4), gewichte = new Float32Array(n * 4);
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < 4; j++) {
                nummern[4 * i + j] = Math.round(si.getComponent(i, j));
                gewichte[4 * i + j] = sw.getComponent(i, j);
            }
        }
        const blob = new Blob([punkte.buffer, dreiecke.buffer, nummern.buffer, gewichte.buffer]);
        return {
            name: netz.userData?.beschriftung || netz.name || schluessel,
            schluessel, farbe: Figurvideostuecke.farbe(netz),
            punkte: n, dreiecke: dreiecke.length / 3, blob,
        };
    }

    /** Die Farbe des Materials als `#rrggbb` — beim Körper-Array das erste. */
    static farbe(netz) {
        const mat = Array.isArray(netz.material) ? netz.material[0] : netz.material;
        return mat?.color?.getHexString ? `#${mat.color.getHexString()}` : null;
    }

    /**
     * Das Formular für `POST /api/animation/video/`: der Auftrag als JSON
     * (mit der Stückliste und den Knochennamen), je Stück ein Paket.
     * `knochen` sind die Namen in Skelettreihenfolge (`bone_names`).
     */
    static formular(auftrag, stuecke, knochen) {
        const daten = new FormData();
        daten.append('auftrag', JSON.stringify({
            ...auftrag, knochen,
            stuecke: stuecke.map((s, i) => ({
                name: s.name, farbe: s.farbe, punkte: s.punkte,
                dreiecke: s.dreiecke, datei: `stueck_${i}`,
            })),
        }));
        stuecke.forEach((s, i) => daten.append(`stueck_${i}`, s.blob, `stueck_${i}.bin`));
        return daten;
    }
}
