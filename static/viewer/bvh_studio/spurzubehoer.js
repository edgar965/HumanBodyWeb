import * as THREE from 'three';
import { sharedState } from '../character_core.js';
import { base64ToFloat32 } from '../gemeinsam/kodierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';

/**
 * Spurzubehoer — Kleidung und Haare einer Modellvorgabe an die Figur einer
 * BVH-Spur hängen.
 *
 * Aus bvh_studio/spur_charakter.js herausgeloest (Umbau 16.08.2026):
 * `_loadPresetAccessories()` hatte 113 Zeilen für zwei Dinge — Kleidung vom
 * Server anpassen lassen und eine Frisur als GLTF laden. Beide endeten mit
 * demselben Muster: Skinning-Attribute setzen, `SkinnedMesh` binden, sonst ein
 * einfaches `Mesh`. Das steht jetzt einmal in `_anhaengen()`.
 */
export class Spurzubehoer {

    /** Vorgaben, wenn die Modellvorgabe nichts nennt. */
    static VORGABE_KOERPERART = 'Female_Caucasian';
    static VORGABE_FARBE = [0.5, 0.5, 0.5];
    static VORGABE_RAUHEIT = 0.7;
    static VORGABE_METALL = 0.0;
    /** Haar: Farbe, wenn die genannte fehlt, und Materialwerte. */
    static VORGABE_HAARFARBE = 'Silken Black';
    static ERSATZ_HAARFARBE = [0.02, 0.02, 0.02];
    static HAAR_RAUHEIT = 0.6;
    static HAAR_METALL = 0.1;
    /** An diesen Knochen wird die Frisur gehängt. */
    static KOPFKNOCHEN = 'spine_006';

    /** Anpassparameter der Kleidung: Feld in der Vorgabe → Name in der Frage. */
    static KLEIDERWERTE = [
        ['offset', 'offset', 0],
        ['stiffness', 'stiffness', 0.5],
        ['minDist', 'min_dist', 0],
        ['crotchFloor', 'crotch_floor', 0],
        ['lift', 'lift', 0],
        ['crotchDepth', 'crotch_depth', 0],
    ];

    constructor(spur, vorgabe) {
        this.spur = spur;
        this.vorgabe = vorgabe;
    }

    async laden() {
        for (const kleid of this.vorgabe.garments || []) {
            await this.kleidungsstueck(kleid);
        }
        await this.frisur();
        return this;
    }

    // ---------------------------------------------------------------- Kleidung

    async kleidungsstueck(kleid) {
        try {
            const daten = await Serverabruf.json(
                `/api/character/garment/fit/?${this._kleiderfrage(kleid)}`);
            if (daten.error) {
                Protokoll.warnung('BVH Studio', `Garment ${kleid.id} fehlgeschlagen:`,
                             daten.error);
                return;
            }
            const geo = Spurzubehoer.geometrie(daten);
            this._anhaengen(geo, this._kleiderstoff(kleid),
                            daten.skin_indices, daten.skin_weights);
            Protokoll.debug('BVH Studio', 'Garment geladen:', kleid.id);
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', `Garment ${kleid.id} Fehler:`, fehler);
        }
    }

    /** Anpassfrage: Kleidungswerte plus die Morphs der Figur. */
    _kleiderfrage(kleid) {
        const frage = new URLSearchParams({
            garment_id: kleid.id,
            body_type: this.spur.bodyType || Spurzubehoer.VORGABE_KOERPERART,
        });
        for (const [feld, name, ersatz] of Spurzubehoer.KLEIDERWERTE) {
            frage.set(name, kleid[feld] ?? ersatz);
        }
        // Das Stück muss auf DIESE Figur passen, nicht auf den Grundkörper.
        for (const [name, wert] of Object.entries(this.vorgabe.morphs || {})) {
            frage.append(`morph_${name}`, wert);
        }
        for (const [name, wert] of Object.entries(this.vorgabe.meta || {})) {
            frage.append(`meta_${name}`, wert);
        }
        return frage;
    }

