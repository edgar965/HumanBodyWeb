import { Netzgeometrie } from './netzgeometrie.js';
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
        const geometrie = Koerpernetz.geometrie(daten, THREE);
        Koerpernetz.gruppen(geometrie, daten);
        return { geometrie, materialien: Koerpernetz.materialien(THREE) };
    }

    /**
     * Die nackte Geometrie: Punkte, Flaechen, UVs, Normalen — ohne
     * Materialgruppen und ohne Materialliste.
     *
     * WARUM GETRENNT (28.08.2026, Befund `doppelcode`): Drei weitere Stellen
     * bauten dieselbe Geometrie noch einmal von Hand — die Spuren im
     * BVH-Studio, das Foto-Netz und die Vergleichsansicht. Sie brauchen die
     * Materialgruppen des Koerpers nicht und konnten `bauen()` deshalb nicht
     * benutzen; das war der ganze Unterschied.
     *
     * @param nachPunkten Optionaler Eingriff am Punktpuffer, NACH der
     *        Achsdrehung und VOR dem Attribut. Das Foto-Netz richtet die
     *        Punkte dort auf SMPL-X aus; ohne diesen Haken haette es seine
     *        eigene Kopie behalten muessen.
     */
    static geometrie(daten, THREE, nachPunkten = null) {
        return Netzgeometrie.bauen(daten, THREE, nachPunkten);
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

    /**
     * Materialgruppen — nur sinnvoll mit Index.
     *
     * Ohne die Gruppen trägt das ganze Netz Material 0 (Haut): Augen, Zähne
     * und Nägel verschwinden optisch im Körper.
     */
    static gruppen(geometrie, daten) {
        if (!geometrie.getIndex()) return;
        for (const g of daten.groups || []) {
            geometrie.addGroup(g.start, g.count, g.materialIndex);
        }
    }

    /**
     * Materialien UND Materialgruppen in einem Schritt.
     *
     * WARUM ZUSAMMEN (28.08.2026, Befund `doppelcode`): Die beiden gehören
     * zusammen und standen trotzdem dreimal getrennt da — in `bauen()` hier,
     * in `bvh_studio/spurfigur.js` und in `photo_to_3d/fotokoerpernetz.js`.
     *
     * Der Rückgabewert ist der heikle Teil: OHNE Gruppen kann Three.js mit
     * einem Array nichts anfangen und rendert das Netz SCHWARZ. Deshalb dann
     * das Hautmaterial allein. `spurfigur` hat diese Verzweigung nur an der
     * Gruppenzahl festgemacht, nicht am Index — ein Netz ohne Index bekam
     * dort eine Materialliste, die keine Gruppe adressiert.
     *
     * @param nachbereiten Optionaler Eingriff an der Liste, BEVOR sie
     *     zurückgeht — die Spuren im BVH-Studio färben dort ihre Hautfarbe
     *     ein.
     */
    static materialsatz(geometrie, daten, THREE, nachbereiten = null) {
        const materialien = Koerpernetz.materialien(THREE);
        if (nachbereiten) nachbereiten(materialien);
        Koerpernetz.gruppen(geometrie, daten);
        return geometrie.groups.length ? materialien : materialien[0];
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
