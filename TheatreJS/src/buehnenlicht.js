import * as THREE from 'three';

/**
 * Die Beleuchtung der Theaterbühne — drei Richtlichter plus Umgebungslicht,
 * jedes Richtlicht mit einem anklickbaren Symbol.
 *
 * Aus scene-setup.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `createScene()` hatte 130 Zeilen). Licht und Boden waren dort dreimal fast
 * wortgleich hintereinander aufgebaut — hier steht der Aufbau einmal.
 */
export class Buehnenlicht {
    /**
     * Ein Richtlicht mit Symbol. Die Werte sind die aus dem Dashboard.
     * @param {string} name Schlüssel in den Rückgabeobjekten
     * @param {number} farbe Lichtfarbe
     * @param {number} staerke Intensität
     * @param {number[]} ort Position [x, y, z]
     */
    constructor(name, farbe, staerke, ort) {
        this.name = name;
        this.licht = new THREE.DirectionalLight(farbe, staerke);
        this.licht.position.set(ort[0], ort[1], ort[2]);
        this.symbol = Buehnenlicht.symbol(new THREE.Color(farbe));
        this.symbol.position.copy(this.licht.position);
        this.symbol.lookAt(new THREE.Vector3(0, 0, 0));
        this.symbol.userData.light = this.licht;
    }

    /** Trägt Licht und Symbol in die Szene ein. */
    eintragen(scene) {
        scene.add(this.licht);
        scene.add(this.symbol);
    }

    /**
     * Kleines Lichtsymbol: Kegel (zeigt die Richtung) auf leuchtender Kugel.
     * `depthTest: false` und `renderOrder: 999` — das Symbol soll auch hinter
     * der Figur sichtbar und anklickbar bleiben.
     * @param {THREE.Color} farbe
     * @returns {THREE.Group}
     */
    static symbol(farbe) {
        const gruppe = new THREE.Group();
        const kegel = new THREE.Mesh(
            new THREE.ConeGeometry(0.4, 1.0, 16),
            new THREE.MeshBasicMaterial({
                color: farbe,
                transparent: true,
                opacity: 1.0,
                side: THREE.DoubleSide,
                depthTest: false,
                depthWrite: false,
            }));
        kegel.rotation.x = Math.PI;          // Spitze zeigt nach unten
        kegel.renderOrder = 999;

        const kugel = new THREE.Mesh(
            new THREE.SphereGeometry(0.35, 32, 32),
            new THREE.MeshBasicMaterial({
                color: new THREE.Color(1, 1, 1),   // weiß, nicht Lichtfarbe
                emissive: farbe,
                emissiveIntensity: 2.0,
                transparent: true,
                opacity: 1.0,
                depthTest: false,
                depthWrite: false,
            }));
        kugel.position.y = 0.5;
        kugel.renderOrder = 999;

        gruppe.add(kegel);
        gruppe.add(kugel);
        return gruppe;
    }

    /**
     * Baut die komplette Bühnenbeleuchtung auf.
     * @param {THREE.Scene} scene
     * @returns {{lights: Object, lightIcons: Object}}
     */
    static aufbauen(scene) {
        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambient);

        const strahler = [
            new Buehnenlicht('spotLeft', 0xffffff, 3.0, [2, 4, -5]),
            new Buehnenlicht('spotRight', 0xeeeeff, 2.0, [-3, 3, -4]),
            new Buehnenlicht('backLight', 0xffeedd, 2.5, [0, 4, 5]),
        ];
        const lights = { ambient };
        const lightIcons = {};
        for (const s of strahler) {
            s.eintragen(scene);
            lights[s.name] = s.licht;
            lightIcons[s.name + 'Icon'] = s.symbol;
        }
        return { lights, lightIcons };
    }
}
