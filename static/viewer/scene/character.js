/**
 * Scene Editor -- CharacterInstance class + character management.
 */
import { THREE, BODY_MATERIALS, state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, _getBodyTop } from './utils.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import './skeleton.js';
import './undo.js';
import './garments.js';
import './modellgenerator/zustand.js';
import { Charakterzubehoer } from './charakter_zubehoer.js';
import { Startmessung } from '../gemeinsam/startmessung.js';
import { Charakterkoerper } from './charakter_koerper.js';
import {
    addCharacterFromPreset, charakterAusModelldaten,
    clearAllCharacters, deleteCharacter,
    deselectCharacter, focusCharacter, loadDefaultCharacter,
    selectCharacter, setTransformMode, updateCharacterListUI,
    updateVertexCount,
} from './charakterliste.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { GarmentcodeAblage } from './garmentcode_ablage.js';
import { Garderobenstand } from './garderobenstand.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';

// =========================================================================
// CharacterInstance
// =========================================================================
export class CharacterInstance {
    constructor(id, presetData) {
        this.id = id;
        this.presetName = presetData.name || presetData.label || 'Unnamed';
        this.bodyType = presetData.body_type || 'Female_Caucasian';
        this.morphs = presetData.morphs || {};
        this.meta = presetData.meta || {};
        this.cloth = presetData.cloth || [];
        this.hairStyle = presetData.hair_style || null;
        this.garments = presetData.garments || [];
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        this.clothMeshes = {};
        this.garmentState = {};
        this.garmentOrigPositions = {};
        this.garmentRegionWeights = {};
        this.hairMesh = null;
        this.initialBodyTop = 0;
        this.selected = false;
        this.isSkinned = false;
        this.rigifySkeleton = null;
        this.generatedConfig = presetData.type === 'generated_model' ? presetData : null;
        this.mhProxies = {};
        this._pendingMHProxies = Array.isArray(presetData.mh_proxy) ? presetData.mh_proxy : [];
    }

    /**
     * Die Figur laden — erst der Körper, dann das Zubehör.
     *
     * DER KÖRPER WIRD GEMELDET, SOBALD ER STEHT (10.09.2026, Edgar: „Lade
     * asynchron, ich will ganz schnell das Modell sehen"). Vorher gab diese
     * Funktion erst zurück, wenn AUCH Stoff, Haare, Kleidung und Proxys
     * geladen waren — vier weitere Abrufe, jeder hinter dem vorigen. Und
     * erst danach setzte `charakterAusModelldaten` die Figur in die Szene.
     * Bis dahin sah der Nutzer eine leere Bühne, obwohl der Körper längst
     * fertig war.
     *
     * @param beiKoerper wird gerufen, sobald der Körper in der Gruppe hängt
     */
    async load(beiKoerper = null) {
        if (this.generatedConfig) {
            const fertig = await Charakterkoerper.ausKonfiguration(this);
            beiKoerper?.(this);
            return fertig;
        }

        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const data = await Startmessung.umAsync('    Körpernetz holen',
            () => Serverabruf.json(`/api/character/mesh/?${params}`));
        if (data.error) throw new Error(data.error);

        // Puffer, Normalen, Materialgruppen: siehe `Koerpernetz`. Diese dreißig
        // Zeilen standen fünfmal im Projekt (Befund `doppelcode`, 17.08.2026).
        Startmessung.um('    Körper aufbauen', () => {
            this.bodyMesh = Koerpernetz.netz(data, THREE);
            const materials = Array.isArray(this.bodyMesh.material)
                ? this.bodyMesh.material : [this.bodyMesh.material];
            Charakterkoerper.hautfarbe(this, materials);
            this.group.add(this.bodyMesh);
            this.initialBodyTop = _getBodyTop(this);
        });

        // HIER IST DIE FIGUR SICHTBAR. Alles Weitere kommt dazu, während sie
        // schon auf der Bühne steht.
        beiKoerper?.(this);

        // Das Zubehör braucht Skelett und Hautgewichte: `Charakterzubehoer`
        // ruft für Haare und Kleidung `convertInstToSkinned`, und das gibt
        // ohne `state.skinWeightData` STILL auf (`skeleton.js`). Die
        // Startsequenz legt das Versprechen ab, statt darauf zu warten,
        // bevor die Figur überhaupt beginnt — 2,4 MB Hautgewichte hielten
        // sonst den Körper auf, der sie gar nicht braucht.
        await Startmessung.umAsync('    auf Skelett und Gewichte warten',
                                   () => state.grunddatenBereit ?? Promise.resolve());
        await Startmessung.umAsync('    Stoff', () => Charakterzubehoer.stoff(this));
        await Startmessung.umAsync('    Haare', () => Charakterzubehoer.haare(this));
        await Startmessung.umAsync('    Kleidung', () => Charakterzubehoer.kleidung(this));
        await Startmessung.umAsync('    Proxys', () => Charakterzubehoer.proxys(this));

        return this;
    }








