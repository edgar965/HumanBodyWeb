import * as THREE from 'three';
import { Modell } from './modell.js';
import { Serverabruf } from './serverabruf.js';
import { Koerpernetz } from './koerpernetz.js';
import { Lippenbau } from './lippenbau.js';
import { Hautfarbe } from './hautfarbe.js';
import { Hautgewichte } from './hautgewichte.js';
import { Koerperdetails } from './koerperdetails.js';
import { Brauenhaut } from './brauenhaut.js';
import { Koerperfrage } from './koerperfrage.js';
import { Modellzubehoer } from './modellzubehoer.js';
import { Erzeugtesmodell } from './erzeugtesmodell.js';
import { Protokoll } from './protokoll.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';

/**
 * HumanbodyModell — die HumanBody-Figur: Netz vom Server nach Morphs und
 * Metawerten, Lippengruppe, Hautfarbe der Körperart, Skelett und Häutung,
 * Details (Iris, Wimpern, Nägel, Brauen), Haare, Kleidung, GarmentCode.
 *
 * DIE EINE BAUSTELLE (Edgar, 13.09.2026): Szene, BVH Studio, Theatre und
 * Ergebnisseite bauten diese Figur je selbst, und jede Fassung fehlte an
 * einer anderen Stelle — das Studio zeigte weder Lippen noch Brauen noch
 * die Nagelfarben, das Theatre lud keine GarmentCode-Stücke. `bauen()`
 * steht jetzt hier; die Seite gibt mit, was sie hat (Skelett, Gewichte,
 * Farbtabellen), und stellt die fertige `group` auf ihre Bühne.
 *
 * REIHENFOLGE, und warum sie zählt:
 *   1. Netz (`Koerpernetz`), dann die Lippen als Gruppe 11 (`Lippenbau`) —
 *      VOR allem, was sich den Index merkt (Hautmaske, Detailplan).
 *   2. Hautfarbe der Körperart (`Hautfarbe`), wenn die Seite die Tabelle hat.
 *   3. Häutung, wenn Skelett UND Gewichte da sind: `SkinnedMesh`, Wurzel-
 *      knochen als Kind, `bind`. Ohne beides bleibt ein `Mesh` — die Szene
 *      häutet erst bei Bedarf (`convertInstToSkinned`).
 *   4. Körper in die Gruppe, dann die Details: Farben auf die Gruppen,
 *      Längen auf die Punkte, die Brauen als Zeichnung im Hautshader
 *      (`Brauenhaut`, 16.09.2026 — vorher ein eigenes Netz, `Augenbrauenbau`).
 *   5. Zubehör (`Modellzubehoer`): Kleidung nebeneinander, GarmentCode,
 *      Haare, Hautmaske — nur mit `zubehoer: true`; die Szene hat dafür
 *      ihren eigenen Weg mit Regionen und Proxys (`Charakterzubehoer`).
 *
 * Erzeugte Modelle (Rig1–4, `type: 'generated_model'`) gehen über
 * `Erzeugtesmodell` und haben weder Details noch Zubehör.
 */
export class HumanbodyModell extends Modell {

    static QUELLE = 'modell';
    static ADRESSE = '/api/character/mesh/';
    static VORGABE_KOERPERART = 'Female_Caucasian';

    /**
     * @param id       Kennung der Figur
     * @param vorgabe  die Modellvorgabe (`/api/character/model/<name>/`)
     */
    constructor(id, vorgabe = {}) {
        super(id, HumanbodyModell.QUELLE);
        this.presetName = vorgabe.name || vorgabe.label || 'Unnamed';
        this.bodyType = vorgabe.body_type || HumanbodyModell.VORGABE_KOERPERART;
        this.morphs = Koerperfrage.morphs(vorgabe);
        this.meta = { ...(vorgabe.meta || {}) };
        this.cloth = vorgabe.cloth || [];
        this.hairStyle = vorgabe.hair_style || null;
        this.garments = vorgabe.garments || [];
        /** GarmentCode-Stücke `{stueck, rig_url, material}` (seit 08.09.2026). */
        this.garmentcode = Array.isArray(vorgabe.garmentcode) ? vorgabe.garmentcode : [];
        /** Iris, Wimpern, Nägel, Lippen, Brauen (Feld `details`, 12.09.2026). */
        this.details = Koerperdetails.aus(vorgabe);
        this.generatedConfig = vorgabe.type === 'generated_model' ? vorgabe : null;
        this._pendingMHProxies = Array.isArray(vorgabe.mh_proxy) ? vorgabe.mh_proxy : [];
        /** Die Hautfarbtabelle der Seite, sobald sie einmal angewendet wurde. */
        this.hautfarben = null;
    }

