import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from './kodierung.js';
import { BODY_MATERIALS } from './koerpermaterialien.js';

/**
 * Körpernetz — die Antwort von `/api/character/mesh/` in eine Three.js-Geometrie.
 *
 * WARUM DIESES MODUL (Umbau 17.08.2026): Diese dreißig Zeilen standen FÜNFMAL im
 * Projekt — `animation/netz.js`, `scene/character.js`, `viewer/mesh.js`
 * (zweimal in derselben Datei) und `result_character/mesh_loading.js`. Gefunden
 * vom Werkzeug `doppelcode`, das allein in `animation/netz.js` 21 Fundstellen
 * meldete (Kriterium 6).
 *
 * Die fünf Fassungen unterschieden sich nur in Kleinigkeiten: einmal `let geo`,
 * einmal `const geo`; einmal die Puffer in Zwischenvariablen, einmal direkt im
 * Aufruf. Fünf Kopien heißen fünf Stellen, an denen die
 * Blender→Three-Umrechnung der NORMALEN vergessen werden kann — und dann
 * leuchtet das Modell auf einer Seite anders als auf der nächsten.
 *
 * WAS HIER PASSIERT, in dieser Reihenfolge:
 *
 *   1. Punkte aus base64, Blender (Z oben) → Three (Y oben), IN PLACE
 *      (bei 70.851 Punkten keine zweite Kopie).
 *   2. Dreiecksindizes und UVs, beide optional — `?nur_punkte=1` liefert sie
 *      nicht, weil sich die Topologie durch Morphs nicht ändert.
 *   3. Materialien aus `BODY_MATERIALS`; der Index IST die Materialgruppe.
 *   4. Normalen aus dem Server ODER berechnet. Die Server-Normalen brauchen
 *      dieselbe Achsdrehung wie die Punkte — das ist die Zeile, die man in
 *      einer Kopie vergisst.
 *   5. Materialgruppen (`addGroup`), damit Augen, Zähne und Nägel ihr eigenes
 *      Material bekommen.
 *
 * `THREE` kommt als Parameter: Die Seiten holen es über verschiedene Importmaps
 * (`scene/state.js`, `viewer/state.js`, …), und ein zweiter Import derselben
 * Bibliothek wäre eine zweite Instanz mit eigenen Klassen.
 */
export class Koerpernetz {

    /**
     * Geometrie und Materialien aus der Netz-Antwort.
     *
     * @param {object} daten Antwort von `/api/character/mesh/`
     * @param {object} THREE die Three.js-Instanz der Seite
     * @returns {{geometrie: object, materialien: object[]}}
     */
    static bauen(daten, THREE) {
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', Koerpernetz._punkte(daten, THREE));

        if (daten.faces) {
            geometrie.setIndex(
                new THREE.BufferAttribute(base64ToUint32(daten.faces), 1));
        }
        if (daten.uvs) {
            geometrie.setAttribute(
                'uv', new THREE.BufferAttribute(base64ToFloat32(daten.uvs), 2));
        }
        Koerpernetz._normalen(geometrie, daten, THREE);
        Koerpernetz._gruppen(geometrie, daten);
        return { geometrie, materialien: Koerpernetz.materialien(THREE) };
    }

    /**
     * Das fertige Netz — mit Materialliste, wenn es Gruppen gibt, sonst mit
     * dem Hautmaterial allein.
     *
     * Diese Verzweigung stand in allen fünf Kopien am Ende: Ohne Gruppen kann
     * Three.js mit einem Array nichts anfangen und rendert das Netz schwarz.
     */
    static netz(daten, THREE) {
        const { geometrie, materialien } = Koerpernetz.bauen(daten, THREE);
        return new THREE.Mesh(geometrie,
                              geometrie.groups.length ? materialien
                                                      : materialien[0]);
    }

    /** Nur die Punktlagen — gedreht und als Attribut. */
    static _punkte(daten, THREE) {
        const puffer = base64ToFloat32(daten.vertices);
        blenderToThreeCoords(puffer);
        return new THREE.BufferAttribute(puffer, 3);
    }

    /**
     * Normalen vom Server, sonst gerechnet.
     *
     * Die Server-Normalen kommen in Blender-Achsen und brauchen dieselbe
     * Drehung wie die Punkte. Ohne sie zeigen die Flächen nach innen und das
     * Modell wirkt von innen beleuchtet.
     */
    static _normalen(geometrie, daten, THREE) {
        if (!daten.normals) {
            geometrie.computeVertexNormals();
            return;
        }
        const puffer = base64ToFloat32(daten.normals);
        blenderToThreeCoords(puffer);
        geometrie.setAttribute('normal', new THREE.BufferAttribute(puffer, 3));
    }

    /**
     * Materialgruppen — nur sinnvoll mit Index.
     *
     * Ohne die Gruppen trägt das ganze Netz Material 0 (Haut): Augen, Zähne
     * und Nägel verschwinden optisch im Körper.
     */
    static _gruppen(geometrie, daten) {
        if (!geometrie.getIndex()) return;
        for (const g of daten.groups || []) {
            geometrie.addGroup(g.start, g.count, g.materialIndex);
        }
    }

    /** Die Materialliste des Körpers, in der Reihenfolge der Gruppen. */
    static materialien(THREE) {
        return BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));
    }
}