    dispose() {
        Netzentsorgung.netz(this.bodyMesh);
        // Ueber `Netzentsorgung`, nicht `mesh.material.dispose()`: Ein Netz
        // mit MEHREREN Materialien haette hier eine TypeError geworfen
        // (`material` ist dann ein Array). Bisher kam das nicht vor — der
        // naechste Stoff mit Materialgruppen haette es ausgeloest.
        for (const netz of Object.values(this.clothMeshes)) {
            Netzentsorgung.netz(netz);
        }
        Netzentsorgung.baum(this.hairMesh);
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    toJSON() {
        if (this.generatedConfig) {
            return {
                id: this.id,
                presetName: this.presetName,
                presetKey: this.presetKey || null,
                bodyType: 'generated',
                generatedConfig: this.generatedConfig,
                transform: this._lage(),
                // Auch eine ERZEUGTE Figur kann ein GarmentCode-Stueck
                // tragen. Dieser Zweig fuehrte es bis zum 09.09.2026 nicht
                // — wer eine generierte Figur in eine Szene speicherte,
                // fand sie beim Laden nackt wieder, ohne Fehler und ohne
                // Meldung. `Szenenausgabe.modelldaten` hat das Feld fuer
                // BEIDE Zweige, seit dem 08.09.2026 mit derselben
                // Begruendung — hier fehlte es noch.
                [GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(this),
            };
        }

        // Farbe, Material und Regionen leben im `garmentState`, nicht in
        // der Liste — `Garderobenstand` fuehrt beides zusammen. Bis zum
        // 09.09.2026 stand die Rechnung nur hier, waehrend „Modell
        // speichern" die rohe Liste nahm und jede Farbaenderung verlor.
        const garments = Garderobenstand.liste(this);
        return {
            id: this.id,
            presetName: this.presetName,
            presetKey: this.presetKey || null,
            bodyType: this.bodyType,
            morphs: this.morphs,
            meta: this.meta,
            cloth: this.cloth,
            hair_style: this.hairStyle,
            garments,
            mh_proxy: Object.values(this.mhProxies || {}),
            // GarmentCode fuehrt eine eigene Liste (08.09.2026): Die Stuecke
            // hingen nur als Netz in der Gruppe, und beim Speichern sah sie
            // niemand an — beim Laden stand die Figur nackt da.
            [GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(this),
            rigParams: this._rigParams || null,
            transform: this._lage(),
        };
    }

    /**
     * Lage der Figur in der Szene — Ort, Drehung, Groesse.
     *
     * BEFUND `doppelcode` (30.08.2026): Der Block stand in `toJSON` zweimal,
     * einmal fuer erzeugte Modelle und einmal fuer alles andere. Die Drehung
     * wird EINZELN ausgeschrieben, weil `Euler.toArray()` als viertes Feld die
     * Achsenreihenfolge mitgibt — die kaeme beim Zurueckladen als vierte Zahl
     * an und wuerde als Skalierungsanteil gelesen.
     *
     * Ohne den Absatz: `Posenabsatz.heben` stellt die Figur auf ihren
     * Schuh und merkt sich den Hub in `group.userData.absatzHub`. Der Hub
     * gehoert nicht in die gespeicherte Lage — nach dem Laden stellt das
     * Modul die Figur erneut auf den Absatz, und der gespeicherte Hub
     * kaeme dazu (gemessen 11.09.2026: 4,9 -> 9,8 -> 14,7 cm je Neuladen).
     */
    _lage() {
        const position = this.group.position.toArray();
        position[1] -= this.group.userData.absatzHub || 0;
        return {
            position,
            rotation: [this.group.rotation.x, this.group.rotation.y,
                       this.group.rotation.z],
            scale: this.group.scale.toArray(),
        };
    }

    /**
     * Eine gespeicherte Figur wieder aufbauen.
     *
     * @param beiKoerper wird gerufen, sobald der Körper steht UND seine Lage
     *        gesetzt ist — erst dann darf sie auf die Bühne, sonst steht sie
     *        für einen Augenblick im Ursprung statt an ihrem Platz.
     */
    static async fromJSON(data, beiKoerper = null) {
        let presetPayload;
        if (data.bodyType === 'generated' && data.generatedConfig) {
            presetPayload = {
                ...data.generatedConfig,
                name: data.presetName,
                type: 'generated_model',
            };
        } else {
            presetPayload = {
                name: data.presetName,
                body_type: data.bodyType,
                morphs: data.morphs || {},
                meta: data.meta || {},
                cloth: data.cloth || [],
                hair_style: data.hair_style || null,
                garments: data.garments || [],
                mh_proxy: data.mh_proxy || [],
            };
        }

        const inst = new CharacterInstance(data.id, presetPayload);
        if (data.presetKey) {
            inst.presetKey = data.presetKey;
            inst.presetName = data.presetKey;
        }
        await inst.load(() => {
            CharacterInstance._lage(inst, data.transform);
            beiKoerper?.(inst);
        });
        if (data.rigParams) inst._rigParams = data.rigParams;
        // NACH `load()` und nach der Lage: Gebunden wird in der Lage der
        // Figurgruppe (`GarmentcodeAnziehen`), und `load()` baut das
        // Skelett — ein Stueck, das vorher kommt, haengt starr da.
        await GarmentcodeAblage.laden(inst, data[GarmentcodeAblage.FELD]);
        return inst;
    }

    /** Die gespeicherte Lage auf die Figurgruppe setzen. */
    static _lage(inst, transform) {
        if (!transform) return;
        if (transform.position) inst.group.position.fromArray(transform.position);
        if (transform.rotation) {
            inst.group.rotation.set(transform.rotation[0], transform.rotation[1],
                                    transform.rotation[2]);
        }
        if (transform.scale) inst.group.scale.fromArray(transform.scale);
    }
}











// Register
fn.CharacterInstance = CharacterInstance;
fn.addCharacterFromPreset = addCharacterFromPreset;
// Der gemeinsame Weg „Modelldaten -> Figur in der Szene". Die Dialoge
// erreichen ihn ueber die Registrierung, weil `szene_dialoge.js` sonst
// `charakterliste.js` importieren muesste und damit das halbe Seitengeruest.
fn.charakterAusModelldaten = charakterAusModelldaten;
fn.loadDefaultCharacter = loadDefaultCharacter;
fn.selectCharacter = selectCharacter;
fn.deselectCharacter = deselectCharacter;
fn.deleteCharacter = deleteCharacter;
fn.focusCharacter = focusCharacter;
fn.updateCharacterListUI = updateCharacterListUI;
fn.updateVertexCount = updateVertexCount;
fn.clearAllCharacters = clearAllCharacters;
fn.setTransformMode = setTransformMode;
