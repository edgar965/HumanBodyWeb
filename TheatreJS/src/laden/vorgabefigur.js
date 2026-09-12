import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Koerperfrage } from './koerperfrage.js';
import { Kleidungsnetz } from './kleidungsnetz.js';
import { Garmentcodestueck }
    from '../../../static/viewer/gemeinsam/garmentcodestueck.js';
import { Figurlage } from './figurlage.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';
import { Koerperdetails } from '../../../static/viewer/gemeinsam/koerperdetails.js';

/**
 * Vorgabefigur — eine Figur samt Haaren und Kleidung aus einer Vorgabe laden.
 *
 * Aus asset-loader.js herausgeloest (Umbau 16.08.2026): `loadCharacterFromPreset`
 * hatte 105 Zeilen und tat fuenf Dinge — Sonderweg fuer erzeugte Modelle, Frage
 * aufbauen, Netz holen, Haare laden, Kleidung laden. Die Frage nach Morphs und
 * Meta-Werten (34 Zeilen) war dabei die dritte Kopie im Projekt; sie steckt
 * jetzt in Koerperfrage.
 */
export class Vorgabefigur {

    static HAAR_ZU_HELL = 0.9;
    /** Ersatzfarbe fuer Haare, die als reines Weiss aus der GLB kommen. */
    static HAARFARBE = [0.1, 0.08, 0.06];
    static MESH_ENDPUNKT = '/api/character/mesh/';

    /**
     * @param {Object} werkzeuge  { netzBauen, erzeugtesModell, inTheatre }
     *        — die drei Dinge, die aus asset-loader.js gebraucht werden.
     */
    constructor(werkzeuge) {
        this.werkzeuge = werkzeuge;
        this.lader = new GLTFLoader();
    }

    /**
     * Figur laden und in die Szene setzen.
     * @param {import('three').Scene} scene
     * @param {Object} vorgabe
     * @param {string} name  Anzeigename fuer Theatre
     * @param {Object} lage  {x, angleichen, vorbildHoehe} aus dem Figurwahl-
     *        Dialog, oder null — dann bleibt die Figur im Ursprung
     */
    async laden(scene, vorgabe, name, lage = null) {
        const gruppe = vorgabe.type === 'generated_model'
            ? await this.werkzeuge.erzeugtesModell(vorgabe)
            : this.werkzeuge.netzBauen(await this._netzdaten(vorgabe));
        scene.add(gruppe);
        this._kennzeichnen(gruppe, vorgabe, name);

        if (vorgabe.type !== 'generated_model') {
            // Iris, Wimpern, Nägel wie in der Szene gespeichert (Feld `details`).
            Koerperdetails.anwenden(gruppe.children[0], Koerperdetails.aus(vorgabe));
            await this._haare(gruppe, vorgabe);
            await this._kleidung(gruppe, vorgabe);
            await this._garmentcode(gruppe, vorgabe);
        }
        // Lage VOR der Anmeldung: Theatre.js nimmt die Position als Startwert.
        Figurlage.anwenden(gruppe, lage);
        // Das Theatre-Objekt bleibt an der Gruppe (Schlüssel in
        // `userData.theatreSchluessel`): Wer die Figur entfernt, meldet es
        // darüber ab (`studio/figurentfernen.js`).
        gruppe.userData.theatreObjekt = this.werkzeuge.inTheatre(gruppe, name);
        return gruppe;
    }

    async _netzdaten(vorgabe) {
        const antwort = await fetch(
            Vorgabefigur.MESH_ENDPUNKT + '?' + Koerperfrage.text(vorgabe));
        if (!antwort.ok) throw new Error('Netz-API: ' + antwort.status);
        return antwort.json();
    }

