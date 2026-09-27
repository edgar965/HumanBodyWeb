import * as THREE from 'three';

/**
 * Gruppennetze — ein Netz mit Material-Array in je ein Netz pro Materialzone
 * zerlegen, für Formate ohne Zonenbegriff (OBJ).
 *
 * FUND 26.09.2026 (Edgar: „besser, aber immer noch Texturfehler"): Three.js'
 * `OBJExporter` schreibt `usemtl` aus `mesh.material.name` — OHNE Index
 * (`OBJExporter.js:46-49`). Ein Material-ARRAY hat kein `.name`, also schreibt
 * er für solche Netze GAR KEIN `usemtl`, und ihre Flächen laufen unter dem
 * Material weiter, das ein vorheriges Netz gesetzt hat. Bei Damira1 erbte so
 * das Haar (3 Zonen) das Schuhmaterial, und die sieben Hautzonen des Körpers
 * verloren ihre Zuordnung — sichtbar als weiße Arme, Beine und Wangen.
 *
 * JE ZONE NUR DIE BENUTZTEN PUNKTE, neu durchnummeriert. Die Attribute bloß zu
 * teilen und nur den Index zu kürzen, reicht NICHT: `OBJExporter` schreibt für
 * jedes Netz ALLE Punkte als `v`-Zeilen, unabhängig davon, ob der Index sie
 * nennt. Sieben Zonen × 400.000 Punkte ergaben so einen Text jenseits von
 * V8s String-Grenze („RangeError: Invalid string length", 26.09.2026).
 */
export class Gruppennetze {

    /**
     * @param objekte  Netze (Ausgabe von `Netzpose.gebacken`)
     * @returns neue Liste — Netze ohne Zonen unverändert, andere aufgeteilt
     */
    static zerlegen(objekte) {
        const aus = [];
        for (const obj of objekte) {
            const mats = obj.material;
            const index = obj.geometry.getIndex();
            if (!Array.isArray(mats) || !obj.geometry.groups.length || !index) {
                aus.push(obj);
                continue;
            }
            obj.geometry.groups.forEach((gruppe, nummer) => {
                const teil = Gruppennetze._teilnetz(obj, index, gruppe);
                if (teil) {
                    teil.name = `${obj.name}_${nummer}`;
                    aus.push(teil);
                }
            });
        }
        return aus;
    }

    static _teilnetz(obj, index, gruppe) {
        const material = obj.material[gruppe.materialIndex];
        if (!material || !gruppe.count) return null;
        const quelle = index.array;
        const nummern = new Map();          // alte Punktnummer -> neue
        const indexNeu = new Array(gruppe.count);
        for (let i = 0; i < gruppe.count; i++) {
            const alt = quelle[gruppe.start + i];
            let neu = nummern.get(alt);
            if (neu === undefined) {
                neu = nummern.size;
                nummern.set(alt, neu);
            }
            indexNeu[i] = neu;
        }
        const geometrie = new THREE.BufferGeometry();
        for (const name of Object.keys(obj.geometry.attributes)) {
            geometrie.setAttribute(name, Gruppennetze._teilAttribut(obj.geometry.attributes[name], nummern));
        }
        geometrie.setIndex(indexNeu);
        const netz = new THREE.Mesh(geometrie, material);
        netz.position.copy(obj.position);
        netz.quaternion.copy(obj.quaternion);
        netz.scale.copy(obj.scale);
        return netz;
    }

    /** Ein Attribut auf die benutzten Punkte eindampfen, in neuer Nummernfolge. */
    static _teilAttribut(attribut, nummern) {
        const breite = attribut.itemSize;
        const daten = new Float32Array(nummern.size * breite);
        for (const [alt, neu] of nummern) {
            for (let k = 0; k < breite; k++) daten[neu * breite + k] = attribut.getComponent(alt, k);
        }
        return new THREE.BufferAttribute(daten, breite, attribut.normalized);
    }
}
