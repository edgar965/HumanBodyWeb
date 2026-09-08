import * as THREE from 'three';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Knochenbau } from '../../gemeinsam/knochenbau.js';
import { Eigenhaut } from '../../gemeinsam/eigenhaut.js';
import { GarmentcodeAblage } from '../garmentcode_ablage.js';

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
        /** Das SMPL-Skelett (24 Gelenke) — dieselbe Form wie bei UMA,
         *  damit `Rigauswahl` es ohne Sonderfall findet. */
        this.skelett = null;
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
        // ERST das Skelett, DANN das Netz einhängen: Die Bindung braucht
        // die Knochen in ihrer Ruhelage (`Eigenhaut.einhaengen`).
        this._skelettBauen(daten.skelett);
        this._hautBinden(daten.hautgewichte);
        this.geschlecht = daten.geschlecht || this.geschlecht;
        this.masse = daten.masse || {};
        this.hoehe = daten.hoehe || 0;
        this.bodyType = `GarmentCode · ${this.koerper}`;
        Protokoll.debug('SmplFigur',
            `${this.koerper}: ${punkte.length} Punkte, ${dreiecke.length} Dreiecke, ${this.hoehe.toFixed(2)} m`);
        return this;
    }

    /**
     * Das SMPL-Skelett aus der Antwort bauen.
     *
     * `null` ist eine gueltige Antwort und keine Panne: GarmentCodes eigene
     * Koerper (`mean_all`, `mean_female`, `mean_male`) sind keine SMPL-Netze
     * und haben keines. Die Figur bekommt dann keine Knochen — der
     * Rig-Schalter laesst sie schlicht aus.
     *
     * Das alte Skelett wird ZUERST abgeraeumt: Die Formregler holen das Netz
     * bei jedem Zug neu, und ohne das haengen nach zehn Zuegen zehn Skelette
     * ineinander.
     */
    _skelettBauen(angaben) {
        this.skelett = Knochenbau.abraeumen(this.skelett);
        if (!angaben) return;
        this.skelett = Knochenbau.bauen(angaben, this.group);
    }

    /**
     * Das Netz an das eigene Skelett binden — sonst bleibt es beim Abspielen
     * starr, während die Knochen sich bewegen.
     *
     * Die Gewichte stammen aus dem SMPL-Modell selbst (`weights`, 6890 × 24);
     * für GarmentCodes eigene Körper (23.752 Punkte) sind sie über den
     * nächstgelegenen SMPL-Punkt übertragen. Ohne Skelett oder ohne Gewichte
     * hängt hier ein gewöhnliches `Mesh` — die Figur ist dann sichtbar, aber
     * nicht animierbar.
     */
    _hautBinden(haut) {
        if (this.skelett && haut) {
            this.bodyMesh = Eigenhaut.binden(this.bodyMesh, this.skelett, haut);
        }
        Eigenhaut.einhaengen(this.group, this.bodyMesh, this.skelett);
        this.isSkinned = !!this.bodyMesh.isSkinnedMesh;
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
            // GarmentCode-Stuecke ueberleben das Speichern (08.09.2026).
            [GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(this),
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
        await GarmentcodeAblage.laden(figur, daten[GarmentcodeAblage.FELD]);
        return figur;
    }
}
