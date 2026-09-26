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
export class Netzattribute {

    //: Was `GLTFExporter` (und externe Werkzeuge wie Blender/MeshLab) als
    //: glTF-Standardattribute kennen. Alles andere ist eigene Shader-Kost.
    static STANDARD = ['position', 'normal', 'uv', 'uv2', 'color', 'skinIndex', 'skinWeight', 'tangent'];

    /** `geometrie` (MUTIERT — der Aufrufer übergibt eine eigene Kopie). */
    static eigeneEntfernen(geometrie) {
        for (const name of Object.keys(geometrie.attributes)) {
            if (!Netzattribute.STANDARD.includes(name)) geometrie.deleteAttribute(name);
        }
        return geometrie;
    }

    /** Ob `geometrie` mindestens ein nicht-Standard-Attribut trägt. */
    static hatEigene(geometrie) {
        return Object.keys(geometrie.attributes).some((n) => !Netzattribute.STANDARD.includes(n));
    }

    /**
     * `obj.geometry` NUR bei Objekten mit eigenen Attributen gegen eine
     * bereinigte Kopie tauschen — für LIVE-Meshes (gerigged, Original bleibt
     * in der Szene), analog `Werkstoffvariante.tauschen`/`Texturskalierung.tauschen`.
     * @returns Rücksetz-Funktion, oder `null` wenn nichts zu tauschen war.
     */
    static tauschen(objekte) {
        const betroffen = objekte.filter((o) => o.geometry && Netzattribute.hatEigene(o.geometry));
        if (!betroffen.length) return null;
        const original = betroffen.map((o) => o.geometry);
        betroffen.forEach((o) => { o.geometry = Netzattribute.eigeneEntfernen(o.geometry.clone()); });
        return () => betroffen.forEach((o, i) => { o.geometry = original[i]; });
    }
}