    /** Werte, die spaeter fuers Nachladen und die Panels gebraucht werden. */
    _kennzeichnen(gruppe, vorgabe, name) {
        gruppe.userData.presetName = name;
        gruppe.userData.bodyType = vorgabe.type === 'generated_model'
            ? 'generated' : (vorgabe.body_type || Koerperfrage.VORGABE_KOERPER);
        if (vorgabe.type === 'generated_model') return;
        gruppe.userData.morphs = Koerperfrage.morphs(vorgabe);
        gruppe.userData.meta = { ...(vorgabe.meta || {}) };
    }

    async _haare(gruppe, vorgabe) {
        const haare = vorgabe.hair_style;
        if (!haare?.url) return;
        try {
            const geladen = await this.haareLaden(haare.url);
            geladen.userData.isHair = true;
            geladen.traverse(kind => {
                if (kind.isMesh) kind.userData.isHair = true;
            });
            gruppe.add(geladen);
            Protokoll.debug('vorgabefigur', '✓ Haare geladen:', haare.name);
        } catch (fehler) {
            console.error('Haare nicht ladbar:', fehler);
        }
    }

    async _kleidung(gruppe, vorgabe) {
        if (!Array.isArray(vorgabe.garments)) return;
        for (const kleid of vorgabe.garments) {
            try {
                const netz = await Kleidungsnetz.laden(
                    kleid, vorgabe.body_type, vorgabe);
                netz.userData.isGarment = true;
                gruppe.add(netz);
                Protokoll.debug('vorgabefigur', '✓ Kleidung geladen:', kleid.id);
            } catch (fehler) {
                console.error('Kleidung nicht ladbar:', kleid.id, fehler);
            }
        }
    }

    /**
     * Die GarmentCode-Stücke der Vorgabe (Feld `garmentcode`, seit 08.09.2026).
     *
     * Edgar, 11.09.2026: „laden des Female1 Modells lädt nicht die Kleider
     * (GarmentCode) des Modells" — die Liste wurde hier schlicht nicht
     * gelesen. Nacheinander, nicht parallel, damit die Reihenfolge der
     * Stücke der der Datei entspricht; ein fehlendes Stück hält die
     * anderen nicht auf.
     */
    async _garmentcode(gruppe, vorgabe) {
        if (!Array.isArray(vorgabe.garmentcode)) return;
        for (const eintrag of vorgabe.garmentcode) {
            if (!eintrag?.stueck || !eintrag?.rig_url) continue;
            try {
                gruppe.add(await Garmentcodestueck.laden(eintrag));
                Protokoll.debug('vorgabefigur', '✓ GarmentCode geladen:', eintrag.stueck);
            } catch (fehler) {
                Protokoll.warnung('vorgabefigur',
                    `GarmentCode „${eintrag.stueck}" nicht ladbar: ${fehler.message || fehler}`);
            }
        }
    }

    /**
     * Haare als GLB laden. Manche Dateien bringen reinweisses Material mit —
     * dann waeren die Haare in der Szene ein weisser Klumpen. Solche Faelle
     * bekommen eine dunkle Ersatzfarbe.
     */
    haareLaden(url) {
        return new Promise((fertig, fehlgeschlagen) => {
            this.lader.load(url, (gltf) => {
                gltf.scene.traverse(kind => {
                    if (!kind.isMesh) return;
                    kind.castShadow = true;
                    kind.receiveShadow = true;
                    this._haarmaterial(kind.material);
                });
                fertig(gltf.scene);
            }, undefined, fehlgeschlagen);
        });
    }

    _haarmaterial(stoff) {
        if (!stoff) return;
        const farbe = stoff.color;
        const grenze = Vorgabefigur.HAAR_ZU_HELL;
        if (farbe && farbe.r > grenze && farbe.g > grenze && farbe.b > grenze) {
            farbe.setRGB(...Vorgabefigur.HAARFARBE);
        }
        if (stoff.roughness === undefined) stoff.roughness = 0.8;
        if (stoff.metalness === undefined) stoff.metalness = 0.0;
    }
}
