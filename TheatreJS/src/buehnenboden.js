import * as THREE from 'three';

/**
 * Der Bühnenboden — Holzfläche mit Randleiste.
 *
 * Aus scene-setup.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`).
 */
export class Buehnenboden {
    /**
     * @param {THREE.Scene} scene
     * @returns {{flaeche: THREE.Mesh, rand: THREE.Mesh}}
     */
    static aufbauen(scene) {
        const flaeche = new THREE.Mesh(
            new THREE.PlaneGeometry(14, 10),
            new THREE.MeshStandardMaterial({
                color: 0x4a3a2e,     // helleres Braun, damit man etwas sieht
                roughness: 0.35,
                metalness: 0.05,
            }));
        flaeche.rotation.x = -Math.PI / 2;
        flaeche.position.y = 0.0;
        flaeche.receiveShadow = true;
        scene.add(flaeche);

        // Schmale Leiste, die die Bühnenkante markiert.
        const rand = new THREE.Mesh(
            new THREE.BoxGeometry(14.2, 0.06, 10.2),
            new THREE.MeshStandardMaterial({ color: 0x3a2a1a, roughness: 0.6 }));
        rand.position.y = -0.04;
        rand.receiveShadow = true;
        scene.add(rand);

        return { flaeche, rand };
    }
}
