import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Buehne } from '../gemeinsam/buehne.js';

/**
 * Meshbetrachter — zeigt ein GLB in einer eigenen Leinwand (Reiter „Mesh", 26.09.2026).
 * Nutzt dieselbe Bühne wie jede Figurenseite (`gemeinsam/buehne.js`), zentriert und
 * skaliert das geladene Netz einmal auf den sichtbaren Bereich (die Höhe kommt aus den
 * Meshoptionen, muss aber nicht exakt stimmen — hier zählt nur „sieht man ganz").
 *
 * ABER mit eigenem Licht (Edgar, 27.09.2026: „licht … soll ambient sein, so kann man nichts
 * erkennen"): Die Bühne leuchtet eine Figur wie im Fotostudio aus — drei gerichtete Lichter
 * und ACES-Tonemapping. Das ist richtig, wenn eine Szene gut AUSSEHEN soll, und falsch, wenn
 * man BEURTEILEN will, was ein Formmodell geliefert hat: Schlagschatten verstecken Dellen,
 * das Tonemapping verschiebt jede Farbe. Hier also rundum gleichmäßig und ohne Tonemapping —
 * was man sieht, steht so in der gebackenen Textur.
 */
export class Meshbetrachter {

    /** Stärke des Umgebungslichts bzw. der Umgebungsspiegelung (ohne Tonemapping gemessen). */
    static UMGEBUNG = 1.0;
    static SPIEGELUNG = 1.4;

    constructor(behaelter) {
        this.behaelter = behaelter;
        this.leinwand = document.createElement('canvas');
        this.behaelter.appendChild(this.leinwand);
        Object.assign(this, Buehne.bauen(this.leinwand, { masse: 'rahmen', stil: true }));
        this._ambientesLicht();
        this._lader = new GLTFLoader();
        this._objekt = null;
        this._laufend = false;
        window.addEventListener('resize', () => this._groesseAnpassen());
        this._animieren();
    }

    /** Studiobeleuchtung raus, Rundumlicht rein — siehe Klassenkommentar.
     *
     *  Ein `AmbientLight` allein reicht nicht: Es beleuchtet nur den diffusen Anteil, und
     *  TRELLIS.2 liefert eine PBR-Textur MIT Metallic-Kanal — metallische Stellen blieben
     *  damit schwarz. Deshalb zusätzlich eine gleichmäßig weiße Umgebung über den
     *  PMREM-Generator, die auch den spiegelnden Anteil bedient.
     *
     *  NICHT über `three/addons/environments/RoomEnvironment.js` (27.09.2026): Diesen Ordner
     *  gibt es in `static/vendor/three/examples/jsm/` nicht, und ein fehlgeschlagener
     *  Modulimport bricht die ganze Seite STUMM ab — die Seite lud mit 200 und zeigte nur
     *  noch „Noch kein Netz" (`~/.claude/rules/es-module-stumme-fehler.md`). Eine Szene mit
     *  weißem Hintergrund tut hier dasselbe und braucht kein Addon.
     */
    _ambientesLicht() {
        for (const name of ['keyLight', 'fillLight', 'backLight']) this[name]?.removeFromParent();
        this.ambient.intensity = Meshbetrachter.UMGEBUNG;
        this.renderer.toneMapping = THREE.NoToneMapping;
        const weiss = new THREE.Scene();
        weiss.background = new THREE.Color(0xffffff);
        const pmrem = new THREE.PMREMGenerator(this.renderer);
        this.scene.environment = pmrem.fromScene(weiss).texture;
        this.scene.environmentIntensity = Meshbetrachter.SPIEGELUNG;
        pmrem.dispose();
    }

    async laden(url) {
        this.entfernen();
        const gltf = await this._lader.loadAsync(url);
        const objekt = gltf.scene;
        this._ausrichten(objekt);
        this.scene.add(objekt);
        this._objekt = objekt;
        return objekt;
    }

    /** Alle Mesh-Knoten des geladenen Netzes — für `Meshfotogewicht` (Live-Vorschau der
     *  Vertexfarben bei Reglerbewegung, ändert `geometry.attributes.color` direkt). */
    meshKnoten() {
        const aus = [];
        this._objekt?.traverse(kind => { if (kind.isMesh) aus.push(kind); });
        return aus;
    }

    entfernen() {
        if (!this._objekt) return;
        this.scene.remove(this._objekt);
        this._objekt.traverse(kind => {
            kind.geometry?.dispose?.();
            const materialien = Array.isArray(kind.material) ? kind.material : [kind.material];
            for (const material of materialien) {
                if (!material) continue;
                for (const schluessel of ['map', 'normalMap', 'roughnessMap', 'metalnessMap']) {
                    material[schluessel]?.dispose?.();
                }
                material.dispose();
            }
        });
        this._objekt = null;
    }

    /** Das Netz auf Größe 2 zentrieren und auf den Boden stellen — unabhängig von seinem
     *  eigenen Maßstab sieht man es damit immer ganz, egal wie `hoehe_cm` gerechnet hat.
     *
     *  Und die Steuerung auf SEINE Mitte richten (Edgar, 27.09.2026: „Die Figur ist auch
     *  sonderbar gedreht, so dass ich die nicht bedienen kann"): Die Bühne setzt das Ziel
     *  fest auf (0, 0.9, 0) — die Höhe einer Figur in der Szene. Ein Netz, das nicht
     *  zufällig genauso hoch steht (ein liegendes Objekt, ein Kopf, ein Zwischenergebnis),
     *  kreist damit um einen Punkt neben sich: Man zieht die Maus und das Objekt wandert
     *  aus dem Bild, statt sich zu drehen. Das Ziel gehört an die halbe Höhe DIESES Netzes.
     */
    _ausrichten(objekt) {
        const kasten = new THREE.Box3().setFromObject(objekt);
        const groesse = kasten.getSize(new THREE.Vector3());
        const mitte = kasten.getCenter(new THREE.Vector3());
        const groesster = Math.max(groesse.x, groesse.y, groesse.z, 1e-6);
        const massstab = 2 / groesster;
        objekt.scale.setScalar(massstab);
        objekt.position.set(-mitte.x * massstab, -kasten.min.y * massstab, -mitte.z * massstab);
        const hoehe = groesse.y * massstab;
        this.controls.target.set(0, hoehe / 2, 0);
        this.camera.position.set(0, hoehe / 2, Math.max(2.6, hoehe * 1.6));
        this.controls.update();
    }

    _groesseAnpassen() {
        const [breite, hoehe] = Buehne.masse(this.leinwand, 'rahmen');
        if (!breite || !hoehe) return;
        this.camera.aspect = breite / hoehe;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(breite, hoehe, true);
    }

    _animieren() {
        if (this._laufend) return;
        this._laufend = true;
        const takt = () => {
            if (!this.behaelter.isConnected) { this._laufend = false; return; }
            this.controls.update();
            this.renderer.render(this.scene, this.camera);
            requestAnimationFrame(takt);
        };
        this._groesseAnpassen();
        requestAnimationFrame(takt);
    }
}
