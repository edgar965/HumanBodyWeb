/**
 * Laden von Bühnenobjekten: GLB-Dateien, Figuren, BVH-Skelette.
 *
 * UMBAU 18.08.2026: 318 Zeilen. Herausgeloest wurden:
 *
 *     laden/figurnetz.js         Netz aus Serverdaten / erzeugtem Modell
 *     laden/bvhszene.js          BVH-Text als Skelett in die Buehne
 *     laden/skelettdaten.js      Skelett, Hautgewichte, Rig-Knochen (gemerkt)
 *     laden/theatreanmeldung.js  Objekt als Theatre-Objekt anmelden (war 4x)
 *
 * Hier bleiben die Fassaden, die rund zwanzig Aufrufstellen benutzen.
 */
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Vorgabefigur } from './laden/vorgabefigur.js';
import { Figurnetz } from './laden/figurnetz.js';
import { Bvhszene } from './laden/bvhszene.js';
import { Theatreanmeldung } from './laden/theatreanmeldung.js';

const gltfLoader = new GLTFLoader();

/**
 * Eine GLB-Datei von einer Adresse laden und in die Szene haengen.
 * @param {string} url
 * @param {THREE.Scene} scene
 * @returns {Promise<THREE.Group>}
 */
export async function loadGLBAsset(url, scene) {
    const gltf = await gltfLoader.loadAsync(url);
    const gruppe = gltf.scene;
    scene.add(gruppe);
    // Schatten an allen Netzen — GLB-Dateien bringen die Einstellung nicht mit.
    gruppe.traverse(teil => {
        if (teil.isMesh) {
            teil.castShadow = true;
            teil.receiveShadow = true;
        }
    });
    Theatreanmeldung.anmelden(gruppe, null, 'Asset');
    return gruppe;
}

/**
 * Eine GLB aus einer lokalen Datei laden.
 * @param {File} file
 * @param {THREE.Scene} scene
 */
export async function loadGLBFromFile(file, scene) {
    const adresse = URL.createObjectURL(file);
    try {
        return await loadGLBAsset(adresse, scene);
    } finally {
        URL.revokeObjectURL(adresse);
    }
}

/** Die HumanBody-Figur mit den Vorgabewerten ueber die Django-API laden. */
export async function loadCharacterModel(scene) {
    const antwort = await fetch('/api/character/mesh/');
    if (!antwort.ok) {
        throw new Error(`Character mesh API error: ${antwort.status}`);
    }
    const gruppe = Figurnetz.bauen(await antwort.json());
    scene.add(gruppe);
    Theatreanmeldung.anmelden(gruppe, 'Character');
    return gruppe;
}

/**
 * Figur samt Haaren und Kleidung aus einer Vorgabe laden.
 *
 * Der Rumpf steckt in laden/vorgabefigur.js (vorher 105 Zeilen hier, plus 40
 * fuer das Haarladen). Diese Fassade bleibt, damit die rund zwanzig
 * Aufrufstellen im Projekt unveraendert weiterlaufen.
 */
export async function loadCharacterFromPreset(scene, preset, presetName) {
    const figur = new Vorgabefigur({
        netzBauen: daten => Figurnetz.bauen(daten),
        erzeugtesModell: vorschrift => Figurnetz.erzeugtesModell(vorschrift),
        inTheatre: (gruppe, name) =>
            Theatreanmeldung.anmelden(gruppe, name, 'Character'),
    });
    return figur.laden(scene, preset, presetName);
}

/** BVH-Text lesen und als Skelett in die Buehne haengen. */
export function loadBVHFromText(bvhText, scene, animName) {
    return Bvhszene.ausText(bvhText, scene, animName);
}
