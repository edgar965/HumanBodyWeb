import * as THREE from 'three';

/**
 * Punktfarbengruppen — Punktfarben in der Exportkopie so, wie three sie zeigt (31.10.2026).
 *
 * three nimmt die Punktfarben (`color`) nur in Materialien mit `vertexColors`; glTF dagegen multipliziert `COLOR_0` IMMER mit Farbfaktor und Bild, und alle Gruppen
 * (Primitive) eines Netzes teilen ihre Attribute. Gemessen 31.10.2026 an Mesh3D-AI Venus (Exportleiste, GLB): die KI-Stücke tragen zwei Gruppen — Bild OHNE Punktfarben und
 * Punktfarben ohne Bild —, und das Haar kam im Export golden × dunkelbraun = dunkelbraun heraus (Punktfarben im Mittel 0,10/0,06/0,03 linear, `glb_netze.py`: Bild ja, COLOR_0 ja).
 * Regel je Netz mit `color`: kein Material mit `vertexColors` → `color` fällt weg; alle → bleibt; gemischt → die Gruppen ohne Punktfarben bekommen eigene Punkte (Kopien) mit Weiß,
 * damit an den Grenzen keine Gruppe die Farbe der anderen mitnimmt.
 */
export class Punktfarbengruppen {

    /** Die Materialien, die das Netz wirklich zeichnet: bei Gruppen nur deren Material (die KI-Stücke tragen ein zweites, von keiner Gruppe benutztes — gemessen an Venus). */
    static _materialien(o) {
        if (!Array.isArray(o.material)) return [o.material];
        const gruppen = o.geometry?.groups || [];
        return gruppen.length ? [...new Set(gruppen.map(g => o.material[g.materialIndex]))] : [o.material[0]];
    }

    /** Ob die Punktfarben von `o` im glTF anders wirkten als in der Szene. */
    static abweichend(o) {
        return !!o.geometry?.attributes?.color && Punktfarbengruppen._materialien(o).some(m => m && !m.vertexColors);
    }

    /** `geometrie` (MUTIERT — der Aufrufer übergibt eine Kopie) an die Materialien von `o` angleichen. */
    static angleichen(geometrie, o) {
        const mats = Punktfarbengruppen._materialien(o);
        if (!geometrie.attributes.color || !mats.some(m => m && !m.vertexColors)) return geometrie;
        if (!mats.some(m => m?.vertexColors)) {
            geometrie.deleteAttribute('color');
            return geometrie;
        }
        const attribute = [...Object.values(geometrie.attributes), ...Object.values(geometrie.morphAttributes || {}).flat()];
        if (attribute.some(a => a.isInterleavedBufferAttribute)) {
            console.warn('Punktfarbengruppen: verschränkte Attribute — die Punktfarben bleiben, wie sie sind', o.name);
            return geometrie;
        }
        const n = geometrie.attributes.position.count;
        if (!geometrie.index) geometrie.setIndex([...Array(n).keys()]);
        const index = Uint32Array.from(geometrie.index.array);
        const neu = new Int32Array(n).fill(-1);
        const kopien = [];
        for (const g of geometrie.groups) {
            if (o.material[g.materialIndex]?.vertexColors) continue;
            for (let i = g.start; i < Math.min(g.start + g.count, index.length); i++) {
                const v = index[i];
                if (neu[v] < 0) { neu[v] = n + kopien.length; kopien.push(v); }
                index[i] = neu[v];
            }
        }
        const verlaengern = (a, weiss) => {
            const k = a.itemSize;
            const feld = new a.array.constructor((n + kopien.length) * k);
            feld.set(a.array);
            const eins = a.normalized && !(a.array instanceof Float32Array) ? 2 ** (8 * a.array.BYTES_PER_ELEMENT) - 1 : 1;
            kopien.forEach((v, j) => {
                for (let c = 0; c < k; c++) feld[(n + j) * k + c] = weiss ? eins : a.array[v * k + c];
            });
            return new THREE.BufferAttribute(feld, k, a.normalized);
        };
        for (const [name, a] of Object.entries(geometrie.attributes)) geometrie.setAttribute(name, verlaengern(a, name === 'color'));
        for (const [name, liste] of Object.entries(geometrie.morphAttributes || {})) geometrie.morphAttributes[name] = liste.map(a => verlaengern(a, false));
        geometrie.setIndex(new THREE.BufferAttribute(index, 1));
        return geometrie;
    }
}
