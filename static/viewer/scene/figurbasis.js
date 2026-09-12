import * as THREE from 'three';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { GarmentcodeAblage } from './garmentcode_ablage.js';

/**
 * Figurbasis — was die vier Figurarten neben HumanBody gemeinsam haben.
 *
 * WARUM (12.09.2026, Befund `doppelcode`): `SmplFigur`, `MhFigur`, `UmaFigur`
 * und `UmapythonFigur` führten dieselben vier Blöcke viermal — die leeren
 * Felder der HumanBody-Figur, `dispose`, den Rumpf von `toJSON` (Kennung,
 * Quelle, Lage, GarmentCode-Stücke) und `fromJSON`. Vier Kopien laufen
 * auseinander: `UmapythonFigur.dispose` rief `Netzentsorgung.entfernen(kind)`
 * mit EINEM Argument — die Methode nimmt (Elternteil, Objekt), gab also
 * nichts frei und liess die leere Gruppe in der Szene stehen.
 *
 * Die Unterklasse setzt nach `super(id, QUELLE)` ihre eigenen Felder,
 * `presetName` und `bodyType`; `toJSON` ergänzt `grunddaten()` um ihre
 * eigenen Werte, und `fromJSON` ruft `Figurbasis.ausJSON(Klasse, daten)`.
 */
export class Figurbasis {

    constructor(id, quelle) {
        this.id = id;
        this.quelle = quelle;
        this.presetName = '';
        this.presetKey = null;
        this.bodyType = '';
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        /** Das eigene Skelett — dieselbe Form bei allen vier Arten, damit
         *  `Rigauswahl` es ohne Sonderfall findet. */
        this.skelett = null;
        // Felder der HumanBody-Figur, hier leer: `charakterliste`,
        // `properties` und die Auswahl fragen sie an jeder Figur ab.
        this.clothMeshes = {};
        this.hairMesh = null;
        this.garments = [];
        this.garmentState = {};
        this.morphs = {};
        this.meta = {};
        this.cloth = [];
        this.hairStyle = null;
        this.mhProxies = {};
        this.generatedConfig = null;
        this.selected = false;
        this.isSkinned = false;
        this.rigifySkeleton = null;
    }

    dispose() {
        Netzentsorgung.baum(this.group);
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    /** Die Lage der Figurgruppe, wie `toJSON` sie ablegt. */
    lage() {
        return {
            position: this.group.position.toArray(),
            rotation: [this.group.rotation.x, this.group.rotation.y,
                       this.group.rotation.z],
            scale: this.group.scale.toArray(),
        };
    }

    /** Die gespeicherte Lage wieder einsetzen; fehlende Teile bleiben stehen. */
    lageSetzen(lage) {
        if (!lage) return;
        if (lage.position) this.group.position.fromArray(lage.position);
        if (lage.rotation) {
            this.group.rotation.set(lage.rotation[0], lage.rotation[1],
                                    lage.rotation[2]);
        }
        if (lage.scale) this.group.scale.fromArray(lage.scale);
    }

    /**
     * Die Felder, die jede Figurart ablegt; die Unterklasse legt ihre
     * eigenen daneben (`{ ...this.grunddaten(), koerper: this.koerper }`).
     */
    grunddaten() {
        return {
            id: this.id,
            quelle: this.quelle,
            presetName: this.presetName,
            presetKey: null,
            bodyType: this.bodyType,
            // GarmentCode-Stuecke ueberleben das Speichern (08.09.2026).
            [GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(this),
            transform: this.lage(),
        };
    }

    /**
     * `fromJSON` aller vier Arten: bauen, laden, Lage setzen, anziehen.
     *
     * Die Reihenfolge zählt: `GarmentcodeAblage.laden` NACH `load()`, weil
     * die Stücke das Skelett der Figur brauchen und in der Lage der
     * Figurgruppe binden (07.09.2026, „Kleider von MakeHuman animieren
     * immer noch nicht").
     */
    static async ausJSON(Klasse, daten) {
        const figur = new Klasse(daten.id, daten);
        await figur.load();
        figur.lageSetzen(daten.transform);
        await GarmentcodeAblage.laden(figur, daten[GarmentcodeAblage.FELD]);
        return figur;
    }
}
