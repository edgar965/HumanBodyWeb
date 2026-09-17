import * as THREE from 'three';
import { Netzentsorgung } from './netzentsorgung.js';
import { Knochenbau } from './knochenbau.js';

/**
 * Modell — die Figur, wie jede Seite sie kennt: EINE Klasse mit `bauen()`.
 *
 * ANLASS (Edgar, 13.09.2026): „Alle HTML-Seiten wie Theatre, BVH Studio,
 * Szene usw. sollen die Figur NICHT selber bauen, sondern eine globale
 * Klasse nutzen … Von der sollen HumanBody, UMA, MakeHuman ableiten und die
 * Bauen-Methode implementieren." Vorher baute jede Seite ihre Figur selbst —
 * die Szene in `CharacterInstance`, das Studio in `Spurfigur`, das Theatre
 * in `Vorgabefigur`, die Ergebnisseite in `mesh_loading.js` — und jede
 * vergaß etwas anderes: das Studio Lippen, Brauen und Nägel, das Theatre
 * die GarmentCode-Stücke.
 *
 * DIE ARTEN (je eine Datei daneben, alle `extends Modell`):
 *   `HumanbodyModell`   — das HumanBody-Netz vom Server, Morphs, Skelett,
 *                          Details, Haare, Kleidung, GarmentCode
 *   `UmaModell`         — die GLB einer UMA-Figur mit Skelett und DNA-Reglern
 *   `MakehumanModell`   — MakeHuman-Basiskörper mit Targets und Kleidung
 *   `SmplModell`        — Referenzkörper von GarmentCode (SMPL)
 *   `UmapythonModell`   — UMAs Rassen, in Python gebaut
 *
 * WAS JEDE ART HAT: `group` (die Gruppe, die auf die Bühne kommt),
 * `bodyMesh` (die Haut), `skelett` (`{skeleton, rootBone, bones,
 * boneByName}` oder null), `presetName`, `bodyType`, `quelle`. Die Felder
 * der HumanBody-Figur (`clothMeshes`, `hairMesh`, `morphs`, …) tragen alle
 * Arten — bei den anderen leer —, damit Listen, Auswahl und Speichern nicht
 * je Quelle unterscheiden müssen (12.09.2026, `Figurbasis`).
 *
 * `bauen()` holt die Daten und füllt `group`; die Unterklasse implementiert
 * es. Wer die Figur danach auf seine Bühne stellt, ist die Seite — sie kennt
 * ihre Szene, ihre Spur, ihren Zustand. Die Speicherseite der Szene
 * (`toJSON`/`fromJSON` mit GarmentCode-Stücken) liegt in
 * `scene/figurablage.js`, weil sie Szenenzustand braucht.
 */
export class Modell {

    constructor(id, quelle) {
        this.id = id;
        this.quelle = quelle;
        this.presetName = '';
        this.presetKey = null;
        this.bodyType = '';
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        /** Das Skelett der Art — Rigify, `Knochenbau` oder GLB; die Form ist je Art anders.
         *  @type {any} */
        this.skelett = null;
        /** @type {Object<string, any>} */
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

    /**
     * Die Figur aufbauen: Daten holen, Netz(e) und Skelett in `group`.
     * @param {Object} optionen  je Art; siehe die Unterklasse
     * @returns {Promise<Modell>} this
     */
    async bauen(optionen = {}) {   // eslint-disable-line no-unused-vars
        throw new Error(`${this.constructor.name}.bauen() ist nicht implementiert`);
    }

    /**
     * Das eigene Skelett aus den Serverangaben bauen — das alte ZUERST abräumen.
     *
     * `bauen()` läuft bei jedem Reglerzug erneut (MakeHuman: 269 Regler,
     * SMPL: die Formregler). Ohne das Abräumen hängen nach zehn Zügen zehn
     * Skelette ineinander, und der `SkeletonHelper` zeigt die alten
     * Stellungen mit. Ohne `angaben` bleibt die Figur ohne Knochen.
     * Stand in `MakehumanModell` und `SmplModell` gleich (Befund `doppelcode`).
     */
    skelettBauen(angaben) {
        this.skelett = Knochenbau.abraeumen(this.skelett);
        if (!angaben) return;
        this.skelett = Knochenbau.bauen(angaben, this.group);
    }

    dispose() {
        Netzentsorgung.baum(this.group);
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    /** Die Lage der Figurgruppe, wie das Speichern sie ablegt. */
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
     * Die Felder, die jede Art ablegt; die Unterklasse legt ihre eigenen
     * daneben. Die Szene ergänzt die GarmentCode-Stücke (`Figurablage`).
     */
    grunddaten() {
        return {
            id: this.id,
            quelle: this.quelle,
            presetName: this.presetName,
            presetKey: null,
            bodyType: this.bodyType,
            transform: this.lage(),
        };
    }
}
