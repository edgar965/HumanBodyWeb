import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Meshfighaut } from './meshfighaut.js';

/**
 * Meshfigurhaarobjekt — ein Haar als eigenes Objekt auf der Figur der Bühne: das Haar aus dem Netz
 * (`ergebnis/haar.glb`, 27.09.2026) oder die Haarkarten aus seiner Schale (`ergebnis/haarkarten.glb`,
 * Schritt „frisur", 29.09.2026). Beide liegen schon in der Ruhelage der Figur — sie hängen ohne eigene Lage
 * in deren Gruppe und wandern mit, wenn die Figur neu gebaut wird (`anhaengen`).
 *
 * `art`: `{name, datei: ergebnis => {datei, bytes, fehler}, karten}`. Karten tragen ein Deckkraftbild
 * (glTF `MASK`): `alphaToCoverage` statt harter Kante — genesis9-inhalte.md, Kin: „alphaTest 0.3 machte
 * krebskranke Haare".
 *
 * SICHTBAR JE NETZ, NICHT JE GRUPPE: Der Export (`Modellexportinhalt.objekte`) fragt `mesh.visible`; eine
 * ausgeblendete Gruppe mit sichtbaren Netzen darin ging mit in die GLB (bis 29.09.2026 beim Schalter „Haar").
 *
 * ANIMIERT (13.10.2026): Trägt der Steckbrief eine Hautdatei (`objekt.haut`), wird das Netz an das Skelett der Figur gebunden (`Meshfighaut`) — dann nimmt die Animation es mit. In der Haltung des Netzes
 * (`haltung`) bleibt es starr: die Figur ist dort fest gebacken, und die Animation schaltet die Haltung ohnehin aus.
 */
export class Meshfigurhaarobjekt {

    constructor(seite, melden, art) {
        this.seite = seite;
        this.melden = melden;
        this.art = art;
        this.objekt = null;
        this.gruppe = null;
        this.an = false;
        this.vorhanden = false;
        this._stand = null;
        this._haltung = false;
        this.skelett = null;        // das Skelett der gezeigten Figur (`anhaengen`)
        this.haut = null;           // die geladene Hautdatei zu `objekt` (`Meshfighaut.laden` + Namensliste)
        this._lauf = 0;             // zählt die Ladevorgänge: eine überholte Hautdatei wird verworfen
        this._gelenkAdresse = null; // wo die Gelenkkorrekturen dieses Objekts liegen (`gelenkadresse`)
    }

    /**
     * Laden, wenn sich die Datei geändert hat; `gruppe` = die Gruppe der Figur (oder null).
     * `haltung`: die Figur steht in der Haltung des Netzes (`Meshfighaltung`) — dann gilt die Fassung des Objekts in dieser Haltung (`objekt.haltung`, unverändert aus dem Netz, im Raum der gebackenen Figur).
     * Hat es keine, ist es dort nicht zu sehen: die Fassung in Ruhe läge neben der Figur.
     */
    zeigen(z, gruppe, haltung = false) {
        const gesamt = this.art.datei(z.ergebnis || {}) || {};
        const o = haltung ? (gesamt.haltung || {}) : gesamt;
        const wechsel = haltung !== this._haltung;
        this._haltung = haltung;
        this.vorhanden = Boolean(o.datei);
        if (gesamt.fehler) this.melden(`${this.art.name}: ${gesamt.fehler}`);
        if (!o.datei) {
            if (wechsel && this.objekt) {
                this.objekt.parent?.remove(this.objekt);
                this.objekt = null;
                this._stand = null;
            }
            return;
        }
        const stand = JSON.stringify([o.datei, o.bytes, o.flaechen, o.punkte, (o.haut || {}).bytes]);
        if (stand !== this._stand) {
            this._stand = stand;
            this._gelenkAdresse = Meshfigurhaarobjekt.gelenkadresse(this.seite.dateiAdresse('ergebnis', o.datei), o.haut, encodeURIComponent(stand));
            this._laden(`${this.seite.dateiAdresse('ergebnis', o.datei)}?t=${encodeURIComponent(stand)}`, o.haut || null, encodeURIComponent(stand));
        }
        if (gruppe) this.anhaengen(gruppe);
    }

