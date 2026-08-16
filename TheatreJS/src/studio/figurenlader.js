import { loadCharacterFromPreset } from '../asset-loader.js';
import { fetchScene, fetchSceneList, fetchModel, fetchModelList,
         saveScene } from '../scene-manager.js';

/**
 * Figurenlader — Figuren aus Vorgaben und Szenen in die Bühne holen.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026). Der Kern stand dort DREIMAL,
 * jeweils fuenf gleiche Zeilen:
 *
 *     charGroup.userData.isCharacter = true;
 *     charGroup.userData.presetName = …;
 *     charGroup.userData.bodyType = … || 'Unknown';
 *     loadedCharacters.push(charGroup);
 *     selectedCharacter = charGroup;   // Auto-select loaded character
 *     skinner.autoUmwandeln(charGroup);
 *
 * einmal beim Laden einer Szene, einmal beim Klick in der Modell-Liste, einmal
 * beim Anwenden der Vorgaben beim Seitenstart. Wer die Kennzeichnung aendert,
 * muss sie sonst an drei Stellen aendern — und findet die dritte nicht.
 */
export class Figurenlader {

    static UNBEKANNT = 'Unknown';

    /**
     * @param {THREE.Scene} scene
     * @param {Array} figuren   Liste aller geladenen Figuren (dieselbe, die
     *        main.js und der Raycaster benutzen)
     * @param {Skinner} skinner
     * @param {Auswahl} auswahl
     */
    constructor(scene, figuren, skinner, auswahl) {
        this.scene = scene;
        this.figuren = figuren;
        this.skinner = skinner;
        this.auswahl = auswahl;
    }

    /**
     * Eine Figur aus einer Vorgabe laden, kennzeichnen, einsortieren,
     * auswaehlen und ans Skelett binden. Der gemeinsame Weg aller drei
     * frueheren Fundstellen.
     */
    async ausVorgabe(vorgabe, name) {
        const figur = await loadCharacterFromPreset(this.scene, vorgabe, name);
        figur.userData.isCharacter = true;
        figur.userData.presetName = name;
        figur.userData.bodyType = vorgabe.body_type || Figurenlader.UNBEKANNT;
        this.figuren.push(figur);
        this.auswahl.figurVormerken(figur);
        this.skinner.autoUmwandeln(figur);
        return figur;
    }

    /** Eine gespeicherte Vorgabe holen und laden. */
    async modell(name) {
        return this.ausVorgabe(await fetchModel(name), name);
    }

    /** Alle Figuren einer gespeicherten Szene laden. */
    async szene(name) {
        const daten = await fetchScene(name);
        const geladen = [];
        for (const figurdaten of (daten.characters || [])) {
            geladen.push(await this.ausVorgabe(figurdaten,
                                               figurdaten.name || name));
        }
        console.debug('Szene geladen:', name, geladen.length, 'Figuren');
        return geladen;
    }

    /** Namen der gespeicherten Szenen. */
    szenenliste() {
        return fetchSceneList();
    }

    /** Namen der gespeicherten Modellvorgaben. */
    modellliste() {
        return fetchModelList();
    }

    /**
     * Aktuellen Bühnenzustand speichern.
     *
     * Der Zustand geht unveraendert als JSON an den Server, deshalb bleibt er
     * ein einfaches Objekt und wird keine Klasse — anders als die Datensaetze,
     * die durch mehrere Funktionen wandern.
     */
    speichern(name, buehne) {
        const { camera, controls, lights } = buehne;
        return saveScene(name, {
            camera: {
                position: camera.position.toArray(),
                fov: camera.fov,
                target: controls.target.toArray(),
            },
            lights: Object.fromEntries(
                ['spotLeft', 'spotRight', 'backLight'].map(name => [name, {
                    position: lights[name].position.toArray(),
                    intensity: lights[name].intensity,
                    color: '#' + lights[name].color.getHexString(),
                }])),
            characters: [],
        });
    }
}
