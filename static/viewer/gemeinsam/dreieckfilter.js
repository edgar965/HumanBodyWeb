/**
 * Dreieckfilter — entartete Dreiecke (zwei Ecken derselbe Vertex-Nummer)
 * aus einer indizierten `BufferGeometry` entfernen.
 *
 * NUR FÜR GEFÜLLTE NETZE — `Netzpose.gebacken` lässt Wireframe-Netze aus.
 *
 * FUND 26.09.2026, und die Berichtigung dazu: dForce-Stranghaar (z. B. „MK
 * Hime Cut Hair") besteht ausschließlich aus entarteten Dreiecken `[a, b, b]`
 * — rund 180.000 Stück. Das ist KEIN Rest und kein Fehler: das Material ist
 * `wireframe`, und im Wireframe zeichnet WebGL die KANTEN. Von `(a, b, b)`
 * bleibt genau eine Linie a–b übrig, also das Strähnensegment selbst
 * (`A:\3DTools\Genesis9\strang.py`, Kopfkommentar). Der Umweg über Dreiecke
 * existiert, weil three.js `LineSegments` nicht skinnen kann, `SkinnedMesh`
 * aber schon — so folgen die Strähnen den Knochen wie jedes andere Netz.
 *
 * Wer sie dort wegfiltert, löscht das ganze Haar. Nur im gefüllten Netz sind
 * sie flächenlos und damit wirkungslos; dort stören sie bloß, weil MeshLab
 * beim Öffnen einer `.obj` „Identical vertex indices found in the same faces"
 * meldet.
 */
export class Dreieckfilter {

    /**
     * Gibt DIESELBE Geometrie zurück (Index ggf. verkürzt), oder unverändert
     * bei fehlendem Index.
     *
     * DIE MATERIALZONEN WANDERN MIT. `geometry.groups` sind Abschnitte IM
     * INDEX (`start`/`count`); jedes entfernte Dreieck verschiebt alle
     * folgenden Grenzen. Ein früherer Stand kürzte nur den Index — solange
     * nichts zu entfernen war, fiel das nicht auf; sobald aber wirklich
     * gefiltert wurde, schnitt `Gruppennetze` die Zonen an falschen Stellen
     * heraus und der Körper verlor den Großteil seiner Flächen (26.09.2026).
     */
    static entfernen(geometrie) {
        const index = geometrie.getIndex();
        if (!index) return geometrie;
        const quelle = index.array;
        const gruppen = geometrie.groups.length
            ? geometrie.groups.map((g) => ({ ...g }))
            : [{ start: 0, count: quelle.length, materialIndex: 0 }];
        const neu = [];
        const neueGruppen = [];
        for (const gruppe of gruppen) {
            const ab = neu.length;
            const bis = Math.min(gruppe.start + gruppe.count, quelle.length);
            for (let i = gruppe.start; i + 2 < bis; i += 3) {
                const a = quelle[i], b = quelle[i + 1], c = quelle[i + 2];
                if (a === b || b === c || a === c) continue;
                neu.push(a, b, c);
            }
            neueGruppen.push({ start: ab, count: neu.length - ab, materialIndex: gruppe.materialIndex });
        }
        if (neu.length === quelle.length) return geometrie;
        geometrie.setIndex(neu);
        if (geometrie.groups.length) {
            geometrie.clearGroups();
            for (const g of neueGruppen) geometrie.addGroup(g.start, g.count, g.materialIndex);
        }
        return geometrie;
    }
}