    /**
     * @param {Object} o
     * @param o.skelettdaten  Rigify-Skelett (JSON) — mit `gewichte` wird gehäutet
     * @param o.gewichte      Hautgewichte (JSON) der Körperart
     * @param o.hautfarben    {ethnie: [r,g,b]} — Hautfarbe der Körperart; null = Vorgabe
     * @param o.haarfarben    {name: [r,g,b]} für die Frisur
     * @param o.zubehoer      Haare, Kleidung, GarmentCode, Hautmaske mitbauen
     * @param o.beiKoerper    (modell) => void, sobald der Körper in der Gruppe hängt
     */
    async bauen({ skelettdaten = null, gewichte = null, hautfarben = null, haarfarben = null,
                  zubehoer = true, beiKoerper = null } = {}) {
        if (this.generatedConfig) {
            await this._erzeugt(skelettdaten, gewichte);
            beiKoerper?.(this);
            return this;
        }
        await this.koerper(skelettdaten, gewichte, hautfarben);
        beiKoerper?.(this);
        if (zubehoer) await new Modellzubehoer(this, haarfarben).laden();
        return this;
    }

    /** Die Frage an `/api/character/mesh/` und `/garment/fit/`: Körperart, Morphs, Meta. */
    frage() {
        return new Koerperfrage({ bodyType: this.bodyType, morphs: this.morphs, meta: this.meta })
            .felder();
    }

    // ------------------------------------------------------------------ Körper

    /** Schritte 1–4: Netz holen, Lippen, Hautfarbe, Häutung, Details. */
    async koerper(skelettdaten = null, gewichte = null, hautfarben = null) {
        const daten = await Serverabruf.json(`${HumanbodyModell.ADRESSE}?${this.frage()}`);
        if (daten.error) throw new Error(daten.error);
        const netz = Koerpernetz.netz(daten, THREE);
        Lippenbau.abspalten(netz, daten.lippen);
        this.hautfarbe(hautfarben, HumanbodyModell.materialien(netz));
        this.bodyMesh = (skelettdaten && gewichte)
            ? this._gehaeutet(netz, skelettdaten, gewichte) : netz;
        this.group.add(this.bodyMesh);
        this.detailsAnwenden();
        Protokoll.debug('HumanbodyModell', `${this.presetName}: ${netz.geometry.attributes.position.count} `
            + `Punkte, ${this.isSkinned ? 'gehäutet' : 'ungehäutet'}, Lippen ${daten.lippen?.length || 0}`);
        return this.bodyMesh;
    }

    /** Aus der Knochenvorschrift (Rig1–4). */
    async _erzeugt(skelettdaten, gewichte) {
        const ergebnis = await Erzeugtesmodell.bauen(this.generatedConfig, skelettdaten, gewichte);
        this.bodyMesh = ergebnis.mesh;
        if (ergebnis.skeleton) {
            this.skelett = ergebnis.skeleton;
            this.rigifySkeleton = ergebnis.skeleton;
            this.isSkinned = !!ergebnis.mesh.isSkinnedMesh;
        }
        this.group.add(this.bodyMesh);
    }

