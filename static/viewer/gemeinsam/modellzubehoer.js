import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { base64ToFloat32 } from './kodierung.js';
import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Netzgeometrie } from './netzgeometrie.js';
import { Kleiderfrage } from './kleiderfrage.js';
import { Kleiderwerkstoff } from './kleiderwerkstoff.js';
import { Garmentcodestueck } from './garmentcodestueck.js';
import { Garmentcodebindung } from './garmentcodebindung.js';
import { Figurhaut } from './figurhaut.js';

/**
 * Modellzubehoer — Haare, Kleidung und GarmentCode-Stücke eines
 * `HumanbodyModell`, dazu die Hautmaske.
 *
 * WARUM HIER (13.09.2026): Das stand dreimal — `studio/spurzubehoer.js`,
 * `TheatreJS/src/laden/vorgabefigur.js` (+ `kleidungsnetz.js`) und
 * `result_character/{hair,cloth_garments,garmentcode_stuecke}.js` — und jede
 * Fassung vergaß etwas anderes (das Theatre die GarmentCode-Stücke, das
 * Studio die Hautmaske, bis sie je einzeln nachgetragen wurden). Die Szene
 * hat ihren eigenen Weg (`scene/charakter_zubehoer.js`): Sie häutet erst
 * bei Bedarf und verschiebt Kleidung nach Regionen; das bleibt dort.
 *
 * DIE FIGUR IST GEHÄUTET ODER NICHT: Mit Skelett werden Stücke mit den
 * Gewichten des Servers gebunden und die Haare mit ALLEN Ecken an den
 * Kopfknochen gehängt (sie sollen mitgehen, ohne sich zu verformen); ohne
 * Skelett kommt ein Stück als `SkinnedMesh` mit `userData.needsBinding`
 * (der Skinner des Theatre bindet es später), GarmentCode bleibt starr mit
 * seiner Rig-Datei, Haare sind ein `Mesh`.
 *
 * Ein Stück trägt `userData.isGarment` — daran sammelt `Figurhaut` die
 * Stoffe für die Hautmaske; Haare tragen `isHair`.
 */
export class Modellzubehoer {

    static VORGABE_HAARFARBE = 'Silken Black';
    static ERSATZ_HAARFARBE = [0.02, 0.02, 0.02];
    static HAAR_RAUHEIT = 0.6;
    static HAAR_METALL = 0.1;
    /** An diesen Knochen werden die Haare gehängt. */
    static KOPFKNOCHEN = 'spine_006';

    static _lader = null;
    /** @type {Promise<Object>|null} Farbtabelle, wenn die Seite keine mitgibt. */
    static _haarfarben = null;

    /**
     * @param {Object} modell  das `HumanbodyModell` (group, bodyMesh, skelett, …)
     * @param {Object<string, number[]>|null} [haarfarben]  Name → [r,g,b] aus `/api/character/hairstyles/`
     */
    constructor(modell, haarfarben = null) {
        this.modell = modell;
        this.haarfarben = haarfarben || {};
    }

    /** Alles: Kleidung nebeneinander, GarmentCode, Haare, dann die Hautmaske. */
    async laden() {
        await Promise.all((this.modell.garments || []).map(k => this.kleidungsstueck(k)));
        await this.garmentcode();
        await this.haare();
        Figurhaut.anwenden({ mesh: this.modell.bodyMesh, group: this.modell.group,
                             name: this.modell.presetName });
        return this;
    }

    // ---------------------------------------------------------------- Kleidung

    async kleidungsstueck(kleid) {
        try {
            const frage = Kleiderfrage.fuer(this.modell.frage(), kleid, THREE.Color);
            const daten = await Serverabruf.json(`/api/character/garment/fit/?${frage}`);
            if (daten.error) throw new Error(daten.error);
            const geo = Netzgeometrie.bauen({ vertices: daten.vertices, faces: daten.faces }, THREE);
            const stoff = Kleiderwerkstoff.bauen(THREE, Kleiderfrage.kanaele(kleid.color, THREE.Color),
                                                 kleid.roughness, kleid.metalness);
            const netz = this._gebunden(geo, stoff, daten.skin_indices, daten.skin_weights);
            netz.name = kleid.id;
            netz.userData.isGarment = true;
            netz.userData.garmentId = kleid.id;
            this.modell.clothMeshes[`gar_${kleid.id}`] = netz;
            this.modell.group.add(netz);
            Protokoll.debug('Modellzubehoer', 'Kleidung geladen:', kleid.id);
        } catch (fehler) {
            Protokoll.warnung('Modellzubehoer', `Kleidung „${kleid.id}":`, fehler.message || fehler);
        }
    }

    // ------------------------------------------------------------- GarmentCode

