import * as THREE from 'three';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * SmplFigur — ein Referenzkörper von GarmentCode als Figur der Szene.
 *
 * WARUM (Edgar, 06.09.2026: „keine experimente, baue erstmal das Online tool
 * nach!"): Das Online-Tool drapiert auf `mean_all` mit dessen vorgegebenen
 * Maßen. Für diese Körper (mean_all, mean_female, mean_male, die zwei
 * SMPL-Durchschnitte) kennt GarmentCode Maße und Segmentierung — der
 * GarmentCode-Reiter läuft auf ihnen exakt wie das Tool. Das ist die
 * Messlatte für die HumanBody-Figur.
 *
 * Das Netz kommt vom Server in Metern mit Y oben — so rechnet GarmentCode,
 * und so rechnet Three.js; nichts wird gedreht. Kein Skelett, keine Morphs.
 *
 * Dieselben Felder wie `CharacterInstance` und `UmaFigur`, damit Liste,
 * Auswahl, Zählung und Speichern nicht je Quelle unterscheiden müssen.
 */
export class SmplFigur {

    static QUELLE = 'smpl';
    static ADRESSE = '/api/character/smpl-figur/';
    static FORMADRESSE = '/api/character/smpl-figur/formen/';

    /** Hautfarbe des Referenzkörpers — bewusst grau, kein Mensch. */
    static FARBE = 0x9a9a9a;

    constructor(id, daten) {
        this.id = id;
        this.quelle = SmplFigur.QUELLE;
        this.koerper = daten.koerper || 'mean_all';
        this.presetName = daten.presetName || `GarmentCode · ${this.koerper}`;
        this.presetKey = null;
        this.bodyType = 'GarmentCode';
        this.geschlecht = daten.geschlecht || null;
        this.masse = daten.masse || {};
        this.hoehe = 0;
        // Form der Figur: zwei Regler, -100..+100, 0 = Durchschnittskörper
        // des Tools. Das Online-Tool hat diese Regler nicht — gemessen
        // bleibt sein 3D-Körper bei jedem Maß derselbe (siehe smplform.py).
        this.form = {
            groesse: Number(daten.form?.groesse) || 0,
            fuelle: Number(daten.form?.fuelle) || 0,
        };
        this.betas = daten.betas || [];
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        // Felder der HumanBody-Figur, hier leer (siehe Kopf).
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

    async load() {
        const geformt = this.form.groesse || this.form.fuelle;
        const daten = geformt
            ? await Serverabruf.senden(SmplFigur.FORMADRESSE, {
                geschlecht: this.geschlecht || 'female',
                groesse: this.form.groesse, fuelle: this.form.fuelle,
            })
            : await Serverabruf.json(
                `${SmplFigur.ADRESSE}${encodeURIComponent(this.koerper)}/netz/`);
        if (daten.fehler) throw new Error(daten.fehler);
        if (daten.name) this.koerper = daten.name;
        this.betas = daten.betas || this.betas;
        const punkte = daten.punkte || [];
        const dreiecke = daten.dreiecke || [];
        if (!punkte.length || !dreiecke.length) {
            throw new Error(`Referenzkörper ${this.koerper} ohne Netz`);
        }
        this.bodyMesh = SmplFigur._netz(punkte, dreiecke);
        this.bodyMesh.name = `garmentcode_koerper_${this.koerper}`;
        this.group.add(this.bodyMesh);
        this.geschlecht = daten.geschlecht || this.geschlecht;
        this.masse = daten.masse || {};
        this.hoehe = daten.hoehe || 0;
        this.bodyType = `GarmentCode · ${this.koerper}`;
        Protokoll.debug('SmplFigur',
            `${this.koerper}: ${punkte.length} Punkte, ${dreiecke.length} Dreiecke, ${this.hoehe.toFixed(2)} m`);
        return this;
    }

    static _netz(punkte, dreiecke) {
        const lage = new Float32Array(punkte.length * 3);
        for (let i = 0; i < punkte.length; i++) {
            lage[i * 3] = punkte[i][0];
            lage[i * 3 + 1] = punkte[i][1];
            lage[i * 3 + 2] = punkte[i][2];
        }
        const index = new Uint32Array(dreiecke.length * 3);
        for (let i = 0; i < dreiecke.length; i++) {
            index[i * 3] = dreiecke[i][0];
            index[i * 3 + 1] = dreiecke[i][1];
            index[i * 3 + 2] = dreiecke[i][2];
        }
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geometrie.setIndex(new THREE.BufferAttribute(index, 1));
        geometrie.computeVertexNormals();
        return new THREE.Mesh(geometrie, new THREE.MeshStandardMaterial({
            color: SmplFigur.FARBE, roughness: 0.7, metalness: 0.0,
        }));
    }

    dispose() {
        Netzentsorgung.baum(this.group);
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    toJSON() {
        return {
            id: this.id,
            quelle: this.quelle,
            presetName: this.presetName,
            presetKey: null,
            bodyType: this.bodyType,
            koerper: this.koerper,
            geschlecht: this.geschlecht,
            form: { groesse: this.form.groesse, fuelle: this.form.fuelle },
            transform: {
                position: this.group.position.toArray(),
                rotation: [this.group.rotation.x, this.group.rotation.y, this.group.rotation.z],
                scale: this.group.scale.toArray(),
            },
        };
    }

    static async fromJSON(daten) {
        const figur = new SmplFigur(daten.id, daten);
        await figur.load();
        const lage = daten.transform;
        if (lage) {
            if (lage.position) figur.group.position.fromArray(lage.position);
            if (lage.rotation) figur.group.rotation.set(lage.rotation[0], lage.rotation[1], lage.rotation[2]);
            if (lage.scale) figur.group.scale.fromArray(lage.scale);
        }
        return figur;
    }
}
