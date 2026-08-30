import * as THREE from 'three';
import { Serverabruf } from './serverabruf.js';
import { Netzgeometrie } from './netzgeometrie.js';

/**
 * Stoffabruf — ein Kleidungsstück vom Server holen und daraus Netz und
 * Material bauen.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Dieselben acht Zeilen standen in
 * `viewer/cloth.js` und `result_character/cloth_garments.js`. Zwei Seiten,
 * dieselbe Schnittstelle, zwei Fassungen — und darin eine Reihenfolge, die man
 * beim Nachbauen leicht anders trifft.
 *
 * DIE REIHENFOLGE IST DER PUNKT: Das alte Stück wird ERST entfernt, wenn die
 * neuen Daten da sind. Wer zuerst aufräumt und dann abruft, hat bei jedem
 * Netzfehler eine nackte Figur — kein Fehlerbild, das jemand meldet, sondern
 * eines, das nach „das Kleidungsstück gibt es wohl nicht" aussieht.
 *
 * DIE FARBE hat drei Quellen, in dieser Reihenfolge:
 *
 *     1. was der Aufrufer vorgibt (eine gespeicherte Farbe)
 *     2. die Farbe aus der Antwort (nur wenn der Aufrufer sie will)
 *     3. das Farbfeld der Seite — und ohne das die Antwortfarbe
 *
 * Punkt 2 gibt es nur auf der Ergebnisseite: Dort trägt ein fertiger Auftrag
 * seine Farbe mit, während im Editor das Farbfeld gewinnt.
 */
export class Stoffabruf {
    /**
     * Ein Kleidungsstück holen und sein Netz bauen.
     *
     * @param {Object} params Abfrageparameter (`region`, `offset`, …)
     * @param {Function} entfernen wird gerufen, SOBALD die Daten da sind —
     *     hier räumt die Seite ihr altes Stück weg
     * @returns {Object|null} {daten, geometrie} — null bei Fehler
     */
    static async netz(params, entfernen) {
        const frage = Object.entries(params)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        const daten = await Serverabruf.json(`/api/character/cloth/?${frage}`);
        if (daten.error) {
            console.error('Cloth error:', daten.error);
            return null;
        }
        if (entfernen) entfernen();
        return { daten, geometrie: Netzgeometrie.bauen(daten, THREE) };
    }

    /**
     * Welche Farbe das Stück bekommt — siehe Klassenkopf.
     *
     * @param {Object} daten Serverantwort mit `color` als [r,g,b] 0..1
     * @param {Object} wahl {wunsch, ausApi, farbfeld}
     * @returns {Object} THREE.Color
     */
    static farbe(daten, { wunsch, ausApi = false, farbfeld } = {}) {
        if (wunsch) return new THREE.Color(wunsch);
        const ausAntwort = () => new THREE.Color(
            daten.color[0], daten.color[1], daten.color[2]);
        if (ausApi && daten.color) return ausAntwort();
        const feld = farbfeld ? document.getElementById(farbfeld) : null;
        return feld ? new THREE.Color(feld.value) : ausAntwort();
    }

    /**
     * Das Material dazu. `DoubleSide`, weil ein Kleidungsstück eine Fläche ist
     * und keine geschlossene Hülle — mit `FrontSide` verschwindet die Innenseite
     * an jeder Falte.
     */
    static material(farbe) {
        return new THREE.MeshStandardMaterial({
            color: farbe, roughness: 0.8, metalness: 0.0,
            side: THREE.DoubleSide,
        });
    }
}
