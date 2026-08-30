import { base64ToFloat32, blenderToThreeCoords } from './kodierung.js';

/**
 * Netzpunkte — die Punktlagen eines bestehenden Netzes ersetzen, ohne die
 * Geometrie neu zu bauen.
 *
 * WARUM (Performance-Durchgang 16.08.2026): Eine Morph- oder Metaänderung
 * ändert nur die Punktlagen. Topologie (Dreiecke), UVs, Materialgruppen und
 * das Skelett-Binding bleiben gleich. Gemessen am weiblichen Grundkörper
 * (70.851 Punkte, 138.304 Dreiecke):
 *
 *     Netz komplett neu bauen   5,24 MB Abruf + neue Geometrie + neues Binding
 *     nur Punkte ersetzen       2,26 MB Abruf, Geometrie bleibt
 *
 * Die Szene machte das schon richtig (`Charakterkoerper.neuLaden`), die
 * Foto-Seite baute bei JEDER Reglerbewegung ein vollständig neues Netz. Jetzt
 * nehmen beide diesen Weg — mit `?nur_punkte=1` am Endpunkt, damit die
 * ungenutzten 3 MB nicht erst über die Leitung gehen.
 */
export class Netzpunkte {

    /**
     * Punkte und Normalen in ein bestehendes Netz schreiben.
     *
     * @param {THREE.Mesh} netz  Netz mit vorhandener Geometrie
     * @param {Object} daten     Antwort des Netz-Endpunkts
     * @param {Function} nachbearbeiten
     *        Wird auf den Punktpuffer angewandt, NACHDEM aus
     *        Blender-Koordinaten umgerechnet wurde. Zwingend fuer Seiten, die
     *        den Koerper verschieben: Die Foto-Seite richtet ihn mit
     *        `alignBodyToSMPLX` neben das SMPL-X-Modell aus. Ohne diesen Schritt
     *        springt das Netz beim ersten Regler an die unverschobene Stelle.
     * @returns {boolean}        false, wenn die Punktzahl NICHT passt — dann
     *                           muss der Aufrufer das Netz neu bauen.
     */
    static aktualisieren(netz, daten, nachbearbeiten = null) {
        const punkte = netz?.geometry?.attributes?.position;
        if (!punkte || !daten?.vertices) return false;
        const neue = base64ToFloat32(daten.vertices);
        blenderToThreeCoords(neue);
        if (nachbearbeiten) nachbearbeiten(neue);
        if (punkte.count !== neue.length / 3) return false;

        punkte.array.set(neue);
        punkte.needsUpdate = true;
        Netzpunkte._normalen(netz, daten);
        netz.geometry.computeBoundingSphere();
        netz.geometry.computeBoundingBox();
        return true;
    }

    /**
     * Punkte aus einem ROHEN Puffer schreiben — der Weg des Live-Reglers.
     *
     * BEFUND `doppelcode` (30.08.2026): Diese sieben Zeilen standen in
     * `viewer/mesh.js` und `result_character/websocket.js`. Der Unterschied zu
     * `aktualisieren`: Hier kommen die Zahlen nicht als Base64 aus einer
     * Antwort, sondern als `ArrayBuffer` über den WebSocket — bei jeder
     * Reglerbewegung, mehrmals je Sekunde. Deshalb wird hier auch NICHTS
     * nachgerechnet, was warten kann: keine Normalen, keine Bounding-Box.
     *
     * DIE UMRECHNUNG DARF NICHT FEHLEN. Blender hat Z nach oben, Three.js Y —
     * ohne `blenderToThreeCoords` liegt die Figur auf dem Rücken, und zwar
     * erst ab dem ersten Reglerzug. Das sieht nach einem Fehler des Reglers
     * aus und ist einer des Puffers.
     *
     * @param {THREE.BufferGeometry} geometrie Geometrie des Körpers
     * @param {ArrayBuffer} puffer Float32-Punkte in Blender-Koordinaten
     * @returns {boolean} false, wenn es nichts zu schreiben gab
     */
    static ausPuffer(geometrie, puffer) {
        if (!geometrie) return false;
        const punkte = geometrie.attributes.position;
        const neue = new Float32Array(puffer);
        blenderToThreeCoords(neue);
        punkte.array.set(neue);
        punkte.needsUpdate = true;
        geometrie.computeBoundingSphere();
        return true;
    }

    /**
     * Normalen übernehmen. Fehlen sie in der Antwort, werden sie gerechnet —
     * das ist teurer, aber besser als flache Beleuchtung.
     */
    static _normalen(netz, daten) {
        const ziel = netz.geometry.attributes.normal;
        if (!daten.normals || !ziel) {
            netz.geometry.computeVertexNormals();
            return;
        }
        const neue = base64ToFloat32(daten.normals);
        blenderToThreeCoords(neue);
        if (ziel.array.length !== neue.length) {
            netz.geometry.computeVertexNormals();
            return;
        }
        ziel.array.set(neue);
        ziel.needsUpdate = true;
    }
}
