import * as THREE from 'three';
import { state, API, MODEL_OFFSET_X } from './state.js';
import { alignBodyToSMPLX, BODY_MATERIALS } from './helpers.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzpunkte } from '../gemeinsam/netzpunkte.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';

/**
 * Fotokoerpernetz — das HumanBody-Netz der Foto-Seite holen und in die Szene
 * setzen, mit Skelett wenn Gewichte vorliegen.
 *
 * Aus photo_to_3d/humanbody_mesh.js herausgeloest (Umbau 16.08.2026):
 * `loadMesh()` hatte 119 Zeilen — Adresse bauen, altes Netz entsorgen,
 * Geometrie, Materialien, Gewichte, Skelett anhängen, Einsetzen. Jetzt je eine
 * Methode.
 *
 * Die Rechnung der Skinning-Gewichte ist bewusst UNVERÄNDERT übernommen: Im
 * Projekt gibt es drei Fassungen davon, die sich in Sortierung und Normierung
 * unterscheiden (hier ohne, in animation/netz.js mit). Sie zu vereinheitlichen
 * wäre eine Verhaltensänderung, und Skinning-Fehler zeigen sich erst bei
 * Einzelknochen-Drehungen — nicht in der Ruhelage.
 */
export class Fotokoerpernetz {

    /** Werte unter dieser Schwelle gehen nicht in die Adresse. */
    static SCHWELLE = 0.001;
    /** So viele Knochen wirken höchstens auf einen Vertex. */
    static EINFLUESSE = 4;
    /** Kopfknochen, dessen Lage nach dem Binden zurückgesetzt wird. */
    static KOPFKNOCHEN = 'DEF-spine.006';

    constructor(koerperart) {
        this.koerperart = koerperart || state.currentBodyType;
    }

    /**
     * Netz holen. Passt es in das vorhandene, werden nur die Punkte ersetzt.
     *
     * Performance-Durchgang 16.08.2026: Jede Reglerbewegung baute hier ein
     * VOLLSTAENDIG neues Netz — 5,24 MB Abruf, neue Geometrie, neues
     * Skelett-Binding. Beim Ziehen eines Reglers aendern sich aber nur die
     * Punktlagen. Der Schnellweg holt 2,26 MB und laesst Geometrie und Binding
     * stehen; die Szene machte das schon so (`Charakterkoerper.neuLaden`).
     */
    async laden() {
        try {
            if (await this._nurPunkte()) return state.bodyMesh;
            const daten = await Serverabruf.json(this.adresse());
            if (daten.error) {
                console.error(daten.error);
                return null;
            }
            this._altesEntsorgen();
            const geo = this._geometrie(daten);
            const material = this._materialien(daten, geo);
            state.bodyMesh = this._netz(geo, material);
            this._einsetzen(geo);
            return state.bodyMesh;
        } catch (fehler) {
            console.error('Netz nicht ladbar:', fehler);
            return null;
        }
    }

    /**
     * Schnellweg: Nur die Punkte holen und ins bestehende Netz schreiben.
     *
     * Nur wenn schon ein Netz derselben Koerperart steht. Passt die Punktzahl
     * nicht (anderes Geschlecht), liefert `Netzpunkte.aktualisieren` false und
     * der vollstaendige Weg laeuft.
     */
    async _nurPunkte() {
        if (!state.bodyMesh || state.currentBodyType !== this.koerperart) {
            return false;
        }
        const daten = await Serverabruf.jsonOderNull(
            this.adresse() + '&nur_punkte=1');
        // `alignBodyToSMPLX` MUSS mit: `_geometrie()` verschiebt den Koerper
        // beim vollstaendigen Aufbau ebenso. Ohne diesen Schritt springt das
        // Netz beim ersten Regler neben das SMPL-X-Modell.
        return !!daten && Netzpunkte.aktualisieren(state.bodyMesh, daten,
                                                  alignBodyToSMPLX);
    }

    /** Adresse mit allen von 0 abweichenden Morph- und Metawerten. */
    adresse() {
        const frage = new URLSearchParams({ body_type: this.koerperart });
        for (const [name, wert] of Object.entries(state.morphValues)) {
            if (Math.abs(wert) > Fotokoerpernetz.SCHWELLE) frage.set(`morph_${name}`, wert);
        }
        for (const [name, wert] of Object.entries(state.metaValues)) {
            if (Math.abs(wert) > Fotokoerpernetz.SCHWELLE) frage.set(`meta_${name}`, wert);
        }
        return `${API}/mesh/?${frage}`;
    }

    /**
     * Altes Netz aus der Szene nehmen. Das Skelett hängt am Netz und muss
     * vorher abgehängt werden, sonst verschwindet es mit.
     */
    _altesEntsorgen() {
        const netz = state.bodyMesh;
        if (!netz) return;
        if (netz.isSkinnedMesh && state.rigifySkeleton?.rootBone) {
            netz.remove(state.rigifySkeleton.rootBone);
        }
        state.scene.remove(netz);
        netz.geometry?.dispose();
        state.bodyMesh = null;
        state.bodyGeometry = null;
    }