    /**
     * Den Körper NACHTRÄGLICH häuten — wenn Skelett und Gewichte erst nach
     * dem Netz da sind (Ergebnisseite, Theatre, Szene bei Bedarf). Die
     * Geometrie wird geklont: Die gezeichnete hält WebGL-Zustand ohne
     * Skinning, und der passt nach dem Binden nicht mehr. Das neue Netz
     * tritt an die Stelle des alten (Elternteil, Lage, Sichtbarkeit), die
     * Brauen werden gehäutet neu gebaut.
     * @returns das SkinnedMesh (oder der Körper, wenn nichts zu tun war)
     */
    haeuten(skelettdaten, gewichte) {
        const alt = this.bodyMesh;
        if (!alt || alt.isSkinnedMesh || !skelettdaten || !gewichte) return alt;
        const neu = this._gehaeutet(alt, skelettdaten, gewichte, true);
        neu.position.copy(alt.position);
        neu.rotation.copy(alt.rotation);
        neu.scale.copy(alt.scale);
        neu.visible = alt.visible;
        neu.name = alt.name;
        const eltern = alt.parent;
        if (eltern) {
            const stelle = eltern.children.indexOf(alt);
            eltern.remove(alt);
            eltern.add(neu);
            // An die alte Stelle — die erste Stelle der Gruppe ist der Körper.
            eltern.children.splice(eltern.children.indexOf(neu), 1);
            eltern.children.splice(stelle, 0, neu);
        }
        this.bodyMesh = neu;
        this.detailsAnwenden();
        return neu;
    }

    /** `SkinnedMesh` am Rigify-Skelett; die Gewichte kommen als Vierervektoren je Punkt. */
    _gehaeutet(netz, skelettdaten, gewichte, klonen = false) {
        const geo = klonen ? netz.geometry.clone() : netz.geometry;
        const { indices, gewichte: werte } = Hautgewichte.vierervektoren(
            gewichte, geo.attributes.position.count);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(indices, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(werte, 4));
        this.skelett = buildRigifySkeleton(skelettdaten, gewichte);
        this.rigifySkeleton = this.skelett;
        const gebunden = new THREE.SkinnedMesh(geo, netz.material);
        gebunden.castShadow = netz.castShadow;
        gebunden.receiveShadow = netz.receiveShadow;
        gebunden.add(this.skelett.rootBone);
        gebunden.bind(this.skelett.skeleton);
        this.isSkinned = true;
        return gebunden;
    }

    /** Hautfarbe der Körperart auf Haut und Censor-Gruppe; leer = Vorgabe des Netzes. */
    hautfarbe(tabelle, materialien = null) {
        if (!tabelle || !Object.keys(tabelle).length) return false;
        const m = materialien || HumanbodyModell.materialien(this.bodyMesh);
        if (!m[0]) return false;
        Hautfarbe.ausKoerperart(m[0], this.bodyType, tabelle, { zweites: m[1], mitErsatz: true });
        this.hautfarben = tabelle;
        return true;
    }

    /**
     * Farben, Längen und Brauen aus `details` — beim Bau, nach frischen
     * Morphpunkten (`neue`, vor dem Schreiben ins Attribut) und nach einem
     * Regler. Haut ohne eigene Farbe trägt wieder die der Körperart. Die
     * Braue kommt asynchron als Karte in den Hautshader (`Brauenhaut`).
     * @returns true, wenn Details angewendet wurden
     */
    detailsAnwenden(neue = null) {
        if (!this.bodyMesh || !this.details) return false;
        if (!this.details.haut && this.hautfarben) this.hautfarbe(this.hautfarben);
        Koerperdetails.anwenden(this.bodyMesh, this.details, neue);
        Brauenhaut.anwenden(this.bodyMesh, this.details, this.bodyType)
            .catch(f => console.warn('Brauenhaut:', f));
        return true;
    }

    static materialien(netz) {
        const m = netz?.material;
        return Array.isArray(m) ? m : (m ? [m] : []);
    }

    dispose() {
        super.dispose();
        this.bodyMesh = null;
        this.clothMeshes = {};
        this.hairMesh = null;
    }
}
