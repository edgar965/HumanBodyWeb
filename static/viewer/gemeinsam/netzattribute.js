/**
 * Netzattribute — eigene (nicht-glTF-Standard) Vertex-Attribute aus einer
 * Exportkopie entfernen.
 *
 * FUND 26.09.2026: Genesis 9 traegt eigene Shader-Eingaben direkt auf der
 * `BufferGeometry` — `dicke` (Skalar, Hautdurchlicht, `genesis9netz.js`) und
 * `einzug` (Vektor, Hauteinzug-Verformung, `hauteinzug.js`). `GLTFExporter`
 * kennt beide Namen nicht und schreibt sie als eigene glTF-Attribute
 * `_DICKE`/`_EINZUG` mit — Blenders `io_scene_gltf2`-Importer bricht beim
 * Mischen von Skalar- und Vektor-Attributen auf DEMSELBEN Netz mit einem
 * numpy-Konkatenations-Fehler ab („Couldn't parse glTF" bzw. beim Mesh-Import
 * `ValueError: ... dimensions ... must match exactly"). Kein Werkzeug
 * außerhalb dieses Viewers braucht diese Werte — sie gehören nicht in den
 * Export.
 */
import * as THREE from 'three';
import { Einzugbacken } from './einzugbacken.js';
import { Punktfarbengruppen } from './punktfarbengruppen.js';

export class Netzattribute {

    //: Was `GLTFExporter` (und externe Werkzeuge wie Blender/MeshLab) als
    //: glTF-Standardattribute kennen. Alles andere ist eigene Shader-Kost.
    static STANDARD = ['position', 'normal', 'uv', 'uv2', 'color', 'skinIndex', 'skinWeight', 'tangent'];

    /**
     * `geometrie` (MUTIERT — der Aufrufer übergibt eine eigene Kopie).
     *
     * EINES DER EIGENEN ATTRIBUTE DARF NICHT EINFACH WEG: `einzug` hält die
     * verdeckte Haut unter Kleid und Schuh — ohne ihn sticht sie hindurch
     * (`Einzugbacken`, Fund 26.09.2026 an Damiras Schuhen). Er wird deshalb
     * hier in die Punkte gerechnet, bevor er gelöscht wird. Das steht
     * absichtlich AN DIESER STELLE und nicht bei den Aufrufern: Beide
     * Exportwege (`Netzpose.gebacken` und der GLB-Pfad mit Rig) kommen hier
     * vorbei — beim vollen Index war genau das vergessen worden und der
     * gerigte Export behielt monatelang seine Löcher.
     */
    static eigeneEntfernen(geometrie) {
        Einzugbacken.anwenden(geometrie);
        for (const name of Object.keys(geometrie.attributes)) {
            if (!Netzattribute.STANDARD.includes(name)) geometrie.deleteAttribute(name);
        }
        Netzattribute.alsFloat32(geometrie);
        return geometrie;
    }

    /** Ob `geometrie` mindestens ein nicht-Standard-Attribut trägt. */
    static hatEigene(geometrie) {
        return Object.keys(geometrie.attributes).some((n) => !Netzattribute.STANDARD.includes(n));
    }

    /**
     * Attribute, die der Export nicht so schreiben darf, wie die Szene sie hält (22.11.2026): Float16 (Farbe je Punkt der Mesh-Genesis-Netze, `Meshgenesisflaechennetz`) kennt glTF nicht —
     * `GLTFExporter` schriebe die Bits als UNSIGNED_SHORT; Normalen als Int8 (gebundene Stücke ohne Abbildung, `Meshgenesisbewegungskleid`) schriebe er mit KHR_mesh_quantization.
     */
    static _nichtFloat32(name, a) {
        return a.isFloat16BufferAttribute || (name === 'normal' && !(a.array instanceof Float32Array));
    }

    static brauchtFloat32(geometrie) {
        return Object.entries(geometrie.attributes).some(([n, a]) => Netzattribute._nichtFloat32(n, a));
    }

    /** Solche Attribute in `geometrie` (MUTIERT) als Float32 — die Werte, die die Karte liest (`getX` … wandelt Float16 und normierte Ganzzahlen); Normalen auf Länge 1 wie vorher. */
    static alsFloat32(geometrie) {
        for (const [name, a] of Object.entries(geometrie.attributes)) {
            if (!Netzattribute._nichtFloat32(name, a) || a.isInterleavedBufferAttribute) continue;
            const k = a.itemSize, aus = new Float32Array(a.count * k), lesen = [a.getX, a.getY, a.getZ, a.getW];
            for (let i = 0; i < a.count; i++) for (let c = 0; c < k; c++) aus[i * k + c] = lesen[c].call(a, i);
            if (name === 'normal' && k === 3) {
                for (let i = 0; i < aus.length; i += 3) {
                    const l = Math.hypot(aus[i], aus[i + 1], aus[i + 2]);
                    if (l > 0) { aus[i] /= l; aus[i + 1] /= l; aus[i + 2] /= l; }
                }
            }
            geometrie.setAttribute(name, new THREE.BufferAttribute(aus, k));
        }
        return geometrie;
    }

    /**
     * `obj.geometry` NUR bei Objekten mit eigenen Attributen gegen eine
     * bereinigte Kopie tauschen — für LIVE-Meshes (gerigged, Original bleibt
     * in der Szene), analog `Werkstoffvariante.tauschen`/`Texturskalierung.tauschen`.
     * @returns Rücksetz-Funktion, oder `null` wenn nichts zu tauschen war.
     */
    static tauschen(objekte) {
        // Seit 31.10.2026 auch Netze, deren Punktfarben glTF anders zeigte als die Szene (`Punktfarbengruppen`, Venus: Haar dunkelbraun statt golden)
        const betroffen = objekte.filter((o) => o.geometry && (Netzattribute.hatEigene(o.geometry) || Punktfarbengruppen.abweichend(o) || Netzattribute.brauchtFloat32(o.geometry)));
        if (!betroffen.length) return null;
        const original = betroffen.map((o) => o.geometry);
        betroffen.forEach((o) => { o.geometry = Punktfarbengruppen.angleichen(Netzattribute.eigeneEntfernen(o.geometry.clone()), o); });
        return () => betroffen.forEach((o, i) => { o.geometry = original[i]; });
    }
}