    // -------------------------------------------------------------- Geometrie

    /**
     * Die Geometrie — gebaut wie ueberall (28.08.2026, Befund `doppelcode`),
     * nur mit einem Schritt mehr: Die Punkte werden nach der Achsdrehung auf
     * SMPL-X ausgerichtet, damit Koerper und SMPL-X-Netz uebereinanderliegen.
     */
    _geometrie(daten) {
        return Koerpernetz.geometrie(daten, THREE, alignBodyToSMPLX);
    }

    /**
     * Materialien nach Körperteil. Nur mit Flächengruppen kann Three.js mehrere
     * Materialien zuordnen — sonst gilt das erste für alles.
     */
    _materialien(daten, geo) {
        const materialien = BODY_MATERIALS.map(angabe =>
            new THREE.MeshStandardMaterial({
                color: angabe.color, roughness: angabe.roughness,
                metalness: angabe.metalness, side: THREE.DoubleSide,
                transparent: angabe.transparent || false,
                opacity: angabe.opacity !== undefined ? angabe.opacity : 1.0,
            }));
        const gruppen = daten.groups || [];
        if (!geo.index || !gruppen.length) return materialien[0];
        for (const gruppe of gruppen) {
            geo.addGroup(gruppe.start, gruppe.count, gruppe.materialIndex);
        }
        return materialien;
    }

    // ---------------------------------------------------------------- Skinning

    _netz(geo, material) {
        if (!state.rigifySkeleton || !state.skinWeightData?.weights) {
            return new THREE.Mesh(geo, material);
        }
        this._gewichteSetzen(geo);
        const netz = new THREE.SkinnedMesh(geo, material);
        netz.add(state.rigifySkeleton.rootBone);
        this._kopfLageZuruecksetzen();
        netz.bind(new THREE.Skeleton(state.rigifySkeleton.bones));
        return netz;
    }

    /**
     * skinIndex/skinWeight aus den Servergewichten. Die Gewichte nennen ihre
     * Knochen über die Namensliste, Three.js über den Index in der
     * Knochenliste — dazwischen liegt die Zuordnung `nachIndex`.
     */
    _gewichteSetzen(geo) {
        const anzahl = geo.attributes.position.count;
        const indizes = new Uint16Array(anzahl * Fotokoerpernetz.EINFLUESSE);
        const gewichte = new Float32Array(anzahl * Fotokoerpernetz.EINFLUESSE);
        const nachIndex = this._knochenzuordnung();

        const daten = state.skinWeightData.weights;
        for (let v = 0; v < Math.min(anzahl, daten.length); v++) {
            const paare = daten[v];
            for (let j = 0; j < Math.min(paare.length, Fotokoerpernetz.EINFLUESSE); j++) {
                const knochen = nachIndex[paare[j][0]];
                const platz = v * Fotokoerpernetz.EINFLUESSE + j;
                indizes[platz] = knochen !== undefined ? knochen : 0;
                gewichte[platz] = knochen !== undefined ? paare[j][1] : 0;
            }
        }
        geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(indizes, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewichte, 4));
    }

    _knochenzuordnung() {
        const zuordnung = {};
        const namen = state.skinWeightData.bone_names;
        for (let i = 0; i < namen.length; i++) {
            const index = state.rigifySkeleton.bones.indexOf(
                state.rigifySkeleton.boneByName[namen[i]]);
            if (index >= 0) zuordnung[i] = index;
        }
        return zuordnung;
    }

    /**
     * Der Kopfknochen wird beim Anpassen des Gesichts verschoben. Beim neuen
     * Binden muss er auf seiner Ruhelage stehen, sonst wandert der Kopf mit
     * jedem Netzwechsel weiter.
     */
    _kopfLageZuruecksetzen() {
        const kopf = state.rigifySkeleton.boneByName[Fotokoerpernetz.KOPFKNOCHEN];
        if (!kopf) return;
        if (kopf._origY === undefined) kopf._origY = kopf.position.y;
        if (kopf._origZ === undefined) kopf._origZ = kopf.position.z;
        kopf.position.y = kopf._origY;
        kopf.position.z = kopf._origZ;
        state.rigifySkeleton.rootBone.updateWorldMatrix(true, true);
    }

    _einsetzen(geo) {
        // Die Foto-Seite zeigt zwei Modelle nebeneinander; das HumanBody-Netz
        // steht links.
        state.bodyMesh.position.x = MODEL_OFFSET_X;
        state.bodyGeometry = geo;
        state.scene.add(state.bodyMesh);
        const anzeige = document.getElementById('vertex-count');
        if (anzeige) {
            anzeige.textContent = geo.attributes.position.count.toLocaleString();
        }
    }
}
