import * as THREE from 'three';
import { _getOrLoadTexture } from './formenbauer.js';

/**
 * Gruppiert Geometriestücke nach ihrem Material.
 *
 * Zwei Stücke teilen sich ein Material, wenn sie dieselbe Textur haben — oder,
 * ohne Textur, dieselbe Farbe. Jede Gruppe wird später zu genau einem
 * `MeshStandardMaterial` und einer Zeichengruppe der verschmolzenen Geometrie.
 *
 * Aus netzverschmelzung.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`: `zusammenfuegen()` hatte 113 Zeilen).
 */
export class Materialgruppen {
    constructor() {
        /** @type {Map<string, {color, texture, indices: number[]}>} */
        this.gruppen = new Map();
    }

    /**
     * @param {Array} stuecke Geometriestücke mit `color`/`texture`
     * @returns {Materialgruppen}
     */
    static von(stuecke) {
        const gruppen = new Materialgruppen();
        stuecke.forEach((stueck, i) => gruppen._eintragen(stueck, i));
        return gruppen;
    }

    _eintragen(stueck, i) {
        const schluessel = stueck.texture
            ? `tex:${stueck.texture}` : `col:${stueck.color}`;
        let gruppe = this.gruppen.get(schluessel);
        if (!gruppe) {
            gruppe = { color: stueck.color, texture: stueck.texture,
                       indices: [] };
            this.gruppen.set(schluessel, gruppe);
        }
        gruppe.indices.push(i);
    }

    /** Reihenfolge der Gruppen — sie bestimmt den Materialindex. */
    [Symbol.iterator]() {
        return this.gruppen.values();
    }

    /**
     * Das Material einer Gruppe.
     * @param {{color, texture}} gruppe
     * @returns {THREE.MeshStandardMaterial}
     */
    static material(gruppe) {
        const werte = {
            color: new THREE.Color(gruppe.color),
            roughness: 0.6,
            metalness: 0.2,
            flatShading: false,
        };
        if (gruppe.texture) {
            werte.map = _getOrLoadTexture(gruppe.texture);
            // Der Farbton bleibt neutral, damit die Textur ihre echten Farben
            // zeigt.
            werte.color = new THREE.Color(0xffffff);
        }
        return new THREE.MeshStandardMaterial(werte);
    }
}