    _kleiderstoff(kleid) {
        const farbe = kleid.color || Spurzubehoer.VORGABE_FARBE;
        return new THREE.MeshStandardMaterial({
            color: new THREE.Color(...farbe),
            roughness: kleid.roughness ?? Spurzubehoer.VORGABE_RAUHEIT,
            metalness: kleid.metalness ?? Spurzubehoer.VORGABE_METALL,
            side: THREE.DoubleSide,
        });
    }

    // ------------------------------------------------------------------- Haare

    async frisur() {
        const frisur = this.vorgabe.hair_style;
        if (!frisur?.url) return;
        try {
            const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
            const lader = new GLTFLoader();
            const gltf = await new Promise((fertig, fehler) =>
                lader.load(frisur.url, fertig, undefined, fehler));
            const gruppe = new THREE.Group();
            const stoff = this._haarstoff(frisur);
            gltf.scene.traverse(teil => {
                if (!teil.isMesh) return;
                gruppe.add(this._haarteil(teil.geometry.clone(), stoff));
            });
            this.spur.group.add(gruppe);
            Protokoll.debug('BVH Studio', 'Haar geladen:', frisur.name || frisur.url);
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'Haar nicht ladbar:', fehler);
        }
    }

    _haarstoff(frisur) {
        const name = frisur.color || Spurzubehoer.VORGABE_HAARFARBE;
        const farbe = sharedState.hairColorData?.[name]
                      || Spurzubehoer.ERSATZ_HAARFARBE;
        return new THREE.MeshStandardMaterial({
            color: new THREE.Color(...farbe),
            roughness: Spurzubehoer.HAAR_RAUHEIT,
            metalness: Spurzubehoer.HAAR_METALL,
            side: THREE.DoubleSide,
        });
    }

    /**
     * Haare hängen mit ALLEN Vertices am Kopfknochen — sie sollen sich mit dem
     * Kopf bewegen, ohne sich zu verformen.
     */
    _haarteil(geo, stoff) {
        const kopf = this._kopfknochenNummer();
        if (kopf < 0 || !this.spur.skeleton) return new THREE.Mesh(geo, stoff);
        const anzahl = geo.attributes.position.count;
        const indizes = new Float32Array(anzahl * 4);
        const gewichte = new Float32Array(anzahl * 4);
        for (let v = 0; v < anzahl; v++) {
            indizes[v * 4] = kopf;
            gewichte[v * 4] = 1.0;
        }
        return this._binden(geo, stoff, indizes, gewichte);
    }

    _kopfknochenNummer() {
        return this.spur.skeleton?.skeleton?.bones.findIndex(knochen =>
            knochen.name.includes(Spurzubehoer.KOPFKNOCHEN)) ?? -1;
    }

    // ------------------------------------------------------------- Gemeinsames

    /** Die Geometrie einer Spur — gebaut wie ueberall (28.08.2026). */
    static geometrie(daten) {
        return Koerpernetz.geometrie(daten, THREE);
    }

    /** Mit Gewichten als SkinnedMesh anhängen, ohne als einfaches Mesh. */
    _anhaengen(geo, stoff, indizesB64, gewichteB64) {
        if (!indizesB64 || !gewichteB64 || !this.spur.skeleton) {
            this.spur.group.add(new THREE.Mesh(geo, stoff));
            return;
        }
        this.spur.group.add(this._binden(geo, stoff,
                                        base64ToFloat32(indizesB64),
                                        base64ToFloat32(gewichteB64)));
    }

    /**
     * Netz an das Skelett der Spur binden. `bindMatrix` der Figur muss mit —
     * sonst sitzt das Teil im Ursprung statt an der Figur.
     */
    _binden(geo, stoff, indizes, gewichte) {
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(indizes, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewichte, 4));
        const netz = new THREE.SkinnedMesh(geo, stoff);
        netz.bind(this.spur.skeleton.skeleton, this.spur.mesh.bindMatrix);
        return netz;
    }
}