    /** Gespeicherte GarmentCode-Stücke holen und ans Skelett binden. */
    async garmentcode() {
        const eintraege = this.modell.garmentcode || [];
        for (const eintrag of eintraege) {
            if (!eintrag?.stueck || !eintrag?.rig_url) continue;
            try {
                this.modell.group.add(await Garmentcodestueck.laden(eintrag));
            } catch (fehler) {
                Protokoll.warnung('Modellzubehoer', `GarmentCode „${eintrag.stueck}":`,
                                  fehler.message || fehler);
            }
        }
        if (!eintraege.length || !this.modell.skelett || !this.modell.bodyMesh) return;
        const gebunden = new Garmentcodebindung(this.modell.skelett)
            .binden(this.modell.group, this.modell.bodyMesh);
        Protokoll.debug('Modellzubehoer', `GarmentCode: ${gebunden}/${eintraege.length} gebunden`);
    }

    // ------------------------------------------------------------------- Haare

    async haare() {
        const frisur = this.modell.hairStyle;
        if (!frisur?.url) return;
        try {
            if (!Object.keys(this.haarfarben).length) this.haarfarben = await Modellzubehoer.haarfarben();
            Modellzubehoer._lader = Modellzubehoer._lader || new GLTFLoader();
            const gltf = await Modellzubehoer._lader.loadAsync(frisur.url);
            const gruppe = new THREE.Group();
            gruppe.userData.isHair = true;
            const stoff = this._haarstoff(frisur);
            gltf.scene.traverse(teil => {
                if (!teil.isMesh) return;
                const haar = this._haarteil(teil.geometry.clone(), stoff);
                haar.userData.isHair = true;
                gruppe.add(haar);
            });
            this.modell.hairMesh = gruppe;
            this.modell.group.add(gruppe);
            Protokoll.debug('Modellzubehoer', 'Haare geladen:', frisur.name || frisur.url);
        } catch (fehler) {
            Protokoll.warnung('Modellzubehoer', 'Haare nicht ladbar:', fehler.message || fehler);
        }
    }

    _haarstoff(frisur) {
        const name = frisur.color || Modellzubehoer.VORGABE_HAARFARBE;
        const farbe = this.haarfarben[name] || Modellzubehoer.ERSATZ_HAARFARBE;
        return new THREE.MeshStandardMaterial({
            color: new THREE.Color(...farbe), roughness: Modellzubehoer.HAAR_RAUHEIT,
            metalness: Modellzubehoer.HAAR_METALL, side: THREE.DoubleSide });
    }

    /** Haare hängen mit ALLEN Ecken am Kopfknochen. */
    _haarteil(geo, stoff) {
        const kopf = this._kopfknochen();
        if (kopf < 0) return new THREE.Mesh(geo, stoff);
        const anzahl = geo.attributes.position.count;
        const indizes = new Float32Array(anzahl * 4);
        const gewichte = new Float32Array(anzahl * 4);
        for (let v = 0; v < anzahl; v++) {
            indizes[v * 4] = kopf;
            gewichte[v * 4] = 1.0;
        }
        return this._binden(geo, stoff, indizes, gewichte);
    }

    _kopfknochen() {
        const knochen = this.modell.skelett?.skeleton?.bones || [];
        return knochen.findIndex(k => k.name.includes(Modellzubehoer.KOPFKNOCHEN));
    }

    // ------------------------------------------------------------- Gemeinsames

    /**
     * Mit Gewichten ein SkinnedMesh: am Skelett des Modells gebunden, oder —
     * ohne Skelett — mit `needsBinding`, damit der Skinner der Seite es
     * später bindet (Theatre). Ohne Gewichte ein starres Mesh.
     */
    _gebunden(geo, stoff, indizesB64, gewichteB64) {
        if (!indizesB64 || !gewichteB64) return new THREE.Mesh(geo, stoff);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(base64ToFloat32(indizesB64), 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(base64ToFloat32(gewichteB64), 4));
        const netz = new THREE.SkinnedMesh(geo, stoff);
        if (this.modell.skelett?.skeleton) netz.bind(this.modell.skelett.skeleton, this.modell.bodyMesh.bindMatrix);
        else netz.userData.needsBinding = true;
        return netz;
    }

    /** Ans Skelett des Modells binden — mit dessen `bindMatrix`, sonst sitzt das Teil im Ursprung. */
    _binden(geo, stoff, indizes, gewichte) {
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(indizes, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewichte, 4));
        const netz = new THREE.SkinnedMesh(geo, stoff);
        netz.bind(this.modell.skelett.skeleton, this.modell.bodyMesh.bindMatrix);
        return netz;
    }

    /** Die Haarfarben des Servers — einmal geholt, dann gemerkt; ohne Antwort leer. */
    static async haarfarben() {
        if (!Modellzubehoer._haarfarben) {
            Modellzubehoer._haarfarben = Serverabruf.json('/api/character/hairstyles/')
                .then(d => d?.colors || {})
                .catch(() => { Modellzubehoer._haarfarben = null; return {}; });
        }
        return Modellzubehoer._haarfarben;
    }
}
