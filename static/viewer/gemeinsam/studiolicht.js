/**
 * Studiolicht — die Standardbeleuchtung der Charakterseite an EINER Stelle (09.11.2026).
 *
 * Die Werte standen bis hierher nur in `charakter/state.js` (`LIGHT_PRESETS.studio`, gemessen aus „cute girl 5.0.blend“, Herleitung dort). Seit 09.11.2026 zeichnet auch Mesh-Genesis
 * die Genesis-Figuren damit (`Meshgenesisansicht`; Edgar zu damiraalt: „scham wieder falsch gebaut … nimm die Pipeline der Scham wie bei Damira Model im Charakter Ansicht“ — das
 * Stück war bitgleich, im Feld sah es nur unter dem Licht von Mesh-Genesis anders aus, Halbkugel 1,1 + Richtung 1,6 von oben links, ohne Tone-Mapping).
 */
import * as THREE from 'three';

export class Studiolicht {
    /** Form wie `LIGHT_PRESETS` der Charakterseite: Stärke, Farbe, Platz (m), Belichtung des ACES-Tone-Mappings. */
    static WERTE = {
        key:     { intensity: 3.0,  color: 0xffffff, pos: [0.43, 1.58, 6.50] },
        fill:    { intensity: 0.375, color: 0xffffff, pos: [6.14, -0.91, -2.52] },
        back:    { intensity: 0.75, color: 0xffffff, pos: [2.25, 0.79, -6.26] },
        ambient: { intensity: 0.8, color: 0xffffff },
        exposure: 1.6,
    };
    static TONEMAPPING = THREE.ACESFilmicToneMapping;

    /** Die vier Lichter (drei gerichtete, ein Umgebungslicht) als neue three.js-Objekte. */
    static lichter() {
        const w = Studiolicht.WERTE;
        const gerichtet = ['key', 'fill', 'back'].map(name => {
            const licht = new THREE.DirectionalLight(w[name].color, w[name].intensity);
            licht.position.set(...w[name].pos);
            return licht;
        });
        return [...gerichtet, new THREE.AmbientLight(w.ambient.color, w.ambient.intensity)];
    }

    /** `zeichnen` mit Tone-Mapping und Belichtung der Charakterseite; danach stehen beide wieder wie vorher. */
    static mitTonwerten(renderer, zeichnen) {
        const tm = renderer.toneMapping, be = renderer.toneMappingExposure;
        renderer.toneMapping = Studiolicht.TONEMAPPING;
        renderer.toneMappingExposure = Studiolicht.WERTE.exposure;
        try {
            zeichnen();
        } finally {
            renderer.toneMapping = tm;
            renderer.toneMappingExposure = be;
        }
    }
}