    /** Adresse der Gelenkfelder (JCM) zu einer Objektdatei — nur für Objekte mit Hautdatei, sonst null (Mesh-3D, `Meshfigurobjektfelder`; andere Seiten haben die Adresse nicht, dann gibt es keine Felder). */
    static gelenkadresse(dateiAdresse, haut, marke) {
        return haut && dateiAdresse.includes('/datei/ergebnis/') ? `${dateiAdresse.replace('/datei/ergebnis/', '/objektfelder/')}?t=${marke}` : null;
    }

    /** Für die Gelenkkorrekturen (`Meshfigurgelenke`): das an die Knochen gebundene Netz und die Adresse seiner Felder — null, solange es nicht gebunden ist, in der Haltung des Netzes steht oder die Seite keine Felder hat. */
    gelenkziel() {
        if (!this.objekt || !this.haut || !this._gelenkAdresse || this._haltung) return null;
        const netz = Meshfighaut.netze(this.objekt)[0];
        return netz?.isSkinnedMesh ? { netz, adresse: this._gelenkAdresse } : null;
    }

    /** In die Gruppe der Figur hängen; mit `skelett` (dem der gezeigten Figur) auch an ihre Knochen binden, wenn das Objekt eine Hautdatei hat. */
    anhaengen(gruppe, skelett = null) {
        this.gruppe = gruppe;
        if (skelett) this.skelett = skelett;
        if (this.objekt && this.objekt.parent !== gruppe) {
            this.objekt.parent?.remove(this.objekt);
            gruppe.add(this.objekt);
        }
        this._binden();
        this.sichtbar(this.an);
    }

    _binden() {
        if (!this.objekt || !this.haut || !this.skelett) return;
        Meshfighaut.binden(this.objekt, this.skelett, this.haut);
    }

    _hautLaden(beschreibung, marke, lauf) {
        Meshfighaut.laden(`${this.seite.dateiAdresse('ergebnis', beschreibung.datei)}?t=${marke}`, beschreibung.punkte)
            .then(haut => {
                if (lauf !== this._lauf) return;                    // inzwischen kam ein anderes Objekt
                this.haut = { ...haut, knochen: beschreibung.knochen };
                this._binden();
            })
            .catch(fehler => this.melden(`${this.art.name}: Hautgewichte nicht geladen (${fehler.message || fehler}) — das Objekt bleibt starr`));
    }

    sichtbar(an) {
        this.an = an;
        this.objekt?.traverse(o => { if (o.isMesh) o.visible = an; });
    }

    _laden(adresse, hautBeschreibung = null, marke = '') {
        const lauf = ++this._lauf;
        this.haut = null;
        new GLTFLoader().load(adresse, gltf => {
            if (lauf !== this._lauf) return;                        // überholt: ein neuerer Stand wird geladen
            const neu = gltf.scene;
            neu.name = this.art.name;
            neu.traverse(o => {
                for (const m of [].concat(o.material || [])) {
                    m.side = THREE.DoubleSide;
                    m.metalness = 0;
                    if (this.art.karten && m.map) m.alphaToCoverage = true;
                }
            });
            if (this.objekt) {
                this.objekt.parent?.remove(this.objekt);
                this.objekt.traverse(o => { o.geometry?.dispose?.(); });
            }
            this.objekt = neu;
            if (this.gruppe) this.anhaengen(this.gruppe);
            if (hautBeschreibung) this._hautLaden(hautBeschreibung, marke, lauf);
        }, undefined, fehler => this.melden(`${this.art.name} nicht geladen: ${fehler.message || fehler}`));
    }
}
